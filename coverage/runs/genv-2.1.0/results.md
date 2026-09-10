## Phase 2 results: generation version genv-2.1.0

### The build and the gate

One blind Opus agent, given `coverage/gen/v2_prompt.md` and the three Phase 1 inventories, delivered in about 65 minutes: a dictionary of 526 ingredients on nine axes (298 grounded in inventory items, 217 in ISIC or FORD entries, 11 authored; all 371 inventory items walked), three programs with the mandated command lines and no language-model step, 5,000 admitted cases from 6,110 attempts (88 contradictions, 235 unresolved searches, 787 proposals diverted to the review pool), a recorded seed, byte-identical reruns, 37 machine checks, 20 of 20 deliberately broken variants caught, and generation plus checking in under seven seconds. The agent recorded one setup revision (dictionary 2.0.0 to 2.1.0: six generic inputs added after 1,867 cases had a deliverable resting on an assumed input) and five weaknesses of its own build: activity-to-product fit holds for 16,506 of 19,894 components by its own measure; beneficiary matched the domain in 2,528 cases; input identity falls back to another entity type when none was minted; 363 admitted cases carry an assumed input form on a non-deliverable part; component labels can repeat within a case.

The gate passed on all eight checks after two fixes on the gate's side (its verdict parser did not read the checker's aggregate report shape, and an empty input list backed by a recorded assumption is informational, not missing):

| gate | result |
|---|---|
| G1 determinism | PASS  seed=18389053631685725381 identical=True differs_on_seed_b=True |
| G2 checker | PASS  batch rejected=0 undetermined=5000 / broken 20/21 rejected / mutants 50/120 rejected, 0 accepted, 70 undetermined {"m3_norequirements": {"rejected": 12, " |
| G3 references | PASS  entries=131661 unresolved=0 (in 0 cases) missing_fields={} expand=PASS |
| G4 duplicates | PASS  exact=0 structural=0 distinct_structures=5000 duplicate_ids=0 |
| G5 diversity | PASS  regimes=7 domains=27 kinds=10 cross=886/500 shortfalls={} unparsed=0 |
| G6 leak | PASS  hard_keys=[] soft_keys=['INP-FAMILY-RECORD', 'SCL-EXTENDED-FAMILY', 'axis'] id_hits=133386 phrase_hits=0 |
| G7 provenance | PASS  grounded_share=0.893 by={"none": 51, "inventory": 298, "taxonomy": 217, "authored": 11} fully_grounded_cases=0/5000 |
| G8 runtime | PASS  generate=7.686 check=2.067 budget=300s |

Two distribution facts measured on the batch matter for reading the results: product use is uneven (a route plan occurs in 6 cases, a field procedure in hundreds), and the same need-plus-products combination recurs across regimes in 120 groups (693 groups on need plus root product), which is the material for the invariance test.

### Canonical form and bridge

The adapter (`coverage/engine/normalize.py`) treats every component product as a deliverable to realize, every component activity as an operation the chain must perform, templated obligations and global constraints as constraints keyed by template, acceptance conditions by ingredient, and conditions, dynamics, situation tags and the need as situation items. Beneficiary and scale are stratifiers, not bridged: the model makes no claim about who benefits, and scale is the cross-scale stratifier next to regime. Two generator-internal admissibility constraints (regime and situation admissibility of vocabulary) were dropped as bookkeeping.

The bridge (`coverage/runs/genv-2.1.0/bridge.json`, sources under `bridge/`) holds 1003 accepted atoms, each with a strength (exact, close, thin), a reason and the count of cases that force it: out 115, proof 150, in 179, rel 13, req 107, con 75, acc 66, sit 298. Strengths: out {'close': 85, 'thin': 12, 'exact': 18}, proof {'close': 135, 'thin': 6, 'exact': 9}, in {'close': 141, 'thin': 15, 'exact': 23}, rel {'exact': 5, 'close': 8}, req {'close': 75, 'exact': 14, 'thin': 18}, con {'exact': 23, 'close': 50, 'thin': 2}, acc {'close': 41, 'exact': 19, 'thin': 6}, sit {'exact': 81, 'close': 187, 'thin': 30}. Every ingredient used in a bridging position has at least one atom; 37 ingredients have only thin atoms, which is the list of things the model has no counterpart for (below). A lexical proposal pass (token overlap between ingredient meanings and the model's role, family, operation, axis and proof texts) was run on a sample as a source of hints; the atoms themselves were judged from the dictionary meanings against the family cards, and the judgment is recorded per atom. Output-role atoms name the family (`F29:Artifact`), because five families produce `Artifact` and three produce `WorkPlan`; without that the solver picked among them arbitrarily.

### Derivation results

Two readings of the same bridge. Strict counts exact and close atoms only; lenient adds the thin atoms. A case is COVERED when every element found a target and every realizing family has a bridged anchoring proof record; PARTIAL when everything is explained but a realizing family has no anchoring record; UNEXPLAINED when a named element found no target. Grounding is well-founded: a family may resolve another family's input only if it is itself grounded back to case inputs, and a family in the chain with no bridged input at all is a name-only fit and counts as unexplained. Suppliers join one level deep, at most four. Each reading ran over the 5,000 cases in under a minute on four workers with no timeouts.

| verdict | strict | lenient |
|---|---|---|
| COVERED | 531 | 2989 |
| PARTIAL | 36 | 209 |
| UNEXPLAINED | 4433 | 1802 |
| NO-WITNESS | 0 | 0 |

By regime (COVERED / PARTIAL / UNEXPLAINED):

| regime | strict | lenient |
|---|---|---|
| R-BIO | 63 / 5 / 658 | 426 / 20 / 280 |
| R-COMP | 267 / 15 / 442 | 460 / 16 / 248 |
| R-ECO | 13 / 0 / 708 | 342 / 42 / 337 |
| R-HOME | 23 / 6 / 685 | 367 / 30 / 317 |
| R-LAW | 45 / 5 / 656 | 554 / 30 / 122 |
| R-ORG | 95 / 5 / 605 | 452 / 35 / 218 |
| R-PHYS | 25 / 0 / 679 | 388 / 36 / 280 |

Gap classes (occurrences and distinct cases):

| class | strict | lenient |
|---|---|---|
| model gap candidate: no counterpart (only thin bridge atoms) | 9836 in 4137 cases | 243 in 221 cases |
| strictness: family realized without any bridged input (name-only fit) | 1547 in 1146 cases | 1141 in 951 cases |
| model gap candidate: input consumed by no family in the chain | 942 in 751 cases | 820 in 692 cases |
| operation not performed by any chain family (activity/product mismatch or gap) | 747 in 688 cases | 623 in 587 cases |
| no qualifying operation (O16) in the chain | 28 in 28 cases | 5 in 5 cases |

### Gap register

**1. No counterpart in the model.** The 37 ingredients that carry only thin atoms decide the strict verdict of 4137 cases. They fall into seven groups, each a candidate hardening item or an explicit scope statement:

- human-performed activities: rehearse a scenario with the real parties (540); consult affected people and record the input (409); perform or present to an audience (330); facilitate a structured session (323); conduct structured interviews (308); carry out a care or service visit and record it (217); negotiate terms between parties (51); collect and label a physical sample (80); fabricate a physical part (33).
- physical environment conditions: extreme cold affecting equipment and people (205); heat and humidity affecting material and people (255); dust, vibration and mechanical noise (87); a hazardous physical environment (181); a controlled clean or sterile area (408).
- authority and presence outside recorded delegation: customary authority not recorded in statute (583); a voluntary standard with no enforcement (111); a site with contested claims or access (540); an uncontrolled public space (508).
- human supervision, capacity and knowledge held by people: work at night with reduced supervision (243); the person performing the work is unsupervised (136); high staff turnover (297); the people who hold the knowledge leave (140); the party who must act lacks tooling, staff or expertise (294); one person or household acts alone, without an organisation (246); undocumented local knowledge held by practitioners (939).
- experiences as products and human-outcome acceptance: a rehearsed exercise run with the real parties (397); an exhibition or public installation (70); a structured game or participatory activity (11); a rehearsal is completed within the stated time by the real parties (209); the receiving party can continue without contacting the sender (438); a replacement part is obtainable for a stated period (93).
- operating states with no axis value: an emergency in which the normal process cannot be followed (257); operating in a degraded but safe mode (87); a queue whose order is itself contested (234).
- expressive and everyday purposes: mark an occasion or a loss in a way that holds (41); give an experience a form other people can encounter (39); carry out a household task safely without professional support (18).

The reading of these is the same as Phase 1's watch items, now at volume: the model constructs information systems and physical designs; it does not perform human acts, represent physical environments, or model authority that is not a recorded delegation. Human input enters only as an attributable boundary (C11, A11). Whether that is a scope statement or a gap is the user's call; the register gives the case counts either way.

**2. Missing port edges between families.** When a part realized by one family feeds a part realized by another (an input, embed or emit relationship) and no output role of the first is an input role of the second, the second family is left without a grounded input. The most frequent pairs (strict reading):

| from family | to family | relationship | cases | example |
|---|---|---|---|---|
| F32 | F09 | RK-INPUT | 20 | UC-00267: PRD-RECOVERY-PLAN -> PRD-HANDOVER-PROTOCOL |
| F32 | F09 | RK-EMBED | 13 | UC-00267: PRD-RECOVERY-PLAN -> PRD-HANDOVER-PROTOCOL |
| F32 | F34 | RK-EMBED | 11 | UC-00077: PRD-RECOVERY-PLAN -> PRD-EARLY-WARNING |
| F09 | F14 | RK-INPUT | 10 | UC-00323: PRD-HANDOVER-PROTOCOL -> PRD-BUDGET-PLAN |
| F09 | F34 | RK-EMBED | 10 | UC-00288: PRD-FIELD-PROCEDURE -> PRD-EARLY-WARNING |
| F19 | F29 | RK-INPUT | 9 | UC-00023: PRD-DECISION-AID -> PRD-EXPLAINER |
| F32 | F34 | RK-INPUT | 9 | UC-00077: PRD-RECOVERY-PLAN -> PRD-EARLY-WARNING |
| F19 | F29 | RK-EMBED | 9 | UC-00023: PRD-DECISION-AID -> PRD-EXPLAINER |
| F09 | F34 | RK-INPUT | 9 | UC-00288: PRD-FIELD-PROCEDURE -> PRD-EARLY-WARNING |
| F17 | F34 | RK-EMBED | 8 | UC-00094: PRD-LINEAGE-MAP -> PRD-EARLY-WARNING |
| F09 | F21 | RK-INPUT | 7 | UC-00015: PRD-FIELD-PROCEDURE -> PRD-REHEARSAL-SPACE |
| F29 | F21 | RK-EMBED | 7 | UC-00297: PRD-WORKED-EXAMPLE -> PRD-REHEARSAL-SPACE |

The encoding already showed the shape behind this: 37 of the 115 port roles are produced by some family and consumed by none, and 58 are consumed but produced by none. Family outputs mostly terminate; the composed chains in the master bind families in prose, not through declared ports. The three pairs at the top (repair plans into workflows, workflows and repair plans into detection and response, decision aids into documents) are concrete port-edge or adapter proposals.

**3. Products realized by a family that has no input role for what the case supplies.** These are name-only fits caught by the grounding rule. Top products (strict): an early-warning arrangement with escalation rules via F34 (128); a configurator that emits a tailored product via F37 (89); a handover protocol with a checklist artefact via F09 (46); a controlled environment for practising a real task via F21 (44); a documented recovery plan with rehearsed steps via F32 (41); a documented published dataset via F03 (33); a plain-language explanation of a technical result via F29 (25); a searchable catalogue with provenance on every entry via F02 (22). Early-warning arrangements composed without a signal input and configurators composed without a family specification are partly the generator's loose composition (its own fit flag marks 17 percent of components) and partly the model: an early warning fed by procedures and people has no input role in F34.

**4. Inputs no family in the chain can take** (lenient reading, top): a physical workspace with access conditions (309; bridged to ResourceModel, consumed only by F11, F12, F19, F22); committed hours of named, qualified people (120; bridged to CalendarModel, ResourceModel, consumed only by F08, F11, F12, F14, F16, F17, F19, F22); consumable material held in stock with a shelf life (76; bridged to MaterialModel, ResourceModel, consumed only by F11, F12, F15, F19, F22, F27); a measured floor plan (40; bridged to Artifact, SpatialDataset, SpatialModel, consumed only by F10, F12, F28, F31, F32); a curriculum, syllabus or learning outcome set (34; bridged to AssessmentModel, CompetencyModel, LearningResourceSet, consumed only by F23); a building information model (30; bridged to Artifact, SpatialModel, consumed only by F10, F28, F31, F32). Production resources (workspace, staff time, stock) are input roles only of the planning, routing, diagnosis and experiment families; a document, register or catalogue built with them has nowhere to put them. Streams reach only detection and control, not measurement and reporting.

**5. Operations required by a part but performed by no family in its chain** (lenient reading, top): build and run a simulation (288; needs O12, product realized by F17); conduct structured interviews (100; needs O01, product realized by F29); observe people or organisms behaving normally (73; needs O01, O13, product realized by F29); consult affected people and record the input (36; needs O17, product realized by F29); hand over work and the items still open (34; needs O08, O17, product realized by F29); carry out a care or service visit and record it (30; needs O08, O17, product realized by F17). Of the components behind this class, 26 percent are flagged by the generator itself as loose activity-to-product fits; the rest say that simulation, scheduling, routing, monitoring and handover are not operations of the document, measurement or workflow families whose products need them, and the port graph gives no supplier path either.

**6. Proof layer.** Realizing families without an anchoring record bridged from the case (strict): F29: a quality and limitation label carried with every figure 121, an annotation guide with adjudication rules 68, an audit procedure with sampling and adjudication rules 12; F30: a simulator for rehearsing a decision before it is real 56; F12: a multi-operator journey or logistics plan 4. Routing (F12) reproduces Phase 1's finding mechanically: the family exists, no proof record covers it. A caveat carried with every figure (the quality label) and an interactive simulator interface have no record under the families that realize them. The lenient reading adds the thin realizations (a drill as F31 qualification, an access pathway as F08 entitlement) with no record. 257 of 349 proof records are never anchored by any derivation; the seven families with no primary record (F12, F22, F27, F28, F35, F36, F38) are unchanged from the encoding.

**7. Parts of the model nothing reaches** (strict): families F18, F26, F36, F38; operation O06; compositions C06, C13; variation rules V05, V07, V09, V11, V14, V15; 67 of 128 axis values; 257 of 349 proofs. The generator's world contains no forecasting, infrastructure, analytical-model or system-assembly product and no dependency-traversal activity, and its situation vocabulary does not carry the model's configuration axes (semantic object, dependency shape, construction target, variability), which the engine could derive from case structure in a later version. This is reported here only; nothing of it goes to the generator, whose expansion follows its own sparse-area counts.

**8. Open inputs.** The model's own question mechanism, not gaps: family input roles the case does not supply. Top (strict): F17 MeasureModel (1595); F29 ArtifactModel (1360); F09 LifecycleState (1301); F29 AuthorizationResult (1180); F09 OperatingModel (1042); F09 WorkflowModel (1010). The world cases start from raw needs; the model presumes accepted measure, artifact, operating and workflow models upstream.

### Cross-regime and cross-scale

Product-level test over the batch: for every product seen at least five times in at least two strata, the dominant realizing family per stratum. By regime: HOLDS 47, STRAINS 12 of 59 products compared. By scale band: HOLDS 38, STRAINS 18 of 56. No product breaks (realized in one stratum, unexplained in another) at the product level; the breaks in the strict per-case reading come from the situation vocabulary in group 1, not from the families. The strains name the products the families cut differently depending on regime:

- an audit procedure with sampling and adjudication rules: ORG F09, LAW F29.
- a costed delivery plan: LAW F14, HOME F14, ORG F11, ECO F14.
- a negotiated community agreement: HOME F10, LAW F10, ORG F10, ECO F10, COMP F08, PHYS F10.
- a holding arrangement that releases on a condition: COMP F13, LAW F08.
- an interchange format with round-trip guarantees: COMP F24, PHYS F24, LAW F24, ORG F25.
- a written field procedure with roles and steps: ORG F09, HOME F29, LAW F09, COMP F29, BIO F29, PHYS F29, ECO F09.
- a governance process with named decision points: LAW F09, ORG F10, COMP F10.
- a monitoring programme with a sampling design: BIO F17, PHYS F17, LAW F17, ECO F17, ORG F17, HOME F22, COMP F17.
- an observatory that samples and reports a recurring gap: ORG F17, LAW F17, ECO F17, COMP F17, HOME F22.
- a low-cost sensing kit with its calibration procedure: PHYS F27, COMP F35, ECO F35.
- a settlement mechanism with compensating actions: COMP F13, ORG F14, LAW F14.
- a test rig that measures a stated property: COMP F35, PHYS F22, BIO F22.

The pattern is consistent: the same world product lands in the computational family in the computation regime (a settlement mechanism as transactions F13, a test rig or sensor kit as physical control F35), in the organizational family in the organization and law regimes (the same settlement as a ledger F14, a governance process as collective decisions F10), and in the physical-design family in the physical regime (a sensor kit as engineering F27). The families hold across regimes as classes; where they strain, they strain along the computational, organizational and physical seams of the catalogue, which is where Phase 1's cross-scale checks also found the recurring strains.

### What changed in the method during this version

- Output-role atoms were made family-qualified after the first full run showed material supply (F15) realizing explainers through the shared `Artifact` role and then lacking anchors.
- Grounding was made well-founded after inspection showed an ungrounded supplier (F03 with no data input) resolving three families' `Dataset` inputs and offsetting its own cost.
- Proof anchoring is required of realizing families only; suppliers are used generically and carry their family-level anchors.
- The solver-driven proposal pass was stopped after 1,423 cases (2.5 seconds a case under the candidate search) and replaced by direct judgment with case-count provenance; its hints were used for the first pass of atoms.

### Hardening items proposed by this version (not applied; the catalogue stays frozen)

- Scope or axis: decide whether human-performed activities, physical environment conditions, informal or voluntary authority, supervision level, crisis and degraded modes, and expressive purposes are out of scope (state it, with C11 and A11 as the boundary) or become axis values, an environment field, a family for designed experiences, and an authority-basis value on the authority field.
- Port graph: declare edges or adapters for repair plan to workflow (F32 to F09), workflow, measurement and repair into detection and response (F09, F17, F32 to F34), decision aid to document (F19 to F29), and a resource or material contract that any family's production can consume; let measurement families take streams.
- Operations: simulation and scheduling as operations available to the measurement, document and workflow families, or the supplier paths that bring them in.
- Proof records: routing (F12), qualifier rendering with figures (F29), simulator interfaces (F30), and primary records for the seven families that have none.
- The 37 thin-only ingredients and the 1,003 atoms are the bridge table to review; changing an atom re-runs in a minute.

### Limits of this version

The bridge is the operator's judgment, recorded per atom; a different judgment moves cases between classes but not out of the register. The generator's loose activity-to-product fit inflates class 5 by about a quarter. Product use is uneven, so per-product counts vary by two orders of magnitude. The volume ladder (25,000 with vocabulary expansion, new bridge atoms per thousand) has not started; the first run of it is the next step.

