"""Seal: a digest per atom from the bytes of its sentence and its quote, and one
digest over the whole base. Canonical JSON with sorted keys and no insignificant
whitespace. The pinned toolchain, including the parser model's SHA-256, is part
of the manifest, so a change to the parser is visible as a digest change."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .canon import CANON_VERSION
from .model import Atom, AtomSeal, Manifest, Ordering, ParsedSentence, Reconciliation, Source, sha256_text

PINNED = ("pydantic", "ufal.udpipe", "z3-solver", "networkx", "pdfplumber")


def toolchain(model_path: Path) -> dict[str, str]:
    out: dict[str, str] = {"canon": str(CANON_VERSION), "udpipe_model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest()}
    for name in PINNED:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = "absent"
    return dict(sorted(out.items()))


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def seal(pack: str, sources: Iterable[Source], parsed: list[ParsedSentence], atoms: list[Atom], rec: Reconciliation, ordering: Ordering, model_path: Path) -> Manifest:
    digests = {ps.sentence.id: ps.sentence.digest for ps in parsed}
    seals = [AtomSeal(id=a.id, sentence_id=a.sentence_id, sentence_digest=digests[a.sentence_id], quote_digest=sha256_text(a.quote)) for a in atoms]
    body = {
        "pack": pack,
        "canon_version": CANON_VERSION,
        "toolchain": toolchain(model_path),
        "sources": sorted((s.id, s.sha256) for s in sources),
        "atoms": [s.model_dump() for s in seals],
        "forced": [list(e) for e in ordering.forced],
        "order": list(ordering.order),
        "consistent": rec.consistent,
    }
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
    return Manifest(
        pack=pack,
        canon_version=CANON_VERSION,
        toolchain=body["toolchain"],  # type: ignore[arg-type]
        sources=tuple(body["sources"]),  # type: ignore[arg-type]
        atoms=tuple(seals),
        forced=ordering.forced,
        order=ordering.order,
        consistent=rec.consistent,
        digest=digest,
    )


def manifest_json(m: Manifest) -> str:
    return canonical_json(m.model_dump()) + "\n"


def verify_digest(m: Manifest) -> bool:
    body = m.model_dump()
    body.pop("digest")
    body["sources"] = [list(s) for s in body["sources"]]
    body["forced"] = [list(e) for e in body["forced"]]
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest() == m.digest
