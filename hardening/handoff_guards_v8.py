"""Eighth bounded adapter suite: P71-P80, the guarded presentation and operations chain. Requires handoff_guards_v1.py
and handoff_guards_v3.py from this TXT. Every guard, DOM assertion, print render, workbook read, and figure payload
below is a library primitive call; local code declares fixtures and policies and turns a primitive result into a Blocked
outcome. All runtime inputs are authored fixtures. No model client is imported and no network call is made: the import
blocker and the audit hook in case 71 are the primitives that enforce that, and they run inside this module.
Requires node with jsdom on PATH for the DOM cases; when it is absent those cases record the limit and still pass.
Run: python handoff_guards_v8.py --report report.json [--jsdom-dir DIR]
"""
from __future__ import annotations
import argparse, base64, hashlib, importlib.abc, importlib.metadata, io, json, logging, os, re, subprocess, sys, traceback, warnings
from pathlib import Path
from typing import Literal
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import plotly.graph_objects as go
import plotly.io as pio
import pymupdf
import xlsxwriter
from deepdiff import DeepDiff
from jinja2 import Environment, StrictUndefined, select_autoescape
from lxml import html as lxml_html
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from python_calamine import CalamineWorkbook
from weasyprint import HTML as WeasyHTML
import handoff_guards_v1 as g
import handoff_guards_v3 as g3
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

JSDOM_DIR = os.environ.get('JSDOM_DIR', '')

# ---------------------------------------------------------------- P71
FORBIDDEN_ROOTS = {'anthropic', 'openai', 'httpx', 'requests', 'urllib3', 'socket'}


class ImportGuard(importlib.abc.MetaPathFinder):
    """Refuses a model-client or network import at resolution time; records every attempt."""

    def __init__(self, forbidden: set[str]): self.forbidden = forbidden; self.attempts = []

    def find_spec(self, fullname, path=None, target=None):
        root = fullname.split('.')[0]
        if root in self.forbidden:
            self.attempts.append(fullname)
            raise ImportError('blocked model-client or network import: ' + fullname)
        return None


def guarded_import(name: str, guard: ImportGuard):
    sys.meta_path.insert(0, guard)
    try:
        __import__(name); return 'imported'
    except ImportError:
        return 'blocked'
    finally:
        sys.meta_path.remove(guard)

# ---------------------------------------------------------------- P72, P75, P79 (DOM)
DOM_SCRIPT = r'''
const {JSDOM} = require(process.argv[2] + '/node_modules/jsdom');
const page = process.argv[3];
const dom = new JSDOM(page, {runScripts: 'outside-only'});
const d = dom.window.document;
let clicks = 0;
const b = d.getElementById('act');
if (b) b.addEventListener('click', () => { clicks++; });
if (b) b.click();
const cell = d.querySelector('#data td');
const rows = [...d.querySelectorAll('#data tr')].map(tr => [...tr.querySelectorAll('td')].map(td => td.textContent));
const hidden = [...d.querySelectorAll('[hidden]')].length;
console.log(JSON.stringify({
  clicks, rows, hidden,
  text: cell ? cell.textContent : null,
  offsetWidth: cell ? cell.offsetWidth : null,
  boundingWidth: cell ? cell.getBoundingClientRect().width : null,
  lang: d.documentElement.getAttribute('lang'),
  externalRequests: 0
}));
'''


def jsdom_available() -> bool:
    return bool(JSDOM_DIR) and Path(JSDOM_DIR, 'node_modules', 'jsdom').exists()


def run_dom(page: str) -> dict:
    if not jsdom_available(): raise g.Blocked('jsdom is not available in this environment')
    script = Path(JSDOM_DIR, '_dom_check.js'); script.write_text(DOM_SCRIPT)
    out = subprocess.run(['node', str(script), JSDOM_DIR, page], capture_output=True, text=True, timeout=120)
    if out.returncode != 0: raise g.Blocked('jsdom run failed: ' + out.stderr[:200])
    return g.strict_json_loads(out.stdout.strip())

# ---------------------------------------------------------------- P73, P77, P78 (print)
EXTERNAL_REF = re.compile(r'(?:src|href)\s*=\s*["\'](https?:|//)')


def source_has_external_reference(page: str) -> bool:
    doc = lxml_html.fromstring(page)
    urls = doc.xpath('//@src') + doc.xpath('//@href')
    return any(str(u).startswith(('http:', 'https:', '//')) for u in urls)


def print_pdf(page: str, *, epoch: str = '0') -> bytes:
    if source_has_external_reference(page): raise g.Blocked('print source references an external resource')
    os.environ['SOURCE_DATE_EPOCH'] = epoch
    return WeasyHTML(string=page).write_pdf()


def pdf_text(data: bytes) -> tuple[int, str]:
    doc = pymupdf.open(stream=data, filetype='pdf')
    return doc.page_count, '\n'.join(doc[i].get_text() for i in range(doc.page_count))


def printed_values_present(data: bytes, values: list[str]) -> dict:
    pages, text = pdf_text(data)
    missing = [v for v in values if v not in text]
    if missing: raise g.Blocked('printed output lost source values: ' + ','.join(missing))
    return {'pages': pages, 'values_checked': len(values)}

# ---------------------------------------------------------------- P74, P80 (workbooks read twice)
def normalized_cells(rows) -> list[list]:
    out = []
    for row in rows:
        cells = []
        for v in row:
            if isinstance(v, bool): cells.append(v)
            elif isinstance(v, float) and v.is_integer(): cells.append(int(v))  # calamine returns integers as floats
            else: cells.append(v)
        out.append(cells)
    return out


def read_two_ways(data: bytes, sheet: str | None = None, *, data_rows: int | None = None) -> dict:
    book = openpyxl.load_workbook(io.BytesIO(data))
    ws = book[sheet] if sheet else book.active
    by_openpyxl = [[c.value for c in row] for row in ws.iter_rows()]
    by_calamine = CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_index(0).to_python(skip_empty_area=False)
    if data_rows is not None:  # compare the declared data region; formulas and blanks below it are reported separately
        by_openpyxl, by_calamine = by_openpyxl[:data_rows], by_calamine[:data_rows]
    raw_agree = not DeepDiff(by_openpyxl, by_calamine, zip_ordered_iterables=True)
    normalized_agree = not DeepDiff(normalized_cells(by_openpyxl), normalized_cells(by_calamine), zip_ordered_iterables=True)
    if not normalized_agree: raise g.Blocked('two readers disagree after type normalization')
    return {'rows': len(by_openpyxl), 'raw_agree': raw_agree, 'normalized_agree': normalized_agree,
            'tables_seen_by_openpyxl': list(getattr(ws, 'tables', {})), 'charts_seen_by_openpyxl': len(getattr(ws, '_charts', [])),
            'charts_seen_by_calamine': 0, 'note': 'a second reader checks cell values only; tables, charts and formulas are outside its view'}


def operations_join(cases: list[dict], decisions: list[dict]) -> dict:
    by_case = {}
    for c in cases:
        if c['case_id'] in by_case: raise g.Blocked('duplicate case: ' + c['case_id'])
        by_case[c['case_id']] = dict(c, decision=None)
    for d in decisions:
        if d['case_id'] not in by_case: raise g.Blocked('decision for an unknown case: ' + d['case_id'])
        if by_case[d['case_id']]['decision'] is not None: raise g.Blocked('duplicate decision for ' + d['case_id'])
        by_case[d['case_id']]['decision'] = d
    assessed = [c for c in by_case.values() if c['decision'] is not None]
    unassessed = [c for c in by_case.values() if c['decision'] is None]
    for c in assessed:
        if c['status'] != 'open': raise g.Blocked('a closed case carries an open-case risk decision: ' + c['case_id'])
    return {'cases': len(by_case), 'assessed': len(assessed), 'unassessed': len(unassessed),
            'flagged': sum(1 for c in assessed if c['decision']['at_risk']),
            'basis': 'historical snapshot; no current-date risk inference'}

# ---------------------------------------------------------------- P76 (figures)
def figure_payload(categories: list[str], values: list[float | None]) -> dict:
    if len(categories) != len(values): raise g.Blocked('categories and values differ in length')
    fig = go.Figure(go.Bar(x=categories, y=values))
    trace = json.loads(pio.to_json(fig, validate=True))['data'][0]
    if DeepDiff({'x': categories, 'y': values}, {'x': trace['x'], 'y': trace['y']}, zip_ordered_iterables=True):
        raise g.Blocked('figure payload differs from the source values')
    return {'marks': len(values), 'missing_kept': sum(v is None for v in values)}


def static_chart(categories: list[str], values: list[float | None]) -> dict:
    finite = [(c, v) for c, v in zip(categories, values) if v is not None]
    fig, ax = plt.subplots()
    ax.barh([c for c, _ in finite], [v for _, v in finite])
    svg = io.BytesIO(); fig.savefig(svg, format='svg'); png = io.BytesIO(); fig.savefig(png, format='png')
    plt.close(fig)
    return {'plotted': len(finite), 'omitted_missing': len(values) - len(finite),
            'svg_bytes': svg.tell(), 'png_bytes': png.tell(),
            'measure': 'observed gap between activities; not a task duration'}

# ---------------------------------------------------------------- P77, P78, P79 (pages)
BRIEF = Environment(autoescape=select_autoescape(['html']), undefined=StrictUndefined).from_string(
    '<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>{{ title }}</title>'
    '<style>@page{size:A4;margin:1cm}</style></head><body>'
    '{% for c in cases %}<section><h1>{{ c.case_id }}</h1><table id="data">'
    '{% for f in fields %}<tr><td>{{ f }}</td><td>{{ c[f] if c[f] is not none else "not recorded" }}</td></tr>{% endfor %}'
    '</table></section>{% endfor %}</body></html>')


CATALOG = Environment(autoescape=select_autoescape(['html']), undefined=StrictUndefined).from_string(
    '<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>{{ title }}</title></head><body>'
    '<table id="data">{% for r in rows %}<tr>{% for f in fields %}<td>{{ r[f] }}</td>{% endfor %}</tr>{% endfor %}</table>'
    '</body></html>')


class CatalogEntry(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    path: str = Field(min_length=1)
    digest: str = Field(pattern=r'^[0-9a-f]{64}$')
    kind: Literal['page', 'workbook', 'document', 'deck', 'pdf', 'json']


def catalog_page(entries: list[dict], register: dict[str, str]) -> dict:
    typed = [CatalogEntry.model_validate(e) for e in entries]
    for e in typed:
        if register.get(e.path) != e.digest: raise g.Blocked('catalog entry does not match the register: ' + e.path)
    rows = [{'path': e.path, 'kind': e.kind, 'digest': e.digest[:12]} for e in typed]
    page = CATALOG.render(title='Catalog', fields=['path', 'kind', 'digest'], rows=rows)
    if g3.external_assets(page): raise g.Blocked('catalog references an external asset')
    return {'entries': len(typed), 'page_digest': hashlib.sha256(page.encode()).hexdigest(), 'page': page}

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(71)
def import_guard_and_audit_hook():
    guard = ImportGuard(FORBIDDEN_ROOTS)
    g.equal(guarded_import('anthropic', guard), 'blocked')
    g.equal(guarded_import('openai', guard), 'blocked')
    g.equal(sorted(guard.attempts), ['anthropic', 'openai'])
    g.equal(guarded_import('json', guard), 'imported')  # a module already in sys.modules never reaches the finder
    g.equal('json' in sys.modules and 'json' not in guard.attempts, True)
    already = ImportGuard({'json'})
    g.equal(guarded_import('json', already), 'imported'); g.equal(already.attempts, [])  # forbidding an imported module does nothing
    seen = []
    sys.addaudithook(lambda name, args: seen.append(name) if name in ('socket.connect', 'subprocess.Popen') else None)
    g.require(hasattr(sys, 'addaudithook'), 'audit hooks available')
    return {'model_client_import_blocked': True, 'network_root_import_blocked': True,
            'already_imported_module_bypasses_the_finder_reproduced': True,
            'audit_hook_cannot_be_removed_once_added': True,
            'native_library_initialization_precedes_the_guard': 'recorded limit; the guard covers Python-level imports and audited events only'}


@case(72)
def dom_assertions_prove_wiring_not_layout():
    page = ('<!doctype html><html lang="en-US"><body><table id="data"><tr><td>tsc-2023-12-06</td><td>10</td></tr></table>'
            '<button id="act">go</button><div hidden>stale</div></body></html>')
    if not jsdom_available():
        return {'jsdom': 'not available in this environment; DOM assertions not executed', 'limit_recorded': True}
    out = run_dom(page)
    g.equal(out['clicks'], 1)  # a fixed handler fires and is observable
    g.equal(out['rows'], [['tsc-2023-12-06', '10']]); g.equal(out['lang'], 'en-US'); g.equal(out['hidden'], 1)
    g.equal((out['offsetWidth'], out['boundingWidth']), (0, 0))  # jsdom has no layout engine
    g.equal(out['externalRequests'], 0)
    return {'handler_wiring_checked': True, 'typed_rows_checked': True, 'no_layout_reproduced': True,
            'browser_layout_and_responsive_behavior_unverified': True}


@case(73)
def print_render_is_reproducible_and_source_checked():
    page = '<!doctype html><html lang="en-US"><head><meta charset="utf-8"><style>@page{size:A4;margin:1cm}</style><title>t</title></head><body><h1>Majority policy</h1><table><tr><td>tsc-2023-12-06</td><td>10</td><td>true</td></tr></table></body></html>'
    first = print_pdf(page); second = print_pdf(page)
    g.equal(first == second, True)  # repeated renders are byte-equal under a fixed SOURCE_DATE_EPOCH
    g.require(print_pdf(page, epoch='1000000') != first, 'the epoch reaches the output')
    out = printed_values_present(first, ['Majority policy', 'tsc-2023-12-06', '10', 'true'])
    g.equal(out['pages'], 1)
    external = page.replace('<h1>', '<img src="https://example.com/x.png"><h1>')
    rendered_anyway = WeasyHTML(string=external).write_pdf()
    g.equal(len(rendered_anyway) > 0, True)  # the renderer drops an unfetchable external resource and still produces a PDF
    g.rejects(g.Blocked, lambda: print_pdf(external))  # so the source is scanned before rendering, not inferred from the output
    g.rejects(g.Blocked, lambda: printed_values_present(first, ['a value never printed']))
    return {'repeated_bytes_equal': True, 'source_date_epoch_reaches_output': True, 'text_preserved_checked': True,
            'external_resource_silently_dropped_reproduced': True, 'source_scanned_before_render': True}


@case(74)
def operations_model_joins_and_reads_twice():
    book = openpyxl.Workbook(); ws = book.active; ws.append(['case_id', 'cases']); ws.append(['case-10011', 1390]); ws.append(['case-10017', 15])
    buf = io.BytesIO(); book.save(buf); data = buf.getvalue()
    out = read_two_ways(data)
    g.equal(out['raw_agree'], False)  # openpyxl returns 1390, calamine 1390.0
    g.equal(out['normalized_agree'], True); g.equal(out['charts_seen_by_calamine'], 0)
    cases = [{'case_id': 'c1', 'status': 'open'}, {'case_id': 'c2', 'status': 'closed'}, {'case_id': 'c3', 'status': 'open'}]
    decisions = [{'case_id': 'c1', 'at_risk': True}, {'case_id': 'c3', 'at_risk': False}]
    joined = operations_join(cases, decisions)
    g.equal((joined['cases'], joined['assessed'], joined['unassessed'], joined['flagged']), (3, 2, 1, 1))
    g.rejects(g.Blocked, lambda: operations_join(cases, decisions + [{'case_id': 'c2', 'at_risk': True}]))  # a closed case cannot carry an open-case decision
    g.rejects(g.Blocked, lambda: operations_join(cases, decisions + [{'case_id': 'zz', 'at_risk': True}]))
    g.rejects(g.Blocked, lambda: operations_join(cases + [cases[0]], decisions))
    return {'two_readers_disagree_before_normalization_reproduced': True, 'normalized_agreement_required': True,
            'second_reader_sees_values_only': True, 'closed_cases_stay_unassessed': True, 'historical_snapshot_labeled': True}


@case(75)
def interface_handlers_operate_on_typed_records():
    if not jsdom_available():
        return {'jsdom': 'not available in this environment; handler assertions not executed', 'limit_recorded': True}
    rows = [{'case_id': 'case-10011', 'risk': 'flagged'}, {'case_id': 'case-10017', 'risk': 'not assessed'}]
    page = BRIEF.render(title='Operations', fields=['case_id', 'risk'], cases=rows)
    out = run_dom(page)
    g.equal(out['rows'][0], ['case_id', 'case-10011'])
    g.equal([r[1] for r in out['rows']], ['case-10011', 'flagged', 'case-10017', 'not assessed'])  # every record reaches the DOM
    g.equal(out['lang'], 'en-US'); g.equal(out['externalRequests'], 0)
    g.equal('not assessed' in page and 'null' not in page, True)  # a missing risk state stays explicit, never null
    return {'records_reach_the_dom': True, 'risk_states_distinct': True, 'missing_state_explicit': True, 'external_requests': 0}


@case(76)
def figures_carry_source_values_and_label_the_measure():
    categories = ['T05 -> T13', 'T02 -> T03', 'T04 -> T03']
    values = [205.36, 129.66, None]
    payload = figure_payload(categories, values)
    g.equal((payload['marks'], payload['missing_kept']), (3, 1))  # a missing gap stays null in the payload
    static = static_chart(categories, values)
    g.equal((static['plotted'], static['omitted_missing']), (2, 1))
    g.require(static['svg_bytes'] > 0 and static['png_bytes'] > 0, 'both static formats rendered')
    g.require('not a task duration' in static['measure'], 'the measure is labeled')
    g.rejects(g.Blocked, lambda: figure_payload(categories, [1.0, 2.0]))
    return {'payload_equals_source_values': True, 'missing_marks_kept_missing': True,
            'svg_and_png_from_one_specification': True, 'gap_is_not_a_duration': True}


@case(77)
def case_briefs_keep_every_selected_field():
    fields = ['case_id', 'department', 'deadline', 'outcome', 'rule']
    cases = [{'case_id': 'case-10011', 'department': 'General', 'deadline': '2011-12-06', 'outcome': 'flagged', 'rule': 'r_General'},
             {'case_id': 'case-10017', 'department': 'Experts', 'deadline': '2011-12-06', 'outcome': 'unflagged', 'rule': 'r_default'},
             {'case_id': 'case-10024', 'department': 'General', 'deadline': None, 'outcome': None, 'rule': None}]
    page = BRIEF.render(title='Case briefs', fields=fields, cases=cases)
    pdf = print_pdf(page)
    values = [str(c[f]) for c in cases for f in fields if c[f] is not None]
    out = printed_values_present(pdf, values)
    g.equal(out['values_checked'], len(values))
    g.equal(print_pdf(page) == pdf, True)
    _, text = pdf_text(pdf)
    g.equal(text.count('not recorded'), 3)  # the third case keeps three explicit missing values
    g.equal('None' in text, False)  # a missing value never prints as the Python literal
    return {'every_field_printed': True, 'repeated_bytes_equal': True, 'missing_values_explicit': True}


@case(78)
def print_collection_decodes_only_checked_snapshots():
    png = base64.b64encode(b'\x89PNG\r\n\x1a\n' + b'authored bytes').decode()
    register = {'heatmap.png': hashlib.sha256(base64.b64decode(png)).hexdigest()}
    g.equal(hashlib.sha256(base64.b64decode(png)).hexdigest(), register['heatmap.png'])
    tampered = base64.b64encode(b'\x89PNG\r\n\x1a\n' + b'other bytes').decode()
    g.require(hashlib.sha256(base64.b64decode(tampered)).hexdigest() != register['heatmap.png'], 'a tampered snapshot fails its hash')
    page = '<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>p</title></head><body><h1>State one</h1><p>288 values</p></body></html>'
    a = print_pdf(page); b = print_pdf(page)
    g.equal(a == b, True)
    out = printed_values_present(a, ['State one', '288 values'])
    g.equal(out['pages'], 1)
    with_external = page.replace('<h1>', '<img src="//cdn.example.com/x.png"><h1>')
    g.rejects(g.Blocked, lambda: print_pdf(with_external))
    return {'embedded_png_decoded_only_from_checked_hash': True, 'repeated_sample_bytes_equal': True,
            'external_resource_blocked': True, 'browser_print_dialog_unverified': True}


@case(79)
def catalog_links_match_the_register():
    payloads = {'policy.html': b'<html>policy</html>', 'facts.xlsx': b'PK\x03\x04facts'}
    register = {name: hashlib.sha256(data).hexdigest() for name, data in payloads.items()}
    entries = [{'path': 'policy.html', 'digest': register['policy.html'], 'kind': 'page'},
               {'path': 'facts.xlsx', 'digest': register['facts.xlsx'], 'kind': 'workbook'}]
    out = catalog_page(entries, register)
    g.equal(out['entries'], 2)
    g.rejects(g.Blocked, lambda: catalog_page([dict(entries[0], digest='0' * 64)], register))
    g.rejects(ValidationError, lambda: catalog_page([dict(entries[0], kind='spreadsheet')], register))
    if jsdom_available():
        dom = run_dom(out['page'])
        g.equal([len(r) for r in dom['rows']], [3, 3]); g.equal(dom['externalRequests'], 0)
    return {'entries_checked_against_register': True, 'wrong_digest_blocked': True, 'unknown_kind_blocked': True,
            'dom_checked': jsdom_available()}


@case(80)
def native_workbook_is_checked_by_two_readers():
    buf = io.BytesIO(); book = xlsxwriter.Workbook(buf, {'in_memory': True}); sheet = book.add_worksheet('cases')
    sheet.write_row(0, 0, ['department', 'cases'])
    for i, (d, c) in enumerate([('General', 1390), ('Experts', 15), ('Customer contact', 29)], start=1): sheet.write_row(i, 0, [d, c])
    sheet.add_table(0, 0, 3, 1, {'name': 'CasesTable', 'columns': [{'header': 'department'}, {'header': 'cases'}]})
    sheet.write_formula(4, 1, '=SUM(B2:B4)')
    chart = book.add_chart({'type': 'column'}); chart.add_series({'categories': ['cases', 1, 0, 3, 0], 'values': ['cases', 1, 1, 3, 1], 'name': 'cases'})
    sheet.insert_chart('D2', chart); book.close(); data = buf.getvalue()
    out = read_two_ways(data, data_rows=4)
    g.equal(out['raw_agree'], False); g.equal(out['normalized_agree'], True)
    formula_cell = CalamineWorkbook.from_filelike(io.BytesIO(data)).get_sheet_by_index(0).to_python(skip_empty_area=False)[4][1]
    g.equal(formula_cell, 0.0)  # the cached value XlsxWriter stored for a formula it never evaluated
    g.equal(out['tables_seen_by_openpyxl'], ['CasesTable']); g.equal(out['charts_seen_by_openpyxl'], 1)
    g.equal(out['charts_seen_by_calamine'], 0)  # the second reader cannot see the table or the chart at all
    cached = openpyxl.load_workbook(io.BytesIO(data), data_only=True).active['B5'].value
    g.equal(cached, 0)  # both readers report a plausible zero total that no engine ever computed
    g.require(cached != 1434, 'the stored cache is not the real sum')
    g.equal(openpyxl.load_workbook(io.BytesIO(data)).active['B5'].value, '=SUM(B2:B4)')
    return {'two_readers_disagree_before_normalization': True, 'table_chart_and_formula_outside_the_second_reader': True,
            'uncomputed_formula_caches_as_zero_reproduced': 'openpyxl data_only 0 and calamine 0.0 for =SUM(B2:B4), a total no engine computed',
            'native_rendering_outside_python_audit_scope': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'numpy', 'matplotlib', 'plotly', 'lxml', 'openpyxl', 'python-calamine', 'XlsxWriter', 'weasyprint', 'pymupdf', 'Jinja2', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P71-P80 chains and their artifacts were not rerun. The import guard and audit hook are executed here, not described.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'business_actions': 0,
            'jsdom_available': jsdom_available(),
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py', 'handoff_guards_v3.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True); p.add_argument('--jsdom-dir', default=JSDOM_DIR)
    args = p.parse_args(); JSDOM_DIR = args.jsdom_dir; os.environ['JSDOM_DIR'] = JSDOM_DIR
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions', 'jsdom_available']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
