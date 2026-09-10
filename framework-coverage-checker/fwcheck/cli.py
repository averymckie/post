import argparse
import json
import sqlite3
import sys
from pathlib import Path
from jsonschema import ValidationError
from .io import read_json, write_json, InputError
from .catalogue import index_framework
from .construction import check_project
from .certificate import make_certificate, replay
from .intake import audit_summaries
from .schema import PROJECT_SCHEMA
from .finite import check_state_model, derive_obligations


def main(argv=None):
    parser = argparse.ArgumentParser(description="Finite framework reconstruction and evidence audit")
    subs = parser.add_subparsers(dest="command", required=True)
    ix = subs.add_parser("index")
    ix.add_argument("framework")
    ix.add_argument("--out", required=True)
    audit = subs.add_parser("audit")
    audit.add_argument("cases")
    audit.add_argument("--framework", required=True)
    audit.add_argument("--out", required=True)
    audit.add_argument("--reviews")
    audit.add_argument("--review-ledger")
    check = subs.add_parser("check")
    check.add_argument("case")
    check.add_argument("--framework", required=True)
    check.add_argument("--out", required=True)
    ver = subs.add_parser("replay")
    ver.add_argument("case")
    ver.add_argument("certificate")
    ver.add_argument("--framework", required=True)
    show = subs.add_parser("show")
    show.add_argument("database")
    show.add_argument("case_id")
    find = subs.add_parser("find")
    find.add_argument("database")
    find.add_argument("query")
    schema = subs.add_parser("schema")
    schema.add_argument("--out", required=True)
    for command in ["states", "obligations"]:
        sub = subs.add_parser(command)
        sub.add_argument("model")
        sub.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "index":
            result = index_framework(args.framework)
            write_json(args.out, result)
            print(json.dumps({"families": len(result["families"]), "proofs": len(result["proofs"]), "sha256": result["source_sha256"]}))
        elif args.command == "audit":
            index = index_framework(args.framework)
            result = audit_summaries(args.cases, index, args.out,
                                    read_json(args.reviews) if args.reviews else None,
                                    read_json(args.review_ledger) if args.review_ledger else None)
            print(json.dumps(result, indent=2))
        elif args.command == "check":
            if Path(args.out).exists(): raise InputError("Certificate exists; use a new output path")
            p = read_json(args.case)
            index = index_framework(args.framework)
            result = check_project(p, index["source_sha256"], index)
            write_json(args.out, make_certificate(p, result))
            print(json.dumps({k: result[k] for k in ["case_id", "construction_status", "coverage_status"]}))
        elif args.command == "replay":
            result = replay(read_json(args.case), read_json(args.certificate), index_framework(args.framework))
            print(json.dumps(result))
        elif args.command in {"show", "find"}:
            # Read-only connection; arguments are bound values, never SQL source.
            con = sqlite3.connect(Path(args.database).resolve().as_uri() + "?mode=ro", uri=True)
            if args.command == "show":
                row = con.execute("SELECT dossier_json FROM cases WHERE id=?", (args.case_id,)).fetchone()
                if row is None: raise InputError("Case not found")
                print(json.dumps(json.loads(row[0]), indent=2, ensure_ascii=False))
            else:
                print(json.dumps(con.execute("SELECT id, snippet(search,1,'[',']','...',20) FROM search WHERE search MATCH ? LIMIT 30", (args.query,)).fetchall(), ensure_ascii=False))
            con.close()
        elif args.command in {"states", "obligations"}:
            if Path(args.out).exists(): raise InputError("Result exists; use a new output path")
            fn = check_state_model if args.command == "states" else derive_obligations
            result = fn(read_json(args.model))
            write_json(args.out, result)
            print(json.dumps({"status": result["status"]}))
        else:
            write_json(args.out, PROJECT_SCHEMA)
        return 0
    except (InputError, ValidationError, ValueError, OSError, sqlite3.Error) as e:
        print(json.dumps({"status": "INPUT_ERROR", "message": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
