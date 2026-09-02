"""A pack: sources with provenance, and the build over them.

    sources.yaml       the sources: file, URL, retrieval, SHA-256, license
    sources/           the source files
    rejections.yaml    optional; atoms an analyst rejected against their sentences
    build/             generated: tokens.tsv, citations.json, parses.conllu,
                       atoms.jsonl, candidates.json, reconciliation.json,
                       ordering.json, manifest.json
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from .adjudicate import apply_rejections, load_rejections
from .check import check_atoms, fragment_candidates
from .fol import compile_atoms
from .model import Atom, Candidate, Manifest, Ordering, ParsedSentence, Reconciliation, Source, Strict
from .normalize import normalize
from .order import order
from .parse import parse_source
from .read import read_html, read_pdf, read_text
from .reconcile import reconcile
from .seal import manifest_json, seal
from .tables import write_tables


class BuildError(Strict):
    code: str
    detail: str


class Build(Strict):
    pack: str
    sources: tuple[Source, ...]
    parsed: tuple[ParsedSentence, ...]
    atoms: tuple[Atom, ...]
    candidates: tuple[Candidate, ...]
    reconciliation: Reconciliation | None
    ordering: Ordering | None
    manifest: Manifest | None
    errors: tuple[BuildError, ...]

    @property
    def ok(self) -> bool:
        return not self.errors and self.manifest is not None


def repo_root(pack_dir: Path) -> Path:
    for p in [pack_dir.resolve(), *pack_dir.resolve().parents]:
        if (p / "pyproject.toml").exists():
            return p
    return pack_dir.resolve().parent.parent


def model_path(pack_dir: Path) -> Path:
    data = yaml.safe_load((repo_root(pack_dir) / "models" / "sources.yaml").read_text(encoding="utf-8"))
    entry = data["models"][0]
    return repo_root(pack_dir) / "models" / str(entry["file"])


def read_sources(pack_dir: Path) -> tuple[list[Source], list[BuildError]]:
    data = yaml.safe_load((pack_dir / "sources.yaml").read_text(encoding="utf-8"))
    sources: list[Source] = []
    errors: list[BuildError] = []
    for entry in data.get("sources", []):
        if not entry.get("file"):
            continue
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
    return sources, errors


def compile_pack(pack_dir: Path) -> Build:
    pack_dir = pack_dir.resolve()
    name = pack_dir.name
    errors: list[BuildError] = []
    sources, src_errors = read_sources(pack_dir)
    errors.extend(src_errors)
    mp = model_path(pack_dir)

    parsed: list[ParsedSentence] = []
    for src in sources:
        parsed.extend(parse_source(src, mp))

    atoms = compile_atoms(parsed)
    atoms, candidates = normalize(atoms, parsed)
    check_atoms(atoms, parsed)
    candidates = sorted(candidates + fragment_candidates(atoms, parsed), key=lambda c: (c.sentence_id, c.code, c.detail))
    atoms = apply_rejections(atoms, load_rejections(pack_dir / "rejections.yaml"))

    rec: Reconciliation | None = None
    ordering: Ordering | None = None
    manifest: Manifest | None = None
    if not errors:
        rec = reconcile(atoms)
        ordering = order(atoms)
        if ordering.cycle:
            errors.append(BuildError(code="ORDER_CYCLE", detail=", ".join(f"{a}->{b}" for a, b in ordering.cycle)))
        if not rec.consistent:
            for core in rec.cores:
                errors.append(BuildError(code="PRECEDENCE_CONTRADICTION", detail=", ".join(core)))
    if not errors and rec is not None and ordering is not None:
        manifest = seal(name, sources, parsed, atoms, rec, ordering, mp)

    return Build(
        pack=name,
        sources=tuple(sources),
        parsed=tuple(parsed),
        atoms=tuple(atoms),
        candidates=tuple(candidates),
        reconciliation=rec,
        ordering=ordering,
        manifest=manifest,
        errors=tuple(sorted(errors, key=lambda e: (e.code, e.detail))),
    )


def write_build(build: Build, out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = write_tables(list(build.parsed), out_dir)
    atoms = out_dir / "atoms.jsonl"
    with atoms.open("w", encoding="utf-8", newline="\n") as fh:
        for a in build.atoms:
            fh.write(json.dumps(a.model_dump(), sort_keys=True, ensure_ascii=False) + "\n")
    written["atoms"] = atoms
    cand = out_dir / "candidates.json"
    cand.write_text(json.dumps([c.model_dump() for c in build.candidates], indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    written["candidates"] = cand
    if build.reconciliation is not None:
        p = out_dir / "reconciliation.json"
        p.write_text(json.dumps(build.reconciliation.model_dump(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written["reconciliation"] = p
    if build.ordering is not None:
        p = out_dir / "ordering.json"
        p.write_text(json.dumps(build.ordering.model_dump(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written["ordering"] = p
    if build.manifest is not None:
        p = out_dir / "manifest.json"
        p.write_text(manifest_json(build.manifest), encoding="utf-8")
        written["manifest"] = p
    errs = out_dir / "errors.json"
    errs.write_text(json.dumps([e.model_dump() for e in build.errors], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written["errors"] = errs
    return written


def load_manifest(path: Path) -> Manifest:
    return Manifest.model_validate_json(path.read_text(encoding="utf-8"))
