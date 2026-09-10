"""Lossless summary intake and audit. Never infers semantic coverage from labels."""
import re
import sqlite3
from collections import Counter
from pathlib import Path
from .io import InputError, canonical, file_hash, digest, write_json

FIELDS = ["id", "regime", "domain", "scale", "beneficiary", "need", "deliverables", "parts", "inputs",
          "conditions", "dynamics", "tags", "window", "verdict"]
MULTI = {"deliverables", "parts", "inputs", "conditions", "dynamics", "tags"}


def read_summaries(path):
    seen = set()
    with Path(path).open() as f:
        header = next(f, "")
        if "verdict strict/lenient" not in header: raise InputError("Unexpected summary export header")
        for line_no, line in enumerate(f, 2):
            values = line.rstrip("\r\n").split(" | ")
            if len(values) != 14: raise InputError(f"Line {line_no}: expected 14 fields, got {len(values)}")
            row = dict(zip(FIELDS, values))
            if not re.fullmatch(r"UC-\d{5}", row["id"]) or row["id"] in seen:
                raise InputError(f"Invalid or duplicate case ID at line {line_no}")
            seen.add(row["id"])
            for key in MULTI: row[key] = row[key].split("; ")
            for part in row["parts"]:
                if len(part.split(" > ")) != 2: raise InputError(f"Invalid part at line {line_no}")
            if not re.fullmatch(r"(COVERED|PARTIAL|UNEXPLAINED)/(COVERED|PARTIAL|UNEXPLAINED)", row["verdict"]):
                raise InputError(f"Invalid source verdict at line {line_no}")
            row["source_line"] = line_no
            row["source_line_sha256"] = digest(line.rstrip("\r\n"))
            yield row


def clause_inventory(row):
    out = []
    # Context and tags are retained as scope constraints pending interpretation.
    # Splitting phrases into atomic predicates is deliberately not fabricated.
    for field in FIELDS[1:-1]:
        values = row[field] if isinstance(row[field], list) else [row[field]]
        for n, value in enumerate(values, 1):
            out.append({"id": f"{row['id']}.{field}.{n:03d}", "source_field": field,
                        "occurrence": n, "text": value,
                        "semantic_state": "UNFORMALIZED_SOURCE_CLAUSE"})
    return out


def assess_row(row, source_hash, framework_hash, needs, conditions):
    findings = []
    if row["verdict"] == "COVERED/PARTIAL":
        findings.append({"kind": "VERDICT_ORDER_REVIEW", "layer": "HISTORICAL_EVALUATOR",
                         "detail": "Strict C / lenient P needs trace or verdict-semantics explanation; not a proven defect without those semantics."})
    for field in ["deliverables", "parts", "inputs"]:
        duplicates = [v for v, n in Counter(row[field]).items() if n > 1]
        if duplicates:
            findings.append({"kind": "MULTIPLICITY_UNRESOLVED", "layer": "CASE_DETAIL", "field": field, "labels": duplicates})
    if "-" in row["inputs"]:
        findings.append({"kind": "INPUT_PLACEHOLDER", "layer": "CASE_DETAIL"})
    part_outputs = {p.split(" > ")[1] for p in row["parts"]}
    missing_outputs = sorted(set(row["deliverables"]) - part_outputs)
    window = re.fullmatch(r"(\d+) days, deadline day (\d+)", row["window"])
    numeric = {"status": "UNPARSED"}
    if window:
        horizon, deadline = map(int, window.groups())
        numeric = {"status": "PASS" if 0 <= deadline <= horizon else "FAIL", "horizon": horizon,
                   "deadline": deadline, "scope": "Literal deadline within literal window only; no schedule feasibility claim"}
    else:
        findings.append({"kind": "WINDOW_ENCODING_UNSUPPORTED", "layer": "ENCODING"})
    if missing_outputs: findings.append({"kind": "ROOT_OUTPUT_LABEL_ABSENT", "layer": "CASE_STRUCTURE", "outputs": missing_outputs})
    if numeric["status"] == "FAIL": findings.append({"kind": "DEADLINE_EXCEEDS_WINDOW", "layer": "CASE_CONSISTENCY"})
    profile = needs.get(row["need"])
    review = None
    if profile:
        review = {"profile_id": "N" + profile["Need number"].zfill(2),
                  "candidate_construction": profile["Candidate construction"],
                  "proofs_to_inspect": profile["Proof records to inspect"],
                  "acceptance_to_establish": profile["Required meaning and acceptance"],
                  "status": "HUMAN_AUTHORED_REVIEW_AID_NOT_A_PROOF"}
        if profile["Example"] == row["id"]:
            review["individual_summary_review"] = profile["Finding on the representative summary"]
    clause_list = clause_inventory(row)
    return {"format": "fwcheck.intake.v1", "case_id": row["id"], "source_sha256": source_hash,
            "framework_sha256": framework_hash, "source": row,
            "source_clauses": clause_list, "clause_inventory_sha256": digest(clause_list),
            "coverage_status": "CASE_FORMALIZATION_REQUIRED", "construction_status": "NOT_SEARCHED_NO_ACCEPTED_CONTRACT",
            "proof_status": "NO_CASE_BOUND_EXECUTION_WITNESS", "source_verdict_unverified": row["verdict"],
            "structural_checks": {"root_labels_in_part_outputs": not missing_outputs, "literal_window": numeric},
            "findings": findings, "need_review_aid": review,
            "context_obligations": [conditions[t] for k in ["conditions", "dynamics"] for t in row[k] if t in conditions],
            "open_items": ["Accept atomic requirements and scope from every retained source clause",
                           "Bind source inputs, component instances and all 14 boundary fields",
                           "Specify root acceptance and joint resource/state/effect constraints",
                           "Provide the selected executable profiles and case-bound proof/integration evidence"]}


def audit_summaries(cases_path, index, output_dir, reviews=None, review_ledger=None):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    # Never overwrite an existing run. New directory per run preserves failures.
    if (out / "case-results.jsonl").exists(): raise InputError("Run already exists; use a new output directory")
    source_hash = file_hash(cases_path)
    needs = {r["Need"]: r for r in (reviews or [])}
    conditions = {}
    if review_ledger:
        for ref, kind, term, count, area, acceptance in review_ledger["conditions"]["values"]:
            conditions[term] = {"reference": ref, "term": term, "framework_area_to_inspect": area,
                                "acceptance_to_establish": acceptance, "status": "REVIEW_AID_NOT_A_PROOF"}
    rows = list(read_summaries(cases_path))  # Full input parse before publishing results.
    counts = {k: Counter() for k in ["verdict", "regime", "domain", "need", "conditions", "dynamics", "parts", "inputs", "deliverables", "tags"]}
    findings = Counter()
    clauses = 0
    connections = 0
    db = sqlite3.connect(out / "cases.sqlite3")
    db.execute("CREATE TABLE cases (id TEXT PRIMARY KEY, need TEXT, regime TEXT, source_verdict TEXT, status TEXT, dossier_json TEXT)")
    db.execute("CREATE VIRTUAL TABLE search USING fts5(id UNINDEXED, text)")
    with (out / "case-results.jsonl").open("w") as f:
        for row in rows:
            result = assess_row(row, source_hash, index["source_sha256"], needs, conditions)
            encoded = canonical(result)
            f.write(encoded + "\n")
            db.execute("INSERT INTO cases VALUES (?,?,?,?,?,?)", (row["id"], row["need"], row["regime"], row["verdict"], result["coverage_status"], encoded))
            db.execute("INSERT INTO search VALUES (?,?)", (row["id"], canonical(row)))
            clauses += len(result["source_clauses"])
            connections += len(row["parts"])
            findings.update({x["kind"] for x in result["findings"]})
            for k in counts:
                counts[k].update(row[k] if isinstance(row[k], list) else [row[k]])
    db.commit()
    db.close()
    summary = {"format": "fwcheck.audit.v1", "cases_sha256": source_hash, "framework_sha256": index["source_sha256"],
               "case_count": len(rows), "clause_occurrences_preserved": clauses, "part_occurrences": connections,
               "status_counts": {"CASE_FORMALIZATION_REQUIRED": len(rows)},
               "full_coverage_certificates": 0, "proved_uncovered_cases": 0,
               "framework_family_count": len(index["families"]), "framework_proof_count": len(index["proofs"]),
               "cases_with_findings": dict(findings), "source_verdict_counts": dict(counts["verdict"]),
               "distinct_vocabulary": {k: len(v) for k, v in counts.items()},
               "individual_prior_summary_reviews_attached": sum(r["id"] in {n["Example"] for n in needs.values()} for r in rows),
               "coverage_interpretation": "Undetermined: missing accepted contracts and bound proofs are not evidence of poor family coverage.",
               "case_results_sha256": file_hash(out / "case-results.jsonl")}
    write_json(out / "summary.json", summary)
    write_json(out / "vocabulary.json", {k: dict(v) for k, v in counts.items()})
    return summary
