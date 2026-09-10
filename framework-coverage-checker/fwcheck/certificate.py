import importlib.metadata
from pathlib import Path
from .io import digest, file_hash, InputError
from .construction import check_project


def versions():
    return {name: importlib.metadata.version(name) for name in ["clingo", "cvc5", "z3-solver", "jsonschema", "hypothesis", "pytest"]}


def code_hash():
    return digest({p.name: file_hash(p) for p in sorted(Path(__file__).parent.glob("*.py"))})


def decision_projection(value):
    # Solver model spelling and unconstrained model choices may differ on replay.
    # Every accepted AST, query identity, verdict and construction is retained.
    if isinstance(value, list): return [decision_projection(x) for x in value]
    if isinstance(value, dict):
        return {k: decision_projection(v) for k, v in value.items() if k not in {"model", "smt2", "term"}}
    return value


def make_certificate(project, result):
    body = {"format": "fwcheck.replay.v1", "case_sha256": digest(project), "code_sha256": code_hash(),
            "engine_versions": versions(), "result": result,
            "assurance": "Re-executable solver evidence, not an independently checked formal proof object"}
    return {**body, "sha256": digest(body)}


def replay(project, certificate, framework_index):
    payload = {k: v for k, v in certificate.items() if k != "sha256"}
    if digest(payload) != certificate.get("sha256"): raise InputError("Replay bundle integrity failure")
    if digest(project) != certificate["case_sha256"]: raise InputError("Case changed since certification")
    if code_hash() != certificate["code_sha256"]: raise InputError("Checker changed: issue a new run")
    if versions() != certificate["engine_versions"]: raise InputError("Dependencies changed: issue a new run")
    result = check_project(project, framework_index["source_sha256"], framework_index)
    if decision_projection(result) != decision_projection(certificate["result"]):
        raise InputError("Independent rerun differs from retained decisions or queries")
    return {"status": "REPLAY_MATCH", "case_id": project["id"], "construction_status": result["construction_status"],
            "coverage_status": result["coverage_status"], "assurance": certificate["assurance"]}
