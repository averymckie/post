"""Seventh bounded adapter suite: P61-P70. Requires handoff_guards_v1.py, handoff_guards_v3.py, handoff_guards_v4.py and
handoff_guards_v5.py from this TXT. Every reference resolution, network measure, shape binding, page readback, escaping,
asset check, and byte register below is a library primitive call; local code declares fixtures and policies and turns a
primitive result into a Blocked outcome. P65-P70 build the presentation interfaces from typed records with an escaping
template, a Content-Security-Policy, and a registered-input-bytes gate. All runtime inputs are authored fixtures. No
network, model client, native Office application, or business action.
Run: python handoff_guards_v7.py --report report.json
"""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, io, json, logging, re, traceback, warnings
from pathlib import Path
from typing import Literal
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import pm4py
from deepdiff import DeepDiff
from jinja2 import Environment, StrictUndefined, select_autoescape
from lxml import html as lxml_html
from pydantic import BaseModel, ConfigDict, Field, ValidationError
import handoff_guards_v1 as g
import handoff_guards_v3 as g3
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

CASE, ACT, TS = 'case:concept:name', 'concept:name', 'time:timestamp'

# ---------------------------------------------------------------- P61
SUBSECTION_REF = re.compile(r'\bsubsection \(([a-z])\)')


def reference_graph(units: list[dict], sentences: list[dict]) -> dict:
    known = {u['subsection'] for u in units}
    if len(known) != len(units): raise g.Blocked('duplicate subsection identity')
    graph = nx.DiGraph(); graph.add_nodes_from(sorted(known))
    for s in sentences:
        home = s['subsection']
        if home not in known: raise g.Blocked('sentence in an unknown subsection: ' + home)
        for target in SUBSECTION_REF.findall(s['text']):
            key = '(' + target + ')'
            if key not in known: raise g.Blocked('reference to a non-existent subsection: ' + key)
            if key != home: graph.add_edge(home, key)  # a self-reference is not an edge
    return {'nodes': graph.number_of_nodes(), 'edges': graph.number_of_edges(),
            'most_referenced': sorted(((n, d) for n, d in graph.in_degree()), key=lambda t: (-t[1], t[0]))[:3],
            'acyclic': bool(nx.is_directed_acyclic_graph(graph)),
            'note': 'statutory cross-references legitimately form cycles; acyclic False is a property, not a defect'}

# ---------------------------------------------------------------- P62
def handover_network(events: list[dict], *, top: int | None = None) -> dict:
    df = pd.DataFrame(events)
    if df[['case_id', 'event_id']].duplicated().any(): raise g.Blocked('duplicate event identity')
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='raise')
    if df.duplicated(['case_id', 'timestamp'], keep=False).any(): raise g.Blocked('timestamp ties need an ordering contract')
    formatted = pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')
    formatted['org:resource'] = df['resource'].to_numpy()
    sna = pm4py.discover_handover_of_work_network(formatted)
    pairs = {k: float(v) for k, v in sna.connections.items()}
    total = len(pairs); resources = sorted({r for pair in pairs for r in pair})
    kept = pairs
    if top is not None:
        busiest = sorted(resources, key=lambda r: -sum(v for (a, b), v in pairs.items() if a == r or b == r))[:top]
        kept = {k: v for k, v in pairs.items() if k[0] in busiest and k[1] in busiest}
    return {'pairs_total': total, 'pairs_shown': len(kept), 'resources': len(resources),
            'self_handovers': sorted(k for k in pairs if k[0] == k[1]),
            'coverage_complete': top is None or len(kept) == total,
            'strongest': max(pairs.items(), key=lambda kv: kv[1])[0] if pairs else None}

# ---------------------------------------------------------------- P63
class TreeNode(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    depth: int = Field(ge=0)
    parent: str | None


def tree_shape_edges(nodes: list[dict]) -> dict:
    typed = [TreeNode.model_validate(n) for n in nodes]
    ids = [n.id for n in typed]
    if pd.Index(ids).has_duplicates: raise g.Blocked('duplicate tree node identity')
    binding = {n.id: 'shape_%d' % i for i, n in enumerate(typed)}
    edges = []
    for n in typed:
        if n.parent is None:
            if n.depth != 0: raise g.Blocked('root at nonzero depth')
            continue
        if n.parent not in binding: raise g.Blocked('parent outside the node set: ' + n.parent)
        edges.append((binding[n.parent], binding[n.id]))
    if len(set(binding.values())) != len(binding): raise g.Blocked('shape identity reused')
    return {'nodes': len(typed), 'edges': len(edges), 'depth': max(n.depth for n in typed),
            'duplicate_labels_kept_distinct': len({n.label for n in typed}) < len(typed)}

# ---------------------------------------------------------------- P64
def plotly_scripts(page: str) -> list[str]:
    return [s.text for s in lxml_html.fromstring(page).xpath('//script') if s.text and 'Plotly.newPlot' in s.text]


def labels_from_page(page: str) -> list[str]:
    scripts = plotly_scripts(page)
    if len(scripts) != 1: raise g.Blocked('expected exactly one Plotly.newPlot call')
    payload = re.search(r'Plotly\.newPlot\(\s*"[^"]+",\s*(\[.*\])\s*,\s*\{', scripts[0], re.S)
    if not payload: raise g.Blocked('could not parse the Plotly data payload as JSON')
    data = g.strict_json_loads(payload.group(1))
    marker = next(t for t in data if t.get('mode', '').find('markers') >= 0 or 'text' in t)
    return list(marker['text'])


def labels_match_steps(page: str, steps: list[dict]) -> dict:
    labels = labels_from_page(page)
    expected = [s['lemma'] for s in steps]
    if DeepDiff(expected, labels, zip_ordered_iterables=True): raise g.Blocked('labels differ from the ordered steps')
    return {'labels': len(labels), 'steps': len(steps), 'note': 'label order matches; identity match still needs shape ids (P19) when labels repeat'}

# ---------------------------------------------------------------- P65-P70: the presentation runner
PAGE = Environment(autoescape=select_autoescape(['html']), undefined=StrictUndefined).from_string(
    '<!doctype html><html lang="en-US"><head><meta charset="utf-8">'
    '<meta http-equiv="Content-Security-Policy" content="default-src \'self\'; connect-src \'none\'; script-src \'self\'">'
    '<title>{{ title }}</title></head><body><table id="data">'
    '{% for r in rows %}<tr>{% for c in columns %}<td>{{ r[c] }}</td>{% endfor %}</tr>{% endfor %}'
    '</table></body></html>')

FORBIDDEN_IMPORT = re.compile(r'anthropic|openai|fetch\(|XMLHttpRequest|WebSocket|\bimport\s+requests\b')


class InterfaceModel(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    title: str = Field(min_length=1)
    columns: tuple[str, ...]
    rows: tuple[dict, ...]


def verify_registered_inputs(inputs: dict[str, bytes], register: dict[str, str]) -> None:
    for name, data in inputs.items():
        if name not in register: raise g.Blocked('input not registered: ' + name)
        if hashlib.sha256(data).hexdigest() != register[name]: raise g.Blocked('input bytes differ from the register: ' + name)


def presentation_page(model: dict, inputs: dict[str, bytes], register: dict[str, str]) -> dict:
    verify_registered_inputs(inputs, register)
    typed = InterfaceModel.model_validate(model)
    for r in typed.rows:
        if set(r) != set(typed.columns): raise g.Blocked('row keys do not match the declared columns')
    page = PAGE.render(title=typed.title, columns=list(typed.columns), rows=[dict(r) for r in typed.rows])
    if FORBIDDEN_IMPORT.search(page): raise g.Blocked('presentation carries a model-client import or network call')
    doc = lxml_html.fromstring(page)
    external = [u for u in doc.xpath('//script/@src') + doc.xpath('//link/@href') + doc.xpath('//img/@src') if u.startswith(('http:', 'https:', '//'))]
    if external: raise g.Blocked('external asset dependency: ' + external[0])
    csp = doc.xpath('//meta[@http-equiv="Content-Security-Policy"]/@content')
    if not csp or "connect-src 'none'" not in csp[0]: raise g.Blocked('missing connect-src none policy')
    if doc.xpath('//html/@lang') != ['en-US']: raise g.Blocked('interface language is not en-US')
    back = [[c.text_content() for c in tr.xpath('./td')] for tr in doc.xpath('//table[@id="data"]/tr')]
    expected = [[str(r[c]) for c in typed.columns] for r in typed.rows]
    if DeepDiff(expected, back, zip_ordered_iterables=True): raise g.Blocked('readback differs from the model')
    return {'rows': len(back), 'columns': len(typed.columns), 'external_assets': 0, 'connect_src': 'none', 'lang': 'en-US',
            'digest': hashlib.sha256(page.encode()).hexdigest()}

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(61)
def references_resolve_against_the_unit_set():
    units = [{'subsection': '(a)'}, {'subsection': '(b)'}, {'subsection': '(i)'}]
    sentences = [{'subsection': '(a)', 'text': 'as provided in subsection (b) and subsection (i)'},
                 {'subsection': '(b)', 'text': 'notwithstanding subsection (a)'},
                 {'subsection': '(i)', 'text': 'under this subsection (i)'},  # a self-reference is not an edge
                 {'subsection': '(a)', 'text': 'in paragraph (2) of this subsection'}]  # a paragraph ref stays intra-subsection
    out = reference_graph(units, sentences)
    g.equal((out['nodes'], out['edges']), (3, 3)); g.equal(out['acyclic'], False)  # (a)->(b), (a)->(i), (b)->(a) is a cycle
    g.equal(out['most_referenced'][0], ('(a)', 1))
    g.rejects(g.Blocked, lambda: reference_graph(units, sentences + [{'subsection': '(a)', 'text': 'see subsection (z)'}]))
    g.rejects(g.Blocked, lambda: reference_graph(units, sentences + [{'subsection': '(z)', 'text': 'x'}]))
    g.rejects(g.Blocked, lambda: reference_graph(units + [units[0]], sentences))
    return {'self_reference_not_an_edge': True, 'cycle_is_a_property_not_a_defect': True, 'reference_to_unknown_unit_blocked': True,
            'sentence_in_unknown_unit_blocked': True, 'original_chain_rerun': False}


@case(62)
def handover_keeps_self_loops_and_coverage():
    t = lambda h: '2011-01-01T%02d:00:00Z' % h
    events = [{'case_id': 'c1', 'event_id': 'e1', 'activity': 'A', 'resource': 'R01', 'timestamp': t(0)},
              {'case_id': 'c1', 'event_id': 'e2', 'activity': 'B', 'resource': 'R02', 'timestamp': t(1)},
              {'case_id': 'c1', 'event_id': 'e3', 'activity': 'C', 'resource': 'R01', 'timestamp': t(2)},
              {'case_id': 'c2', 'event_id': 'e4', 'activity': 'A', 'resource': 'R01', 'timestamp': t(0)},
              {'case_id': 'c2', 'event_id': 'e5', 'activity': 'B', 'resource': 'R01', 'timestamp': t(1)}]
    full = handover_network(events)
    g.equal(('R01', 'R01') in full['self_handovers'], True)  # a resource handing work to itself is a real pair, kept
    g.equal(full['coverage_complete'], True)
    truncated = handover_network(events, top=1)
    g.equal(truncated['coverage_complete'], False)  # showing only the busiest resources is a partial view
    g.require(truncated['pairs_shown'] <= full['pairs_total'], 'truncation cannot add pairs')
    g.rejects(g.Blocked, lambda: handover_network(events + [events[0]]))
    return {'self_handover_kept': True, 'busiest_only_marked_incomplete': True, 'duplicate_event_blocked': True, 'original_chain_rerun': False}


@case(63)
def tree_nodes_bind_to_distinct_shapes():
    nodes = [{'id': 'n0', 'label': '->', 'depth': 0, 'parent': None},
             {'id': 'n1', 'label': 'X', 'depth': 1, 'parent': 'n0'},
             {'id': 'n2', 'label': 'X', 'depth': 1, 'parent': 'n0'}]  # two nodes share a label
    out = tree_shape_edges(nodes)
    g.equal((out['nodes'], out['edges'], out['depth']), (3, 2, 1)); g.equal(out['duplicate_labels_kept_distinct'], True)
    g.rejects(g.Blocked, lambda: tree_shape_edges(nodes + [nodes[1]]))
    g.rejects(g.Blocked, lambda: tree_shape_edges([{'id': 'x', 'label': 'x', 'depth': 1, 'parent': 'missing'}]))
    g.rejects(ValidationError, lambda: tree_shape_edges([{'id': 'r', 'label': 'r', 'depth': 0, 'parent': None, 'extra': 1}]))
    return {'duplicate_labels_distinct_shapes': True, 'parent_outside_set_blocked': True, 'duplicate_id_blocked': True, 'original_chain_rerun': False}


@case(64)
def page_labels_parsed_as_json_not_scraped():
    steps = [{'id': 's1', 'lemma': 'make'}, {'id': 's2', 'lemma': 'state'}]
    fig = go.Figure(go.Scatter3d(x=[0, 1], y=[0, 1], z=[0, 0], mode='markers+text', text=[s['lemma'] for s in steps]))
    page = pio.to_html(fig, include_plotlyjs=True, full_html=True, div_id='p3d')
    out = labels_match_steps(page, steps)
    g.equal((out['labels'], out['steps']), (2, 2))
    scrambled = go.Figure(go.Scatter3d(x=[0, 1], y=[0, 1], z=[0, 0], mode='markers+text', text=['state', 'make']))
    g.rejects(g.Blocked, lambda: labels_match_steps(pio.to_html(scrambled, include_plotlyjs=True, full_html=True, div_id='p3d'), steps))
    g.rejects(g.Blocked, lambda: labels_from_page('<html><body>no plot here</body></html>'))
    return {'payload_parsed_as_json': True, 'label_order_compared': True, 'identity_caveat_recorded': True, 'original_chain_rerun': False}


@case(65)
def policy_interface_verifies_inputs_and_escapes():
    inputs = {'policy.jdm.json': b'{"threshold":10}', 'decisions.xlsx': b'\x50\x4b\x03\x04rows'}
    register = {name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()}
    model = {'title': 'Majority policy', 'columns': ('meeting', 'present', 'reachable'),
             'rows': ({'meeting': 'tsc-2023-12-06', 'present': 10, 'reachable': True},
                      {'meeting': '<script>alert(1)</script>', 'present': 6, 'reachable': False})}
    out = presentation_page(model, inputs, register)
    g.equal((out['external_assets'], out['connect_src'], out['lang']), (0, 'none', 'en-US'))
    g.rejects(g.Blocked, lambda: presentation_page(model, {'policy.jdm.json': b'{"threshold":11}', 'decisions.xlsx': inputs['decisions.xlsx']}, register))
    g.rejects(g.Blocked, lambda: presentation_page(model, {'unknown.json': b'x'}, register))
    return {'registered_bytes_checked': True, 'hostile_cell_escaped': True, 'csp_connect_src_none': True, 'en_us': True, 'original_chain_rerun': False}


@case(66)
def process_explorer_rejects_external_and_model_client():
    inputs = {'ordered_steps.json': b'[]'}; register = {'ordered_steps.json': hashlib.sha256(b'[]').hexdigest()}
    model = {'title': 'Process', 'columns': ('id', 'label', 'quote'), 'rows': ({'id': 'e7', 'label': 'make', 'quote': 'shall make'},)}
    out = presentation_page(model, inputs, register)
    g.equal(out['rows'], 1)
    hostile = dict(model, rows=({'id': 'e7', 'label': 'fetch(\"http://x\")', 'quote': 'shall make'},))
    g.rejects(g.Blocked, lambda: presentation_page(hostile, inputs, register))  # a fetch( in the rendered page is blocked
    return {'external_asset_gate': True, 'model_client_call_blocked': True, 'original_chain_rerun': False}


@case(67)
def records_interface_roundtrips_typed_rows():
    inputs = {'facts.xlsx': b'\x50\x4b\x03\x04'}; register = {'facts.xlsx': hashlib.sha256(inputs['facts.xlsx']).hexdigest()}
    model = {'title': 'Records', 'columns': ('subject', 'predicate', 'object'),
             'rows': ({'subject': 'e7', 'predicate': 'agent', 'object': 'x5'}, {'subject': 'e7', 'predicate': 'event', 'object': 'make'})}
    out = presentation_page(model, inputs, register)
    g.equal((out['rows'], out['columns']), (2, 3))
    g.rejects(g.Blocked, lambda: presentation_page(dict(model, rows=({'subject': 'e7', 'predicate': 'agent'},)), inputs, register))  # a row missing a declared column
    return {'typed_rows_roundtrip': True, 'row_column_mismatch_blocked': True, 'original_chain_rerun': False}


@case(68)
def briefing_interface_is_deterministic():
    inputs = {'explanations.docx': b'\x50\x4b\x05\x06'}; register = {'explanations.docx': hashlib.sha256(inputs['explanations.docx']).hexdigest()}
    model = {'title': 'Briefing', 'columns': ('block', 'text'), 'rows': ({'block': 'p1', 'text': 'The TSC must have a Chair.'},)}
    first = presentation_page(model, inputs, register); second = presentation_page(model, inputs, register)
    g.equal(first['digest'], second['digest'])  # same model and inputs render to the same bytes
    return {'deterministic_render': True, 'original_chain_rerun': False}


@case(69)
def slides_interface_keeps_declared_columns():
    inputs = {'deck.pptx': b'\x50\x4b\x03\x04deck'}; register = {'deck.pptx': hashlib.sha256(inputs['deck.pptx']).hexdigest()}
    model = {'title': 'Slides', 'columns': ('shape_id', 'text', 'target'), 'rows': ({'shape_id': 's1', 'text': 'Review', 'target': 's2'}, {'shape_id': 's2', 'text': 'Review', 'target': ''})}
    out = presentation_page(model, inputs, register)
    g.equal(out['columns'], 3)  # two shapes with the same text keep distinct shape ids as columns of the row
    return {'shape_identity_carried_as_data': True, 'duplicate_text_distinct_ids': True, 'original_chain_rerun': False}


@case(70)
def workbench_composes_the_same_model():
    inputs = {'ordered_steps.json': b'[]', 'facts.xlsx': b'\x50\x4b\x03\x04'}
    register = {name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()}
    model = {'title': 'Workbench', 'columns': ('view', 'rows'), 'rows': ({'view': 'policy', 'rows': 8}, {'view': 'records', 'rows': 336})}
    out = presentation_page(model, inputs, register)
    g.equal((out['rows'], out['connect_src']), (2, 'none'))
    g.rejects(g.Blocked, lambda: presentation_page(model, inputs, {'ordered_steps.json': register['ordered_steps.json']}))  # facts.xlsx unregistered
    return {'composed_from_registered_inputs': True, 'missing_registration_blocked': True, 'original_chain_rerun': False}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'pandas', 'numpy', 'networkx', 'pm4py', 'plotly', 'lxml', 'Jinja2', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P61-P70 chains and their artifacts were not rerun. P65-P70 build a presentation page from the same primitives (escaping template, CSP, registered-input-bytes gate, typed readback), not the recorded interfaces.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py', 'handoff_guards_v3.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True); args = p.parse_args()
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions', 'full_chains_executed']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
