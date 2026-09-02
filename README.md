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
| `packs/foia/` | The FOIA pack: sources with provenance, the case record, proposals, the checklist, the rules, the invariants |
| `tests/` | Deterministic tests, including the double-build gate |

See `docs/ASSESSMENT.md` for the plan and the guarantees, and `packs/foia/README.md` for what the slice does and what is still provisional.
