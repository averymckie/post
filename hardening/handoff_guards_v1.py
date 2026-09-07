"""Bounded handoff guards, not replacements for the 300 complete proof chains.
All runtime inputs here are authored fixtures unless explicitly marked as a quote
already present in the user's proof file. No network, LLM, or business actions.
Run: python handoff_guards_v1.py --report report.json
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.metadata, importlib.util, itertools, json, math, re, traceback, unicodedata
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal
import networkx as nx
import pandas as pd
import regex
import spacy
from spacy.matcher import PhraseMatcher, Matcher, DependencyMatcher
from spacy.tokens import Doc
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from lark import Lark, UnexpectedInput
from jinja2 import Environment, StrictUndefined, UndefinedError
from dateutil.relativedelta import relativedelta
from dateutil import tz

class Blocked(ValueError):
    """Input is unsuitable for this specified handoff, not evidence of falsity."""

class Port(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', frozen=True)
    producer: str = Field(min_length=1)
    schema_id: str = Field(min_length=1)
    schema_version: int = Field(ge=1)
    payload_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    scope: str = Field(min_length=1)
    basis: Literal['source','mention','candidate','observation','scenario','rendered']
    coverage: Literal['complete','partial','unknown']
    source_ids: tuple[str, ...]
    validation: Literal['passed','failed','not_run','unknown']


def strict_json_loads(raw: str) -> Any:
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise Blocked('duplicate JSON member: '+k)
            out[k]=v
        return out
    def bad_constant(x): raise Blocked('nonfinite JSON constant: '+x)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)


def canonical_local(value: Any) -> bytes:
    # Local deterministic JSON profile only. This is not RFC 8785/JCS.
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')


def accept_port(port: dict, payload: Any, *, schema: str, scope: str,
                allowed_basis: set[str], require_complete: bool=True) -> Port:
    p=Port.model_validate(port)
    if p.schema_id != schema or p.scope != scope: raise Blocked('schema or scope mismatch')
    if hashlib.sha256(canonical_local(payload)).hexdigest()!=p.payload_sha256: raise Blocked('payload mismatch')
    if p.basis not in allowed_basis: raise Blocked('evidential basis cannot be promoted')
    if not p.source_ids or len(set(p.source_ids))!=len(p.source_ids): raise Blocked('missing or duplicate source IDs')
    if p.validation!='passed': raise Blocked('validation did not pass')
    if require_complete and p.coverage!='complete': raise Blocked('incomplete input population')
    return p


def normalized_span(raw: str, start: int, end: int) -> dict:
    """Map NFC spans only at extended-grapheme-cluster boundaries.
    An internal cluster offset has no unique raw boundary and is rejected.
    """
    pieces=[]; boundaries={0:0}; npos=0
    for m in regex.finditer(r'\X',raw):
        value=unicodedata.normalize('NFC',m.group())
        pieces.append(value); npos+=len(value); boundaries[npos]=m.end()
    normalized=''.join(pieces)
    if normalized!=unicodedata.normalize('NFC',raw): raise Blocked('normalization crosses mapped cluster boundary')
    if type(start) is not int or type(end) is not int or not 0<=start<end<=len(normalized): raise Blocked('invalid span')
    if start not in boundaries or end not in boundaries: raise Blocked('span splits a normalization cluster')
    rs,re_=boundaries[start],boundaries[end]
    result={'normalized_quote':normalized[start:end],'raw_quote':raw[rs:re_],
            'raw_codepoint_span':[rs,re_],'raw_utf8_span':[len(raw[:rs].encode()),len(raw[:re_].encode())]}
    if unicodedata.normalize('NFC',result['raw_quote'])!=result['normalized_quote']:raise Blocked('span check failed')
    return result


def reduce_precedence(g: nx.DiGraph) -> tuple[nx.DiGraph, list[dict]]:
    if type(g) is not nx.DiGraph or not nx.is_directed_acyclic_graph(g): raise Blocked('requires a simple DAG')
    for _,_,d in g.edges(data=True):
        if d.get('kind')!='precedence' or not d.get('source_ids'): raise Blocked('untyped or unsupported edge')
    reduced=nx.transitive_reduction(g)
    reduced.graph.update(copy.deepcopy(g.graph))
    reduced.add_nodes_from((n,copy.deepcopy(d)) for n,d in g.nodes(data=True))
    reduced.add_edges_from((u,v,copy.deepcopy(g.edges[u,v])) for u,v in list(reduced.edges))
    removed=[{'from':u,'to':v,'original_attributes':copy.deepcopy(g.edges[u,v]),
              'display_witness':nx.shortest_path(reduced,u,v)} for u,v in g.edges if not reduced.has_edge(u,v)]
    return reduced,removed


def anchored_month(anchor: date | None, months: int) -> date:
    if anchor is None or type(anchor) is not date: raise Blocked('exact date anchor required')
    if type(months) is not int or months<0: raise Blocked('nonnegative whole calendar months required')
    return anchor+relativedelta(months=months)

GRAMMAR=r'''
start: MODAL ACTOR ACTION OBJECT "when" FIELD OP INT
MODAL: "require" | "permit" | "forbid"
ACTOR: /[A-Z][A-Za-z_]*/
ACTION: /[a-z][a-z_]*/
OBJECT: /[a-z][a-z_]*/
FIELD: /[a-z][a-z_]*/
OP: ">=" | ">" | "=="
%import common.INT
%import common.WS
%ignore WS
'''
PARSER=Lark(GRAMMAR,parser='lalr',propagate_positions=True)

def parse_rule(text: str) -> dict:
    try: tree=PARSER.parse(text)
    except UnexpectedInput as e: raise Blocked('unsupported clause; interpretation remains unresolved') from e
    tokens=[str(t) for t in tree.children]
    return dict(zip(['modality','actor','action','object','field','operator','threshold'],tokens)) | {'threshold':int(tokens[-1])}


def validate_process_map(expected: dict[str,str], records: list[dict]) -> dict:
    keys=[r['id'] for r in records]
    if len(keys)!=len(set(keys)): raise Blocked('duplicate BPMN identity')
    if set(keys)!=set(expected): raise Blocked('missing or extra process elements')
    if any(r['kind']!=expected[r['id']] for r in records): raise Blocked('gateway or task semantics changed')
    return {'retained':len(keys)}

class Event(BaseModel):
    model_config=ConfigDict(strict=True,extra='forbid')
    namespace: str=Field(min_length=1)
    event_id: str=Field(min_length=1)
    case_id: str=Field(min_length=1)
    activity_id: str=Field(min_length=1)
    count: int=Field(ge=0)


def observed_action(kind: str, evidence: dict | None) -> str:
    if kind!='observed_completion' or not evidence: raise Blocked('mention or proposal is not a completed action')
    if not {'case_id','action_id','receipt_id','timestamp'}<=set(evidence): raise Blocked('incomplete occurrence receipt')
    if not all(isinstance(evidence[k],str) and evidence[k] for k in ['case_id','action_id','receipt_id','timestamp']): raise Blocked('empty occurrence field')
    return 'observed'


def disjoint_partition(train: set, test: set, group_by: dict) -> None:
    if not train or not test or train&test: raise Blocked('empty or overlapping partition')
    if not (train|test)<=set(group_by):raise Blocked('missing grouping identity')
    if {group_by[x] for x in train}&{group_by[x] for x in test}: raise Blocked('shared entity leaks across partitions')


def replay_summary(expected_ids: set[str], rows: list[dict], model_role: str) -> dict:
    ids=[r['case_id'] for r in rows]
    if len(ids)!=len(set(ids)) or set(ids)!=expected_ids:raise Blocked('replay population mismatch')
    states=[r['state'] for r in rows]
    allowed={'fit','deviates','not_run','unknown','unsupported'}
    if set(states)-allowed:raise Blocked('unrecognized replay state')
    return {'fit':states.count('fit'),'deviates':states.count('deviates'),
            'unassessed':sum(x in {'not_run','unknown','unsupported'} for x in states),
            'model_role':model_role,'regulatory_compliance_established':False}


def alias_candidates(text: str, lexicon: dict[str,list[str]]) -> list[str]:
    nlp=spacy.blank('en'); matcher=PhraseMatcher(nlp.vocab,attr='LOWER',validate=True)
    for concept,forms in lexicon.items():matcher.add(concept,[nlp.make_doc(f) for f in forms])
    return sorted({nlp.vocab.strings[mid] for mid,_,_ in matcher(nlp.make_doc(text))})


def resolve_alias(text: str, lexicon: dict, *, scope: str, allowed_scope: str,
                  polarity: str, expected_polarity: str) -> str:
    if scope!=allowed_scope or polarity!=expected_polarity:raise Blocked('alias scope or polarity mismatch')
    candidates=alias_candidates(text,lexicon)
    if len(candidates)!=1:raise Blocked('missing or ambiguous approved alias')
    return candidates[0]


def checked_join(left: pd.DataFrame,right: pd.DataFrame,keys:list[str],relation:str='many_to_one') -> pd.DataFrame:
    if not keys:raise Blocked('no identity keys')
    for frame in [left,right]:
        if not set(keys)<=set(frame.columns):raise Blocked('missing join key')
        if frame[keys].isna().any().any():raise Blocked('null identity cannot join')
        if any(not frame[k].map(lambda x:type(x) is str and bool(x)).all() for k in keys):raise Blocked('keys must be exact nonempty string identities')
    result=left.merge(right,on=keys,how='left',validate=relation,indicator=True)
    if not result['_merge'].eq('both').all():raise Blocked('unmatched required rows')
    if len(result)!=len(left):raise Blocked('join changed left row count')
    return result

CASES=[]; ASSERTIONS=0

def require(condition,msg):
    global ASSERTIONS
    ASSERTIONS+=1
    if not condition:raise AssertionError(msg)

def equal(a,b):require(a==b,repr(a)+' != '+repr(b))

def rejects(exc,fn):
    try:fn()
    except exc:require(True,'expected rejection')
    else:require(False,'expected rejection '+exc.__name__)

def case(proof):
    def register(fn):CASES.append((proof,fn));return fn
    return register

@case(1)
def source_span_and_missing_parser():
    raw='Cafe\u0301 approves.';m=normalized_span(raw,0,4)
    equal(m['normalized_quote'],'Café');equal(m['raw_quote'],'Cafe\u0301')
    equal(m['raw_codepoint_span'],[0,5]);equal(m['raw_utf8_span'],[0,6])
    d=spacy.blank('en')('The board approves.')
    equal(d.has_annotation('DEP',require_complete=True),False)
    rejects(Blocked,lambda:normalized_span('x',0,2))
    # Authored dependency annotation tests the matcher, not a pretrained parser.
    nlp=spacy.blank('en')
    d=Doc(nlp.vocab,words=['Board','must','not','approve'],heads=[3,3,3,3],deps=['nsubj','aux','neg','ROOT'])
    dm=DependencyMatcher(nlp.vocab)
    dm.add('NEGATED',[ [{'RIGHT_ID':'action','RIGHT_ATTRS':{'LOWER':'approve'}},{'LEFT_ID':'action','REL_OP':'>','RIGHT_ID':'negator','RIGHT_ATTRS':{'DEP':'neg'}}] ])
    equal(len(dm(d)),1)
    return {'normalization_mapping':'checked','unannotated_document_rejected_for_dependency_use':True,'dependency_matcher':'checked on authored parse','statistical_parser_accuracy':'not tested'}

@case(2)
def reduction_retains_evidence():
    g=nx.DiGraph();g.add_node('isolated',source_id='s4')
    g.add_edge('a','b',kind='precedence',source_ids=['s1']);g.add_edge('b','c',kind='precedence',source_ids=['s2']);g.add_edge('a','c',kind='precedence',source_ids=['s3'])
    raw=nx.transitive_reduction(g);equal(raw.edges['a','b'],{})
    r,removed=reduce_precedence(g)
    equal(r.edges['a','b']['source_ids'],['s1']);equal(r.nodes['isolated']['source_id'],'s4')
    equal(removed[0]['original_attributes']['source_ids'],['s3']);equal(removed[0]['display_witness'],['a','b','c'])
    r.edges['a','b']['source_ids'].append('bad');equal(g.edges['a','b']['source_ids'],['s1'])
    g.add_edge('c','a',kind='precedence',source_ids=['s5']);rejects(Blocked,lambda:reduce_precedence(g))
    return {'metadata_loss_reproduced':True,'retained_and_removed_edge_lineage':'checked','z3_entailment':'not run'}

@case(3)
def dates_need_clock_contract():
    equal(anchored_month(date(2024,1,31),1),date(2024,2,29))
    require(anchored_month(date(2024,1,31),1)!=date(2024,1,31)+timedelta(days=30),'month treated as 30 days')
    rejects(Blocked,lambda:anchored_month(None,1));rejects(Blocked,lambda:anchored_month(date(2024,1,31),True))
    z=tz.gettz('America/New_York');require(z is not None,'zone unavailable')
    equal(tz.datetime_exists(datetime(2024,3,10,2,30),z),False)
    equal(tz.datetime_ambiguous(datetime(2024,11,3,1,30),z),True)
    return {'unanchored_duration':'blocked','calendar_month':'checked','DST_gap_and_fold':'detected','TIMEX_extraction':'not run'}

@case(4)
def modality_and_unsupported_exception_gate():
    rows=[parse_rule(f'{m} Board approve request when members >= 4') for m in ['require','permit','forbid']]
    equal([r['modality'] for r in rows],['require','permit','forbid'])
    require(rows[0]!=rows[2],'polarity collapsed')
    for text in ['must not merely be open','require Board approve request when members >= 4 unless emergency','require Board approve request when members >= 4 or privileged']:
        rejects(Blocked,lambda text=text:parse_rule(text))
    env=Environment(undefined=StrictUndefined)
    rejects(UndefinedError,lambda:env.from_string('{{ actor }} {{ condition }}').render(actor='Board'))
    equal(strict_json_loads(canonical_local(rows).decode()),rows)
    return {'supported_modalities':3,'unmodeled_scope_clauses':'blocked','missing_template_field':'blocked','legal_interpretation':'not established'}

@case(5)
def gateway_identity_and_type_gate():
    expected={'start':'start','choose':'exclusive','approve':'task','end':'end'}
    rows=[{'id':k,'kind':v} for k,v in expected.items()]
    equal(validate_process_map(expected,rows),{'retained':4})
    for mutated in [rows[:-1], rows+[rows[0]], [dict(r,kind='parallel') if r['id']=='choose' else r for r in rows]]:
        rejects(Blocked,lambda mutated=mutated:validate_process_map(expected,mutated))
    return {'gateway_mutation':'blocked','missing_node':'blocked','duplicate_id':'blocked','BPMN_conversion':'not run'}

@case(6)
def strict_fact_transport():
    good={'namespace':'A','event_id':'001','case_id':'c','activity_id':'review','count':1}
    equal(Event.model_validate(good).event_id,'001')
    for v in [True,'1',1.0,-1,None]:rejects(ValidationError,lambda v=v:Event.model_validate(good|{'count':v}))
    rejects(ValidationError,lambda:Event.model_validate(good|{'unmapped':1}))
    rejects(Blocked,lambda:strict_json_loads('{"count":1,"count":2}'))
    for x in ['NaN','Infinity','-Infinity']:rejects(Blocked,lambda x=x:strict_json_loads('{"count":'+x+'}'))
    equal(strict_json_loads(canonical_local(good).decode()),good)
    return {'coercion_and_extra_fields':'rejected','duplicate_JSON_keys':'rejected','clingo_symbol_adapter':'not run'}

@case(7)
def discussion_is_not_completion():
    receipt={'case_id':'c','action_id':'review','receipt_id':'r','timestamp':'2026-01-01T00:00:00Z'}
    equal(observed_action('observed_completion',receipt),'observed')
    for kind in ['proposal','question','mention','quoted_requirement']:
        rejects(Blocked,lambda kind=kind:observed_action(kind,receipt))
    rejects(Blocked,lambda:observed_action('observed_completion',{'case_id':'c'}))
    return {'speech_act_promotions_blocked':4,'receipt_completeness':'checked','speech_act_classifier':'not implemented'}

@case(8)
def process_discovery_partition_gate():
    groups={'c1':'A','c2':'A','c3':'B','c4':'C'}
    equal(disjoint_partition({'c1','c2'},{'c3','c4'},groups),None)
    rejects(Blocked,lambda:disjoint_partition({'c1'},{'c2','c3'},groups))
    rejects(Blocked,lambda:disjoint_partition(set(),{'c3'},groups))
    rejects(Blocked,lambda:disjoint_partition({'c1'},{'c1'},groups))
    rejects(Blocked,lambda:disjoint_partition({'absent'},{'c3'},groups))
    return {'entity_leakage':'blocked','empty_or_overlapping_partitions':'blocked','process_discovery':'not run'}

@case(9)
def replay_completeness_and_role():
    rows=[{'case_id':'a','state':'fit'},{'case_id':'b','state':'unknown'}]
    result=replay_summary({'a','b'},rows,'discovered')
    equal(result['fit'],1);equal(result['unassessed'],1);equal(result['regulatory_compliance_established'],False)
    rejects(Blocked,lambda:replay_summary({'a','b'},rows[:1],'discovered'))
    rejects(Blocked,lambda:replay_summary({'a','b'},rows+[rows[0]],'discovered'))
    rejects(Blocked,lambda:replay_summary({'a'},[{'case_id':'a','state':'timeout_is_fit'}],'discovered'))
    return {'replay_population':'reconciled','unknown_is_fit':False,'token_replay_engine':'not run'}

@case(10)
def scoped_synonym_and_fuzzy_candidate_gates():
    lex={'APPROVE':['approve','sign off'],'EXECUTE_CODE':['execute'],'EXECUTE_AGREEMENT':['execute']}
    equal(alias_candidates('Please sign off',lex),['APPROVE'])
    equal(alias_candidates('execute',lex),['EXECUTE_AGREEMENT','EXECUTE_CODE'])
    equal(resolve_alias('sign off',lex,scope='review',allowed_scope='review',polarity='positive',expected_polarity='positive'),'APPROVE')
    rejects(Blocked,lambda:resolve_alias('sign off',lex,scope='other',allowed_scope='review',polarity='positive',expected_polarity='positive'))
    rejects(Blocked,lambda:resolve_alias('approve',lex,scope='review',allowed_scope='review',polarity='negative',expected_polarity='positive'))
    rejects(Blocked,lambda:resolve_alias('execute',lex,scope='review',allowed_scope='review',polarity='positive',expected_polarity='positive'))
    equal(alias_candidates('disapprove',lex),[])
    from rapidfuzz import process, fuzz
    near=process.extract('aprove',['approve','remove'],scorer=fuzz.ratio,limit=2)
    equal(near[0][0],'approve')
    require(near[0][1]<100,'misspelling reported exact')
    return {'multiword_aliases':'checked','polysemy':'unresolved','polarity_change':'blocked','fuzzy_output':'candidate only','WordNet_corpus':'not installed; no lexical expansion executed'}


def run():
    global ASSERTIONS
    ASSERTIONS=0;results=[]
    for proof,fn in CASES:
        before=ASSERTIONS
        try:out=fn();state='passed';error=None
        except Exception:out={};state='failed';error=traceback.format_exc()
        results.append({'proof':proof,'test':fn.__name__,'status':state,'assertions':ASSERTIONS-before,'result':out,'error':error})
    packages=['pydantic','networkx','pandas','spacy','lark','Jinja2','python-dateutil','regex','rapidfuzz']
    return {'scope':'Local handoff adapters and authored counterexamples only; full proof chains and production integration not executed.',
            'test_cases':len(results),'passed':sum(r['status']=='passed' for r in results),'failed':sum(r['status']=='failed' for r in results),
            'assertions':ASSERTIONS,'full_chains_executed':0,'network_calls':0,'business_actions':0,
            'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'library_versions':{n:importlib.metadata.version(n) for n in packages},'results':results}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);args=p.parse_args()
    result=run();args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ['test_cases','passed','failed','assertions','full_chains_executed']}))
    if result['failed']:
        print('\n'.join(r['error'] for r in result['results'] if r['error']));raise SystemExit(1)
