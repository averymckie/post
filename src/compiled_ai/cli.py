"""Command line.

    compiled-ai compile <pack>    parse, compile atoms, normalize, check, reconcile, order, seal
    compiled-ai verify <pack>     rebuild and compare with build/manifest.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_compile(args: argparse.Namespace) -> int:
    from .pack import compile_pack, write_build

    pack_dir = Path(args.pack)
    build = compile_pack(pack_dir)
    written = write_build(build, pack_dir / "build")
    counts: dict[str, int] = {}
    for a in build.atoms:
        counts[a.predicate] = counts.get(a.predicate, 0) + 1
    print(f"{build.pack}: {len(build.parsed)} sentences, {len(build.atoms)} atoms " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"candidates for adjudication: {len(build.candidates)}")
    if build.reconciliation is not None:
        print(f"precedence constraints: {build.reconciliation.checked}, consistent: {build.reconciliation.consistent}")
    if build.manifest is not None:
        print(f"sealed: {build.manifest.digest}")
    for e in build.errors:
        print(f"error {e.code}: {e.detail}", file=sys.stderr)
    print(f"build: {written['manifest'].parent if 'manifest' in written else pack_dir / 'build'}")
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
    old = {a.id for a in sealed.atoms}
    new = {a.id for a in build.manifest.atoms}
    for aid in sorted(new - old):
        print(f"added {aid}")
    for aid in sorted(old - new):
        print(f"removed {aid}")
    if sealed.toolchain != build.manifest.toolchain:
        print(f"toolchain changed: {sealed.toolchain} -> {build.manifest.toolchain}")
    print("rebuild does not reproduce the sealed manifest", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="compiled-ai")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile")
    c.add_argument("pack")
    c.set_defaults(fn=cmd_compile)
    v = sub.add_parser("verify")
    v.add_argument("pack")
    v.set_defaults(fn=cmd_verify)
    args = p.parse_args(argv)
    result: int = args.fn(args)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
