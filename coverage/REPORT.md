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

## Iteration 2

### Agent run

| Field | Value |
| --- | --- |
| model_selector | opus |
| subagent_type | general-purpose |
| started_utc | 2026-09-09T19:47:00Z |
| duration_ms | 1958124 |
| tool_uses | 116 |
| subagent_tokens | 282960 |
| raw | coverage/iterations/02.raw.md |
| raw_note | final message emitted in two consecutive continuation blocks; concatenated with a single space at the boundary 'P-G-' / '01-2 *Timezone-preservation audit*' (extract_final.py) |
| prompt_file_sha256 | aa6845bceb2af60ccd581ebaac88ecfb33fab835621180b11cf2b85cb32ce2f7 |
| prompt_received_sha256 | a0b8ea9ecebcc18f18342e7b49014ce6b72e189dbdeef20bd7aeaa2689b07abe |
| prompt_identity | identical to iteration 1's received prompt; identical to the file modulo its trailing newline |

### Agent-reported discovery and sampling

| Field | Value |
| --- | --- |
| isic_version | UN ISIC Rev. 4 (2008) letters A-U used as the frame; Rev. 5 (2023) noted, sections A-F verified from a GitHub-hosted structure file, H-V unverified |
| ford_version | OECD FORD, Frascati Manual 2015, six fields (SNIPPET) |
| seed | 15045947676547694015 (hex d0cdf1b1e9bd3dbf) |
| randomness_tool | os.urandom(8) via getrandom(2) |
| runtime | Python 3.11.15, Linux 6.18.44, drawn 2026-09-09T20:04:10Z |
| sampling_algorithm | random.Random(seed) MT19937; random.sample(stratum, 2) without replacement; strata in fixed order ISIC A-U then FORD 1-6, each sorted by case ID; FORD strata exclude IDs already drawn |
| inventory_size | 122 |
| inventory_sha256 | not reported |
| categories | 27 |
| selected | 54 |
| read_status_selected | {'READ': 41, 'READ-thin': 9, 'SNIPPET': 4} |
| source_acquisition | WebFetch on github.com and raw.githubusercontent.com; all other hosts blocked; 51 of 54 selected cases read at least thinly |
| scope_decision | 54 sampled cases briefed in full; 122-entry inventory delivered with status and clusters; two proposals per case; ten compositions and two generators; one stress variation per case |

Discovery shortages (agent side, kept separate from coverage gaps):
- ISIC G: 3 entries, one cluster (CL-EPCIS), effectively 2 origins; both picks cluster-adjacent
- ISIC L: 4 entries, three in cluster CL-RESO, 2 origins
- ISIC F: 5 entries, 3 organisations
- ISIC I, P, S: 4 origins each, short by one
- ISIC Q: 7 entries, 4 organisations
- ISIC T: 5 origins found, all hosts blocked, zero READ sources; both picks SNIPPET
- ISIC B: B-01 repository holds only a licence; B-04 host blocked
- Thin reads recorded per case: H-04, I-01, N-02, O-04, Q-05, Q-07, R-06, X-03, M-02, N-04, A-01, A-06, R-02 lack the substance the case needed
- G-01: schema summary claimed six core event types and enumerated five, unresolved
- ISIC Rev. 5 titles beyond section F unverified; FORD text unverifiable

### Per-case mapping

| Case | Origin | Cat. | Src | Families (primary first) | O | C | V | R | X | Anchors | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A-03 | NOAA Fisheries \| FIMS | ISIC A | READ | F36 F18 F21 F24 F31 F22 | O10 O12 O14 O16 O09 | C01 C05 C11 | V04 V05 | R23 R31 R16 R07 | X06 | P335 P347 P322 P277 P268 P290 | COVERED |
| A-05 | AgGateway ADAPT \| ADAPT Standard | ISIC A | READ | F03 F02 F10 F07 F32 F31 | O03 O04 O07 O08 O18 O16 | C01 C04 C11 | V16 | R02 R25 R30 R31 | X11 | P95 P282 P216 P257 P13 P261 | COVERED |
| B-01 | Global Mining Guidelines Group \| Open Mining Format | ISIC B | READ-thin | F01 F29 F32 | O01 O02 O16 | C01 | V15 | R06 R02 | - | P204 P300 P250 | COVERED |
| B-06 | PDS Technology \| WITSML Studio | ISIC B | READ | F30 F25 F34 F21 F26 F31 | O15 O17 O08 O12 O03 O16 | C01 C07 C08 | V06 V11 | R11 R19 R13 R02 | - | P315 P327 P241 P249 P261 | COVERED |
| C-05 | OPC Foundation \| UA-Nodeset | ISIC C | READ | F02 F33 F31 F10 F06 F32 | O03 O04 O16 O18 O07 | C01 C14 | - | R02 R12 R30 R25 | - | P194 P263 P284 P208 P264 P95 | COVERED |
| C-06 | DMSC QIF via J. Michaloski \| QIF FAIR generation | ISIC C | READ | F27 F31 F17 F02 F03 | O09 O16 O05 O04 O03 | C01 C02 C06 | V09 | R17 R15 R16 R31 | X03 | P321 P184 P282 P148 P51 | COVERED |
| D-02 | LF Energy CoMPAS \| IEC 61850 PACS configuration components | ISIC D | READ | F03 F35 F26 F31 F06 F02 | O03 O14 O16 O04 O17 | C01 C13 C09 | V10 V07 | R20 R28 R13 R27 R02 | X10 | P310 P261 P264 P318 P257 | COVERED |
| D-05 | open-dynamic-export (independent) \| CSIP-AUS dynamic export control | ISIC D | READ | F35 F34 F25 F13 F31 | O08 O17 O07 O11 O16 | C12 C07 C04 C10 | V10 V01 V11 | R20 R28 R10 R14 | X10 | P329 P330 P244 P257 P218 | COVERED |
| E-02 | US EPA \| SWMM | ISIC E | READ | F21 F03 F31 F26 | O12 O09 O16 O14 | C01 C05 | V04 | R16 R31 R13 | X09 | P322 P347 P249 P265 P268 | COVERED |
| E-01 | US EPA / OpenWaterAnalytics \| EPANET 2.2 | ISIC E | READ | F21 F03 F31 F32 | O12 O09 O16 O18 | C01 C05 | V04 | R16 R31 R30 | X09 | P322 P347 P261 P245 P268 | COVERED |
| F-04 | LabEEE UFSC \| IDS for BIM-BEM validation | ISIC F | READ | F05 F31 F27 F03 | O07 O16 O03 O02 | C01 C13 | V09 | R15 R02 R04 | X03 | P191 P194 P148 P261 | COVERED |
| F-03 | buildingSMART International \| bSDD verification procedure | ISIC F | READ | F31 F07 F10 F05 F02 F04 F32 | O07 O16 O04 O06 O08 O18 | C04 C11 C01 | V16 | R29 R25 R02 R30 | X02 | P199 P200 P194 P282 P288 P205 P250 | COVERED |
| G-01 | GS1 \| EPCIS 2.0 XSD | ISIC G | READ | F15 F34 F02 F03 F13 | O03 O04 O08 O05 O17 | C02 C06 C01 | V11 | R02 R19 R12 R10 | X02 | P177 P160 P153 P283 P262 P210 | COVERED |
| G-02 | OpenEPCIS (benelog) \| EPCIS 2.0 toolkit | ISIC G | READ | F03 F25 F31 F32 F34 | O03 O17 O16 O18 O05 | C01 C08 C14 | V11 | R02 R29 R30 R19 | X11 | P197 P30 P262 P344 P261 P268 | COVERED |
| H-04 | DCSA \| Track and Trace API reference implementation | ISIC H | READ-thin | F25 F24 F06 F26 F31 | O17 O14 O07 O16 | C01 C04 | V15 V07 | R09 R27 R13 R02 | - | P206 P207 P264 P266 P318 | COVERED |
| H-01 | Open Mobility Foundation \| MDS Policy API | ISIC H | READ | F05 F28 F33 F06 F08 F32 | O07 O09 O08 O18 O15 | C04 C07 C14 | - | R04 R18 R12 R30 | X07 | P4 P192 P326 P215 P263 P212 P244 | COVERED |
| I-01 | OpenTravel Alliance \| OpenTravel specifications | ISIC I | READ-thin | F03 F32 F02 | O03 O18 O04 | C01 C13 | - | R02 R30 | - | P261 P245 P95 P204 | COVERED |
| I-04 | USDA FoodData Central \| FDC API release notice | ISIC I | READ | F25 F04 F32 F06 F31 | O17 O05 O18 O16 O07 | C05 C07 C01 | - | R09 R30 R02 | X04 | P311 P294 P266 P197 P215 P228 | COVERED |
| J-06 | UK CDDO \| open standards process | ISIC J | READ | F10 F09 F07 F06 F01 | O07 O08 O02 O16 O05 | C04 C11 C01 | V16 | R25 R06 R14 | X07 | P13 P106 P216 P199 P195 P231 | COVERED |
| J-04 | Model Context Protocol \| authorization discussion | ISIC J | READ | F06 F25 F13 F33 F31 | O07 O17 O08 O16 | C01 C04 C07 C09 | V07 V01 | R27 R09 R10 R28 | - | P206 P207 P247 P244 P248 P262 | COVERED |
| K-06 | UK GDS Data Standards Authority \| ISO 20022 catalogue entry | ISIC K | READ | F04 F08 F32 F02 F29 | O04 O01 O18 O15 | C01 C07 | - | R30 R02 | - | P79 P215 P255 P204 P265 | COVERED |
| K-05 | Moov \| iso20022 Go library (archived) | ISIC K | READ | F24 F25 F32 F26 F13 F31 | O03 O16 O17 O18 O14 | C01 C13 | V15 | R30 R13 R09 R02 | X04 | P345 P249 P265 P30 P197 P272 | COVERED |
| L-03 | BuildingSync consortium (US DOE) \| BuildingSync schema | ISIC L | READ | F03 F31 F05 F32 F21 F02 | O03 O07 O16 O18 O12 | C01 C04 C14 | V16 | R02 R30 R16 R04 | - | P192 P198 P148 P261 P322 P208 | COVERED |
| L-01 | RESO \| Common Format proposal (ratified 2023) | ISIC L | READ | F03 F02 F32 F25 F31 | O03 O04 O16 O18 | C01 C04 | - | R02 R30 R09 | - | P302 P95 P261 P307 P282 | COVERED |
| M-02 | DataCite \| metadata schema documentation | ISIC M | READ | F29 F32 F31 F03 | O15 O18 O16 O14 | C01 C14 | - | R24 R30 R02 | X11 | P140 P261 P120 P148 | COVERED |
| X-02 | Zarr developers \| GeoZarr CF alignment issue | ISIC M | READ | F01 F10 F28 F03 F32 | O02 O07 O09 O16 O18 | C04 C11 C13 | V16 | R06 R25 R18 R30 | - | P193 P281 P325 P288 P13 P214 | COVERED |
| N-01 | Brick Consortium \| Brick schema | ISIC N | READ | F04 F01 F32 F26 F31 F02 | O02 O06 O14 O18 O16 | C06 C14 C01 | - | R06 R30 R13 R08 | X11 | P306 P203 P318 P309 P261 | COVERED |
| N-02 | Open Contracting Partnership \| OCDS standard repository README | ISIC N | READ-thin | F29 F03 F31 F10 | O15 O03 O16 O07 | C01 | - | R24 R02 R30 | X11 | P140 P148 P261 | COVERED |
| O-04 | GSA / 18F \| Login.gov identity provider | ISIC O | READ-thin | F06 F02 F25 F26 F31 | O07 O04 O17 O16 O14 | C01 C04 C09 | V07 V13 | R27 R09 R13 R11 | - | P206 P247 P262 P284 P207 | COVERED |
| O-06 | EU Digital Identity Wallet \| OpenID4VP adoption issue | ISIC O | READ | F06 F25 F31 F32 F02 | O07 O17 O16 O18 O04 | C01 C04 C13 | V13 | R27 R09 R29 R30 R28 | - | P247 P262 P264 P343 P302 P250 | COVERED |
| P-03 | Ed-Fi Alliance \| Ed-Fi API Standards | ISIC P | READ | F25 F31 F02 F32 F03 | O17 O16 O04 O18 O03 | C01 C02 | V05 | R09 R29 R02 R30 | - | P311 P266 P343 P250 P307 | COVERED |
| P-04 | CEDS \| Common Education Data Standards | ISIC P | READ | F03 F01 F02 F04 F32 F29 | O03 O02 O04 O14 O18 O05 | C06 C01 C14 | - | R02 R06 R12 R30 | X11 | P307 P310 P140 P297 P203 | COVERED |
| Q-07 | OHDSI \| organisation repositories (CDM, Atlas, CohortMethod, PatientLevelPrediction, Vocabulary) | ISIC Q | READ-thin | F03 F36 F17 F02 F06 F31 | O03 O10 O05 O04 O16 | C06 C01 C13 | V04 V13 | R23 R12 R27 R30 | X06 | P310 P335 P268 P282 P264 P261 | COVERED |
| Q-04 | HL7 International \| US Core Implementation Guide (FHIR R4) | ISIC Q | READ | F01 F31 F29 F10 F32 F25 | O02 O16 O15 O07 O18 O17 | C01 C11 C14 | V16 | R06 R29 R24 R25 R30 | X11 | P140 P307 P346 P13 P250 P302 | COVERED |
| R-06 | Bodleian Libraries \| IIIF Manifest Editor | ISIC R | READ-thin | F30 F29 F25 F32 F31 | O15 O17 O03 O16 O18 | C01 C13 | V06 | R11 R24 R30 R13 | - | P315 P266 P249 P265 P337 | COVERED |
| X-03 | TEI Consortium \| TEI P5 Guidelines | ISIC R | READ-thin | F29 F01 F37 F32 F31 | O02 O14 O15 O18 O16 | C01 C13 C14 | - | R24 R04 R30 R06 | X11 | P140 P307 P260 P212 P148 | COVERED |
| S-03 | The Restart Project \| environmental impact data | ISIC S | READ | F14 F17 F02 F31 F06 F08 | O09 O05 O04 O16 O15 | C02 C06 | V03 V04 | R31 R27 R02 | X08 | P169 P282 P280 P22 P296 P240 | COVERED |
| S-02 | Open Repair Alliance \| downloadable datasets | ISIC S | READ | F03 F17 F02 F32 F33 F06 | O03 O05 O04 O18 O01 | C06 C02 | V03 | R02 R12 R30 R27 | - | P95 P261 P22 P211 P294 | COVERED |
| T-05 | USCIS \| I-9 Central: domestic workers | ISIC T | SNIPPET | F07 F05 F33 F06 F08 | O07 O04 O16 O18 | C04 C11 | V13 V17 | R27 R04 R25 | X02 | P199 P192 P342 P264 P258 | COVERED |
| T-01 | US DOL Women's Bureau \| sample employment agreement for home care workers | ISIC T | SNIPPET | F08 F29 F10 F14 | O15 O07 O04 O09 | C11 C01 | V16 | R25 R24 R31 | X07 | P259 P25 P151 P156 | COVERED |
| U-05 | IOM (UN Migration) \| HTCDS with HXL hashtags issue | ISIC U | READ | F03 F01 F06 F31 F08 F04 | O03 O02 O07 O16 O15 | C01 C11 | V13 | R27 R06 R29 R02 | - | P310 P344 P298 P264 P204 | COVERED |
| U-04 | UN OCHA \| Humanitarian ID (decommissioned) | ISIC U | READ | F06 F07 F32 F02 F25 | O07 O08 O18 O04 O17 | C07 C13 C11 | V13 | R27 R30 R09 R14 | X04 | P256 P345 P284 P206 P215 | COVERED |
| E-03 | DataStream (The Gordon Foundation) \| WQX JSON Schema | FORD 1 | READ | F03 F02 F32 F17 F31 | O03 O04 O18 O16 | C01 C14 | - | R02 R30 R12 | - | P261 P310 P265 P345 P30 | COVERED |
| B-03 | USGS \| GeMS tools documentation | FORD 1 | READ | F28 F03 F02 F31 F18 F06 | O03 O04 O09 O16 O06 | C02 C01 | V09 | R18 R02 R31 R29 | X09 | P326 P325 P194 P323 P204 P95 | COVERED |
| H-06 | DCSA \| Conformance Gateway | FORD 2 | READ | F31 F37 F21 F10 F25 | O16 O14 O12 O07 O17 | C03 C13 C01 | V18 | R29 R09 R05 R14 | X12 | P266 P343 P289 P286 P348 P288 P193 | COVERED |
| E-04 | Open Environment / Windsor \| Open Waters | FORD 2 | READ | F03 F13 F05 F30 F26 F06 | O03 O17 O07 O15 O14 O05 | C01 C04 C10 C11 | V01 V05 | R10 R28 R04 R13 | X02 | P310 P242 P314 P192 P318 | COVERED |
| I-05 | littlebunch \| fdc-api | FORD 3 | READ | F04 F25 F03 F26 F32 | O05 O17 O03 O14 O18 | C13 C01 C05 | - | R09 R12 R30 R13 | - | P122 P123 P285 P203 P294 P310 | COVERED |
| Q-05 | HL7 International with CARIN Alliance \| CARIN Blue Button IG | FORD 3 | READ-thin | F06 F25 F03 F10 F02 | O07 O17 O03 O04 | C01 C11 C04 | V13 | R27 R09 R25 R02 | - | P206 P264 P311 P302 P310 | COVERED |
| A-06 | AgGateway \| Modus | FORD 4 | READ | F03 F02 F09 F13 F10 F32 | O03 O04 O05 O16 O17 O18 | C01 C02 C07 | V16 | R02 R12 R25 R30 | X08 | P95 P261 P242 P259 P184 P282 P197 | COVERED |
| A-01 | BrAPI community \| BrAPI v2.1 | FORD 4 | READ | F25 F02 F22 F04 F03 F31 | O17 O04 O05 O13 O03 O16 | C02 C01 C05 | - | R09 R21 R02 R12 | X06 | P311 P302 P294 P282 P331 P266 | COVERED |
| N-04 | OCDS extensions community \| extensions and profiles | FORD 5 | READ | F37 F03 F32 F31 F02 | O14 O03 O07 O16 O18 | C06 C01 C04 | - | R04 R02 R30 R03 | - | P260 P273 P274 P302 P303 | COVERED |
| S-04 | European Commission \| Right to repair Q&A (2024) | FORD 5 | SNIPPET | F08 F05 F14 F31 F07 F17 | O07 O09 O16 O08 O15 | C04 C11 C01 | V16 | R04 R31 R25 R29 | X02 | P215 P185 P192 P258 P288 P282 | COVERED |
| R-02 | OCFL editors \| Oxford Common File Layout specifications | FORD 6 | READ | F33 F03 F31 F32 F29 | O01 O03 O16 O18 O15 | C01 C14 C13 | - | R12 R27 R29 R30 | - | P269 P263 P265 P51 P52 P148 | COVERED |
| R-05 | Harvard Art Museums \| IIIF service documentation | FORD 6 | READ | F25 F06 F29 F02 F31 | O17 O07 O15 O04 O16 | C01 C04 | V13 | R27 R09 R24 R02 | - | P264 P206 P311 P266 P337 | COVERED |

Axis values per case:
- A-03: A06:probability, A15:statistical performance, A05:calendar, A08:approve, A16:out-of-envelope, A14:policy revision
- A-05: A01:model, A10:units, A03:state machine, A08:approve, A11:sign-off, A13:mandatory
- B-01: A01:text, A09:unknown coverage, A16:missing, A11:accepted upstream interpretation
- B-06: A04:streaming, A12:UI, A17:local, A14:backend replacement, A16:invalid, A13:alternative
- C-05: A01:record, A14:policy revision, A08:disclose, A11:sign-off, A07:replicated
- C-06: A01:geometry, A10:units, A03:chain, A15:physical validation, A11:sign-off, A12:physical design
- D-02: A12:infrastructure, A08:commit, A16:invalid, A07:shared, A13:requires, A17:shared
- D-05: A04:real-time, A08:actuate, A17:embedded, A16:unavailable, A18:latency, A11:sign-off
- E-02: A15:physical validation, A10:floating tolerance, A05:interval, A12:software, A09:closed finite domain, A16:out-of-envelope
- E-01: A15:physical validation, A10:floating tolerance, A05:interval, A14:migration, A16:out-of-envelope, A18:latency
- F-04: A01:rule, A15:structural validity, A13:requires, A08:approve, A12:physical design
- F-03: A08:approve, A11:adjudication, A15:structural validity, A03:tree, A10:units, A14:policy revision
- G-01: A01:event, A05:event time, A07:distributed, A03:DAG, A11:accepted upstream interpretation, A08:commit
- G-02: A01:event, A14:migration, A18:memory, A15:behavioral refinement, A04:streaming
- H-04: A08:read, A07:distributed, A16:missing, A17:shared, A11:accepted upstream interpretation
- H-01: A01:rule, A05:calendar, A08:disclose, A14:policy revision, A03:hierarchy, A10:topology
- I-01: A14:migration, A13:alternative, A09:unknown coverage, A01:model
- I-04: A09:paginated snapshot, A14:expiry, A08:read, A05:calendar, A13:alternative
- J-06: A08:approve, A11:sign-off, A03:state machine, A09:closed finite domain, A05:interval
- J-04: A08:commit, A07:distributed, A17:cloud, A16:stale, A11:recorded runtime input, A13:alternative
- K-06: A01:record, A14:expiry, A08:disclose, A05:calendar, A11:accepted upstream interpretation
- K-05: A14:withdrawal, A12:software, A16:unavailable, A15:structural validity, A01:record
- L-03: A01:record, A13:requires, A15:structural validity, A03:state machine, A14:policy revision
- L-01: A01:record, A13:mandatory, A14:policy revision, A09:paginated snapshot, A11:accepted upstream interpretation
- M-02: A14:migration, A13:alternative, A01:text, A15:structural validity
- X-02: A11:adjudication, A01:model, A10:coordinates, A08:approve, A14:policy revision, A06:unknown
- N-01: A01:entity graph, A14:policy revision, A03:DAG, A12:generator, A15:structural validity
- N-02: A01:text, A14:policy revision, A15:structural validity, A11:accepted upstream interpretation
- O-04: A08:approve, A07:distributed, A17:shared, A18:concurrency, A16:conflicting, A11:recorded runtime input
- O-06: A08:disclose, A13:alternative, A14:migration, A17:federated, A15:behavioral refinement
- P-03: A15:behavioral refinement, A13:mandatory, A14:policy revision, A12:software, A11:accepted upstream interpretation
- P-04: A01:model, A03:hierarchy, A12:records, A14:policy revision, A11:accepted upstream interpretation
- Q-07: A17:federated, A06:probability, A01:record, A08:disclose, A14:policy revision
- Q-04: A11:sign-off, A15:behavioral refinement, A14:policy revision, A13:mandatory, A08:approve
- R-06: A12:UI, A14:backend replacement, A01:artifact, A16:stale, A11:recorded runtime input
- X-03: A01:text, A14:expiry, A13:alternative, A12:office/media, A11:adjudication
- S-03: A01:quantity, A10:units, A06:interval uncertainty, A09:partial collection, A08:disclose, A11:accepted upstream interpretation
- S-02: A01:record, A05:known-at time, A09:partial collection, A14:policy revision, A08:disclose
- T-05: A08:approve, A11:recorded runtime input, A13:requires, A05:calendar, A16:missing
- T-01: A08:approve, A11:sign-off, A01:text, A13:optional, A05:calendar
- U-05: A08:disclose, A11:accepted upstream interpretation, A16:missing, A01:record, A13:mandatory
- U-04: A14:withdrawal, A08:approve, A05:calendar, A07:federated, A16:unavailable
- E-03: A01:record, A14:migration, A11:accepted upstream interpretation, A09:closed finite domain, A17:federated
- B-03: A01:geometry, A10:uncertainty, A10:topology, A15:structural validity, A11:accepted upstream interpretation, A03:tree
- H-06: A15:behavioral refinement, A07:distributed, A13:alternative, A11:adjudication, A14:policy revision
- E-04: A08:commit, A17:local, A13:requires, A16:invalid, A11:recorded runtime input, A12:software
- I-05: A09:paginated snapshot, A12:software, A13:alternative, A14:new source, A01:record
- Q-05: A08:disclose, A11:sign-off, A07:distributed, A01:record, A13:mandatory
- A-06: A01:record, A02:coordinate, A03:chain, A08:commit, A11:sign-off, A14:migration
- A-01: A01:record, A03:DAG, A17:federated, A09:paginated snapshot, A10:units, A11:accepted upstream interpretation
- N-04: A13:requires, A13:excludes, A14:policy revision, A11:accepted upstream interpretation, A09:closed finite domain
- S-04: A05:calendar, A11:adjudication, A08:disclose, A13:requires, A10:exact, A14:policy revision
- R-02: A01:artifact, A17:offline, A14:migration, A15:structural validity, A07:historical replay
- R-05: A08:disclose, A01:artifact, A13:alternative, A07:replicated, A14:policy revision

Mapping notes:
- **A-03**: Experimental lifecycle and the scientific-product disclaimer are HG01 basis limits: fitted output is SCENARIO evidence until accepted (A11 sign-off). Structural hypothesis comparison across model types is an experiment over models (F22) with declared tolerances (P347). Benchmark reproduction is accuracy-gated measurement (P268).
- **A-05**: Data-only, no toolkit dependency, is an environment-binding constraint. The change-proposal state machine is a guarded lifecycle model (P216); 'no component released before its counterparts' is an object-level readiness barrier across components (P257).
- **B-01**: Degenerate case: the source carries no requirements beyond a licence. The construction is the catalogue's missing-source path: an acquisition gap (O01) recorded with the unresolved location of the normative text (P204, P300), and any conformance rule blocked for lack of accepted source meaning. Rediscovered origin from iteration 1, where mirrors supplied the content.
- **B-06**: Schema version negotiated on connect is the HG00 envelope version shared by all plug-ins; a non-recursive clone silently losing schemas is a dependency-manifest defect (P249). DataReplay is deterministic replay of a recorded stream (P241, P327).
- **C-05**: A NodeId meaning the same node in all three artefacts is one identity across three representations; effective immutability after release is an append-only identity ledger (P263). Member-only drafts versus public release is a release policy under F06.
- **C-06**: Every result citing a planned characteristic defined in the product model is the design-to-manufacturing correspondence claim R17 with characteristic identity as the join key; units resolving through one shared component is P282. Byte-stable regeneration except timestamps is canonical file digesting (P51).
- **D-02**: CIM to SCL mapping with consistent equipment identity is an approved transform with reconciled destination (P310); the edition gate is dialect-specific validation (P261). The shared demo database is a missing tenant isolation contract (V07), which the catalogue blocks for utility data.
- **D-05**: First case with F35 as the primary family. Default DER control on loss of the utility server is the C07 timeout_path with a C04 safe default; ramping is a declared actuation contract under R20; certification by one DNSP is an accepted operating envelope (R28) scoped to that provider.
- **E-02**: Mass balance across hydrology, hydraulics and quality modules is the conservation invariant under R14 and O09; public-domain release with no upstream integrity guarantee is a sealed-bundle obligation on the consumer (P249, P265); continuity error under a stated percentage is the declared tolerance regime (P347).
- **E-01**: Quality transport bound to the hydraulic timestep and topology is a C01 handoff with a shared clock contract; a 14-year input compatibility window is explicit migration and dialect validation (P261, P245); the 'as is' basis forbids promoting model output to observation (HG01).
- **F-04**: A ruleset decoupled from any one checker is the replaceable-engine posture (C13, P197 shape); the unread entity list inside the .ids file is an unresolved input carried explicitly.
- **F-03**: Registration to Active to badge is an admission lifecycle with separate gate decisions (P199); cycle detection in class parentage and relations is shape and completeness validation (P194); 'Unit must match the Dimension' is P282 verbatim; the no-threshold qualitative gates are a human evidence boundary (C11).
- **G-01**: TransformationEvent inputs consumed and outputs produced is lot linkage through transformation (P160, P177); eventTime with eventTimeZoneOffset preserved is the boundary time field carrying local time; canonical event hashing across partners is P262. The five-versus-six event-type discrepancy is a discovery-side unresolved input.
- **G-02**: Semantic equivalence across three serialisations is two-representation equivalence with round trip (P197, P30); the test-data generator is generated-input evidence (P344); larger-than-memory conversion is a measured resource envelope (P268) declared in the boundary resources field. Self-declared conformance stays an open claim until independently checked.
- **H-04**: The missing authorisation layer is a missing provider capability, which blocks every party-scoped read under the catalogue's rule that missing authority blocks the effect; the README's warning becomes an HG00 authority field that the deployment cannot populate.
- **H-01**: Rules scoped by geography and vehicle state are spatially scoped decisions (P326, P192); prev_policies is an append-only supersession chain (P263); the 20-minute lead is a publication timing contract in the boundary time field (P244). The informational user rule is a declared non-enforceable modality.
- **I-01**: Thin source. Dated suites with stable code meanings are versioned dialects (P261) over a code-list identity registry; the unreadable README is an acquisition gap (P204) carried as unresolved.
- **I-04**: Three renderings of one interface agreeing is representation equivalence (P197); paged browsing is stable-snapshot pagination (P294); the dated cut-off is a recurring-obligation deadline inherited by dependents (P215).
- **J-06**: Problem statement surviving unchanged into the challenge is stable span mapping with semantic-change detection (P195); one proposal per challenge reaching the Board is a guarded lifecycle transition with transferred authority (P216, P199); stage latency is interval accounting (P231).
- **J-04**: Clients never holding third-party credentials is a permitted-edge rule (P207); session identifiers and refresh rotation are authority state with expiry and freshness fences (P244); local baked-in credentials versus multi-tenant remote is the deployment axis (A17).
- **K-06**: A catalogue entry is a typed catalog record (P79) whose review date is a review clock (P255); a proprietary licence is an obligation the entry references but does not resolve, carried in the authority field. Staleness is expiry (A14).
- **K-05**: An archived dependency with no fix path is lost support in the dependency closure (P345) and a pinned sealed bundle (P249, P265); the exit plan to a successor is least-cost repair (P272) with substitution (C13). XML to JSON to XML survival is round trip (P30).
- **L-03**: Rediscovered document from iteration 1 (F-02). The three measure states proposed, implemented, discarded are lifecycle labels (P208); a use case never contradicting the base schema is a refinement constraint on scoped rules (P198).
- **L-01**: Local fields ignorable but never fatal is the explicit extra-field policy P302 requires on every boundary; the version URN is the schema-version field; human-friendly versus OData enumerations mapping to one meaning is P282. Same organisation as iteration 1's L-01, different document.
- **M-02**: One documentation branch per schema version with no divergence from the XSD is single-source publication (X11) plus document-content comparison (P120); three live versions force version-qualified statements, the schema-version boundary field.
- **X-02**: Two conventions encoding one fact differently is a contradiction register over accepted mappings (P193) with alternatives retained until adjudicated (P281); CRS in grid_mapping versus proj: is reference metadata preservation (P325); the SWG vote with CF consultation is a decision record with transferred authority (P13).
- **N-01**: Tests must use a generated, not hand-edited, artefact: reproducible build (P318); minor releases largely backward compatible and removals needing a major version is the change-propagation contract; nightly builds indistinguishable from releases is a missing HG00 producer-version stamp.
- **N-02**: Thin source; same organisation as iteration 1's O-02 with the substantive model unread here. Documented fields existing in the schema and vice versa is single-source generation with a divergence gate.
- **O-04**: A stable subject identifier per agency pairing is identity scoped by tenant (the boundary identity field with purpose scope); assurance level is an attribute of the authority field the source does not populate, carried as unresolved.
- **O-06**: Format negotiation among three credential formats is a capability-envelope check (P343) preceding exchange (P302); selective disclosure is P264; the v1.0 pin with a v1.1 moving target is a versioned adoption decision under R30.
- **P-03**: Same organisation as iteration 1's P-03, different document. Three specifications satisfied together is a conjunction of obligations; Discovery advertising versions is the capability envelope a client reads before binding (P343); 'compatible' as a vendor assertion is an open claim until P266 tests run.
- **P-04**: One element meaning the same thing across four physical forms is typed column lineage from one definition (P297) with generated representations (P307, P310); normalised and denormalised forms pulling apart is why generation from one source is mandatory, which the catalogue states as X11.
- **Q-07**: Same organisation as iteration 1's Q-02, thinner document. Analyses travel and data does not is federated evaluation under a nonleaking release contract (P264); vocabulary version differences silently changing cohorts is the schema-version boundary field on results (P261).
- **Q-04**: Must-Support as a certification obligation is a required consumer assumption checked at the boundary (P302); a technical correction that must not change conformance is the preserved-contract check of controlled regeneration (P346); ballot votes are decision records with workgroup authority (P13).
- **R-06**: An exported manifest opening in an independent viewer is the independent-oracle rule (I-class) applied to a generated artefact; a pinned obsolete Node version is a dependency-manifest hazard (P249); the unstated Presentation API version is the missing schema-version field.
- **X-03**: Rediscovered document from iteration 1 (H6-01), thinner read. Prose and schema never disagreeing because both derive from one source is X11; maximally expressive and minimally obsolescent implies deprecation over deletion, the F32 register.
- **S-03**: Category-keyed lookups with a quality grade travelling with each number are exact allocation (P169) with origin-aware support groups from manufacturers, journals and agencies (P296) and a declared partial population (V03); share-alike licence propagation is an inherited authority obligation (F08). Unstated system boundary for pre-use CO2e is an unresolved unit-and-meaning input (P282).
- **S-02**: Same organisation as iteration 1's S-01, the data rather than the standard. A three-month lag between cut-off and release is known-at versus valid time (P211) declared on the release; counts stated per release are count reconciliation (P294); the rejects report is the excluded-contributor lineage the catalogue keeps by default.
- **T-05**: Snippet-only. Employee-versus-contractor determination is applicability evaluation (P192, P258); completion within a timeframe and retention are gate decisions with calendar obligations (P199) and bounded retention (P342); producing the record without exposing unrelated data is field-level filtering (P264).
- **T-01**: Snippet-only. A template rendered into an executed bilingual agreement held identically by both parties is agreement version binding (P259) with document generation (P25, P151); agreed rate and hours feeding pay records is billable-line construction (P156). Voluntary status is a declared modality (MAY) in the meaning field.
- **U-05**: Structure public while instances cannot be is the split between an accepted schema and protected-unit data (P298, P264); fictional examples only is generated test data (P344, GP01) applied to a sensitive domain; the licence blocker is missing authority that blocks adoption, kept explicit.
- **U-04**: Decommissioning is controlled deactivation with closure evidence (P256) over the dependency closure of relying platforms (P345); the stable subject identifier that breaks is the identity equivalence that a successor mapping must preserve (P284). No named successor is an unresolved input the catalogue keeps as a blocked migration edge.
- **E-03**: A JSON adaptation of an XML federal standard that must map back losslessly is an approved transform with reconciled destination (P310) and round trip (P30); coupling of the code-list version to the WQX version is a pinned sealed dependency (P265) in the closure (P345).
- **B-03**: Existence, identity and location confidence on every contact and fault is uncertainty as a first-class boundary field (A10, P323); _ID keys repeated as foreign keys with no orphans is referential shape validation (P194); DataSourceID on every feature is per-record provenance (P204). ArcGIS binding is an environment binding.
- **H-06**: Scenarios versioned with the standard is the schema-version field on the test artefact; simulating the absent counterparty is a substitute execution environment (C13, P289); distinguishing an implementation defect from a standard ambiguity is disagreement measurement over independent implementations (P288) feeding a contradiction register (P193). Actual party-to-party transport is HG04 and P348's transport stage.
- **E-04**: Translation applied before, never after, submission is C01 ordering with an approved transform (P310); automated submission to a regulator is an external effect that needs receipt reconciliation (P242, P314), which the source's behind-the-scenes automation omits; 'Sample' requiring method and equipment is scoped applicability (P192).
- **I-05**: Full-text index and ranked excerpts are P122 and P123; a second datastore added by implementing one interface is replaceable storage adapters with query-result equivalence (P203); nutrient numbers keeping their FDC meaning is the meaning field on the loader boundary. Undocumented refresh is an unresolved dependency trigger.
- **Q-05**: Authorised caregivers as first-class is the delegation sub-field of the authority contract (P206); consumer-facing meaning matching the adjudicated claim is an approved transform (P310) with a producer-consumer check (P302); joint governance is shared authority over the accepted set.
- **A-06**: Rediscovered document from iteration 1 (A-02). The added element this time is two live format generations whose representations must carry identical values and units (P197, P30); method identity accompanying every analyte remains P282.
- **A-01**: Trait, scale and method travelling together is the meaning-and-units boundary field (P282); an observation always resolving to a study and unit is a keyed join with mandatory referents (C02); deferred search handles are stable-snapshot pagination (P294); trials and observation units are experiment-campaign records (F22, P331).
- **N-04**: Profiles as bundles of additive extensions over a core is a feature model with requires and excludes (P260, P273); a core-only consumer still reading an extended document is the extra-field policy (P302); two profiles applied to one publisher without conflicting definitions is constrained interaction testing (P274), which the catalogue requires and the source lacks.
- **S-04**: Snippet-only. Parts availability for five or ten years by part type is a recurring obligation with notice and renewal clocks (P215, P185); applicability by product category and jurisdiction is P192 and P258; a self-assessed score with legal consequence is an open claim until independently reproduced (P288). The unread directive text is an unresolved source.
- **R-02**: A layout interpretable without the original software is a sealed checkpoint with verified restore (P269) over self-describing canonical files (P51, P52); two live versions both readable is dialect migration (P261 shape); fixtures as conformance evidence are traceability material (P148). The unread inventory and versioning rules are unresolved inputs.
- **R-05**: The same manifest identifier yielding different content by user class is authorised source views with field-level filtering (P264) applied at generation; explicit omission rather than a silent gap is HG05's distinct unavailable state; version 2.1 rather than 3.x is a declared dialect limit.

### Stress variations

| Case | # | Changed condition | Maps to | Expressed |
| --- | --- | --- | --- | --- |
| A-03 | SV-A-03 | council deadline halves and data vintage arrives two weeks late | P228, P224, P290, HG05 | yes: dependency-aware plan repair under a fixed calendar; pre-computed benchmarks are guarded cache reuse; the disclaimer becomes load-bearing exactly as the catalogue's basis rule says |
| A-05 | SV-A-05 | two committee members hold incompatible unit conventions and neither concedes | P193, P282, C11, P257 | yes: contradiction register with an adjudication boundary; the readiness barrier keeps the release blocked rather than letting components diverge |
| B-01 | SV-B-01 | an implementer claims OMF conformance with no normative text to adjudicate | V15, HG01, F31 open claim | yes: the catalogue refuses to score conformance without an accepted source; the claim stays an open claim |
| B-06 | SV-B-06 | server upgraded mid-shift to a version the tool has not seen | HG00 schema version, P261, HG05 unsupported | yes: the catalogue returns an explicit unsupported state instead of rendering misleading annotations |
| C-05 | SV-C-05 | a NodeId reassigned between two released tags | P284, P212, HG00 identity stability, P263 | yes: an identity ledger detects reassignment across tags; the affected devices are the affected-case population |
| C-06 | SV-C-06 | supplier reports results for a characteristic removed from the revised product model | C02 join referent, P213, HG06, A14:correction | yes: a dangling characteristic reference is a rejected join; the model revision invalidates dependent results |
| D-02 | SV-D-02 | a utility uploads real substation files to the shared demo | V07, P264, A08:disclose | yes: an isolation contract is mandatory before real data; the demo has none, so the catalogue rejects the upload path rather than the upload |
| D-05 | SV-D-05 | the DNSP server returns a malformed schedule instead of failing | HG02 whole-input validation before effects, A16:invalid, C04 | yes: a malformed schedule is rejected before actuation and routed to the invalid path, which is distinct from the lost-contact path; the source tests only the latter |
| E-02 | SV-E-02 | a large impervious development mid-record makes one continuous run span two catchments | A14:new source, P322 applicability, HG01 SCENARIO | yes: the model's applicability scope is declared per interval; the discontinuity becomes an explicit scope boundary rather than a mechanically valid run |
| E-01 | SV-E-01 | contamination event needs an answer within the hour and no tolerance is stated | P347, HG05, A06:unknown | yes: the catalogue emits the answer under an explicit unknown-confidence state; it cannot invent a tolerance and says so, which is the honest form of the source's silence |
| F-04 | SV-F-04 | designer supplies a newer IFC schema version than the IDS targets | P261, HG00 schema version, HG05 | yes: dialect mismatch is detected at the boundary and reported as unsupported rather than under-checked |
| F-03 | SV-F-03 | a badged dictionary later publishes a version adding circular relations; nothing re-checks | P255, P213, HG06, A14:policy revision | yes: the catalogue re-qualifies on every change and invalidates the badge; bSDD's grant-only gate is the missing review clock |
| G-01 | SV-G-01 | two partners record one move in different time zones and one normalises to UTC | P262 canonical bytes, HG00 time field, P283 | yes: a declared canonicalisation contract precedes hashing; without it the hash divergence is exactly what the catalogue predicts |
| G-02 | SV-G-02 | regulator mandates a field the CBV lacks, six-week deadline | A13 variability limit, V15, P212 | yes: blocked path with an affected-population computation; the extension is a proposal, not coverage |
| H-04 | SV-H-04 | deployed to a shared test environment with real carrier data | P264, V07, HG00 authority field | yes: the seal travels with the envelope, not the README; the catalogue refuses the path for real data |
| H-01 | SV-H-01 | an emergency needs a policy effective in five minutes against a 20-minute floor | C07 deadline, A13:alternative, P224 | yes: a declared timing conflict; only an emergency profile with its own lead-time contract resolves it, which the catalogue would require to exist before use |
| I-01 | SV-I-01 | one integrator must serve partners pinned to different suites | P261, HG00 schema version, A13:alternative | yes: per-partner dialect validation; forward compatibility stays unverified as the source records |
| I-04 | SV-I-04 | the migration deadline lands while a dependent product is mid-certification | C07 deadline, P228, A14:expiry | yes: inherited deadline handled by dependency-aware plan repair; abridged-only migration is a declared reduced profile |
| J-06 | SV-J-06 | evidence for a suggestion is commercially confidential and the process is public | P264, F06 purpose-bound release, C11 | yes: a declared conflict between openness and evidence; selective disclosure with attestation is the catalogue's available shape, which the process lacks |
| J-04 | SV-J-04 | a session identifier leaks through a proxy log | P244, HG00 authority expiry, P276 | yes: leaked authority is stale-authority rejection plus rotation; the blast radius is a failure-model analysis over dependent effects |
| K-06 | SV-K-06 | the specification URL moves and stops resolving | P265, P204, A16:unavailable, P255 | yes: a sealed copy or pinned reference plus the review clock catches it; the entry's own fields cannot |
| K-05 | SV-K-05 | a vulnerability in the archived library sits in a live payments path | P345, P272, C13, A16:unavailable | yes: dependency closure names affected paths; corrective action is fork-and-own or substitute, both explicit |
| L-03 | SV-L-03 | programme mandates a Level 2 element the use case does not require; examples gate blocks the update | P189, P148, F37 requiredness set | yes: a new required set is a profile change gated by traceability; the examples must extend first, which the catalogue orders explicitly |
| L-01 | SV-L-01 | a payload cites Data Dictionary 1.6 below the 1.7 floor | P261, HG00 schema version, HG05 | yes: rejected at the boundary with an explicit unsupported-version state; the source leaves behaviour unspecified |
| M-02 | SV-M-02 | a property's obligation level changes between 4.6 and 4.7 | P212, HG00 schema version, P195 | yes: version-scoped rule change with affected-population computation; the reconciliation check is the detector |
| X-02 | SV-X-02 | a widely used tool ships assuming CF wins before the vote | HG01, A11 missing acceptance, P214 | yes: an implementation's choice is not an accepted mapping; shadow evaluation of both precedence rules is the catalogue's way to keep the decision open |
| N-01 | SV-N-01 | a nightly build is deployed to production analytics by mistake | HG00 producer/environment version, P249, A14:backend replacement | yes: the envelope carries build provenance; a sealed bundle makes the nightly distinguishable |
| N-02 | SV-N-02 | a jurisdiction's law requires a contract stage the model lacks | A13 variability limit, V15, F37 extension proposal | yes: blocked as unsupported; the extension is a proposal outside the frozen catalogue's score |
| O-04 | SV-O-04 | an agency needs step-up assurance mid-transaction | P244, C04 guarded choice, HG00 authority level | yes: re-authorisation gate on a declared assurance attribute; the catalogue treats assurance as authority state that a step-up refreshes |
| O-06 | SV-O-06 | a wallet supports only mdoc, a relying party only SD-JWT VC; spec satisfied, deployment fails | P343, P302, HG04 actual producer and consumer | yes: the catalogue tests actual capability envelopes, not specification conformance; the assessment that found no gaps checked the wrong layer |
| P-03 | SV-P-03 | a vendor implements Resources and Descriptors but not Discovery | P343, P266, P348 adverse guard: unimplemented server operation | yes: generated protocol cases fail on the missing operation; the compatibility claim is falsified rather than unchallenged |
| P-04 | SV-P-04 | a state changes an option-set value locally to match statute | P208, P282, P297, P345 | yes: a versioned local mapping to the standard value with lineage into all four forms; silent divergence is the failure the catalogue's closure prevents |
| Q-07 | SV-Q-07 | two sites run one cohort definition on different vocabulary versions | P261, P212, HG00 schema version on results | yes: results carry the vocabulary version; a version mismatch is a declared incomparability, not a silent one |
| Q-04 | SV-Q-04 | a technical correction inadvertently tightens a Must-Support element | P346, P212, HG00 schema version | yes: the preserved-contract check fails the release; affected certified systems are the affected population |
| R-06 | SV-R-06 | institution migrates viewers to Presentation 3.0 while the editor emits 2.1 | HG00 schema version, P261, P345 | yes: a declared output version makes affected manifests enumerable; without it the dependency closure cannot be computed, which is the source's gap |
| X-03 | SV-X-03 | a widely used element must be withdrawn for scholarly reasons | P212, F32 deprecation register, A14:expiry | yes: scheduled deprecation with affected-corpus enumeration; the register the source lacks is what the catalogue requires |
| S-03 | SV-S-03 | a funder demands one headline CO2e figure with no qualifiers | HG05, HG01, F30 rendering of evidence state | yes: the catalogue forbids stripping the quality state at presentation; the number cannot be emitted without its basis |
| S-02 | SV-S-02 | ORDS v0.4 renames a category, breaking historical aggregation | P208, P284, P212 | yes: versioned category mapping with equivalence classes preserves historical totals; the publication lag delays discovery, which the time field makes visible |
| T-05 | SV-T-05 | the household reclassifies the worker as an independent contractor | P192, P258, A11 unresolved input | yes: the determination is a scoped decision on unread thresholds, kept as an unresolved input; the asymmetric consequence is recorded, not resolved |
| T-01 | SV-T-01 | the schedule changes weekly with the care recipient's needs | P259, P293, P215 | yes: amendments as version-bound corrections under a recurring obligation, rather than re-execution of a static document |
| U-05 | SV-U-05 | a partner publishes real records with names removed | P298, P264, A08:disclose | yes: de-identified is still a protected unit under adjacency accounting; the catalogue rejects the publication path regardless of the missing licence instrument |
| U-04 | SV-U-04 | decommissioning proceeds with three platforms unmigrated | P256, P345, P284, A14:withdrawal | yes: closure evidence must list dependents; unmigrated dependents are a recorded loss of support, not a silent breakage |
| E-03 | SV-E-03 | EPA publishes new domain values without a WQX version bump | HG00 payload hash, P345, P265 | yes: the catalogue keys dependencies on content hashes, not version labels alone; a changed list with an unchanged version is still a changed dependency |
| B-03 | SV-B-03 | a map compiled from two surveys with different location-confidence conventions | P282, A10:uncertainty, HG02 meaning | yes: uncertainty semantics must be declared per source before values are compared; structurally valid but semantically incomparable is the catalogue's named adverse case |
| H-06 | SV-H-06 | a scenario fails identically for every adopter | P288, P193, P281 | yes: uniform disagreement with the scenario is evidence against the standard, which the catalogue records as a contradiction candidate rather than as non-conformance |
| E-04 | SV-E-04 | a translation maps a local code to the wrong EPA value and automation carries it into the federal record | HG02, HG04, P310 reconciliation, C11 | yes: reconciliation against destination readback and an optional human boundary before an irreversible effect; the audit trail is the retained original value the catalogue keeps by default |
| I-05 | SV-I-05 | USDA republishes with a changed nutrient-number meaning | P282, P195, P345 | yes: a semantic change on an upstream identifier invalidates the index through the dependency closure; the missing watcher is the catalogue's invalidation trigger |
| Q-05 | SV-Q-05 | a member revokes caregiver access while the caregiver holds an unexpired token | P244, HG00 authority expiry, A14:withdrawal | yes: a freshness fence re-checks authority at dispatch; unexpired tokens without a fence are the gap the catalogue names |
| A-06 | SV-A-06 | a lab adopts a new extraction method under an existing analyte name, bypassing the method process | P282, P288, HG01, A11 missing acceptance | yes: a changed meaning under an unchanged identifier is the catalogue's named adverse case; independent annotation disagreement is the detector |
| A-01 | SV-A-01 | a server implements Phenotyping but not Core, so observations cannot resolve studies | C02 referents, HG02 missing keys, V12 bound ports | yes: an unresolved join edge blocks the deployment in the catalogue; the module structure that permits it is the missing bound-port rule |
| N-04 | SV-N-04 | EU and eForms profiles define one field with different cardinality | P274, P273, A13:excludes | yes: an invalid combination in the finite configuration space; the catalogue computes it before publication |
| S-04 | SV-S-04 | a self-assessed score is challenged by an independent teardown with no adjudication route | P288, C11, A11 missing authority | yes: disagreement recorded; without a named adjudicator the claim stays open, which the catalogue states rather than resolves |
| R-02 | SV-R-02 | repository software decommissioned, only storage remains, fixtures held in a separate repository | P269, P265, A17:offline | yes: cold restore is the design case and must be rehearsed; fixtures must be sealed with the content, which the separate repository does not guarantee |
| R-05 | SV-R-05 | rights change to restricted after manifests are cached widely; stable URLs propagate images | P342, A09:unknown coverage, P244 | yes: replica inventory and freshness fences at the image service; the catalogue records unknown downstream copies as an open state, the same pattern as iteration 1's consent-withdrawal cases |

### Composed wholes proposed by the agent, compared with X01 to X12

| Composed system | Members | Families | Closest chain | R | Note |
| --- | --- | --- | --- | --- | --- |
| C1 Water evidence chain | E-03 E-04 E-01 E-02 | F17 F21 F03 F13 F38 | X09 | R14 R16 R10 | Measured records and simulated results kept in distinct evidence bases (HG01 OBSERVATION versus SCENARIO) under one WQX version and one location identity; the 'as is' disclaimer is the promotion rule. Covered. |
| C2 Repair impact ledger | S-02 S-03 S-04 | F14 F17 F02 F08 F38 | X08 | R14 R31 R27 | Category identifier and ORDS version as the joint invariant, quality qualifier travelling with every aggregate, share-alike licence inherited. The agent flags that the invariant depends on the unsampled ORDS standard; the catalogue carries that as an unresolved accepted source. Covered. |
| C3 Conformance-driven standards development | H-06 H-04 G-01 G-02 | F31 F10 F25 F38 | X12 | R29 R32 R14 | Version under test shared by scenarios, reference implementation and adopter; defect reports split implementation-wrong from standard-ambiguous (P288, P193); never against production data (H-04 R3 as an authority constraint). Covered. |
| C4 Machine-readable regulation loop | H-01 J-06 N-02 N-04 | F05 F10 F13 F02 F38 | X07 | R30 R14 R25 | Problem statement identity from suggestion to adopted standard to published policy to contract; geography and organisation identifiers shared; the 20-minute lead is an inherited timing contract. Covered. |
| C5 Building information spine | F-03 F-04 L-03 N-01 | F02 F04 F27 F16 F38 | X03 | R17 R14 R30 | One equipment concept across bSDD class, IFC entity, BEDES term and Brick class is a cross-system identity equivalence (P284); unit-dimension and no-IFC-recreation rules inherited. First appearance of X03 as a sampled composition. Covered. |
| C6 Portable evidence for health decisions | Q-04 Q-05 Q-07 | F03 F06 F36 F17 F38 | X06 | R23 R27 R14 | Patient identity within a site and concept identity across sites with the vocabulary version pinned; analyses travel, data does not (P264). Covered. |
| C7 Identity continuity across a shutdown | U-04 O-04 O-06 J-04 | F06 F02 F07 F32 F38 | X04 | R27 R30 R14 | Subject identifier per relying party preserved through decommissioning by a successor mapping (P284, P256); clients never hold third-party credentials; three credential formats negotiated. Covered. |
| C8 Agricultural decision provenance | A-01 A-05 A-06 | F22 F03 F02 F13 F38 | X06 | R21 R31 R14 | Sample identity from order to result, germplasm and study identity, unit abbreviations shared; method identity on every analyte; data-only constraint inherited as an environment binding. Covered. |
| C9 Preservation-grade cultural publishing | R-02 R-05 R-06 X-03 | F33 F29 F06 F02 F38 | X11 | R12 R24 R27 | Object identifier across storage, manifest and citation with rights status attached; a citation resolving after the software is gone is the cold-restore property (P269). Covered. |
| C10 Grid change with a safe floor | D-02 D-05 | F35 F26 F38 | X10 | R20 R28 R14 | Equipment identity and active limit shared between substation configuration and edge control; default fallback and edition gate inherited; a defined safe state when the link fails is the C07 timeout path. Covered. |

### Generators proposed by the agent, compared with F37

| Generator | Families | Anchors | Note |
| --- | --- | --- | --- |
| C11 Conformance-Pack Builder | F37 F31 F21 | P343 P344 P266 P305 P303 | Schema plus party-role model plus acceptance criteria to scenarios, synthetic fixtures, a counterparty simulator and a report splitting implementation defects from standard ambiguities; concrete product a BrAPI v2.1 Phenotyping pack. A configurator over generated protocol cases and guards. Covered. |
| C12 Requirement-Card Compiler | F37 F01 F31 | P191 P303 P200 P305 | Requirement list to per-requirement cards marking machine-checkable versus human-judged with the check or the reviewer prompt; concrete product a twenty-card bSDD deck. The rule that a card without a threshold must say so is HG05's preserved unknown. Covered. |

### Family fits without an anchoring proof record (candidate additions, not counted)

- A-03: integrated state-space population-dynamics likelihood fitting has no anchoring record beyond P322 and P347
- C-06: measurement-plan to result binding for dimensional metrology (characteristic identity through plan, execution and statistics) has no anchoring record beyond P184 unit-aware findings
- D-02: substation protection-configuration semantics (IEC 61850 SCL) have no anchoring record; the transform and validation shape anchors on P310 and P261
- F-03: ISO 704 definitional quality (circularity, negativity, accuracy of definitions) as a human-judged gate has no anchoring record beyond P288 reliability measures
- N-01: minimality of a relationship set as a design constraint to be guarded across releases has no anchoring record; P309 architecture rules are the nearest

### Extension proposals (never counted as coverage)

- none

No case required a new family, semantic rule or adapter. Three cases (G-02, N-02, N-04 stresses) hit the catalogue's declared unsupported-requirement path, which is a blocked path, not an extension. The agent's 108 proposals, ten compositions and two generators are products within existing families.

### Findings

**Verdicts.** 54 COVERED, 0 PARTIAL, 0 UNCOVERED, 0 NO-WITNESS. 54 of 54 stress variations are expressed by an axis value, variation rule or proof record. Cumulative after two iterations: 108 of 108 cases construct; 107 of 108 stresses are expressed; no extension proposal has been needed.

**A broader sample than iteration 1.** The blind agent's second draw contains fourteen software tools, engines or reference implementations (FIMS, WITSML Studio, CoMPAS, open-dynamic-export, SWMM, EPANET, OpenEPCIS, DCSA TNT, Moov iso20022, Login.gov, Humanitarian ID, fdc-api, Open Waters, the Bodleian manifest editor), six governance or verification procedures (ADAPT's nine-state process, bSDD verification, OPC UA release tagging, the UK open standards process, the GDS catalogue, US Core's ballot route), three legal or regulatory instruments (MDS policy, I-9, EU right to repair) and three scientific models (FIMS, SWMM, EPANET). As a result F35 has its first two primary cases (D-05, D-02), F21 its first two primary cases (SWMM, EPANET), F27 its first primary case (QIF), and F36, F18, F22, F15, F13 and F14 are all exercised again. R17 (design-to-manufacturing correspondence) is exercised for the first time through QIF. Every chain X01 to X12 has now appeared at least once; X03 appears twice.

**Still never exercised after two iterations.** Families F12 (routing, packing, network allocation), F19 (diagnosis and next-evidence selection) and F20 (trade-off, portfolio and allocation decisions); requirements R01, R26 and R32; variation rule V14, which is excluded by contract. F11, F16, F23 and F38 were hit in iteration 1 only. The absence of F12, F19 and F20 across 108 GitHub-hosted cases is consistent with the discovery bias: optimisation, diagnosis and allocation needs are rarely published as open specifications.

**Where the catalogue named what the source lacks.** Twelve stress cases land on a catalogue rule the real artefact is missing: whole-input validation before actuation for a malformed schedule (open-dynamic-export); a tenant-isolation contract for a shared demo (CoMPAS); a review clock after a badge is granted (bSDD); a declared canonicalisation before hashing across time zones (EPCIS); an authority envelope that travels with the deployment rather than the README (DCSA TNT); an emergency profile with its own lead-time contract (MDS); a preserved-contract check on technical corrections (US Core); a capability-envelope test rather than specification conformance (EUDI wallets, Ed-Fi Discovery); content-hash rather than version-label dependency keys (WQX domain values); interaction tests across profiles (OCDS extensions); a freshness fence on delegated authority (CARIN caregivers); reconciliation against destination readback before an irreversible regulatory submission (Open Waters).

**Thin and degenerate fits.** B-01 (OMF) is a degenerate case: the sampled URL holds a licence and nothing else, so the construction is the catalogue's missing-source path. It is also the same origin iteration 1 sampled, where mirrors supplied the content. Nine cases were read thinly by the agent (H-04, I-01, N-02, O-04, Q-05, Q-07, R-06, X-03, M-02) and their mappings rest on the structure the agent could see.

**No-anchor ledger additions.** Four new entries: integrated state-space population-dynamics fitting (FIMS); measurement-plan to result binding for dimensional metrology (QIF); IEC 61850 substation protection-configuration semantics (CoMPAS); minimality of a relationship set as a guarded design constraint (Brick); and ISO 704 definitional quality as a human-judged gate (bSDD). Cumulative no-anchor entries: 17.

**Rediscovery.** Four documents recur from iteration 1 (Modus, BuildingSync, OMF, TEI) and nine further organisations recur with a different document (RESO, Ed-Fi, OHDSI, DCSA, Open Contracting Partnership, Open Repair Alliance, buildingSMART, GS1 EPCIS, BrAPI). Unique origin clusters after two iterations: 104 of 108 cases. Saturation is not yet visible at the document level.

**Composed wholes.** The ten compositions fall on X09, X08, X12, X07, X03, X06 (twice), X04, X11 and X10; the two generators are F37 configurators over generated protocol cases (C11) and over a requirement relation with an explicit human-judged partition (C12). C5 (building information spine) is the first sampled composition on X03, the configured-product-to-maintained-asset chain.

**Discovery-side shortages, kept separate.** ISIC T again has zero readable sources; ISIC G and L drew from pools below the five-origin target with cluster-adjacent picks; nine thin reads; the EPCIS five-versus-six event-type discrepancy is unresolved on the agent's side.

**Process notes.** The received prompt hash is identical to iteration 1's. The final message again arrived in two continuation blocks and was joined by the committed extractor. No PR exists; the branch is pushed after this iteration.

### Cross-scale family checks (analyst reasoning, no primary sources; blind-agent prompt unchanged)

Seven patterns surfaced by iteration 2's cases, chosen to differ from iteration 1's eight, each taken across regimes with the record form that regime actually keeps.

#### SC9. Simulation as evidence: model output versus observation

Source cases: E-01 EPANET, E-02 SWMM, A-03 FIMS, D-02 rehearsal, H-01 policy rehearsal proposal.

| Regime | Data form kept in that regime | Family mapping | Holds? |
| --- | --- | --- | --- |
| Engineering: hydraulic and digital twins, hardware in the loop | Scenario runs `{model_version, params, inputs, outputs, t, validity_scope, tolerance}` alongside SCADA observations | F21 + HG01 SCENARIO basis + R16 + P322, P347 | holds |
| Biology and pharmacology: in-silico models, PK/PD | Model predictions paired with assay results `{compound, model, predicted, observed, CI}` | F21 + F18 + P268 accuracy gating | holds |
| Economics and finance: stress tests, macro models | Scenario tables `{scenario, assumptions, projected_metric, horizon}`; regulators accept the output as evidence by rule | F21 + F20 shape + A11 sign-off | holds; acceptance is an explicit authority act |
| Climate: gridded model output in CF and GeoZarr conventions | Arrays with convention metadata `{variable, grid_mapping, source: model or obs}` | F21 + F28 + P325 | holds; the source-versus-model flag is the basis field |
| Law: mock trials, moot courts | Rehearsal records; never evidence | F21 shape only | holds; the regime itself forbids promotion |

Verdict: HOLDS. Every regime keeps model output and observation apart and admits promotion only by an explicit acceptance act; the catalogue's basis field and A11 sign-off are that act. The "as is" disclaimer on EPANET and SWMM is the same rule in prose.

#### SC10. Reflexive conformance: testing implementations tests the standard

Source cases: H-06 Conformance Gateway, F-03 bSDD, G-02 OpenEPCIS, C-05 OPC UA, P-03 Ed-Fi, O-06 EUDI, Q-04 ballot.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Metrology: inter-laboratory round robins, gauge R&R | `{lab, sample, method, result, consensus, deviation}`; the reference sample calibrates labs and exposes method ambiguity | F31 + I-class oracle independence + P288 | holds |
| Law: litigation as statute testing | Case law `{case, clause, holding, ambiguity_found}`; rulings feed drafting | F31 + F05 + P193, P281 | holds |
| Immunology: self versus non-self testing with clonal selection | Repertoire tables `{clone, antigen, affinity, tolerance}`; the test set updates the tester | F31 shape + C05 iteration | holds at model level |
| Sport: referee rulings clarifying rules | Ruling logs `{match, incident, rule, decision}` | F10 + F05 | holds |
| Software: conformance suites and reference implementations | Scenario results `{scenario, party, step, outcome, standard_version}` | F31 + P266, P343, P267 | holds |

Verdict: HOLDS. The round-robin principle is the catalogue's oracle-independence rule; uniform failure across independent implementations is evidence against the standard in every regime, which is P288 feeding P193.

#### SC11. Decommissioning and orphaned dependencies

Source cases: U-04 Humanitarian ID, K-05 archived library, I-04 NDB sunset, R-06 pinned Node, B-01 empty repository, I-01 unreachable README.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Software and services: end-of-life notices | `{asset, eol_date, successor, migration_path, dependents}` | F32 + F07 + P345, P256, P272 | holds |
| Ecology: keystone species removal and trophic cascades | Food webs `{species, depends_on, strength}`; removal effects propagate through the web | P345 closure shape | holds; nature enumerates dependents by consequence, the catalogue by manifest |
| Cell biology: apoptosis and senescence | Programmed shutdown with cleanup signals `{cell, signal, phagocytosed_by}` | F07 closure with P256 evidence | holds |
| Business: product end-of-life and spare-parts obligations (S-04) | `{model, last_sale, parts_until, service_until}` | F08 + P215, P185 | holds |
| Infrastructure: bridge closure, utility decommissioning | Successor-service plans `{asset, closure_date, alternative_route}` | F16 + F32 | holds |

Verdict: HOLDS. The rule "enumerate dependents before removal" is universal; only engineered and legal regimes add a named successor mapping, which is why P256's closure evidence lists dependents and successors and ecology does not.

#### SC12. Uncertainty as a first-class field

Source cases: B-03 GeMS confidence fields, S-03 quality grades, A-03 experimental status, E-01 no stated tolerance, H-01 informational user rule.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Geology: confidence per contact and fault | `{feature, existence_conf, identity_conf, location_conf_m, source}` | A10 uncertainty + P323 | holds |
| Genomics: Phred quality per base | `{position, base, phred}`; uncertainty travels with every record | A10 + boundary numeric field | holds |
| Metrology: GUM uncertainty budgets | `{measurand, value, u, k, contributions}` | P323 propagation + P347 | holds |
| Law: standards of proof | `{claim, standard: preponderance, clear and convincing, beyond reasonable doubt, finding}` | A06 four-state evidence + F31 | holds |
| Finance: ratings with outlooks, value at risk | `{instrument, rating, outlook, VaR, horizon}` | F18 + A06 probability | holds |

Verdict: HOLDS. Every regime records uncertainty as a field beside the value and refuses comparison across undeclared conventions; the GeMS stress (two surveys, two confidence conventions) is Phred versus a different quality scale, which the meaning field catches.

#### SC13. Delegated authority and its revocation

Source cases: J-04 client, server and third party; Q-05 caregivers; O-04 one account across agencies; O-06 wallets; R-05 rights by user class; T-05 identity documents.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Law: power of attorney, guardianship, agency | Registers `{principal, agent, scope, purpose, granted, expires, revoked}` | F06 + P206 + authority field (principal, resource, action, purpose, delegation, expiry) | holds |
| Computing: OAuth scopes, capability tokens | `{subject, scope, audience, iat, exp, revocation}` | F06 + P206, P244 | holds |
| Endocrinology: hormonal instruction with receptor gating | `{signal, receptor, target, downregulation}`; released molecules act until degraded | F06 shape; revocation as expiry | holds; unrevocable in-flight effects match the unexpired-token stress |
| Business: procurement delegation limits | Delegation matrices `{role, limit, approver, valid_from, valid_to}` | F06 + F05 | holds |
| Military and civil chains of command | Orders with authority references `{order, issuer, authority_ref, validity}` | F06 + P196 dependency closure of authority | holds |

Verdict: HOLDS. The authority sub-fields the catalogue requires (scope, purpose, delegation, expiry) appear in every regime's register; the unexpired-token problem is universal and is what the freshness fence exists for.

#### SC14. Additive extension without breaking the core

Source cases: N-04 OCDS extensions and profiles, N-01 Brick minor releases, C-05 companion specifications, L-01 ignorable local fields, X-02 convention registry, P-04 four forms.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Bacterial genetics: plasmids and horizontal gene transfer | `{host, plasmid, incompatibility_group}`; two plasmids of one group cannot coexist | F37 feature model + P274 interaction tests | holds; incompatibility groups are the pairwise conflict check |
| Law: amendments layered on statutes | `{statute, amendment, inserts, repeals}` | F32 + P212 | holds |
| Contracts: riders and annexes | `{contract, annex, precedence_clause}` | F08 + P292 conflict strategy | holds |
| Language: loanwords | Lexicon entries with origin | F04 | holds trivially |
| Software: semantic versioning, protocol extension negotiation | `{core_version, extension_id, additive, conflicts_with}` | F37 + P260, P273, P302 | holds |

Verdict: HOLDS. The OCDS stress (two profiles, one field, two cardinalities) is the plasmid incompatibility case: additivity holds per extension and fails pairwise, which is why the catalogue demands interaction tests rather than per-extension validation.

#### SC15. Timing contracts between publisher and consumer

Source cases: H-01 20-minute lead time, I-04 sunset date, K-06 review date, S-02 publication lag, U-04 decommission date, D-05 ramp rates.

| Regime | Data form | Family mapping | Holds? |
| --- | --- | --- | --- |
| Signal processing: sampling theorem | `{signal_bandwidth, sample_rate}`; poll rate must exceed twice the change rate | R19, R20 timing + C07 | holds; MDS's 20-minute lead is a sampling condition on policy polling |
| Ecology: phenology and pollinator matching | `{species, event, date}`; a mismatch is a broken lead-time contract | A05 + P215 | holds |
| Molecular biology: mRNA half-life versus transcription rate | `{transcript, synthesis_rate, half_life}` | A05 expiry + P244 passive fence | holds |
| Finance: settlement cycles, notice periods | `{trade, T, settle_at, notice_days}` | P224 + P215 | holds |
| Law: sunset clauses and statutory notice | `{instrument, effective, sunset, notice_period}` | F08 + A14 expiry | holds |

Verdict: HOLDS. Publish-then-poll with a minimum lead is the same contract as Nyquist sampling and as phenological matching; the catalogue's time field with lead, expiry and poll interval is sufficient in every regime.

#### Break watch after iteration 2

No pattern broke. Iteration 1's candidate crack, shared state with no owner, did not recur in a damaging form: X-02's shared meaning between two conventions has divided ownership resolved by a vote, which the catalogue expresses through F10 authority. Two new observations for the watch list. First, voluntary instruments (the DOL sample agreement, the GDS catalogue entry, self-assessed repairability scores) form a modality gradient from mandatory through recommended to voluntary and self-declared; the catalogue's meaning field carries modality, but the gradient's effect on evidence strength is carried only by A11 acceptance, which is coarse. Second, the E-01 stress shows a decision proceeding on model output with no statable tolerance; the catalogue can only record the decision under an explicit unknown state, which is honest but is not a construction of the decision itself. Neither is a break; both are places where later iterations should look for a case the catalogue cannot express.

#### Cumulative after iteration 2

| Measure | Value |
| --- | --- |
| Iterations | 2 |
| Cases mapped | 108 |
| Unique origin clusters | 104 |
| COVERED | 108 |
| PARTIAL | 0 |
| UNCOVERED | 0 |
| NO-WITNESS | 0 |
| Stress variations expressed by catalogue | 107 of 108 |
| Extension proposals (not counted as coverage) | 0 |

| Family | Name | Cases (any role) | Cases (primary) | Iterations hit |
| --- | --- | --- | --- | --- |
| F01 | Source formalization and operating-model assembly | 18 | 7 | 1,2 |
| F02 | Entity identity and relationship registries | 60 | 4 | 1,2 |
| F03 | Data transformation, migration and synchronization | 59 | 30 | 1,2 |
| F04 | Query, retrieval and knowledge navigation | 17 | 6 | 1,2 |
| F05 | Rules, policies and scoped decisions | 17 | 3 | 1,2 |
| F06 | Authority, access, delegation and information release | 43 | 6 | 1,2 |
| F07 | Admission, readiness and lifecycle transitions | 9 | 1 | 1,2 |
| F08 | Agreements, entitlements and recurring obligations | 11 | 2 | 1,2 |
| F09 | Workflow and case coordination | 7 | 2 | 1,2 |
| F10 | Collaborative review and decision records | 19 | 3 | 1,2 |
| F11 | Planning, scheduling and qualified assignment | 2 | 0 | 1 |
| F12 | Routing, packing and network allocation | 0 | 0 | - |
| F13 | Transactions, external effects and reconciliation | 11 | 1 | 1,2 |
| F14 | Quantitative ledgers, allocation and valuation | 6 | 1 | 1,2 |
| F15 | Material supply and fulfillment | 2 | 2 | 1,2 |
| F16 | Asset maintenance and service reliability | 2 | 0 | 1 |
| F17 | Measurement, analytics and reporting | 20 | 1 | 1,2 |
| F18 | Prediction, inference and uncertainty | 3 | 0 | 1,2 |
| F19 | Diagnosis and next-evidence selection | 0 | 0 | - |
| F20 | Trade-off, portfolio and allocation decisions | 0 | 0 | - |
| F21 | Simulation and digital twins | 9 | 2 | 1,2 |
| F22 | Experiment and measurement campaigns | 4 | 1 | 1,2 |
| F23 | Learning, assessment and qualification paths | 2 | 0 | 1 |
| F24 | Software application construction and maintenance | 7 | 3 | 1,2 |
| F25 | API, connector and event-service construction | 36 | 8 | 1,2 |
| F26 | Infrastructure, deployment and operations configuration | 12 | 1 | 1,2 |
| F27 | Engineering design and manufacturing preparation | 4 | 1 | 1,2 |
| F28 | Spatial and spatiotemporal information products | 7 | 1 | 1,2 |
| F29 | Document, media and communication construction | 27 | 5 | 1,2 |
| F30 | Interactive interfaces and visualization construction | 9 | 4 | 1,2 |
| F31 | Verification, qualification and assurance | 64 | 5 | 1,2 |
| F32 | Change impact, repair and modernization | 53 | 0 | 1,2 |
| F33 | Recovery, replay and records lifecycle | 18 | 3 | 1,2 |
| F34 | Streaming detection and governed response | 9 | 1 | 1,2 |
| F35 | Physical control and embedded automation | 3 | 2 | 1,2 |
| F36 | Analytical model construction and deployment | 5 | 1 | 1,2 |
| F37 | Product-family configurator generation | 12 | 1 | 1,2 |
| F38 | Assembly of systems from multiple families | 2 | 0 | 1 |

Families never hit: F12, F19, F20

O exercised: O01(7), O02(19), O03(60), O04(57), O05(30), O06(10), O07(44), O08(24), O09(17), O10(4), O11(4), O12(8), O13(2), O14(27), O15(32), O16(83), O17(35), O18(54)
O never exercised: none

C exercised: C01(76), C02(30), C03(5), C04(36), C05(9), C06(21), C07(14), C08(3), C09(7), C10(5), C11(22), C12(2), C13(19), C14(24)
C never exercised: none

V exercised: V01(7), V02(2), V03(12), V04(7), V05(6), V06(6), V07(5), V08(2), V09(4), V10(3), V11(5), V12(2), V13(15), V15(3), V16(22), V17(5), V18(2)
V never exercised: V14

R exercised: R02(57), R03(1), R04(14), R05(4), R06(18), R07(3), R08(2), R09(22), R10(11), R11(8), R12(30), R13(13), R14(7), R15(3), R16(7), R17(1), R18(6), R19(5), R20(3), R21(3), R22(2), R23(5), R24(15), R25(22), R27(28), R28(9), R29(16), R30(55), R31(14)
R never exercised: R01, R26, R32

X exercised: X01(1), X02(10), X03(2), X04(4), X05(2), X06(7), X07(6), X08(5), X09(4), X10(3), X11(16), X12(3)
X never exercised: none

| Axis | Values seen (count) |
| --- | --- |
| A01 | artifact(5), entity graph(6), event(4), geometry(4), model(5), quantity(2), record(33), rule(3), text(8) |
| A02 | construct(1), coordinate(2), decide(1), qualify(2), quantify(1) |
| A03 | DAG(6), chain(5), hierarchy(5), state machine(4), tree(4) |
| A04 | event-driven(3), interactive(1), real-time(2), streaming(3) |
| A05 | calendar(12), event time(2), interval(6), known-at time(5), uncertain clock(1), valid time(3) |
| A06 | classical(2), four-state evidence(2), interval uncertainty(3), probability(6), unknown(1) |
| A07 | distributed(19), federated(1), historical replay(1), local transactional(1), offline(1), replicated(4), shared(1) |
| A08 | actuate(5), approve(13), commit(9), disclose(26), propose(1), read(2) |
| A09 | closed finite domain(5), open stream(1), paginated snapshot(5), partial collection(11), unknown coverage(5) |
| A10 | coordinates(5), exact(3), floating tolerance(2), topology(2), uncertainty(1), units(7) |
| A11 | accepted upstream interpretation(25), adjudication(10), recorded runtime input(12), sign-off(20) |
| A12 | UI(3), generator(3), infrastructure(3), office/media(4), physical design(3), records(1), software(8) |
| A13 | alternative(16), excludes(1), mandatory(7), numeric parameter(2), optional(5), requires(13) |
| A14 | backend replacement(2), correction(7), expiry(8), migration(16), new source(3), policy revision(29), withdrawal(5) |
| A15 | behavioral refinement(8), physical validation(4), statistical performance(2), structural validity(15) |
| A16 | conflicting(2), invalid(6), missing(5), out-of-envelope(4), partial effect(3), stale(6), unavailable(5) |
| A17 | cloud(1), embedded(4), federated(7), local(2), offline(6), shared(3) |
| A18 | capacity(1), concurrency(4), latency(3), memory(1) |

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
- it2 A-03: integrated state-space population-dynamics likelihood fitting has no anchoring record beyond P322 and P347
- it2 C-06: measurement-plan to result binding for dimensional metrology (characteristic identity through plan, execution and statistics) has no anchoring record beyond P184 unit-aware findings
- it2 D-02: substation protection-configuration semantics (IEC 61850 SCL) have no anchoring record; the transform and validation shape anchors on P310 and P261
- it2 F-03: ISO 704 definitional quality (circularity, negativity, accuracy of definitions) as a human-judged gate has no anchoring record beyond P288 reliability measures
- it2 N-01: minimality of a relationship set as a design constraint to be guarded across releases has no anchoring record; P309 architecture rules are the nearest

Origin clusters rediscovered in more than one iteration:
- AgGateway | Modus: it1 A-02, it2 A-06
- BuildingSync consortium (US DOE) | BuildingSync schema: it1 F-02, it2 L-03
- Global Mining Guidelines Group | Open Mining Format: it1 B-01, it2 B-01
- TEI Consortium | TEI P5 Guidelines: it1 H6-01, it2 X-03



## Halt of the blind-agent phase after iteration 3 (partial)

The user stopped the blind-agent research loop after iteration 3's response arrived and before its mapping was complete. Iteration 3's verbatim response is retained at `coverage/iterations/03.raw.md` (54 briefs, 112-entry inventory, 70 of 112 snippet-only, seed 1158297115365469046, prompt hash identical to iterations 1 and 2). The 22 cases mapped before the halt are retained at `coverage/iterations/03.partial.jsonl`; they are not counted in the cumulative tally, which stands at iterations 1 and 2 (108 of 108 COVERED, 107 of 108 stresses expressed). All 22 partial mappings were COVERED with expressed stresses; the strongest observations from the partially mapped set are recorded here so they are not lost: beneficial-ownership disclosure (EITI) is anchored unusually well by P202, P253, P254 and P291; Basel's non-binding waste classification with binding consequences is a second data point for the modality-gradient watch item; the digital emblem's undetectable validation (not yet mapped) is the strongest strain candidate seen so far, because the boundary contract presumes a handoff both parties know about. Iteration 4's agent was launched and then stopped without a response. The next phase is procedural generation at volume, recorded in a new section when it starts.

