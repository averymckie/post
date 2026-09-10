#!/usr/bin/env python3
"""Render the Phase 2 results section for one generation version from the run's analysis files."""
import json, os, sys
from collections import Counter, defaultdict
R = sys.argv[1]
V = os.path.basename(R.rstrip('/'))
S = json.load(open(os.path.join(R, 'derive_strict', 'analysis.json'))); L = json.load(open(os.path.join(R, 'derive_lenient', 'analysis.json')))
SS = json.load(open(os.path.join(R, 'derive_strict', 'summary.json'))); LS = json.load(open(os.path.join(R, 'derive_lenient', 'summary.json')))
B = json.load(open(os.path.join(R, 'bridge.json'))); G = json.load(open(os.path.join(R, 'gate_report.json')))
GR = json.load(open(os.path.join(R, 'build', 'generation_record.json')))
ings = {i['id']: i for i in json.load(open(os.path.join(R, 'ingredients.json')))}
cat = json.load(open(os.path.join(R, '..', '..', 'model', 'catalogue.json')))
n_axis_vals = sum(len(x['values']) for x in cat['axes'].values())
def lab(i):
    x = ings.get(i) or {}
    if x.get('axis') == 'situation_tag':
        return (x.get('meaning') or i).rstrip('.').lower()
    return x.get('label') or i
o = []
o.append('## Phase 2 results: generation version %s' % V)
o.append('')
o.append('### The build and the gate')
o.append('')
o.append('One blind Opus agent, given `coverage/gen/v2_prompt.md` and the three Phase 1 inventories, delivered in about 65 minutes: a dictionary of 526 ingredients on nine axes (298 grounded in inventory items, 217 in ISIC or FORD entries, 11 authored; all 371 inventory items walked), three programs with the mandated command lines and no language-model step, 5,000 admitted cases from 6,110 attempts (88 contradictions, 235 unresolved searches, 787 proposals diverted to the review pool), a recorded seed, byte-identical reruns, 37 machine checks, 20 of 20 deliberately broken variants caught, and generation plus checking in under seven seconds. The agent recorded one setup revision (dictionary 2.0.0 to 2.1.0: six generic inputs added after 1,867 cases had a deliverable resting on an assumed input) and five weaknesses of its own build: activity-to-product fit holds for 16,506 of 19,894 components by its own measure; beneficiary matched the domain in 2,528 cases; input identity falls back to another entity type when none was minted; 363 admitted cases carry an assumed input form on a non-deliverable part; component labels can repeat within a case.')
o.append('')
o.append('The gate passed on all eight checks after two fixes on the gate\'s side (its verdict parser did not read the checker\'s aggregate report shape, and an empty input list backed by a recorded assumption is informational, not missing):')
o.append('')
o.append('| gate | result |'); o.append('|---|---|')
for line in G['summary']:
    name, rest = line[:15].strip(), line[15:].strip()
    o.append('| %s | %s |' % (name, rest.replace('|', '/')[:160]))
o.append('')
o.append('Two distribution facts measured on the batch matter for reading the results: product use is uneven (a route plan occurs in 6 cases, a field procedure in hundreds), and the same need-plus-products combination recurs across regimes in 120 groups (693 groups on need plus root product), which is the material for the invariance test.')
o.append('')
o.append('### Canonical form and bridge')
o.append('')
o.append('The adapter (`coverage/engine/normalize.py`) treats every component product as a deliverable to realize, every component activity as an operation the chain must perform, templated obligations and global constraints as constraints keyed by template, acceptance conditions by ingredient, and conditions, dynamics, situation tags and the need as situation items. Beneficiary and scale are stratifiers, not bridged: the model makes no claim about who benefits, and scale is the cross-scale stratifier next to regime. Two generator-internal admissibility constraints (regime and situation admissibility of vocabulary) were dropped as bookkeeping.')
o.append('')
st = B['summary']['strengths']; bp = B['summary']['by_position']
o.append('The bridge (`coverage/runs/%s/bridge.json`, sources under `bridge/`) holds %d accepted atoms, each with a strength (exact, close, thin), a reason and the count of cases that force it: %s. Strengths: %s. Every ingredient used in a bridging position has at least one atom; %d ingredients have only thin atoms, which is the list of things the model has no counterpart for (below). A lexical proposal pass (token overlap between ingredient meanings and the model\'s role, family, operation, axis and proof texts) was run on a sample as a source of hints; the atoms themselves were judged from the dictionary meanings against the family cards, and the judgment is recorded per atom. Output-role atoms name the family (`F29:Artifact`), because five families produce `Artifact` and three produce `WorkPlan`; without that the solver picked among them arbitrarily.' % (
    V, B['summary']['atoms'], ', '.join('%s %d' % (k, v) for k, v in bp.items()), ', '.join('%s %s' % (k, dict(v)) for k, v in st.items()), sum(len(v) for v in B['summary']['only_thin_ingredients'].values())))
o.append('')
o.append('### Derivation results')
o.append('')
o.append('Two readings of the same bridge. Strict counts exact and close atoms only; lenient adds the thin atoms. A case is COVERED when every element found a target and every realizing family has a bridged anchoring proof record; PARTIAL when everything is explained but a realizing family has no anchoring record; UNEXPLAINED when a named element found no target. Grounding is well-founded: a family may resolve another family\'s input only if it is itself grounded back to case inputs, and a family in the chain with no bridged input at all is a name-only fit and counts as unexplained. Suppliers join one level deep, at most four. Each reading ran over the 5,000 cases in under a minute on four workers with no timeouts.')
o.append('')
o.append('| verdict | strict | lenient |'); o.append('|---|---|---|')
for k in ('COVERED', 'PARTIAL', 'UNEXPLAINED', 'NO-WITNESS'):
    o.append('| %s | %d | %d |' % (k, S['verdicts'].get(k, 0), L['verdicts'].get(k, 0)))
o.append('')
o.append('By regime (COVERED / PARTIAL / UNEXPLAINED):')
o.append('')
o.append('| regime | strict | lenient |'); o.append('|---|---|---|')
for reg in sorted(S['by_stratifier']['regime']):
    a, b = S['by_stratifier']['regime'][reg], L['by_stratifier']['regime'].get(reg, {})
    o.append('| %s | %d / %d / %d | %d / %d / %d |' % (reg, a.get('COVERED', 0), a.get('PARTIAL', 0), a.get('UNEXPLAINED', 0), b.get('COVERED', 0), b.get('PARTIAL', 0), b.get('UNEXPLAINED', 0)))
o.append('')
o.append('Gap classes (occurrences and distinct cases):')
o.append('')
o.append('| class | strict | lenient |'); o.append('|---|---|---|')
keys = list(dict.fromkeys(list(S['gap_classes']) + list(L['gap_classes'])))
for k in keys:
    a, b = S['gap_classes'].get(k, {'occurrences': 0, 'distinct_cases': 0}), L['gap_classes'].get(k, {'occurrences': 0, 'distinct_cases': 0})
    o.append('| %s | %d in %d cases | %d in %d cases |' % (k, a['occurrences'], a['distinct_cases'], b['occurrences'], b['distinct_cases']))
o.append('')
o.append('### Gap register')
o.append('')
o.append('**1. No counterpart in the model.** The %d ingredients that carry only thin atoms decide the strict verdict of %d cases. They fall into seven groups, each a candidate hardening item or an explicit scope statement:' % (sum(len(v) for v in B['summary']['only_thin_ingredients'].values()), S['gap_classes'].get('model gap candidate: no counterpart (only thin bridge atoms)', {}).get('distinct_cases', 0)))
o.append('')
groups = [
 ('human-performed activities', ['ACT-REHEARSE-DRILL', 'ACT-CONSULT-PUBLIC', 'ACT-PERFORM', 'ACT-FACILITATE-SESSION', 'ACT-INTERVIEW', 'ACT-CARE-VISIT', 'ACT-NEGOTIATE', 'ACT-COLLECT-SAMPLE', 'ACT-FABRICATE']),
 ('physical environment conditions', ['CND-COLD-CLIMATE', 'CND-HEAT-HUMIDITY', 'CND-DUST-VIBRATION', 'CND-HAZARDOUS-SITE', 'CND-STERILE-AREA']),
 ('authority and presence outside recorded delegation', ['CND-CUSTOMARY-AUTHORITY', 'CND-VOLUNTARY-STANDARD', 'CND-CONTESTED-SITE', 'CND-PUBLIC-SPACE']),
 ('human supervision, capacity and knowledge held by people', ['CND-NIGHT-SHIFT', 'CND-SUPERVISION-ABSENT', 'CND-HIGH-TURNOVER', 'DYN-STAFF-CHANGE', 'S-LOW-CAPACITY', 'S-SOLO', 'INP-LOCAL-KNOWLEDGE']),
 ('experiences as products and human-outcome acceptance', ['PRD-DRILL-EXERCISE', 'PRD-EXHIBITION', 'PRD-GAME-ACTIVITY', 'ACC-DRILL-PASSED', 'ACC-HANDOVER-COMPLETE', 'ACC-SPARE-AVAILABLE']),
 ('operating states with no axis value', ['S-CRISIS', 'DYN-DEGRADED-MODE', 'DYN-QUEUE-PRIORITY']),
 ('expressive and everyday purposes', ['NED-COMMEMORATE', 'NED-EXPRESS-EXPERIENCE', 'NED-RUN-HOUSEHOLD']),
]
reg_idx = {(x['kind'], x['item']): x for x in S['gap_register']}
for name, items in groups:
    parts = []
    for it in items:
        n = max([x['distinct_cases'] for (k, i), x in reg_idx.items() if i == it] or [0])
        parts.append('%s (%d)' % (lab(it), n))
    o.append('- %s: %s.' % (name, '; '.join(parts)))
o.append('')
o.append('The reading of these is the same as Phase 1\'s watch items, now at volume: the model constructs information systems and physical designs; it does not perform human acts, represent physical environments, or model authority that is not a recorded delegation. Human input enters only as an attributable boundary (C11, A11). Whether that is a scope statement or a gap is the user\'s call; the register gives the case counts either way.')
o.append('')
o.append('**2. Missing port edges between families.** When a part realized by one family feeds a part realized by another (an input, embed or emit relationship) and no output role of the first is an input role of the second, the second family is left without a grounded input. The most frequent pairs (strict reading):')
o.append('')
o.append('| from family | to family | relationship | cases | example |'); o.append('|---|---|---|---|---|')
for x in S['port_gaps_between_families'][:12]:
    o.append('| %s | %s | %s | %d | %s |' % (x['from_family'], x['to_family'], x['relationship'], x['cases'], (x['examples'][0] if x['examples'] else '').replace('|', '/')))
o.append('')
o.append('The encoding already showed the shape behind this: 37 of the 115 port roles are produced by some family and consumed by none, and 58 are consumed but produced by none. Family outputs mostly terminate; the composed chains in the master bind families in prose, not through declared ports. The three pairs at the top (repair plans into workflows, workflows and repair plans into detection and response, decision aids into documents) are concrete port-edge or adapter proposals.')
o.append('')
o.append('**3. Products realized by a family that has no input role for what the case supplies.** These are name-only fits caught by the grounding rule. Top products (strict): %s. Early-warning arrangements composed without a signal input and configurators composed without a family specification are partly the generator\'s loose composition (its own fit flag marks 17 percent of components) and partly the model: an early warning fed by procedures and people has no input role in F34.' % '; '.join('%s via %s (%d)' % (', '.join(lab(p) for p in x['products']) or 'supplier', x['family'], x['cases']) for x in S['products_realized_without_inputs'][:8]))
o.append('')
o.append('**4. Inputs no family in the chain can take** (lenient reading, top): %s. Production resources (workspace, staff time, stock) are input roles only of the planning, routing, diagnosis and experiment families; a document, register or catalogue built with them has nowhere to put them. Streams reach only detection and control, not measurement and reporting.' % '; '.join('%s (%d; bridged to %s, consumed only by %s)' % (lab(x['input']), x['cases'], ', '.join(x['bridged_roles']), ', '.join(x['consuming_families'])) for x in L['unconsumed_inputs'][:6]))
o.append('')
o.append('**5. Operations required by a part but performed by no family in its chain** (lenient reading, top): %s. Of the components behind this class, 26 percent are flagged by the generator itself as loose activity-to-product fits; the rest say that simulation, scheduling, routing, monitoring and handover are not operations of the document, measurement or workflow families whose products need them, and the port graph gives no supplier path either.' % '; '.join('%s (%d; needs %s, product realized by %s)' % (lab(x['activity']), x['cases'], ', '.join(x['patterns'][0]['operations']), ', '.join(x['patterns'][0]['product_families'])) for x in L['unperformed_operations'][:6]))
o.append('')
o.append('**6. Proof layer.** Realizing families without an anchoring record bridged from the case (strict): %s. Routing (F12) reproduces Phase 1\'s finding mechanically: the family exists, no proof record covers it. A caveat carried with every figure (the quality label) and an interactive simulator interface have no record under the families that realize them. The lenient reading adds the thin realizations (a drill as F31 qualification, an access pathway as F08 entitlement) with no record. %d of 349 proof records are never anchored by any derivation; the seven families with no primary record (F12, F22, F27, F28, F35, F36, F38) are unchanged from the encoding.' % (
    '; '.join('%s: %s' % (f, ', '.join('%s %d' % (lab(p), n) for p, n in list(v['products'].items())[:3])) for f, v in S['proof_gaps_by_family'].items()), S['never_reached']['proofs_never_reached']))
o.append('')
o.append('**7. Parts of the model nothing reaches** (strict): families %s; operation %s; compositions %s; variation rules %s; %d of %d axis values; %d of 349 proofs. The generator\'s world contains no forecasting, infrastructure, analytical-model or system-assembly product and no dependency-traversal activity, and its situation vocabulary does not carry the model\'s configuration axes (semantic object, dependency shape, construction target, variability), which the engine could derive from case structure in a later version. This is reported here only; nothing of it goes to the generator, whose expansion follows its own sparse-area counts.' % (
    ', '.join(S['never_reached']['families']), ', '.join(S['never_reached']['operations']), ', '.join(S['never_reached']['compositions']), ', '.join(S['never_reached']['variation_rules']), len(S['never_reached']['axis_values']), n_axis_vals, S['never_reached']['proofs_never_reached']))
o.append('')
o.append('**8. Open inputs.** The model\'s own question mechanism, not gaps: family input roles the case does not supply. Top (strict): %s. The world cases start from raw needs; the model presumes accepted measure, artifact, operating and workflow models upstream.' % '; '.join('%s %s (%d)' % (x['family'], x['role'], x['count']) for x in S['open_inputs_top'][:6]))
o.append('')
o.append('### Cross-regime and cross-scale')
o.append('')
pr = S['product_by_stratum']
o.append('Product-level test over the batch: for every product seen at least five times in at least two strata, the dominant realizing family per stratum. By regime: %s of %d products compared. By scale band: %s of %d. No product breaks (realized in one stratum, unexplained in another) at the product level; the breaks in the strict per-case reading come from the situation vocabulary in group 1, not from the families. The strains name the products the families cut differently depending on regime:' % (
    ', '.join('%s %d' % (k, v) for k, v in pr['regime']['status'].items()), pr['regime']['products_compared'], ', '.join('%s %d' % (k, v) for k, v in pr['scale_band']['status'].items()), pr['scale_band']['products_compared']))
o.append('')
for d in pr['regime']['detail']:
    if d['status'] != 'HOLDS':
        o.append('- %s: %s.' % (lab(d['product']), ', '.join('%s %s' % (k.replace('R-', ''), v) for k, v in d['dominant_family_by_stratum'].items())))
o.append('')
o.append('The pattern is consistent: the same world product lands in the computational family in the computation regime (a settlement mechanism as transactions F13, a test rig or sensor kit as physical control F35), in the organizational family in the organization and law regimes (the same settlement as a ledger F14, a governance process as collective decisions F10), and in the physical-design family in the physical regime (a sensor kit as engineering F27). The families hold across regimes as classes; where they strain, they strain along the computational, organizational and physical seams of the catalogue, which is where Phase 1\'s cross-scale checks also found the recurring strains.')
o.append('')
o.append('### What changed in the method during this version')
o.append('')
o.append('- Output-role atoms were made family-qualified after the first full run showed material supply (F15) realizing explainers through the shared `Artifact` role and then lacking anchors.')
o.append('- Grounding was made well-founded after inspection showed an ungrounded supplier (F03 with no data input) resolving three families\' `Dataset` inputs and offsetting its own cost.')
o.append('- Proof anchoring is required of realizing families only; suppliers are used generically and carry their family-level anchors.')
o.append('- The solver-driven proposal pass was stopped after 1,423 cases (2.5 seconds a case under the candidate search) and replaced by direct judgment with case-count provenance; its hints were used for the first pass of atoms.')
o.append('')
o.append('### Hardening items proposed by this version (not applied; the catalogue stays frozen)')
o.append('')
o.append('- Scope or axis: decide whether human-performed activities, physical environment conditions, informal or voluntary authority, supervision level, crisis and degraded modes, and expressive purposes are out of scope (state it, with C11 and A11 as the boundary) or become axis values, an environment field, a family for designed experiences, and an authority-basis value on the authority field.')
o.append('- Port graph: declare edges or adapters for repair plan to workflow (F32 to F09), workflow, measurement and repair into detection and response (F09, F17, F32 to F34), decision aid to document (F19 to F29), and a resource or material contract that any family\'s production can consume; let measurement families take streams.')
o.append('- Operations: simulation and scheduling as operations available to the measurement, document and workflow families, or the supplier paths that bring them in.')
o.append('- Proof records: routing (F12), qualifier rendering with figures (F29), simulator interfaces (F30), and primary records for the seven families that have none.')
o.append('- The 37 thin-only ingredients and the 1,003 atoms are the bridge table to review; changing an atom re-runs in a minute.')
o.append('')
o.append('### Limits of this version')
o.append('')
o.append('The bridge is the operator\'s judgment, recorded per atom; a different judgment moves cases between classes but not out of the register. The generator\'s loose activity-to-product fit inflates class 5 by about a quarter. Product use is uneven, so per-product counts vary by two orders of magnitude. The volume ladder (25,000 with vocabulary expansion, new bridge atoms per thousand) has not started; the first run of it is the next step.')
o.append('')
text = '\n'.join(o) + '\n'
open(os.path.join(R, 'results.md'), 'w').write(text)
print(text)
