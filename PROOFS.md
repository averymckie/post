# Proofs

```
thing
-> change (functions)
-> thing
a line naming two things is a join
every function ran on the named input; every deliverable carries its sha256
```

## Doors

```
procedures   packs/foia/sources/usdoj-foia.gov-foia-statute.html (5 U.S.C. 552, DOJ); packs/nodejs-tsc-charter/sources/tsc-TSC-Charter.md; packs/nodejs-governance/sources/GOVERNANCE.md
records      proofs/in/receipt.csv (WABO receipt phase, 8577 rows); proofs/in/node-README.md (TSC voting members)
minutes      packs/nodejs-tsc-minutes/sources/tsc-*.md (eight Node.js TSC meetings)
event log    proofs/in/receipt.xes (WABO receipt phase, 1434 cases)
```

## P1  procedures -> facts

```
procedures
-> read (compiled_ai.read.read_html | compiled_ai.read.read_text; html.parser.HTMLParser)
-> canonical text (compiled_ai.canon.canonicalize; unicodedata.normalize NFC)
-> dependency parse (compiled_ai.parse.parse_source; ufal.udpipe.Pipeline.process)
-> predicate extraction (compiled_ai.fol.compile_atoms; predpatt.PredPatt)
-> project (compiled_ai.fol.compile_atoms; projection table as data)
-> route roles (compiled_ai.normalize.normalize; clorm.clingo.Control, two rules as data)
-> byte check (compiled_ai.check.check_atoms; sentence.text[lo:hi] == quote)
-> adjudicate (compiled_ai.adjudicate.apply_rejections; yaml.safe_load)
-> facts
```

**usc5-552-doj**

```
proofs/out/P1/usc5-552-doj/facts.jsonl                     sha256 08d2fc2fff7c11e7810c7658fa2f0deac188bae1cffa32603a21a903556991b3
shows: facts 1869; sentences 327
shows: agent(e7, x5)  "agency shall make"
shows: obligatory(e7)  "shall make"
shows: event(e7, make)  "make"
shows: theme(e7, x12)  "make available to the public information"
```

**nodejs-tsc-charter**

```
proofs/out/P1/nodejs-tsc-charter/facts.jsonl               sha256 693daac33fdd38aab8a0a887edabdc6615cdbb30e72cc2127134d09a02d0cb47
shows: facts 336; sentences 95
shows: event(e1, guide)  "Guiding"
shows: patient(e1, x2)  "Guiding Principle"
shows: theme(e5, x3)  "project is part"
shows: event(e5, part)  "part"
```

**nodejs-governance**

```
proofs/out/P1/nodejs-governance/facts.jsonl                sha256 ce60a372408888a0e047ec3e23085bd97dae2db11bb50114ea565af5b20fba85
shows: facts 815; sentences 178
shows: agent(e56, x54)  "Who can nominate"
shows: event(e56, nominate)  "nominate"
shows: patient(e56, x57)  "nominate Collaborators"
shows: event(e75, Nominat)  "Nominating"
```

## P2  facts -> ordered steps -> digest

```
facts
-> consistency proof (compiled_ai.reconcile.reconcile; z3.Solver.check, z3.Solver.unsat_core)
-> forced order (compiled_ai.order.order; networkx.transitive_reduction, networkx.lexicographical_topological_sort)
-> seal (compiled_ai.seal.seal; json.dumps, hashlib.sha256)
-> ordered steps, digest
```

**usc5-552-doj**

```
proofs/out/P2/usc5-552-doj/ordered_steps.json              sha256 58a3c227a23125b3d645f2ea62e9be716b6e2987cdc40b837987c4bbfcf5c70f
proofs/out/P2/usc5-552-doj/manifest.json                   sha256 117f82af151b14b539f97097097e455d89f4a96e31958b89c948c9014c6e5f2c
shows: consistent: True; cycle: []
shows: request -> make   forced
shows: receipt -> except   forced
shows: determination -> make   forced
shows: give -> arrange   forced
shows: digest ff8b1bee4b54894437f2f31013ab3e450fe29c9c1f541f53b3fd8938f9d3fdda
```

**nodejs-tsc-charter**

```
proofs/out/P2/nodejs-tsc-charter/ordered_steps.json        sha256 f0bbb34105387719734233f7ea1ed88b41b00c6feeac7fa600dd620d9c637dc1
proofs/out/P2/nodejs-tsc-charter/manifest.json             sha256 859cba40cf774897b4a323396202d6af2a210389592519f7e53e66320c381bd9
shows: consistent: True; cycle: []
shows: digest 20cb5a00aa44905414ff9d4e85127342e60e314ea72793385c55e1c14c02347a
```

**nodejs-governance**

```
proofs/out/P2/nodejs-governance/ordered_steps.json         sha256 46fdd991c2c12639b557c1cb52000915cf18ec3782a34c6d5f18b1b9caf9fbce
proofs/out/P2/nodejs-governance/manifest.json              sha256 6d165ccb2a474de1fcc29237a5e744c45ff40c67b41d8265e70f21b0fcff4048
shows: consistent: True; cycle: []
shows: collaborator -> more   forced
shows: share -> meeting   forced
shows: meeting -> ensure   forced
shows: hour -> be   forced
shows: digest 86aa9af42984b91c0fe1470f89e6999a5afca3f896de636b1ed0fa67bfc190c8
```

## P3  facts -> anchor dates

```
facts
-> anchor dates (timexy (spacy.blank('en').add_pipe('timexy')); TIMEX3 durations and dates)
-> anchor dates
```

**usc5-552-doj**

```
proofs/out/P3/usc5-552-doj/anchor_dates.jsonl              sha256 f835e3f6bbabc0adcc8e3d0e44673fd9ded73241250429327fd07ab7dd3a6da3
shows: "November 1, 1996" -> TIMEX3 type="DATE" value="1996-11-01T00:00:00"
shows: "one year" -> TIMEX3 type="DURATION" value="P1Y"
shows: "July 4, 1967" -> TIMEX3 type="DATE" value="1967-07-04T00:00:00"
shows: "December 31, 1999" -> TIMEX3 type="DATE" value="1999-12-31T00:00:00"
```

**nodejs-tsc-charter**

```
proofs/out/P3/nodejs-tsc-charter/anchor_dates.jsonl        sha256 0fa0ca1b1eb87b16b47381b86b335b0c3877c51756a88d3a3b339bfeba475de0
shows: "one year" -> TIMEX3 type="DURATION" value="P1Y"
```

## P4  facts -> required actions -> decision table -> policy

```
facts
-> required actions (the obligatory facts with their event lemma and quote)
-> decision table (jinja2.Environment.from_string(...).render -> GoRules JDM)
-> policy (zen.ZenEngine.create_decision; zen.ZenDecision.evaluate)
-> policy
```

**usc5-552-doj**

```
proofs/out/P4/usc5-552-doj/policy.jdm.json                 sha256 c8930334e2ce3d584228d60d760abda5f6367efc7df80ede11d3c75c5ef54ca2
shows: make  "shall make"
shows: state  "shall separately state"
shows: make  "shall make"
shows: zen loads the table; evaluate({action: 'make'}) -> {'required': True, 'rule': 'r1'}
```

**nodejs-tsc-charter**

```
proofs/out/P4/nodejs-tsc-charter/policy.jdm.json           sha256 8d0dd9917df562ecac23b7c06d73905ed2aa7c264eb6df19d0773f6bfd28457a
shows: open  "must not merely be open"
shows: have  "must have"
shows: remedy  "must be immediately remedied"
shows: zen loads the table; evaluate({action: 'open'}) -> {'required': True, 'rule': 'r1'}
```

## P5  ordered steps -> process model -> process

```
ordered steps
-> process model (pm4py.objects.bpmn.obj.BPMN (StartEvent, Task, EndEvent, Flow); pm4py.objects.bpmn.exporter.exporter.apply)
-> process
```

**usc5-552-doj**

```
proofs/out/P5/usc5-552-doj/process.bpmn                    sha256 d9d971a9a885bc30235b38276e1b3d30b247decee25ab37f25006adad9178953
shows: tasks 24, flows 36; first flow request -> make
```

**nodejs-governance**

```
proofs/out/P5/nodejs-governance/process.bpmn               sha256 c38de863a2d578f57ac33fbb6162284b5204c4b74f2f52b257680ea34cf3d167
shows: tasks 18, flows 27; first flow collaborator -> more
```

## P6  records -> facts

```
records
-> read rows (csv.DictReader | markdown.markdown + lxml.html.fromstring)
-> type (pydantic.create_model)
-> assert (clingo.Control.add; rows as ground facts)
-> facts
```

**receipt-csv**

```
proofs/out/P6/receipt-csv/facts.lp                         sha256 61ceee89f87cc39c2de45474c2e2f3c093e297e410489314fdd60798722e4126
shows: columns ['case:channel', 'case:concept:name', 'case:deadline', 'case:department', 'case:enddate', 'case:enddate_planned']...
shows: first row {'case:channel': 'Internet', 'case:concept:name': 'case-10011', 'case:deadline': '2011-12-06 13:41:31.788000+01:00'}
shows: pydantic model receipt_event with fields ['case:channel', 'case:concept:name', 'case:deadline', 'case:department']...
shows: clingo grounds 8577 facts; first event_row("case-10011","Confirmation of receipt","2011-10-11 13:45:40.276000+02:00","Resource21","General","Internet").
```

**tsc-voting-members**

```
proofs/out/P6/tsc-voting-members/facts.lp                  sha256 02494e198a159fbb0a4553a9f23ed650d027b0e94a838828089fba92f423e839
shows: first rows [{'handle': 'aduh95', 'name': 'Antoine du Hamel'}, {'handle': 'anonrig', 'name': 'Yagiz Nizipli'}]
shows: pydantic model voting_member with fields ['handle', 'name']...
shows: clingo grounds 18 facts; first voting_member("aduh95","Antoine du Hamel").
```

## P7  minutes -> parsed minutes

```
minutes
-> read (compiled_ai.read.read_text)
-> dependency parse (compiled_ai.parse.parse_source; ufal.udpipe.Pipeline.process)
-> predicate extraction (compiled_ai.fol.compile_atoms; predpatt.PredPatt)
-> route roles (compiled_ai.normalize.normalize; clorm.clingo.Control)
-> byte check (compiled_ai.check.check_atoms)
-> adjudicate (compiled_ai.adjudicate.apply_rejections)
-> parsed minutes
```

**nodejs-tsc-minutes**

```
proofs/out/P7/nodejs-tsc-minutes/facts.jsonl               sha256 a8aa9ada6ba446dbd6136cf9cdfd1d9e4c352ec7abda6432dd469f44a7ca9758
shows: facts 1583; sentences 414
shows: negated(e7)  "not stream"
shows: event(e7, stream)  "stream"
shows: patient(e7, x12)  "stream> * **GitHub Issue"
shows: event(e4, move)  "move"
```

## P8  event log -> log -> process model -> process diagram

```
event log
-> read (pm4py.read_xes)
-> discover (pm4py.discover_petri_net_inductive)
-> chart (pm4py.write_pnml; pm4py.objects.conversion.wf_net.variants.to_bpmn.apply; pm4py.objects.bpmn.exporter.exporter.apply)
-> process diagram
```

**receipt-xes**

```
proofs/out/P8/receipt-xes/process.pnml                     sha256 3c096e55edcc20f300a68b17398d1c6083a863b6ee476eba37bec018785fb80d
proofs/out/P8/receipt-xes/process.bpmn                     sha256 2a157d59a8ddf1315cab98d827d512e76f9318de8fdb6dddd39b2bec9881b0bc
shows: events 8577, cases 1434, activities 27
shows: span 2010-10-02 to 2012-01-23
shows: discovered from the first half of cases by id; start activities {'Confirmation of receipt': 717}
shows: petri net places 44, transitions 72; bpmn nodes 79
```

## P9  process, event log -> conformance -> workbook

```
process, event log
-> replay (pm4py.convert_to_event_log; pm4py.conformance_diagnostics_token_based_replay)
-> tabulate (openpyxl.Workbook.save)
-> conformance
```

**receipt-xes**

```
proofs/out/P9/receipt-xes/conformance.xlsx                 sha256 26a3ab4fa7a0bdd562cf0ce61a36afa95cecbf0c258ecb0ac97b512a7f6d140f
shows: cases fit 1425 of 1434; model from the first 717 cases
shows: first rows [['case-10011', 1.0, True, 0, 0], ['case-10017', 1.0, True, 0, 0]]
```

## P10  ordered steps, parsed minutes -> tagged steps -> workbook

```
ordered steps, parsed minutes
-> tag (clingo: shared words, #max score, ties flagged, untagged listed; stopword list as data)
-> tabulate (openpyxl.Workbook.save)
-> tagged steps
```

**nodejs-governance+nodejs-tsc-minutes**

```
proofs/out/P10/nodejs-governance+nodejs-tsc-minutes/tagged_steps.xlsx sha256 add3219e9ddd2cb9a41807ad2a35e4e82001f91f4973c846de3c92dffaa23ffd
proofs/out/P10/nodejs-governance+nodejs-tsc-minutes/tags.jsonl sha256 00216f1e1e3eb38cb74e11d3478787ffb2cc219d093277e9fb74dec5e2389f2d
shows: tagged sentences 78, ties 33, untagged 96
shows: address <- "* gireesh: personally in favor of fixing CI flakes as issues become ha"  shared: address effort
shows: be <- "Unless there are objections in meeting lets move to the times suggeste"  shared: be tsc
shows: be <- "* Commented last week that it should be in WinterCG repo, or somewhere"  shared: be tsc
shows: require <- "* lib: rewrite AsyncLocalStorage without async_hooks [#48528](https://"  shared: require requires
```

## P11  tagged steps -> measured steps -> workbook

```
tagged steps
-> measure (clingo #count per step)
-> tabulate (openpyxl.Workbook.save)
-> measured steps
```

**nodejs-governance**

```
proofs/out/P11/nodejs-governance/measured_steps.xlsx       sha256 d45da313770c165e52cd21082ffa8ab78a4841469b14c4e5165bebc1fba6cbb1
shows: be: 40
shows: add: 16
shows: share: 13
shows: time: 11
```

## P12  process, records -> measured steps -> workbook

```
process, records
-> key (duckdb: join on activity name between the model's transition labels and the rows)
-> measure (duckdb: count, avg(epoch(ts - lag(ts))))
-> tabulate (openpyxl.Workbook.save)
-> measured steps
```

**receipt-xes+receipt-csv**

```
proofs/out/P12/receipt-xes+receipt-csv/measured_activities.xlsx sha256 fcb5be3f545783b8accec11b9588eae961231f2e7f3e30c564ad04095f8faf1a
shows: Confirmation of receipt: events 1434, mean hours since previous None
shows: T02 Check confirmation of receipt: events 1368, mean hours since previous 27.94
shows: T03 Adjust confirmation of receipt: events 55, mean hours since previous 129.66
shows: T04 Determine confirmation of receipt: events 1307, mean hours since previous 10.23
```

## P13  policy, records -> decisions -> workbook

```
policy (charter: simple majority of all TSC voting members), records (roster; attendance from the minutes)
-> attendance rows (markdown.markdown; lxml.html.fromstring; the Present list of each minutes file)
-> policy (jinja2 render of the rule with the roster count -> GoRules JDM; zen.ZenEngine.create_decision)
-> evaluate (zen.ZenDecision.evaluate per meeting)
-> tabulate (openpyxl.Workbook.save)
-> decisions
```

**charter+roster+minutes**

```
proofs/out/P13/charter+roster+minutes/policy.jdm.json      sha256 e038135743787da6ec53bb05fbff39ff9be42b7ceba99398f9dcddb9c11428d9
proofs/out/P13/charter+roster+minutes/decisions.xlsx       sha256 850849d047dfa541489194091395c25fab9e6b80f79cc21ae4272ac56ed90447
shows: tsc-2023-11-08: voting members present 6
shows: tsc-2023-12-06: voting members present 10
shows: tsc-2024-01-10: voting members present 10
shows: roster: 18 voting members (nodejs/node README, retrieved 2026-09-04); majority = 10; rule quoted from the charter: "For all votes, the winning candidate option is the one that wins a simple majority of all ..."
shows: tsc-2023-11-08: present 6 -> majority reachable False
shows: tsc-2023-12-06: present 10 -> majority reachable True
shows: tsc-2024-01-10: present 10 -> majority reachable True
shows: tsc-2024-01-17: present 12 -> majority reachable True
shows: tsc-2024-02-07: present 8 -> majority reachable False
shows: tsc-2025-01-08: present 13 -> majority reachable True
shows: tsc-2025-02-05: present 6 -> majority reachable False
shows: tsc-2025-03-05: present 11 -> majority reachable True
```

## P14  ordered steps -> deck

```
ordered steps
-> layers (networkx.topological_generations)
-> draw (pptx.Presentation; Shapes.add_shape, Shapes.add_connector, Connector.begin_connect, Connector.end_connect; Presentation.save)
-> deck
```

**usc5-552-doj**

```
proofs/out/P14/usc5-552-doj/dependencies.pptx              sha256 1ac4206631f506649502d9dfbd35f5912a9d2b39cb48dcbc9b3bdc8c26764bb0
shows: layers 2, boxes 24, connectors 12
```

**nodejs-governance**

```
proofs/out/P14/nodejs-governance/dependencies.pptx         sha256 b81addd37191e7c2b395d1b97add7c2bed30f81c4a83bbdf42029422b264392e
shows: layers 2, boxes 18, connectors 9
```

## P15  ordered steps -> document

```
ordered steps
-> write (docx.Document; Document.add_heading, add_paragraph, add_table; docx.document.Document.save)
-> document
```

**usc5-552-doj**

```
proofs/out/P15/usc5-552-doj/ordered_steps.docx             sha256 c667775b907b4e0904ad39089534222508fc0c8c2e096d20b790693ee1ebf163
shows: paragraphs 50, table rows 13
```

## P16  facts -> workbook

```
facts
-> tabulate (openpyxl.Workbook; Worksheet.append; Workbook.save)
-> workbook
```

**usc5-552-doj**

```
proofs/out/P16/usc5-552-doj/facts.xlsx                     sha256 1c9ee3a7ab0f60c24b4163db79fb3969b861a0be35fa7f36fd8866662fc6b83b
shows: rows 1869; first agent usc5-552-doj:u0001:s00#e7 usc5-552-doj:u0001:s00#x5 "agency shall make"
```

## P17  anything -> digest

```
every deliverable above
-> seal (json.dumps sort_keys; hashlib.sha256)
-> digest
```

**all**

```
proofs/out/P17/all/digests.json                            sha256 9e322e6c80be00f8781ad22f7dfb8d8b32f7cec06dca9dc564d4af8fc9d783a2
shows: deliverables 35; digest a2afe43607c51dc2fb2ed8173e6cb515a95f52b16ea05e3d17a659e7ff1ad853
```

## P18  ordered steps, parsed minutes -> tagged steps -> measured steps -> selected steps -> deck -> digest

```
tagged steps (P10), forced order (P2)
-> select (clingo: steps tagged by lines of one meeting; forced edges among them; #count lines per step)
-> layers (networkx.topological_generations)
-> draw (pptx.Presentation; add_shape, add_connector; Presentation.save)
-> seal (json.dumps sort_keys; hashlib.sha256)
-> deck, digest
```

**nodejs-governance+tsc-2024-01-17**

```
proofs/out/P18/nodejs-governance+tsc-2024-01-17/deck.pptx  sha256 811dbbd95322a1aa1437bcf772deb76b6a4d429c5c32016bc6910bbb6749949c
proofs/out/P18/nodejs-governance+tsc-2024-01-17/digest.json sha256 b2328db5e57553bf2e78baeae9d4ab96bf46dd621ad37e82c3c6a4c1f274c684
shows: meeting tsc-2024-01-17: steps discussed 8, forced edges among them 2
shows: deck layers 2, boxes 8, connectors 2
shows: digest over the rows 50eb80166c955055f3b483e174ff4cbe33216d892ae519183301cc586d7c12d6
```

## P19  deck -> rows -> digest' ; digest', digest -> match

```
deck (P18)
-> read shapes (pptx.Presentation; slide.shapes, Shape.text_frame)
-> seal (json.dumps sort_keys; hashlib.sha256)
-> compare (csv_diff.compare)
-> match, or the differing cell
```

**nodejs-governance**

```
proofs/out/P19/nodejs-governance/compare.json              sha256 a9a0e05c609bc913ab1654c8731d319fa7581ac6f8563f474f5dd438c1a8849c
shows: boxes read back 8
shows: digest' 72880cfbc855245c498419eee938dd060ea9eea70a88f4d68d9bf5e99c9bc596
shows: rows match: True; changed 0, added 0, removed 0
```

## P20  tagged steps -> event log ; process, event log -> conformance -> workbook

```
tagged steps (P10), forced order (P2)
-> event log (clingo: case = meeting, activity = tagged step (ties dropped), time = first sentence that mentions it)
-> replay (clingo: violated(M,A,B) :- forced(A,B), first mention of B before first mention of A)
-> tabulate (openpyxl.Workbook.save)
-> conformance
```

**nodejs-governance**

```
proofs/out/P20/nodejs-governance/conformance.xlsx          sha256 b53ea0adab90081ffc1bd56b82c5395434e278d7abbde3601c5297610f9ff083
shows: forced edges respected in the minutes 0, violated 2
shows: VIOLATED tsc-2024-01-17: add discussed before time
shows: VIOLATED tsc-2025-01-08: add discussed before time
```

## Pins

```
ufal.udpipe 1.4.0.1 · predpatt 1.0.1 · clingo 5.8.2 · clorm 1.6.3 · z3-solver 5.1.0.0 · networkx 3.6.1 · timexy 0.1.3 · spacy 3.8.16 · zen-engine 2.0.2 · Jinja2 3.1.6 · pm4py 2.7.23.8 · pydantic 2.13.5 · duckdb 1.5.5 · markdown 3.6 · lxml 6.1.3 · python-pptx 1.0.2 · python-docx 1.2.0 · openpyxl 3.1.2 · csv-diff 1.2 · PyYAML 6.0.3
```
