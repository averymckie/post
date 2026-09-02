# FOIA pack

The request-handling rules of the Freedom of Information Act, 5 U.S.C. 552, compiled from the Department of Justice's published copy of the statute. This is the first vertical slice of the pipeline: every step from reading the source to running a case works, deterministically, with a byte-exact quote behind every rule.

## What it compiles

| Count | What |
| --- | --- |
| 1 | source: the DOJ FOIA.gov statute page, hash recorded in `sources.yaml` |
| 237 | units of text read (struck-through repealed language dropped, 3,732 characters, recorded in the build notes) |
| 284 | sentences cut |
| 38 | sentences with recorded proposals (the request-handling core: (a)(6), (a)(8), (b), (f)) |
| 51 | statements accepted by the checker, out of 51 proposed |
| 45 | statements confirmed and compiled into rule functions |
| 12 | decisions the statute reserves to a person, routed and never made by a rule |
| 17 | constraints checked for consistency by the solver: consistent, no variation points |

The sealed manifest is `build/manifest.json`. `compiled-ai verify packs/foia` rebuilds the pack and compares every digest.

## What a case gets back

A case is a JSON record matching `record.py`: dates received, the determination and its date, what the notice states, withholdings with their exemptions and recorded findings, any extension, tolling, and appeal, and the date the case is evaluated as of. The runtime never reads the clock.

The result is one of two values. A proof lists every rule that applied with the sentence it came from and the decisions routed to the agency or the head of the agency. A reasons list names each clause the case tripped, quotes it, and says the remedy. Two examples are in `cases/`.

```
compiled-ai run packs/foia packs/foia/cases/clean-partial-grant.json      # a proof
compiled-ai run packs/foia packs/foia/cases/late-denial-without-names.json   # three reasons
```

## What is provisional

Everything in this pack is marked provisional, and every result says so. Two things need a named person:

1. **The proposals** were authored by a language model in an interactive session and written as fixtures, because the build session had no API credential for the propose adapter. Every quote was checked byte-exact by the checker before compiling. `compiled-ai fixtures packs/foia --live` re-records them through the adapter when a credential is available.
2. **The confirmations** in `checklist.yaml` carry `reviewer: session-assistant` and `provisional: true`. A reviewer confirms a statement by reading its allowed and forbidden examples, then setting `reviewer` to their name, `answer` to true or false, and `provisional` to false. The build then drops the provisional flag from the manifest and from every result.

One more caveat: the working-day calendar in `calendar.py` lists the legal public holidays under 5 U.S.C. 6103 and the observance rules, but that statute was unreachable from the build session and the list was not verified against fetched text. Verify it before relying on a computed deadline.

## What is not compiled

- The rest of the statute: fees and fee waivers, judicial review, the definition of unusual circumstances in (a)(6)(B)(iii), aggregation and multitrack processing, the compelling-need definition for expedited processing, records available under (a)(2), annual reports, the Chief FOIA Officer and Council provisions.
- Words that are judgments and cannot be mechanized: "immediately" in the notice rule and "promptly" in the release rule. The rules check that the act happened and is dated no earlier than the determination; the checklist notes say so.
- Agency regulations. The statute is compiled alone. An agency's own FOIA regulation would be a second source with its own scope; the reconcile step reports where it varies from the statute.

## Files

| File | What |
| --- | --- |
| `sources.yaml`, `sources/` | The source with URL, commit, retrieval date, hash, license |
| `reserved.yaml` | Roles the statute names and decisions it reserves, each with a byte-exact quote the build verifies |
| `record.py` | The typed case record |
| `calendar.py` | Working days, cited to 5 U.S.C. 6103 |
| `fixtures/proposals/` | One recorded proposal file per sentence, keyed by the sentence digest, with provenance |
| `checklist.yaml` | One recorded answer per statement |
| `rules.py` | One function per confirmed statement, registered by statement id |
| `tests/test_invariants.py` | The calendar, and the properties that must never break |
| `cases/` | Example cases |
| `build/` | The sealed manifest and the build report |
