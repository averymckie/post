# Compiled AI

Compile a regulation into rules a program can run, with a byte-exact quote behind every rule, one recorded human answer per sentence, and no model at decision time.

This repository holds the method paper, the audit of its claims, the assessment and plan, and the first vertical slice of the pipeline: the Freedom of Information Act request-handling rules, compiled from the Department of Justice's published copy of 5 U.S.C. 552.

| Where | What |
| --- | --- |
| `papers/` | The method paper, kept verbatim with its hash, and the verified bibliography |
| `docs/ASSESSMENT.md` | What exists, what is missing, what was checked, what to build |
| `docs/CITATION_LEDGER.md` | Every regulatory claim in the paper with a status, the URL fetched, and an excerpt |
| `docs/TOOLING_AUDIT.md` | Every library claim in the paper checked against official documentation |
| `src/compiled_ai/` | The pipeline, one module per step |
| `packs/foia/` | The FOIA pack: source with provenance, the case record, proposals, the checklist, the rules, the invariants |
| `tests/` | Deterministic tests, including the double-build gate |

## The chain

| Step | Module | Who | What |
| --- | --- | --- | --- |
| 1 read | `read.py` | program | every character of the source with its position; struck-through text dropped and counted |
| 2 cut | `cut.py` | program | sentences with their positions, by punctuation rules; no statistical model |
| 3 propose | `propose.py` | model | a typed statement per sentence, recorded as a fixture |
| 4 check | `check.py` | program | byte-exact quote, defined actor, connective table, clock stated in the quote, reserved decisions |
| 5 confirm | `confirm.py` | person | one recorded answer per statement; two reviewers' agreement measured |
| 6 generate | `generate.py` | model | a rule function per confirmed statement; no rule without a statement, no statement without a rule |
| 7 prove | `prove.py` | program | mypy strict and the property tests (testing, not proof) |
| 8 reconcile | `reconcile.py` | program | the solver checks the rules can all be true; a minimal conflicting set otherwise |
| 9 order | `order.py` | program | the unique lexicographic order of the steps; cycles reported |
| 10 seal | `seal.py` | program | a digest per rule from its sentence bytes and its function bytes; a manifest digest over all |
| 11 run | `runtime.py` | program | a proof or a list of reasons; never a third outcome; no model |

## Commands

```
uv venv .venv --python 3.11 && uv pip install --python .venv/bin/python -e ".[compiler,dev]"
.venv/bin/compiled-ai compile packs/foia         # build and seal
.venv/bin/compiled-ai verify packs/foia          # rebuild and compare every digest
.venv/bin/compiled-ai run packs/foia packs/foia/cases/clean-partial-grant.json
.venv/bin/compiled-ai prove packs/foia           # mypy --strict and the pack's tests
.venv/bin/python -m pytest                       # everything, deterministic, no network
.venv/bin/python -m mypy --strict src/compiled_ai packs
```

The `live` extra installs the model client. It is used by exactly one command, `compiled-ai fixtures <pack> --live`, which records proposals for sentences that have none. No test and no build calls a model.

## Guarantees and the tests that check them

| Id | Guarantee | Test |
| --- | --- | --- |
| G1 | Every rule carries a quote that is a byte-exact substring of the canonical source | `tests/test_check.py::test_any_altered_quote_is_rejected_unless_it_is_still_in_the_source` |
| G2 | Same sources, same checklist, same toolchain seal to an identical manifest | `tests/test_determinism.py` (two processes, two hash seeds, and the committed manifest) |
| G3 | The runtime returns a proof or reasons for any input and never raises | `tests/test_runtime.py::test_runtime_never_raises_on_arbitrary_input` |
| G4 | The runtime depends on no model and no compiler library | `tests/test_boundary.py` |
| G5 | The rule base is satisfiable, or the build fails with a minimal conflicting set | `tests/test_reconcile_order_seal.py::test_injected_contradiction_is_reported_as_the_minimal_pair` |
| G6 | The order respects every precedence, or the build fails with the cycle | `tests/test_reconcile_order_seal.py::test_order_is_unique_and_cycle_is_reported` |
| G7 | No rule makes a decision the source reserves to a role | `tests/test_runtime.py::test_every_route_names_a_reserved_decision_and_results_are_provisional` |

How determinism is achieved: no step reads the clock or a random source; every collection is iterated in sorted order; the sentence cutter is rule-based; the solver runs with fixed seeds and a resource limit instead of a wall-clock timeout, and conflicting sets are minimized by deletion in a fixed order; the topological order is the lexicographic one; the manifest is canonical JSON with sorted keys; Hypothesis runs under its `ci` profile. The model's output is recorded as fixtures, and the checker, not the fixture, decides what compiles.

## Status

The FOIA pack builds, verifies, and runs, and all tests pass. Everything in it is marked provisional until a named reviewer confirms the checklist and the proposals are re-recorded through the propose adapter; see `packs/foia/README.md`. The assessment in `docs/ASSESSMENT.md` lists what comes next.
