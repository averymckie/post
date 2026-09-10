#!/usr/bin/env python3
"""Assemble bridge.json from the operator's judgment sources, validating every target against the
catalogue and every ingredient against the generator's vocabulary. Reports uncovered ingredients."""
import json, os, sys, importlib.util
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
cat = json.load(open(os.path.join(RUN, '..', '..', 'model', 'catalogue.json')))
ings = {i['id']: i for i in json.load(open(os.path.join(RUN, 'ingredients.json')))}

def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
prod, inp, ops, sit = load('src_products'), load('src_inputs'), load('src_ops'), load('src_situation')
prod_fam = load('src_products_fam')
roles = cat['indexes']['roles']
out_roles = {r for r, rr in roles.items() if rr['produced_by']}
in_roles = {r for r, rr in roles.items() if rr['consumed_by']}
C, O, V, B, P, A = set(cat['compositions']), set(cat['operations']), set(cat['variation_rules']), set(cat['boundary_fields']), set(cat['proofs']), cat['axes']
axis_vals = {a['id'] + '|' + v.lower() for a in A.values() for v in a['values']}
con_targets = B | V | {'R14'} | C | O
RC = set(cat['required_claims'])
acc_targets = {'A15|' + v.lower() for v in A['A15']['values']} | {'A11|' + v.lower() for v in A['A11']['values']} | {'R|' + r for r in RC}
sit_targets = axis_vals | {'V|' + v for v in V} | {'B|' + b for b in B} | {'C|' + c for c in C} | {'R|' + r for r in RC}
out_fam_roles = {f + ':' + r for r, rr in roles.items() for f in rr['produced_by']}
universe = {'out': out_fam_roles, 'in': in_roles, 'rel': C, 'req': O, 'con': con_targets, 'acc': acc_targets, 'sit': sit_targets, 'proof': P}
rev = load('src_revision')
sources = [('out', prod_fam.OUT), ('proof', prod.PROOF), ('in', inp.IN), ('rel', inp.REL), ('req', ops.REQ), ('con', ops.CON), ('acc', ops.ACC), ('sit', sit.SIT)]
atoms, errors = [], []
seen = set()
for pos, lst in sources:
    for ing, target, strength, reason in lst:
        if ing not in ings:
            errors.append('%s: unknown ingredient %s' % (pos, ing))
        if target not in universe[pos]:
            errors.append('%s: unknown target %s for %s' % (pos, target, ing))
        if strength not in ('exact', 'close', 'thin'):
            errors.append('%s: bad strength %s' % (pos, strength))
        key = (pos, ing, target)
        if key in seen:
            errors.append('duplicate atom %s' % (key,)); continue
        seen.add(key)
        atoms.append(dict(position=pos, ingredient=ing, target=target, strength=strength, reason=reason, status='accepted', source='operator'))
by_key = {(a['position'], a['ingredient'], a['target']): a for a in atoms}
for pos, ing, target, strength, reason, verdict in rev.REVISION:
    if ing not in ings:
        errors.append('revision: unknown ingredient %s' % ing)
    if target not in universe[pos]:
        errors.append('revision: unknown target %s for %s' % (target, ing))
    key = (pos, ing, target)
    if key in by_key:
        a = by_key[key]
        a['revised_from'] = dict(strength=a['strength'], reason=a['reason'])
        a['strength'], a['reason'], a['review_verdict'] = strength, reason, verdict
    else:
        a = dict(position=pos, ingredient=ing, target=target, strength=strength, reason=reason, status='accepted', source='operator-revision', review_verdict=verdict)
        atoms.append(a); by_key[key] = a
# proof atoms must be reachable: some out-target family of the product is a proof_fam of the record
p2f = cat['indexes']['proof_to_families']
fam_of_role = defaultdict(set)
for r, rr in roles.items():
    for f in rr['produced_by']:
        fam_of_role[r].add(f)
out_fams = defaultdict(set)
for a in atoms:
    if a['position'] == 'out':
        out_fams[a['ingredient']].add(a['target'].split(':')[0])
unreachable = []
for a in atoms:
    if a['position'] == 'proof':
        rec = p2f[a['target']]
        pf = set(rec['anchoring']) | set(rec['extension_of']) | ({rec['primary']} if rec['primary'] and rec['primary'] != 'UNASSIGNED' else set())
        if not (pf & out_fams[a['ingredient']]):
            unreachable.append((a['ingredient'], a['target'], sorted(pf), sorted(out_fams[a['ingredient']])))
# coverage of the vocabulary actually used in cases
used = defaultdict(set)
for line in open(os.path.join(RUN, 'cases.jsonl')):
    c = json.loads(line)
    for d in c['deliverables']: used['out'].add(d)
    for i in c['inputs']: used['in'].add(i)
    for r in c['relationships']: used['rel'].add(r['kind'])
    for r in c['requirements']: used['req'].add(r['ing'])
    for r in c['constraints']: used['con'].add(r['ing'])
    for r in c['acceptance']: used['acc'].add(r['ing'])
    for s in c['situation']: used['sit'].add(s['ing'])
covered = defaultdict(set)
for a in atoms:
    covered[a['position']].add(a['ingredient'])
missing = {pos: sorted(used[pos] - covered[pos]) for pos in used}
strength_counts = {pos: dict(Counter(a['strength'] for a in atoms if a['position'] == pos)) for pos, _ in sources}
only_thin = defaultdict(list)
for pos in used:
    for ing in sorted(used[pos]):
        st = [a['strength'] for a in atoms if a['position'] == pos and a['ingredient'] == ing]
        if st and all(s == 'thin' for s in st):
            only_thin[pos].append(ing)
# provenance: the cases that force each atom (every case using the ingredient in that position)
forced = defaultdict(list)
for line in open(os.path.join(RUN, 'cases.jsonl')):
    c = json.loads(line)
    for d in c['deliverables']: forced[('out', d)].append(c['case_id']); forced[('proof', d)].append(c['case_id'])
    for i in c['inputs']: forced[('in', i)].append(c['case_id'])
    for r in c['relationships']: forced[('rel', r['kind'])].append(c['case_id'])
    for r in c['requirements']: forced[('req', r['ing'])].append(c['case_id'])
    for r in c['constraints']: forced[('con', r['ing'])].append(c['case_id'])
    for r in c['acceptance']: forced[('acc', r['ing'])].append(c['case_id'])
    for s in c['situation']: forced[('sit', s['ing'])].append(c['case_id'])
for a in atoms:
    lst = forced.get((a['position'], a['ingredient']), [])
    a['forced_by_cases'] = len(set(lst))
    a['forced_by_examples'] = sorted(set(lst))[:5]
bridge = dict(version='genv-2.1.0/bridge-2', catalogue_sha256=cat['source']['sha256'], atoms=atoms,
              summary=dict(atoms=len(atoms), by_position={pos: len([a for a in atoms if a['position'] == pos]) for pos, _ in sources},
                           strengths=strength_counts, uncovered_used_ingredients=missing, only_thin_ingredients=dict(only_thin),
                           unreachable_proof_atoms=[dict(ingredient=u[0], proof=u[1], proof_families=u[2], product_families=u[3]) for u in unreachable]))
json.dump(bridge, open(os.path.join(RUN, 'bridge.json'), 'w'), indent=1)
print('atoms', len(atoms), 'errors', len(errors))
for e in errors[:40]: print('  ERROR', e)
print('by position', bridge['summary']['by_position'])
print('strengths', json.dumps(strength_counts))
print('uncovered used ingredients:', json.dumps(missing))
print('only-thin ingredients:', json.dumps(dict(only_thin)))
print('unreachable proof atoms (%d):' % len(unreachable), [(u[0], u[1]) for u in unreachable][:30])
sys.exit(1 if errors else 0)
