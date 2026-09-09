#!/usr/bin/env python3
"""Reverse-engineering engine: derive each canonical case into the catalogue with clingo.

Inputs
  --catalogue coverage/model/catalogue.json         (mechanical encoding of the master)
  --triggers  coverage/engine/feature_triggers.json (operator's V-rule trigger reading)
  --ingredients ING.json   canonical ingredient list: [{id, axis, meaning, regimes}] (from normalize.py)
  --cases CASES.jsonl      canonical cases (from normalize.py):
       {case_id, regime, domain, semantic_key, deliverables[], inputs[], relationships[{id,kind,from,to}],
        requirements[{id,ing}], constraints[{id,ing}], acceptance[{id,ing}], situation[{ing,axis}]}
  --bridge BRIDGE.json     accepted bridge atoms with reasons and provenance (may be absent)

Modes
  propose  lexical candidates + solver-chosen candidates per (position, ingredient) -> proposals.jsonl
  derive   accepted atoms only -> derivations.jsonl, summary.json, gaps.json, invariance.json

No language-model step runs here. Lexical candidates are token overlap; every accepted bridge atom
carries the operator's reason and the cases that forced it.
"""
import argparse, json, multiprocessing, os, re, sys, time
from collections import Counter, defaultdict, OrderedDict
import clingo

HERE = os.path.dirname(os.path.abspath(__file__))
STOP = set('''a an the of and or to for in on at by with from into as is are be this that these those its it their his her
our your which who whom what when where while than then so such not no nor via per each any all some other another same one
two more most many much very also only just may can could must should will would shall over under between within without
against about after before during through across up down out off new old own per'''.split())
POSITIONS = ('out', 'in', 'rel', 'req', 'con', 'acc', 'sit', 'proof')


def stem(w):
    for suf in ('ations', 'ation', 'ising', 'izing', 'ings', 'ing', 'ies', 'ers', 'er', 'ed', 'es', 's'):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            return w[:-len(suf)]
    return w


def tokens(s):
    if not s:
        return set()
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', str(s))
    return {stem(w) for w in re.findall(r'[a-z]+', s.lower()) if w not in STOP and len(w) > 2}


def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


class Model:
    def __init__(self, cat, trig):
        self.cat = cat
        F, O, C, A, V, B, P = cat['families'], cat['operations'], cat['compositions'], cat['axes'], cat['variation_rules'], cat['boundary_fields'], cat['proofs']
        self.F, self.O, self.C, self.A, self.V, self.B, self.P = F, O, C, A, V, B, P
        facts = []
        for f in F.values():
            facts.append('family(%s).' % q(f['id']))
            for r in f['output_roles'] or []:
                facts.append('fam_out(%s,%s).' % (q(f['id']), q(r)))
            for r in f['input_roles'] or []:
                facts.append('fam_in(%s,%s).' % (q(f['id']), q(r)))
            for o in f['operation_classes'] or []:
                facts.append('fam_op(%s,%s).' % (q(f['id']), q(o)))
        for c in C:
            facts.append('comp(%s).' % q(c))
        for a in A.values():
            for v in a['values']:
                facts.append('axis_val(%s,%s).' % (q(a['id']), q(v.lower())))
        for v in V:
            facts.append('vrule(%s).' % q(v))
        for b in B:
            facts.append('bfield(%s).' % q(b))
        p2f = cat['indexes']['proof_to_families']
        for p, rec in P.items():
            facts.append('proof(%s).' % q(p))
            fams = set(p2f[p]['anchoring']) | set(p2f[p]['extension_of'])
            if rec['primary_family'] and rec['primary_family'] != 'UNASSIGNED':
                fams.add(rec['primary_family'])
            for f in sorted(fams):
                facts.append('proof_fam(%s,%s).' % (q(p), q(f)))
        for v, pairs in trig.items():
            if v.startswith('_'):
                continue
            for a, val in pairs:
                facts.append('trig(%s,%s,%s).' % (q(v), q(a), q(val.lower())))
        self.facts = '\n'.join(facts) + '\n'
        # lexical index per position: list of (target_key, name_tokens, desc_tokens)
        roles = cat['indexes']['roles']
        self.index = {p: [] for p in POSITIONS}
        for r, rr in roles.items():
            fam_txt = ' '.join(F[f]['title'] + ' ' + (F[f]['product_contract'] or '') for f in rr['produced_by'] + rr['consumed_by'])
            generic = len(rr['produced_by']) + len(rr['consumed_by']) >= 8   # roles nearly every family carries
            entry = (r, tokens(r), tokens(fam_txt), generic)
            if rr['produced_by']:
                self.index['out'].append(entry)
            if rr['consumed_by']:
                self.index['in'].append(entry)
        for c in C.values():
            self.index['rel'].append((c['id'], tokens(c['name']) | tokens(c['form']), tokens(c['obligation']), False))
        for o in O.values():
            self.index['req'].append((o['id'], tokens(o['name']), tokens(o['signature']) | tokens(o['obligation']), False))
        for b, txt in B.items():
            self.index['con'].append((b, tokens(b), tokens(txt), False))
        for v in V.values():
            self.index['con'].append((v['id'], tokens(v['feature']), tokens(' '.join(v['capabilities'])), False))
        self.index['con'].append(('R14', tokens('global invariants shared state authority conservation progress effects'), set(), False))
        for val in A['A15']['values']:
            self.index['acc'].append((val.lower(), tokens(val), set(), False))
        for a in A.values():
            for val in a['values']:
                self.index['sit'].append((a['id'] + '|' + val.lower(), tokens(val), tokens(a['axis']), False))
        for p, rec in P.items():
            name = rec['title'] + ' ' + (rec.get('hardening', {}) or {}).get('title', '')
            desc = ' '.join(s['step'] for s in (rec.get('chain') or {}).get('steps', [])) + ' ' + (rec.get('input_contract') or '') + ' ' + (rec.get('output_contract') or '')
            self.index['proof'].append((p, tokens(name), tokens(desc), False))

    def candidates(self, pos, ing_tokens, k=6):
        scored = []
        for key, nt, dt, generic in self.index[pos]:
            s = 2 * len(ing_tokens & nt) + len(ing_tokens & dt) - (2 if generic else 0)
            if s > 0:
                scored.append((s, key))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return scored[:k]


def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def case_facts(c):
    fx = []
    for d in c.get('deliverables', []):
        fx.append('deliv(%s).' % q(d))
    for i in c.get('inputs', []):
        fx.append('input(%s).' % q(i))
    for r in c.get('relationships', []):
        fx.append('rel(%s,%s,%s,%s).' % (q(r['id']), q(r['kind']), q(r.get('from') or 'none'), q(r.get('to') or 'none')))
    for r in c.get('requirements', []):
        fx.append('req(%s,%s).' % (q(r['id']), q(r['ing'])))
    for r in c.get('constraints', []):
        fx.append('con(%s,%s).' % (q(r['id']), q(r['ing'])))
    for r in c.get('acceptance', []):
        fx.append('acc(%s,%s).' % (q(r['id']), q(r['ing'])))
    for s in c.get('situation', []):
        fx.append('sit(%s,%s).' % (q(s['ing']), q(s.get('axis') or 'situation')))
    return '\n'.join(fx) + '\n'


def bridge_facts(bridge):
    fx = []
    for atom in bridge.get('atoms', []):
        if atom.get('status', 'accepted') != 'accepted':
            continue
        pos, ing, target = atom['position'], atom['ingredient'], atom['target']
        if pos == 'sit':
            a, v = target.split('|', 1)
            fx.append('b_sit(%s,%s,%s).' % (q(ing), q(a), q(v)))
        else:
            fx.append('b_%s(%s,%s).' % (pos, q(ing), q(target)))
    return '\n'.join(fx) + '\n'


def candidate_facts(model, ings, c):
    """Lexical candidate atoms for every bridging position used by the case."""
    fx, cands = [], {}
    def add(pos, ing):
        key = (pos, ing)
        if key in cands:
            return
        toks = tokens(ing) | tokens((ings.get(ing) or {}).get('meaning', ''))
        cands[key] = model.candidates(pos, toks)
        for rank, (s, t) in enumerate(cands[key], 1):
            if pos == 'sit':
                a, v = t.split('|', 1)
                fx.append('c_sit(%s,%s,%s,%d).' % (q(ing), q(a), q(v), rank))
            else:
                fx.append('c_%s(%s,%s,%d).' % (pos, q(ing), q(t), rank))
    for d in c.get('deliverables', []):
        add('out', d); add('proof', d)
    for i in c.get('inputs', []):
        add('in', i); add('proof', i)
    for r in c.get('relationships', []):
        add('rel', r['kind'])
    for r in c.get('requirements', []):
        add('req', r['ing']); add('proof', r['ing'])
    for r in c.get('constraints', []):
        add('con', r['ing'])
    for r in c.get('acceptance', []):
        add('acc', r['ing']); add('proof', r['ing'])
    for s in c.get('situation', []):
        add('sit', s['ing'])
    return '\n'.join(fx) + '\n', cands


def solve(program, timeout):
    ctl = clingo.Control(['--opt-mode=opt'])
    ctl.add('base', [], program)
    ctl.ground([('base', [])])
    best = {'atoms': None, 'cost': None}
    def on_model(m):
        best['atoms'] = [str(s) for s in m.symbols(shown=True)]
        best['cost'] = list(m.cost)
    with ctl.solve(on_model=on_model, async_=True) as h:
        finished = h.wait(timeout)
        if not finished:
            h.cancel()
        res = h.get()
    return best, bool(finished), res


ATOM = re.compile(r'^(\w+)\((.*)\)$')


def parse_args_str(s):
    out, cur, depth, inq = [], '', 0, False
    i = 0
    while i < len(s):
        ch = s[i]
        if inq:
            if ch == '\\':
                cur += s[i + 1]; i += 2; continue
            if ch == '"':
                inq = False
            else:
                cur += ch
        elif ch == '"':
            inq = True
        elif ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
            cur += ch
        i += 1
    out.append(cur)
    return out


def parse_atoms(atoms):
    d = defaultdict(list)
    for a in atoms or []:
        m = ATOM.match(a)
        if m:
            d[m.group(1)].append(parse_args_str(m.group(2)))
        else:
            d[a].append([])
    return d


def derive_case(model, ings, c, bridge_fx, program, timeout, propose):
    cand_fx, cands = ('', {})
    if propose:
        cand_fx, cands = candidate_facts(model, ings, c)
    prog = program + model.facts + bridge_fx + cand_fx + case_facts(c)
    t = time.time()
    best, finished, res = solve(prog, timeout)
    secs = round(time.time() - t, 3)
    if best['atoms'] is None:
        return OrderedDict(case_id=c['case_id'], verdict='NO-WITNESS', note='no model within budget' if not finished else 'unsatisfiable', seconds=secs), cands
    at = parse_atoms(best['atoms'])
    unexplained = [OrderedDict(kind=k, item=x) for k, x in at.get('unexplained', [])]
    chain = sorted(set(f[0] for f in at.get('in_chain', [])))
    proof_gaps = sorted(set(f[0] for f in at.get('proof_gap', [])))
    if unexplained:
        verdict = 'UNEXPLAINED'
    elif proof_gaps:
        verdict = 'PARTIAL'
    else:
        verdict = 'COVERED'
    used = []
    for pos in POSITIONS:
        for args in at.get('use_' + pos, []):
            used.append(OrderedDict(position=pos, ingredient=args[0], target='|'.join(args[1:])))
    rec = OrderedDict(
        case_id=c['case_id'], regime=c.get('regime'), domain=c.get('domain'), semantic_key=c.get('semantic_key'),
        verdict=verdict, cost=best['cost'], seconds=secs, timed_out=not finished,
        families=chain,
        realized=[OrderedDict(deliverable=a[0], role=a[1], family=a[2]) for a in at.get('realize', [])],
        suppliers=[OrderedDict(family=a[0], feeds=a[1], role=a[2]) for a in at.get('supply', [])],
        open_inputs=[OrderedDict(family=a[0], role=a[1]) for a in at.get('open_input', [])],
        compositions=sorted(set(a[1] for a in at.get('map_rel', []))),
        operations=sorted(set(a[1] for a in at.get('map_req', []))),
        constraint_targets=sorted(set(a[1] for a in at.get('map_con', []))),
        assurance=sorted(set(a[1] for a in at.get('map_acc', []))),
        axis_values=sorted(set(a[1] + '|' + a[2] for a in at.get('map_sit', []))),
        variation_rules=sorted(set(a[0] for a in at.get('vrule_on', []))),
        anchors=[OrderedDict(family=a[0], proof=a[1]) for a in at.get('anchor', [])],
        proof_gaps=proof_gaps,
        unexplained=unexplained,
        candidate_atoms_used=used)
    return rec, cands


_W = {}


def _init(cat_path, trig_path, ing_path, program, bridge_fx, timeout, propose):
    _W['model'] = Model(json.load(open(cat_path)), json.load(open(trig_path)))
    _W['ings'] = {i['id']: i for i in json.load(open(ing_path))}
    _W.update(program=program, bridge_fx=bridge_fx, timeout=timeout, propose=propose)


def _work(c):
    return derive_case(_W['model'], _W['ings'], c, _W['bridge_fx'], _W['program'], _W['timeout'], _W['propose'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('mode', choices=['propose', 'derive'])
    ap.add_argument('--catalogue', default=os.path.join(HERE, '..', 'model', 'catalogue.json'))
    ap.add_argument('--triggers', default=os.path.join(HERE, 'feature_triggers.json'))
    ap.add_argument('--program', default=os.path.join(HERE, 'derive.lp'))
    ap.add_argument('--ingredients', required=True)
    ap.add_argument('--cases', required=True)
    ap.add_argument('--bridge', default=None)
    ap.add_argument('--out', required=True, help='output directory')
    ap.add_argument('--timeout', type=float, default=5.0)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--workers', type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cat = json.load(open(a.catalogue))
    trig = json.load(open(a.triggers))
    model = Model(cat, trig)
    ings = {i['id']: i for i in json.load(open(a.ingredients))}
    cases = load_jsonl(a.cases)
    if a.limit:
        cases = cases[:a.limit]
    bridge = json.load(open(a.bridge)) if a.bridge and os.path.exists(a.bridge) else {'atoms': []}
    bridge_fx = bridge_facts(bridge)
    program = open(a.program).read()
    propose = a.mode == 'propose'
    t0 = time.time()
    recs, proposals = [], {}
    if a.workers > 1:
        pool = multiprocessing.Pool(a.workers, initializer=_init,
                                    initargs=(a.catalogue, a.triggers, a.ingredients, program, bridge_fx, a.timeout, propose))
        results = pool.imap(_work, cases, chunksize=4)
    else:
        results = (derive_case(model, ings, c, bridge_fx, program, a.timeout, propose) for c in cases)
    with open(os.path.join(a.out, 'derivations.jsonl'), 'w') as fout:
        for n, (c, (rec, cands)) in enumerate(zip(cases, results), 1):
            recs.append(rec)
            fout.write(json.dumps(rec) + '\n')
            if propose:
                for (pos, ing), cl in cands.items():
                    p = proposals.setdefault((pos, ing), OrderedDict(position=pos, ingredient=ing, meaning=(ings.get(ing) or {}).get('meaning'),
                                                                     axis=(ings.get(ing) or {}).get('axis'), lexical=[{'target': t, 'score': s} for s, t in cl],
                                                                     solver_used=Counter(), cases=0, examples=[]))
                    p['cases'] += 1
                    if len(p['examples']) < 5:
                        p['examples'].append(c['case_id'])
                for u in rec.get('candidate_atoms_used', []):
                    key = (u['position'], u['ingredient'])
                    if key in proposals:
                        proposals[key]['solver_used'][u['target']] += 1
            if n % 200 == 0:
                print('%d/%d cases, %.0fs' % (n, len(cases), time.time() - t0), file=sys.stderr)
    if propose:
        with open(os.path.join(a.out, 'proposals.jsonl'), 'w') as f:
            for p in sorted(proposals.values(), key=lambda p: (-p['cases'], p['position'], p['ingredient'])):
                p['solver_used'] = dict(p['solver_used'])
                f.write(json.dumps(p) + '\n')
    write_reports(a.out, cat, recs, cases)
    print('done: %d cases in %.0fs -> %s' % (len(recs), time.time() - t0, a.out))


def write_reports(out, cat, recs, cases):
    verdicts = Counter(r['verdict'] for r in recs)
    fam_hits, op_hits, comp_hits, ax_hits, v_hits, p_hits, role_hits = Counter(), Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    for r in recs:
        if r['verdict'] == 'NO-WITNESS':
            continue
        for f in r['families']:
            fam_hits[f] += 1
        for o in r['operations']:
            op_hits[o] += 1
        for c in r['compositions']:
            comp_hits[c] += 1
        for av in r['axis_values']:
            ax_hits[av] += 1
        for v in r['variation_rules']:
            v_hits[v] += 1
        for an in r['anchors']:
            p_hits[an['proof']] += 1
        for rz in r['realized']:
            role_hits[rz['role']] += 1
    F, O, C, A, V, P = cat['families'], cat['operations'], cat['compositions'], cat['axes'], cat['variation_rules'], cat['proofs']
    all_axis_vals = [a['id'] + '|' + v.lower() for a in A.values() for v in a['values']]
    summary = OrderedDict(
        cases=len(recs), verdicts=dict(verdicts),
        timed_out=sum(1 for r in recs if r.get('timed_out')),
        mean_seconds=round(sum(r.get('seconds', 0) for r in recs) / max(1, len(recs)), 3),
        families_reached=OrderedDict((f, fam_hits.get(f, 0)) for f in F),
        families_never_reached=[f for f in F if not fam_hits.get(f)],
        operations_never_reached=[o for o in O if not op_hits.get(o)],
        compositions_never_reached=[c for c in C if not comp_hits.get(c)],
        axis_values_never_reached=[v for v in all_axis_vals if not ax_hits.get(v)],
        variation_rules_never_reached=[v for v in V if not v_hits.get(v)],
        proofs_reached=len(p_hits), proofs_never_reached=len(P) - len(p_hits),
        output_roles_reached=dict(role_hits),
        operations_reached=dict(op_hits), compositions_reached=dict(comp_hits), variation_rules_reached=dict(v_hits))
    json.dump(summary, open(os.path.join(out, 'summary.json'), 'w'), indent=1)
    gaps = defaultdict(lambda: OrderedDict(count=0, examples=[]))
    ing_of = {}
    for c in cases:
        for r in c.get('requirements', []):
            ing_of[(c['case_id'], r['id'])] = r['ing']
        for r in c.get('constraints', []):
            ing_of[(c['case_id'], r['id'])] = r['ing']
        for r in c.get('acceptance', []):
            ing_of[(c['case_id'], r['id'])] = r['ing']
        for r in c.get('relationships', []):
            ing_of[(c['case_id'], r['id'])] = r['kind']
    for r in recs:
        for u in r.get('unexplained', []):
            label = ing_of.get((r['case_id'], u['item']), u['item'])
            g = gaps[(u['kind'], label)]
            g['count'] += 1
            if len(g['examples']) < 5:
                g['examples'].append(r['case_id'])
    pg = defaultdict(lambda: OrderedDict(count=0, examples=[]))
    for r in recs:
        for f in r.get('proof_gaps', []):
            pg[f]['count'] += 1
            if len(pg[f]['examples']) < 5:
                pg[f]['examples'].append(r['case_id'])
    gap_list = [OrderedDict(kind=k, item=i, count=v['count'], examples=v['examples']) for (k, i), v in sorted(gaps.items(), key=lambda kv: -kv[1]['count'])]
    json.dump(OrderedDict(unexplained=gap_list, proof_gaps=OrderedDict(sorted(pg.items()))), open(os.path.join(out, 'gaps.json'), 'w'), indent=1)
    groups = defaultdict(list)
    for r in recs:
        if r.get('semantic_key'):
            groups[r['semantic_key']].append(r)
    inv = []
    for key, rs in groups.items():
        regs = set(r['regime'] for r in rs)
        if len(regs) < 2:
            continue
        by_reg = {}
        for r in rs:
            by_reg.setdefault(r['regime'], []).append((tuple(r['families']), r['verdict']))
        famsets = set(fs for lst in by_reg.values() for fs, _ in lst)
        verdicts_ = set(v for lst in by_reg.values() for _, v in lst)
        if 'UNEXPLAINED' in verdicts_ and len(verdicts_) > 1:
            status = 'BREAKS'
        elif len(famsets) > 1:
            status = 'STRAINS'
        else:
            status = 'HOLDS'
        inv.append(OrderedDict(semantic_key=key, regimes=sorted(regs), status=status,
                               per_regime={k: [{'families': list(fs), 'verdict': v} for fs, v in lst] for k, lst in by_reg.items()}))
    inv_summary = Counter(i['status'] for i in inv)
    json.dump(OrderedDict(groups=len(inv), status_counts=dict(inv_summary), groups_detail=inv), open(os.path.join(out, 'invariance.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
