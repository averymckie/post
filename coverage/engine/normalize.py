#!/usr/bin/env python3
"""Adapter from a generator build (genv-2.x record format) to the engine's canonical form.

Writes OUT/ingredients.json and OUT/cases.jsonl. Mechanical. The modelling decisions it
embodies are fixed and recorded here:
  - every component's product is a deliverable the chain must realize (required ones flagged);
  - each component's activity is a requirement: an operation class a chain family must perform;
  - templated atomic requirements (RT-*) and global constraints (CT-*) are constraints keyed by
    template id, one entry per template per case;
  - acceptance conditions are keyed by acceptance ingredient (ACC-*), one entry per ingredient per case;
  - situation = conditions (CND-*), dynamics (DYN-*), situation tags (S-*) and the need (NED-*);
  - relationship endpoints are the products of the components they connect;
  - beneficiary (BEN-*) and scale (SCL-*) are stratifiers, not bridged: the model makes no claim
    about who benefits, and scale is the cross-scale stratifier alongside regime.
Usage: python3 normalize.py BUILD_DIR OUT_DIR
"""
import json, os, sys
from collections import OrderedDict

build, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
d = json.load(open(os.path.join(build, 'dictionary.json')))
ings = []
for i in d['ingredients'].values():
    ings.append(OrderedDict(id=i['id'], axis=i['axis'], label=i.get('label'),
                            meaning=(i.get('label') or '') + '. ' + (i.get('meaning') or ''),
                            regimes=i.get('regimes'), provenance=i.get('provenance'), extra={k: i[k] for k in ('form', 'kind', 'check_mode', 'verb', 'band', 'purpose_class') if k in i}))
for k, v in d['relationship_kinds'].items():
    ings.append(OrderedDict(id=k, axis='relationship', label=v.get('label'),
                            meaning='%s. %s Transfers: %s. Changes: %s. Shares: %s.' % (v.get('label'), v.get('meaning'), v.get('transfers'), v.get('changes'), v.get('shares')),
                            regimes=None, provenance={'source': 'dictionary', 'section': 'relationship_kinds'}, extra={}))
for k, v in d['requirement_templates'].items():
    ings.append(OrderedDict(id=k, axis='requirement_template', label=k, meaning=v if isinstance(v, str) else json.dumps(v), regimes=None,
                            provenance={'source': 'dictionary', 'section': 'requirement_templates'}, extra={}))
for k, v in d['constraint_templates'].items():
    ings.append(OrderedDict(id=k, axis='constraint_template', label=k, meaning=v.get('text') if isinstance(v, dict) else str(v), regimes=None,
                            provenance={'source': 'dictionary', 'section': 'constraint_templates'}, extra={k2: v[k2] for k2 in ('machine_checkable', 'severity', 'check') if isinstance(v, dict) and k2 in v}))
for k, v in d['situations'].items():
    ings.append(OrderedDict(id=k, axis='situation_tag', label=k, meaning=v if isinstance(v, str) else json.dumps(v), regimes=None,
                            provenance={'source': 'dictionary', 'section': 'situations'}, extra={}))
json.dump(ings, open(os.path.join(out, 'ingredients.json'), 'w'), indent=1)
ing_by = {i['id']: i for i in ings}
regime_label = {k: v['label'] for k, v in d['regimes'].items()}

n = 0
with open(os.path.join(build, 'cases.jsonl')) as f, open(os.path.join(out, 'cases.jsonl'), 'w') as g:
    for line in f:
        c = json.loads(line)
        comps = {x['component_id']: x for x in c['components']}
        products = sorted(set(x['product'] for x in c['components']))
        required = sorted(set(x['product'] for x in c['required_deliverables']))
        root = [x['product'] for x in c['components'] if x.get('depth') == 0]
        need = c['need_and_context']['need']
        rels = []
        for r in c['component_relationships']:
            rels.append(OrderedDict(id=r['rel_id'], kind=r['kind'], from_component=r['from'], to_component=r['to'],
                                    **{'from': comps[r['from']]['product'], 'to': comps[r['to']]['product']}))
        reqs = []
        seen = set()
        for x in c['components']:
            key = x['activity']
            if key in seen:
                continue
            seen.add(key)
            reqs.append(OrderedDict(id='act:' + x['activity'], ing=x['activity']))
        cons = []
        seen = set()
        for x in c['atomic_requirements_with_stable_ids']:
            t = x['template']
            if t not in seen:
                seen.add(t)
                cons.append(OrderedDict(id='rt:' + t, ing=t))
        for x in c['global_constraints']:
            t = x['template']
            if t not in seen:
                seen.add(t)
                cons.append(OrderedDict(id='ct:' + t, ing=t))
        acc = []
        seen = set()
        for x in c['acceptance_conditions']:
            if x['ingredient'] not in seen:
                seen.add(x['ingredient'])
                acc.append(OrderedDict(id='acc:' + x['ingredient'], ing=x['ingredient'], check_mode=x.get('check_mode')))
        sit = []
        seen = set()
        for kind, lst in (('condition', c['situation'].get('conditions', [])), ('dynamic', c['situation'].get('dynamics', [])),
                          ('tag', c['situation'].get('tags', [])), ('need', [need])):
            for s in lst:
                if s not in seen:
                    seen.add(s)
                    sit.append(OrderedDict(ing=s, axis=kind))
        scale = c['situation'].get('scale')
        rec = OrderedDict(
            case_id=c['case_id'], regime=c['regime'], regime_label=regime_label.get(c['regime']), domain=c['primary_domain'],
            scale=scale, scale_band=(ing_by.get(scale) or {}).get('extra', {}).get('band'),
            beneficiary=c['beneficiary']['ingredient'], need=need,
            deliverables=products, required=required, inputs=sorted(set(x['ingredient'] for x in c['concrete_inputs'])),
            relationships=rels, requirements=reqs, constraints=cons, acceptance=acc, situation=sit,
            semantic_key=need + '|' + ','.join(products), coarse_key=need + '|' + (root[0] if root else ''),
            components=len(c['components']), cross_regime_components=c['diversity_signature'].get('cross_regime_components', []))
        g.write(json.dumps(rec) + '\n')
        n += 1
print('ingredients', len(ings), 'cases', n, '->', out)
