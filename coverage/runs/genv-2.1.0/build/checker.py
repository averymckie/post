#!/usr/bin/env python3
"""Independent checker for generated use cases.

    python3 checker.py --dictionary dictionary.json --cases cases.jsonl --report checker_report.json
    python3 checker.py --dictionary dictionary.json --broken --report broken_report.json

Every verdict is re-derived from dictionary.json and the emitted record alone.
The record's own `validation_status_and_evidence` block is never used as
evidence: it is read only so that a disagreement between what the generator
claimed and what this program finds can itself be reported.

Mechanical validity and semantic judgment are kept apart.  A check is `pass`,
`fail`, or `unavailable`; `unavailable` means this program has no way to decide
it (a qualitative acceptance condition, a constraint template marked not
machine-checkable), and is never counted as a pass.
"""
import argparse, hashlib, json, os, sys
from collections import defaultdict, Counter

CHECKER_VERSION = "checker.py/2.0.0"

REQUIRED_FIELDS = [
    "case_id", "generation_version", "primary_domain", "regime", "beneficiary",
    "need_and_context", "required_deliverables", "concrete_inputs",
    "component_relationships", "atomic_requirements_with_stable_ids",
    "global_constraints", "acceptance_conditions", "assumptions_and_provenance",
    "validation_status_and_evidence", "diversity_signature", "seed_or_replay_reference",
]
EXTRA_FIELDS = ["components", "entities", "situation", "dictionary_version"]


def h(*parts):
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]


class Report:
    def __init__(self, case_id):
        self.case_id = case_id
        self.checks = {}
        self.violations = []

    def ok(self, code):
        self.checks.setdefault(code, "pass")

    def bad(self, code, detail):
        self.checks[code] = "fail"
        self.violations.append({"code": code, "detail": detail})

    def unavailable(self, code, detail):
        if self.checks.get(code) != "fail":
            self.checks[code] = "unavailable"
        self.violations.append({"code": code, "detail": detail, "severity": "unavailable"})


def check_case(D, case):
    ing = D["ingredients"]
    units = D["units"]
    rk = D["relationship_kinds"]
    ct = D["constraint_templates"]
    rt = D["requirement_templates"]
    bounds = D["generation_bounds"]
    comp_rules = D["compatibility_rules"]
    R = Report(case.get("case_id", "<no id>"))

    # ---- 1. structural completeness -------------------------------------
    missing = [f for f in REQUIRED_FIELDS if f not in case]
    empty = [f for f in ("required_deliverables", "component_relationships",
                         "atomic_requirements_with_stable_ids", "global_constraints",
                         "acceptance_conditions") if f in case and not case[f]]
    missing += [f for f in EXTRA_FIELDS if f not in case]
    if missing or empty:
        R.bad("STRUCTURE", "missing %s; empty %s" % (missing, empty))
        return R
    R.ok("STRUCTURE")

    regime = case["regime"]
    domain = case["primary_domain"]
    sits = set(case["situation"]["tags"])
    comps = {c["component_id"]: c for c in case["components"]}
    rels = case["component_relationships"]
    pools = {p["pool_id"]: p for p in case["situation"]["resource_pools"]}

    if regime not in D["regimes"]:
        R.bad("VOCAB_RESOLVE", "unknown regime %s" % regime)
    if domain not in D["domains"]:
        R.bad("VOCAB_RESOLVE", "unknown primary_domain %s" % domain)
    for s in sits:
        if s not in D["situations"]:
            R.bad("VOCAB_RESOLVE", "unknown situation tag %s" % s)

    # ---- 2. every referenced ingredient resolves ------------------------
    uses = []          # (ingredient_id, regime_it_is_used_in, where)
    def use(iid, r, where):
        if iid not in ing:
            R.bad("VOCAB_RESOLVE", "unknown ingredient %s at %s" % (iid, where))
        else:
            uses.append((iid, r, where))

    use(case["beneficiary"]["ingredient"], regime, "beneficiary")
    use(case["need_and_context"]["need"], regime, "need")
    use(case["situation"]["scale"], regime, "situation.scale")
    for c in case["situation"]["conditions"]:
        use(c, regime, "situation.conditions")
    for d in case["situation"]["dynamics"]:
        use(d, regime, "situation.dynamics")
    for cid, c in sorted(comps.items()):
        use(c["product"], c["regime"], "%s.product" % cid)
        use(c["activity"], c["regime"], "%s.activity" % cid)
        if c["regime"] not in D["regimes"]:
            R.bad("VOCAB_RESOLVE", "unknown component regime %s at %s" % (c["regime"], cid))
    for i in case["concrete_inputs"]:
        owner = i["used_by"][0] if i.get("used_by") else None
        r = comps[owner]["regime"] if owner in comps else regime
        use(i["ingredient"], r, "input %s" % i["input_id"])
    for a in case["acceptance_conditions"]:
        use(a["ingredient"], regime, "acceptance %s" % a["ac_id"])
    for q in case["atomic_requirements_with_stable_ids"]:
        if q["ingredient"] not in ing:
            R.bad("VOCAB_RESOLVE", "requirement %s references unknown ingredient %s"
                  % (q["req_id"], q["ingredient"]))
        if q["template"] not in rt:
            R.bad("VOCAB_RESOLVE", "requirement %s references unknown template %s"
                  % (q["req_id"], q["template"]))
    for g in case["global_constraints"]:
        if g["template"] not in ct:
            R.bad("VOCAB_RESOLVE", "global constraint %s references unknown template %s"
                  % (g["gc_id"], g["template"]))
    for r in rels:
        if r["kind"] not in rk:
            R.bad("VOCAB_RESOLVE", "unknown relationship kind %s at %s" % (r["kind"], r["rel_id"]))
    R.ok("VOCAB_RESOLVE")

    # ---- 3. regime and situation admissibility --------------------------
    for iid, r, where in uses:
        if r not in ing[iid]["regimes"]:
            R.bad("REGIME_ADMISSIBLE", "%s (%s) does not declare regime %s at %s"
                  % (iid, ing[iid]["axis"], r, where))
        if not (set(ing[iid]["situations"]) & sits):
            R.bad("SITUATION_ADMISSIBLE", "%s declares none of the case situation tags at %s"
                  % (iid, where))
    R.ok("REGIME_ADMISSIBLE")
    R.ok("SITUATION_ADMISSIBLE")

    # ---- 4. domain gate --------------------------------------------------
    need = case["need_and_context"]["need"]
    if need in ing and domain not in ing[need]["domains"]:
        R.bad("DOMAIN_GATE", "need %s does not admit primary_domain %s" % (need, domain))
    for cid, c in sorted(comps.items()):
        p = c["product"]
        if p in ing and domain not in ing[p]["domains"]:
            R.bad("DOMAIN_GATE", "product %s at %s does not admit primary_domain %s"
                  % (p, cid, domain))
    R.ok("DOMAIN_GATE")

    # ---- 5. beneficiary band --------------------------------------------
    b = case["beneficiary"]["ingredient"]
    if b in ing and need in ing:
        if ing[b]["scale_band"] not in ing[need]["beneficiary_bands"]:
            R.bad("BENEFICIARY_BAND", "beneficiary band %s not among the need's bands %s"
                  % (ing[b]["scale_band"], ing[need]["beneficiary_bands"]))
        if case["beneficiary"]["scale_band"] != ing[b]["scale_band"]:
            R.bad("BENEFICIARY_BAND", "declared scale_band disagrees with the ingredient")
    R.ok("BENEFICIARY_BAND")

    # ---- 6. relationship integrity --------------------------------------
    seen_rel = set()
    seen_trip = set()
    inbound_forms = defaultdict(set)
    for r in rels:
        if r["rel_id"] in seen_rel:
            R.bad("REL_INTEGRITY", "duplicate rel_id %s" % r["rel_id"])
        seen_rel.add(r["rel_id"])
        for end in ("from", "to"):
            if r[end] not in comps:
                R.bad("REL_INTEGRITY", "%s endpoint %s is not a component" % (r["rel_id"], r[end]))
        if r["from"] == r["to"]:
            R.bad("REL_INTEGRITY", "%s connects a component to itself" % r["rel_id"])
        trip = (r["kind"], r["from"], r["to"])
        if trip in seen_trip:
            R.bad("REL_INTEGRITY", "%s repeats %s between the same ordered pair of parts"
                  % (r["rel_id"], r["kind"]))
        seen_trip.add(trip)
        t = r.get("transfers") or {}
        if not t.get("what"):
            R.bad("REL_INTEGRITY", "%s does not say what it transfers, enables, changes or shares"
                  % r["rel_id"])
        if t.get("ingredient") and t["ingredient"] not in ing:
            R.bad("REL_INTEGRITY", "%s transfers an unknown ingredient %s"
                  % (r["rel_id"], t["ingredient"]))
        k = r["kind"]
        if k == "RK-INPUT":
            q = t.get("quantity")
            if not q:
                R.bad("REL_INTEGRITY", "%s transfers no quantity" % r["rel_id"])
            else:
                u = q.get("unit"); ru = t.get("receiving_unit")
                if u not in units or ru not in units:
                    R.bad("UNITS_DECLARED", "%s uses an undeclared unit (%s -> %s)"
                          % (r["rel_id"], u, ru))
                else:
                    if units[u]["dimension"] != units[ru]["dimension"]:
                        R.bad("REL_UNIT_DIMENSION", "%s transfers %s (%s) into %s (%s)"
                              % (r["rel_id"], u, units[u]["dimension"], ru, units[ru]["dimension"]))
                    if t.get("expects_dimension") != units[ru]["dimension"]:
                        R.bad("REL_UNIT_DIMENSION", "%s declares expects_dimension %s but the "
                              "receiving unit is %s" % (r["rel_id"], t.get("expects_dimension"),
                                                        units[ru]["dimension"]))
                    conv = t.get("conversion")
                    if u != ru and not conv:
                        R.bad("REL_UNIT_DIMENSION", "%s changes unit without a conversion" % r["rel_id"])
                    if conv:
                        want = units[conv["from_unit"]]["factor_to_base"] / \
                            units[conv["to_unit"]]["factor_to_base"]
                        if abs(conv["factor"] - want) > 1e-9 * max(1.0, abs(want)):
                            R.bad("REL_UNIT_DIMENSION", "%s conversion factor %s should be %s"
                                  % (r["rel_id"], conv["factor"], want))
                        got = q["value"] * want
                        if abs(conv["converted_value"] - got) > 1e-3 * max(1.0, abs(got)):
                            R.bad("REL_UNIT_DIMENSION", "%s converted value %s should be %s"
                                  % (r["rel_id"], conv["converted_value"], got))
            if t.get("form"):
                inbound_forms[r["to"]].add(t["form"])
        elif k == "RK-COORD":
            if not r.get("joint_outcome"):
                R.bad("REL_JOINT_OUTCOME", "%s names no joint outcome" % r["rel_id"])
        elif k == "RK-SHARE":
            so = r.get("shared_object") or {}
            if so.get("kind") == "resource_pool":
                if so.get("ref") not in pools:
                    R.bad("REL_SHARED_OBJECT", "%s shares unknown pool %s" % (r["rel_id"], so.get("ref")))
            elif so.get("kind") == "entity":
                if so.get("ref") not in {e["entity_id"] for e in case["entities"]}:
                    R.bad("REL_SHARED_OBJECT", "%s shares unknown entity %s" % (r["rel_id"], so.get("ref")))
            else:
                R.bad("REL_SHARED_OBJECT", "%s shares neither a pool nor an entity" % r["rel_id"])
        elif k == "RK-COND":
            if not r.get("predicate") or not r.get("else_branch"):
                R.bad("REL_PREDICATE", "%s has no predicate or no else branch" % r["rel_id"])
        elif k == "RK-TIME":
            sb = r.get("staleness_bound") or {}
            if not r.get("cadence") or sb.get("unit") not in units:
                R.bad("REL_STALENESS", "%s has no cadence or no declared staleness bound" % r["rel_id"])
        elif k == "RK-FEEDBACK":
            cb = r.get("cycle_bound")
            if not isinstance(cb, int) or cb < 1 or cb > bounds["max_feedback_cycles"]:
                R.bad("REL_CYCLE_BOUND", "%s cycle bound %s is outside 1..%d"
                      % (r["rel_id"], cb, bounds["max_feedback_cycles"]))
            if not r.get("stop_criterion"):
                R.bad("REL_STOP_CRITERION", "%s states no stopping criterion" % r["rel_id"])
        elif k == "RK-DELEGATE":
            if not r.get("scope") or r.get("expiry_day") is None:
                R.bad("REL_SCOPE_EXPIRY", "%s has no scope or no expiry" % r["rel_id"])
            elif not (0 < r["expiry_day"] <= case["situation"]["window_days"]):
                R.bad("REL_SCOPE_EXPIRY", "%s expiry day %s falls outside the case window"
                      % (r["rel_id"], r["expiry_day"]))
            auth_kinds = {ing[c]["kind"] for c in case["situation"]["conditions"] if c in ing}
            if "authority" not in auth_kinds:
                R.bad("REL_AUTHORITY_PRESENT", "%s delegates without any authority condition"
                      % r["rel_id"])
        elif k == "RK-CONSTRAIN":
            lim = r.get("limit") or {}
            if lim.get("unit") not in units:
                R.bad("REL_LIMIT_UNIT", "%s publishes a limit without a declared unit" % r["rel_id"])
            if not r.get("edge_behaviour"):
                R.bad("REL_EDGE_BEHAVIOUR", "%s states no behaviour at the limit" % r["rel_id"])
        elif k == "RK-EMIT":
            src = comps.get(r["from"], {}); dst = comps.get(r["to"], {})
            if not ing.get(src.get("product"), {}).get("generator"):
                R.bad("REL_GENERATOR_FORM", "%s emits from a non-generator product" % r["rel_id"])
            if ing.get(dst.get("product"), {}).get("generator"):
                R.bad("REL_EMITTED_CONCRETE", "%s emits another generator rather than a concrete product"
                      % r["rel_id"])
        elif k == "RK-EMBED":
            scope_reqs = [q for q in case["atomic_requirements_with_stable_ids"]
                          if q["scope"] == r["rel_id"] and q["template"] == "RT-INHERIT"]
            if not scope_reqs:
                R.bad("REL_INHERIT_ACCEPTANCE", "%s embeds without an inherited-acceptance requirement"
                      % r["rel_id"])
    R.ok("REL_INTEGRITY"); R.ok("UNITS_DECLARED"); R.ok("REL_UNIT_DIMENSION")
    R.ok("REL_JOINT_OUTCOME"); R.ok("REL_SHARED_OBJECT"); R.ok("REL_PREDICATE")
    R.ok("REL_STALENESS"); R.ok("REL_CYCLE_BOUND"); R.ok("REL_STOP_CRITERION")
    R.ok("REL_SCOPE_EXPIRY"); R.ok("REL_AUTHORITY_PRESENT"); R.ok("REL_LIMIT_UNIT")
    R.ok("REL_EDGE_BEHAVIOUR"); R.ok("REL_GENERATOR_FORM"); R.ok("REL_EMITTED_CONCRETE")
    R.ok("REL_INHERIT_ACCEPTANCE")

    # ---- 7. acyclicity and depth ----------------------------------------
    adj = defaultdict(set)
    for r in rels:
        if "PRECEDENCE" in rk.get(r["kind"], {}).get("checks", []):
            adj[r["from"]].add(r["to"])
    colour = {}
    cyc = []

    def dfs(n):
        colour[n] = 1
        for m in sorted(adj[n]):
            if colour.get(m) == 1:
                cyc.append((n, m))
            elif colour.get(m) is None:
                dfs(m)
        colour[n] = 2

    for n in sorted(comps):
        if colour.get(n) is None:
            dfs(n)
    if cyc:
        R.bad("ACYCLIC", "precedence cycle through %s" % cyc[:3])
    else:
        R.ok("ACYCLIC")
    if max(c["depth"] for c in comps.values()) > bounds["max_depth"]:
        R.bad("DEPTH", "composition depth exceeds %d" % bounds["max_depth"])
    else:
        R.ok("DEPTH")
    if not (bounds["min_components"] <= len(comps) <= bounds["max_components"]):
        R.bad("DEPTH", "component count %d outside %d..%d"
              % (len(comps), bounds["min_components"], bounds["max_components"]))

    # ---- 8. prerequisite closure ----------------------------------------
    inputs_by_comp = defaultdict(set)
    for i in case["concrete_inputs"]:
        for cid in i.get("used_by", []):
            inputs_by_comp[cid].add(i["form"])
    assumption_text = " ".join(case["assumptions_and_provenance"]["assumptions"])
    for cid, c in sorted(comps.items()):
        act = ing.get(c["activity"], {})
        declared = set(c.get("prerequisites", []))
        if set(act.get("prerequisites", [])) - declared:
            R.bad("PREREQ_CLOSURE", "%s does not carry all prerequisites of %s"
                  % (cid, c["activity"]))
        wants = {t.split(":", 1)[1] for t in ing.get(c["product"], {}).get("prerequisites", [])
                 if t.startswith("needs_form:")}
        yields = {r.split(":", 1)[1] for r in act.get("results", []) if r.startswith("yields_form:")}
        if c.get("activity_form_match") is not None:
            if bool(yields & wants) != bool(c["activity_form_match"]):
                R.bad("ACTIVITY_PRODUCT_FIT", "%s records activity_form_match=%s, the dictionary "
                      "gives %s (activity yields %s, product needs %s)"
                      % (cid, c["activity_form_match"], bool(yields & wants),
                         sorted(yields), sorted(wants)))
        for t in sorted(declared):
            if t.startswith("needs_form:"):
                form = t.split(":", 1)[1]
                if form in inputs_by_comp[cid] or form in inbound_forms[cid]:
                    continue
                if form in (c.get("assumed_forms") or []):
                    continue
                R.bad("PREREQ_CLOSURE", "%s needs form %s and has neither an input, an inbound "
                                        "transfer, nor a recorded assumption" % (cid, form))
            elif t.startswith("needs_capacity:"):
                kind = t.split(":", 1)[1]
                used = [ru for ru in c.get("resource_use", [])
                        if pools.get(ru["pool"], {}).get("resource_kind") == kind]
                if used:
                    continue
                if ("Capacity of kind %s is assumed available" % kind) in assumption_text:
                    continue
                R.bad("PREREQ_CLOSURE", "%s needs capacity %s with neither an allocation nor a "
                                        "recorded assumption" % (cid, kind))
    R.ok("PREREQ_CLOSURE")
    R.ok("ACTIVITY_PRODUCT_FIT")

    # ---- 9. capacity ----------------------------------------------------
    recomputed = defaultdict(float)
    for cid, c in sorted(comps.items()):
        for ru in c.get("resource_use", []):
            if ru["pool"] not in pools:
                R.bad("CAPACITY", "%s draws on unknown pool %s" % (cid, ru["pool"]))
                continue
            if ru["unit"] != pools[ru["pool"]]["unit"]:
                R.bad("CAPACITY", "%s draws on %s in %s but the pool is denominated in %s"
                      % (cid, ru["pool"], ru["unit"], pools[ru["pool"]]["unit"]))
            if ru["amount"] <= 0:
                R.bad("CAPACITY", "%s draws a non-positive amount from %s" % (cid, ru["pool"]))
            recomputed[ru["pool"]] += ru["amount"]
    for pid, p in sorted(pools.items()):
        if recomputed[pid] - p["capacity"] > 1e-6:
            R.bad("CAPACITY", "pool %s: parts draw %.2f %s against a capacity of %.2f"
                  % (pid, recomputed[pid], p["unit"], p["capacity"]))
    R.ok("CAPACITY")

    # ---- 10. schedule ---------------------------------------------------
    preds = defaultdict(list)
    for r in rels:
        if "PRECEDENCE" in rk.get(r["kind"], {}).get("checks", []):
            preds[r["to"]].append(r["from"])
    start = {}
    if not cyc:
        order, temp = [], set()

        def topo(n):
            if n in temp:
                return
            temp.add(n)
            for p in sorted(preds[n]):
                topo(p)
            if n not in order:
                order.append(n)

        for n in sorted(comps):
            topo(n)
        for n in order:
            s = 0
            for p in preds[n]:
                s = max(s, start.get(p, 0) + comps[p]["duration_days"])
            start[n] = s
        for cid, c in sorted(comps.items()):
            if c["duration_days"] <= 0:
                R.bad("SCHEDULE", "%s has a non-positive duration" % cid)
            if c["start_day"] < start[cid]:
                R.bad("SCHEDULE", "%s starts on day %d but its predecessors finish on day %d"
                      % (cid, c["start_day"], start[cid]))
            if c["finish_day"] != c["start_day"] + c["duration_days"]:
                R.bad("SCHEDULE", "%s finish day is not start plus duration" % cid)
        deadline = case["situation"]["deadline_day"]
        latest = max(c["finish_day"] for c in comps.values())
        if latest > deadline:
            R.bad("SCHEDULE", "last finish day %d is after the deadline day %d" % (latest, deadline))
        if deadline > case["situation"]["window_days"]:
            R.bad("SCHEDULE", "deadline day %d falls outside the %d-day window"
                  % (deadline, case["situation"]["window_days"]))
        w = case["situation"]["window_days"]
        if not (bounds["case_window_days"]["min"] <= w <= bounds["case_window_days"]["max"]):
            R.bad("SCHEDULE", "window of %d days is outside the declared bounds" % w)
        for q in case["atomic_requirements_with_stable_ids"]:
            if q["template"] == "RT-DEADLINE" and q["scope"] in comps:
                if str(comps[q["scope"]]["finish_day"]) not in q["text"]:
                    R.bad("SCHEDULE", "%s states a day that is not %s's finish day"
                          % (q["req_id"], q["scope"]))
        R.ok("SCHEDULE")
    else:
        R.unavailable("SCHEDULE", "schedule not evaluated because the precedence graph has a cycle")

    # ---- 11. identity ----------------------------------------------------
    ents = {}
    for e in case["entities"]:
        if e["entity_type"] not in D["entity_types"]:
            R.bad("IDENTITY_CONSISTENT", "unknown entity type %s" % e["entity_type"])
        if e["entity_id"] in ents and ents[e["entity_id"]] != e["entity_type"]:
            R.bad("IDENTITY_CONSISTENT", "identifier %s denotes two entity types" % e["entity_id"])
        ents[e["entity_id"]] = e["entity_type"]
        if not e["entity_id"].startswith(e["entity_type"] + "-"):
            R.bad("IDENTITY_CONSISTENT", "identifier %s does not carry its declared type %s"
                  % (e["entity_id"], e["entity_type"]))
    for i in case["concrete_inputs"]:
        if i.get("identity") and i["identity"] not in ents:
            R.bad("IDENTITY_CONSISTENT", "input %s refers to entity %s that is not in the entity set"
                  % (i["input_id"], i["identity"]))
    if case["beneficiary"].get("party_id") not in ents:
        R.bad("IDENTITY_CONSISTENT", "beneficiary party_id %s is not in the entity set"
              % case["beneficiary"].get("party_id"))
    R.ok("IDENTITY_CONSISTENT")

    # ---- 12. generator / emitted product --------------------------------
    gens = [cid for cid, c in sorted(comps.items()) if ing.get(c["product"], {}).get("generator")]
    emits = {r["from"] for r in rels if r["kind"] == "RK-EMIT"}
    for g in gens:
        if g not in emits:
            R.bad("GENERATOR_EMITS", "%s is a generator with no concrete emitted product" % g)
    R.ok("GENERATOR_EMITS")

    # ---- 13. acceptance coverage ----------------------------------------
    dl = {d["deliverable_id"]: d for d in case["required_deliverables"]}
    acc_by_dl = defaultdict(list)
    for a in case["acceptance_conditions"]:
        if a["deliverable"] not in dl:
            R.bad("ACCEPTANCE_COVER", "acceptance %s attaches to unknown deliverable %s"
                  % (a["ac_id"], a["deliverable"]))
        acc_by_dl[a["deliverable"]].append(a)
        if a["ingredient"] in ing and a["check_mode"] != ing[a["ingredient"]]["check_mode"]:
            R.bad("ACCEPTANCE_COVER", "acceptance %s declares check_mode %s, the ingredient says %s"
                  % (a["ac_id"], a["check_mode"], ing[a["ingredient"]]["check_mode"]))
    for did, d in sorted(dl.items()):
        if not acc_by_dl[did]:
            R.bad("ACCEPTANCE_COVER", "deliverable %s has no acceptance condition" % did)
        if d["component"] not in comps:
            R.bad("ACCEPTANCE_COVER", "deliverable %s names an unknown component" % did)
        elif comps[d["component"]]["product"] != d["product"]:
            R.bad("ACCEPTANCE_COVER", "deliverable %s and its component disagree about the product" % did)
        if set(d.get("acceptance_ids", [])) != {a["ac_id"] for a in acc_by_dl[did]}:
            R.bad("ACCEPTANCE_COVER", "deliverable %s acceptance_ids disagree with the conditions" % did)
    R.ok("ACCEPTANCE_COVER")

    # ---- 14. requirements ------------------------------------------------
    seen_req = set()
    for q in case["atomic_requirements_with_stable_ids"]:
        if q["req_id"] in seen_req:
            R.bad("REQUIREMENT_IDS", "duplicate requirement id %s" % q["req_id"])
        seen_req.add(q["req_id"])
        if not q["req_id"].startswith(case["case_id"] + "/"):
            R.bad("REQUIREMENT_IDS", "requirement id %s is not scoped to the case" % q["req_id"])
        if q["scope"] not in comps and q["scope"] not in seen_rel and q["scope"] != "case":
            R.bad("REQUIREMENT_IDS", "requirement %s has an unresolvable scope %s"
                  % (q["req_id"], q["scope"]))
        if not q.get("text"):
            R.bad("REQUIREMENT_IDS", "requirement %s carries no text" % q["req_id"])
    R.ok("REQUIREMENT_IDS")

    # ---- 15. global constraints present and evaluated --------------------
    present = {g["template"] for g in case["global_constraints"]}
    need_present = {"CT-SCHEDULE_FEASIBLE", "CT-IDENTITY_UNIQUE", "CT-ACYCLIC", "CT-DEPTH_BOUND",
                    "CT-PREREQ_CLOSED", "CT-ACCEPTANCE_COVER", "CT-REGIME_ADMISSIBLE",
                    "CT-SITUATION_ADMISSIBLE", "CT-UNIT_DECLARED", "CT-HYPOTHETICAL_LABELLED"}
    if gens:
        need_present.add("CT-GENERATOR_EMITS")
    if any(r["kind"] == "RK-DELEGATE" for r in rels):
        need_present.add("CT-AUTHORITY_SCOPED")
    if any(r["kind"] == "RK-TIME" for r in rels):
        need_present.add("CT-STALENESS_BOUND")
    if any(r["kind"] == "RK-INPUT" for r in rels):
        need_present.add("CT-DIMENSION_MATCH")
    missing_gc = sorted(need_present - present)
    if missing_gc:
        R.bad("GLOBAL_CONSTRAINTS", "the combination requires %s and they are not declared" % missing_gc)
    pool_gc = {g["params"].get("pool_id") for g in case["global_constraints"]
               if g["template"] == "CT-CAPACITY_BOUND"}
    for pid, p in sorted(pools.items()):
        if pid not in pool_gc:
            R.bad("GLOBAL_CONSTRAINTS", "pool %s has no capacity constraint" % pid)
        else:
            gc = [g for g in case["global_constraints"]
                  if g["template"] == "CT-CAPACITY_BOUND" and g["params"].get("pool_id") == pid][0]
            if abs(float(gc["params"]["capacity"]) - p["capacity"]) > 1e-9:
                R.bad("GLOBAL_CONSTRAINTS", "capacity constraint for %s states %s, the pool holds %s"
                      % (pid, gc["params"]["capacity"], p["capacity"]))
    for g in case["global_constraints"]:
        if g["template"] in ct and not ct[g["template"]]["machine_checkable"]:
            R.unavailable("QUALITATIVE_CONSTRAINT",
                          "%s (%s) is not machine-checkable by this program" % (g["gc_id"], g["template"]))
    R.ok("GLOBAL_CONSTRAINTS")

    # ---- 16. fixtures and hypothetical labelling -------------------------
    for i in case["concrete_inputs"]:
        if not (i.get("fixture") or {}).get("hypothetical"):
            R.bad("FIXTURE_LABELLED", "input %s is not labelled hypothetical" % i["input_id"])
        q = i.get("quantity") or {}
        if q.get("unit") not in units:
            R.bad("UNITS_DECLARED", "input %s carries an undeclared unit %s"
                  % (i["input_id"], q.get("unit")))
        if not i.get("state_at_day_zero"):
            R.bad("FIXTURE_LABELLED", "input %s has no initial state" % i["input_id"])
    if not case["need_and_context"].get("hypothetical"):
        R.bad("FIXTURE_LABELLED", "the case does not declare itself hypothetical")
    R.ok("FIXTURE_LABELLED")

    # ---- 17. diversity signature recomputation ---------------------------
    sig = case["diversity_signature"]
    idea = h(need, comps["C1"]["product"] if "C1" in comps else "",
             tuple(sorted(c["product"] for c in comps.values())),
             tuple(sorted({r["kind"] for r in rels})))
    if sig.get("idea_key") != idea:
        R.bad("SIGNATURE", "idea_key does not recompute from the record")
    shape = tuple(sorted((r["kind"], comps[r["from"]]["depth"], comps[r["to"]]["depth"])
                         for r in rels if r["from"] in comps and r["to"] in comps))
    struct = h(len(comps), max(c["depth"] for c in comps.values()), shape)
    if sig.get("structure_key") != struct:
        R.bad("SIGNATURE", "structure_key does not recompute from the record")
    situ = h(tuple(sorted(sits)), tuple(sorted(case["situation"]["conditions"])),
             tuple(sorted(case["situation"]["dynamics"])))
    if sig.get("situation_key") != situ:
        R.bad("SIGNATURE", "situation_key does not recompute from the record")
    if sig.get("full_key") != h(idea, struct, situ, regime, domain,
                                case["beneficiary"]["ingredient"], case["situation"]["scale"]):
        R.bad("SIGNATURE", "full_key does not recompute from the record")
    R.ok("SIGNATURE")

    # ---- 18. witness re-verification -------------------------------------
    w = case["validation_status_and_evidence"].get("witness") or {}
    wa = w.get("resource_allocation") or {}
    for pid, p in sorted(pools.items()):
        rec = wa.get(pid)
        if not rec:
            R.bad("WITNESS", "no retained allocation for pool %s" % pid)
            continue
        if abs(sum(rec["allocated"].values()) - rec["total"]) > 1e-6:
            R.bad("WITNESS", "retained total for %s does not add up" % pid)
        if rec["total"] - p["capacity"] > 1e-6:
            R.bad("WITNESS", "retained allocation for %s exceeds the capacity" % pid)
        if abs(rec["total"] - recomputed[pid]) > 1e-6:
            R.bad("WITNESS", "retained allocation for %s disagrees with the components" % pid)
    ws = w.get("schedule") or {}
    for cid, c in sorted(comps.items()):
        s = ws.get(cid)
        if not s:
            R.bad("WITNESS", "no retained schedule for %s" % cid)
        elif s["start_day"] != c["start_day"] or s["finish_day"] != c["finish_day"]:
            R.bad("WITNESS", "retained schedule for %s disagrees with the component" % cid)
    R.ok("WITNESS")

    # ---- 19. qualitative acceptance is recorded, never passed -------------
    n_machine = 0
    for a in case["acceptance_conditions"]:
        if a["check_mode"] == "machine":
            n_machine += 1
        else:
            R.unavailable("QUALITATIVE_ACCEPTANCE",
                          "%s (%s) needs human judgment: %s" % (a["ac_id"], a["ingredient"],
                                                                a.get("judgment_needed")))
    if n_machine == 0:
        R.bad("ACCEPTANCE_COVER", "no acceptance condition of this case is machine-checkable")
    R.unavailable("PLAUSIBILITY", "whether this need, beneficiary and set of relationships make "
                                  "sense in the world is not decided by this program")
    return R


# --------------------------------------------------------------------------
# deliberately broken examples
# --------------------------------------------------------------------------


def minimal_case(D):
    """Assemble a small valid case directly from the dictionary, without the
    generator, so that the broken-example suite does not depend on it."""
    ing = D["ingredients"]
    regime = "R-ORG"
    domain = "ISIC-N"
    sits = ["S-ROUTINE", "S-AUDIT", "S-COLLABORATIVE"]

    def first(axis, pred):
        for iid in sorted(ing):
            v = ing[iid]
            if v["axis"] == axis and regime in v["regimes"] and set(v["situations"]) & set(sits) \
                    and pred(v):
                return iid
        raise SystemExit("cannot assemble a minimal case for axis %s" % axis)

    need = first("need", lambda v: domain in v["domains"])
    ben = first("beneficiary", lambda v: v["scale_band"] in ing[need]["beneficiary_bands"])
    scale = first("scale", lambda v: True)
    prod1 = first("product", lambda v: domain in v["domains"] and not v.get("generator"))
    prod2 = first("product", lambda v: domain in v["domains"] and not v.get("generator")
                  and v["id"] != prod1)
    act1 = first("activity", lambda v: "needs_capacity:staff_hours" in v["prerequisites"])
    act2 = first("activity", lambda v: v["id"] != act1)
    pool_ing = first("condition", lambda v: v["kind"] == "resource" and v["resource_kind"] == "staff_hours")
    auth = first("condition", lambda v: v["kind"] == "authority")
    dyn = [first("dynamic", lambda v: True)]
    for iid in sorted(ing):
        v = ing[iid]
        if v["axis"] == "dynamic" and iid not in dyn and regime in v["regimes"] \
                and set(v["situations"]) & set(sits):
            dyn.append(iid)
        if len(dyn) == 3:
            break
    acc = first("acceptance", lambda v: v["check_mode"] == "machine")

    ents = [{"entity_id": "PARTY-1001", "entity_type": "PARTY", "label": "party 1"},
            {"entity_id": "SITE-1002", "entity_type": "SITE", "label": "site 1"}]

    comps = []
    for idx, (pid, aid) in enumerate([(prod1, act1), (prod2, act2)], start=1):
        comps.append({"component_id": "C%d" % idx, "product": pid, "activity": aid,
                      "regime": regime, "depth": idx - 1, "inputs": [], "resource_use": [],
                      "prerequisites": list(ing[aid]["prerequisites"]),
                      "duration_days": 4, "start_day": 0, "finish_day": 4,
                      "assumed_forms": []})
    inputs = []
    n = 0
    assumptions = []
    for c in comps:
        for t in c["prerequisites"]:
            if t.startswith("needs_form:"):
                form = t.split(":", 1)[1]
                cand = None
                for iid in sorted(ing):
                    v = ing[iid]
                    if v["axis"] == "input" and v["form"] == form and regime in v["regimes"] \
                            and set(v["situations"]) & set(sits):
                        cand = iid
                        break
                if cand is None:
                    c["assumed_forms"].append(form)
                    assumptions.append("The %s input that %s requires is assumed available in the "
                                       "setting and is not specified here; no vocabulary input of "
                                       "that form is admissible in %s under these situation tags."
                                       % (form, c["component_id"], D["regimes"][regime]["label"]))
                    continue
                n += 1
                inputs.append({"input_id": "I%d" % n, "ingredient": cand, "form": form,
                               "identity": "SITE-1002",
                               "quantity": {"value": 120.0, "unit": ing[cand].get("unit") or "U-COUNT"},
                               "state_at_day_zero": "held by the party named above and not yet checked",
                               "fixture": {"hypothetical": True, "note": "compact synthetic fixture"},
                               "used_by": [c["component_id"]]})
                c["inputs"].append("I%d" % n)
            elif t.startswith("needs_capacity:"):
                kind = t.split(":", 1)[1]
                if kind == "staff_hours":
                    c["resource_use"].append({"pool": "P1", "amount": 100.0, "unit": ing[pool_ing]["unit"]})
                else:
                    assumptions.append("Capacity of kind %s is assumed available in the setting and is "
                                       "not metered by this case; no pool is declared for it." % kind)
    pools = [{"pool_id": "P1", "condition": pool_ing, "resource_kind": "staff_hours",
              "unit": ing[pool_ing]["unit"], "capacity": 400.0}]
    # C2 provides an input to C1 -> precedence, so C1 starts after C2
    rels = [{"rel_id": "L1", "kind": "RK-INPUT", "from": "C2", "to": "C1",
             "transfers": {"what": "records produced by C2 and required by C1", "form": "data",
                           "ingredient": comps[1]["product"],
                           "quantity": {"value": 500.0, "unit": "U-RECORD"},
                           "expects_dimension": "records", "receiving_unit": "U-RECORD",
                           "conversion": None},
             "enables": "C1 can start", "changes": "C1's prerequisite set closes", "shares": None},
            {"rel_id": "L2", "kind": "RK-SHARE", "from": "C1", "to": "C2",
             "transfers": {"what": "nothing is transferred; both parts name the same entity",
                           "ingredient": scale, "quantity": None},
             "shared_object": {"kind": "entity", "ref": "SITE-1002"},
             "enables": "results can be joined", "changes": "a rename in one breaks the other",
             "shares": "entity identifier SITE-1002"}]
    comps[1]["start_day"], comps[1]["finish_day"] = 0, 4
    comps[0]["start_day"], comps[0]["finish_day"] = 4, 8
    comps[0]["depth"], comps[1]["depth"] = 0, 1
    # C1 receives form data through L1
    deadline, window = 20, 40
    deliverables = [{"deliverable_id": "D1", "component": "C1", "product": prod1,
                     "form": ing[prod1]["form"], "title": "deliverable one",
                     "quantity": {"value": 1, "unit": "U-COUNT"}, "due_day": 8,
                     "acceptance_ids": ["AC1"]}]
    acceptance = [{"ac_id": "AC1", "ingredient": acc, "deliverable": "D1",
                   "check_mode": "machine", "statement": "%s." % ing[acc]["label"],
                   "observable": ing[acc]["observable"],
                   "threshold": {"value": 0.95, "basis": "proportion"},
                   "judgment_needed": ing[acc]["judgment_needed"]}]
    reqs = []

    def add(iid, tpl, text, scope, check, source):
        reqs.append({"req_id": "BRK-00000/R%d" % (len(reqs) + 1), "ingredient": iid,
                     "template": tpl, "text": text, "scope": scope, "check": check, "source": source})

    for c in comps:
        for t in c["prerequisites"]:
            if t.startswith("needs_form:"):
                add(c["activity"], "RT-INPUT-PRESENT",
                    "%s shall not begin before the required %s input is present in the stated form "
                    "and quantity." % (c["component_id"], t.split(":", 1)[1]),
                    c["component_id"], "machine", "inherited")
        for ru in c["resource_use"]:
            add(pool_ing, "RT-CAPACITY-RESPECTED",
                "%s shall draw no more than its allocated %s from pool %s."
                % (c["component_id"], ru["amount"], ru["pool"]), c["component_id"], "machine",
                "inherited")
        add(c["product"], "RT-DEADLINE",
            "%s shall be complete by day %d of the case window." % (c["component_id"], c["finish_day"]),
            c["component_id"], "machine", "inherited")
    add(comps[1]["product"], "RT-UNIT-CARRIED",
        "Every quantity C2 emits shall carry a unit from the declared unit table.",
        "L1", "machine", "combination")
    add(scale, "RT-IDENTITY-STABLE",
        "C1 and C2 shall refer to SITE-1002 by the identifier minted for it and by no other.",
        "L2", "machine", "combination")
    add(need, "RT-FIXTURE-LABEL",
        "The case as a whole shall label every synthetic fixture as hypothetical wherever it is "
        "displayed.", "case", "machine", "combination")

    gcs = [{"gc_id": "G1", "template": "CT-CAPACITY_BOUND",
            "params": {"pool_id": "P1", "resource": "staff_hours", "capacity": 400.0,
                       "unit": D["units"][pools[0]["unit"]]["display"]}}]
    for i, tpl in enumerate(["CT-SCHEDULE_FEASIBLE", "CT-IDENTITY_UNIQUE", "CT-ACYCLIC",
                             "CT-DEPTH_BOUND", "CT-PREREQ_CLOSED", "CT-ACCEPTANCE_COVER",
                             "CT-REGIME_ADMISSIBLE", "CT-SITUATION_ADMISSIBLE", "CT-UNIT_DECLARED",
                             "CT-HYPOTHETICAL_LABELLED", "CT-DIMENSION_MATCH"], start=2):
        params = {}
        if tpl == "CT-SCHEDULE_FEASIBLE":
            params = {"deadline_day": deadline}
        if tpl == "CT-DEPTH_BOUND":
            params = {"max_depth": D["generation_bounds"]["max_depth"]}
        gcs.append({"gc_id": "G%d" % i, "template": tpl, "params": params})

    idea = h(need, prod1, tuple(sorted(c["product"] for c in comps)),
             tuple(sorted({r["kind"] for r in rels})))
    shape = tuple(sorted((r["kind"], {c["component_id"]: c["depth"] for c in comps}[r["from"]],
                          {c["component_id"]: c["depth"] for c in comps}[r["to"]]) for r in rels))
    struct = h(len(comps), max(c["depth"] for c in comps), shape)
    situ = h(tuple(sorted(sits)), tuple(sorted([pool_ing, auth])), tuple(sorted(dyn)))
    case = {
        "case_id": "BRK-00000",
        "generation_version": D["generation_version"],
        "dictionary_version": D["dictionary_version"],
        "primary_domain": domain, "regime": regime,
        "situation": {"tags": sits, "scale": scale, "conditions": sorted([pool_ing, auth]),
                      "authority": auth, "resource_pools": pools, "dynamics": sorted(dyn),
                      "window_days": window, "deadline_day": deadline, "domain_matched_axes": []},
        "beneficiary": {"ingredient": ben, "scale_band": ing[ben]["scale_band"],
                        "party_id": "PARTY-1001", "statement": ing[ben]["label"]},
        "need_and_context": {"need": need, "purpose_class": ing[need]["purpose_class"],
                             "statement": ing[need]["label"], "context": ing[need]["meaning"],
                             "hypothetical": True},
        "required_deliverables": deliverables,
        "concrete_inputs": inputs,
        "entities": ents,
        "components": comps,
        "component_relationships": rels,
        "atomic_requirements_with_stable_ids": reqs,
        "global_constraints": gcs,
        "acceptance_conditions": acceptance,
        "assumptions_and_provenance": {
            "assumptions": assumptions + ["Every identifier and quantity here is a hypothetical fixture."],
            "ingredients_used": sorted({ben, need, scale, prod1, prod2, act1, act2, pool_ing, auth,
                                        acc} | set(dyn) | {i["ingredient"] for i in inputs}),
            "provenance_note": "resolve ids in dictionary.json", "open_questions": []},
        "validation_status_and_evidence": {
            "structural_completeness": "hand-assembled base fixture for the broken-example suite",
            "encoded_constraints": "asserted by this fixture, re-derived by the checker",
            "plausibility_review": "not_reviewed",
            "witness": {"resource_allocation": {"P1": {
                "capacity": 400.0, "unit": pools[0]["unit"],
                "allocated": {c["component_id"]: ru["amount"] for c in comps
                              for ru in c["resource_use"]},
                "total": sum(ru["amount"] for c in comps for ru in c["resource_use"])}},
                "schedule": {c["component_id"]: {"start_day": c["start_day"],
                                                 "finish_day": c["finish_day"]} for c in comps},
                "deadline_day": deadline},
            "witness_establishes": ["CT-CAPACITY_BOUND", "CT-SCHEDULE_FEASIBLE"],
            "witness_does_not_establish": ["real-world suitability"],
            "remaining_judgments": ["none beyond the encoded checks"]},
        "diversity_signature": {"idea_key": idea, "structure_key": struct, "situation_key": situ,
                                "variant_key": h(idea, struct, regime, domain),
                                "full_key": h(idea, struct, situ, regime, domain, ben, scale),
                                "purpose_class": ing[need]["purpose_class"],
                                "root_product_form": ing[prod1]["form"],
                                "component_forms": sorted(ing[c["product"]]["form"] for c in comps),
                                "relationship_kinds": sorted({r["kind"] for r in rels}),
                                "depth": 1, "components": 2, "branching": 1, "coupling": 2,
                                "cross_regime_components": [], "flags": []},
        "seed_or_replay_reference": {"seed": 0, "case_index": 0, "phase": "broken-suite-base",
                                     "stratum": "%s|%s" % (regime, domain),
                                     "replay": "constructed inside checker.py, not by generate.py"},
    }
    return case


def broken_suite(D):
    import copy
    base = minimal_case(D)
    out = []

    def variant(name, expect, mutate):
        c = copy.deepcopy(base)
        c["case_id"] = "BRK-%s" % name
        for q in c["atomic_requirements_with_stable_ids"]:
            q["req_id"] = q["req_id"].replace("BRK-00000", c["case_id"])
        mutate(c)
        out.append({"name": name, "case": c, "expected_violations": expect})

    def m_missing_prereq(c):
        c["concrete_inputs"] = []
        for comp in c["components"]:
            comp["inputs"] = []
            comp["assumed_forms"] = []
        c["assumptions_and_provenance"]["assumptions"] = ["nothing is assumed"]
        for r in c["component_relationships"]:
            if r["kind"] == "RK-INPUT":
                r["transfers"].pop("form", None)
    variant("missing-prerequisite", ["PREREQ_CLOSURE"], m_missing_prereq)

    def m_identity(c):
        c["entities"][1] = {"entity_id": "PARTY-1001", "entity_type": "SITE", "label": "clash"}
    variant("conflicting-identity", ["IDENTITY_CONSISTENT"], m_identity)

    def m_units(c):
        for r in c["component_relationships"]:
            if r["kind"] == "RK-INPUT":
                r["transfers"]["receiving_unit"] = "U-KG"
                r["transfers"]["expects_dimension"] = "records"
    variant("incompatible-units", ["REL_UNIT_DIMENSION"], m_units)

    def m_capacity(c):
        for comp in c["components"]:
            for ru in comp["resource_use"]:
                ru["amount"] = 900.0
    variant("excess-shared-resource", ["CAPACITY", "WITNESS"], m_capacity)

    def m_cycle(c):
        c["component_relationships"].append({
            "rel_id": "L3", "kind": "RK-COND", "from": "C1", "to": "C2",
            "transfers": {"what": "a verdict", "ingredient": c["situation"]["dynamics"][0],
                          "quantity": None},
            "predicate": "always true", "else_branch": "stop",
            "enables": "x", "changes": "y", "shares": None})
    variant("precedence-cycle", ["ACYCLIC"], m_cycle)

    def m_schedule(c):
        c["situation"]["deadline_day"] = 2
    variant("deadline-before-finish", ["SCHEDULE"], m_schedule)

    def m_regime(c):
        c["regime"] = "R-BIO"
        for comp in c["components"]:
            comp["regime"] = "R-BIO"
    variant("regime-not-admitted", ["REGIME_ADMISSIBLE"], m_regime)

    def m_situation(c):
        c["situation"]["tags"] = ["S-CRISIS"]
    variant("situation-not-admitted", ["SITUATION_ADMISSIBLE"], m_situation)

    def m_domain(c):
        ing = D["ingredients"]
        narrow = sorted(i for i in ing
                        if ing[i]["axis"] == "product" and len(ing[i]["domains"]) < 27
                        and c["regime"] in ing[i]["regimes"]
                        and set(ing[i]["situations"]) & set(c["situation"]["tags"])
                        and c["primary_domain"] not in ing[i]["domains"])
        if narrow:
            c["components"][1]["product"] = narrow[0]
        else:
            c["primary_domain"] = "FORD-6" if c["primary_domain"] != "FORD-6" else "ISIC-B"
    variant("domain-not-admitted", ["DOMAIN_GATE"], m_domain)

    def m_acceptance(c):
        c["required_deliverables"].append({
            "deliverable_id": "D2", "component": "C2", "product": c["components"][1]["product"],
            "form": D["ingredients"][c["components"][1]["product"]]["form"],
            "title": "deliverable two", "quantity": {"value": 1, "unit": "U-COUNT"},
            "due_day": 4, "acceptance_ids": []})
    variant("deliverable-without-acceptance", ["ACCEPTANCE_COVER"], m_acceptance)

    def m_generator(c):
        ing = D["ingredients"]
        gen = sorted(i for i in ing if ing[i]["axis"] == "product" and ing[i].get("generator")
                     and c["regime"] in ing[i]["regimes"]
                     and c["primary_domain"] in ing[i]["domains"]
                     and set(ing[i]["situations"]) & set(c["situation"]["tags"]))
        if gen:
            c["components"][0]["product"] = gen[0]
            c["required_deliverables"][0]["product"] = gen[0]
            c["required_deliverables"][0]["form"] = ing[gen[0]]["form"]
            c["global_constraints"].append({"gc_id": "G99", "template": "CT-GENERATOR_EMITS",
                                            "params": {}})
    variant("configurator-without-emitted-product", ["GENERATOR_EMITS", "SIGNATURE"], m_generator)

    def m_dangling(c):
        c["atomic_requirements_with_stable_ids"][0]["ingredient"] = "NED-DOES-NOT-EXIST"
    variant("dangling-ingredient-reference", ["VOCAB_RESOLVE"], m_dangling)

    def m_witness(c):
        c["validation_status_and_evidence"]["witness"]["resource_allocation"]["P1"]["total"] = 1.0
    variant("witness-does-not-add-up", ["WITNESS"], m_witness)

    def m_signature(c):
        c["diversity_signature"]["idea_key"] = "0" * 16
    variant("fabricated-signature", ["SIGNATURE"], m_signature)

    def m_reqids(c):
        c["atomic_requirements_with_stable_ids"][1]["req_id"] = \
            c["atomic_requirements_with_stable_ids"][0]["req_id"]
    variant("duplicate-requirement-id", ["REQUIREMENT_IDS"], m_reqids)

    def m_struct(c):
        del c["global_constraints"]
    variant("missing-required-field", ["STRUCTURE"], m_struct)

    def m_gc(c):
        c["global_constraints"] = [g for g in c["global_constraints"]
                                   if g["template"] != "CT-CAPACITY_BOUND"]
    variant("pool-without-capacity-constraint", ["GLOBAL_CONSTRAINTS"], m_gc)

    def m_fixture(c):
        c["concrete_inputs"][0]["fixture"]["hypothetical"] = False if c["concrete_inputs"] else None
        if not c["concrete_inputs"]:
            c["need_and_context"]["hypothetical"] = False
    variant("fixture-not-labelled-hypothetical", ["FIXTURE_LABELLED"], m_fixture)

    def m_band(c):
        ing = D["ingredients"]
        wrong = sorted(i for i in ing if ing[i]["axis"] == "beneficiary"
                       and ing[i]["scale_band"] not in ing[c["need_and_context"]["need"]]["beneficiary_bands"]
                       and c["regime"] in ing[i]["regimes"]
                       and set(ing[i]["situations"]) & set(c["situation"]["tags"]))
        if wrong:
            c["beneficiary"]["ingredient"] = wrong[0]
            c["beneficiary"]["scale_band"] = ing[wrong[0]]["scale_band"]
    variant("beneficiary-band-mismatch", ["BENEFICIARY_BAND", "SIGNATURE"], m_band)

    def m_embed(c):
        c["component_relationships"].append({
            "rel_id": "L4", "kind": "RK-EMBED", "from": "C2", "to": "C1",
            "transfers": {"what": "the whole of C2", "ingredient": c["components"][1]["product"],
                          "quantity": None},
            "enables": "one delivery", "changes": "obligations inherited", "shares": "identity"})
    variant("embed-without-inherited-acceptance", ["REL_INHERIT_ACCEPTANCE"], m_embed)

    return base, out


# --------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dictionary", required=True)
    ap.add_argument("--cases")
    ap.add_argument("--broken", action="store_true")
    ap.add_argument("--report", required=True)
    args = ap.parse_args()

    import time
    t0 = time.time()
    with open(args.dictionary, encoding="utf-8") as fh:
        D = json.load(fh)
    t_setup = time.time() - t0

    if args.broken:
        base, suite = broken_suite(D)
        base_report = check_case(D, base)
        rows = []
        detected = 0
        for v in suite:
            rep = check_case(D, v["case"])
            found = sorted({x["code"] for x in rep.violations
                            if x.get("severity") != "unavailable"})
            hit = all(code in found for code in v["expected_violations"])
            detected += 1 if hit else 0
            rows.append({"name": v["name"], "case_id": v["case"]["case_id"],
                         "expected_violations": v["expected_violations"],
                         "violations_found": found,
                         "expected_all_detected": hit,
                         "detail": [x for x in rep.violations
                                    if x.get("severity") != "unavailable"][:4]})
        report = {
            "checker_version": CHECKER_VERSION,
            "dictionary_version": D["dictionary_version"],
            "mode": "broken-examples",
            "base_fixture": {
                "case_id": base["case_id"],
                "note": "assembled inside checker.py directly from the dictionary, so the suite does "
                        "not depend on generate.py",
                "checks": base_report.checks,
                "violations": [v for v in base_report.violations if v.get("severity") != "unavailable"],
                "clean": not [v for v in base_report.violations if v.get("severity") != "unavailable"],
            },
            "counts": {"variants": len(suite), "all_expected_violations_detected": detected,
                       "variants_missed": len(suite) - detected},
            "variants": rows,
            "timings_seconds": {"setup": round(t_setup, 3),
                                "checking": round(time.time() - t0 - t_setup, 3)},
        }
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=1, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        print("broken examples: %d/%d detected; base fixture clean: %s"
              % (detected, len(suite), report["base_fixture"]["clean"]))
        if not report["base_fixture"]["clean"]:
            for v in report["base_fixture"]["violations"][:10]:
                print("  base violation:", v)
        for r in rows:
            if not r["expected_all_detected"]:
                print("  MISSED:", r["name"], "expected", r["expected_violations"],
                      "found", r["violations_found"])
        return

    if not args.cases:
        ap.error("--cases is required unless --broken is given")

    t1 = time.time()
    n = 0
    passed = 0
    check_tally = Counter()
    violation_tally = Counter()
    unavailable_tally = Counter()
    failures = []
    seen_ids = set()
    seen_full = set()
    dup_ids, dup_keys = 0, 0
    claim_mismatch = 0
    for line in open(args.cases, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        case = json.loads(line)
        n += 1
        if case.get("case_id") in seen_ids:
            dup_ids += 1
        seen_ids.add(case.get("case_id"))
        fk = (case.get("diversity_signature") or {}).get("full_key")
        if fk in seen_full:
            dup_keys += 1
        seen_full.add(fk)
        rep = check_case(D, case)
        hard = [v for v in rep.violations if v.get("severity") != "unavailable"]
        for code, verdict in rep.checks.items():
            check_tally[(code, verdict)] += 1
        for v in hard:
            violation_tally[v["code"]] += 1
        for v in rep.violations:
            if v.get("severity") == "unavailable":
                unavailable_tally[v["code"]] += 1
        if not hard:
            passed += 1
        else:
            if len(failures) < 50:
                failures.append({"case_id": rep.case_id, "violations": hard[:6]})
        claimed = (case.get("validation_status_and_evidence") or {}).get("encoded_constraints", "")
        if hard and "satisfied by construction" in claimed:
            claim_mismatch += 1
    t_check = time.time() - t1

    codes = sorted({c for c, _ in check_tally})
    report = {
        "checker_version": CHECKER_VERSION,
        "dictionary_version": D["dictionary_version"],
        "mode": "cases",
        "cases_file": os.path.basename(args.cases),
        "cases_sha256": hashlib.sha256(open(args.cases, "rb").read()).hexdigest(),
        "dictionary_sha256": hashlib.sha256(open(args.dictionary, "rb").read()).hexdigest(),
        "evidence_policy": "every verdict is re-derived from dictionary.json and the record; the "
                           "record's own validation block is read only to report disagreement, "
                           "never as evidence",
        "counts": {
            "cases_read": n,
            "structurally_and_mechanically_clean": passed,
            "with_at_least_one_violation": n - passed,
            "duplicate_case_ids": dup_ids,
            "duplicate_full_keys": dup_keys,
            "generator_claim_contradicted_by_checker": claim_mismatch,
        },
        "check_results": {code: {verdict: check_tally[(code, verdict)]
                                 for verdict in ("pass", "fail", "unavailable")
                                 if check_tally[(code, verdict)]}
                          for code in codes},
        "violations_by_code": dict(sorted(violation_tally.items())),
        "unavailable_by_code": dict(sorted(unavailable_tally.items())),
        "unavailable_meaning": "an `unavailable` result is not a pass: it records that this program "
                               "cannot decide the item (qualitative acceptance conditions, "
                               "constraint templates marked not machine-checkable, and the "
                               "plausibility of the case itself)",
        "failures": failures,
        "timings_seconds": {"setup": round(t_setup, 3), "checking": round(t_check, 3),
                            "throughput_cases_per_second": round(n / max(t_check, 1e-9), 1)},
    }
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")
    print("checked %d cases: %d clean, %d with violations (setup %.2fs, checking %.2fs)"
          % (n, passed, n - passed, t_setup, t_check))
    if violation_tally:
        for k, v in sorted(violation_tally.items()):
            print("   %-28s %d" % (k, v))


if __name__ == "__main__":
    main()
