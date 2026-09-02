"""A pack: one industry's sources, record, proposals, checklist, rules, invariants.

Layout of a pack directory:

    sources.yaml      the sources with URL, edition, retrieval date, SHA-256, license
    sources/          the source files (public-domain ones are committed)
    reserved.yaml     roles the source names and decisions it reserves, each with
                      a byte-exact quote
    record.py         the typed case record (a pydantic model named `Record`)
    rules.py          the rule functions, registered with @rule
    fixtures/proposals/*.json   recorded proposals per sentence digest
    checklist.yaml    the reviewer's answers
    build/            the sealed manifest and the build report (generated)

`compile_pack` runs steps 1 to 10 except prove, which is a separate command
because it runs mypy and pytest.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml
from pydantic import BaseModel

from .check import check_all, defined_terms_from
from .confirm import confirmed_statements, load_checklist
from .cut import cut
from .generate import GenerateReport, match_rules
from .model import Confirmation, Manifest, Sentence, Source, Statement, Strict
from .order import Ordering, edges_from, order
from .propose import Proposer, ReplayProposer, records_to_proposals
from .read import read_html, read_pdf, read_text
from .reconcile import Reconciliation, constraints_from, reconcile
from .registry import RuleDef, RuleFn, collect_rules
from .seal import manifest_json, rule_specs, seal


class RoleSpec(Strict):
    name: str
    path: str
    quote: str


class DecisionSpec(Strict):
    decision: str
    role: str
    path: str
    quote: str


class BuildError(Strict):
    code: str
    detail: str


class Build(Strict):
    pack: str
    sources: tuple[Source, ...]
    sentences: tuple[Sentence, ...]
    statements: tuple[Statement, ...]
    confirmed: tuple[tuple[Statement, Confirmation], ...]
    generate: GenerateReport
    reconciliation: Reconciliation | None
    ordering: Ordering | None
    manifest: Manifest | None
    errors: tuple[BuildError, ...]

    @property
    def ok(self) -> bool:
        return not self.errors and self.manifest is not None


def _load_module(pack_dir: Path, name: str) -> ModuleType:
    """Import `<packs>.<pack>.<name>` with the packs' parent directory on sys.path,
    so a pack's modules can import each other as a package."""
    pack_dir = pack_dir.resolve()
    root = pack_dir.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(f"{pack_dir.parent.name}.{pack_dir.name}.{name}")


def load_record_type(pack_dir: Path) -> type[BaseModel]:
    mod = _load_module(pack_dir, "record")
    rec = getattr(mod, "Record")
    if not (isinstance(rec, type) and issubclass(rec, BaseModel)):
        raise TypeError("record.py must define a pydantic model named Record")
    return rec


def load_rules(pack_dir: Path) -> list[tuple[RuleDef, RuleFn]]:
    mod = _load_module(pack_dir, "rules")
    return collect_rules(mod)


def read_sources(pack_dir: Path) -> tuple[list[Source], dict[str, str], list[BuildError]]:
    data = yaml.safe_load((pack_dir / "sources.yaml").read_text(encoding="utf-8"))
    sources: list[Source] = []
    errors: list[BuildError] = []
    scope_of: dict[str, str] = {}
    for entry in data.get("sources", []):
        if not entry.get("file"):
            continue  # cited, not compiled
        path = pack_dir / entry["file"]
        kind = entry.get("kind", "text")
        sid = entry["id"]
        if kind == "html":
            src = read_html(path, sid, start_marker=entry.get("start_marker"))
        elif kind == "pdf":
            src = read_pdf(path, sid)
        else:
            src = read_text(path, sid)
        expected = entry.get("sha256")
        if expected and expected != src.sha256:
            errors.append(BuildError(code="SOURCE_HASH_MISMATCH", detail=f"{sid}: sources.yaml says {expected}, file is {src.sha256}"))
        sources.append(src)
        scope_of[sid] = entry.get("scope", sid)
    return sources, scope_of, errors


def load_reserved(pack_dir: Path, sentences: list[Sentence]) -> tuple[list[RoleSpec], list[DecisionSpec], list[BuildError]]:
    path = pack_dir / "reserved.yaml"
    if not path.exists():
        return [], [], []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    by_path: dict[str, list[Sentence]] = {}
    for s in sentences:
        by_path.setdefault(s.path, []).append(s)
    errors: list[BuildError] = []
    roles = [RoleSpec.model_validate(r) for r in data.get("roles", [])]
    decisions = [DecisionSpec.model_validate(d) for d in data.get("decisions", [])]
    for r in roles:
        if not any(r.quote.encode("utf-8") in s.text.encode("utf-8") for s in by_path.get(r.path, [])):
            errors.append(BuildError(code="ROLE_QUOTE_NOT_BYTE_EXACT", detail=f"role {r.name!r}: quote not found byte-exact at {r.path}"))
    role_names = {r.name for r in roles}
    for d in decisions:
        if not any(d.quote.encode("utf-8") in s.text.encode("utf-8") for s in by_path.get(d.path, [])):
            errors.append(BuildError(code="DECISION_QUOTE_NOT_BYTE_EXACT", detail=f"decision {d.decision!r}: quote not found byte-exact at {d.path}"))
        if d.role not in role_names:
            errors.append(BuildError(code="DECISION_ROLE_UNKNOWN", detail=f"decision {d.decision!r} names role {d.role!r}, which is not listed"))
    return roles, decisions, errors


def compile_pack(pack_dir: Path, proposer: Proposer | None = None) -> Build:
    pack_dir = pack_dir.resolve()
    name = pack_dir.name
    errors: list[BuildError] = []

    sources, scope_of, src_errors = read_sources(pack_dir)
    errors.extend(src_errors)

    sentences: list[Sentence] = []
    for src in sources:
        sentences.extend(cut(src))

    proposer = proposer or ReplayProposer(pack_dir / "fixtures" / "proposals")
    records = {}
    for s in sentences:
        rec = proposer.propose(s)
        if rec is not None:
            records[s.digest] = rec
    proposals = records_to_proposals(records)

    roles, decisions, reserved_errors = load_reserved(pack_dir, sentences)
    errors.extend(reserved_errors)
    role_names = [r.name for r in roles]

    # Two passes: definitions accepted in the first pass define terms for the second.
    first = check_all(sentences, proposals, defined_terms=(), roles=role_names)
    terms = defined_terms_from(first)
    statements = check_all(sentences, proposals, defined_terms=terms, roles=role_names)

    checklist = load_checklist(pack_dir / "checklist.yaml") if (pack_dir / "checklist.yaml").exists() else []
    confirmed = confirmed_statements(statements, checklist)

    rules = load_rules(pack_dir) if (pack_dir / "rules.py").exists() else []
    gen = match_rules(confirmed, [r for r, _ in rules])
    for e in gen.errors:
        errors.append(BuildError(code=e.code, detail=e.detail))

    reconciliation: Reconciliation | None = None
    ordering: Ordering | None = None
    manifest: Manifest | None = None
    if not errors:
        confirmed_statements_only = [st for st, _ in confirmed]
        reconciliation = reconcile(constraints_from(confirmed_statements_only, scope_of))
        if not reconciliation.consistent:
            for core in reconciliation.contradictions:
                errors.append(BuildError(code="CONTRADICTION", detail=", ".join(core)))
        ordering = order(edges_from(confirmed_statements_only))
        if ordering.cycle:
            errors.append(BuildError(code="ORDER_CYCLE", detail=", ".join(f"{a}->{b}" for a, b in ordering.cycle)))
    if not errors and reconciliation is not None and ordering is not None:
        specs = rule_specs(confirmed, rules)
        manifest = seal(name, sources, specs, ordering.order)

    return Build(
        pack=name,
        sources=tuple(sources),
        sentences=tuple(sentences),
        statements=tuple(statements),
        confirmed=tuple(confirmed),
        generate=gen,
        reconciliation=reconciliation,
        ordering=ordering,
        manifest=manifest,
        errors=tuple(sorted(errors, key=lambda e: (e.code, e.detail))),
    )


def write_build(build: Build, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    if build.manifest is not None:
        p = out_dir / "manifest.json"
        p.write_text(manifest_json(build.manifest), encoding="utf-8")
        written["manifest"] = p
    report: dict[str, Any] = {
        "pack": build.pack,
        "sources": [{"id": s.id, "sha256": s.sha256, "units": len(s.units), "notes": list(s.notes)} for s in build.sources],
        "sentences": len(build.sentences),
        "proposed_sentences": sorted({st.sentence.id for st in build.statements}),
        "accepted_statements": sorted(f"{st.sentence.id}:{st.proposal.kind}" for st in build.statements if st.check.ok),
        "rejected": [
            {"sentence": st.sentence.id, "kind": st.proposal.kind, "failures": [f.model_dump() for f in st.check.failures]}
            for st in build.statements
            if not st.check.ok
        ],
        "confirmed": [c.id for _, c in build.confirmed],
        "provisional": [c.id for _, c in build.confirmed if c.provisional],
        "generate": build.generate.model_dump(),
        "reconciliation": build.reconciliation.model_dump() if build.reconciliation else None,
        "ordering": build.ordering.model_dump() if build.ordering else None,
        "errors": [e.model_dump() for e in build.errors],
    }
    import json

    p = out_dir / "report.json"
    p.write_text(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    written["report"] = p
    return written


def load_manifest(path: Path) -> Manifest:
    return Manifest.model_validate_json(path.read_text(encoding="utf-8"))
