# Deterministic Function Chains: A Reference Architecture for Semantic Translation and Auditable Execution

**Operationalizing the STRIDE Paradigm via Pinned Syntax Graphs, Answer Set Programming, and SMT Solvers**

---

## Executive Summary

Enterprise adoption of artificial intelligence stands at an impasse known as the Trust Ceiling: the operational barrier imposed by statistical error rates, latent representations, and hallucinations inherent to autoregressive language models. In legal compliance, financial reporting, corporate governance, and safety-critical engineering, probabilistic outputs cannot substitute for verifiable guarantees. Current mitigation strategies, particularly agentic loops that grant large language models access to external tools, fail to resolve this fundamental weakness. The probabilistic model remains the unconstrained decision-maker, compounding error rates across sequential execution steps.

This paper presents the Function Chain, an open-source reference architecture and implementation of the STRIDE framework (Semantic Translation into Deterministic Execution) formulated by William Tunstall-Pedoe. Rather than attempting to suppress hallucinations through model fine-tuning or prompt engineering, the architecture enforces a strict structural separation: the generative model is excluded from computation, deduction, and artifact generation.

Linguistic models and statistical parsers are restricted to the perceptual perimeter, where unstructured documents are translated into canonical dependency graphs. Once this structured representation is established, execution transfers entirely to deterministic, version-pinned software: grammatical dependency rules, Answer Set Programming solvers, Satisfiability Modulo Theories engines, and discrete business-calendar clocks. Every derived fact maintains byte-exact pointers back to the original source text. 

While natural language parsing at the perimeter remains subject to syntactic ambiguity, the Function Chain isolates these ambiguities into an explicit review gate before computation occurs. Once a parse is certified, downstream execution is mathematically deterministic. This paper presents the complete 13-line reference pipeline, documents an end-to-end statutory compliance execution under the Freedom of Information Act (5 U.S.C. § 552), transparently defines the four-tier implementation taxonomy across its 92-pipeline catalog, and provides a direct rebuttal to common architectural criticisms.

---

## 1. The Crisis of Trust: Why Agentic AI Fails High-Liability Operations

### 1.1 The Statistical Barrier of Autoregressive Models

Modern large language models operate as autoregressive estimators. They model the conditional probability distribution of a token sequence:

$$P(x_t \mid x_1, x_2, \dots, x_{t-1})$$

Their objective function rewards statistical plausibility across a vast training distribution, optimizing for high-dimensional textual continuation. When an autoregressive model encounters an ambiguous prompt, an edge case in tax law, or an intricate temporal constraint, it samples the most probable textual completion. What industry literature terms "hallucination" is the ordinary operation of an unconstrained statistical predictor operating over linguistic manifolds.

In enterprise operations, system failure is governed by tail risk. An accuracy rate of 98% on standard benchmarks leaves a 2% failure rate distributed unpredictably across production workloads. A system may summarize fifty pages of technical documentation with high fidelity, yet miscalculate a statutory filing deadline by a single day or invert an exclusionary clause in a commercial lease. Because failure points cannot be anticipated or bounded, human operators are forced to audit every line of output, negating the economic value of automation.

### 1.2 Compounded Failure in Agentic Chains

The predominant industry response to hallucination has been agentic orchestration, wherein a central language model is provided with external APIs, database connectors, and calculators.

```
Agentic Architecture (Compounded Probability):
[User Query] ──► [LLM Tool Selection (Step 1)]
                        │
                        ▼
                 [Deterministic API Call]
                        │
                        ▼
                 [LLM Output Synthesis (Step 2)] ──► [Compounded Uncertainty]
```

This pattern preserves the underlying trust problem because the probabilistic model remains in control of the execution path:

1. The model decides when and which tool to invoke based on heuristic pattern matching.
2. The model generates query parameters and payloads, introducing syntax and semantic errors.
3. The model receives the deterministic result and summarizes it into natural language prose, re-introducing hallucination over valid data.

When each decision in an agentic workflow carries an individual reliability of $p = 0.95$, a five-step chain yields an aggregate reliability of:

$$P(\text{Success}) = (0.95)^5 \approx 0.774 \quad (77.4\%)$$

Chaining probabilistic decisions compounds uncertainty. As the operational sequence lengthens, overall system reliability rapidly degrades.

---

## 2. The STRIDE Foundation: Separating Perception from Execution

To build trustworthy autonomous systems, systems engineering must abandon the attempt to turn statistical predictors into verifiable guarantors. In July 2026, William Tunstall-Pedoe (UnlikelyAI) formulated the STRIDE architecture (Semantic Translation into Deterministic Execution) to formalize this boundary.

```
                         THE STRIDE PARADIGM
                         
       THE PERCEPTUAL EDGE                THE DETERMINISTIC CORE
 ┌─────────────────────────────┐      ┌─────────────────────────────┐
 │    Unstructured Reality     │      │      Semantic Artifact      │
 │  (Statutes, Leases, Scans,  │ ───► │  (Dependency Trees, Logics, │
 │      Workbooks, Audio)      │      │      Typed Constraint Sets) │
 └─────────────────────────────┘      └─────────────────────────────┘
                │                                    │
    Linguistic Parsing at the Edge                   ▼
      [Executed once at rest;         ┌─────────────────────────────┐
       amortized over lifecycle]      │    Deterministic Solvers    │
                                      │   (Z3 SMT, Clingo ASP,      │
                                      │    Business-Day Clocks)     │
                                      └─────────────────────────────┘
                                                     │
                                                     ▼
                                      ┌─────────────────────────────┐
                                      │     Certified Output        │
                                      │   (Executable Decisions,    │
                                      │    Verified Spreadsheets)   │
                                      └─────────────────────────────┘
```

STRIDE establishes three foundational principles:

1. **Neural Perception at the Edge:** Neural networks and statistical parsers operate solely at the input boundary, translating unstructured human text, PDFs, and layout elements into structured, typed semantic representations.
2. **Deterministic Processing at the Core:** Once text is compiled into a formal semantic artifact, neural models are removed from the pipeline. Logic, temporal arithmetic, planning, and rendering are executed exclusively by deterministic algorithms and mathematical solvers.
3. **Economic Amortization of Review:** Translating an authoritative document (such as a statute, an insurance policy, or a standard operating procedure) occurs once at rest. Because governing text is static relative to runtime queries, engineering effort can be concentrated on verifying the parsed representation a single time. Once certified, the semantic artifact executes runtime queries with zero operational drift.

The Function Chain serves as an open-source reference implementation of these principles.

---

## 3. The 13-Line Processing Chain: Specification and Implementation Taxonomy

The central operational invariant of the Function Chain is:

$$\text{Runtime Answer} \notin \text{Domain}(\text{Generative Model})$$

The generative model is never asked to calculate a date, evaluate an eligibility constraint, or draft an authoritative finding. The answer is computed by an explicit chain of version-pinned software functions operating on validated inputs.

### 3.1 Verification Taxonomy

To maintain engineering rigor, every library call in the architecture is categorized according to four explicit implementation states:

- **Wired:** The core build toolchain calls this function in the continuous integration environment.
- **Exercised:** The function was resolved in the installed environment at its pinned version and executed on source text or representative test structures.
- **Located:** The function was resolved by import path validation against installed packages via automated test suites (`tests/test_function_chain.py`).
- **Catalog Blueprint:** A formal specification of interface contracts and library bindings establishing the architectural path for a given operational domain.

```
[Line 0: Source Integrity] ───────► SHA-256 Digest Matching
           │
[Line 1: Document Ingestion] ─────► Structural AST (docling / lxml)
           │
[Line 2: Canonical Normalization] ► Unicode NFC & Byte Indexing
           │
[Line 3: Grammatical Parsing] ────► CoNLL-U Graphs (ufal.udpipe 1.4.0.1)
           │
[Line 4: Relational Indexing] ────► Graph Query Tables (kuzu 0.11.3)
           │
[Line 5: Predicate Extraction] ───► UD v2 Graph Rewrite Rules (predpatt 1.0.1)
           │
[Line 6: Logic Compilation] ──────► ASP and FOL Compilation (clingo 5.8.2)
           │
[Line 7: Temporal Anchoring] ─────► TIMEX3 and Calendar Math (numpy.busday)
           │
[Line 8: Animacy Normalization] ──► Explicit Role Routing (clorm 1.6.3)
           │
[Line 9: Adjudication Gate] ──────► Human Discrepancy Logging & Cohen's Kappa
           │
[Line 10: SMT Precedence Proof] ──► Z3 SMT Solver 5.1.0 & Unsat Cores
           │
[Line 11: Topological Ordering] ──► Transitive Reduction (networkx 3.6.1)
           │
[Line 12: Cryptographic Sealing] ─► Manifest Digest Generation (hashlib)
```

### 3.2 Step-by-Step Functional Mechanics

#### Line 0: Source Integrity and Pinning
Raw document bytes are hashed using SHA-256 and matched against a pre-registered digest in `sources.yaml`. If the file changes by a single byte, execution halts immediately. *(Status: Wired).*

#### Line 1: Structural Parsing
The source document is parsed into an explicit hierarchy:
* **Statutory XML (USLM):** Parsed with `lxml.etree` (v6.1.3), isolating statutory paths (such as `/us/usc/t5/s552/a/6/A/ii`) and distinguishing headings from clauses. *(Status: Exercised on USLM structural fragments).*
* **HTML and Office Documents:** Parsed with `docling` (v2.124.0), yielding structured `DoclingDocument` items containing layout bounding boxes, character spans, and structural parent-child groups. *(Status: Wired and Exercised on Department of Justice statutory web sources).*

#### Line 2: Text Normalization and Character Mapping
Text is normalized to Unicode NFC via `unicodedata.normalize`. An exact bidirectional index maps every normalized character offset directly back to raw file byte spans. *(Status: Wired).*

#### Line 3: Dependency Parsing under Frozen Weights
Normalized sentences pass to `ufal.udpipe` (v1.4.0.1), executing the pre-trained Universal Dependencies 2.5 model (`english-ewt-ud-2.5-191206.udpipe`, SHA-256: `784bd0fa85e3d831fd02a55290d0acfd05c953159dc38cc33d52e1b28add9957`).

The parser assigns part-of-speech tags, head pointers, and dependency labels to each token, producing a CoNLL-U graph. Because model weights are frozen, this transformation is functionally deterministic: identical input yields an identical syntax tree on every execution. *(Status: Wired).*

#### Line 4: Relational Graph Storage
The parsed CoNLL-U graph is validated against strict schemas (`pydantic` v2.13.5) and ingested into an embedded analytical graph database (`kuzu` v0.11.3). Grammatical structures are queried via Cypher without calling language models:

```cypher
MATCH (action:Tok)-[:Head]->(object:Tok)
WHERE action.deprel = 'obj'
RETURN action.lemma, object.lemma
```

*(Status: Exercised; returned `[['make', 'determination']]`).*

#### Line 5: Semantic Predicate-Argument Extraction
The dependency graph is evaluated by `predpatt` (v1.0.1) configured for Universal Dependencies v2 (`dep_v2.VERSION`). PredPatt executes formal graph rewriting algorithms to extract verbal roots, subject arguments (`nsubj`), direct objects (`obj`), and oblique modifiers (`obl`). Every extracted predicate records the specific rewrite rule that produced it. *(Status: Wired with standard resolvers; Exercised with advanced coreference resolvers).*

#### Line 6: Logic Compilation into Answer Set Programming
Predicates are compiled into formal logic via `typedlogic` (v0.2.4) and `clingo` (v5.8.2). The system generates explicit facts:

```prolog
event(E, L)     :- pred(E, L).
agent(E, X)     :- arg(E, X, "nsubj").
agent(E, X)     :- arg(E, X, "csubj").
agent(E, X)     :- arg(E, X, "obl:agent").
patient(E, X)   :- arg(E, X, "obj").
patient(E, X)   :- arg(E, X, "nsubj:pass").
theme(E, X)     :- arg(E, X, "iobj").
theme(E, X)     :- arg(E, X, "obl"), not anchor(X).
obligatory(E)   :- pred(E, _), child(E, C, "aux", W), obligation(W).
precedes(X, E)  :- pred(E, _), child(E, X, "obl", _), child(X, C, "case", W), after(W), anchor(X).

obligation("shall"). obligation("must").
after("after").      after("upon").
```

Every compiled logic atom maintains an exact byte pointer back to the underlying source sentence:

$$\text{sentence.text}[lo:hi] == \text{quote}$$

*(Status: Exercised on core projection rules; production build utilizes Python relational module `fol.py`).*

#### Line 7: Temporal Anchoring and Business Calendars
Temporal expressions are extracted deterministically:
* `timexy` (v0.1.3) tags durations and normalizes them into ISO 8601 / TIMEX3 formats (for example, `"twenty days"` resolves to `DURATION value="P20D"`).
* Working-day calendars are instantiated using `holidays` (v0.103) and `numpy` (v2.3.5). When a rule excludes weekends and legal public holidays, the pipeline instantiates the official schedule (`numpy.busdaycalendar`). Deadlines are evaluated algebraically via discrete integer offsets. *(Status: Exercised).*

#### Line 8: Animacy and Role Disambiguation
Syntactic edge cases, such as passive voice constructions and inanimate grammatical subjects, are handled via explicit Answer Set rules:

```prolog
animate(X) :- agent(E, X), patient(E, _).
theme(E, X) :- agent(E, X), not animate(X).
```

*(Status: Wired via `clorm` 1.6.3).*

#### Line 9: The Adjudication Gate
This step constitutes the critical human-in-the-loop review boundary. When the parser encounters ambiguous syntax, low attachment confidence, or multiple parse interpretations, the extraction is flagged in `rejections.yaml`. Human analysts adjudicate disputed structures, with agreement quantified via Cohen's Kappa ($\kappa$) using `statsmodels` (v0.15.0). Disputed extractions are filtered out before reaching downstream solvers. *(Status: Wired for rejection filtering; Exercised for multi-rater agreement scoring).*

#### Line 10: SMT Precedence Proofs
Temporal constraints are converted to integer difference logic and evaluated by the Z3 Satisfiability Modulo Theories solver (`z3-solver` v5.1.0.0):

$$t_{E_2} - t_{E_1} \ge 1$$

Z3 executes with fixed random seeds and strict resource limits (`rlimit`). If contradictory constraints exist, Z3 halts and isolates the minimal unsatisfiable core (`unsat_core`), identifying the precise conflicting clauses. *(Status: Wired).*

#### Line 11: Topological Ordering
Satisfiable execution paths are structured into directed graphs via `networkx` (v3.6.1). Redundant dependencies are stripped via transitive reduction:

$$G_{\text{reduced}} = \text{transitive\_reduction}(G)$$

A deterministic topological sort (`lexicographical_topological_sort`) establishes the required execution order. *(Status: Wired).*

#### Line 12: Cryptographic Manifest Sealing
The extracted facts, source sentence hash, byte offsets, parser model version, and solver outputs are serialized into a canonical JSON representation. A SHA-256 digest is computed over this record:

$$\text{ManifestSeal} = \text{SHA-256}(\text{CanonicalRecord})$$

This manifest digest cryptographically binds the output record to the specific source document and toolchain configuration that produced it. *(Status: Wired).*

---

## 4. Concrete Implementation: Statutory Compliance under 5 U.S.C. § 552 (FOIA)

To demonstrate the architecture in a real legal compliance workflow, consider the statutory mandate governing administrative agency determinations under the Freedom of Information Act (5 U.S.C. § 552(a)(6)(A)(ii)):

> "(ii) make a determination with respect to any appeal within twenty days (excepting Saturdays, Sundays, and legal public holidays) after the receipt of such appeal."

### 4.1 The Failure Mode of Generative Models
When an LLM is prompted to compute this statutory deadline for an appeal received on Thursday, September 3, 2026, it attempts to generate the date via statistical token prediction:
* It frequently overlooks that Monday, September 7, 2026 is Labor Day, an official federal public holiday under 5 U.S.C. § 6103.
* It routinely calculates twenty calendar days rather than twenty business days, or mishandles weekend boundaries.
* It outputs incorrect deadlines (such as September 23, 2026 or October 1, 2026) while producing plausible-sounding explanations for its arithmetic.

### 4.2 The Function Chain Execution Trace

The reference implementation executes this determination through the concrete function chain recorded below:

```
Raw Statute: 5 U.S.C. § 552(a)(6)(A)(ii)
Source File: packs/foia/source.html (DOJ Statute Page)
  │
  ▼ [Line 1: docling 2.124.0]
Docling Document Item: #/texts/77 -> ListGroup #/groups/22 -> #/groups/23
Extracted Text: "(ii) make a determination with respect to any appeal within twenty days 
(excepting Saturdays, Sundays, and legal public holidays) after the receipt of such appeal."
  │
  ▼ [Line 3: ufal.udpipe 1.4.0.1 (Model: english-ewt-ud-2.5-191206.udpipe)]
CoNLL-U Tokens (32 tokens total):
  token 1:  "("             TokenRange=0:1
  token 2:  "ii"            TokenRange=1:3
  token 3:  ")"             TokenRange=3:4
  token 4:  "make"          lemma="make"          upos="VERB" deprel="root"    TokenRange=5:9
  token 6:  "determination" lemma="determination" upos="NOUN" deprel="obj"     TokenRange=12:25
  token 8:  "respect"       lemma="respect"       upos="NOUN" deprel="obl"     TokenRange=31:38
  token 14: "days"          lemma="day"           upos="NOUN" deprel="obl"     TokenRange=66:70
  token 16: "excepting"     lemma="except"        upos="VERB" deprel="advcl"   TokenRange=72:81
  token 28: "receipt"       lemma="receipt"       upos="NOUN" deprel="obl"     TokenRange=139:146
  │
  ▼ [Line 5: predpatt 1.0.1 (ud="2.0")]
Extracted Predicate Structure:
  Predicate: "make ?a with ?b within ?c"
  Rule Trace: [make-root, add_root(make/3)_for_advcl_from_(excepting/15),
               add_root(make/3)_for_obj_from_(determination/5),
               add_root(make/3)_for_obl_from_(days/13),
               add_root(make/3)_for_obl_from_(respect/7)]
  Arguments:
    ?a (obj): "determination"
    ?b (obl): "respect" [case="with"]
    ?c (obl): "days" [nummod="twenty", case="within"]
  │
  ▼ [Line 6: typedlogic 0.2.4 -> clingo 5.8.2 / fol.py]
Derived Logical Atoms:
  event("e1", "make").
  patient("e1", "determination").
  timex_span("e1", "twenty days").
  event("e2", "receipt").
  precedes("e2", "e1").
  │
  ▼ [Line 7: timexy 0.1.3 + numpy.busdaycalendar]
Base Date Parameter: 2026-09-03 (Thursday)
Extracted Duration: TIMEX3 type="DURATION" value="P20D"
Calendar Engine: numpy.busdaycalendar(holidays=holidays.country_holidays("US", years=[2026]))
Active Excluded Holiday: 2026-09-07 (Labor Day, 5 U.S.C. § 6103)
Offset Computation: numpy.busday_offset('2026-09-03', 20, roll='forward', busdaycal=cal)
Computed Statutory Deadline: 2026-10-02 (Friday)
  │
  ▼ [Line 10: z3-solver 5.1.0.0]
Precedence Assertion: (Int("e2") - Int("e1") <= -1) -> Check SAT -> Satisfiable
  │
  ▼ [Line 12: hashlib.sha256]
Certified Output Manifest:
  {
    "statute": "5 U.S.C. 552(a)(6)(A)(ii)",
    "action": "make_determination",
    "receipt_date": "2026-09-03",
    "due_date": "2026-10-02",
    "working_days": 20,
    "holidays_excluded": ["2026-09-07"],
    "citation_byte_span": [5, 158],
    "provenance": {
      "parser_model_sha256": "784bd0fa85e3d831fd02a55290d0acfd05c953159dc38cc33d52e1b28add9957",
      "clingo_version": "5.8.2",
      "z3_version": "5.1.0.0"
    },
    "manifest_digest": "4a18e26db47587842db20b925b42d72ebf49e49a941e17d686150ef75a7c2937"
  }
```

The computed deadline (Friday, October 2, 2026) is the algebraic result of counting twenty non-holiday weekdays forward from September 3, 2026, accounting for Labor Day on September 7. The generative model is absent from the arithmetic.

---

## 5. Direct Rebuttal: Confronting the Critic's Allegations

To evaluate the Function Chain objectively, engineering claims must be separated from common misinterpretations. This section addresses the key technical objections raised against the system.

### 5.1 Allegation 1: The Claim of Eliminating Hallucination Is Overstated
The critic argues that because the dependency parser (`ufal.udpipe`) and predicate extractor (`predpatt`) rely on statistical heuristics, the system does not eradicate hallucination.

**The Engineering Reality:**
The distinction lies in the architectural boundary between compile-time translation and runtime execution.
* In an agentic large language model architecture, hallucination occurs silently at runtime inside the latent space of every user query. It is unobservable, unbounded, and unpredictable.
* In the Function Chain, parsing is conducted upfront at rest. Natural language syntax is converted into a structured graph where errors manifest as explicit structural anomalies (such as invalid dependency relations or ungrounded arguments).
* Downstream solvers (Clingo, Z3, NumPy) possess zero generative capacity. Once facts are established, they cannot invent a date, invert a logic constraint, or create a fact.
* Therefore, the Function Chain eliminates runtime generative hallucination by removing the generative model from the answer generation path. Syntactic parsing ambiguities at the edge are isolated into the Line 9 review gate (`rejections.yaml`) before computation occurs.

### 5.2 Allegation 2: The 92 Pipelines Are a Smoke-Tested Catalog Rather Than Industrial Deployments
The critic notes that the 92 pipelines in the technical catalog consist of 46 forward and 46 reverse templates, and that many steps execute basic verification functions (such as writing a test workbook or checking satisfiability) rather than operating as live factory implementations.

**The Engineering Reality:**
This observation is correct regarding operational deployment and is fully acknowledged. The 92 pipelines are formal architectural specifications, interface contracts, and library call-graph bindings. 
* They define the exact deterministic libraries required to replace probabilistic text generation across 46 business disciplines.
* The test suite `tests/test_function_chain.py` dynamically resolves and imports every dotted path across the entire inventory, verifying that all public interfaces exist and are callable in the environment.
* The FOIA statutory compliance pack (P0) serves as the primary end-to-end reference implementation. The remaining pipelines establish the formal blueprints and verified interface bindings for expanding the architecture into adjacent domains.

### 5.3 Allegation 3: Handcrafted Glue Rules Mean the System Is Not an Autonomous Compiler
The critic points out that the rule mapping `"P20D"` and the preposition `"after"` to `numpy.busday_offset` was authored by human engineers, meaning the system did not autonomously discover the legal meaning of the statute.

**The Engineering Reality:**
Authoring compilation rules is the intended core of the STRIDE methodology. 
* In high-liability operations, an automated system must never improvise legal interpretations dynamically at runtime.
* Legal scholars, compliance officers, and systems engineers formalize statutory interpretations, projection axioms, and calendar schedules **once at rest**.
* Once these rules are registered in the repository, runtime execution across millions of transactions is completely automated, deterministic, and auditable. Conflating upfront rule formalization with runtime human intervention misunderstands the compiler model.

### 5.4 Allegation 4: Byte-Span Provenance Does Not Prove Legal Truth
The critic notes that validating token byte offsets (`sentence.text[lo:hi] == quote`) proves string containment, not that the statutory interpretation is correct.

**The Engineering Reality:**
This is an accurate distinction. Byte-span verification guarantees provenance and attribution: it proves that every extracted fact originates from a specific set of characters in the source text, preventing silent fabrication. It does not certify that the underlying statute is free from legal ambiguity. Evaluating substantive legal intent is precisely why the Line 9 adjudication gate is retained. Provenance guarantees that every asserted claim is checkable against its cited sentence.

### 5.5 Allegation 5: Hash Conflation in Provenance Records
The critic observed that an earlier draft conflated the parser model hash with the execution manifest digest.

**The Engineering Reality:**
This was an accuracy error in earlier documentation and has been corrected. The architecture maintains a strict separation between cryptographic components:
1. **Source Document Digest:** SHA-256 of the raw source file (`sources.yaml`).
2. **Parser Model Fingerprint:** SHA-256 of the frozen UDPipe model (`784bd0fa85e3d831fd02a55290d0acfd05c953159dc38cc33d52e1b28add9957`).
3. **Execution Manifest Digest:** SHA-256 of the canonical output JSON containing facts, dates, byte spans, and solver status (`4a18e26db47587842db20b925b42d72ebf49e49a941e17d686150ef75a7c2937`).

### 5.6 Allegation 6: Attribution of STRIDE and the Trust Ceiling
The critic noted that the conceptual framing of the Trust Ceiling and STRIDE originates from William Tunstall-Pedoe, whereas the essay previously blurred this lineage.

**The Engineering Reality:**
The conceptual foundation of STRIDE belongs entirely to William Tunstall-Pedoe and UnlikelyAI. This paper presents the Function Chain as an open-source reference architecture and implementation testing those principles using standard, version-pinned Python scientific libraries. The citation and intellectual debt are explicitly recognized.

---

## 6. Symmetric Verification: The Invert Compiler Pattern (Pipeline R0)

In high-liability enterprise environments, auditability requires bidirectional verifiability: when an automated compiler generates an operational spreadsheet or dashboard from rules, an independent verification process must prove that the generated artifact conforms to the original rules.

The Function Chain implements this pattern through Pipeline R0:

```
                         THE INVERT COMPILER (R0)
                         
   FORWARD PIPELINE                                       REVERSE PIPELINE (R0)
  ┌─────────────────┐                                    ┌──────────────────────┐
  │ Source Document │                                    │  Rendered Dashboard, │
  │ (Statute/Policy)│                                    │  Slide Deck, or PDF  │
  └─────────────────┘                                    └──────────────────────┘
           │                                                         │
           ▼ [Forward Chain]                                         ▼ [Playwright / Docling]
  ┌─────────────────┐                                    ┌──────────────────────┐
  │ Solved Decision │                                    │ Flattened DOM / Text │
  │    Artifact     │                                    │   & Ingested Specs   │
  └─────────────────┘                                    └──────────────────────┘
           │                                                         │
           ▼                                                         ▼ [Z3 / Clingo]
  ┌─────────────────┐       EXACT RECONSTRUCTION CHECK   ┌──────────────────────┐
  │ Certified Table │ ◄────────────────────────────────► │ Decompiled Ledger /  │
  │    (Output)     │         (Hash & Schema Match)      │ Constraint Model     │
  └─────────────────┘                                    └──────────────────────┘
```

1. **Structured Ingestion:** Pipeline R0 utilizes headless browser automation (`playwright` v1.62.0) and document parsers (`python-docx`, `python-pptx`, `pymupdf`) to extract rendered tables and visual layouts from published artifacts.
2. **Schema Reconstruction:** Extracted tables are flattened and parsed into typed `pydantic` models via `dpath`.
3. **Consistency Checking:** Extracted constraints are recompiled into Answer Set rules and verified against forward models using Z3. Any discrepancy is identified down to the individual cell or field using structural diff tools (`daff` v1.4.2 and `csv-diff` v1.2).

Pipeline R0 serves as an automated structural regression suite, ensuring that operational databases and spreadsheets remain mathematically aligned with the governing specifications.

---

## 7. The 92-Pipeline Domain Inventory and Verification Status

The catalog below summarizes the primary forward and reverse pipeline pairs defined in the reference implementation, indicating their core libraries and implementation statuses:

| Pipeline ID | Operational Domain | Ingestion Toolchain | Logic & Solving Engine | Terminal Output Asset | Verification Status |
|:---|:---|:---|:---|:---|:---|
| **P0 / R0** | Orchestrator Compiler | `docling`, `markitdown`, `calamine` | `typedlogic`, `clingo`, `networkx` | Dynamic Prefect/Dagster Flows | **Wired & Exercised** |
| **P1 / R1** | Quality Engineering | `docling`, `undoc`, `fmdtools` | `pysmt`, `lifelines`, `scipy` | FMEA Simulation & Weibull Fits | Located & Smoke-Tested |
| **P2 / R2** | Financial Dashboarding | `firecrawl-anydoc`, `stanza` | `clingo` (ASP), `zen-engine` | Double-Entry Verified Ledgers | Located & Smoke-Tested |
| **P3 / R3** | Architecture Documentation | `undoc`, `prefect`, `nltk` | `networkx`, `clingo`, `z3-solver` | C4 Dependency & Acyclicity Models | Located & Smoke-Tested |
| **P5 / R5** | Process Mining Control | `markitdown`, `docling`, `duckdb`| `pm4py`, `simpn`, `clingo` | Petri Nets & Bottleneck Graphs | Located & Smoke-Tested |
| **P6 / R6** | Causal Policy Evaluation | `docling`, `stanza`, `dowhy` | `pgmpy`, `z3-solver`, `statsmodels` | Causal DAGs & Adjustment Sets | Located & Smoke-Tested |
| **P7 / R7** | Supply Chain Scheduling | `calamine`, `pulp`, `pyomo` | `ortools` (CP-SAT), `highspy` | Critical Path Gantt Workbooks | Located & Smoke-Tested |
| **P8 / R8** | Geospatial Cartography | `geopandas`, `shapely`, `osmnx` | `cpmpy`, `python-constraint2` | Proved Spatial Exclusion Maps | Located & Smoke-Tested |
| **P9 / R9** | Contract Constraint Prover | `docling`, `pypdf`, `amrlib` | `cvc5`, `pysmt`, `pycasbin` | Proved Deontic Access Policies | Located & Smoke-Tested |
| **P10 / R10**| Spec-to-Slide Compiler | `mammoth`, `markitdown`, `pptx` | `networkx`, `business-rules`, `z3` | Verified Slide Decks & DAGs | Located & Smoke-Tested |
| **P11 / R11**| Fleet Reliability Dossier | `csvkit`, `anydoc`, `lifelines` | `scipy.optimize`, `z3-solver` | Parametric Survival Curves | Located & Smoke-Tested |
| **P12 / R12**| Ontology Reasoner | `rdflib`, `owlready2` | `owlrl`, `clingo`, `cvc5` | Deductive ABox/TBox Knowledge | Located & Smoke-Tested |
| **P13 / R13**| Configuration Management | `docling`, `duckdb`, `networkx` | `clingo`, `z3-solver`, `pm4py` | Proved Acyclic CI Graphs | Located & Smoke-Tested |
| **P16 / R16**| Enterprise Architecture | `pyArchimate`, `owlready2` | `rustworkx`, `criticalpath`, `z3` | ArchiMate Models & Roadmaps | Located & Smoke-Tested |
| **P23 / R23**| Enterprise Risk Management | `docling`, `pgmpy`, `pymc` | `ortools`, `z3-solver`, `arviz` | Bayesian Risk Nets & Bounds | Located & Smoke-Tested |
| **P26 / R26**| Information Security (ISMS) | `docling`, `pypdf`, `owlready2` | `openfga-sdk`, `pycasbin`, `z3` | Conflict-Free Access Matrices | Located & Smoke-Tested |
| **P39 / R39**| Change Enablement | `firecrawl-anydoc`, `simpy` | `business-rules`, `clingo`, `pm4py` | Proved Change Windows & Replays | Located & Smoke-Tested |

---

## 8. Economic and Operational Implications for Enterprise Adoption

The transition from probabilistic agentic architectures to deterministic function chains fundamentally alters the unit economics of enterprise AI deployment.

### 8.1 Amortized Verification versus Continuous Auditing
In standard language model deployments, every user query carries statistical risk, requiring continuous manual review or exposing the enterprise to systemic tail liability.
* **Continuous Auditing Cost:** If an enterprise processes 50,000 regulatory compliance determinations annually using an agentic LLM with a 98% accuracy rate, human reviewers must audit all 50,000 outputs to locate the 1,000 unpredictable failures.
* **Amortized Verification:** Under the Function Chain, engineering and legal review are concentrated upfront during the compilation of the statutory rule artifact. Once certified and sealed with a cryptographic manifest digest, the rule executes 50,000 times with zero drift and zero variance. The cost of verification is paid once at rest, rather than on every query.

### 8.2 Air-Gapped and Zero-Data-Leakage Deployment
Because the core computation relies exclusively on local symbolic engines (Clingo, Z3, NumPy, NetworkX), the Function Chain executes entirely within air-gapped, sovereign infrastructure:
* No runtime API calls to commercial language model providers are required.
* Corporate intellectual property, proprietary financial ledgers, and confidential legal queries are never transmitted outside the enterprise boundary.
* Version-pinned wheels and local virtual environments ensure that system execution remains completely reproducible across years of operational service.

---

## 9. Conclusion: A Pragmatic Path to Trustworthy Automation

Scaling neural parameters will not alter the fundamental mathematical nature of autoregressive next-token prediction. Unconstrained statistical models will remain approximation engines, permanently bounded by the Trust Ceiling in high-liability environments.

The solution is to stop asking language models to compute answers.

By operationalizing the STRIDE paradigm, the Function Chain establishes an effective division of labor:
1. Statistical models and dependency parsers operate at the perimeter, translating unstructured human language into explicit, inspectable syntax graphs.
2. Deterministic mathematical solvers, formal logic engines, and calendar libraries govern computation at the core.
3. Every derived fact carries byte-level citations to source text, and all syntactic ambiguities are isolated into an upfront review gate before execution occurs.

This architecture shifts artificial intelligence from an untrustworthy, unconstrained oracle into an auditable, verifiable compiler of human rules.

---

## References

1. Tunstall-Pedoe, W. (2026). *The Trust Ceiling: The invisible limit on what AI is allowed to do.* UnlikelyAI Technical Essays.
2. Tunstall-Pedoe, W. (2026). *Breaking Through AI's Trust Ceiling: How trustworthy AI can actually be delivered.* UnlikelyAI Technical Essays.
3. Barrett, C., & Tinelli, C. (2018). Satisfiability Modulo Theories. In *Handbook of Model Checking* (pp. 305-343). Springer.
4. Gebser, M., Kaminski, R., Kaufmann, B., & Schaub, T. (2012). *Answer Set Solving in Practice.* Synthesis Lectures on Artificial Intelligence and Machine Learning, Morgan & Claypool.
5. de Marneffe, M. C., Manning, C. D., Nivre, J., & Zeman, D. (2021). Universal Dependencies. *Computational Linguistics*, 47(2), 255-308.
6. van der Aalst, W. M. P. (2016). *Process Mining: Data Science in Action.* Springer-Verlag Berlin Heidelberg.