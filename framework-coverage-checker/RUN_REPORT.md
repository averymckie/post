# Checker implementation and completed run

The checker is built and has processed the latest 5,000 cases. It searches finite constructions, checks them with independent Z3 and cvc5 encoders, preserves counterexamples and limits, and records missing evidence separately. The framework has been updated with the implemented scope, the actual results and the remaining hardening items.

**The current export does not establish poor conceptual coverage.** It also does not supply enough accepted contracts and implementation evidence to certify any original case as fully covered. The mechanical result is 5,000 cases requiring formalization, zero full coverage certificates and zero proved uncovered cases. This is not a 0% coverage finding.

## What is delivered

| Deliverable | Contents |
| --- | --- |
| Executable checker | Python package and CLI; pinned dependency lock; no runtime LLM or hosted service |
| Full-case results | 5,000 JSON dossiers, a searchable SQLite database, source clauses, findings and open obligations |
| Frozen framework | Original bytes, all 38 family cards and all 349 indexed proof records |
| Updated framework | Explicit independent generation rule, corrected F29/P99 retrieval anchor, CK01 implementation scope and hardening register |
| Verification evidence | 45 passing tests, generated-input statistics, solver query traces, counterexamples and replay results |
| Reproduction material | Formal JSON schema, complete demonstration inputs, exact commands and a reviewable framework patch |

## The corpus run

The checker read every record in the latest `cases_simple.txt`, including UC-05000 on source line 5001. It preserved 131,659 source-clause occurrences and 19,894 activity/product occurrences. Repeated labels were retained with separate occurrence identities.

| Mechanical finding | Cases | Interpretation |
| --- | ---: | --- |
| Missing accepted formal reconstruction and case-bound implementation witness | 5,000 | Full coverage remains undetermined |
| At least one repeated input, part or deliverable label | 3,321 | Multiplicity needs interpretation; repetition is not automatically an error |
| Dash input placeholder | 31 | Explicitly missing input detail in the export |
| Strict covered / lenient partial | 14 | Requires evaluator trace or verdict-semantics explanation |
| Root label absent from the case's own part outputs | 0 | A narrow syntactic check passed |
| Literal deadline beyond literal time window | 0 | A narrow numeric check passed; scheduling feasibility is unproved |

Every dossier preserves the original need, context, products, parts, inputs, conditions, dynamics, tags, window and source verdict. It includes the applicable need and condition review aids from the earlier assessment. The 52 previously authored individual summary reviews are explicitly identified; the other 4,948 records are not presented as individually proven semantic constructions.

The source summaries lack accepted atomic requirement predicates, precise source-to-input bindings, selected component contracts, exact typed edges, full acceptance criteria and case-bound qualification evidence. The checker cannot derive the truth of these items from labels. It therefore does not run a fictional construction search over family names and call the result coverage.

## What the checker actually demonstrated

| Execution | Observed result |
| --- | --- |
| Three-stage plan construction | clingo recursively selected all three prerequisites; both SMT engines validated the graph, handoffs, root and joint capacity predicate |
| Same construction with excess shared demand | The capacity claim failed; retained counterexample gives demand 5 + 5 against capacity 8 |
| Scenario input presented as observation | No identity-compatible binding; diagnostic names the evidence-basis mismatch and absent qualified adapter |
| Alternate supplier | Search found a working conditional construction when another supplier's contract failed |
| One-candidate limit | Returned incomplete search instead of claiming no framework construction exists |
| Circular prerequisites | Both ASP search and independent SMT replay rejected the cycle |
| Consent revocation state model | Found the reachable state allowing an effect after revocation |
| Joint feature rule | Derived the shared-resource obligation only when both fork and shared-resource features were present; SMT agreed |
| Changed certificate | Rejected the altered verdict, including when the outer integrity hash was recomputed |

These are separately authored demonstrations and development tests. They do not count toward original-case coverage. Even the successful model reconstruction reports a proof gap because its component implementation contracts are assumptions without actual domain execution evidence.

The final standard pytest run collected and passed **45 tests**, with **zero failures, errors or skips**. Three Hypothesis tests each ran 100 passing examples, with zero failing or invalid examples. Settings were deterministic generation, 100 examples, no Hypothesis database and no deadline filter. One test body was generated unchanged by Ghostwriter in unittest style; it uses the published `TestCase.assertEqual` assertion. The other tests are authored development tests and are not claimed to satisfy the inherited generated-guard qualification rule.

The corpus database passed SQLite's integrity check. The result contains exactly 5,000 case rows. The stored conditional plan certificate was replayed successfully against its frozen inputs and checker identity. No full framework proof chain was promoted on the strength of these bounded checks.

## Framework changes

The framework's generation rule now explicitly starts from practical world cases and keeps family, grammar, proof and mapping feedback out of the generator. Cases freeze before reverse engineering, and extensions cannot retrospectively improve the baseline score.

F29's short anchor list now includes P99. The full proof record already existed; this is a retrieval correction. All 349 original proof bodies are preserved. The other 37 family cards are unchanged.

New section 11, CK01, specifies the implemented checker, supported predicate and composition profiles, result semantics, dependency versions, run counts and exact open obligations. It distinguishes partial implementation of P301/P302/P303/P319 mechanisms from full qualification of those records. GP01, P344 and the original integration gates remain in force.

## What remains open

| Layer | Exact remaining work |
| --- | --- |
| Case formalization | Accept each original clause's meaning and bind it to atomic requirements, inputs, outputs and constraints |
| Executable family catalogue | Bind approved family profiles to actual public primitives, required ports, assumptions and implementation evidence |
| Typed adapters and integration | Supply qualified nonidentity adapters; execute actual producer, serialization, reload, adapter and consumer paths |
| Complete interaction rules | Approve the full rule table for the selected grammar; engine agreement cannot expose a rule omitted from every encoding |
| Stateful and physical correspondence | Connect actual runtime behavior to accepted state abstractions; establish liveness, fairness and physical/effect evidence where required |
| Proof-artifact verification | Add independently checked proof objects before claiming that assurance level; the current bundle supports solver re-execution |
| F12 routing and packing | Qualify their own chains and acceptance arguments; scheduling foundations alone do not close the existing gap |

The current construction kernel supports finite static Seq, Join and ForkJoin DAGs with identity-compatible envelopes and quantifier-free Boolean/linear integer/rational predicates. The separate state checker establishes safety and nonterminal-deadlock results for an explicit graph of at most 50 states. It does not establish general liveness or actual implementation behavior. Full unconditional `COVERED` is intentionally unavailable until the required implementation evidence can be validated.

## Evidence identities and commands

The frozen case file is SHA256 `9caa4c997dd012f1a330d4e50259a32800c4c4f49bd9edf2909ac329f39c52bc`. The original framework is SHA256 `2ef09333cdb41f82302ce0a12565afd2d653190b444705fb19684e60e25251de`. The amendment's hash and preservation checks are in `results/framework-update-verification.json`; the package's file hashes are in `MANIFEST.json`.

Start with the installation and run commands in `README.md`. For a case dossier:

```bash
.venv/bin/python -m fwcheck show results/corpus-baseline/cases.sqlite3 UC-00049
```

For the conditional model and its actual replay:

```bash
.venv/bin/python -m fwcheck replay examples/planning.json results/planning-certificate.json --framework data/framework-baseline.txt
```

The implementation uses public [clingo solving APIs](https://potassco.org/clingo/python-api/5.8/clingo/solving.html), [Z3](https://microsoft.github.io/z3guide/docs/logic/intro/), [cvc5 1.3.4](https://cvc5.github.io/docs/cvc5-1.3.4/), [jsonschema 4.23.0](https://python-jsonschema.readthedocs.io/en/v4.23.0/validate/) and [Hypothesis Ghostwriter](https://hypothesis.readthedocs.io/en/latest/reference/integrations.html). Those libraries supply search, decision, validation and test-generation mechanisms; none supplies an automatic proof that a natural-language world case was faithfully encoded.
