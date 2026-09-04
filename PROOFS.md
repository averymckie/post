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
-> process model (pm4py.objects.bpmn.obj.BPMN (StartEvent, Task, EndEvent, SequenceFlow); pm4py.objects.bpmn.exporter.exporter.apply)
-> process
```

**usc5-552-doj**

```
proofs/out/P5/usc5-552-doj/process.bpmn                    sha256 57d47a0195fa48e6fbdd464771ba39e68f4a8af964fa5190f865e7411f291316
shows: tasks 24, parallel gateways 2, flows 38; first flow request -> make
```

**nodejs-governance**

```
proofs/out/P5/nodejs-governance/process.bpmn               sha256 d446d05dabfa30e83285d58fba8447d1b6f8a781e3262a196ece3c5dfe052dcc
shows: tasks 18, parallel gateways 2, flows 29; first flow collaborator -> more
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
proofs/out/P8/receipt-xes/process.pnml                     sha256 4a1bb1cb575c27f49fe89b644930aa020261fdd1350047428d24e024b8c94f1e
proofs/out/P8/receipt-xes/process.bpmn                     sha256 a5fe7dba55e950afa04eb788a2df0de5a6ac01d09591809d8c7bcc1c9f84ff90
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
proofs/out/P9/receipt-xes/conformance.xlsx                 sha256 0e510617be36e849a3a4d10fca2a5052dca37e14fe99c0de8d648bd8fa38bee5
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
proofs/out/P10/nodejs-governance+nodejs-tsc-minutes/tagged_steps.xlsx sha256 e5b169582feb195f4f2280b6fca0c2e1262848abcac783c881c2a8ada90ae87f
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
proofs/out/P11/nodejs-governance/measured_steps.xlsx       sha256 dfd6e624661834de2cb96f5dffa668fce3037ba9cde66824ce2f9ef3e2b8e113
shows: be: 40
shows: add: 16
shows: share: 13
shows: time: 11
```

**nodejs-tsc-charter**

```
proofs/out/P11/nodejs-tsc-charter/measured_steps.xlsx      sha256 20443e14c9f6228810f23c9a898d4735c5dbdddf1118e017fd1dbd35bb99976e
shows: have: 31
shows: establish: 30
shows: direct: 15
shows: meet: 9
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
proofs/out/P12/receipt-xes+receipt-csv/measured_activities.xlsx sha256 3ddbda555a9b23126beba2d6d2fe38b200e6456db52b9c85f4a07f9473f20fb7
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
proofs/out/P13/charter+roster+minutes/decisions.xlsx       sha256 63ea6ded301ca9d7d1be14bd3e3dedd2e6f2bd757bc2834ecc9131508fa85391
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
proofs/out/P14/usc5-552-doj/dependencies.pptx              sha256 10ccd43ef3377afb1e1e892d0ebac8ff5d959492c43698dac84fb22421e15469
shows: layers 2, boxes 24, connectors 12
```

**nodejs-governance**

```
proofs/out/P14/nodejs-governance/dependencies.pptx         sha256 adc48e4226748f9fd205d0757aa41a465290b6f98b6dfc8337962902def713fb
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
proofs/out/P15/usc5-552-doj/ordered_steps.docx             sha256 f99706ec269b16884af8dbef45a7277208d4372a7a885c8572e4e4c6f2d589d2
shows: paragraphs 50, table rows 13
```

**nodejs-governance**

```
proofs/out/P15/nodejs-governance/ordered_steps.docx        sha256 9d361f69b034842890c34dc8894d4d32e34d659e8976eb545df9d7d18c34964f
shows: paragraphs 38, table rows 10
```

## P16  facts -> workbook

```
facts
-> tabulate (openpyxl.Workbook; Worksheet.append; Workbook.save)
-> workbook
```

**usc5-552-doj**

```
proofs/out/P16/usc5-552-doj/facts.xlsx                     sha256 8709580ecd02e9fee5ffa3950eec6b8825b6f630876e00d7c90c2b9d8fcb90de
shows: rows 1869; first agent usc5-552-doj:u0001:s00#e7 usc5-552-doj:u0001:s00#x5 "agency shall make"
```

**nodejs-tsc-charter**

```
proofs/out/P16/nodejs-tsc-charter/facts.xlsx               sha256 27631b41edcb375bdb8d593f78c07dcb2c680eb7564300ab6f71fa4995a1e7f2
shows: rows 336; first event nodejs-tsc-charter:u0001:s02#e1 guide "Guiding"
```

**nodejs-governance**

```
proofs/out/P16/nodejs-governance/facts.xlsx                sha256 6bae41d3a38439864d0782bc5bc3779afc5b2b0e78d0835a1bf8357b440265ba
shows: rows 815; first agent nodejs-governance:u0002:s00#e56 nodejs-governance:u0002:s00#x54 "Who can nominate"
```

## P17  anything -> digest

```
every deliverable above
-> seal (json.dumps sort_keys; hashlib.sha256)
-> digest
```

**all**

```
proofs/out/P17/all/digests.json                            sha256 d1d5d7ff5c6ad011403f7af0e0bd8e16c51da7889785dabab86135372c516056
shows: deliverables 76; digest 7e078180dc2a01ccd178ec4f264b104089cfd33997a6cd795e3c776156f5d6e4
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
proofs/out/P18/nodejs-governance+tsc-2024-01-17/deck.pptx  sha256 286e17ccf7fdd27f4844e776306ddb0f3c9efb3ee141888dec3cb172ccb0004f
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
proofs/out/P20/nodejs-governance/conformance.xlsx          sha256 c8458192be3ec3b6a683ddb5be287e3bf3eeb1fd95540b110425ea870423f6f7
shows: forced edges respected in the minutes 0, violated 2
shows: VIOLATED tsc-2024-01-17: add discussed before time
shows: VIOLATED tsc-2025-01-08: add discussed before time
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
proofs/out/P21/receipt-csv/deadlines.xlsx                  sha256 e1467d34b9f7cf35925ea8f403c01bca9a30dc8a32fea45057cfcee0de69c160
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
proofs/out/P22/receipt-csv/by_department_and_channel.xlsx  sha256 b7968ad8fb54b5fb8c19d09d3f64da5aceb4b5e19ddc66e50e6d9f8618756ef0
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
proofs/out/P23/receipt-xes/directly_follows.xlsx           sha256 460ec5e13044cf8bbb6d79d9139193e7eaffa6a0a37dba32b273c178aa155352
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
proofs/out/P25/usc5-552-doj/required_actions.docx          sha256 0e9281346d39f73562aa5bff6425336a951fd69b9d0115d152d4a7ce05e68940
shows: table rows 122
shows: agency shall make must make
shows: agency shall separately state must state
shows: agency, in accordance with published rules, shall make must make
```

**nodejs-tsc-charter**

```
proofs/out/P25/nodejs-tsc-charter/required_actions.docx    sha256 eb8a74661f1daf79a8cf9542fd979b06914542c1f34fa638f7a534f2d4b139d8
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
proofs/out/P26/nodejs-tsc-charter+nodejs-tsc-minutes/tagged_steps.xlsx sha256 f72ba52bdb7634024dabd6e65822f9e72857672704a02d1f99cea6d24b7c2a0c
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
proofs/out/P27/receipt-xes+receipt-csv/conformance_by_group.xlsx sha256 2f714e476cbf83529036a91c8ab32a072075830735c1a211cb9126068b3e6653
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
proofs/out/P28/majority+charter-tags/decisions_with_discussion.xlsx sha256 249e153b1b8071167599252588e14b03195e8318defb46cbe5adfa4af114a7f9
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
proofs/out/P29/usc5-552-doj/process.executable.bpmn        sha256 f10a92a5d94b2373a74258f1990d8d8bbee7c6ac687de980a6103e910489253a
proofs/out/P29/usc5-552-doj/execution_trace.xlsx           sha256 824842dce7aab634a91443d9ea353fb2c053d97c83c84b5e71c5c7f0a72729b2
shows: workflow completed: True; tasks run 24
shows: forced edges completed in order: 12 of 12
shows: first tasks ['authorize [u0131:s00#e16]', 'base [u0089:s02#e53]', 'agency [u0089:s02#e59]', 'description [u0131:s00#e44]']
```

**nodejs-governance**

```
proofs/out/P29/nodejs-governance/process.executable.bpmn   sha256 5b792af708eda700afe0b0e26bd6a63ccead9886863286b13fe09c580ef6164a
proofs/out/P29/nodejs-governance/execution_trace.xlsx      sha256 e839a664bca37a1830aba6eadaf9e0acce10287dea735c94e15844e39a057c98
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

## Pins

```
ufal.udpipe 1.4.0.1 · predpatt 1.0.1 · clingo 5.8.2 · clorm 1.6.3 · z3-solver 5.1.0.0 · networkx 3.6.1 · timexy 0.1.3 · spacy 3.8.16 · zen-engine 2.0.2 · Jinja2 3.1.6 · pm4py 2.7.23.8 · pydantic 2.13.5 · duckdb 1.5.5 · markdown 3.6 · lxml 6.1.3 · python-pptx 1.0.2 · python-docx 1.2.0 · openpyxl 3.1.2 · csv-diff 1.2 · PyYAML 6.0.3
```
