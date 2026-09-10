#!/usr/bin/env python3
"""Operator-side reliability gate for a generator build.

The build's own programs (generate.py, checker.py, expand.py) are run here in
separate processes, and the batch is checked for what the build cannot vouch
for itself:

  G1 determinism   the recorded seed and count reproduce cases.jsonl
                   byte-for-byte in two separate processes; another seed differs
  G2 checker       checker.py passes the batch, rejects its own broken
                   examples, and rejects operator-made mutations of admitted
                   cases (unresolvable reference, no acceptance conditions,
                   no requirements, no inputs)
  G3 references    every relationship and requirement entry resolves to a
                   dictionary id; every record has the sixteen required
                   fields; expand.py expands every case
  G4 duplicates    exact duplicates (identity fields stripped) and structural
                   duplicates (same ingredient set, regime, domain, kinds)
  G5 diversity     floors per regime, ISIC section, FORD field, relationship
                   kind, and cross-regime cases (scaled to the batch size)
  G6 leak          catalogue identifiers or phrases in the dictionary, the
                   cases or the programs (hard: catalogue field names as keys;
                   soft: id-shaped tokens and phrases, listed with context)
  G7 provenance    share of ingredients grounded in the inventories or the
                   taxonomies; cases built only from grounded ingredients
  G8 runtime       generation plus checking wall-clock against the budget

Usage:
  python3 gate.py BUILD_DIR [--count N] [--seed-b S] [--mutations M]
                            [--report FILE] [--skip-runs]
Exit status 0 when every gate that ran passed.
"""
import argparse, hashlib, json, math, os, random, re, shutil, subprocess, sys, time
from collections import Counter, defaultdict

FLOORS = {'regime': 60, 'isic': 20, 'ford': 40, 'relation': 30, 'cross': 100, 'cell': 3}  # per 1,000 cases
PROVENANCE_FLOOR = 0.80          # share of ingredients grounded in inventories or taxonomies
RUNTIME_BUDGET_S = 60.0          # generate + check, per 1,000 cases
ISIC = ['ISIC-' + chr(c) for c in range(ord('A'), ord('U') + 1)]
FORD = ['FORD-%d' % i for i in range(1, 7)]
ID_PATTERNS = re.compile(r'\b(?:F|O|C|A|V|R|X|L)\d{2}\b|\bHG\d{2}\b|\bP(?:[1-9]\d?|[12]\d\d|3[0-4]\d)\b')
PHRASES = ['boundary contract', 'fourteen-field', 'fourteen field', 'proof record', 'operation class',
           'composition form', 'state-space ax', 'variation rule', 'familyspec', 'family spec',
           'frozen catalogue', 'product famil']
HARD_KEYS = re.compile(r'operation_class|composition_form|state_space|variation_rule|proof_record|boundary_contract', re.I)
SOFT_KEYS = re.compile(r'famil|anchor|\baxis\b', re.I)
TOKEN = re.compile(r'[A-Za-z0-9_.:\-/]+')
ING_FIELDS = {'meaning', 'regimes', 'provenance', 'prerequisites', 'results', 'constraints',
              'situations', 'applicable_situations', 'applicable_regimes'}
KIND_KEYS = ('kind', 'type', 'relationship', 'relation', 'rel', 'relationship_kind', 'relation_type')
STRIP = {'case_id', 'seed_or_replay_reference', 'diversity_signature', 'generation_version'}
REQUIRED = ['case_id', 'generation_version', 'primary_domain', 'regime', 'beneficiary', 'need_and_context',
            'required_deliverables', 'concrete_inputs', 'component_relationships',
            'atomic_requirements_with_stable_ids', 'global_constraints', 'acceptance_conditions',
            'assumptions_and_provenance', 'validation_status_and_evidence', 'diversity_signature',
            'seed_or_replay_reference']
FAILISH = re.compile(r'fail|reject|invalid|error|contradict|incomplete|broken|unresolved|missing|violation|detected', re.I)
PASSISH = re.compile(r'pass|valid|\bok\b|admit|accept|clean', re.I)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def sha_text(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load_jsonl(path):
    out = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as e:
                out.append({'__bad_line__': i, '__error__': str(e)})
    return out


def run(cmd, cwd, timeout=3600):
    t = time.time()
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return {'cmd': ' '.join(cmd), 'rc': r.returncode, 'seconds': round(time.time() - t, 3),
                'stdout': r.stdout[-3000:], 'stderr': r.stderr[-3000:]}
    except subprocess.TimeoutExpired:
        return {'cmd': ' '.join(cmd), 'rc': None, 'seconds': round(time.time() - t, 3),
                'stdout': '', 'stderr': 'TIMEOUT'}


def strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from strings(v)
    elif isinstance(o, list):
        for x in o:
            yield from strings(x)


def keys_of(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from keys_of(v)
    elif isinstance(o, list):
        for x in o:
            yield from keys_of(x)


def entries(x):
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return list(x.values())
    if x is None:
        return []
    return [x]


def ingredients_of(d):
    ing = {}

    def rec(o):
        if isinstance(o, dict):
            if isinstance(o.get('id'), str) and ING_FIELDS & set(o.keys()):
                ing.setdefault(o['id'], o)
            for k, v in o.items():
                if isinstance(v, dict) and not isinstance(v.get('id'), str) and ING_FIELDS & set(v.keys()):
                    ing.setdefault(k, v)
                rec(v)
        elif isinstance(o, list):
            for x in o:
                rec(x)
    rec(d)
    return ing


def all_ids(d):
    ids = set()

    def rec(o):
        if isinstance(o, dict):
            if isinstance(o.get('id'), str):
                ids.add(o['id'])
            for v in o.values():
                rec(v)
        elif isinstance(o, list):
            for x in o:
                rec(x)
    rec(d)
    return ids


def refs_in(o, ids):
    found = set()
    for s in strings(o):
        if s in ids:
            found.add(s)
            continue
        for t in TOKEN.findall(s):
            if t in ids:
                found.add(t)
    return found


def rel_kind(e):
    if isinstance(e, dict):
        for k in KIND_KEYS:
            v = e.get(k)
            if isinstance(v, str):
                return v
        return None
    if isinstance(e, str):
        parts = e.split()
        return parts[0] if parts else None
    return None


def regime_of(c):
    r = c.get('regime')
    if isinstance(r, str):
        return r
    if isinstance(r, dict):
        for k in ('primary', 'id', 'name', 'regime'):
            if isinstance(r.get(k), str):
                return r[k]
    if isinstance(r, list) and r:
        return regime_of({'regime': r[0]})
    return None


def domain_of(c):
    d = c.get('primary_domain')
    s = d if isinstance(d, str) else json.dumps(d)
    m = re.search(r'ISIC[\s:_-]*([A-U])\b', s, re.I)
    if m:
        return 'ISIC-' + m.group(1).upper()
    m = re.search(r'FORD[\s:_-]*([1-6])\b', s, re.I)
    if m:
        return 'FORD-' + m.group(1)
    if isinstance(d, str):
        m = re.fullmatch(r'\s*([A-U])\s*', d)
        if m:
            return 'ISIC-' + m.group(1)
        m = re.fullmatch(r'\s*([1-6])\s*', d)
        if m:
            return 'FORD-' + m.group(1)
    return 'OTHER:' + s[:40]


def find_int(record, pred):
    hits = []

    def rec(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if pred(k.lower()) and isinstance(v, (int, str)) and not isinstance(v, bool):
                    try:
                        hits.append((len(path), int(v)))
                    except ValueError:
                        pass
                rec(v, path + [k])
        elif isinstance(o, list):
            for x in o:
                rec(x, path)
    rec(record, [])
    hits.sort()
    return hits[0][1] if hits else None


def collect_case_ids(o, acc=None):
    acc = set() if acc is None else acc
    if isinstance(o, dict):
        if isinstance(o.get('case_id'), str):
            acc.add(o['case_id'])
        for v in o.values():
            collect_case_ids(v, acc)
    elif isinstance(o, list):
        for x in o:
            collect_case_ids(x, acc)
    return acc


def vote(path, st):
    if st is not None:
        k, v = st
        if isinstance(v, bool):
            return (not v) if k in ('valid', 'ok', 'admitted', 'passed', 'accepted', 'clean') else v
        s = str(v)
        if FAILISH.search(s):
            return True
        if PASSISH.search(s):
            return False
        return None
    joined = ' '.join(str(p) for p in path)
    if FAILISH.search(joined):
        return True
    if PASSISH.search(joined):
        return False
    return None


def case_verdicts(report, wanted):
    """Map each wanted case id to True (rejected), False (accepted) or None (undetermined)."""
    votes = defaultdict(list)

    def rec(o, path):
        if isinstance(o, dict):
            cid = o.get('case_id')
            if isinstance(cid, str) and cid in wanted:
                st = None
                for k in ('status', 'verdict', 'result', 'valid', 'ok', 'admitted', 'passed',
                          'accepted', 'rejected', 'failed', 'clean', 'detected', 'expected_all_detected'):
                    if k in o:
                        st = (k, o[k])
                        break
                votes[cid].append(vote(path, st))
            for k, v in o.items():
                rec(v, path + [k])
        elif isinstance(o, list):
            for x in o:
                rec(x, path)
        elif isinstance(o, str) and o in wanted:
            votes[o].append(vote(path, None))
    rec(report, [])
    out = {}
    for cid in wanted:
        vs = [v for v in votes.get(cid, []) if v is not None]
        out[cid] = True if True in vs else (False if False in vs else None)
    return out


def summary_numbers(report):
    out = {}

    def rec(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool) and len(path) <= 2:
                    out['.'.join(path + [k])] = v
                rec(v, path + [k])
    rec(report, [])
    return out


def mutants_of(c, ids):
    out = []
    cid = str(c.get('case_id'))
    c1 = json.loads(json.dumps(c))
    state = {'done': False}

    def repl(o):
        if state['done']:
            return o
        if isinstance(o, str):
            if o in ids:
                state['done'] = True
                return 'zz_nonexistent_ingredient'
            return o
        if isinstance(o, dict):
            return {k: repl(v) for k, v in o.items()}
        if isinstance(o, list):
            return [repl(x) for x in o]
        return o
    for f in ('component_relationships', 'atomic_requirements_with_stable_ids'):
        if f in c1 and not state['done']:
            c1[f] = repl(c1[f])
    if state['done']:
        c1['case_id'] = cid + '__m1_badref'
        out.append(c1)
    for tag, field in (('m2_noacceptance', 'acceptance_conditions'),
                       ('m3_norequirements', 'atomic_requirements_with_stable_ids')):
        cm = json.loads(json.dumps(c))
        v = cm.get(field)
        cm[field] = type(v)() if isinstance(v, (list, dict, str)) else None
        cm['case_id'] = cid + '__' + tag
        out.append(cm)
    cm = json.loads(json.dumps(c))
    cm.pop('concrete_inputs', None)
    cm['case_id'] = cid + '__m4_noinputs'
    out.append(cm)
    return out


def status(p):
    return 'PASS' if p is True else 'FAIL' if p is False else 'SKIP'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('build')
    ap.add_argument('--count', type=int, default=None, help='count to rerun with (default: from the record, else batch size)')
    ap.add_argument('--seed-b', type=int, default=None)
    ap.add_argument('--mutations', type=int, default=30, help='admitted cases to mutate (4 mutants each)')
    ap.add_argument('--report', default=None)
    ap.add_argument('--skip-runs', action='store_true', help='analyse the batch only; do not rerun the programs')
    a = ap.parse_args()
    B = os.path.abspath(a.build)
    tmp = os.path.join(B, '_gate')
    W = os.path.join(tmp, 'work')
    os.makedirs(W, exist_ok=True)
    py = sys.executable
    R = {'build': B, 'started': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'gates': {}}
    need = ['dictionary.json', 'generate.py', 'checker.py', 'expand.py', 'cases.jsonl', 'generation_record.json']
    missing = [f for f in need if not os.path.exists(os.path.join(B, f))]
    R['missing_files'] = missing
    R['file_hashes'] = {f: sha(os.path.join(B, f)) for f in need if f not in missing}

    def have(f):
        return f not in missing

    # working copy of the programs and the dictionary, so reruns never touch the build's outputs
    for f in os.listdir(B):
        p = os.path.join(B, f)
        if os.path.isfile(p) and (f.endswith('.py') or f == 'dictionary.json'):
            shutil.copy(p, os.path.join(W, f))

    D = json.load(open(os.path.join(B, 'dictionary.json'))) if have('dictionary.json') else {}
    cases_raw = load_jsonl(os.path.join(B, 'cases.jsonl')) if have('cases.jsonl') else []
    record = json.load(open(os.path.join(B, 'generation_record.json'))) if have('generation_record.json') else {}
    bad_lines = [c for c in cases_raw if '__bad_line__' in c]
    cases = [c for c in cases_raw if '__bad_line__' not in c]
    ing = ingredients_of(D)
    ids = all_ids(D) | set(ing.keys())
    ing_ids = set(ing.keys())
    case_ids = [str(c.get('case_id')) for c in cases]
    n_cases = len(cases)
    count = a.count or find_int(record, lambda k: 'request' in k or k == 'count') or n_cases
    scale = n_cases / 1000.0 if n_cases else 1.0
    floors = {k: math.ceil(v * scale) for k, v in FLOORS.items()}
    R['count_for_rerun'] = count
    R['floors_scaled_to_batch'] = floors
    R['record_claims'] = summary_numbers(record)
    R['batch'] = {'cases': n_cases, 'bad_lines': len(bad_lines), 'ingredients': len(ing),
                  'dictionary_ids': len(ids), 'distinct_case_ids': len(set(case_ids))}
    case_refs = {i: refs_in(c, ids) for i, c in enumerate(cases)}

    # ---- G1 determinism (+ generation timing for G8)
    g1 = {'seed': find_int(record, lambda k: 'seed' in k), 'runs': []}
    gen_seconds = None
    if not a.skip_runs and have('generate.py') and have('cases.jsonl') and g1['seed'] is not None:
        hashes = []
        for i in (1, 2):
            out = os.path.join(tmp, 'cases_a%d.jsonl' % i)
            r = run([py, 'generate.py', '--dictionary', 'dictionary.json', '--seed', str(g1['seed']),
                     '--count', str(count), '--out', out, '--record', os.path.join(tmp, 'record_a%d.json' % i)], W)
            g1['runs'].append(r)
            hashes.append(sha(out) if os.path.exists(out) else None)
        seed_b = a.seed_b if a.seed_b is not None else g1['seed'] + 1
        outb = os.path.join(tmp, 'cases_b.jsonl')
        r = run([py, 'generate.py', '--dictionary', 'dictionary.json', '--seed', str(seed_b),
                 '--count', str(count), '--out', outb, '--record', os.path.join(tmp, 'record_b.json')], W)
        g1['runs'].append(r)
        hb = sha(outb) if os.path.exists(outb) else None
        g1.update({'build_hash': R['file_hashes'].get('cases.jsonl'), 'rerun_hashes': hashes,
                   'seed_b': seed_b, 'seed_b_hash': hb})
        g1['identical'] = hashes[0] is not None and hashes[0] == hashes[1] == g1['build_hash']
        g1['differs_on_seed_b'] = hb is not None and hb != g1['build_hash']
        g1['pass'] = bool(g1['identical'] and g1['differs_on_seed_b'])
        gen_seconds = g1['runs'][0]['seconds']
    else:
        g1['pass'] = None
        g1['note'] = 'skipped, or seed / generate.py / cases.jsonl missing'
    R['gates']['G1_determinism'] = g1

    # ---- G2 checker: batch, broken examples, operator mutations
    g2 = {}
    check_seconds = None
    if not a.skip_runs and have('checker.py') and have('cases.jsonl'):
        rp = os.path.join(tmp, 'checker_report_rerun.json')
        r = run([py, 'checker.py', '--dictionary', 'dictionary.json', '--cases', os.path.join(B, 'cases.jsonl'),
                 '--report', rp], W)
        check_seconds = r['seconds']
        rep = json.load(open(rp)) if os.path.exists(rp) else None
        v = case_verdicts(rep, set(case_ids)) if rep else {}
        g2['batch'] = {'run': r, 'report_found': rep is not None,
                       'summary_numbers': summary_numbers(rep) if rep else {},
                       'rejected': sum(1 for x in v.values() if x is True),
                       'accepted': sum(1 for x in v.values() if x is False),
                       'undetermined': sum(1 for x in v.values() if x is None)}
        nums_b = g2['batch']['summary_numbers']
        fail_counts = [n for k, n in nums_b.items() if FAILISH.search(k) and not PASSISH.search(k)]
        g2['batch']['reported_failures'] = fail_counts
        g2['batch']['pass'] = r['rc'] == 0 and rep is not None and g2['batch']['rejected'] == 0 and all(n == 0 for n in fail_counts)

        bp = os.path.join(tmp, 'broken_report_rerun.json')
        r = run([py, 'checker.py', '--dictionary', 'dictionary.json', '--broken', '--report', bp], W)
        brep = json.load(open(bp)) if os.path.exists(bp) else None
        nums = summary_numbers(brep) if brep else {}
        g2['broken'] = {'run': r, 'report_found': brep is not None, 'summary_numbers': nums}
        if brep is not None:
            wanted = collect_case_ids(brep)
            v = case_verdicts(brep, wanted)
            rej = sum(1 for x in v.values() if x is True)
            acc = sum(1 for x in v.values() if x is False)
            passish0 = any(n == 0 for k, n in nums.items() if PASSISH.search(k) and not FAILISH.search(k))
            failpos = any(n > 0 for k, n in nums.items() if FAILISH.search(k))
            g2['broken'].update({'examples': len(wanted), 'rejected': rej, 'accepted': acc,
                                 'undetermined': len(wanted) - rej - acc})
            missed0 = any(n == 0 for k, n in nums.items() if 'missed' in k.lower())
            detected = any(n > 0 for k, n in nums.items() if 'detected' in k.lower())
            g2['broken']['pass'] = (len(wanted) > 0 and rej >= len(wanted) - 1 and acc <= 1) or (missed0 and detected) or (len(wanted) == 0 and passish0 and failpos)
        else:
            g2['broken']['pass'] = False

        rng = random.Random(20260909)
        pool = [c for c in cases if isinstance(c.get('case_id'), str)]
        sample = rng.sample(pool, min(a.mutations, len(pool))) if pool else []
        muts = [m for c in sample for m in mutants_of(c, ids)]
        mp = os.path.join(tmp, 'mutants.jsonl')
        mrp = os.path.join(tmp, 'mutants_report.json')
        with open(mp, 'w') as f:
            for m in muts:
                f.write(json.dumps(m, sort_keys=True) + '\n')
        r = run([py, 'checker.py', '--dictionary', 'dictionary.json', '--cases', mp, '--report', mrp], W)
        mrep = json.load(open(mrp)) if os.path.exists(mrp) else None
        wanted = set(m['case_id'] for m in muts)
        v = case_verdicts(mrep, wanted) if mrep else {}
        by_kind = defaultdict(Counter)
        for cid, x in v.items():
            by_kind[cid.rsplit('__', 1)[1]]['rejected' if x is True else 'accepted' if x is False else 'undetermined'] += 1
        nums = summary_numbers(mrep) if mrep else {}
        rej = sum(1 for x in v.values() if x is True)
        acc = sum(1 for x in v.values() if x is False)
        und = len(wanted) - rej - acc
        passish0 = any(n == 0 for k, n in nums.items() if PASSISH.search(k) and not FAILISH.search(k))
        g2['mutations'] = {'run': r, 'report_found': mrep is not None, 'mutants': len(muts), 'rejected': rej,
                           'accepted': acc, 'undetermined': und,
                           'by_kind': {k: dict(c) for k, c in by_kind.items()}, 'summary_numbers': nums}
        failing_total = any(n == len(muts) for k, n in nums.items() if FAILISH.search(k) and not PASSISH.search(k))
        g2['mutations']['pass'] = mrep is not None and len(muts) > 0 and (rej == len(muts) or (acc == 0 and (passish0 or failing_total)))
        g2['pass'] = bool(g2['batch']['pass'] and g2['broken']['pass'] and g2['mutations']['pass'])
    else:
        g2['pass'] = None
    R['gates']['G2_checker'] = g2

    # ---- G3 references, required fields, expansion
    g3 = {'entries_checked': 0, 'unresolved_entries': 0, 'cases_with_unresolved': 0, 'examples': []}
    for i, c in enumerate(cases):
        bad = 0
        for f in ('component_relationships', 'atomic_requirements_with_stable_ids'):
            for e in entries(c.get(f)):
                g3['entries_checked'] += 1
                if not refs_in(e, ids):
                    bad += 1
                    if len(g3['examples']) < 10:
                        g3['examples'].append({'case_id': c.get('case_id'), 'field': f, 'entry': json.dumps(e)[:200]})
        if bad:
            g3['unresolved_entries'] += bad
            g3['cases_with_unresolved'] += 1
    mf = Counter()
    assumed_empty = 0
    for c in cases:
        for f in REQUIRED:
            if f not in c or c[f] in (None, '', [], {}):
                if f == 'concrete_inputs' and f in c and 'assum' in json.dumps(c.get('assumptions_and_provenance', '')).lower():
                    assumed_empty += 1
                    continue
                mf[f] += 1
    g3['missing_fields'] = dict(mf)
    g3['empty_inputs_with_recorded_assumption'] = assumed_empty
    if not a.skip_runs and have('expand.py') and have('cases.jsonl'):
        ep = os.path.join(tmp, 'expanded_all.md')
        r = run([py, 'expand.py', '--dictionary', 'dictionary.json', '--cases', os.path.join(B, 'cases.jsonl'), '--out', ep], W)
        txt = open(ep, errors='replace').read() if os.path.exists(ep) else ''
        found = set(re.findall(r'[A-Za-z0-9_.:\-]{3,}', txt)) if txt else set()
        present = sum(1 for cid in case_ids if cid in found)
        g3['expand'] = {'run': r, 'bytes': len(txt), 'case_ids_present': present}
        g3['expand_pass'] = r['rc'] == 0 and present == len(case_ids) and len(case_ids) > 0
    else:
        g3['expand_pass'] = None
    g3['pass'] = bool(g3['unresolved_entries'] == 0 and not mf and g3['expand_pass'] is not False and n_cases > 0)
    R['gates']['G3_references'] = g3

    # ---- G4 duplicates
    exact = Counter(sha_text(json.dumps({k: v for k, v in c.items() if k not in STRIP}, sort_keys=True)) for c in cases)
    struct = Counter()
    for i, c in enumerate(cases):
        kinds = sorted(k for k in (rel_kind(e) for e in entries(c.get('component_relationships'))) if k)
        struct[sha_text(json.dumps([sorted(case_refs[i]), regime_of(c), domain_of(c), kinds]))] += 1
    g4 = {'exact_duplicates': sum(n - 1 for n in exact.values() if n > 1),
          'structural_duplicates': sum(n - 1 for n in struct.values() if n > 1),
          'distinct_structures': len(struct),
          'duplicate_case_ids': len(case_ids) - len(set(case_ids))}
    g4['pass'] = g4['exact_duplicates'] == 0 and g4['duplicate_case_ids'] == 0 and n_cases > 0
    R['gates']['G4_duplicates'] = g4

    # ---- G5 diversity floors
    regimes = Counter(regime_of(c) for c in cases)
    domains = Counter(domain_of(c) for c in cases)
    rel_cases = Counter()
    for c in cases:
        for k in set(k for k in (rel_kind(e) for e in entries(c.get('component_relationships'))) if k):
            rel_cases[k] += 1
    regime_vocab = set(k for k in regimes if k)
    cross_mention = cross_ingredient = 0
    for i, c in enumerate(cases):
        own = regime_of(c)
        rest = {k: v for k, v in c.items() if k != 'regime'}
        if set(s for s in strings(rest) if s in regime_vocab) - {own}:
            cross_mention += 1
        for rid in case_refs[i]:
            rec = ing.get(rid) or {}
            rg = rec.get('regimes') or rec.get('applicable_regimes')
            if isinstance(rg, list) and rg and own not in rg:
                cross_ingredient += 1
                break
    short = {}
    for rname, n in regimes.items():
        if n < floors['regime']:
            short['regime:%s' % rname] = n
    if len(regime_vocab) != 7:
        short['regime_count'] = len(regime_vocab)
    for d in ISIC:
        if domains.get(d, 0) < floors['isic']:
            short[d] = domains.get(d, 0)
    for d in FORD:
        if domains.get(d, 0) < floors['ford']:
            short[d] = domains.get(d, 0)
    for k, n in rel_cases.items():
        if n < floors['relation']:
            short['relation:%s' % k] = n
    cross = max(cross_mention, cross_ingredient)
    if cross < floors['cross']:
        short['cross_regime'] = cross
    unparsed = {k: v for k, v in domains.items() if k.startswith('OTHER')}
    cells = Counter((regime_of(c), domain_of(c)) for c in cases)
    short_cells = {}
    for rg in sorted(regime_vocab):
        for d in ISIC + FORD:
            if cells.get((rg, d), 0) < floors['cell']:
                short_cells['%s|%s' % (rg, d)] = cells.get((rg, d), 0)
    if short_cells:
        short['cells_below_floor'] = len(short_cells)
    g5 = {'regimes': dict(regimes), 'domains': dict(domains), 'relationship_kinds': dict(rel_cases),
          'cross_regime_by_mention': cross_mention, 'cross_regime_by_ingredient': cross_ingredient,
          'unparsed_domains': unparsed, 'shortfalls': short, 'cells_below_floor': short_cells,
          'cells_total': 7 * 27, 'cell_floor': floors['cell']}
    g5['pass'] = not short and not unparsed and n_cases > 0
    R['gates']['G5_diversity'] = g5

    # ---- G6 leak
    g6 = {'hard_keys': [], 'soft_keys': [], 'id_hits': [], 'phrase_hits': [], 'id_hit_count': 0, 'phrase_hit_count': 0}
    for f in ('dictionary.json', 'cases.jsonl', 'generate.py', 'checker.py', 'expand.py'):
        p = os.path.join(B, f)
        if not os.path.exists(p):
            continue
        txt = open(p, errors='replace').read()
        for m in ID_PATTERNS.finditer(txt):
            g6['id_hit_count'] += 1
            if len(g6['id_hits']) < 40:
                g6['id_hits'].append({'file': f, 'match': m.group(0),
                                      'context': txt[max(0, m.start() - 40):m.end() + 40].replace('\n', ' ')})
        low = txt.lower()
        for ph in PHRASES:
            i = low.find(ph)
            while i != -1:
                g6['phrase_hit_count'] += 1
                if len(g6['phrase_hits']) < 40:
                    g6['phrase_hits'].append({'file': f, 'phrase': ph,
                                              'context': txt[max(0, i - 40):i + len(ph) + 40].replace('\n', ' ')})
                i = low.find(ph, i + 1)
    allkeys = set(keys_of(D))
    for c in cases:
        allkeys |= set(keys_of(c))
    g6['hard_keys'] = sorted(k for k in allkeys if HARD_KEYS.search(k))
    g6['soft_keys'] = sorted(k for k in allkeys if SOFT_KEYS.search(k))
    g6['pass'] = not g6['hard_keys']
    R['gates']['G6_leak'] = g6

    # ---- G7 provenance
    prov = Counter()
    grounded = set()
    for rid, rec in ing.items():
        p = rec.get('provenance')
        src = ''
        if isinstance(p, dict):
            src = str(p.get('source', ''))
        elif isinstance(p, list) and p:
            q = p[0]
            src = str(q.get('source', '')) if isinstance(q, dict) else str(q)
        elif p is not None:
            src = str(p)
        s = src.lower()
        if 'raw.md' in s or 'assets' in s or 'inventor' in s:
            cls = 'inventory'
        elif 'isic' in s or 'ford' in s:
            cls = 'taxonomy'
        elif not s:
            cls = 'none'
        else:
            cls = 'authored'
        prov[cls] += 1
        if cls in ('inventory', 'taxonomy'):
            grounded.add(rid)
    total = sum(prov.values())
    share = (prov['inventory'] + prov['taxonomy']) / total if total else 0.0
    fully = sum(1 for i, c in enumerate(cases) if (case_refs[i] & ing_ids) and (case_refs[i] & ing_ids) <= grounded)
    g7 = {'ingredients_by_provenance': dict(prov), 'grounded_share': round(share, 4),
          'cases_fully_grounded': fully, 'cases_total': n_cases, 'floor': PROVENANCE_FLOOR}
    g7['pass'] = share >= PROVENANCE_FLOOR and total > 0
    R['gates']['G7_provenance'] = g7

    # ---- G8 runtime
    g8 = {'generate_seconds': gen_seconds, 'check_seconds': check_seconds, 'budget_seconds': RUNTIME_BUDGET_S * scale}
    if gen_seconds is not None and check_seconds is not None:
        g8['total_seconds'] = round(gen_seconds + check_seconds, 3)
        g8['pass'] = g8['total_seconds'] <= g8['budget_seconds']
    else:
        g8['pass'] = None
    R['gates']['G8_runtime'] = g8

    # ---- summary
    lines = []
    lines.append('G1 determinism  %s  seed=%s identical=%s differs_on_seed_b=%s' % (
        status(g1['pass']), g1.get('seed'), g1.get('identical'), g1.get('differs_on_seed_b')))
    if g2.get('batch'):
        lines.append('G2 checker      %s  batch rejected=%d undetermined=%d | broken %s/%s rejected | mutants %d/%d rejected, %d accepted, %d undetermined %s' % (
            status(g2['pass']), g2['batch']['rejected'], g2['batch']['undetermined'],
            g2['broken'].get('rejected', '?'), g2['broken'].get('examples', '?'),
            g2['mutations']['rejected'], g2['mutations']['mutants'], g2['mutations']['accepted'],
            g2['mutations']['undetermined'], json.dumps(g2['mutations']['by_kind'])))
    else:
        lines.append('G2 checker      SKIP')
    lines.append('G3 references   %s  entries=%d unresolved=%d (in %d cases) missing_fields=%s expand=%s' % (
        status(g3['pass']), g3['entries_checked'], g3['unresolved_entries'], g3['cases_with_unresolved'],
        json.dumps(g3['missing_fields']), status(g3['expand_pass'])))
    lines.append('G4 duplicates   %s  exact=%d structural=%d distinct_structures=%d duplicate_ids=%d' % (
        status(g4['pass']), g4['exact_duplicates'], g4['structural_duplicates'], g4['distinct_structures'], g4['duplicate_case_ids']))
    lines.append('G5 diversity    %s  regimes=%d domains=%d kinds=%d cross=%d/%d shortfalls=%s unparsed=%d' % (
        status(g5['pass']), len(regime_vocab), len(domains), len(rel_cases), cross, floors['cross'],
        json.dumps(short)[:300], sum(unparsed.values())))
    lines.append('G6 leak         %s  hard_keys=%s soft_keys=%s id_hits=%d phrase_hits=%d' % (
        status(g6['pass']), g6['hard_keys'], g6['soft_keys'][:10], g6['id_hit_count'], g6['phrase_hit_count']))
    lines.append('G7 provenance   %s  grounded_share=%.3f by=%s fully_grounded_cases=%d/%d' % (
        status(g7['pass']), share, json.dumps(dict(prov)), fully, n_cases))
    lines.append('G8 runtime      %s  generate=%s check=%s budget=%.0fs' % (
        status(g8['pass']), g8['generate_seconds'], g8['check_seconds'], g8['budget_seconds']))
    R['summary'] = lines
    R['all_pass'] = all(g.get('pass') is not False for g in R['gates'].values())
    out = a.report or os.path.join(B, 'gate_report.json')
    with open(out, 'w') as f:
        json.dump(R, f, indent=1, sort_keys=True)
    print('build: %s  cases=%d ingredients=%d bad_lines=%d' % (B, n_cases, len(ing), len(bad_lines)))
    for l in lines:
        print(l)
    print('report: %s' % out)
    sys.exit(0 if R['all_pass'] else 1)


if __name__ == '__main__':
    main()
