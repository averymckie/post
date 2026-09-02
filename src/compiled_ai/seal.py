"""Step 10, seal: a digest per rule from the bytes of its source sentence.

The manifest lists every rule with the digest of its sentence's canonical
bytes and the digest of its function's source. It also carries the
canonicalization version and the pinned tool versions, so a rebuild on the
same toolchain reproduces every digest and a toolchain change is visible as
a digest change. The manifest's own digest is the SHA-256 of its canonical
JSON, with sorted keys and no insignificant whitespace.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from .canon import CANON_VERSION
from .model import Confirmation, Manifest, RuleSpec, Source, Statement, sha256_text
from .registry import RuleDef

PINNED = ("pydantic", "pdfplumber", "spacy", "z3-solver", "networkx", "mypy", "hypothesis")


def toolchain() -> dict[str, str]:
    out: dict[str, str] = {"canon": str(CANON_VERSION)}
    for name in PINNED:
        try:
            out[name] = version(name)
        except PackageNotFoundError:
            out[name] = "absent"
    return dict(sorted(out.items()))


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def rule_specs(
    confirmed: Iterable[tuple[Statement, Confirmation]], rules: Iterable[tuple[RuleDef, Any]]
) -> list[RuleSpec]:
    by_statement = {r.statement: r for r, _ in rules}
    specs: list[RuleSpec] = []
    for st, conf in confirmed:
        r = by_statement.get(conf.id)
        specs.append(
            RuleSpec(
                id=r.id if r else f"statement.{conf.id}",
                sentence_id=st.sentence.id,
                sentence_digest=st.sentence.digest,
                path=st.sentence.path,
                kind=st.proposal.kind,
                function=r.function if r else "",
                function_digest=sha256_text(r.source) if r else "",
                quote=st.proposal.quote,
                provisional=conf.provisional,
            )
        )
    return sorted(specs, key=lambda s: s.id)


def seal(pack: str, sources: Iterable[Source], specs: list[RuleSpec], order: Iterable[str]) -> Manifest:
    body = {
        "pack": pack,
        "canon_version": CANON_VERSION,
        "toolchain": toolchain(),
        "sources": sorted((s.id, s.sha256) for s in sources),
        "rules": [s.model_dump() for s in specs],
        "order": list(order),
        "provisional": any(s.provisional for s in specs),
    }
    digest = hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()
    return Manifest(
        pack=pack,
        canon_version=CANON_VERSION,
        toolchain=body["toolchain"],  # type: ignore[arg-type]
        sources=tuple(body["sources"]),  # type: ignore[arg-type]
        rules=tuple(specs),
        order=tuple(order),
        provisional=bool(body["provisional"]),
        digest=digest,
    )


def manifest_json(m: Manifest) -> str:
    return canonical_json(m.model_dump()) + "\n"


def verify_digest(m: Manifest) -> bool:
    body = m.model_dump()
    body.pop("digest")
    body["sources"] = [list(s) for s in body["sources"]]
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest() == m.digest
