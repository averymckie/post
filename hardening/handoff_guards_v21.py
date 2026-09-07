"""Twentieth bounded adapter suite: P191-P200, the theoretical-requirement proofs.

These ten proofs are recorded in this TXT as "theoretical requirement; full chain not executed" and each names a
theoretical positive test, a theoretical adverse test, and a required-implementation-and-evidence section. This
module executes those named tests with the primitives the proofs themselves name, so that the specific claims stop
being theoretical, and records which parts remain unexecutable. It does not implement the proposed chains.

Every meaningful operation is a library primitive call: the controlled grammar is Lark, the typed AST is Pydantic,
applicability is Clingo under its own closed-world semantics, contradiction and coverage witnesses are Z3, graph
shape validation is pySHACL over rdflib, closure and cycles are NetworkX, span comparison is difflib over
unicodedata normalization, cardinality is a validated pandas merge, and canonical output is json with declared
ordering. Requires handoff_guards_v1.py from this TXT. All runtime inputs are authored fixtures. No model client
and no network.
Run: python handoff_guards_v21.py --report report.json
"""
from __future__ import annotations
import argparse, difflib, hashlib, importlib.metadata, itertools, json, logging, traceback, unicodedata, warnings
from pathlib import Path
from typing import Literal
from urllib.parse import urldefrag, urljoin
import clingo
import networkx as nx
import pandas as pd
import pyshacl
import z3
from lark import Lark, UnexpectedInput
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from rdflib import Graph
import handoff_guards_v1 as g
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)


def _quiet(code, message):
    """Clingo reports undefined atoms as info messages; the guards assert on the answer sets instead."""
    return None

# ---------------------------------------------------------------- P191
GRAMMAR = r'''
start: MODALITY actor "count" OP INT
MODALITY: "require" | "permit" | "forbid"
actor: WORD
OP: ">=" | "<=" | ">" | "<" | "=="
%import common.WORD
%import common.INT
%import common.WS
%ignore WS
'''
PARSER = Lark(GRAMMAR)


class RuleAST(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', frozen=True)
    modality: Literal['require', 'permit', 'forbid']
    actor: str = Field(min_length=1)
    operator: Literal['>=', '<=', '>', '<', '==']
    threshold: int = Field(ge=0)
    clause: str = Field(min_length=1)


def compile_rule(text: str, clause: str) -> RuleAST:
    try:
        tree = PARSER.parse(text)
    except UnexpectedInput as failure:
        raise g.Blocked('controlled language does not accept %r (%s)' % (text, type(failure).__name__))
    modality, actor, operator, threshold = tree.children
    return RuleAST.model_validate({'modality': str(modality), 'actor': str(actor.children[0]),
                                   'operator': str(operator), 'threshold': int(threshold), 'clause': clause})


def satisfies(rule: RuleAST, count: int) -> bool:
    solver = z3.Solver(); n = z3.Int('n')
    solver.add(n == count)
    solver.add({'>=': n >= rule.threshold, '<=': n <= rule.threshold, '>': n > rule.threshold,
                '<': n < rule.threshold, '==': n == rule.threshold}[rule.operator])
    return solver.check() == z3.sat


# ---------------------------------------------------------------- P192
SCOPE_PROGRAM = '''
region(eu). region(us).
rule_scope(r1, eu).
applies(R) :- rule_scope(R, X), request_region(X).
has_region :- request_region(_).
unresolved(R) :- rule_scope(R, _), not has_region.
'''


def applicability(request_region: str | None) -> list[str]:
    program = SCOPE_PROGRAM + ('request_region(%s).\n' % request_region if request_region else '')
    control = clingo.Control(['0'], logger=_quiet); control.add('base', [], program); control.ground([('base', [])])
    with control.solve(yield_=True) as handle:
        for model in handle:
            return sorted(str(a) for a in model.symbols(shown=True)
                          if str(a).startswith(('applies', 'unresolved')))
    raise g.Blocked('scope program has no answer set')


# ---------------------------------------------------------------- P193
def conflict_core(rules: dict) -> tuple[str, list[str]]:
    solver = z3.Solver(); n = z3.Int('n')
    for name, formula in rules.items():
        solver.assert_and_track(formula(n), name)
    state = solver.check()
    if state == z3.unsat:
        return 'contradiction', sorted(str(c) for c in solver.unsat_core())
    if state == z3.sat:
        return 'satisfiable', []
    return 'undecided', []


def core_is_minimal(rules: dict, core: list[str]) -> bool:
    n = z3.Int('n')
    for dropped in core:
        solver = z3.Solver()
        for name in core:
            if name != dropped:
                solver.assert_and_track(rules[name](n), name)
        if solver.check() != z3.sat:
            return False
    return True


# ---------------------------------------------------------------- P194
SHAPES = """
@prefix sh: <http://www.w3.org/ns/shacl#> . @prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:ControlShape a sh:NodeShape ; sh:targetClass ex:Control ;
  sh:property [ sh:path ex:owner ; sh:minCount 1 ] ;
  sh:property [ sh:path ex:evidenceDate ; sh:minCount 1 ; sh:datatype xsd:date ] .
"""


def shacl(data: str) -> tuple[bool, int]:
    shapes = Graph().parse(data=SHAPES, format='turtle')
    graph = Graph().parse(data=data, format='turtle')
    conforms, _, text = pyshacl.validate(graph, shacl_graph=shapes, advanced=True)
    return bool(conforms), sum(1 for line in text.splitlines() if 'Constraint Violation' in line)


def target_coverage(data: str, expected: list[str]) -> list[str]:
    """The independent inventory check the chain requires beside the shape validation."""
    graph = Graph().parse(data=data, format='turtle')
    present = {str(s).rsplit('/', 1)[-1] for s, _, o in graph
               if str(o) == 'http://example.org/Control'}
    return sorted(set(expected) - present)


# ---------------------------------------------------------------- P195
def spans(raw: str) -> dict:
    normalized = unicodedata.normalize('NFC', raw)
    return {'raw_codepoints': len(raw), 'nfc_codepoints': len(normalized),
            'raw_bytes': len(raw.encode('utf-8')), 'nfc_bytes': len(normalized.encode('utf-8')),
            'length_preserved': len(raw) == len(normalized)}


def change_kinds(before: str, after: str) -> list[str]:
    return [op[0] for op in difflib.SequenceMatcher(None, before, after).get_opcodes() if op[0] != 'equal']


# ---------------------------------------------------------------- P196
def resolve_reference(base: str, reference: str) -> tuple[str, str]:
    target, fragment = urldefrag(urljoin(base, reference))
    return target, fragment


def closure(edges: list[tuple[str, str]], root: str) -> list[str]:
    graph = nx.DiGraph(edges)
    if root not in graph:
        raise g.Blocked('root %r is not present in the reference graph' % root)
    return sorted(nx.descendants(graph, root))


def cycles(edges: list[tuple[str, str]]) -> list[list[str]]:
    graph = nx.DiGraph(edges)
    return [sorted(component) for component in nx.strongly_connected_components(graph) if len(component) > 1]


# ---------------------------------------------------------------- P197
def z3_states(count: int | None, threshold: int) -> set:
    n = z3.Int('n')
    out = set()
    for label, formula in (('true', n >= threshold), ('false', z3.Not(n >= threshold))):
        solver = z3.Solver()
        if count is not None:
            solver.add(n == count)
        solver.add(formula)
        if solver.check() == z3.sat:
            out.add(label)
    return out


def clingo_states(count: int | None, threshold: int) -> list[str]:
    program = 'approved :- count(N), N >= %d.\n#show approved/0.\n' % threshold
    if count is not None:
        program += 'count(%d).\n' % count
    control = clingo.Control(['0'], logger=_quiet); control.add('base', [], program); control.ground([('base', [])])
    with control.solve(yield_=True) as handle:
        for model in handle:
            return sorted(str(a) for a in model.symbols(shown=True))
    return []


def answer_sets(program: str) -> list[list[str]]:
    control = clingo.Control(['0'], logger=_quiet); control.add('base', [], program); control.ground([('base', [])])
    out = []
    with control.solve(yield_=True) as handle:
        for model in handle:
            out.append(sorted(str(a) for a in model.symbols(shown=True)))
    return sorted(out)


# ---------------------------------------------------------------- P198
def uncovered(rows, *, domain_low: int = 0):
    n = z3.Int('n'); solver = z3.Solver()
    solver.add(n >= domain_low)
    solver.add(z3.Not(z3.Or([row(n) for row in rows])))
    if solver.check() == z3.sat:
        return int(str(solver.model()[n]))
    return None


def overlapping(rows, *, domain_low: int = 0):
    n = z3.Int('n'); solver = z3.Solver()
    solver.add(n >= domain_low)
    solver.add(z3.And([row(n) for row in rows]))
    if solver.check() == z3.sat:
        return int(str(solver.model()[n]))
    return None


# ---------------------------------------------------------------- P199
def bound_approvals(cases: list[dict], approvals: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(cases).merge(pd.DataFrame(approvals), on='case',
                                     validate='one_to_one', indicator=True)


def gate(approval: dict, artifact: bytes, declared_sha: str, *, at: str) -> str:
    if hashlib.sha256(artifact).hexdigest() != declared_sha:
        return 'blocked: artifact does not match the bound hash'
    if approval['state'] != 'signed':
        return 'blocked: approval is %s' % approval['state']
    if approval['role'] != 'cpc':
        return 'blocked: approval role is %s' % approval['role']
    if approval['on'] > at:
        return 'blocked: approval post-dates the evaluation time'
    return 'satisfied'


# ---------------------------------------------------------------- P200
def canonical(rows: list[dict], *, sort_rows: bool) -> str:
    ordered = sorted(rows, key=lambda r: json.dumps(r, sort_keys=True)) if sort_rows else rows
    return json.dumps(ordered, sort_keys=True, separators=(',', ':'), allow_nan=False)


def manifest(items: list[dict]) -> dict:
    buckets = {'required': [], 'satisfied': [], 'missing': [], 'conflicting': [], 'unresolved': []}
    for item in items:
        if item['state'] not in buckets:
            raise g.Blocked('undeclared manifest state %r' % item['state'])
        buckets[item['state']].append(item['id'])
    return {k: sorted(v) for k, v in buckets.items()}


C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(191)
def the_controlled_grammar_refuses_what_it_does_not_support():
    rule = compile_rule('require voting count >= 4', 'S01-3.2')
    g.equal(rule.modality, 'require'); g.equal(rule.actor, 'voting')
    g.equal(rule.operator, '>='); g.equal(rule.threshold, 4); g.equal(rule.clause, 'S01-3.2')
    g.equal(satisfies(rule, 4), True)  # the four-member boundary satisfies it
    g.equal(satisfies(rule, 3), False)  # three does not
    g.equal(satisfies(rule, 5), True)
    for unsupported in ('not merely voting count >= 4', 'require voting count >= four',
                        'require voting count', 'forbid voting count >= -1'):
        g.rejects(g.Blocked, lambda t=unsupported: compile_rule(t, 'S01-3.2'))
    g.equal(compile_rule('forbid voting count >= 4', 'S01-3.2').modality, 'forbid')
    g.equal(compile_rule('permit voting count >= 4', 'S01-3.2').modality, 'permit')
    g.equal(compile_rule('require voting count >= 4', 'S01').modality
            != compile_rule('forbid voting count >= 4', 'S01').modality, True)
    g.rejects(ValidationError, lambda: RuleAST.model_validate(
        {'modality': 'demand', 'actor': 'voting', 'operator': '>=', 'threshold': 4, 'clause': 'S01'}))
    g.rejects(ValidationError, lambda: RuleAST.model_validate(
        {'modality': 'require', 'actor': 'voting', 'operator': '>=', 'threshold': 4}))
    return {'boundary_satisfied_at_four_not_three': True,
            'not_merely_is_refused_by_the_grammar': True,
            'modalities_stay_distinct': True}


@case(192)
def a_missing_dimension_does_not_become_every_dimension():
    bound = applicability('eu')
    g.equal(bound, ['applies(r1)'])
    absent = applicability(None)
    g.equal(absent, ['unresolved(r1)'])
    g.equal(any(a.startswith('applies') for a in absent), False)  # no catch-all was invented
    g.equal(applicability('us'), ['unresolved(r1)'] if False else [])  # out of scope, and not unresolved either
    g.equal(bound != absent, True)
    g.equal(len(applicability('eu')), 1)
    return {'bound_request_applies': True, 'missing_dimension_is_unresolved': True,
            'out_of_scope_is_neither_applies_nor_unresolved': True}


@case(193)
def the_unsat_core_names_a_sufficient_subset_not_the_conflicting_set():
    n_rules = {'r1': lambda n: n > 4, 'r2': lambda n: n > 3, 'r3': lambda n: n < 2, 'r4': lambda n: n > 0}
    state, core = conflict_core(n_rules)
    g.equal(state, 'contradiction')
    g.equal(len(core), 2)
    g.equal(core_is_minimal(n_rules, core), True)  # this core is minimal
    g.equal('r1' in core, False)  # yet r1 also contradicts r3 and is absent from it
    g.equal(conflict_core({'r1': n_rules['r1'], 'r3': n_rules['r3']})[0], 'contradiction')
    g.equal(sorted(conflict_core({'r1': n_rules['r1'], 'r3': n_rules['r3']})[1]), ['r1', 'r3'])
    disjoint = {'a': lambda n: n > 4, 'b': lambda n: n > 3}
    g.equal(conflict_core(disjoint)[0], 'satisfiable')
    g.equal(conflict_core(disjoint)[1], [])
    g.equal(core_is_minimal(n_rules, ['r2', 'r3']), True)
    g.equal(core_is_minimal(n_rules, ['r1', 'r2', 'r3']), False)  # a superset is not minimal
    return {'core_is_minimal_here': True, 'core_omits_an_equally_conflicting_rule': True,
            'minimality_needs_its_own_test': True}


@case(194)
def a_shape_report_conforms_when_it_targets_nothing():
    valid = """@prefix ex: <http://example.org/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:c1 a ex:Control ; ex:owner ex:alice ; ex:evidenceDate "2026-09-07"^^xsd:date ."""
    g.equal(shacl(valid), (True, 0))
    no_owner = """@prefix ex: <http://example.org/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:c1 a ex:Control ; ex:evidenceDate "2026-09-07"^^xsd:date ."""
    g.equal(shacl(no_owner), (False, 1))
    bad_date = """@prefix ex: <http://example.org/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:c1 a ex:Control ; ex:owner ex:alice ; ex:evidenceDate "not-a-date"^^xsd:date ."""
    g.equal(shacl(bad_date), (False, 1))
    wrong_class = """@prefix ex: <http://example.org/> . @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
ex:c1 a ex:Widget ; ex:evidenceDate "2026-09-07"^^xsd:date ."""
    g.equal(shacl(wrong_class), (True, 0))  # the same missing owner, now unreported
    g.equal(shacl('@prefix ex: <http://example.org/> .'), (True, 0))  # an empty graph conforms
    g.equal(shacl(wrong_class)[0] == shacl(valid)[0], True)  # indistinguishable by the report alone
    g.equal(target_coverage(valid, ['c1']), [])
    g.equal(target_coverage(wrong_class, ['c1']), ['c1'])  # only the inventory check catches it
    g.equal(target_coverage('@prefix ex: <http://example.org/> .', ['c1', 'c2']), ['c1', 'c2'])
    return {'wrong_class_node_conforms_vacuously': True, 'empty_graph_conforms': True,
            'independent_inventory_is_the_only_detector': True}


@case(195)
def normalization_moves_the_offsets_it_is_asked_to_preserve():
    composed = 'Café approves'
    measured = spans(composed)
    g.equal(measured['raw_codepoints'], 14); g.equal(measured['nfc_codepoints'], 13)
    g.equal(measured['raw_bytes'], 15); g.equal(measured['nfc_bytes'], 14)
    g.equal(measured['length_preserved'], False)  # an offset into the raw text does not index the normalized one
    precomposed = 'Café approves'
    g.equal(composed == precomposed, False)
    g.equal(unicodedata.normalize('NFC', composed) == precomposed, True)  # normalized equality hides the difference
    g.equal(spans(precomposed)['length_preserved'], True)
    g.equal(change_kinds('require count >= 4', 'require  count >= 4'), ['insert'])
    g.equal(change_kinds('require count >= 4', 'require count >= 5'), ['replace'])
    g.equal(change_kinds('members must not vote', 'members must vote'), ['delete'])
    g.equal(change_kinds('require count >= 4', 'require count >= 4'), [])
    g.equal(compile_rule('require voting count >= 4', 'v1').threshold
            != compile_rule('require voting count >= 5', 'v2').threshold, True)
    g.equal(compile_rule('require voting count >= 4', 'v1').threshold,
            compile_rule('require  voting count >= 4', 'v2').threshold)  # whitespace is not a semantic change
    return {'nfc_is_not_length_preserving': True, 'codepoints_lost': 1, 'bytes_lost': 1,
            'normalized_equality_hides_the_composed_form': True,
            'whitespace_and_threshold_changes_are_different_findings': True}


@case(196)
def a_reference_cycle_does_not_stop_the_closure():
    target, fragment = resolve_reference('https://example.org/cat/base.json', 'profile.json#ac-1')
    g.equal(target, 'https://example.org/cat/profile.json'); g.equal(fragment, 'ac-1')
    g.equal(resolve_reference('https://example.org/cat/base.json', '#ac-2')[1], 'ac-2')
    g.equal(closure([('cat', 'ac-1'), ('ac-1', 'ac-2'), ('ac-2', 'ac-3')], 'cat'), ['ac-1', 'ac-2', 'ac-3'])
    g.rejects(g.Blocked, lambda: closure([('cat', 'ac-1')], 'absent'))
    cyclic = [('a', 'b'), ('b', 'c'), ('c', 'a'), ('d', 'a')]
    g.equal(cycles(cyclic), [['a', 'b', 'c']])
    g.equal(closure(cyclic, 'd'), ['a', 'b', 'c'])  # the closure returns normally over the cycle
    g.equal(nx.is_directed_acyclic_graph(nx.DiGraph(cyclic)), False)
    g.equal(cycles([('cat', 'ac-1'), ('ac-1', 'ac-2')]), [])  # so the cycle test must be run separately
    g.equal(len(closure(cyclic, 'd')) == len(closure([('cat', 'ac-1'), ('ac-1', 'ac-2')], 'cat')) + 1, True)
    return {'fragment_resolution_is_urllib': True, 'closure_succeeds_over_a_cycle': True,
            'cycle_detection_is_a_separate_call': True}


@case(197)
def the_two_engines_disagree_on_the_same_missing_count():
    g.equal(z3_states(4, 4), {'true'}); g.equal(z3_states(3, 4), {'false'}); g.equal(z3_states(5, 4), {'true'})
    g.equal(clingo_states(4, 4), ['approved']); g.equal(clingo_states(3, 4), [])
    g.equal(clingo_states(5, 4), ['approved'])
    for count in (3, 4, 5):
        g.equal(('true' in z3_states(count, 4)), (clingo_states(count, 4) == ['approved']))
    g.equal(z3_states(None, 4), {'true', 'false'})  # unknown: both remain satisfiable
    g.equal(clingo_states(None, 4), [])  # closed world: simply not approved
    g.equal(len(z3_states(None, 4)) > 1 and clingo_states(None, 4) == [], True)
    g.equal(z3_states(None, 4) == {'true'} or z3_states(None, 4) == {'false'}, False)
    sets = answer_sets('{ a; b } = 1.')
    g.equal(sets, [['a'], ['b']]); g.equal(len(sets), 2)  # not a unique decision
    g.equal(len(answer_sets('a.')), 1)
    return {'engines_agree_on_every_known_count': True,
            'unknown_is_both_states_in_z3_and_absent_in_clingo': True,
            'multiple_answer_sets_are_not_one_decision': True}


@case(198)
def the_gap_is_exactly_at_the_boundary():
    g.equal(uncovered([lambda n: n < 4, lambda n: n >= 4]), None)  # a true partition leaves nothing
    g.equal(uncovered([lambda n: n < 4, lambda n: n > 4]), 4)  # the mutation exposes n = 4
    g.equal(overlapping([lambda n: n < 4, lambda n: n >= 4]), None)
    g.equal(overlapping([lambda n: n >= 4, lambda n: n >= 3]), 4)  # the added row overlaps at n = 4
    g.equal(overlapping([lambda n: n >= 4, lambda n: n < 3]), None)
    g.equal(uncovered([lambda n: n >= 0]), None)
    g.equal(uncovered([lambda n: n > 0]), 0)  # the domain floor is its own boundary
    g.equal(uncovered([lambda n: n < 4, lambda n: n > 4], domain_low=5), None)  # totality is relative to the domain
    g.equal(uncovered([lambda n: n < 4, lambda n: n > 4], domain_low=0), 4)
    known = list(itertools.product(range(3), repeat=2))
    g.equal(len(known), 9)  # the enumerated finite domain the solver result is relative to
    return {'partition_has_no_gap': True, 'gap_witness': 4, 'overlap_witness': 4,
            'totality_is_relative_to_the_declared_domain': True}


@case(199)
def a_role_label_is_not_an_authentication():
    artifact = b'charter v1'
    declared = hashlib.sha256(artifact).hexdigest()
    signed = {'state': 'signed', 'role': 'cpc', 'on': '2026-09-01'}
    g.equal(gate(signed, artifact, declared, at='2026-09-07'), 'satisfied')
    g.equal(gate(signed, artifact + b'.', declared, at='2026-09-07'),
            'blocked: artifact does not match the bound hash')
    g.equal(gate({'state': 'draft', 'role': 'cpc', 'on': '2026-09-01'}, artifact, declared, at='2026-09-07'),
            'blocked: approval is draft')
    g.equal(gate({'state': 'withdrawn', 'role': 'cpc', 'on': '2026-09-01'}, artifact, declared, at='2026-09-07'),
            'blocked: approval is withdrawn')
    g.equal(gate({'state': 'signed', 'role': 'reviewer', 'on': '2026-09-01'}, artifact, declared, at='2026-09-07'),
            'blocked: approval role is reviewer')
    g.equal(gate(signed, artifact, declared, at='2026-08-01'),
            'blocked: approval post-dates the evaluation time')
    outcomes = {gate(a, artifact, declared, at='2026-09-07') for a in
                ({'state': 'draft', 'role': 'cpc', 'on': '2026-09-01'},
                 {'state': 'signed', 'role': 'reviewer', 'on': '2026-09-01'})}
    g.equal(len(outcomes), 2)  # each blocked reason stays distinct
    joined = bound_approvals([{'case': 'K1', 'artifact': 'a1'}, {'case': 'K2', 'artifact': 'a2'}],
                             [{'case': 'K1', 'role': 'cpc'}, {'case': 'K2', 'role': 'cpc'}])
    g.equal(len(joined), 2); g.equal(sorted(joined['_merge'].astype(str).unique()), ['both'])
    g.rejects(pd.errors.MergeError, lambda: bound_approvals(
        [{'case': 'K1', 'artifact': 'a1'}],
        [{'case': 'K1', 'role': 'cpc'}, {'case': 'K1', 'role': 'reviewer'}]))
    return {'hash_binding_precedes_the_role_check': True, 'each_block_reason_is_distinct': True,
            'duplicate_approval_is_refused_by_cardinality': True,
            'no_signature_was_authenticated': True}


@case(200)
def canonical_key_order_is_not_canonical_row_order():
    rows = [{'b': 2, 'a': 1}, {'a': 3, 'b': 4}]
    g.equal(canonical(rows, sort_rows=False), '[{"a":1,"b":2},{"a":3,"b":4}]')  # keys normalized
    g.equal(canonical(rows, sort_rows=False) == canonical(list(reversed(rows)), sort_rows=False), False)
    g.equal(canonical(rows, sort_rows=True), canonical(list(reversed(rows)), sort_rows=True))  # rows too
    g.equal(hashlib.sha256(canonical(rows, sort_rows=True).encode()).hexdigest(),
            hashlib.sha256(canonical(list(reversed(rows)), sort_rows=True).encode()).hexdigest())
    g.equal(hashlib.sha256(canonical(rows, sort_rows=False).encode()).hexdigest()
            == hashlib.sha256(canonical(list(reversed(rows)), sort_rows=False).encode()).hexdigest(), False)
    items = [{'id': 'c1', 'state': 'satisfied'}, {'id': 'c2', 'state': 'missing'},
             {'id': 'c3', 'state': 'conflicting'}, {'id': 'c4', 'state': 'unresolved'}]
    built = manifest(items)
    g.equal(built['satisfied'], ['c1']); g.equal(built['missing'], ['c2'])
    g.equal(built['conflicting'], ['c3']); g.equal(built['unresolved'], ['c4'])
    g.equal(built['required'], [])
    g.equal(sum(len(v) for v in built.values()), 4)  # every item lands in exactly one bucket
    g.rejects(g.Blocked, lambda: manifest([{'id': 'c5', 'state': 'ready'}]))
    g.equal(manifest(items) == manifest(list(reversed(items))), True)  # input order does not change the manifest
    return {'sort_keys_does_not_order_rows': True, 'row_sort_is_required_for_a_stable_hash': True,
            'undeclared_manifest_state_is_blocked': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['clingo', 'lark', 'networkx', 'pandas', 'pydantic', 'pyshacl', 'rdflib', 'z3-solver']
    here = Path(__file__).resolve().parent
    return {'scope': 'Executes the named theoretical positive and adverse tests of P191-P200 with the primitives those proofs name. The proposed chains themselves were not implemented and no proof artifact was produced.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
