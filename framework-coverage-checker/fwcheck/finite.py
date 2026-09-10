"""Finite explicit-state safety and monotone obligation closure, with engine parity.

These are model checks, not claims that a runtime implements the supplied model.
"""
import clingo
from jsonschema import Draft202012Validator
from .schema import obj, arr, NAME, TEXT
from .io import InputError
from .logic import solve_pair, conjunction


def asp_atoms(program):
    c = clingo.Control(["--models=0", "--warn=none"])
    c.add("base", [], program)
    c.ground([("base", [])])
    models = []
    with c.solve(yield_=True) as handle:
        for model in handle:
            models.append(model.symbols(shown=True))
        result = handle.get()
    if not result.exhausted or len(models) != 1:
        raise InputError("Finite deterministic relation did not produce one complete model")
    return models[0]


def check_state_model(model):
    schema = obj({"format": {"const": "fwcheck.states.v1"}, "id": NAME,
                  "states": {**arr(NAME, 1), "maxItems": 50, "uniqueItems": True},
                  "initial": {**arr(NAME, 1), "uniqueItems": True},
                  "unsafe": {**arr(NAME), "uniqueItems": True},
                  "terminal": {**arr(NAME), "uniqueItems": True},
                  "transitions": arr(obj({"from": NAME, "to": NAME})),
                  "interpretation": TEXT})
    Draft202012Validator(schema).validate(model)
    names = model["states"]
    ids = {s: n for n, s in enumerate(names)}
    mentioned = set(model["initial"] + model["unsafe"] + model["terminal"])
    mentioned |= {t[k] for t in model["transitions"] for k in ["from", "to"]}
    if not mentioned <= set(names): raise InputError("Unknown state reference")
    if any(t["from"] in model["terminal"] for t in model["transitions"]):
        raise InputError("Terminal states must have no outgoing transitions in this profile")
    edges = [(ids[t["from"]], ids[t["to"]]) for t in model["transitions"]]
    initial = [ids[x] for x in model["initial"]]
    program = "\n".join([f"initial({i})." for i in initial] + [f"edge({a},{b})." for a, b in edges] + [
        "reachable(S) :- initial(S).", "reachable(T) :- reachable(S), edge(S,T).",
        "#show reachable/1."])
    atoms = asp_atoms(program)
    reached = {a.arguments[0].number for a in atoms}
    steps = len(names) - 1
    declarations = {f"s{i}": "Int" for i in range(steps + 1)}
    # Stuttering lets a path shorter than n-1 be represented at the same bound.
    # It is used for reachability only, never as evidence of runtime transitions.
    clauses = [{"or": [{"=": ["s0", i]} for i in initial]}]
    for i in range(steps):
        clauses.append({"or": [{"=": [f"s{i}", f"s{i+1}"]}] + [
            conjunction([{"=": [f"s{i}", a]}, {"=": [f"s{i+1}", b]}]) for a, b in edges]})
    checks = []
    consistent = True
    unknown = False
    for i, state in enumerate(names):
        result = solve_pair(declarations, conjunction(clauses + [{"=": [f"s{steps}", i]}]))
        expected = "sat" if i in reached else "unsat"
        if result["status"] not in {"sat", "unsat"}: unknown = True
        if result["status"] != expected: consistent = False
        checks.append({"state": state, "asp_reachable": i in reached, "smt": result})
    unsafe = sorted(s for s in model["unsafe"] if ids[s] in reached)
    outgoing = {a for a, b in edges}
    deadlocks = sorted(names[i] for i in reached if i not in outgoing and names[i] not in model["terminal"])
    return {"format": "fwcheck.states-result.v1", "id": model["id"],
            "status": "UNKNOWN" if unknown else "ENGINE_DISAGREEMENT" if not consistent else "COUNTEREXAMPLE" if unsafe or deadlocks else "FINITE_SAFETY_PASS",
            "unsafe_reachable": unsafe, "nonterminal_deadlocks": deadlocks,
            "reachable_states": sorted(names[i] for i in reached), "complete_reachability_bound": steps,
            "checks": checks, "asp_program": program,
            "scope": "Exhaustive reachability for this explicit finite graph; safety and nonterminal deadlock only. No liveness/fairness, abstraction, implementation, or physical-effect proof."}


def derive_obligations(model):
    schema = obj({"format": {"const": "fwcheck.obligations.v1"}, "id": NAME,
                  "features": {**arr(NAME), "uniqueItems": True},
                  "selected": {**arr(NAME), "uniqueItems": True},
                  "rules": arr(obj({"id": NAME, "all_of": {**arr(NAME, 1), "uniqueItems": True}, "obligation": NAME}), 1),
                  "reviewed_rule_scope": TEXT})
    Draft202012Validator(schema).validate(model)
    features = model["features"]
    if not set(model["selected"]) <= set(features): raise InputError("Unknown selected feature")
    if len({r["id"] for r in model["rules"]}) != len(model["rules"]): raise InputError("Duplicate rule ID")
    if any(not set(r["all_of"]) <= set(features) for r in model["rules"]): raise InputError("Unknown rule feature")
    fids = {f: i for i, f in enumerate(features)}
    obligations = sorted({r["obligation"] for r in model["rules"]})
    oids = {o: i for i, o in enumerate(obligations)}
    selected = set(model["selected"])
    lines = [f"selected({fids[f]})." for f in selected]
    for n, r in enumerate(model["rules"]):
        body = ", ".join(f"selected({fids[f]})" for f in r["all_of"])
        lines.append(f"triggered({n}) :- {body}.")
        lines.append(f"obligation({oids[r['obligation']]}) :- triggered({n}).")
    lines += ["#show obligation/1.", "#show triggered/1."]
    program = "\n".join(lines)
    atoms = asp_atoms(program)
    derived = {obligations[a.arguments[0].number] for a in atoms if a.name == "obligation"}
    triggered = [model["rules"][a.arguments[0].number]["id"] for a in atoms if a.name == "triggered"]
    declarations = {f: "Bool" for f in features}
    assignments = [{"=": [f, f in selected]} for f in features]
    checks = []
    status = "FINITE_RULE_PARITY_PASS"
    for obligation in obligations:
        condition = {"or": [conjunction(r["all_of"]) for r in model["rules"] if r["obligation"] == obligation]}
        query = conjunction(assignments + [condition])
        result = solve_pair(declarations, query)
        if result["status"] not in {"sat", "unsat"}: status = "UNKNOWN"
        elif (result["status"] == "sat") != (obligation in derived): status = "ENGINE_DISAGREEMENT"
        checks.append({"obligation": obligation, "smt": result})
    return {"format": "fwcheck.obligation-result.v1", "status": status,
            "derived": sorted(derived), "triggered_rules": sorted(triggered), "checks": checks,
            "asp_program": program, "reviewed_rule_scope": model["reviewed_rule_scope"],
            "scope": "Parity for the supplied finite rule table only; an omitted world requirement remains omitted in every engine."}
