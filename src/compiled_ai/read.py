"""Step 1, read: every character of the source with its position.

Three readers, one output type. Each reader produces units of canonical text
with an offset map back to the original file. Nothing is summarized.

- read_html: for a government web page that carries a statute. Text inside
  <s> (struck through, meaning repealed language) is dropped and the drop is
  recorded in the source notes. Text inside <strong> (newly enacted language
  on the DOJ page) is kept. Units are <p>, <li>, and heading elements.
- read_pdf: pdfplumber, with every option fixed explicitly so the output is
  a function of the file and the pinned library version.
- read_text: plain text, units are blank-line separated paragraphs.
"""

from __future__ import annotations

import hashlib
import html
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .canon import CANON_VERSION, canonicalize
from .model import Source, Unit

_DESIGNATOR = re.compile(r"^(?:\([A-Za-z0-9]{1,4}\))+")
_LEVEL = re.compile(r"statute-indent-level-(\d+)")
_BLOCK_TAGS = {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6"}
_SKIP_TAGS = {"s", "del", "strike", "script", "style"}


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Block:
    __slots__ = ("chars", "offsets", "level", "tag")

    def __init__(self, tag: str, level: int) -> None:
        self.tag = tag
        self.level = level
        self.chars: list[str] = []
        self.offsets: list[int] = []


class _StatuteHTML(HTMLParser):
    def __init__(self, raw: str) -> None:
        super().__init__(convert_charrefs=False)
        self.raw = raw
        self.line_starts = [0]
        for i, ch in enumerate(raw):
            if ch == "\n":
                self.line_starts.append(i + 1)
        self.blocks: list[_Block] = []
        self.current: _Block | None = None
        self.skip_depth = 0
        self.level_stack: list[int] = []
        self.dropped = 0

    def _offset(self) -> int:
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self.skip_depth += 1
            return
        if tag == "ul" or tag == "ol":
            cls = dict(attrs).get("class") or ""
            m = _LEVEL.search(cls)
            self.level_stack.append(int(m.group(1)) if m else len(self.level_stack) + 1)
            return
        if tag in _BLOCK_TAGS:
            level = self.level_stack[-1] if (tag == "li" and self.level_stack) else 0
            self.current = _Block(tag, level)
            self.blocks.append(self.current)

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if tag == "ul" or tag == "ol":
            if self.level_stack:
                self.level_stack.pop()
            return
        if tag in _BLOCK_TAGS:
            self.current = None

    def _emit(self, text: str, base: int) -> None:
        if self.current is None:
            return
        if self.skip_depth:
            self.dropped += len(text)
            return
        for i, ch in enumerate(text):
            self.current.chars.append(ch)
            self.current.offsets.append(base + i)

    def handle_data(self, data: str) -> None:
        self._emit(data, self._offset())

    def handle_entityref(self, name: str) -> None:
        self._emit(html.unescape(f"&{name};"), self._offset())

    def handle_charref(self, name: str) -> None:
        self._emit(html.unescape(f"&#{name};"), self._offset())


_ONE_DESIGNATOR = re.compile(r"\(([A-Za-z0-9]{1,4})\)")
_ROMAN_LOWER = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv"}
_ROMAN_UPPER = {r.upper() for r in _ROMAN_LOWER}


def _designator_kind(body: str, kinds_so_far: list[str]) -> str:
    """Classify a designator by the US Code numbering grammar.

    subsection (a) > paragraph (1) > subparagraph (A) > clause (i) >
    subclause (I) > item (aa). '(i)' is a clause only under a subparagraph;
    otherwise it is the subsection after (h).
    """
    if body.isdigit():
        return "number"
    if body.islower():
        if body in _ROMAN_LOWER and "upper" in kinds_so_far:
            return "roman_lower"
        if len(body) == 2 and body[0] == body[1]:
            return "double_lower"
        return "lower"
    if body in _ROMAN_UPPER and "roman_lower" in kinds_so_far:
        return "roman_upper"
    return "upper"


def _paths_for_blocks(blocks: list[_Block]) -> list[str]:
    """Derive a statutory path such as (a)(6)(A)(i) for each block.

    The page's HTML nesting does not always match the statute's structure, so
    the path is derived from the designators themselves: each designator
    either replaces the designator of the same kind in the running path (a
    sibling) or extends the path (a child). A block with no designator is
    trailing text of the previous block and gets its path plus '+'.
    """
    paths: list[str] = []
    path: list[tuple[str, str]] = []  # (designator, kind)
    for b in blocks:
        text = "".join(b.chars).strip()
        m = _DESIGNATOR.match(text)
        if not m:
            paths.append("".join(d for d, _ in path) + "+")
            continue
        for dm in _ONE_DESIGNATOR.finditer(m.group(0)):
            body = dm.group(1)
            kind = _designator_kind(body, [k for _, k in path])
            existing = [i for i, (_, k) in enumerate(path) if k == kind]
            if existing:
                path = path[: existing[0]]
            path.append((f"({body})", kind))
        paths.append("".join(d for d, _ in path))
    return paths


def read_html(path: Path, source_id: str, start_marker: str | None = None) -> Source:
    raw = path.read_text(encoding="utf-8")
    parser = _StatuteHTML(raw)
    parser.feed(raw)
    parser.close()
    paths = _paths_for_blocks(parser.blocks)
    units: list[Unit] = []
    started = start_marker is None
    skipped_before_marker = 0
    for i, (b, p) in enumerate(zip(parser.blocks, paths)):
        text, offsets = canonicalize(b.chars, b.offsets)
        if not text:
            continue
        if not started:
            if text.startswith(start_marker or ""):
                started = True
            else:
                skipped_before_marker += 1
                continue
        is_heading = b.tag.startswith("h") or text.startswith("§")
        units.append(
            Unit(
                id=f"u{len(units):04d}",
                path=p if not is_heading else "",
                text=text,
                offsets=tuple(offsets),
                page=1,
                is_heading=is_heading,
            )
        )
    notes = [
        "html: text inside <s>/<del>/<strike> (struck-through, repealed language) was dropped; "
        f"{parser.dropped} characters dropped",
        "html: text inside <strong> was kept",
    ]
    if start_marker is not None:
        notes.append(
            f"html: {skipped_before_marker} block(s) before the first block starting with "
            f"{start_marker!r} were not read (page front matter and introduction)"
        )
    return Source(
        id=source_id,
        kind="html",
        path=str(path),
        sha256=_sha256_file(path),
        canon_version=CANON_VERSION,
        units=tuple(units),
        notes=tuple(notes),
    )


def read_text(path: Path, source_id: str) -> Source:
    raw = path.read_text(encoding="utf-8")
    units: list[Unit] = []
    pos = 0
    for para in re.split(r"\n[ \t]*\n", raw):
        start = raw.index(para, pos)
        pos = start + len(para)
        chars = list(para)
        offsets = list(range(start, start + len(para)))
        text, omap = canonicalize(chars, offsets)
        if not text:
            continue
        units.append(Unit(id=f"u{len(units):04d}", path="", text=text, offsets=tuple(omap)))
    return Source(
        id=source_id,
        kind="text",
        path=str(path),
        sha256=_sha256_file(path),
        canon_version=CANON_VERSION,
        units=tuple(units),
    )


def read_pdf(path: Path, source_id: str) -> Source:
    """pdfplumber with every option fixed. A paragraph break is a line gap of
    more than one and a half line heights. A hyphen at a line end followed by
    a lowercase letter is a broken word and is joined. Both rules are recorded
    in the source notes."""
    import pdfplumber  # compiler-only dependency

    units: list[Unit] = []
    notes = [
        "pdf: pdfplumber extract_words(x_tolerance=3, y_tolerance=3, use_text_flow=False, "
        "expand_ligatures=True, split_at_punctuation=False, return_chars=True)",
        "pdf: a new unit starts when the vertical gap between lines exceeds 1.5 line heights",
        "pdf: a line ending in '-' directly followed by a lowercase letter on the next line is "
        "joined without the hyphen",
    ]
    with pdfplumber.open(str(path)) as pdf:
        running = 0
        for page_no, page in enumerate(pdf.pages, start=1):
            words = page.extract_words(
                x_tolerance=3,
                y_tolerance=3,
                keep_blank_chars=False,
                use_text_flow=False,
                extra_attrs=[],
                split_at_punctuation=False,
                expand_ligatures=True,
                return_chars=True,
            )
            lines: list[list[dict[str, Any]]] = []
            typed_words: list[dict[str, Any]] = list(words)
            for w in sorted(typed_words, key=lambda w: (round(float(w["top"]), 1), float(w["x0"]))):
                if lines and abs(float(lines[-1][0]["top"]) - float(w["top"])) <= 3:
                    lines[-1].append(w)
                else:
                    lines.append([w])
            chars: list[str] = []
            offsets: list[int] = []
            prev_bottom: float | None = None
            prev_height: float | None = None

            def flush() -> None:
                nonlocal chars, offsets
                text, omap = canonicalize(chars, offsets)
                if text:
                    units.append(
                        Unit(id=f"u{len(units):04d}", path="", text=text, offsets=tuple(omap), page=page_no)
                    )
                chars, offsets = [], []

            for line in lines:
                top = float(line[0]["top"])
                bottom = float(line[0]["bottom"])
                height = bottom - top
                if prev_bottom is not None and prev_height is not None and top - prev_bottom > 1.5 * prev_height:
                    flush()
                if chars:
                    if chars[-1] == "-" and line and str(line[0]["text"])[:1].islower():
                        chars.pop()
                        offsets.pop()
                    else:
                        chars.append(" ")
                        offsets.append(running)
                for wi, w in enumerate(line):
                    if wi:
                        chars.append(" ")
                        offsets.append(running)
                    for c in w["chars"]:
                        chars.append(str(c["text"]))
                        offsets.append(running)
                        running += 1
                prev_bottom, prev_height = bottom, height
            flush()
    return Source(
        id=source_id,
        kind="pdf",
        path=str(path),
        sha256=_sha256_file(path),
        canon_version=CANON_VERSION,
        units=tuple(units),
        notes=tuple(notes),
    )
