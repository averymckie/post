#!/usr/bin/env python3
"""Post-process a derive run into the gap register and coverage tables.

Usage: python3 analyze.py RUN_DIR DERIVE_DIR [--label strict|lenient]
Reads RUN_DIR/{cases.jsonl,ingredients.json,bridge.json} and DERIVE_DIR/{derivations.jsonl,summary.json,invariance.json};
writes DERIVE_DIR/analysis.json and DERIVE_DIR/analysis.md.
"""
import argparse, json, os
from collections import Counter, defaultdict, OrderedDict

ap = argparse.ArgumentParser()
ap.add_argument('run'); ap.add_argument('derive'); ap.add_argument('--label', default='')
a = ap.parse_args()
cases = {json.loads(l)['case_id']: json.loads(l) for l in open(os.path.join(a.run, 'cases.jsonl'))}
ings = {i['id']: i for i in json.load(open(os.path.join(a.run, 'ingredients.json')))}
bridge = json.load(open(os.path.join(a.run, 'bridge.json')))
recs = [json.loads(l) for l in open(os.path.join(a.derive, 'derivations.jsonl'))]
summary = json.load(open(os.path.join(a.derive, 'summary.json')))
inv = json.load(open(os.path.join(a.derive, 'invariance.json')))
atoms_by = defaultdict(list)
for at in bridge['atoms']:
    atoms_by[(at['position'], at['ingredient'])].append(at)
only_thin = set()
for (pos, ing), lst in atoms_by.items():
    if all(x['strength'] == 'thin' for x in lst):
        only_thin.add(ing)

def label(ing):
    i = ings.get(ing)
    return (i.get('label') or ing) if i else ing

# verdicts by stratifier
by = {}
for strat in ('regime', 'domain', 'scale_band', 'beneficiary'):
    d = defaultdict(Counter)
    for r in recs:
        key = r.get(strat) or cases[r['case_id']].get(strat)
        d[key][r['verdict']] += 1
    by[strat] = OrderedDict((k, dict(v)) for k, v in sorted(d.items(), key=lambda kv: -sum(kv[1].values())))

# gap register
gaps = defaultdict(lambda: OrderedDict(count=0, cases=set()))
ing_of = {}
for cid, c in cases.items():
    for r in c['requirements']: ing_of[(cid, r['id'])] = r['ing']
    for r in c['constraints']: ing_of[(cid, r['id'])] = r['ing']
    for r in c['acceptance']: ing_of[(cid, r['id'])] = r['ing']
    for r in c['relationships']: ing_of[(cid, r['id'])] = r['kind']
for r in recs:
    for u in r.get('unexplained', []):
        item = ing_of.get((r['case_id'], u['item']), u['item'])
        g = gaps[(u['kind'], item)]
        g['count'] += 1
        g['cases'].add(r['case_id'])
register = []
for (kind, item), g in gaps.items():
    axis = (ings.get(item) or {}).get('axis') or ('family' if item.startswith('F') and len(item) == 3 else kind)
    if kind in ('deliverable', 'input', 'requirement', 'constraint', 'acceptance', 'situation', 'relationship', 'endpoint') and item in only_thin:
        cls = 'model gap candidate: no counterpart (only thin bridge atoms)'
    elif kind == 'grounding':
        cls = 'strictness: family realized without any bridged input (name-only fit)'
    elif kind == 'input':
        cls = 'model gap candidate: input consumed by no family in the chain'
    elif kind == 'requirement':
        cls = 'operation not performed by any chain family (activity/product mismatch or gap)'
    elif kind == 'endpoint':
        cls = 'relationship endpoint unexplained (follows from an unexplained product)'
    elif kind == 'acceptance_qualifier':
        cls = 'no qualifying operation (O16) in the chain'
    else:
        cls = 'unexplained: ' + kind
    register.append(OrderedDict(kind=kind, item=item, label=label(item), axis=axis, count=g['count'], distinct_cases=len(g['cases']),
                                examples=sorted(g['cases'])[:5], classification=cls))
register.sort(key=lambda x: -x['count'])
class_counts = Counter()
class_cases = defaultdict(set)
for x in register:
    class_counts[x['classification']] += x['count']
    class_cases[x['classification']] |= set(gaps[(x['kind'], x['item'])]['cases'])
# proof gaps by realizing family with products
pg = defaultdict(Counter)
for r in recs:
    prod_by_fam = defaultdict(set)
    for rz in r.get('realized', []):
        prod_by_fam[rz['family']].add(rz['deliverable'])
    for f in r.get('proof_gaps', []):
        for p in prod_by_fam.get(f, {'(none)'}):
            pg[f][p] += 1
proof_gaps = OrderedDict((f, OrderedDict(total=sum(c.values()), products=dict(c.most_common()))) for f, c in sorted(pg.items(), key=lambda kv: -sum(kv[1].values())))
# open inputs by family/role
oi = Counter()
for r in recs:
    for o in r.get('open_inputs', []):
        oi[(o['family'], o['role'])] += 1
open_inputs = [dict(family=f, role=ro, count=n) for (f, ro), n in oi.most_common(30)]
# cases fully explained but unanchored: which products lack anchors
inv_summary = OrderedDict()
for name, detail in inv['detail'].items():
    cnt = Counter(x['status'] for x in detail)
    ex = [x for x in detail if x['status'] != 'HOLDS'][:6]
    inv_summary[name] = OrderedDict(groups=len(detail), status=dict(cnt), examples=[OrderedDict(key=x['key'], status=x['status'], per_stratum={k: [(v['families'], v['verdict']) for v in vs] for k, vs in x['per_stratum'].items()}) for x in ex])
out = OrderedDict(label=a.label, cases=len(recs), verdicts=summary['verdicts'], timed_out=summary['timed_out'],
                  by_stratifier=by, gap_classes=OrderedDict((k, dict(occurrences=v, distinct_cases=len(class_cases[k]))) for k, v in class_counts.most_common()),
                  gap_register=register[:200], only_thin_ingredients=sorted(only_thin),
                  proof_gaps_by_family=proof_gaps, open_inputs_top=open_inputs,
                  never_reached=OrderedDict(families=summary['families_never_reached'], operations=summary['operations_never_reached'],
                                            compositions=summary['compositions_never_reached'], variation_rules=summary['variation_rules_never_reached'],
                                            axis_values=summary['axis_values_never_reached'], proofs_never_reached=summary['proofs_never_reached']),
                  invariance=inv_summary)
json.dump(out, open(os.path.join(a.derive, 'analysis.json'), 'w'), indent=1)
md = []
md.append('### %s reading: %d cases' % (a.label or 'derive', len(recs)))
md.append('')
md.append('| verdict | cases |'); md.append('|---|---|')
for k, v in sorted(summary['verdicts'].items(), key=lambda kv: -kv[1]):
    md.append('| %s | %d |' % (k, v))
md.append('')
md.append('Verdicts by regime:'); md.append(''); md.append('| regime | COVERED | PARTIAL | UNEXPLAINED | NO-WITNESS |'); md.append('|---|---|---|---|---|')
for k, v in by['regime'].items():
    md.append('| %s | %d | %d | %d | %d |' % (k, v.get('COVERED', 0), v.get('PARTIAL', 0), v.get('UNEXPLAINED', 0), v.get('NO-WITNESS', 0)))
md.append(''); md.append('Verdicts by scale band:'); md.append(''); md.append('| scale band | COVERED | PARTIAL | UNEXPLAINED |'); md.append('|---|---|---|---|')
for k, v in by['scale_band'].items():
    md.append('| %s | %d | %d | %d |' % (k, v.get('COVERED', 0), v.get('PARTIAL', 0), v.get('UNEXPLAINED', 0)))
md.append(''); md.append('Gap classes:'); md.append(''); md.append('| class | occurrences | distinct cases |'); md.append('|---|---|---|')
for k, v in out['gap_classes'].items():
    md.append('| %s | %d | %d |' % (k, v['occurrences'], v['distinct_cases']))
md.append(''); md.append('Gap register (top 40):'); md.append(''); md.append('| kind | item | axis | cases | classification |'); md.append('|---|---|---|---|---|')
for x in register[:40]:
    md.append('| %s | %s: %s | %s | %d | %s |' % (x['kind'], x['item'], x['label'], x['axis'], x['distinct_cases'], x['classification']))
md.append(''); md.append('Proof gaps by realizing family (product: cases):'); md.append('')
for f, v in list(proof_gaps.items())[:20]:
    md.append('- %s (%d): %s' % (f, v['total'], ', '.join('%s %d' % (p, n) for p, n in list(v['products'].items())[:6])))
md.append(''); md.append('Never reached: families %s; operations %s; compositions %s; variation rules %s; axis values %d of %d; proofs never anchored %d.' % (
    out['never_reached']['families'], out['never_reached']['operations'], out['never_reached']['compositions'], out['never_reached']['variation_rules'],
    len(out['never_reached']['axis_values']), sum(len(ax['values']) for ax in json.load(open(os.path.join(a.run, '..', '..', 'model', 'catalogue.json')))['axes'].values()), out['never_reached']['proofs_never_reached']))
md.append(''); md.append('Regime and scale invariance (same semantic combination in several strata):'); md.append('')
for name, v in inv_summary.items():
    md.append('- %s: %d groups, %s' % (name, v['groups'], v['status']))
open(os.path.join(a.derive, 'analysis.md'), 'w').write('\n'.join(md) + '\n')
print('\n'.join(md[:12]))
print('...')
print('written', os.path.join(a.derive, 'analysis.md'))

# ---------------------------------------------------------------------------------------------
# Second pass: explanations behind the three mechanical gap classes, and product-level invariance.
cat = json.load(open(os.path.join(a.run, '..', '..', 'model', 'catalogue.json')))
fam_out = defaultdict(set); fam_in = defaultdict(set)
for f in cat['families'].values():
    for r in f['output_roles'] or []: fam_out[f['id']].add(r)
    for r in f['input_roles'] or []: fam_in[f['id']].add(r)
in_targets = defaultdict(set)
for at in bridge['atoms']:
    if at['position'] == 'in' and at['status'] == 'accepted':
        in_targets[at['ingredient']].add(at['target'])
req_targets = defaultdict(set)
for at in bridge['atoms']:
    if at['position'] == 'req' and at['status'] == 'accepted':
        req_targets[at['ingredient']].add(at['target'])
fam_ops = {f['id']: set(f['operation_classes'] or []) for f in cat['families'].values()}

missing_edges = Counter(); no_inbound = Counter(); grounding_examples = defaultdict(list)
unconsumed = defaultdict(Counter)
unperformed = defaultdict(Counter)
for r in recs:
    c = cases[r['case_id']]
    fam_of_prod = {rz['deliverable']: rz['family'] for rz in r.get('realized', [])}
    chain = set(r.get('families', []))
    for u in r.get('unexplained', []):
        if u['kind'] == 'grounding':
            F = u['item']
            prods = [p for p, f in fam_of_prod.items() if f == F]
            inbound = [(rel['from'], rel['kind']) for rel in c['relationships'] if rel['to'] in prods and rel['kind'] in ('RK-INPUT', 'RK-EMBED', 'RK-EMIT')]
            if not inbound:
                no_inbound[(F, tuple(sorted(prods)))] += 1
            for src, kind in inbound:
                G = fam_of_prod.get(src)
                if G and G != F and not (fam_out[G] & fam_in[F]):
                    missing_edges[(G, F, kind)] += 1
                    if len(grounding_examples[(G, F)]) < 3:
                        grounding_examples[(G, F)].append('%s: %s -> %s' % (r['case_id'], src, prods[0] if prods else '?'))
        elif u['kind'] == 'input':
            unconsumed[u['item']][tuple(sorted(chain))] += 1
        elif u['kind'] == 'requirement':
            act = ing_of.get((r['case_id'], u['item']), u['item'])
            prods_of_act = sorted(set(p['product'] for p in c.get('parts', []) if p['activity'] == act))
            fams = sorted(set(fam_of_prod.get(p, '-') for p in prods_of_act))
            unperformed[act][(tuple(sorted(req_targets.get(act, ()))), tuple(fams))] += 1

def top(counter, n):
    return [dict(key=list(k) if isinstance(k, tuple) else k, count=v) for k, v in counter.most_common(n)]
port_gaps = [OrderedDict(from_family=g, to_family=f, relationship=k, cases=n, examples=grounding_examples[(g, f)]) for (g, f, k), n in missing_edges.most_common(40)]
composed_without_inputs = [OrderedDict(family=f, products=list(p), cases=n) for (f, p), n in no_inbound.most_common(25)]
unconsumed_report = []
for ing, cnt in sorted(unconsumed.items(), key=lambda kv: -sum(kv[1].values())):
    roles_ = sorted(in_targets.get(ing, ()))
    consumers = sorted(set(f for ro in roles_ for f in cat['indexes']['roles'][ro]['consumed_by']))
    unconsumed_report.append(OrderedDict(input=ing, label=label(ing), cases=sum(cnt.values()), bridged_roles=roles_, consuming_families=consumers,
                                         chains_seen=[dict(families=list(k), count=v) for k, v in cnt.most_common(4)]))
unperformed_report = []
for act, cnt in sorted(unperformed.items(), key=lambda kv: -sum(kv[1].values())):
    unperformed_report.append(OrderedDict(activity=act, label=label(act), cases=sum(cnt.values()),
                                          patterns=[dict(operations=list(k[0]), product_families=list(k[1]), count=v) for k, v in cnt.most_common(4)]))
# product-level invariance: same product realized by the same family across strata
inv2 = OrderedDict()
for key_field in ('semantic_key', 'coarse_key'):
    for strat in ('regime', 'scale_band'):
        groups = defaultdict(list)
        for r in recs:
            if r.get(key_field) and r.get(strat):
                groups[r[key_field]].append(r)
        cnt = Counter(); examples = []
        for key, rs in groups.items():
            strata = set(r[strat] for r in rs)
            if len(strata) < 2:
                continue
            shared = set.intersection(*[set(cases[r['case_id']]['deliverables']) for r in rs])
            if key_field == 'coarse_key':
                shared = {key.split('|', 1)[1]} & shared if '|' in key else shared
            status = 'HOLDS'
            per = {}
            for r in rs:
                fam_of_prod = {rz['deliverable']: rz['family'] for rz in r.get('realized', [])}
                per.setdefault(r[strat], []).append({p: fam_of_prod.get(p) for p in shared})
            for p in shared:
                fams = set()
                unexpl = False
                for st, lst in per.items():
                    for m in lst:
                        if m[p] is None: unexpl = True
                        else: fams.add(m[p])
                if unexpl and fams:
                    status = 'BREAKS'; break
                if len(fams) > 1:
                    status = 'STRAINS'
            cnt[status] += 1
            if status != 'HOLDS' and len(examples) < 8:
                examples.append(OrderedDict(key=key, status=status, strata=sorted(strata), per_stratum={k: v[:2] for k, v in per.items()}))
        inv2[key_field + '_by_' + strat] = OrderedDict(groups=sum(cnt.values()), status=dict(cnt), examples=examples)
out['port_gaps_between_families'] = port_gaps
out['products_realized_without_inputs'] = composed_without_inputs
out['unconsumed_inputs'] = unconsumed_report[:30]
out['unperformed_operations'] = unperformed_report[:30]
out['invariance_product_level'] = inv2
json.dump(out, open(os.path.join(a.derive, 'analysis.json'), 'w'), indent=1)
md2 = []
md2.append(''); md2.append('Missing port edges (a product realized by one family feeds a product realized by another, but no output role of the first is an input role of the second):'); md2.append('')
md2.append('| from family | to family | relationship | cases | example |'); md2.append('|---|---|---|---|---|')
for x in port_gaps[:20]:
    md2.append('| %s | %s | %s | %d | %s |' % (x['from_family'], x['to_family'], x['relationship'], x['cases'], x['examples'][0] if x['examples'] else ''))
md2.append(''); md2.append('Products realized by a family with no bridged input and no inbound part (composed without inputs):'); md2.append('')
for x in composed_without_inputs[:12]:
    md2.append('- %s: %s (%d cases)' % (x['family'], ', '.join(x['products']), x['cases']))
md2.append(''); md2.append('Inputs no chain family consumes (top 12):'); md2.append('')
for x in unconsumed_report[:12]:
    md2.append('- %s (%d cases): bridged to %s, consumed only by %s; chains seen e.g. %s' % (x['input'], x['cases'], x['bridged_roles'], x['consuming_families'], x['chains_seen'][0]['families'] if x['chains_seen'] else ''))
md2.append(''); md2.append('Operations required by an activity but performed by no chain family (top 12):'); md2.append('')
for x in unperformed_report[:12]:
    p = x['patterns'][0]
    md2.append('- %s (%d cases): needs %s; the part\'s product was realized by %s' % (x['activity'], x['cases'], p['operations'], p['product_families']))
md2.append(''); md2.append('Product-level invariance (same product realized by the same family across strata):'); md2.append('')
for name, v in inv2.items():
    md2.append('- %s: %d groups, %s' % (name, v['groups'], v['status']))
with open(os.path.join(a.derive, 'analysis.md'), 'a') as fh:
    fh.write('\n'.join(md2) + '\n')
print('\n'.join(md2))

# ---------------------------------------------------------------------------------------------
# Batch-wide product x stratum realization: which family realizes each product in each regime / scale band.
prod_strat = OrderedDict()
for strat in ('regime', 'scale_band'):
    dist = defaultdict(lambda: defaultdict(Counter))
    for r in recs:
        c = cases[r['case_id']]
        fam = {z['deliverable']: z['family'] for z in r.get('realized', [])}
        for p in c['deliverables']:
            dist[p][r.get(strat) or c.get(strat)][fam.get(p, 'UNEXPLAINED')] += 1
    status = Counter(); detail = []
    for p, bys in dist.items():
        regs = {k: cnt for k, cnt in bys.items() if k and sum(cnt.values()) >= 5}
        if len(regs) < 2:
            continue
        dom = {k: cnt.most_common(1)[0][0] for k, cnt in regs.items()}
        unex = {k for k, cnt in regs.items() if cnt.get('UNEXPLAINED', 0) > 0.5 * sum(cnt.values())}
        if unex and any(d != 'UNEXPLAINED' for d in dom.values()) and len(unex) < len(regs):
            st = 'BREAKS'
        elif len(set(dom.values())) > 1:
            st = 'STRAINS'
        else:
            st = 'HOLDS'
        status[st] += 1
        detail.append(OrderedDict(product=p, status=st, dominant_family_by_stratum=dom, counts={k: dict(v) for k, v in regs.items()}))
    detail.sort(key=lambda x: ({'BREAKS': 0, 'STRAINS': 1, 'HOLDS': 2}[x['status']], x['product']))
    prod_strat[strat] = OrderedDict(products_compared=sum(status.values()), status=dict(status), detail=detail)
out['product_by_stratum'] = prod_strat
json.dump(out, open(os.path.join(a.derive, 'analysis.json'), 'w'), indent=1)
md3 = ['', 'Product-by-stratum realization (products seen at least five times in at least two strata; dominant realizing family per stratum):', '']
for strat, v in prod_strat.items():
    md3.append('- by %s: %d products compared, %s' % (strat, v['products_compared'], v['status']))
    for d in v['detail']:
        if d['status'] != 'HOLDS':
            md3.append('  - %s %s: %s' % (d['status'], d['product'], json.dumps(d['dominant_family_by_stratum'])))
with open(os.path.join(a.derive, 'analysis.md'), 'a') as fh:
    fh.write('\n'.join(md3) + '\n')
print('\n'.join(md3))
