## Correction after review: genv-2.1.0

An external review of the results section above made two objections. First, the evaluator limited supporting chains to one level and at most four suppliers, while the framework's grammar composes recursively. Second, 37 disputed vocabulary mappings decided 4,137 of the 5,000 strict verdicts, so the headline table reported places where this evaluator failed to reconstruct a case as if they were framework gaps. Both objections are correct. The verdict table in the results section is superseded by the tables here; the rest of that section stands where this one does not withdraw it.

### Check 1: the supplier bound

Both readings were re-run with recursive, uncapped suppliers under the same well-founded grounding rule (a family may resolve another family's input only if it is itself grounded back to case inputs). Each run takes about 70 seconds, no timeouts; chains carry 2.8 suppliers on average instead of 1.0.

| run | COVERED | PARTIAL | UNEXPLAINED |
|---|---|---|---|
| bridge-1, one supplier level, strict | 531 | 36 | 4433 |
| bridge-1, one supplier level, lenient | 2989 | 209 | 1802 |
| bridge-1, recursive suppliers, strict | 733 | 44 | 4223 |
| bridge-1, recursive suppliers, lenient | 4336 | 245 | 419 |
| bridge-2, recursive suppliers, strict | 1638 | 72 | 3290 |
| bridge-2, recursive suppliers, lenient | 4556 | 242 | 202 |

With the bound removed, 210 strict and 1,383 lenient cases that were reported as unexplained reconstruct. The classes reported above as "missing port edges", "inputs no family in the chain consumes" and "operations no chain family performs" were mostly this evaluator's bound: under recursive composition they shrink to a few cases each and are withdrawn as findings, except for the residuals listed below.

### Check 2: the 37 disputed mappings

Each of the 37 ingredients that carried only thin atoms was re-examined against the framework text for the construction it offers and the assumption that construction needs. Verdicts: "missed construction" (the text names a construction and the first rating was too low), "contrary assumption" (reconstructible only under an assumption the case itself contradicts), "boundary" (reconstructible around a human or physical boundary the framework declares through C11, A11 and R28), "no construction". The review is recorded as a revision block on the bridge (`bridge/src_revision.py`); original ratings are kept beside the revised ones.

| ingredient | position | construction offered | verdict |
|---|---|---|---|
| a rehearsal is completed within the stated time by the real parties | acc | A11|adjudication: F23 acceptance: each claimed capability has applicable assessment evidence, recorded and judged | missed construction |
| the receiving party can continue without contacting the sender | acc | A15|behavioral refinement: HG04: execute the actual consumer without substitutes; the receiving party continuing without the sender is that gate with a human consumer | missed construction |
| a replacement part is obtainable for a stated period | acc | R|R28: a commitment tested by ordering one is provider qualification: a real external system implements the receipt contract over its envelope | missed construction |
| consult affected people and record the input | req | O17: R25 preserves attribution, conflicts and quorum of collective input; C11 records attributable human input; the asking is the boundary | missed construction |
| facilitate a structured session | req | O08: F10 collaborative review and decision records: the session advances a decision state under R25; facilitation is the boundary | missed construction |
| conduct structured interviews | req | O01: a structured instrument (F30 forms, F22 measurement) acquiring recorded runtime input (A11) comparably; the conversation is the boundary | missed construction |
| negotiate terms between parties | req | O07: negotiated terms are checked as versioned agreement terms (F08, P259) and allocation mechanisms carry stability and incentive claims (R26); the bargaining is the boundary | missed construction |
| rehearse a scenario with the real parties | req | O16: the drill qualifies readiness with recorded human evidence (F23 assessment, C11); the rehearsing itself is the boundary | missed construction |
| extreme cold affecting equipment and people | sit | V|V10: for equipment, climate is part of the qualified operating envelope (V10 bounded operating envelope, R28 provider and sensor qualification); effects on people are a boundary | missed construction |
| dust, vibration and mechanical noise | sit | V|V10: as above: equipment envelope under V10 and R28 | missed construction |
| heat and humidity affecting material and people | sit | V|V10: as above: equipment envelope under V10 and R28; people are a boundary | missed construction |
| work at night with reduced supervision | sit | A11|recorded runtime input: A11 separates plain recorded runtime input from adjudication and sign-off; reduced supervision is input without sign-off | missed construction |
| the person performing the work is unsupervised | sit | A11|recorded runtime input: as above: unsupervised work is recorded runtime input with no adjudication or sign-off step | missed construction |
| a voluntary standard with no enforcement | sit | B|meaning: modality is a meaning-field element and require, permit and forbid are distinct (P191); a voluntary standard is permit-modality obligations with no compelling authority | missed construction |
| operating in a degraded but safe mode | sit | V|V10: F35 lists fallback and interlocks as a variation; V10 bounded envelope; C07 timeout path; RT-DEGRADE already maps to the declared safe state | missed construction |
| a queue whose order is itself contested | sit | R|R26: a contested order of service is an allocation mechanism with declared fairness, stability or incentive properties (R26) | missed construction |
| a rehearsed exercise run with the real parties | out | F23:AssessmentResult: F23 constructs assessment paths and records which competencies have supporting evidence; a rehearsal with the real parties is an assessment with recorded evidence, and the corrected plan is F32 | missed construction |
| an early-warning arrangement with escalation rules | out | F09:ActionIntent: an arrangement with escalation rules and a named person at the end is a workflow with escalation (F09) when no signal stream exists; F34 remains the realization when one does | missed construction |
| a structured game or participatory activity | out | F30:ExecutableBundle: a structured game mediated by rules and an interface is F30 (interactions preserve domain state) over a rule model; an unmediated participatory activity remains outside | missed construction |
| an emergency in which the normal process cannot be followed | sit | C|C04: a guarded alternative branch under temporary emergency authority (C04 guarded choice, authority with expiry); the framework has explicit alternatives, not a suspended process | missed construction |
| carry out a care or service visit and record it | req | O17: the visit record and the case-state advance are constructible (F09, F07); the care itself is a human act the framework does not claim | boundary |
| collect and label a physical sample | req | O01: the sample record enters with OBSERVATION basis and a custody identity; the physical taking is outside O01, which acquires bytes | boundary |
| fabricate a physical part | req | O14: manufacturing correspondence is constructed (P324 toolpath); the cutting is an actuator under R28, not an operation | boundary |
| perform or present to an audience | req | O15: F29 executes prescribed media processing and takes open-ended creative choices as accepted content; a live performance is neither | no construction |
| a site with contested claims or access | sit | B|authority: access authority unresolved blocks the edge (HG02 missing authority); the contest itself is adjudicated outside | contrary assumption |
| customary authority not recorded in statute | sit | B|authority: the authority field needs a principal and a delegation; organization configuration fixes accepted authority models, so customary authority is admissible once recorded as one; the case says the record cannot express it | contrary assumption |
| a hazardous physical environment | sit | V|V10: the equipment envelope is constructible; a place that injures people is not | boundary |
| high staff turnover | sit | A11|accepted upstream interpretation: the framework answers turnover with its own premise: knowledge held in accepted models, not people; the case describes the state before that premise holds | contrary assumption |
| an uncontrolled public space | sit | V|V13: the information side is a release surface under V13; the physical presence of people who did not consent is not modelled | boundary |
| a controlled clean or sterile area | sit | B|authority: entry authority is F06; the contamination-control regime itself is not modelled | boundary |
| the people who hold the knowledge leave | sit | A11|accepted upstream interpretation: as above | contrary assumption |
| undocumented local knowledge held by practitioners | in | SourceBundle: the framework admits knowledge only once elicited and recorded (C11 attributable input, A11 accepted upstream interpretation; HG02 rejects missing source coverage); the case says it is undocumented | contrary assumption |
| mark an occasion or a loss in a way that holds | sit | A02|construct: the artifact is constructed from accepted creative content (F29); commemoration is not a transformation purpose | no construction |
| give an experience a form other people can encounter | sit | A02|construct: as above | no construction |
| carry out a household task safely without professional support | sit | A02|coordinate: guides and procedures are constructed; performing the task safely is the boundary | boundary |
| an exhibition or public installation | out | F29:Artifact: the media and layout are constructible (F29, F28); the encounter and its intended effect are not a product contract | no construction |
| the party who must act lacks tooling, staff or expertise | sit | A17|local: tooling and runtime resources are the operating envelope; missing expertise is not modelled | boundary |
| one person or household acts alone, without an organisation | sit | A17|local: a single person deploying locally is expressible; the absence of an organisation is not a value | boundary |

Verdict counts over the reviewed atoms: missed construction 21, boundary 10, contrary assumption 5, no construction 4. The revised bridge has 1020 atoms; 18 ingredients still carry only thin atoms.

### Corrected reading

Reference from here on: revised bridge, recursive suppliers.

| verdict | strict (exact and close) | lenient (thin included) |
|---|---|---|
| COVERED | 1638 | 4556 |
| PARTIAL | 72 | 242 |
| UNEXPLAINED | 3290 | 202 |

What the two numbers mean. 1638 cases reconstruct with mappings that follow the family cards' own contracts. 4556 reconstruct when the 18 remaining thin items are read as the boundaries the framework itself declares (a person's act enters as attributable input through C11, knowledge and authority are admitted once recorded, equipment lives inside a qualified envelope under R28) or as assumptions the case contradicts. Neither number is a count of framework gaps.

Strict UNEXPLAINED decomposes into: vocabulary only 2921, both 263, structural only 106. The vocabulary items and the cases they decide:

- undocumented local knowledge held by practitioners: 939 cases, contrary assumption.
- customary authority not recorded in statute: 583 cases, contrary assumption.
- a site with contested claims or access: 540 cases, contrary assumption.
- an uncontrolled public space: 508 cases, boundary.
- a controlled clean or sterile area: 408 cases, boundary.
- perform or present to an audience: 330 cases, no construction.
- high staff turnover: 297 cases, contrary assumption.
- the party who must act lacks tooling, staff or expertise: 294 cases, boundary.
- one person or household acts alone, without an organisation: 246 cases, boundary.
- carry out a care or service visit and record it: 217 cases, boundary.
- a hazardous physical environment: 181 cases, boundary.
- the people who hold the knowledge leave: 140 cases, contrary assumption.
- an exhibition or public installation: 140 cases, no construction.
- collect and label a physical sample: 80 cases, boundary.
- mark an occasion or a loss in a way that holds: 41 cases, no construction.
- give an experience a form other people can encounter: 39 cases, no construction.
- fabricate a physical part: 33 cases, boundary.
- carry out a household task safely without professional support: 18 cases, boundary.

Lenient UNEXPLAINED decomposes into: structural only 201, both 1. The structural residual is almost entirely one product: configurators. a configurator that emits a tailored product via F37 (88 cases); a documented recovery plan with rehearsed steps via F32 (8 cases); a low-cost sensing kit with its calibration procedure via F35 (7 cases); protective packaging designed for one route via F27 (5 cases)

The 139 configurator cases never supply what F37 takes (a family specification, a capability catalogue, a proof-requirement catalogue, a target profile). Either the world's configurators are lighter objects than F37 (parameterized templates, which F29 constructs) or F37's inputs are the framework's own artifacts and never occur in the wild. That is a genuine observation about the framework's reach, and the one structural finding of this version that survives both checks.

### What survives as findings

- Boundary and contrary-assumption items (18): carry out a care or service visit and record it; collect and label a physical sample; fabricate a physical part; perform or present to an audience; a site with contested claims or access; customary authority not recorded in statute; a hazardous physical environment; high staff turnover; an uncontrolled public space; a controlled clean or sterile area; the people who hold the knowledge leave; undocumented local knowledge held by practitioners; mark an occasion or a loss in a way that holds; give an experience a form other people can encounter; carry out a household task safely without professional support; an exhibition or public installation; the party who must act lacks tooling, staff or expertise; one person or household acts alone, without an organisation. These decide the strict verdicts of 3184 cases. They are the framework's declared boundaries or its recording premise, stated as gap candidates only if the user wants them inside the model.
- Configurators as above (88 cases).
- Proof layer (strict): F29 186; F30 36; F12 4. Routing under F12 reproduces the Phase 1 finding; the F09 and F23 entries in the first run of this check were anchors I had omitted and are now bridged.
- Never reached: families F18, F20, F26, F36, F38; operation O06; compositions C06, C13; variation rules V05, V07, V09, V11, V14, V15. Generator sparse areas, reported here and not fed to the generator.
- Cross-regime at product level: HOLDS 48, STRAINS 11 of 59 products by regime; HOLDS 39, STRAINS 17 of 56 by scale band; no product breaks. Strains: a negotiated community agreement (HOME F10, LAW F10, ORG F10, ECO F10, COMP F08, PHYS F10); a holding arrangement that releases on a condition (COMP F13, LAW F08); an interchange format with round-trip guarantees (COMP F24, PHYS F24, LAW F24, ORG F25); a written field procedure with roles and steps (ORG F09, HOME F09, LAW F09, COMP F09, BIO F29, PHYS F29, ECO F09); a governance process with named decision points (LAW F09, ORG F09, COMP F10); an observatory that samples and reports a recurring gap (ORG F17, LAW F17, ECO F17, COMP F17, HOME F22); a quality and limitation label carried with every figure (ORG F17, LAW F17, ECO F17, COMP F17, HOME F29, PHYS F17, BIO F17); a low-cost sensing kit with its calibration procedure (PHYS F27, COMP F35, ECO F35); a settlement mechanism with compensating actions (COMP F13, ORG F14, LAW F14); a test rig that measures a stated property (COMP F35, PHYS F22, BIO F22); a validator that reports per-record verdicts with reasons (LAW F31, ORG F31, COMP F24).
- Port edges surviving at material count (strict): F32 to F09 over RK-INPUT (20); F32 to F09 over RK-EMBED (13); F09 to F14 over RK-INPUT (8). Everything else in that table is withdrawn.
- Phase 1's seventeen no-anchor entries are unchanged.

### Corrected hardening list

- A scope statement in the master for the boundary class (human acts, physical environments as they affect people, presence without consent, authority and knowledge that are not recorded), or axis values if the user wants them inside the model.
- F37's input roles against world configurators: either a lighter configurator profile or an explicit statement that F37 configures families, not products.
- Proof records: routing (F12), qualifier rendering with figures (F29), simulator interfaces (F30), primary records for the seven families that have none.
- The one port edge with a material count: repair plan into workflow (F32 to F09).
- The evaluator itself: recursive suppliers are now the default reading; the bounded runs are kept for the record.

