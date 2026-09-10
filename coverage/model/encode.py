#!/usr/bin/env python3
"""Mechanical encoding of the framework master into data.

Every field is read from the master's own labelled lines, tables and fenced
chains; no judgment is applied. The output is the model under test for the
reverse-engineering engine. It is never supplied to the case generator.

Usage: python3 encode.py [MASTER_PATH] [OUT_DIR]
Writes OUT_DIR/catalogue.json and OUT_DIR/encode_report.txt.
"""
import hashlib, json, os, re, sys
from collections import OrderedDict, defaultdict

MASTER = sys.argv[1] if len(sys.argv) > 1 else '/root/.claude/uploads/29b9af63-7d01-5359-bed5-a0fd619c61bc/7af1d490-frameworkmaster.txt'
OUT_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.abspath(__file__))

text = open(MASTER, encoding='utf-8').read()
lines = text.split('\n')
SHA = hashlib.sha256(text.encode('utf-8')).hexdigest()


def find_line(prefix, start=0):
    for i in range(start, len(lines)):
        if lines[i].startswith(prefix):
            return i
    raise KeyError(prefix)


def id_list(s):
    s = s.strip().rstrip('.')
    if not s or s.lower().startswith('none'):
        return []
    return [x.strip() for x in re.split(r'[,;]\s*', s) if x.strip()]


def semi_list(s):
    s = s.strip().rstrip('.')
    return [x.strip() for x in s.split(';') if x.strip()]


def questions(s):
    return [q.strip() + '?' for q in s.strip().split('?') if q.strip()]


def parse_tables(seg):
    tables, cur = [], None
    for ln in seg:
        if ln.startswith('|'):
            cells = [c.strip() for c in ln.strip().strip('|').split('|')]
            if all(re.fullmatch(r'-+', c) for c in cells):
                continue
            if cur is None:
                cur = (tuple(cells), [])
                tables.append(cur)
            else:
                cur[1].append(cells)
        else:
            cur = None
    return tables


def fenced_blocks(seg):
    blocks, cur = [], None
    for ln in seg:
        if ln.startswith('```'):
            if cur is None:
                cur = []
            else:
                blocks.append(cur)
                cur = None
        elif cur is not None:
            cur.append(ln)
    return blocks


def labelled(seg, labels):
    """Single-line 'Label: value' fields; returns dict label -> value (first occurrence)."""
    out = OrderedDict()
    for ln in seg:
        m = re.match(r'^([A-Za-z][A-Za-z /-]*?):\s*(.*)$', ln)
        if m and m.group(1) in labels and m.group(1) not in out:
            out[m.group(1)] = m.group(2).strip()
    return out


s2 = find_line('## 2. '); s3 = find_line('## 3. '); s4 = find_line('## 4. '); s5 = find_line('## 5. ')
s6 = find_line('## 6. '); s7 = find_line('## 7. '); s7b = find_line('### Prerequisite order'); s8 = find_line('## 8. ')
s9 = find_line('## 9. '); s10 = find_line('## 10. ')

cat = OrderedDict()
cat['source'] = {'file': os.path.basename(MASTER), 'sha256': SHA, 'lines': len(lines)}
cat['order_of_operations_text'] = '\n'.join(lines[s2:s3]).strip()
cat['execution_contract_text'] = '\n'.join(lines[s3:s4]).strip()
hg = OrderedDict()
for ln in lines[s3:s4]:
    m = re.match(r'^\|?\s*(HG0\d)\s*[|:.\-]\s*(.*)$', ln)
    if m:
        hg[m.group(1)] = m.group(2).strip().strip('|').strip()
cat['execution_contract'] = hg

# ---- section 4: grammar
g = lines[s4:s5]
prods = []
for ln in fenced_blocks(g)[0]:
    m = re.match(r'^\s*(?:System\s*:=|\|)\s*(.+)$', ln)
    if m:
        prods.append(m.group(1).strip())
cat['grammar_productions'] = prods
O, C, A, BND, V, FS = OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict(), OrderedDict()
for header, rows in parse_tables(g):
    if header[:2] == ('ID', 'Operation class'):
        for r in rows:
            O[r[0]] = OrderedDict(id=r[0], name=r[1], signature=r[2], obligation=r[3])
    elif header[:2] == ('ID', 'Composition'):
        for r in rows:
            C[r[0]] = OrderedDict(id=r[0], name=r[1], form=r[2], obligation=r[3])
    elif header[:2] == ('ID', 'Axis'):
        for r in rows:
            A[r[0]] = OrderedDict(id=r[0], axis=r[1], values=[v.strip() for v in r[2].split(',')])
    elif header[:2] == ('Field', 'Required contract'):
        for r in rows:
            BND[r[0]] = r[1]
    elif header[:2] == ('Rule', 'Selected feature'):
        for r in rows:
            V[r[0]] = OrderedDict(id=r[0], feature=r[1], capabilities=semi_list(r[2]),
                                  proof_requirements=[x.strip() for x in r[3].split(',')])
    elif header[:2] == ('Record', 'Required content'):
        for r in rows:
            FS[r[0]] = r[1]
cat['operations'] = O; cat['compositions'] = C; cat['axes'] = A; cat['boundary_fields'] = BND
cat['variation_rules'] = V; cat['familyspec_records'] = FS
cat['guard_generation_text'] = '\n'.join(lines[s5:s6]).strip()

# ---- section 6: families
FAM_LABELS = {'Product contract': ('product_contract', 'text'), 'Input roles': ('input_roles', 'semi'),
              'Output roles': ('output_roles', 'semi'), 'Variation': ('variation', 'semi'),
              'Configurator questions': ('configurator_questions', 'q'), 'Acceptance': ('acceptance', 'text'),
              'Composition': ('composition', 'text'), 'Operation classes': ('operation_classes', 'ids'),
              'Existing anchors': ('existing_anchors', 'ids'),
              'Specific proof requirements': ('specific_proof_requirements', 'ids'),
              'Mapped extensions': ('mapped_extensions', 'ids')}
CONV = {'text': lambda s: s.strip(), 'semi': semi_list, 'q': questions, 'ids': id_list}


def parse_cards(seg, header_re, labels):
    cards, cur, body = OrderedDict(), None, []

    def flush():
        if cur is not None:
            got = labelled(body, labels)
            for lab, (key, kind) in labels.items():
                cur[key] = CONV[kind](got[lab]) if lab in got else None
            cur['_body'] = body[:]
            cards[cur['id']] = cur
    for ln in seg:
        m = header_re.match(ln)
        if m:
            flush()
            cur, body = OrderedDict(id=m.group(1), title=m.group(2).strip()), []
        elif cur is not None:
            body.append(ln)
    flush()
    return cards


F = parse_cards(lines[s6:s7], re.compile(r'^### (F\d{2})\. (.+)$'), FAM_LABELS)
cat['families_preamble'] = '\n'.join(lines[s6 + 1:find_line('### F01', s6)]).strip()
for f in F.values():
    del f['_body']
cat['families'] = F

# ---- section 7: required claims
R_LABELS = {'Required claim': ('required_claim', 'text'), 'Required evidence': ('required_evidence', 'text'),
            'Existing anchors': ('existing_anchors', 'ids'), 'Prerequisites': ('prerequisites', 'ids'),
            'Mapped proofs': ('mapped_proofs', 'ids'), 'Literal projection profile': ('literal_projection_profile', 'text')}
R = parse_cards(lines[s7:s7b], re.compile(r'^### (R\d{2})\. (.+)$'), R_LABELS)
for r in R.values():
    r['prerequisites'] = [x for x in (r['prerequisites'] or []) if re.fullmatch(r'R\d{2}', x)]
    del r['_body']
cat['required_claims'] = R
layers = []
for ln in lines[s7b:s8]:
    m = re.match(r'^(\d+)\. (P.+)$', ln)
    if m:
        layers.append(id_list(m.group(2)))
cat['prerequisite_layers_P301_P349'] = layers

# ---- section 8: chains
X_LABELS = {'Families': ('families', 'ids'), 'Inputs': ('inputs', 'text'), 'Generated product': ('generated_product', 'text'),
            'Emergent obligations': ('emergent_obligations', 'text'), 'Change propagation': ('change_propagation', 'text'),
            'Proof requirements': ('proof_requirements', 'ids')}
X = parse_cards(lines[s8:s9], re.compile(r'^### (X\d{2})\. (.+)$'), X_LABELS)
for x in X.values():
    b = []
    for ln in x['_body']:
        m = re.match(r'^(\d+)\) (.+)$', ln)
        if m:
            b.append(OrderedDict(n=int(m.group(1)), text=m.group(2).strip(), families=re.findall(r'\bF\d{2}\b', m.group(2))))
    x['bindings'] = b
    del x['_body']
cat['chains'] = X

# ---- section 9: libraries
L = OrderedDict(); cur = None
for ln in lines[s9:s10]:
    m = re.match(r'^### (L\d{2}) \| (.+?) \| (.+?) \| (.+)$', ln)
    if m:
        cur = OrderedDict(id=m.group(1), name=m.group(2).strip(), version=m.group(3).strip(), package=m.group(4).strip(), entries=[])
        L[cur['id']] = cur
        continue
    if cur is None:
        continue
    m = re.match(r'^(Role|Assurance|Boundary|Recorded project sources): (.*)$', ln)
    if m:
        cur[m.group(1).lower().replace(' ', '_')] = m.group(2).strip()
        continue
    m = re.match(r'^  (L\d{2}\.\w+): (.+)$', ln)
    if m:
        cur['entries'].append(OrderedDict(ref=m.group(1), callable=m.group(2).strip()))
        continue
    m = re.match(r'^    Contract: (.+)$', ln)
    if m and cur['entries']:
        cur['entries'][-1]['contract'] = m.group(1).strip()
cat['libraries'] = L
cat['library_preamble'] = '\n'.join(lines[s9 + 1:find_line('### L01', s9)]).strip()

# ---- section 10: proof records
P = OrderedDict()
hdr = re.compile(r'^## (P\d+)\s+(.+)$')
starts = [i for i in range(s10, len(lines)) if hdr.match(lines[i])]
starts.append(len(lines))
cat['proof_preamble'] = '\n'.join(lines[s10 + 1:starts[0]]).strip()
STEP = re.compile(r'^-> (.*?)(?: \((.*)\))?$')
for a, b in zip(starts, starts[1:]):
    m = hdr.match(lines[a])
    pid, title = m.group(1), m.group(2).strip()
    body = lines[a + 1:b]
    if body and body[-1].startswith('End of framework specification'):
        body = body[:-1]
    rec = OrderedDict(id=pid, title=title, title_roles=[t.strip() for t in title.split('->')])
    pf = re.search(r'^Primary family: (F\d{2}|UNASSIGNED)', '\n'.join(body), re.M)
    rec['primary_family'] = pf.group(1) if pf else None
    joined = '\n'.join(body)
    if re.search(r'^State:', joined, re.M):
        rec['class'] = 'specified'
    elif '**theoretical requirement' in joined:
        rec['class'] = 'theoretical'
    elif re.search(r'^Status:', joined, re.M):
        rec['class'] = 'historical'
    else:
        rec['class'] = 'unknown'
    up = labelled(body, {'Status', 'Recorded defect class', 'State', 'Requirements', 'Existing anchors', 'Proof prerequisites',
                         'Admitted profile', 'Input contract', 'Output contract', 'Independent oracle/invariant',
                         'Generated positive guards', 'Generated adverse guards', 'Library references'})
    for k, v in up.items():
        key = k.lower().replace(' ', '_').replace('/', '_')
        if k in ('Requirements', 'Existing anchors', 'Proof prerequisites'):
            v = id_list(v)
        rec[key] = v
    low = OrderedDict()
    for ln in body:
        m2 = re.match(r'^(reuses|new capability|contract|theoretical positive test|theoretical adverse test|assessment|public-data limit|required implementation and evidence): (.*)$', ln)
        if m2 and m2.group(1) not in low:
            low[m2.group(1)] = m2.group(2).strip()
    for k, v in low.items():
        rec[k.replace(' ', '_').replace('-', '_')] = v
    if 'assessment' in rec:
        m3 = re.match(r'([A-Z_]+)', rec['assessment'])
        rec['assessment_code'] = m3.group(1) if m3 else None
    blocks = fenced_blocks(body)
    chain = None
    for blk in blocks:
        if any(l.startswith('-> ') for l in blk):
            chain = blk
            break
    if chain is not None:
        steps, inputs, outputs = [], [], None
        for l in chain:
            if not l.strip():
                continue
            if l.startswith('-> '):
                m4 = STEP.match(l.rstrip())
                name, funcs = m4.group(1).strip(), m4.group(2)
                steps.append(OrderedDict(step=name, functions=funcs))
            elif not steps:
                inputs.append(l.strip())
        if steps and steps[-1]['functions'] is None:
            outputs = steps.pop()['step']
        rec['chain'] = OrderedDict(inputs=' '.join(inputs), steps=steps, outputs=outputs)
    # recorded pins: the fenced block after 'Recorded chain pins:' / 'Recorded pins:'
    for i, ln in enumerate(body):
        if re.match(r'^Recorded (chain )?pins:', ln):
            for blk in blocks:
                pos = body.index(blk[0]) if blk and blk[0] in body else -1
                if pos > i:
                    rec['recorded_pins'] = '\n'.join(blk).strip()
                    break
            break
    hd = OrderedDict()
    for i, ln in enumerate(body):
        m5 = re.match(r'^### HARDENING (P\d+) -- (.*)$', ln)
        if m5:
            hd['title'] = m5.group(2).strip()
            rest = [x for x in body[i + 1:] if x.strip()]
            if rest and not re.match(r'^(functions|sources):', rest[0]):
                hd['chain'] = rest[0].strip()
            for x in rest[:4]:
                m6 = re.match(r'^(functions|sources): (.*)$', x)
                if m6:
                    hd[m6.group(1)] = m6.group(2).strip()
            break
    if hd:
        rec['hardening'] = hd
    stages = []
    for i, ln in enumerate(body):
        m7 = re.match(r'^  (P\d+\.S\d+): (\S+) -> (\S+)$', ln)
        if m7:
            st = OrderedDict(id=m7.group(1), input=m7.group(2), output=m7.group(3), functions=[], stage_contract=None)
            for x in body[i + 1:i + 4]:
                m8 = re.match(r'^    Functions: (.*)$', x)
                if m8:
                    for fn in m8.group(1).split(';'):
                        fn = fn.strip()
                        if not fn:
                            continue
                        parts = fn.split(' ', 1)
                        st['functions'].append(OrderedDict(ref=parts[0], callable=parts[1] if len(parts) > 1 else None))
                m9 = re.match(r'^    Stage contract: (.*)$', x)
                if m9:
                    st['stage_contract'] = m9.group(1).strip()
            stages.append(st)
    if stages:
        rec['stages'] = stages
    rw = []
    on = False
    for ln in body:
        if ln.startswith('Remaining work:'):
            on = True
            continue
        if on:
            m10 = re.match(r'^  - (.*)$', ln)
            if m10:
                rw.append(m10.group(1).strip())
            elif ln.strip():
                on = False
    if rw:
        rec['remaining_work'] = rw
    P[pid] = rec
cat['proofs'] = P

# ---- indexes
idx = OrderedDict()
role_out, role_in = defaultdict(list), defaultdict(list)
for f in F.values():
    for r in f['output_roles'] or []:
        role_out[r].append(f['id'])
    for r in f['input_roles'] or []:
        role_in[r].append(f['id'])
roles = sorted(set(role_out) | set(role_in))
idx['roles'] = OrderedDict((r, OrderedDict(produced_by=role_out.get(r, []), consumed_by=role_in.get(r, []))) for r in roles)
op_fam = defaultdict(list)
for f in F.values():
    for o in f['operation_classes'] or []:
        op_fam[o].append(f['id'])
idx['operation_to_families'] = OrderedDict((o, op_fam.get(o, [])) for o in O)
p_fam_anchor, p_fam_ext, p_req_anchor, p_req_mapped = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
for f in F.values():
    for p in f['existing_anchors'] or []:
        p_fam_anchor[p].append(f['id'])
    for p in f['mapped_extensions'] or []:
        p_fam_ext[p].append(f['id'])
for r in R.values():
    for p in r['existing_anchors'] or []:
        p_req_anchor[p].append(r['id'])
    for p in r['mapped_proofs'] or []:
        p_req_mapped[p].append(r['id'])
idx['proof_to_families'] = OrderedDict()
for pid, rec in P.items():
    idx['proof_to_families'][pid] = OrderedDict(primary=rec['primary_family'], anchoring=p_fam_anchor.get(pid, []),
                                                extension_of=p_fam_ext.get(pid, []), anchoring_requirements=p_req_anchor.get(pid, []),
                                                mapped_by_requirements=p_req_mapped.get(pid, []),
                                                declared_requirements=rec.get('requirements', []))
fam_proofs = OrderedDict()
for f in F.values():
    prim = [pid for pid, rec in P.items() if rec['primary_family'] == f['id']]
    fam_proofs[f['id']] = OrderedDict(primary=prim, anchors=f['existing_anchors'] or [], extensions=f['mapped_extensions'] or [])
idx['family_to_proofs'] = fam_proofs
cat['indexes'] = idx

# ---- integrity checks
rep = []
rep.append('master sha256 %s lines %d' % (SHA, len(lines)))
counts = OrderedDict(families=len(F), operations=len(O), compositions=len(C), axes=len(A), boundary_fields=len(BND),
                     variation_rules=len(V), familyspec_records=len(FS), execution_contract_entries=len(hg),
                     grammar_productions=len(prods), required_claims=len(R), prerequisite_layers=len(layers),
                     chains=len(X), libraries=len(L), proofs=len(P), roles=len(roles))
for k, v in counts.items():
    rep.append('%-28s %d' % (k, v))
expected = dict(families=38, operations=18, compositions=14, axes=18, boundary_fields=14, variation_rules=18,
                required_claims=32, chains=12, libraries=65, proofs=349)
bad = [(k, counts[k], v) for k, v in expected.items() if counts[k] != v]
rep.append('expected counts: ' + ('all match' if not bad else 'MISMATCH %s' % bad))
cls = defaultdict(int)
for rec in P.values():
    cls[rec['class']] += 1
rep.append('proof classes: %s' % dict(cls))
missing_fields = defaultdict(int)
for f in F.values():
    for lab, (key, kind) in FAM_LABELS.items():
        if f[key] is None:
            missing_fields[key] += 1
rep.append('family cards with a missing label: %s' % (dict(missing_fields) or 'none'))
errs = []
for f in F.values():
    for o in f['operation_classes'] or []:
        if o not in O:
            errs.append('%s operation %s unknown' % (f['id'], o))
    for p in (f['existing_anchors'] or []) + (f['mapped_extensions'] or []):
        if p not in P:
            errs.append('%s proof %s unknown' % (f['id'], p))
    for r in f['specific_proof_requirements'] or []:
        if r not in R:
            errs.append('%s requirement %s unknown' % (f['id'], r))
for r in R.values():
    for p in (r['existing_anchors'] or []) + (r['mapped_proofs'] or []):
        if p not in P:
            errs.append('%s proof %s unknown' % (r['id'], p))
    for q in r['prerequisites']:
        if q not in R:
            errs.append('%s prerequisite %s unknown' % (r['id'], q))
for v in V.values():
    for r in v['proof_requirements']:
        if re.fullmatch(r'R\d{2}', r) and r not in R:
            errs.append('%s requirement %s unknown' % (v['id'], r))
for x in X.values():
    for f in x['families'] or []:
        if f not in F:
            errs.append('%s family %s unknown' % (x['id'], f))
    for r in x['proof_requirements'] or []:
        if r not in R:
            errs.append('%s requirement %s unknown' % (x['id'], r))
for pid, rec in P.items():
    if rec['primary_family'] not in F and rec['primary_family'] != 'UNASSIGNED':
        errs.append('%s primary family %s unknown' % (pid, rec['primary_family']))
    for q in rec.get('existing_anchors', []) + rec.get('proof_prerequisites', []):
        if q not in P:
            errs.append('%s proof ref %s unknown' % (pid, q))
    for r in rec.get('requirements', []):
        if r not in R:
            errs.append('%s requirement %s unknown' % (pid, r))
    for st in rec.get('stages', []):
        for fn in st['functions']:
            if fn['ref'].split('.')[0] not in L:
                errs.append('%s stage %s library %s unknown' % (pid, st['id'], fn['ref']))
    if rec['class'] in ('historical', 'theoretical') and 'chain' not in rec:
        errs.append('%s has no parsed chain' % pid)
    if rec['class'] == 'specified' and not rec.get('stages'):
        errs.append('%s has no parsed stages' % pid)
    if rec['class'] == 'historical' and 'hardening' not in rec:
        errs.append('%s has no hardening block' % pid)
layer_ids = [p for lay in layers for p in lay]
rep.append('prerequisite layers cover %d proofs; expected P301-P349: %s' % (len(layer_ids), sorted(set(layer_ids)) == ['P%d' % i for i in range(301, 350)] or 'MISMATCH'))
rep.append('reference errors: %d' % len(errs))
no_hd = [pid for pid, rec in P.items() if rec['class'] == 'theoretical' and 'hardening' not in rec]
rep.append('theoretical records without a hardening block in the master (informational): %d (%s..%s)' % (len(no_hd), no_hd[0] if no_hd else '-', no_hd[-1] if no_hd else '-'))
ext_in = [r for r in roles if not role_out.get(r)]
rep.append('input roles supplied from outside every family (operating-model inputs): %d' % len(ext_in))
rep.extend('  ' + e for e in errs[:60])
unanchored = [f['id'] for f in F.values() if not f['existing_anchors']]
rep.append('families with no existing anchors: %s' % (unanchored or 'none'))
noprim = [f['id'] for f in F.values() if not fam_proofs[f['id']]['primary']]
rep.append('families with no primary proof record: %s' % (noprim or 'none'))
orphan_roles = [r for r in roles if not role_out.get(r)]
rep.append('input roles no family produces (%d): %s' % (len(orphan_roles), orphan_roles))
sink_roles = [r for r in roles if not role_in.get(r)]
rep.append('output roles no family consumes (%d): %s' % (len(sink_roles), sink_roles))

os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, 'catalogue.json'), 'w') as fh:
    json.dump(cat, fh, indent=1, ensure_ascii=False)
with open(os.path.join(OUT_DIR, 'encode_report.txt'), 'w') as fh:
    fh.write('\n'.join(rep) + '\n')
print('\n'.join(rep))
