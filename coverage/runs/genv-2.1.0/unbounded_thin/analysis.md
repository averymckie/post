### unbounded_thin reading: 5000 cases

| verdict | cases |
|---|---|
| COVERED | 4336 |
| UNEXPLAINED | 419 |
| PARTIAL | 245 |

Verdicts by regime:

| regime | COVERED | PARTIAL | UNEXPLAINED | NO-WITNESS |
|---|---|---|---|---|
| R-BIO | 621 | 34 | 71 | 0 |
| R-COMP | 608 | 17 | 99 | 0 |
| R-ECO | 596 | 53 | 72 | 0 |
| R-HOME | 647 | 47 | 20 | 0 |
| R-LAW | 674 | 27 | 5 | 0 |
| R-ORG | 621 | 32 | 52 | 0 |
| R-PHYS | 569 | 35 | 100 | 0 |

Verdicts by scale band:

| scale band | COVERED | PARTIAL | UNEXPLAINED |
|---|---|---|---|
| device | 795 | 43 | 120 |
| regional | 583 | 35 | 56 |
| network | 498 | 28 | 58 |
| community | 459 | 23 | 17 |
| international | 411 | 19 | 50 |
| local | 287 | 28 | 24 |
| organization | 275 | 13 | 15 |
| individual | 272 | 13 | 16 |
| facility | 195 | 11 | 25 |
| national | 168 | 2 | 8 |
| enterprise | 113 | 6 | 10 |
| household | 86 | 9 | 5 |
| micro | 77 | 5 | 8 |
| team | 60 | 0 | 2 |
| landscape | 48 | 5 | 5 |
| group | 5 | 5 | 0 |
| service | 4 | 0 | 0 |

Gap classes:

| class | occurrences | distinct cases |
|---|---|---|
| strictness: family realized without any bridged input (name-only fit) | 456 | 418 |
| model gap candidate: input consumed by no family in the chain | 5 | 4 |
| operation not performed by any chain family (activity/product mismatch or gap) | 5 | 4 |
| no qualifying operation (O16) in the chain | 2 | 2 |
| model gap candidate: no counterpart (only thin bridge atoms) | 2 | 2 |

Gap register (top 40):

| kind | item | axis | cases | classification |
|---|---|---|---|---|
| grounding | F34: F34 | family | 223 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F37: F37 | family | 139 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F27: F27 | family | 21 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F09: F09 | family | 16 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F32: F32 | family | 13 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F35: F35 | family | 11 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F33: F33 | family | 6 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F17: F17 | family | 6 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F14: F14 | family | 5 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F22: F22 | family | 3 | strictness: family realized without any bridged input (name-only fit) |
| acceptance_qualifier | chain: chain | acceptance_qualifier | 2 | no qualifying operation (O16) in the chain |
| grounding | F03: F03 | family | 2 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F02: F02 | family | 2 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F19: F19 | family | 2 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F12: F12 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| input | INP-CONSUMABLE-STOCK: consumable material held in stock with a shelf life | input | 1 | model gap candidate: input consumed by no family in the chain |
| requirement | ACT-CALIBRATE: calibrate against a reference | activity | 1 | operation not performed by any chain family (activity/product mismatch or gap) |
| requirement | ACT-PROTOTYPE-TEST: build and test a prototype | activity | 1 | operation not performed by any chain family (activity/product mismatch or gap) |
| grounding | F01: F01 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| requirement | ACT-DECOMMISSION: take a thing out of service and close its record | activity | 1 | operation not performed by any chain family (activity/product mismatch or gap) |
| input | INP-LOCAL-KNOWLEDGE: undocumented local knowledge held by practitioners | input | 1 | model gap candidate: no counterpart (only thin bridge atoms) |
| input | INP-SATELLITE-IMAGE: a satellite or aerial image with acquisition metadata | input | 1 | model gap candidate: input consumed by no family in the chain |
| grounding | F29: F29 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| input | INP-WORK-QUEUE: a queue of pending items with arrival times | input | 1 | model gap candidate: input consumed by no family in the chain |
| requirement | ACT-BACKUP-RESTORE: take a backup and test that it restores | activity | 1 | operation not performed by any chain family (activity/product mismatch or gap) |
| grounding | F31: F31 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F16: F16 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| requirement | ACT-INTERVIEW: conduct structured interviews | activity | 1 | model gap candidate: no counterpart (only thin bridge atoms) |
| requirement | ACT-MEASURE-INSTRUMENT: take instrument measurements on a schedule | activity | 1 | operation not performed by any chain family (activity/product mismatch or gap) |
| grounding | F21: F21 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| grounding | F30: F30 | family | 1 | strictness: family realized without any bridged input (name-only fit) |
| input | INP-FOOD-ONTOLOGY: a food and ingredient vocabulary | input | 1 | model gap candidate: input consumed by no family in the chain |
| input | INP-OCCUPATION-TAXONOMY: an occupation and skills taxonomy | input | 1 | model gap candidate: input consumed by no family in the chain |

Proof gaps by realizing family (product: cases):

- F29 (179): PRD-QUALITY-LABEL 124, PRD-EXHIBITION 27, PRD-BENCH-PROTOCOL 26, PRD-AUDIT-PROCEDURE 2
- F30 (44): PRD-SIMULATOR 28, PRD-EXHIBITION 11, PRD-GAME-ACTIVITY 5
- F31 (39): PRD-DRILL-EXERCISE 39
- F08 (20): PRD-ACCESS-PATHWAY 20

Never reached: families ['F18', 'F26', 'F36', 'F38']; operations ['O06']; compositions ['C06', 'C13']; variation rules ['V05', 'V09', 'V14', 'V15']; axis values 61 of 128; proofs never anchored 254.

Regime and scale invariance (same semantic combination in several strata):

- semantic_key_by_regime: 120 groups, {'STRAINS': 95, 'BREAKS': 14, 'HOLDS': 11}
- semantic_key_by_scale_band: 196 groups, {'STRAINS': 160, 'BREAKS': 17, 'HOLDS': 19}
- coarse_key_by_regime: 693 groups, {'STRAINS': 522, 'BREAKS': 171}
- coarse_key_by_scale_band: 862 groups, {'STRAINS': 674, 'BREAKS': 188}

Missing port edges (a product realized by one family feeds a product realized by another, but no output role of the first is an input role of the second):

| from family | to family | relationship | cases | example |
|---|---|---|---|---|
| F09 | F34 | RK-EMBED | 10 | UC-00288: PRD-FIELD-PROCEDURE -> PRD-EARLY-WARNING |
| F17 | F34 | RK-EMBED | 9 | UC-00094: PRD-LINEAGE-MAP -> PRD-EARLY-WARNING |
| F09 | F34 | RK-INPUT | 9 | UC-00288: PRD-FIELD-PROCEDURE -> PRD-EARLY-WARNING |
| F32 | F34 | RK-EMBED | 9 | UC-00077: PRD-RECOVERY-PLAN -> PRD-EARLY-WARNING |
| F32 | F34 | RK-INPUT | 8 | UC-00077: PRD-RECOVERY-PLAN -> PRD-EARLY-WARNING |
| F21 | F34 | RK-INPUT | 6 | UC-00202: PRD-DRILL-EXERCISE -> PRD-EARLY-WARNING |
| F32 | F09 | RK-INPUT | 6 | UC-01791: PRD-RECOVERY-PLAN -> PRD-HANDOVER-PROTOCOL |
| F29 | F34 | RK-EMBED | 5 | UC-00414: PRD-POCKET-CARD -> PRD-EARLY-WARNING |
| F17 | F34 | RK-INPUT | 5 | UC-00094: PRD-LINEAGE-MAP -> PRD-EARLY-WARNING |
| F17 | F37 | RK-EMBED | 4 | UC-00146: PRD-QUALITY-LABEL -> PRD-CONFIGURATOR |
| F29 | F34 | RK-INPUT | 4 | UC-00414: PRD-POCKET-CARD -> PRD-EARLY-WARNING |
| F29 | F37 | RK-EMBED | 4 | UC-00963: PRD-QUALITY-LABEL -> PRD-CONFIGURATOR |
| F09 | F14 | RK-INPUT | 4 | UC-01234: PRD-HANDOVER-PROTOCOL -> PRD-BUDGET-PLAN |
| F23 | F34 | RK-EMBED | 3 | UC-00010: PRD-TRAINING-COURSE -> PRD-EARLY-WARNING |
| F22 | F34 | RK-EMBED | 3 | UC-00710: PRD-OBSERVATORY -> PRD-EARLY-WARNING |
| F22 | F34 | RK-INPUT | 3 | UC-00710: PRD-OBSERVATORY -> PRD-EARLY-WARNING |
| F21 | F34 | RK-EMBED | 3 | UC-00202: PRD-DRILL-EXERCISE -> PRD-EARLY-WARNING |
| F16 | F34 | RK-INPUT | 3 | UC-03499: PRD-MAINTENANCE-SCHEDULE -> PRD-EARLY-WARNING |
| F24 | F37 | RK-EMBED | 3 | UC-00457: PRD-CONFORMANCE-PACK -> PRD-CONFIGURATOR |
| F31 | F37 | RK-INPUT | 2 | UC-00052: PRD-CONFORMANCE-PACK -> PRD-CONFIGURATOR |

Products realized by a family with no bridged input and no inbound part (composed without inputs):

- F34: PRD-EARLY-WARNING (128 cases)
- F37: PRD-CONFIGURATOR (88 cases)
- F32: PRD-RECOVERY-PLAN (8 cases)
- F27: PRD-PACKAGING (5 cases)
- F27: PRD-SENSOR-KIT (5 cases)
- F35: PRD-SENSOR-KIT (5 cases)
- F09: PRD-HANDOVER-PROTOCOL (4 cases)
- F33: PRD-RECOVERY-PLAN (3 cases)
- F17: PRD-OBSERVATORY (1 cases)
- F35: PRD-SENSOR-KIT, PRD-TEST-RIG (1 cases)
- F29: PRD-WORKED-EXAMPLE (1 cases)
- F37: PRD-CONFIGURATOR, PRD-STATEMENT-GENERATOR (1 cases)

Inputs no chain family consumes (top 12):

- INP-CONSUMABLE-STOCK (1 cases): bridged to ['MaterialModel', 'ResourceModel'], consumed only by ['F11', 'F12', 'F15', 'F19', 'F22', 'F27']; chains seen e.g. ['F34']
- INP-LOCAL-KNOWLEDGE (1 cases): bridged to ['SourceBundle'], consumed only by ['F01', 'F04', 'F29']; chains seen e.g. ['F35']
- INP-SATELLITE-IMAGE (1 cases): bridged to ['Dataset', 'SpatialDataset'], consumed only by ['F02', 'F03', 'F04', 'F05', 'F06', 'F08', 'F09', 'F10', 'F12', 'F14', 'F16', 'F17', 'F18', 'F19', 'F21', 'F23', 'F28', 'F29', 'F36']; chains seen e.g. ['F34', 'F35']
- INP-WORK-QUEUE (1 cases): bridged to ['Dataset', 'TaskModel', 'WorkflowModel'], consumed only by ['F02', 'F03', 'F04', 'F05', 'F06', 'F08', 'F09', 'F10', 'F11', 'F14', 'F16', 'F17', 'F18', 'F19', 'F21', 'F23', 'F28', 'F29', 'F36']; chains seen e.g. ['F27']
- INP-FOOD-ONTOLOGY (1 cases): bridged to ['MappingModel', 'SourceBundle'], consumed only by ['F01', 'F03', 'F04', 'F25', 'F29']; chains seen e.g. ['F35']
- INP-OCCUPATION-TAXONOMY (1 cases): bridged to ['CompetencyModel', 'MappingModel', 'SourceBundle'], consumed only by ['F01', 'F03', 'F04', 'F23', 'F25', 'F29']; chains seen e.g. ['F35']

Operations required by an activity but performed by no chain family (top 12):

- ACT-CALIBRATE (1 cases): needs ['O09', 'O16']; the part's product was realized by ['F34']
- ACT-PROTOTYPE-TEST (1 cases): needs ['O14', 'O16']; the part's product was realized by ['F34']
- ACT-DECOMMISSION (1 cases): needs ['O08', 'O18']; the part's product was realized by ['F17']
- ACT-BACKUP-RESTORE (1 cases): needs ['O17', 'O18']; the part's product was realized by ['F27']
- ACT-INTERVIEW (1 cases): needs ['O01']; the part's product was realized by ['F09']
- ACT-MEASURE-INSTRUMENT (1 cases): needs ['O01', 'O08']; the part's product was realized by ['F22']

Product-level invariance (same product realized by the same family across strata):

- semantic_key_by_regime: 120 groups, {'STRAINS': 62, 'HOLDS': 58}
- semantic_key_by_scale_band: 196 groups, {'STRAINS': 106, 'HOLDS': 90}
- coarse_key_by_regime: 693 groups, {'STRAINS': 345, 'HOLDS': 348}
- coarse_key_by_scale_band: 862 groups, {'STRAINS': 416, 'HOLDS': 446}

Product-by-stratum realization (products seen at least five times in at least two strata; dominant realizing family per stratum):

- by regime: 59 products compared, {'HOLDS': 46, 'STRAINS': 13}
  - STRAINS PRD-BENCH-PROTOCOL: {"R-ECO": "F29", "R-PHYS": "F29", "R-BIO": "F22"}
  - STRAINS PRD-BUDGET-PLAN: {"R-LAW": "F11", "R-HOME": "F14", "R-ORG": "F14", "R-ECO": "F14"}
  - STRAINS PRD-CALIBRATION-SERVICE: {"R-BIO": "F17", "R-COMP": "F17", "R-PHYS": "F17", "R-ECO": "F31"}
  - STRAINS PRD-COMMUNITY-AGREEMENT: {"R-HOME": "F10", "R-LAW": "F10", "R-ORG": "F10", "R-ECO": "F10", "R-COMP": "F08", "R-PHYS": "F10"}
  - STRAINS PRD-EXCHANGE-FORMAT: {"R-COMP": "F24", "R-PHYS": "F24", "R-LAW": "F24", "R-ORG": "F25"}
  - STRAINS PRD-FIELD-PROCEDURE: {"R-ORG": "F29", "R-HOME": "F29", "R-LAW": "F09", "R-COMP": "F09", "R-BIO": "F29", "R-PHYS": "F29", "R-ECO": "F09"}
  - STRAINS PRD-GOVERNANCE-PROCESS: {"R-LAW": "F09", "R-ORG": "F10", "R-COMP": "F10"}
  - STRAINS PRD-QUALITY-LABEL: {"R-ORG": "F17", "R-LAW": "F17", "R-ECO": "F17", "R-COMP": "F17", "R-HOME": "F29", "R-PHYS": "F17", "R-BIO": "F17"}
  - STRAINS PRD-REGISTER: {"R-ORG": "F02", "R-LAW": "F02", "R-COMP": "F02", "R-ECO": "F33"}
  - STRAINS PRD-SENSOR-KIT: {"R-PHYS": "F27", "R-COMP": "F35", "R-ECO": "F35"}
  - STRAINS PRD-SETTLEMENT-MECHANISM: {"R-COMP": "F13", "R-ORG": "F14", "R-LAW": "F14"}
  - STRAINS PRD-TEST-RIG: {"R-COMP": "F35", "R-PHYS": "F22", "R-BIO": "F22"}
  - STRAINS PRD-VALIDATOR: {"R-LAW": "F31", "R-ORG": "F31", "R-COMP": "F24"}
- by scale_band: 56 products compared, {'HOLDS': 35, 'STRAINS': 21}
  - STRAINS PRD-ANNOTATION-GUIDE: {"device": "F29", "regional": "F01", "community": "F01", "individual": "F01", "international": "F29", "network": "F01", "organization": "F01"}
  - STRAINS PRD-AUDIT-PROCEDURE: {"regional": "F29", "network": "F09", "organization": "F09", "community": "F22", "national": "F09"}
  - STRAINS PRD-BENCH-PROTOCOL: {"regional": "F29", "international": "F22", "device": "F29", "individual": "F29", "micro": "F29", "network": "F22"}
  - STRAINS PRD-BUDGET-PLAN: {"network": "F14", "national": "F14", "community": "F11", "regional": "F14", "facility": "F14", "international": "F14", "local": "F14", "organization": "F14", "enterprise": "F11", "individual": "F11", "team": "F14", "household": "F14", "device": "F11"}
  - STRAINS PRD-CATALOGUE: {"community": "F02", "regional": "F02", "facility": "F02", "organization": "F02", "national": "F02", "international": "F02", "network": "F02", "device": "F02", "local": "F02", "team": "F04", "individual": "F02"}
  - STRAINS PRD-CLINIC-SERVICE: {"device": "F11", "community": "F11", "organization": "F09", "individual": "F11", "network": "F11", "micro": "F11", "landscape": "F11", "regional": "F11", "local": "F11", "team": "F11", "international": "F11", "household": "F09"}
  - STRAINS PRD-CONFORMANCE-PACK: {"regional": "F24", "device": "F31", "network": "F31", "national": "F24", "international": "F24", "micro": "F24", "facility": "F31", "local": "F31"}
  - STRAINS PRD-EXCHANGE-FORMAT: {"regional": "F24", "international": "F25", "national": "F24", "micro": "F25", "network": "F24", "enterprise": "F24", "device": "F24", "local": "F25"}
  - STRAINS PRD-FIELD-PROCEDURE: {"network": "F29", "community": "F29", "international": "F29", "team": "F29", "individual": "F29", "regional": "F09", "household": "F09", "national": "F29", "device": "F09", "landscape": "F09", "organization": "F29", "local": "F29", "enterprise": "F09", "facility": "F09", "micro": "F29"}
  - STRAINS PRD-GOVERNANCE-PROCESS: {"community": "F09", "regional": "F09", "organization": "F10", "network": "F09", "international": "F09", "national": "F09"}
  - STRAINS PRD-HABITAT-PLAN: {"landscape": "F28", "regional": "F11", "individual": "F11", "device": "F11"}
  - STRAINS PRD-KIT-OF-PARTS: {"organization": "F15", "device": "F27"}
  - STRAINS PRD-MONITORING-PROGRAMME: {"household": "F22", "device": "F17", "network": "F17", "local": "F17", "individual": "F17", "national": "F17", "enterprise": "F17", "community": "F17", "micro": "F17", "facility": "F17", "regional": "F17", "international": "F17", "landscape": "F17", "organization": "F17"}
  - STRAINS PRD-QUALITY-LABEL: {"regional": "F29", "network": "F17", "national": "F17", "community": "F17", "international": "F17", "device": "F17", "micro": "F17", "local": "F29", "organization": "F17", "facility": "F17", "individual": "F17", "landscape": "F17", "enterprise": "F17", "household": "F29"}
  - STRAINS PRD-REGISTER: {"regional": "F02", "network": "F02", "enterprise": "F02", "local": "F33", "community": "F02", "national": "F02", "international": "F02", "organization": "F02", "facility": "F02", "device": "F33"}
  - STRAINS PRD-SENSOR-KIT: {"international": "F27", "device": "F35", "regional": "F35"}
  - STRAINS PRD-SETTLEMENT-MECHANISM: {"device": "F13", "international": "F14", "network": "F14"}
  - STRAINS PRD-SIMULATOR: {"enterprise": "F21", "international": "F21", "device": "F21", "network": "F21", "regional": "F21", "facility": "F21", "national": "F21", "local": "F30", "community": "F21", "organization": "F21", "individual": "F21", "micro": "F21"}
  - STRAINS PRD-SPARE-PARTS-PLAN: {"device": "F15", "facility": "F16", "enterprise": "F15", "local": "F15"}
  - STRAINS PRD-TEST-RIG: {"international": "F27", "device": "F22", "micro": "F22"}
  - STRAINS PRD-VALIDATOR: {"local": "F31", "network": "F31", "organization": "F31", "international": "F24", "regional": "F31", "device": "F24", "community": "F31", "national": "F31"}
