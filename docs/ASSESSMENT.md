# Assessment and proposal: making Compiled AI testable, deployable, and free of fabrication

Date: 2026-09-02. Scope: the repository `averymckie/post` and the document "Compiled AI, industry by industry" (dated 2026-09-01), uploaded on 2026-09-02. This file answers four questions. What exists. What is missing. What was checked and what was found. What to build, in what order, with what acceptance test.

Every statement in this file that reports a fact about a source was checked against the source on 2026-09-02, or is marked as not checked. The check results are in `CITATION_LEDGER.md` beside this file.

## 1. Bottom line

Yes, this can be done. It cannot be done in one step, and it is not a model in the machine-learning sense. It is a method paper plus a software pipeline. Today the paper exists and the pipeline does not.

What exists is a clear description of a ten-step method and twelve worked examples. What is missing is everything that would let someone test it, run it, or trust a number in it:

- There is no code. None of the ten steps is implemented.
- There are no tests, no build, no dependency lockfile, no continuous integration.
- There is no `papers/` folder, and no bibliography of the research the method rests on.
- The document's regulatory claims had not been independently checked. This assessment checks them. The results are in section 4.
- The document promises outcomes ("in seconds", "cannot be produced") that are design goals, not measurements.

The four asks split into work that is days and work that is weeks:

| Ask | Size | Blocking dependency |
| --- | --- | --- |
| Research papers on `main` in their own folder | Days | Only one paper is in hand. Other papers must be supplied. |
| Tighten the language for a lay reader | Days | Citation fixes from section 4 should land first, so the rewrite carries correct facts. |
| Deterministic tests | Weeks | The pipeline must exist before it can be tested. A one-industry vertical slice comes first. |
| Deployable across industries | Weeks, after the slice | Six of the twelve industries compile paywalled standards that cannot be redistributed. |

"Zero fabrication" is not a fifth ask. It is the acceptance test for the other four. Sections 7 and 9 give the controls that make it checkable rather than promised.

### Progress since this assessment was written

Later on 2026-09-02, the first vertical slice was built and committed: the eleven-step pipeline under `src/compiled_ai/`, and a FOIA pack under `packs/foia/` compiled from the Department of Justice's published copy of 5 U.S.C. 552. The pack cuts 284 sentences, accepts 51 statements through the checker, compiles 45 of them into rule functions, routes 12 reserved decisions, reconciles 17 constraints with no contradiction, and seals to a manifest that two separate processes under different hash seeds reproduce byte for byte. All tests in section 7.3 exist and pass. Everything in the pack is marked provisional: the proposals were authored by a language model in an interactive session rather than through the propose adapter (the build session had no API credential), and the confirmations await a named reviewer. `packs/foia/README.md` states exactly what is compiled, what is provisional, and what is not compiled.

## 2. What exists today

### 2.1 The repository

| Item | State |
| --- | --- |
| Files on `main` | Three: `CLAUDE.md`, `.gitignore`, `.claude/skills/fable-prompting/SKILL.md` |
| Commits | One |
| Source code, tests, CI, lockfile | None |
| Difference between `main` and this branch at start | None |

The skill file is a reference for calling the Claude API. It is unrelated to the method and can stay.

### 2.2 The document

"Compiled AI, industry by industry" has three parts. Part 1 states the method once: ten steps, each done by one library, two of them neural (a language model proposes) and eight symbolic (a program checks). Part 2 gives twelve worked examples, one per industry, each in the same five-paragraph shape. Part 3 lists what the examples share.

Measured on 2026-09-02 with a local syllable counter (Pyphen) and the standard readability formulas:

| Measure | Whole document | Part 1 (method) | Part 2 (twelve examples) |
| --- | --- | --- | --- |
| Words | 5,816 | about 1,500 | about 4,100 |
| Average words per sentence | 12.6 | 10 to 13 | 12 to 14 |
| Flesch-Kincaid grade | 7.8 | 4.9 to 7.5 | 7.1 to 9.9 |
| Flesch reading ease | 61.5 | 61 to 80 | 47 to 67 |
| Sentences over 30 words | 22 of 475 | | |
| Longest sentence | 52 words | | |

For a lay reader, the common targets are a grade around 8 and a reading ease above 60. Part 1 already meets them. Six of the twelve examples do not (Manufacturing 9.9, Banking 9.6, Healthcare 9.5, Pharmaceuticals 9.3, Insurance 9.0, Aerospace 8.5).

The bigger readability problem is not sentence length. It is repetition and undefined terms:

- Ten tool names appear about 170 times. `pydantic` appears 26 times and "the anthropic SDK" 24 times, almost all inside the twelve examples, where they add nothing a lay reader can use.
- Five template sentences repeat eleven times each, once per example: "Cut with spaCy", "Check with the checker", "Propose through the anthropic SDK into a pydantic schema", "Seal with hashlib and run", and "Everyone else evaluates a record."
- Fifteen technical terms are used before or without a definition: typed record, schema, invariant, unsatisfiable core, topological, precedence, variation point, reserved decision, reserved judgment, property tester, digest, byte-exact, constraint solver, type checker, and "sampler" as the word for a worked example.

### 2.3 What the document gets right

These should survive any rewrite:

- The separation of "propose" (neural) from "check" (symbolic), and the rule that nothing downstream trusts the proposal.
- The byte-exact quote requirement. This is the mechanism that makes zero fabrication checkable instead of promised.
- The reserved decision: a sentence that names a role compiles into a routing rule, not a decision rule.
- The "What is honest to say" section. It is the most important paragraph in the document and it is currently buried.
- The seal step. Hashing each rule to its source bytes is what makes a rebuild verifiable and what makes bring-your-own-PDF deployment possible (section 8.3).

## 3. What is missing

### 3.1 For "research papers on main in their own folder"

- No `papers/` folder exists. This pull request creates it.
- Only one paper is in hand: the uploaded document. If there are others, they must be supplied. I have not seen them and will not guess at them.
- The document cites regulations and standards, not research. A method paper that claims to be at the frontier must place itself against prior work: logic-programming formalizations of statutes, "rules as code", property-based testing, satisfiability solvers and unsatisfiable cores, neurosymbolic reasoning with language models, and the measured hallucination rates of legal language models. `papers/REFERENCES.md` in this pull request holds only entries whose title and authors were confirmed by fetching the publisher, DOI, or arXiv page. Section 5 gives the counts.
- The document's own provenance is not recorded. The copy in `papers/` carries its SHA-256 so later edits are visible.

### 3.2 For "tighten the language for the layman"

- No glossary. Section 2.2 lists fifteen terms that need one.
- No single statement of the recipe. The "how you do it" paragraph is restated twelve times with tool names. It should be stated once in Part 1, and each example should carry only what differs: which sentences become which kind of statement, and who signs.
- No footnotes. A lay reader cannot check "31 CFR 1010.230 says 25 percent" without a link. Every regulatory claim needs a source link and the date it was read.
- No marking of measured versus expected. "Receives, in seconds" and "cannot be produced" read as facts. Until the pipeline exists and is timed, they are expectations.
- No measurable target. "Tight for the layman" should be a test: grade at or below 8 per section, no sentence over 30 words, every technical term defined at first use. A script can check all three on every commit.

### 3.3 For "tested deterministically"

- There is nothing to test. The pipeline must be built first.
- Two of the ten steps call a language model. Model output is not deterministic, and the current Claude API does not accept temperature or other sampling controls; the API documentation notes that temperature zero never guaranteed identical output even when it was accepted. Determinism therefore cannot come from the model call. It has to come from architecture: record the model's proposals as fixtures, run every test against the fixtures, and make every symbolic step a pure function of its inputs. Section 7 gives the design.
- The document's own guarantees need to become named tests. "A validation never fails to answer", "a rebuild produces the same digests", "no denial without a stated basis", and "after step ten, nothing neural runs" are each testable, and each is currently just a sentence.
- Three design gaps would break determinism or provenance in a naive implementation:
  1. "Byte-exact in the pdfplumber output" is underspecified. PDF text extraction produces ligatures (fi as one character), line-end hyphenation, and inconsistent whitespace. Two extractor versions can produce different bytes for the same page. The fix is a versioned canonicalization function (Unicode normalization, whitespace collapse, hyphenation repair) whose output is what "byte-exact" refers to, with the extractor version pinned and recorded in the sealed manifest.
  2. "There is no third outcome" needs a fail-closed rule. A crash, a timeout, or a malformed record must be reported as typed reasons, never as a proof and never as an exception escaping the runtime.
  3. The reconcile step describes the solver as returning "the smallest set" of conflicting sentences. A solver's unsatisfiable core is not minimal by default; it must be minimized explicitly, and even then it is one minimal set, not necessarily the smallest. The paper should say "a minimal set". Section 6 has the documentation check.

### 3.4 For "deployable across industries"

- No package, no command-line interface, no container, no configuration format for an industry.
- No separation between the compiler (which needs the model) and the runtime (which must not). The claim "at decision time there is no model in the room" should be enforced by shipping two images, with the runtime image containing no model client at all.
- No licensing plan. The twelve examples compile these sources:

| Industry | Public and redistributable | Copyrighted or sold by the publisher |
| --- | --- | --- |
| Aerospace and defense | 22 CFR 120-130, 15 CFR 734, FAR 1.602-1, DFARS 252.204-7012, MIL-HDBK-61A, DCMA manuals | EIA-649, AS9100, AS9102 (SAE) |
| Banking and wealth | 31 CFR 1010.230, 1023.210, 1023.320; FINRA Rules 4512, 2360, 3260 (published free by FINRA) | None |
| Insurance | 10 CCR 2695.7 (California) | NAIC Model 900 (published by NAIC; redistribution terms to check); the policy form (the insurer's own) |
| Healthcare | CMS-0057-F, 42 CFR 422.566 | The payer's medical policy (the payer's own) |
| Pharmaceuticals and devices | 21 CFR 211.22, 211.100, 21 CFR 820 | ISO 13485 (incorporated by reference; sold by ISO) |
| Energy and utilities | NERC CIP-010, CIP-003 (published free by NERC) | None |
| Government | 5 U.S.C. 552 | None |
| Manufacturing | None | ISO 9001:2015 (ISO), IATF 16949 (IATF) |
| Technology and software | GDPR Articles 12 and 15 | None |
| Logistics and supply chain | 19 CFR 141, 142, 111; HTS; 19 U.S.C. 1485 | None |
| Legal and professional services | State rules of professional conduct (state-published) | ABA Model Rules (viewable free; copyrighted by the ABA) |
| Telecommunications | 47 CFR 52.35, 52.36; FCC orders | None |

A rule base for a copyrighted standard contains that standard's sentences. Shipping it is redistribution. Section 8.3 gives the bring-your-own-PDF design that avoids this, and it falls out of the seal step the document already has.

### 3.5 For "frontier scientific"

A method becomes a scientific claim when it states exactly what it guarantees, shows the guarantee mechanically, and measures what it cannot guarantee. The document does the first informally. It needs:

- A precise guarantee list (section 9.1), each guarantee mapped to the mechanism that enforces it and the test that checks it.
- An honest name for step seven. Property-based testing is testing, not proof. A type checker is a type checker. The only proving component in the chain is the satisfiability solver. Either rename the step "Test", or add real proof: encode each rule function's logic for the solver and prove each invariant by showing its negation is unsatisfiable. Both are reasonable. The second is stronger and is feasible for rules over boolean and numeric fields, which is most of them.
- An evaluation protocol (section 9.2): annotated sentences, measured agreement between two reviewers, a fabrication-injection test, a determinism test, and a baseline that uses a model at decision time so the paper's central claim is measured rather than asserted.
- A limitations section. Rules that span sentences (an exception two paragraphs later, a definition in another part), standards written as judgment ("reasonably designed"), extraction errors, and version drift of the source are all real and are not addressed by the sentence-by-sentence design.

## 4. Citation audit

Every regulation, standard, clause, deadline, threshold, and signatory the document asserts was checked on 2026-09-02. Ninety-seven claims were checked. The full ledger, with the URL fetched and an excerpt from the source for each claim, is in `CITATION_LEDGER.md` beside this file.

One caveat governs the whole audit. Every primary host was blocked by this session's network policy: eCFR, govinfo, the House's US Code site, the Federal Register, FINRA, CMS, NERC, the FCC, EUR-Lex, the ABA, ISO, and the rest. The checks therefore used verbatim copies on GitHub: government-published source repositories where they exist (the Department of Justice's foia.gov site, GSA's FAR and DFARS publishing repositories) and third-party mirrors of public-domain text otherwise, matched across two mirrors where possible. "Verified" below means verified against a fetched verbatim copy. Nothing was marked verified from memory. The first job on an unrestricted network is to re-run the ledger against the primary hosts; the recorded URLs and excerpts make that mechanical.

| Status | Count | Meaning |
| --- | --- | --- |
| Verified | 62 | A fetched copy of the source supports the claim as stated |
| Partial | 15 | The requirement exists, but the citation, the scope, or the wording is off |
| Incorrect | 1 | The fetched source contradicts the claim |
| Unverifiable | 19 | Paywalled standard or blocked source; what could be confirmed is recorded |

The findings that change the document, in order of consequence:

1. **Incorrect, customs.** "The summary clock is tracked from arrival." The ten working days run from the time of entry, which by default is the moment CBP authorizes release, not arrival (19 CFR 142.12(b) and 141.68(a)(1)).
2. **Partial, legal.** ABA Model Rule 1.7(b) has four cumulative conditions. The document states two and says "only if". A rule compiled from the document's sentence would treat conflicts the rule forbids as waivable. The two omitted conditions: the representation is not prohibited by law, and it does not involve one client asserting a claim against another in the same litigation.
3. **Unverifiable with no source, aerospace.** The section's "thirty-day" clock has no identifiable source among its citations. Until a source is named, that sentence is what zero fabrication forbids.
4. **Partial, aerospace.** "Only the contracting officer may bind the government" is FAR 1.601(a), not 1.602-1. Acceptance is the contracting officer's responsibility under FAR 46.502, assignable to the contract administration office; "the government inspector" is not the regulatory signatory. MIL-HDBK-61A was superseded by MIL-HDBK-61B in 2020, and the fetched Air Force implementation counts reliability and maintainability among the Class I criteria, so "form, fit, function, or interface" understates them.
5. **Partial, customs.** The ten-working-day entry summary rule is 19 CFR 142.12(b), and Form 7501 is 142.11(a). Part 141 holds the definitions and the time of entry.
6. **Partial, telecom.** The four-field validation limit is not in 47 CFR 52.36, which lists fourteen required fields plus an optional passcode; the four-field limit comes from an FCC order. The 8 a.m. to 1 p.m. window is in 52.35(a) itself, which also carries a "unless a longer period is requested" exception the document omits.
7. **Partial, banking.** 31 CFR 1023.210 designates an individual responsible for the program; it assigns neither suspicious activity report decisions nor screening decisions to that person. FINRA Rule 2360(b)(16)(B), seen only in a search snippet, lets a branch office manager or a Limited Principal approve options accounts, not only a Registered Options Principal.
8. **Partial, government.** The statute names "the head of the agency" for appeals; "or the designee" comes from agency regulations. Exemption 6 applies only where disclosure "would constitute a clearly unwarranted invasion of personal privacy", and segregable portions must be released, so "a personnel file is denied" over-simplifies.
9. **Partial, manufacturing.** IATF 16949 clause 8.7.1.1 in its 2016 text covers "use as is" and rework; Sanctioned Interpretation 9 changed it to repair with a cross-reference to 8.7.1.5. Cite both.
10. **Partial, energy.** Firmware is a baseline item only "where no independent operating system exists". The version numbers are missing: CIP-010-4 and CIP-003-9 are in force, with successors approved for 2028.
11. **Partial, healthcare.** The CMS-0057-F timeframes are verified (72 hours expedited, 7 calendar days standard, in effect from 2026-01-01), but the document omits the rule's scope limits. 42 CFR 422.566(d) is the physician-review paragraph, with expertise conditions the document omits.
12. **Partial, insurance.** NAIC Model 900 lists the unfair practices and a fifteen-day forms deadline but sets no numeric acknowledgment deadline; those are in Model Regulation 902.
13. **Precision, pharmaceuticals.** "Anything that affects the product" overstates 21 CFR 211.22(a), which enumerates categories. The device rule took effect on 2026-02-02 and incorporates ISO 13485:2016; the document gives neither the day nor the edition.

The audit also shows that the FOIA section is the most accurate in the document. Every subparagraph it relies on was found at the clause the document implies, and no claim in it was incorrect. That is one more reason to build the first pack there.

## 5. Bibliography audit

The document cites no research. `papers/REFERENCES.md` is a bibliography of the prior work the method rests on, built on 2026-09-02 under the same rule as the ledger: an entry is listed as verified only if a page showing its title and authors was fetched. The bibliographic hosts (the DOI resolver, arXiv, the ACM Digital Library, Springer, the ACL Anthology site, Semantic Scholar, Crossref) were all blocked, so verification used publisher source data on GitHub (ACL Anthology XML, the JOSS Crossref deposit, PMLR volume sources), Microsoft Research pages, and author-maintained citation files, each entry saying which.

| Status | Count |
| --- | --- |
| Verified | 19 |
| Verified alternates for unverified candidates | 3 |
| Unverified in this session | 12 |

The verified entries cover rules as code (Catala), property-based testing (Hypothesis), SMT solving (Z3) and its use at scale, neurosymbolic reasoning that pairs a language model with a solver (Logic-LM, LINC, SatLM), verified code generation (Clover, Lemur), measured hallucination rates of legal language models (Dahl and others, Journal of Legal Analysis), constrained decoding (Willard and Louf; Beurer-Kellner and others), extraction of norms from statutes (NOMOS; Holzenberger and Van Durme), a statutory reasoning benchmark (LegalBench), attribution measurement, and synthesis of formal specifications from natural language.

The twelve unverified entries are well-known works whose pages could not be fetched, among them QuickCheck, the British Nationality Act logic program, Cohen's kappa, and the reproducible builds paper. They stay listed as unverified with what was tried, rather than dropped or filled in from memory. Two of them have two DOIs in circulation and third-party citations of a third disagree on the issue number, which is why a fetched page is the standard.

## 6. Tooling audit

Every claim the document makes about a library was checked on 2026-09-02 against that library's official documentation. The rendered documentation sites were blocked by this session's network policy, so each check used the upstream source of the same page in the project's official repository, and the URL fetched is recorded per row. The full table with excerpts is in `TOOLING_AUDIT.md` beside this file.

| Claim in the document | Result |
| --- | --- |
| pdfplumber returns every character with its page, position, and size, plus words and tables | Confirmed. |
| spaCy's sentencizer splits by punctuation rules and needs no statistical model | Confirmed. The punctuation list is configurable and character offsets are available. |
| pydantic rejects a record that is missing a field or has a field of the wrong type | Confirmed, with one caveat: extra fields are ignored by default. Every schema a model fills must set `extra='forbid'`. |
| mypy rejects a function whose inputs and outputs do not match the types | Confirmed under `--strict`. The set of checks that flag enables may change between versions, so the version must be pinned. |
| hypothesis generates thousands of cases, shrinks a failure, and runs confirmed examples as permanent tests | Confirmed. Explicit examples run in their own phase. Reproducibility under `derandomize=True` (the built-in `ci` profile) holds only until the library, Python, or the test function changes. |
| z3 "returns the smallest set of rules that conflict, called the unsatisfiable core" | Contradicted. The documentation states that Z3 does not guarantee that unsatisfiable cores are minimal. Core minimization is off by default, and turning it on gives a minimal set, not the smallest. The paper should say "a minimal set" and the build must enable minimization. |
| The reconcile step is deterministic | Not documented. The random seeds default to zero and can be fixed, but no determinism guarantee is published. Wall-clock timeouts are documented as non-deterministic; the resource limit option is the deterministic alternative and is what the build should use. |
| networkx computes the order by topological sort and reports any cycle | Confirmed with a caveat. The plain topological sort is documented as "nonunique". The lexicographic variant with a key gives a unique order. The cycle finder picks its starting node "arbitrarily" unless one is given. |
| hashlib seals each rule so a rebuild produces the same digests | Confirmed for the hash. Whether the bytes being hashed are the same depends on the extractor: pdfplumber expands ligatures by default since version 0.9.0, changes its parser pin in most releases, and documents no handling of line-end hyphens. The canonicalization rule in section 3.3 is therefore the pipeline's own responsibility. |

Versions on PyPI on 2026-09-02, to pin in the lockfile:

| Library | Version | Released |
| --- | --- | --- |
| hypothesis | 6.167.1 | 2026-08-30 |
| z3-solver | 5.1.0.0 | 2026-08-16 |
| networkx | 3.6.1 | 2025-12-08 |
| spacy | 3.8.16 | 2026-08-24 |
| pdfplumber | 0.11.10 | 2026-06-15 |
| mypy | 2.3.1 | 2026-08-15 |
| pydantic | 2.13.5 | 2026-08-28 |
| anthropic | 1.3.0 | 2026-09-01 |

## 7. Proposal: deterministic testing

The design principle: every step is a pure function of its inputs, the two neural steps are recorded, and the build proves its own reproducibility by running twice.

### 7.1 Neural steps run against fixtures

- Steps three (propose) and six (generate) call the model through a thin adapter with two implementations: `live` and `replay`.
- `replay` returns a stored proposal keyed by the digest of the input sentence. Every test uses `replay`. No test opens a network connection.
- `live` is used only to create or refresh fixtures, behind an explicit command. A refreshed fixture is committed only after the checker accepts it. A fixture the checker rejects is kept as a negative fixture so the rejection path stays tested.
- The model is asked for a fixed schema using the API's structured output feature, so a malformed proposal is rejected by the API before it reaches the checker. The checker then verifies truth, not shape: the quote is byte-exact, the actor is defined, the connective matches the statement type.

### 7.2 Symbolic steps are pure and ordered

- No step reads the clock, the environment, or a random source. Inputs are bytes and prior step outputs.
- Every collection is iterated in sorted order. Sets are never iterated directly. Python's hash randomization is the most common source of accidental nondeterminism, and the test suite runs the build under two different hash seeds to catch it.
- Sentence splitting uses the rule-based sentencizer with no statistical model, so the same bytes always cut the same way.
- Precedence ordering uses the lexicographic topological sort keyed by sentence digest, so ties break the same way every time.
- The solver is run with fixed seeds and the core minimization option on. The reconcile step is run twice inside the build and the two cores must match.
- The seal is SHA-256 over the canonicalized sentence bytes plus the pinned versions of the extractor and the canonicalizer, recorded in a manifest.

### 7.3 The guarantees become named tests

| Guarantee in the document | Test |
| --- | --- |
| A quote is accepted only if it is byte-exact in the source | `test_checker_rejects_any_altered_quote`: mutate one byte of a valid quote (case, whitespace, ligature, a word) and assert rejection. Property-tested over thousands of mutations. |
| A rebuild from the same sources produces the same digests | `test_rebuild_is_byte_identical`: build the pack twice in separate processes with different hash seeds and temp directories; assert the manifests are identical. Runs in CI on every commit. |
| A validation never fails to answer | `test_runtime_is_total`: property test over arbitrary records, including malformed ones and ones with extra fields; assert the result is a proof or a reasons list and no exception escapes. |
| After step ten, nothing neural runs | `test_runtime_has_no_model_dependency`: import the runtime package and assert the model client is absent from loaded modules; the runtime container image is built without it. |
| No decision the source reserves to a role is ever made by a rule | `test_reserved_decisions_only_route`: for every reserved decision in the pack, assert no rule output can carry that decision's value. |
| A confirmed example is a permanent test | Each confirmed example is registered as an explicit example on the rule's property test, so it runs on every build and cannot be dropped silently. |
| Rules are consistent or the build fails with the conflicting set | `test_reconcile_reports_minimal_core`: inject a known contradiction and assert the reported core is exactly the injected pair. |
| The order respects every precedence sentence | `test_order_respects_precedence` and `test_cycle_is_reported`. |

### 7.4 Deterministic language tests

The rewrite gets the same treatment. A script in CI computes per-section grade level and sentence length, checks that every glossary term is defined before first use, and checks that every regulatory citation has a footnote with a URL. Then "tightened for the layman" has a pass or fail.

## 8. Proposal: deployable across industries

### 8.1 Layout

```
compiled-ai/
  pyproject.toml, uv.lock          pinned toolchain
  src/compiled_ai/                 the core, one module per step
    read.py cut.py propose.py check.py confirm.py
    generate.py prove.py reconcile.py order.py seal.py runtime.py
  packs/<industry>/                one folder per industry
    sources.yaml                   each source: URL, edition, retrieval date, SHA-256, license class
    record.py                      the typed case record
    invariants.py                  the properties that must never break
    reserved.yaml                  who signs, and the sentence that says so
    fixtures/                      recorded proposals and confirmed examples
    build/                         the sealed rule base and manifest (generated)
  tests/                           unit, golden, property, determinism, import-boundary
  papers/                          the paper, the bibliography, the citation ledger
  docs/                            glossary, assessment, deployment guide
```

### 8.2 Two images, not one

- `compiled-ai-compiler`: has the model client, the solver, the extractor. Runs steps one to ten. Used by the team that owns the rule base.
- `compiled-ai-runtime`: has the sealed rule base, the typed record, and the runtime. No model client is installed. Runs step eleven. Used in production.

This turns "no model at decision time" from a sentence into a property of the artifact that a deployer can verify by listing the installed packages.

### 8.3 Bring-your-own-PDF for copyrighted standards

For a source that cannot be redistributed, the pack ships everything except the text: the offsets, the digests, the statement types, the rule functions, and the confirmed examples. The deployer supplies their licensed PDF. The compiler extracts it, canonicalizes it, and checks that every digest matches. If one does not match, the edition is wrong and the build stops with the first mismatched sentence. If all match, the quotes are read from the deployer's own copy at run time. No sentence of the standard leaves the deployer's environment in the pack, and every proof still shows the sentence.

### 8.4 Command line

- `compiled-ai compile packs/foia` builds and seals a pack.
- `compiled-ai verify packs/foia` rebuilds and compares every digest.
- `compiled-ai run packs/foia case.json` returns a proof or a reasons list as JSON.
- `compiled-ai fixtures refresh packs/foia --live` is the only command that calls the model.

### 8.5 Order of industries

Start where the source is public domain, short, and exercises every statement type. The Freedom of Information Act example does: it has clocks (twenty working days), conditions (nine exemptions), required fields (the reasons, the appeal notice, the names and titles), and reserved decisions (the appeal). The banking example is the natural second because the customer due diligence rule has a numeric definition (25 percent) and a reserved signature. The six examples with copyrighted standards come last and use the bring-your-own-PDF path.

## 9. Proposal: the scientific claim

### 9.1 Guarantees, stated precisely

| Id | Guarantee | Enforced by | Checked by |
| --- | --- | --- | --- |
| G1 | Every rule carries a quote that is a byte-exact substring of the canonicalized source | The checker | Mutation property test |
| G2 | Same sources, same reviewer answers, same pinned toolchain give an identical sealed manifest | Pure steps, sorted iteration, fixed seeds | Double build in CI |
| G3 | The runtime returns a proof or a reasons list for every record and never raises | Fail-closed runtime | Totality property test |
| G4 | The runtime depends on no model | Separate image | Import-boundary test |
| G5 | The rule base is satisfiable, or the build fails with a minimal conflicting set | The solver with core minimization | Injected-contradiction test |
| G6 | The workflow order respects every precedence sentence, or the build fails with the cycle | Topological sort | Injected-cycle test |
| G7 | No rule produces a decision the source reserves to a role | The checker and the record type | Reserved-decision property test |

What is not guaranteed, and must be measured instead: that the typed statement means what the sentence means (the reviewer's answer); that the set of sentences is complete; that a rule function is correct beyond its tests, unless it is also proved by the solver.

### 9.2 Evaluation protocol

- Gold set: two reviewers independently type every sentence of three public sources (the FOIA statute, the customer due diligence rule, and the number porting rule). Report agreement with Cohen's kappa. Disagreements are adjudicated and recorded.
- Proposal quality: acceptance rate of model proposals by the checker, and by the reviewer after the checker, per statement type.
- Fabrication injection: seed proposals with altered quotes, invented section numbers, and undefined actors. The checker must catch every quote and actor injection. Report the rate.
- Determinism: one hundred rebuilds across machines and hash seeds. The identical-manifest rate must be one hundred percent.
- Baseline: the same cases answered by a model reading the source at decision time, ten runs each. Report answer variance and citation error rate. This is the comparison the paper's argument rests on.
- Runtime: latency distribution per case on the runtime image. This replaces "in seconds".

### 9.3 Limitations to state

Cross-sentence rules. Definitions that live in other documents. Judgment standards that do not compile. Extraction errors in scanned or multi-column PDFs. Source version drift and the need to recompile. The reviewer step is human and its cost scales with sentence count.

## 10. Proposal: the language pass

Do it after the citation fixes so the rewrite carries correct facts. Keep the original verbatim in `papers/` with its hash; publish the rewrite beside it.

- State the recipe once in Part 1 with the tool names, and once more without them for the lay reader. Remove every tool name from Part 2.
- Replace each example's "how you do it" paragraph with a short table: sentence, kind of statement, who signs. The prose that remains is the workflow, the rules, and the outcome.
- Add a glossary of the fifteen terms in section 2.2, and define each at first use.
- Split the twenty-two sentences over thirty words.
- Rename "sampler" to "worked example".
- Move "What is honest to say" to the front of Part 1.
- Footnote every regulatory claim with the source URL and the date read, using the ledger.
- Mark every outcome claim as measured or expected.
- Add the CI readability check from section 7.4.

Two before-and-after examples of the intended register:

Before: "A constraint solver checks that all the rules are consistent, and when they are not, it returns the smallest set of sentences that contradict each other."

After: "A solver checks that all the rules can be true at the same time. When they cannot, it returns a small group of sentences that cannot all be true together, so a person can read exactly where the source contradicts itself."

Before: "A type checker rejects a malformed function, and a property tester runs the confirmed examples and thousands of generated cases against every invariant."

After: "One tool checks that each rule takes the right kind of input and gives the right kind of output. Another tool runs the confirmed examples and thousands of made-up cases against each rule, looking for a case that breaks it. A rule that must never break is called an invariant, and every invariant gets this treatment."

## 11. Plan and estimates

Estimates are for one engineer with review from the document's author. They are estimates.

| Phase | Deliverable | Acceptance test | Estimate |
| --- | --- | --- | --- |
| 0 (this pull request) | `papers/` with the original document and hash, the verified bibliography, the citation ledger, this assessment | Every bibliography entry has a fetched URL; every ledger row has a status and a source | Done |
| 1 | Citation fixes in the document; the language pass; glossary; footnotes; readability check in CI | Readability script passes on every section; zero unverified citations | 2 to 4 days |
| 2 | Core pipeline, one pack (FOIA), fixtures, the eight tests in section 7.3, the double-build gate in CI | All tests pass with no network; double build identical | Built on 2026-09-02 as a provisional slice (see "Progress" above). Remaining: live fixtures, a named reviewer, the prove step wired into CI |
| 3 | Banking, telecom, healthcare, energy, pharma, customs, GDPR, and aerospace packs on public sources | Same tests per pack; each pack has a gold set | 2 to 4 days per pack |
| 4 | Bring-your-own-PDF path; manufacturing, insurance, legal, and device packs | Edition mismatch stops the build at the first sentence; matched edition builds identically | 1 to 2 weeks |
| 5 | Evaluation in section 9.2; paper revision with measured numbers | Every number in the paper has a script that produced it | 2 to 3 weeks, including annotation time |
| 6 | Two container images, command line, deployment guide, signed manifests | Runtime image has no model client; `verify` passes on a fresh machine | 1 week |

## 12. Decisions needed

1. The other research papers. Only one is in hand. Upload them or point to them, and say which are yours and which are third-party.
2. First industry for the vertical slice. FOIA is recommended for the reasons in section 8.5.
3. Licensing posture for the six copyrighted standards. Bring-your-own-PDF is recommended. An alternative is to obtain redistribution licenses, which is slower and costs money.
4. Whether the paper has a publication target. A venue changes how much of section 9.2 is required and when.
5. Whether the rewrite replaces the original or is published beside it. Beside is recommended, with the original's hash recorded, so the record of what was claimed on 2026-09-01 is not lost.
