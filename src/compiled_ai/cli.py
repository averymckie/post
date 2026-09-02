"""Command line.

    compiled-ai compile <pack>           build and seal a pack
    compiled-ai verify <pack>            rebuild and compare every digest with build/manifest.json
    compiled-ai run <pack> <case.json>   evaluate one case; prints a proof or reasons as JSON
    compiled-ai prove <pack>             mypy --strict and the pack's tests
    compiled-ai fixtures <pack> --live   record model proposals for sentences with no fixture
                                         (the only command that calls a model)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in here.parents:
        if (p / "pyproject.toml").exists():
            return p
    return Path.cwd()


def cmd_compile(args: argparse.Namespace) -> int:
    from .pack import compile_pack, write_build

    pack_dir = Path(args.pack)
    build = compile_pack(pack_dir)
    written = write_build(build, pack_dir / "build")
    if build.manifest is not None:
        print(f"sealed {build.pack}: {len(build.manifest.rules)} rules, digest {build.manifest.digest}")
        if build.manifest.provisional:
            print("provisional: one or more confirmations await a named reviewer")
    for e in build.errors:
        print(f"error {e.code}: {e.detail}", file=sys.stderr)
    print(f"report: {written['report']}")
    return 0 if build.ok else 1


def cmd_verify(args: argparse.Namespace) -> int:
    from .pack import compile_pack, load_manifest
    from .seal import verify_digest

    pack_dir = Path(args.pack)
    sealed = load_manifest(pack_dir / "build" / "manifest.json")
    if not verify_digest(sealed):
        print("manifest digest does not match its contents", file=sys.stderr)
        return 1
    build = compile_pack(pack_dir)
    if build.manifest is None:
        for e in build.errors:
            print(f"error {e.code}: {e.detail}", file=sys.stderr)
        return 1
    if build.manifest.digest == sealed.digest:
        print(f"verified: rebuild reproduces digest {sealed.digest}")
        return 0
    old = {r.id: r for r in sealed.rules}
    new = {r.id: r for r in build.manifest.rules}
    for rid in sorted(set(old) | set(new)):
        if rid not in old:
            print(f"added rule {rid}")
        elif rid not in new:
            print(f"removed rule {rid}")
        elif old[rid] != new[rid]:
            print(f"changed rule {rid}")
    if sealed.toolchain != build.manifest.toolchain:
        print(f"toolchain changed: {sealed.toolchain} -> {build.manifest.toolchain}")
    print("rebuild does not reproduce the sealed manifest", file=sys.stderr)
    return 1


def cmd_run(args: argparse.Namespace) -> int:
    from .pack import load_manifest, load_record_type, load_rules
    from .runtime import Runtime

    pack_dir = Path(args.pack)
    manifest = load_manifest(pack_dir / "build" / "manifest.json")
    rt = Runtime(manifest, load_rules(pack_dir), load_record_type(pack_dir))
    raw = json.loads(Path(args.case).read_text(encoding="utf-8"))
    result = rt.evaluate(raw)
    print(result.model_dump_json(indent=2))
    return 0 if result.kind == "proof" else 2


def cmd_prove(args: argparse.Namespace) -> int:
    from .prove import prove

    report = prove(Path(args.pack), _repo_root())
    print("mypy:", "ok" if report.mypy_ok else "failed")
    if not report.mypy_ok:
        print(report.mypy_output)
    print("tests:", "ok" if report.tests_ok else "failed")
    print(report.tests_output.splitlines()[-1] if report.tests_output else "")
    if not report.tests_ok:
        print(report.tests_output)
    return 0 if report.ok else 1


def cmd_fixtures(args: argparse.Namespace) -> int:
    from .pack import read_sources
    from .cut import cut
    from .propose import ReplayProposer, write_fixture

    pack_dir = Path(args.pack)
    if not args.live:
        print("fixtures are recorded only with --live; nothing done")
        return 0
    from .propose import LiveProposer

    live = LiveProposer(model=args.model)
    replay = ReplayProposer(pack_dir / "fixtures" / "proposals")
    sources, _, errors = read_sources(pack_dir)
    if errors:
        for e in errors:
            print(f"error {e.code}: {e.detail}", file=sys.stderr)
        return 1
    n = 0
    for src in sources:
        for s in cut(src):
            if replay.propose(s) is not None:
                continue
            rec = live.propose(s)
            if rec is None:
                continue
            path = write_fixture(pack_dir / "fixtures" / "proposals", rec)
            print(f"recorded {path.name} for {s.path or s.id}")
            n += 1
    print(f"recorded {n} fixture(s); run compile to see which the checker accepts")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="compiled-ai")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile")
    c.add_argument("pack")
    c.set_defaults(fn=cmd_compile)
    v = sub.add_parser("verify")
    v.add_argument("pack")
    v.set_defaults(fn=cmd_verify)
    r = sub.add_parser("run")
    r.add_argument("pack")
    r.add_argument("case")
    r.set_defaults(fn=cmd_run)
    pr = sub.add_parser("prove")
    pr.add_argument("pack")
    pr.set_defaults(fn=cmd_prove)
    f = sub.add_parser("fixtures")
    f.add_argument("pack")
    f.add_argument("--live", action="store_true")
    f.add_argument("--model", default="claude-opus-5")
    f.set_defaults(fn=cmd_fixtures)
    args = p.parse_args(argv)
    fn = args.fn
    result: int = fn(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
