#!/usr/bin/env python3
"""Procedural generator of useful use cases.

    python3 generate.py --dictionary dictionary.json --seed <integer> --count <n> \
        --out cases.jsonl --record generation_record.json

No language-model step occurs inside this program.  Every choice is drawn from
one random.Random instance seeded by --seed (or, when --seed is omitted, by a
single draw from os.urandom which is then recorded).  Every emitted record is a
function of (dictionary, seed, count) alone: no wall-clock, path or environment
value enters a case record.
"""
import argparse, hashlib, json, os, random, sys, time
from collections import defaultdict, Counter

GEN_PROGRAM_VERSION = "generate.py/2.0.0"

# --------------------------------------------------------------------------
# indexes
# --------------------------------------------------------------------------


class Vocab:
    def __init__(self, doc):
        self.doc = doc
        self.ing = doc["ingredients"]
        self.rules = doc["compatibility_rules"]
        self.bounds = doc["generation_bounds"]
        self.units = doc["units"]
        self.rk = doc["relationship_kinds"]
        self.ct = doc["constraint_templates"]
        self.rt = doc["requirement_templates"]
        self.regimes = sorted(doc["regimes"])
        self.domains = sorted(doc["domains"], key=lambda d: (d.split("-")[0], d))
        self.by_axis = defaultdict(list)
        for iid in sorted(self.ing):
            self.by_axis[self.ing[iid]["axis"]].append(iid)
        # axis x regime
        self.axis_regime = defaultdict(list)
        for axis in sorted(self.by_axis):
            for iid in self.by_axis[axis]:
                for r in self.ing[iid]["regimes"]:
                    self.axis_regime[(axis, r)].append(iid)
        # axis x regime x domain (used for the domain-gated axes and as a preference elsewhere)
        self.axis_regime_domain = defaultdict(list)
        for axis in sorted(self.by_axis):
            for iid in self.by_axis[axis]:
                ing = self.ing[iid]
                for r in ing["regimes"]:
                    for d in ing["domains"]:
                        self.axis_regime_domain[(axis, r, d)].append(iid)
        # inputs by form
        self.input_form_regime = defaultdict(list)
        for iid in self.by_axis["input"]:
            ing = self.ing[iid]
            for r in ing["regimes"]:
                self.input_form_regime[(ing["form"], r)].append(iid)
        # products by form
        self.product_form = defaultdict(list)
        for iid in self.by_axis["product"]:
            self.product_form[self.ing[iid]["form"]].append(iid)
        # resource conditions by kind
        self.pool_by_kind = defaultdict(list)
        for iid in self.by_axis["condition"]:
            ing = self.ing[iid]
            if ing["kind"] == "resource":
                self.pool_by_kind[ing["resource_kind"]].append(iid)
        self.authority = [i for i in self.by_axis["condition"] if self.ing[i]["kind"] == "authority"]
        self.environment = [i for i in self.by_axis["condition"] if self.ing[i]["kind"] == "environment"]
        self.generator_products = sorted(
            i for i in self.by_axis["product"] if self.ing[i].get("generator"))

    def sit_ok(self, iid, sits):
        return any(s in sits for s in self.ing[iid]["situations"])


FORM_UNITS = {
    "material": ["U-KG", "U-TONNE", "U-LITRE", "U-M3", "U-COUNT"],
    "data": ["U-RECORD", "U-GB", "U-COUNT"],
    "signal": ["U-RECORD", "U-COUNT"],
    "artifact": ["U-COUNT"],
    "credential": ["U-COUNT"],
    "knowledge": ["U-COUNT"],
    "organism": ["U-COUNT"],
    "energy": ["U-KWH", "U-MWH"],
    "space": ["U-M2", "U-SLOT"],
    "funding": ["U-CU", "U-KCU"],
    "person_time": ["U-PERSON-HOUR", "U-PERSON-DAY"],
}
DURATION_BAND = {"hours": (1, 3), "days": (2, 7), "weeks": (8, 26), "months": (28, 95)}

FLAGS = [
    "uncertain_evidence", "shared_resource_contention", "revision_after_partial_completion",
    "divided_authority", "interruption_recovery", "irreversible_effect", "scarce_capacity",
    "cross_regime_component", "configurator", "deep_nesting", "multi_party_concurrency",
    "privacy_tension", "long_horizon", "public_facing",
]
FLAG_SITUATION = {
    "uncertain_evidence": "S-UNCERTAIN-EVIDENCE",
    "shared_resource_contention": "S-SCARCITY",
    "revision_after_partial_completion": "S-INTERRUPTED",
    "divided_authority": "S-DIVIDED-AUTHORITY",
    "interruption_recovery": "S-INTERRUPTED",
    "irreversible_effect": "S-IRREVERSIBLE",
    "scarce_capacity": "S-SCARCITY",
    "multi_party_concurrency": "S-CONCURRENT",
    "privacy_tension": "S-PRIVACY-SENSITIVE",
    "long_horizon": "S-LONG-HORIZON",
    "public_facing": "S-PUBLIC-FACING",
}
FLAG_DYNAMIC = {
    "uncertain_evidence": ["DYN-NOISY-MEASUREMENT", "DYN-MISSING-DATA", "DYN-CONTESTED-EVIDENCE",
                           "DYN-MODEL-UNCERTAINTY", "DYN-SELF-REPORTED", "DYN-PROXY-MEASURE",
                           "DYN-SMALL-SAMPLE", "DYN-UNVERIFIED-SOURCE", "DYN-ASSUMED-PARAMETER"],
    "revision_after_partial_completion": ["DYN-PARTIAL-COMPLETION", "DYN-REVISION-CYCLE"],
    "interruption_recovery": ["DYN-INTERRUPTION", "DYN-RECOVERY-COMPENSATE", "DYN-ROLLBACK"],
    "irreversible_effect": ["DYN-IRREVERSIBLE-STEP", "DYN-RECOVERY-COMPENSATE"],
    "multi_party_concurrency": ["DYN-CONCURRENT-ACTORS", "DYN-CONTENTION-PEAK"],
    "long_horizon": ["DYN-LONG-HORIZON", "DYN-SUCCESSION"],
    "shared_resource_contention": ["DYN-CONTENTION-PEAK", "DYN-QUEUE-PRIORITY"],
}
FLAG_CONDITION = {
    "divided_authority": ["CND-DIVIDED-AUTHORITY", "CND-DELEGATED-AUTHORITY", "CND-TWO-KEY",
                          "CND-COMMITTEE-CONSENSUS"],
    "privacy_tension": ["CND-DATA-SENSITIVE"],
}

DYNAMIC_REQUIREMENT = {
    "DYN-INTERRUPTION": ("RT-RESUME", {}),
    "DYN-PARTIAL-COMPLETION": ("RT-RESUME", {}),
    "DYN-IRREVERSIBLE-STEP": ("RT-COMPENSATE", {}),
    "DYN-RECOVERY-COMPENSATE": ("RT-COMPENSATE", {}),
    "DYN-VERSION-BOUNDARY": ("RT-VERSION-STAMP", {}),
    "DYN-REGULATION-CHANGE": ("RT-VERSION-STAMP", {}),
    "DYN-STALE-STATE": ("RT-STALENESS", {}),
    "DYN-QUIET-FAILURE": ("RT-DEGRADE", {}),
    "DYN-DEGRADED-MODE": ("RT-DEGRADE", {}),
    "DYN-EXPIRY": ("RT-REVOCATION", {}),
    "DYN-SUCCESSION": ("RT-TRACE", {}),
    "DYN-NOISY-MEASUREMENT": ("RT-JUDGMENT", {}),
    "DYN-MODEL-UNCERTAINTY": ("RT-JUDGMENT", {}),
    "DYN-CONTESTED-EVIDENCE": ("RT-RECORD-DISAGREEMENT", {}),
    "DYN-ASSUMED-PARAMETER": ("RT-JUDGMENT", {}),
    "DYN-SELF-REPORTED": ("RT-JUDGMENT", {}),
    "DYN-MISSING-DATA": ("RT-TRACE", {}),
    "DYN-RETRACTION": ("RT-TRACE", {}),
    "DYN-DRIFT": ("RT-METHOD-CITED", {}),
    "DYN-HARD-DEADLINE": ("RT-DEADLINE", {}),
}
CONDITION_REQUIREMENT = {
    "CND-DATA-SENSITIVE": "RT-PRIVACY",
    "CND-CONSENT-BASED": "RT-REVOCATION",
    "CND-DELEGATED-AUTHORITY": "RT-AUTHORITY",
    "CND-DIVIDED-AUTHORITY": "RT-AUTHORITY",
    "CND-TWO-KEY": "RT-AUTHORITY",
    "CND-REGULATOR-OVERSIGHT": "RT-TRACE",
    "CND-EMERGENCY-POWERS": "RT-AUTHORITY",
    "CND-CUSTOMARY-AUTHORITY": "RT-RECORD-DISAGREEMENT",
    "CND-COMMUNITY-CONSENT": "RT-JUDGMENT",
    "CND-MULTILINGUAL": "RT-FIXTURE-LABEL",
}

ENTITY_NOUN = {
    "PARTY": "party", "SITE": "site", "ASSET": "asset", "DEVICE": "device", "LOT": "lot",
    "SPECIMEN": "specimen", "PARCEL": "parcel", "ROUTE": "route", "CONSIGNMENT": "consignment",
    "WORKORDER": "work order", "PERMIT": "permit", "CASEFILE": "case file", "COHORT": "cohort",
    "COLLECTION": "collection", "DATASET": "dataset", "MODEL": "model", "EVENT": "event",
    "ACCOUNT": "account", "VESSEL": "vessel", "RECORDSET": "record set",
}


def h(*parts):
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:16]


class Abort(Exception):
    def __init__(self, kind, detail):
        super().__init__(detail)
        self.kind = kind          # "contradiction" | "unresolved"
        self.detail = detail


# --------------------------------------------------------------------------
# case construction
# --------------------------------------------------------------------------


class Builder:
    def __init__(self, V, rng, rk_counts, idea_seen):
        self.V = V
        self.rng = rng
        self.rk_counts = rk_counts
        self.idea_seen = idea_seen

    # -- small helpers -----------------------------------------------------
    def pick(self, seq):
        return seq[self.rng.randrange(len(seq))]

    def pick_least_used(self, seq, counts):
        """Deterministic bias toward the least-used option, without ever excluding others."""
        if not seq:
            raise Abort("unresolved", "no option to pick")
        best = min(counts.get(x, 0) for x in seq)
        low = [x for x in seq if counts.get(x, 0) <= best + 2]
        if self.rng.random() < 0.8:
            return self.pick(sorted(low))
        return self.pick(seq)

    def candidates(self, axis, regime, sits, domain=None, gated=False):
        V = self.V
        base = V.axis_regime_domain[(axis, regime, domain)] if (gated and domain) \
            else V.axis_regime[(axis, regime)]
        out = [i for i in base if V.sit_ok(i, sits)]
        return out

    def preferred(self, axis, regime, sits, domain):
        """Domain-preferred axes: try domain-matching first, then any regime match."""
        pref = [i for i in self.V.axis_regime_domain[(axis, regime, domain)]
                if self.V.sit_ok(i, sits)]
        if pref:
            return pref, True
        allc = self.candidates(axis, regime, sits)
        if not allc:
            raise Abort("unresolved", "no %s ingredient for regime %s" % (axis, regime))
        return allc, False

    def repair(self, sits, pool_all, why):
        """Return (candidates, sits).  When no candidate admits the case's current
        situation tags, the case's situation set is widened by one tag taken from a
        candidate's own declared situations.  Widening never invalidates an earlier
        choice, because the situation rule is satisfied by any one matching tag."""
        ok = [i for i in pool_all if self.V.sit_ok(i, sits)]
        if ok:
            return ok, sits
        if not pool_all:
            raise Abort("contradiction", why)
        pick = self.pick(sorted(pool_all))
        newsit = self.pick(sorted(self.V.ing[pick]["situations"]))
        sits = sorted(set(sits) | {newsit})
        return [i for i in pool_all if self.V.sit_ok(i, sits)], sits

    # -- main --------------------------------------------------------------
    def build(self, case_no, regime, domain, flags, seed, phase):
        V, rng = self.V, self.rng
        B = V.bounds

        # ---------- situation ----------
        sits = set()
        for f in flags:
            if f in FLAG_SITUATION:
                sits.add(FLAG_SITUATION[f])
        pool = sorted(V.doc["situations"])
        g = 0
        while len(sits) < 3 and g < 60:
            sits.add(self.pick(pool))
            g += 1
        sits = sorted(sits)

        # ---------- need (domain gated) ----------
        needs, sits = self.repair(sits, V.axis_regime_domain[("need", regime, domain)],
                                  "no need admits regime %s and domain %s" % (regime, domain))
        if not needs:
            raise Abort("contradiction", "no need admits regime %s and domain %s"
                        % (regime, domain))
        need = self.pick_least_used(needs, self.idea_seen)
        need_ing = V.ing[need]

        # ---------- beneficiary (band must match the need) ----------
        bcands, bmatched = self.preferred("beneficiary", regime, sits, domain)
        bands = set(need_ing["beneficiary_bands"])
        band_ok = [b for b in bcands if V.ing[b]["scale_band"] in bands]
        if not band_ok:
            pool_all = [b for b in V.axis_regime[("beneficiary", regime)]
                        if V.ing[b]["scale_band"] in bands]
            band_ok, sits = self.repair(sits, pool_all,
                                        "no beneficiary in bands %s for regime %s"
                                        % (sorted(bands), regime))
            bmatched = False
        if not band_ok:
            raise Abort("contradiction",
                        "no beneficiary in bands %s for regime %s" % (sorted(bands), regime))
        beneficiary = self.pick(sorted(band_ok))

        # ---------- scale ----------
        scands, smatched = self.preferred("scale", regime, sits, domain)
        scale = self.pick(sorted(scands))
        self._sits = sits

        # ---------- components ----------
        n_comp = rng.randint(B["min_components"], B["max_components"])
        if "deep_nesting" in flags:
            n_comp = max(n_comp, 4)
        if "configurator" in flags:
            n_comp = min(n_comp, B["max_components"] - 1)
        max_depth = B["max_depth"]

        prod_pool, sits = self.repair(sits, V.axis_regime_domain[("product", regime, domain)],
                                      "no product admits %s/%s" % (regime, domain))
        if len(prod_pool) < 2:
            raise Abort("contradiction",
                        "fewer than two products admit %s/%s under the situation" % (regime, domain))
        if "configurator" in flags:
            gens = [p for p in prod_pool if V.ing[p].get("generator")]
            root_product = self.pick(sorted(gens)) if gens else self.pick_least_used(prod_pool, self.idea_seen)
        else:
            root_product = self.pick_least_used(prod_pool, self.idea_seen)

        comps = []
        parents = {}
        depths = {}
        cid0 = "C1"
        comps.append({"component_id": cid0, "product": root_product, "depth": 0})
        depths[cid0] = 0
        for i in range(2, n_comp + 1):
            cid = "C%d" % i
            eligible = [c["component_id"] for c in comps if depths[c["component_id"]] < max_depth]
            par = self.pick(sorted(eligible))
            depths[cid] = depths[par] + 1
            parents[cid] = par
            comps.append({"component_id": cid, "product": self.pick(sorted(prod_pool)),
                          "depth": depths[cid]})

        # ---------- component regimes (cross-regime where asked for) ----------
        n_cross = 0
        for c in comps:
            c["regime"] = regime
        if "cross_regime_component" in flags and len(comps) > 1:
            want = 2 if len(comps) >= 4 and rng.random() < 0.45 else 1
            others = [r for r in V.regimes if r != regime]
            for c in comps[1:]:
                if n_cross >= want:
                    break
                cand_r = self.pick(others)
                ok = [p for p in self.candidates("product", cand_r, sits, domain, gated=True)]
                if ok:
                    c["regime"] = cand_r
                    c["product"] = self.pick(sorted(ok))
                    n_cross += 1

        # ---------- generator / emitted-product normalisation ----------
        by_id = {c["component_id"]: c for c in comps}
        children = defaultdict(list)
        for cid_, par_ in sorted(parents.items()):
            children[par_].append(cid_)
        for c in comps:
            c.pop("emitted_by", None)
        for c in list(comps):
            if not V.ing[c["product"]].get("generator"):
                continue
            cid = c["component_id"]
            cand = [k for k in sorted(children[cid])
                    if not V.ing[by_id[k]["product"]].get("generator")
                    and not by_id[k].get("emitted_by")]
            if cand:
                by_id[cand[0]]["emitted_by"] = cid
                continue
            pcands = [p for p in self.candidates("product", c["regime"], sits, domain, gated=True)
                      if not V.ing[p].get("generator")]
            if pcands and len(comps) < B["max_components"] and depths[cid] < max_depth:
                ncid = "C%d" % (len(comps) + 1)
                depths[ncid] = depths[cid] + 1
                parents[ncid] = cid
                nc = {"component_id": ncid, "product": self.pick(sorted(pcands)),
                      "depth": depths[ncid], "regime": c["regime"], "emitted_by": cid}
                comps.append(nc)
                by_id[ncid] = nc
                children[cid].append(ncid)
                continue
            if pcands:
                c["product"] = self.pick(sorted(pcands))
            else:
                raise Abort("contradiction",
                            "a generator product cannot be paired with, or replaced by, a concrete one")

        root_product = comps[0]["product"]   # the normalisation pass may have demoted it

        # ---------- activities ----------
        for c in comps:
            acts, sits = self.repair(sits, V.axis_regime[("activity", c["regime"])],
                                     "no activity for regime %s" % c["regime"])
            if not acts:
                raise Abort("contradiction", "no activity for regime %s" % c["regime"])
            wants = {t.split(":", 1)[1] for t in V.ing[c["product"]]["prerequisites"]
                     if t.startswith("needs_form:")}
            fmatch = [a for a in acts
                      if {r.split(":", 1)[1] for r in V.ing[a]["results"]
                          if r.startswith("yields_form:")} & wants]
            pool_a = fmatch or acts
            dpref = [a for a in pool_a if domain in V.ing[a]["domains"]]
            c["activity"] = self.pick(sorted(dpref)) if (dpref and rng.random() < 0.7) \
                else self.pick(sorted(pool_a))
            c["activity_form_match"] = bool(
                {r.split(":", 1)[1] for r in V.ing[c["activity"]]["results"]
                 if r.startswith("yields_form:")} & wants)

        # ---------- resource pools ----------
        kinds = []
        for c in comps:
            for t in V.ing[c["activity"]]["prerequisites"]:
                if t.startswith("needs_capacity:"):
                    k = t.split(":", 1)[1]
                    if k not in kinds:
                        kinds.append(k)
        dropped_kinds = []
        if len(kinds) > B["max_resource_pools"]:
            dropped_kinds = kinds[B["max_resource_pools"]:]
            kinds = kinds[:B["max_resource_pools"]]
        pools = []
        for idx, k in enumerate(kinds):
            all_k = [i for i in V.pool_by_kind.get(k, []) if regime in V.ing[i]["regimes"]]
            if not all_k:
                dropped_kinds.append(k)
                continue
            opts, sits = self.repair(sits, all_k,
                                     "no pool of kind %s in regime %s" % (k, regime))
            if not opts:
                dropped_kinds.append(k)
                continue
            ing = V.ing[self.pick(sorted(opts))]
            lo, hi = ing["cap_range"]
            cap = round(rng.uniform(lo, hi), 1)
            pools.append({"pool_id": "P%d" % (idx + 1), "condition": ing["id"],
                          "resource_kind": k, "unit": ing["unit"], "capacity": cap})
        pool_by_kind = {p["resource_kind"]: p for p in pools}
        got_kinds = set(pool_by_kind)
        unmetered = sorted(set(dropped_kinds) | (set(kinds) - got_kinds))

        # ---------- allocations (constructive: draw inside what remains) ----------
        alloc = {p["pool_id"]: {} for p in pools}
        tightness = 0.93 if "shared_resource_contention" in flags else 0.62
        for p in pools:
            users = [c["component_id"] for c in comps
                     if ("needs_capacity:" + p["resource_kind"]) in V.ing[c["activity"]]["prerequisites"]]
            if not users:
                continue
            budget = p["capacity"] * tightness
            weights = [rng.uniform(0.5, 1.5) for _ in users]
            tot = sum(weights)
            for u, w in zip(users, weights):
                amt = round(budget * w / tot, 2)
                if amt <= 0:
                    amt = 0.01
                alloc[p["pool_id"]][u] = amt
            over = sum(alloc[p["pool_id"]].values()) - p["capacity"]
            if over > 0:
                raise Abort("contradiction", "allocation exceeds pool %s" % p["pool_id"])
        for c in comps:
            c["resource_use"] = []
            for p in pools:
                a = alloc[p["pool_id"]].get(c["component_id"])
                if a:
                    c["resource_use"].append({"pool": p["pool_id"], "amount": a, "unit": p["unit"]})

        # ---------- authority and environment ----------
        acands, sits = self.repair(sits, [i for i in V.authority if regime in V.ing[i]["regimes"]],
                                   "no authority condition for regime %s" % regime)
        if not acands:
            raise Abort("contradiction", "no authority condition for regime %s" % regime)
        if "divided_authority" in flags:
            forced = [i for i in FLAG_CONDITION["divided_authority"] if i in acands]
            authority = self.pick(sorted(forced)) if forced else self.pick(sorted(acands))
        else:
            authority = self.pick(sorted(acands))
        envs = [i for i in V.environment if regime in V.ing[i]["regimes"] and V.sit_ok(i, sits)]
        if "privacy_tension" in flags and "CND-DATA-SENSITIVE" in envs:
            env_sel = ["CND-DATA-SENSITIVE"]
            rest = [e for e in envs if e != "CND-DATA-SENSITIVE"]
            if rest and rng.random() < 0.6:
                env_sel.append(self.pick(sorted(rest)))
        else:
            k = rng.randint(1, 2) if envs else 0
            env_sel = sorted(rng.sample(envs, min(k, len(envs)))) if envs else []
        conditions = sorted(set([p["condition"] for p in pools] + [authority] + env_sel))

        # ---------- dynamics ----------
        dyns = set()
        for f in flags:
            for cand in FLAG_DYNAMIC.get(f, []):
                if regime in V.ing[cand]["regimes"] and V.sit_ok(cand, sits):
                    dyns.add(cand)
                    break
        dpool, sits = self.repair(sits, V.axis_regime[("dynamic", regime)],
                                  "no dynamic ingredient for regime %s" % regime)
        if not dpool:
            raise Abort("contradiction", "no dynamic ingredient for regime %s" % regime)
        guard = 0
        while len(dyns) < 3 and guard < 60:
            dyns.add(self.pick(dpool))
            guard += 1
        if len(dyns) < 2:
            raise Abort("contradiction", "fewer than two dynamics admissible in %s" % regime)
        dyns = sorted(dyns)

        # ---------- entities ----------
        ents = []
        etypes = []
        for c in comps:
            pass
        for iid in [need, root_product] + [c["product"] for c in comps]:
            t = V.ing[iid].get("identity_type")
            if t and t not in etypes:
                etypes.append(t)
        et_from_scale = {"micro": "SPECIMEN", "individual": "PARTY", "household": "PARTY",
                         "group": "COHORT", "local": "SITE", "device": "DEVICE",
                         "facility": "SITE", "landscape": "PARCEL", "enterprise": "PARTY",
                         "organization": "PARTY", "team": "PARTY", "community": "PARTY",
                         "regional": "SITE", "national": "PARTY", "international": "PARTY",
                         "network": "PARTY", "service": "MODEL"}
        base_t = et_from_scale.get(V.ing[scale]["band"], "SITE")
        etypes = ["PARTY"] + [t for t in ([base_t] + etypes) if t != "PARTY"]
        n_ent = min(B["max_entities"], max(3, min(len(etypes), rng.randint(3, 5))))
        for i in range(n_ent):
            t = etypes[i % len(etypes)]
            ents.append({"entity_id": "%s-%04d" % (t, rng.randrange(1000, 9999)),
                         "entity_type": t,
                         "label": "%s %d of %s" % (ENTITY_NOUN[t], i + 1, V.ing[scale]["label"])})
        seen_ids = set()
        for e in ents:
            while e["entity_id"] in seen_ids:
                e["entity_id"] = "%s-%04d" % (e["entity_type"], rng.randrange(1000, 9999))
            seen_ids.add(e["entity_id"])
        shared_entity = ents[0]["entity_id"]

        # ---------- relationships ----------
        rels = []
        rid = 0

        prec_adj = defaultdict(set)

        def reaches(x0, y0):
            stack, seen = [x0], set()
            while stack:
                x = stack.pop()
                if x == y0:
                    return True
                if x in seen:
                    continue
                seen.add(x)
                stack.extend(sorted(prec_adj[x]))
            return False

        def orient(frm, to):
            """Orientation that keeps the precedence graph acyclic, or None."""
            if not reaches(to, frm):
                return frm, to
            if not reaches(frm, to):
                return to, frm
            return None

        def add_rel(kind, frm, to, extra):
            nonlocal rid
            rid += 1
            r = {"rel_id": "L%d" % rid, "kind": kind, "from": frm, "to": to}
            r.update(extra)
            if "PRECEDENCE" in V.rk[kind]["checks"]:
                prec_adj[frm].add(to)
            self.rk_counts[kind] += 1
            rels.append(r)
            return r

        comp_by_id = {c["component_id"]: c for c in comps}
        transfers_in = defaultdict(list)

        for c in comps[1:]:
            cid = c["component_id"]
            par = parents[cid]
            if c.get("emitted_by") == par:
                add_rel("RK-EMIT", par, cid, {
                    "transfers": {"what": "a configuration drawn from the generator's rule set, and the "
                                          "artefact produced from it",
                                  "ingredient": c["product"], "quantity": None},
                    "enables": "the emitted product exists as a concrete deliverable rather than a description",
                    "changes": "the emitted product acquires acceptance conditions of its own",
                    "shares": "the generator's rule set and its version"})
                continue
            options = ["RK-INPUT", "RK-EMBED", "RK-COORD"]
            kind = self.pick_least_used(options, self.rk_counts)
            if kind == "RK-INPUT":
                form = self.pick(sorted(set(
                    t.split(":", 1)[1] for t in V.ing[comp_by_id[par]["activity"]]["prerequisites"]
                    if t.startswith("needs_form:")) or {"data"}))
                units = FORM_UNITS.get(form, ["U-COUNT"])
                u_src = self.pick(units)
                same_dim = [u for u in units
                            if V.units[u]["dimension"] == V.units[u_src]["dimension"]]
                u_dst = self.pick(same_dim) if (rng.random() < 0.3 and len(same_dim) > 1) else u_src
                qty = round(rng.uniform(2, 4000), 2)
                conv = None
                if u_dst != u_src:
                    conv = {"from_unit": u_src, "to_unit": u_dst,
                            "factor": V.units[u_src]["factor_to_base"] / V.units[u_dst]["factor_to_base"],
                            "converted_value": round(qty * V.units[u_src]["factor_to_base"]
                                                     / V.units[u_dst]["factor_to_base"], 4)}
                add_rel("RK-INPUT", cid, par, {
                    "transfers": {"what": "%s produced by %s and required by %s"
                                          % (form, V.ing[c["product"]]["label"],
                                             V.ing[comp_by_id[par]["activity"]]["label"]),
                                  "form": form, "ingredient": c["product"],
                                  "quantity": {"value": qty, "unit": u_src},
                                  "expects_dimension": V.units[u_dst]["dimension"],
                                  "receiving_unit": u_dst, "conversion": conv},
                    "enables": "%s can start, because its %s prerequisite is met"
                               % (par, form),
                    "changes": "the prerequisite set of %s becomes closed" % par,
                    "shares": None})
                transfers_in[par].append(form)
            elif kind == "RK-EMBED":
                add_rel("RK-EMBED", cid, par, {
                    "transfers": {"what": "the whole of %s, carrying its own acceptance conditions"
                                          % V.ing[c["product"]]["label"],
                                  "ingredient": c["product"], "quantity": None},
                    "enables": "%s can be delivered as one thing rather than two" % par,
                    "changes": "%s inherits the obligations of the embedded product" % par,
                    "shares": "the embedded product's identity %s" % shared_entity})
            else:
                add_rel("RK-COORD", cid, par, {
                    "transfers": {"what": "commitments and status about the joint outcome",
                                  "ingredient": need, "quantity": None},
                    "joint_outcome": "the %s that neither part delivers alone" % V.ing[need]["label"],
                    "enables": "a result attributable to the pair rather than to either part",
                    "changes": "attribution becomes joint",
                    "shares": "the joint outcome"})

        extra_kinds = ["RK-SHARE", "RK-COND", "RK-TIME", "RK-FEEDBACK", "RK-DELEGATE", "RK-CONSTRAIN"]
        n_extra = rng.randint(1, 3)
        if "multi_party_concurrency" in flags:
            n_extra = max(n_extra, 2)
        if "revision_after_partial_completion" in flags:
            n_extra = max(n_extra, 2)
        for _ in range(n_extra):
            if len(comps) < 2:
                break
            kind = self.pick_least_used(extra_kinds, self.rk_counts)
            a, b = rng.sample([c["component_id"] for c in comps], 2)
            if "PRECEDENCE" in V.rk[kind]["checks"]:
                o = orient(a, b)
                if o is None:
                    continue
                a, b = o
            fa, fb = (b, a) if kind == "RK-FEEDBACK" else (a, b)
            if any(x["kind"] == kind and x["from"] == fa and x["to"] == fb for x in rels):
                continue          # one relationship of a kind per ordered pair of parts
            if kind == "RK-SHARE":
                if pools and rng.random() < 0.6:
                    p = self.pick(pools)
                    add_rel("RK-SHARE", a, b, {
                        "transfers": {"what": "nothing is transferred; both parts draw on pool %s"
                                              % p["pool_id"], "ingredient": p["condition"],
                                      "quantity": None},
                        "shared_object": {"kind": "resource_pool", "ref": p["pool_id"]},
                        "enables": "neither part can be sized without the other",
                        "changes": "consumption by one reduces what remains for the other",
                        "shares": "capacity pool %s (%s %s)" % (p["pool_id"], p["capacity"], p["unit"])})
                else:
                    add_rel("RK-SHARE", a, b, {
                        "transfers": {"what": "nothing is transferred; both parts name the same entity",
                                      "ingredient": scale, "quantity": None},
                        "shared_object": {"kind": "entity", "ref": shared_entity},
                        "enables": "results from the two parts can be joined at all",
                        "changes": "a rename in one part silently breaks the other",
                        "shares": "entity identifier %s" % shared_entity})
            elif kind == "RK-COND":
                thr = round(rng.uniform(0.55, 0.97), 2)
                add_rel("RK-COND", a, b, {
                    "transfers": {"what": "a verdict and the values it was computed from",
                                  "ingredient": self.pick(dyns), "quantity": None},
                    "predicate": "proportion of %s records passing validation at %s is at least %s"
                                 % (V.ing[comp_by_id[a]["product"]]["label"], a, thr),
                    "else_branch": "%s is not started; the shortfall is recorded against %s with its reason"
                                   % (b, a),
                    "enables": "%s runs only when the evidence supports it" % b,
                    "changes": "%s becomes conditional rather than unconditional" % b,
                    "shares": None})
            elif kind == "RK-TIME":
                cad = self.pick(["daily", "weekly", "fortnightly", "monthly"])
                bound = {"daily": 2, "weekly": 10, "fortnightly": 20, "monthly": 45}[cad]
                add_rel("RK-TIME", a, b, {
                    "transfers": {"what": "a dated exchange repeated on a %s cadence" % cad,
                                  "ingredient": self.pick(dyns), "quantity": None},
                    "cadence": cad, "staleness_bound": {"value": bound, "unit": "U-DAY"},
                    "enables": "%s works from current rather than founding-day values" % b,
                    "changes": "the exchanged state becomes perishable",
                    "shares": "one clock and one staleness convention"})
            elif kind == "RK-FEEDBACK":
                cyc = rng.randint(1, V.bounds["max_feedback_cycles"])
                add_rel("RK-FEEDBACK", b, a, {
                    "transfers": {"what": "a measured discrepancy and the revision it implies",
                                  "ingredient": self.pick(dyns), "quantity": None},
                    "cycle_bound": cyc,
                    "stop_criterion": "the discrepancy falls below the stated tolerance, or %d cycles "
                                      "are exhausted and the residual is published" % cyc,
                    "enables": "%s is corrected after it was thought finished" % a,
                    "changes": "completed work is revised rather than replaced",
                    "shares": None})
            elif kind == "RK-DELEGATE":
                add_rel("RK-DELEGATE", a, b, {
                    "transfers": {"what": "a scoped authorisation derived from %s"
                                          % V.ing[authority]["label"],
                                  "ingredient": authority, "quantity": None},
                    "scope": "acts on %s only, and only for the purpose of %s"
                             % (shared_entity, V.ing[need]["label"]),
                    "expiry_day": None,
                    "enables": "%s may act without the holder of the authority being present" % b,
                    "changes": "who may act, and who answers for the act",
                    "shares": "accountability for the delegated act"})
            else:
                lim_unit = self.pick(["U-KW", "U-M3", "U-PERSON-HOUR", "U-CU", "U-COUNT"])
                add_rel("RK-CONSTRAIN", a, b, {
                    "transfers": {"what": "an operating envelope published by %s" % a,
                                  "ingredient": self.pick(sorted(conditions)), "quantity": None},
                    "limit": {"value": round(rng.uniform(5, 900), 1), "unit": lim_unit},
                    "edge_behaviour": "on reaching the limit %s holds at the last admissible value and "
                                      "raises the condition rather than continuing" % b,
                    "enables": "%s can act without waiting for permission each time" % b,
                    "changes": "the admissible operating range of %s narrows" % b,
                    "shares": "the limit value"})

        # ---------- schedule ----------
        preds = defaultdict(list)
        for r in rels:
            if "PRECEDENCE" in V.rk[r["kind"]]["checks"]:
                preds[r["to"]].append(r["from"])
        order = []
        temp = {c["component_id"]: 0 for c in comps}
        stack = sorted(temp)

        def visit(nid, seen):
            if nid in seen:
                raise Abort("contradiction", "cycle through %s" % nid)
            if nid in order:
                return
            seen = seen | {nid}
            for p in sorted(preds[nid]):
                visit(p, seen)
            order.append(nid)

        for nid in sorted(temp):
            visit(nid, frozenset())

        for c in comps:
            band = V.ing[c["activity"]]["duration_band"]
            lo, hi = DURATION_BAND[band]
            c["duration_days"] = rng.randint(lo, hi)
        sched = {}
        for nid in order:
            start = 0
            for p in preds[nid]:
                start = max(start, sched[p][1])
            c = comp_by_id[nid]
            sched[nid] = (start, start + c["duration_days"])
        finish = max(v[1] for v in sched.values())
        slack = rng.randint(2, 30)
        deadline = finish + slack
        window = deadline + rng.randint(3, 40)
        if window > V.bounds["case_window_days"]["max"]:
            raise Abort("unresolved", "case window %d days exceeds the bound" % window)
        if window < V.bounds["case_window_days"]["min"]:
            window = V.bounds["case_window_days"]["min"]
        for c in comps:
            s, f = sched[c["component_id"]]
            c["start_day"], c["finish_day"] = s, f
        for r in rels:
            if r["kind"] == "RK-DELEGATE":
                r["expiry_day"] = min(deadline, sched[r["to"]][1] + rng.randint(1, 10))

        # ---------- inputs and prerequisite closure ----------
        inputs = []
        assumptions = ["Capacity of kind %s is assumed available in the setting and is not metered by "
                       "this case; no pool is declared for it." % k for k in unmetered]
        n_in = 0
        for c in comps:
            cid = c["component_id"]
            c["inputs"] = []
            c["prerequisites"] = list(V.ing[c["activity"]]["prerequisites"])
            got = set(transfers_in.get(cid, []))
            for t in c["prerequisites"]:
                if not t.startswith("needs_form:"):
                    continue
                form = t.split(":", 1)[1]
                if form in got:
                    continue
                cands = [i for i in V.input_form_regime.get((form, c["regime"]), [])
                         if V.sit_ok(i, sits)]
                if not cands:
                    assumptions.append(
                        "The %s input that %s requires is assumed available in the setting and is not "
                        "specified here; no vocabulary input of that form is admissible in %s under "
                        "these situation tags." % (form, cid, V.doc["regimes"][c["regime"]]["label"]))
                    c.setdefault("assumed_forms", []).append(form)
                    continue
                dpref = [i for i in cands if domain in V.ing[i]["domains"]]
                iid = self.pick(sorted(dpref)) if (dpref and rng.random() < 0.75) else self.pick(sorted(cands))
                n_in += 1
                ing = V.ing[iid]
                unit = ing.get("unit") or self.pick(FORM_UNITS.get(form, ["U-COUNT"]))
                want_t = ing.get("identity_type")
                same = [e for e in ents if e["entity_type"] == want_t]
                ent = self.pick(same) if same else self.pick(ents)
                rec = {"input_id": "I%d" % n_in, "ingredient": iid, "form": form,
                       "identity": ent["entity_id"],
                       "quantity": {"value": round(rng.uniform(1, 5200), 2), "unit": unit},
                       "state_at_day_zero": self.pick([
                           "held by the party named above and not yet checked",
                           "partially complete: about %d%% of the set exists" % rng.randint(15, 80),
                           "current as at day 0 and refreshed on the stated cadence",
                           "inherited from the previous arrangement, provenance incomplete"]),
                       "fixture": {"hypothetical": True,
                                   "note": "compact synthetic fixture, labelled hypothetical; not an "
                                           "observed record"},
                       "used_by": [cid]}
                inputs.append(rec)
                c["inputs"].append(rec["input_id"])
                got.add(form)

        # ---------- deliverables ----------
        deliverables = []
        dnum = 0
        deliver_ids = ["C1"] + [c["component_id"] for c in comps if c.get("emitted_by")]
        for c in comps:
            if c["component_id"] not in deliver_ids and rng.random() < 0.35:
                deliver_ids.append(c["component_id"])
        for cid in sorted(set(deliver_ids), key=lambda x: int(x[1:])):
            dnum += 1
            c = comp_by_id[cid]
            ing = V.ing[c["product"]]
            deliverables.append({
                "deliverable_id": "D%d" % dnum, "component": cid, "product": c["product"],
                "form": ing["form"],
                "title": "%s for %s" % (ing["label"][0].upper() + ing["label"][1:],
                                        V.ing[scale]["label"]),
                "quantity": {"value": rng.randint(1, 12), "unit": "U-COUNT"},
                "due_day": c["finish_day"],
                "acceptance_ids": []})
            c["deliverable"] = True

        # ---------- acceptance conditions ----------
        acc_pool, sits = self.repair(sits, V.axis_regime[("acceptance", regime)],
                                     "no acceptance ingredient for regime %s" % regime)
        if not acc_pool:
            raise Abort("contradiction", "no acceptance ingredient for regime %s" % regime)
        machine_pool = [a for a in acc_pool if V.ing[a]["check_mode"] == "machine"]
        acceptance = []
        anum = 0
        for d in deliverables:
            k = rng.randint(1, 3)
            chosen = []
            if machine_pool:
                chosen.append(self.pick(sorted(machine_pool)))
            g = 0
            while len(chosen) < k and g < 40:
                cand = self.pick(acc_pool)
                if cand not in chosen:
                    chosen.append(cand)
                g += 1
            for a in sorted(chosen):
                anum += 1
                ai = V.ing[a]
                thr = None
                if ai["check_mode"] == "machine":
                    thr = {"value": round(rng.uniform(0.8, 0.999), 3), "basis": "proportion"} \
                        if "PCT" in a or "COVERAGE" in a else \
                        {"value": round(rng.uniform(1, 96), 2), "basis": "stated tolerance or bound"}
                acceptance.append({
                    "ac_id": "AC%d" % anum, "ingredient": a, "deliverable": d["deliverable_id"],
                    "check_mode": ai["check_mode"],
                    "statement": "%s, for %s." % (ai["label"][0].upper() + ai["label"][1:], d["title"]),
                    "observable": ai["observable"],
                    "threshold": thr,
                    "judgment_needed": ai["judgment_needed"]})
                d["acceptance_ids"].append("AC%d" % anum)

        # ---------- atomic requirements ----------
        reqs = []

        def add_req(ingredient, template, text, scope, check, source):
            reqs.append({"req_id": "R%d" % (len(reqs) + 1), "ingredient": ingredient,
                         "template": template, "text": text, "scope": scope,
                         "check": check, "source": source})

        for c in comps:
            cid = c["component_id"]
            for t in c["prerequisites"]:
                if t.startswith("needs_form:"):
                    form = t.split(":", 1)[1]
                    add_req(c["activity"], "RT-INPUT-PRESENT",
                            V.rt["RT-INPUT-PRESENT"].format(part=cid, what="the required %s input" % form),
                            cid, "machine", "inherited")
            for ru in c["resource_use"]:
                add_req([p for p in pools if p["pool_id"] == ru["pool"]][0]["condition"],
                        "RT-CAPACITY-RESPECTED",
                        V.rt["RT-CAPACITY-RESPECTED"].format(part=cid, amount=ru["amount"],
                                                             unit=V.units[ru["unit"]]["display"],
                                                             pool_id=ru["pool"]),
                        cid, "machine", "inherited")
            add_req(c["product"], "RT-DEADLINE",
                    V.rt["RT-DEADLINE"].format(part=cid, day=c["finish_day"]),
                    cid, "machine", "inherited")
        for r in rels:
            k = r["kind"]
            if k == "RK-INPUT":
                q = r["transfers"]["quantity"]
                add_req(r["transfers"]["ingredient"], "RT-UNIT-CARRIED",
                        V.rt["RT-UNIT-CARRIED"].format(part=r["from"]) +
                        " The transfer on %s is %s %s and is received as %s."
                        % (r["rel_id"], q["value"], V.units[q["unit"]]["display"],
                           V.units[r["transfers"]["receiving_unit"]]["display"]),
                        r["rel_id"], "machine", "combination")
            elif k == "RK-TIME":
                add_req(r["transfers"]["ingredient"], "RT-STALENESS",
                        V.rt["RT-STALENESS"].format(part=r["to"], what="the exchanged state",
                                                    bound=r["staleness_bound"]["value"],
                                                    unit="days"),
                        r["rel_id"], "machine", "combination")
            elif k == "RK-DELEGATE":
                add_req(authority, "RT-AUTHORITY",
                        V.rt["RT-AUTHORITY"].format(part=r["to"], authority=V.ing[authority]["label"]) +
                        " The delegation expires on day %d." % r["expiry_day"],
                        r["rel_id"], "machine", "combination")
            elif k == "RK-SHARE":
                so = r["shared_object"]
                if so["kind"] == "entity":
                    add_req(scale, "RT-IDENTITY-STABLE",
                            V.rt["RT-IDENTITY-STABLE"].format(part="%s and %s" % (r["from"], r["to"]),
                                                              entity=so["ref"]),
                            r["rel_id"], "machine", "combination")
                else:
                    add_req([p for p in pools if p["pool_id"] == so["ref"]][0]["condition"],
                            "RT-CAPACITY-RESPECTED",
                            "The combined draw of %s and %s on pool %s shall not exceed its capacity at "
                            "any point in the window." % (r["from"], r["to"], so["ref"]),
                            r["rel_id"], "machine", "combination")
            elif k == "RK-COORD":
                add_req(need, "RT-JOINT-OUTCOME",
                        V.rt["RT-JOINT-OUTCOME"].format(part=r["from"], outcome=r["joint_outcome"]),
                        r["rel_id"], "human", "combination")
            elif k == "RK-EMIT":
                add_req(comp_by_id[r["from"]]["product"], "RT-EMIT-CONCRETE",
                        V.rt["RT-EMIT-CONCRETE"].format(part=r["from"]) +
                        " The concrete product is %s." % r["to"],
                        r["rel_id"], "machine", "combination")
            elif k == "RK-EMBED":
                add_req(comp_by_id[r["from"]]["product"], "RT-INHERIT",
                        V.rt["RT-INHERIT"].format(part=r["to"]),
                        r["rel_id"], "machine", "combination")
            elif k == "RK-CONSTRAIN":
                add_req(r["transfers"]["ingredient"], "RT-LIMIT-RESPECT",
                        V.rt["RT-LIMIT-RESPECT"].format(part=r["to"], amount=r["limit"]["value"],
                                                        unit=V.units[r["limit"]["unit"]]["display"],
                                                        source=r["from"]),
                        r["rel_id"], "machine", "combination")
            elif k == "RK-FEEDBACK":
                add_req(r["transfers"]["ingredient"], "RT-RESUME",
                        "Revision of %s driven by %s shall stop after %d cycles and publish the residual."
                        % (r["to"], r["from"], r["cycle_bound"]),
                        r["rel_id"], "machine", "combination")
            elif k == "RK-COND":
                add_req(r["transfers"]["ingredient"], "RT-JUDGMENT",
                        "The verdict gating %s shall be recorded with the values it was computed from "
                        "and the branch actually taken." % r["to"],
                        r["rel_id"], "mixed", "combination")
        for d in sorted(dyns):
            if d in DYNAMIC_REQUIREMENT:
                tpl, _ = DYNAMIC_REQUIREMENT[d]
                txt = V.rt[tpl]
                fills = {"part": "the case as a whole", "what": V.ing[d]["label"],
                         "bound": 7, "unit": "days", "day": deadline,
                         "entity": shared_entity, "amount": 1, "pool_id": "P1",
                         "authority": V.ing[authority]["label"], "outcome": V.ing[need]["label"],
                         "source": "C1"}
                try:
                    text = txt.format(**fills)
                except KeyError:
                    text = txt
                add_req(d, tpl, text, "case", "mixed", "combination")
        for cnd in sorted(conditions):
            if cnd in CONDITION_REQUIREMENT:
                tpl = CONDITION_REQUIREMENT[cnd]
                fills = {"part": "the case as a whole", "what": "the affected records",
                         "authority": V.ing[authority]["label"], "bound": 5, "unit": "days",
                         "day": deadline, "entity": shared_entity, "amount": 1, "pool_id": "P1",
                         "outcome": V.ing[need]["label"], "source": "C1"}
                try:
                    text = V.rt[tpl].format(**fills)
                except KeyError:
                    text = V.rt[tpl]
                add_req(cnd, tpl, text, "case", "mixed", "combination")
        add_req(need, "RT-FIXTURE-LABEL",
                V.rt["RT-FIXTURE-LABEL"].format(part="the case as a whole"),
                "case", "machine", "combination")

        # ---------- global constraints ----------
        gcs = []

        def add_gc(tpl, params, text=None):
            V.ct[tpl]["text"].format(**params)   # fails loudly if the params do not fill the template
            gcs.append({"gc_id": "G%d" % (len(gcs) + 1), "template": tpl, "params": params})

        for p in pools:
            add_gc("CT-CAPACITY_BOUND", {"pool_id": p["pool_id"], "resource": p["resource_kind"],
                                         "capacity": p["capacity"],
                                         "unit": V.units[p["unit"]]["display"]})
        add_gc("CT-SCHEDULE_FEASIBLE", {"deadline_day": deadline})
        add_gc("CT-IDENTITY_UNIQUE", {})
        add_gc("CT-ACYCLIC", {})
        add_gc("CT-DEPTH_BOUND", {"max_depth": V.bounds["max_depth"]})
        add_gc("CT-PREREQ_CLOSED", {})
        add_gc("CT-ACCEPTANCE_COVER", {})
        add_gc("CT-REGIME_ADMISSIBLE", {})
        add_gc("CT-SITUATION_ADMISSIBLE", {})
        add_gc("CT-UNIT_DECLARED", {})
        add_gc("CT-HYPOTHETICAL_LABELLED", {})
        if any(r["kind"] == "RK-INPUT" for r in rels):
            add_gc("CT-DIMENSION_MATCH", {})
        if any(V.ing[c["product"]].get("generator") for c in comps):
            add_gc("CT-GENERATOR_EMITS", {})
        if any(r["kind"] == "RK-DELEGATE" for r in rels):
            add_gc("CT-AUTHORITY_SCOPED", {})
        if any(r["kind"] == "RK-TIME" for r in rels):
            add_gc("CT-STALENESS_BOUND", {})
        if "CND-DATA-SENSITIVE" in conditions or "S-PRIVACY-SENSITIVE" in sits:
            add_gc("CT-PII_MINIMISED", {})
        if "DYN-IRREVERSIBLE-STEP" in dyns or "DYN-RECOVERY-COMPENSATE" in dyns:
            add_gc("CT-REVERSIBILITY_DECLARED", {})
        if "CND-MULTILINGUAL" in conditions or "S-MULTILINGUAL" in sits:
            add_gc("CT-LANGUAGE_PARITY", {})
        if "S-SAFETY-CRITICAL" in sits:
            add_gc("CT-SAFETY_INTERLOCK", {})
        if any(a["check_mode"] != "machine" for a in acceptance):
            add_gc("CT-JUDGMENT_RECORDED", {})
        if any(d in ("DYN-VERSION-BOUNDARY", "DYN-REGULATION-CHANGE") for d in dyns):
            add_gc("CT-VERSION_STAMPED", {})

        # ---------- signatures ----------
        idea_key = h(need, root_product, tuple(sorted(c["product"] for c in comps)),
                     tuple(sorted(set(r["kind"] for r in rels))))
        shape = tuple(sorted((r["kind"], depths[r["from"]], depths[r["to"]]) for r in rels))
        structure_key = h(len(comps), max(depths.values()), shape)
        situation_key = h(tuple(sits), tuple(sorted(conditions)), tuple(dyns))
        variant_key = h(idea_key, structure_key, regime, domain)
        full_key = h(idea_key, structure_key, situation_key, regime, domain, beneficiary, scale)

        branching = Counter(parents.values())
        coupling = len(rels)

        cross_regimes = sorted(set(c["regime"] for c in comps if c["regime"] != regime))

        case = {
            "case_id": "UC-%05d" % case_no,
            "generation_version": V.doc["generation_version"],
            "dictionary_version": V.doc["dictionary_version"],
            "primary_domain": domain,
            "regime": regime,
            "situation": {
                "tags": sits,
                "scale": scale,
                "conditions": conditions,
                "authority": authority,
                "resource_pools": pools,
                "dynamics": dyns,
                "window_days": window,
                "deadline_day": deadline,
                "domain_matched_axes": sorted(
                    [a for a, m in (("beneficiary", bmatched), ("scale", smatched)) if m]),
            },
            "beneficiary": {
                "ingredient": beneficiary,
                "scale_band": V.ing[beneficiary]["scale_band"],
                "party_id": ents[0]["entity_id"],
                "statement": "%s, at the scale of %s."
                             % (V.ing[beneficiary]["label"][0].upper() + V.ing[beneficiary]["label"][1:],
                                V.ing[scale]["label"]),
            },
            "need_and_context": {
                "need": need,
                "purpose_class": need_ing["purpose_class"],
                "statement": "%s." % (need_ing["label"][0].upper() + need_ing["label"][1:]),
                "context": "%s The setting is %s: %s The people who carry it are %s: %s "
                           "What makes this situation particular: %s."
                           % (need_ing["meaning"], V.ing[scale]["label"], V.ing[scale]["meaning"],
                              V.ing[beneficiary]["label"], V.ing[beneficiary]["meaning"],
                              "; ".join(V.doc["situations"][s].rstrip(".").lower() for s in sits)),
                "hypothetical": True,
            },
            "required_deliverables": deliverables,
            "concrete_inputs": inputs,
            "entities": ents,
            "components": comps,
            "component_relationships": rels,
            "atomic_requirements_with_stable_ids": [
                dict(r, req_id="UC-%05d/%s" % (case_no, r["req_id"])) for r in reqs],
            "global_constraints": gcs,
            "acceptance_conditions": acceptance,
            "assumptions_and_provenance": {
                "assumptions": assumptions + [
                    "Every entity identifier, quantity and date in this record is a hypothetical "
                    "fixture minted by the generator; none refers to a real party, site or dataset.",
                    "Mathematical consistency of the allocation and the schedule under these "
                    "hypothetical values does not establish real-world suitability.",
                ],
                "ingredients_used": sorted(set(
                    [beneficiary, need, scale, root_product, authority]
                    + conditions + dyns
                    + [c["product"] for c in comps] + [c["activity"] for c in comps]
                    + [i["ingredient"] for i in inputs]
                    + [a["ingredient"] for a in acceptance])),
                "provenance_note": "Resolve each ingredient id in dictionary.json for its provenance "
                                   "record; ingredient provenance is one of an inventory item, an ISIC "
                                   "or FORD code, or an authored reason.",
                "open_questions": [
                    "Whether %s is the right party to carry the obligation created by %s."
                    % (V.ing[beneficiary]["label"], V.ing[authority]["label"]),
                ],
            },
            "validation_status_and_evidence": {
                "structural_completeness": "all required record fields populated by construction",
                "encoded_constraints": "satisfied by construction; re-derived independently by checker.py "
                                       "from dictionary.json and this record alone",
                "plausibility_review": "not_reviewed",
                "witness": {
                    "resource_allocation": {p["pool_id"]: {
                        "capacity": p["capacity"], "unit": p["unit"],
                        "allocated": alloc[p["pool_id"]],
                        "total": round(sum(alloc[p["pool_id"]].values()), 2)} for p in pools},
                    "schedule": {k: {"start_day": v[0], "finish_day": v[1]} for k, v in sorted(sched.items())},
                    "deadline_day": deadline,
                },
                "witness_establishes": [
                    "CT-CAPACITY_BOUND for every declared pool, at the stated capacities",
                    "CT-SCHEDULE_FEASIBLE against the stated deadline, given the declared precedences",
                ],
                "witness_does_not_establish": [
                    "that the stated capacities, durations or quantities are the real ones",
                    "that the need, beneficiary and component relationships are sensible in the world",
                ],
                "remaining_judgments": sorted(set(
                    [a["judgment_needed"] for a in acceptance if a["judgment_needed"]])) or
                    ["none beyond the encoded checks"],
            },
            "diversity_signature": {
                "idea_key": idea_key, "structure_key": structure_key,
                "situation_key": situation_key, "variant_key": variant_key, "full_key": full_key,
                "purpose_class": need_ing["purpose_class"],
                "root_product_form": V.ing[root_product]["form"],
                "component_forms": sorted(V.ing[c["product"]]["form"] for c in comps),
                "relationship_kinds": sorted(set(r["kind"] for r in rels)),
                "depth": max(depths.values()), "components": len(comps),
                "branching": max(branching.values()) if branching else 0,
                "coupling": coupling,
                "cross_regime_components": cross_regimes,
                "flags": sorted(flags),
            },
            "seed_or_replay_reference": {
                "seed": seed, "case_index": case_no, "phase": phase,
                "stratum": "%s|%s" % (regime, domain),
                "replay": "python3 generate.py --dictionary dictionary.json --seed %d --count <n> "
                          "--out cases.jsonl --record generation_record.json" % seed,
            },
        }
        return case


# --------------------------------------------------------------------------
# batch driver
# --------------------------------------------------------------------------


def plan_strata(V, count, rng):
    """Phase 1 fills every regime x domain cell above its floor; phase 2 is
    directed at underrepresented higher-order combinations."""
    isic = [d for d in V.domains if d.startswith("ISIC-")]
    ford = [d for d in V.domains if d.startswith("FORD-")]
    scale = count / 1000.0
    base_isic = max(15, int(round(16 * scale * 1000 / max(count, 1) * scale)))
    # keep it simple and explicit: floors are stated per 1000 and scaled linearly
    base_isic = max(3, int(round(16 * (count / 5000.0))))
    base_ford = max(6, int(round(30 * (count / 5000.0))))
    plan = []
    for r in V.regimes:
        for d in isic:
            plan += [(r, d, "phase1")] * base_isic
        for d in ford:
            plan += [(r, d, "phase1")] * base_ford
    return plan, base_isic, base_ford


HIGHER_ORDER = [
    ["uncertain_evidence", "shared_resource_contention", "revision_after_partial_completion"],
    ["divided_authority", "irreversible_effect", "cross_regime_component"],
    ["interruption_recovery", "scarce_capacity", "multi_party_concurrency"],
    ["configurator", "cross_regime_component", "uncertain_evidence"],
    ["privacy_tension", "divided_authority", "public_facing"],
    ["long_horizon", "revision_after_partial_completion", "uncertain_evidence"],
    ["deep_nesting", "shared_resource_contention", "cross_regime_component"],
    ["irreversible_effect", "interruption_recovery", "uncertain_evidence"],
    ["configurator", "deep_nesting", "divided_authority"],
    ["multi_party_concurrency", "privacy_tension", "scarce_capacity"],
]


def draw_flags(rng, phase, cell_counts, flag_counts, forced=None):
    if forced:
        return sorted(set(forced))
    if phase == "phase1":
        n = rng.choice([1, 2, 2, 3])
        pool = sorted(FLAGS, key=lambda f: (flag_counts[f], f))[:max(6, n + 4)]
        return sorted(rng.sample(pool, min(n, len(pool))))
    combo = HIGHER_ORDER[rng.randrange(len(HIGHER_ORDER))]
    extra = sorted(FLAGS, key=lambda f: (flag_counts[f], f))[:4]
    out = set(combo)
    if rng.random() < 0.5:
        out.add(rng.choice(extra))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dictionary", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--record", required=True)
    ap.add_argument("--review-out", default=None)
    args = ap.parse_args()

    t0 = time.time()
    with open(args.dictionary, encoding="utf-8") as fh:
        raw = fh.read()
    doc = json.loads(raw)
    V = Vocab(doc)
    dict_sha = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    if args.seed is None:
        seed = int.from_bytes(os.urandom(8), "big")
        seed_source = "os.urandom(8) drawn once at the start of this run"
    else:
        seed = args.seed
        seed_source = "supplied on the command line (originally drawn from os.urandom(8))"
    rng = random.Random(seed)
    t_setup = time.time() - t0

    review_path = args.review_out or os.path.join(os.path.dirname(os.path.abspath(args.out)),
                                                  "review_needed.jsonl")
    t1 = time.time()
    plan, base_isic, base_ford = plan_strata(V, args.count, rng)
    rng.shuffle(plan)
    phase1 = plan[:args.count]
    n_phase2 = max(0, args.count - len(phase1))

    rk_counts = Counter({k: 0 for k in sorted(V.rk)})
    idea_seen = Counter()
    flag_counts = Counter({f: 0 for f in FLAGS})
    cell_counts = Counter()
    seen_full = set()
    variant_counts = Counter()
    idea_struct = set()

    builder = Builder(V, rng, rk_counts, idea_seen)

    admitted = []
    review = []
    stats = Counter()
    fail_examples = []

    def attempt(regime, domain, phase, case_no, forced=None):
        flags = draw_flags(rng, phase, cell_counts, flag_counts, forced)
        return builder.build(case_no, regime, domain, flags, seed, phase), flags

    queue = list(phase1)
    # phase 2: directed at cells that are still light and at higher-order flag combinations
    case_no = 0
    order_idx = 0
    while len(admitted) < args.count:
        if order_idx < len(queue):
            regime, domain, phase = queue[order_idx]
            order_idx += 1
        else:
            phase = "phase2"
            light = sorted(((cell_counts[(r, d)], r, d) for r in V.regimes for d in V.domains))
            k = min(24, len(light))
            _, regime, domain = light[rng.randrange(k)]
        placed = False
        for _attempt in range(V.bounds["max_backtracks_per_case"]):
            stats["attempted"] += 1
            case_no += 1
            try:
                case, flags = attempt(regime, domain, phase, len(admitted) + 1)
            except Abort as e:
                stats[e.kind] += 1
                if len(fail_examples) < 40:
                    fail_examples.append({"kind": e.kind, "detail": e.detail,
                                          "stratum": "%s|%s" % (regime, domain)})
                continue
            fk = case["diversity_signature"]["full_key"]
            if fk in seen_full:
                stats["duplicate"] += 1
                continue
            # review-needed diversion: proposals that exceed the available checks
            reasons = []
            if not any(a["check_mode"] == "machine" for a in case["acceptance_conditions"]):
                reasons.append("no machine-checkable acceptance condition: all evidence for this "
                               "proposal rests on human judgment")
            assumed_deliverables = sorted(c["component_id"] for c in case["components"]
                                          if c.get("assumed_forms") and c.get("deliverable"))
            if assumed_deliverables:
                reasons.append("a prerequisite of a deliverable-producing part (%s) is met only by a "
                               "recorded assumption, not by a supplied input, so the job cannot be "
                               "fully understood from the record"
                               % ", ".join(assumed_deliverables))
            novelty = h(case["need_and_context"]["purpose_class"],
                        case["diversity_signature"]["root_product_form"],
                        tuple(sorted(set([case["regime"]] +
                                         case["diversity_signature"]["cross_regime_components"]))))
            if len(case["diversity_signature"]["cross_regime_components"]) >= 2 and \
                    novelty not in idea_struct:
                reasons.append("unfamiliar cross-regime combination: two or more components sit in "
                               "regimes other than the case regime and this purpose/form/regime "
                               "combination has not occurred before in this batch")
            idea_struct.add(novelty)
            if reasons:
                case["validation_status_and_evidence"]["plausibility_review"] = "review_needed"
                case["validation_status_and_evidence"]["review_reasons"] = reasons
                case["case_id"] = "RV-%05d" % (len(review) + 1)
                case["seed_or_replay_reference"]["case_index"] = len(review) + 1
                review.append(case)
                stats["review_needed"] += 1
                continue
            seen_full.add(fk)
            variant_counts[case["diversity_signature"]["variant_key"]] += 1
            idea_seen[case["need_and_context"]["need"]] += 1
            for f in case["diversity_signature"]["flags"]:
                flag_counts[f] += 1
            cell_counts[(case["regime"], case["primary_domain"])] += 1
            admitted.append(case)
            stats["admitted"] += 1
            placed = True
            break
        if not placed:
            stats["stratum_exhausted"] += 1
        if case_no > args.count * 60:
            break

    t_gen = time.time() - t1

    t2 = time.time()
    with open(args.out, "w", encoding="utf-8") as fh:
        for c in admitted:
            fh.write(json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n")
    with open(review_path, "w", encoding="utf-8") as fh:
        for c in review:
            fh.write(json.dumps(c, sort_keys=True, ensure_ascii=False) + "\n")
    t_write = time.time() - t2

    # ---- diversity accounting ----
    per_regime = Counter(c["regime"] for c in admitted)
    per_domain = Counter(c["primary_domain"] for c in admitted)
    per_cell = Counter((c["regime"], c["primary_domain"]) for c in admitted)
    per_kind = Counter()
    cross_regime_cases = 0
    for c in admitted:
        for k in set(r["kind"] for r in c["component_relationships"]):
            per_kind[k] += 1
        if c["diversity_signature"]["cross_regime_components"]:
            cross_regime_cases += 1
    floors = {
        "per_regime_floor": int(round(60 * args.count / 1000.0)),
        "per_isic_section_floor": int(round(20 * args.count / 1000.0)),
        "per_ford_field_floor": int(round(40 * args.count / 1000.0)),
        "per_relationship_kind_floor": int(round(30 * args.count / 1000.0)),
        "cross_regime_case_floor": int(round(100 * args.count / 1000.0)),
        "per_cell_floor": 15,
    }
    shortfalls = []
    for r in V.regimes:
        if per_regime[r] < floors["per_regime_floor"]:
            shortfalls.append({"kind": "regime", "key": r, "have": per_regime[r],
                               "floor": floors["per_regime_floor"]})
    for d in V.domains:
        fl = floors["per_isic_section_floor"] if d.startswith("ISIC-") else floors["per_ford_field_floor"]
        if per_domain[d] < fl:
            shortfalls.append({"kind": "domain", "key": d, "have": per_domain[d], "floor": fl})
    for k in sorted(V.rk):
        if per_kind[k] < floors["per_relationship_kind_floor"]:
            shortfalls.append({"kind": "relationship_kind", "key": k, "have": per_kind[k],
                               "floor": floors["per_relationship_kind_floor"]})
    if cross_regime_cases < floors["cross_regime_case_floor"]:
        shortfalls.append({"kind": "cross_regime_cases", "key": "any",
                           "have": cross_regime_cases, "floor": floors["cross_regime_case_floor"]})
    for r in V.regimes:
        for d in V.domains:
            if per_cell[(r, d)] < floors["per_cell_floor"]:
                shortfalls.append({"kind": "cell", "key": "%s|%s" % (r, d),
                                   "have": per_cell[(r, d)], "floor": floors["per_cell_floor"]})

    def sha(path):
        return hashlib.sha256(open(path, "rb").read()).hexdigest()

    here = os.path.dirname(os.path.abspath(args.out))
    prog_sha = {}
    for name in ("generate.py", "checker.py", "expand.py"):
        p = os.path.join(here, name)
        if os.path.exists(p):
            prog_sha[name] = sha(p)

    record = {
        "generation_version": doc["generation_version"],
        "dictionary_version": doc["dictionary_version"],
        "program_version": GEN_PROGRAM_VERSION,
        "seed": seed,
        "randomness": {
            "source": "operating-system entropy via os.urandom(8), used once to seed a recorded "
                      "pseudo-random generator",
            "seed_origin": seed_source,
            "generator": "python random.Random (Mersenne Twister), one instance for the whole batch",
            "determinism": "same dictionary, seed and count reproduce cases.jsonl byte for byte",
        },
        "requested_count": args.count,
        "counts": {
            "attempted": stats["attempted"],
            "admitted": stats["admitted"],
            "duplicate_rejected": stats["duplicate"],
            "contradiction_rejected": stats["contradiction"],
            "unresolved_bounded_search": stats["unresolved"],
            "review_needed": stats["review_needed"],
            "strata_exhausted": stats["stratum_exhausted"],
            "substantive_use_cases": len(set((c["diversity_signature"]["idea_key"],
                                              c["diversity_signature"]["structure_key"])
                                             for c in admitted)),
            "distinct_idea_keys": len(set(c["diversity_signature"]["idea_key"] for c in admitted)),
            "parameter_or_situation_variants": sum(v - 1 for v in variant_counts.values() if v > 1),
        },
        "sampling_policy": {
            "kind": "stratified, constraint-conditioned and adaptively weighted; not uniform",
            "phase1": "every regime x primary_domain cell is filled to a base allocation: %d cases per "
                      "ISIC cell and %d per FORD cell, scaled linearly from the per-1000 floors"
                      % (base_isic, base_ford),
            "phase2": "remaining draws are directed at the lightest cells and at declared higher-order "
                      "flag combinations",
            "higher_order_combinations": HIGHER_ORDER,
            "relationship_kind_balancing": "when several relationship kinds are admissible the least "
                                           "used is preferred with probability 0.8",
            "domain_gating": doc["compatibility_rules"]["domain_rule"],
            "dedup_rule": "a case is rejected when its full_key (idea, structure, situation, regime, "
                          "domain, beneficiary, scale) has already been admitted",
            "review_diversion": "three rules divert a proposal to review_needed.jsonl instead of "
                                "admitting it: (1) it has no machine-checkable acceptance condition, "
                                "so all its evidence would rest on human judgment; (2) a "
                                "deliverable-producing part has a form prerequisite met only by a "
                                "recorded assumption rather than a supplied input; (3) it is a "
                                "first-of-kind combination with two or more cross-regime components. "
                                "Diverted proposals are retained in full and are not counted as "
                                "admitted cases",
            "phase1_planned": len(phase1), "phase2_planned": n_phase2,
        },
        "diversity": {
            "floors_applied": floors,
            "per_regime": dict(sorted(per_regime.items())),
            "per_primary_domain": dict(sorted(per_domain.items())),
            "per_relationship_kind_cases": dict(sorted(per_kind.items())),
            "relationship_instances": dict(sorted(rk_counts.items())),
            "cross_regime_cases": cross_regime_cases,
            "cells_below_floor": sum(1 for r in V.regimes for d in V.domains
                                     if per_cell[(r, d)] < floors["per_cell_floor"]),
            "min_cell": min(per_cell[(r, d)] for r in V.regimes for d in V.domains),
            "purpose_classes": dict(sorted(Counter(
                c["need_and_context"]["purpose_class"] for c in admitted).items())),
            "root_product_forms": dict(sorted(Counter(
                c["diversity_signature"]["root_product_form"] for c in admitted).items())),
            "depth_distribution": dict(sorted(Counter(
                c["diversity_signature"]["depth"] for c in admitted).items())),
            "component_count_distribution": dict(sorted(Counter(
                c["diversity_signature"]["components"] for c in admitted).items())),
            "flag_distribution": dict(sorted(flag_counts.items())),
            "shortfalls": shortfalls,
        },
        "timings_seconds": {
            "setup": round(t_setup, 3),
            "generation": round(t_gen, 3),
            "writing": round(t_write, 3),
            "throughput_cases_per_second": round(len(admitted) / max(t_gen, 1e-9), 1),
        },
        "artifact_sha256": {
            "dictionary.json": dict_sha,
            os.path.basename(args.out): sha(args.out),
            os.path.basename(review_path): sha(review_path),
        },
        "program_sha256": prog_sha,
        "failure_examples": fail_examples[:20],
        "notes": [
            "Case records contain no wall-clock time, path or environment value; all dates are "
            "relative day numbers from day 0 of the case window.",
            "Timings in this record are measured wall-clock and therefore differ between runs; "
            "cases.jsonl does not.",
        ],
    }
    with open(args.record, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")

    print("admitted %d / requested %d  (attempted %d, dup %d, contradiction %d, unresolved %d, "
          "review %d)" % (stats["admitted"], args.count, stats["attempted"], stats["duplicate"],
                          stats["contradiction"], stats["unresolved"], stats["review_needed"]))
    print("setup %.2fs  generation %.2fs  writing %.2fs" % (t_setup, t_gen, t_write))
    if shortfalls:
        print("SHORTFALLS: %d" % len(shortfalls))
        for s in shortfalls[:12]:
            print("  ", s)


if __name__ == "__main__":
    main()
