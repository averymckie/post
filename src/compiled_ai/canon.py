"""Canonical text. Version 1.

"Byte-exact" in the checker means byte-exact against this canonical form,
never against raw extractor output, because extractor output changes with
ligature handling, whitespace, and library versions. The rule is small,
versioned, and applied identically to PDF, HTML, and plain-text sources:

1. Each character is normalized to Unicode NFC on its own.
2. Every whitespace character (including no-break and thin spaces) becomes an
   ASCII space.
3. Runs of spaces collapse to one space.
4. Leading and trailing spaces of a unit are removed.

The canonical index -> original offset map is preserved through every step,
so a canonical span can always be located in the source file.

Changing anything here changes CANON_VERSION, which is part of every sealed
manifest, so a change to one rule changes every digest visibly.
"""

from __future__ import annotations

import unicodedata

CANON_VERSION = 1

_EXTRA_SPACES = {
    " ",  # no-break space
    " ",  # figure space
    " ",  # narrow no-break space
    "​",  # zero width space
    "﻿",  # byte order mark
}


def is_space(ch: str) -> bool:
    return ch.isspace() or ch in _EXTRA_SPACES


def canonicalize(chars: list[str], offsets: list[int]) -> tuple[str, list[int]]:
    """Return (canonical text, offset map) for one unit."""
    if len(chars) != len(offsets):
        raise ValueError("chars and offsets must have the same length")
    out: list[str] = []
    out_off: list[int] = []
    pending_space_offset: int | None = None
    for ch, off in zip(chars, offsets):
        for n in unicodedata.normalize("NFC", ch):
            if is_space(n):
                if out and pending_space_offset is None:
                    pending_space_offset = off
                continue
            if pending_space_offset is not None:
                out.append(" ")
                out_off.append(pending_space_offset)
                pending_space_offset = None
            out.append(n)
            out_off.append(off)
    return "".join(out), out_off
