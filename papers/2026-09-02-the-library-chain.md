# The Library Chain: Compiling a Regulated Procedure into a Cited Logic Base, with the Executor Contributing Nothing

Date: 2026-09-03. Draft 0.2. Supersedes draft 0.1 of 2026-09-02; the corrections are listed at the end.

## Abstract

This paper states a method that turns the published text of a regulated procedure into a base of first-order-logic facts, each fact cited to the exact bytes of the sentence it came from, and derives from that base a proof that the procedure's ordering claims are consistent, the order those claims force, and a digest that lets anyone rebuild the base and confirm it is the same. Every step is a call to a named, public library with a named input, a named output, and a certificate. The executor of the method, whether a person, a script, or any language model, contributes nothing: it selects no library, writes no rule, and authors no fact. One human step remains, and it rejects facts against their cited sentences; it never authors. The method has one learned component, a dependency parser with fixed weights, and everything above it is rule-based or symbolic. The paper reports the first instance, the Freedom of Information Act, with every number measured from a build that is committed beside the paper, and it states which steps of the method were executed on that instance and which were not.

## Claims

Claims 1 through 5 are measured on the first instance. Claim 6 is a property of the method's design and has one instance so far.

- Claim 1. Every executed step, from the source file to the sealed manifest, is a call to a named library or to a fixed table stated in this paper; the executor's contribution is zero.
- Claim 2. Every fact in the base cites a byte range of one source sentence, and a fact whose quote is not the byte-exact slice of its sentence cannot enter the base.
- Claim 3. Every step above the parse returns a certificate: a stable model, a satisfying assignment or an unsatisfiable core, a transitive reduction with a topological order, or a digest.
- Claim 4. Given the same source bytes, the same parser model, the same pinned library versions, and the same rejections, two independent processes produce a byte-identical manifest.
- Claim 5. The only human step rejects facts; it authors nothing, so the human cannot introduce a fact the source does not contain.
- Claim 6. The chain is invariant across industries. An industry is a set of sources with provenance and a table of rejections; nothing else varies.

## The chain in plain words

The procedure's text is read from its file, and every character keeps its position in that file. The text is parsed: each sentence becomes a tree that says which word depends on which. From each tree, the predicates and their arguments are extracted: who does what to whom. Each predicate and argument is written down as a fact of one of seven kinds, and every fact carries the exact words it came from. Two rules clean the facts: a pronoun is replaced by the noun it stands for when a rule can find it, and a subject that never acts on anything is moved from the "who does it" role to the "what it involves" role. The "before" facts are handed to a solver, which either proves that they can all be true at once or names the smallest group that cannot. The forced order is computed from the "before" facts, and every fact is sealed with a digest. A person then reads each flagged fact next to its quote and either leaves it or rejects it; the person writes nothing. That is the whole chain. The method continues past this point, to a rule base and a process model, and those steps are named below with their libraries; they were not executed on the first instance.

## Terminology

Literature terms are used in their established sense: dependency parse, Universal Dependencies, predicate-argument extraction, first-order logic, answer set programming, stable model, satisfiability modulo theories, difference logic, unsatisfiable core, transitive reduction, topological order.

Three terms are introduced here. The executor is whoever or whatever runs the chain; the method is written so that its identity does not matter. A certificate is the proof object a step returns, in the sense of the companion meta-model paper of 2026-08-26, which defines the substrate as a chain of data structure, algorithm, and certificate above a single abstraction step. The abstraction step is that paper's term for the one place where prose becomes structure; this paper mechanizes it with a parser, a rule-based extractor, and a fixed table, and no author.

## The executor-contribution-zero property

A step contributes nothing from the executor when its input is the output of the previous step or a source file with recorded provenance, its output is produced by a library call whose options are fixed in the pack or by a fixed table stated in the method, and its acceptance is decided by a certificate or a mechanical check rather than by the executor's judgment. When every step has this property, the chain is a function of its inputs, and any executor produces the same result. This is what makes the method independent of language models: a language model may run the chain, but the chain never asks it for a fact, a rule, a table entry, a choice of library, or a judgment.

## The chain per document

Every fact from step 5 onward carries the identifier of its source sentence, the identifiers of the tokens it was compiled from, and the byte-exact slice of the sentence spanning those tokens. The table gives the step, the library, the input, the output, the certificate or check, and whether the step was executed on the first instance.

| Step | Library | Input | Output | Certificate or check | First instance |
| --- | --- | --- | --- | --- | --- |
| 1 Read | Python's html.parser for a statute web page; pdfplumber for PDF; plain text | the source file | units of canonical text, each character mapped to its offset in the file; struck-through text dropped and counted | the source SHA-256; the drop count; the count of blocks skipped before the start marker | executed (html) |
| 2 Parse | ufal.udpipe, tokenizer option `ranges`, with a pinned Universal Dependencies model | each unit | CoNLL-U per sentence: each token with lemma, part of speech, head, relation, and character range | the model's SHA-256; every token range reproduces its form, or the build stops | executed |
| 3 Tables | pydantic types every row | the CoNLL-U | the token table, the citation index, and the parses, written in a fixed order | the files are a function of the parse | executed |
| 4 Extract | PredPatt, with its Universal Dependencies v2 relation table selected | each sentence's tokens | the predicates of the sentence and the arguments of each, as token positions | none; PredPatt is rule-based and its rules are published with it | executed |
| 5 Compile | the projection table of this paper, applied without exception | PredPatt's predicates and arguments; the dependency children of each predicate root | facts over seven predicates, each with sentence id, token ids, and quote | every quote is the byte-exact slice of its sentence spanning its tokens, or the build stops | executed |
| 6 Normalize | clingo through clorm, with the two rules of this paper; a deterministic pronoun rule | the facts | pronouns resolved where the rule finds an antecedent; inanimate subjects routed from agent to theme; a flag for every routing and every unresolved pronoun | the unique stable model | executed |
| 7 Adjudicate | a YAML table read by the chain | the flagged facts beside their quotes | the same facts minus the rejected ones | the table names the analyst and the reason per rejection | mechanism executed; no rejection recorded yet |
| 8 Precedence proof | z3-solver, difference logic, fixed seeds, resource limit | the precedes facts | satisfiable, or a minimal conflicting set | sat, or the unsatisfiable core minimized by deletion | executed |
| 9 Order | networkx | the precedes facts as a directed graph | the forced-precedence graph and the derivation order, or the cycle | the transitive reduction and the lexicographic topological order | executed |
| 10 Seal | hashlib over canonical JSON | every fact, its sentence digest, its quote digest; the pinned toolchain; the sources; the order | a digest per fact and one digest over the base | a rebuild reproduces the digest | executed |
| 11 Rule base | experta; z3-solver | the obligatory events with their agent, patient, and theme facts | the required document set per configuration; the maximal feasible configuration | the satisfying assignment | specified, not executed |
| 12 Process | pm4py | the forced-precedence graph; an event log when one exists | BPMN 2.0; fitness, precision, and per-case deviation by token replay and alignment | the alignment | specified, not executed |
| 13 Publish | openpyxl, xlsxwriter, python-docx, mermaid, quarto, streamlit, as selected | the certified tables | one spreadsheet per artifact, and the selected renderings | the output hashes | specified, not executed |

Step 2 pins the parser model by its SHA-256 and the library by version. Step 4 selects PredPatt's v2 relation table because the parser model emits Universal Dependencies v2 relation names; PredPatt's default is its v1 table, whose names for the object, the passive subject, and the oblique never occur in a v2 parse, so under the default PredPatt finds no objects at all. Step 8 fixes the solver's random seeds and uses a resource limit rather than a wall-clock timeout, because the solver's documentation describes wall-clock timeouts as non-deterministic. Step 10 writes every collection in sorted order.

The method also names a second route from a sentence to logic: amrlib parses the sentence to Abstract Meaning Representation, penman serializes the graph, and amr-logic-converter converts the graph to a first-order-logic formula. That route was not executed on the first instance because amrlib's parser model could not be retrieved from the build environment. amrlib, penman, and amr-logic-converter were installed and are not in the executed chain. The method names kuzu for the token tables and stanza for coreference; neither was executed, and the tables are files and the pronoun rule is the deterministic one below.

## The seven predicates and the projection table

The base uses seven predicates and no others. Each is produced from PredPatt's output and from the Universal Dependencies relations of the parse by the table below. The table is data of the method, stated once here, and it is applied by the compilation operator without exception. It is finite because the Universal Dependencies relation inventory is closed. No executor, human or model, decides an entry at run time.

| Predicate | Meaning | Produced from |
| --- | --- | --- |
| event(E, lemma) | something happens or is done | every PredPatt predicate; E is its root token, lemma is the parser's lemma for it |
| agent(E, X) | who does it | a PredPatt argument whose relation to the predicate is nsubj or csubj, or obl:agent |
| patient(E, X) | what it is done to | a PredPatt argument whose relation is obj, or nsubj:pass |
| theme(E, X) | what else it involves | a PredPatt argument whose relation is iobj, or obl whose case marker is not temporal |
| obligatory(E) | it must be done | the predicate root has an aux child with lemma shall or must |
| negated(E) | it is not the case | the predicate root has an advmod child with lemma not or never, or its subject has the determiner no |
| precedes(E1, E2) | E1 comes before E2 | an obl child of the predicate root whose case marker is after, following, upon, once, or since gives precedes(anchor, E); before, prior, until, or pending gives precedes(E, anchor); an advcl child that is itself a predicate root, with the same words as its mark, gives the same two readings |

A temporal anchor that is a noun, such as "the receipt", becomes an event so that precedes always relates two events, and it is not also written as a theme. Coordination, control, relative clauses, and embedded predicates are handled by PredPatt's published rules, not by this table.

## Normalization as two rules

Normalization is two answer-set rules run by clingo over the fact base, keyed by lemma. A subject is animate when it is the agent of some transitive event, an event that has a patient, anywhere in the corpus. An inanimate subject is routed from the agent role to the theme role, and every routing is flagged for the analyst.

```
animate(X) :- agent(E, X), patient(E, _).
theme(E, X) :- agent(E, X), not animate(X).
```

These two lines are the whole routing operator. They are data, not code; the executor does not write them.

The pronoun rule is deterministic and runs before routing: a pronoun argument is replaced by the nearest preceding noun argument of the same animacy in the same unit of text, where a pronoun's animacy is given by a closed list and a noun's by the routing above. A pronoun with no such antecedent keeps its place and is flagged.

## Certificates, and what each one does and does not establish

The parse returns no certificate, because its input is prose. Every step above it returns one or performs a mechanical check:

- The citation check of step 5 proves that every fact's quote is the byte-exact slice of its sentence. It does not prove that the fact means what the sentence means; that is the analyst's question.
- The stable model of step 6 proves that the two rules were applied exactly.
- Satisfiability at step 8 proves that every ordering claim in the corpus can be true at once. An unsatisfiable core names the facts that cannot.
- The transitive reduction at step 9 proves which orderings the sources force and which are implied by other forced orderings.
- The digest at step 10 proves that a rebuild produced the same base.

Nothing in the chain proves that the sources are complete or correct, and nothing in it corrects the parser. The chain proves that what was compiled is what the sources say, and it says where every fact came from.

## Determinism

The chain is deterministic under four conditions, all recorded in the pack: the source files by SHA-256, the parser model by SHA-256, the library versions by pin, and the rejections by content. The test is a double build. Two separate processes, under different hash seeds, compile the same pack and write the manifest of step 10. The two manifests must be byte-identical, and a third build must be identical to the manifest committed with the pack. On the first instance, the builds under hash seeds 1 and 424242 are byte-identical, the build under seed 7 is identical to the committed manifest, and the verify command rebuilds the pack and reproduces the committed digest.

Three places would break determinism in a careless implementation, and each is closed by a library setting rather than by executor discipline: the parser tokenizes with ranges so citations never depend on re-tokenization; the solver runs with fixed seeds and a resource limit; the manifest is canonical JSON with sorted keys. A fourth is closed by the manifest itself: the pinned toolchain, including the model's SHA-256, is part of the digest, so a change to any library or to the model is visible as a digest change.

## The human step

There is one human step, and it comes after step 6. The analyst reads a fact beside the sentence it cites and either leaves it or rejects it. A rejection is a row in a table with three fields: the fact identifier, the analyst's name, and the reason. The table is data; the chain reads it and removes the rejected facts before step 8. The analyst never authors a fact, never edits a fact, and never writes a rule. Any fact may be rejected, flagged or not.

Four classes of fact or sentence are flagged for the analyst by the chain itself: a sentence that produced no event; a sentence whose root is not a predicate, which is usually a heading or an enumerated fragment; a pronoun the rule could not resolve; and a subject routed to theme by the animacy rule, because the open-class boundary between a human collective and an object noun is not decided by the rule. When two analysts adjudicate the same facts, their agreement is measured with Cohen's kappa and their disagreements are recorded by fact identifier.

The audit of the whole chain is back-translation: an accepted fact is read against its sentence, and the sentence must say what the fact says.

## Deployment across industries

An industry pack is two things: a set of sources, each with its URL, edition, retrieval date, SHA-256, and license, and a rejections table. Nothing else varies. The chain, the predicates, the projection table, the two rules, and the certificates are the same for a statute, a standard, a contract, or an internal procedure. The companion document of 2026-09-01 describes twelve industries in these terms.

Two sources may govern one process, for example a statute and the agency's own regulation. Both are compiled; both are cited; the precedence proof of step 8 runs over the union. A conflicting set whose facts come from two sources is a variation point, recorded and kept. A conflicting set inside one source is a contradiction, and the build stops and names the facts.

A copyrighted standard cannot be redistributed. The seal of step 10 makes that unnecessary: the pack ships the digests, the token ranges, and the fact identifiers, and the deployer supplies their licensed copy. The chain reads the deployer's copy, recomputes the digests, and stops at the first sentence whose bytes differ from the edition the pack was built against. No sentence of the standard leaves the deployer's environment.

## The first instance, measured

The first instance is the Freedom of Information Act, 5 U.S.C. 552, in the copy published by the United States Department of Justice on FOIA.gov. Every number in this section was measured from the build committed in the pack beside this paper, and the build can be reproduced with the commands in the reproduction section.

### Source, model, and toolchain

| Item | Value |
| --- | --- |
| Source | 5 U.S.C. 552 as published on FOIA.gov; a work of the United States government, public domain in the United States and CC0 1.0 worldwide under the publisher's repository license |
| Retrieved | 2026-09-02, from the publisher's source repository usdoj/foia.gov at commit dc020ffc0b6eb7380f430f62c00557ff37a667cc |
| Source SHA-256 | 4b36841eab2a27fa746cfb338daf73668e14f781aaa6e61f5885b6c0b4512103 |
| Parser model | UDPipe model english-ewt-ud-2.5-191206, trained on the Universal Dependencies 2.5 English EWT treebank, published by the Institute of Formal and Applied Linguistics, Charles University, at LINDAT/CLARIAH-CZ handle 11234/1-3131; retrieved 2026-09-02 from the mirror maintained for the R udpipe package |
| Model SHA-256 | 784bd0fa85e3d831fd02a55290d0acfd05c953159dc38cc33d52e1b28add9957 |
| Model license | CC BY-NC-SA 4.0, non-commercial |
| ufal.udpipe | 1.4.0.1 (MPL-2.0) |
| predpatt | 1.0.1, installed from repository hltcoe/PredPatt at commit 34bc751656a0766c7ac233b077ea8511a8004876 (BSD 3-Clause) |
| clingo | 5.8.2 (MIT); clorm 1.6.3 (MIT) |
| z3-solver | 5.1.0.0 (MIT) |
| networkx | 3.6.1 (BSD-3-Clause per the package record). PredPatt declares a dependency, concrete, that requires networkx below 2.8; the chain never imports concrete, and the constraint is overridden at install time in `pyproject.toml` (`[tool.uv] override-dependencies`) |
| pydantic | 2.13.5 (MIT); pdfplumber 0.11.10 (MIT), installed and not exercised by an HTML source |
| Canonical text rule | version 1: NFC per character, every whitespace character to one space, runs collapsed, unit trimmed |

### Read and parse

| Measurement | Value |
| --- | --- |
| Blocks skipped before the first block starting with "§ 552." | 3 |
| Characters of struck-through, repealed text dropped | 3,732 |
| Units of canonical text | 237 |
| Characters of canonical text | 50,565 |
| Sentences | 327 |
| Tokens | 9,664 |
| Token ranges that failed to reproduce their form | 0 |

### Extraction and compilation

| Measurement | Value |
| --- | --- |
| Facts | 1,869 |
| event | 621 |
| agent | 283 |
| patient | 424 |
| theme | 373 |
| obligatory | 122 |
| negated | 34 |
| precedes | 12 |
| Sentences with at least one event | 233 of 327 |
| Facts whose quote failed the byte-exact check | 0 |

### Flags for the analyst

| Flag | Count |
| --- | --- |
| Sentence with no event | 94 |
| Sentence whose root is not a predicate | 71 |
| Pronoun with no antecedent found by the rule | 108 |
| Subject routed from agent to theme by the animacy rule | 73 |
| Total | 346 |
| Rejections recorded | 0; no analyst has adjudicated this instance |

The pronoun rule resolved 40 of the 148 pronoun arguments the compilation produced, and the other 108 are flagged. The flagged forms are "that" 36 times, "which" 35, "i" 26, "it" 6, "nothing" 2, "there" 2, and "whom" 1. The 26 occurrences of "i" are the statute's clause designator "(i)", which the parser tagged as a pronoun. Most of the rest are the relative pronouns "which" and "that", whose antecedent is the noun their clause modifies; the parse names that noun directly, and the rule stated in this paper does not yet read it. The animacy rule routed 73 subjects; the most frequent routed lemmas are "information", "schedule", "purpose", "example", "period", "report", "President", and "meeting". "President" is a person, and the rule routed it because the corpus never has the President as the agent of an event with a patient; that is the open-class boundary the human step exists for.

### Precedence

All 12 precedes facts are listed, because the reading of a case marker as temporal is the least certain entry in the projection table and the reader should see every instance. The quote is the byte-exact slice the fact cites; the statutory path is the designator of its unit.

| Path | Quote | Fact | Reading |
| --- | --- | --- | --- |
| (a)(3)(A) | upon any request for records which (i) reasonably describes such records and (ii) is made | precedes(request, made) | temporal "upon"; the parser attached the anchor to "is made", not to the agency's "shall make" |
| (a)(6)(A)(ii) | excepting Saturdays, Sundays, and legal public holidays) after the receipt | precedes(receipt, excepting) | temporal "after"; the parser attached the anchor to "excepting", not to "make a determination" |
| (a)(6)(C)(i) | Upon any determination by an agency to comply with a request for records, the records shall be made | precedes(determination, made) | temporal |
| (a)(6)(C)(iii) | arrange an alternative time frame for processing a request (or a modified request) under clause (ii) after being given | precedes(given, arrange) | temporal |
| (a)(6)(E)(iii) | based on the record before the agency | precedes(based, agency) | not temporal: "before the agency" names the forum |
| (e)(1) | On or before February 1 of each year, each agency shall submit | precedes(submit, February) | temporal |
| (e)(1)(B)(ii) | relies upon to authorize | precedes(authorize, relies) | not temporal: "relies upon" is a phrasal verb |
| (e)(1)(B)(ii) | relied upon, a description | precedes(description, relied) | not temporal: "relied upon" is a phrasal verb |
| (e)(1)(C) | pending before the agency | precedes(pending, agency) | not temporal: "before the agency" names the forum |
| (e)(1)(G) | elapsed since each request | precedes(request, elapsed) | temporal |
| (e)(1)(J) | elapsed since each request was originally received | precedes(received, elapsed) | temporal |
| (e)(1)(K) | elapsed since the requests were originally received | precedes(received, elapsed) | temporal |

The solver checked 12 constraints and found them satisfiable, with no conflicting set. The forced-precedence graph has 12 edges over 24 events, no edge implied by another, and no cycle. Four of the 12 facts read a non-temporal "before" or "upon" as temporal and are for the analyst to reject; no rule in the chain flags them, and the chain does not yet flag precedes facts at all. Deadlines such as "within 20 days" are not compiled: the table has no duration predicate, and "within" is not a temporal case marker in it.

### One sentence end to end

Unit (a)(6)(A)(i) reads: "(i) determine within 20 days (excepting Saturdays, Sundays, and legal public holidays) after the receipt of any such request whether to comply with such request and shall immediately notify the person making such a request of –". The chain compiled eight facts from it, each with its quote:

| Fact | Quote |
| --- | --- |
| event(determine) | determine |
| theme(determine, days) | determine within 20 days |
| patient(determine, Saturdays) | determine within 20 days (excepting Saturdays |
| obligatory(notify) | shall immediately notify |
| event(notify) | notify |
| patient(notify, person) | notify the person |
| event(make) | making |
| patient(make, request) | making such a request |

The third fact is wrong: the parser attached "Saturdays" as the object of "determine", and the projection table wrote what the parser gave it. The quote shows the analyst exactly that, and the rejection is one row. Two facts are missing: obligatory(determine) and agent(determine, agency), because the words "Each agency ... shall—" sit in the parent unit (a)(6)(A), which the statute writes as a separate list item and the reader keeps as a separate unit; that parent unit produced no event and is flagged. The phrase "after the receipt of any such request" produced no precedes fact in this unit, because the parser did not attach it to a predicate root. In unit (a)(3)(A), the parser lemmatized "stating" as "sta", and the event carries that lemma. These are the parser's errors, and the chain's answer to them is the flag and the quote, not a correction.

### Seal and tests

| Measurement | Value |
| --- | --- |
| Manifest digest | ff8b1bee4b54894437f2f31013ab3e450fe29c9c1f541f53b3fd8938f9d3fdda |
| Double build under hash seeds 1 and 424242 | byte-identical |
| Build under hash seed 7 against the committed manifest | identical |
| Verify command | rebuild reproduces the digest |
| Tests | 11, all passing |
| Modules loaded during a build from anthropic, openai, spacy, hypothesis, transformers, or torch | none |
| Static type check, strict | no issues in 15 source files |

The companion meta-model paper of 2026-08-26 reports an earlier instance of the same chain on a regulated client-onboarding procedure, with 17,217 source sentences and 103,187 atoms; those figures are that paper's and are not re-derived here.

## What the method names that the first instance did not run

| Library | Role in the method | Status on the first instance |
| --- | --- | --- |
| amrlib, penman, amr-logic-converter | the meaning-representation route to first-order logic | installed; amrlib's parser model could not be retrieved; not in the executed chain |
| typedlogic | writing facts and rules in typed form | installed; not in the executed chain |
| kuzu | the token table as a graph with Cypher queries | not installed; the tables are files |
| stanza | neural coreference | not installed; the deterministic pronoun rule stands |
| unified-planning | the partial-order plan | not installed; the forced order is networkx's transitive reduction |
| experta | the rule base | not installed |
| pm4py | the process model and conformance | not installed |
| docling, markitdown, ydata-profiling, dasel, jinja2, prefect, dagster, temporalio | Pipeline 0, the orchestrator compiler | not installed |

Pipeline 0, as the method specifies it, runs once per artifact folder and writes the orchestration that runs everything else: ingest with docling or markitdown, a census with ydata-profiling, schemas as dasel projections typed by pydantic, a capability model as clingo facts written by typedlogic and solved to a stable model, a task graph in networkx rendered by jinja2 to a prefect, dagster, or temporalio module, and self-load. None of it was executed on the first instance; the first instance was run by a command-line entry point that calls the steps in order.

## Limitations and open points

- The learned component is the parser. A parse error propagates into the facts; the instance above shows an object attached to the wrong verb, an anchor attached to the wrong verb, and a wrong lemma. The chain does not correct parses; it flags and quotes, and the analyst rejects.
- The pronoun rule resolved 40 of 148 pronoun arguments on this instance. The next rule to state is the relative-pronoun rule the parse supports directly: the antecedent of a pronoun that is the subject or object of a relative clause is the head that clause modifies.
- The animacy rule decides by verb selection alone, so "President" is routed to theme and a noun such as "information" that is ever the subject of a transitive verb would be kept as an agent.
- Four of the twelve precedes facts read a non-temporal "before" or "upon" as temporal, and precedes facts are not flagged. A flag for every precedes fact is the smallest correction.
- The statute writes one sentence across several list items. The reader keeps each item as a unit, so a verb loses the subject and the modal that sit in its parent item. A reader rule that joins a parent unit ending in a dash to its children is the candidate correction; it was not built.
- Deadlines are not compiled. A duration predicate is outside the seven.
- The parser model carries a non-commercial license. A commercial deployment needs a model under another license or a license from the publisher.
- The steps past the seal, the rule base and the process model, are specified with their libraries and certificates and have not been run on any instance in this pack.

## Reproduction

The pack, the model file, the build outputs, and the tests are committed beside this paper. From the repository root:

```
uv venv .venv
uv pip install -e ".[dev]"
.venv/bin/compiled-ai compile packs/foia
.venv/bin/compiled-ai verify packs/foia
.venv/bin/python -m pytest
.venv/bin/python -m mypy
```

The compile command writes the token table, the citation index, the parses, the facts, the flags, the reconciliation, the ordering, and the manifest into the pack's build directory. The verify command rebuilds and compares the digest.

## Corrections to draft 0.1

- Draft 0.1 said the facts were "projected onto seven predicates and written by typedlogic". The projection is the fixed table of this paper, applied by the compilation operator; typedlogic is installed and not in the executed chain.
- Draft 0.1 listed kuzu, amrlib, penman, amr-logic-converter, stanza, unified-planning, experta, and pm4py as the libraries of steps 3 through 9 without saying that none of them had been executed on the first instance. This draft says, per step and per library, what was executed.
- Draft 0.1 said the method has two learned components. The executed chain has one, the parser; PredPatt is rule-based.
- Between draft 0.1 and this draft, PredPatt was found to have been run under its Universal Dependencies v1 relation table against v2 parses, which produced no patient fact at all; the v2 table is now selected, and every number above is from the corrected build.

## References

Only works whose title and authors were confirmed against a publisher or author-published record are listed; each entry names the record. Software is cited by repository, version, and the record that names its license.

1. de Moura, Leonardo; Bjørner, Nikolaj. "Z3: An Efficient SMT Solver." Tools and Algorithms for the Construction and Analysis of Systems (TACAS 2008), Springer, 2008. DOI 10.1007/978-3-540-78800-3_24. Record: the Microsoft Research publication page.
2. Merigoux, Denis; Chataing, Nicolas; Protzenko, Jonathan. "Catala: A Programming Language for the Law." Proceedings of the ACM on Programming Languages 5(ICFP), Article 77, 2021. DOI 10.1145/3473582. Record: the Microsoft Research publication page and the authors' citation file.
3. Pennisi, Andrea; González Hernández, Elvira; Koivula, Nina. "NOMOS: Navigating Obligation Mining in Official Statutes." Proceedings of the Natural Legal Language Processing Workshop 2023, pp. 8–16. DOI 10.18653/v1/2023.nllp-1.2. Record: the ACL Anthology source record.
4. Holzenberger, Nils; Van Durme, Benjamin. "Connecting Symbolic Statutory Reasoning with Legal Information Extraction." Proceedings of the Natural Legal Language Processing Workshop 2023, pp. 113–131. DOI 10.18653/v1/2023.nllp-1.12. Record: the ACL Anthology source record.
5. Rashkin, Hannah; Nikolaev, Vitaly; Lamm, Matthew; Aroyo, Lora; Collins, Michael; Das, Dipanjan; Petrov, Slav; Tomar, Gaurav Singh; Turc, Iulia; Reitter, David. "Measuring Attribution in Natural Language Generation Models." Computational Linguistics 49(4): 777–840, 2023. DOI 10.1162/coli_a_00486. Record: the ACL Anthology source record.
6. Coupette, Corinna; Beckedorf, Janis; Hartung, Dirk; Bommarito, Michael; Katz, Daniel Martin. "Measuring Law Over Time: A Network Analytical Framework with an Application to Statutes and Regulations in the United States and Germany." Frontiers in Physics 9, 2021. DOI 10.3389/fphy.2021.658463. Record: the authors' organization repositories.
7. Dahl, Matthew; Magesh, Varun; Suzgun, Mirac; Ho, Daniel E. "Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models." Journal of Legal Analysis 16(1): 64–93, 2024. DOI 10.1093/jla/laae003. Record: the authors' repository citation.
8. Straka, Milan; Straková, Jana. "Tokenizing, POS Tagging, Lemmatizing and Parsing UD 2.0 with UDPipe." Proceedings of the CoNLL 2017 Shared Task: Multilingual Parsing from Raw Text to Universal Dependencies, Vancouver, 2017. Record: the Publications section of the README distributed with the Universal Dependencies 2.5 models for UDPipe.
9. Straka, Milan; Hajič, Jan; Straková, Jana. "UDPipe: Trainable Pipeline for Processing CoNLL-U Files Performing Tokenization, Morphological Analysis, POS Tagging and Parsing." Proceedings of the Tenth International Conference on Language Resources and Evaluation (LREC 2016), Portorož, 2016. Record: the same README.
10. White, Aaron Steven; Reisinger, Drew; Sakaguchi, Keisuke; Vieira, Tim; Zhang, Sheng; Rudinger, Rachel; Rawlins, Kyle; Van Durme, Benjamin. "Universal Decompositional Semantics on Universal Dependencies." Proceedings of EMNLP 2016. Record: the references file in the PredPatt repository at the pinned commit, which names this paper as the one PredPatt was used for.
11. PredPatt. Repository hltcoe/PredPatt, commit 34bc751656a0766c7ac233b077ea8511a8004876, version 1.0.1. License: BSD 3-Clause, Johns Hopkins University Human Language Technology Center of Excellence, 2017, per the repository's LICENSE file.
12. UDPipe. Repository ufal/udpipe; Python package ufal.udpipe 1.4.0.1. License: MPL-2.0 per the package record and the repository README, which also states that the models are CC BY-NC-SA 4.0.
13. Universal Dependencies 2.5 models for UDPipe. LINDAT/CLARIAH-CZ handle 11234/1-3131; mirror repository jwijffels/udpipe.models.ud.2.5. License: CC BY-NC-SA 4.0 per the mirror's LICENSE and README.
14. clingo 5.8.2 and clorm 1.6.3. Repositories potassco/clingo and potassco/clorm. License: MIT per the package records.
15. z3-solver 5.1.0.0. Repository Z3Prover/z3. License: MIT per the package record.
16. networkx 2.7.1. License: BSD per the package record. pydantic 2.13.5, pdfplumber 0.11.10: MIT per the package records.
17. 5 U.S.C. 552, FOIA.gov. Repository usdoj/foia.gov, commit dc020ffc0b6eb7380f430f62c00557ff37a667cc, file www.foia.gov/foia-statute.html. License: CC0 1.0 per the repository's LICENSE.md.

The companion documents are "The 150% Model of Product Line Engineering: A Reflexive Meta-Model of the Discipline," draft 0.2, 2026-08-26, and "Compiled AI, industry by industry," 2026-09-01.

## Glossary

- Abstract Meaning Representation: a graph of a sentence's meaning, with a node for each concept and labeled edges for who did what to whom; named by the method's second route, not used in the executed chain.
- Answer set programming: a way of writing rules so that a solver returns every set of facts consistent with them; that set is a stable model.
- Case marker: a preposition such as "after" or "before" that attaches to a noun in the dependency parse.
- Certificate: the proof object a step returns, which can be checked without re-running the step.
- Citation: the identifier of a sentence plus the token ids and the byte-exact quote within it that a fact came from.
- Dependency parse: a tree over a sentence's words that says which word depends on which and how; the "how" is a relation from a closed inventory.
- Difference logic: constraints of the form one time minus another time is at most a constant; the solver decides them quickly and exactly.
- Executor: whoever or whatever runs the chain.
- Fact: one statement in the logic base, such as obligatory(E) or precedes(E1, E2).
- Forced precedence: an ordering that some source clause states and that no other stated orderings already imply.
- Pack: an industry's sources, with provenance, and its rejections.
- PredPatt: a published, rule-based extractor of predicates and their arguments from a dependency parse.
- Rejection: an analyst's decision that a fact does not say what its sentence says.
- Seal: the digests that let anyone rebuild the base and confirm it is the same.
- Stable model: the set of facts a solver returns as consistent with a set of rules.
- Universal Dependencies: the shared inventory of parts of speech and relations that the parser's output uses.
- Unsatisfiable core: the smallest group of constraints the solver can point to that cannot all be true.
