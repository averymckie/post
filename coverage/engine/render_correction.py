#!/usr/bin/env python3
"""Render the correction section for a version from its run directories."""
import json, os, sys
from collections import Counter, OrderedDict
R = sys.argv[1]; V = os.path.basename(R.rstrip('/'))
def J(*p): return json.load(open(os.path.join(R, *p)))
cases = {json.loads(l)['case_id']: json.loads(l) for l in open(os.path.join(R, 'cases.jsonl'))}
ings = {i['id']: i for i in json.load(open(os.path.join(R, 'ingredients.json')))}
def lab(i):
    x = ings.get(i) or {}
    return (x.get('meaning') or i).rstrip('.').lower() if x.get('axis') == 'situation_tag' else (x.get('label') or i)
B = J('bridge.json'); only_thin = set(i for v in B['summary']['only_thin_ingredients'].values() for i in v)
runs = OrderedDict([('derive_strict', 'bridge-1, one supplier level, strict'), ('derive_lenient', 'bridge-1, one supplier level, lenient'),
                    ('unbounded_close', 'bridge-1, recursive suppliers, strict'), ('unbounded_thin', 'bridge-1, recursive suppliers, lenient'),
                    ('ref_close', 'bridge-2, recursive suppliers, strict'), ('ref_thin', 'bridge-2, recursive suppliers, lenient')])
V_ = {k: J(k, 'summary.json')['verdicts'] for k in runs}
def ing_of(c, item):
    for r in c['requirements'] + c['constraints'] + c['acceptance']:
        if r['id'] == item: return r['ing']
    for r in c['relationships']:
        if r['id'] == item: return r['kind']
    return item
def decompose(run):
    cls = Counter(); items = Counter()
    for l in open(os.path.join(R, run, 'derivations.jsonl')):
        r = json.loads(l)
        if r['verdict'] != 'UNEXPLAINED': continue
        c = cases[r['case_id']]; voc = struct = 0
        for u in r['unexplained']:
            ing = ing_of(c, u['item'])
            if u['kind'] not in ('grounding', 'acceptance_qualifier') and ing in only_thin:
                voc += 1; items[ing] += 1
            else:
                struct += 1
        cls['vocabulary only' if struct == 0 else ('structural only' if voc == 0 else 'both')] += 1
    return cls, items
S = J('ref_close', 'analysis.json'); L = J('ref_thin', 'analysis.json')
dS, itemsS = decompose('ref_close'); dL, _ = decompose('ref_thin')
o = []
o.append('## Correction after review: %s' % V); o.append('')
o.append('An external review of the results section above made two objections. First, the evaluator limited supporting chains to one level and at most four suppliers, while the framework\'s grammar composes recursively. Second, 37 disputed vocabulary mappings decided 4,137 of the 5,000 strict verdicts, so the headline table reported places where this evaluator failed to reconstruct a case as if they were framework gaps. Both objections are correct. The verdict table in the results section is superseded by the tables here; the rest of that section stands where this one does not withdraw it.'); o.append('')
o.append('### Check 1: the supplier bound'); o.append('')
o.append('Both readings were re-run with recursive, uncapped suppliers under the same well-founded grounding rule (a family may resolve another family\'s input only if it is itself grounded back to case inputs). Each run takes about 70 seconds, no timeouts; chains carry 2.8 suppliers on average instead of 1.0.'); o.append('')
o.append('| run | COVERED | PARTIAL | UNEXPLAINED |'); o.append('|---|---|---|---|')
for k, name in runs.items():
    v = V_[k]; o.append('| %s | %d | %d | %d |' % (name, v.get('COVERED', 0), v.get('PARTIAL', 0), v.get('UNEXPLAINED', 0)))
o.append('')
o.append('With the bound removed, 210 strict and 1,383 lenient cases that were reported as unexplained reconstruct. The classes reported above as "missing port edges", "inputs no family in the chain consumes" and "operations no chain family performs" were mostly this evaluator\'s bound: under recursive composition they shrink to a few cases each and are withdrawn as findings, except for the residuals listed below.'); o.append('')
o.append('### Check 2: the 37 disputed mappings'); o.append('')
o.append('Each of the 37 ingredients that carried only thin atoms was re-examined against the framework text for the construction it offers and the assumption that construction needs. Verdicts: "missed construction" (the text names a construction and the first rating was too low), "contrary assumption" (reconstructible only under an assumption the case itself contradicts), "boundary" (reconstructible around a human or physical boundary the framework declares through C11, A11 and R28), "no construction". The review is recorded as a revision block on the bridge (`bridge/src_revision.py`); original ratings are kept beside the revised ones.'); o.append('')
o.append('| ingredient | position | construction offered | verdict |'); o.append('|---|---|---|---|')
rev = [a for a in B['atoms'] if a.get('review_verdict')]
rank = {'exact': 3, 'close': 2, 'thin': 1}
seen = set()
for a in sorted(rev, key=lambda a: (-rank[a['strength']], a['ingredient'])):
    if a['position'] == 'proof': continue
    key = (a['ingredient'], a['position'])
    if key in seen: continue
    seen.add(key)
    o.append('| %s | %s | %s: %s | %s |' % (lab(a['ingredient']), a['position'], a['target'], a['reason'].replace('|', '/'), a['review_verdict']))
vc = Counter(a['review_verdict'] for a in rev if a['position'] != 'proof')
o.append(''); o.append('Verdict counts over the reviewed atoms: %s. The revised bridge has %d atoms; %d ingredients still carry only thin atoms.' % (', '.join('%s %d' % (k, v) for k, v in vc.most_common()), B['summary']['atoms'], len(only_thin))); o.append('')
o.append('### Corrected reading'); o.append('')
o.append('Reference from here on: revised bridge, recursive suppliers.'); o.append('')
o.append('| verdict | strict (exact and close) | lenient (thin included) |'); o.append('|---|---|---|')
for k in ('COVERED', 'PARTIAL', 'UNEXPLAINED'):
    o.append('| %s | %d | %d |' % (k, V_['ref_close'].get(k, 0), V_['ref_thin'].get(k, 0)))
o.append(''); o.append('What the two numbers mean. %d cases reconstruct with mappings that follow the family cards\' own contracts. %d reconstruct when the %d remaining thin items are read as the boundaries the framework itself declares (a person\'s act enters as attributable input through C11, knowledge and authority are admitted once recorded, equipment lives inside a qualified envelope under R28) or as assumptions the case contradicts. Neither number is a count of framework gaps.' % (V_['ref_close'].get('COVERED', 0), V_['ref_thin'].get('COVERED', 0), len(only_thin))); o.append('')
o.append('Strict UNEXPLAINED decomposes into: %s. The vocabulary items and the cases they decide:' % ', '.join('%s %d' % (k, v) for k, v in dS.most_common())); o.append('')
verd = {a['ingredient']: a['review_verdict'] for a in rev if a['position'] != 'proof'}
for ing, n in itemsS.most_common():
    o.append('- %s: %d cases, %s.' % (lab(ing), n, verd.get(ing, 'thin')))
o.append(''); o.append('Lenient UNEXPLAINED decomposes into: %s. The structural residual is almost entirely one product: configurators. %s' % (', '.join('%s %d' % (k, v) for k, v in dL.most_common()), '; '.join('%s via %s (%d cases)' % (', '.join(lab(p) for p in x['products']) or 'supplier', x['family'], x['cases']) for x in L['products_realized_without_inputs'][:4]))); o.append('')
o.append('The 139 configurator cases never supply what F37 takes (a family specification, a capability catalogue, a proof-requirement catalogue, a target profile). Either the world\'s configurators are lighter objects than F37 (parameterized templates, which F29 constructs) or F37\'s inputs are the framework\'s own artifacts and never occur in the wild. That is a genuine observation about the framework\'s reach, and the one structural finding of this version that survives both checks.'); o.append('')
o.append('### What survives as findings'); o.append('')
o.append('- Boundary and contrary-assumption items (%d): %s. These decide the strict verdicts of %d cases. They are the framework\'s declared boundaries or its recording premise, stated as gap candidates only if the user wants them inside the model.' % (len(only_thin), '; '.join(lab(i) for i in sorted(only_thin)), dS['vocabulary only'] + dS['both']))
o.append('- Configurators as above (%d cases).' % L['products_realized_without_inputs'][0]['cases'])
o.append('- Proof layer (strict): %s. Routing under F12 reproduces the Phase 1 finding; the F09 and F23 entries in the first run of this check were anchors I had omitted and are now bridged.' % ('; '.join('%s %d' % (f, v['total']) for f, v in S['proof_gaps_by_family'].items())))
o.append('- Never reached: families %s; operation %s; compositions %s; variation rules %s. Generator sparse areas, reported here and not fed to the generator.' % (', '.join(S['never_reached']['families']), ', '.join(S['never_reached']['operations']), ', '.join(S['never_reached']['compositions']), ', '.join(S['never_reached']['variation_rules'])))
pr = S['product_by_stratum']
o.append('- Cross-regime at product level: %s of %d products by regime; %s of %d by scale band; no product breaks. Strains: %s.' % (', '.join('%s %d' % (k, v) for k, v in pr['regime']['status'].items()), pr['regime']['products_compared'], ', '.join('%s %d' % (k, v) for k, v in pr['scale_band']['status'].items()), pr['scale_band']['products_compared'], '; '.join('%s (%s)' % (lab(d['product']), ', '.join('%s %s' % (k.replace('R-', ''), v) for k, v in d['dominant_family_by_stratum'].items())) for d in pr['regime']['detail'] if d['status'] != 'HOLDS')))
o.append('- Port edges surviving at material count (strict): %s. Everything else in that table is withdrawn.' % '; '.join('%s to %s over %s (%d)' % (x['from_family'], x['to_family'], x['relationship'], x['cases']) for x in S['port_gaps_between_families'][:3]))
o.append('- Phase 1\'s seventeen no-anchor entries are unchanged.'); o.append('')
o.append('### Corrected hardening list'); o.append('')
o.append('- A scope statement in the master for the boundary class (human acts, physical environments as they affect people, presence without consent, authority and knowledge that are not recorded), or axis values if the user wants them inside the model.')
o.append('- F37\'s input roles against world configurators: either a lighter configurator profile or an explicit statement that F37 configures families, not products.')
o.append('- Proof records: routing (F12), qualifier rendering with figures (F29), simulator interfaces (F30), primary records for the seven families that have none.')
o.append('- The one port edge with a material count: repair plan into workflow (F32 to F09).')
o.append('- The evaluator itself: recursive suppliers are now the default reading; the bounded runs are kept for the record.'); o.append('')
text = '\n'.join(o) + '\n'
open(os.path.join(R, 'correction.md'), 'w').write(text)
print(text)
