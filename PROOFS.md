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

## Pins

```
ufal.udpipe 1.4.0.1 · predpatt 1.0.1 · clingo 5.8.2 · clorm 1.6.3 · z3-solver 5.1.0.0 · networkx 3.6.1 · timexy 0.1.3 · spacy 3.8.16 · zen-engine 2.0.2 · Jinja2 3.1.6 · pm4py 2.7.23.8 · pydantic 2.13.5 · duckdb 1.5.5 · markdown 3.6 · lxml 6.1.3 · python-pptx 1.0.2 · python-docx 1.2.0 · openpyxl 3.1.2 · csv-diff 1.2 · PyYAML 6.0.3
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

### P11  tagged steps -> measured steps -> workbook  (further input)

**nodejs-tsc-charter**

```
proofs/out/P11/nodejs-tsc-charter/measured_steps.xlsx      sha256 c47f5c8d9b00930bc8cb26b281b3ba54d5d6404ca46d9dac009f7e0917eedb12
shows: have: 31
shows: establish: 30
shows: direct: 15
shows: meet: 9
```

### P15  ordered steps -> document  (further input)

**nodejs-governance**

```
proofs/out/P15/nodejs-governance/ordered_steps.docx        sha256 5a98fa1036e2907f48b87aa9cbc4dd02f9ca9cd79c2bcd9d204f7abcabca7cf4
shows: paragraphs 38, table rows 10
```

### P16  facts -> workbook  (further input)

**nodejs-tsc-charter**

```
proofs/out/P16/nodejs-tsc-charter/facts.xlsx               sha256 006843be61ac4cb9d35f14e02d71e39c7995b9e93839579dd9e2496ca80ca535
shows: rows 336; first event nodejs-tsc-charter:u0001:s02#e1 guide "Guiding"
```

### P16  facts -> workbook  (further input)

**nodejs-governance**

```
proofs/out/P16/nodejs-governance/facts.xlsx                sha256 2ffbc8222d66f2dc2bbf372bb8fc17ef9076acadd3440e749fad17588eeccace
shows: rows 815; first agent nodejs-governance:u0002:s00#e56 nodejs-governance:u0002:s00#x54 "Who can nominate"
```

## P21  records -> measured cases -> workbook

```
records (receipt.csv: the rows carry case:deadline and case:enddate)
-> key (duckdb: group the rows by case)
-> measure (duckdb: enddate compared with deadline per case; open when enddate is empty)
-> tabulate (openpyxl.Workbook.save)
-> measured cases
```

**receipt-csv**

```
proofs/out/P21/receipt-csv/deadlines.xlsx                  sha256 b747794df52a4a57706efbb3379f16935dd4da8a2c8ad3d11c8177e8130b8635
shows: outcomes {'after deadline': 377, 'by deadline': 952, 'open': 105}
shows: first rows [('case-10011', 'open'), ('case-10017', 'by deadline'), ('case-10024', 'by deadline')]
```

## P22  records -> measured groups -> workbook

```
records
-> key (duckdb: group by case, then by department and by channel)
-> measure (duckdb: count, avg(epoch(last - first)), cases ended after deadline)
-> tabulate (openpyxl.Workbook.save)
-> measured groups
```

**receipt-csv**

```
proofs/out/P22/receipt-csv/by_department_and_channel.xlsx  sha256 ecb5795581c99d3c908bae5eb1f3d6d788d1a7555489090e22c14a0e87ef42db
shows: Customer contact: cases 29, mean days 1.66, after deadline 1
shows: Experts: cases 15, mean days 11.32, after deadline 6
shows: General: cases 1390, mean days 5.42, after deadline 370
shows: channel Desk: cases 109, mean days 5.88
shows: channel Intern: cases 1, mean days 0.97
```

## P23  log -> directly-follows graph -> workbook

```
log (P8)
-> discover (pm4py.discover_dfg)
-> tabulate (openpyxl.Workbook.save; json.dumps)
-> directly-follows graph
```

**receipt-xes**

```
proofs/out/P23/receipt-xes/directly_follows.xlsx           sha256 891c5814ebe0d16cce1e2e572fc1b629182b9702da4d23c6f9c6811da0f4e8ae
proofs/out/P23/receipt-xes/directly_follows.json           sha256 947a329a7817cca79e8268d567bdec66cf9268f03b103d7ae31dddb81dc9a904
shows: edges 99; strongest T04 Determine confirmation of receipt -> T05 Print and send confirmation of receipt (1177)
shows: end activities [['T10 Determine necessity to stop indication', 828], ['T05 Print and send confirmation of receipt', 400]]
```

## P24  measured steps -> chart -> page

```
measured steps (P12)
-> chart (plotly.express.bar; Figure.update_layout)
-> page (plotly.io.write_html(full_html, div_id))
-> page
```

**receipt-xes+receipt-csv**

```
proofs/out/P24/receipt-xes+receipt-csv/dashboard.html      sha256 9e9eafed6a5d4e719bd43e1e7589d3645912c0db53f420d8670510903940d21a
shows: one bar per activity, 26 bars; plotly.js from cdn
```

## P25  required actions -> document

```
required actions (P4), facts (P1)
-> write (docx.Document; Document.add_table; docx.document.Document.save)
-> document
```

**usc5-552-doj**

```
proofs/out/P25/usc5-552-doj/required_actions.docx          sha256 20dc73844b6eda2e1d730452a8070fcbe449b0df4bfbd75ea18cfb138d875e79
shows: table rows 122
shows: agency shall make must make
shows: agency shall separately state must state
shows: agency, in accordance with published rules, shall make must make
```

**nodejs-tsc-charter**

```
proofs/out/P25/nodejs-tsc-charter/required_actions.docx    sha256 1ff341a1edf18851e2e5d81937382ab568f004b205ff74813a1e6fb6d2654d3a
shows: table rows 13
shows:  must open
shows: TSC must have must have
shows:  must remedy
```

## P26  required actions, parsed minutes -> tagged actions -> workbook

```
required actions (P4), parsed minutes
-> tag (clingo: shared words, #max score, ties flagged, untagged listed; stopword list as data)
-> tabulate (openpyxl.Workbook.save)
-> tagged actions
```

**nodejs-tsc-charter+nodejs-tsc-minutes**

```
proofs/out/P26/nodejs-tsc-charter+nodejs-tsc-minutes/tagged_steps.xlsx sha256 86f7882d295e60003c4d65c3ce5e9cafe894b3254cbb07b110fa01092ce8e65a
proofs/out/P26/nodejs-tsc-charter+nodejs-tsc-minutes/tags.jsonl sha256 9f1e239f2364163034070c055de5d26c87b3539df330ecdbf717a1c603442a7f
shows: tagged sentences 72, ties 19, untagged 102
shows: establish <- "It’s not causing any maintenance burdens AFAIK, so it should be alrigh"  shared: consensus expected time tsc
shows: establish <- "* lib: promote process.binding/_tickCallback to runtime deprecation [#"  shared: process time tsc
shows: direct <- "I think it’s only fair if they want to make up their case in a TSC mee"  shared: meeting tsc
shows: establish <- "I think it’s only fair if they want to make up their case in a TSC mee"  shared: process tsc
```

## P27  conformance, records -> measured groups -> workbook

```
conformance (P9), records (P6)
-> key (duckdb: join on case id)
-> measure (duckdb: cases, fit cases, avg(fitness) per department and per channel)
-> tabulate (openpyxl.Workbook.save)
-> measured groups
```

**receipt-xes+receipt-csv**

```
proofs/out/P27/receipt-xes+receipt-csv/conformance_by_group.xlsx sha256 c47d4fd9fcca8086e2ad4e35d393f160b6229113d74749db09b43990d2fe2f66
shows: Customer contact: cases 29, fit 29, mean fitness 1.0
shows: Experts: cases 15, fit 15, mean fitness 1.0
shows: General: cases 1390, fit 1381, mean fitness 0.9999
```

## P28  decisions, tagged actions -> meetings -> workbook

```
decisions (P13), tagged actions (P26)
-> key (clingo: join on meeting id)
-> measure (clingo #count of required actions discussed per meeting)
-> tabulate (openpyxl.Workbook.save)
-> meetings
```

**majority+charter-tags**

```
proofs/out/P28/majority+charter-tags/decisions_with_discussion.xlsx sha256 8604c41c5f827847ab8591a19f7c1c75ce570a4b11d5976a6c68b88277c94b5c
shows: tsc-2023-11-08: majority false, required actions discussed 1: establish
shows: tsc-2023-12-06: majority true, required actions discussed 5: direct, establish, have, open, publish
shows: tsc-2024-01-10: majority true, required actions discussed 5: approve, do, establish, have, remedy
shows: tsc-2024-01-17: majority true, required actions discussed 5: establish, have, open, publish, take
```

## P29  process -> executable process -> execution trace -> workbook

```
process (P5), forced order (P2)
-> mark executable (lxml.etree.parse; process.set('isExecutable', 'true'); each task renamed manualTask; ElementTree.write)
-> load (SpiffWorkflow.bpmn.parser.BpmnParser.add_bpmn_file; BpmnParser.get_spec)
-> execute (SpiffWorkflow.bpmn.workflow.BpmnWorkflow; do_engine_steps; Task.run on ready tasks in name order)
-> check (every forced edge: first completion of the earlier task precedes the later)
-> tabulate (openpyxl.Workbook.save)
-> execution trace
```

**usc5-552-doj**

```
proofs/out/P29/usc5-552-doj/process.executable.bpmn        sha256 b630a4c41554be7954d4421a8c71157af76614e53f389297d8819c1edd251731
proofs/out/P29/usc5-552-doj/execution_trace.xlsx           sha256 67824bf5929d40f73ec72f649811facbc130f9e0599dcc4ef2487f866fe62cda
shows: workflow completed: True; tasks run 24
shows: forced edges completed in order: 12 of 12
shows: first tasks ['authorize [u0131:s00#e16]', 'base [u0089:s02#e53]', 'agency [u0089:s02#e59]', 'description [u0131:s00#e44]']
```

**nodejs-governance**

```
proofs/out/P29/nodejs-governance/process.executable.bpmn   sha256 60cc794db4e0df4e77cc06d7f2ede4ac81a9ccbd553d66291edad6cd71d8df8d
proofs/out/P29/nodejs-governance/execution_trace.xlsx      sha256 553150f3815291eeaf11c08731f67e058799a4dec62bf16cea180dc519f317ad
shows: workflow completed: True; tasks run 18
shows: forced edges completed in order: 9 of 9
shows: first tasks ['address [u0068:s01#e29]', 'advance [u0068:s01#e33]', 'collaborator [u0020:s00#e25]', 'hour [u0040:s01#e8]']
```

## P30  workbook -> facts' -> digest' ; digest', digest -> match

```
workbook (P16), facts (P1)
-> read rows (python_calamine.CalamineWorkbook.from_path; CalamineSheet.to_python)
-> seal (json.dumps sort_keys; hashlib.sha256)
-> compare (csv_diff.compare)
-> match, or the differing cell
```

**usc5-552-doj**

```
proofs/out/P30/usc5-552-doj/roundtrip.json                 sha256 a8f11bdab6e62f5cc18f74624aa4bcb5840327bc674962224602cb3d4a412f39
shows: rows read back 1869; digest forward 55b30c7360337452…, back 55b30c7360337452…; match True; changed 0
```

## P31  decisions -> chart -> page

```
decisions (P13)
-> chart (plotly.graph_objects.Figure; add_bar; add_hline)
-> page (plotly.io.write_html(full_html, div_id))
-> page
```

**majority**

```
proofs/out/P31/majority/attendance.html                    sha256 80b764943b5eddb180a1575ec68af0999293a318c238ab8b31aae043c17586ec
shows: 8 bars, threshold line at 10
```

## P32  tagged actions -> coverage matrix -> workbook

```
tagged actions (P26)
-> measure (duckdb: count per (meeting, action); one row per action, one column per meeting)
-> tabulate (openpyxl.Workbook.save)
-> coverage matrix
```

**charter+minutes**

```
proofs/out/P32/charter+minutes/coverage_matrix.xlsx        sha256 99bf122d73b115921b3f68edf495826240c17f3d26c84f71fe3e1486e0f2b595
shows: matrix 9 actions x 8 meetings
shows: row approve: [0, 0, 1, 0, 0, 0, 0, 0]
```

## P33  ordered steps, tagged steps -> undiscussed steps -> workbook

```
ordered steps (P2), tagged steps (P10)
-> complement (clingo: never(E) :- step(E), not discussed(E))
-> tabulate (openpyxl.Workbook.save)
-> undiscussed steps
```

**nodejs-governance**

```
proofs/out/P33/nodejs-governance/never_discussed.xlsx      sha256 534562e3d17a9c3a5234eec28166b66f93c01449146bac76ec9f5d03780c4f32
shows: steps never discussed 9 of 18: more, collaborator, meeting, meeting, ensure, hour, oppose, zero, onboarded
```

## P34  process model -> soundness proof

```
process model (P8, discovered)
-> soundness proof (pm4py.check_soundness (woflan): workflow net, liveness, boundedness)
-> soundness proof
```

**receipt-xes**

```
proofs/out/P34/receipt-xes/process.pnml                    sha256 e75e4c1e7f195eea21e50295697bf4f0d942476e98567f579c3cf9723ae91ebd
proofs/out/P34/receipt-xes/soundness.json                  sha256 eec74566c5ddaccd1d63515e762b7a631f2f4937481101f52376ebea1f689ecb
shows: sound: True
shows: s_c_net: places: [ p_10, p_11, p_12, p_13, p_16, p_17, p_18, p_19, p_20, p_21, p_22, p_23, p_24, p_25, p_26, p_27, p_28, p_29, p_3, p_30, p_31, p_32, p_33, p_34, p_35, p_36, p_37, p_38, p_39, p_4, p_40, p_42, p_43, p_44, p_46, p_49, p_5, p_50, p_52, p_6, p_8, p_9, sink, source ]
transitions: [ (02f88d52-f9e2
shows: place_invariants: [[[ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [-1.]
  [-1.]
  [ 1.]
  [ 1.]
  [ 1.]
  [ 1.]
  [ 1.]
  [ 1.]
  [ 0.]
  [ 1.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 0.]
  [ 
shows: uniform_place_invariants: [array([[0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [0.],
       [1.],
       [0.],
       [0.],
       [0.],
       [0.],

shows: s_components: [{source, p_6, sink, p_3, p_4, (skip_1, None), (tauSplit_2, None), (e44f8c37-9009-4683-8145-8ad3117a8a4f, 'Confirmation of receipt'), (tauJoin_3, None), (skip_55, None), (cc1eb8b7-cdc7-4b32-9e8b-1b8dad144a1d, 'T15 Print document X request unlicensed'), p_5, (ae506bdb-69b5-480a-b985-977c0d6002a8, 'T0
```

## P35  process -> petri net -> soundness proof

```
process (P5)
-> read (pm4py.read_bpmn)
-> petri net (pm4py.convert_to_petri_net; pm4py.write_pnml)
-> soundness proof (pm4py.check_soundness (woflan))
-> soundness proof
```

**usc5-552-doj**

```
proofs/out/P35/usc5-552-doj/process.pnml                   sha256 df4d75ccb33a6b50e3394fb377542a6fe774043ca40b3b23ef28b7ffe1d0e4ad
proofs/out/P35/usc5-552-doj/soundness.json                 sha256 7f0efe217d243d09d2a00ad7ff51b4acf3b02bf570be0c393450528437710a4b
shows: read back 28 bpmn nodes; petri net places 38, transitions 26
shows: sound: woflan did not finish within 420 s
```

**nodejs-governance**

```
proofs/out/P35/nodejs-governance/process.pnml              sha256 8c2ab70bd4a9e282d854099206039a42150de0b51ff3434b91a84c78a9ef7ece
proofs/out/P35/nodejs-governance/soundness.json            sha256 c687384fae8a44be0c6adae3c50b017000b0c92c8268435d85e182850d473426
shows: read back 22 bpmn nodes; petri net places 29, transitions 20
shows: sound: woflan did not finish within 420 s
```

## P36  log -> variants -> workbook

```
log (P8)
-> variants (pm4py.get_variants_as_tuples)
-> tabulate (openpyxl.Workbook.save)
-> variants
```

**receipt-xes**

```
proofs/out/P36/receipt-xes/variants.xlsx                   sha256 8b4c196689661c7ea60a40ea80196634a6b460d067936f2556afb8042c9b2e81
shows: variants 116; most common (713 cases): Confirmation of receipt -> T02 Check confirmation of receipt -> T04 Determine confirmation of receipt -> T05 P
```

## P37  facts -> knowledge graph -> query results -> workbook

```
facts (P1)
-> knowledge graph (rdflib.Graph.add; Graph.serialize(format='turtle'))
-> query (rdflib.Graph.query (SPARQL))
-> tabulate (openpyxl.Workbook.save)
-> query results
```

**usc5-552-doj**

```
proofs/out/P37/usc5-552-doj/facts.ttl                      sha256 f71d193a71bbf2f5dcab6e6a337f86445e565e0397e6cce32c890dbb1633b2de
proofs/out/P37/usc5-552-doj/sparql_required_actions.xlsx   sha256 1f30aa012c9a18d4ae4630f9e27196cce9d99a72fbb216117a1fdc7a7b03effa
proofs/out/P37/usc5-552-doj/query.sparql                   sha256 f5bc9ca135b1412b919c5347bc162a0ca69b5aed1839ce6cda3226489d679715
shows: triples 4191; obligatory events with an agent 104
shows: make by agency shall make
shows: state by agency shall separately state
shows: state by agency shall separately state and currently publish
```

**nodejs-tsc-charter**

```
proofs/out/P37/nodejs-tsc-charter/facts.ttl                sha256 857fcd473d295406a3ce9e1ad9ec02502856d13ecddc7080069c1f6e1327a282
proofs/out/P37/nodejs-tsc-charter/sparql_required_actions.xlsx sha256 4eccfd89131c2ca15de3c003ab9fac75be664db5fb2026aa25d90b0964b95d73
proofs/out/P37/nodejs-tsc-charter/query.sparql             sha256 f5bc9ca135b1412b919c5347bc162a0ca69b5aed1839ce6cda3226489d679715
shows: triples 760; obligatory events with an agent 7
shows: have by TSC must have
shows: meet by TSC shall meet
shows: meet by TSC shall meet regularly using
```

## P38  facts -> graph database -> query results -> workbook

```
facts (P1)
-> graph database (kuzu.Database; kuzu.Connection.execute: CREATE NODE TABLE, CREATE REL TABLE, CREATE)
-> query (kuzu.Connection.execute (Cypher MATCH); QueryResult.get_all)
-> tabulate (openpyxl.Workbook.save)
-> query results
```

**usc5-552-doj**

```
proofs/out/P38/usc5-552-doj/cypher_results.xlsx            sha256 9b2db14d45742d8065cc490788441dc0a1baa89154c5aa280fc43ed0c2b3796e
proofs/out/P38/usc5-552-doj/queries.cypher                 sha256 156db773c1e21c62f110a3a99d280c0fa66b217b4d614bf36a3247bbc1440105
shows: events 621, args 940; obligatory events with an agent 68; precedes edges 12
shows: make by agency shall make
shows: state by agency shall separately state
shows: request precedes make
shows: receipt precedes except
```

## P39  ordered steps, facts -> pages -> site

```
ordered steps (P2), facts (P1)
-> pages (markdown tables written from the rows)
-> site (mkdocs.config.load_config; mkdocs.commands.build.build)
-> site
```

**usc5-552-doj**

```
proofs/out/P39/usc5-552-doj/site/index.html                sha256 c6422220006d2e3a745f7d8113b7c6ea1d569fe7cf14f7ef9b167574f16678b5
proofs/out/P39/usc5-552-doj/site/facts.html                sha256 977568f33992fb43e5640c6edc17fbe4097d418b8c75f9c80d6367d46d05cfbc
shows: pages 3; index rows 24; facts rows 1869
```

## P40  document -> steps' -> digest' ; digest', digest -> match

```
document (P15), ordered steps (P2)
-> read paragraphs (docx.Document; Document.paragraphs)
-> seal (json.dumps sort_keys; hashlib.sha256)
-> compare (csv_diff.compare)
-> match, or the differing cell
```

**usc5-552-doj**

```
proofs/out/P40/usc5-552-doj/roundtrip.json                 sha256 c7dd5eaa4558c9725afe526cb11feffee61dce89d0baffdcbc3801f7d5e335be
shows: steps read back 24 of 24; match True; changed 0, added 0, removed 0
```
### P4  facts -> required actions -> decision table -> policy  (further input)

**nodejs-governance**

```
proofs/out/P4/nodejs-governance/policy.jdm.json            sha256 49ffeb14ab911e7aa42c283c5daf90cd0fd4013e136093d6637d4af1413647c7  registered
shows: approve  "must approve"
shows: collaborator  "must be from collaborators"
shows: zen loads the table; evaluate({action: 'approve'}) -> {'required': True, 'rule': 'r1'}
```

## P41  ordered steps -> layers -> 3D process page

```
ordered steps (P2)
-> layers (networkx.topological_generations; z from the source unit of each step)
-> draw (plotly.graph_objects.Scatter3d (lines, markers+text))
-> page (plotly.io.write_html(full_html, div_id))
-> 3D process page
```

**usc5-552-doj**

```
proofs/out/P41/usc5-552-doj/process_3d.html                sha256 de6cf2d9dadd83c946af728172c4a94ab0f2290312d89df4adf3d341cc183931  registered
shows: nodes 24, edges 12, layers 2; z = source unit index
```

### P41  ordered steps -> layers -> 3D process page  (further input)

**nodejs-governance**

```
proofs/out/P41/nodejs-governance/process_3d.html           sha256 3327c62a2f8f1d88e1db3142b2dfae12612c46a791c43dc7c53e0c66dec111b2  registered
shows: nodes 18, edges 9, layers 2; z = source unit index
```

## P42  policy -> readable policy page

```
policy (P4 or P13), decisions (P13)
-> read table (json.loads of the GoRules JDM; inputs, outputs, rules, rule descriptions)
-> page (jinja2.Environment(autoescape).from_string(...).render -> html)
-> policy page
```

**majority**

```
proofs/out/P42/majority/policy.html                        sha256 65c31de300fd01cd146714fb7773e18061a5a2887b0afe03c28c9e9400fe83f9  registered
shows: rules 2; first: if present voting members >= 10 then majority reachable = true; rule = r1
```

### P42  policy -> readable policy page  (further input)

**usc5-552-doj**

```
proofs/out/P42/usc5-552-doj/policy.html                    sha256 8d432f293ecc14adb3df2d04f0bfc94ea77524d72e2f51e7c62fc39a536a3e80  registered
shows: rules 66; first: if action "make" then required = true; rule = r1
```

## P43  records -> measured cells -> heatmap page

```
records (P6)
-> measure (duckdb: avg(epoch(ts - lag(ts))) per department and activity)
-> chart (plotly.express.imshow)
-> page (plotly.io.write_html(full_html, div_id))
-> heatmap page
```

**receipt-csv**

```
proofs/out/P43/receipt-csv/heatmap.html                    sha256 3504954defb53f9ea3ac88bdec339a03c5b8c1ce74d8d196d92327f057ce545a  registered
proofs/out/P43/receipt-csv/heatmap.xlsx                    sha256 1066a4d0170faf376a4b4188d0d324f8bc09d58b85af50452718d9af5efaf644  registered
shows: 3 departments x 26 activities
shows: Experts / T13 Adjust document X request unlicensed: 410.72 h
shows: General / T03 Adjust confirmation of receipt: 154.61 h
shows: General / T09-3 Process or receive external advice from party 3: 108.14 h
```

## P44  facts -> actor by action matrix -> workbook

```
facts (P1)
-> measure (duckdb: count per (agent quote, event lemma) over obligatory events)
-> tabulate (openpyxl.Workbook.save)
-> actor by action matrix
```

**usc5-552-doj**

```
proofs/out/P44/usc5-552-doj/who_must_what.xlsx             sha256 aa06b6378b2ce858c477a33f3ecc432bfc47f3cbad98620ae1e2705afb6124a7  registered
shows: 56 actors x 36 required actions
shows: agency shall make must make (9)
shows: agency shall notify must notify (2)
shows: agency shall promulgate must promulgate (2)
```

## P45  tagged steps -> timeline page

```
tagged steps (P10)
-> measure (count of lines per (meeting, step))
-> chart (plotly.graph_objects.Scatter (marker size = lines))
-> page (plotly.io.write_html)
-> timeline page
```

**nodejs-governance**

```
proofs/out/P45/nodejs-governance/timeline.html             sha256 363997bc9a827017d9d25339455ffd01d02b01cd435f2ae1764dcc6819c52739  registered
shows: points 22; meetings 8, steps 9
```

## P46  directly-follows graph, measured steps -> bottlenecks -> workbook

```
directly-follows graph (P23), measured steps (P12)
-> key (duckdb: join edges to the waiting time of their target activity)
-> rank (duckdb: order by mean hours desc)
-> tabulate (openpyxl.Workbook.save)
-> bottlenecks
```

**receipt-xes**

```
proofs/out/P46/receipt-xes/bottlenecks.xlsx                sha256 24e95ee3c33152b11796844dee5d4aab374d9bb3933b4efe29179ea1225211ca  registered
shows: T05 Print and send confirmation of receipt -> T13 Adjust document X request unlicensed: 2 cases, 205.36 h
shows: T02 Check confirmation of receipt -> T03 Adjust confirmation of receipt: 43 cases, 129.66 h
shows: T04 Determine confirmation of receipt -> T03 Adjust confirmation of receipt: 6 cases, 129.66 h
```

## P47  records, measured groups -> decision table -> decisions -> workbook

```
records (P6), measured groups (P22)
-> measure (duckdb: department mean duration; elapsed days of each open case at the log's end)
-> decision table (jinja2 render: one rule per department, threshold = its mean -> GoRules JDM)
-> evaluate (zen.ZenEngine.create_decision; zen.ZenDecision.evaluate per open case)
-> tabulate (openpyxl.Workbook.save)
-> decisions
```

**receipt-csv**

```
proofs/out/P47/receipt-csv/policy.jdm.json                 sha256 6bc04dac17275fce6bb01debab65ddcdff1d73ce370fde16e8b3766e090cf312  registered
proofs/out/P47/receipt-csv/at_risk.xlsx                    sha256 48d3f15fc112a71ea5d5bad8f507eb3efdee23b05d1efb836f9471680bc9ab3a  registered
shows: log ends 2012-01-23; open cases 105; at risk 94
shows: department means [('Customer contact', 1.66), ('Experts', 11.32), ('General', 5.42)]
shows: first rows [['case-10011', 'General', 60.0, True, 'r3'], ['case-10073', 'General', 54.19, True, 'r3']]
```

## P48  required actions -> checklist document

```
required actions (P4), facts (P1)
-> write (docx.Document; add_paragraph with a box glyph per required action and its sentence; docx.document.Document.save)
-> checklist document
```

**nodejs-tsc-charter**

```
proofs/out/P48/nodejs-tsc-charter/checklist.docx           sha256 90fc5c88ddec2436d62e40eb2d2f3183537afc8c21e6eca3712e65430adda49b  registered
shows: checklist items 13
```

### P48  required actions -> checklist document  (further input)

**usc5-552-doj**

```
proofs/out/P48/usc5-552-doj/checklist.docx                 sha256 0f28c008d487ab23e99bceb293a4134e02da5af00f9968081c4008f8c1275c8d  registered
shows: checklist items 122
```

## P49  required actions, required actions -> shared and unshared actions -> workbook

```
required actions of two documents (P4)
-> key (clingo: join on the action lemma across documents)
-> tabulate (openpyxl.Workbook.save)
-> shared and unshared actions
```

**nodejs-tsc-charter+nodejs-governance**

```
proofs/out/P49/nodejs-tsc-charter+nodejs-governance/cross_document.xlsx sha256 63bafd8676d8c8269d4fc8a076f758d423af5b4b499285c050ccaa8498167c53  registered
shows: required in both documents: ['approve']
shows: only in one: 13
```

## P50  site -> steps' -> digest' ; digest', digest -> match

```
site (P39), ordered steps (P2)
-> read page (lxml.html.fromstring; xpath over the steps table)
-> seal (json.dumps sort_keys; hashlib.sha256)
-> compare (csv_diff.compare)
-> match, or the differing cell
```

**usc5-552-doj**

```
proofs/out/P50/usc5-552-doj/roundtrip.json                 sha256 275f48efe8a265823f93a4f37c7679ab78f0075e201b9e182ad617fc89bffde6  registered
shows: rows read back 24 of 24; match True; changed 0
```

## P51  deliverable -> canonical office file -> digest

```
ordered steps (P2)
-> save twice (openpyxl.Workbook.save, one second apart)
-> canonical office (zipfile: docProps/core.xml created and modified fixed; entry dates fixed; entries sorted)
-> digest (hashlib.sha256)
-> digest
```

**usc5-552-doj**

```
proofs/out/P51/usc5-552-doj/a.xlsx                         sha256 0318e5d777d88c20cd9977a3c1ecb00364b398b78f248c9d606d088a09d3a851  registered
shows: two saves of the same rows, one second apart: raw bytes equal False; after canonical office True
shows: digest 0318e5d777d88c20cd9977a3c1ecb00364b398b78f248c9d606d088a09d3a851
```

## P52  process model -> canonical ids -> one byte sequence

```
process model (P5, P8)
-> scramble (lxml: fresh random ids, shuffled children, three times)
-> canonical ids (colour refinement over references, individualization on ties, elements ordered by the result; lxml.etree.indent)
-> compare (bytes equal across all three)
-> one byte sequence
```

**usc5-552-doj**

```
proofs/out/P52/usc5-552-doj/canonical.bpmn                 sha256 6209f474a27c67b72b44c6dc345b5d9f06bf2f24c86d485582cb8442e5697d61  registered
shows: three scrambles (fresh ids, shuffled order) canonicalize to one byte sequence: True; equal to the canonical original: True
```

### P52  process model -> canonical ids -> one byte sequence  (further input)

**receipt-xes**

```
proofs/out/P52/receipt-xes/canonical.pnml                  sha256 64593d43e20fd6e3b2290bba6654397e12237e08247d2517f11684b17c9b0d55  registered
shows: three scrambles (fresh ids, shuffled order) canonicalize to one byte sequence: True; equal to the canonical original: True
```

## P53  deliverable digests -> register -> reproduced, registered or changed ; sections -> ledger append

```
every deliverable of this run; proofs/register.json; proofs/ledger.json
-> compare (json: each digest against the registered one; a match is reproduced, a new file is registered, a difference is changed)
-> append (PROOFS.md opened in append mode: new sections only; changes as an amendment block)
-> register state
```

**all**

```
proofs/out/P53/all/register_state.json                     sha256 477775f6280ea73641d71b52d368c58c65526b06c245021f89a518d8764328e4  index
shows: deliverables reproduced 31, registered now 143, changed 45; ledger sections before this run 97, amendments 0
```

## Baseline: the ITIL surface

Every practice's deliverables, each a chain of operations bound to library functions, run on the real inputs; proofs/itil.yaml is the register.

### coverage

```
practice                                      deliverables  proven  empty  failed  no real input
Architecture management                                  4       4      0       0              0
Continual improvement                                    4       3      0       0              1
Information security management                          4       4      0       0              0
Knowledge management                                     4       4      0       0              0
Measurement and reporting                                4       4      0       0              0
Organizational change management                         4       3      0       0              1
Portfolio management                                     3       3      0       0              0
Project management                                       4       4      0       0              0
Relationship management                                  3       2      0       0              1
Risk management                                          3       3      0       0              0
Service financial management                             4       1      0       0              3
Strategy management                                      3       3      0       0              0
Supplier management                                      3       2      0       0              1
Workforce and talent management                          4       4      0       0              0
Availability management                                  3       3      0       0              0
Business analysis                                        4       4      0       0              0
Capacity and performance management                      4       4      0       0              0
Change enablement                                        5       5      0       0              0
Incident management                                      6       6      0       0              0
IT asset management                                      4       4      0       0              0
Monitoring and event management                          4       4      0       0              0
Problem management                                       4       4      0       0              0
Release management                                       4       4      0       0              0
Service catalogue management                             3       3      0       0              0
Service configuration management                         4       4      0       0              0
Service continuity management                            4       4      0       0              0
Service design                                           3       3      0       0              0
Service desk                                             4       4      0       0              0
Service level management                                 4       4      0       0              0
Service request management                               4       4      0       0              0
Service validation and testing                           4       4      0       0              0
Deployment management                                    4       4      0       0              0
Infrastructure and platform management                   3       3      0       0              0
Software development and management                      4       4      0       0              0
all                                                    130     123      0       0              7
```

### Architecture management / component dependency model  proven

```
shape: components and the dependencies between them, with the strength of each dependency
instantiated on: activities and directly-follows edges of the receipt-phase log
-> dfg (P23: pm4py.discover_dfg)
-> sort by=["count"], desc=true (duckdb ORDER BY)
-> workbook name=dependency_model (openpyxl.Workbook.save)
-> component dependency model
proofs/out/itil/architecture-management/component-dependency-model/dependency_model.xlsx sha256 18d955657444fd3eb9ebde649272460f6daa31d5bad719da33b7b4731c342909  registered
shows: rows 99; first {"from": "T04 Determine confirmation of receipt", "to": "T05 Print and send confirmation of receipt", "count": 1177}
```

### Architecture management / architecture standards register  proven

```
shape: the standing rules a design must satisfy, each with its source sentence
instantiated on: obligations of the Node.js TSC charter
-> required_actions of=nodejs-tsc-charter (P4: the obligatory facts with agent quotes)
-> select fields=["unit", "who", "action", "sentence"] (duckdb SELECT)
-> workbook name=standards (openpyxl.Workbook.save)
-> architecture standards register
proofs/out/itil/architecture-management/architecture-standards-register/standards.xlsx sha256 f7e6e02e08fce77cb37eda55c09761e20d4eb51df6f1678f5e20309785f7db4f  registered
shows: rows 13; first {"unit": "u0002", "who": "", "action": "open", "sentence": "Project proposals, timelines, and status must not merely be open, but also easily visible to outsiders."}
```

### Architecture management / architecture roadmap  proven

```
shape: steps grouped into phases in forced order
instantiated on: ordered steps of the Node.js governance document
-> ordered_steps of=nodejs-governance (P2: z3 consistency proof; networkx forced order)
-> select fields=["phase", "position", "step", "sentence"] (duckdb SELECT)
-> page name=roadmap, title=roadmap: phases of the governance steps, kind=table (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> architecture roadmap
proofs/out/itil/architecture-management/architecture-roadmap/roadmap.html sha256 6494d3671edde9365e6da9a1557a670c722d47aeb39384715dd4156094295144  registered
shows: rows 18; first {"phase": 1, "position": 1, "step": "collaborator", "sentence": "A collaborator is automatically made emeritus (and removed from active collaborator status) if it has been more than 12 months since the collaborator has a
```

### Architecture management / change impact assessment  proven

```
shape: for each component, everything that depends on it, transitively
instantiated on: forced precedence of 5 U.S.C. 552
-> forced_edges of=usc5-552-doj (P2: networkx.transitive_reduction)
-> clingo in=edge, fields=["before", "after", "before_step", "after_step"], out=impact, out_fields=["component", "step", "dependents"] program: dep(A,B) :- edge(A,B,_,_). dep(A,C) :- dep(A,B), edge(B,C,_,_). name(A,N) :- edge(A,_,N,_). name(B,N) :- edge(_,B,_,N). impact(A,N,K) :- name(A,N), K = #count{  (clingo.Control.add / ground / solve; rows as ground facts)
-> sort by=["dependents"], desc=true (duckdb ORDER BY)
-> workbook name=impact (openpyxl.Workbook.save)
-> change impact assessment
proofs/out/itil/architecture-management/change-impact-assessment/impact.xlsx sha256 2e7543679eaf64df3fc94a1bac96a83cb313b7222fc85b388bad46cbeb1aad66  registered
shows: rows 12; first {"component": "usc5-552-doj:u0021:s00#e43", "step": "request", "dependents": 1}
```

### Continual improvement / improvement register  proven

```
shape: candidate improvements with where they were raised
instantiated on: TSC minutes sentences whose actions include improve, fix, rework, migrate, deprecate, remove or simplify
-> minutes_sentences (P7: compiled_ai parse of the minutes; one row per sentence with its event lemmas)
-> filter where=[["lemmas", "matches", "\\b(improve|fix|rework|migrate|deprecate|remove|simplify|unflag|enable)\\b"]] (duckdb WHERE)
-> select fields=["meeting", "sentence_id", "lemmas", "sentence"] (duckdb SELECT)
-> workbook name=improvement_register (openpyxl.Workbook.save)
-> improvement register
proofs/out/itil/continual-improvement/improvement-register/improvement_register.xlsx sha256 ff1e5ae1fbaded86922a72f8bda2c28a5fd2322445b4450d69fde3533a6deb55  registered
shows: rows 29; first {"meeting": "tsc-2023-11-08", "sentence_id": "tsc-2023-11-08:u0010:s06", "lemmas": "remove say wait", "sentence": "wait for a week to see what Kafra says, remove the label."}
```

### Continual improvement / improvement measurement  proven

```
shape: the measure before and after, per period
instantiated on: receipt-phase cases per month, mean duration and cases after deadline
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=["month"], aggregates=[["count", "*", "cases"], ["avg", "duration_days", "mean_days"], ["sum", "late", "after_deadline"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=measurement_by_month (openpyxl.Workbook.save)
-> improvement measurement
proofs/out/itil/continual-improvement/improvement-measurement/measurement_by_month.xlsx sha256 403198098487f5be6e5379dd2aa472591ac17cbc2a0708d9973286a2db941e73  registered
shows: rows 16; first {"month": "2010-10", "cases": 15, "mean_days": 10.38, "after_deadline": 10.0}
```

### Continual improvement / improvement review report  proven

```
shape: conformance of the work to the model, per group
instantiated on: receipt-phase conformance joined to case departments
-> cases (duckdb: one row per case from the event rows)
-> save_as name=cases (the relation kept under a name for a later join)
-> conformance (P9: pm4py.conformance_diagnostics_token_based_replay)
-> join with=cases, keys=[["case", "case"]] (duckdb JOIN)
-> derive field=fit, fn=contains, of=is_fit, value=true (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=["department"], aggregates=[["count", "*", "cases"], ["sum", "fit", "fit_cases"], ["avg", "fitness", "mean_fitness"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> document name=review_report, title=review: fitness to the process model, per department (docx.Document; add_table; docx.document.Document.save)
-> improvement review report
proofs/out/itil/continual-improvement/improvement-review-report/review_report.docx sha256 d743b15186fe1bd6bf852154aed3dca1d1c0d78ac93960bbe4d79aa027ab3697  registered
shows: rows 3; first {"department": "Customer contact", "cases": 29, "fit_cases": 29.0, "mean_fitness": 1.0}
```

### Continual improvement / improvement business case  no real input

```
shape: cost and benefit of a proposed improvement
instantiated on: none
-> cases (duckdb: one row per case from the event rows)
-> workbook name=business_case (openpyxl.Workbook.save)
-> improvement business case
```

### Information security management / confidentiality obligations register  proven

```
shape: obligations about withholding, exempting or protecting information, with sources
instantiated on: 5 U.S.C. 552 sentences containing withhold, exempt, classified, confidential or privacy
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> filter where=[["sentence", "matches", "(?i)withh|exempt|classif|confiden|privacy"]] (duckdb WHERE)
-> select fields=["unit", "who", "action", "sentence"] (duckdb SELECT)
-> workbook name=confidentiality_obligations (openpyxl.Workbook.save)
-> confidentiality obligations register
proofs/out/itil/information-security-management/confidentiality-obligations-register/confidentiality_obligations.xlsx sha256 5156f7a28bc7003cd7802016679474adeb90e01087ade7bac7d2d318eb8c996f  registered
shows: rows 15; first {"unit": "u0018", "who": "", "action": "explain", "sentence": "However, in each case the justification for the deletion shall be explained fully in writing, and the extent of such deletion shall be indicated on the porti
```

### Information security management / access control matrix  proven

```
shape: who is required to do what
instantiated on: agents and required actions of 5 U.S.C. 552
-> who_must_what of=usc5-552-doj (P44: duckdb count per (agent, action))
-> pivot row=who, col=action, value=count, fn=sum (duckdb GROUP BY, laid out as a matrix)
-> workbook name=access_matrix (openpyxl.Workbook.save)
-> access control matrix
proofs/out/itil/information-security-management/access-control-matrix/access_matrix.xlsx sha256 d6501053fd60b08aca40bca95acb9afdeda53f38788d6960588c14134ad77c0a  registered
shows: rows 54; first {"who": "administrator of general services shall provide", "accord": 0, "allow": 0, "assess": 0, "assist": 0, "chair": 0, "conduct": 0, "consult": 0, "cover": 0, "designate": 0, "determine": 0, "develop": 0, "director": 
```

### Information security management / prohibitions register  proven

```
shape: what must not be done, with the sentence
instantiated on: negated obligations of 5 U.S.C. 552
-> prohibitions of=usc5-552-doj (P1 facts where obligatory and negated)
-> workbook name=prohibitions (openpyxl.Workbook.save)
-> prohibitions register
proofs/out/itil/information-security-management/prohibitions-register/prohibitions.xlsx sha256 b2ef042b7d089d3e3eb650a4e0a5abb921a36d3829aebf54a74d0d94706e1369  registered
shows: rows 10; first {"event": "usc5-552-doj:u0025:s00#e52", "action": "make", "sentence_id": "usc5-552-doj:u0025:s00", "sentence": "(E) An agency, or part of an agency, that is an element of the intelligence community (as that term is defin
```

### Information security management / security incident report  proven

```
shape: security releases with date, line and releaser
instantiated on: Node.js 22 changelog, releases marked as security releases
-> changelog (re over CHANGELOG_V22.md: one row per release, security releases flagged)
-> filter where=[["security", "eq", true]] (duckdb WHERE)
-> select fields=["date", "version", "codename", "kind", "releaser", "commits"] (duckdb SELECT)
-> document name=security_incidents, title=security releases of Node.js 22 (docx.Document; add_table; docx.document.Document.save)
-> security incident report
proofs/out/itil/information-security-management/security-incident-report/security_incidents.docx sha256 516acdcdfe51f10ae31548bb509898d0d3bd951597db1cf98b00096318c2e15d  registered
shows: rows 6; first {"date": "2026-07-29", "version": "22.23.2", "codename": "Jod", "kind": "LTS", "releaser": "marco-ippolito", "commits": 12}
```

### Knowledge management / glossary  proven

```
shape: defined terms with their defining sentences
instantiated on: definitional sentences of 5 U.S.C. 552 (mean, include, define)
-> definitions of=usc5-552-doj (P1 facts where the event lemma is mean, include or define)
-> select fields=["unit", "verb", "sentence"] (duckdb SELECT)
-> workbook name=glossary (openpyxl.Workbook.save)
-> glossary
proofs/out/itil/knowledge-management/glossary/glossary.xlsx            sha256 6db1bc44fdb5bd3cc3c013808933dcd50871570b672dc908da7b2f26a90228ce  registered
shows: rows 17; first {"unit": "u0024", "verb": "mean", "sentence": "For purposes of this paragraph, the term \"search\" means to review, manually or by automated means, agency records for the purpose of locating those records which are respo
```

### Knowledge management / knowledge article  proven

```
shape: a procedure written out in order with its sources
instantiated on: ordered steps of 5 U.S.C. 552
-> ordered_steps of=usc5-552-doj (P2: z3 consistency proof; networkx forced order)
-> document name=knowledge_article, title=the statutory steps, in forced order, columns=["position", "step", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> knowledge article
proofs/out/itil/knowledge-management/knowledge-article/knowledge_article.docx sha256 3e85de966b34570b854d7bfa1fb570761e307b54efe6d151c84d00bddcbf8e9c  registered
shows: rows 24; first {"position": 1, "event": "usc5-552-doj:u0021:s00#e43", "step": "request", "phase": 1, "sentence": "(3)(A) Except with respect to the records made available under paragraphs (1) and (2) of this subsection, and except as p
```

### Knowledge management / knowledge index  proven

```
shape: what each source contains, counted by kind
instantiated on: facts of the three procedure documents
-> facts of=usc5-552-doj (P1: compiled_ai read, parse, extract, project, route, check, adjudicate)
-> group by=["predicate"], aggregates=[["count", "*", "facts"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=index_usc5_552 (openpyxl.Workbook.save)
-> knowledge index
proofs/out/itil/knowledge-management/knowledge-index/index_usc5_552.xlsx sha256 3cf8be4fccf39374be7554287dab8a8f0335c5bbe1b97a99b5206c9e52f50147  registered
shows: rows 7; first {"predicate": "agent", "facts": 283}
```

### Knowledge management / frequently discussed topics  proven

```
shape: the steps most often referred to in meetings
instantiated on: governance steps tagged in TSC minutes
-> tags of=nodejs-governance (P10/P26: clingo shared-word tagging)
-> filter where=[["tie", "eq", false]] (duckdb WHERE)
-> group by=["step_lemma"], aggregates=[["count", "*", "mentions"], ["distinct", "meeting", "meetings"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["mentions"], desc=true (duckdb ORDER BY)
-> workbook name=topics (openpyxl.Workbook.save)
-> frequently discussed topics
proofs/out/itil/knowledge-management/frequently-discussed-topics/topics.xlsx sha256 aa4c93ed15750e2a161242b98f1be49528a9e3cc7e05f68c6b09426638f44817  registered
shows: rows 9; first {"step_lemma": "be", "mentions": 21, "meetings": 7}
```

### Measurement and reporting / KPI report  proven

```
shape: the agreed indicators per group and period
instantiated on: receipt-phase cases per department
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=["department"], aggregates=[["count", "*", "cases"], ["avg", "duration_days", "mean_days"], ["median", "duration_days", "median_days"], ["sum", "late", "after_deadline"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=late_share, fn=ratio, num=after_deadline, den=cases (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> workbook name=kpi_report (openpyxl.Workbook.save)
-> KPI report
proofs/out/itil/measurement-and-reporting/kpi-report/kpi_report.xlsx   sha256 8a39162c0d8b0552e9c44232ab184f6e2e3451854a907223984bd2ee2c36fba0  registered
shows: rows 3; first {"department": "Customer contact", "cases": 29, "mean_days": 1.66, "median_days": 0.0, "after_deadline": 1.0, "late_share": 0.0345}
```

### Measurement and reporting / dashboard  proven

```
shape: the indicators as a chart page
instantiated on: receipt-phase events per activity
-> events (P6 rows as a relation)
-> group by=["activity"], aggregates=[["count", "*", "events"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> page name=dashboard, title=events per activity, kind=bar, x=activity, y=events (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> dashboard
proofs/out/itil/measurement-and-reporting/dashboard/dashboard.html     sha256 53306bfe359d052835628d9ba408164083be82326369b256bcfaa3c2e82b9c7a  registered
shows: rows 27; first {"activity": "Confirmation of receipt", "events": 1434}
```

### Measurement and reporting / scorecard  proven

```
shape: pass or fail per period against a rule
instantiated on: majority reachable per TSC meeting
-> decisions (P13: zen.ZenDecision.evaluate)
-> page name=scorecard, title=scorecard: could a vote carry at each meeting, kind=table (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> scorecard
proofs/out/itil/measurement-and-reporting/scorecard/scorecard.html     sha256 5296906fa43153bfd9065d5ea5fe7b65b05d1d45b7d38113e4c6cdf0a794e3cf  registered
shows: rows 8; first {"meeting": "tsc-2023-11-08", "present_voting": 6, "majority_reachable": false}
```

### Measurement and reporting / measurement plan  proven

```
shape: the clocks and durations the rules define
instantiated on: TIMEX3 durations found in 5 U.S.C. 552
-> anchors of=usc5-552-doj (P3: timexy)
-> filter where=[["timex3", "contains", "DURATION"]] (duckdb WHERE)
-> distinct fields=["span", "timex3", "sentence"] (duckdb DISTINCT)
-> workbook name=measurement_plan (openpyxl.Workbook.save)
-> measurement plan
proofs/out/itil/measurement-and-reporting/measurement-plan/measurement_plan.xlsx sha256 712f6783c15c46cb44bfed962630c2fc32d6dee8c305851179382861742c73bb  registered
shows: rows 17; first {"span": "one year", "timex3": "TIMEX3 type=\"DURATION\" value=\"P1Y\"", "sentence": "For records created on or after November 1, 1996, within one year after such date, each agency shall make such records available, incl
```

### Organizational change management / stakeholder map  proven

```
shape: who takes part, in what role, how often
instantiated on: the Present lists of eight TSC meetings
-> participants (markdown.markdown; lxml.html: the Present list of each meeting)
-> group by=["name", "role"], aggregates=[["count", "*", "meetings"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["meetings"], desc=true (duckdb ORDER BY)
-> workbook name=stakeholders (openpyxl.Workbook.save)
-> stakeholder map
proofs/out/itil/organizational-change-management/stakeholder-map/stakeholders.xlsx sha256 eb0333dd666d2a3efdd9c4e1ac822cd23599cf70f543590d18517d6023381919  registered
shows: rows 30; first {"name": "Richard Lau", "role": "voting member", "meetings": 8}
```

### Organizational change management / communication log  proven

```
shape: announcements and updates made to the group, by date
instantiated on: Announcements and update sections of the TSC minutes
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["section", "matches", "(?i)announce|update"]] (duckdb WHERE)
-> select fields=["meeting", "section", "item", "link"] (duckdb SELECT)
-> workbook name=communications (openpyxl.Workbook.save)
-> communication log
proofs/out/itil/organizational-change-management/communication-log/communications.xlsx sha256 0251e986176b09ed1184b8e63d09c023ac07c000cbb5aac99fdaa17950168c52  registered
shows: rows 20; first {"meeting": "tsc-2023-12-06", "section": "CPC and Board Meeting Updates", "item": "Michael - CPC discussion updates to the Travel fund, if you are interested please check out the issue or comment on updated proposal when
```

### Organizational change management / readiness assessment  proven

```
shape: whether the group can decide, per occasion
instantiated on: majority reachable per TSC meeting
-> decisions (P13: zen.ZenDecision.evaluate)
-> workbook name=readiness (openpyxl.Workbook.save)
-> readiness assessment
proofs/out/itil/organizational-change-management/readiness-assessment/readiness.xlsx sha256 3e9beefff35ce027cb13eb539e1b93736151dcd067da9396dd38f9f85bb8d121  registered
shows: rows 8; first {"meeting": "tsc-2023-11-08", "present_voting": 6, "majority_reachable": false}
```

### Organizational change management / training records  no real input

```
shape: who was trained in what, when
instantiated on: none
-> participants (markdown.markdown; lxml.html: the Present list of each meeting)
-> workbook name=training (openpyxl.Workbook.save)
-> training records
```

### Portfolio management / portfolio register  proven

```
shape: the items under consideration, with references
instantiated on: agenda items with links in the TSC minutes
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["links", "gt", 0]] (duckdb WHERE)
-> select fields=["meeting", "section", "item", "link"] (duckdb SELECT)
-> workbook name=portfolio (openpyxl.Workbook.save)
-> portfolio register
proofs/out/itil/portfolio-management/portfolio-register/portfolio.xlsx sha256 1ae5a206019ea1a57271b48069fe638e62378689c7c6c11a9027aa8a336ce857  registered
shows: rows 92; first {"meeting": "tsc-2023-11-08", "section": "Links", "item": "GitHub Issue: https://github.com/nodejs/TSC/issues/1468", "link": "https://github.com/nodejs/TSC/issues/1468"}
```

### Portfolio management / prioritization matrix  proven

```
shape: items ranked by how often they recur
instantiated on: links recurring across TSC meetings
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["link", "notnull", ""]] (duckdb WHERE)
-> group by=["link"], aggregates=[["distinct", "meeting", "meetings"], ["count", "*", "mentions"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["meetings", "mentions"], desc=true (duckdb ORDER BY)
-> workbook name=prioritization (openpyxl.Workbook.save)
-> prioritization matrix
proofs/out/itil/portfolio-management/prioritization-matrix/prioritization.xlsx sha256 4c84d0fe2fd393fe7c7ed51f73c135196207b75974deafcba6a0869dd4bde30c  registered
shows: rows 68; first {"link": "https://nodejs.org/calendar", "meetings": 8, "mentions": 8}
```

### Portfolio management / portfolio review  proven

```
shape: the items per section per meeting
instantiated on: TSC minutes sections
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> pivot row=section, col=meeting (duckdb GROUP BY, laid out as a matrix)
-> page name=portfolio_review, title=items per section per meeting, kind=table (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> portfolio review
proofs/out/itil/portfolio-management/portfolio-review/portfolio_review.html sha256 68fa5cfee2b9c81f9ed859491333ae9a926a115ea63da07072576263a8eb0ce6  registered
shows: rows 14; first {"section": "Announcements", "tsc-2023-11-08": 0, "tsc-2023-12-06": 0, "tsc-2024-01-10": 1, "tsc-2024-01-17": 1, "tsc-2024-02-07": 3, "tsc-2025-01-08": 1, "tsc-2025-02-05": 1, "tsc-2025-03-05": 1}
```

### Project management / project charter  proven

```
shape: purpose, responsibilities and rules of the undertaking
instantiated on: the Node.js TSC charter's obligations
-> required_actions of=nodejs-tsc-charter (P4: the obligatory facts with agent quotes)
-> document name=charter, title=charter: what the TSC must do, columns=["unit", "who", "action", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> project charter
proofs/out/itil/project-management/project-charter/charter.docx        sha256 35070667ee78f2329af2aa47a42d2612d2677735fd55e7ac75e77a85710c15a4  registered
shows: rows 13; first {"event": "nodejs-tsc-charter:u0002:s02#e12", "action": "open", "who": "", "sentence_id": "nodejs-tsc-charter:u0002:s02", "sentence": "Project proposals, timelines, and status must not merely be open, but also easily vis
```

### Project management / project schedule  proven

```
shape: work packages in phases
instantiated on: ordered steps of 5 U.S.C. 552 by phase
-> ordered_steps of=usc5-552-doj (P2: z3 consistency proof; networkx forced order)
-> select fields=["phase", "position", "step", "unit"] (duckdb SELECT)
-> workbook name=schedule (openpyxl.Workbook.save)
-> project schedule
proofs/out/itil/project-management/project-schedule/schedule.xlsx      sha256 a16532af1261ac68dd83600f2b1ddeb9fe73259e36a1dff7ef0e7113d950b778  registered
shows: rows 24; first {"phase": 1, "position": 1, "step": "request", "unit": "u0021"}
```

### Project management / status report  proven

```
shape: open, closed and late work per period
instantiated on: receipt-phase cases per month
-> cases (duckdb: one row per case from the event rows)
-> pivot row=month, col=outcome (duckdb GROUP BY, laid out as a matrix)
-> document name=status_report, title=status by month: open, by deadline, after deadline (docx.Document; add_table; docx.document.Document.save)
-> status report
proofs/out/itil/project-management/status-report/status_report.docx    sha256 234679fc31873865d4b770e63292375fed72bc2def1cf7d87deda72c237a3851  registered
shows: rows 16; first {"month": "2010-10", "after deadline": 10, "by deadline": 4, "open": 1}
```

### Project management / RAID log  proven

```
shape: risks, assumptions, issues and dependencies raised
instantiated on: TSC minutes sentences mentioning risk, block, issue, depend or concern
-> minutes_sentences (P7: compiled_ai parse of the minutes; one row per sentence with its event lemmas)
-> filter where=[["sentence", "matches", "(?i)\\b(risk|block|blocker|issue|depend|concern)"]] (duckdb WHERE)
-> select fields=["meeting", "sentence_id", "sentence"] (duckdb SELECT)
-> workbook name=raid_log (openpyxl.Workbook.save)
-> RAID log
proofs/out/itil/project-management/raid-log/raid_log.xlsx              sha256 f9c1b4c08d767e311663b6e135e187e2a32797a14051b688f1993d5f8c7578fc  registered
shows: rows 84; first {"meeting": "tsc-2023-11-08", "sentence_id": "tsc-2023-11-08:u0002:s02", "sentence": "<Not available, did not stream> * **GitHub Issue**: <https://github.com/nodejs/TSC/issues/1468>"}
```

### Relationship management / stakeholder register  proven

```
shape: parties, their standing and contact points
instantiated on: TSC voting members joined with meeting participants
-> participants (markdown.markdown; lxml.html: the Present list of each meeting)
-> group by=["handle"], aggregates=[["count", "*", "meetings_attended"], ["min", "name", "name"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> save_as name=attended (the relation kept under a name for a later join)
-> records of=tsc-voting-members (P6: csv.DictReader; pydantic.create_model)
-> join with=attended, keys=[["handle", "handle"]], how=left (duckdb JOIN)
-> workbook name=stakeholder_register (openpyxl.Workbook.save)
-> stakeholder register
proofs/out/itil/relationship-management/stakeholder-register/stakeholder_register.xlsx sha256 b5c7d92625b5f527c0fcec33647d1ed470c5643b9e9e53131df8af27d478e69a  registered
shows: rows 18; first {"handle": "BridgeAR", "name": "Ruben Bridgewater", "meetings_attended": 4}
```

### Relationship management / decision log  proven

```
shape: decisions taken with the meeting where they were taken
instantiated on: TSC minutes sentences whose actions include agree, approve, vote, decide, resolve or consensus
-> minutes_sentences (P7: compiled_ai parse of the minutes; one row per sentence with its event lemmas)
-> filter where=[["lemmas", "matches", "\\b(agree|approve|vote|decide|resolve|consensus|object)\\b"]] (duckdb WHERE)
-> select fields=["meeting", "sentence_id", "lemmas", "sentence"] (duckdb SELECT)
-> workbook name=decision_log (openpyxl.Workbook.save)
-> decision log
proofs/out/itil/relationship-management/decision-log/decision_log.xlsx sha256 063f5fcb396353d97a5979e1b8212cf1f80e5b61bc09d97e5640fe4c8cd5a78d  registered
shows: rows 14; first {"meeting": "tsc-2023-12-06", "sentence_id": "tsc-2023-12-06:u0011:s00", "lemmas": "agree discuss do follow get have make open promote runtime say suggest turn", "sentence": "* lib: promote process.binding/_tickCallback 
```

### Relationship management / satisfaction report  no real input

```
shape: satisfaction measured per party
instantiated on: none
-> participants (markdown.markdown; lxml.html: the Present list of each meeting)
-> workbook name=satisfaction (openpyxl.Workbook.save)
-> satisfaction report
```

### Risk management / risk register  proven

```
shape: open items exposed beyond their group's norm
instantiated on: open receipt-phase cases against their department's mean duration
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["avg", "duration_days", "mean_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> save_as name=means (the relation kept under a name for a later join)
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "open"]] (duckdb WHERE)
-> join with=means, keys=[["department", "department"]] (duckdb JOIN)
-> derive field=exposure, fn=ratio, num=days_since_last_event, den=mean_days (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> sort by=["exposure"], desc=true (duckdb ORDER BY)
-> workbook name=risk_register (openpyxl.Workbook.save)
-> risk register
proofs/out/itil/risk-management/risk-register/risk_register.xlsx       sha256 6870a2aa4290dba471de3fab3d07aba5fc7dd7750290df446d016678dcecfe9d  registered
shows: rows 105; first {"case": "case-416", "department": "General", "channel": "Internet", "responsible": "Resource26", "start": "2010-10-20 10:56:58.348000+00:00", "end": "2010-11-08 13:07:42.360000+00:00", "events": 6, "duration_days": 19.0
```

### Risk management / risk matrix  proven

```
shape: likelihood against impact per group
instantiated on: receipt-phase departments, share late against mean duration
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=["department"], aggregates=[["count", "*", "cases"], ["sum", "late", "late_cases"], ["avg", "duration_days", "impact_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=likelihood, fn=ratio, num=late_cases, den=cases (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> page name=risk_matrix, title=likelihood of lateness against mean duration, kind=scatter, x=likelihood, y=impact_days, size=cases (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> risk matrix
proofs/out/itil/risk-management/risk-matrix/risk_matrix.html           sha256 89bd50c2374beed820a734e6aa4fb5e5d3a8a0203de107dc2dcc1c71e091ee0d  registered
shows: rows 3; first {"department": "Customer contact", "cases": 29, "late_cases": 1.0, "impact_days": 1.66, "likelihood": 0.0345}
```

### Risk management / risk report  proven

```
shape: the register summarized for review
instantiated on: receipt-phase departments
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=["department", "channel"], aggregates=[["count", "*", "cases"], ["sum", "late", "late_cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=late_share, fn=ratio, num=late_cases, den=cases (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> document name=risk_report, title=lateness by department and channel (docx.Document; add_table; docx.document.Document.save)
-> risk report
proofs/out/itil/risk-management/risk-report/risk_report.docx           sha256 2cf5fbb078f8b0f8f1b57ce26a1bc00e7118fe8da60aa505bf5674895a8904d5  registered
shows: rows 10; first {"department": "Customer contact", "channel": "Desk", "cases": 3, "late_cases": 0.0, "late_share": 0.0}
```

### Service financial management / fee rules register  proven

```
shape: the rules under which charges are made
instantiated on: fee provisions of 5 U.S.C. 552
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> filter where=[["sentence", "matches", "(?i)\\bfee"]] (duckdb WHERE)
-> select fields=["unit", "who", "action", "sentence"] (duckdb SELECT)
-> workbook name=fee_rules (openpyxl.Workbook.save)
-> fee rules register
proofs/out/itil/service-financial-management/fee-rules-register/fee_rules.xlsx sha256 10c522669ac6b9b8dbe988c694e8dd6ffd6d8aa3e95bfe35e4c0e78209543ddf  registered
shows: rows 14; first {"unit": "u0028", "who": "agency shall promulgate", "action": "promulgate", "sentence": "(4)(A)(i) In order to carry out the provisions of this section, each agency shall promulgate regulations, pursuant to notice and re
```

### Service financial management / budget  no real input

```
shape: planned spend per period and cost centre
instantiated on: none
-> cases (duckdb: one row per case from the event rows)
-> workbook name=budget (openpyxl.Workbook.save)
-> budget
```

### Service financial management / cost model  no real input

```
shape: cost per unit of service
instantiated on: none
-> cases (duckdb: one row per case from the event rows)
-> workbook name=cost_model (openpyxl.Workbook.save)
-> cost model
```

### Service financial management / chargeback report  no real input

```
shape: charges per consumer
instantiated on: none
-> cases (duckdb: one row per case from the event rows)
-> workbook name=chargeback (openpyxl.Workbook.save)
-> chargeback report
```

### Strategy management / objectives register  proven

```
shape: the standing commitments of the organization
instantiated on: obligations of the Node.js governance document
-> required_actions of=nodejs-governance (P4: the obligatory facts with agent quotes)
-> select fields=["unit", "who", "action", "sentence"] (duckdb SELECT)
-> workbook name=objectives (openpyxl.Workbook.save)
-> objectives register
proofs/out/itil/strategy-management/objectives-register/objectives.xlsx sha256 8f2d87098ec744d9b124efbb661b2f3350946be88491286eaead77acbcf39d32  registered
shows: rows 2; first {"unit": "u0013", "who": "collaborators must approve", "action": "approve", "sentence": "Two collaborators must approve a pull request before the pull request can land."}
```

### Strategy management / strategic roadmap  proven

```
shape: phases and steps
instantiated on: ordered steps of the Node.js governance document
-> ordered_steps of=nodejs-governance (P2: z3 consistency proof; networkx forced order)
-> group by=["phase"], aggregates=[["count", "*", "steps"], ["list", "step", "steps_in_phase"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=strategic_roadmap (openpyxl.Workbook.save)
-> strategic roadmap
proofs/out/itil/strategy-management/strategic-roadmap/strategic_roadmap.xlsx sha256 7be2e9b3d390c513389bb34dedf68277b92ba104286a95c831a170b60141b71b  registered
shows: rows 2; first {"phase": 1, "steps": 9, "steps_in_phase": "address, collaborator, hour, meeting, onboarded, require, share, time, week"}
```

### Strategy management / strategy review  proven

```
shape: what the leadership discussed, by topic
instantiated on: charter actions tagged in TSC minutes
-> tags of=nodejs-tsc-charter (P10/P26: clingo shared-word tagging)
-> filter where=[["tie", "eq", false]] (duckdb WHERE)
-> pivot row=step_lemma, col=meeting (duckdb GROUP BY, laid out as a matrix)
-> workbook name=strategy_review (openpyxl.Workbook.save)
-> strategy review
proofs/out/itil/strategy-management/strategy-review/strategy_review.xlsx sha256 608a888d96c75ffe5949e36c7d86a258245a41802c60d11f38553fe672877655  registered
shows: rows 9; first {"step_lemma": "approve", "tsc-2023-11-08": 0, "tsc-2023-12-06": 0, "tsc-2024-01-10": 1, "tsc-2024-01-17": 0, "tsc-2024-02-07": 0, "tsc-2025-01-08": 0, "tsc-2025-02-05": 0, "tsc-2025-03-05": 0}
```

### Supplier management / third-party obligations register  proven

```
shape: obligations toward or from external parties
instantiated on: TSC charter sentences naming the CPC or the Foundation
-> required_actions of=nodejs-tsc-charter (P4: the obligatory facts with agent quotes)
-> filter where=[["sentence", "matches", "CPC|Foundation|Board"]] (duckdb WHERE)
-> select fields=["unit", "who", "action", "sentence"] (duckdb SELECT)
-> workbook name=third_party_obligations (openpyxl.Workbook.save)
-> third-party obligations register
proofs/out/itil/supplier-management/third-party-obligations-register/third_party_obligations.xlsx sha256 37aab9e3c82159358794a010fd17c90da8aacbe5ab5a6b3ee50cf213952b98ad  registered
shows: rows 2; first {"unit": "u0026", "who": "TSC shall hold", "action": "hold", "sentence": "The TSC shall hold annual elections to select a TSC Chairperson and voting CPC member; there are no limits on the number of terms a TSC Chairperso
```

### Supplier management / supplier register  proven

```
shape: external components relied on, with their license
instantiated on: Node.js maintained dependencies joined to the LICENSE register
-> licenses (re over the Node.js LICENSE file: one row per bundled component)
-> derive field=key, fn=upper, of=component (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> save_as name=lic (the relation kept under a name for a later join)
-> dependencies (re over maintaining-dependencies.md: one row per maintained dependency)
-> derive field=key, fn=upper, of=dependency (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> join with=lic, keys=[["key", "key"]], how=left (duckdb JOIN)
-> select fields=["dependency", "component", "location", "license_heading"] (duckdb SELECT)
-> workbook name=suppliers (openpyxl.Workbook.save)
-> supplier register
proofs/out/itil/supplier-management/supplier-register/suppliers.xlsx   sha256 8b3c044d6c55fb03ef769721906c112980ab0205690ff5273600bc0409f5d0f2  registered
shows: rows 31; first {"dependency": "acorn", "component": "Acorn", "location": "deps/acorn", "license_heading": "MIT License"}
```

### Supplier management / supplier performance report  no real input

```
shape: delivered against agreed, per supplier
instantiated on: none
-> events (P6 rows as a relation)
-> workbook name=supplier_performance (openpyxl.Workbook.save)
-> supplier performance report
```

### Workforce and talent management / roles and responsibilities  proven

```
shape: who must do what
instantiated on: agents and required actions of the TSC charter
-> who_must_what of=nodejs-tsc-charter (P44: duckdb count per (agent, action))
-> workbook name=roles (openpyxl.Workbook.save)
-> roles and responsibilities
proofs/out/itil/workforce-and-talent-management/roles-and-responsibilities/roles.xlsx sha256 5960c68351c7adacc8a9db1dc003bc1dbda335eca3210423ab60b11ebfca8f57  registered
shows: rows 5; first {"who": "collaborators shall operate", "action": "operate", "count": 1}
```

### Workforce and talent management / attendance report  proven

```
shape: participation per occasion
instantiated on: voting members present at eight TSC meetings
-> attendance (P13: voting members present per meeting)
-> page name=attendance, title=voting members present per meeting, kind=bar, x=meeting, y=present_voting (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> attendance report
proofs/out/itil/workforce-and-talent-management/attendance-report/attendance.html sha256 9e8d4ce0789939b9405a0a6ae2d966f10feaefe10a8d3dc2e4500beae20ee435  registered
shows: rows 8; first {"meeting": "tsc-2023-11-08", "present_voting": 6, "present": 6}
```

### Workforce and talent management / workload report  proven

```
shape: work handled per person
instantiated on: receipt-phase events per resource
-> events (P6 rows as a relation)
-> group by=["resource"], aggregates=[["count", "*", "events"], ["distinct", "case", "cases"], ["distinct", "activity", "activities"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["events"], desc=true (duckdb ORDER BY)
-> workbook name=workload (openpyxl.Workbook.save)
-> workload report
proofs/out/itil/workforce-and-talent-management/workload-report/workload.xlsx sha256 f299c0a1684cf8745db1c0c97e021de10309c45f65eebe380e94227cdbe703e9  registered
shows: rows 48; first {"resource": "Resource01", "events": 1228, "cases": 243, "activities": 14}
```

### Workforce and talent management / skills matrix  proven

```
shape: people against skills
instantiated on: receipt-phase resources against the activities they performed
-> events (P6 rows as a relation)
-> pivot row=resource, col=activity (duckdb GROUP BY, laid out as a matrix)
-> workbook name=skills_matrix (openpyxl.Workbook.save)
-> skills matrix
proofs/out/itil/workforce-and-talent-management/skills-matrix/skills_matrix.xlsx sha256 d17309c1815087e6898a7832df4043a42c218a6d173fa585879d434e4c915ea3  registered
shows: rows 48; first {"resource": "Resource01", "Confirmation of receipt": 195, "T02 Check confirmation of receipt": 209, "T03 Adjust confirmation of receipt": 1, "T04 Determine confirmation of receipt": 184, "T05 Print and send confirmation
```

### Availability management / availability requirements  proven

```
shape: the time limits the rules impose
instantiated on: durations in 5 U.S.C. 552 with their sentences
-> anchors of=usc5-552-doj (P3: timexy)
-> filter where=[["timex3", "contains", "DURATION"]] (duckdb WHERE)
-> select fields=["span", "timex3", "sentence"] (duckdb SELECT)
-> distinct (duckdb DISTINCT)
-> workbook name=availability_requirements (openpyxl.Workbook.save)
-> availability requirements
proofs/out/itil/availability-management/availability-requirements/availability_requirements.xlsx sha256 712f6783c15c46cb44bfed962630c2fc32d6dee8c305851179382861742c73bb  registered
shows: rows 17; first {"span": "one year", "timex3": "TIMEX3 type=\"DURATION\" value=\"P1Y\"", "sentence": "For records created on or after November 1, 1996, within one year after such date, each agency shall make such records available, incl
```

### Availability management / availability report  proven

```
shape: achieved availability per period
instantiated on: share of voting members available per TSC meeting
-> decisions (P13: zen.ZenDecision.evaluate)
-> derive field=availability, fn=ratio, num=present_voting, den=present_voting (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> select fields=["meeting", "present_voting", "majority_reachable"] (duckdb SELECT)
-> workbook name=availability_report (openpyxl.Workbook.save)
-> availability report
proofs/out/itil/availability-management/availability-report/availability_report.xlsx sha256 3e9beefff35ce027cb13eb539e1b93736151dcd067da9396dd38f9f85bb8d121  registered
shows: rows 8; first {"meeting": "tsc-2023-11-08", "present_voting": 6, "majority_reachable": false}
```

### Availability management / availability plan  proven

```
shape: the windows in which each service line is supported
instantiated on: Node.js release lines with start, LTS, maintenance and end dates
-> release_schedule (json.loads of nodejs/Release schedule.json)
-> derive field=supported_days, fn=days_between, a=start, b=end (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> workbook name=availability_plan (openpyxl.Workbook.save)
-> availability plan
proofs/out/itil/availability-management/availability-plan/availability_plan.xlsx sha256 321680589d2b9990de07e8086547537471b38d2004dd2f07f49cda65b00824a0  registered
shows: rows 27; first {"version": "v0.8", "codename": "", "start": "2012-06-25", "lts": "", "maintenance": "", "end": "2014-07-31", "supported_days": 766.0}
```

### Business analysis / requirements catalogue  proven

```
shape: every requirement with its source and owner
instantiated on: obligations of 5 U.S.C. 552
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> select fields=["unit", "who", "action", "sentence"] (duckdb SELECT)
-> workbook name=requirements (openpyxl.Workbook.save)
-> requirements catalogue
proofs/out/itil/business-analysis/requirements-catalogue/requirements.xlsx sha256 6e6b1b61aded21bc43e1631a5c6337d00176a534b6503e98f9131ac45e1f9774  registered
shows: rows 122; first {"unit": "u0001", "who": "agency shall make", "action": "make", "sentence": "(a) Each agency shall make available to the public information as follows:"}
```

### Business analysis / as-is process model  proven

```
shape: the process as performed
instantiated on: receipt-phase directly-follows edges
-> dfg (P23: pm4py.discover_dfg)
-> workbook name=as_is_process (openpyxl.Workbook.save)
-> as-is process model
proofs/out/itil/business-analysis/as-is-process-model/as_is_process.xlsx sha256 18d955657444fd3eb9ebde649272460f6daa31d5bad719da33b7b4731c342909  registered
shows: rows 99; first {"from": "T04 Determine confirmation of receipt", "to": "T05 Print and send confirmation of receipt", "count": 1177}
```

### Business analysis / gap analysis  proven

```
shape: requirements present in one source and absent in another
instantiated on: required actions of the TSC charter against the governance document
-> required_actions of=nodejs-tsc-charter (P4: the obligatory facts with agent quotes)
-> select fields=["action"] (duckdb SELECT)
-> distinct (duckdb DISTINCT)
-> save_as name=charter (the relation kept under a name for a later join)
-> required_actions of=nodejs-governance (P4: the obligatory facts with agent quotes)
-> select fields=["action"] (duckdb SELECT)
-> distinct (duckdb DISTINCT)
-> join with=charter, keys=[["action", "action"]], how=left (duckdb JOIN)
-> workbook name=gap_analysis (openpyxl.Workbook.save)
-> gap analysis
proofs/out/itil/business-analysis/gap-analysis/gap_analysis.xlsx       sha256 79b1a36ad7ee69a986b7662f16eb9ef20fa1dee32026e7449b573849cb0d9168  registered
shows: rows 2; first {"action": "approve"}
```

### Business analysis / acceptance criteria  proven

```
shape: each required action with its clock
instantiated on: 5 U.S.C. 552 obligations joined to durations in the same sentence
-> anchors of=usc5-552-doj (P3: timexy)
-> filter where=[["timex3", "contains", "DURATION"]] (duckdb WHERE)
-> save_as name=clocks (the relation kept under a name for a later join)
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> join with=clocks, keys=[["sentence_id", "sentence_id"]] (duckdb JOIN)
-> select fields=["unit", "who", "action", "span", "timex3", "sentence"] (duckdb SELECT)
-> workbook name=acceptance_criteria (openpyxl.Workbook.save)
-> acceptance criteria
proofs/out/itil/business-analysis/acceptance-criteria/acceptance_criteria.xlsx sha256 06697e82453161bb8a0c5a6811e58c5e92867933cde32018207f21cadbbf8a79  registered
shows: rows 6; first {"unit": "u0018", "who": "agency shall make", "action": "make", "span": "one year", "timex3": "TIMEX3 type=\"DURATION\" value=\"P1Y\"", "sentence": "For records created on or after November 1, 1996, within one year after
```

### Capacity and performance management / capacity plan  proven

```
shape: demand per period and group
instantiated on: receipt-phase events per month and department
-> events (P6 rows as a relation)
-> derive field=month, fn=month, of=ts (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> pivot row=month, col=department (duckdb GROUP BY, laid out as a matrix)
-> workbook name=capacity_plan (openpyxl.Workbook.save)
-> capacity plan
proofs/out/itil/capacity-and-performance-management/capacity-plan/capacity_plan.xlsx sha256 fab180bfb9e59e2b5f5d547ca78cd2690d068327e616cf76abd4ee21d85b7a74  registered
shows: rows 16; first {"month": "2010-10", "Customer contact": 0, "Experts": 26, "General": 55}
```

### Capacity and performance management / performance report  proven

```
shape: duration statistics per group
instantiated on: receipt-phase cases per department
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["count", "*", "cases"], ["min", "duration_days", "min_days"], ["median", "duration_days", "median_days"], ["avg", "duration_days", "mean_days"], ["max", "duration_days", "max_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=performance_report (openpyxl.Workbook.save)
-> performance report
proofs/out/itil/capacity-and-performance-management/performance-report/performance_report.xlsx sha256 1b6af16c4b4fe3ff6398bac3c904b7933f066a4fc08b04a0e70f7ea0d13c6364  registered
shows: rows 3; first {"department": "Customer contact", "cases": 29, "min_days": 0.0, "median_days": 0.0, "mean_days": 1.66, "max_days": 12.25}
```

### Capacity and performance management / demand trend  proven

```
shape: cases started per month
instantiated on: receipt-phase cases
-> cases (duckdb: one row per case from the event rows)
-> group by=["month"], aggregates=[["count", "*", "cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> page name=demand, title=cases started per month, kind=line, x=month, y=cases (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> demand trend
proofs/out/itil/capacity-and-performance-management/demand-trend/demand.html sha256 655c52141c02f2c6934b190413eecd58177652f4795241ae5eeca3c1cdb8158c  registered
shows: rows 16; first {"month": "2010-10", "cases": 15}
```

### Capacity and performance management / bottleneck analysis  proven

```
shape: the transitions with the longest waits
instantiated on: receipt-phase directly-follows edges with waiting times
-> bottlenecks (P46: duckdb join of edges and waiting time)
-> workbook name=bottlenecks (openpyxl.Workbook.save)
-> bottleneck analysis
proofs/out/itil/capacity-and-performance-management/bottleneck-analysis/bottlenecks.xlsx sha256 bfdf9be9a88d4c5b0a7d7e2758e87d313b654b907eb7a68da0308a9ba4dfcc25  registered
shows: rows 25; first {"from": "T05 Print and send confirmation of receipt", "to": "T13 Adjust document X request unlicensed", "cases": 2, "mean_hours_waiting_into_to": 205.36}
```

### Change enablement / change request record  proven

```
shape: proposed changes with their reference
instantiated on: pull requests referenced in TSC minutes
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["link", "contains", "/pull/"]] (duckdb WHERE)
-> select fields=["meeting", "section", "item", "link"] (duckdb SELECT)
-> workbook name=change_requests (openpyxl.Workbook.save)
-> change request record
proofs/out/itil/change-enablement/change-request-record/change_requests.xlsx sha256 ba38755eed41043d4f39eed30418cd52107a2ac30541da4d6ba9d87ae7380f9d  registered
shows: rows 20; first {"meeting": "tsc-2023-11-08", "section": "nodejs/node", "item": "doc: move deprecated utils to runtime deprecation #50488", "link": "https://github.com/nodejs/node/pull/50488"}
```

### Change enablement / change model  proven

```
shape: the standard steps of a change in forced order
instantiated on: forced precedence of the Node.js governance document
-> forced_edges of=nodejs-governance (P2: networkx.transitive_reduction)
-> bpmn name=change_model (pm4py.objects.bpmn.obj.BPMN with parallel gateways; bpmn exporter; canonical ids)
-> change model
proofs/out/itil/change-enablement/change-model/change_model.bpmn       sha256 9c83f8172d8fdb4540f84c74140c665ad49f564a9cf2e792fb6eede61449927f  registered
shows: rows 9; first {"before": "nodejs-governance:u0020:s00#e25", "after": "nodejs-governance:u0020:s00#e19", "before_step": "collaborator", "after_step": "more"}
```

### Change enablement / change schedule  proven

```
shape: changes by date
instantiated on: pull requests per TSC meeting date
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["link", "contains", "/pull/"]] (duckdb WHERE)
-> group by=["meeting"], aggregates=[["count", "*", "changes"], ["list", "link", "links"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=change_schedule (openpyxl.Workbook.save)
-> change schedule
proofs/out/itil/change-enablement/change-schedule/change_schedule.xlsx sha256 a7e70fe13108f94c6844c44bc870f1e533df9a94dc99964762a8cc4963e78682  registered
shows: rows 6; first {"meeting": "tsc-2023-11-08", "changes": 5, "links": "https://github.com/nodejs/node/pull/49867, https://github.com/nodejs/node/pull/50169, https://github.com/nodejs/node/pull/50250, https://github.com/nodejs/node/pull/5
```

### Change enablement / change authority matrix  proven

```
shape: who must authorize what
instantiated on: agents and required actions of the TSC charter
-> who_must_what of=nodejs-tsc-charter (P44: duckdb count per (agent, action))
-> pivot row=who, col=action, value=count, fn=sum (duckdb GROUP BY, laid out as a matrix)
-> workbook name=authority_matrix (openpyxl.Workbook.save)
-> change authority matrix
proofs/out/itil/change-enablement/change-authority-matrix/authority_matrix.xlsx sha256 c5f21da356efff6344a93a997e853da976ec3bd76e1efc56bf006d8100541344  registered
shows: rows 5; first {"who": "collaborators shall operate", "establish": 0, "have": 0, "hold": 0, "meet": 0, "operate": 1.0}
```

### Change enablement / post-implementation review  proven

```
shape: whether performed changes matched the model
instantiated on: receipt-phase conformance per variant
-> conformance (P9: pm4py.conformance_diagnostics_token_based_replay)
-> derive field=fit, fn=contains, of=is_fit, value=true (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=[], aggregates=[["count", "*", "cases"], ["sum", "fit", "fit_cases"], ["avg", "fitness", "mean_fitness"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=post_implementation_review (openpyxl.Workbook.save)
-> post-implementation review
proofs/out/itil/change-enablement/post-implementation-review/post_implementation_review.xlsx sha256 e8ae029d962f6dff01922e51869356f3a0ede233bb4a92d91ede3bdc1c4f0f38  registered
shows: rows 1; first {"cases": 1434, "fit_cases": 1425.0, "mean_fitness": 1.0}
```

### Incident management / incident record  proven

```
shape: one row per case with category, status, timestamps and outcome
instantiated on: receipt-phase cases
-> cases (duckdb: one row per case from the event rows)
-> select fields=["case", "department", "channel", "responsible", "start", "end", "events", "duration_days", "outcome"] (duckdb SELECT)
-> workbook name=case_records (openpyxl.Workbook.save)
-> incident record
proofs/out/itil/incident-management/incident-record/case_records.xlsx  sha256 21d9cb2b5cc71589fceb9e208a456eb038993dc64db91f8c5f8f985f8f63478f  registered
shows: rows 1434; first {"case": "case-10011", "department": "General", "channel": "Internet", "responsible": "Resource21", "start": "2011-10-11 11:45:40.276000+00:00", "end": "2011-11-24 14:37:16.553000+00:00", "events": 4, "duration_days": 44
```

### Incident management / incident model  proven

```
shape: the standard sequence of steps
instantiated on: the most common receipt-phase variant
-> variants (P36: pm4py.get_variants_as_tuples)
-> limit n=5 (duckdb LIMIT)
-> workbook name=models (openpyxl.Workbook.save)
-> incident model
proofs/out/itil/incident-management/incident-model/models.xlsx         sha256 e71b4a1a2c43329fb68ecf5bfdea7bf0d6dc0f31b958d5448b0c40e54f65b77c  registered
shows: rows 5; first {"rank": 1, "cases": 713, "length": 6, "variant": "Confirmation of receipt -> T02 Check confirmation of receipt -> T04 Determine confirmation of receipt -> T05 Print and send confirmation of receipt -> T06 Determine nece
```

### Incident management / major incident report  proven

```
shape: the longest cases with their timeline
instantiated on: the ten longest receipt-phase cases
-> cases (duckdb: one row per case from the event rows)
-> sort by=["duration_days"], desc=true (duckdb ORDER BY)
-> limit n=10 (duckdb LIMIT)
-> document name=major_cases, title=the ten longest cases, columns=["case", "department", "channel", "start", "end", "duration_days", "outcome"] (docx.Document; add_table; docx.document.Document.save)
-> major incident report
proofs/out/itil/incident-management/major-incident-report/major_cases.docx sha256 933867beef3f8615c36f580658985f768e5fcd2036298983c9d138e5014c3eda  registered
shows: rows 10; first {"case": "case-4601", "department": "General", "channel": "Internet", "responsible": "Resource12", "start": "2010-12-14 13:36:38.009000+00:00", "end": "2011-09-16 09:45:39.533000+00:00", "events": 6, "duration_days": 275
```

### Incident management / incident status report  proven

```
shape: open work per group
instantiated on: open receipt-phase cases per department
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "open"]] (duckdb WHERE)
-> group by=["department"], aggregates=[["count", "*", "open_cases"], ["avg", "days_since_last_event", "mean_days_idle"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=status (openpyxl.Workbook.save)
-> incident status report
proofs/out/itil/incident-management/incident-status-report/status.xlsx sha256 2f67f489cd263e6644402e28a856624e808c69173b83ffee3bf334a96111520f  registered
shows: rows 1; first {"department": "General", "open_cases": 105, "mean_days_idle": 69.47}
```

### Incident management / deadline breach list  proven

```
shape: cases that ended after their deadline
instantiated on: receipt-phase cases
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "after deadline"]] (duckdb WHERE)
-> select fields=["case", "department", "channel", "deadline", "enddate", "duration_days"] (duckdb SELECT)
-> workbook name=breaches (openpyxl.Workbook.save)
-> deadline breach list
proofs/out/itil/incident-management/deadline-breach-list/breaches.xlsx sha256 de3fec19361ddd4d0cf4ab1dbaa3f97317be96bc765ad6a91cd82d7dd5ecb7e8  registered
shows: rows 377; first {"case": "case-10028", "department": "General", "channel": "Internet", "deadline": "2011-12-05 01:06:40+01:00", "enddate": "2011-12-05 15:34:49.174000+01:00", "duration_days": 0.01}
```

### Incident management / escalation matrix  proven

```
shape: who hands work to whom
instantiated on: receipt-phase handover-of-work network
-> handover (pm4py.discover_handover_of_work_network)
-> limit n=200 (duckdb LIMIT)
-> workbook name=escalation (openpyxl.Workbook.save)
-> escalation matrix
proofs/out/itil/incident-management/escalation-matrix/escalation.xlsx  sha256 68e49809f003ca00200d70a43e49d792ef16320dffd3a93a81d2d44c21d3e095  registered
shows: rows 200; first {"from": "Resource01", "to": "Resource01", "value": 0.136497}
```

### IT asset management / asset register  proven

```
shape: the assets in use with counts of use
instantiated on: receipt-phase resources and groups
-> events (P6 rows as a relation)
-> group by=["group", "resource"], aggregates=[["count", "*", "events"], ["min", "ts", "first_seen"], ["max", "ts", "last_seen"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=asset_register (openpyxl.Workbook.save)
-> asset register
proofs/out/itil/it-asset-management/asset-register/asset_register.xlsx sha256 57cee043168cbdcdd529da658da9f0856ed485ae428c38acbba5d013419a47f6  registered
shows: rows 215; first {"group": "EMPTY", "resource": "Resource01", "events": 193, "first_seen": "2010-12-10 12:09:40.789000+01:00", "last_seen": "2011-12-28 15:36:23.336000+01:00"}
```

### IT asset management / lifecycle records  proven

```
shape: first and last use per asset
instantiated on: receipt-phase resources
-> events (P6 rows as a relation)
-> group by=["resource"], aggregates=[["min", "ts", "first_seen"], ["max", "ts", "last_seen"], ["count", "*", "events"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=active_days, fn=days_between, a=first_seen, b=last_seen (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> workbook name=lifecycle (openpyxl.Workbook.save)
-> lifecycle records
proofs/out/itil/it-asset-management/lifecycle-records/lifecycle.xlsx   sha256 9917d89c410763ad50ec5e22be2226de7b786d18f6edbf1164e18f13ac839fce  registered
shows: rows 48; first {"resource": "Resource01", "first_seen": "2010-11-02 12:42:19.582000+01:00", "last_seen": "2011-12-28 15:44:34.115000+01:00", "events": 1228, "active_days": 421.13}
```

### IT asset management / audit reconciliation  proven

```
shape: forward records against what was read back from the deliverables
instantiated on: the reverse proofs of this file
-> roundtrips (P19, P30, P40, P50: reverse proofs and csv_diff.compare)
-> workbook name=reconciliation (openpyxl.Workbook.save)
-> audit reconciliation
proofs/out/itil/it-asset-management/audit-reconciliation/reconciliation.xlsx sha256 6e49e3dabd08905d28f3db4a1b676853ddf59176de68a1eb014200f5af8a32e5  registered
shows: rows 4; first {"proof": "P19", "label": "deck", "match": true, "changed": 0}
```

### IT asset management / license compliance report  proven

```
shape: every bundled component with its license
instantiated on: the Node.js LICENSE file, one section per bundled dependency
-> licenses (re over the Node.js LICENSE file: one row per bundled component)
-> workbook name=licenses (openpyxl.Workbook.save)
-> license compliance report
proofs/out/itil/it-asset-management/license-compliance-report/licenses.xlsx sha256 52b7dbe497fec705d1367adf6f4cb119d779757e16f965a7c51f130ea794d96b  registered
shows: rows 43; first {"component": "Acorn", "location": "deps/acorn", "license_heading": "MIT License", "license_lines": 24}
```

### Monitoring and event management / event records  proven

```
shape: every event with case, activity, time and resource
instantiated on: receipt-phase events
-> events (P6 rows as a relation)
-> select fields=["case", "activity", "ts", "resource", "department", "channel"] (duckdb SELECT)
-> workbook name=event_records (openpyxl.Workbook.save)
-> event records
proofs/out/itil/monitoring-and-event-management/event-records/event_records.xlsx sha256 693c9ee65f6f95513f807da32af5b541423750e7cf30bb5bdebc2271bb3cbf91  registered
shows: rows 8577; first {"case": "case-10011", "activity": "Confirmation of receipt", "ts": "2011-10-11 13:45:40.276000+02:00", "resource": "Resource21", "department": "General", "channel": "Internet"}
```

### Monitoring and event management / monitoring thresholds  proven

```
shape: the threshold per group beyond which an alert is raised
instantiated on: receipt-phase department mean durations
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["avg", "duration_days", "threshold_days"], ["count", "*", "cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=thresholds (openpyxl.Workbook.save)
-> monitoring thresholds
proofs/out/itil/monitoring-and-event-management/monitoring-thresholds/thresholds.xlsx sha256 90e04cdcfd6b51aedf7977745aaae77d11d6e04437b86069181d02b3f9d332df  registered
shows: rows 3; first {"department": "Customer contact", "threshold_days": 1.66, "cases": 29}
```

### Monitoring and event management / alert list  proven

```
shape: open items past threshold, decided by a rule
instantiated on: open receipt-phase cases against department means
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["avg", "duration_days", "threshold_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> save_as name=thresholds (the relation kept under a name for a later join)
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "open"]] (duckdb WHERE)
-> join with=thresholds, keys=[["department", "department"]] (duckdb JOIN)
-> derive field=over, fn=ratio, num=days_since_last_event, den=threshold_days (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> decision_table name=alert, inputs=["over"], outputs=["alert"] (jinja2 -> GoRules JDM; zen.ZenEngine.create_decision; zen.ZenDecision.evaluate)
-> workbook name=alerts (openpyxl.Workbook.save)
-> alert list
proofs/out/itil/monitoring-and-event-management/alert-list/policy.jdm.json sha256 9835ab6f3625f14d66147c79c28d997b9ac1c310a7149f095b956eda0abab2c0  registered
proofs/out/itil/monitoring-and-event-management/alert-list/alerts.xlsx sha256 5c51e871f2df40a50fa46d6b0c5b64ced009098dcfd4d8bb8d4abcfa39be4799  registered
shows: rows 105; first {"case": "case-10011", "department": "General", "channel": "Internet", "responsible": "Resource21", "start": "2011-10-11 11:45:40.276000+00:00", "end": "2011-11-24 14:37:16.553000+00:00", "events": 4, "duration_days": 44
```

### Monitoring and event management / event correlation  proven

```
shape: which events follow which, with counts
instantiated on: receipt-phase directly-follows edges
-> dfg (P23: pm4py.discover_dfg)
-> workbook name=correlation (openpyxl.Workbook.save)
-> event correlation
proofs/out/itil/monitoring-and-event-management/event-correlation/correlation.xlsx sha256 18d955657444fd3eb9ebde649272460f6daa31d5bad719da33b7b4731c342909  registered
shows: rows 99; first {"from": "T04 Determine confirmation of receipt", "to": "T05 Print and send confirmation of receipt", "count": 1177}
```

### Problem management / problem record  proven

```
shape: recurring failures grouped by cause candidate
instantiated on: late receipt-phase cases per department and channel
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "after deadline"]] (duckdb WHERE)
-> group by=["department", "channel"], aggregates=[["count", "*", "late_cases"], ["avg", "duration_days", "mean_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["late_cases"], desc=true (duckdb ORDER BY)
-> workbook name=problems (openpyxl.Workbook.save)
-> problem record
proofs/out/itil/problem-management/problem-record/problems.xlsx        sha256 126a467908e80e746c650bec72fbe175f6703fd6f58858feb2938c18d28ba74c  registered
shows: rows 8; first {"department": "General", "channel": "Internet", "late_cases": 308, "mean_days": 9.54}
```

### Problem management / known error record  proven

```
shape: paths that deviate from the model
instantiated on: receipt-phase variants of cases that did not fit the model
-> conformance (P9: pm4py.conformance_diagnostics_token_based_replay)
-> filter where=[["is_fit", "eq", false]] (duckdb WHERE)
-> workbook name=known_errors (openpyxl.Workbook.save)
-> known error record
proofs/out/itil/problem-management/known-error-record/known_errors.xlsx sha256 06ec4a4303c58a7d328c8b90e36969e93f8336ffa60d894dcb11a99dd3b37d08  registered
shows: rows 9; first {"case": "case-4771", "fitness": 0.9783, "is_fit": false, "missing_tokens": 2, "remaining_tokens": 2}
```

### Problem management / root-cause analysis  proven

```
shape: where the waiting accumulates
instantiated on: receipt-phase bottlenecks
-> bottlenecks (P46: duckdb join of edges and waiting time)
-> limit n=10 (duckdb LIMIT)
-> document name=root_cause, title=root cause: the ten slowest transitions (docx.Document; add_table; docx.document.Document.save)
-> root-cause analysis
proofs/out/itil/problem-management/root-cause-analysis/root_cause.docx sha256 b201d52d7cc6105787e56a888f1a46208a8dfda2998807422d7e4e6ce014099b  registered
shows: rows 10; first {"from": "T05 Print and send confirmation of receipt", "to": "T13 Adjust document X request unlicensed", "cases": 2, "mean_hours_waiting_into_to": 205.36}
```

### Problem management / trend analysis  proven

```
shape: failures per period
instantiated on: late receipt-phase cases per month
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> group by=["month"], aggregates=[["count", "*", "cases"], ["sum", "late", "late_cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=late_share, fn=ratio, num=late_cases, den=cases (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> page name=trend, title=share of cases ending after deadline, per month, kind=line, x=month, y=late_share (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> trend analysis
proofs/out/itil/problem-management/trend-analysis/trend.html           sha256 90e8251c6c3ff64e4a2a95d7bd81491f46a21b3acb26f56e165a6d1955cabb3c  registered
shows: rows 16; first {"month": "2010-10", "cases": 15, "late_cases": 10.0, "late_share": 0.6667}
```

### Release management / release plan  proven

```
shape: steps grouped into releases
instantiated on: ordered steps of the Node.js governance document by phase
-> ordered_steps of=nodejs-governance (P2: z3 consistency proof; networkx forced order)
-> select fields=["phase", "position", "step", "sentence"] (duckdb SELECT)
-> workbook name=release_plan (openpyxl.Workbook.save)
-> release plan
proofs/out/itil/release-management/release-plan/release_plan.xlsx      sha256 a8f3112bfee8f787be65b3ab97ef8e4944c20e6fa787b1a3649e59b780c66138  registered
shows: rows 18; first {"phase": 1, "position": 1, "step": "collaborator", "sentence": "A collaborator is automatically made emeritus (and removed from active collaborator status) if it has been more than 12 months since the collaborator has a
```

### Release management / release notes  proven

```
shape: what changed, with references
instantiated on: agenda items with links in the TSC minutes
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["links", "gt", 0]] (duckdb WHERE)
-> document name=release_notes, title=items with references, by meeting, columns=["meeting", "section", "item", "link"] (docx.Document; add_table; docx.document.Document.save)
-> release notes
proofs/out/itil/release-management/release-notes/release_notes.docx    sha256 bfe057deb3393d7b6909668536ec6cb1a21f2e1088d03b0d7d63750d73dbe640  registered
shows: rows 92; first {"meeting": "tsc-2023-11-08", "section": "Links", "item": "GitHub Issue: https://github.com/nodejs/TSC/issues/1468", "link": "https://github.com/nodejs/TSC/issues/1468", "links": 1}
```

### Release management / release schedule  proven

```
shape: releases by date with their line and kind
instantiated on: Node.js 22 changelog
-> changelog (re over CHANGELOG_V22.md: one row per release, security releases flagged)
-> select fields=["date", "version", "kind", "releaser", "security"] (duckdb SELECT)
-> sort by=["date"] (duckdb ORDER BY)
-> workbook name=release_schedule (openpyxl.Workbook.save)
-> release schedule
proofs/out/itil/release-management/release-schedule/release_schedule.xlsx sha256 fe0564f9f4b51fa8fba353e7b224f830993f448d192cd93e8d0685bedd0f92e1  registered
shows: rows 19; first {"date": "2024-10-29", "version": "22.11.0", "kind": "LTS", "releaser": "richardlau", "security": false}
```

### Release management / release readiness checklist  proven

```
shape: what must be true before release
instantiated on: obligations of the TSC charter
-> required_actions of=nodejs-tsc-charter (P4: the obligatory facts with agent quotes)
-> checklist name=readiness_checklist, title=readiness: the charter's obligations, item=action, note=sentence (docx.Document; one box glyph per row; docx.document.Document.save)
-> release readiness checklist
proofs/out/itil/release-management/release-readiness-checklist/readiness_checklist.docx sha256 7a609a0676f5c6c5ad399eeebf0b5bba0cb6900430e164bc523c9196f24c2e48  registered
shows: rows 13; first {"event": "nodejs-tsc-charter:u0002:s02#e12", "action": "open", "who": "", "sentence_id": "nodejs-tsc-charter:u0002:s02", "sentence": "Project proposals, timelines, and status must not merely be open, but also easily vis
```

### Service catalogue management / service catalogue  proven

```
shape: the services offered with volumes
instantiated on: receipt-phase activities
-> events (P6 rows as a relation)
-> group by=["activity"], aggregates=[["count", "*", "events"], ["distinct", "case", "cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=catalogue (openpyxl.Workbook.save)
-> service catalogue
proofs/out/itil/service-catalogue-management/service-catalogue/catalogue.xlsx sha256 a30f1360f5877670feefe77b74bdb11df64e4f049613c908825895c244526c71  registered
shows: rows 27; first {"activity": "Confirmation of receipt", "events": 1434, "cases": 1434}
```

### Service catalogue management / service descriptions  proven

```
shape: what each term means, from the governing text
instantiated on: definitional sentences of 5 U.S.C. 552
-> definitions of=usc5-552-doj (P1 facts where the event lemma is mean, include or define)
-> document name=descriptions, title=definitions in the statute, columns=["unit", "verb", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> service descriptions
proofs/out/itil/service-catalogue-management/service-descriptions/descriptions.docx sha256 9675d5075ed67446fb2b87425b701a3538e3c71451e56bfbc0beb8a09633b44f  registered
shows: rows 17; first {"event": "usc5-552-doj:u0024:s01#e12", "verb": "mean", "sentence_id": "usc5-552-doj:u0024:s01", "sentence": "For purposes of this paragraph, the term \"search\" means to review, manually or by automated means, agency re
```

### Service catalogue management / request catalogue  proven

```
shape: what can be requested through which channel
instantiated on: receipt-phase activities per channel
-> events (P6 rows as a relation)
-> pivot row=activity, col=channel (duckdb GROUP BY, laid out as a matrix)
-> workbook name=request_catalogue (openpyxl.Workbook.save)
-> request catalogue
proofs/out/itil/service-catalogue-management/request-catalogue/request_catalogue.xlsx sha256 faffad86140e0b0e33d934ba3bdf5e57f78938011d789f539fc9822399b482a7  registered
shows: rows 27; first {"activity": "Confirmation of receipt", "Desk": 109, "Intern": 1, "Internet": 1250, "Post": 53, "e-mail": 21}
```

### Service configuration management / configuration item register  proven

```
shape: the items and their attributes
instantiated on: receipt-phase activities, resources and groups
-> events (P6 rows as a relation)
-> distinct fields=["activity", "resource", "group"] (duckdb DISTINCT)
-> workbook name=ci_register (openpyxl.Workbook.save)
-> configuration item register
proofs/out/itil/service-configuration-management/configuration-item-register/ci_register.xlsx sha256 d3f0f5ae52283b9194d2593db8ef4ea31c493773c76de93ad77d50b67e02ca08  registered
shows: rows 526; first {"activity": "Confirmation of receipt", "resource": "Resource21", "group": "Group 1"}
```

### Service configuration management / CI relationship map  proven

```
shape: which item relates to which, with strength
instantiated on: receipt-phase directly-follows edges
-> dfg (P23: pm4py.discover_dfg)
-> page name=relationships, title=directly-follows relationships, kind=table (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> CI relationship map
proofs/out/itil/service-configuration-management/ci-relationship-map/relationships.html sha256 a0184388aad4d53c76d2336aa24b1ee8ba28d224d6bcfc9edfbe4be4b523a295  registered
shows: rows 99; first {"from": "T04 Determine confirmation of receipt", "to": "T05 Print and send confirmation of receipt", "count": 1177}
```

### Service configuration management / configuration baseline  proven

```
shape: the sealed state of the model
instantiated on: the forced order of 5 U.S.C. 552
-> ordered_steps of=usc5-552-doj (P2: z3 consistency proof; networkx forced order)
-> json name=baseline (json.dumps sort_keys)
-> configuration baseline
proofs/out/itil/service-configuration-management/configuration-baseline/baseline.json sha256 5851a99fe1fdb483cbe7e2459721066168905140f96ee9cec3edbfb40994b207  registered
shows: rows 24; first {"position": 1, "event": "usc5-552-doj:u0021:s00#e43", "step": "request", "phase": 1, "sentence": "(3)(A) Except with respect to the records made available under paragraphs (1) and (2) of this subsection, and except as p
```

### Service configuration management / configuration verification report  proven

```
shape: what was read back matches what was written
instantiated on: the reverse proofs of this file
-> roundtrips (P19, P30, P40, P50: reverse proofs and csv_diff.compare)
-> workbook name=verification (openpyxl.Workbook.save)
-> configuration verification report
proofs/out/itil/service-configuration-management/configuration-verification-report/verification.xlsx sha256 6e49e3dabd08905d28f3db4a1b676853ddf59176de68a1eb014200f5af8a32e5  registered
shows: rows 4; first {"proof": "P19", "label": "deck", "match": true, "changed": 0}
```

### Service continuity management / business impact analysis  proven

```
shape: volume and duration per group
instantiated on: receipt-phase departments
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["count", "*", "cases"], ["avg", "duration_days", "mean_days"], ["max", "duration_days", "max_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=bia (openpyxl.Workbook.save)
-> business impact analysis
proofs/out/itil/service-continuity-management/business-impact-analysis/bia.xlsx sha256 2336582410bc401f781a3621079ebcfb9e8ff068c8fd0e49a6edcf378d083681  registered
shows: rows 3; first {"department": "Customer contact", "cases": 29, "mean_days": 1.66, "max_days": 12.25}
```

### Service continuity management / continuity plan  proven

```
shape: the required actions in order
instantiated on: 5 U.S.C. 552 required actions
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> document name=continuity_plan, title=required actions, columns=["unit", "who", "action", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> continuity plan
proofs/out/itil/service-continuity-management/continuity-plan/continuity_plan.docx sha256 bc76be40df9526b65b44eb0f971b62a7a0b61fbdd1db8711c029dc6228c3b084  registered
shows: rows 122; first {"event": "usc5-552-doj:u0001:s00#e7", "action": "make", "who": "agency shall make", "sentence_id": "usc5-552-doj:u0001:s00", "sentence": "(a) Each agency shall make available to the public information as follows:", "quo
```

### Service continuity management / recovery procedure  proven

```
shape: the ordered steps to restore
instantiated on: ordered steps of 5 U.S.C. 552
-> ordered_steps of=usc5-552-doj (P2: z3 consistency proof; networkx forced order)
-> document name=recovery_procedure, title=steps in forced order, columns=["position", "phase", "step", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> recovery procedure
proofs/out/itil/service-continuity-management/recovery-procedure/recovery_procedure.docx sha256 bfe2abce4ca66498589f4f09426593317b95ae8edd0eb134498c8327472f7db0  registered
shows: rows 24; first {"position": 1, "event": "usc5-552-doj:u0021:s00#e43", "step": "request", "phase": 1, "sentence": "(3)(A) Except with respect to the records made available under paragraphs (1) and (2) of this subsection, and except as p
```

### Service continuity management / continuity test report  proven

```
shape: the procedure executed and checked
instantiated on: execution trace of the statutory process in SpiffWorkflow
-> execution_trace of=usc5-552-doj (P29: SpiffWorkflow execution of the process)
-> workbook name=test_report (openpyxl.Workbook.save)
-> continuity test report
proofs/out/itil/service-continuity-management/continuity-test-report/test_report.xlsx sha256 3ace901e86701e2edc3c1a79417fdc535a4594dab61d0b02b4acb91b3c2a3d8a  registered
shows: rows 24; first {"position": 1, "task": "authorize [u0131:s00#e16]"}
```

### Service design / service design package  proven

```
shape: requirements, steps and rules together
instantiated on: 5 U.S.C. 552
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> document name=design_package, title=design package: requirements, columns=["unit", "who", "action", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> service design package
proofs/out/itil/service-design/service-design-package/design_package.docx sha256 69ebdd2d5274d2d1f879445cf5b26029b1d88b33719252d299aad0f0e6111616  registered
shows: rows 122; first {"event": "usc5-552-doj:u0001:s00#e7", "action": "make", "who": "agency shall make", "sentence_id": "usc5-552-doj:u0001:s00", "sentence": "(a) Each agency shall make available to the public information as follows:", "quo
```

### Service design / requirements traceability matrix  proven

```
shape: each requirement traced to its source unit
instantiated on: 5 U.S.C. 552 obligations per unit
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> pivot row=unit, col=action (duckdb GROUP BY, laid out as a matrix)
-> workbook name=traceability (openpyxl.Workbook.save)
-> requirements traceability matrix
proofs/out/itil/service-design/requirements-traceability-matrix/traceability.xlsx sha256 34a591089bc4a9518095fc49d7cc5b25e7b40e22edbaef5834f760c4bcd9389c  registered
shows: rows 74; first {"unit": "u0001", "accord": 0, "aggregate": 0, "allow": 0, "apply": 0, "assess": 0, "assist": 0, "available": 0, "base": 0, "chair": 0, "commence": 0, "comprise": 0, "conduct": 0, "conform": 0, "consider": 0, "construe":
```

### Service design / service blueprint  proven

```
shape: the process with its steps and order
instantiated on: forced precedence of 5 U.S.C. 552
-> forced_edges of=usc5-552-doj (P2: networkx.transitive_reduction)
-> bpmn name=blueprint (pm4py.objects.bpmn.obj.BPMN with parallel gateways; bpmn exporter; canonical ids)
-> service blueprint
proofs/out/itil/service-design/service-blueprint/blueprint.bpmn        sha256 6209f474a27c67b72b44c6dc345b5d9f06bf2f24c86d485582cb8442e5697d61  registered
shows: rows 12; first {"before": "usc5-552-doj:u0021:s00#e43", "after": "usc5-552-doj:u0021:s00#e59", "before_step": "request", "after_step": "make"}
```

### Service desk / ticket log  proven

```
shape: contacts by channel and time
instantiated on: receipt-phase cases by channel
-> cases (duckdb: one row per case from the event rows)
-> pivot row=month, col=channel (duckdb GROUP BY, laid out as a matrix)
-> workbook name=ticket_log (openpyxl.Workbook.save)
-> ticket log
proofs/out/itil/service-desk/ticket-log/ticket_log.xlsx                sha256 76022eca427bcdc10a0277150e5f1daa1c56906191fbddd4bbc21184d4dab74f  registered
shows: rows 16; first {"month": "2010-10", "Desk": 3, "Intern": 0, "Internet": 12, "Post": 0, "e-mail": 0}
```

### Service desk / interaction records  proven

```
shape: the interactions that came through the desk
instantiated on: receipt-phase events on the Desk channel
-> events (P6 rows as a relation)
-> filter where=[["channel", "eq", "Desk"]] (duckdb WHERE)
-> select fields=["case", "activity", "ts", "resource"] (duckdb SELECT)
-> workbook name=desk_interactions (openpyxl.Workbook.save)
-> interaction records
proofs/out/itil/service-desk/interaction-records/desk_interactions.xlsx sha256 d8e5f4c0f929a94c88e3f68d298f7edbf8bccbf68a0488a4514a85424099d58d  registered
shows: rows 657; first {"case": "case-10199", "activity": "Confirmation of receipt", "ts": "2011-10-31 12:27:03.433000+01:00", "resource": "Resource13"}
```

### Service desk / knowledge suggestions  proven

```
shape: the steps most discussed, as candidates for articles
instantiated on: governance steps tagged in TSC minutes
-> tags of=nodejs-governance (P10/P26: clingo shared-word tagging)
-> filter where=[["tie", "eq", false]] (duckdb WHERE)
-> group by=["step_lemma"], aggregates=[["count", "*", "lines"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["lines"], desc=true (duckdb ORDER BY)
-> limit n=10 (duckdb LIMIT)
-> workbook name=knowledge_suggestions (openpyxl.Workbook.save)
-> knowledge suggestions
proofs/out/itil/service-desk/knowledge-suggestions/knowledge_suggestions.xlsx sha256 0f5df56b186ff344862cb8c3eb675685e0b8452ae16c9a2297ea09c9d57f2146  registered
shows: rows 9; first {"step_lemma": "be", "lines": 21}
```

### Service desk / user communications  proven

```
shape: what was announced, when
instantiated on: Announcements sections of the TSC minutes
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["section", "contains", "announce"]] (duckdb WHERE)
-> select fields=["meeting", "item"] (duckdb SELECT)
-> workbook name=announcements (openpyxl.Workbook.save)
-> user communications
proofs/out/itil/service-desk/user-communications/announcements.xlsx    sha256 0b5660bfd43832d1200998bd9a118c9c2e3ed34eecd769882df91b01dc6fb3af  registered
shows: rows 8; first {"meeting": "tsc-2024-01-10", "item": "Richard, Ulises did a release for Node.js 20"}
```

### Service level management / service level targets  proven

```
shape: each target with the clock the text sets
instantiated on: 5 U.S.C. 552 obligations with durations in the same sentence
-> anchors of=usc5-552-doj (P3: timexy)
-> filter where=[["timex3", "contains", "DURATION"]] (duckdb WHERE)
-> save_as name=clocks (the relation kept under a name for a later join)
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> join with=clocks, keys=[["sentence_id", "sentence_id"]] (duckdb JOIN)
-> select fields=["unit", "who", "action", "span", "timex3"] (duckdb SELECT)
-> distinct (duckdb DISTINCT)
-> workbook name=targets (openpyxl.Workbook.save)
-> service level targets
proofs/out/itil/service-level-management/service-level-targets/targets.xlsx sha256 366c2583ed86b99b8cfcfc167ae3404841b64e610c207233e5a67df6c649c554  registered
shows: rows 6; first {"unit": "u0018", "who": "agency shall make", "action": "make", "span": "one year", "timex3": "TIMEX3 type=\"DURATION\" value=\"P1Y\""}
```

### Service level management / service level report  proven

```
shape: achieved against deadline per group
instantiated on: receipt-phase cases per department
-> cases (duckdb: one row per case from the event rows)
-> pivot row=department, col=outcome (duckdb GROUP BY, laid out as a matrix)
-> workbook name=service_level_report (openpyxl.Workbook.save)
-> service level report
proofs/out/itil/service-level-management/service-level-report/service_level_report.xlsx sha256 903be867ca0c14f8a85ba373b273d86569859d09a3d12e53b73bf978f6af6870  registered
shows: rows 3; first {"department": "Customer contact", "after deadline": 1, "by deadline": 28, "open": 0}
```

### Service level management / breach analysis  proven

```
shape: breaches by channel and department
instantiated on: receipt-phase cases after deadline
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "after deadline"]] (duckdb WHERE)
-> pivot row=department, col=channel (duckdb GROUP BY, laid out as a matrix)
-> workbook name=breach_analysis (openpyxl.Workbook.save)
-> breach analysis
proofs/out/itil/service-level-management/breach-analysis/breach_analysis.xlsx sha256 56529eea81ba8f9c33dd208034d3be2da4048437e4b43411f637c3dd791a709b  registered
shows: rows 3; first {"department": "Customer contact", "Desk": 0, "Internet": 1, "Post": 0, "e-mail": 0}
```

### Service level management / dependency map  proven

```
shape: who depends on whom for delivery
instantiated on: receipt-phase handover-of-work network
-> handover (pm4py.discover_handover_of_work_network)
-> limit n=100 (duckdb LIMIT)
-> page name=dependency_map, title=handover of work, kind=table (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> dependency map
proofs/out/itil/service-level-management/dependency-map/dependency_map.html sha256 5177064a413070c13dd15286a6b73a7095565c03c8849c521bad7b4440f3fb40  registered
shows: rows 100; first {"from": "Resource01", "to": "Resource01", "value": 0.136497}
```

### Service request management / request models  proven

```
shape: the standard paths a request takes
instantiated on: receipt-phase variants
-> variants (P36: pm4py.get_variants_as_tuples)
-> limit n=20 (duckdb LIMIT)
-> workbook name=request_models (openpyxl.Workbook.save)
-> request models
proofs/out/itil/service-request-management/request-models/request_models.xlsx sha256 09e5a890c7fcfaafddaf1258567de08a0f09e662640cb2c6d8b1ee7092f7e991  registered
shows: rows 20; first {"rank": 1, "cases": 713, "length": 6, "variant": "Confirmation of receipt -> T02 Check confirmation of receipt -> T04 Determine confirmation of receipt -> T05 Print and send confirmation of receipt -> T06 Determine nece
```

### Service request management / fulfilment records  proven

```
shape: closed requests with their duration
instantiated on: receipt-phase cases that ended
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "ne", "open"]] (duckdb WHERE)
-> select fields=["case", "department", "channel", "start", "end", "duration_days", "outcome"] (duckdb SELECT)
-> workbook name=fulfilment_records (openpyxl.Workbook.save)
-> fulfilment records
proofs/out/itil/service-request-management/fulfilment-records/fulfilment_records.xlsx sha256 02f041b87e93d3d29dfaf27f0cdf39d1422ef99ddb4779c2f790af7c1de0ce6f  registered
shows: rows 1329; first {"case": "case-10017", "department": "General", "channel": "Internet", "start": "2011-10-18 11:46:39.679000+00:00", "end": "2011-10-18 11:56:57.603000+00:00", "duration_days": 0.01, "outcome": "by deadline"}
```

### Service request management / fulfilment time report  proven

```
shape: duration statistics per channel
instantiated on: receipt-phase cases per channel
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "ne", "open"]] (duckdb WHERE)
-> group by=["channel"], aggregates=[["count", "*", "cases"], ["median", "duration_days", "median_days"], ["avg", "duration_days", "mean_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=fulfilment_time (openpyxl.Workbook.save)
-> fulfilment time report
proofs/out/itil/service-request-management/fulfilment-time-report/fulfilment_time.xlsx sha256 d4236c595aca262e0db942d91cbf74ca1ed5613de062fabc51b7879e3376561e  registered
shows: rows 5; first {"channel": "Desk", "cases": 107, "median_days": 0.76, "mean_days": 5.89}
```

### Service request management / approvals log  proven

```
shape: approvals and votes recorded
instantiated on: TSC minutes sentences whose actions include approve or vote
-> minutes_sentences (P7: compiled_ai parse of the minutes; one row per sentence with its event lemmas)
-> filter where=[["lemmas", "matches", "\\b(approve|vote|lgtm|merge)\\b"]] (duckdb WHERE)
-> select fields=["meeting", "sentence_id", "sentence"] (duckdb SELECT)
-> workbook name=approvals (openpyxl.Workbook.save)
-> approvals log
proofs/out/itil/service-request-management/approvals-log/approvals.xlsx sha256 921e6c2fa4548a0d67688968f880488ea527118a26fee039a40596ac5be543c5  registered
shows: rows 3; first {"meeting": "tsc-2024-01-10", "sentence_id": "tsc-2024-01-10:u0014:s09", "sentence": "If we Have a vote lets vote on removing npm, versus vote on corepack."}
```

### Service validation and testing / test plan  proven

```
shape: what must be verified
instantiated on: obligations of 5 U.S.C. 552 as a checklist
-> required_actions of=usc5-552-doj (P4: the obligatory facts with agent quotes)
-> checklist name=test_plan, title=test plan: every obligation, item=action, note=sentence (docx.Document; one box glyph per row; docx.document.Document.save)
-> test plan
proofs/out/itil/service-validation-and-testing/test-plan/test_plan.docx sha256 5a46ef6b9e9f8c5b61b4cf061f0f5deb8a3f47f03d8db28fd1cfff6a0e0ca052  registered
shows: rows 122; first {"event": "usc5-552-doj:u0001:s00#e7", "action": "make", "who": "agency shall make", "sentence_id": "usc5-552-doj:u0001:s00", "sentence": "(a) Each agency shall make available to the public information as follows:", "quo
```

### Service validation and testing / test cases  proven

```
shape: ordering tests, one per forced edge
instantiated on: forced precedence of 5 U.S.C. 552
-> forced_edges of=usc5-552-doj (P2: networkx.transitive_reduction)
-> workbook name=test_cases (openpyxl.Workbook.save)
-> test cases
proofs/out/itil/service-validation-and-testing/test-cases/test_cases.xlsx sha256 3f7d90a88d1f7d5e554226e1ef22997afffadf123c6a060bd2501acc18761ebf  registered
shows: rows 12; first {"before": "usc5-552-doj:u0021:s00#e43", "after": "usc5-552-doj:u0021:s00#e59", "before_step": "request", "after_step": "make"}
```

### Service validation and testing / test results  proven

```
shape: the executed order against the required order
instantiated on: SpiffWorkflow execution of the statutory process
-> execution_trace of=usc5-552-doj (P29: SpiffWorkflow execution of the process)
-> workbook name=test_results (openpyxl.Workbook.save)
-> test results
proofs/out/itil/service-validation-and-testing/test-results/test_results.xlsx sha256 3ace901e86701e2edc3c1a79417fdc535a4594dab61d0b02b4acb91b3c2a3d8a  registered
shows: rows 24; first {"position": 1, "task": "authorize [u0131:s00#e16]"}
```

### Service validation and testing / acceptance record  proven

```
shape: reverse checks that passed
instantiated on: the reverse proofs of this file
-> roundtrips (P19, P30, P40, P50: reverse proofs and csv_diff.compare)
-> filter where=[["match", "eq", true]] (duckdb WHERE)
-> workbook name=acceptance (openpyxl.Workbook.save)
-> acceptance record
proofs/out/itil/service-validation-and-testing/acceptance-record/acceptance.xlsx sha256 6e49e3dabd08905d28f3db4a1b676853ddf59176de68a1eb014200f5af8a32e5  registered
shows: rows 4; first {"proof": "P19", "label": "deck", "match": true, "changed": 0}
```

### Deployment management / deployment plan  proven

```
shape: ordered steps with phases
instantiated on: ordered steps of the Node.js governance document
-> ordered_steps of=nodejs-governance (P2: z3 consistency proof; networkx forced order)
-> select fields=["phase", "position", "step"] (duckdb SELECT)
-> workbook name=deployment_plan (openpyxl.Workbook.save)
-> deployment plan
proofs/out/itil/deployment-management/deployment-plan/deployment_plan.xlsx sha256 21e9a27b47b4352ad555d5fe68a11a33f7a02d56fa92b01f564845971c2acca9  registered
shows: rows 18; first {"phase": 1, "position": 1, "step": "collaborator"}
```

### Deployment management / deployment records  proven

```
shape: deployments performed, with references
instantiated on: TSC minutes items mentioning release, deploy or land
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["item", "matches", "(?i)\\b(release|deploy|land|ship)"]] (duckdb WHERE)
-> select fields=["meeting", "item", "link"] (duckdb SELECT)
-> workbook name=deployment_records (openpyxl.Workbook.save)
-> deployment records
proofs/out/itil/deployment-management/deployment-records/deployment_records.xlsx sha256 ddc268f511762e5c67fdbb464dfcea809fa7a60ae798886f86b00556a4822485  registered
shows: rows 14; first {"meeting": "tsc-2023-11-08", "item": "Support for file-system based persistent code cache in user-land module loaders #47472", "link": "https://github.com/nodejs/node/issues/47472"}
```

### Deployment management / environment inventory  proven

```
shape: the environments and who works in them
instantiated on: receipt-phase groups and resources
-> events (P6 rows as a relation)
-> group by=["group"], aggregates=[["distinct", "resource", "resources"], ["count", "*", "events"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=environments (openpyxl.Workbook.save)
-> environment inventory
proofs/out/itil/deployment-management/environment-inventory/environments.xlsx sha256 40b50ca380cbb2543a3631115f814add9e97ea9a20416de192e425f6c6e2b7d5  registered
shows: rows 10; first {"group": "EMPTY", "resources": 44, "events": 1936}
```

### Deployment management / rollback procedure  proven

```
shape: the ordered steps, reversed
instantiated on: ordered steps of the Node.js governance document
-> ordered_steps of=nodejs-governance (P2: z3 consistency proof; networkx forced order)
-> sort by=["position"], desc=true (duckdb ORDER BY)
-> document name=rollback, title=rollback: the steps in reverse order, columns=["position", "step", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> rollback procedure
proofs/out/itil/deployment-management/rollback-procedure/rollback.docx sha256 32f39b5d1c99ad969475ef4830d70bd6d5d25bc5eaf8b967e899e30e13d43f04  registered
shows: rows 18; first {"position": 18, "event": "nodejs-governance:u0070:s00#e11", "step": "visible", "phase": 2, "sentence": "Remember that all private discussions about a nomination will be visible to the nominee once they are onboarded.", 
```

### Infrastructure and platform management / infrastructure inventory  proven

```
shape: groups, resources and activity counts
instantiated on: receipt-phase groups and resources
-> events (P6 rows as a relation)
-> pivot row=group, col=activity (duckdb GROUP BY, laid out as a matrix)
-> workbook name=infrastructure_inventory (openpyxl.Workbook.save)
-> infrastructure inventory
proofs/out/itil/infrastructure-and-platform-management/infrastructure-inventory/infrastructure_inventory.xlsx sha256 188a7f3b131f07df59060d0f4e3e4e50e9565190708de98bcc22be549e4b1e5c  registered
shows: rows 10; first {"group": "EMPTY", "Confirmation of receipt": 1136, "T02 Check confirmation of receipt": 373, "T03 Adjust confirmation of receipt": 0, "T04 Determine confirmation of receipt": 204, "T05 Print and send confirmation of rec
```

### Infrastructure and platform management / runbook  proven

```
shape: the steps to perform, in order, with sources
instantiated on: ordered steps of 5 U.S.C. 552
-> ordered_steps of=usc5-552-doj (P2: z3 consistency proof; networkx forced order)
-> document name=runbook, title=runbook, columns=["position", "phase", "step", "sentence"] (docx.Document; add_table; docx.document.Document.save)
-> runbook
proofs/out/itil/infrastructure-and-platform-management/runbook/runbook.docx sha256 ecfced8d56bf9967c71b9693c72796e151623f78a74fc8d21d63867b91b79700  registered
shows: rows 24; first {"position": 1, "event": "usc5-552-doj:u0021:s00#e43", "step": "request", "phase": 1, "sentence": "(3)(A) Except with respect to the records made available under paragraphs (1) and (2) of this subsection, and except as p
```

### Infrastructure and platform management / utilization report  proven

```
shape: use per resource per period
instantiated on: receipt-phase events per resource per month
-> events (P6 rows as a relation)
-> derive field=month, fn=month, of=ts (duckdb expression (closed set: month, days_between, hours_between, contains, ratio, length))
-> pivot row=resource, col=month (duckdb GROUP BY, laid out as a matrix)
-> workbook name=utilization (openpyxl.Workbook.save)
-> utilization report
proofs/out/itil/infrastructure-and-platform-management/utilization-report/utilization.xlsx sha256 e85de9fce1d4b8979ecd6b9ddb63c7ed637121276cd604954ce9f91285de6b02  registered
shows: rows 48; first {"resource": "Resource01", "2010-10": 0, "2010-11": 6, "2010-12": 50, "2011-01": 24, "2011-02": 150, "2011-03": 160, "2011-04": 199, "2011-05": 94, "2011-06": 105, "2011-07": 227, "2011-08": 87, "2011-09": 83, "2011-10":
```

### Software development and management / backlog  proven

```
shape: work items with references and where they were raised
instantiated on: issues referenced in TSC minutes
-> minutes_sections (markdown.markdown; lxml.html: heading sections and their list items)
-> filter where=[["link", "contains", "/issues/"]] (duckdb WHERE)
-> select fields=["meeting", "section", "item", "link"] (duckdb SELECT)
-> workbook name=backlog (openpyxl.Workbook.save)
-> backlog
proofs/out/itil/software-development-and-management/backlog/backlog.xlsx sha256 1ab9c7c3ccc86209c1a37f5671c7b199d892f22cb3539b7f0c23d6e0162f4841  registered
shows: rows 47; first {"meeting": "tsc-2023-11-08", "section": "Links", "item": "GitHub Issue: https://github.com/nodejs/TSC/issues/1468", "link": "https://github.com/nodejs/TSC/issues/1468"}
```

### Software development and management / code review decisions  proven

```
shape: approvals and objections recorded
instantiated on: TSC minutes sentences whose actions include approve, object, merge or block
-> minutes_sentences (P7: compiled_ai parse of the minutes; one row per sentence with its event lemmas)
-> filter where=[["lemmas", "matches", "\\b(approve|object|merge|block|revert)\\b"]] (duckdb WHERE)
-> select fields=["meeting", "sentence_id", "lemmas", "sentence"] (duckdb SELECT)
-> workbook name=review_decisions (openpyxl.Workbook.save)
-> code review decisions
proofs/out/itil/software-development-and-management/code-review-decisions/review_decisions.xlsx sha256 02e0dc5e6eb3dbbdf5d14bd3c41388b1c0c30fb261fe17ffc262b04d5023f874  registered
shows: rows 1; first {"meeting": "tsc-2025-03-05", "sentence_id": "tsc-2025-03-05:u0021:s07", "lemmas": "lose move need object seem", "sentence": "But it seems that the initiative lost its momentum * Michael anybody in the meeting who object
```

### Software development and management / version records  proven

```
shape: versions released, with dates and commit counts
instantiated on: Node.js 22 changelog
-> changelog (re over CHANGELOG_V22.md: one row per release, security releases flagged)
-> workbook name=versions (openpyxl.Workbook.save)
-> version records
proofs/out/itil/software-development-and-management/version-records/versions.xlsx sha256 6c7a8fa240dfc7dea56be8f882a7c4e51803a65ca1921a87db44e92080725e1e  registered
shows: rows 19; first {"date": "2026-07-29", "version": "22.23.2", "codename": "Jod", "kind": "LTS", "releaser": "marco-ippolito", "security": true, "commits": 12}
```

### Software development and management / verification report  proven

```
shape: what was executed and what was read back
instantiated on: the execution and reverse proofs of this file
-> roundtrips (P19, P30, P40, P50: reverse proofs and csv_diff.compare)
-> workbook name=verification_report (openpyxl.Workbook.save)
-> verification report
proofs/out/itil/software-development-and-management/verification-report/verification_report.xlsx sha256 6e49e3dabd08905d28f3db4a1b676853ddf59176de68a1eb014200f5af8a32e5  registered
shows: rows 4; first {"proof": "P19", "label": "deck", "match": true, "changed": 0}
```

## Amendment 1

reason: exports made reproducible: Office core timestamps and zip entry dates fixed, BPMN and PNML ids canonical, mkdocs build date fixed; the soundness proofs replaced the state-space search with structural checks (P34, P35)

```
proofs/out/P10/nodejs-governance+nodejs-tsc-minutes/tagged_steps.xlsx  add3219e9ddd2cb9… -> ef1b2d2ffe354186…
proofs/out/P11/nodejs-governance/measured_steps.xlsx                   d45da313770c165e… -> 1cf193eb87f0f788…
proofs/out/P11/nodejs-tsc-charter/measured_steps.xlsx                  c47f5c8d9b00930b… -> 2bdf39eabedc9f5d…
proofs/out/P12/receipt-xes+receipt-csv/measured_activities.xlsx        fcb5be3f545783b8… -> 544bda186c506df7…
proofs/out/P13/charter+roster+minutes/decisions.xlsx                   850849d047dfa541… -> c333cd29051c0297…
proofs/out/P14/nodejs-governance/dependencies.pptx                     b81addd37191e7c2… -> 349160c68b6d1a1f…
proofs/out/P14/usc5-552-doj/dependencies.pptx                          1ac4206631f50664… -> 36f04460d3c94f48…
proofs/out/P15/nodejs-governance/ordered_steps.docx                    5a98fa1036e2907f… -> fa6b8164919d776b…
proofs/out/P15/usc5-552-doj/ordered_steps.docx                         c667775b907b4e09… -> 6da847e325f9ebb5…
proofs/out/P16/nodejs-governance/facts.xlsx                            2ffbc8222d66f2dc… -> f9608a6e76ef2643…
proofs/out/P16/nodejs-tsc-charter/facts.xlsx                           006843be61ac4cb9… -> 549f9290f6744b52…
proofs/out/P16/usc5-552-doj/facts.xlsx                                 1c9ee3a7ab0f60c2… -> 895cd74f2f48c34d…
proofs/out/P18/nodejs-governance+tsc-2024-01-17/deck.pptx              811dbbd95322a1aa… -> 90af16c70fab459d…
proofs/out/P20/nodejs-governance/conformance.xlsx                      b53ea0adab90081f… -> 041de6a3fcad86ee…
proofs/out/P21/receipt-csv/deadlines.xlsx                              b747794df52a4a57… -> f923fdc8cd38481f…
proofs/out/P22/receipt-csv/by_department_and_channel.xlsx              ecb5795581c99d3c… -> 4ad652e5f73e2286…
proofs/out/P23/receipt-xes/directly_follows.xlsx                       891c5814ebe0d16c… -> 07dfafdeaa64f352…
proofs/out/P25/nodejs-tsc-charter/required_actions.docx                1ff341a1edf18851… -> 128db0ce380dbcf9…
proofs/out/P25/usc5-552-doj/required_actions.docx                      20dc73844b6eda2e… -> c910688d18800d40…
proofs/out/P26/nodejs-tsc-charter+nodejs-tsc-minutes/tagged_steps.xlsx 86f7882d295e6000… -> e3b7806a5238fa63…
proofs/out/P27/receipt-xes+receipt-csv/conformance_by_group.xlsx       c47d4fd9fcca8086… -> 70e4bb450df3a838…
proofs/out/P28/majority+charter-tags/decisions_with_discussion.xlsx    8604c41c5f827847… -> 4f0ba45d8e29fd3e…
proofs/out/P29/nodejs-governance/execution_trace.xlsx                  553150f3815291ee… -> 829d201465e891e4…
proofs/out/P29/nodejs-governance/process.executable.bpmn               60cc794db4e0df4e… -> 2910ac675d259a9b…
proofs/out/P29/usc5-552-doj/execution_trace.xlsx                       67824bf5929d40f7… -> adbd07ad97584717…
proofs/out/P29/usc5-552-doj/process.executable.bpmn                    b630a4c41554be79… -> 049228aef5479a26…
proofs/out/P32/charter+minutes/coverage_matrix.xlsx                    99bf122d73b11592… -> c601b257f4de26d0…
proofs/out/P33/nodejs-governance/never_discussed.xlsx                  534562e3d17a9c3a… -> 3d8f0878f0063c1f…
proofs/out/P34/receipt-xes/soundness.json                              eec74566c5ddaccd… -> c651a83c5d8abd78…
proofs/out/P35/nodejs-governance/process.pnml                          8c2ab70bd4a9e282… -> 770db4add3daeafb…
proofs/out/P35/nodejs-governance/soundness.json                        c687384fae8a44be… -> c3de2f706af4e4e0…
proofs/out/P35/usc5-552-doj/process.pnml                               df4d75ccb33a6b50… -> b4dc2128d6148861…
proofs/out/P35/usc5-552-doj/soundness.json                             7f0efe217d243d09… -> f22af95ac05e4cd4…
proofs/out/P36/receipt-xes/variants.xlsx                               8b4c196689661c7e… -> fb2540bb2ab8ecfa…
proofs/out/P37/nodejs-tsc-charter/facts.ttl                            857fcd473d295406… -> 5e4f210151b30ecd…
proofs/out/P37/nodejs-tsc-charter/sparql_required_actions.xlsx         4eccfd89131c2ca1… -> aff33c5ad3a210af…
proofs/out/P37/usc5-552-doj/facts.ttl                                  f71d193a71bbf2f5… -> b5d077ed4c3b1e4a…
proofs/out/P37/usc5-552-doj/sparql_required_actions.xlsx               1f30aa012c9a18d4… -> 20e20eae695f1d7e…
proofs/out/P38/usc5-552-doj/cypher_results.xlsx                        9b2db14d45742d80… -> 02537128a315c8af…
proofs/out/P39/usc5-552-doj/site/index.html                            c6422220006d2e3a… -> 3da483de604dff91…
proofs/out/P5/nodejs-governance/process.bpmn                           c38de863a2d578f5… -> 9c83f8172d8fdb45…
proofs/out/P5/usc5-552-doj/process.bpmn                                d9d971a9a885bc30… -> 6209f474a27c67b7…
proofs/out/P8/receipt-xes/process.bpmn                                 2a157d59a8ddf131… -> 1f4fc44ee45b11e9…
proofs/out/P8/receipt-xes/process.pnml                                 3c096e55edcc20f3… -> 64593d43e20fd6e3…
proofs/out/P9/receipt-xes/conformance.xlsx                             26a3ab4fa7a0bdd5… -> 339533b73457ffcd…
```
## Amendment 2

reason: pm4py per-run counters in place and silent-transition names replaced by canonical ids; mkdocs build date fixed

```
proofs/out/P35/nodejs-governance/process.pnml                          770db4add3daeafb… -> 6b8430fb8cf886b0…
proofs/out/P35/nodejs-governance/soundness.json                        c3de2f706af4e4e0… -> e25411e84e2ad67a…
proofs/out/P35/usc5-552-doj/process.pnml                               b4dc2128d6148861… -> 26aff4e9247dffef…
proofs/out/P35/usc5-552-doj/soundness.json                             f22af95ac05e4cd4… -> 63c9dd4c1f982a35…
proofs/out/P39/usc5-552-doj/site/index.html                            3da483de604dff91… -> d8cee796da958596…
proofs/out/P52/receipt-xes/canonical.pnml                              64593d43e20fd6e3… -> cbb8e62b911aa5f2…
proofs/out/P8/receipt-xes/process.pnml                                 64593d43e20fd6e3… -> cbb8e62b911aa5f2…
```
## Amendment 3

reason: uuid names and localNodeID attributes in the Petri net exports replaced by canonical ids

```
proofs/out/P35/nodejs-governance/process.pnml                          6b8430fb8cf886b0… -> dc149693d9a6058f…
proofs/out/P35/nodejs-governance/soundness.json                        e25411e84e2ad67a… -> 845d8a655f04710b…
proofs/out/P35/usc5-552-doj/process.pnml                               26aff4e9247dffef… -> d4d8dfed1baf1020…
proofs/out/P35/usc5-552-doj/soundness.json                             63c9dd4c1f982a35… -> d703bae13849e7de…
proofs/out/P52/receipt-xes/canonical.pnml                              cbb8e62b911aa5f2… -> 9475109f51c0c7e1…
proofs/out/P8/receipt-xes/process.pnml                                 cbb8e62b911aa5f2… -> 9475109f51c0c7e1…
```
### P5  ordered steps -> process model -> process  (revised chain 1)

```
ordered steps
-> process model (pm4py.objects.bpmn.obj.BPMN (StartEvent, Task, EndEvent, SequenceFlow); pm4py.objects.bpmn.exporter.exporter.apply)
-> process
```

### P8  event log -> log -> process model -> process diagram  (revised chain 1)

```
event log
-> read (pm4py.read_xes)
-> discover (pm4py.discover_process_tree_inductive; pm4py.convert_to_petri_net)
-> chart (pm4py.write_pnml; pm4py.objects.conversion.wf_net.variants.to_bpmn.apply; pm4py.objects.bpmn.exporter.exporter.apply)
-> process diagram
```

### P34  process model -> soundness proof  (revised chain 1)

```
process model (P8, discovered)
-> soundness proof (pm4py check_wfnet; networkx.is_directed_acyclic_graph; marked-graph check; sound by construction from the process tree)
-> soundness proof
```

### P35  process -> petri net -> soundness proof  (revised chain 1)

```
process (P5)
-> read (pm4py.read_bpmn)
-> petri net (pm4py.convert_to_petri_net; pm4py.write_pnml)
-> soundness proof (pm4py check_wfnet; networkx.is_directed_acyclic_graph; marked-graph check: acyclic marked-graph workflow nets are sound)
-> soundness proof
```

## P54  policy -> every possible input -> decisions -> workbook, page

```
policy (P13), roster (P6)
-> enumerate (range over the closed input space: present voting members 0..N)
-> evaluate (zen.ZenDecision.evaluate per input)
-> tabulate (openpyxl.Workbook.save; jinja2 table page)
-> the whole rule, enumerated
```

**majority**

```
proofs/out/P54/majority/truth_table.xlsx                   sha256 27cbadd2eb1b2ef6d555b5f43d11b7ae6b3e924ab62d79a1cda5f61ed7f0bbf3  registered
proofs/out/P54/majority/truth_table.html                   sha256 99bf76a07e4391960cde062d843746ea550540033779306d455c75ab0ba83652  registered
shows: inputs enumerated 19; majority reachable from 10 present upward
```

## P55  policy -> DMN decision table -> decisions' ; decisions, decisions' -> agreement

```
policy (P13), decisions (P13)
-> compile (jinja2 -> DMN 1.3 decision table XML with the charter sentence as the rule description)
-> evaluate (SpiffWorkflow.dmn.parser.BpmnDmnParser.add_dmn_str; SpiffWorkflow.dmn.engine.DMNEngine.result per meeting)
-> compare (zen result against the DMN result per meeting)
-> tabulate (openpyxl.Workbook.save)
-> agreement
```

**majority**

```
proofs/out/P55/majority/majority.dmn                       sha256 2ab96f26abba5d4c8d5ed62a719e4cdea34e6b7f410ae328cf033f6cafc4243c  registered
proofs/out/P55/majority/cross_engine.xlsx                  sha256 0fdb587e4572f113b9792746644d11f5459bfbf029b6ba9b71f43d569cbed108  registered
shows: meetings 8; engines agree on all: True
shows: tsc-2023-11-08: present 6 zen False dmn False
shows: tsc-2023-12-06: present 10 zen True dmn True
```

## P56  decisions, policy -> explanation document

```
decisions (P13), policy (P13), roster (P6)
-> write (docx.Document: one section per meeting; the numbers from the decision rows; the rule as the charter's own sentence)
-> explanation document
```

**majority**

```
proofs/out/P56/majority/explanations.docx                  sha256 1eb74cd516f9735d5fd5d51138a9527a0c8fcc963717a40c3106962f50ec0c64  registered
shows: meetings explained 8; each paragraph names the count, the threshold, and quotes the charter sentence
```

## P57  directly-follows graph, measured steps, records -> 3D performance map page

```
directly-follows graph (P23), measured steps (P12), records (P6)
-> position (duckdb: mean position of each activity within its case)
-> draw (plotly.graph_objects.Scatter3d: edges by frequency, z = waiting hours)
-> page (plotly.io.write_html(full_html, div_id))
-> 3D performance map page
```

**receipt**

```
proofs/out/P57/receipt/performance_map_3d.html             sha256 ca827be6f5ca0689e4f800684d1005ffb105d9db6aac3be32abd578e8e6bfa61  registered
shows: activities 27, edges 99; slowest to reach: T13 Adjust document X request unlicensed (205.36 h)
```

### coverage

```
practice                                      deliverables  proven  empty  failed  no real input
Architecture management                                  4       4      0       0              0
Continual improvement                                    4       3      0       0              1
Information security management                          4       4      0       0              0
Knowledge management                                     4       4      0       0              0
Measurement and reporting                                4       4      0       0              0
Organizational change management                         4       3      0       0              1
Portfolio management                                     3       3      0       0              0
Project management                                       4       4      0       0              0
Relationship management                                  3       2      0       0              1
Risk management                                          3       3      0       0              0
Service financial management                             4       1      0       0              3
Strategy management                                      3       3      0       0              0
Supplier management                                      3       3      0       0              0
Workforce and talent management                          4       4      0       0              0
Availability management                                  3       3      0       0              0
Business analysis                                        4       4      0       0              0
Capacity and performance management                      4       4      0       0              0
Change enablement                                        5       5      0       0              0
Incident management                                      6       6      0       0              0
IT asset management                                      4       4      0       0              0
Monitoring and event management                          4       4      0       0              0
Problem management                                       4       4      0       0              0
Release management                                       4       4      0       0              0
Service catalogue management                             3       3      0       0              0
Service configuration management                         4       4      0       0              0
Service continuity management                            4       4      0       0              0
Service design                                           3       3      0       0              0
Service desk                                             4       4      0       0              0
Service level management                                 4       4      0       0              0
Service request management                               4       4      0       0              0
Service validation and testing                           4       4      0       0              0
Deployment management                                    4       4      0       0              0
Infrastructure and platform management                   3       3      0       0              0
Software development and management                      4       4      0       0              0
all                                                    130     124      0       0              6
```

### Continual improvement / improvement measurement  proven  (revised 1)

```
shape: the measure before and after, per period
instantiated on: receipt-phase cases per month, mean duration and cases after deadline
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["month"], aggregates=[["count", "*", "cases"], ["avg", "duration_days", "mean_days"], ["sum", "late", "after_deadline"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=measurement_by_month (openpyxl.Workbook.save)
-> improvement measurement
proofs/out/itil/continual-improvement/improvement-measurement/measurement_by_month.xlsx sha256 403198098487f5be6e5379dd2aa472591ac17cbc2a0708d9973286a2db941e73  reproduced
shows: rows 16; first {"month": "2010-10", "cases": 15, "mean_days": 10.38, "after_deadline": 10.0}
```

### Continual improvement / improvement review report  proven  (revised 1)

```
shape: conformance of the work to the model, per group
instantiated on: receipt-phase conformance joined to case departments
-> cases (duckdb: one row per case from the event rows)
-> save_as name=cases (the relation kept under a name for a later join)
-> conformance (P9: pm4py.conformance_diagnostics_token_based_replay)
-> join with=cases, keys=[["case", "case"]] (duckdb JOIN)
-> derive field=fit, fn=contains, of=is_fit, value=true (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["department"], aggregates=[["count", "*", "cases"], ["sum", "fit", "fit_cases"], ["avg", "fitness", "mean_fitness"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> document name=review_report, title=review: fitness to the process model, per department (docx.Document; add_table; docx.document.Document.save)
-> improvement review report
proofs/out/itil/continual-improvement/improvement-review-report/review_report.docx sha256 d743b15186fe1bd6bf852154aed3dca1d1c0d78ac93960bbe4d79aa027ab3697  reproduced
shows: rows 3; first {"department": "Customer contact", "cases": 29, "fit_cases": 29.0, "mean_fitness": 1.0}
```

### Measurement and reporting / KPI report  proven  (revised 1)

```
shape: the agreed indicators per group and period
instantiated on: receipt-phase cases per department
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["department"], aggregates=[["count", "*", "cases"], ["avg", "duration_days", "mean_days"], ["median", "duration_days", "median_days"], ["sum", "late", "after_deadline"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=late_share, fn=ratio, num=after_deadline, den=cases (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> workbook name=kpi_report (openpyxl.Workbook.save)
-> KPI report
proofs/out/itil/measurement-and-reporting/kpi-report/kpi_report.xlsx   sha256 8a39162c0d8b0552e9c44232ab184f6e2e3451854a907223984bd2ee2c36fba0  reproduced
shows: rows 3; first {"department": "Customer contact", "cases": 29, "mean_days": 1.66, "median_days": 0.0, "after_deadline": 1.0, "late_share": 0.0345}
```

### Risk management / risk register  proven  (revised 1)

```
shape: open items exposed beyond their group's norm
instantiated on: open receipt-phase cases against their department's mean duration
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["avg", "duration_days", "mean_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> save_as name=means (the relation kept under a name for a later join)
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "open"]] (duckdb WHERE)
-> join with=means, keys=[["department", "department"]] (duckdb JOIN)
-> derive field=exposure, fn=ratio, num=days_since_last_event, den=mean_days (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> sort by=["exposure"], desc=true (duckdb ORDER BY)
-> workbook name=risk_register (openpyxl.Workbook.save)
-> risk register
proofs/out/itil/risk-management/risk-register/risk_register.xlsx       sha256 6870a2aa4290dba471de3fab3d07aba5fc7dd7750290df446d016678dcecfe9d  reproduced
shows: rows 105; first {"case": "case-416", "department": "General", "channel": "Internet", "responsible": "Resource26", "start": "2010-10-20 10:56:58.348000+00:00", "end": "2010-11-08 13:07:42.360000+00:00", "events": 6, "duration_days": 19.0
```

### Risk management / risk matrix  proven  (revised 1)

```
shape: likelihood against impact per group
instantiated on: receipt-phase departments, share late against mean duration
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["department"], aggregates=[["count", "*", "cases"], ["sum", "late", "late_cases"], ["avg", "duration_days", "impact_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=likelihood, fn=ratio, num=late_cases, den=cases (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> page name=risk_matrix, title=likelihood of lateness against mean duration, kind=scatter, x=likelihood, y=impact_days, size=cases (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> risk matrix
proofs/out/itil/risk-management/risk-matrix/risk_matrix.html           sha256 89bd50c2374beed820a734e6aa4fb5e5d3a8a0203de107dc2dcc1c71e091ee0d  reproduced
shows: rows 3; first {"department": "Customer contact", "cases": 29, "late_cases": 1.0, "impact_days": 1.66, "likelihood": 0.0345}
```

### Risk management / risk report  proven  (revised 1)

```
shape: the register summarized for review
instantiated on: receipt-phase departments
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["department", "channel"], aggregates=[["count", "*", "cases"], ["sum", "late", "late_cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=late_share, fn=ratio, num=late_cases, den=cases (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> document name=risk_report, title=lateness by department and channel (docx.Document; add_table; docx.document.Document.save)
-> risk report
proofs/out/itil/risk-management/risk-report/risk_report.docx           sha256 2cf5fbb078f8b0f8f1b57ce26a1bc00e7118fe8da60aa505bf5674895a8904d5  reproduced
shows: rows 10; first {"department": "Customer contact", "channel": "Desk", "cases": 3, "late_cases": 0.0, "late_share": 0.0}
```

### Supplier management / supplier register  proven  (revised 1)

```
shape: external components relied on, with their license
instantiated on: Node.js maintained dependencies joined to the LICENSE register
-> licenses (re over the Node.js LICENSE file: one row per bundled component)
-> derive field=key, fn=upper, of=component (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> save_as name=lic (the relation kept under a name for a later join)
-> dependencies (re over maintaining-dependencies.md: one row per maintained dependency)
-> derive field=key, fn=upper, of=dependency (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> join with=lic, keys=[["key", "key"]], how=left (duckdb JOIN)
-> select fields=["dependency", "component", "location", "license_heading"] (duckdb SELECT)
-> workbook name=suppliers (openpyxl.Workbook.save)
-> supplier register
proofs/out/itil/supplier-management/supplier-register/suppliers.xlsx   sha256 8b3c044d6c55fb03ef769721906c112980ab0205690ff5273600bc0409f5d0f2  reproduced
shows: rows 31; first {"dependency": "acorn", "component": "Acorn", "location": "deps/acorn", "license_heading": "MIT License"}
```

### Supplier management / supplier performance report  proven  (revised 1)

```
shape: how often each supplied component had to be updated, and when
instantiated on: dependency update commits in the Node.js 22 changelog
-> changelog_commits (re over CHANGELOG_V22.md: one row per commit with release, date, scope, message, author, CVE)
-> filter where=[["scope", "eq", "deps"], ["message", "matches", "^(update|upgrade|bump) "]] (duckdb WHERE)
-> derive field=component, fn=word, of=message, n=2 (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["component"], aggregates=[["count", "*", "updates"], ["min", "date", "first_update"], ["max", "date", "last_update"], ["distinct", "version", "releases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> sort by=["updates"], desc=true (duckdb ORDER BY)
-> workbook name=supplier_performance (openpyxl.Workbook.save)
-> supplier performance report
proofs/out/itil/supplier-management/supplier-performance-report/supplier_performance.xlsx sha256 cd1a20a31dcec5343df3cef9b678fd8eba9310f9e7a444478cec5883e320d4ad  registered
shows: rows 30; first {"component": "googletest", "updates": 31, "first_update": "2024-05-15", "last_update": "2026-05-13", "releases": 13}
```

### Availability management / availability report  proven  (revised 1)

```
shape: achieved availability per period
instantiated on: share of voting members available per TSC meeting
-> decisions (P13: zen.ZenDecision.evaluate)
-> derive field=availability, fn=ratio, num=present_voting, den=present_voting (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> select fields=["meeting", "present_voting", "majority_reachable"] (duckdb SELECT)
-> workbook name=availability_report (openpyxl.Workbook.save)
-> availability report
proofs/out/itil/availability-management/availability-report/availability_report.xlsx sha256 3e9beefff35ce027cb13eb539e1b93736151dcd067da9396dd38f9f85bb8d121  reproduced
shows: rows 8; first {"meeting": "tsc-2023-11-08", "present_voting": 6, "majority_reachable": false}
```

### Availability management / availability plan  proven  (revised 1)

```
shape: the windows in which each service line is supported
instantiated on: Node.js release lines with start, LTS, maintenance and end dates
-> release_schedule (json.loads of nodejs/Release schedule.json)
-> derive field=supported_days, fn=days_between, a=start, b=end (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> workbook name=availability_plan (openpyxl.Workbook.save)
-> availability plan
proofs/out/itil/availability-management/availability-plan/availability_plan.xlsx sha256 321680589d2b9990de07e8086547537471b38d2004dd2f07f49cda65b00824a0  reproduced
shows: rows 27; first {"version": "v0.8", "codename": "", "start": "2012-06-25", "lts": "", "maintenance": "", "end": "2014-07-31", "supported_days": 766.0}
```

### Capacity and performance management / capacity plan  proven  (revised 1)

```
shape: demand per period and group
instantiated on: receipt-phase events per month and department
-> events (P6 rows as a relation)
-> derive field=month, fn=month, of=ts (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> pivot row=month, col=department (duckdb GROUP BY, laid out as a matrix)
-> workbook name=capacity_plan (openpyxl.Workbook.save)
-> capacity plan
proofs/out/itil/capacity-and-performance-management/capacity-plan/capacity_plan.xlsx sha256 fab180bfb9e59e2b5f5d547ca78cd2690d068327e616cf76abd4ee21d85b7a74  reproduced
shows: rows 16; first {"month": "2010-10", "Customer contact": 0, "Experts": 26, "General": 55}
```

### Change enablement / post-implementation review  proven  (revised 1)

```
shape: whether performed changes matched the model
instantiated on: receipt-phase conformance per variant
-> conformance (P9: pm4py.conformance_diagnostics_token_based_replay)
-> derive field=fit, fn=contains, of=is_fit, value=true (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=[], aggregates=[["count", "*", "cases"], ["sum", "fit", "fit_cases"], ["avg", "fitness", "mean_fitness"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> workbook name=post_implementation_review (openpyxl.Workbook.save)
-> post-implementation review
proofs/out/itil/change-enablement/post-implementation-review/post_implementation_review.xlsx sha256 e8ae029d962f6dff01922e51869356f3a0ede233bb4a92d91ede3bdc1c4f0f38  reproduced
shows: rows 1; first {"cases": 1434, "fit_cases": 1425.0, "mean_fitness": 1.0}
```

### IT asset management / lifecycle records  proven  (revised 1)

```
shape: first and last use per asset
instantiated on: receipt-phase resources
-> events (P6 rows as a relation)
-> group by=["resource"], aggregates=[["min", "ts", "first_seen"], ["max", "ts", "last_seen"], ["count", "*", "events"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=active_days, fn=days_between, a=first_seen, b=last_seen (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> workbook name=lifecycle (openpyxl.Workbook.save)
-> lifecycle records
proofs/out/itil/it-asset-management/lifecycle-records/lifecycle.xlsx   sha256 9917d89c410763ad50ec5e22be2226de7b786d18f6edbf1164e18f13ac839fce  reproduced
shows: rows 48; first {"resource": "Resource01", "first_seen": "2010-11-02 12:42:19.582000+01:00", "last_seen": "2011-12-28 15:44:34.115000+01:00", "events": 1228, "active_days": 421.13}
```

### Monitoring and event management / alert list  proven  (revised 1)

```
shape: open items past threshold, decided by a rule
instantiated on: open receipt-phase cases against department means
-> cases (duckdb: one row per case from the event rows)
-> group by=["department"], aggregates=[["avg", "duration_days", "threshold_days"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> save_as name=thresholds (the relation kept under a name for a later join)
-> cases (duckdb: one row per case from the event rows)
-> filter where=[["outcome", "eq", "open"]] (duckdb WHERE)
-> join with=thresholds, keys=[["department", "department"]] (duckdb JOIN)
-> derive field=over, fn=ratio, num=days_since_last_event, den=threshold_days (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> decision_table name=alert, inputs=["over"], outputs=["alert"] (jinja2 -> GoRules JDM; zen.ZenEngine.create_decision; zen.ZenDecision.evaluate)
-> workbook name=alerts (openpyxl.Workbook.save)
-> alert list
proofs/out/itil/monitoring-and-event-management/alert-list/policy.jdm.json sha256 9835ab6f3625f14d66147c79c28d997b9ac1c310a7149f095b956eda0abab2c0  reproduced
proofs/out/itil/monitoring-and-event-management/alert-list/alerts.xlsx sha256 5c51e871f2df40a50fa46d6b0c5b64ced009098dcfd4d8bb8d4abcfa39be4799  reproduced
shows: rows 105; first {"case": "case-10011", "department": "General", "channel": "Internet", "responsible": "Resource21", "start": "2011-10-11 11:45:40.276000+00:00", "end": "2011-11-24 14:37:16.553000+00:00", "events": 4, "duration_days": 44
```

### Problem management / trend analysis  proven  (revised 1)

```
shape: failures per period
instantiated on: late receipt-phase cases per month
-> cases (duckdb: one row per case from the event rows)
-> derive field=late, fn=contains, of=outcome, value=after (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> group by=["month"], aggregates=[["count", "*", "cases"], ["sum", "late", "late_cases"]] (duckdb GROUP BY with count, sum, avg, min, max, list)
-> derive field=late_share, fn=ratio, num=late_cases, den=cases (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> page name=trend, title=share of cases ending after deadline, per month, kind=line, x=month, y=late_share (plotly.express / plotly.graph_objects; plotly.io.write_html | jinja2 table page)
-> trend analysis
proofs/out/itil/problem-management/trend-analysis/trend.html           sha256 90e8251c6c3ff64e4a2a95d7bd81491f46a21b3acb26f56e165a6d1955cabb3c  reproduced
shows: rows 16; first {"month": "2010-10", "cases": 15, "late_cases": 10.0, "late_share": 0.6667}
```

### Infrastructure and platform management / utilization report  proven  (revised 1)

```
shape: use per resource per period
instantiated on: receipt-phase events per resource per month
-> events (P6 rows as a relation)
-> derive field=month, fn=month, of=ts (duckdb expression (closed set: month, year, days_between, hours_between, contains, ratio, length, words, upper, gt, word))
-> pivot row=resource, col=month (duckdb GROUP BY, laid out as a matrix)
-> workbook name=utilization (openpyxl.Workbook.save)
-> utilization report
proofs/out/itil/infrastructure-and-platform-management/utilization-report/utilization.xlsx sha256 e85de9fce1d4b8979ecd6b9ddb63c7ed637121276cd604954ce9f91285de6b02  reproduced
shows: rows 48; first {"resource": "Resource01", "2010-10": 0, "2010-11": 6, "2010-12": 50, "2011-01": 24, "2011-02": 150, "2011-03": 160, "2011-04": 199, "2011-05": 94, "2011-06": 105, "2011-07": 227, "2011-08": 87, "2011-09": 83, "2011-10":
```
## P58  records -> working-day clock -> the term the deadlines imply -> workbook

```
records (P6: case start and deadline dates)
-> calendar (holidays.country_holidays('NL'); numpy.busdaycalendar(weekmask, holidays))
-> count (numpy.busday_count(start, deadline, busdaycal))
-> tabulate (openpyxl.Workbook.save)
-> working days to deadline
```

**receipt-csv**

```
proofs/out/P58/receipt-csv/working_days_to_deadline.xlsx   sha256 4025b71ccaf0ae7dca84bace48f2ec932874ae226d95f6f17287077ea95ef952  registered
shows: cases with start and deadline 1434; Dutch public holidays from the holidays library for [2010, 2011, 2012, 2013]
shows: most common working-day terms (days: cases): [(40, 693), (38, 221), (39, 138)]
shows: first rows [['case-10011', 'General', '2011-10-11', '2011-12-06', 56, 40], ['case-10017', 'General', '2011-10-11', '2011-12-06', 56, 40]]
```

## P59  required actions, units -> obligations per subsection -> workbook, page

```
required actions (P4), units with paths (P1)
-> key (the unit path of each required action's sentence, cut to its first designator)
-> measure (collections.Counter per subsection)
-> tabulate (openpyxl.Workbook.save; plotly.express.bar; plotly.io.write_html)
-> obligations per subsection
```

**usc5-552-doj**

```
proofs/out/P59/usc5-552-doj/obligations_by_subsection.xlsx sha256 276deb268bf1d0ea28ac4e4f72f6a935864f2ff0718af22568a8a689ef3673ea  registered
proofs/out/P59/usc5-552-doj/obligations_by_subsection.html sha256 e44f95f2cf3aaaf1b6b7b1b4722d2e9ff47ce828d1633aa711dc426242fa905f  registered
shows: subsections 10; heaviest (a) with 72 required actions
```

## P60  workbook -> threshold' ; threshold', policy -> match

```
the enumerated rule (P54), policy (P13)
-> read rows (python_calamine.CalamineWorkbook.from_path; CalamineSheet.to_python)
-> derive (the smallest input decided true; monotonicity over the whole space)
-> compare (against the threshold rendered into the decision table)
-> match
```

**majority**

```
proofs/out/P60/majority/roundtrip.json                     sha256 cae43519b49b0d42bca8ccca4e30d5d3a2db75aebbbdd3c7526707a0668fa0d4  registered
shows: threshold read back 10, policy threshold 10, match True; monotone True
```
## P61  sentences, units -> cross-reference graph -> workbook

```
parsed sentences (P1), units with paths (P1)
-> references (re: 'subsection (x)', 'paragraph (n)' patterns in each sentence, resolved against the sentence's own subsection)
-> graph (networkx.DiGraph; in_degree; is_directed_acyclic_graph)
-> tabulate (openpyxl.Workbook.save; json.dumps)
-> cross-reference graph
```

**usc5-552-doj**

```
proofs/out/P61/usc5-552-doj/cross_references.xlsx          sha256 3202988ddf25b58c20324893ebe7f64f68b39b344be8ac187095804b031c39ce  registered
proofs/out/P61/usc5-552-doj/cross_references.json          sha256 386bc896d835269c528ccddb7207a7a2173be1fc01e36fe00733fc470123e262  registered
shows: reference edges 35 between 23 subsections; most referenced [('(b)', 13), ('(i)', 8), ('(ii)', 8)]; acyclic False
```

## P62  log -> handover network -> heatmap page, workbook

```
log (P8)
-> handover (pm4py.discover_handover_of_work_network)
-> chart (plotly.express.imshow over the busiest resources)
-> page (plotly.io.write_html; openpyxl.Workbook.save)
-> heatmap page
```

**receipt-xes**

```
proofs/out/P62/receipt-xes/handover_heatmap.html           sha256 53cadc0d94ae89bac1333f4c53ee70a88c1572b9e7c6de27746570b60c85b819  registered
proofs/out/P62/receipt-xes/handover.xlsx                   sha256 5fea249b89c4eb9a7e08b42be107c72854e80ba296a778e96f104fccd09eb4bd  registered
shows: resource pairs 286; strongest Resource01 -> Resource01 (0.1365)
```

## P63  process tree -> deck

```
process tree (P8)
-> draw (pptx.Presentation: one box per tree node, depth as column, connectors parent to child)
-> deck
```

**receipt-xes**

```
proofs/out/P63/receipt-xes/process_tree.pptx               sha256 34f7ef23e8b2f7f6a1d45389bd82c3e5e75bd22a14ef6f3b2323c7152c35a14e  registered
shows: tree nodes 103, depth 25; root operator ->
```

## P64  3D process page -> labels' ; labels', ordered steps -> match

```
3D process page (P41), ordered steps (P2)
-> read page (re over the html for the Plotly.newPlot data; json.loads)
-> compare (the marker labels against the ordered steps' lemmas)
-> match
```

**usc5-552-doj**

```
proofs/out/P64/usc5-552-doj/roundtrip.json                 sha256 93dc615d0e4ad74fef3c3436749a01adb8d0340f9e1b6c298271dec4fcb3202a  registered
shows: labels read out of the page 24, steps in the order 24, match True
```
### P61  sentences, units -> cross-reference graph -> workbook  (revised chain 1)

```
parsed sentences (P1), units with paths (P1)
-> references (re: 'subsection (x)' in each sentence; paragraph and clause references stay inside their subsection and are not edges)
-> graph (networkx.DiGraph; in_degree; is_directed_acyclic_graph)
-> tabulate (openpyxl.Workbook.save; json.dumps)
-> cross-reference graph
```

## Amendment 4

reason: P61 revised: only subsection references are edges; paragraph and clause references are intra-subsection

```
proofs/out/P61/usc5-552-doj/cross_references.json                      386bc896d835269c… -> f8244167e0545ee4…
proofs/out/P61/usc5-552-doj/cross_references.xlsx                      3202988ddf25b58c… -> 75b43ea314ce165d…
```
### P5  ordered steps -> process model -> process  (evidence after revision 1)

**usc5-552-doj**

```
proofs/out/P5/usc5-552-doj/process.bpmn                    sha256 6209f474a27c67b72b44c6dc345b5d9f06bf2f24c86d485582cb8442e5697d61  reproduced
shows: tasks 24, parallel gateways 2, flows 38; first flow request -> make
```

### P5  ordered steps -> process model -> process  (evidence after revision 1)

**nodejs-governance**

```
proofs/out/P5/nodejs-governance/process.bpmn               sha256 9c83f8172d8fdb4540f84c74140c665ad49f564a9cf2e792fb6eede61449927f  reproduced
shows: tasks 18, parallel gateways 2, flows 29; first flow collaborator -> more
```

### P8  event log -> log -> process model -> process diagram  (evidence after revision 1)

**receipt-xes**

```
proofs/out/P8/receipt-xes/process.pnml                     sha256 9475109f51c0c7e1ba204969aa2cfe6b275b8ed4910e6d31a9f14672ac836725  reproduced
proofs/out/P8/receipt-xes/process.bpmn                     sha256 1f4fc44ee45b11e960caa1da0436ae6da78e13e1ebcfa8c0429fb92f70560a35  reproduced
shows: events 8577, cases 1434, activities 27
shows: span 2010-10-02 to 2012-01-23
shows: discovered from the first half of cases by id; start activities {'Confirmation of receipt': 717}
shows: petri net places 44, transitions 72; bpmn nodes 79
```

### P34  process model -> soundness proof  (evidence after revision 1)

**receipt-xes**

```
proofs/out/P34/receipt-xes/process.pnml                    sha256 e75e4c1e7f195eea21e50295697bf4f0d942476e98567f579c3cf9723ae91ebd  reproduced
proofs/out/P34/receipt-xes/soundness.json                  sha256 c651a83c5d8abd78fbe3f2c42f8f74e800c58da2f930822c8a1ee495c8005a82  reproduced
shows: sound: False; workflow net True, acyclic False, marked graph False
shows: because: not decided structurally
```

### P35  process -> petri net -> soundness proof  (evidence after revision 1)

**usc5-552-doj**

```
proofs/out/P35/usc5-552-doj/process.pnml                   sha256 d4d8dfed1baf10204eb215e5936ca8cd183389052fcc8ec6ffbdf6a5287b2997  reproduced
proofs/out/P35/usc5-552-doj/soundness.json                 sha256 d703bae13849e7def6b18212c62e9141befcf107cd0735d0f2dfca43fef24a7f  reproduced
shows: read back 28 bpmn nodes; petri net places 38, transitions 26
shows: sound: True; workflow net True, acyclic True, marked graph True
shows: because: acyclic marked-graph workflow net: every transition fires exactly once
```

### P35  process -> petri net -> soundness proof  (evidence after revision 1)

**nodejs-governance**

```
proofs/out/P35/nodejs-governance/process.pnml              sha256 dc149693d9a6058f506f6cc561b2e612d8b73c493ad88471aa1d4af3f9de752a  reproduced
proofs/out/P35/nodejs-governance/soundness.json            sha256 845d8a655f04710bdd2943e6881af8f4870b13ac92bdc79da299ea7afd404866  reproduced
shows: read back 22 bpmn nodes; petri net places 29, transitions 20
shows: sound: True; workflow net True, acyclic True, marked graph True
shows: because: acyclic marked-graph workflow net: every transition fires exactly once
```

### P61  sentences, units -> cross-reference graph -> workbook  (evidence after revision 1)

**usc5-552-doj**

```
proofs/out/P61/usc5-552-doj/cross_references.xlsx          sha256 75b43ea314ce165deb70833a912df18c407611dbea4f216912729d3cf0611461  reproduced
proofs/out/P61/usc5-552-doj/cross_references.json          sha256 f8244167e0545ee47bd5fbe3e51150757aa4bc81f9324b5353cfaa194223f674  reproduced
shows: reference edges 12 between 9 subsections; most referenced [('(b)', 13), ('(a)', 6), ('(c)', 1)]; acyclic True
```
