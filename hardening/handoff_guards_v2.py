"""Second bounded adapter suite. Requires handoff_guards_v1.py from this TXT.
No native Office applications, original chain implementations, or live actions.
"""
from __future__ import annotations
import argparse, hashlib, json, traceback, copy
from pathlib import Path
from collections import Counter
from datetime import date
import pandas as pd
from pandas.errors import MergeError
import networkx as nx
import handoff_guards_v1 as g


def tally_mentions(rows):
    keys=[(r['source_version'],r['mention_id']) for r in rows]
    if len(keys)!=len(set(keys)):raise g.Blocked('duplicate mention identity')
    if any(r['state'] not in {'approved_tag','ambiguous','unmatched'} for r in rows):raise g.Blocked('unknown mapping state')
    counts=Counter(r['concept_id'] for r in rows if r['state']=='approved_tag')
    if None in counts:raise g.Blocked('missing approved concept')
    return {'mentions':dict(counts),'ambiguous':sum(r['state']=='ambiguous' for r in rows),'unmatched':sum(r['state']=='unmatched' for r in rows),'population':len(rows)}


def case_gaps(rows):
    df=pd.DataFrame(rows)
    required={'case_id','event_id','timestamp'}
    if not required<=set(df):raise g.Blocked('missing event fields')
    if df[['case_id','event_id','timestamp']].isna().any().any():raise g.Blocked('null identity or time')
    if df[['case_id','event_id']].duplicated().any():raise g.Blocked('duplicate event')
    df['timestamp']=pd.to_datetime(df['timestamp'],utc=True,errors='raise')
    if df[['case_id','timestamp']].duplicated().any():raise g.Blocked('timestamp ties need causal ordering contract')
    df=df.sort_values(['case_id','timestamp'])
    df['prior']=df.groupby('case_id',dropna=False)['timestamp'].shift(1)
    df['gap']=(df['timestamp']-df['prior']).dt.total_seconds()
    return {r.event_id:None if pd.isna(r.gap) else int(r.gap) for r in df.itertuples()}


def majority_at(meeting:date,rosters:list[dict],present:set[str]):
    rows=[r for r in rosters if r['valid_from']<=meeting<r['valid_to']]
    if len(rows)!=1 or rows[0]['coverage']!='complete':raise g.Blocked('historical voting roster unresolved')
    eligible=rows[0]['voters']
    if not eligible or len(eligible)!=len(set(eligible)):raise g.Blocked('invalid voting population')
    threshold=len(eligible)//2+1
    return {'present_voters':len(present&set(eligible)),'threshold':threshold,'majority_reachable':len(present&set(eligible))>=threshold,'vote_result':None}


def shape_edges(nodes,bindings,edges):
    if set(nodes)!=set(bindings):raise g.Blocked('node binding mismatch')
    if len(set(bindings.values()))!=len(bindings):raise g.Blocked('shape identity reused')
    if any(u not in nodes or v not in nodes for u,v in edges):raise g.Blocked('connector endpoint missing')
    return [(bindings[u],bindings[v]) for u,v in edges]


def typed_readback(before,after):
    # JSON strings encode null/Boolean/number/string distinctions lost by Python
    # equality (True == 1). Row order and repeated values remain significant.
    if g.canonical_local(before)!=g.canonical_local(after):raise g.Blocked('typed ordered content mismatch')
    return True


def dependency_complete(gph,selected):
    if not set(selected)<=set(gph):raise g.Blocked('unknown selected node')
    missing=set().union(*(nx.ancestors(gph,n) for n in selected))-set(selected) if selected else set()
    if missing:raise g.Blocked('missing prerequisites: '+','.join(sorted(missing)))
    return True

C=[]
def case(i):
    def reg(fn):C.append((i,fn));return fn
    return reg

@case(11)
def mention_counts():
    rows=[{'source_version':'v1','mention_id':'m1','concept_id':'approve','state':'approved_tag'}, {'source_version':'v1','mention_id':'m2','concept_id':None,'state':'ambiguous'}]
    r=tally_mentions(rows);g.equal(r,{'mentions':{'approve':1},'ambiguous':1,'unmatched':0,'population':2})
    g.rejects(g.Blocked,lambda:tally_mentions(rows+[rows[0]]))
    return {'denominator_keeps_ambiguity':True,'duplicate_mention_rejected':True}

@case(12)
def partitioned_lag_and_null_join():
    rows=[{'case_id':'a','event_id':'a1','timestamp':'2026-01-01T00:00:00Z'}, {'case_id':'b','event_id':'b1','timestamp':'2026-01-01T00:00:05Z'}, {'case_id':'a','event_id':'a2','timestamp':'2026-01-01T00:00:10Z'}]
    g.equal(case_gaps(rows),{'a1':None,'a2':10,'b1':None})
    g.rejects(g.Blocked,lambda:case_gaps(rows+[dict(rows[0],event_id='a3')]))
    left=pd.DataFrame({'id':[None],'v':[1]});right=pd.DataFrame({'id':[None],'x':[2]})
    g.equal(len(left.merge(right,on='id')),1)
    g.rejects(g.Blocked,lambda:g.checked_join(left,right,['id']))
    a=pd.DataFrame({'id':['1'],'v':[1]});b=pd.DataFrame({'id':['1','1'],'x':[2,3]})
    g.rejects(MergeError,lambda:g.checked_join(a,b,['id']))
    return {'case_partitioned_gaps':True,'pandas_null_match_reproduced':True,'guard_blocks_null_and_fanout':True}

@case(13)
def historical_roster():
    r={'valid_from':date(2020,1,1),'valid_to':date(2021,1,1),'coverage':'complete','voters':['a','b','c','d']}
    g.equal(majority_at(date(2020,3,1),[r],{'a','b','guest'})['majority_reachable'],False)
    g.equal(majority_at(date(2020,3,1),[r],{'a','b','c'})['threshold'],3)
    g.equal(majority_at(date(2020,3,1),[r],{'a','b','c'})['vote_result'],None)
    g.rejects(g.Blocked,lambda:majority_at(date(2019,1,1),[r],{'a','b','c'}))
    g.rejects(g.Blocked,lambda:majority_at(date(2020,3,1),[r,r],{'a'}))
    return {'time_specific_population':True,'actual_vote_not_inferred':True}

@case(14)
def duplicate_labels_distinct_nodes():
    nodes={'n1':'Review','n2':'Review'}
    g.equal(shape_edges(nodes,{'n1':'s1','n2':'s2'},[('n1','n2')]),[('s1','s2')])
    g.rejects(g.Blocked,lambda:shape_edges(nodes,{'n1':'s1','n2':'s1'},[('n1','n2')]))
    g.rejects(g.Blocked,lambda:shape_edges(nodes,{'n1':'s1','n2':'s2'},[('n1','n3')]))
    return {'bindings_checked_as_data':True,'native_pptx_not_created':True}

@case(15)
def document_body_order():
    blocks=[{'id':'b1','type':'paragraph','text':'Rule'}, {'id':'b2','type':'table','cells':[['not','approved']]}]
    g.equal(typed_readback(blocks,copy.deepcopy(blocks)),True)
    g.rejects(g.Blocked,lambda:typed_readback(blocks,list(reversed(blocks))))
    changed=copy.deepcopy(blocks);changed[1]['cells'][0][0]='now'
    g.rejects(g.Blocked,lambda:typed_readback(blocks,changed))
    return {'paragraph_table_order_and_negation':'checked','native_docx_not_created':True}

@case(16)
def typed_cells():
    cells=[None,'',False,0,'001','=1+1']
    g.equal(typed_readback(cells,list(cells)),True)
    for i,value in [(0,0),(1,None),(2,0),(4,1),(5,2)]:
        changed=list(cells);changed[i]=value;g.rejects(g.Blocked,lambda changed=changed:typed_readback(cells,changed))
    return {'null_empty_bool_numeric_and_formula_like_text_distinguished':True,'native_spreadsheet_not_created':True}

@case(17)
def local_digest_scope():
    g.equal(g.canonical_local({'b':2,'a':1}),g.canonical_local({'a':1,'b':2}))
    g.require(g.canonical_local({'v':1})!=g.canonical_local({'v':True}),'typed values collapsed')
    g.rejects(g.Blocked,lambda:g.strict_json_loads('{"a":1,"a":2}'))
    g.rejects(ValueError,lambda:g.canonical_local({'v':float('nan')}))
    return {'local_json_profile_checked':True,'JCS_compliance_or_signer_authority':False}

@case(18)
def predecessor_closed_selection():
    graph=nx.DiGraph([('A','B'),('B','C')])
    g.equal(dependency_complete(graph,{'A','B','C'}),True)
    g.rejects(g.Blocked,lambda:dependency_complete(graph,{'B','C'}))
    return {'omitted_prerequisite_detected':True,'discussion_subset_not_an_executable_plan':True}

@case(19)
def keyed_reverse_read():
    a=[{'id':'n1','label':'review'},{'id':'n2','label':'review'}]
    g.equal(typed_readback(a,copy.deepcopy(a)),True)
    g.rejects(g.Blocked,lambda:typed_readback(a,[a[0],a[0]]))
    return {'duplicate_labels_do_not_hide_lost_identity':True}

@case(20)
def discourse_order_veto():
    payload=[{'first_mention':1,'action':'approve'}]
    p={'producer':'P20','schema_id':'events','schema_version':1,'payload_sha256':hashlib.sha256(g.canonical_local(payload)).hexdigest(),'scope':'case-A','basis':'mention','coverage':'complete','source_ids':('m1',),'validation':'passed'}
    g.rejects(g.Blocked,lambda:g.accept_port(p,payload,schema='events',scope='case-A',allowed_basis={'observation'}))
    g.equal(g.accept_port(p,payload,schema='events',scope='case-A',allowed_basis={'mention'}).basis,'mention')
    return {'mention_to_execution_promotion_blocked':True}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--report',type=Path,required=True);args=p.parse_args();g.ASSERTIONS=0;rows=[]
    for i,fn in C:
        before=g.ASSERTIONS
        try:r=fn();state='passed';error=None
        except Exception:r={};state='failed';error=traceback.format_exc()
        rows.append({'proof':i,'test':fn.__name__,'status':state,'assertions':g.ASSERTIONS-before,'result':r,'error':error})
    result={'scope':'Bounded authored handoff fixtures; actual original chain integrations and native Office exporters not executed.','test_cases':len(rows),'passed':sum(r['status']=='passed' for r in rows),'failed':sum(r['status']=='failed' for r in rows),'assertions':g.ASSERTIONS,'full_chains_executed':0,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'dependency_sha256':hashlib.sha256(Path(g.__file__).read_bytes()).hexdigest(),'results':rows}
    args.report.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k] for k in ['test_cases','passed','failed','assertions']}))
    if result['failed']:print('\n'.join(r['error'] for r in rows if r['error']));raise SystemExit(1)
