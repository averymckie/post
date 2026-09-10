"""clingo enumerates closed acyclic constructions; SMT independently checks them.

Ports have accepted instance bindings in a shared symbol namespace. No automatic
name-based semantic matching, arbitrary adapters, or purported universal absence.
"""
import time
import clingo
from .io import InputError, digest
from .logic import conjunction, implication, solve_pair
from .schema import validate_project, BOUNDARY_FIELDS


def inventory_hash(p):
    return digest({"source_sha256": p["source_sha256"], "source_clauses": p["source_clauses"],
                   "requirements": p["requirements"]})


def prepare(p):
    outputs, owners, inputs = {}, {}, {}
    for source in p["sources"]:
        key = f"source:{source['id']}"
        outputs[key], owners[key] = source, None
    for c in p["components"]:
        for port in c["outputs"]:
            key = f"{c['id']}:{port['id']}"
            outputs[key], owners[key] = port, c["id"]
        for port in c["inputs"]:
            inputs[f"{c['id']}:{port['id']}"] = (c["id"], port)
    return outputs, owners, inputs


def binding_diagnostics(p):
    outputs, owners, inputs = prepare(p)
    findings = []
    for inp, (consumer, port) in inputs.items():
        eligible = {k: v for k, v in outputs.items() if owners[k] != consumer}
        exact = [k for k, v in eligible.items() if v["envelope"] == port["envelope"]]
        if exact:
            continue
        near = []
        for out, value in eligible.items():
            a, b = value["envelope"], port["envelope"]
            if a["schema"] == b["schema"] or a["meaning"] == b["meaning"]:
                near.append({"output": out, "mismatched_fields": [k for k in BOUNDARY_FIELDS if a[k] != b[k]]})
        findings.append({"input": inp, "kind": "NO_EXACT_SUPPLIER_IN_DECLARED_CATALOGUE",
                         "near_outputs": near, "adapter_state": "NO_QUALIFIED_NONIDENTITY_ADAPTER_ADMITTED"})
    return findings


def asp_program(p):
    outputs, owners, inputs = prepare(p)
    components = [c["id"] for c in p["components"]]
    roots = [r for r in p["requirements"] if r["envelope"] is not None]
    if not roots:
        raise InputError("At least one root deliverable is required")
    cids = {v: i for i, v in enumerate(components)}
    oids = {v: i for i, v in enumerate(outputs)}
    iids = {v: i for i, v in enumerate(inputs)}
    lines = []
    for c, i in cids.items(): lines.append(f"component({i}).")
    for out, i in oids.items():
        lines.append(f"output({i}).")
        if owners[out] is not None: lines.append(f"owner({i},{cids[owners[out]]}).")
    for inp, (owner, port) in inputs.items():
        j = iids[inp]
        lines.append(f"input({cids[owner]},{j}).")
        for out, value in outputs.items():
            if value["envelope"] == port["envelope"] and owners[out] != owner:
                lines.append(f"compatible({j},{oids[out]}).")
    for j, root in enumerate(roots):
        lines.append(f"root({j}).")
        for out, value in outputs.items():
            if value["envelope"] == root["envelope"]:
                lines.append(f"root_candidate({j},{oids[out]}).")
    lines.extend([
        "1 { deliver(R,O) : root_candidate(R,O) } 1 :- root(R).",
        "selected(C) :- deliver(R,O), owner(O,C).",
        "1 { bind(I,O) : compatible(I,O) } 1 :- selected(C), input(C,I).",
        "selected(P) :- bind(I,O), owner(O,P).",
        "depends(C,P) :- bind(I,O), input(C,I), owner(O,P).",
        "reaches(C,P) :- depends(C,P).",
        "reaches(C,Q) :- reaches(C,P), depends(P,Q).",
        ":- reaches(C,C).",
        f":- #count {{ C : selected(C) }} > {p['limits']['max_components']}.",
        "#show selected/1.", "#show bind/2.", "#show deliver/2."])
    return "\n".join(lines), (components, list(outputs), list(inputs), roots)


def decode(atoms, names):
    components, outputs, inputs, roots = names
    w = {"selected": [], "bindings": {}, "deliveries": {}}
    for a in atoms:
        ints = [x.number for x in a.arguments]
        if a.name == "selected": w["selected"].append(components[ints[0]])
        if a.name == "bind": w["bindings"][inputs[ints[0]]] = outputs[ints[1]]
        if a.name == "deliver": w["deliveries"][roots[ints[0]]["id"]] = outputs[ints[1]]
    w["selected"].sort()
    return w


def validate_witness(p, witness):
    """Replay every premise, including graph constraints, without trusting clingo."""
    validate_project(p)
    outputs, owners, inputs = prepare(p)
    cs = {c["id"]: c for c in p["components"]}
    selected = witness["selected"]
    checks, gaps = [], []
    if len(selected) != len(set(selected)) or any(c not in cs for c in selected):
        return {"status": "INVALID_WITNESS", "gaps": ["Unknown or duplicate component"]}
    if len(selected) > p["limits"]["max_components"]:
        return {"status": "INVALID_WITNESS", "gaps": ["Component bound exceeded"]}
    expected_inputs = {i for i, (owner, _) in inputs.items() if owner in selected}
    roots = {r["id"]: r for r in p["requirements"] if r["envelope"] is not None}
    if set(witness["bindings"]) != expected_inputs or set(witness["deliveries"]) != set(roots):
        return {"status": "INVALID_WITNESS", "gaps": ["Missing or extra input/root binding"]}
    ranks = {"rank_" + c: "Int" for c in selected}
    graph_constraints = []
    for c in selected:
        graph_constraints.extend([{">=": ["rank_" + c, 0]}, {"<": ["rank_" + c, len(selected)]}])
    dependencies = {c: set() for c in selected}
    for inp, out in witness["bindings"].items():
        if out not in outputs or (owners[out] is not None and owners[out] not in selected):
            return {"status": "INVALID_WITNESS", "gaps": ["Dangling supplier"]}
        consumer, port = inputs[inp]
        if outputs[out]["envelope"] != port["envelope"]:
            differences = [k for k in BOUNDARY_FIELDS if outputs[out]["envelope"][k] != port["envelope"][k]]
            return {"status": "ADAPTER_GAP", "gaps": [{"input": inp, "fields": differences}]}
        if owners[out] is not None:
            dependencies[consumer].add(owners[out])
            graph_constraints.append({"<": ["rank_" + owners[out], "rank_" + consumer]})
    root_owners = set()
    for req, out in witness["deliveries"].items():
        if out not in outputs or outputs[out]["envelope"] != roots[req]["envelope"]:
            return {"status": "INVALID_WITNESS", "gaps": ["Invalid root output"]}
        if owners[out] is not None:
            if owners[out] not in selected:
                return {"status": "INVALID_WITNESS", "gaps": ["Unselected root producer"]}
            root_owners.add(owners[out])
    used = set(root_owners)
    while True:
        expanded = used | {d for c in used for d in dependencies[c]}
        if expanded == used: break
        used = expanded
    if used != set(selected):
        return {"status": "INVALID_WITNESS", "gaps": ["Extraneous components cannot supply unrelated guarantees"]}
    graph_result = solve_pair(ranks, conjunction(graph_constraints), p["limits"]["timeout_ms"])
    checks.append({"obligation": "closed_acyclic_graph", "result": graph_result})
    if graph_result["status"] != "sat":
        return {"status": "INVALID_WITNESS" if graph_result["status"] == "unsat" else "UNKNOWN",
                "checks": checks, "gaps": ["Acyclicity not established"]}
    variables, timeout = p["variables"], p["limits"]["timeout_ms"]
    base = conjunction([p["context"]] + [s["guarantee"] for s in p["sources"]])
    base_check = solve_pair(variables, base, timeout)
    checks.append({"obligation": "admitted_input_nonvacuity", "result": base_check})
    if base_check["status"] != "sat":
        return {"status": "VACUOUS" if base_check["status"] == "unsat" else "UNKNOWN", "checks": checks}
    remaining = set(selected)
    established = set()
    while remaining:
        ready = sorted(c for c in remaining if dependencies[c] <= established)
        if not ready: return {"status": "INVALID_WITNESS", "checks": checks}
        for cid in ready:
            component = cs[cid]
            input_guarantees = [outputs[witness["bindings"][f"{cid}:{port['id']}"]]["guarantee"] for port in component["inputs"]]
            antecedent = conjunction([base] + input_guarantees)
            consequent = conjunction([component["requires"]] + [port["requires"] for port in component["inputs"]])
            result = implication(variables, antecedent, consequent, timeout)
            checks.append({"obligation": f"{cid}.input_contract", "result": result})
            if result["status"] != "PROVED":
                gaps.append({"kind": "CONTRACT_MISMATCH" if result["status"] == "COUNTEREXAMPLE" else result["status"],
                             "component": cid})
            established.add(cid)
            remaining.remove(cid)
    all_guarantees = [port["guarantee"] for cid in selected for port in cs[cid]["outputs"]]
    aggregate = conjunction([base] + all_guarantees)
    joint = solve_pair(variables, aggregate, timeout)
    checks.append({"obligation": "joint_contract_nonvacuity", "result": joint})
    if joint["status"] != "sat":
        gaps.append({"kind": "INCONSISTENT_CONTRACTS" if joint["status"] == "unsat" else "UNKNOWN"})
    for requirement in p["requirements"]:
        # A root's own product must satisfy its acceptance clause; unrelated output
        # guarantees cannot substitute for that product's quality contract.
        if requirement["envelope"] is not None:
            out = witness["deliveries"][requirement["id"]]
            antecedent = conjunction([base, outputs[out]["guarantee"]])
        else:
            antecedent = aggregate
        result = implication(variables, antecedent, requirement["predicate"], timeout)
        checks.append({"obligation": requirement["id"], "source_clause": requirement["source_clause"], "result": result})
        if result["status"] != "PROVED":
            gaps.append({"kind": "REQUIREMENT_UNPROVED", "requirement": requirement["id"], "state": result["status"]})
    unknown = any(c["result"]["status"] in {"UNKNOWN", "ENGINE_DISAGREEMENT"} for c in checks)
    status = "UNKNOWN" if unknown else "CONSTRUCTION_FAILED" if gaps else "MODEL_RECONSTRUCTED"
    return {"status": status, "checks": checks, "gaps": gaps,
            "assurance": "Conditional on accepted component contracts; component totality and actual implementation are unverified"}


def check_project(p, framework_hash=None, proof_index=None):
    validate_project(p)
    if framework_hash is not None and p["framework_sha256"] != framework_hash:
        raise InputError("Framework hash does not match the supplied frozen baseline")
    if p["semantic_review"]["inventory_sha256"] != inventory_hash(p):
        raise InputError("Changed requirement inventory invalidates semantic review")
    unsupported = sorted(set(p["grammar"]) - {"Seq", "Join", "ForkJoin"})
    base = {"format": "fwcheck.result.v1", "case_id": p["id"], "case_sha256": digest(p),
            "framework_sha256": p["framework_sha256"], "bounds": p["limits"],
            "coverage_status": "UNESTABLISHED", "evidence_state": "INTEGRATION_UNVERIFIED",
            "semantic_review": p["semantic_review"]["status"],
            "scope": "Finite static DAG under explicitly supplied contract axioms; no runtime or temporal assurance"}
    if unsupported:
        return {**base, "construction_status": "UNSUPPORTED_ENCODING", "unsupported_forms": unsupported}
    if proof_index is not None:
        known_families = set(proof_index["families"])
        known_proofs = set(proof_index["proofs"])
        for c in p["components"]:
            if c["family"] not in known_families or not set(c["proof_refs"]) <= known_proofs:
                raise InputError(f"Unknown framework/proof reference on {c['id']}")
    program, names = asp_program(p)
    control = clingo.Control(["--models=0", "--warn=none", "--seed=0"])
    control.add("base", [], program)
    control.ground([("base", [])])
    candidates, winner, unknown_seen = [], None, False
    complete = False
    stop_reason = None
    deadline = time.monotonic() + p["limits"]["search_seconds"]
    with control.solve(yield_=True, async_=True) as handle:
        while True:
            time_left = deadline - time.monotonic()
            if time_left <= 0 or not handle.wait(max(0, time_left)):
                stop_reason = "TIMEOUT"
                handle.cancel()
                break
            model = handle.model()
            if model is None:
                final = handle.get()
                complete = bool(final.exhausted)
                if not complete: stop_reason = "SEARCH_UNKNOWN"
                break
            witness = decode(model.symbols(shown=True), names)
            validation = validate_witness(p, witness)
            candidates.append({"witness": witness, "validation": validation})
            if validation["status"] == "MODEL_RECONSTRUCTED":
                winner = candidates[-1]
                handle.cancel()
                break
            if validation["status"] == "UNKNOWN": unknown_seen = True
            if len(candidates) >= p["limits"]["max_candidates"]:
                stop_reason = "CANDIDATE_LIMIT"
                handle.cancel()
                break
            handle.resume()
    if winner:
        state = "MODEL_RECONSTRUCTED"
    elif not complete or unknown_seen:
        state = "SEARCH_INCOMPLETE"
    else:
        state = "NO_CONSTRUCTION_IN_DECLARED_CATALOGUE_AND_BOUNDS"
    proof_gaps = []
    if winner:
        selected = set(winner["witness"]["selected"])
        for c in p["components"]:
            if c["id"] in selected:
                proof_gaps.append({"component": c["id"], "family": c["family"], "proof_refs": c["proof_refs"],
                                   "kind": "COMPONENT_IMPLEMENTATION_EVIDENCE_MISSING",
                                   "external_effect": c["external_effect"]})
    return {**base, "construction_status": state, "search_exhausted": complete,
            "search_stop_reason": stop_reason, "asp_program": program,
            "binding_diagnostics": binding_diagnostics(p),
            "candidate_count": len(candidates), "candidates": candidates, "witness": winner,
            "proof_gaps": proof_gaps,
            "coverage_status": "PROOF_GAP" if winner else "UNESTABLISHED",
            "limitation": "No result here asserts absence from the full framework. Proof references alone never qualify a component."}
