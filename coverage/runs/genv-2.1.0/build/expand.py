#!/usr/bin/env python3
"""Loss-free expander: turns a compact case record into a readable specification.

    python3 expand.py --dictionary dictionary.json --cases cases.jsonl --out expanded.md
    python3 expand.py --dictionary dictionary.json --cases cases.jsonl --out sample.md \
        --ids UC-00001,UC-00002

Every dictionary reference in the record is resolved here, so the rendered text
carries the meaning that the record only points at.  No language model runs.
"""
import argparse, json, os, time


def prov_str(p):
    if p["source"].startswith("assets/"):
        return "%s — item %r" % (p["source"], p["item"])
    if p["source"] in ("ISIC", "FORD"):
        return "%s %s" % (p["source"], p["code"])
    return "authored — %s" % p["reason"]


def render(D, case):
    ing = D["ingredients"]
    units = D["units"]
    rk = D["relationship_kinds"]
    ct = D["constraint_templates"]
    L = []
    w = L.append

    def lab(i):
        return ing[i]["label"] if i in ing else i

    def unit(u):
        return units[u]["display"] if u in units else u

    def qty(q):
        if not q:
            return "—"
        return "%s %s" % (q["value"], unit(q["unit"]))

    cid_map = {c["component_id"]: c for c in case["components"]}
    need = ing[case["need_and_context"]["need"]]
    ben = ing[case["beneficiary"]["ingredient"]]
    scale = ing[case["situation"]["scale"]]

    w("## %s — %s" % (case["case_id"], case["need_and_context"]["statement"].rstrip(".")))
    w("")
    w("*%s · %s · regime: %s · generation %s, dictionary %s*"
      % (case["primary_domain"], D["domains"][case["primary_domain"]]["label"],
         D["regimes"][case["regime"]]["label"], case["generation_version"],
         case.get("dictionary_version", "?")))
    w("")

    w("**Beneficiary.** %s (`%s`) — %s Scale band: %s. Named party in this case: `%s`."
      % (ben["label"], ben["id"], ben["meaning"], ben["scale_band"],
         case["beneficiary"]["party_id"]))
    w("")
    w("**Need and context.** %s (`%s`, purpose class *%s*). %s"
      % (need["label"][0].upper() + need["label"][1:], need["id"], need["purpose_class"],
         case["need_and_context"]["context"]))
    w("")
    w("**Situation.** At the scale of %s (`%s`): %s The case window is %d days and the deadline "
      "for the last deliverable is day %d."
      % (scale["label"], scale["id"], scale["meaning"], case["situation"]["window_days"],
         case["situation"]["deadline_day"]))
    w("")
    w("- Situation tags: " + "; ".join("**%s** — %s" % (s, D["situations"][s].rstrip("."))
                                       for s in case["situation"]["tags"]))
    w("- Conditions: " + "; ".join("`%s` %s (%s)" % (c, lab(c), ing[c]["kind"])
                                   for c in case["situation"]["conditions"]))
    w("- Time, uncertainty, state and change: " +
      "; ".join("`%s` %s — %s" % (d, lab(d), ing[d]["meaning"].rstrip("."))
                for d in case["situation"]["dynamics"]))
    if case["situation"]["resource_pools"]:
        w("- Shared resource pools:")
        for p in case["situation"]["resource_pools"]:
            w("    - `%s` %s of %s, capacity **%s %s** (`%s`)"
              % (p["pool_id"], p["resource_kind"], lab(p["condition"]), p["capacity"],
                 unit(p["unit"]), p["condition"]))
    w("")

    w("### Required deliverables")
    w("")
    for d in case["required_deliverables"]:
        pi = ing[d["product"]]
        w("- **%s** (`%s`, form *%s*) — %s Quantity %s, due day %d, produced by component `%s`. "
          "Acceptance: %s."
          % (d["title"], d["product"], d["form"], pi["meaning"], qty(d["quantity"]),
             d["due_day"], d["component"], ", ".join(d["acceptance_ids"]) or "none"))
    w("")

    w("### Concrete inputs")
    w("")
    if not case["concrete_inputs"]:
        w("- No vocabulary input was admissible for this setting; see the recorded assumptions.")
    for i in case["concrete_inputs"]:
        ii = ing[i["ingredient"]]
        w("- `%s` **%s** (form *%s*, `%s`) — %s Identity `%s`; quantity %s; state at day 0: %s. "
          "Used by %s. *Hypothetical fixture.*"
          % (i["input_id"], ii["label"], i["form"], i["ingredient"], ii["meaning"],
             i["identity"], qty(i["quantity"]), i["state_at_day_zero"], ", ".join(i["used_by"])))
    w("")
    w("Entities named in this case: " +
      "; ".join("`%s` (%s) %s" % (e["entity_id"], e["entity_type"], e["label"])
                for e in case["entities"]) + ".")
    w("")

    w("### Components")
    w("")
    for c in case["components"]:
        pi, ai = ing[c["product"]], ing[c["activity"]]
        extra = []
        if c["regime"] != case["regime"]:
            extra.append("sits in a different regime: %s" % D["regimes"][c["regime"]]["label"])
        if c.get("emitted_by"):
            extra.append("emitted by `%s`" % c["emitted_by"])
        if c.get("deliverable"):
            extra.append("is a required deliverable")
        if c.get("assumed_forms"):
            extra.append("assumes availability of: " + ", ".join(c["assumed_forms"]))
        w("- `%s` (depth %d) **%s** produced by *%s*. %s %s Days %d–%d (%d days).%s"
          % (c["component_id"], c["depth"], pi["label"], ai["label"], pi["meaning"],
             ai["meaning"], c["start_day"], c["finish_day"], c["duration_days"],
             (" " + "; ".join(extra) + ".") if extra else ""))
        if c.get("resource_use"):
            w("    - draws " + ", ".join("%s %s from `%s`" % (r["amount"], unit(r["unit"]), r["pool"])
                                         for r in c["resource_use"]))
        if c.get("prerequisites"):
            w("    - prerequisites: " + ", ".join("`%s`" % t for t in c["prerequisites"]))
    w("")

    w("### Component relationships")
    w("")
    for r in case["component_relationships"]:
        k = rk[r["kind"]]
        t = r.get("transfers") or {}
        bits = ["**`%s` %s → %s** (`%s`, %s)" % (r["rel_id"], r["from"], r["to"], r["kind"],
                                                 k["label"])]
        bits.append("*Transfers:* %s" % t.get("what", "—"))
        if t.get("quantity"):
            bits.append("*Quantity:* %s" % qty(t["quantity"]))
            if t.get("receiving_unit"):
                bits.append("*Received as:* %s (dimension %s)"
                            % (unit(t["receiving_unit"]), t.get("expects_dimension")))
            if t.get("conversion"):
                cv = t["conversion"]
                bits.append("*Conversion:* x%.6g, giving %s %s"
                            % (cv["factor"], cv["converted_value"], unit(cv["to_unit"])))
        for key, name in (("enables", "Enables"), ("changes", "Changes"), ("shares", "Shares"),
                          ("joint_outcome", "Joint outcome"), ("predicate", "Predicate"),
                          ("else_branch", "Otherwise"), ("cadence", "Cadence"),
                          ("cycle_bound", "Cycle bound"), ("stop_criterion", "Stops when"),
                          ("scope", "Scope"), ("expiry_day", "Expires on day"),
                          ("edge_behaviour", "At the limit")):
            if r.get(key):
                bits.append("*%s:* %s" % (name, r[key]))
        if r.get("staleness_bound"):
            bits.append("*Stale after:* %s" % qty(r["staleness_bound"]))
        if r.get("limit"):
            bits.append("*Limit:* %s" % qty(r["limit"]))
        if r.get("shared_object"):
            bits.append("*Shared object:* %s `%s`" % (r["shared_object"]["kind"],
                                                      r["shared_object"]["ref"]))
        w("- " + " ".join(bits))
    w("")

    w("### Atomic requirements")
    w("")
    for q in case["atomic_requirements_with_stable_ids"]:
        w("- `%s` (%s, scope `%s`, %s check, %s) %s"
          % (q["req_id"], q["template"], q["scope"], q["check"], q["source"], q["text"]))
    w("")

    w("### Global constraints (obligations of the combination)")
    w("")
    for g in case["global_constraints"]:
        tpl = ct[g["template"]]
        try:
            text = tpl["text"].format(**g["params"])
        except Exception:
            text = tpl["text"]
        w("- `%s` **%s** — %s (%s, %s)"
          % (g["gc_id"], g["template"], text, tpl["severity"],
             "machine-checkable" if tpl["machine_checkable"] else "needs human judgment"))
    w("")

    w("### Acceptance conditions (what the requested product must show)")
    w("")
    for a in case["acceptance_conditions"]:
        ai = ing[a["ingredient"]]
        thr = ""
        if a.get("threshold"):
            thr = " Threshold: %s (%s)." % (a["threshold"]["value"], a["threshold"]["basis"])
        jn = (" Judgment needed: %s." % a["judgment_needed"]) if a.get("judgment_needed") else ""
        w("- `%s` (for %s, %s check, `%s`) %s Observable: %s.%s%s"
          % (a["ac_id"], a["deliverable"], a["check_mode"], a["ingredient"], a["statement"],
             a["observable"], thr, jn))
    w("")

    w("### Assumptions and provenance")
    w("")
    for x in case["assumptions_and_provenance"]["assumptions"]:
        w("- %s" % x)
    for x in case["assumptions_and_provenance"].get("open_questions", []):
        w("- *Open question:* %s" % x)
    w("")
    w("Vocabulary used, with provenance:")
    for i in case["assumptions_and_provenance"]["ingredients_used"]:
        if i in ing:
            w("- `%s` (%s) %s — provenance: %s" % (i, ing[i]["axis"], ing[i]["label"],
                                                   prov_str(ing[i]["provenance"])))
    w("")

    v = case["validation_status_and_evidence"]
    w("### Validation status and evidence (about this specification, not about the product)")
    w("")
    w("- Structural completeness: %s" % v["structural_completeness"])
    w("- Encoded constraints: %s" % v["encoded_constraints"])
    w("- Plausibility review of the need and the relationships: **%s**" % v["plausibility_review"])
    for rr in v.get("review_reasons", []):
        w("    - review reason: %s" % rr)
    wit = v.get("witness") or {}
    if wit.get("resource_allocation"):
        w("- Retained satisfying assignment (resource allocation):")
        for pid in sorted(wit["resource_allocation"]):
            rec = wit["resource_allocation"][pid]
            w("    - `%s`: %s of %s %s allocated as %s"
              % (pid, rec["total"], rec["capacity"], unit(rec["unit"]),
                 ", ".join("%s=%s" % (k, rec["allocated"][k]) for k in sorted(rec["allocated"]))))
    if wit.get("schedule"):
        w("- Retained schedule: " + ", ".join(
            "%s %d–%d" % (k, wit["schedule"][k]["start_day"], wit["schedule"][k]["finish_day"])
            for k in sorted(wit["schedule"])) + " against deadline day %d" % wit["deadline_day"])
    w("- The witness establishes: " + "; ".join(v["witness_establishes"]) + ".")
    w("- The witness does not establish: " + "; ".join(v["witness_does_not_establish"]) + ".")
    w("- Remaining judgments: " + "; ".join(v["remaining_judgments"]) + ".")
    w("")

    s = case["diversity_signature"]
    w("### Diversity signature and replay")
    w("")
    w("- purpose class `%s`; root product form `%s`; component forms %s"
      % (s["purpose_class"], s["root_product_form"], ", ".join(s["component_forms"])))
    w("- relationship kinds %s; depth %d; %d components; branching %d; coupling %d"
      % (", ".join(s["relationship_kinds"]), s["depth"], s["components"], s["branching"],
         s["coupling"]))
    w("- cross-regime components: %s; sampling flags: %s"
      % (", ".join(s["cross_regime_components"]) or "none", ", ".join(s["flags"]) or "none"))
    w("- keys: idea `%s`, structure `%s`, situation `%s`, variant `%s`, full `%s`"
      % (s["idea_key"], s["structure_key"], s["situation_key"], s["variant_key"], s["full_key"]))
    rp = case["seed_or_replay_reference"]
    w("- replay: seed `%s`, case index %s, stratum `%s`, phase `%s`; `%s`"
      % (rp["seed"], rp["case_index"], rp["stratum"], rp["phase"], rp["replay"]))
    w("")
    w("---")
    w("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dictionary", required=True)
    ap.add_argument("--cases", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids", default=None)
    args = ap.parse_args()

    t0 = time.time()
    with open(args.dictionary, encoding="utf-8") as fh:
        D = json.load(fh)
    want = None
    if args.ids:
        want = [x.strip() for x in args.ids.split(",") if x.strip()]
    t_setup = time.time() - t0

    t1 = time.time()
    n_read = n_written = n_failed = 0
    failures = []
    chosen = {}
    with open(args.out, "w", encoding="utf-8") as out:
        out.write("# Expanded case specifications\n\n")
        out.write("Generated by expand.py from `%s` and `%s`. Every dictionary reference in the "
                  "records below is resolved in place, so each section stands alone.\n\n"
                  % (os.path.basename(args.cases), os.path.basename(args.dictionary)))
        if want:
            out.write("Subset: %s\n\n" % ", ".join(want))
        out.write("---\n\n")
        for line in open(args.cases, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            case = json.loads(line)
            n_read += 1
            if want is not None:
                if case["case_id"] not in want:
                    continue
                chosen[case["case_id"]] = case
                continue
            try:
                out.write(render(D, case))
                n_written += 1
            except Exception as exc:            # a render failure must be visible, not silent
                n_failed += 1
                if len(failures) < 20:
                    failures.append({"case_id": case.get("case_id"), "error": repr(exc)})
        if want is not None:
            for cid in want:
                if cid in chosen:
                    try:
                        out.write(render(D, chosen[cid]))
                        n_written += 1
                    except Exception as exc:
                        n_failed += 1
                        failures.append({"case_id": cid, "error": repr(exc)})
                else:
                    n_failed += 1
                    failures.append({"case_id": cid, "error": "not found in the cases file"})
    t_render = time.time() - t1
    print("expanded %d of %d cases into %s (%d failed); setup %.2fs, rendering %.2fs"
          % (n_written, n_read if want is None else len(want), args.out, n_failed,
             t_setup, t_render))
    for f in failures:
        print("  FAILED:", f)


if __name__ == "__main__":
    main()
