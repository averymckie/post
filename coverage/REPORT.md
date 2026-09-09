# Conceptual coverage report

## Purpose

Test whether the frozen framework catalogue conceptually covers independently expressed real-world needs. Ten iterations. Each iteration: one fresh zero-context agent on the opus model selector researches needs and writes construction briefs from the brief in `coverage/agent_prompt.md`; then the session model in this conversation maps every returned case onto the frozen catalogue by hand. Nothing is executed. Libraries, pins and proof chains are not re-run or re-verified.

## Frozen catalogue

Framework master: `7af1d490-frameworkmaster.txt`, sha256 `2ef09333cdb41f82302ce0a12565afd2d653190b444705fb19684e60e25251de`, 12,327 lines. Reference sets used for mapping:

| Set | Members | Meaning |
| --- | --- | --- |
| F | F01 to F38 | Product families |
| O | O01 to O18 | Operation classes |
| C | C01 to C14 | Composition forms |
| A | A01 to A18 | State-space axes |
| V | V01 to V18 | Variation rules |
| R | R01 to R32 | Required claims |
| X | X01 to X12 | Composed family chains |
| P | P1 to P349 | Proof records, cited only as conceptual anchors |

Coverage-test rule, from section 2 of the framework master: the catalogue is frozen. An added family, semantic rule or adapter is an extension proposal and cannot be used to score the catalogue as covering a case. Unsupported requirements stay intact. Failure to find a construction within the search budget means no witness was found within that budget.

## Method per case

1. Each required deliverable gets the smallest matching family, then predecessor families until every branch ends at a source, a typed human input, an environment binding or a named primitive.
2. Each atomic requirement gets an operation class and, where it spans parts, a composition form.
3. The situation and constraints get axis values, the variation rules they trigger, and the R claims those pull in.
4. Each mapped step gets the proof records that already anchor it, or a "family fits, no anchor" mark.
5. The composed whole is compared with X01 to X12 for shape.
6. The stress variation gets the axis or variation rule its changed condition corresponds to, and whether the catalogue expresses the consequence.

Verdicts: COVERED (full construction found), PARTIAL (a named requirement has no construction), UNCOVERED (no family fits the primary deliverable), NO-WITNESS (search budget exhausted without a construction). Extension proposals are listed separately and never counted.

Two things are kept apart: a discovery shortage (the agent could not find enough cases in a category) and a coverage gap (the catalogue cannot construct a case).

## Environment constraint

The session's egress policy blocks WebFetch for all hosts except GitHub (github.com, raw.githubusercontent.com). WebSearch works and returns titles, URLs and snippets. The agent is told this in its ground rules and must label each source READ (original fetched) or SNIPPET (search result only). Snippet-only sources are a recorded limitation of source fidelity, not of the coverage test.

## Files

- `coverage/agent_prompt.md`: the byte-identical prompt given to every iteration's agent.
- `coverage/iterations/NN.raw.md`: the agent's final message, verbatim.
- `coverage/iterations/NN.mapping.json`: the hand-made mapping for that iteration, read by `tally.py`.
- `coverage/tally.py`: counts the mapping files and renders the cumulative block appended to each iteration section.

Mapping record fields: `id`, `origin` (organization | document, the origin-cluster key), `category` (ISIC section or FORD field as the agent classified it), `source_status` (READ or SNIPPET), `deliverables`, `families` (primary first), `O`, `C`, `A` (as `Axx:value`), `V`, `R`, `X` (closest chain or null), `anchors` (P records), `no_anchor` (steps with a family fit but no anchoring record), `verdict`, `blocking`, `stress` (`condition`, `maps_to`, `expressed`, `note`).

## Iteration 1

### Agent run

| Field | Value |
| --- | --- |
| model_selector | opus |
| subagent_type | general-purpose |
| started_utc | 2026-09-09T18:34:12Z |
| duration_ms | 2891175 |
| tool_uses | 69 |
| subagent_tokens | 325891 |
| raw | coverage/iterations/01.raw.md |
| raw_note | final message emitted in two consecutive continuation blocks; concatenated with a single space at the boundary 'minimum population threshold' / 'below which sewershed identification' |
| prompt_file_sha256 | aa6845bceb2af60ccd581ebaac88ecfb33fab835621180b11cf2b85cb32ce2f7 |
| prompt_received_sha256 | a0b8ea9ecebcc18f18342e7b49014ce6b72e189dbdeef20bd7aeaa2689b07abe |
| prompt_identity | identical modulo the file's trailing newline |

### Agent-reported discovery and sampling

| Field | Value |
| --- | --- |
| isic_version | UN ISIC Rev. 4 (2008), 21 sections A-U (SNIPPET); Rev. 5 noted but not used |
| ford_version | OECD FORD, Frascati Manual 2015 Annex, 6 major fields (SNIPPET) |
| seed | 1709478065826606892 |
| randomness_tool | od -An -N8 -tu8 /dev/urandom |
| runtime | CPython 3.11.15 on Linux 6.18.44, drawn 2026-09-09T18:59:13Z |
| sampling_algorithm | random.Random(seed) MT19937; per category pool ordered by case ID; rng.sample(pool, 2) without replacement; categories in inventory order ISIC A-U then FORD 1-6; generator state carried across categories |
| inventory_size | 137 |
| inventory_sha256 | a0622db96a8127b53f4de0adde35c334da74cb27cd3f11a295fbdc0117770e85 |
| categories | 27 |
| selected | 54 |
| read_status_selected | {'READ': 42, 'SNIPPET': 12} |
| source_acquisition | 131 repositories cloned with git from GitHub (allowed host); all other hosts blocked |
| scope_decision | full briefs for the 54 sampled cases only; the 137-case inventory delivered with metadata and read status; proposals and stress variations for the 54 |

Discovery shortages (agent side, kept separate from coverage gaps):
- ISIC B: only 3 of 5 READ; GISTM and EITI on blocked hosts; canonical gmggroup/omf clone held only a licence, content read via mirrors
- ISIC D: OpenADR SNIPPET; OCPP and EEBus read via implementation repositories carrying official schemas, not the standards bodies' documents
- ISIC I: weakest section; 3 READ, one a third-party mirror; both sampled cases (LIVES, FSMA 204) SNIPPET-only
- ISIC L: 3 READ, 2 SNIPPET (PDTF, ISO 19152)
- ISIC N: 3 READ, 2 SNIPPET; both sampled cases (ESCO, HR Open) SNIPPET-only
- ISIC S: 3 READ, 2 SNIPPET; S-01/S-04/S-05 one origin cluster
- ISIC T: severe; 1 of 5 READ; both sampled cases SNIPPET-only
- FORD 2: E2-01 and E2-05 same origin; sample avoided drawing both
- FORD 5: S5-05 SNIPPET-only
- Both classifications are themselves SNIPPET-only sources

### Per-case mapping

| Case | Origin | Cat. | Src | Families (primary first) | O | C | V | R | X | Anchors | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-01 | fiboa community \| fiboa Core Specification | ISIC A | READ | F03 F02 F28 F06 F31 | O03 O04 O09 O16 O02 | C01 C02 | V03 | R02 R18 R12 | - | P95 P261 P325 P302 P204 | COVERED |
| A-02 | AgGateway \| Modus | ISIC A | READ | F03 F02 F09 F13 F10 | O03 O04 O05 O16 O17 | C01 C02 C07 | V16 | R02 R12 R25 | X08 | P95 P261 P242 P259 P184 P282 | COVERED |
| B-05 | Global Tailings Review \| GISTM | ISIC B | SNIPPET | F05 F16 F07 F06 F10 F32 F31 | O07 O08 O16 O18 O15 | C04 C11 | V16 | R28 R30 R25 | X05 | P4 P199 P215 P255 P213 P42 | COVERED |
| B-01 | Global Mining Guidelines Group \| Open Mining Format | ISIC B | READ | F03 F27 F28 F32 F29 | O03 O09 O01 O16 | C06 C13 | V09 | R15 R02 R30 | - | P320 P321 P51 P52 P30 P261 | COVERED |
| C-05 | Open Compute Project \| ONIE | ISIC C | READ | F26 F24 F31 F37 F06 F21 | O14 O16 O17 O11 | C01 C13 C04 | V01 V05 | R13 R28 R08 R05 | X12 | P318 P249 P247 P257 P260 P309 | COVERED |
| C-03 | MTConnect Institute \| MTConnect | ISIC C | READ | F34 F25 F02 F17 | O08 O05 O03 O16 | C08 C07 C03 | V11 | R19 R10 R02 | X09 | P327 P328 P218 P219 P283 P237 | COVERED |
| D-04 | EEBus Initiative (via Enbility) \| SHIP 1.0.1 / SPINE 1.3.0 | ISIC D | READ | F35 F25 F13 F06 F34 F38 | O08 O17 O11 O07 | C03 C07 C12 C04 | V10 V01 V12 | R20 R28 R14 R10 | X10 | P329 P330 P244 P257 P242 | COVERED |
| D-01 | EVRoaming Foundation \| OCPI 2.2.1 | ISIC D | READ | F25 F02 F13 F08 F06 F07 F33 | O17 O04 O08 O05 O03 | C01 C09 C10 C02 | V01 V02 | R10 R12 R27 R02 | X08 | P208 P211 P242 P264 P293 P156 P154 | COVERED |
| E-03 | ODM2 / CUAHSI \| ODM2 Observations Data Model | ISIC E | READ | F02 F28 F17 F03 F16 F33 | O04 O03 O05 O09 O18 | C02 C14 | V03 | R18 R16 R12 R30 | X06 | P325 P326 P95 P213 P184 P282 | COVERED |
| E-04 | FIWARE Foundation \| Smart Data Models dataModel.WasteWater | ISIC E | READ | F03 F01 F29 F37 F31 | O03 O14 O15 O16 | C01 C06 | V03 | R02 R24 R04 R05 | X11 | P95 P301 P307 P140 P304 | COVERED |
| F-02 | BuildingSync consortium (US DOE) \| BuildingSync schema | ISIC F | READ | F03 F31 F05 F32 F21 F10 | O03 O07 O16 O18 O12 | C01 C04 C14 | V16 | R02 R30 R16 R25 | - | P192 P198 P148 P261 P322 P189 | COVERED |
| F-01 | buildingSMART International \| BCF REST API 3.0 | ISIC F | READ | F10 F02 F25 F06 F27 | O04 O17 O16 O03 | C02 C09 C11 | V16 V02 | R25 R09 R12 R02 | X01 | P316 P293 P266 P284 P213 P289 | COVERED |
| G-05 | UN/CEFACT \| UN Transparency Protocol DPP | ISIC G | READ | F31 F02 F06 F14 F05 F29 F32 | O16 O04 O09 O07 O15 O18 | C02 C06 C14 | V16 | R29 R31 R27 R30 | X02 | P247 P262 P250 P296 P213 P282 P323 | COVERED |
| G-02 | OASIS UBL TC \| Universal Business Language 2.x | ISIC G | READ | F03 F05 F02 F37 F32 F31 | O03 O07 O04 O16 O18 | C01 C04 | - | R02 R04 R30 | - | P95 P261 P194 P196 P260 P304 | COVERED |
| H-01 | MobilityData / GTFS community \| GTFS Schedule Reference (2026-04-27) | ISIC H | READ | F03 F05 F02 F32 F11 | O03 O07 O04 O16 O18 | C02 C04 | V03 | R02 R04 R30 | - | P95 P192 P198 P261 P94 P224 P215 | COVERED |
| H-05 | Digital Container Shipping Association \| DCSA eBL / Booking OpenAPI | ISIC H | READ | F13 F08 F02 F07 F25 F33 F06 | O17 O04 O08 O03 O16 | C01 C09 C11 | V01 V16 | R10 R12 R25 R28 | X08 | P263 P262 P259 P244 P247 P311 | COVERED |
| I-04 | Yelp / City of San Francisco / City of New York \| LIVES 2.0 | ISIC I | SNIPPET | F03 F02 F17 F29 F30 | O03 O04 O05 O15 O16 | C02 C04 | V03 | R02 R12 | - | P201 P95 P137 P22 P282 | COVERED |
| I-05 | US FDA \| FSMA 204 Food Traceability Rule | ISIC I | SNIPPET | F15 F02 F33 F17 F09 F34 | O04 O05 O08 O15 O17 | C02 C07 C06 | V03 V17 | R12 R27 R10 | X02 | P177 P153 P160 P342 P58 P16 P224 | COVERED |
| J-04 | OpenAPI Initiative \| OpenAPI Specification 3.2.0 | ISIC J | READ | F01 F25 F31 F03 | O02 O03 O16 O14 | C01 | - | R06 R09 R02 | X11 | P311 P266 P301 P197 P288 P191 | COVERED |
| J-02 | CNCF OpenTelemetry \| Specification: Metrics SDK | ISIC J | READ | F24 F25 F17 F31 F32 | O14 O16 O08 O05 O18 | C01 C04 | V05 | R07 R09 R29 R30 | X11 | P307 P308 P286 P250 P212 | COVERED |
| K-02 | FINOS \| FDC3 Desktop Agent API | ISIC K | READ | F09 F25 F02 F06 F30 F34 | O07 O08 O17 O04 | C03 C04 C07 | V06 | R10 R11 R14 | - | P248 P207 P244 P219 P316 | COVERED |
| K-04 | FIX Trading Community \| FIX Orchestra | ISIC K | READ | F01 F05 F25 F29 F31 F32 | O02 O07 O14 O15 O16 O18 | C01 C04 C14 | - | R06 R04 R24 R30 | X11 | P191 P192 P198 P266 P307 P245 P140 | COVERED |
| L-01 | RESO \| Web API Core + Data Dictionary | ISIC L | READ | F25 F04 F03 F02 F32 F06 | O05 O17 O04 O03 O18 | C01 C02 C05 | V03 | R09 R12 R30 R27 | - | P294 P311 P266 P261 P210 P264 | COVERED |
| L-04 | Property Data Trust Framework \| PDTF schemas | ISIC L | SNIPPET | F02 F03 F31 F06 F29 F32 F08 | O04 O03 O16 O15 O18 | C02 C13 | V13 V16 | R27 R29 R30 R25 | X02 | P296 P247 P264 P86 P136 P261 | COVERED |
| M-01 | ODK \| XForms Specification | ISIC M | READ | F30 F05 F03 F29 F33 F02 | O07 O03 O15 O08 | C05 C04 C11 | V08 V06 | R11 R12 R25 | - | P192 P241 P313 P72 P315 P98 P2 | COVERED |
| M-02 | Research Object community \| RO-Crate 1.x | ISIC M | READ | F03 F02 F04 F33 F06 F29 | O01 O03 O04 O06 O16 | C06 C01 | - | R02 R24 R27 | - | P204 P265 P203 P79 P124 P249 | COVERED |
| N-04 | European Commission \| ESCO | ISIC N | SNIPPET | F02 F04 F23 F03 F32 | O04 O06 O03 O18 | C02 C14 | - | R22 R30 R02 | X07 | P333 P195 P212 P203 P37 P201 | COVERED |
| N-05 | HR Open Standards Consortium \| HR Open 4.1 recruiting/screening | ISIC N | SNIPPET | F03 F02 F09 F33 F06 | O03 O04 O08 O18 O16 | C01 C02 C10 | V13 V17 V16 | R27 R12 R02 | X02 | P342 P30 P197 P261 P95 P264 | COVERED |
| O-02 | Open Contracting Partnership \| OCDS 1.2 | ISIC O | READ | F33 F02 F03 F13 F17 F06 | O03 O04 O05 O18 O16 | C01 C06 C14 | V17 | R12 R27 R02 | X02 | P263 P293 P310 P283 P30 P202 | COVERED |
| O-04 | US GSA \| U.S. Web Design System | ISIC O | READ | F10 F30 F32 F24 F31 | O07 O16 O14 O18 | C04 C11 | V06 V16 | R25 R11 R30 | - | P13 P106 P316 P315 P212 P199 | COVERED |
| P-05 | DCMI \| LRMI | ISIC P | READ | F04 F02 F23 F32 F01 | O04 O06 O02 O18 | C02 | - | R22 R30 R06 | X07 | P333 P203 P195 P204 | COVERED |
| P-03 | Ed-Fi Alliance \| Ed-Fi Data Standard | ISIC P | READ | F03 F02 F25 F06 F32 F37 | O03 O04 O14 O16 O18 | C02 C06 C14 | V07 V13 | R09 R12 R27 R30 | X04 | P311 P210 P201 P261 P264 P345 P260 | COVERED |
| Q-05 | OpenHIE \| Architecture Specification | ISIC Q | READ | F09 F38 F02 F25 F06 F31 | O08 O07 O16 O04 | C01 C07 C10 C13 | V12 V13 | R14 R10 R27 R02 | X12 | P200 P257 P286 P216 P243 P244 P201 | COVERED |
| Q-02 | OHDSI \| OMOP Common Data Model 5.x | ISIC Q | READ | F03 F02 F05 F17 F36 F06 F32 | O03 O04 O07 O05 O18 O16 | C01 C06 C14 | V13 | R12 R06 R23 R30 R27 | X06 | P310 P317 P261 P191 P282 P268 P288 P211 | COVERED |
| R-05 | OpenActive \| Modelling Opportunity Data 2.0 | ISIC R | READ | F06 F02 F25 F11 F34 F33 | O07 O04 O17 O08 O18 | C04 C11 | V13 V17 | R27 R02 R19 | - | P206 P264 P342 P215 P244 | COVERED |
| R-04 | IPTC \| SportsML-G2 3.x | ISIC R | READ | F03 F29 F37 F06 F32 F31 | O03 O14 O15 O16 O18 | C13 C01 | - | R24 R04 R30 | X11 | P260 P95 P261 P307 P140 | COVERED |
| S-04 | iFixit \| Repairability Scoring Rubric v2.2 and guide standards | ISIC S | SNIPPET | F29 F14 F17 F32 F10 F31 | O15 O09 O05 O16 O18 | C06 C01 | V16 | R24 R31 R30 | - | P337 P169 P288 P48 P25 | COVERED |
| S-01 | Open Repair Alliance \| Open Repair Data Standard v0.3 | ISIC S | READ | F03 F02 F17 F06 F31 | O03 O04 O05 O16 | C02 C06 | V03 | R02 R12 | - | P95 P261 P22 P91 P208 | COVERED |
| T-02 | FAO Voices of the Hungry \| Food Insecurity Experience Scale | ISIC T | SNIPPET | F22 F18 F36 F17 F31 F29 | O13 O10 O16 O05 O15 | C04 C01 | V04 | R21 R31 R23 | X06 | P280 P234 P277 P331 P332 P347 | COVERED |
| T-01 | International Labour Organization \| Convention No. 189 | ISIC T | SNIPPET | F01 F05 F08 F29 F14 F17 F06 | O02 O07 O15 O09 O05 | C01 C11 | V16 | R06 R25 R31 | X07 | P4 P191 P25 P259 P156 P58 P171 P196 P292 | COVERED |
| U-01 | IATI Secretariat \| IATI Standard SSOT | ISIC U | READ | F03 F02 F05 F29 F17 F32 F31 | O03 O04 O07 O15 O16 O06 | C01 C02 C06 | V03 | R02 R24 R30 | X11 | P95 P261 P194 P140 P202 P294 | COVERED |
| U-04 | Open SDG partnership \| Open SDG platform | ISIC U | READ | F17 F30 F29 F03 F37 F31 | O05 O09 O15 O16 O03 | C04 C01 | V04 | R31 R11 R24 | - | P282 P24 P31 P76 P96 P43 | COVERED |
| N1-04 | IVOA \| VOTable | FORD 1 | READ | F03 F02 F28 F04 F32 | O03 O04 O06 O16 | C02 | - | R18 R02 R30 | - | P325 P194 P265 P283 P261 | COVERED |
| N1-02 | Materials-Consortia \| OPTIMADE API | FORD 1 | READ | F25 F04 F02 F03 | O05 O04 O03 O17 | C02 C06 | V03 | R09 R02 R12 | - | P311 P203 P210 P294 P285 P201 | COVERED |
| E2-05 | RISC-V International \| SBI Specification | FORD 2 | READ | F24 F25 F06 F31 | O14 O07 O08 O16 | C01 C04 | V05 | R07 R09 R02 | - | P307 P312 P257 P274 | COVERED |
| E2-03 | CHIPS Alliance \| riscv-dv | FORD 2 | READ | F31 F22 F21 F37 F25 | O11 O16 O12 O14 | C03 C01 C05 | V18 | R29 R05 R21 | - | P344 P273 P289 P197 P286 P268 | COVERED |
| M3-03 | PHA4GE \| Wastewater Contextual Data Specification | FORD 3 | READ | F01 F02 F03 F10 F32 F06 F31 | O02 O04 O03 O07 O18 O16 | C02 C11 C14 | V13 V16 | R06 R02 R27 R30 R25 | X05 | P306 P310 P204 P316 P298 P208 | COVERED |
| M3-04 | HL7 International \| FHIR conformance rules | FORD 3 | READ | F31 F25 F01 F06 | O16 O07 O02 O17 | C01 | - | R29 R09 R06 R02 | - | P302 P266 P250 P191 P343 | COVERED |
| A4-05 | FAO \| Open Foris Arena | FORD 4 | READ | F30 F03 F17 F26 F37 F33 F32 | O15 O03 O05 O14 O18 O08 | C01 C04 C14 | V06 V08 | R11 R13 R30 R12 | X06 | P318 P260 P304 P241 P297 P30 | COVERED |
| A4-04 | FoodOn consortium \| FoodOn ontology | FORD 4 | READ | F04 F01 F02 F03 F32 F26 F36 | O02 O04 O06 O14 O18 O10 | C06 C14 C01 | - | R06 R30 R13 R23 | - | P306 P265 P345 P318 P281 P164 | COVERED |
| S5-01 | Psych-DS community \| Psych-DS specification | FORD 5 | READ | F03 F31 F02 F04 F33 | O03 O16 O04 O01 | C02 C04 | - | R02 R12 R29 | - | P95 P137 P194 P203 P189 | COVERED |
| S5-05 | Center for Open Science \| OSF preregistration | FORD 5 | SNIPPET | F33 F10 F29 F02 F31 | O17 O15 O16 O04 | C09 C11 | V16 | R12 R25 R27 | - | P263 P262 P51 P211 P293 | COVERED |
| H6-04 | FAU Erlangen / CIDOC \| Erlangen CRM OWL | FORD 6 | READ | F04 F01 F02 F32 F03 | O02 O04 O06 O18 O16 | C14 C02 | - | R06 R30 R02 | X11 | P306 P281 P288 P296 P261 P203 | COVERED |
| H6-01 | TEI Consortium \| TEI P5 Guidelines | FORD 6 | READ | F29 F01 F37 F32 F31 F03 | O02 O14 O15 O16 O18 | C01 C13 C14 | - | R24 R04 R30 R06 | X11 | P140 P307 P260 P212 P281 P148 | COVERED |

Axis values per case:
- A-01: A01:record, A05:valid time, A10:coordinates, A08:disclose, A11:accepted upstream interpretation, A14:new source
- A-02: A01:record, A02:coordinate, A03:chain, A05:interval, A08:commit, A11:sign-off, A14:policy revision
- B-05: A02:decide, A08:disclose, A11:sign-off, A14:expiry, A16:out-of-envelope, A15:physical validation
- B-01: A01:geometry, A10:coordinates, A03:tree, A12:physical design, A14:migration, A13:alternative
- C-05: A12:infrastructure, A08:actuate, A11:sign-off, A17:embedded, A16:partial effect, A13:alternative
- C-03: A04:streaming, A05:event time, A09:open stream, A07:distributed, A18:concurrency, A16:stale
- D-04: A04:real-time, A07:distributed, A08:actuate, A17:embedded, A16:unavailable, A18:capacity
- D-01: A08:commit, A05:known-at time, A07:distributed, A14:correction, A01:record, A16:stale
- E-03: A01:record, A10:coordinates, A05:interval, A06:interval uncertainty, A14:correction, A03:hierarchy
- E-04: A01:model, A12:generator, A13:optional, A09:partial collection, A02:construct
- F-02: A01:record, A13:requires, A15:structural validity, A14:policy revision, A11:sign-off
- F-01: A07:distributed, A08:propose, A11:recorded runtime input, A18:concurrency, A14:correction, A01:geometry
- G-05: A01:record, A06:interval uncertainty, A08:disclose, A11:sign-off, A14:withdrawal, A10:units
- G-02: A01:record, A13:alternative, A14:policy revision, A11:accepted upstream interpretation, A15:structural validity
- H-01: A01:record, A13:requires, A05:calendar, A09:closed finite domain, A14:policy revision, A16:stale
- H-05: A08:commit, A03:chain, A07:distributed, A11:sign-off, A14:correction, A01:record
- I-04: A01:record, A09:partial collection, A05:known-at time, A16:missing, A02:quantify
- I-05: A01:event, A03:DAG, A05:calendar, A07:distributed, A09:partial collection, A18:latency, A14:expiry
- J-04: A01:text, A11:accepted upstream interpretation, A15:structural validity, A13:optional, A12:software
- J-02: A12:software, A15:behavioral refinement, A16:invalid, A14:policy revision, A02:qualify
- K-02: A04:event-driven, A07:distributed, A08:actuate, A18:concurrency, A11:recorded runtime input, A16:partial effect
- K-04: A01:rule, A13:requires, A14:migration, A12:generator, A11:accepted upstream interpretation
- L-01: A09:paginated snapshot, A07:replicated, A14:policy revision, A08:disclose, A01:record
- L-04: A11:sign-off, A08:disclose, A14:migration, A01:record, A06:four-state evidence
- M-01: A17:offline, A13:requires, A04:interactive, A07:offline, A11:recorded runtime input, A14:migration
- M-02: A01:artifact, A03:tree, A17:offline, A14:migration, A08:disclose
- N-04: A01:entity graph, A03:DAG, A14:policy revision, A11:accepted upstream interpretation, A06:probability
- N-05: A01:record, A07:distributed, A08:disclose, A14:withdrawal, A11:recorded runtime input
- O-02: A01:event, A05:known-at time, A07:distributed, A14:correction, A09:partial collection, A11:accepted upstream interpretation
- O-04: A08:approve, A11:sign-off, A03:hierarchy, A14:expiry, A15:structural validity
- P-05: A01:entity graph, A14:expiry, A11:accepted upstream interpretation, A09:unknown coverage
- P-03: A01:record, A07:distributed, A08:disclose, A13:optional, A14:migration
- Q-05: A04:event-driven, A07:distributed, A17:federated, A16:unavailable, A08:disclose, A06:probability
- Q-02: A01:record, A17:federated, A11:accepted upstream interpretation, A05:valid time, A14:migration, A08:disclose
- R-05: A08:disclose, A11:sign-off, A05:calendar, A16:stale, A07:replicated, A09:unknown coverage
- R-04: A13:alternative, A12:office/media, A14:correction, A08:disclose, A04:event-driven
- S-04: A12:office/media, A10:exact, A14:policy revision, A11:adjudication, A16:partial effect
- S-01: A01:record, A09:partial collection, A08:disclose, A11:recorded runtime input, A13:optional
- T-02: A06:probability, A15:statistical performance, A05:interval, A11:recorded runtime input, A16:invalid, A09:partial collection
- T-01: A01:text, A03:hierarchy, A08:approve, A11:sign-off, A05:calendar, A10:units
- U-01: A01:record, A09:unknown coverage, A07:distributed, A14:policy revision, A03:DAG
- U-04: A01:quantity, A10:exact, A09:partial collection, A08:disclose, A13:numeric parameter, A12:UI
- N1-04: A01:record, A10:coordinates, A05:uncertain clock, A14:policy revision, A17:offline
- N1-02: A17:federated, A09:partial collection, A01:record, A07:distributed
- E2-05: A17:embedded, A08:actuate, A13:numeric parameter, A03:state machine, A16:invalid, A07:local transactional
- E2-03: A06:probability, A15:behavioral refinement, A13:requires, A12:software, A16:conflicting, A11:accepted upstream interpretation
- M3-03: A01:entity graph, A11:adjudication, A14:new source, A08:disclose, A03:chain
- M3-04: A15:behavioral refinement, A11:accepted upstream interpretation, A13:alternative, A02:qualify
- A4-05: A17:offline, A13:requires, A12:infrastructure, A14:migration, A11:recorded runtime input, A15:structural validity
- A4-04: A01:entity graph, A14:withdrawal, A11:adjudication, A06:classical, A09:partial collection
- S5-01: A01:record, A15:structural validity, A11:accepted upstream interpretation, A13:mandatory, A17:offline
- S5-05: A05:known-at time, A08:commit, A11:sign-off, A14:correction, A01:artifact
- H6-04: A01:entity graph, A14:policy revision, A11:adjudication, A06:classical, A05:valid time
- H6-01: A01:text, A06:four-state evidence, A13:alternative, A14:expiry, A12:office/media, A11:adjudication

Mapping notes:
- **A-01**: Two-part identity (collection,id) and licence relocation on merge map to the boundary identity field and F06 release contracts; determination:datetime as observation end-time is A05 valid time with HG01 basis. Category vocabulary unpublished = unresolved input retained.
- **A-02**: Submit/result pairing is an intent and receipt pair (P242); method list governance is a versioned registry with review (F10). Turnaround target is motivational prose and stays unresolved.
- **B-05**: Brownfield flexibility (4.7/5.7) is a declared exception, expressible as a recorded gate decision with justification (P199). Physical engineering evidence sits under R28/R16 and is not constructed by the catalogue.
- **B-01**: Recursive composites are the grammar's recursive composition; version declaration and refusal of unsupported versions is the HG00 envelope schema version rule.
- **C-05**: Per-platform ports are a variation model (F37); divided ODM/operator authority is the A08/A11 split; remote install irreversibility is V01 with receipt reconciliation.
- **C-03**: Filter suppression means absence of a report is not absence of change: expressible as the boundary coverage field and HG01 basis. Buffer overrun detection is C08 correction plus HG05 gap preservation.
- **D-04**: Fuse limit across devices is the R14 conservation/capacity invariant; pairing trust is authority state; safe fallback on peer loss is C07 timeout_path with C04 default.
- **D-01**: REMOVED status instead of deletion is a lifecycle label (P208) under append-only records; private-location exclusion is F06 release policy (P264); tariff at session start is bitemporal selection (P211).
- **E-03**: Two temporal regimes (dense series, sparse specimens) are A04/A05 profiles on one identity spine; annotations that never mutate values are HG07 append-only evidence.
- **E-04**: Template-generated repositories are a generator (F37 territory); one model to several audience outputs is X11. The needed discharge-compliance profile is a feature-model requiredness set, which the catalogue expresses and the source lacks.
- **F-02**: Examples as a regression gate on the schema is P148 traceability; per-use-case required elements is scoped applicability (P192/P198); partial Level 2 translation is a declared unsupported path (HG05).
- **F-01**: Immutable comments with corrections as new comments is HG07; viewpoint to element GUID is a cross-system identity edge whose stability is a boundary identity obligation.
- **G-05**: Claim plus criterion plus evidence plus issuer is F31's claim ledger with signed envelopes; accuracy ranges are propagated uncertainty (P323); comparability across issuers is exact meaning and unit checks (P282).
- **G-02**: Three validation authorities are three conjunctive obligations (schema, cross-field rules, code-list membership); customisation by configuration rather than forking is the variation model.
- **H-01**: Conditionally Required is scoped applicability (P192/P198) and the validator must explain the verdict, which P200 supplies. Feed expiry is the boundary time/freshness field.
- **H-05**: Array-order preservation is canonical serialization (P262); endorsement chain is an append-only commitment log (P263); party identification tightening along the lineage is per-state requiredness (F07). Legal possession mechanism stays an unresolved external dependency.
- **I-04**: Municipal business to platform listing matching is probabilistic linkage with reviewed candidates (P201); optional violations file is a declared partial population with graceful rendering.
- **I-05**: Lot linkage through transformation is BOM-style explosion and reconciled movement (P160/P177); the 24-hour clock including weekends is a calendar profile on a retrieval obligation (P224/P58); retention is P342.
- **J-04**: Prose authoritative over JSON Schema is F01's document authority and scope variation; agreement of independent generators is two-engine equivalence (P197). Optional by default is A13.
- **J-02**: Degrade-never-fail is C04 default with HG05 state propagation; cross-language semantic equivalence is observable trace comparison (P286); status-scoped conformance is the promotion ledger with requirement versions (P250).
- **K-02**: Intent resolution by declared context types is a typed verifier over a permitted action map (P248); self-initiated changes still producing events is idempotence under A08.
- **K-04**: Conditional DSL rules are controlled-syntax typed rules (P191) with scenario scope (P192); one source to docs and bindings is X11; a generated conformance suite is P266.
- **L-01**: Server-driven paging and replication convergence are stable-snapshot and count reconciliation (P294); two independently versioned standards cited together is the boundary schema-version field with two entries.
- **L-04**: Verified versus unverified fields is the four-state evidence axis; form-position labels are explicit field mapping (P86/P136); selective disclosure is P264. Liability for a wrong verified claim is governance outside any product and stays unresolved.
- **M-01**: Requiredness as an expression over other answers is scoped applicability; evaluation order of dependent expressions is forced precedence (P2); resumption re-deriving computed state is deterministic replay (P241).
- **M-02**: Offline interpretability is bounded resolution without network (P265); crate-in-crate is the grammar's recursive composition with licence and authorship inherited as boundary fields.
- **N-04**: Skills graph is the competency graph (P333); cross-language matching of CV and vacancy is probabilistic linkage; release diffs are semantic-change candidates (P195).
- **N-05**: Parallel JSON and XML must not diverge: round-trip and two-engine equivalence (P30/P197); erasure of one node without breaking the hire record is bounded erasure with object lineage (P342).
- **O-02**: Immutable releases are append-only commitments (P263); null-as-deletion merge is a declared patch semantics (P293/P310); mandatory timezones are the boundary time field.
- **O-04**: Approval with recorded reasoning at each rung is F10's version-bound review record; accessibility gates are R11 acceptance; deprecation windows are change propagation with expiry.
- **P-05**: Alignment to an external competency framework is a required input the catalogue leaves as a named external dependency; document currency ('OLD STUFF') is the governing-version obligation of F01 (P204).
- **P-03**: Bulk and API ingestion converging on one student identity is overlapping-source reconciliation (P210); descriptors as local value sets are the variation model; domain-scoped versioning is dependency closure (P345).
- **Q-05**: Explicit prerequisites are gate decisions with a deterministic explained resolver (P200); component replaceability is C13 with refinement counterexamples (P286); alerts to people carry consent constraints under F06.
- **Q-02**: ETL conventions as prose in a CSV are exactly F01's controlled-language obligation (P191) and the catalogue's rule that meaning is a boundary field beyond schema; last-known fields versus history is the bitemporal distinction (P211). Site deviation declaration is P288 attribution.
- **R-05**: Consent as a precondition for publishing leader qualifications is authorization with purpose and expiry (P206/P264); perishable sessions are freshness-fenced dispatch (P244).
- **R-04**: Core plus extension is the feature model's mandatory core with alternative extensions (P260); rights and embargo from the news envelope are F06/F08 boundary fields; live corrections are versioned revisions.
- **S-04**: Guides are documents under a presentation contract (fixed markup colour order); the score is a declared exact calculation; inter-assessor agreement is disagreement and reliability measurement (P288); rubric version travels with each score as the boundary schema version.
- **S-01**: Graded obligation under busy collection conditions is a declared partial population (V03) reported in aggregates; comparability rests on codelist identity registries.
- **T-02**: Validation as a gate that can fail is HG05 (failed state published, no estimate promoted); recall period reported with the estimate is the boundary time field.
- **T-01**: Written particulars are an agreement record rendered as a bilingual document (F08/F29); rest and stand-by hours are calendar-clocked ledgers (P58/P156); the four-hop delegation chain is inherited permissions and prohibitions (P292/P196). Enforcement outcomes in private homes are not a product and are retained as unresolved.
- **U-01**: Three-layer conformance (schema, codelists, ruleset) is a conjunction of obligations; single-source documentation is X11; funder-to-implementer chains are look-through relationship graphs (P202).
- **U-04**: A zero target silently reset to 0.001 is a silent numeric conversion the execution contract forbids (HG00/HG02 no silent conversions; O09 exact quantities). Proxy flags are declared evidence-basis qualifiers.
- **N1-04**: Dangling TIMESYS references are shape and completeness validation (P194); external vocabulary dependence is a pinned sealed registry (P265); coordinate frames are reference metadata (P325).
- **N1-02**: Provider-scoped identity is the boundary identity scope; provenance-preserving federated results are source-linked answers (P285); cross-provider duplicates of one physical structure are a linkage decision (P201).
- **E2-05**: Thin fit. Boot-time setup before runtime calls is a readiness barrier (P257) with pre-state in the boundary state field; reserved-bits handling is the declared exceptions field (reject versus ignore must be stated). The catalogue's vocabulary is organisational and stretches to a firmware privilege boundary without contradiction but without support.
- **E2-03**: Seeded reproducible random generation is GP01's recorded seeds and settings; ISA-subset configuration is a finite feature model (P273); DUT versus reference mismatch localisation is refinement counterexample reporting (P286). Thin on the hardware side.
- **M3-03**: Term identity surviving renaming across template and repository is the identity chain with ontology IDs; governed term growth is a reviewed change process (F10/F32); sewershed re-identification is a protected-unit limit (P298).
- **M3-04**: Scoped conformance is the boundary contract: a CapabilityStatement is a producer guarantee and P302 checks it against consumer assumptions before exchange. Contextual readings of SHALL/SHOULD are the accepted-meaning field, which weakens mechanical checking exactly as the catalogue predicts.
- **A4-05**: Conditional requirement sets per provider are a feature model with requires/excludes (P304); survey design as a user activity is a configurator; cycle-to-cycle variable mapping is typed column lineage (P297); byte-identical reprocessing is deterministic replay.
- **A4-04**: Reproducible imports are a sealed pinned registry (P265); deprecation redirects are dependency closure with supersession (P345); free-text ingredient recognition is a learned or lexical mapping under F36/P164 with recall as an empirical claim.
- **S5-01**: Metadata authoritative over data columns is HG02 whole-input validation with reject-unknown-fields; named addressable rules with defaults are a rule set whose configurability is a declared profile.
- **S5-05**: Frozen snapshot with digest and persistent identifier is an append-only commitment (P263/P51); amendments that point to the original are version-bound corrections (P293). That the artefact proves commitment time and not the world's event time is the known-at versus valid-time distinction (P211).
- **H6-04**: Contradictory attributions coexisting with their asserters is F01's retained unresolved alternatives plus origin-aware support groups (P296/P281); dated namespaces are pinned schema versions; the base standard behind a blocked host is a missing accepted-source input.
- **H6-01**: One ODD source to prose and schemas is X11; per-project customisation is the variation model with exemplars as accepted configurations (P260); encoded certainty and responsibility are the evidence-basis and attribution fields, which must survive rendering (P337-type preservation).

### Stress variations

| Case | # | Changed condition | Maps to | Expressed |
| --- | --- | --- | --- | --- |
| A-01 | 1 | boundaries submitted by financially interested parties; determination:method becomes a claim | A11:recorded runtime input, HG01 basis CANDIDATE vs OBSERVATION, P247, P296 | yes: catalogue separates a mention/claim from an observation and requires evidence binding before promotion |
| A-02 | 2 | issuing laboratory ceases trading with results outstanding | C10, P243, P256, A16:unavailable | yes: partially completed workflow with declared compensation and offboarding; result portability is a new obligation the catalogue names via P205 reuse eligibility |
| B-05 | 3 | downstream population grows tenfold after classification | A14:expiry, P255, P213, HG06 | yes: catalogue treats the classification as state with a review clock; a stale basis invalidates the disclosed claim |
| B-01 | 4 | beta v2 stabilises with incompatible changes mid-project | A14:migration, P261, P245, HG00 schema version | yes: explicit migration and version pinning; reader refuses rather than misreads |
| C-05 | 5 | ODM abandons a port still in fleet use | A14:withdrawal, P345, P256, F16 | yes: lost support invalidates the port's evidence; custodianship becomes an orphan-asset maintenance obligation |
| C-03 | 6 | agent restarts and resets its sequence-number timeline | P328, P283, HG00 producer/environment version, A16:stale | yes: envelope carries producer instance and timeline identity so restart is distinguishable from overrun |
| D-04 | 7 | two home energy managers both claim authority | V12 shared-state owner, R14, C03 interference | yes: catalogue requires a named shared-state owner; EEBus lacks the arbitration rule the catalogue demands |
| D-01 | 8 | tariff published mid-session | P211, A05:known-at time, C09 | yes: tariff version pinned at session start by bitemporal selection |
| E-03 | 9 | instrument found miscalibrated retroactively over two years | P213, HG06, A14:correction | yes: equipment provenance gives precise invalidation scope; downstream notification is the exact dependency propagation rule |
| E-04 | 10 | regulator mandates cross-city comparison | F37 feature model requiredness, V rules, P304 | yes: profile-specific required sets are the catalogue's ordinary variation mechanism |
| F-02 | 11 | owner contracted Level 2, delivered file supports only Level 1 | P189, A08:approve, F31 declared level | yes: declared audit level becomes an acceptance gate with recorded authority |
| F-01 | 12 | model re-exported, element GUIDs regenerate, viewpoints dangle | HG06, P213, P345, A14:backend replacement | yes: changed upstream identity invalidates every dependent viewpoint; the catalogue cannot impose GUID stability on the authoring tool either, and says so as a blocked edge |
| G-05 | 13 | issuer revokes one credential after purchase; mixed-validity passport | P213, HG05 mixed states, A14:withdrawal | yes: per-claim invalidation with retained history; surfacing partial revocation to a buyer is F30 rendering of HG05 states |
| G-02 | 14 | jurisdiction mandates a field the base schema lacks; CVA cannot add elements | A13 variability limit, V15, HG05 unsupported | yes: catalogue records the unsupported requirement as blocked rather than silently extending the schema |
| H-01 | 15 | two agencies merge; agency and route identifiers change | P208, P284, P212, A14:migration | yes: versioned identity mapping with continuity records; the catalogue names the deprecation mechanism the format lacks |
| H-05 | 16 | holder of title becomes unreachable; cargo unclaimable | C07 timeout_path, C11 human boundary, A16:unavailable | yes: a defined escalation path with authority that preserves chain integrity; the catalogue keeps the path blocked until such authority exists |
| I-04 | 17 | merged jurisdictions with different scoring scales in one feed | P282, A10:units, HG02 meaning | yes: scale identity is part of meaning; the catalogue refuses comparison across undeclared scales |
| I-05 | 18 | upstream partner refuses to share KDEs | A09:partial collection, V03, HG02 missing source coverage | yes: blind lots are a named coverage gap; obligation on the weaker party is recorded as a blocked path, not resolved |
| J-04 | 19 | generator vendor treats JSON Schema as authoritative, violating R4 silently | P197, P288, F01 authority | yes: independent-engine disagreement is a first-class measured outcome, not silent |
| J-02 | 20 | a Development-status requirement changes after certification | P250, P212, A14:policy revision | yes: evidence is scoped to requirement versions and invalidated on revision |
| K-02 | 21 | bridged desktops with app directories that disagree about context types | C02 join scope, P210, R14 | yes: directory reconciliation is an identity and completeness reconciliation across sources |
| K-04 | 22 | venue changes a scenario rule with 24 hours notice | P212, P346, P266 | yes: affected-case population and controlled regeneration of the conformance suite |
| L-01 | 23 | MLS revokes a consumer's licence; replicated data already held | V17, P342, A08:disclose | yes: replica inventory and deletion propagation are named obligations the transport spec omits |
| L-04 | 24 | an authoritative source's verified data was wrong | P213, A11:adjudication, HG06 | yes: invalidation and attribution are expressed; liability assignment is not a product property |
| M-01 | 25 | form definition edited while devices hold partial records | P245, A14:migration, V08 | yes: explicit migration between form versions before replay |
| M-02 | 26 | external identifier service shuts down | P265, A16:unavailable, HG00 identity | yes: inline human-readable labels beside identifiers is the sealed-registry pattern |
| N-04 | 27 | two skill concepts merged in a release | P284, P212, A14:migration | yes: reconstructed equivalence classes with reversible identity decisions |
| N-05 | 28 | right-to-erasure request between assessment and offer | P342, V17, A14:withdrawal | yes: bounded erasure with lineage is the catalogue's own rule |
| O-02 | 29 | a release containing personal data must be withdrawn; immutability conflicts with erasure | P263 vs P342, F33 explicit contracts, HG07 | yes: the catalogue holds both rules and makes the conflict a declared retention/erasure contract; copies already held by consumers are outside any construction |
| O-04 | 30 | urgent accessibility fix versus approval latency | C04 priority, P244, F10 recorded rationale | yes: an expedited guarded path that still records authority and reasoning |
| P-05 | 31 | host vocabulary schema.org deprecates a relied-on term | P345, P195, A14:withdrawal | yes: dependency closure names the affected published pages; host beyond control is a blocked edge |
| P-03 | 32 | district changes vendor mid-year | X04, P210, A14:backend replacement | yes: system replacement with data and operating-model migration is a catalogued chain |
| Q-05 | 33 | client registry offline during an emergency; care continues | C07 timeout_path, C10, P242, P243, A16:unavailable | yes: a declared degraded mode with later reconciliation is required by the catalogue and absent from the source |
| Q-02 | 34 | site populates gender_concept_id with gender identity despite scope restriction | P282, P288, HG00 meaning field | yes: schema-valid wrong-meaning is the catalogue's named adverse case; an accepted mapping per site is the mitigation |
| R-05 | 35 | leader withdraws consent after publication; indexers hold copies | P342, V17, A09:unknown coverage | yes: replica inventory is required; unknown downstream copies stay an open coverage state rather than a claimed erasure |
| R-04 | 36 | new sport without an extension at a major event | C13, A16:unsupported, HG05 | yes: core-only degradation is an explicit unsupported-extension path with retained partial output |
| S-04 | 37 | two internally different devices share one model number | HG00 identity scope, P208, A01:entity graph | yes: identity must scope to the production variant; the catalogue rejects joins on display labels |
| S-01 | 38 | a group records only three fields | V03, A09:partial collection, HG05 | yes: comparability degrades explicitly and the aggregate carries the coverage state |
| T-02 | 39 | items fail Rasch validation three years running | HG05, F31 open claim, A16:invalid | yes: publishing the failure instead of the estimate is the catalogue's default; what to do instead stays an open requirement |
| T-01 | 40 | worker's immigration status tied to the employer makes rights nominal | A08 authority, C11 | no: no construction: the constraint is a social power asymmetry outside any product; the catalogue can only record missing authority as a blocked path, which does not express the consequence |
| U-01 | 41 | a publisher stops publishing mid-programme | A09:unknown coverage, HG01 basis, P294 | yes: no publication versus no activity is a coverage state, never inferred as absence |
| U-04 | 42 | target is genuinely zero (elimination goal) | P282, O09 exact, HG02 | yes: the catalogue rejects the substitution rather than displaying it; an explicit unsupported-target state replaces the rewrite |
| N1-04 | 43 | refframe vocabulary revision changes a term's meaning | P195, HG06, HG00 schema version | yes: vocabulary version pinned in the document boundary; a semantic change is a candidate invalidation |
| N1-02 | 44 | same structure at three providers returns triplicates | P201, P210, C02 scope | yes: deduplication is a reviewed identity decision, not a client heuristic |
| E2-05 | 45 | one firmware ignores rather than rejects non-zero reserved bits | HG02 declared exception behaviour, GP01 adverse guards, P274 | yes: generated adverse inputs across implementations expose reject-versus-ignore divergence |
| E2-03 | 46 | the reference model, not the DUT, has the bug | I-class oracle independence, P197, accepted semantics as third reference | yes: the catalogue never treats one engine as ground truth; a second reference or the accepted specification text is the required third opinion |
| M3-03 | 47 | novel pathogen needs fields mid-outbreak | P275, P208, A14:new source, F32 provisional term | yes: provisional terms as unresolved dimensions with a mandatory reconciliation deadline |
| M3-04 | 48 | two conformant systems with disjoint support cannot exchange | P302, R02, HG00 | yes: the negotiation step comparing statements is the catalogue's typed handoff check |
| A4-05 | 49 | ministry loses cloud budget; hosting moves on short notice | X04, P318, A14:migration | yes: deployment realisation with migration of the survey definition as the identity-bearing asset |
| A4-04 | 50 | upstream NCBITaxon retires a taxon FoodOn imports | P345, P265, A14:withdrawal | yes: pinned import protects releases; supersession propagates through the closure |
| S5-01 | 51 | a column is added after deposit without metadata | HG02, P189, P275 | yes: blocked at the gate; the authoring-time prompt is question generation for a missing dimension |
| S5-05 | 52 | registration filed after data collection but before analysis | P211, HG01 no promotion, A05:known-at time | yes: the catalogue states the limitation exactly: a commitment timestamp cannot be promoted to evidence about collection order without independent observation |
| H6-04 | 53 | two institutions integrate across CRM namespace versions | P261, P245, P208 | yes: explicit cross-version alignment as a dialect migration |
| H6-01 | 54 | a project's customisation uses a now-deprecated element | P212, F32 deprecation register, A14:expiry | yes: the well-handled case: scheduled deprecation with project-controlled schema is exactly the catalogue's change-propagation posture |

### Composed wholes proposed by the agent, compared with X01 to X12

| Composed system | Members | Families | Closest chain | R | Note |
| --- | --- | --- | --- | --- | --- |
| CS-1 Field-to-payment assurance chain | A-01 A-02 A4-03 G-05 | F28 F03 F13 F31 F02 F38 | X02 | R14 R02 R30 | Field identity across four sources and observation-time versus operation-time is the joint identity and time contract of F38; claim with evidence is F31. Covered as an X02-style admission-to-claim chain. |
| CS-2 Repair evidence loop | S-01 S-04 G-05 | F17 F14 F31 F38 | X02 | R14 R31 | Product-category identity across codelists and passports; rubric version stamping. Covered. The agent's own caveat that ORDS and iFixit share an origin holds. |
| CS-3 Outbreak-to-plate traceback | I-05 G-01 M3-03 A4-04 | F15 F34 F04 F02 F38 | X05 | R14 R19 R27 | Detection to traceback query is X05 shape; lot identity through transformation and food-term identity are the shared identity contract. Covered; FSMA side rests on SNIPPET requirements. |
| CS-4 Building lifecycle handover | F-01 F-02 F-04 F-05 | F10 F16 F02 F27 F38 | X03 | R14 R17 R30 | Design issue to as-built element to operations is X03 (configured product to maintained asset); element identity across revisions is the unresolved edge the catalogue blocks explicitly. Covered. |
| CS-5 Mobility trip across operators | H-01 H-02 H-03 H-06 | F11 F12 F13 F06 F38 | X08 | R14 R10 R27 | Stop and place identity across feeds and a trip identifier surviving operator boundaries are F38 joint identity; booking and payment are F13 with receipts. Covered. |
| CS-6 Clinical study definition to evidence | M3-01 M3-04 Q-02 S5-05 | F01 F03 F22 F33 F36 F38 | X06 | R21 R23 R14 | Frozen analysis plan versus executed analysis is X06 (research question to campaign and report) with P263 commitments. Covered. |
| CS-7 Public money to public outcome | O-02 U-01 S-03 U-04 | F02 F14 F17 F33 F38 | X08 | R14 R12 | Organisation identity across four schemes is the hard join (P202/P201); append-only records. Covered; identity resolution is the named risk. |
| CS-8 Heritage object across institutions | H6-04 R-03 R-01 H6-01 H6-02 | F04 F01 F29 F02 F38 | X11 | R06 R24 R14 | Contested attribution shown with image, transcript and archival record is retained-ambiguity presentation (P281/P296). Covered. |
| CS-9 Energy at the meter boundary | D-01 D-03 D-04 D-02 | F35 F13 F25 F38 | X10 | R20 R14 R28 R10 | EVSE identity across OCPP and OCPI and the physical fuse limit as the shared invariant are R14 plus V10. Covered. |
| CS-10 Survey instrument to public statistic | M-01 S5-04 A4-05 S5-03 S5-02 U-05 | F30 F03 F17 F29 F38 | X06 | R14 R24 R31 | Variable identity from question to aggregate is typed column lineage (P297). Covered. |
| CS-11 Water safety across the chain | E-01 E-03 M3-03 E-02 | F21 F28 F34 F19 F38 | X09 | R16 R18 R19 R14 | Hydraulic model locating contaminant travel plus observations and early genomic signal is X09 (spatial observation to field response) with F21 simulation. Covered. |
| CS-12 Skills-to-work chain | N-04 N-05 P-01 P-05 | F23 F02 F04 F38 | X07 | R22 R30 R14 | Skill concept URI stability across releases is the identity thread (P333/P212). Covered; two members are SNIPPET-only. |
| CS-13 Household support pathway | Q-03 T-01 T-02 Q-05 | F18 F08 F09 F06 F38 | X02 | R27 R14 | Household identity without a surveillance record and consent for contact are F06 purpose-bound release (P206/P264). Covered; composition partly fills the ISIC T discovery shortage rather than a catalogue gap. |
| CS-14 Assurance of a claim, generically | G-05 M3-04 J-05 O-01 | F31 F06 F29 F38 | - | R29 R14 | Claim plus criterion plus evidence plus declared capability is F31's product contract restated; C2PA media binding is P247 signed envelopes. Covered as a family, not a new chain. |
| CS-15 Irreversibility register (pattern library) | O-02 S5-05 H-05 B-05 | F04 F33 | - | R12 R27 | A pattern library is knowledge navigation over four F33 mechanisms; the catalogue's own answer to 'this record must not be quietly changed' is HG07 plus P263/P293/P342. Covered as documentation, not a system. |
| CS-16 Conditional-obligation pattern library | H-01 M-01 K-04 A4-05 F-02 | F05 F04 | - | R04 | Five encodings of 'required only sometimes' all map to scoped applicability with explained verdicts (P192/P198/P200). The agent's finding that flat requiredness is insufficient is the catalogue's premise. |

### Generators proposed by the agent, compared with F37

| Generator | Families | Anchors | Note |
| --- | --- | --- | --- |
| GEN-1 Conditional-requirement validator generator | F37 F05 F31 | P198 P200 P304 P305 P303 | Requiredness rules in a small notation to a validator that prints condition, inputs and verdict: a configurator over a finite obligation relation with explained resolution. Covered. |
| GEN-2 Two-authority conformance labeller | F37 F31 F32 | P250 P261 P305 | Badge plus verification endpoint from two independently versioned standards: evidence scoped to two schema versions. Covered. |
| GEN-3 Provenance-panel builder | F37 F30 F31 | P296 P138 P315 P305 | Per-field asserter, verifier, evidence and staleness from a claims model: generated interface over four-state evidence. Covered. |
| GEN-4 Single-source documentation-and-schema pipeline | F37 F29 F03 | P140 P307 P346 | One model source to prose, schemas and fixtures with a divergence gate: X11 as a generator. Covered. |
| GEN-5 Instrument-to-statistic tracer generator | F37 F17 F31 | P297 P148 P305 | Lineage map plus checker failing on untraceable aggregates: typed column lineage and requirements traceability. Covered. |
| GEN-6 Degradation-behaviour test generator | F37 F31 | P344 P289 P274 | Chaos tests from degrade-not-fail and prerequisite rules: generated adverse guards under HG05. Covered. |

### Family fits without an anchoring proof record (candidate additions, not counted)

- B-05: physical failure-consequence modelling (loss-of-life classes) has no anchoring record; the classification decision itself is F05
- B-01: volumetric block-model and sub-block grid semantics have no anchoring record
- C-05: hardware emulation as a substitute execution environment has no anchoring record beyond P249 isolated execution
- D-04: peer-to-peer power negotiation without a central controller has no anchoring record; R14 names the global capacity invariant
- S-04: physical disassembly-path enumeration with tool scaling factors has no anchoring record; the weighted-sum score itself is exact allocation (P169)
- T-02: Rasch or item-response-theory fit as a validation gate has no anchoring record
- T-02: cross-language item equating for comparability has no anchoring record
- E2-05: bit-level binary interface layout (reserved-must-be-zero fields, XLEN-parameterised widths) has no anchoring record
- E2-05: hardware privilege modes as an authority principal have no anchoring record; A08 values are organisational
- E2-03: a hardware core as the device under test has no anchoring record; the differential flow itself anchors on generated guards and two-engine comparison
- A4-04: OWL description-logic reasoning and classification has no anchoring record; P306 covers SHACL Core only
- A4-04: culturally variant definitions of one food held side by side has no anchoring record beyond P281 ambiguity preservation
- H6-04: OWL-DL consistency and expressivity limits have no anchoring record

### Extension proposals (never counted as coverage)

- none

No case required a new family, semantic rule or adapter to construct. The agent's own proposal collection (108 per-case proposals, 16 composed systems, 6 generators) consists of products constructible within existing families; it is not a set of catalogue extension proposals. The no_anchor entries are candidate proof-record additions, listed and not counted.

### Findings

**Verdicts.** All 54 sampled cases construct from the frozen catalogue: 54 COVERED, 0 PARTIAL, 0 UNCOVERED, 0 NO-WITNESS. Every required deliverable found a family, every atomic requirement an operation class, and every cross-part requirement a composition form. 53 of 54 stress variations are expressed by an axis value, variation rule or proof record; the one exception is the ILO C189 variation where a worker's immigration status is tied to the employer, which is a social power asymmetry no product expresses.

**What the sample actually tested.** All 54 cases are data standards, interface specifications, data models or governance documents hosted on GitHub, because the session's egress policy left GitHub as the only readable primary-source host. So iteration 1 is a hard test of the catalogue's data-contract families (F03, F02, F25, F31, F32, F01, F05, F06, F33, F29) and a weak test of everything else. F12, F19 and F20 were not exercised by any sampled case; F11, F15, F16, F21, F22, F27, F35 and F36 appear only once or twice, and mostly as supporting families. Nothing can be concluded about those families from this iteration.

**Where the catalogue named what the source lacks.** In eight stress cases the catalogue's own rule is precisely the missing piece in the real specification: a named shared-state owner (EEBus, stress 7); a declared degraded mode with later reconciliation (OpenHIE, 33); declared reject-versus-ignore exception behaviour (RISC-V SBI, 45); a producer-guarantee against consumer-assumption check before exchange (FHIR, 48); an explicit retention-versus-erasure contract (OCDS, 29); refusal of silent numeric substitution (Open SDG, 42); accepted meaning as a boundary field beyond schema validity (OMOP, 34); invalidation on upstream identity change (BCF, 12). The agent's four cross-cutting findings map the same way: conditional obligation is scoped applicability with explained verdicts (P192, P198, P200); the five irreversibility mechanisms are HG07 with P263, P293 and P342; conformance mistaken for fitness is the boundary meaning field and P302; consent where least expected is F06 with P206 and P264.

**Thin fits.** Four cases construct but with vocabulary that stretches: E2-05 and E2-03 (hardware privilege boundary, bit-level binary layout, a hardware core as device under test), D-04 (peer-to-peer physical power negotiation with no controller), T-01 (a convention whose enforcement outcomes in private homes are not a product). These are recorded as no-anchor entries and notes, not as verdict changes.

**No-anchor ledger.** Twelve steps fit a family but have no anchoring proof record: OWL description-logic reasoning (A4-04, H6-04); Rasch or IRT validation gates and cross-language item equating (T-02); bit-level ABI layout and hardware privilege modes (E2-05); a hardware DUT (E2-03); peer-to-peer physical negotiation (D-04); volumetric block-model grids (B-01); disassembly-path enumeration with tool scaling (S-04); physical failure-consequence classes (B-05); hardware emulation as an execution substrate (C-05); culturally variant definitions held side by side (A4-04). These are candidate proof-record additions for the user to consider; they are not counted as coverage gaps because the construction exists at family and operation level.

**Composed wholes.** The agent's 16 composed systems all fall on existing chain shapes: X02 (five), X06 (three), X11, X08 (two each), X03, X04, X05, X07, X09, X10 and X12 (one each); CS-14 restates F31's product contract and CS-15 and CS-16 are pattern libraries (F04 over F33 and F05). The six generators are all F37 configurators over finite obligation relations with anchors in P303, P304, P305 and P344. No composed whole required a composition form outside C01 to C14 or a global obligation outside R14.

**Discovery-side shortages** are recorded above and kept apart from coverage: ISIC T is severe; both sampled cases in ISIC I, ISIC N and ISIC T rest on snippet-only requirements; the classification frame is ISIC Rev. 4 because Rev. 5 section titles could not be verified; and the classifications themselves were snippet-only.

**Process notes.** The agent's final message arrived in two consecutive continuation blocks and was concatenated at the recorded boundary. The prompt it received is identical to the committed prompt file apart from the file's trailing newline; the received-prompt hash is the reference for later iterations. The agent obtained sources by cloning 131 repositories with git, which stays within the allowed host.

**Never exercised after iteration 1.** Families F12, F19, F20; variation rules V14 (excluded by contract) and V15 (no case blocked on a missing primitive); requirements R01, R03, R17, R26 and R32, which are factory-level and manufacturing or allocation claims that no data-standard case reaches; chain X03 appears only inside the agent's composed system CS-4.

#### Cumulative after iteration 1

| Measure | Value |
| --- | --- |
| Iterations | 1 |
| Cases mapped | 54 |
| Unique origin clusters | 54 |
| COVERED | 54 |
| PARTIAL | 0 |
| UNCOVERED | 0 |
| NO-WITNESS | 0 |
| Stress variations expressed by catalogue | 53 of 54 |
| Extension proposals (not counted as coverage) | 0 |

| Family | Name | Cases (any role) | Cases (primary) | Iterations hit |
| --- | --- | --- | --- | --- |
| F01 | Source formalization and operating-model assembly | 10 | 4 | 1 |
| F02 | Entity identity and relationship registries | 34 | 3 | 1 |
| F03 | Data transformation, migration and synchronization | 31 | 17 | 1 |
| F04 | Query, retrieval and knowledge navigation | 9 | 3 | 1 |
| F05 | Rules, policies and scoped decisions | 10 | 1 | 1 |
| F06 | Authority, access, delegation and information release | 24 | 1 | 1 |
| F07 | Admission, readiness and lifecycle transitions | 3 | 0 | 1 |
| F08 | Agreements, entitlements and recurring obligations | 4 | 0 | 1 |
| F09 | Workflow and case coordination | 5 | 2 | 1 |
| F10 | Collaborative review and decision records | 8 | 2 | 1 |
| F11 | Planning, scheduling and qualified assignment | 2 | 0 | 1 |
| F12 | Routing, packing and network allocation | 0 | 0 | - |
| F13 | Transactions, external effects and reconciliation | 5 | 1 | 1 |
| F14 | Quantitative ledgers, allocation and valuation | 3 | 0 | 1 |
| F15 | Material supply and fulfillment | 1 | 1 | 1 |
| F16 | Asset maintenance and service reliability | 2 | 0 | 1 |
| F17 | Measurement, analytics and reporting | 14 | 1 | 1 |
| F18 | Prediction, inference and uncertainty | 1 | 0 | 1 |
| F19 | Diagnosis and next-evidence selection | 0 | 0 | - |
| F20 | Trade-off, portfolio and allocation decisions | 0 | 0 | - |
| F21 | Simulation and digital twins | 3 | 0 | 1 |
| F22 | Experiment and measurement campaigns | 2 | 1 | 1 |
| F23 | Learning, assessment and qualification paths | 2 | 0 | 1 |
| F24 | Software application construction and maintenance | 4 | 2 | 1 |
| F25 | API, connector and event-service construction | 17 | 3 | 1 |
| F26 | Infrastructure, deployment and operations configuration | 3 | 1 | 1 |
| F27 | Engineering design and manufacturing preparation | 2 | 0 | 1 |
| F28 | Spatial and spatiotemporal information products | 4 | 0 | 1 |
| F29 | Document, media and communication construction | 16 | 2 | 1 |
| F30 | Interactive interfaces and visualization construction | 6 | 2 | 1 |
| F31 | Verification, qualification and assurance | 26 | 3 | 1 |
| F32 | Change impact, repair and modernization | 24 | 0 | 1 |
| F33 | Recovery, replay and records lifecycle | 12 | 2 | 1 |
| F34 | Streaming detection and governed response | 5 | 1 | 1 |
| F35 | Physical control and embedded automation | 1 | 1 | 1 |
| F36 | Analytical model construction and deployment | 3 | 0 | 1 |
| F37 | Product-family configurator generation | 9 | 0 | 1 |
| F38 | Assembly of systems from multiple families | 2 | 0 | 1 |

Families never hit: F12, F19, F20

O exercised: O01(3), O02(10), O03(32), O04(32), O05(17), O06(7), O07(18), O08(14), O09(7), O10(2), O11(3), O12(2), O13(1), O14(13), O15(17), O16(40), O17(13), O18(25)
O never exercised: none

C exercised: C01(29), C02(22), C03(4), C04(18), C05(3), C06(13), C07(6), C08(1), C09(4), C10(3), C11(9), C12(1), C13(6), C14(13)
C never exercised: none

V exercised: V01(4), V02(2), V03(10), V04(2), V05(3), V06(4), V07(1), V08(2), V09(1), V10(1), V11(1), V12(2), V13(7), V16(13), V17(4), V18(1)
V never exercised: V14, V15

R exercised: R02(27), R04(6), R05(3), R06(10), R07(2), R08(1), R09(8), R10(7), R11(5), R12(19), R13(3), R14(3), R15(1), R16(2), R18(3), R19(2), R20(1), R21(2), R22(2), R23(3), R24(8), R25(11), R27(14), R28(4), R29(6), R30(25), R31(5)
R never exercised: R01, R03, R17, R26, R32

X exercised: X01(1), X02(5), X04(1), X05(2), X06(4), X07(3), X08(3), X09(1), X10(1), X11(8), X12(2)
X never exercised: X03

| Axis | Values seen (count) |
| --- | --- |
| A01 | artifact(2), entity graph(5), event(2), geometry(2), model(1), quantity(1), record(20), rule(1), text(3) |
| A02 | construct(1), coordinate(1), decide(1), qualify(2), quantify(1) |
| A03 | DAG(3), chain(3), hierarchy(3), state machine(1), tree(2) |
| A04 | event-driven(3), interactive(1), real-time(1), streaming(1) |
| A05 | calendar(4), event time(1), interval(3), known-at time(4), uncertain clock(1), valid time(3) |
| A06 | classical(2), four-state evidence(2), interval uncertainty(2), probability(4) |
| A07 | distributed(13), local transactional(1), offline(1), replicated(2) |
| A08 | actuate(4), approve(2), commit(4), disclose(15), propose(1) |
| A09 | closed finite domain(1), open stream(1), paginated snapshot(1), partial collection(9), unknown coverage(3) |
| A10 | coordinates(4), exact(2), units(2) |
| A11 | accepted upstream interpretation(11), adjudication(5), recorded runtime input(7), sign-off(11) |
| A12 | UI(1), generator(2), infrastructure(2), office/media(3), physical design(1), software(3) |
| A13 | alternative(6), mandatory(1), numeric parameter(2), optional(4), requires(6) |
| A14 | correction(7), expiry(5), migration(8), new source(2), policy revision(11), withdrawal(3) |
| A15 | behavioral refinement(3), physical validation(1), statistical performance(1), structural validity(6) |
| A16 | conflicting(1), invalid(3), missing(1), out-of-envelope(1), partial effect(3), stale(4), unavailable(2) |
| A17 | embedded(3), federated(3), offline(5) |
| A18 | capacity(1), concurrency(3), latency(1) |

FORD categories with at least one mapped case: FORD 1, FORD 2, FORD 3, FORD 4, FORD 5, FORD 6
ISIC categories with at least one mapped case: ISIC A, ISIC B, ISIC C, ISIC D, ISIC E, ISIC F, ISIC G, ISIC H, ISIC I, ISIC J, ISIC K, ISIC L, ISIC M, ISIC N, ISIC O, ISIC P, ISIC Q, ISIC R, ISIC S, ISIC T, ISIC U

Gap ledger (catalogue side):
- none

Family fits but no anchoring proof record:
- it1 B-05: physical failure-consequence modelling (loss-of-life classes) has no anchoring record; the classification decision itself is F05
- it1 B-01: volumetric block-model and sub-block grid semantics have no anchoring record
- it1 C-05: hardware emulation as a substitute execution environment has no anchoring record beyond P249 isolated execution
- it1 D-04: peer-to-peer power negotiation without a central controller has no anchoring record; R14 names the global capacity invariant
- it1 S-04: physical disassembly-path enumeration with tool scaling factors has no anchoring record; the weighted-sum score itself is exact allocation (P169)
- it1 T-02: Rasch or item-response-theory fit as a validation gate has no anchoring record; cross-language item equating for comparability has no anchoring record
- it1 E2-05: bit-level binary interface layout (reserved-must-be-zero fields, XLEN-parameterised widths) has no anchoring record; hardware privilege modes as an authority principal have no anchoring record; A08 values are organisational
- it1 E2-03: a hardware core as the device under test has no anchoring record; the differential flow itself anchors on generated guards and two-engine comparison
- it1 A4-04: OWL description-logic reasoning and classification has no anchoring record; P306 covers SHACL Core only; culturally variant definitions of one food held side by side has no anchoring record beyond P281 ambiguity preservation
- it1 H6-04: OWL-DL consistency and expressivity limits have no anchoring record

Origin clusters rediscovered in more than one iteration:
- none



## Method amendment after iteration 1

Recorded as an amendment; earlier sections stand verbatim.

1. **No pull request.** The repository does not use pull requests. PR #4 was closed, its activity subscription and check-in removed. The branch is pushed after each iteration and the coverage folder is mirrored to `main` when the ten iterations are done.
2. **Per-iteration summary.** After each iteration a coverage summary is given to the user in the conversation, in addition to the report section.
3. **Cross-scale family checks.** Each iteration section gains a hand-written subsection that takes the patterns surfaced by that iteration's cases and examines them across regimes at different scales (physical and engineering, cellular and biological, ecological, economic and business, legal and social, computational), looking at the data forms and schemas each regime actually records. The question is whether the family, operation and composition mapping holds when the same pattern appears at another scale. Verdict per pattern: HOLDS, STRAINS (with the strain named), or BREAKS. This is analyst reasoning without primary sources; it hardens or damages the family hypothesis, and a BREAKS verdict is recorded as such. The blind agents' prompt is not changed by this amendment.

### Iteration 1 addendum: cross-scale family checks (analyst reasoning, no primary sources; blind-agent prompt unchanged)

Eight patterns surfaced by iteration 1's cases, each taken across regimes. For every regime the data form is sketched as the record a practitioner in that regime actually keeps, then mapped onto the frozen catalogue. Record forms already present in the agent's own inventory are cited where they are the regime's native schema (OPC UA and SunSpec for plant telemetry, Phenopackets and mmCIF for biology, Darwin Core for ecology, FIX and UBL and OCDS for markets and procurement, OpenTelemetry for computing).

#### SC1. Peer negotiation under a shared hard limit with no central controller

Source cases: D-04 EEBus (fuse limit), C-03 MTConnect (one agent, many clients), K-02 FDC3 (channels).

| Regime | Data form kept in that regime | Family mapping | Holds? |
| --- | --- | --- | --- |
| Household or grid electrical | Per-device power setpoints and measured draw at sample times; the limit as a constant; SunSpec and OPC UA telemetry rows `{device_id, t, P_set, P_meas, limit}` | F35 + C12 feedback + R14 capacity invariant + R20 timing | holds |
| Cellular: quorum sensing, stomatal coordination, sinoatrial cell synchrony | Expression or conductance per cell versus a sensed shared signal; single-cell matrices `{cell, gene, level}`, calcium time series `{cell, t, signal}`; no identity carried by the cell itself, only by the observation | F35 + C12 at the model level; F21 for the population twin; authority field empty | holds via the observation layer; authority degenerates |
| Network transport: TCP congestion control, CSMA/CA | Per-flow window and observed loss or ECN marks `{flow, t, cwnd, loss}`; the link capacity is the fuse | F34 + C12 + R14; convergence anchors P316 | holds |
| Business: production quotas, syndicated lending, consortium cost-sharing | Offers, commitments and observed totals `{party, t, commitment, observed_total, cap}`; FIX orders and UBL commitments are the native forms | F20 + F13 + F10 + R26 strategic behaviour | holds; a new obligation (R26) appears only here |
| Ecological: flocking, foraging under a shared food patch | Positions and neighbour sets `{agent, t, x, v, neighbours}`; Darwin Core occurrence rows aggregate the population | F21 + C12 | holds at model level |
| Stigmergy: pheromone trails, wiki editing | Agents read and write a shared environment; the environment has no owner `{agent, t, read_state, write_delta}` | C09 atomic reads and writes over shared state; F38 requires a shared-state owner | strains: the catalogue insists on a named owner, the regime has none; the model must nominate the environment as owner |

Verdict: HOLDS. Two systematic observations. The authority field is populated only in social and economic regimes; elsewhere it is a constant (physics permits the effect), which the boundary contract allows but does not exploit. Strategic behaviour (R26) attaches only at the economic scale, and the catalogue already carries it as a separate claim, so the family is the same structure with a scale-dependent obligation set.

#### SC2. Conditional obligation: required only sometimes

Source cases: H-01 GTFS, M-01 ODK, K-04 FIX Orchestra, A4-05 Arena, F-02 BuildingSync.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Law and regulation | Rule with applicability conditions and exceptions `{rule_id, scope_predicate, modality, exception_refs}` | F05 + P191, P192, P198, P200 | holds |
| Gene regulation: operons, checkpoints | Regulatory logic tables `{gene, condition_inputs, expression}`; the lac operon is a two-input decision table | F05 shape, but the modality is causal not deontic; the record is OBSERVATION basis | holds with a split: causal conditional is F21 or F35 dynamics, deontic conditional is F05; HG01 already separates the bases |
| Contracts and finance: covenants, insurance clauses | Term with trigger `{clause, trigger_metric, threshold, duty}`; UBL and HR Open carry these as structured terms | F08 + F05 | holds |
| Engineering interlocks | Safety requirement with guard `{actuator, guard_condition, required_state}` | F35 + F05 + C04 guarded choice | holds |
| Chemistry: catalysed reactions | Feasibility condition `{reaction, catalyst_present, rate}` | F21; no obligation exists | out of pattern: feasibility is not obligation |

Verdict: HOLDS. The pattern bifurcates on modality: "must, if" versus "does, if". The catalogue separates these by evidence basis rather than by family, which is the right joint; every regime still needs an explained verdict (P200).

#### SC3. Irreversible records with correction as a new event

Source cases: O-02 OCDS, S5-05 preregistration, H-05 eBL endorsement chain, D-01 OCPI REMOVED, B-05 disclosure.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Accounting and ledgers | Journal with reversing entries, never deletion `{entry, t, debit, credit, reverses}` | F33 + F14 + P155, P263 | holds |
| Land registries, court records, notarisation | Instrument with date and reference to what it amends `{instrument, t, amends}` | F33 + P293 | holds |
| Biology: lineage and mutation, differentiation | Phylogenetic trees and variant calls `{lineage, position, variant, generation}`; repair enzymes add corrective events, they do not rewrite history | F33 + F02 + C10 compensation | holds |
| Neural systems: memory, pruning | Synaptic weights that decay; no record of deletion | F33 with bounded erasure by decay (P342) | holds; erasure exists as decay rather than deletion |
| Thermodynamics, quantum measurement | Trajectories; no record form | none | out of scope: no typed record |

Verdict: HOLDS. The right-to-erasure conflict (stress 29) has a biological analogue in decay, which suggests the catalogue's retention contract should admit time-bounded erasure as a first-class policy value; P342 already does.

#### SC4. Consent-gated, purpose-bound release with revocation

Source cases: R-05 OpenActive, M3-03 sewershed identification, D-01 private locations, N-05 candidate data, L-04 selective disclosure.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Cell biology: receptor-gated signalling, MHC presentation | Ligand and receptor specificity tables `{signal, receptor, cell_type, response}`; the receptor is the purpose binding | F06 + P206, P264 | holds; revocation is receptor downregulation, and molecules already released cannot be recalled |
| Business: need-to-know, clean rooms, Chinese walls | Access grants `{principal, resource, purpose, expiry, grantor}`; permitted-edge matrices | F06 + P207, P298 | holds |
| Social: secrets, gossip norms, territory marking | Informal; when recorded, `{holder, audience, condition}` | F06 | holds |
| Computing: capabilities, OAuth scopes | Tokens `{subject, scope, audience, exp}` | F06 + P206 | holds |

Verdict: HOLDS. The unknown-coverage-of-replicas state (A09) recurs in every regime: once released, copies exist beyond the grantor's inventory. The catalogue names this rather than promising erasure.

#### SC5. Identity through transformation, or conserved quantity instead

Source cases: I-05 lot codes through transformation, B-01 composites, N-04 concept merge, H-01 agency merge, F-01 GUID regeneration, N1-02 provider-scoped identity.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Manufacturing and supply | Batch genealogy and BOM explosion `{lot_out, lot_in, qty, event}` | F15 + F02 + P160, P177 | holds |
| Cell biology: division, metabolism, isotope tracing | Lineage graphs `{cell, parent, t}`; tracer studies label molecules through pathways exactly like lot codes | F02 + F15 shape + P284 | holds |
| Finance: money, commodities | Fungible; identity is lost at pooling, only quantity is conserved `{account, t, amount}` | F14 conserved quantity, not F02 identity | holds by bifurcation: the catalogue has both families and A01 separates entity from quantity |
| Organisations: mergers, successors in interest | Equivalence classes with dates `{old_id, new_id, effective, evidence}` | F02 + P284, P212 | holds |
| Particle physics: indistinguishable particles | No identity in the substrate | none | out of scope: identity is a record property, not a substrate property |

Verdict: HOLDS. The strengthening insight is the principled bifurcation: a transformation either preserves identity (F02 and F15) or preserves only quantity (F14), and the catalogue chooses by semantic object, not by industry.

#### SC6. Scoped conformance: two valid parties that cannot interoperate

Source cases: M3-04 FHIR, G-02 UBL customisation, H6-01 TEI customisation, L-01 two-standard versioning, D-04 use cases.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Transplant medicine: HLA matching; blood groups | Compatibility matrices `{donor_type, recipient_type, compatible}` | P302 producer guarantee against consumer assumption | holds; the check before exchange is the catalogue's handoff check |
| Biology: reproductive isolation between valid species | Mating compatibility records | P302 shape | holds |
| Trade: jurisdictional profiles of one standard | Profile declarations `{party, standard, profile, version}` | F31 + R02 + P261 | holds |
| Language: mutually unintelligible dialects | Intelligibility matrices | P302 shape | holds |
| Protocols: TLS cipher negotiation | Offered and accepted suites `{client_offer, server_accept}` | P302 + P343 | holds |

Verdict: HOLDS. Conformance plural and scoped is the boundary contract itself; every regime needs a negotiation step before exchange.

#### SC7. Validation gates that can fail with no fallback

Source cases: T-02 Rasch gate, S5-01 deposit gate, Q-02 required fields, F-02 examples gate, E2-05 boot ordering.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Cell cycle checkpoints | Checkpoint state `{cell, phase, DNA_intact, outcome: proceed, arrest, apoptosis}` | HG02 whole-input validation before effects; HG05 failed and not-run states; P199 gate decisions | holds |
| Manufacturing inspection | Inspection records `{lot, test, result, disposition}` | F31 + P189 | holds |
| Law: admissibility of evidence | Rulings `{item, rule, admitted}` | F31 + F05 | holds |
| Statistics: model fit gates | Fit statistics and thresholds `{model, statistic, threshold, pass}` | F31 + F18 + P347 | holds; no anchor for IRT fit, recorded in the no-anchor ledger |

Verdict: HOLDS. Publishing the failure instead of the estimate is HG05 in every regime; biology implements it as arrest or apoptosis.

#### SC8. State that expires: review clocks and freshness

Source cases: B-05 classification, R-05 perishable sessions, D-01 tariffs, H-01 feed validity, G-05 revocation.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Molecular biology: mRNA and protein half-lives | Turnover rates `{species, half_life}`; stale instructions vanish by decay | P244 freshness fence realised passively; A05 | holds |
| Metrology: calibration intervals | Calibration certificates `{instrument, calibrated_at, due}` | F16 + P215, P255 | holds |
| Licensing and permits | Terms with expiry `{licence, issued, expires, renewal_conditions}` | F08 + P215 | holds |
| Physics: radioactive decay | Decay constants | A05 only | out of pattern: no obligation attaches |

Verdict: HOLDS. Freshness is enforced actively (a fence) in engineered and social regimes and passively (decay) in biological ones; both are A05 with an expiry event (A14).

#### Break watch after iteration 1

No pattern broke. Three strains recur and all coincide with distinctions the catalogue already draws: the authority field degenerates outside social regimes (A08 and A11 stay well defined but constant); deontic versus causal conditionals split on evidence basis (HG01); identity versus quantity split on semantic object (A01). One strain is not yet drawn by the catalogue: shared state with no owner (stigmergy) forces the modeller to nominate the environment as owner under F38, which is a modelling convention rather than a fact of the regime. It is recorded here as the first candidate crack to watch across later iterations. The substrate-versus-record boundary (physics and particle identity) is the catalogue's declared scope, not a break.

