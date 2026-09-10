from jsonschema import Draft202012Validator
from .io import InputError
from .logic import validate_formula

BOUNDARY_FIELDS = ["schema", "meaning", "identity", "time", "basis", "coverage", "authority", "state",
                   "effects", "numeric", "resources", "evidence", "change", "exceptions"]
NAME = {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_.-]{0,119}$"}
TEXT = {"type": "string", "minLength": 1}
HASH = {"type": "string", "pattern": "^[a-f0-9]{64}$"}


def obj(props, required=None):
    return {"type": "object", "properties": props, "required": list(props) if required is None else required,
            "additionalProperties": False}


def arr(item, minimum=0):
    return {"type": "array", "items": item, "minItems": minimum}


ENVELOPE = obj({k: TEXT for k in BOUNDARY_FIELDS})
OUTPUT = obj({"id": NAME, "envelope": ENVELOPE, "guarantee": {}})
INPUT = obj({"id": NAME, "envelope": ENVELOPE, "requires": {}})
COMPONENT = obj({"id": NAME, "family": {"type": "string", "pattern": "^F[0-9]{2}$"},
                 "proof_refs": arr({"type": "string", "pattern": "^P[0-9]+$"}),
                 "inputs": arr(INPUT, 1), "outputs": arr(OUTPUT, 1), "requires": {},
                 "profile_origin": {"enum": ["ANALYST_PROPOSED", "ACCEPTED_CONTRACT"]},
                 "external_effect": {"type": "boolean"}})
REQUIREMENT = obj({"id": NAME, "source_clause": NAME, "predicate": {},
                   "envelope": {"anyOf": [ENVELOPE, {"type": "null"}]}},
                  ["id", "source_clause", "predicate", "envelope"])
PROJECT_SCHEMA = obj({
    "format": {"const": "fwcheck.case.v1"}, "id": NAME, "source_sha256": HASH, "framework_sha256": HASH,
    "variables": {"type": "object", "propertyNames": NAME, "additionalProperties": {"enum": ["Bool", "Int", "Real"]}},
    "context": {},
    "source_clauses": arr(obj({"id": NAME, "text": TEXT}), 1),
    "semantic_review": obj({"status": {"enum": ["DRAFT", "ACCEPTED"]}, "reviewer": TEXT,
                            "inventory_sha256": HASH}),
    "sources": arr(OUTPUT, 1), "components": arr(COMPONENT), "requirements": arr(REQUIREMENT, 1),
    "grammar": arr({"enum": ["Seq", "Join", "ForkJoin", "Choice", "Iterate", "MapReduce", "Await", "StreamWindow",
                                 "Atomic", "Saga", "HumanInput", "Feedback", "Substitute", "Revise"]}, 1),
    "acceptance_scope": {"enum": ["FORMAL_MODEL", "DELIVERED_SYSTEM"]},
    "limits": obj({"max_components": {"type": "integer", "minimum": 1, "maximum": 100},
                   "max_candidates": {"type": "integer", "minimum": 1, "maximum": 10000},
                   "timeout_ms": {"type": "integer", "minimum": 1, "maximum": 30000},
                   "search_seconds": {"type": "integer", "minimum": 1, "maximum": 60}}),
})
PROJECT_SCHEMA["$schema"] = "https://json-schema.org/draft/2020-12/schema"


def validate_project(project):
    Draft202012Validator.check_schema(PROJECT_SCHEMA)
    Draft202012Validator(PROJECT_SCHEMA).validate(project)
    groups = [project["sources"], project["components"], project["requirements"], project["source_clauses"]]
    for group in groups:
        ids = [x["id"] for x in group]
        if len(set(ids)) != len(ids):
            raise InputError("Duplicate entity/requirement/clause ID")
    if set(x["id"] for x in project["sources"]) & set(x["id"] for x in project["components"]):
        raise InputError("Source and component IDs overlap")
    vars_ = project["variables"]
    validate_formula(project["context"], vars_)
    for source in project["sources"]:
        validate_formula(source["guarantee"], vars_)
    for c in project["components"]:
        names = [p["id"] for p in c["inputs"] + c["outputs"]]
        if len(names) != len(set(names)):
            raise InputError(f"Duplicate port on {c['id']}")
        validate_formula(c["requires"], vars_)
        for p in c["inputs"]:
            validate_formula(p["requires"], vars_)
        for p in c["outputs"]:
            validate_formula(p["guarantee"], vars_)
    for req in project["requirements"]:
        validate_formula(req["predicate"], vars_)
    known = {x["id"] for x in project["source_clauses"]}
    used = {x["source_clause"] for x in project["requirements"]}
    if used != known:
        raise InputError(f"Requirement inventory mismatch: missing={sorted(known-used)}, unknown={sorted(used-known)}")
