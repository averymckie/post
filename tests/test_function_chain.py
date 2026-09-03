"""Every function the function-chain file names resolves in the installed
package. The file is `papers/2026-09-03-the-function-chain.md`; each `locate:`
line lists dotted paths. A path whose top-level package is installed must
resolve. A path whose package is not installed is reported and skipped, so the
test says what it did not check."""

from __future__ import annotations

import importlib
import re
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "papers" / "2026-09-03-the-function-chain.md"

# the wired chain: these must be installed and must resolve
REQUIRED_TOP = {"ufal", "predpatt", "typedlogic", "clingo", "clorm", "z3", "networkx", "pydantic", "hashlib", "json", "unicodedata", "html", "yaml", "pdfplumber"}


def _paths() -> list[str]:
    text = CHAIN.read_text(encoding="utf-8")
    out: list[str] = []
    for m in re.finditer(r"^\s*`locate: ([^`]+)`\s*$", text, flags=re.MULTILINE):
        out.extend(p.strip() for p in m.group(1).split(",") if p.strip())
    return sorted(set(out))


def _resolve(path: str):
    parts = path.split(".")
    for i in range(len(parts), 0, -1):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                obj = importlib.import_module(".".join(parts[:i]))
        except ImportError:
            continue
        try:
            for attr in parts[i:]:
                obj = getattr(obj, attr)
            return obj
        except AttributeError:
            return None
    return None


def _installed(top: str) -> bool:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            importlib.import_module(top)
        return True
    except ImportError:
        return False


def test_every_located_function_in_the_chain_file_resolves() -> None:
    paths = _paths()
    assert paths, "no locate: lines found"
    skipped: list[str] = []
    missing: list[str] = []
    for p in paths:
        top = p.split(".")[0]
        if not _installed(top):
            skipped.append(p)
            continue
        if _resolve(p) is None:
            missing.append(p)
    assert not missing, f"named in the chain file but not resolvable: {missing}"
    tops_not_installed = sorted({p.split('.')[0] for p in skipped})
    assert not (REQUIRED_TOP & set(tops_not_installed)), f"wired chain packages missing: {REQUIRED_TOP & set(tops_not_installed)}"
    print(f"resolved {len(paths) - len(skipped)} paths; not installed here: {tops_not_installed}")
