# Review of the 37 ingredients that carried only thin atoms, after the external critique that thin-only
# counts do not establish framework gaps. Each entry names the construction the framework text offers.
# Tuple: (position, ingredient, target, strength, reason, verdict) where verdict is one of
#   'missed construction'   the framework text names this construction; my first rating was too low
#   'contrary assumption'   reconstructible only under an assumption the case itself contradicts
#   'boundary'              reconstructible around a human or physical boundary the framework declares (C11, A11, R28)
#   'no construction'       nothing in the catalogue covers it
REVISION = [
 # products
 ('out', 'PRD-DRILL-EXERCISE', 'F23:AssessmentResult', 'close', 'F23 constructs assessment paths and records which competencies have supporting evidence; a rehearsal with the real parties is an assessment with recorded evidence, and the corrected plan is F32', 'missed construction'),
 ('out', 'PRD-DRILL-EXERCISE', 'F21:ScenarioResult', 'thin', 'a rehearsal with people is not a simulation run', 'boundary'),
 ('out', 'PRD-EXHIBITION', 'F29:Artifact', 'thin', 'the media and layout are constructible (F29, F28); the encounter and its intended effect are not a product contract', 'no construction'),
 ('out', 'PRD-GAME-ACTIVITY', 'F30:ExecutableBundle', 'close', 'a structured game mediated by rules and an interface is F30 (interactions preserve domain state) over a rule model; an unmediated participatory activity remains outside', 'missed construction'),
 # input
 ('in', 'INP-LOCAL-KNOWLEDGE', 'SourceBundle', 'thin', 'the framework admits knowledge only once elicited and recorded (C11 attributable input, A11 accepted upstream interpretation; HG02 rejects missing source coverage); the case says it is undocumented', 'contrary assumption'),
 # activities
 ('req', 'ACT-REHEARSE-DRILL', 'O16', 'close', 'the drill qualifies readiness with recorded human evidence (F23 assessment, C11); the rehearsing itself is the boundary', 'missed construction'),
 ('req', 'ACT-CONSULT-PUBLIC', 'O17', 'close', 'R25 preserves attribution, conflicts and quorum of collective input; C11 records attributable human input; the asking is the boundary', 'missed construction'),
 ('req', 'ACT-FACILITATE-SESSION', 'O08', 'close', 'F10 collaborative review and decision records: the session advances a decision state under R25; facilitation is the boundary', 'missed construction'),
 ('req', 'ACT-INTERVIEW', 'O01', 'close', 'a structured instrument (F30 forms, F22 measurement) acquiring recorded runtime input (A11) comparably; the conversation is the boundary', 'missed construction'),
 ('req', 'ACT-NEGOTIATE', 'O07', 'close', 'negotiated terms are checked as versioned agreement terms (F08, P259) and allocation mechanisms carry stability and incentive claims (R26); the bargaining is the boundary', 'missed construction'),
 ('req', 'ACT-PERFORM', 'O15', 'thin', 'F29 executes prescribed media processing and takes open-ended creative choices as accepted content; a live performance is neither', 'no construction'),
 ('req', 'ACT-CARE-VISIT', 'O17', 'thin', 'the visit record and the case-state advance are constructible (F09, F07); the care itself is a human act the framework does not claim', 'boundary'),
 ('req', 'ACT-COLLECT-SAMPLE', 'O01', 'thin', 'the sample record enters with OBSERVATION basis and a custody identity; the physical taking is outside O01, which acquires bytes', 'boundary'),
 ('req', 'ACT-FABRICATE', 'O14', 'thin', 'manufacturing correspondence is constructed (P324 toolpath); the cutting is an actuator under R28, not an operation', 'boundary'),
 # acceptance
 ('acc', 'ACC-DRILL-PASSED', 'A11|adjudication', 'close', 'F23 acceptance: each claimed capability has applicable assessment evidence, recorded and judged', 'missed construction'),
 ('acc', 'ACC-HANDOVER-COMPLETE', 'A15|behavioral refinement', 'close', 'HG04: execute the actual consumer without substitutes; the receiving party continuing without the sender is that gate with a human consumer', 'missed construction'),
 ('acc', 'ACC-SPARE-AVAILABLE', 'R|R28', 'close', 'a commitment tested by ordering one is provider qualification: a real external system implements the receipt contract over its envelope', 'missed construction'),
 # situation: physical environment
 ('sit', 'CND-COLD-CLIMATE', 'V|V10', 'close', 'for equipment, climate is part of the qualified operating envelope (V10 bounded operating envelope, R28 provider and sensor qualification); effects on people are a boundary', 'missed construction'),
 ('sit', 'CND-HEAT-HUMIDITY', 'V|V10', 'close', 'as above: equipment envelope under V10 and R28; people are a boundary', 'missed construction'),
 ('sit', 'CND-DUST-VIBRATION', 'V|V10', 'close', 'as above: equipment envelope under V10 and R28', 'missed construction'),
 ('sit', 'CND-HAZARDOUS-SITE', 'V|V10', 'thin', 'the equipment envelope is constructible; a place that injures people is not', 'boundary'),
 ('sit', 'CND-STERILE-AREA', 'B|authority', 'thin', 'entry authority is F06; the contamination-control regime itself is not modelled', 'boundary'),
 # situation: authority and presence
 ('sit', 'CND-CUSTOMARY-AUTHORITY', 'B|authority', 'thin', 'the authority field needs a principal and a delegation; organization configuration fixes accepted authority models, so customary authority is admissible once recorded as one; the case says the record cannot express it', 'contrary assumption'),
 ('sit', 'CND-VOLUNTARY-STANDARD', 'B|meaning', 'close', 'modality is a meaning-field element and require, permit and forbid are distinct (P191); a voluntary standard is permit-modality obligations with no compelling authority', 'missed construction'),
 ('sit', 'CND-CONTESTED-SITE', 'B|authority', 'thin', 'access authority unresolved blocks the edge (HG02 missing authority); the contest itself is adjudicated outside', 'contrary assumption'),
 ('sit', 'CND-PUBLIC-SPACE', 'V|V13', 'thin', 'the information side is a release surface under V13; the physical presence of people who did not consent is not modelled', 'boundary'),
 # situation: supervision, capacity, knowledge held by people
 ('sit', 'CND-NIGHT-SHIFT', 'A11|recorded runtime input', 'close', 'A11 separates plain recorded runtime input from adjudication and sign-off; reduced supervision is input without sign-off', 'missed construction'),
 ('sit', 'CND-SUPERVISION-ABSENT', 'A11|recorded runtime input', 'close', 'as above: unsupervised work is recorded runtime input with no adjudication or sign-off step', 'missed construction'),
 ('sit', 'CND-HIGH-TURNOVER', 'A11|accepted upstream interpretation', 'thin', 'the framework answers turnover with its own premise: knowledge held in accepted models, not people; the case describes the state before that premise holds', 'contrary assumption'),
 ('sit', 'DYN-STAFF-CHANGE', 'A11|accepted upstream interpretation', 'thin', 'as above', 'contrary assumption'),
 ('sit', 'S-LOW-CAPACITY', 'A17|local', 'thin', 'tooling and runtime resources are the operating envelope; missing expertise is not modelled', 'boundary'),
 ('sit', 'S-SOLO', 'A17|local', 'thin', 'a single person deploying locally is expressible; the absence of an organisation is not a value', 'boundary'),
 # situation: operating states
 ('sit', 'S-CRISIS', 'C|C04', 'close', 'a guarded alternative branch under temporary emergency authority (C04 guarded choice, authority with expiry); the framework has explicit alternatives, not a suspended process', 'missed construction'),
 ('sit', 'DYN-DEGRADED-MODE', 'V|V10', 'close', 'F35 lists fallback and interlocks as a variation; V10 bounded envelope; C07 timeout path; RT-DEGRADE already maps to the declared safe state', 'missed construction'),
 ('sit', 'DYN-DEGRADED-MODE', 'C|C07', 'close', 'loss of a dependency takes the declared timeout path', 'missed construction'),
 ('sit', 'DYN-QUEUE-PRIORITY', 'R|R26', 'close', 'a contested order of service is an allocation mechanism with declared fairness, stability or incentive properties (R26)', 'missed construction'),
 # situation: expressive and everyday purposes
 ('sit', 'NED-COMMEMORATE', 'A02|construct', 'thin', 'the artifact is constructed from accepted creative content (F29); commemoration is not a transformation purpose', 'no construction'),
 ('sit', 'NED-EXPRESS-EXPERIENCE', 'A02|construct', 'thin', 'as above', 'no construction'),
 ('sit', 'NED-RUN-HOUSEHOLD', 'A02|coordinate', 'thin', 'guides and procedures are constructed; performing the task safely is the boundary', 'boundary'),
 # anchors for the two realizations added by this review (records exist; the omission was mine)
 ('proof', 'PRD-DRILL-EXERCISE', 'P333', 'close', 'competency graph and evidence to an admissible learning path', 'missed construction'),
 ('proof', 'PRD-DRILL-EXERCISE', 'P334', 'close', 'executed scoring to a governed assessment result', 'missed construction'),
 ('proof', 'PRD-DRILL-EXERCISE', 'P183', 'close', 'training records to attendance and completion checks', 'missed construction'),
 ('proof', 'PRD-EARLY-WARNING', 'P241', 'close', 'approved workflow with durable case execution state', 'missed construction'),
 ('proof', 'PRD-EARLY-WARNING', 'P29', 'close', 'process to executable process with execution trace', 'missed construction'),
 # structural residual: early-warning arrangements composed from procedures and people
 ('out', 'PRD-EARLY-WARNING', 'F09:ActionIntent', 'close', 'an arrangement with escalation rules and a named person at the end is a workflow with escalation (F09) when no signal stream exists; F34 remains the realization when one does', 'missed construction'),
]
