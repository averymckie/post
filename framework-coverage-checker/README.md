# Framework coverage checker 0.1.0

This release runs a mechanical reconstruction checker and preserves the evidence needed to distinguish a failed candidate, incomplete search, missing case detail and an unqualified proof application. It includes the full audit of the latest 5,000 cases, the frozen original framework, an updated framework, source code, tests and replayable solver results.

**The corpus result is undetermined coverage.** All 5,000 supplied records are summaries without accepted formal contracts and case-bound implementation evidence. They are not 5,000 proved framework failures. No original case is awarded a full coverage certificate by this release.

## Start

Use Python 3.12. The recorded run used Python 3.12.14 on Linux x86-64. From this directory:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m fwcheck --help
.venv/bin/python -m fwcheck show results/corpus-baseline/cases.sqlite3 UC-00049
.venv/bin/python -m fwcheck find results/corpus-baseline/cases.sqlite3 'consent'
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`. Platform wheel availability must be checked on an untested operating system. No runtime language model, API key or network service is used after dependency installation.

Read `RUN_REPORT.md` first for the findings. `results/corpus-baseline/case-results.jsonl` has one complete dossier per case. `cases.sqlite3` contains those dossiers and a searchable index. `data/cases_simple.txt` preserves the source export byte for byte.

## Run the checker

```bash
# A conditional three-stage reconstruction. Full implementation evidence remains open.
.venv/bin/python -m fwcheck check examples/planning.json --framework data/framework-baseline.txt --out new-plan-run.json
.venv/bin/python -m fwcheck replay examples/planning.json new-plan-run.json --framework data/framework-baseline.txt

# Joint capacity counterexample and incompatible evidence basis.
.venv/bin/python -m fwcheck check examples/overbooked.json --framework data/framework-baseline.txt --out new-capacity-run.json
.venv/bin/python -m fwcheck check examples/wrong-basis.json --framework data/framework-baseline.txt --out new-basis-run.json

# Explicit finite state graph and finite interaction rule table.
.venv/bin/python -m fwcheck states examples/revocation-states.json --out new-state-run.json
.venv/bin/python -m fwcheck obligations examples/interaction-rules.json --out new-obligation-run.json

# Repeat the complete corpus intake. Use a new directory to preserve the old run.
.venv/bin/python -m fwcheck audit data/cases_simple.txt --framework data/framework-baseline.txt --reviews data/need-reviews.json --review-ledger data/review-ledger.json --out results/new-corpus-run

# Standard test runner, including the untouched Ghostwriter-generated test body.
.venv/bin/python -m pytest --hypothesis-show-statistics
```

The example files are separately authored demonstrations. They are not substituted into the 5,000 cases and are not representations of missing original case details. New models must bind the appropriate framework hash. Baseline certificates remain tied to the original framework even after its amendment.

## What executes

| Capability | Implementation and decision |
| --- | --- |
| Whole-input intake | Strict 14-field summary parser; duplicate JSON keys and nonfinite numbers rejected in formal input; Draft 2020-12 JSON Schema validates model structure |
| Full framework retrieval | All 38 families and all 349 complete proof records, with source spans and hashes; short family anchor lists do not limit retrieval |
| Backward construction search | clingo selects output producers, recursively resolves every required input and rejects cycles; finite instance catalogue and explicit bounds |
| Independent graph check | Z3 and cvc5 establish a rank assignment for the selected DAG; dangling or extraneous bindings are rejected |
| Contract refinement | Separate AST encoders for Z3 and cvc5; satisfiable antecedent first, then search for an admitted counterexample |
| Root and global acceptance | Every declared requirement checked; output-specific acceptance uses the chosen output contract; global conditions use the composed contracts |
| Boundary contracts | Exact agreement on all 14 framework connection fields; no inferred conversion, unit change, authority promotion or evidence promotion |
| State safety | clingo reachability and independent SMT path queries over a supplied graph of at most 50 states; complete reachability bound of number of states minus one |
| Interaction obligations | clingo derives rules, including conjunctions of features; independent SMT checks every possible obligation in the supplied rule table |
| Replay | Case, framework, checker source and dependency identities; new solver execution checks recorded decisions and query identities; tampering rejected |
| Case handling | Source clause IDs and repeated occurrences retained; structural findings, prior review aids and open obligations per case |

## Formal model input

`docs/case.schema.json` is the actual schema. `examples/planning.json` is a complete syntactic example. A model contains:

1. The source and frozen framework identities, explicit source clauses and a review-bound requirement inventory.
2. A shared, accepted namespace of Bool, Int and Real variables; symbolic domains are allowed. Numbers are exact integers or `{"rat":"3/7"}`. Floats, division, nonlinear products, quantifiers and arbitrary code are unsupported.
3. Explicit supplied-source guarantees and a finite catalogue of bound component instances. Each component identifies its family, relevant proof records, mandatory input ports, output guarantees and profile origin. Proof references are retrieval pointers, not execution evidence.
4. Root product requirements and global predicates. Every source clause must be represented by a requirement ID. This syntactic reconciliation cannot determine whether a natural-language clause was faithfully formalized. Semantic acceptance remains upstream and attributable.
5. The admitted grammar and finite search limits. The construction kernel supports static acyclic Seq, Join and ForkJoin only. Stateful forms must not be flattened into this model. The separate explicit-state command checks its own graph; it does not automatically discharge the construction's temporal obligations.

Component contracts are **assumptions of the conditional model proof**. The checker has no mechanism that turns an asserted output guarantee or an `ACCEPTED` metadata value into evidence that a real component implements it. In particular, nonvacuity of a joint contract is weaker than totality for every admitted input.

The 14 envelope fields are schema, meaning, identity, time, basis, coverage, authority, state, effects, numeric, resources, evidence, change and exceptions. Values are accepted symbolic contract identifiers. Exact equality of these identifiers is checked; their real-world truth is not inferred. Nonidentity adapters remain unsupported in version 0.1.0.

## Read the result correctly

| Result | Meaning |
| --- | --- |
| `CASE_FORMALIZATION_REQUIRED` | Source summary is preserved but does not provide the accepted formal model needed for construction search |
| `MODEL_RECONSTRUCTED` | A finite candidate satisfies the encoded contracts, conditional on its component axioms; this is not delivery or execution qualification |
| `PROOF_GAP` | Model reconstruction succeeded but selected component implementation evidence is missing |
| `NO_CONSTRUCTION_IN_DECLARED_CATALOGUE_AND_BOUNDS` | Every enumerated candidate in the supplied finite profile failed, or no structurally admissible candidate exists; this says nothing about all possible framework constructions |
| `SEARCH_INCOMPLETE` | Candidate/time limit, unknown or disagreement blocks a complete decision |
| `UNSUPPORTED_ENCODING` | A declared composition form is outside the static kernel |
| `COUNTEREXAMPLE` | An encoded claim has a retained counterexample, such as a reachable unsafe state or overbooked capacity |
| `FINITE_SAFETY_PASS` | No unsafe state or nonterminal deadlock is reachable in the exact supplied finite graph; no liveness or real-system claim |
| `FINITE_RULE_PARITY_PASS` | ASP and both SMT encoders agree for the exact supplied rule table; omitted requirements cannot be discovered by parity alone |
| `REPLAY_MATCH` | Re-execution matches the retained bounded evidence; this is not a checked Alethe or other proof object |

Version 0.1.0 deliberately has no unconditional `COVERED` exit. It has no qualified domain execution registry capable of establishing that end-to-end claim. This is an explicit remaining integration requirement, not a configurable boolean bypass.

## Assurance boundary

The final development suite passed 45 tests. Three generated-input tests ran 100 examples each with no failing or invalid examples. One test body was generated unchanged by Hypothesis Ghostwriter and uses `unittest.TestCase.assertEqual`. The other test bodies are authored development tests and do not qualify under the framework's inherited generated-guard rule. The diagnostic adapters are project-owned and disclosed. GP01 and the full P301, P302, P303, P319 and P344 records remain unqualified at their original full scope.

Z3 and cvc5 are different engines with separate encoders here. They still share the accepted AST and can agree on an incorrect interpretation. Neither solver verifies that the original prose was complete or faithful. The replay bundle is not an independently checked formal proof artifact: Alethe/Carcara integration is not implemented.

The construction search is exhaustive only within the supplied finite instance catalogue, compatible identity edges and component bound. It does not enumerate arbitrary new instances, arbitrary adapters or every possible grammar construction. The search time limit is checked around solver waits and between candidate validations; individual validation calls have their own per-query timeout, so it is not a hard process-wide deadline. Solver errors cannot produce a successful coverage result.

The tool reads files and runs local solvers. It never evaluates case text as Python, shell or an SMT command script, sends messages, executes effects or changes the case source. CLI exit zero means the command completed; inspect the result status to determine the assessment. Input errors exit 2.

## Source documentation

The implementation uses the public APIs of [clingo 5.8](https://potassco.org/clingo/python-api/5.8/), [Z3](https://microsoft.github.io/z3guide/docs/logic/intro/), [cvc5 1.3.4](https://cvc5.github.io/docs/cvc5-1.3.4/), [jsonschema](https://python-jsonschema.readthedocs.io/en/v4.23.0/validate/) and [Hypothesis Ghostwriter](https://hypothesis.readthedocs.io/en/latest/reference/integrations.html). The installed pinned package APIs and sources were also inspected. The online Hypothesis reference is rolling; the generated test records the actual 6.131.9 generator used.

The earlier proposal considered [Pacti](https://www.pacti.org/), [OCRA](https://ocra.fbk.eu/), [AGREE](https://loonwerks.com/tools/agree.html), [Apalache](https://apalache-mc.org/) and [Carcara](https://github.com/ufmg-smite/carcara). None is presented as an implemented backend in this release.
