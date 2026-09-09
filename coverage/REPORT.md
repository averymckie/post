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

