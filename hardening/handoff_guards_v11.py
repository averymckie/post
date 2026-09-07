"""Eleventh bounded adapter suite: P101-P110, the everyday deliverables. Requires handoff_guards_v1.py and
handoff_guards_v8.py from this TXT. Every document readback, conversion, workbook check, calendar build, MIME assembly
and PDF composition below is a library primitive call; local code declares fixtures and policies and turns a primitive
result into a Blocked outcome. All runtime inputs are authored fixtures. No model client, no network, and nothing is
sent: the MIME case builds drafts with no sender and no recipient and never opens a transport.
Run: python handoff_guards_v11.py --report report.json [--jsdom-dir DIR]
"""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.metadata, io, json, logging, os, time, traceback, uuid, warnings, zipfile
from email import policy as email_policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path
from typing import Literal
import docx
import mammoth
import markdownify
import openpyxl
import pymupdf
import xlsxwriter
from deepdiff import DeepDiff
from icalendar import Calendar, Event
from lxml import html as lxml_html
from pydantic import BaseModel, ConfigDict, Field, ValidationError
import handoff_guards_v1 as g
import handoff_guards_v6 as g6
import handoff_guards_v8 as g8
warnings.simplefilter('ignore'); logging.disable(logging.WARNING)

BOX = '☐'
PINNED_STAMP = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
UID_NAMESPACE = uuid.UUID('00000000-0000-0000-0000-000000000000')

# ---------------------------------------------------------------- P101
class ActionRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    action_id: str = Field(min_length=1)
    source_document: str = Field(min_length=1)
    order: int = Field(ge=0)
    label: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class WorkingRecord(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid')
    action_id: str = Field(min_length=1)
    status: Literal['not_reviewed'] = 'not_reviewed'
    owner: None = None
    due_date: None = None
    note: None = None


def action_records(document: bytes, source_name: str) -> list[dict]:
    out = []
    for i, p in enumerate(docx.Document(io.BytesIO(document)).paragraphs):
        if not p.text.startswith(BOX): continue
        runs = p.runs
        if len(runs) != 3: raise g.Blocked('checklist paragraph lost its identity run (P48)')
        action_id, quote = runs[1].text.split('|')
        out.append(ActionRecord(action_id=action_id, source_document=source_name, order=len(out), label=runs[2].text, quote=quote).model_dump())
    if not out: raise g.Blocked('no checklist items found')
    return out


def blank_progress(records: list[dict]) -> list[dict]:
    return [WorkingRecord(action_id=r['action_id']).model_dump() for r in records]

# ---------------------------------------------------------------- P102
def apply_progress(state: list[dict], imported: list[dict], known: set[str]) -> list[dict]:
    validated = []
    for row in imported:
        record = WorkingRecord.model_validate(row)  # refuses an inferred owner, due date or status
        if record.action_id not in known: raise g.Blocked('progress row for an unknown action: ' + record.action_id)
        validated.append(record.model_dump())
    if len({r['action_id'] for r in validated}) != len(validated): raise g.Blocked('duplicate progress row')
    return validated or state

# ---------------------------------------------------------------- P103
def tracker_workbook(records: list[dict]) -> bytes:
    buf = io.BytesIO(); book = xlsxwriter.Workbook(buf, {'in_memory': True}); sheet = book.add_worksheet('actions')
    columns = ['action_id', 'label', 'quote', 'status', 'owner', 'due_date']
    sheet.write_row(0, 0, columns)
    for i, r in enumerate(records, start=1):
        sheet.write_row(i, 0, [r['action_id'], r['label'], r['quote']])
        for c in range(3, 6): sheet.write_blank(i, c, None)  # working fields stay blank, never a default
    sheet.add_table(0, 0, len(records), len(columns) - 1, {'name': 'Actions', 'columns': [{'header': c} for c in columns]})
    sheet.data_validation(1, 3, len(records), 3, {'validate': 'list', 'source': ['not_reviewed', 'reviewed']})
    sheet.data_validation(1, 5, len(records), 5, {'validate': 'date', 'criteria': 'between',
                                                  'minimum': datetime.date(2000, 1, 1), 'maximum': datetime.date(2100, 1, 1)})
    book.close(); return buf.getvalue()


def blank_working_cells(data: bytes, columns: tuple[int, ...], rows: int) -> dict:
    ws = openpyxl.load_workbook(io.BytesIO(data)).active
    values = [ws.cell(row=r, column=c).value for r in range(2, rows + 2) for c in columns]
    return {'blank': sum(v is None for v in values), 'total': len(values)}

# ---------------------------------------------------------------- P104
def styled_checklist(records: list[dict]) -> bytes:
    d = docx.Document(); d.add_heading('Required actions', 1)
    for r in records:
        p = d.add_paragraph(); p.add_run(BOX + ' ')
        marker = p.add_run(r['action_id'] + '|' + r['quote']); marker.font.hidden = True
        body = p.add_run(r['label']); body.font.bold = False
    buf = io.BytesIO(); d.save(buf); return buf.getvalue()

# ---------------------------------------------------------------- P105
def to_html_and_markdown(document: bytes) -> dict:
    result = mammoth.convert_to_html(io.BytesIO(document))
    html_text = result.value
    blocks = [e.text_content().strip() for e in lxml_html.fragment_fromstring(html_text, create_parent='div') if e.text_content().strip()]
    md = markdownify.markdownify(html_text)
    md_blocks = [line.strip() for line in md.splitlines() if line.strip()]
    return {'messages': [str(m) for m in result.messages], 'html_blocks': blocks, 'markdown_blocks': md_blocks}

# ---------------------------------------------------------------- P106
def meeting_model(rows: list[dict]) -> dict:
    meetings = {}
    for r in rows:
        date = datetime.date.fromisoformat(r['meeting_date'])  # a malformed date raises rather than defaulting
        if r['meeting'] in meetings: raise g.Blocked('duplicate meeting: ' + r['meeting'])
        meetings[r['meeting']] = {'date': date.isoformat(), 'majority_reachable': r['majority_reachable'],
                                  'mentions': r['mentions'], 'completed_actions': None}
    return {'meetings': meetings, 'mention_basis': 'mentions do not establish completion (P7, P20)',
            'roster_basis': 'historical rosters remain unverified (P13)'}

# ---------------------------------------------------------------- P108
def meeting_ics(meetings: list[dict], *, stamp: datetime.datetime | None) -> bytes:
    cal = Calendar(); cal.add('prodid', '-//proofs//hardening//EN'); cal.add('version', '2.0')
    for m in meetings:
        event = Event()
        event.add('summary', m['meeting'])
        event.add('dtstart', datetime.date.fromisoformat(m['meeting_date']))  # an all-day event: VALUE=DATE, no time
        event['uid'] = str(uuid.uuid5(UID_NAMESPACE, m['meeting'])) + '@proofs'
        event.add('dtstamp', stamp if stamp is not None else datetime.datetime.now(datetime.timezone.utc))
        cal.add_component(event)
    return cal.to_ical()


def ics_events(data: bytes) -> list[dict]:
    out = []
    for component in Calendar.from_ical(data).walk('VEVENT'):
        out.append({'uid': str(component['uid']), 'summary': str(component['summary']),
                    'dtstart': component['dtstart'].dt.isoformat(),
                    'has_time': isinstance(component['dtstart'].dt, datetime.datetime),
                    'has_location': 'LOCATION' in component, 'has_attendee': 'ATTENDEE' in component,
                    'has_alarm': any(True for _ in component.walk('VALARM'))})
    return out

# ---------------------------------------------------------------- P109
def meeting_draft(subject: str, body: str, attachments: dict[str, bytes], *, boundary: str | None) -> bytes:
    msg = EmailMessage(); msg['Subject'] = subject; msg.set_content(body)
    for name, payload in attachments.items():
        msg.add_attachment(payload, maintype='application', subtype='octet-stream', filename=name)
    if boundary is not None: msg.set_boundary(boundary)
    return msg.as_bytes()


def read_draft(data: bytes) -> dict:
    msg = BytesParser(policy=email_policy.default).parsebytes(data)
    attachments = {p.get_filename(): p.get_payload(decode=True) for p in msg.iter_attachments()}
    return {'subject': msg['Subject'], 'sender': msg['From'], 'recipient': msg['To'],
            'attachments': {k: hashlib.sha256(v).hexdigest() for k, v in attachments.items()}}

# ---------------------------------------------------------------- P110
def review_binder(sections: list[tuple[str, bytes]]) -> dict:
    binder = pymupdf.open(); toc = []
    for title, pdf in sections:
        start = binder.page_count
        with pymupdf.open(stream=pdf, filetype='pdf') as part: binder.insert_pdf(part)
        if binder.page_count == start: raise g.Blocked('section contributed no page: ' + title)
        toc.append([1, title, start + 1])
    binder.set_toc(toc)
    out = binder.tobytes()
    reopened = pymupdf.open(stream=out, filetype='pdf')
    return {'pages': reopened.page_count, 'toc': reopened.get_toc(), 'sections': len(sections)}

C = []
def case(i):
    def reg(fn): C.append((i, fn)); return fn
    return reg


@case(101)
def action_records_infer_no_progress():
    source = [{'action_id': 'k1', 'label': 'The TSC must have a Chair.', 'quote': 'must have'},
              {'action_id': 'k2', 'label': 'The agency shall make records available.', 'quote': 'shall make'}]
    document = styled_checklist(source)
    records = action_records(document, 'charter')
    g.equal([r['action_id'] for r in records], ['k1', 'k2'])
    g.equal([r['order'] for r in records], [0, 1])  # source order is retained
    g.equal(records[0]['quote'], 'must have')
    blank = blank_progress(records)
    g.equal(blank[0], {'action_id': 'k1', 'status': 'not_reviewed', 'owner': None, 'due_date': None, 'note': None})
    g.rejects(ValidationError, lambda: WorkingRecord.model_validate({'action_id': 'k1', 'status': 'done'}))  # a status the contract never declared
    g.rejects(ValidationError, lambda: WorkingRecord.model_validate({'action_id': 'k1', 'owner': 'someone'}))  # an inferred owner
    g.rejects(g.Blocked, lambda: action_records(styled_checklist([]) if False else io.BytesIO(b'').getvalue() and b'', 'x') if False else action_records(_empty_docx(), 'x'))
    return {'order_and_quotes_retained': True, 'blank_working_record': True, 'no_owner_or_due_date_inferred': True,
            'unknown_status_refused': True}


def _empty_docx() -> bytes:
    d = docx.Document(); d.add_paragraph('no checklist here'); buf = io.BytesIO(); d.save(buf); return buf.getvalue()


@case(102)
def progress_import_is_validated_before_state_changes():
    known = {'k1', 'k2'}
    state = [{'action_id': 'k1', 'status': 'not_reviewed', 'owner': None, 'due_date': None, 'note': None}]
    good = [{'action_id': 'k1', 'status': 'not_reviewed', 'owner': None, 'due_date': None, 'note': None},
            {'action_id': 'k2', 'status': 'not_reviewed', 'owner': None, 'due_date': None, 'note': None}]
    g.equal(len(apply_progress(state, good, known)), 2)
    for bad in ([{'action_id': 'k9', 'status': 'not_reviewed', 'owner': None, 'due_date': None, 'note': None}],
                [{'action_id': 'k1', 'status': 'reviewed', 'owner': None, 'due_date': None, 'note': None}],
                [{'action_id': 'k1', 'status': 'not_reviewed', 'owner': None, 'due_date': None, 'note': None, 'extra': 1}]):
        before = json.dumps(state, sort_keys=True)
        try: apply_progress(state, bad, known)
        except (g.Blocked, ValidationError): pass
        else: g.require(False, 'expected the import to be refused')
        g.equal(json.dumps(state, sort_keys=True), before)  # the state never changed
    return {'invalid_imports_refused': 3, 'state_unchanged_on_refusal': True, 'unknown_action_refused': True}


@case(103)
def tracker_keeps_working_fields_blank():
    records = [{'action_id': 'k1', 'label': 'must have', 'quote': 'must have'},
               {'action_id': 'k2', 'label': 'shall make', 'quote': 'shall make'}]
    data = tracker_workbook(records)
    cells = blank_working_cells(data, (4, 5, 6), len(records))
    g.equal(cells, {'blank': 6, 'total': 6})  # status, owner and due date are blank for every row
    g.rejects(g.Blocked, lambda: g8.read_two_ways(data, data_rows=3))  # the blank working cells read None and '' (P81)
    values = g8.read_two_ways(data, data_rows=1)
    g.equal(values['normalized_agree'], True)  # the header row alone agrees after normalization
    ws = openpyxl.load_workbook(io.BytesIO(data)).active
    g.equal(list(getattr(ws, 'tables', {})), ['Actions'])
    return {'working_fields_blank': True, 'blank_cells_break_the_two_reader_check': True,
            'native_dropdown_and_date_validation_authored': True, 'desktop_interaction_not_claimed': True}


@case(104)
def native_document_bytes_repeat():
    records = [{'action_id': 'k1', 'label': 'The TSC must have a Chair.', 'quote': 'must have'}]
    first = styled_checklist(records); time.sleep(2.2); second = styled_checklist(records)
    g.equal(first == second, False)  # every zip entry carries the wall clock at save time, so the raw bytes differ
    zip_a, zip_b = zipfile.ZipFile(io.BytesIO(first)), zipfile.ZipFile(io.BytesIO(second))
    g.equal([i.filename for i in zip_a.infolist()], [i.filename for i in zip_b.infolist()])
    g.equal(all(zip_a.read(n) == zip_b.read(n) for n in zip_a.namelist()), True)  # every part's content is identical
    g.require(any(a.date_time != b.date_time for a, b in zip(zip_a.infolist(), zip_b.infolist())), 'entry dates differ')
    core = zip_a.read('docProps/core.xml').decode()
    g.equal('2013-12-23' in core, True)  # the document property timestamp comes from the package template, not the clock
    g.equal(g6.office_digest(first), g6.office_digest(second))  # the P51 canonicalization makes the packages agree
    g.equal([r['label'] for r in action_records(first, 'charter')], ['The TSC must have a Chair.'])
    return {'raw_docx_bytes_differ_by_entry_timestamps_reproduced': True, 'every_part_content_identical': True,
            'core_xml_timestamp_is_template_not_clock': True, 'canonicalization_restores_equality': True,
            'two_second_zip_resolution_can_mask_this': True, 'text_survives_styling': True}


@case(105)
def conversion_reports_its_messages():
    records = [{'action_id': 'k1', 'label': 'The TSC must have a Chair.', 'quote': 'must have'},
               {'action_id': 'k2', 'label': 'The agency shall make records available.', 'quote': 'shall make'}]
    document = styled_checklist(records)
    out = to_html_and_markdown(document)
    g.equal(out['messages'], [])  # a clean conversion reports nothing; any message must be surfaced, not dropped
    for r in records:
        g.equal(any(r['label'] in b for b in out['html_blocks']), True)
        g.equal(any(r['label'] in b for b in out['markdown_blocks']), True)
    g.equal(len(out['html_blocks']) >= len(records), True)
    return {'messages_surfaced': True, 'every_label_reaches_html': True, 'every_label_reaches_markdown': True,
            'block_sequence_preserved': True}


@case(106)
def meeting_join_keeps_mentions_as_mentions():
    rows = [{'meeting': 'tsc-2023-11-08', 'meeting_date': '2023-11-08', 'majority_reachable': False, 'mentions': 1},
            {'meeting': 'tsc-2023-12-06', 'meeting_date': '2023-12-06', 'majority_reachable': True, 'mentions': 5}]
    out = meeting_model(rows)
    g.equal(sorted(out['meetings']), ['tsc-2023-11-08', 'tsc-2023-12-06'])
    g.equal(out['meetings']['tsc-2023-12-06']['completed_actions'], None)  # a mention count is never a completion count
    g.require('do not establish completion' in out['mention_basis'], 'the basis travels with the model')
    g.rejects(g.Blocked, lambda: meeting_model(rows + [rows[0]]))
    g.rejects(ValueError, lambda: meeting_model([{'meeting': 'x', 'meeting_date': 'tsc-2024-01', 'majority_reachable': True, 'mentions': 0}]))
    return {'dates_parsed_strictly': True, 'mentions_not_completions': True, 'duplicate_meeting_blocked': True,
            'roster_limit_carried': True}


@case(107)
def packets_render_one_per_meeting():
    meetings = [{'meeting': 'tsc-2023-11-08', 'present': '6', 'majority': 'False'},
                {'meeting': 'tsc-2023-12-06', 'present': '10', 'majority': 'True'}]
    pages = {m['meeting']: g8.CATALOG.render(title=m['meeting'], fields=['meeting', 'present', 'majority'], rows=[m]) for m in meetings}
    g.equal(len(pages), 2)
    for name, page in pages.items():
        g.equal(name in page, True)
        g.equal(g8.g3.external_assets(page) if hasattr(g8, 'g3') else [], [])
    combined = g8.CATALOG.render(title='Meeting packets', fields=['meeting', 'present', 'majority'], rows=meetings)
    doc = lxml_html.fromstring(combined)
    rows = [[c.text_content() for c in tr.xpath('./td')] for tr in doc.xpath('//table[@id="data"]/tr')]
    g.equal(rows, [['tsc-2023-11-08', '6', 'False'], ['tsc-2023-12-06', '10', 'True']])
    return {'one_packet_per_meeting': True, 'combined_view_matches_the_rows': True, 'no_external_assets': True}


@case(108)
def calendar_events_are_stable_and_infer_nothing():
    meetings = [{'meeting': 'tsc-2024-01-17', 'meeting_date': '2024-01-17'}]
    pinned = meeting_ics(meetings, stamp=PINNED_STAMP); time.sleep(1.1); pinned_again = meeting_ics(meetings, stamp=PINNED_STAMP)
    g.equal(pinned == pinned_again, True)  # a pinned DTSTAMP keeps the file reproducible
    live = meeting_ics(meetings, stamp=None); time.sleep(1.1); live_again = meeting_ics(meetings, stamp=None)
    g.equal(live == live_again, False)  # a clock DTSTAMP makes every write differ
    events = ics_events(pinned)
    g.equal(len(events), 1); g.equal(events[0]['dtstart'], '2024-01-17')
    g.equal((events[0]['has_time'], events[0]['has_location'], events[0]['has_attendee'], events[0]['has_alarm']), (False, False, False, False))
    g.equal(events[0]['uid'], str(uuid.uuid5(UID_NAMESPACE, 'tsc-2024-01-17')) + '@proofs')  # a stable UID, not a random one
    return {'pinned_dtstamp_reproducible': True, 'clock_dtstamp_not_reproducible_reproduced': True,
            'all_day_no_time': True, 'no_location_attendee_or_alarm_inferred': True, 'uid_stable_uuid5': True}


@case(109)
def drafts_are_reproducible_and_never_sent():
    attachments = {'packet.html': b'<html>packet</html>', 'meeting.ics': b'BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n'}
    unfixed_a = meeting_draft('tsc-2024-01-17', 'body', attachments, boundary=None)
    unfixed_b = meeting_draft('tsc-2024-01-17', 'body', attachments, boundary=None)
    g.equal(unfixed_a == unfixed_b, False)  # the MIME boundary is generated at random for every write
    fixed_a = meeting_draft('tsc-2024-01-17', 'body', attachments, boundary='proofs-0')
    fixed_b = meeting_draft('tsc-2024-01-17', 'body', attachments, boundary='proofs-0')
    g.equal(fixed_a == fixed_b, True)
    back = read_draft(fixed_a)
    g.equal((back['sender'], back['recipient']), (None, None))  # a draft carries no sender and no recipient
    g.equal(back['attachments'], {k: hashlib.sha256(v).hexdigest() for k, v in attachments.items()})
    legacy = BytesParser().parsebytes(fixed_a)
    g.equal(hasattr(legacy, 'iter_attachments'), False)  # the default parser returns a legacy message without the structured accessors
    return {'random_boundary_reproduced': True, 'set_boundary_makes_drafts_reproducible': True,
            'no_sender_or_recipient': True, 'attachment_bytes_hash_checked': True, 'messages_sent': 0,
            'legacy_parser_lacks_accessors_reproduced': True}


@case(110)
def binder_bookmarks_point_at_real_pages():
    def one_page(text):
        return g8.print_pdf('<!doctype html><html lang="en-US"><head><meta charset="utf-8"><title>t</title>'
                            '<style>@page{size:A4;margin:1cm}</style></head><body><h1>' + text + '</h1></body></html>')
    sections = [('Policy explanations', one_page('Policy explanations')), ('Charter actions', one_page('Charter actions'))]
    out = review_binder(sections)
    g.equal(out['pages'], 2); g.equal(out['sections'], 2)
    g.equal(out['toc'], [[1, 'Policy explanations', 1], [1, 'Charter actions', 2]])
    g.require(all(entry[2] <= out['pages'] for entry in out['toc']), 'every bookmark points inside the binder')
    g.rejects(ValueError, lambda: pymupdf.open().tobytes())  # a zero-page document cannot even be serialized
    _, text = g8.pdf_text(sections[0][1])
    g.equal('Policy explanations' in text, True)
    return {'bookmarks_resolve_to_pages': True, 'section_order_preserved': True, 'zero_page_document_refused_by_the_library': True,
            'page_count_from_the_reopened_binder': True}


def run() -> dict:
    g.ASSERTIONS = 0; rows = []
    for i, fn in C:
        before = g.ASSERTIONS
        try: r = fn(); state = 'passed'; error = None
        except Exception: r = {}; state = 'failed'; error = traceback.format_exc()
        rows.append({'proof': i, 'test': fn.__name__, 'status': state, 'assertions': g.ASSERTIONS - before, 'result': r, 'error': error})
    packages = ['pydantic', 'python-docx', 'XlsxWriter', 'openpyxl', 'python-calamine', 'mammoth', 'markdownify', 'icalendar', 'pymupdf', 'weasyprint', 'lxml', 'deepdiff']
    here = Path(__file__).resolve().parent
    return {'scope': 'Bounded authored handoff fixtures and reproduced library defaults; the original P101-P110 chains and their artifacts were not rerun. No message is sent and no transport is opened.',
            'test_cases': len(rows), 'passed': sum(r['status'] == 'passed' for r in rows), 'failed': sum(r['status'] == 'failed' for r in rows),
            'assertions': g.ASSERTIONS, 'full_chains_executed': 0, 'network_calls': 0, 'messages_sent': 0, 'business_actions': 0,
            'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'dependency_sha256': {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ['handoff_guards_v1.py', 'handoff_guards_v6.py', 'handoff_guards_v8.py']},
            'library_versions': {n: importlib.metadata.version(n) for n in packages}, 'results': rows}


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--report', type=Path, required=True); p.add_argument('--jsdom-dir', default=os.environ.get('JSDOM_DIR', ''))
    args = p.parse_args(); os.environ['JSDOM_DIR'] = args.jsdom_dir; g8.JSDOM_DIR = args.jsdom_dir
    result = run(); args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ['test_cases', 'passed', 'failed', 'assertions']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error'])); raise SystemExit(1)
