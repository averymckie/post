# The Library Chain: Compiling Regulated Procedures into a Certified Logic Base with No Executor Contribution

Date: 2026-09-02. Draft 0.1.

## Abstract

This paper states a method that turns the published procedures of a regulated process into a base of first-order-logic facts, each fact cited to the exact bytes of the sentence it came from, and derives the order of the process, its rule base, and its process model from that base. Every step of the method is a call to a named, public library with a named input, a named output, and a certificate. The executor of the method, whether a person, a script, or any language model, contributes nothing: it selects no library, writes no logic, and authors no fact. One human step remains, and it rejects candidates against their cited sentences; it never authors. The method has two learned components, both parsers with fixed weights, and everything above them is symbolic and certified. The same chain applies to any industry; only the sources and the rejections change. The paper states the chain, the seven predicates, the certificates, the determinism procedure, the human step, the deployment model, the first instance, and the open points. Every number in the paper is either a property of the method or a measurement from a step that was actually run, and the paper says which.

## Thesis statement and claims

The thesis is that a regulated procedure can be compiled by libraries alone, and that the compilation can be certified at every step above the parse.

- Claim 1. Every step from source text to process model is a call to a named library with a named input and a named output, so the executor's contribution is zero.
- Claim 2. Every fact in the logic base is cited to a byte range of one source sentence, and a fact whose citation does not match the source bytes cannot enter the base.
- Claim 3. Every step above the parse returns a certificate: a satisfying assignment, a stable model, a plan, an alignment, or a digest, and a step that returns no certificate is not admitted.
- Claim 4. Given the same sources, the same pinned library versions, the same parser model hashes, and the same rejections, two independent executions produce byte-identical outputs.
- Claim 5. The only human step rejects candidates; it authors nothing, so the human cannot introduce a fact the source does not contain.
- Claim 6. The chain is invariant across industries; an industry is a set of sources with provenance and a set of rejections.

## Terminology

Literature terms are used in their established sense: dependency parse, Universal Dependencies, Abstract Meaning Representation, first-order logic, answer set programming, satisfiability modulo theories, difference logic, unsatisfiable core, partial-order plan, transitive reduction, token replay, alignment, stable model.

Three terms are introduced here. The executor is whoever or whatever runs the chain; the method is written so that its identity does not matter. A certificate is the proof object a step returns, in the sense of the companion meta-model paper of 2026-08-26, which defines the substrate as a chain of data structure, algorithm, and certificate above a single abstraction step. The abstraction step is that paper's term for the one place where prose becomes structure, and this paper mechanizes it with two parsers and no author.

## The executor-contribution-zero property

A step contributes nothing from the executor when its input is the output of the previous step or a source file with recorded provenance, its output is produced by a library call whose options are fixed in the pack, and its acceptance is decided by a certificate rather than by the executor's judgment. When every step has this property, the chain is a function of its inputs, and any executor produces the same result. This property is what makes the method independent of language models: a language model may run the chain, but the chain never asks it for a fact, a rule, a schema, a choice of library, or a judgment.

## Pipeline 0: the orchestrator compiler

Pipeline 0 runs once per artifact folder and writes the orchestration that runs everything else. No flow, schedule, or retry policy exists before it.

| Step | Library | Input | Output | Certificate |
| --- | --- | --- | --- | --- |
| 0 Ingest | docling, markitdown, undoc, firecrawl-anydoc for documents; python-calamine, fastexcel, csvkit for workbooks | the raw artifact folder | Markdown, JSON, and CSV per artifact, no schema declared | file hashes |
| 1 Census | ydata-profiling, sweetviz, dataprep for tables; dasel for JSON, YAML, XML; pymupdf, pypdf for PDF fingerprints | the ingested files | one machine-readable manifest | the manifest hash |
| 2 Schema | dasel projections typed by pydantic; datamodel-code-generator instantiates the models | the manifest | the only schemas the run may use | schema validation |
| 3 Capability logic | typedlogic writes clingo facts from the manifest; clingo solves | file classes, entities, units, time columns, clause markers | the unique stable model: required libraries, banned libraries, legal handoff edges | the stable model |
| 4 Graph | networkx and graphable build the task graph; jinja2 renders it | the stable model | a prefect flow, dagster asset definitions, or a temporalio workflow module, with retries, result persistence, and compensation on solver unsat | the rendered source and its hash |
| 5 Self-load | the chosen orchestrator | the rendered source | a registered, running flow | the orchestrator's run record |

## The chain per document

The chain runs inside the flow Pipeline 0 wrote. Every fact from step 3 onward carries the identifier of its source sentence and the character range of the tokens it came from. The table gives the step, the library, the input, the output, and the certificate. The text after the table gives what each step needs pinned.

| Step | Library | Input | Output | Certificate |
| --- | --- | --- | --- | --- |
| 1 Read | docling or markitdown; pymupdf for PDF; Python's html.parser for a statute web page | the source file | every sentence with its character offsets in the file; struck-through text dropped and counted | the source hash and the drop count |
| 2 Parse | ufal.udpipe with the Universal Dependencies model for the language, tokenizer option `ranges` | each unit of text | CoNLL-U per sentence; each token with lemma, part of speech, head, relation, and character range | the model hash; every token range reproduces its form |
| 3 Tables | pydantic types the rows; kuzu stores token nodes and dependency edges; Cypher queries | the CoNLL-U | the token table, the citation index, and every later extraction table keyed by sentence id | row counts and the table hashes |
| 4 Logic | amrlib parses each sentence to Abstract Meaning Representation; penman serializes the graph; amr-logic-converter converts the graph to a first-order-logic formula; typedlogic writes the facts; clorm holds the fact base | each sentence | facts over seven predicates, each with sentence id and token range | every fact's citation matches the source bytes |
| 5 Normalize | stanza's coreference processor; clingo over the fact base with two rules | the facts | pronouns resolved to antecedents; inanimate subjects routed from agent to theme | the stable model |
| 6 Precedence proof | z3-solver | the precedes facts | satisfiable, or a minimal conflicting set | sat, or the unsatisfiable core |
| 7 Order | unified-planning | events as actions with their cited precedes facts as preconditions | the partial-order plan, which is the forced-precedence graph | the plan |
| 8 Rule base | experta; z3-solver | the obligatory events with their agent, patient, and theme facts | the required document set per configuration; the maximal feasible configuration | the satisfying assignment |
| 9 Process | pm4py | the partial-order plan; an event log when one exists | BPMN 2.0; fitness, precision, and per-case deviation by token replay and alignment | the alignment |
| 10 Seal | hashlib | every fact and its sentence bytes; the pinned toolchain | a digest per fact and one digest over the base, as canonical JSON with sorted keys | a rebuild reproduces the digest |
| 11 Publish | openpyxl, xlsxwriter, pandas-xlsx-tables; python-docx, mermaid, quarto, streamlit as Pipeline 0 selected | the certified tables | one spreadsheet per artifact, and the selected renderings | the output hashes |

Step 2 pins the parser model by its SHA-256 and the library by version. Step 4 pins the AMR parser model the same way. Step 6 fixes the solver's random seeds and uses a resource limit rather than a wall-clock timeout, because the solver's documentation describes wall-clock timeouts as non-deterministic. Step 10 writes every collection in sorted order.

## The seven predicates and where each comes from

The logic base uses seven predicates and no others. The table gives the predicate, its meaning in plain words, the Universal Dependencies relation that produces it, and the Abstract Meaning Representation role that produces it. The two sources agree by construction on ordinary sentences; where they disagree, both facts are candidates and the analyst rejects one.

| Predicate | Meaning | From the dependency parse | From the meaning representation |
| --- | --- | --- | --- |
| event(E, lemma) | something happens or is done | a verb, or a root predicate with an auxiliary or copula | a concept with a PropBank frame |
| agent(E, X) | who does it | nsubj; obl:agent in a passive | ARG0 |
| patient(E, X) | what it is done to | obj; nsubj:pass in a passive | ARG1 |
| theme(E, X) | what else it involves | obl, iobj | ARG2 and later arguments |
| obligatory(E) | it must be done | the auxiliary shall or must | the obligate-01 frame |
| negated(E) | it is not the case | not or never on the event; no on its subject | polarity minus |
| precedes(E1, E2) | E1 comes before E2 | after, following, upon, once, since as case or mark give precedes(anchor, E); before, prior to, until give precedes(E, anchor) | a time role with the before or after concept |

A temporal anchor that is a noun, such as "the receipt", becomes an event so that precedes always relates two events. A verb coordinated with another and lacking its own subject inherits that subject. A control complement inherits the subject of its matrix verb.

## Normalization as two rules

Normalization is two answer-set rules run by clingo over the fact base, after stanza has resolved pronouns to their antecedents. A subject is animate when it is the agent of some transitive event anywhere in the corpus. An inanimate subject is routed from the agent role to the theme role.

```
animate(X) :- agent(E, X), patient(E, _).
theme(E, X) :- agent(E, X), not animate(X).
```

These two lines are the whole normalization operator. They are data, not code, and the executor does not write them; they are part of the method.

## Certificates, and what each one does and does not establish

A certificate is a proof object over a formal input. The parse returns none, because its input is prose. Every step above it returns one:

- The stable model of step 3 in Pipeline 0 proves that the selected libraries and handoff edges satisfy the capability rules.
- The citation check of step 4 proves that every fact's bytes are in the source. It does not prove that the fact means what the sentence means; that is the analyst's question.
- The stable model of step 5 proves that the routing rules were applied exactly.
- Satisfiability at step 6 proves that every ordering claim in the corpus can be true at once. An unsatisfiable core names the sentences that cannot.
- The partial-order plan at step 7 proves which orderings the sources force and which are only presentational.
- The satisfying assignment at step 8 proves that the rule base admits a configuration and names the maximal one.
- The alignment at step 9 measures conformance of an observed log to the normative model; it is a measurement, not a proof.
- The digest at step 10 proves that a rebuild produced the same base.

Nothing in the chain proves that the sources are complete or correct. The chain proves that what was compiled is what the sources say, and it says where every fact came from.

## Determinism

The chain is deterministic under four conditions, all recorded in the pack: the source files by hash, the parser models by hash, the library versions by pin, and the rejections by content. The test is a double build. Two separate processes, under different hash seeds, compile the same pack and write the manifest of step 10. The two manifests must be byte-identical, and each must be identical to the manifest committed with the pack. A difference of one byte fails the build and names the first fact that differs.

Three places would break determinism in a careless implementation, and each is closed by a library setting rather than by executor discipline: the parser tokenizes with ranges so citations never depend on re-tokenization; the solver runs with fixed seeds and a resource limit; the manifest is canonical JSON with sorted keys.

## The human step

There is one human step, and it comes after step 4. The analyst reads each candidate fact beside the sentence it cites and either leaves it or rejects it. A rejection is a row in a table with three fields: the fact identifier, the analyst's name, and the reason. The table is data; the chain reads it and removes the rejected facts before step 6. The analyst never authors a fact, never edits a fact, and never writes a rule.

Three classes of candidate are flagged for the analyst by the chain itself: a sentence that produced no event; a sentence whose root is not a predicate, which is usually a heading fragment; and a subject routed to theme by the animacy rule, because the open-class boundary between a human collective and an object noun is not decided by the rules. When two analysts adjudicate the same candidates, their agreement is measured with Cohen's kappa and their disagreements are recorded by fact identifier.

The audit of the whole chain is back-translation: an accepted fact is read against its sentence, and the sentence must say what the fact says.

## Deployment across industries

An industry pack is two things: a set of sources, each with its URL, edition, retrieval date, hash, and license, and a rejections table. Nothing else varies. The chain, the predicates, the normalization rules, and the certificates are the same for a statute, a standard, a contract, or an internal procedure. The companion document of 2026-09-01 describes twelve industries in these terms.

Two sources may govern one process, for example a statute and the agency's own regulation. Both are compiled; both are cited; the precedence proof of step 6 runs over the union. A conflicting set whose facts come from two sources is a variation point, recorded and kept. A conflicting set inside one source is a contradiction, and the build stops and names the sentences.

A copyrighted standard cannot be redistributed. The seal of step 10 makes that unnecessary: the pack ships the digests, the token ranges, and the facts' identifiers, and the deployer supplies their licensed copy. The chain reads the deployer's copy, recomputes the digests, and stops at the first sentence whose bytes differ from the edition the pack was built against. No sentence of the standard leaves the deployer's environment.

## The first instance

The first instance is the Freedom of Information Act, 5 U.S.C. 552, in the copy published by the United States Department of Justice on FOIA.gov. The source is a work of the United States government, public domain in the United States and CC0 worldwide under the publisher's repository license. It was retrieved on 2026-09-02 from the publisher's source repository at commit dc020ffc0b6eb7380f430f62c00557ff37a667cc, and its SHA-256 is 4b36841eab2a27fa746cfb338daf73668e14f781aaa6e61f5885b6c0b4512103.

The parser model is the English EWT model of Universal Dependencies 2.5 for UDPipe, from the LINDAT/CLARIAH-CZ repository at handle 11234/1-3131, retrieved on 2026-09-02 from a mirror maintained for the R udpipe package. Its SHA-256 is 784bd0fa85e3d831fd02a55290d0acfd05c953159dc38cc33d52e1b28add9957. Its license is CC BY-NC-SA 4.0, which does not permit commercial use; a commercial deployment needs a model under another license or a license from the publisher.

Steps 1 and 2 have been executed on this source with the named libraries. The read produced 237 units of text and dropped 3,732 characters of struck-through repealed language, counted and recorded. The parse produced 327 sentences, and every token's character range reproduces its form. Steps 3 through 11 are specified in this paper and have not yet been executed with the named libraries on this source; no number is reported for them here.

The companion meta-model paper of 2026-08-26 reports an earlier instance of the same chain on a regulated client-onboarding procedure, with 17,217 source sentences and 103,187 atoms; those figures are that paper's and are not re-derived here.

## Limitations and open points

- The two learned components are parsers with fixed weights. A parse error propagates into the facts. The chain does not correct parses; it flags candidates and the analyst rejects.
- The dependency parser and the meaning-representation parser can disagree on a sentence. Both facts are candidates; the method does not yet state a rule for choosing, and the analyst decides.
- The animacy rule decides by verb selection alone, so a noun such as "notification" that is the subject of a transitive verb is marked animate until an analyst rejects it.
- The parser model in the first instance carries a non-commercial license.
- The rule base of step 8 is the least specified step of the chain: the mapping from obligatory events with their arguments to rule-engine facts is stated here, and the certificate is stated, but no instance has run it.
- The conformance measurement of step 9 requires an event log, which most sources do not come with.

## References

Only works whose title and authors were confirmed against a publisher or author-published record are listed; each entry names the record.

1. de Moura, Leonardo; Bjørner, Nikolaj. "Z3: An Efficient SMT Solver." Tools and Algorithms for the Construction and Analysis of Systems (TACAS 2008), Springer, 2008. DOI 10.1007/978-3-540-78800-3_24. Record: the Microsoft Research publication page.
2. Merigoux, Denis; Chataing, Nicolas; Protzenko, Jonathan. "Catala: A Programming Language for the Law." Proceedings of the ACM on Programming Languages 5(ICFP), Article 77, 2021. DOI 10.1145/3473582. Record: the Microsoft Research publication page and the authors' citation file.
3. Pennisi, Andrea; González Hernández, Elvira; Koivula, Nina. "NOMOS: Navigating Obligation Mining in Official Statutes." Proceedings of the Natural Legal Language Processing Workshop 2023, pp. 8–16. DOI 10.18653/v1/2023.nllp-1.2. Record: the ACL Anthology source record.
4. Holzenberger, Nils; Van Durme, Benjamin. "Connecting Symbolic Statutory Reasoning with Legal Information Extraction." Proceedings of the Natural Legal Language Processing Workshop 2023, pp. 113–131. DOI 10.18653/v1/2023.nllp-1.12. Record: the ACL Anthology source record.
5. Rashkin, Hannah; Nikolaev, Vitaly; Lamm, Matthew; Aroyo, Lora; Collins, Michael; Das, Dipanjan; Petrov, Slav; Tomar, Gaurav Singh; Turc, Iulia; Reitter, David. "Measuring Attribution in Natural Language Generation Models." Computational Linguistics 49(4): 777–840, 2023. DOI 10.1162/coli_a_00486. Record: the ACL Anthology source record.
6. Coupette, Corinna; Beckedorf, Janis; Hartung, Dirk; Bommarito, Michael; Katz, Daniel Martin. "Measuring Law Over Time: A Network Analytical Framework with an Application to Statutes and Regulations in the United States and Germany." Frontiers in Physics 9, 2021. DOI 10.3389/fphy.2021.658463. Record: the authors' organization repositories.
7. Dahl, Matthew; Magesh, Varun; Suzgun, Mirac; Ho, Daniel E. "Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models." Journal of Legal Analysis 16(1): 64–93, 2024. DOI 10.1093/jla/laae003. Record: the authors' repository citation.

The companion documents are "The 150% Model of Product Line Engineering: A Reflexive Meta-Model of the Discipline," draft 0.2, 2026-08-26, and "Compiled AI, industry by industry," 2026-09-01.

## Glossary

- Abstract Meaning Representation: a graph of a sentence's meaning, with a node for each concept and labeled edges for who did what to whom.
- Answer set programming: a way of writing rules so that a solver returns every set of facts consistent with them; that set is a stable model.
- Certificate: the proof object a step returns, which can be checked without re-running the step.
- Citation: the identifier of a sentence plus the character range within it that a fact came from.
- Dependency parse: a tree over a sentence's words that says which word depends on which and how.
- Difference logic: constraints of the form one time minus another time is at most a constant; the solver decides them quickly and exactly.
- Executor: whoever or whatever runs the chain.
- Fact: one statement in the logic base, such as obligatory(E) or precedes(E1, E2).
- Forced precedence: an ordering that some source clause states, as opposed to one that merely appears in the order the text was written.
- Pack: an industry's sources, with provenance, and its rejections.
- Rejection: an analyst's decision that a candidate fact does not say what its sentence says.
- Seal: the digests that let anyone rebuild the base and confirm it is the same.
- Stable model: the set of facts a solver returns as consistent with a set of rules.
- Unsatisfiable core: the smallest group of constraints the solver can point to that cannot all be true.
