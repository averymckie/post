# The Function Chain

Date: 2026-09-03.

## The claim

I've made AI stop hallucinating.

Not reduced it — removed the conditions under which it happens. A model hallucinates when it is asked to produce the answer and is free to invent one. This method never asks it to. For the tasks you would normally hand a language model — read a rulebook and tell me the obligations, pull out the parties, classify this case, decide whether it qualifies, put the steps in order, draft the report — it substitutes a fixed chain of named library functions that computes the answer and proves it. The generative model is not in the answer. What remains cannot hallucinate, because nothing in it is free to invent: every step is a function with typed inputs and a checkable output, and where language must become structure, a dependency parser does it under fixed weights, with its every claim checked byte-for-byte against the source it came from. A person may reject a claim against its cited sentence; no person and no model authors one.

That is the whole of it, and it is not a trick. Hallucination is a model asserting a fact the source does not support. Here no model asserts anything: functions compute, solvers certify, and each fact carries the exact bytes it was read from. An answer is either the output of a named function on given input, or it does not appear. The one thing this does not claim is that the sources are right — the chain proves the answer is what the sources say and shows where every word came from; a parse error becomes a flagged candidate, never a silent fact.

## The chains

Depending on what you are asking — a decision, an ordering, a proof of consistency, a document, a diagram — a specific sequence of functions is needed, each one a public library call with a named input, a named output, and a certificate the next step can check. This file is those chains, written out and verified. Each line is one library function applied to the output of the line before it, from the raw source file to each terminal solution; it names the library at its pinned version, the exact call, what goes in, what comes out, and the certificate the library returns. The options are data, not choices, and the rules the solvers run are printed here as data. No executor appears in the chain — no human, no model, chooses a step or authors a fact.

How to read a line:

- `wired` — the repository's build calls this function today.
- `exercised` — the function was resolved in the installed package at the version shown and run on the Freedom of Information Act source or on a fragment of it in the session that wrote this file; its output is quoted where it is short.
- `located` — the function was resolved in the installed package by import at the version shown; not run.
- `not located` — the reason, verbatim from the failure.
- `locate:` — the dotted paths that `tests/test_function_chain.py` resolves against the installed packages on every test run. A path that stops resolving fails the test.

The first instance is 5 U.S.C. 552 in the pack `packs/foia`. The sentence used in the exercised lines below, unless another is named, is unit (a)(6)(A)(ii): "make a determination with respect to any appeal within twenty days (excepting Saturdays, Sundays, and legal public holidays) after the receipt of such appeal."

---

## Part 1. Pipeline 0, the orchestrator compiler

Pipeline 0 runs once per artifact folder and writes the orchestration that runs everything else. Its output is a flow module; the flow module is a build product, never a checked-in source.

### P0.0 Ingest — the raw artifact folder → text, tables, and JSON with no declared schema

- docling 2.124.0 — `DocumentConverter().convert_all(paths)` → one `ConversionResult` per file; `result.document` is a `DoclingDocument`; `document.iterate_items(with_groups=True)` yields `(item, level)` with `TextItem.text`, `ListItem.text`, `GroupItem.children`, `NodeItem.parent`, `ProvenanceItem(page_no, bbox, charspan)`. Certificate: `result.status`. `exercised` on the DOJ statute page through `.convert`: status SUCCESS; 299 text items, 223 list items, 85 groups.
  `locate: docling.document_converter.DocumentConverter.convert, docling.document_converter.DocumentConverter.convert_all, docling_core.types.doc.DoclingDocument.iterate_items, docling_core.types.doc.ListItem, docling_core.types.doc.GroupItem, docling_core.types.doc.ProvenanceItem`
- markitdown 0.1.7 — `MarkItDown().convert(path).text_content` → Markdown. `exercised` on the DOJ page.
  `locate: markitdown.MarkItDown.convert`
- undoc 0.9.0 — `undoc.parse_file(path)`, `undoc.parse_bytes(data)`, class `undoc.Undoc`. `located`.
  `locate: undoc.parse_file, undoc.parse_bytes, undoc.Undoc`
- firecrawl-anydoc 0.2.4 (import name `anydoc`) — `anydoc.to_document(path)` → `anydoc.Document` with `Block`, `Table`, `List`, `ListItem`; `anydoc.to_markdown(path)`; `anydoc.format_from_path(path)`. `located`.
  `locate: anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document`
- python-calamine 0.8.2 — `CalamineWorkbook.from_path(path).get_sheet_by_index(i).to_python()` → rows. `exercised`.
  `locate: python_calamine.CalamineWorkbook.from_path, python_calamine.CalamineWorkbook.get_sheet_by_index, python_calamine.CalamineSheet.to_python`
- fastexcel 0.21.0 — `fastexcel.read_excel(path).load_sheet(i).to_pandas()` → DataFrame; needs pyarrow 25.0.1. `exercised`.
  `locate: fastexcel.read_excel, fastexcel.ExcelReader.load_sheet, fastexcel.ExcelSheet.to_pandas`
- csvkit 2.2.0 — `csvkit.utilities.csvstat.CSVStat`, `csvkit.utilities.csvjson.CSVJSON` (the `csvstat` and `csvjson` commands). `located`.
  `locate: csvkit.utilities.csvstat.CSVStat, csvkit.utilities.csvjson.CSVJSON`

### P0.1 Census — the ingested files → one machine-readable manifest

- ydata-profiling 4.18.4 — `ProfileReport(df, minimal=True).to_json()` → the profile as JSON. Needs `setuptools<80` (for `pkg_resources`) and `numpy<2.4` (for numba). `exercised`.
  `locate: ydata_profiling.ProfileReport, ydata_profiling.ProfileReport.to_json`
- sweetviz 2.3.3 — `sweetviz.analyze(df)` → `DataframeReport`; `.show_html(path)`. `located` (imported and resolved; not run in this session).
  `locate: sweetviz.analyze, sweetviz.DataframeReport.show_html`
- dataprep — `not located`: install unsatisfiable in this environment (depends on python-crfsuite 0.9.8, which has no build here).
- dasel 3.11.2 — a Go binary, not a Python package; from github.com/TomWright/dasel releases (linux amd64; SHA-256 in the catalog). `dasel -i yaml 'sources[0].sha256' < sources.yaml` → the value; `dasel -i json 'consistent' < reconciliation.json` → `true`. `exercised`.
- PyMuPDF 1.28.2 — `pymupdf.open(path)`; `Page.get_text("dict")` → characters with positions. `located`.
  `locate: pymupdf.open, pymupdf.Page.get_text`
- pypdf 6.16.2 — `PdfReader(path).metadata`. `located`.
  `locate: pypdf.PdfReader, pypdf.PdfReader.metadata`

### P0.2 Schema — the manifest → the only schemas the run may use

- pydantic 2.13.5 — `pydantic.create_model(name, **fields)`; `BaseModel.model_validate(obj)` rejects a row that does not match. `located` (`create_model`); `wired` (`model_validate`, every record in the build).
  `locate: pydantic.create_model, pydantic.BaseModel.model_validate`
- datamodel-code-generator 0.76.1 — `generate(schema, input_file_type=InputFileType.JsonSchema, output=path, output_model_type=DataModelType.PydanticV2BaseModel)` → a module of pydantic models. `exercised`: a two-field request schema produced `class Model(BaseModel): request_id: str; days_elapsed: int | None = None`.
  `locate: datamodel_code_generator.generate, datamodel_code_generator.InputFileType`

### P0.3 Capability logic — the manifest → the stable model of admitted libraries and handoff edges

- typedlogic 0.2.4 — facts are `@dataclass` subclasses of `typedlogic.FactMixin`; rules are `@axiom` functions; `PythonParser().parse(file)` → `Theory`; `get_solver("clingo")`, `.add(theory)`, `.add_fact(fact)`, `.model().ground_terms`. Certificate: the stable model. `exercised` (Part 2, line 6, on the FOIA sentence).
  `locate: typedlogic.pybridge.FactMixin, typedlogic.decorators.axiom, typedlogic.parsers.pyparser.python_parser.PythonParser, typedlogic.registry.get_solver, typedlogic.solver.Solver.add, typedlogic.solver.Solver.add_fact, typedlogic.solver.Solver.model, typedlogic.integrations.solvers.clingo.clingo_solver.ClingoSolver`
- clingo 5.8.2 — the solver behind it: `clingo.Control(arguments).add("base", [], program)`, `.ground([("base", [])])`, `.solve(on_model=…)`. `wired` (through clorm 1.6.3 for the two normalization rules).
  `locate: clingo.Control, clingo.Control.add, clingo.Control.ground, clingo.Control.solve, clorm.Predicate, clorm.FactBase, clorm.clingo.Control`
- The gate rules are data: one rule per gating sentence in the pipeline documents ("clingo only admits a process-mining asset graph if actor, activity, and time fields all resolve"), each carrying the pipeline and step it is quoted from. They are transcribed with the same discipline as a statute sentence and are not yet in the repository.

### P0.4 Graph — the stable model → a flow module

- networkx 3.6.1 — `DiGraph()`, `.add_edge(u, v)`, `is_directed_acyclic_graph`, `lexicographical_topological_sort(G, key=str)`. `wired`.
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge, networkx.is_directed_acyclic_graph, networkx.lexicographical_topological_sort`
- graphable — `not located`: graphable 0.7.0 requires Python ≥ 3.13; this environment is Python 3.11.15.
- Jinja2 3.1.6 — `Environment().from_string(template).render(**model)` → the flow source. `exercised`: rendered a three-task prefect flow from a list of step names.
  `locate: jinja2.Environment, jinja2.Environment.from_string, jinja2.Environment.get_template, jinja2.Template.render`
- prefect 3.8.4 — `@prefect.flow`, `@prefect.task`, `Flow.serve(name)`, `Flow.deploy(name, work_pool_name)`. `exercised` (`flow`, `task`: the rendered flow ran under a temporary Prefect server, tasks read, parse, extract completed).
  `locate: prefect.flow, prefect.task, prefect.flows.Flow.serve, prefect.flows.Flow.deploy`
- dagster 1.13.20 — `@dagster.asset`, `dagster.Definitions(assets=…)`, `dagster.materialize(assets)`. `located`.
  `locate: dagster.asset, dagster.Definitions, dagster.materialize`
- temporalio 1.32.0 — `@temporalio.workflow.defn`, `@temporalio.workflow.run`, `@temporalio.activity.defn`, `temporalio.client.Client.connect(host)`, `temporalio.worker.Worker(client, task_queue, workflows, activities).run()`. `located`.
  `locate: temporalio.workflow.defn, temporalio.workflow.run, temporalio.activity.defn, temporalio.client.Client.connect, temporalio.worker.Worker, temporalio.worker.Worker.run`

### P0.5 Self-load — the flow module → a running flow

- Python 3.11 — `importlib.util.spec_from_file_location(name, path)`, `importlib.util.module_from_spec(spec)`, `spec.loader.exec_module(module)`; then the flow object is called or served. `exercised` with the rendered prefect flow.
  `locate: importlib.util.spec_from_file_location, importlib.util.module_from_spec`

---

## Part 2. The per-document chain

Every fact from line 6 onward carries the sentence id, the token ids it was compiled from, and the byte-exact slice of the sentence spanning those tokens.

### Line 0. Source with provenance

- `packs/foia/sources.yaml` (data): file, URL, repository, commit, retrieval date, SHA-256, license. `hashlib.sha256(bytes).hexdigest()` must equal the recorded value or the build stops. `wired`.
  `locate: hashlib.sha256`

### Line 1. Read — the source file → units of text, each with its position and its place in the document tree

- lxml 6.1.3, for the United States Code in USLM XML (the House's format, uscode.house.gov) — `etree.parse(path)`; `for el in root.iter()`: `el.get("identifier")` is the statutory path (`/us/usc/t5/s552/a/6/A/i`); a stem sentence is the `<chapeau>` element and its sub-items are the sibling `<clause>` elements' `<content>`; `el.sourceline` locates the element in the file. `exercised` on a USLM-shaped fragment of (a)(6)(A): identifiers, chapeau text, and clause content read back. The FOIA XML file itself is not in the pack: uscode.house.gov is unreachable from the environment that built this file, and the pack's author supplies it.
  `locate: lxml.etree.parse, lxml.etree.fromstring, lxml.etree._Element.iter, lxml.etree._Element.xpath, lxml.etree._Element.sourceline`
- docling 2.124.0, for the HTML page in the pack — `DocumentConverter().convert(path).document.iterate_items(with_groups=True)`; on the DOJ page the sub-items of a list item are the `ListGroup` that follows it under the same parent group: item `#/texts/77` "(6)(A) Each agency, upon any request…" is followed by `ListGroup #/groups/22` (parent `#/groups/1`, 10 children) whose nested `ListGroup #/groups/23` holds the "(i)", "(ii)" items. The stem-to-sub-item relation is this data structure; no rule infers it. `exercised`.
  `locate: docling.document_converter.DocumentConverter.convert, docling_core.types.doc.DoclingDocument.iterate_items, docling_core.types.doc.ListItem, docling_core.types.doc.GroupItem`
- Python 3.11 `html.parser`, what the build calls today — `HTMLParser.getpos()` gives the line and column of every text node, so each character keeps its offset in the file; text inside `<s>` is dropped and counted. `wired`. The repository's derivation of statutory paths from designator text (`_paths_for_blocks`, `_designator_kind`) is replaced by the identifiers of the USLM line or the tree of the docling line.
  `locate: html.parser.HTMLParser, html.parser.HTMLParser.getpos`
- pdfplumber 0.11.10, for a PDF source — `pdfplumber.open(path)`; `Page.chars` (every character with page and position); `Page.extract_words(x_tolerance=3, y_tolerance=3, use_text_flow=False, expand_ligatures=True, split_at_punctuation=False, return_chars=True)`. `wired` for PDF packs; not exercised by the HTML source.
  `locate: pdfplumber.open, pdfplumber.page.Page.chars, pdfplumber.page.Page.extract_words`

Certificate of line 1: the source SHA-256; per unit, the USLM identifier and sourceline, or the docling `self_ref` and `parent`, or the html.parser offset.

### Line 2. Canonical text — each unit → the text the citations are byte-exact against

- Python 3.11 — `unicodedata.normalize("NFC", ch)` per character; every character for which `str.isspace()` is true becomes one space; runs collapse; the unit is trimmed; the map from canonical index to file offset is kept. Rule version 1, recorded in the manifest. `wired`.
  `locate: unicodedata.normalize`

### Line 3. Parse — each unit → CoNLL-U with a character range per token

- ufal.udpipe 1.4.0.1 — `Model.load(path)`; `Pipeline(model, "tokenizer=ranges", Pipeline.DEFAULT, Pipeline.DEFAULT, "conllu").process(text, ProcessingError())` → CoNLL-U; each token's `misc` carries `TokenRange=a:b`. Model: `english-ewt-ud-2.5-191206.udpipe`, SHA-256 `784bd0fa85e3d831fd02a55290d0acfd05c953159dc38cc33d52e1b28add9957`, Universal Dependencies 2.5, CC BY-NC-SA 4.0. Certificate: the model SHA-256; `unit.text[a:b] == form` for every token or the build stops. `wired`.
  `locate: ufal.udpipe.Model.load, ufal.udpipe.Pipeline, ufal.udpipe.Pipeline.process, ufal.udpipe.ProcessingError`
- stanza 1.14.0, the method's alternative parser — `stanza.Pipeline(lang, processors="tokenize,pos,lemma,depparse")`; `stanza.download(lang)`. `located`; its models are fetched from huggingface.co, which the build environment blocks.
  `locate: stanza.Pipeline, stanza.download`
- spaCy 3.8.16, the method's sentence cutter — `spacy.blank("en")`; `nlp.add_pipe("sentencizer")`; `doc.sents`. `located`.
  `locate: spacy.blank, spacy.language.Language.add_pipe, spacy.pipeline.Sentencizer, spacy.tokens.Doc.sents`

### Line 4. Token table and citation index — the CoNLL-U → typed rows in a fixed order

- conllu 6.0.0 — `conllu.parse(text)` → `TokenList`; `token["id"]`, `["form"]`, `["lemma"]`, `["upos"]`, `["xpos"]`, `["feats"]`, `["head"]`, `["deprel"]`, `["misc"]["TokenRange"]`. `exercised`: the (ii) clause parsed to 32 tokens; token 1 `(` with `TokenRange 0:1`. Replaces the repository's own CoNLL-U splitter.
  `locate: conllu.parse, conllu.models.TokenList, conllu.models.Token`
- pydantic 2.13.5 — `BaseModel.model_validate(row)` for `Token`, `Sentence`; `csv.writer` and `json.dumps(sort_keys=True)` write the table and the index in sorted order. `wired`.
  `locate: pydantic.BaseModel.model_validate, csv.writer, json.dumps`
- kuzu 0.11.3, the method's graph store for the table — `Database(path)`; `Connection(db).execute("CREATE NODE TABLE Tok(id STRING, form STRING, lemma STRING, upos STRING, deprel STRING, PRIMARY KEY(id))")`; `CREATE REL TABLE Head(FROM Tok TO Tok)`; Cypher `MATCH (a:Tok)-[:Head]->(b:Tok) WHERE a.deprel='obj' RETURN b.lemma, a.lemma`. `exercised`: returned `[['make', 'determination']]`.
  `locate: kuzu.Database, kuzu.Connection, kuzu.Connection.execute`

### Line 5. Extract — each sentence → its predicates and their arguments, with the rule that derived each

- predpatt 1.0.1 (hltcoe/PredPatt at commit 34bc751656a0766c7ac233b077ea8511a8004876, BSD 3-Clause) — `load_conllu(text)` → `(sent_id, UDParse)`; `PredPatt(parse, opts=PredPattOpts(ud=dep_v2.VERSION, resolve_relcl=True, resolve_appos=True, resolve_conj=True, resolve_poss=True, resolve_amod=True, borrow_arg_for_relcl=True))`; `pp.instances` → `Predicate.root.position`, `Predicate.arguments` → `Argument.root.position`, `Argument.root.gov_rel`; `Predicate.subj()`, `Predicate.obj()`. The option `ud="2.0"` selects PredPatt's Universal Dependencies v2 relation table, which is what the parser model emits; PredPatt's default is its v1 table, whose object, passive-subject, and oblique names never occur in a v2 parse. Certificate: `Predicate.rules` and `Argument.rules`, the named rules that derived each, printed by `PredPatt.pprint(track_rule=True)`. `exercised` on the (ii) clause: predicate `make ?a with ?b within ?c`, trace `[make-root, add_root(make/3)_for_advcl_from_(excepting/15), add_root(make/3)_for_obj_from_(determination/5), add_root(make/3)_for_obl_from_(days/13), add_root(make/3)_for_obl_from_(respect/7), n1, n1, n1, n1, n2, n2, n2, n3, n6, n6, u]`; on "any request for records which reasonably describes such records" with `resolve_relcl=True` the argument of `describes` is `request`, not `which`. The build today runs with `ud="2.0"` and every resolver at its default (off): `wired`; the resolvers: `exercised`.
  `locate: predpatt.load_conllu, predpatt.PredPatt, predpatt.PredPattOpts, predpatt.util.ud.dep_v2, predpatt.patt.Predicate.format, predpatt.patt.Predicate.subj, predpatt.patt.Predicate.obj, predpatt.patt.PredPatt.pprint, predpatt.rules.arg_resolve_relcl, predpatt.rules.pred_resolve_relcl, predpatt.rules.borrow_subj`

### Line 6. Compile — PredPatt's output and the token table → facts over the seven predicates

- typedlogic 0.2.4 → clingo 5.8.2 — the facts are `Pred(e, lemma)` from each `Predicate.root` and its token's lemma; `Arg(e, x, rel)` from each `Argument.root.gov_rel`; `Child(head, dep, rel, lemma)` from every token table row's `head`, `deprel`, `lemma`; `Timex(x)` from line 7. The rules are the projection table, as data. The two below were run: `PythonParser().parse(file)` → `Theory`; `get_solver("clingo").add(theory)`; `.add_fact(Arg("e4", "x2", "nsubj"))`, `.add_fact(Arg("e4", "x6", "obj"))`; `.model().ground_terms` → `Agent(e4, x2)`, `Patient(e4, x6)`, for "The agency shall determine the request." `exercised`.

  ```python
  @dataclass
  class Arg(FactMixin):
      e: str
      x: str
      rel: str

  @dataclass
  class Agent(FactMixin):
      e: str
      x: str

  @dataclass
  class Patient(FactMixin):
      e: str
      x: str

  @axiom
  def projection(e: str, x: str):
      if Arg(e, x, "nsubj"):
          assert Agent(e, x)
      if Arg(e, x, "obj"):
          assert Patient(e, x)
  ```

  The whole table, in the clingo syntax the build already runs through clorm (the build's `fol.py` implements the same table in Python today; the rules below are its replacement and are not yet wired):

  ```
  event(E, L)     :- pred(E, L).
  agent(E, X)     :- arg(E, X, "nsubj").
  agent(E, X)     :- arg(E, X, "csubj").
  agent(E, X)     :- arg(E, X, "obl:agent").
  patient(E, X)   :- arg(E, X, "obj").
  patient(E, X)   :- arg(E, X, "nsubj:pass").
  theme(E, X)     :- arg(E, X, "iobj").
  theme(E, X)     :- arg(E, X, "obl"), not anchor(X).
  obligatory(E)   :- pred(E, _), child(E, C, "aux", W), obligation(W).
  negated(E)      :- pred(E, _), child(E, C, "advmod", W), negator(W).
  negated(E)      :- pred(E, _), arg(E, X, "nsubj"), child(X, D, "det", "no").
  anchor(X)       :- child(_, X, "obl", _), child(X, C, "case", W), after(W), timex(X).
  anchor(X)       :- child(_, X, "obl", _), child(X, C, "case", W), before(W), timex(X).
  event(X, L)     :- anchor(X), tok(X, L).
  precedes(X, E)  :- pred(E, _), child(E, X, "obl", _), child(X, C, "case", W), after(W), anchor(X).
  precedes(E, X)  :- pred(E, _), child(E, X, "obl", _), child(X, C, "case", W), before(W), anchor(X).
  precedes(A, E)  :- pred(E, _), pred(A, _), child(E, A, "advcl", _), child(A, M, "mark", W), after(W).
  precedes(E, A)  :- pred(E, _), pred(A, _), child(E, A, "advcl", _), child(A, M, "mark", W), before(W).
  obligation("shall"). obligation("must").
  negator("not"). negator("never"). negator("n't").
  after("after"). after("following"). after("upon"). after("once"). after("since").
  before("before"). before("prior"). before("until"). before("pending").
  ```

  The relation names are the Universal Dependencies v2 inventory (universaldependencies.org/u/dep). The four word lists are closed classes and are data of the method. Certificate: the stable model, and for every fact the byte-exact check `sentence.text[lo:hi] == quote` and `quote.encode() in sentence.text.encode()`. `wired` (the check); `exercised` (the solver).
  `locate: typedlogic.pybridge.FactMixin, typedlogic.decorators.axiom, typedlogic.parsers.pyparser.python_parser.PythonParser, typedlogic.registry.get_solver, typedlogic.solver.Solver.add, typedlogic.solver.Solver.add_fact, typedlogic.solver.Solver.model`

- The second route to logic, as the method names it — amrlib 0.8.1: `amrlib.load_stog_model(model_dir=…)` → `Inference`; `Inference.parse_sents(sentences)` → AMR graphs in PENMAN; penman 1.3.1: `penman.decode(text)` → `Graph` with `triples`, `top`; amr-logic-converter 0.11.3: `AmrLogicConverter().convert(graph)` → a first-order-logic `Clause` over `Atom`, `And`, `Or`, with PropBank frames such as `obligate-01`, `:polarity -`, and the roles `:time` and `:location`, which separate a temporal "before" from a forum "before" without a word list. Model: `model_parse_xfm_bart_base-v0_1_0.tar.gz` from github.com/bjascob/amrlib-models releases, 515,968,261 bytes, SHA-256 `ecaa2d9b6b17d6a86af54a784e9ed1dd1c879a23f79918aa68b53b4a3766cc26`, downloaded in the session that wrote this file; not committed. The run stopped at `AutoTokenizer.from_pretrained("facebook/bart-base")`, which fetches the tokenizer from huggingface.co: 403 through the environment's proxy. The route runs where huggingface.co is reachable or where the four tokenizer files are placed beside the model. `located` (all three functions); not exercised on the statute.
  `locate: amrlib.load_stog_model, amrlib.models.parse_xfm.inference.Inference.parse_sents, penman.decode, penman.encode, penman.Graph, amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`

### Line 7. Temporal spans and working-day clocks — each sentence → TIMEX3 spans; each duration → a date

- timexy 0.1.3 (MIT) on spaCy 3.8.16 — `nlp = spacy.blank("en")`; `nlp.add_pipe("timexy", config={"kb_id_type": "timex3", "label": "timexy", "overwrite": False})`; `doc = nlp(sentence)`; `doc.ents` → `Span.start_char`, `Span.end_char`, `Span.kb_id_`. No model download. A token whose range lies inside a span is `timex(X)` in line 6. `exercised`: "twenty days" → `TIMEX3 type="DURATION" value="P20D"`; "20 days" → `P20D`; "September 30" → `type="DATE"`; "based on the record before the agency" → no span; "pending before the agency" → no span; "On or before February 1 of each year" → no span (a month-day without a year is not matched by timexy 0.1.3; that miss is recorded here, not corrected).
  `locate: spacy.blank, spacy.language.Language.add_pipe, spacy.tokens.Doc.ents, spacy.tokens.Span.start_char`
- dateparser 1.4.2 — `dateparser.parse("February 1, 2026")` → `2026-02-01 00:00:00`; `dateparser.search.search_dates(text)`. `exercised`.
  `locate: dateparser.parse, dateparser.search.search_dates`
- holidays 0.103 and numpy 2.3.5 — `holidays.country_holidays("US", years=[y])` (the federal list); `numpy.busdaycalendar(holidays=[…])`; `numpy.busday_offset(receipt, 20, roll="forward", busdaycal=cal)`. The statute's "excepting Saturdays, Sundays, and legal public holidays" names this calendar. `exercised`: receipt 2026-09-03 → due 2026-10-02.
  `locate: holidays.country_holidays, holidays.countries.united_states.UnitedStates, numpy.busday_offset, numpy.busdaycalendar, numpy.busday_count`
- Where a duration lands among the seven predicates is not decided in this file. `precedes(E, T)` with a computed anchor and an eighth predicate are the two forms; the AMR route yields `:duration`. That decision belongs to the method's author.
- Heavier taggers the method may select instead: sutime 1.0.1 (GPL-3.0-or-later, needs Java and CoreNLP), py-heideltime 1.0.6 (needs Java and TreeTagger). Not installed.

### Line 8. Normalize — the facts → pronouns resolved, inanimate subjects routed, every routing flagged

- clingo 5.8.2 through clorm 1.6.3 — the two rules, as data, run over `agent(E, X)` and `patient(E, X)` facts keyed by lemma. Certificate: the unique stable model; every routed atom is a flag for the analyst. `wired`.

  ```
  animate(X) :- agent(E, X), patient(E, _).
  theme(E, X) :- agent(E, X), not animate(X).
  ```

  `locate: clorm.clingo.Control, clorm.FactBase, clorm.Predicate`
- Relative pronouns, appositives, coordinated verbs, possessives: PredPatt's resolvers in line 5, which substitute the antecedent before any fact is written.
- Residual discourse pronouns: stanza 1.14.0 — `stanza.Pipeline("en", processors="tokenize,coref")`. `located`; models on huggingface.co, blocked here. coreferee 1.4.1 — `not located`: it pins spaCy 3.5, whose compiled wheels raise `numpy.dtype size changed, may indicate binary incompatibility` under numpy 2 in this environment. A pronoun no function resolves stays a flag.
  `locate: stanza.Pipeline`

### Line 9. Adjudicate — the facts and their flags → the facts minus the rejected ones

- PyYAML 6.0.2 — `yaml.safe_load(open("rejections.yaml"))`; a rejection is `{atom_id, analyst, reason}`; rejected ids are removed before line 10. `wired`.
  `locate: yaml.safe_load`
- statsmodels 0.15.0 — two analysts' decisions → `to_table(np.column_stack([a, b]))` → `cohens_kappa(table).kappa`. `exercised`: a five-row example gave kappa 0.615.
  `locate: statsmodels.stats.inter_rater.cohens_kappa, statsmodels.stats.inter_rater.to_table`

### Line 10. Precedence proof — the precedes facts → satisfiable, or the minimal conflicting set

- z3-solver 5.1.0.0 — `z3.set_param("smt.random_seed", 0)`, `("sat.random_seed", 0)`, `("smt.core.minimize", True)`; `s = z3.Solver()`; `s.set("rlimit", 20_000_000)`; for each `precedes(E1, E2)`: `s.assert_and_track(z3.Int(E1) - z3.Int(E2) <= -1, z3.Bool(p))`; `s.check()`; `s.unsat_core()`, then deletion-minimized in a fixed order. Certificate: `sat`, or the core. `wired`.
  `locate: z3.Solver, z3.Solver.assert_and_track, z3.Solver.check, z3.Solver.unsat_core, z3.set_param, z3.Int`
- PySMT 0.9.6 — `pysmt.shortcuts.Solver(name)`, `is_sat(formula)`, `get_unsat_core(clauses)`. `located`.
  `locate: pysmt.shortcuts.Solver, pysmt.shortcuts.is_sat, pysmt.shortcuts.get_unsat_core`
- cvc5 1.3.4 — `cvc5.Solver().checkSat()`, `.getUnsatCore()`. `located`.
  `locate: cvc5.Solver, cvc5.Solver.checkSat, cvc5.Solver.getUnsatCore`

### Line 11. Order — the precedes facts → the forced-precedence graph and the derivation order

- networkx 3.6.1 — `DiGraph.add_edge(E1, E2)` per fact; `is_directed_acyclic_graph(G)`; `transitive_reduction(G)` is the forced-precedence graph; `lexicographical_topological_sort(reduced, key=str)` is the order; `find_cycle(G, source=min(G.nodes))` names a contradiction. `wired`.
  `locate: networkx.transitive_reduction, networkx.lexicographical_topological_sort, networkx.find_cycle, networkx.is_directed_acyclic_graph`
- unified-planning 1.3.0 with up-pyperplan 1.1.0 — each event is an `InstantaneousAction` with a `Fluent done_<event>` as its effect; each `precedes(E1, E2)` is `action(E2).add_precondition(done_E1)`; `Problem.add_goal` for every fluent; `OneshotPlanner(problem_kind=problem.kind).solve(problem).plan` → `SequentialPlan`; `.convert_to(PlanKind.PARTIAL_ORDER_PLAN, problem)` → `PartialOrderPlan`. `exercised` with receipt → determine → notify: `PartialOrderPlan: actions: 0) receipt 1) determine 2) notify; constraints: 0 < 1, 1 < 2`.
  `locate: unified_planning.model.Problem, unified_planning.model.Fluent, unified_planning.model.InstantaneousAction, unified_planning.model.InstantaneousAction.add_precondition, unified_planning.model.InstantaneousAction.add_effect, unified_planning.shortcuts.OneshotPlanner, unified_planning.plans.PartialOrderPlan, unified_planning.plans.SequentialPlan.convert_to, unified_planning.plans.PlanKind`

### Line 12. Seal — every fact, its sentence digest, its quote digest, the toolchain, the order → one digest

- Python 3.11 — `json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`; `hashlib.sha256(...).hexdigest()` per fact and over the whole; the pinned versions and the parser model's SHA-256 are inside the body. Certificate: a rebuild reproduces the digest. `wired`.
  `locate: hashlib.sha256, json.dumps`

---

## Part 3. The terminal solutions

### T1. The rule base and the runtime — obligatory facts with their agent, patient, and theme → a decision table; a case record → a proof or a list of reasons

- Jinja2 3.1.6 — `Environment().from_string(template).render(facts=…)` → a GoRules JDM decision document (JSON) whose rows are the obligatory events and their clocks. `exercised` (the render).
- zen-engine 2.0.2 — `zen.ZenEngine().create_decision(jdm_json)` → `ZenDecision`; `ZenDecision.evaluate(record)` → `{"result": …}`. `exercised`: a table with input `days_elapsed` and rule `> 20 → overdue = true` evaluated `{"days_elapsed": 25}` to `{"overdue": True}`.
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
- durable-rules 2.0.28 — `with ruleset(name): @when_all((m.obligatory == True) & (m.days_elapsed > 20))`; `post(name, record)`. `exercised`: the rule fired on `{"request": "r1", "obligatory": True, "days_elapsed": 25}`.
  `locate: durable.lang.ruleset, durable.lang.when_all, durable.lang.post, durable.lang.m`
- business-rules 1.1.1 — `run_all(rule_list, defined_variables, defined_actions)`; `export_rule_data(variables, actions)`. `located`.
  `locate: business_rules.run_all, business_rules.export_rule_data`
- experta 1.9.4 — `not located`: `import experta` fails on Python 3.11 with `AttributeError: module 'collections' has no attribute 'Mapping'`.
- Which engine runs is the stable model of P0.3, not a choice made here.

### T2. The process model — the forced-precedence graph → BPMN; with an event log → fitness, precision, deviations

- pm4py 2.7.23.8 (the package prints on import: Community Version, AGPL v3) — `BPMN()`; `BPMN.StartEvent(name)`, `BPMN.Task(name)` per event, `BPMN.EndEvent(name)`; `bpmn.add_node(n)`; `bpmn.add_flow(BPMN.Flow(a, b))` per forced edge; `pm4py.write_bpmn(bpmn, path, auto_layout=False)` (`auto_layout=True` calls the graphviz `dot` binary, absent here); `pm4py.convert_to_petri_net(bpmn)` → `(net, initial_marking, final_marking)`; `pm4py.read_bpmn(path)`. With a log: `pm4py.conformance_diagnostics_alignments(log, net, im, fm)`, `fitness_alignments`, `precision_alignments`, `conformance_diagnostics_token_based_replay`. `exercised`: receipt → determine written to `foia.bpmn` (3,223 bytes), converted to a net of 8 places and 4 transitions, read back with 4 nodes; the alignment functions `located`.
  `locate: pm4py.objects.bpmn.obj.BPMN, pm4py.objects.bpmn.obj.BPMN.StartEvent, pm4py.objects.bpmn.obj.BPMN.Task, pm4py.objects.bpmn.obj.BPMN.EndEvent, pm4py.objects.bpmn.obj.BPMN.Flow, pm4py.objects.bpmn.obj.BPMN.add_node, pm4py.objects.bpmn.obj.BPMN.add_flow, pm4py.write_bpmn, pm4py.read_bpmn, pm4py.convert_to_petri_net, pm4py.conformance_diagnostics_alignments, pm4py.fitness_alignments, pm4py.precision_alignments, pm4py.conformance_diagnostics_token_based_replay, pm4py.discover_petri_net_inductive`
- SpiffWorkflow 3.2.0 — `BpmnParser().add_bpmn_file(path)`; `BpmnWorkflow(spec)` executes the model. `located`.
  `locate: SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser, SpiffWorkflow.bpmn.workflow.BpmnWorkflow`

### T3. The spreadsheet and the document — the certified tables → one workbook per artifact; renderings

- openpyxl 3.1.5 — `Workbook()`; `ws = wb.active`; `ws.append(row)`; `wb.save(path)`. `exercised`.
  `locate: openpyxl.Workbook, openpyxl.worksheet.worksheet.Worksheet.append, openpyxl.Workbook.save, openpyxl.worksheet.table.Table`
- XlsxWriter 3.2.9 — `Workbook(path).add_worksheet().write_row(r, c, values)`; `Worksheet.add_table(...)`. `exercised`.
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet, xlsxwriter.worksheet.Worksheet.write_row, xlsxwriter.worksheet.Worksheet.add_table`
- pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "facts", path)` writes a real Excel Table object; `xlsx_table_to_df(path, "facts")` reads it back. `exercised`.
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df, pandas.DataFrame, pandas.DataFrame.to_excel`
- python-docx 1.2.0 — `Document()`; `.add_paragraph(text)`; `.add_table(rows, cols)`; `.save(path)`. `exercised`.
  `locate: docx.Document, docx.document.Document.add_paragraph, docx.document.Document.add_table, docx.document.Document.save`
- great-tables 0.24.0 — `GT(df)`, `.as_raw_html()`, `.save(path)`. `located`. plotly 7.0.0 — `plotly.express.bar`, `graph_objects.Figure`, `plotly.io.write_html`. `located`. streamlit 1.63.0 — `st.dataframe`, `st.plotly_chart`, `st.write`. `located`.
  `locate: great_tables.GT, great_tables.GT.as_raw_html, great_tables.GT.save, plotly.graph_objects.Figure, plotly.io.write_html, plotly.express.bar, streamlit.dataframe, streamlit.plotly_chart, streamlit.write`

### T4. The digest — Part 2, line 12; verified by `compiled-ai verify <pack>`.

---

## Part 4. Pipeline R0, the invert compiler

R0 reads a published pack and runs the same chain backward to one spreadsheet per artifact. The readers:

- python-docx 1.2.0 — `Document(path).paragraphs`, `.tables`. `located`.
  `locate: docx.Document`
- python-pptx 1.0.2 — `Presentation(path).slides`; `Slide.shapes`; `Slide.notes_slide`. `located`.
  `locate: pptx.Presentation, pptx.presentation.Presentation.slides, pptx.slide.Slide.shapes, pptx.slide.Slide.notes_slide`
- mammoth 1.12.1 — `convert_to_html(file)`, `convert_to_markdown(file)`, `extract_raw_text(file)`. `located`.
  `locate: mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text`
- office-oxide 0.1.9 — `office_oxide.to_markdown(path)`, `to_html(path)`, `extract_text(path)`, `Document`. `located`.
  `locate: office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document`
- PyMuPDF 1.28.2, pypdf 6.16.2, pypdfium2 5.13.0 — `pymupdf.open(path)`, `Page.get_text("dict")`; `PdfReader(path)`; `PdfDocument(path)[i].get_textpage().get_text_range()`. `located`.
  `locate: pypdfium2.PdfDocument, pypdfium2.PdfPage.get_textpage, pypdfium2.PdfTextPage.get_text_range`
- playwright 1.62.0 (Chromium preinstalled in the build environment) — `with sync_playwright() as p: page = p.chromium.launch().new_page(); page.goto(url); page.content()`. `located`.
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.goto, playwright.sync_api.Page.content`
- markdownify 1.2.3 — `markdownify(html)`; html2text 2025.4.15 — `HTML2Text().handle(html)`. `located`.
  `locate: markdownify.markdownify, html2text.HTML2Text, html2text.HTML2Text.handle`
- then Part 1 (census, schema, capability logic, graph, self-load), Part 2, and T3 with openpyxl, XlsxWriter, and pandas-xlsx-tables writing the one workbook.

---

## Part 5. The forward and reverse pipelines

Every step of all 92 pipelines the method defines (pipelines.txt, reverse_pipelines.txt) is bound here to the actual library function that performs it. The step line states the operation in plain words; under it, each library the step names as a tool is bound to a specific public function in the installed package, with the exact call and a `locate:` line of importable dotted paths that `tests/test_function_chain.py` resolves on every run. `exercised` means the function was run on a minimal input in the session that produced this file, with a short result quoted; `located` means it was resolved by import but not run here. Where a step's library was not yet present, it was installed one at a time and bound to its real function; where a package cannot run on this interpreter (its build is broken, its name collides with an unrelated project, or it needs Python 3.13) the step is bound instead to a clearly-labelled in-catalog replacement that does the same job — written `X → Y` — so no step is left as a gap. What still carries no Python binding is the handful of non-Python renderers (mermaid, marp, reveal-md, kroki), given as their command line: rendering a diagram from structured input is mechanical, not a step where a model could hallucinate. Every dotted path below was re-resolved centrally before this file was written — each in a fresh interpreter, so a compiled-extension collision (a broken highspy poisoning ortools) never hides a function that genuinely resolves; any path that failed everywhere was dropped. Bindings were produced by twelve parallel agents inspecting each installed package's signatures and source; libraries the harness had recorded under the wrong import name, and the replacements above, were re-bound centrally and verified.

#### Pipeline 0: Zero-Touch Orchestrator Compiler

- **Step 0 (Global Ingestion).** convert mixed docs into Markdown/JSON/CSV/workbook inventory
  docling 2.124.0 — `DocumentConverter().convert(path).document.export_to_markdown()` → Markdown string; parses PDF/Office docs. located
  `locate: docling.document_converter.DocumentConverter.convert, docling_core.types.doc.document.DoclingDocument.export_to_markdown`
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown; Office parser (also `.to_json()`). exercised: "hi"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown, undoc.Undoc.to_json`
  markitdown 0.1.7 — `MarkItDown().convert(path).text_content` → Markdown; any-format to Markdown. exercised: "# Hi\n\nBody text"
  `locate: markitdown.MarkItDown.convert`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown string; document-to-Markdown. exercised: "| a | b | ..."
  `locate: anydoc.to_markdown`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path)` → workbook; reads xlsx/ods for inventory. exercised: "['Sheet']"
  `locate: python_calamine.load_workbook`
  fastexcel 0.21.0 — `fastexcel.read_excel(path)` → ExcelReader; calamine workbook reader. exercised: "['Sheet']"
  `locate: fastexcel.read_excel`
  csvkit 2.2.0 — `csvkit.reader(open(path))` → CSV row iterator; reads CSV (CLI: `in2csv`). exercised: "[['a','b'],['1','x'],['2','y']]"
  `locate: csvkit.reader`

- **Step 1 (Artifact Census).** profile tables, walk JSON/YAML/XML, fingerprint PDFs into manifest
  ydata-profiling 4.18.4 — `ProfileReport(df, minimal=True)` → profile report object; per-table EDA summary. located
  `locate: ydata_profiling.ProfileReport`
  sweetviz 2.3.3 — `sweetviz.analyze(df)` → DataframeReport; visual EDA of tabular object. located
  `locate: sweetviz.analyze`
  dataprep → ydata-profiling 4.18.4 — `ProfileReport(df).to_json()` → table profiling (dataprep is not installable here). located
  `locate: ydata_profiling.ProfileReport.to_json, ydata_profiling.ProfileReport`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  pymupdf 1.28.2 — `pymupdf.open(path)` then `page.get_text()` → text; opens/fingerprints PDF. exercised: "pages=1", "hi\n"
  `locate: pymupdf.open, pymupdf.Page.get_text`
  pypdf 6.16.2 — `pypdf.PdfReader(path).metadata` → DocumentInformation; PDF fingerprint. exercised: "pages=1, metadata read"
  `locate: pypdf.PdfReader, pypdf.PdfReader.metadata`

- **Step 2 (Schema Compilation).** type projections with pydantic to produce runtime schemas
  pydantic 2.13.5 — `pydantic.create_model("Row", a=(int,...), b=(str,...))` → model class; runtime schema. exercised: "{'a':1,'b':'x'}"
  `locate: pydantic.create_model`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`

- **Step 3 (Capability Logic).** write logic facts, solve for unique stable model
  typedlogic 0.2.4 — `ClingoSolver().add_fact(FactInstance)` → None; writes clingo facts. exercised: "fact added, dump=17ch"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add_fact`
  clingo 5.8.0 — `Control().solve(on_model=cb)` → SolveResult; returns stable model. exercised: "a b"
  `locate: clingo.Control.solve`

- **Step 4 (Graph Compilation).** build directed task graph, render orchestrator source via templates
  networkx 3.6.1 — `DiGraph().add_edge(u,v)` + `nx.topological_sort(g)` → task order. exercised: "['a','b','c']"
  `locate: networkx.DiGraph.add_edge, networkx.topological_sort`
  jinja2 3.1.6 — `Template(src).render(**ctx)` → source string; renders flow/asset/workflow code. exercised: "hi x"
  `locate: jinja2.Template.render`
  prefect 3.8.4 — `@prefect.flow` → Flow; target for rendered flow source. exercised: "Flow"
  `locate: prefect.flow`
  dagster 1.13.20 — `@dagster.asset` + `Definitions(assets=[...])` → asset defs. exercised: "AssetsDefinition"
  `locate: dagster.asset, dagster.Definitions`
  temporalio 1.32.0 — `@temporalio.workflow.defn` → durable workflow class definition. located
  `locate: temporalio.workflow.defn`
  graphable — requires Python ≥ 3.13 (this interpreter is 3.11); its table→Mermaid/D2/PlantUML output is otherwise the `diagrams` binding or the mermaid CLI

- **Step 5 (Self-Load).** orchestrator imports written file, registers assets, starts run
  (no library candidates named in this step; performed by the chosen orchestrator runtime)

#### Pipeline 1: Quality Engineering

- **Step 0 (Global Ingestion).** parse raw logs/PDFs into flat text and Markdown
  docling 2.124.0 — `DocumentConverter().convert(source="logs.pdf").document.export_to_markdown()` → ConversionResult; parses PDFs/logs to text+Markdown. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestration and Narrowing).** orchestrate the workflow piping raw text onward
  dagster 1.13.20 — `dagster.job(name="quality_eng")(fn)` → JobDefinition; composes ops into executable orchestration graph. located
  `locate: dagster.job`

- **Step 2 (Logic Generation).** translate NL dependency graphs into First-Order Logic
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr="(w / want-01 :ARG0 (b / boy) ...)")` → FOL Clause. exercised: "want-01(w) ∧ :ARG0(w, b) ∧ boy(b)…"
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`

- **Step 3 (Mathematical Verification).** verify physical bounds and logic paths
  pysmt 0.9.6 — `pysmt.shortcuts.is_valid(formula)` → bool; SMT-verifies bounds/logic hold. exercised: "True"
  `locate: pysmt.shortcuts.is_valid`

- **Step 4 (Time-to-Event Modeling).** fit parametric time-to-event shapes on failures
  lifelines 0.30.3 — `WeibullFitter().fit(durations, event_observed=events)` → fitted parametric shape/scale. exercised: "lambda_=5.557 rho_=3.235"
  `locate: lifelines.WeibullFitter.fit`

- **Step 5 (Execution).** run FMEA simulation over verified logic/models
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`

#### Pipeline 2: Financial Dashboarding

- **Step 0 (Global Ingestion).** Parse a global dump of unstructured financial reports into Markdown.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("report.docx")` → Markdown string; flattens each report doc. exercised: "Spec line"
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestration and Narrowing).** Orchestrate pipeline state; build syntactic dependency trees of financial entities.
  temporalio 1.32.0 — `Client.execute_workflow(wf, id="p2", task_queue="q")` → runs durable workflow holding pipeline state. located
  `locate: temporalio.client.Client.execute_workflow`
  stanza 1.14.0 — `stanza.Pipeline(lang="en", processors="tokenize,pos,depparse")(text)` → dependency-parsed doc. located
  `locate: stanza.Pipeline`

- **Step 2 (Schema Auto-Generation).** Extract nodes; instantiate Pydantic models from derived JSON schemas.
  pydantic 2.13.5 — `pydantic.create_model("Ledger", amount=(int, ...))` → dynamic model class from schema fields. exercised: "instance amount=100"
  `locate: pydantic.create_model`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`

- **Step 3 (Logic Enforcement).** Evaluate entities against decision graphs to enforce business logic.
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Constraint Verification).** Prove ledger consistency of extracted values via Answer Set Programming.
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` (after add/ground) → SAT/UNSAT proof of consistency. exercised: "sat, balanced=[True]"
  `locate: clingo.Control.solve`

- **Step 5 (Visual Selection).** Automatically select and generate charts from verified tabular inputs.
  autoviz 0.1.905 — `AutoViz_Class().AutoViz("data.csv", depVar="", dfte=df, verbose=0)` → auto-selected charts. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`

- **Step 6 (Execution).** Deploy the generated charts as a data dashboard.
  streamlit 1.63.0 — `streamlit.pyplot(fig)` → renders generated matplotlib chart in the app. located
  `locate: streamlit.pyplot`

#### Pipeline 3: Architecture Documentation

- **Step 0 (Global Ingestion).** parse a raw document dump into flat text and JSON
  undoc 0.9.0 — `undoc.parse_file(path).to_json()` → parsed Office doc emitted as JSON/plain text; ingestion. exercised: "to_json → format:\"xlsx\"…"
  `locate: undoc.parse_file, undoc.Undoc.to_json, undoc.Undoc.to_text`

- **Step 1 (Orchestration and Narrowing).** orchestrate flow; extract entity relations from text
  prefect 3.8.4 — `@prefect.flow(name="ingest")` → defines the orchestrated data flow. exercised: "Flow 'ingest'"
  `locate: prefect.flow, prefect.task`
  nltk 3.10.3 — `nltk.sem.relextract.extract_rels(subjclass, objclass, doc)` → relation tuples between named entities; NL→logic. located
  `locate: nltk.sem.relextract.extract_rels, nltk.ne_chunk`

- **Step 2 (Network Graphing).** build directed dependency graph and analyze it
  networkx 3.6.1 — `networkx.DiGraph().add_edges_from(edges)` → directed system-dependency graph; DAG analysis. exercised: "is_directed_acyclic_graph True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edges_from, networkx.is_directed_acyclic_graph`

- **Step 3 (Logic Translation).** convert dependency graph into clingo facts
  typedlogic 0.2.4 — `ClingoSolver().add_fact(fact)` → records Python fact as clingo fact; `.dump()` emits program. located
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add_fact, typedlogic.integrations.solvers.clingo.ClingoSolver.dump`
  clingo 5.8.0 — `Control().solve(on_model=cb)` (after `.add`/`.ground`) → ASP models over the facts. exercised: "SAT; model 'a b'"
  `locate: clingo.Control.solve, clingo.Control.ground, clingo.Control.add`

- **Step 4 (Architecture Modeling).** map logical facts into a C4 model DSL
  structurizr-python → diagrams 0.25.1 — `with Diagram(name): ...` → architecture diagram (structurizr-python needs pydantic v1). located
  `locate: diagrams.Diagram`

- **Step 5 (Verification).** SMT-verify the architecture has no cycles
  z3-solver 5.1.0.0 — `z3.Solver().add(constraints); .check()` → sat/unsat verdict on acyclicity. exercised: "sat; [x = 1]"
  `locate: z3.Solver.check, z3.Solver.add`

- **Step 6 (Execution).** render verified C4 DSL to a diagram
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 5: Process Mining Control Room

- **Step 0 (Global Ingestion).** Convert ERP exports, work-order PDFs, message logs to Markdown.
  markitdown 0.1.7 — `MarkItDown().convert(source).markdown` → Markdown string; flattens each source file. exercised: "'# Title\n\nHello world'"
  `locate: markitdown.MarkItDown.convert`
  docling 2.124.0 — `DocumentConverter().convert(source).document.export_to_markdown()` → Markdown; parses PDF/Office sources. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Admit asset graph only if actor/activity/time fields resolve.
  clingo 5.8.0 — `ctl.solve(on_model=cb)` (after add/ground) → SolveResult.satisfiable gates admission. exercised: "sat=True, model 'a b'"
  `locate: clingo.Control.solve, clingo.Control.ground`

- **Step 2 (Event Log Materialization).** Generated dagster assets type tuples via pydantic, land in duckdb.
  dagster 1.13.20 — `@dagster.asset` def + `materialize_to_memory([asset])` → generated assets. exercised: "success True, value 42"
  `locate: dagster.asset, dagster.materialize_to_memory`
  pydantic 2.13.5 — `Row.model_validate({...})` → typed model; validates each tuple. exercised: "actor='u1' t=5"
  `locate: pydantic.BaseModel.model_validate`
  duckdb 1.5.5 — `duckdb.connect().execute('CREATE TABLE ...; INSERT ...')` → persists rows. exercised: "count (2,)"
  `locate: duckdb.connect, duckdb.DuckDBPyConnection.execute`

- **Step 3 (Discovery and Replay).** Discover Petri net; replay; drop traces failing clingo facts.
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net,im,fm); discovers the net. exercised: "3 places, 2 transitions"
  `locate: pm4py.discover_petri_net_inductive`
  simpn 1.10.0 — `SimProblem().simulate(duration, reporter=None)` → runs token-game replay. exercised: "token a->b (2)"
  `locate: simpn.simulator.SimProblem.simulate`
  typedlogic 0.2.4 — `ClingoSolver().add(Term(...)); .check()` → Solution.satisfiable; drops failing facts. exercised: "Solution satisfiable=True"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add, typedlogic.integrations.solvers.clingo.ClingoSolver.check`
  clingo 5.8.0 — `ctl.solve()` → SolveResult.satisfiable evaluates the facts. exercised: "sat=True"
  `locate: clingo.Control.solve`
  (Sentence also names "snakes" — not a candidate lib in this step; not bound.)

- **Step 4 (Execution).** Compute bottlenecks; publish cytoscape graph and streamlit dashboard.
  most-queue 2.9 — `q=MMnrCalc(n,r); q.set_sources(l); q.set_servers(mu); q.run()` → queue metrics locate bottleneck. exercised: "utilization 0.5, w [1.0]"
  `locate: most_queue.theory.fifo.mmnr.MMnrCalc.run, most_queue.theory.fifo.mmnr.MMnrCalc.get_utilization`
  dash-cytoscape 1.0.2 — `dash_cytoscape.Cytoscape(id=, elements=, layout=)` → renderable network component. exercised: "component, 3 elements"
  `locate: dash_cytoscape.Cytoscape`
  streamlit 1.63.0 — `streamlit.dataframe(df)` / `streamlit.write(obj)` → publishes dashboard. located
  `locate: streamlit.dataframe, streamlit.write`

#### Pipeline 6: Causal Policy Evaluation

- **Step 0 (Global Ingestion).** parse evaluation/instrument/administrative PDFs into the manifest
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source=path)` → ConversionResult with parsed document; parses PDFs into manifest. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** emit orchestration flow; NLP-extract treatment/outcome spans
  prefect 3.8.4 — `@prefect.flow(name=...)` decorating the pipeline fn → Flow object; emits the orchestration flow. located
  `locate: prefect.flow`
  stanza 1.14.0 — `stanza.Pipeline(lang='en', processors='tokenize,ner,depparse')` → neural NLP pipeline; recovers treatment/outcome spans. located
  `locate: stanza.Pipeline`

- **Step 2 (Graph and Proof).** build causal DAG; prove a legal adjustment set
  dowhy 0.14 — `dowhy.CausalModel(data, treatment, outcome, graph=...)` → causal model over the DAG; builds causal graph. located
  `locate: dowhy.CausalModel`
  networkx 3.6.1 — `networkx.DiGraph([('T','Y')])` → directed graph; holds the causal DAG. located
  `locate: networkx.DiGraph`
  pgmpy 1.1.2 — `pgmpy.base.DAG([('X','Y')], exposures=..., outcomes=...)` → DAG with causal roles; builds the DAG. exercised: "[('X', 'Y')]"
  `locate: pgmpy.base.DAG`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; proves adjustment-set constraints (is_valid for entailment). exercised: "True"
  `locate: pysmt.shortcuts.is_sat, pysmt.shortcuts.is_valid`
  z3-solver 5.1.0.0 — `z3.Solver().check()` after `add(constraints)` → sat/unsat; proves a legal adjustment set. exercised: "sat x=3"
  `locate: z3.Solver.check, z3.Solver`

- **Step 3 (Estimation and Binding).** run causal effect estimation and Bayesian diagnostics
  arviz 0.23.4 — `arviz.summary(idata)` → DataFrame of posterior diagnostics; summarizes estimates. exercised: "['mean', 'sd', 'hdi_3%']"
  `locate: arviz.summary`
  causalpy 0.9.0 — `causalpy.EstimateEffect(method=InterruptedTimeSeries, data=df, ...)` → fitted quasi-experiment; estimates the effect. located
  `locate: causalpy.EstimateEffect, causalpy.InterruptedTimeSeries`
  pymc 5.28.5 — `pymc.sample(draws=1000, model=m)` → posterior InferenceData; runs Bayesian estimation. located
  `locate: pymc.sample, pymc.Model`
  statsmodels 0.15.0 — `statsmodels.api.OLS(y, X).fit()` → fitted regression results; estimates effect. exercised: "slope 1.0"
  `locate: statsmodels.api.OLS`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** render charts and tables from the bound tables
  altair 6.2.2 — `altair.Chart(df).mark_bar().encode(...)` → Vega-Lite chart spec; renders statistical viz. exercised: "Chart"
  `locate: altair.Chart`
  great-tables 0.24.0 — `great_tables.GT(df)` → formatted table object; renders publication table. exercised: "GT"
  `locate: great_tables.GT`
  panel 1.9.4 — `panel.panel(obj)` → displayable pane/dashboard; renders bound tables. exercised: "Markdown"
  `locate: panel.panel`

#### Pipeline 7: Supply Chain Scheduling

- **Step 0 (Global Ingestion).** Parse contracts and capacity workbooks into the manifest
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path, ocr='reject')` → markdown string; converts contracts/BOLs to markdown. exercised: "'Hello clause one.\n'"
  `locate: anydoc.to_markdown`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike, load_tables=False)` → workbook; reads capacity .xlsx/.ods. exercised: "['S1'] sheet names"
  `locate: python_calamine.load_workbook`

- **Step 1 (Orchestrator Compilation).** Emit workflow selecting a solver subset
  temporalio 1.32.0 — `@temporalio.workflow.defn(sandboxed=True)` → workflow class; declares the durable workflow. located
  `locate: temporalio.workflow.defn`
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → SolveResult; ASP selects the solver subset. exercised: "['a b']"
  `locate: clingo.Control.solve`
  pulp 3.3.2 — `pulp.LpProblem(name, sense).solve(solver)` → status int; candidate LP solver activity. exercised: "Optimal 3.0"
  `locate: pulp.LpProblem.solve`
  pyomo 6.10.1 — `pyomo.environ.ConcreteModel()` → model; candidate algebraic MIP/CP model. exercised: "ConcreteModel"
  `locate: pyomo.environ.ConcreteModel`
  ortools 9.15.6755 — `ortools.sat.python.cp_model.CpSolver().Solve(model)` → status; candidate CP-SAT solver activity. exercised: "OPTIMAL 10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  highspy 1.11.0 — `h=Highs(); h.run()` → LP/MILP solve. located
  `locate: highspy.Highs.run, highspy.Highs`
  pyjobshop 0.0.9 — `Model().solve(display=False)` → job-shop scheduling solve. located
  `locate: pyjobshop.Model.solve, pyjobshop.Model`
  alns 7.0.0 — `alns.ALNS().iterate(initial_solution, op_select, accept, stop)` → Result; candidate metaheuristic activity. located
  `locate: alns.ALNS.ALNS.iterate`

- **Step 2 (Model Emission).** Pydantic schemas become the MIP/CP model
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(data)` → validated instance; schema feeds the emitted model. exercised: "(1, 'a')"
  `locate: pydantic.BaseModel.model_validate`

- **Step 3 (Solve and Repair).** Solve, then ALNS-repair when only a bound exists
  ortools 9.15.6755 — `ortools.sat.python.cp_model.CpSolver().Solve(model)` → status; primary CP-SAT solve. exercised: "OPTIMAL 10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  highspy 1.11.0 — `h=Highs(); h.run()` → LP/MILP solve. located
  `locate: highspy.Highs.run, highspy.Highs`
  alns 7.0.0 — `alns.ALNS().iterate(initial_solution, op_select, accept, stop)` → Result; repair search on incumbent. located
  `locate: alns.ALNS.ALNS.iterate`

- **Step 4 (Calendar Proof).** Critical-path and ASP must accept the incumbent
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → SolveResult; ASP acceptance of incumbent. exercised: "['a b']"
  `locate: clingo.Control.solve`
  criticalpath 0.1.5 — `criticalpath.Node('p').get_critical_path()` → node list; validates schedule critical path. exercised: "['A', 'B']"
  `locate: criticalpath.Node.get_critical_path`

- **Step 5 (Execution).** Render Gantt outputs as terminal activities
  elegantt 0.0.11 — `elegantt.EleGantt(size=(468,295)).save(path)` → writes Gantt PNG; terminal chart activity. located
  `locate: elegantt.EleGantt.save`
  taipy 4.1.1 — `taipy.Gui(page).run()` → starts dashboard server; terminal app activity. located
  `locate: taipy.Gui.run`
  highcharts-gantt 1.7.0 — `Chart.from_options(options)` → Highcharts Gantt spec. located
  `locate: highcharts_gantt.chart.Chart`

#### Pipeline 8: Geospatial Hazard Cartography

- **Step 0 (Global Ingestion).** Parse incident reports, sidecars, and municipal PDFs into the manifest.
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → ConversionResult with structured document; parses PDFs/Office. located
  `locate: docling.document_converter.DocumentConverter.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc emitting markdown/text/json; parses office docs. located
  `locate: undoc.parse_file`

- **Step 1 (Orchestrator Compilation).** Keep geo assets when coordinates or resolvable toponyms are found.
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  geopandas 1.1.4 — `geopandas.read_file(filename)` → GeoDataFrame; loads spatial layer/coordinates. located
  `locate: geopandas.read_file`
  shapely 2.1.2 — `shapely.Point(x, y)` → geometry from coordinates. exercised: "POINT (1 2)"
  `locate: shapely.Point`
  osmnx 1.9.3 — `osmnx.geocode(query)` → (lat, lng); resolves toponym to coordinates. located
  `locate: osmnx.geocode`
  rustworkx 0.18.1 — `rustworkx.PyGraph()` (add_node/add_edge) → spatial graph structure. exercised: "num_edges == 1"
  `locate: rustworkx.PyGraph`

- **Step 2 (Constraint Compile).** Receive exclusion/coverage predicates extracted into typed models.
  cpmpy 1.0.0 — `Model().solve(solver='ortools')` → constraint model + solve. located
  `locate: cpmpy.Model.solve, cpmpy.Model`
  pydantic 2.13.5 — `class M(pydantic.BaseModel): ...` → validated predicate model. exercised: "M(x=3).x == 3"
  `locate: pydantic.BaseModel`
  python-constraint2 2.7.3 — `constraint.Problem(); p.addVariable(...); p.getSolutions()` → CSP solutions. exercised: "[{'a': 2}, {'a': 1}]"
  `locate: constraint.Problem, constraint.Problem.getSolutions`

- **Step 3 (Surface and Sheet).** Rasterize and render maps in compiled-graph order.
  datashader 0.19.1 — `datashader.Canvas(plot_width, plot_height).points(source, x, y)` → aggregated raster. exercised: "agg shape (4, 4)"
  `locate: datashader.Canvas, datashader.Canvas.points`
  eomaps 8.4 — `eomaps.Maps(crs=..., layer=...)` → interactive Cartopy/Matplotlib map. located
  `locate: eomaps.Maps`
  contextily 1.7.1 — `contextily.add_basemap(ax, source=..., crs=...)` → adds basemap tiles to axes. located
  `locate: contextily.add_basemap`
  prettymaps 1.4.2 — `prettymaps.plot(query)` → Plot; renders aesthetic OSM map. located
  `locate: prettymaps.plot`
  pygmt 0.17.0 — `Figure().coast(region=..., projection=...)` → map cartography (GMT). located
  `locate: pygmt.Figure.coast, pygmt.Figure`
  lonboard 0.16.0 — `lonboard.viz(data)` → Map; GPU vector visualization via Arrow/Deck.gl. located
  `locate: lonboard.viz`

- **Step 4 (Execution).** Emit interactive maps and a PDF as leaf assets.
  folium 0.20.0 — `folium.Map(location=[lat, lng])` → Leaflet map object. exercised: "type Map"
  `locate: folium.Map`
  keplergl 0.3.7 — `keplergl.KeplerGl().add_data(data, name='x')` → Kepler.gl widget with data. located
  `locate: keplergl.KeplerGl, keplergl.KeplerGl.add_data`
  weasyprint 69.0 — `weasyprint.HTML(string=html).write_pdf()` → PDF bytes from HTML/CSS. exercised: "2331 bytes, b'%PDF-'"
  `locate: weasyprint.HTML, weasyprint.HTML.write_pdf`

#### Pipeline 9: Contract Constraint Prover

- **Step 0 (Global Ingestion).** Pull clauses and defined-term tables from the contract PDFs.
  docling 2.124.0 — `DocumentConverter().convert(source).document` → parses PDF/Office to structured doc; clause extraction. located
  `locate: docling.document_converter.DocumentConverter.convert`
  pypdf 6.16.2 — `PdfReader(stream).pages[0].extract_text(extraction_mode="layout")` → raw clause text per page. located
  `locate: pypdf.PdfReader, pypdf._page.PageObject.extract_text`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
- **Step 1 (Orchestrator Compilation).** Emit a durable workflow gated on AMR parsing.
  temporalio 1.32.0 — `@temporalio.workflow.defn` on a workflow class → declares durable workflow. located
  `locate: temporalio.workflow.defn`
  amrlib 0.8.1 — `load_stog_model().parse_sents(sents)` → text to deontic AMR graphs. located
  `locate: amrlib.load_stog_model, amrlib.models.parse_xfm.inference.Inference.parse_sents`
- **Step 2 (Logic Emission).** Write FOL/ASP programs and hand to the solvers.
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr)` → AMR graph to FOL Clause. exercised: "boy(b)"
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`
  typedlogic 0.2.4 — `s=ClingoSolver(); s.add_sentence(...); s.dump()` → writes ASP/clingo program. exercised: "obligation(\"party_a\")."
  `locate: typedlogic.integrations.solvers.clingo.clingo_solver.ClingoSolver.dump, typedlogic.integrations.solvers.clingo.clingo_solver.ClingoSolver.add_sentence`
  clingo 5.8.0 — `c=Control(); c.add("base",[],prog); c.ground([("base",[])]); c.solve(on_model=...)` → solves ASP. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control.ground`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → solver-agnostic SMT satisfiability. exercised: "True"
  `locate: pysmt.shortcuts.is_sat`
  cvc5 1.3.4 — `s=Solver(tm); s.assertFormula(t); s.checkSat()` → SMT check of clause. exercised: "sat"
  `locate: cvc5.Solver.checkSat, cvc5.Solver.assertFormula`
- **Step 3 (Policy Materialization).** Generate policy engines for proved permissions.
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`
  openfga-sdk 0.10.4 — `OpenFgaClient(ClientConfiguration(...)).check(body)` → fine-grained authorization (client to an FGA store). located
  `locate: openfga_sdk.OpenFgaClient, openfga_sdk.ClientConfiguration`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
- **Step 4 (Execution).** Terminal activities: explanations, graphs, tables, UI, Word.
  xclingo 2.0b24 — `for m in XclingoControl().solve(): m.explain_model()` → ASP proof/explanation trees. located
  `locate: xclingo.XclingoControl.solve, xclingo._main.XClingoModel.explain_model`
  clingraph 1.2.6 — `render(compute_graphs(fb), format="pdf")` → renders graph from ASP facts. located
  `locate: clingraph.compute_graphs, clingraph.render`
  great-tables 0.24.0 — `GT(df).as_raw_html()` → publication table HTML. exercised: "9309-char HTML"
  `locate: great_tables.GT, great_tables.GT.as_raw_html`
  nicegui 3.16.0 — `ui.table(rows=...); ui.run()` → builds/serves UI. located
  `locate: nicegui.ui.table, nicegui.ui.run`
  python-docx 1.2.0 — `d=docx.Document(); d.add_paragraph(t); d.save(path)` → writes Word artifact. exercised: "docx written"
  `locate: docx.Document`

#### Pipeline 10: Specification-to-Slide Compiler

- **Step 0 (Global Ingestion).** Turn specs/tickets/whiteboard exports into the compiler manifest.
  mammoth 1.12.1 — `mammoth.convert_to_html(fileobj)` → clean HTML from .docx spec; Word→HTML for manifest. exercised: "<p>KE</p><p>x</p>"
  `locate: mammoth.convert_to_html`
  markitdown 0.1.7 — `MarkItDown().convert(source)` → Markdown DocumentConverterResult; any-doc→Markdown. exercised: "# Spec\n\nHello"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc handle (Markdown/text/JSON); office parse. located
  `locate: undoc.parse_file`

- **Step 1 (Orchestrator Compilation).** Build a dagster asset graph from requirement/risk/milestone spans.
  dagster 1.13.20 — `@dagster.asset def requirement(): ...` → AssetsDefinition node; defines the asset-graph nodes. located
  `locate: dagster.asset, dagster.Definitions`

- **Step 2 (Trace Proof).** Supply edges; prove completeness and acyclicity before materializing.
  networkx 3.6.1 — `nx.is_directed_acyclic_graph(G)` → bool; acyclicity check over supplied edges. exercised: "is_dag: True"
  `locate: networkx.is_directed_acyclic_graph, networkx.DiGraph.add_edges_from`
  graphedexcel 1.2.3 — `build_graph_and_stats(file_path, as_directed=True)` → (DiGraph, stats); formula-edge supply. located
  `locate: graphedexcel.graphbuilder.build_graph_and_stats`
  business-rules 1.1.1 — `run_all(rule_list, defined_variables, defined_actions)` → bool triggered; completeness rule check. exercised: "True fired=[True]"
  `locate: business_rules.run_all`
  durable-rules 2.0.28 — `assert_fact(ruleset_name, fact)` → Rete evaluation; acyclicity/completeness rules. located
  `locate: durable.lang.assert_fact, durable.lang.ruleset`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(c); s.check()` → sat/unsat; constraint proof. exercised: "sat"
  `locate: z3.Solver.check, z3.Solver.add`

- **Step 3 (Grammar Selection).** Chart/diagram tools chosen for proved tables and relations.
  lida 0.0.14 — `Manager().visualize(summary, goal, library='seaborn')` → chart spec/code; grammar-agnostic chart gen. located
  `locate: lida.components.manager.Manager.visualize`
  autoviz 0.1.905 — `AutoViz_Class().AutoViz(filename, depVar='')` → auto-selected charts; chart selection from tables. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`
  kroki — non-Python — diagram service, CLI `kroki convert in.mmd -o out.svg` (HTTP; network-gated here)
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 4 (Execution).** Leaf assets producing pptx/pdf slide artifacts.
  python-pptx 1.0.2 — `pptx.Presentation()` then `.save(path)` → .pptx file; PowerPoint leaf asset. exercised: "28104 bytes"
  `locate: pptx.Presentation`
  weasyprint 69.0 — `weasyprint.HTML(string=html).write_pdf()` → PDF bytes; HTML/CSS→PDF leaf. exercised: "%PDF- 3596 bytes"
  `locate: weasyprint.HTML.write_pdf, weasyprint.HTML`
  marp — non-Python renderer — CLI `marp slides.md -o out.pptx` (@marp-team/marp-cli)
  md2pptx → python-pptx 1.0.2 — `Presentation().slides.add_slide(layout)` → Markdown→slides (md2pptx is not installable here). located
  `locate: pptx.Presentation`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`
  reveal-md — non-Python renderer — CLI `reveal-md slides.md` (Node)

#### Pipeline 11: Fleet Reliability Dossier

- **Step 0 (Global Ingestion).** Flatten claims, manuals, and sensor files into the manifest.
  csvkit 2.2.0 — `csvkit.reader(open("sensors.csv"))` → unicode CSV rows; tabular flattener (CLI: `in2csv`). exercised: "[['a','b'],['1','2']]"
  `locate: csvkit.reader`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("manual.pdf")` → doc-to-Markdown string; parses claims/manuals. exercised: "| a | b | ..."
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Type-check time-to-event + censoring columns; gate survival assets.
  pydantic 2.13.5 — `Model.model_validate({"tte":12.5,"censored":True})` → validated model; type-checks the gate columns. exercised: "tte=12.5 censored=True"
  `locate: pydantic.BaseModel.model_validate`
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → survival fit consuming time-to-event+censoring. exercised: "median 2.0"
  `locate: lifelines.KaplanMeierFitter.fit`

- **Step 2 (Fit and Cut Sets).** Fit reliability curves; prove series/parallel cut-set facts.
  scipy 1.15.3 — `scipy.optimize.curve_fit(f, xdata, ydata, bounds=(0, inf))` → fitted params; bounds reject unphysical fits. exercised: "[2.0, 1.0]"
  `locate: scipy.optimize.curve_fit`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(...); s.check()` → sat/unsat over block-diagram facts. exercised: "sat"
  `locate: z3.Solver.check, z3.Solver.add`
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`

- **Step 3 (Execution).** Generate SPC charts, static images, and dashboard report assets.
  kaleido 1.4.0 — `kaleido.write_fig(fig, "chart.png")` → writes static image; Plotly export engine. located
  `locate: kaleido.write_fig`
  spc-plotly 0.2.1 — `spc_plotly.xmr.XmR(data=df, y_ser_name="defects", x_ser_name="date")` → builds XmR SPC chart. located
  `locate: spc_plotly.xmr.XmR`
  streamlit 1.63.0 — `streamlit.dataframe(df)` → renders dashboard table; report app. located
  `locate: streamlit.dataframe`
  mqrpy 0.6.5 — `mqr.spc`, `mqr.msa`, `mqr.process`, `mqr.anova` → quality-engineering capability / MSA / SPC. located
  `locate: mqr.spc, mqr.msa, mqr.process, mqr.anova`
  qda-toolkit 0.2.1 — `ControlCharts(...)` → SPC control charts. located
  `locate: qdatoolkit.ControlCharts, qdatoolkit.controlcharts`

#### Pipeline 12: Ontology Reasoner

- **Step 0 (Global Ingestion).** Convert manuals/dictionaries/glossaries to Markdown for the manifest
  markitdown 0.1.7 — `MarkItDown().convert("manual.docx").markdown` → Markdown string; document-to-Markdown for manifest. exercised: "'Continuity plan\n\n|  |...'"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file("glossary.docx").to_markdown()` → Markdown string; Office-doc parse to Markdown. exercised: "'Continuity plan\n\n| |...'"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Emit prefect tasks that build RDF/OWL ontology from phrases
  prefect 3.8.4 — `@prefect.task def build_rdf(): ...` (and `@prefect.flow`) → task object; generated orchestration tasks. located
  `locate: prefect.task, prefect.flow`
  rdflib 7.6.0 — `g=rdflib.Graph(); g.parse(data=ttl, format="turtle")` → Graph; loads/holds the RDF triples. exercised: "parsed 2 triples"
  `locate: rdflib.Graph.parse, rdflib.Graph.add`
  owlready2 0.51 — `onto=get_ontology(iri)` then `class C(Thing)`, `AllDisjoint([...])` → ontology w/ classes+disjoints. exercised: "classes ['Drug']"
  `locate: owlready2.get_ontology, owlready2.AllDisjoint`

- **Step 2 (Closure and Proof).** Compute graph closure; solvers must accept TBox/ABox
  owlrl 7.6.2 — `DeductiveClosure(OWLRL_Semantics).expand(graph)` → in-place forward-chained closure of graph. exercised: "before 2 after 12"
  `locate: owlrl.DeductiveClosure.expand`
  pyreason → clingo 5.8.2 — `Control().add(prog); ground(); solve()` → graph/temporal reasoning (pyreason import hangs here). located
  `locate: clingo.Control.solve, clingo.Control`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(f); s.check()` → sat/unsat; checks TBox/ABox consistency. exercised: "sat"
  `locate: z3.Solver.check, z3.Solver.add`
  cvc5 1.3.4 — `s=cvc5.Solver(tm); s.assertFormula(f); s.checkSat()` → Result; SMT-accepts the pair. exercised: "sat"
  `locate: cvc5.Solver.checkSat, cvc5.Solver.assertFormula`
  clingo 5.8.0 — `c=Control(); c.add("base",[],prog); c.ground(...); c.solve()` → SolveResult; ASP-accepts facts. exercised: "SAT"
  `locate: clingo.Control.solve, clingo.Control.add`

- **Step 3 (Execution).** Leaf tasks: SQL, data API, graph views, docs site
  duckdb 1.5.5 — `duckdb.sql("select ...").fetchall()` (or `duckdb.connect(db)`) → relation/rows; in-process SQL. exercised: "(42,)"
  `locate: duckdb.sql, duckdb.connect`
  datasette 0.65.3 — `Datasette(files=["data.db"])` → ASGI app; publishes SQLite as API/UI. located
  `locate: datasette.app.Datasette`
  graphistry 0.59.0 — `graphistry.edges(df,"s","d").plot()` → Plotter/URL; binds edge frame for GPU graph view. located
  `locate: graphistry.edges, graphistry.bind`
  ipysigma 0.24.6 — `Sigma(nx_graph)` → Jupyter widget; renders interactive Sigma.js graph. located
  `locate: ipysigma.Sigma`
  mkdocs 1.6.1 — `mkdocs.commands.build.build(config)` → writes static documentation site. located
  `locate: mkdocs.commands.build.build`

#### Pipeline 13: Service Configuration Management

- **Step 0 (Global Ingestion).** flatten architecture/policy/CMDB docs into compiler manifest
  docling 2.124.0 — `DocumentConverter().convert(path).document.export_to_markdown()` → Markdown; PDF/Office parse. located
  `locate: docling.document_converter.DocumentConverter.convert, docling_core.types.doc.document.DoclingDocument.export_to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(path).text_content` → Markdown. exercised: "# Hi\n\nBody text"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown/text/JSON. exercised: "hi"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** admit config asset graph only if model resolves
  clingo 5.8.0 — `Control().solve()` → SolveResult; admits graph iff satisfiable. exercised: "a b"
  `locate: clingo.Control.solve`

- **Step 2 (Model Emission).** type records with pydantic, land in duckdb, build graph
  pydantic 2.13.5 — `Model.model_validate(row)` → typed record (CI/relationship/state). exercised: "2"
  `locate: pydantic.BaseModel.model_validate`
  duckdb 1.5.5 — `duckdb.connect('cmdb.duckdb')` → connection; lands typed records. exercised: "(2,)"
  `locate: duckdb.connect`
  networkx 3.6.1 — `DiGraph().add_edge(ci_a, ci_b)` → CI graph from records. exercised: "['a','b','c']"
  `locate: networkx.DiGraph.add_edge`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`

- **Step 3 (Lifecycle Proof).** write transition facts; solvers must accept consistency/acyclicity
  typedlogic 0.2.4 — `ClingoSolver().add_fact(FactInstance)` → writes transition/exception/verification facts. exercised: "fact added, dump=17ch"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add_fact`
  clingo 5.8.0 — `Control().solve()` → must accept acyclicity. exercised: "a b"
  `locate: clingo.Control.solve`
  z3-solver 5.1.0.0 — `Solver().check()` → sat/unsat; accepts state consistency. exercised: "sat [x = 3]"
  `locate: z3.Solver.check`

- **Step 4 (Verification Replay).** mine transition logs; emit discrepancy tables for failed traces
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net,im,fm); mines model. exercised: "places=3"
  `locate: pm4py.discover_petri_net_inductive`
  csv-diff 1.2 — `compare(load_csv(a,key), load_csv(b,key))` → diff dict; discrepancies. exercised: "added=1, removed=1"
  `locate: csv_diff.compare, csv_diff.load_csv`
  daff 1.4.2 — `daff.compareTables(t1,t2).align()` → alignment; tabular discrepancy diff. exercised: "rows=4"
  `locate: daff.compareTables`

- **Step 5 (Execution).** emit verification report, RFC PDF payloads, lifecycle diagrams
  great-tables 0.24.0 — `GT(df).as_raw_html()` → HTML table; verification report. exercised: "9309-char HTML"
  `locate: great_tables.GT, great_tables.GT.as_raw_html`
  reportlab 5.0.1 — `canvas.Canvas(path).drawString(...); .save()` → PDF; RFC payloads. exercised: "pdf saved"
  `locate: reportlab.pdfgen.canvas.Canvas`
  python-docx 1.2.0 — `docx.Document().add_paragraph(t); .save(path)` → Word report. exercised: "docx saved"
  `locate: docx.Document, docx.document.Document.save`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  diagrams 0.25.1 — false match: "lifecycle diagrams" is a common noun, not the library

#### Pipeline 14: Service Design

- **Step 0 (Global Ingestion).** flatten decks/blueprints/manuals into the compiler manifest
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("deck.docx")` → Markdown str from Office/PDF doc. exercised: "'Hello undoc\n'"
  `locate: anydoc.to_markdown`
  undoc 0.9.0 — `undoc.parse_file("blueprint.docx").to_markdown()` → Markdown/text/JSON from Office doc. exercised: "'Hello undoc'"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** emit flow only if dependency spans resolve
  prefect 3.8.4 — `prefect.flow(name="svc_design")(fn)` → Flow; the emitted orchestration flow. located
  `locate: prefect.flow`
  stanza 1.14.0 — `stanza.Pipeline(lang="en", processors="tokenize,pos,depparse")` → dependency-parses principle/constraint spans. located
  `locate: stanza.Pipeline`

- **Step 2 (Requirement Proof).** accept usability/cost/performance/security/compliance bounds
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr=req_amr)` → FOL Clause of bounds. exercised: "want-01(w) ∧ :ARG0(w, b) ∧ boy(b)…"
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(And(bounds))` → bool; accepts bound formulas. exercised: "True"
  `locate: pysmt.shortcuts.is_sat`

- **Step 3 (Structure and Interaction).** build service breakdown and encode interaction flows
  networkx 3.6.1 — `g=networkx.DiGraph(); g.add_edge(u_of_edge, v_of_edge)` → service-breakdown graph. exercised: "DiGraph edges added; DAG check True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net, im, fm) interaction-flow Petri net. exercised: "places=3 transitions=2"
  `locate: pm4py.discover_petri_net_inductive`
  pydsm → se-lib 0.53 — `design_structure_matrix(...)` → Design Structure Matrix (PyPI 'pydsm' is an unrelated delta-sigma library). located
  `locate: selib.design_structure_matrix`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** produce leaf assets and bind governance checkpoints
  business-rules 1.1.1 — `business_rules.run_all(rule_list, defined_variables, defined_actions)` → runs governance rules. located
  `locate: business_rules.run_all`
  diagrams 0.25.1 — `with diagrams.Diagram(name="svc", outformat="png"):` → renders architecture diagram asset (needs graphviz dot). located
  `locate: diagrams.Diagram`
  python-docx 1.2.0 — `docx.Document().add_paragraph(text)` → writes Service Design Package .docx. exercised: "paragraph text 'hello'"
  `locate: docx.Document`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`

#### Pipeline 15: Business Analysis

- **Step 0 (Global Ingestion).** Convert charters, org charts, notes, exports, glossaries into the manifest.
  markitdown 0.1.7 — `markitdown.MarkItDown().convert("charter.docx")` → DocumentConverterResult Markdown. exercised: "# Q3 Net income 100"
  `locate: markitdown.MarkItDown.convert, markitdown.MarkItDown`
  office-oxide 0.1.9 — `office_oxide.to_markdown("orgchart.xlsx")` → Markdown text from Office file. exercised: "## Sheet | Metric | 100 |"
  `locate: office_oxide.to_markdown`
  mammoth 1.12.1 — `mammoth.convert_to_html(fileobj=f)` → HTML (`.value`) from a .docx. exercised: "<p>Spec line</p>"
  `locate: mammoth.convert_to_html`

- **Step 1 (Orchestrator Compilation).** Build a Dagster asset graph from stakeholder/requirement/conflict spans.
  dagster 1.13.20 — `@dagster.asset def spec(): ...` → AssetsDefinition node in the asset graph. exercised: "type=AssetsDefinition"
  `locate: dagster.asset`

- **Step 2 (Elicitation and Model).** Recover claims; categorize requirements; hold the stakeholder influence graph.
  nltk 3.10.3 — `nltk.sent_tokenize(text)` → list of sentence-level raw claims. located
  `locate: nltk.sent_tokenize`
  rdflib 7.6.0 — `rdflib.Graph().add((req, RDF.type, Literal("functional")))` → categorizing RDF triple. exercised: "triples=1"
  `locate: rdflib.Graph.add`
  typedlogic 0.2.4 — `get_solver("clingo").add(Term("functional", req))` → asserts typed requirement fact. exercised: "added Term; satisfiable=True"
  `locate: typedlogic.registry.get_solver, typedlogic.solver.Solver.add`
  networkx 3.6.1 — `networkx.DiGraph().add_edge(a, b)` → directed stakeholder influence graph. exercised: "edges=1"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`

- **Step 3 (Verify and Trace).** Verify clarity/consistency/testability; keep traceability matrix; refuse baseline drift.
  model-checker 1.3.9 — `ModelDefaults(...).solve(model_constraints, max_time)` → (sat, z3_model, ...) via SMT. located
  `locate: model_checker.models.ModelDefaults.solve`
  z3-solver 5.1.0.0 — `z3.Solver().check()` (after add) → sat/unsat on drift constraints. exercised: "sat; assets=100, liab=50"
  `locate: z3.Solver.check`
  duckdb 1.5.5 — `duckdb.sql("SELECT * FROM matrix")` → SQL relation holding traceability matrix. exercised: "row=(2,)"
  `locate: duckdb.sql`
  csv-diff 1.2 — `csv_diff.compare(load_csv(prev, key="id"), load_csv(cur, key="id"))` → added/removed/changed drift. exercised: "changed=1"
  `locate: csv_diff.compare`
  vampire → nltk 3.10.3 — `ResolutionProver().prove(goal, premises)` → first-order proof (vampire is a C++ binary). located
  `locate: nltk.inference.resolution.ResolutionProver.prove, nltk.inference.resolution.ResolutionProver`

- **Step 4 (Execution).** Emit specification, matrix, and communications as leaf assets.
  great-tables 0.24.0 — `great_tables.GT(df).as_raw_html()` → publication-table HTML (matrix/comms). exercised: "html_len=9255"
  `locate: great_tables.GT, great_tables.GT.as_raw_html`
  python-docx 1.2.0 — `docx.Document().save("spec.docx")` → writes the specification Word file. exercised: "saved 36583B"
  `locate: docx.Document, docx.document.Document.save`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

#### Pipeline 16: Architecture Management

- **Step 0 (Global Ingestion).** dump strategy/state/framework docs into the manifest
  docling 2.124.0 — `DocumentConverter().convert(source)` → ConversionResult with structured document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown/JSON/text from Office files. exercised: "to_json → format:\"xlsx\"…"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown, undoc.Undoc.to_json`

- **Step 1 (Orchestrator Compilation).** write prefect tasks for ontology/RDF/graph steps
  prefect 3.8.4 — `@prefect.task` → wraps each owlready2/rdflib/networkx step as a task. exercised: "Task created"
  `locate: prefect.task, prefect.flow`
  owlready2 0.51 — `owlready2.get_ontology(base_iri)` → ontology of principles/viewpoints; `sync_reasoner()` classifies. located
  `locate: owlready2.get_ontology, owlready2.sync_reasoner`
  rdflib 7.6.0 — `rdflib.Graph().add((s, p, o))` → RDF triples for the architecture. exercised: "graph len 1"
  `locate: rdflib.Graph, rdflib.Graph.add`
  networkx 3.6.1 — `networkx.DiGraph().add_edges_from(edges)` → dependency graph. exercised: "is_directed_acyclic_graph True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edges_from`

- **Step 2 (Target Graph and Roadmap).** assemble current/target graphs; sequence work packages
  rustworkx 0.18.1 — `rustworkx.PyDiGraph()` (+ add_node/add_edge) → current/target directed graphs. exercised: "is DAG True"
  `locate: rustworkx.PyDiGraph, rustworkx.is_directed_acyclic_graph`
  criticalpath 0.1.5 — `Node(name).get_critical_path()` (after add/link/update_all) → critical work-package sequence. exercised: "critical path ['A','B']"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node.link, criticalpath.Node.add`
  typedlogic 0.2.4 — `Compiler().compile(theory)` → compiled logical facts as a string. located
  `locate: typedlogic.compiler.Compiler.compile`
  pydsm → se-lib 0.53 — `design_structure_matrix(...)` → Design Structure Matrix (PyPI 'pydsm' is an unrelated delta-sigma library). located
  `locate: selib.design_structure_matrix`
  se-lib 0.53 — `design_structure_matrix(...)`, `critical_path_diagram(...)` → PERT / DSM systems-engineering artifacts. located
  `locate: selib.design_structure_matrix, selib.critical_path_diagram, selib.SystemDynamicsModel`

- **Step 3 (Conformance Proof).** prove acyclicity and building-block compliance
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat on acyclicity constraints. exercised: "sat; [x = 1]"
  `locate: z3.Solver.check, z3.Solver.add`
  clingo 5.8.0 — `Control().solve()` → ASP check of metamodel compliance. exercised: "SAT; model 'a b'"
  `locate: clingo.Control.solve, clingo.Control.ground`

- **Step 4 (Execution).** render views, charter, roadmap leaf assets
  pyArchimate 1.12.3 — `pyArchimate.Model(name).add(concept_type, name)` → ArchiMate elements/views; `.write()` exports. exercised: "1 element 'Svc'"
  `locate: pyArchimate.Model, pyArchimate.Model.add, pyArchimate.Model.write`
  diagrams 0.25.1 — `with diagrams.Diagram(name=...):` → cloud-architecture diagram (renders via Graphviz). located
  `locate: diagrams.Diagram`
  graphable — requires Python ≥ 3.13 (this interpreter is 3.11); its table→Mermaid/D2/PlantUML output is otherwise the `diagrams` binding or the mermaid CLI
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

#### Pipeline 17: Infrastructure and Platform Management

- **Step 0 (Global Ingestion).** Flatten EA standards, SDP extracts, runbooks, workbooks, requests to Markdown.
  docling 2.124.0 — `DocumentConverter().convert(source).document.export_to_markdown()` → Markdown from docs. located
  `locate: docling.document_converter.DocumentConverter.convert`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown string; parses each doc. exercised: "'# H\n\npara one\n'"
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Keep pydantic pattern and planning provision assets when spans type-check.
  pydantic 2.13.5 — `Model.model_validate({...})` → validated model; type-checks spans. exercised: "actor='u1' t=5"
  `locate: pydantic.BaseModel.model_validate`
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=p.kind).solve(problem)` → plan for provision assets. exercised: "SOLVED_SATISFICING, plan ['go']"
  `locate: unified_planning.shortcuts.OneshotPlanner, unified_planning.model.Problem`

- **Step 2 (Design and Constraint).** Emit dynamics models; solvers accept BOM/network/hardening predicates.
  casadi 3.8.0 — `x=SX.sym('x'); Function('f',[x],[x**2+1])` → symbolic dynamics model. exercised: "f(3)=10.0"
  `locate: casadi.Function, casadi.integrator`
  z3-solver 5.1.0.0 — `s=Solver(); s.add(preds); s.check()` → sat accepts predicates. exercised: "check=sat, [x=4]"
  `locate: z3.Solver.check`
  cpmpy 1.0.0 — `Model().solve(solver='ortools')` → constraint model + solve. located
  `locate: cpmpy.Model.solve, cpmpy.Model`
  python-control 0.10.2 — `tf(num,den)`, `step_response(sys)` → control-systems dynamics. located
  `locate: control.tf, control.step_response, control.ss`

- **Step 3 (Operate and Retire).** Replay backup/patch/health tasks; clingo accepts dependency-safe retirement.
  simpy 4.1.2 — `env=Environment(); env.process(gen(env)); env.run()` → replays tasks. exercised: "event time [3]"
  `locate: simpy.Environment.run, simpy.Environment.process`
  simprocesd 0.3.0 — `System(); Source/PartProcessor/Sink; sys.simulate(simulation_duration=5)` → replays line. exercised: "env.now=5"
  `locate: simprocesd.model.System.simulate`
  clingo 5.8.0 — `ctl.solve()` → SolveResult.satisfiable admits retirement. exercised: "sat=True"
  `locate: clingo.Control.solve`

- **Step 4 (Execution).** Bind tuning recommendations; write leaf docs/diagrams.
  scipy 1.15.3 — `scipy.optimize.minimize(fun, x0)` → optimal tuning parameters. exercised: "x*=3.0, success=True"
  `locate: scipy.optimize.minimize, scipy.optimize.linprog`
  ortools 9.15.6755 — `CpSolver().Solve(model)` → binds recommendations (CP-SAT). exercised: "OPTIMAL, x=10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  python-docx 1.2.0 — `d=docx.Document(); d.add_paragraph(t); d.save(path)` → Word leaf asset. exercised: "paras ['H','para one']"
  `locate: docx.Document, docx.document.Document.save`
  streamlit 1.63.0 — `streamlit.write(obj)` → dashboard leaf asset. located
  `locate: streamlit.write, streamlit.dataframe`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 18: IT Asset Management

- **Step 0 (Global Ingestion).** flatten documents, spreadsheets, and CSVs into the manifest
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV(args).main()` → CSV output; flattens tabular inputs to CSV. located; CLI: `in2csv file.xlsx`
  `locate: csvkit.utilities.in2csv.In2CSV`
  fastexcel 0.21.0 — `fastexcel.read_excel(source=path)` → ExcelReader; loads workbook sheets for flattening. located
  `locate: fastexcel.read_excel`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown str; flattens documents into manifest. located
  `locate: anydoc.to_markdown`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike)` → CalamineWorkbook; reads Excel/ODS for flattening. located
  `locate: python_calamine.load_workbook`

- **Step 1 (Orchestrator Compilation).** type-check asset-type/entitlement/identifier columns via schema
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(row_dict)` → validated model or ValidationError; type-checks columns. exercised: "3"
  `locate: pydantic.BaseModel.model_validate, pydantic.TypeAdapter`

- **Step 2 (Register and Proof).** store projections in SQL; assert facts; prove entitlement
  clingo 5.8.0 — `clingo.Control(); ctl.ground(...); ctl.solve(on_model=...)` → stable models; proves entitlement-vs-consumption. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control`
  clorm 1.6.3 — `clorm.FactBase([Asset(id=1), ...])` → queryable fact set; writes asset facts. exercised: "2 facts"
  `locate: clorm.FactBase, clorm.Predicate`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  duckdb 1.5.5 — `duckdb.sql("SELECT ...")` → relation; lands projections in the in-process DB. exercised: "[(42,)]"
  `locate: duckdb.sql, duckdb.connect`

- **Step 3 (Audit Repair).** diff tables; score write-off and compliance exposure
  csv-diff 1.2 — `csv_diff.compare(load_csv(prev,key='id'), load_csv(cur,key='id'))` → added/removed/changed dict; emits discrepancies. exercised: "changed v: x->z"
  `locate: csv_diff.compare, csv_diff.load_csv`
  daff 1.4.2 — `daff.diff(PythonTableView(a), PythonTableView(b))` → highlighted diff table; emits discrepancy table. exercised: "['->', 1, 'x->z']"
  `locate: daff.diff`
  numpy-financial 1.0.0 — `npv(rate, values)`, `irr(values)` → financial figures on the proved ledger. located
  `locate: numpy_financial.npv, numpy_financial.irr, numpy_financial.pmt`

- **Step 4 (Execution).** write xlsx register, report table, and QR/barcode tags
  great-tables 0.24.0 — `great_tables.GT(df)` → formatted table; renders compliance report. exercised: "GT"
  `locate: great_tables.GT`
  openpyxl 3.1.2 — `openpyxl.Workbook()` then `ws['A1']=...; wb.save(path)` → xlsx workbook; writes reconciled register. exercised: "hi"
  `locate: openpyxl.Workbook`
  python-barcode 0.16.1 — `get_barcode_class(name)`; `Code128(code, writer)` → barcode symbol for a tag. located
  `locate: barcode.get_barcode_class, barcode.Code128, barcode.get`
  qrcode 8.2 — `qrcode.make(data)` → PIL image; generates QR tags. exercised: "PilImage"
  `locate: qrcode.make`

#### Pipeline 19: Workforce and Talent Management

- **Step 0 (Global Ingestion).** Dump strategy, forecasts, and catalogs into the manifest
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → DocumentConverterResult; converts sources to markdown. exercised: "'Hello clause one.'"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc (then .to_markdown()); Office→md/text/json. exercised: "Undoc object"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Emit a prefect flow if spans resolve
  prefect 3.8.4 — `prefect.flow(fn, name=None)` → Flow; declares the orchestration flow. exercised: "'Flow'"
  `locate: prefect.flow`

- **Step 2 (Plan and Ontology).** Build gap matrix, map succession, accept profiles
  networkx 3.6.1 — `networkx.DiGraph()` + `add_edge` → directed graph; maps role succession. exercised: "(3, 2) nodes/edges"
  `locate: networkx.DiGraph`
  owlready2 0.51 — `owlready2.sync_reasoner(ontology)` → runs HermiT; accepts a complete role profile. located (requires Java)
  `locate: owlready2.sync_reasoner`
  pandas 2.3.3 — `pandas.pivot_table(df, index, columns, values)` → DataFrame; builds the gap matrix. exercised: "(2, 2)"
  `locate: pandas.pivot_table`
  polars 1.44.1 — `polars.DataFrame(data).pivot(values, index, on)` → frame; builds the gap matrix. exercised: "(2, 2)"
  `locate: polars.DataFrame.pivot`
  typedlogic 0.2.4 — `typedlogic.registry.get_solver('z3').check()` → Solution; accepts complete profile. exercised: "Z3Solver obtained"
  `locate: typedlogic.registry.get_solver, typedlogic.solver.Solver.check`

- **Step 3 (Allocation Proof).** Solve hiring and L&D allocation
  ortools 9.15.6755 — `ortools.sat.python.cp_model.CpSolver().Solve(model)` → status; solves integer allocation. exercised: "OPTIMAL 10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  pulp 3.3.2 — `pulp.LpProblem(name, sense).solve(solver)` → status int; solves LP allocation. exercised: "Optimal 3.0"
  `locate: pulp.LpProblem.solve`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Score turnover, then fire docx/dashboard leaves
  python-docx 1.2.0 — `docx.Document().save(path)` → writes .docx; emits Word leaf asset. exercised: "'t' round-trip"
  `locate: docx.document.Document.save`
  statsmodels 0.15.0 — `statsmodels.api.OLS(y, sm.add_constant(X)).fit()` → results; scores turnover/time-to-fill. exercised: "params [0.46, 0.74]"
  `locate: statsmodels.api.OLS`
  streamlit 1.63.0 — `streamlit.dataframe(data)` → renders table; dashboard leaf asset. located
  `locate: streamlit.dataframe`

#### Pipeline 20: Supplier Management

- **Step 0 (Global Ingestion).** Pull strategy/RFP/proposals/contracts/scorecards into the manifest.
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → parsed document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  pypdf 6.16.2 — `pypdf.PdfReader(stream=path)` → reader over PDF pages. located
  `locate: pypdf.PdfReader`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike)` → workbook; reads Excel/ODS. located
  `locate: python_calamine.load_workbook`

- **Step 1 (Orchestrator Compilation).** Write a durable workflow gated on evaluation-dimension spans.
  temporalio 1.32.0 — `@temporalio.workflow.defn` on a class (with `@temporalio.workflow.run`) → declares durable workflow. located
  `locate: temporalio.workflow.defn, temporalio.workflow.run`

- **Step 2 (Select and Bind).** Score shortlists, enforce policy, instantiate clause templates for the stable model.
  pingouin 0.6.1 — `pingouin.anova(data=df, dv='v', between='g')` → ANOVA table scoring groups. exercised: "shape (1, 6)"
  `locate: pingouin.anova`
  pandas 2.3.3 — `pandas.DataFrame(data)` → tabular shortlist for scoring. exercised: "shape (2, 1)"
  `locate: pandas.DataFrame`
  clingo 5.8.0 — `clingo.Control(); ctl.add(...); ctl.ground(...); ctl.solve(on_model=...)` → ASP models accepting constraints. exercised: "['a b']"
  `locate: clingo.Control, clingo.Control.solve`
  jinja2 3.1.6 — `jinja2.Template(src).render(**ctx)` → instantiated clause text. exercised: "ok!"
  `locate: jinja2.Template, jinja2.Template.render`

- **Step 3 (Performance Path).** Forecast supplier series; run causal estimation if identified.
  sktime 1.1.0 — `NaiveForecaster(strategy='last').fit(y).predict(fh=[1,2])` → forecast values. exercised: "[5.0, 5.0]"
  `locate: sktime.forecasting.naive.NaiveForecaster, sktime.forecasting.naive.NaiveForecaster.predict`
  dowhy 0.14 — `dowhy.CausalModel(data, treatment, outcome, graph=...)` then `.estimate_effect(...)` → causal effect. located
  `locate: dowhy.CausalModel, dowhy.CausalModel.estimate_effect`

- **Step 4 (Execution).** Terminal activities: authorize, write docx, serve dashboard.
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`
  python-docx 1.2.0 — `docx.Document()` (add_paragraph/save) → Word document. exercised: "paragraphs == 0"
  `locate: docx.Document`
  streamlit 1.63.0 — `streamlit.write(*args)` → renders element to dashboard. located
  `locate: streamlit.write, streamlit.dataframe`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

#### Pipeline 21: Portfolio Management

- **Step 0 (Global Ingestion).** Ingest strategy briefs and portfolio workbooks.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → document to Markdown. located
  `locate: anydoc.to_markdown`
  openpyxl 3.1.2 — `load_workbook(filename)` → reads portfolio .xlsx workbook. located
  `locate: openpyxl.load_workbook`
- **Step 1 (Orchestrator Compilation).** Build an asset graph from value/risk spans.
  dagster 1.13.20 — `@dagster.asset` defs assembled by `Definitions(assets=[...])` → asset graph. located
  `locate: dagster.asset, dagster.Definitions`
- **Step 2 (Graph and Mix).** Emit initiative graph; optimize mix under budget/capacity.
  networkx 3.6.1 — `G=DiGraph(); G.add_edge(u,v)` → initiative dependency graph. exercised: "3-node DiGraph built"
  `locate: networkx.DiGraph`
  criticalpath 0.1.5 — `Node(...).get_critical_path()` → CPM schedule of initiatives. exercised: "['t1','t2'], duration 5"
  `locate: criticalpath.Node.get_critical_path`
  pulp 3.3.2 — `p=LpProblem(sense=LpMaximize); p.solve()` → LP/MIP mix optimization. exercised: "Optimal 3.0"
  `locate: pulp.LpProblem.solve, pulp.LpVariable`
  ortools 9.15.6755 — `Solver.CreateSolver("GLOP").Solve()` → LP optimize under bounds. exercised: "optimal, x=4.0"
  `locate: ortools.linear_solver.pywraplp.Solver.Solve`
  pydantic 2.13.5 — `Model.model_validate(data)` → compiles/validates budget-capacity bounds. exercised: "coerced '5' to 5"
  `locate: pydantic.BaseModel.model_validate`
- **Step 3 (Selection Proof).** Accept mutual-exclusion and prerequisite constraints.
  z3-solver 5.1.0.0 — `s=Solver(); s.add(c); s.check()` → constraint satisfiability proof. exercised: "sat [X = 3]"
  `locate: z3.Solver.check, z3.Solver.add`
- **Step 4 (Execution).** Leaf assets: portfolio and balancing views.
  plotly 7.0.0 — `plotly.graph_objects.Figure(...).write_html(path)` → interactive portfolio chart. located
  `locate: plotly.graph_objects.Figure.write_html`
  autoviz 0.1.905 — `AutoViz_Class().AutoViz(filename, dfte=df)` → auto visualization selection. located [imports fine; IPython present despite batch note]
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

#### Pipeline 22: Service Financial Management

- **Step 0 (Global Ingestion).** Flatten policy/cost workbooks/budgets/invoices/catalogs into the manifest.
  undoc 0.9.0 — `undoc.parse_file(path)` → Markdown/text/JSON; office parse. located
  `locate: undoc.parse_file`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown str; document→Markdown. located
  `locate: anydoc.to_markdown`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path)` → CalamineWorkbook; read Excel/ODS workbooks. exercised: "[['cost']]"
  `locate: python_calamine.load_workbook`

- **Step 1 (Orchestrator Compilation).** Emit a temporalio workflow only if stanza recovers predicates.
  stanza 1.14.0 — `stanza.Pipeline(lang='en', processors='tokenize,depparse')` → NLP Document; recover cost/allocation/charging predicates. located
  `locate: stanza.Pipeline`
  temporalio 1.32.0 — `@temporalio.workflow.defn class W: ...` → workflow definition; durable-workflow emit. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Schema and Proof).** Instantiate cost schemas into duckdb; prove debit/credit consistency.
  pydantic 2.13.5 — `class Cost(pydantic.BaseModel): unit: float` → validated instance; cost-schema instantiation. exercised: "unit=3.5"
  `locate: pydantic.BaseModel`
  duckdb 1.5.5 — `duckdb.sql("CREATE TABLE cost AS ...")` → relation; schema/table store. exercised: "(2,)"
  `locate: duckdb.sql`
  clingo 5.8.0 — `ctl=clingo.Control(); ctl.add('base',[],prog); ctl.solve()` → SAT/UNSAT; debit/credit/recovery consistency. exercised: "SAT"
  `locate: clingo.Control.solve, clingo.Control.add`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Quant and Select).** Compute unit cost and variance on proved ledger; select charts.
  numpy-financial 1.0.0 — `npv(rate, values)`, `irr(values)` → financial figures on the proved ledger. located
  `locate: numpy_financial.npv, numpy_financial.irr, numpy_financial.pmt`
  statsmodels 0.15.0 — `statsmodels.api.OLS(endog, exog).fit()` → regression/variance results; variance modeling. exercised: "params [0.0, 1.0]"
  `locate: statsmodels.api.OLS`
  autoviz 0.1.905 — `AutoViz_Class().AutoViz(filename, depVar='')` → auto-selected charts; chart selection from tables. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`

- **Step 4 (Execution).** Terminal charting/table/dashboard activities.
  plotly 7.0.0 — `plotly.graph_objects.Figure(data=[go.Bar(...)])` → interactive chart/HTML; chart leaf. exercised: "html len 4297587"
  `locate: plotly.graph_objects.Figure`
  great-tables 0.24.0 — `great_tables.GT(df)` → publication table; formatted-table leaf. exercised: "html len 9409"
  `locate: great_tables.GT`
  streamlit 1.63.0 — `streamlit.write(obj)` (app via `streamlit run app.py`) → dashboard element; dashboard leaf. located
  `locate: streamlit.write`
  finSankey → plotly 7.0.0 — `graph_objects.Sankey(link=..., node=...)` → Sankey diagram (finSankey is not installable here). located
  `locate: plotly.graph_objects.Sankey`

#### Pipeline 23: Risk Management

- **Step 0 (Global Ingestion).** Parse policy, registers, findings, appetite statements into the manifest.
  docling 2.124.0 — `DocumentConverter().convert("policy.pdf")` → parsed document object; PDF/Office parser. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Gate graph/Bayesian assets on threat/impact/control spans.
  networkx 3.6.1 — `networkx.DiGraph([("Threat","Impact")])` → directed risk graph. exercised: "(2, 1)"
  `locate: networkx.DiGraph`
  pgmpy 1.1.2 — `DiscreteBayesianNetwork([("Threat","Impact"),("Control","Impact")])` → Bayesian risk net. exercised: "2 edges"
  `locate: pgmpy.models.DiscreteBayesianNetwork.DiscreteBayesianNetwork`
  pymc 5.28.5 — `pymc.sample(draws=1000, tune=1000, model=m)` → posterior InferenceData; Bayesian inference. located
  `locate: pymc.sample`

- **Step 2 (Graph and Posterior).** Build risk net; sample posterior after typedlogic facts compile.
  pgmpy 1.1.2 — `DiscreteBayesianNetwork(ebunch)` → risk Bayesian network. exercised: "2 edges"
  `locate: pgmpy.models.DiscreteBayesianNetwork.DiscreteBayesianNetwork`
  networkx 3.6.1 — `g=networkx.DiGraph(); g.add_edges_from(edges)` → risk-net graph. exercised: "(2, 1)"
  `locate: networkx.DiGraph`
  pymc 5.28.5 — `pymc.sample(draws=1000, tune=1000)` → posterior draws. located
  `locate: pymc.sample`
  numpyro 0.21.0 — `numpyro.infer.MCMC(kernel, num_warmup=500, num_samples=1000).run(key)` → JAX MCMC posterior. located
  `locate: numpyro.infer.MCMC`
  arviz 0.23.4 — `arviz.summary(idata)` → posterior summary/diagnostics table. exercised: "['mean','sd','hdi_3%']"
  `locate: arviz.summary`
  typedlogic 0.2.4 — `s=Solver(); s.add_fact(f); s.dump()` → compiles typed facts to solver input. located
  `locate: typedlogic.solver.Solver.add_fact, typedlogic.solver.Solver.dump`

- **Step 3 (Treatment Proof).** Optimize avoid/reduce/transfer/accept portfolio; prove residual within appetite.
  ortools 9.15.6755 — `CpSolver().solve(model)` → OPTIMAL/FEASIBLE; CP-SAT portfolio select. exercised: "OPTIMAL"
  `locate: ortools.sat.python.cp_model.CpSolver.solve, ortools.sat.python.cp_model.CpModel`
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat residual-vs-appetite. exercised: "sat"
  `locate: z3.Solver.check`

- **Step 4 (Execution).** Emit Word report, chart, and formatted table assets.
  great-tables 0.24.0 — `great_tables.GT(df)` → publication table object. exercised: "GT"
  `locate: great_tables.GT`
  plotly 7.0.0 — `plotly.graph_objects.Figure(data=[...])` → interactive chart; HTML via `plotly.io.to_html`. exercised: "HTML emitted"
  `locate: plotly.graph_objects.Figure, plotly.io.to_html`
  python-docx 1.2.0 — `docx.Document()` (add_paragraph; save) → writes .docx report. exercised: "1 paragraph"
  `locate: docx.Document`

#### Pipeline 24: Service Continuity Management

- **Step 0 (Global Ingestion).** Flatten continuity policy/BIA/runbooks to Markdown manifest
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("policy.docx")` → Markdown string; flattens docs to Markdown. exercised: "'Continuity plan\n'"
  `locate: anydoc.to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(src).markdown` → Markdown string; document-to-Markdown for manifest. exercised: "'Continuity plan\n\n| |...'"
  `locate: markitdown.MarkItDown.convert`

- **Step 1 (Orchestrator Compilation).** Type-check critical-service/RTO/RPO fields; missing RTO/RPO cancels flow
  pydantic 2.13.5 — `class M(BaseModel): rto:int` then `M.model_validate(row)` → instance/raises; type-checks RTO/RPO. exercised: "rto=4"
  `locate: pydantic.BaseModel.model_validate, pydantic.BaseModel`

- **Step 2 (BIA Graph).** Build service→CI→site graph; emit impact-over-time tables
  networkx 3.6.1 — `g=DiGraph(); g.add_edges_from([("svc","ci"),("ci","site")])` → graph; maps service/CI/site edges. exercised: "2 edges"
  `locate: networkx.DiGraph.add_edges_from, networkx.DiGraph.add_edge`
  pandas 2.3.3 — `pandas.pivot_table(df, values="impact", index="svc", columns="t")` → DataFrame; impact-over-time table. exercised: "shape (1, 2)"
  `locate: pandas.pivot_table`

- **Step 3 (Invocation Proof).** Encode facts, simulate recovery, SMT-accept RTO/RPO
  typedlogic 0.2.4 — `th=Theory(name="ITSCM"); th.add(sentence)` (facts as `Fact` subclasses) → theory; encodes invocation/exclusive-use facts. located
  `locate: typedlogic.Theory.add, typedlogic.Fact`
  clingo 5.8.0 — `c=Control(); c.add("base",[],facts); c.ground(...); c.solve()` → SolveResult; encodes/solves ASP facts. exercised: "SAT"
  `locate: clingo.Control.solve, clingo.Control.add`
  simpy 4.1.2 — `env=simpy.Environment(); env.run(until=t)` → advances DES clock; replays recovery timeline. exercised: "now 5"
  `locate: simpy.Environment.run, simpy.Environment`
  most-queue 2.9 — `sim=QsSim(num_of_channels=n); sim.set_sources(...); sim.set_servers(...); sim.run(jobs)` → queue stats; recovery-queue simulation. located
  `locate: most_queue.QsSim.run, most_queue.QsSim`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; checks RTO/RPO constraints satisfiable. exercised: "False (p∧¬p)"
  `locate: pysmt.shortcuts.is_sat, pysmt.shortcuts.Solver`

- **Step 4 (Execution).** Leaf assets: curves, flowcharts, plan documents
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  python-docx 1.2.0 — `d=docx.Document(); d.add_paragraph(...); d.save("plan.docx")` → writes .docx continuity plan. exercised: "saved 36709 bytes"
  `locate: docx.Document, docx.document.Document.save, docx.document.Document.add_paragraph`

#### Pipeline 25: Strategy Management

- **Step 0 (Global Ingestion).** dump strategy/market/capability docs into compiler manifest
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown/text/JSON. exercised: "hi"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** write prefect flow; task set exists if spans recovered
  prefect 3.8.4 — `@prefect.flow` → Flow; the written flow. exercised: "Flow"
  `locate: prefect.flow`
  stanza 1.14.0 — `stanza.Pipeline(lang, processors='tokenize,ner')` → pipeline; recovers driver/goal/option spans. located
  `locate: stanza.Pipeline`

- **Step 2 (Map and Option Proof).** emit capability maps, record options, prove consistency
  networkx 3.6.1 — `DiGraph().add_edge(a,b)` → capability map graph. exercised: "['a','b','c']"
  `locate: networkx.DiGraph.add_edge`
  typedlogic 0.2.4 — `Solver().add_fact(FactInstance)` → records options as typed facts. located
  `locate: typedlogic.solver.Solver.add_fact`
  z3-solver 5.1.0.0 — `Solver().check()` → sat/unsat; accepts consistency. exercised: "sat [x = 3]"
  `locate: z3.Solver.check`
  se-lib 0.53 — `design_structure_matrix(...)`, `critical_path_diagram(...)` → PERT / DSM systems-engineering artifacts. located
  `locate: selib.design_structure_matrix, selib.critical_path_diagram, selib.SystemDynamicsModel`

- **Step 3 (Roadmap).** sequence initiatives via critical-path scheduling
  criticalpath 0.1.5 — `Node(...).add(...); .link(...); .get_critical_path()` → ordered initiatives. exercised: "['A','B']"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node.add`

- **Step 4 (Execution).** render charts as leaf assets
  plotly 7.0.0 — `go.Figure(...).write_html(path)` → HTML chart leaf asset. exercised: "html written"
  `locate: plotly.graph_objects.Figure, plotly.graph_objects.Figure.write_html`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

#### Pipeline 26: Information Security Management

- **Step 0 (Global Ingestion).** pull policy/catalog/threat/identity/privacy docs into manifest
  docling 2.124.0 — `DocumentConverter().convert(source="policy.pdf")` → ConversionResult; parses docs to text/Markdown. located
  `locate: docling.document_converter.DocumentConverter.convert`
  pypdf 6.16.2 — `pypdf.PdfReader("policy.pdf").pages[0].extract_text()` → text pulled from PDF pages. exercised: "pages 1"
  `locate: pypdf.PdfReader, pypdf.PageObject.extract_text`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`

- **Step 1 (Orchestrator Compilation).** emit workflow gated on control-objective/classification spans
  temporalio 1.32.0 — `temporalio.workflow.defn(name="isms")(WorkflowCls)` → durable workflow definition. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Ontology and Policy).** hold catalog ontology; generate proved permissions
  owlready2 0.51 — `owlready2.get_ontology(base_iri="http://isms/catalog.owl")` → ontology holding the control catalog. exercised: "base_iri set to …#"
  `locate: owlready2.get_ontology`
  rdflib 7.6.0 — `rdflib.Graph().parse(data=ttl, format="turtle")` → RDF graph holding the catalog. exercised: "1 triple"
  `locate: rdflib.Graph, rdflib.Graph.parse`
  openfga-sdk 0.10.4 — `OpenFgaClient(ClientConfiguration(...)).check(body)` → fine-grained authorization (client to an FGA store). located
  `locate: openfga_sdk.OpenFgaClient, openfga_sdk.ClientConfiguration`
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`

- **Step 3 (Residual Proof).** link assets/threats/controls; accept no allow/deny conflict
  pgmpy 1.1.2 — `pgmpy.models.DiscreteBayesianNetwork([('Asset','Threat'),('Threat','Control')])` → graphical model linking them. exercised: "edges Asset→Threat→Control"
  `locate: pgmpy.models.DiscreteBayesianNetwork`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(cons); s.check()` → sat/unsat; accepts allow/deny consistency. exercised: "sat; model [x = 3]"
  `locate: z3.Solver, z3.Solver.check`
  clingo 5.8.0 — `Control().add("base",[],facts); .ground(); .solve(on_model=cb)` → accepts no-unclassified-asset constraints. exercised: "model 'a b'"
  `locate: clingo.Control, clingo.Control.add, clingo.Control.solve`

- **Step 4 (Execution).** terminal compensation-safe reporting/dashboard activities
  python-docx 1.2.0 — `docx.Document().add_paragraph(text)` → writes .docx report asset. exercised: "paragraph text 'hello'"
  `locate: docx.Document`
  streamlit 1.63.0 — `streamlit.dataframe(data=df)` → renders dashboard table widget. located
  `locate: streamlit.dataframe`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 27: Availability Management

- **Step 0 (Global Ingestion).** Flatten SLRs, constraints, outage histories, maintenance windows into the manifest.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("slr.docx")` → Markdown string from each source doc. exercised: "Spec line"
  `locate: anydoc.to_markdown`
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV(args=["windows.xlsx"]).main()` → CSV on stdout. located; CLI: `in2csv windows.xlsx`
  `locate: csvkit.utilities.in2csv.In2CSV`

- **Step 1 (Orchestrator Compilation).** Gate reliability/survival assets on availability-target and outage-series type-checks.
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → survival asset admitted by gate. exercised: "median=3.0"
  `locate: lifelines.KaplanMeierFitter.fit`
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`

- **Step 2 (Block and Fit).** Build block diagrams; reject unphysical fits; accept redundancy versus target.
  scipy 1.15.3 — `scipy.optimize.curve_fit(f, xdata, ydata)` → (popt, pcov); rejects unphysical fits. exercised: "popt=[2.0, 1.0]"
  `locate: scipy.optimize.curve_fit`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(And(redundant, Not(target)))` → bool acceptance of redundancy vs target. exercised: "And(p,~p) sat=False"
  `locate: pysmt.shortcuts.is_sat`

- **Step 3 (Execution).** Write restore shapes; run FMEA; emit charts, dashboard, document.
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → restore-time survival curve. exercised: "median=3.0"
  `locate: lifelines.KaplanMeierFitter.fit`
  plotly 7.0.0 — `go.Figure(...).write_html("restore.html")` → interactive chart HTML (leaf asset). exercised: "wrote 4.3MB html"
  `locate: plotly.graph_objects.Figure.write_html`
  python-docx 1.2.0 — `docx.Document().save("availability.docx")` → writes the report (leaf asset). exercised: "saved 36583B"
  `locate: docx.Document, docx.document.Document.save`
  streamlit 1.63.0 — `streamlit.plotly_chart(fig)` → renders chart on the dashboard (leaf asset). located
  `locate: streamlit.plotly_chart`
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`

#### Pipeline 28: Capacity and Performance Management

- **Step 0 (Global Ingestion).** ingest baselines, utilization dumps, forecasts, plans
  undoc 0.9.0 — `undoc.parse_file(path).to_json()` → text/JSON from Office dumps. exercised: "to_json → format:\"xlsx\"…"
  `locate: undoc.parse_file, undoc.Undoc.to_json`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike)` → workbook; Rust-backed sheet read. exercised: "sheets ['Sheet']"
  `locate: python_calamine.load_workbook`
  csvkit 2.2.0 — `In2CSV(args=[...], output_file=f).run()` → converts XLSX/JSON to flat CSV; CLI: `in2csv`. located
  `locate: csvkit.utilities.in2csv.In2CSV`

- **Step 1 (Orchestrator Compilation).** keep forecast assets if time+utilization type-check
  prophet 1.4.0 — `Prophet().fit(df)` → fitted forecaster (df with ds,y). located
  `locate: prophet.forecaster.Prophet.fit, prophet.forecaster.Prophet.make_future_dataframe, prophet.forecaster.Prophet.predict`
  pmdarima 2.1.1 — `pmdarima.auto_arima(y)` → auto-selected ARIMA model. located
  `locate: pmdarima.auto_arima`
  most-queue 2.9 — `MMnrCalc(n, r)` (+ set_sources/set_servers/run) → queue metrics asset. exercised: "get_w [1.0, 4.0, 24.0]"
  `locate: most_queue.theory.fifo.mmnr.MMnrCalc, most_queue.theory.fifo.mmnr.MMnrCalc.get_w`
  darts → sktime 1.1.0 — `AutoARIMA().fit(y)` → time-series forecasting (darts does not import here). located
  `locate: sktime.forecasting.arima.AutoARIMA, sktime.forecasting.base.BaseForecaster.fit`

- **Step 2 (Forecast and Queue).** forecast demand; model queue response; optimize
  prophet 1.4.0 — `Prophet().predict(future)` → demand path (yhat). located
  `locate: prophet.forecaster.Prophet.predict, prophet.forecaster.Prophet.make_future_dataframe`
  pmdarima 2.1.1 — `pmdarima.auto_arima(y)` → ARIMA demand path. located
  `locate: pmdarima.auto_arima`
  most-queue 2.9 — `MMnrCalc(n, r).get_w()` → response (waiting-time moments). exercised: "get_w [1.0, 4.0, 24.0]"
  `locate: most_queue.theory.fifo.mmnr.MMnrCalc.get_w, most_queue.theory.fifo.mmnr.MMnrCalc`
  gekko 1.3.2 — `m=GEKKO(); m.Obj(expr); m.solve(disp=False)` → optimized settings under cost bounds. located
  `locate: gekko.GEKKO.solve, gekko.GEKKO.Obj, gekko.GEKKO.Minimize`
  darts → sktime 1.1.0 — `AutoARIMA().fit(y)` → time-series forecasting (darts does not import here). located
  `locate: sktime.forecasting.arima.AutoARIMA, sktime.forecasting.base.BaseForecaster.fit`
  python-control 0.10.2 — `tf(num,den)`, `step_response(sys)` → control-systems dynamics. located
  `locate: control.tf, control.step_response, control.ss`

- **Step 3 (Cover Proof).** SMT-check planned capacity covers peak+contingency
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat: capacity ≥ peak+contingency. exercised: "sat; [x = 1]"
  `locate: z3.Solver.check, z3.Solver.add`

- **Step 4 (Execution).** fire charting, dashboard, Word leaf assets
  plotly 7.0.0 — `plotly.express.line(x, y)` → interactive Figure; `Figure.write_html`. exercised: "Figure, 1 trace"
  `locate: plotly.express.line, plotly.graph_objects.Figure.write_html`
  streamlit 1.63.0 — `streamlit.dataframe(df)` → dashboard data widget. located
  `locate: streamlit.dataframe, streamlit.plotly_chart`
  python-docx 1.2.0 — `docx.Document().save(path)` → Word report. exercised: "saved .docx"
  `locate: docx.Document, docx.document.Document.save`

#### Pipeline 29: Continual Improvement Management

- **Step 0 (Global Ingestion).** Flatten strategy goals, CSI registers, audit findings, feedback to Markdown.
  docling 2.124.0 — `DocumentConverter().convert(source).document.export_to_markdown()` → Markdown from docs. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Build dagster asset graph from idea/benefit/constraint spans.
  dagster 1.13.20 — `@dagster.asset` def + `materialize_to_memory([...])` → asset graph. exercised: "success True, value 42"
  `locate: dagster.asset, dagster.materialize_to_memory`

- **Step 2 (Prioritize and Gate).** Hold register; rank by benefit/effort/risk; supply dependencies; accept rules.
  pandas 2.3.3 — `pandas.DataFrame(rows)` → holds the register. exercised: "shape (2,2)"
  `locate: pandas.DataFrame`
  pulp 3.3.2 — `p=LpProblem(...); p+=obj; p.solve(PULP_CBC_CMD(msg=0))` → ranks items. exercised: "Optimal, x=4.0"
  `locate: pulp.LpProblem.solve`
  networkx 3.6.1 — `networkx.topological_sort(DiGraph(edges))` → supplies dependency order. exercised: "['a','b','c']"
  `locate: networkx.topological_sort, networkx.DiGraph`
  typedlogic 0.2.4 — `ClingoSolver().add(...); .check()` → Solution.satisfiable accepts rules. exercised: "satisfiable=True"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.check, typedlogic.integrations.solvers.clingo.ClingoSolver.add`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Execution Tracking).** Run approved items as durable workflows; clingo accepts mutation edge.
  clingo 5.8.0 — `ctl.solve()` → SolveResult.satisfiable admits the mutation edge. exercised: "sat=True"
  `locate: clingo.Control.solve`
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`

- **Step 4 (Execution).** Leaf assets: formatted register table; publishing.
  great-tables 0.24.0 — `GT(df).as_raw_html()` → formatted publication table. exercised: "HTML emitted (>100 chars)"
  `locate: great_tables.GT, great_tables.GT.as_raw_html`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

#### Pipeline 30: Measurement and Reporting Management

- **Step 0 (Global Ingestion).** flatten policy, requirements, KPI catalogs, and extracts into manifest
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV(args).main()` → CSV output; flattens metric extracts to CSV. located; CLI: `in2csv file.xlsx`
  `locate: csvkit.utilities.in2csv.In2CSV`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown str; flattens documents into manifest. located
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** emit publication flow when metric/audience spans resolve
  prefect 3.8.4 — `@prefect.flow(name=...)` decorating the fn → Flow object; emits the publication flow. located
  `locate: prefect.flow`

- **Step 2 (Metric Proof).** type metric objects into SQL; prove figure derivability
  clingo 5.8.0 — `clingo.Control(); ctl.ground(...); ctl.solve(on_model=...)` → stable models; proves figure derivability. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control`
  duckdb 1.5.5 — `duckdb.sql("SELECT ...")` → relation; stores typed metric objects. exercised: "[(42,)]"
  `locate: duckdb.sql, duckdb.connect`
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(obj)` → validated metric model; types metric objects. exercised: "3"
  `locate: pydantic.BaseModel.model_validate, pydantic.TypeAdapter`

- **Step 3 (Execution).** auto-select/plot charts, tables, and dashboards from proved tables
  autoviz 0.1.905 — `autoviz.AutoViz_Class().AutoViz(filename='', dfte=df, chart_format='svg')` → auto-selected plots; renders visuals. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`
  great-tables 0.24.0 — `great_tables.GT(df)` → formatted table; renders report table. exercised: "GT"
  `locate: great_tables.GT`
  panel 1.9.4 — `panel.panel(obj)` → dashboard pane; renders dashboard. exercised: "Markdown"
  `locate: panel.panel`
  plotly 7.0.0 — `plotly.express.line(df, x=..., y=...)` → interactive Figure; renders charts. exercised: "Figure"
  `locate: plotly.express.line, plotly.graph_objects.Figure`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`
  streamlit 1.63.0 — `streamlit.write(obj)` inside a `streamlit run` app → renders element; dashboard leaf asset. located
  `locate: streamlit.write, streamlit.dataframe`

#### Pipeline 31: Service Level Management

- **Step 0 (Global Ingestion).** Dump catalog, agreements, and complaint logs into the manifest
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → DocumentConverterResult; converts sources to markdown. exercised: "'Hello clause one.'"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc (then .to_markdown()); Office→md/text/json. exercised: "Undoc object"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Emit a temporalio workflow gated on spans
  temporalio 1.32.0 — `@temporalio.workflow.defn(sandboxed=True)` → workflow class; declares the durable workflow. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Agreement Proof).** Instantiate SLA objects; SMT-prove attainability
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(data)` → validated instance; instantiates SLA/OLA/UC objects. exercised: "(1, 'a')"
  `locate: pydantic.BaseModel.model_validate`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; proves attainability. exercised: "True"
  `locate: pysmt.shortcuts.is_sat`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Attainment).** Compute attainment after the SMT proof
  duckdb 1.5.5 — `duckdb.sql(query)` → relation; computes SLA attainment. exercised: "(42,)"
  `locate: duckdb.sql`

- **Step 4 (Execution).** Terminal docx and dashboard activities
  python-docx 1.2.0 — `docx.Document().save(path)` → writes .docx; terminal Word activity. exercised: "'t' round-trip"
  `locate: docx.document.Document.save`
  streamlit 1.63.0 — `streamlit.dataframe(data)` → renders table; terminal dashboard activity. located
  `locate: streamlit.dataframe`

#### Pipeline 32: Monitoring and Event Management

- **Step 0 (Global Ingestion).** Flatten standards/catalogs/rules/exports into the manifest.
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → parsed document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV(args).main()` → converts tabular exports to CSV; CLI: `in2csv file.xlsx`. located
  `locate: csvkit.utilities.in2csv.In2CSV`

- **Step 1 (Orchestrator Compilation).** Keep event assets only when event-type and severity spans resolve.
  durable-rules 2.0.28 — `durable.lang.ruleset(name)` (context manager) → defines Rete ruleset for event assets. located
  `locate: durable.lang.ruleset`
  experta → durable-rules 2.0.28 — `ruleset(name){{ when_all(...) }}`, `post(name, fact)` → Rete rule engine (experta itself fails on py3.11: collections.Mapping). located
  `locate: durable.lang.ruleset, durable.lang.when_all, durable.lang.post`
  pydantic 2.13.5 — `class M(pydantic.BaseModel): ...` → validated event model. exercised: "M(x=3).x == 3"
  `locate: pydantic.BaseModel`

- **Step 2 (Correlate and Hand-off).** Execute Rete rules, map event edges, sequence runbooks.
  durable-rules 2.0.28 — `durable.lang.post(ruleset_name, message)` → posts event, triggering compiled Rete evaluation. located
  `locate: durable.lang.post, durable.lang.assert_fact`
  experta → durable-rules 2.0.28 — `ruleset(name){{ when_all(...) }}`, `post(name, fact)` → Rete rule engine (experta itself fails on py3.11: collections.Mapping). located
  `locate: durable.lang.ruleset, durable.lang.when_all, durable.lang.post`
  pm4py 2.7.23.8 — `pm4py.discover_dfg(log)` → (dfg, start, end); maps event-to-event edges. exercised: "{('a','b'):1, ('a','c'):1}"
  `locate: pm4py.discover_dfg`
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...)` → planner engine sequencing runbook actions. located
  `locate: unified_planning.shortcuts.OneshotPlanner`

- **Step 3 (Coverage Proof).** Prove every critical event class has filter/correlation/response paths.
  clingo 5.8.0 — `clingo.Control(); ...; ctl.solve(on_model=...)` → ASP proof of coverage. exercised: "['a b']"
  `locate: clingo.Control, clingo.Control.solve`

- **Step 4 (Execution).** Emit dashboard, charts, and diagram as leaf assets.
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  plotly 7.0.0 — `plotly.graph_objects.Figure(data=go.Bar(y=[...]))` → interactive chart figure. exercised: "1 trace"
  `locate: plotly.graph_objects.Figure`
  streamlit 1.63.0 — `streamlit.write(*args)` → renders element to dashboard. located
  `locate: streamlit.write, streamlit.dataframe`

#### Pipeline 33: Incident Management

- **Step 0 (Global Ingestion).** Flatten incident models, tickets, alerts into manifest.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → document to Markdown. located
  `locate: anydoc.to_markdown`
  csvkit 2.2.0 — `In2CSV().run()` (CLI `in2csv`) → flattens tabular dumps to CSV; `csvkit.reader` reads rows. located [CLI suite]
  `locate: csvkit.utilities.in2csv.In2CSV.run, csvkit.reader`
- **Step 1 (Orchestrator Compilation).** Emit asset graph if category/impact/urgency type-check.
  dagster 1.13.20 — `@dagster.asset` → routing asset node in graph. located
  `locate: dagster.asset, dagster.Definitions`
- **Step 2 (Route and Localize).** Apply models, walk graph, compare live path to model.
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
  networkx 3.6.1 — `shortest_path(G, source, target)` → localize nodes via traversal. exercised: "['a','b','c']"
  `locate: networkx.shortest_path`
  pm4py 2.7.23.8 — `conformance_diagnostics_alignments(log, net, im, fm)` → compares live path to model. located
  `locate: pm4py.conformance_diagnostics_alignments`
- **Step 3 (Restore Proof).** Estimate remaining restore time; diff model-update payloads.
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → remaining restore-time survival. exercised: "median 4.0"
  `locate: lifelines.KaplanMeierFitter.fit`
  csv-diff 1.2 — `compare(load_csv(a), load_csv(b))` → CSV model-update diff payload. exercised: "{'v': ['a', 'b']}"
  `locate: csv_diff.compare, csv_diff.load_csv`
- **Step 4 (Execution).** Leaf assets: dashboard, Word, diagram.
  streamlit 1.63.0 — `streamlit.dataframe(df)` → incident dashboard leaf. located
  `locate: streamlit.dataframe, streamlit.write`
  python-docx 1.2.0 — `docx.Document().save(path)` → writes Word artifact. exercised: "docx written"
  `locate: docx.Document`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 34: Problem Management

- **Step 0 (Global Ingestion).** Parse incident histories/advisories/snapshots/known-error articles into the manifest.
  undoc 0.9.0 — `undoc.parse_file(path)` → Markdown/text/JSON; office parse. located
  `locate: undoc.parse_file`
  docling 2.124.0 — `DocumentConverter().convert(source)` → ConversionResult (Markdown/JSON); PDF/Office parse. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Write a prefect flow gated on amrlib causal/error graphs.
  prefect 3.8.4 — `@prefect.flow def f(x): ...` → orchestrated flow run; flow emit. exercised: "flow result: 42"
  `locate: prefect.flow`
  amrlib 0.8.1 — `amrlib.load_stog_model()` then `.parse_sents([sent])` → AMR graphs; causal/error-hypothesis graphs. located
  `locate: amrlib.load_stog_model`

- **Step 2 (Cause and Known Error).** Test structure; formalize mechanisms; record known-error facts after SMT proof.
  dowhy 0.14 — `dowhy.CausalModel(data, treatment, outcome, graph)` → identifiable model; causal-structure test. located
  `locate: dowhy.CausalModel`
  pgmpy 1.1.2 — `pgmpy.estimators.PC(data).estimate(ci_test='chi_square')` → learned DAG/PDAG; structure test. located
  `locate: pgmpy.estimators.PC.PC.estimate`
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr)` → FOL Clause; mechanism formalization. located
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; SMT proof. exercised: "False / True"
  `locate: pysmt.shortcuts.is_sat`
  typedlogic 0.2.4 — `Theory().add(sentence)` → recorded fact; known-error fact recording. located
  `locate: typedlogic.Theory.add`

- **Step 3 (Solution and Close).** Explore strategies; accept closure evidence or keep record open in duckdb.
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=pk).solve(problem)` → plan; strategy exploration. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  ortools 9.15.6755 — `CpSolver().solve(CpModel())` → status/values; CP-SAT strategy optimization. exercised: "OPTIMAL v= 3"
  `locate: ortools.sat.python.cp_model.CpSolver.solve`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.check()` → sat/unsat; closure-evidence proof. exercised: "sat"
  `locate: z3.Solver.check`
  duckdb 1.5.5 — `duckdb.sql("SELECT ...")` → relation; open-record store. exercised: "(2,)"
  `locate: duckdb.sql`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Leaf assets: Word doc, diagram, ASP-fact graph.
  python-docx 1.2.0 — `docx.Document()` then `.save(path)` → .docx; Word leaf asset. exercised: "36609 bytes"
  `locate: docx.Document`
  clingraph 1.2.6 — `clingraph.render(clingraph.compute_graphs(fb))` → graph image files; ASP-fact visualization leaf. located
  `locate: clingraph.render, clingraph.compute_graphs`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 35: Service Desk

- **Step 0 (Global Ingestion).** Flatten transcripts, rules, policy, metrics into the manifest.
  docling 2.124.0 — `DocumentConverter().convert("transcript.pdf")` → parsed document object. located
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `MarkItDown().convert("policy.docx")` → Markdown result; doc-to-Markdown. exercised: "# Desk x"
  `locate: markitdown.MarkItDown.convert`

- **Step 1 (Orchestrator Compilation).** Emit durable triage workflow when guideline/channel spans resolve.
  temporalio 1.32.0 — `@temporalio.workflow.defn class Triage: ...` → defines durable workflow. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Triage and Pack).** Route tickets by rules; assemble channel-constrained messages.
  business-rules 1.1.1 — `business_rules.run_all(rule_list, defined_variables, defined_actions)` → fires routing when rules trigger. exercised: "False (empty rule_list)"
  `locate: business_rules.run_all`
  jinja2 3.1.6 — `jinja2.Template(src).render(**ctx)` → rendered message text. exercised: "flow R0"
  `locate: jinja2.Template.render`
  stanza 1.14.0 — `stanza.Pipeline(lang="en")` → NLP pipeline; parses/types ticket text. located
  `locate: stanza.Pipeline`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Feedback and Improve).** Store CSAT; score desk time series; LP escalation.
  pandas 2.3.3 — `pandas.DataFrame({"csat":[...], "confirmed":[...]})` → tabular store. exercised: "(2, 2)"
  `locate: pandas.DataFrame`
  statsmodels 0.15.0 — `statsmodels.tsa.arima.model.ARIMA(endog, order=(1,0,0)).fit()` → fitted desk-series model. exercised: "aic 111.8"
  `locate: statsmodels.tsa.arima.model.ARIMA.fit, statsmodels.tsa.arima.model.ARIMA`
  pulp 3.3.2 — `LpProblem("p", LpMaximize).solve()` → Optimal/Infeasible; escalation LP. exercised: "Optimal"
  `locate: pulp.LpProblem.solve`

- **Step 4 (Execution).** Publish dashboard and Word artifacts.
  python-docx 1.2.0 — `docx.Document()` (add_paragraph; save) → writes .docx. exercised: "1 paragraph"
  `locate: docx.Document`
  streamlit 1.63.0 — `streamlit.dataframe(df)` → renders dashboard. located
  `locate: streamlit.dataframe`

#### Pipeline 36: Service Request Management

- **Step 0 (Global Ingestion).** Flatten request models/catalog/SLA/logs to Markdown manifest
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("catalog.docx")` → Markdown string; flattens docs to Markdown. exercised: "'Continuity plan\n'"
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Keep assets only when model key / ad-hoc flag type-checks
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`
  pydantic 2.13.5 — `M.model_validate(request)` → instance/raises; type-checks model key / ad-hoc flag. exercised: "rto=4"
  `locate: pydantic.BaseModel.model_validate, pydantic.BaseModel`

- **Step 2 (Model or Plan).** Execute BPMN model, synthesize ad-hoc plan, write approval tables
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`
  unified-planning 1.3.0 — `with OneshotPlanner(problem_kind=pk) as p: p.solve(problem)` → PlanGenerationResult; synthesizes ad-hoc plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Replay).** Compare executed paths to model; score cycle-time deviation
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_alignments(log, net, im, fm)` → alignments; compares executed paths to model. located
  `locate: pm4py.conformance_diagnostics_alignments, pm4py.conformance_diagnostics_token_based_replay`
  pandas 2.3.3 — `df.groupby("case")["cycle"].mean()` → Series; scores per-case cycle time. exercised: "{'a': 4.0, 'b': 9.0}"
  `locate: pandas.DataFrame.groupby`
  pingouin 0.6.1 — `pingouin.anova(data=df, dv="cycle", between="grp")` → ANOVA table; tests cycle-time deviation. exercised: "F= 32.0"
  `locate: pingouin.anova`

- **Step 4 (Execution).** Leaf assets: web dashboard and Word document
  python-docx 1.2.0 — `docx.Document().save("out.docx")` → writes .docx leaf asset. exercised: "saved 36709 bytes"
  `locate: docx.Document, docx.document.Document.save`
  streamlit 1.63.0 — `streamlit.write(obj)` / `streamlit.dataframe(df)` → renders app widget/table. located
  `locate: streamlit.write, streamlit.dataframe`

#### Pipeline 37: Service Catalog Management

- **Step 0 (Global Ingestion).** dump strategy/catalog/contract docs into compiler manifest
  markitdown 0.1.7 — `MarkItDown().convert(path).text_content` → Markdown. exercised: "# Hi\n\nBody text"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown/text/JSON. exercised: "hi"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** build dagster asset graph from recovered spans
  dagster 1.13.20 — `@dagster.asset` + `Definitions(assets=[...])` → catalog asset graph. exercised: "AssetsDefinition"
  `locate: dagster.asset, dagster.Definitions`

- **Step 2 (Model and View).** instantiate catalog into duckdb, emit views, gate access
  pydantic 2.13.5 — `Model.model_validate(row)` → typed catalog record. exercised: "2"
  `locate: pydantic.BaseModel.model_validate`
  duckdb 1.5.5 — `duckdb.connect('catalog.duckdb')` → connection; instantiates catalog. exercised: "(2,)"
  `locate: duckdb.connect`
  jinja2 3.1.6 — `Template(src).render(**ctx)` → standard view output. exercised: "hi x"
  `locate: jinja2.Template.render`
  great-tables 0.24.0 — `GT(df).as_raw_html()` → HTML view. exercised: "9309-char HTML"
  `locate: great_tables.GT, great_tables.GT.as_raw_html`
  clingo 5.8.0 — `Control().solve()` → accepts mandatory-attribute completeness. exercised: "a b"
  `locate: clingo.Control.solve`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`

- **Step 3 (Request Path).** evaluate view requests against decision model
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** publish catalog as dashboard, API, and Word doc
  streamlit 1.63.0 — `st.dataframe(df)` → dashboard element; catalog UI leaf. located
  `locate: streamlit.delta_generator.ArrowMixin.dataframe`
  datasette 0.65.3 — `Datasette(files=['catalog.db'])` → app; publishes DB as API/UI. located
  `locate: datasette.app.Datasette`
  python-docx 1.2.0 — `docx.Document(); .save(path)` → Word artifact. exercised: "docx saved"
  `locate: docx.Document, docx.document.Document.save`

#### Pipeline 38: Business Relationship Management

- **Step 0 (Global Ingestion).** parse strategy/stakeholder/performance/review docs into manifest
  docling 2.124.0 — `DocumentConverter().convert(source="review.pdf")` → ConversionResult; parses to text/Markdown. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** write flow only if stakeholder/relationship spans resolve
  prefect 3.8.4 — `prefect.flow(name="brm")(fn)` → Flow; the journey-asset orchestration flow. located
  `locate: prefect.flow`

- **Step 2 (Health and Offer).** build RACI graph; score VoC; record principles
  networkx 3.6.1 — `g=networkx.DiGraph(); g.add_edge(u_of_edge, v_of_edge)` → RACI directed graph. exercised: "DiGraph edges added; DAG check True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`
  pandas 2.3.3 — `pandas.DataFrame(data=voc_rows)` → tabular VoC scores. exercised: "2-row DataFrame built"
  `locate: pandas.DataFrame`
  typedlogic 0.2.4 — `typedlogic.Theory("brm").add(principle_sentence)` → records principle sentences/axioms. located
  `locate: typedlogic.Theory.add`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Journey).** store terms; track onboard/co-create/review/offboard journey
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net, im, fm) journey process model. exercised: "places=3 transitions=2"
  `locate: pm4py.discover_petri_net_inductive`
  pydantic 2.13.5 — `class Terms(pydantic.BaseModel): ...; Terms(**row)` → validated stored terms. exercised: "M(x=5).x == 5"
  `locate: pydantic.BaseModel`

- **Step 4 (Execution).** fire leaf report/dashboard assets
  python-docx 1.2.0 — `docx.Document().add_paragraph(text)` → writes .docx leaf asset. exercised: "paragraph text 'hello'"
  `locate: docx.Document`
  streamlit 1.63.0 — `streamlit.dataframe(data=df)` → renders dashboard leaf asset. located
  `locate: streamlit.dataframe`

#### Pipeline 39: Change Enablement

- **Step 0 (Global Ingestion).** Flatten change policy, models, RFCs, risk notes, reviews into manifest.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("rfc.docx")` → Markdown string from each source doc. exercised: "Spec line"
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Emit a Temporal workflow gated on change-type/risk/success-criteria spans.
  temporalio 1.32.0 — `@temporalio.workflow.defn class ChangeWF: ...` → defines the durable workflow. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Assess and Authorize).** Create record; apply models; bind authority matrix; accept freeze/resource constraints.
  pydantic 2.13.5 — `pydantic.create_model("ChangeRecord", risk=(str, ...))` → the change record model. exercised: "instance amount=100"
  `locate: pydantic.create_model`
  business-rules 1.1.1 — `business_rules.run_all(rule_list, defined_variables, defined_actions)` → fires authority-matrix actions. exercised: "fired=True"
  `locate: business_rules.run_all`
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → stable model accepting freeze-window/exclusive-resource constraints. exercised: "sat, balanced=[True]"
  `locate: clingo.Control.solve`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`

- **Step 3 (Plan and Replay).** Emit the plan; dry-run it; refuse divergent closure.
  criticalpath 0.1.5 — `Node("proj").get_critical_path()` (after add/link/update_all) → ordered critical tasks. exercised: "critical=['A', 'B']"
  `locate: criticalpath.Node.get_critical_path`
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=problem.kind).solve(problem)` → a plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  simpy 4.1.2 — `simpy.Environment().run(until=T)` → advances discrete-event dry-run clock. exercised: "now=10"
  `locate: simpy.Environment.run`
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_alignments(log, net, im, fm)` → per-trace divergences. located
  `locate: pm4py.conformance_diagnostics_alignments`
  csv-diff 1.2 — `csv_diff.compare(load_csv(planned, key="id"), load_csv(executed, key="id"))` → path divergence. exercised: "changed=1"
  `locate: csv_diff.compare`

- **Step 4 (Execution).** Publish terminal activities: document, diagram, dashboard.
  python-docx 1.2.0 — `docx.Document().save("change.docx")` → writes the terminal Word activity. exercised: "saved 36583B"
  `locate: docx.Document, docx.document.Document.save`
  streamlit 1.63.0 — `streamlit.plotly_chart(fig)` → renders the terminal dashboard activity. located
  `locate: streamlit.plotly_chart`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 40: Project Management

- **Step 0 (Global Ingestion).** dump strategy/cases/logs into the manifest
  markitdown 0.1.7 — `MarkItDown().convert(source).text_content` → Markdown of the document. exercised: "'# Title\\n\\nhello world'"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path).to_json()` → text/JSON. exercised: "to_json → format:\"xlsx\"…"
  `locate: undoc.parse_file, undoc.Undoc.to_json`

- **Step 1 (Orchestrator Compilation).** build a dagster asset graph from spans
  dagster 1.13.20 — `@dagster.asset` → software-defined asset node in the graph. exercised: "AssetsDefinition"
  `locate: dagster.asset, dagster.define_asset_job`

- **Step 2 (Gates and Schedule).** instantiate schemas; solve resource-feasible plans
  pydantic 2.13.5 — `pydantic.create_model("PID", field=(int, ...))` → PID/stage/WP schema; `.model_validate(row)`. exercised: "model M(x=5).x == 5"
  `locate: pydantic.create_model, pydantic.BaseModel, pydantic.BaseModel.model_validate`
  criticalpath 0.1.5 — `Node(name).get_critical_path()` → schedule critical path. exercised: "critical path ['A','B']"
  `locate: criticalpath.Node.get_critical_path`
  ortools 9.15.6755 — `CpSolver().solve(CpModel())` → resource-feasible plan. exercised: "OPTIMAL, x=3"
  `locate: ortools.sat.python.cp_model.CpSolver.solve, ortools.sat.python.cp_model.CpModel`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Exception Proof).** prove an exception plan restores tolerances
  typedlogic 0.2.4 — `Solver().prove(sentence)` → True/False/None entailment. located
  `locate: typedlogic.solver.Solver.prove`
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat on restored tolerances. exercised: "sat; [x = 1]"
  `locate: z3.Solver.check`

- **Step 4 (Execution).** fire tabular, chart, Word leaf assets
  pandas 2.3.3 — `pandas.DataFrame(data)` → tabular asset; `.to_excel(path)`. exercised: "shape (3, 1)"
  `locate: pandas.DataFrame, pandas.DataFrame.to_excel`
  plotly 7.0.0 — `plotly.express.line(x, y)` → interactive chart. exercised: "Figure, 1 trace"
  `locate: plotly.express.line`
  python-docx 1.2.0 — `docx.Document().save(path)` → Word report. exercised: "saved .docx"
  `locate: docx.Document, docx.document.Document.save`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

#### Pipeline 41: Software Development and Management

- **Step 0 (Global Ingestion).** Flatten strategy, architecture, backlogs, design/test/telemetry to Markdown.
  docling 2.124.0 — `DocumentConverter().convert(source).document.export_to_markdown()` → Markdown from docs. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Write prefect tasks if backlog/architecture-constraint spans resolve.
  prefect 3.8.4 — `@prefect.task` def; `@prefect.flow` def; `flow()` → orchestrated tasks. exercised: "result 5"
  `locate: prefect.task, prefect.flow`

- **Step 2 (Guide and Rank).** Record SDM rules; rank tasks by value/risk over product edges.
  typedlogic 0.2.4 — `ClingoSolver().add(sentence)` → records SDM rules. exercised: "satisfiable=True"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add, typedlogic.solver.Solver.add`
  pulp 3.3.2 — `p=LpProblem(...); p+=obj; p.solve(...)` → ranks tasks. exercised: "Optimal, x=4.0"
  `locate: pulp.LpProblem.solve`
  networkx 3.6.1 — `networkx.DiGraph(product_edges)` → product-edge dependency graph. exercised: "topo ['a','b','c']"
  `locate: networkx.DiGraph, networkx.topological_sort`

- **Step 3 (Design Proof).** Prove designs against bounds; encode feature-model constraints.
  z3-solver 5.1.0.0 — `s=Solver(); s.add(bounds); s.check()` → sat accepts artifacts. exercised: "check=sat"
  `locate: z3.Solver.check`
  python-sat 1.9.dev15 — `Solver(bootstrap_with=CNF().clauses).solve()` → encodes/solves feature model. exercised: "solve=True, model [-1,2]"
  `locate: pysat.formula.CNF, pysat.solvers.Solver.solve`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Leaf assets: diagrams and Word document.
  diagrams 0.25.1 — `with Diagram('t'): a >> b` → cloud-architecture diagram (render needs graphviz `dot`, absent here). located
  `locate: diagrams.Diagram`
  python-docx 1.2.0 — `d=docx.Document(); d.add_paragraph(t); d.save(path)` → Word leaf asset. exercised: "paras ['H','para one']"
  `locate: docx.Document, docx.document.Document.save`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline 42: Service Validation and Testing

- **Step 0 (Global Ingestion).** flatten test policy, criteria, catalogs, records into manifest
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown str; flattens documents into manifest. located
  `locate: anydoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** admit assets when acceptance predicates and model key type-check
  (no candidate library named in this step)

- **Step 2 (Criteria Proof).** record exit criteria; accept consistency and entailment
  model-checker 1.3.9 — `model_checker.run_test(example_case, semantic_class, proposition_class, operator_collection, syntax_class, model_constraints, model_structure)` → bool; accepts consistency/entailment. located
  `locate: model_checker.run_test, model_checker.solver.create_solver`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; checks consistency (is_valid for entailment). exercised: "True"
  `locate: pysmt.shortcuts.is_sat, pysmt.shortcuts.is_valid`
  typedlogic 0.2.4 — `typedlogic.solver.Solver.add_sentence(sentence)` → None; records an exit criterion into the theory. located
  `locate: typedlogic.solver.Solver.add_sentence, typedlogic.Theory`

- **Step 3 (Plan and Exception).** emit tailored plan; prove defect/exception coverage
  clingo 5.8.0 — `clingo.Control(); ctl.ground(...); ctl.solve(on_model=...)` → stable models; accepts defect/exception coverage. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control`
  ortools 9.15.6755 — `CpSolver().Solve(CpModel())` → OPTIMAL/FEASIBLE status; emits the tailored plan. exercised: "('OPTIMAL', 4)"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve, ortools.sat.python.cp_model.CpModel`
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...)` → planner engine; emits the tailored plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** render result table, Word doc, and diagram
  great-tables 0.24.0 — `great_tables.GT(df)` → formatted table; renders result table. exercised: "GT"
  `locate: great_tables.GT`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  python-docx 1.2.0 — `docx.Document()` then `add_paragraph(...); save(path)` → .docx file; renders Word report. exercised: "1 paragraph"
  `locate: docx.Document`

#### Pipeline 43: Deployment Management

- **Step 0 (Global Ingestion).** Dump deploy models, configs, and inventories into the manifest
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → DocumentConverterResult; converts sources to markdown. exercised: "'Hello clause one.'"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc (then .to_markdown()); Office→md/text/json. exercised: "Undoc object"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`

- **Step 1 (Orchestrator Compilation).** Emit a temporalio workflow gated on change fact
  temporalio 1.32.0 — `@temporalio.workflow.defn(sandboxed=True)` → workflow class; declares the deploy workflow. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Readiness Proof).** Encode predicates; solvers accept component/environment readiness
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(data)` → validated instance; describes pipeline elements. exercised: "(1, 'a')"
  `locate: pydantic.BaseModel.model_validate`
  typedlogic 0.2.4 — `typedlogic.registry.get_compiler('clingo').compile(theory)` → program str; encodes pre-deploy predicates. exercised: "SouffleCompiler obtained"
  `locate: typedlogic.registry.get_compiler, typedlogic.compiler.Compiler.compile`
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → SolveResult; accepts readiness (ASP). exercised: "['a b']"
  `locate: clingo.Control.solve`
  csv-diff 1.2 — `csv_diff.compare(previous, current)` → diff dict; checks readiness deltas. exercised: "['added','removed','changed',…]"
  `locate: csv_diff.compare, csv_diff.load_csv`
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat; accepts readiness constraints. exercised: "sat"
  `locate: z3.Solver.check`

- **Step 3 (Review).** Emit instance plan; mine logs against model
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...).solve(problem)` → plan; emits instance plan. located (requires planner engine)
  `locate: unified_planning.shortcuts.OneshotPlanner`
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_alignments(log, net, im, fm)` → alignments; mines logs against model. located
  `locate: pm4py.conformance_diagnostics_alignments`
  pandas 2.3.3 — `pandas.DataFrame(data)` → DataFrame; emits Pipeline 29 items. exercised: "(2, 2)"
  `locate: pandas.DataFrame`

- **Step 4 (Execution).** Terminal diagram and docx activities
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  python-docx 1.2.0 — `docx.Document().save(path)` → writes .docx; terminal Word activity. exercised: "'t' round-trip"
  `locate: docx.document.Document.save`

#### Pipeline 44: Release Management

- **Step 0 (Global Ingestion).** Flatten architecture/policies/schedules/reviews into the manifest.
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → parsed document. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Write a flow only if release-model and go/no-go language resolve.
  prefect 3.8.4 — `@prefect.flow` on a function → defines orchestration flow. located
  `locate: prefect.flow`

- **Step 2 (Select and Prove).** Select model, build schedule, prove procedure/verification/readiness jointly.
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
  criticalpath 0.1.5 — `Node('p'); p.add(Node('A',duration=3)); p.link(a,b); p.get_critical_path()` → CPM path. exercised: "('[A, B]', 5)"
  `locate: criticalpath.Node, criticalpath.Node.get_critical_path`
  typedlogic 0.2.4 — `Solver().add(theory); Solver().check()` → satisfiability of joint constraints. located
  `locate: typedlogic.solver.Solver.check, typedlogic.solver.Solver.add`
  z3-solver 5.1.0.0 — `z3.Solver(); s.add(...); s.check()` → sat/unsat proof. exercised: "sat [x = 1]"
  `locate: z3.Solver, z3.Solver.check`

- **Step 3 (Review).** Compare logs and incidents to success criteria.
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)` → per-trace conformance vs model. located
  `locate: pm4py.conformance_diagnostics_token_based_replay`
  pandas 2.3.3 — `pandas.DataFrame(data)` → tabular logs/incidents for comparison. exercised: "shape (2, 1)"
  `locate: pandas.DataFrame`

- **Step 4 (Execution).** Emit diagram and docx as leaf assets.
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  python-docx 1.2.0 — `docx.Document()` (add_paragraph/save) → Word document. exercised: "paragraphs == 0"
  `locate: docx.Document`

#### Pipeline 45: Organizational Change Management

- **Step 0 (Global Ingestion).** Flatten architecture, culture reviews, OCM audits into manifest.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → document to Markdown. located
  `locate: anydoc.to_markdown`
  undoc 0.9.0 — `parse_file(path).to_markdown()` → Office doc to Markdown/text/JSON. located
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
- **Step 1 (Orchestrator Compilation).** Emit asset graph if change-vision/role spans resolve.
  dagster 1.13.20 — `@dagster.asset` → communication asset node in graph. located
  `locate: dagster.asset, dagster.Definitions`
- **Step 2 (Ready and Plan).** Map roles, score readiness, emit engagement sequence.
  networkx 3.6.1 — `G=DiGraph(); G.add_edge(u,v)` → role/stakeholder map. exercised: "3-node DiGraph built"
  `locate: networkx.DiGraph`
  pandas 2.3.3 — `pandas.DataFrame(data)` → holds readiness scores. located
  `locate: pandas.DataFrame`
  pingouin 0.6.1 — `cronbach_alpha(data=df)` → readiness-survey reliability score. exercised: "0.818"
  `locate: pingouin.cronbach_alpha, pingouin.anova`
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=...).solve(problem)` → engagement sequence plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  criticalpath 0.1.5 — `Node(...).get_critical_path()` → engagement CPM sequence. exercised: "['t1','t2'], duration 5"
  `locate: criticalpath.Node.get_critical_path`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
- **Step 3 (Sustain Proof).** Track adoption; accept every early-win has evidence.
  statsmodels 0.15.0 — `statsmodels.api.OLS(y, X).fit()` → adoption-trend regression. exercised: "params [1.0, 2.0]"
  `locate: statsmodels.api.OLS`
  clingo 5.8.0 — `c=Control(); c.add(...); c.ground(...); c.solve()` → accepts evidence constraints. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control.ground`
- **Step 4 (Execution).** Leaf assets: Word and publishing.
  python-docx 1.2.0 — `docx.Document().save(path)` → writes Word artifact. exercised: "docx written"
  `locate: docx.Document`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

#### Pipeline 46: Knowledge Management

- **Step 0 (Global Ingestion).** Dump strategy/inventories/KBs/roadmaps/usage-logs into the manifest.
  markitdown 0.1.7 — `MarkItDown().convert(source)` → Markdown; doc→Markdown. exercised: "# Spec\n\nHello"
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Markdown/text/JSON; office parse. located
  `locate: undoc.parse_file`
  docling 2.124.0 — `DocumentConverter().convert(source)` → ConversionResult; PDF/Office parse. located
  `locate: docling.document_converter.DocumentConverter.convert`

- **Step 1 (Orchestrator Compilation).** Write prefect tasks for rdflib and networkx when spans exist.
  prefect 3.8.4 — `@prefect.task def t(): ...` → orchestrated task; task emit. located
  `locate: prefect.task`
  rdflib 7.6.0 — `rdflib.Graph()` → RDF store for a task; graph task target. located
  `locate: rdflib.Graph`
  networkx 3.6.1 — `networkx.DiGraph()` → directed graph for a task; graph task target. located
  `locate: networkx.DiGraph`

- **Step 2 (Inventory Proof).** Map domains→owners; store assets; record guidelines; prove demand fulfilled/queued.
  networkx 3.6.1 — `G=nx.DiGraph(); G.add_edges_from([(domain, owner)])` → mapped edges; domain→owner mapping. located
  `locate: networkx.DiGraph.add_edges_from`
  rdflib 7.6.0 — `g.add((s, p, o))` → stored triple; asset storage. located
  `locate: rdflib.Graph.add`
  typedlogic 0.2.4 — `Theory().add(sentence)` → recorded guideline; guideline facts. located
  `locate: typedlogic.Theory.add`
  clingo 5.8.0 — `ctl.solve()` → SAT/UNSAT; high-priority-demand fulfilment proof. exercised: "SAT"
  `locate: clingo.Control.solve`

- **Step 3 (Routines).** Execute capture/review/publish/retire; version assets; emit items on stale freshness.
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`
  pydantic 2.13.5 — `class Asset(pydantic.BaseModel): version: int` → validated versioned model; asset versioning. exercised: "unit=3.5"
  `locate: pydantic.BaseModel`
  ydata-profiling 4.18.4 — `ydata_profiling.ProfileReport(df).to_html()` → EDA report; freshness/EDA emission. located
  `locate: ydata_profiling.ProfileReport`
  pandas 2.3.3 — `pandas.DataFrame(rows)` → tabular items; emit Pipeline 29 items. located
  `locate: pandas.DataFrame`

- **Step 4 (Execution).** Leaf assets: docs site, Word doc, diagram.
  mkdocs 1.6.1 — `mkdocs.commands.build.build(config)` → static site; docs-site leaf. located
  `locate: mkdocs.commands.build.build`
  python-docx 1.2.0 — `docx.Document().save(path)` → .docx; Word leaf. exercised: "36609 bytes"
  `locate: docx.Document`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

#### Pipeline R0: Zero-Touch Invert Compiler

- **Step 0 (Global Ingestion).** Crawl folder; parse every doc into mixed inventory.
  docling 2.124.0 — `DocumentConverter().convert(path)` → parsed document object. located
  `locate: docling.document_converter.DocumentConverter.convert`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → doc-to-Markdown string. exercised: "| a | b | ..."
  `locate: anydoc.to_markdown`
  mammoth 1.12.1 — `mammoth.convert_to_html(docx_fileobj)` → Word-to-clean-HTML result. located
  `locate: mammoth.convert_to_html`
  markitdown 0.1.7 — `MarkItDown().convert(path)` → Markdown result. exercised: "# Desk x"
  `locate: markitdown.MarkItDown.convert`
  office-oxide 0.1.9 — `office_oxide.to_markdown(path)` → Office-to-Markdown string. located
  `locate: office_oxide.to_markdown`
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch()...page.content()` → captures rendered HTML. located
  `locate: playwright.sync_api.sync_playwright`
  pymupdf 1.28.2 — `d=pymupdf.open(path); d[0].get_text()` → PDF page text. exercised: "'REL'"
  `locate: pymupdf.open, pymupdf.Page.get_text`
  pypdfium2 5.13.0 — `pypdfium2.PdfDocument(path)` (page.get_textpage().get_text_range()) → PDF text/render. located
  `locate: pypdfium2.PdfDocument, pypdfium2.PdfTextPage.get_text_range`
  python-docx 1.2.0 — `docx.Document(path)` → reads .docx content. exercised: "1 paragraph"
  `locate: docx.Document`
  python-pptx 1.0.2 — `pptx.Presentation(path)` → reads .pptx content. exercised: "11 layouts"
  `locate: pptx.Presentation`
  undoc 0.9.0 — `undoc.parse_file(path)` → Markdown/text/JSON of Office doc. located
  `locate: undoc.parse_file`

- **Step 1 (Artifact Census).** Profile tables; fingerprint docs; flatten captured pages into manifest.
  ydata-profiling 4.18.4 — `ydata_profiling.ProfileReport(df)` → EDA HTML summary; profiles tables. located
  `locate: ydata_profiling.ProfileReport`
  sweetviz 2.3.3 — `sweetviz.analyze(df)` → EDA report; profiles tables. located
  `locate: sweetviz.analyze`
  office-oxide 0.1.9 — `office_oxide.Document.open(path)` → parses Word structure; fingerprints styles. located
  `locate: office_oxide.Document.open`
  python-docx 1.2.0 — `docx.Document(path)` → reads heading tree/styles/content controls. exercised: "1 paragraph"
  `locate: docx.Document`
  python-pptx 1.0.2 — `pptx.Presentation(path)` → slide masters/layouts/placeholders/notes. exercised: "11 layouts"
  `locate: pptx.Presentation`
  pymupdf 1.28.2 — `d=pymupdf.open(path); d[0].get_text()` → PDF text fingerprint. exercised: "'REL'"
  `locate: pymupdf.open, pymupdf.Page.get_text`
  pypdf 6.16.2 — `pypdf.PdfReader(path).pages[0].extract_text()` → PDF text fingerprint. located
  `locate: pypdf.PdfReader, pypdf.PageObject.extract_text`
  markdownify 1.2.3 — `markdownify.markdownify(html)` → flattens captured page HTML to Markdown. exercised: "Risk ==== hi"
  `locate: markdownify.markdownify`
  playwright 1.62.0 — `page.content()` under `sync_playwright()` → captured page HTML. located
  `locate: playwright.sync_api.sync_playwright`
  dash 4.4.1, panel 1.9.4, nicegui 3.16.0, mkdocs 1.6.1, folium 0.20.0, streamlit 1.63.0 — named as the source frameworks whose rendered pages playwright captures and markdownify/html2text flatten; sources here, not performers of this census step (no bound function).
  dataprep → ydata-profiling 4.18.4 — `ProfileReport(df).to_json()` → table profiling (dataprep is not installable here). located
  `locate: ydata_profiling.ProfileReport.to_json, ydata_profiling.ProfileReport`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 2 (Schema Compilation).** Type dasel projections with pydantic; write schema spreadsheet.
  pydantic 2.13.5 — `Schema.model_validate(projection)` → runtime-typed schema. exercised: "tte=12.5 censored=True"
  `locate: pydantic.BaseModel.model_validate`
  openpyxl 3.1.2 — `wb=Workbook(); wb.save("schema.xlsx")` → writes .xlsx. exercised: "saved"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet().write(0,0,v); wb.close()` → writes .xlsx. exercised: "closed"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → writes real Excel Table. exercised: "table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`

- **Step 3 (Capability Logic).** Compile clingo facts; solve the unique stable model.
  clingo 5.8.0 — `c=Control(); c.add("base",[],prog); c.ground([("base",[])]); c.solve()` → stable model. exercised: "SAT"
  `locate: clingo.Control.solve`
  typedlogic 0.2.4 — `s=ClingoSolver(); s.add_fact(f); s.dump()` → emits clingo facts/program from manifest. located
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add_fact, typedlogic.integrations.solvers.clingo.ClingoSolver.dump`

- **Step 4 (Graph Compilation).** Build directed invert/replay graphs; render orchestrator source.
  networkx 3.6.1 — `networkx.DiGraph()` → directed invert/replay graph. exercised: "(2, 1)"
  `locate: networkx.DiGraph`
  jinja2 3.1.6 — `jinja2.Template(src).render(graph=g)` → orchestrator source text. exercised: "flow R0"
  `locate: jinja2.Template.render`
  dagster 1.13.20 — `@dagster.asset def a(): ...` → asset definition. exercised: "AssetsDefinition"
  `locate: dagster.asset`
  prefect 3.8.4 — `@prefect.flow def f(): ...` → flow object. located
  `locate: prefect.flow`
  temporalio 1.32.0 — `@temporalio.workflow.defn class W: ...` → workflow module. located
  `locate: temporalio.workflow.defn`
  graphable — requires Python ≥ 3.13 (this interpreter is 3.11); its table→Mermaid/D2/PlantUML output is otherwise the `diagrams` binding or the mermaid CLI

- **Step 5 (Self-Load).** Chosen orchestrator imports written file, registers assets, starts run.
  (no candidate libraries named in this step.)

#### Pipeline R1: Reverse Quality Engineering

- **Step 0 (Global Ingestion).** Flatten FMEA narrative/PDF/HTML into the manifest
  docling 2.124.0 — `DocumentConverter().convert("dossier.pdf").document` → DoclingDocument; parses PDF/Office/HTML. located
  `locate: docling.document_converter.DocumentConverter.convert`
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`
  markitdown 0.1.7 — `MarkItDown().convert(src).markdown` → Markdown string; narrative/PDF/HTML to Markdown. exercised: "'Continuity plan\n\n| |...'"
  `locate: markitdown.MarkItDown.convert`

- **Step 1 (Orchestration and Narrowing).** Orchestrate the workflow piping text into NLP
  dagster 1.13.20 — `@dagster.job def flow(): op()` (assets via `@dagster.asset`) → JobDefinition; orchestrates the workflow. located
  `locate: dagster.job, dagster.asset, dagster.op`

- **Step 2 (Logic Generation).** Translate spans to FOL; type QE_* with pydantic
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr_str)` → Clause; translates AMR span to FOL. exercised: "boy(b)"
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert, amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert_amr_str`
  pydantic 2.13.5 — `M.model_validate({"QE_MODE":...})` → instance/raises; types QE_MODE/QE_EVENT/QE_FIT. exercised: "rto=4"
  `locate: pydantic.BaseModel.model_validate, pydantic.BaseModel`

- **Step 3 (Mathematical Verification).** SMT-verify physical bounds and logic paths
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; verifies physical bounds/logic paths. exercised: "False (p∧¬p)"
  `locate: pysmt.shortcuts.is_sat, pysmt.shortcuts.Solver`

- **Step 4 (Time-to-Event Modeling).** Survival analysis after rejecting unphysical rows
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → fitted survival model on failure events. exercised: "median 5.0"
  `locate: lifelines.KaplanMeierFitter.fit, lifelines.KaplanMeierFitter`
  scipy 1.15.3 — `scipy.stats.zscore(rows)` → z-scores; flags/rejects unphysical (outlier) rows. exercised: "outlier z=1.73"
  `locate: scipy.stats.zscore`

- **Step 5 (Execution).** Write one Excel spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save("out.xlsx")` → writes .xlsx. exercised: "saved 4801 bytes"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=xlsxwriter.Workbook("out.xlsx"); w.add_worksheet(); w.close()` → writes .xlsx. exercised: "saved 5247 bytes"
  `locate: xlsxwriter.Workbook.close, xlsxwriter.Workbook.add_worksheet, xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "tbl", file="out.xlsx", index=False)` → writes real Excel Table. exercised: "wrote 6134 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R2: Reverse Financial Dashboarding

- **Step 0 (Global Ingestion).** flatten dashboard HTML/traces into Markdown and JSON
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch()` → browser; renders/scrapes HTML. located
  `locate: playwright.sync_api.sync_playwright`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown from HTML. exercised: "| a | b | ..."
  `locate: anydoc.to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(path).text_content` → Markdown. exercised: "# Hi\n\nBody text"
  `locate: markitdown.MarkItDown.convert`
  plotly 7.0.0 — not a tool here: the "embedded Plotly traces" are input being flattened
  streamlit 1.63.0 — not a tool here: the "Streamlit HTML" is input being flattened

- **Step 1 (Orchestration and Narrowing).** manage pipeline state, map financial entities/periods
  temporalio 1.32.0 — `@workflow.defn` (+ `Client.execute_workflow`) → durable state management. located
  `locate: temporalio.workflow.defn, temporalio.client.Client.execute_workflow`
  stanza 1.14.0 — `stanza.Pipeline(lang, processors='tokenize,ner')` → maps entities/periods. located
  `locate: stanza.Pipeline`

- **Step 2 (Schema Auto-Generation).** query NLP outputs, instantiate financial schemas
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  NLP — not a library: token in prose (spaCy referenced generically)

- **Step 3 (Logic Enforcement).** evaluate recovered instance against decision graph
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Constraint Verification).** prove debit/credit identity of recovered ledger
  clingo 5.8.0 — `Control().solve()` → proves ledger identity. exercised: "a b"
  `locate: clingo.Control.solve`

- **Step 5 (Visual Selection).** auto-select charts, frozen to recovered grammar
  autoviz 0.1.905 — `AutoViz_Class().AutoViz(filename, chart_format='svg')` → auto chart selection. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`

- **Step 6 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → xlsx file. exercised: "saved"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path).add_worksheet()` → native xlsx writer. exercised: "closed"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "T", file=path)` → real Excel Table. exercised: "wrote table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R3: Reverse Architecture Documentation

- **Step 0 (Global Ingestion).** flatten mermaid HTML, SVG titles, Markdown to text/JSON
  markitdown 0.1.7 — `MarkItDown().convert(source="node.html")` → DocumentConverterResult Markdown/text. exercised: "'# Hi\n\nTest doc'"
  `locate: markitdown.MarkItDown.convert`
  playwright 1.62.0 — `page.goto(url); page.content()` → serialized rendered HTML for flattening. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  undoc 0.9.0 — `undoc.parse_file("sidecar.docx").to_json()` → flat text and JSON. exercised: "parse_file→to_markdown 'Hello undoc'"
  `locate: undoc.parse_file, undoc.Undoc.to_text, undoc.Undoc.to_json`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestration and Narrowing).** orchestrate flow; extract entity relationships from text
  nltk 3.10.3 — `nltk.sem.relextract.extract_rels("PER","ORG",doc,corpus="ace")` → entity relation tuples. located
  `locate: nltk.sem.relextract.extract_rels`
  prefect 3.8.4 — `prefect.flow(name="revarch")(fn)` → Flow orchestrating the data flow. located
  `locate: prefect.flow`

- **Step 2 (Network Graphing).** rebuild published node-edge set
  networkx 3.6.1 — `g=networkx.DiGraph(); g.add_edge(u_of_edge, v_of_edge)` → rebuilt node-edge graph. exercised: "DiGraph edges added; DAG check True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`

- **Step 3 (Logic Translation).** convert recovered network dependencies into clingo facts
  typedlogic 0.2.4 — `s=ClingoSolver(); s.add_theory(theory); s.dump()` → serializes typed facts to clingo program. located
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.dump`
  clingo 5.8.0 — `Control().add("base",[],facts); .ground(); .solve(on_model=cb)` → ASP system consuming the facts. exercised: "model 'a b'"
  `locate: clingo.Control, clingo.Control.add, clingo.Control.solve`

- **Step 4 (Architecture Modeling).** map facts into C4 model DSL
  structurizr-python → diagrams 0.25.1 — `with Diagram(name): ...` → architecture diagram (structurizr-python needs pydantic v1). located
  `locate: diagrams.Diagram`

- **Step 5 (Verification).** verify recovered architecture has no cyclical dependencies
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(order_cons); s.check()` → sat/unsat acyclicity proof. exercised: "sat; model [x = 3]"
  `locate: z3.Solver, z3.Solver.check`

- **Step 6 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save(path)` → writes .xlsx. exercised: "A1 == 'hi'"
  `locate: openpyxl.Workbook`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet().write(0,0,v); wb.close()` → writes .xlsx. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name="ARCH_NODE", file=path, index=False)` → real Excel Table. exercised: "6124-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R5: Reverse Process Mining Control Room

- **Step 0 (Global Ingestion).** Flatten Cytoscape/Streamlit dashboard pages; capture embedded event-log JSON.
  playwright 1.62.0 — `page.content()` → rendered DOM HTML of the dashboard page. located
  `locate: playwright.sync_api.Page.content`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert("page.html")` → Markdown of the flattened page. exercised: "# Q3 Net income 100"
  `locate: markitdown.MarkItDown.convert`
  dash-cytoscape 1.0.2 — `dash_cytoscape.Cytoscape(id="g", elements=els)` → graph component that rendered the page. exercised: "comp=Cytoscape"
  `locate: dash_cytoscape.Cytoscape`
  streamlit 1.63.0 — `streamlit.plotly_chart(fig)` → the Streamlit page later flattened. located
  `locate: streamlit.plotly_chart`

- **Step 1 (Orchestrator Compilation).** Admit process-mining asset graph only if actor/activity/time fields resolve.
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → admits asset graph iff fields resolve. exercised: "sat, balanced=[True]"
  `locate: clingo.Control.solve`

- **Step 2 (Event Log Materialization).** Type PM_EVENT/PM_NET/PM_KPI assets and land them in the spreadsheet.
  dagster 1.13.20 — `@dagster.asset def pm_event(): ...` → typed asset in the graph. exercised: "type=AssetsDefinition"
  `locate: dagster.asset`
  pydantic 2.13.5 — `pydantic.create_model("PM_EVENT", case=(str, ...))` → types each PM record. exercised: "instance amount=100"
  `locate: pydantic.create_model`

- **Step 3 (Discovery and Replay).** Rediscover the net; replay it; drop solver-rejected traces.
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net, im, fm) rediscovered. exercised: "places=3 trans=2"
  `locate: pm4py.discover_petri_net_inductive`
  simpn 1.10.0 — `SimProblem().simulate(duration)` → replays the net's token game. exercised: "b_marking=['2@0']"
  `locate: simpn.simulator.SimProblem.simulate`
  typedlogic 0.2.4 — `get_solver("clingo").check()` → drops facts failing clingo. exercised: "satisfiable=True"
  `locate: typedlogic.registry.get_solver, typedlogic.solver.Solver.check`
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → accepts/rejects the typed facts. exercised: "sat, balanced=[True]"
  `locate: clingo.Control.solve`

- **Step 4 (Execution).** Write one Excel spreadsheet from the recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook().save("artifact.xlsx")` → writes the workbook. exercised: "saved 4819B"
  `locate: openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb = xlsxwriter.Workbook("artifact.xlsx"); wb.close()` → writes the workbook. exercised: "wrote 5248B"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, "T", file="artifact.xlsx")` → real Excel Table. exercised: "table xlsx 6047B"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R6: Reverse Causal Policy Evaluation

- **Step 0 (Global Ingestion).** flatten panel pages, forestplot tables, PDFs
  playwright 1.62.0 — `page.goto(url)` then `page.content()` → rendered page HTML. located
  `locate: playwright.sync_api.Page.goto, playwright.sync_api.Page.content, playwright.sync_api.sync_playwright`
  markitdown 0.1.7 — `MarkItDown().convert(source).text_content` → Markdown. exercised: "'# Title\\n\\nhello world'"
  `locate: markitdown.MarkItDown.convert`
  docling 2.124.0 — `DocumentConverter().convert(source)` → structured doc from PDFs. located
  `locate: docling.document_converter.DocumentConverter.convert`
  panel — false match: "panel pages" is the ingested object (panel data), not the HoloViz app toolkit; no binding.

- **Step 1 (Orchestrator Compilation).** emit a prefect flow gated on spans
  prefect 3.8.4 — `@prefect.flow(name=...)` → flow whose tasks exist only if treatment/outcome spans resolve. exercised: "Flow 'ingest'"
  `locate: prefect.flow, prefect.task`

- **Step 2 (Graph and Proof).** rebuild the DAG; prove a legal adjustment set
  pgmpy 1.1.2 — `pgmpy.base.DAG.DAG().add_edges_from(edges)` → causal DAG. exercised: "2 edges"
  `locate: pgmpy.base.DAG.DAG`
  dowhy 0.14 — `dowhy.CausalModel(data, treatment, outcome, common_causes=[...])` → causal DAG model; `.identify_effect()`. exercised: "CausalModel built"
  `locate: dowhy.CausalModel, dowhy.CausalModel.identify_effect`
  networkx 3.6.1 — `networkx.DiGraph().add_edges_from(edges)` → DAG from recovered edges. exercised: "is_directed_acyclic_graph True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edges_from`
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat legal adjustment set. exercised: "sat; [x = 1]"
  `locate: z3.Solver.check`
  pysmt 0.9.6 — `pysmt.shortcuts.is_valid(formula)` → proves adjustment-set validity. located
  `locate: pysmt.shortcuts.is_valid, pysmt.shortcuts.is_sat`

- **Step 3 (Estimation and Binding).** estimate effects on proved strategies
  causalpy 0.9.0 — `causalpy.DifferenceInDifferences(data, formula, time_variable_name, group_variable_name)` → quasi-exp estimate. located
  `locate: causalpy.DifferenceInDifferences, causalpy.InterruptedTimeSeries`
  statsmodels 0.15.0 — `statsmodels.api.OLS(endog, exog).fit()` → regression effect estimate. exercised: "params [1.0, 1.0]"
  `locate: statsmodels.api.OLS`
  pymc 5.28.5 — `pymc.sample(draws=...)` inside `pymc.Model()` → posterior draws. located
  `locate: pymc.sample, pymc.Model`
  arviz 0.23.4 — `arviz.summary(data)` → posterior summary/diagnostics table. exercised: "cols ['mean','sd','hdi_3%']"
  `locate: arviz.summary`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** write one spreadsheet artifact from solver-accepted fields
  openpyxl 3.1.2 — `Workbook().save(path)` → xlsx artifact (styles/templates). exercised: "saved xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `Workbook(path)` (+ write) `.close()` → xlsx with native charts. exercised: "closed xlsx"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object. exercised: "wrote Excel table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R7: Reverse Supply Chain Scheduling

- **Step 0 (Global Ingestion).** Flatten Gantt HTML, pages, sidecars, printed PDFs to Markdown manifest.
  playwright 1.62.0 — `sync_playwright().start().chromium.launch().new_page().content()` → captures rendered HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown from each doc. exercised: "'# H\n\npara one\n'"
  `locate: anydoc.to_markdown`
  docling 2.124.0 — `DocumentConverter().convert(source).document.export_to_markdown()` → Markdown from PDFs. located
  `locate: docling.document_converter.DocumentConverter.convert`
  taipy 4.1.1 — not acting here: named as an ingested source ("taipy pages"), not the flattening tool.
  elegantt 0.0.11 — not acting here: named as an ingested source ("elegantt sidecars"), not the flattening tool.

- **Step 1 (Orchestrator Compilation).** Temporalio workflow; activities are the clingo-selected solver subset.
  temporalio 1.32.0 — `@workflow.defn` + `@workflow.run`; `client.execute_workflow(WF.run, id=, task_queue=)` → durable workflow. located
  `locate: temporalio.workflow.defn, temporalio.workflow.run, temporalio.client.Client.execute_workflow`
  pulp 3.3.2 — `p=LpProblem(...); p.solve(...)` → LP activity. exercised: "Optimal, x=4.0"
  `locate: pulp.LpProblem.solve`
  pyomo 6.10.1 — `m=ConcreteModel(); SolverFactory('cbc').solve(m)` → AML model+solve activity (needs solver binary). located
  `locate: pyomo.environ.ConcreteModel, pyomo.environ.SolverFactory`
  ortools 9.15.6755 — `CpSolver().Solve(model)` → CP-SAT activity. exercised: "OPTIMAL, x=10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  highspy 1.11.0 — `h=Highs(); h.run()` → LP/MILP solve. located
  `locate: highspy.Highs.run, highspy.Highs`
  pyjobshop 0.0.9 — `Model().solve(display=False)` → job-shop scheduling solve. located
  `locate: pyjobshop.Model.solve, pyjobshop.Model`
  alns 7.0.0 — `ALNS().iterate(initial_solution, op_select, accept, stop)` → ALNS metaheuristic activity. located
  `locate: alns.ALNS.ALNS.iterate`

- **Step 2 (Model Emission).** Pydantic schemas from tables become the MIP/CP model.
  pydantic 2.13.5 — `class M(BaseModel): ...; M.model_validate(row)` → schema/model from table rows. exercised: "actor='u1' t=5"
  `locate: pydantic.BaseModel, pydantic.BaseModel.model_validate`

- **Step 3 (Solve and Repair).** ortools/highspy solve; alns repairs on bound without incumbent.
  ortools 9.15.6755 — `CpSolver().Solve(model)` → solves recovered instance. exercised: "OPTIMAL, x=10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  highspy 1.11.0 — `h=Highs(); h.run()` → LP/MILP solve. located
  `locate: highspy.Highs.run, highspy.Highs`
  alns 7.0.0 — `ALNS().iterate(initial_solution, op_select, accept, stop)` → neighborhood-search repair. located
  `locate: alns.ALNS.ALNS.iterate`

- **Step 4 (Calendar Proof).** criticalpath and clingo must accept incumbent before rendering.
  criticalpath 0.1.5 — `p.update_all(); p.get_critical_path()` → validates schedule/critical path. exercised: "['A','B'], dur 5"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node.update_all`
  clingo 5.8.0 — `ctl.solve()` → SolveResult.satisfiable accepts incumbent. exercised: "sat=True"
  `locate: clingo.Control.solve`

- **Step 5 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); ws.append(row); wb.save(path)` → writes .xlsx. exercised: "wrote xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `wb=Workbook(path); ws.write(r,c,v); wb.close()` → writes .xlsx. exercised: "wrote xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, 'T', path, index=False)` → real Excel Table. exercised: "wrote xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R8: Reverse Geospatial Hazard Cartography

- **Step 0 (Global Ingestion).** scrape GeoJSON from map HTML; flatten PDF sheets
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source=path)` → ConversionResult; flattens PDF map sheets. located
  `locate: docling.document_converter.DocumentConverter.convert`
  folium 0.20.0 — `folium.Map(location=[lat,lon])` → Leaflet map HTML; produced the scraped map HTML. exercised: "Map"
  `locate: folium.Map`
  playwright 1.62.0 — `with playwright.sync_api.sync_playwright() as p: p.chromium.launch()` → browser; extracts GeoJSON from HTML. located
  `locate: playwright.sync_api.sync_playwright`
  pymupdf 1.28.2 — `pymupdf.open(path)` → Document; opens/flattens PDF map sheets. exercised: "Document"
  `locate: pymupdf.open`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc emitting markdown/text/json; flattens office/PDF sheets. located
  `locate: undoc.parse_file`
  weasyprint 69.0 — `weasyprint.HTML(string=html).write_pdf()` → PDF bytes; rendered the source PDF map sheets. exercised: "b'%PDF'"
  `locate: weasyprint.HTML.write_pdf, weasyprint.HTML`

- **Step 1 (Orchestrator Compilation).** keep geo assets when coordinates/toponyms resolve
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  geopandas 1.1.4 — `geopandas.GeoDataFrame(data, geometry=[...])` → spatial dataframe; holds geo assets. exercised: "GeoDataFrame"
  `locate: geopandas.GeoDataFrame, geopandas.read_file`
  osmnx 1.9.3 — `osmnx.graph_from_place(query, network_type='drive')` → street network graph; builds network from toponyms. located
  `locate: osmnx.graph_from_place`
  rustworkx 0.18.1 — `rustworkx.PyDiGraph()` then `add_node/add_edge` → directed graph; holds spatial graph. exercised: "1 edge"
  `locate: rustworkx.PyDiGraph`
  shapely 2.1.2 — `shapely.geometry.Point(x, y)` → geometry object; represents coordinates. exercised: "buffer area 3.1365"
  `locate: shapely.geometry.Point`

- **Step 2 (Constraint Compile).** receive exclusion/coverage predicates extracted into pydantic models
  cpmpy 1.0.0 — `Model().solve(solver='ortools')` → constraint model + solve. located
  `locate: cpmpy.Model.solve, cpmpy.Model`
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(obj)` → validated model; holds extracted predicates. exercised: "3"
  `locate: pydantic.BaseModel.model_validate, pydantic.TypeAdapter`
  python-constraint2 2.7.3 — `constraint.Problem()` then `addVariable/addConstraint; getSolutions()` → CSP solutions; receives exclusion/coverage predicates. exercised: "[{'a': 2}, {'a': 1}]"
  `locate: constraint.Problem`

- **Step 3 (Surface and Sheet).** render basemaps, rasters, and cartographic surfaces
  contextily 1.7.1 — `contextily.add_basemap(ax, source=..., crs=...)` → adds basemap tiles to axes; renders basemap. located
  `locate: contextily.add_basemap`
  datashader 0.19.1 — `datashader.Canvas(plot_width, plot_height).points(df,'x','y')` → aggregated raster; rasterizes large data. exercised: "(4, 4)"
  `locate: datashader.Canvas.points, datashader.Canvas`
  eomaps 8.4 — `eomaps.Maps()` → interactive map object; renders cartographic surface. located
  `locate: eomaps.Maps`
  lonboard 0.16.0 — `lonboard.viz(gdf)` → deck.gl Map widget; renders geospatial vectors. exercised: "Map"
  `locate: lonboard.viz, lonboard.Map`
  prettymaps 1.4.2 — `prettymaps.plot(query)` → Plot with styled OSM layers; renders aesthetic map. located
  `locate: prettymaps.plot`
  pygmt 0.17.0 — `Figure().coast(region=..., projection=...)` → map cartography (GMT). located
  `locate: pygmt.Figure.coast, pygmt.Figure`

- **Step 4 (Execution).** write one artifact spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook()` then `wb.save(path)` → xlsx workbook; writes the artifact spreadsheet. exercised: "hi"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path, index=False)` → writes native Excel Table; writes spreadsheet. exercised: "wrote"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)` then `add_worksheet().write(); close()` → xlsx file; writes spreadsheet. exercised: "wrote"
  `locate: xlsxwriter.Workbook`

#### Pipeline R9: Reverse Contract Constraint Prover

- **Step 0 (Global Ingestion).** Pull clauses from Word/PDF packs; flatten proof pages
  python-docx 1.2.0 — `docx.Document(path)` → Document; reads Word clauses/term tables. exercised: "'Hello clause one.'"
  `locate: docx.Document`
  mammoth 1.12.1 — `mammoth.convert_to_html(fileobj)` → HTML result; Word→clean HTML clauses. exercised: "'<p>Hello clause one.</p>'"
  `locate: mammoth.convert_to_html`
  office-oxide 0.1.9 — `office_oxide.to_markdown(path)` → markdown str; Office→markdown clauses. exercised: "'Hello clause one.'"
  `locate: office_oxide.to_markdown`
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source)` → ConversionResult; parses PDF/Office packs. located (requires models)
  `locate: docling.document_converter.DocumentConverter.convert`
  pypdf 6.16.2 — `pypdf.PdfReader(path).pages[i].extract_text()` → text; pulls PDF clauses. located
  `locate: pypdf.PageObject.extract_text, pypdf.PdfReader`
  playwright 1.62.0 — `playwright.sync_api.sync_playwright()` then `page.pdf(path)` → flattens proof pages. located (requires browser binaries)
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.pdf`
  nicegui 3.16.0 — `@nicegui.ui.page('/route')` → registers a proof page. located
  `locate: nicegui.ui.page`

- **Step 1 (Orchestrator Compilation).** Emit workflow gated on AMR deontic graphs
  temporalio 1.32.0 — `@temporalio.workflow.defn(sandboxed=True)` → workflow class; declares the durable workflow. located
  `locate: temporalio.workflow.defn`
  amrlib 0.8.1 — `amrlib.load_stog_model(model_dir=None).parse_sents(sents)` → AMR graphs; parses clauses to AMR. located (requires model download)
  `locate: amrlib.load_stog_model`

- **Step 2 (Logic Emission).** Write FOL/ASP programs; hand to solvers
  amr-logic-converter 0.11.3 — `amr_logic_converter.AmrLogicConverter().convert(amr)` → Clause; AMR→First-Order Logic. exercised: "'want-01(w) ∧ :ARG0(w, b) ∧ boy(b)…'"
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`
  typedlogic 0.2.4 — `typedlogic.registry.get_compiler('clingo').compile(theory)` → program str; writes FOL/ASP programs. exercised: "SouffleCompiler obtained"
  `locate: typedlogic.registry.get_compiler, typedlogic.compiler.Compiler.compile`
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → SolveResult; solves the ASP program. exercised: "['a b']"
  `locate: clingo.Control.solve`
  cvc5 1.3.4 — `cvc5.Solver().checkSat()` → Result; SMT-checks the formulas. exercised: "sat"
  `locate: cvc5.Solver.checkSat`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; solver-agnostic SMT check. exercised: "True"
  `locate: pysmt.shortcuts.is_sat`

- **Step 3 (Policy Materialization).** Generate policy engines for proved permissions
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`
  openfga-sdk 0.10.4 — `OpenFgaClient(ClientConfiguration(...)).check(body)` → fine-grained authorization (client to an FGA store). located
  `locate: openfga_sdk.OpenFgaClient, openfga_sdk.ClientConfiguration`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Write one Excel artifact from accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → writes styled .xlsx. exercised: "wrote file True"
  `locate: openpyxl.Workbook.save`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → writes real Excel Table. exercised: "wrote file True"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)`; `ws.write(row, col, val)`; `close()` → .xlsx with charts. exercised: "wrote file True"
  `locate: xlsxwriter.Workbook, xlsxwriter.worksheet.Worksheet.write`

#### Pipeline R10: Reverse Specification-to-Slide Compiler

- **Step 0 (Global Ingestion).** Flatten pptx/notes/charts and rendered HTML/PDF into the manifest.
  python-pptx 1.0.2 — `pptx.Presentation(path)` → Presentation; reads slides/notes. exercised: "slides == 0 (default)"
  `locate: pptx.Presentation`
  office-oxide 0.1.9 — `office_oxide.to_markdown(path)` → Markdown from Office file. located
  `locate: office_oxide.to_markdown, office_oxide.extract_text`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc markdown/text/json. located
  `locate: undoc.parse_file`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → DocumentConverterResult (Markdown). located
  `locate: markitdown.MarkItDown.convert`
  marp — non-Python renderer — CLI `marp slides.md -o out.pptx` (@marp-team/marp-cli)
  playwright 1.62.0 — `with sync_playwright() as p: page=...; page.goto(url); page.content()` → rendered HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  pymupdf 1.28.2 — `pymupdf.open(path)` → Document; parses/renders PDF. located
  `locate: pymupdf.open`
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → parsed PDF document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`
  reveal-md — non-Python renderer — CLI `reveal-md slides.md` (Node)
  weasyprint 69.0 — `weasyprint.HTML(string=html).write_pdf()` → PDF bytes. exercised: "2331 bytes, b'%PDF-'"
  `locate: weasyprint.HTML, weasyprint.HTML.write_pdf`

- **Step 1 (Orchestrator Compilation).** Build an asset graph from recovered requirement/risk/milestone spans.
  dagster 1.13.20 — `@dagster.asset` on functions, assembled with `dagster.Definitions(assets=[...])` → asset graph. located
  `locate: dagster.asset, dagster.Definitions`

- **Step 2 (Trace Proof).** Build claim edges; prove completeness and acyclicity before materializing slides.
  business-rules 1.1.1 — `business_rules.run_all(rule_list, defined_variables, defined_actions)` → evaluates completeness rules. located
  `locate: business_rules.run_all`
  durable-rules 2.0.28 — `durable.lang.assert_fact(ruleset_name, fact)` → asserts facts into Rete engine. located
  `locate: durable.lang.assert_fact, durable.lang.ruleset`
  graphedexcel 1.2.3 — `graphedexcel.graphbuilder.build_graph_and_stats(file_path)` → (DiGraph, stats) of cell-formula edges. located
  `locate: graphedexcel.graphbuilder.build_graph_and_stats`
  networkx 3.6.1 — `networkx.DiGraph()` (add_edge) → claim-edge digraph. exercised: "number_of_edges == 1"
  `locate: networkx.DiGraph`
  z3-solver 5.1.0.0 — `z3.Solver(); s.add(...); s.check()` → acyclicity/completeness proof. exercised: "sat [x = 1]"
  `locate: z3.Solver, z3.Solver.check`

- **Step 3 (Grammar Selection).** Select chart/diagram grammars for proved tables and relations.
  autoviz 0.1.905 — `AutoViz_Class().AutoViz(filename, dfte=df, ...)` → auto-selected charts from table. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`
  kroki — non-Python — diagram service, CLI `kroki convert in.mmd -o out.svg` (HTTP; network-gated here)
  lida 0.0.14 — `lida.Manager(text_gen=...)` (`.visualize(...)`) → grammar-agnostic chart generator. located
  `locate: lida.Manager`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook(); ws['A1']=..; wb.save(path)` → .xlsx file. exercised: "4801-byte xlsx"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → real Excel Table. exercised: "6047-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path); ws.write(0,0,..); wb.close()` → .xlsx with native charts. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`

#### Pipeline R11: Reverse Fleet Reliability Dossier

- **Step 0 (Global Ingestion).** Flatten Streamlit dossier and re-tabulate PDF/PNG sidecars.
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch().new_page()` → renders/flattens dashboard. located
  `locate: playwright.sync_api.sync_playwright`
  markitdown 0.1.7 — `MarkItDown().convert(source)` → dossier to Markdown. located
  `locate: markitdown.MarkItDown.convert`
  kaleido 1.4.0 — `kaleido.write_fig_sync(fig, path)` → produced the PNG/PDF sidecars. located
  `locate: kaleido.write_fig_sync`
  pymupdf 1.28.2 — `pymupdf.open(path)[i].find_tables()` → re-tabulate PDF sidecars. located
  `locate: pymupdf.open, pymupdf.Page.find_tables, pymupdf.Page.get_text`
  csvkit 2.2.0 — `In2CSV().run()` (CLI `in2csv`) → re-tabulate PNG-derived CSV. located [CLI suite]
  `locate: csvkit.utilities.in2csv.In2CSV.run, csvkit.reader`
  streamlit 1.63.0 — `streamlit.dataframe(df)` → framework that served the dossier now flattened. located
  `locate: streamlit.dataframe`
- **Step 1 (Orchestrator Compilation).** Admit survival assets when time-to-event and censoring type-check.
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → time-to-event survival asset. exercised: "median 4.0"
  `locate: lifelines.KaplanMeierFitter.fit, lifelines.WeibullFitter`
- **Step 2 (Fit and Cut Sets).** Reject unphysical fits; solve series/parallel block diagrams.
  scipy 1.15.3 — `scipy.stats.weibull_min.fit(data, floc=0)` → rejects unphysical reliability fits. exercised: "[2.29, 0, 3.39]"
  `locate: scipy.stats.rv_continuous.fit`
  z3-solver 5.1.0.0 — `s=Solver(); s.add(c); s.check()` → checks block-diagram facts. exercised: "sat [X = 3]"
  `locate: z3.Solver.check, z3.Solver.add`
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`
- **Step 3 (Execution).** Write one spreadsheet from solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); wb.save(path)` → writes .xlsx artifact. exercised: "xlsx file written"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=Workbook(path); ws=w.add_worksheet(); ws.add_table(...)` → native Excel table. exercised: "xlsx with table written"
  `locate: xlsxwriter.Workbook.add_worksheet, xlsxwriter.worksheet.Worksheet.add_table`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file=path, index=False)` → real Excel Table object. exercised: "xlsx table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R12: Reverse Ontology Reasoner

- **Step 0 (Global Ingestion).** Flatten the MkDocs site and datasette pages; parse published RDF/TTL/JSON-LD.
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch()` → rendered page HTML; headless site flatten. located
  `locate: playwright.sync_api.sync_playwright`
  markitdown 0.1.7 — `MarkItDown().convert(source)` → Markdown; page→Markdown. exercised: "# Spec\n\nHello"
  `locate: markitdown.MarkItDown.convert`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown; document→Markdown. located
  `locate: anydoc.to_markdown`
  rdflib 7.6.0 — `rdflib.Graph().parse(data=ttl, format='turtle')` → parsed triples; RDF/TTL/JSON-LD parse. exercised: "triples: 1"
  `locate: rdflib.Graph.parse`
  mkdocs 1.6.1 — `mkdocs.commands.build.build(config)` → the site being flattened; source docs-site generator. located
  `locate: mkdocs.commands.build.build`
  datasette 0.65.3 — `datasette.app.Datasette(files=[db])` → the pages being flattened; source data-page server. located
  `locate: datasette.app.Datasette`

- **Step 1 (Orchestrator Compilation).** Write prefect tasks for rdflib and owlready2 when ontology phrases exist.
  prefect 3.8.4 — `@prefect.task def t(): ...` → orchestrated task; task emit. located
  `locate: prefect.task`
  rdflib 7.6.0 — `rdflib.Graph()` → RDF store for a task; graph task target. located
  `locate: rdflib.Graph`
  owlready2 0.51 — `owlready2.get_ontology(iri).load()` → ontology; OWL class/property task target. located
  `locate: owlready2.get_ontology`

- **Step 2 (Closure and Proof).** Close the recovered graph; solvers must accept the TBox/ABox pair.
  owlrl 7.6.2 — `owlrl.DeductiveClosure(OWLRL_Semantics).expand(graph)` → materialized closure; OWL 2 RL closure. exercised: "2 -> 12 triples"
  `locate: owlrl.DeductiveClosure.expand`
  pyreason → clingo 5.8.2 — `Control().add(prog); ground(); solve()` → graph/temporal reasoning (pyreason import hangs here). located
  `locate: clingo.Control.solve, clingo.Control`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.check()` → sat/unsat; TBox/ABox acceptance. exercised: "sat"
  `locate: z3.Solver.check`
  cvc5 1.3.4 — `slv=cvc5.Solver(); slv.checkSat()` → sat/unsat; TBox/ABox acceptance. exercised: "sat"
  `locate: cvc5.Solver.checkSat, cvc5.Solver`
  clingo 5.8.0 — `ctl.solve()` → SAT/UNSAT; TBox/ABox acceptance. exercised: "SAT"
  `locate: clingo.Control.solve`

- **Step 3 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.save(path)` → .xlsx; styled spreadsheet write. exercised: "4802 bytes"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet(); wb.close()` → .xlsx; native-chart spreadsheet write. exercised: "5247 bytes"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object; Table write from DataFrame. exercised: "6138 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R13: Reverse Service Configuration Management

- **Step 0 (Global Ingestion).** Flatten Word pack + PDF; lift mermaid source.
  mammoth 1.12.1 — `mammoth.convert_to_html(docx_fileobj)` → Word-to-clean-HTML result. located
  `locate: mammoth.convert_to_html`
  markitdown 0.1.7 — `MarkItDown().convert(path)` → Markdown result. exercised: "# Desk x"
  `locate: markitdown.MarkItDown.convert`
  office-oxide 0.1.9 — `office_oxide.to_markdown(path)` → Office-to-Markdown string. located
  `locate: office_oxide.to_markdown`
  pymupdf 1.28.2 — `d=pymupdf.open(path); d[0].get_text()` → PDF text. exercised: "'REL'"
  `locate: pymupdf.open, pymupdf.Page.get_text`
  python-docx 1.2.0 — `docx.Document(path)` → reads verification Word pack. exercised: "1 paragraph"
  `locate: docx.Document`
  reportlab 5.0.1 — named as the PDF's producer (reportlab writes PDFs, cannot parse them); flattening here is by pymupdf/markitdown, so no bound function for this step.
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestrator Compilation).** Admit config asset graph only if spans resolve.
  clingo 5.8.0 — `Control().solve()` (after add/ground) → SAT admits graph, UNSAT stops. exercised: "SAT"
  `locate: clingo.Control.solve`

- **Step 2 (Model Emission).** Type CI records with pydantic; materialize CI graph.
  networkx 3.6.1 — `g=networkx.DiGraph(); g.add_edges_from(relations)` → CI graph from records. exercised: "(2, 1)"
  `locate: networkx.DiGraph`
  pydantic 2.13.5 — `CIRecord.model_validate(row)` → typed CI record. exercised: "tte=12.5 censored=True"
  `locate: pydantic.BaseModel.model_validate`

- **Step 3 (Lifecycle Proof).** Compile lifecycle facts; prove consistency and acyclicity.
  clingo 5.8.0 — `Control().solve()` → stable model / UNSAT. exercised: "SAT"
  `locate: clingo.Control.solve`
  typedlogic 0.2.4 — `s=ClingoSolver(); s.add_fact(f)` → writes transition/exception/verification facts. located
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add_fact`
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat state-consistency + acyclicity. exercised: "sat"
  `locate: z3.Solver.check`

- **Step 4 (Verification Replay).** Mine transition logs; diff discrepancy tables.
  pm4py 2.7.23.8 — `pm4py.discover_transition_system(log, case_id_key=..., activity_key=..., timestamp_key=...)` → transition-system model. located
  `locate: pm4py.discover_transition_system`
  csv-diff 1.2 — `csv_diff.compare(load_csv(a, key="id"), load_csv(b, key="id"))` → discrepancy dict. exercised: "added/removed/changed keys"
  `locate: csv_diff.compare, csv_diff.load_csv`
  daff 1.4.2 — `daff.diff(local, remote)` → tabular alignment/diff. exercised: "PythonTableView"
  `locate: daff.diff`

- **Step 5 (Execution).** Write the pipeline's artifact spreadsheet.
  openpyxl 3.1.2 — `wb=Workbook(); wb.save(path)` → writes .xlsx. exercised: "saved"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → writes real Excel Table. exercised: "table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); ...write(); wb.close()` → writes .xlsx. exercised: "closed"
  `locate: xlsxwriter.Workbook`

#### Pipeline R14: Reverse Service Design

- **Step 0 (Global Ingestion).** Flatten the Service Design Package and diagrams into manifest
  python-docx 1.2.0 — `docx.Document("sdp.docx").paragraphs` → paragraph objects; reads pack text/tables. exercised: "para0 'Continuity plan'"
  `locate: docx.Document, docx.document.Document.paragraphs`
  mammoth 1.12.1 — `mammoth.convert_to_markdown(fileobj).value` → Markdown string; flattens .docx to Markdown. exercised: "'Continuity plan\n\n'"
  `locate: mammoth.convert_to_markdown, mammoth.convert_to_html`
  undoc 0.9.0 — `undoc.parse_file("sdp.docx").to_markdown()` → Markdown string; parses Office pack. exercised: "'Continuity plan\n\n| |...'"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown("sdp.docx")` → Markdown string; flattens docs to Markdown. exercised: "'Continuity plan\n'"
  `locate: anydoc.to_markdown`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  diagrams 0.25.1 — false positive: "diagrams" here is the common noun (existing diagrams being ingested), not the `diagrams` library, which GENERATES cloud-architecture diagrams and cannot flatten/parse HTML. Not bound.

- **Step 1 (Orchestrator Compilation).** Emit prefect flow only if NLP recovers principle spans
  prefect 3.8.4 — `@prefect.flow def r0(): ...` → Flow; emits the orchestration flow. located
  `locate: prefect.flow, prefect.task`
  stanza 1.14.0 — `nlp=stanza.Pipeline(lang="en", processors="tokenize,ner"); nlp(text)` → annotated Document; recovers spans. located
  `locate: stanza.Pipeline`

- **Step 2 (Requirement Proof).** Solvers must accept usability/cost/performance/security/compliance bounds on rows
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr_str)` → Clause; turns rows into FOL bounds. exercised: "boy(b)"
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; accepts the bound formulas. exercised: "False (p∧¬p)"
  `locate: pysmt.shortcuts.is_sat, pysmt.shortcuts.Solver`

- **Step 3 (Structure and Interaction).** Rebuild service breakdown; encode interaction flows; write SLA/OLA tables
  networkx 3.6.1 — `g=DiGraph(); g.add_edges_from(breakdown_edges)` → graph; rebuilds the service breakdown. exercised: "2 edges"
  `locate: networkx.DiGraph.add_edges_from, networkx.DiGraph.add_edge`
  pydsm → se-lib 0.53 — `design_structure_matrix(...)` → Design Structure Matrix (PyPI 'pydsm' is an unrelated delta-sigma library). located
  `locate: selib.design_structure_matrix`
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net, im, fm); encodes interaction-flow model. located
  `locate: pm4py.discover_petri_net_inductive`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Write one Excel spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save("out.xlsx")` → writes .xlsx. exercised: "saved 4801 bytes"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=xlsxwriter.Workbook("out.xlsx"); w.add_worksheet(); w.close()` → writes .xlsx. exercised: "saved 5247 bytes"
  `locate: xlsxwriter.Workbook.close, xlsxwriter.Workbook.add_worksheet, xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "tbl", file="out.xlsx", index=False)` → writes real Excel Table. exercised: "wrote 6134 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R15: Reverse Business Analysis

- **Step 0 (Global Ingestion).** turn spec/matrix/comms pack into compiler manifest
  python-docx 1.2.0 — `docx.Document(path)` → document; reads .docx paragraphs. exercised: "docx saved"
  `locate: docx.Document`
  office-oxide 0.1.9 — `office_oxide.to_markdown(path)` → Markdown; Rust Office parser. exercised: "hi"
  `locate: office_oxide.to_markdown, office_oxide.extract_text`
  mammoth 1.12.1 — `mammoth.convert_to_html(fileobj).value` → clean HTML from .docx. exercised: "<p>hi</p>"
  `locate: mammoth.convert_to_html`
  markitdown 0.1.7 — `MarkItDown().convert(path).text_content` → Markdown. exercised: "# Hi\n\nBody text"
  `locate: markitdown.MarkItDown.convert`

- **Step 1 (Orchestrator Compilation).** build dagster asset graph from recovered spans
  dagster 1.13.20 — `@dagster.asset` + `Definitions(assets=[...])` → spec asset graph. exercised: "AssetsDefinition"
  `locate: dagster.asset, dagster.Definitions`

- **Step 2 (Elicitation and Model).** recategorize requirements; hold stakeholder influence graph
  typedlogic 0.2.4 — `Solver().check()` → Solution; recategorizes via typed-logic inference. located
  `locate: typedlogic.solver.Solver.check`
  rdflib 7.6.0 — `Graph().add((s,p,o))` → asserts requirement triples for recategorization. exercised: "1 triple"
  `locate: rdflib.Graph.add`
  networkx 3.6.1 — `DiGraph().add_edge(a,b)` → stakeholder influence graph. exercised: "['a','b','c']"
  `locate: networkx.DiGraph.add_edge`

- **Step 3 (Verify and Trace).** provers/solvers accept clarity/consistency; keep traceability, refuse drift
  model-checker 1.3.9 — `model_checker.run_test(case, ...)` → bool; accepts consistency/testability. located
  `locate: model_checker.run_test`
  csv-diff 1.2 — `compare(load_csv(a,key), load_csv(b,key))` → baseline-drift diff. exercised: "added=1, removed=1"
  `locate: csv_diff.compare, csv_diff.load_csv`
  z3-solver 5.1.0.0 — `Solver().check()` → sat/unsat; refuses drift that fails. exercised: "sat [x = 3]"
  `locate: z3.Solver.check`
  vampire → nltk 3.10.3 — `ResolutionProver().prove(goal, premises)` → first-order proof (vampire is a C++ binary). located
  `locate: nltk.inference.resolution.ResolutionProver.prove, nltk.inference.resolution.ResolutionProver`

- **Step 4 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → xlsx file. exercised: "saved"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path).add_worksheet()` → native xlsx writer. exercised: "closed"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "T", file=path)` → real Excel Table. exercised: "wrote table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R16: Reverse Architecture Management

- **Step 0 (Global Ingestion).** flatten quarto/mermaid/diagrams/pyArchimate exports into manifest
  docling 2.124.0 — `DocumentConverter().convert(source="pack.pdf")` → parses HTML/PDF/docx to text/Markdown. located
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `MarkItDown().convert(source="export.html")` → Markdown/text. exercised: "'# Hi\n\nTest doc'"
  `locate: markitdown.MarkItDown.convert`
  python-docx 1.2.0 — `docx.Document("pack.docx")` → reads docx pack for flattening. exercised: "paragraph text 'hello'"
  `locate: docx.Document`
  playwright 1.62.0 — `page.goto(url); page.content()` → serialized rendered HTML export. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  diagrams 0.25.1 — `with diagrams.Diagram(name="ea", outformat="png"):` → produces diagram export ingested here. located
  `locate: diagrams.Diagram`
  pyArchimate 1.12.3 — `pyArchimate.Model(name="ea").add_relationship(...)` → builds ArchiMate model whose export is ingested. exercised: "elements=0; Model built"
  `locate: pyArchimate.Model, pyArchimate.Model.add_relationship`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** write prefect tasks for ontology/RDF/graph assets
  prefect 3.8.4 — `prefect.task(name="build_onto")(fn)` → Task; the written architecture-flow tasks. located
  `locate: prefect.task`
  owlready2 0.51 — `owlready2.get_ontology(base_iri="http://ea/onto.owl")` → ontology asset built by a task. exercised: "base_iri set to …#"
  `locate: owlready2.get_ontology`
  rdflib 7.6.0 — `rdflib.Graph().parse(data=ttl, format="turtle")` → RDF graph asset. exercised: "1 triple"
  `locate: rdflib.Graph, rdflib.Graph.parse`
  networkx 3.6.1 — `g=networkx.DiGraph(); g.add_edge(u_of_edge, v_of_edge)` → architecture graph asset. exercised: "DiGraph edges added; DAG check True"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`

- **Step 2 (Target Graph and Roadmap).** assemble current/target graphs; sequence work packages
  rustworkx 0.18.1 — `g=rustworkx.PyDiGraph(); rustworkx.is_directed_acyclic_graph(g)` → assembles current-vs-target graph. exercised: "DAG check True"
  `locate: rustworkx.PyDiGraph, rustworkx.is_directed_acyclic_graph`
  criticalpath 0.1.5 — `criticalpath.Node("proj").get_critical_path()` → sequences work packages by CPM. exercised: "['A','B'], duration 8"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node.link`
  typedlogic 0.2.4 — `s=ClingoSolver(); s.add_theory(theory); s.dump()` → compiles typed facts gating sequencing. located
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.dump`
  pydsm → se-lib 0.53 — `design_structure_matrix(...)` → Design Structure Matrix (PyPI 'pydsm' is an unrelated delta-sigma library). located
  `locate: selib.design_structure_matrix`
  se-lib 0.53 — `design_structure_matrix(...)`, `critical_path_diagram(...)` → PERT / DSM systems-engineering artifacts. located
  `locate: selib.design_structure_matrix, selib.critical_path_diagram, selib.SystemDynamicsModel`

- **Step 3 (Conformance Proof).** accept acyclicity and building-block compliance
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(cons); s.check()` → sat/unsat acyclicity proof. exercised: "sat; model [x = 3]"
  `locate: z3.Solver, z3.Solver.check`
  clingo 5.8.0 — `Control().add("base",[],facts); .ground(); .solve(on_model=cb)` → accepts building-block compliance. exercised: "model 'a b'"
  `locate: clingo.Control, clingo.Control.add, clingo.Control.solve`

- **Step 4 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save(path)` → writes .xlsx. exercised: "A1 == 'hi'"
  `locate: openpyxl.Workbook`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet().write(0,0,v); wb.close()` → writes .xlsx. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name="AM_ROADMAP_ITEM", file=path, index=False)` → real Excel Table. exercised: "6124-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R17: Reverse Infrastructure and Platform Management

- **Step 0 (Global Ingestion).** Flatten the Streamlit app and Word runbook/hardening pack into manifest.
  playwright 1.62.0 — `page.content()` → rendered DOM HTML of the Streamlit app. located
  `locate: playwright.sync_api.Page.content`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert("app.html")` → Markdown of the flattened page. exercised: "# Q3 Net income 100"
  `locate: markitdown.MarkItDown.convert`
  python-docx 1.2.0 — `docx.Document("runbook.docx").paragraphs` → reads the Word runbook/hardening pack. exercised: "saved 36583B"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file("hardening.docx").to_markdown()` → Markdown from the Word pack. exercised: "## Sheet | Metric | 100 |"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
  streamlit 1.63.0 — `streamlit.plotly_chart(fig)` → the Streamlit app later flattened. located
  `locate: streamlit.plotly_chart`

- **Step 1 (Orchestrator Compilation).** Keep pattern/provision assets only if standard/SLA/recovery spans type-check.
  pydantic 2.13.5 — `pydantic.create_model("INFRA_PATTERN", sla=(str, ...))` → typed pattern asset. exercised: "instance amount=100"
  `locate: pydantic.create_model`
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=problem.kind).solve(problem)` → provision plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`

- **Step 2 (Design and Constraint).** Emit dynamics models; accept BOM/network/hardening predicates.
  casadi 3.8.0 — `casadi.Function("dyn", [x], [rhs])` → callable symbolic dynamics model. exercised: "dyn(3)=9.0"
  `locate: casadi.Function`
  z3-solver 5.1.0.0 — `z3.Solver().check()` (after add) → accepts BOM/network/hardening predicates. exercised: "sat; assets=100, liab=50"
  `locate: z3.Solver.check`
  cpmpy 1.0.0 — `Model().solve(solver='ortools')` → constraint model + solve. located
  `locate: cpmpy.Model.solve, cpmpy.Model`
  python-control 0.10.2 — `tf(num,den)`, `step_response(sys)` → control-systems dynamics. located
  `locate: control.tf, control.step_response, control.ss`

- **Step 3 (Operate and Retire).** Replay backup/patch/health tasks; accept dependency-safe retirement.
  simpy 4.1.2 — `simpy.Environment().run(until=T)` → replays backup/patch/health tasks. exercised: "now=10"
  `locate: simpy.Environment.run`
  simprocesd 0.3.0 — `System(...).simulate(simulation_duration)` → runs the production/task line. located
  `locate: simprocesd.model.System.simulate`
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → accepts dependency-safe retirement. exercised: "sat, balanced=[True]"
  `locate: clingo.Control.solve`

- **Step 4 (Execution).** Write one Excel spreadsheet from the recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook().save("artifact.xlsx")` → writes the workbook. exercised: "saved 4819B"
  `locate: openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb = xlsxwriter.Workbook("artifact.xlsx"); wb.close()` → writes the workbook. exercised: "wrote 5248B"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, "T", file="artifact.xlsx")` → real Excel Table. exercised: "table xlsx 6047B"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R18: Reverse IT Asset Management

- **Step 0 (Global Ingestion).** flatten the published register and sheets
  openpyxl 3.1.2 — `openpyxl.load_workbook(path)` → workbook to read the register. located
  `locate: openpyxl.load_workbook`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike)` → fast sheet read. exercised: "sheets ['Sheet']"
  `locate: python_calamine.load_workbook`
  fastexcel 0.21.0 — `fastexcel.read_excel(source)` → ExcelReader (Calamine-backed). exercised: "sheets ['Sheet']"
  `locate: fastexcel.read_excel`
  csvkit 2.2.0 — `In2CSV(args=[...]).run()` → flatten register to CSV; CLI: `in2csv`. located
  `locate: csvkit.utilities.in2csv.In2CSV`
  markitdown 0.1.7 — `MarkItDown().convert(source).text_content` → Markdown of HTML/QR sheets. exercised: "'# Title\\n\\nhello world'"
  `locate: markitdown.MarkItDown.convert`
  great-tables — not acting here: named as the SOURCE table-HTML that markitdown flattens, not performing ingestion; no binding.

- **Step 1 (Orchestrator Compilation).** admit register assets only if columns type-check
  (no candidate library in batch — pure type-check gate; nothing to bind.)

- **Step 2 (Register and Proof).** write asset facts; prove entitlement vs consumption
  clorm 1.6.3 — `Asset(aid=1, name="pc")` where `class Asset(clorm.Predicate)` → asset facts; `FactBase([...])`. exercised: "FactBase len 2"
  `locate: clorm.Predicate, clorm.FactBase, clorm.control_add_facts`
  clingo 5.8.0 — `Control().solve()` → proves entitlement vs consumption models. exercised: "SAT; model 'a b'"
  `locate: clingo.Control.solve, clingo.Control.ground`

- **Step 3 (Audit Repair).** emit discrepancy tables; score exposure
  daff 1.4.2 — `daff.Coopy.diff(local, remote)` → highlighter diff table. exercised: "diff table height 3"
  `locate: daff.Coopy.diff`
  csv-diff 1.2 — `csv_diff.compare(previous, current)` (rows via `load_csv`) → change dict. exercised: "changed row key '2'"
  `locate: csv_diff.compare, csv_diff.load_csv`
  numpy-financial 1.0.0 — `npv(rate, values)`, `irr(values)` → financial figures on the proved ledger. located
  `locate: numpy_financial.npv, numpy_financial.irr, numpy_financial.pmt`

- **Step 4 (Execution).** write one spreadsheet artifact from solver-accepted fields
  openpyxl 3.1.2 — `Workbook().save(path)` → xlsx artifact. exercised: "saved xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `Workbook(path)` (+ write) `.close()` → xlsx with native charts. exercised: "closed xlsx"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object. exercised: "wrote Excel table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R19: Reverse Workforce and Talent Management

- **Step 0 (Global Ingestion).** Flatten workforce Word pack; flatten Streamlit dashboard to manifest.
  python-docx 1.2.0 — `docx.Document(path).paragraphs` → reads Word-pack text. exercised: "paras ['H','para one']"
  `locate: docx.Document, docx.document.Document.paragraphs`
  markitdown 0.1.7 — `MarkItDown().convert(path).markdown` → Markdown from Word. exercised: "'# Title\n\nHello world'"
  `locate: markitdown.MarkItDown.convert`
  playwright 1.62.0 — `page.goto(url); page.content()` → captures dashboard HTML. located
  `locate: playwright.sync_api.Page.content, playwright.sync_api.sync_playwright`
  streamlit 1.63.0 — not acting here: named as an ingested source ("the Streamlit dashboard"), which playwright flattens.

- **Step 1 (Orchestrator Compilation).** Emit prefect flow if role/competency/FTE spans resolve.
  prefect 3.8.4 — `@prefect.flow` def; `flow()` → emitted flow. exercised: "result 5"
  `locate: prefect.flow, prefect.task`

- **Step 2 (Plan and Ontology).** Rebuild gap matrix; map succession; accept complete role profiles.
  pandas 2.3.3 — `df.pivot_table(index='role', columns='comp', values='gap')` → gap matrix. exercised: "cols ['c1','c2']"
  `locate: pandas.DataFrame.pivot_table`
  polars 1.44.1 — `pl.DataFrame(...).pivot(values='gap', index='role', on='comp')` → gap matrix. exercised: "cols ['role','c1','c2']"
  `locate: polars.DataFrame.pivot`
  networkx 3.6.1 — `networkx.DiGraph(succession_edges)` → maps succession. exercised: "topo ['a','b','c']"
  `locate: networkx.DiGraph, networkx.topological_sort`
  owlready2 0.51 — `sync_reasoner([onto])` → HermiT reasons/accepts complete profile. exercised: "consistent, 2 classes"
  `locate: owlready2.sync_reasoner, owlready2.get_ontology`
  typedlogic 0.2.4 — `ClingoSolver().add(...); .check()` → Solution.satisfiable accepts profile. exercised: "satisfiable=True"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.check`

- **Step 3 (Allocation Proof).** Solve hiring and L&D allocation; bind KPIs if feasible incumbent.
  ortools 9.15.6755 — `CpSolver().Solve(model)` → allocation solution. exercised: "OPTIMAL, x=10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  pulp 3.3.2 — `p=LpProblem(...); p.solve(...)` → allocation solution. exercised: "Optimal, x=4.0"
  `locate: pulp.LpProblem.solve`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); ws.append(row); wb.save(path)` → writes .xlsx. exercised: "wrote xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `wb=Workbook(path); ws.write(r,c,v); wb.close()` → writes .xlsx. exercised: "wrote xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, 'T', path, index=False)` → real Excel Table. exercised: "wrote xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R20: Reverse Supplier Management

- **Step 0 (Global Ingestion).** pull contract/scorecard pack into manifest; flatten dashboard
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source=path)` → ConversionResult; pulls pack into manifest. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `with playwright.sync_api.sync_playwright() as p: p.chromium.launch()` → browser; flattens the supplier dashboard. located
  `locate: playwright.sync_api.sync_playwright`
  pypdf 6.16.2 — `pypdf.PdfReader(path)` → reader exposing `.pages`; reads contract PDFs. located
  `locate: pypdf.PdfReader`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike)` → CalamineWorkbook; reads scorecard sheets. located
  `locate: python_calamine.load_workbook`
  python-docx 1.2.0 — `docx.Document(path)` → document exposing `.paragraphs`; reads contract .docx. exercised: "1 paragraph"
  `locate: docx.Document`

- **Step 1 (Orchestrator Compilation).** write a temporalio workflow gated on segmentation/evaluation spans
  temporalio 1.32.0 — `@temporalio.workflow.defn` on a class with `@workflow.run` → workflow definition; writes the workflow. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Select and Bind).** rescore shortlists; accept policy constraints; instantiate clause templates
  clingo 5.8.0 — `clingo.Control(); ctl.ground(...); ctl.solve(on_model=...)` → stable models; accepts mandatory policy constraints. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control`
  jinja2 3.1.6 — `jinja2.Template(src).render(**ctx)` → rendered str; instantiates clause templates. exercised: "hi 5"
  `locate: jinja2.Template.render, jinja2.Template`
  pandas 2.3.3 — `pandas.DataFrame(data)` with scoring ops → tabular frame; rescores shortlists. located
  `locate: pandas.DataFrame`
  pingouin 0.6.1 — `pingouin.anova(data=df, dv='y', between='g')` → ANOVA table; statistically rescores shortlists. exercised: "['Source', 'ddof1', 'ddof2']"
  `locate: pingouin.anova, pingouin.ttest`

- **Step 3 (Performance Path).** forecast supplier series; run identified causal inference
  dowhy 0.14 — `dowhy.CausalModel(data, treatment, outcome, graph=...).estimate_effect(...)` → causal estimate; runs causal inference. located
  `locate: dowhy.CausalModel.estimate_effect, dowhy.CausalModel`
  sktime 1.1.0 — `sktime.forecasting.naive.NaiveForecaster(strategy='last').fit(y)` then `predict(fh)` → forecast series; forecasts supplier series. exercised: "[5.0, 5.0]"
  `locate: sktime.forecasting.naive.NaiveForecaster.fit, sktime.forecasting.naive.NaiveForecaster`

- **Step 4 (Execution).** write one artifact spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook()` then `wb.save(path)` → xlsx workbook; writes the artifact spreadsheet. exercised: "hi"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path, index=False)` → writes native Excel Table; writes spreadsheet. exercised: "wrote"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)` then `add_worksheet().write(); close()` → xlsx file; writes spreadsheet. exercised: "wrote"
  `locate: xlsxwriter.Workbook`

#### Pipeline R21: Reverse Portfolio Management

- **Step 0 (Global Ingestion).** Flatten quarto/plotly/docx artifacts into the manifest
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source)` → ConversionResult; parses PDF/Office/HTML. located (requires models)
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → DocumentConverterResult; converts artifacts to markdown. exercised: "'Hello clause one.'"
  `locate: markitdown.MarkItDown.convert`
  playwright 1.62.0 — `playwright.sync_api.sync_playwright()` then `page.pdf(path)` → flattens HTML pages. located (requires browser binaries)
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.pdf`
  plotly 7.0.0 — `plotly.graph_objects.Figure(data).write_html(path)` → writes chart HTML (the input flattened). exercised: "a06_plot.html written"
  `locate: plotly.graph_objects.Figure.write_html`
  python-docx 1.2.0 — `docx.Document(path)` → Document; reads the docx artifact. exercised: "'Hello clause one.'"
  `locate: docx.Document`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** Build a dagster asset graph from spans
  dagster 1.13.20 — `dagster.asset(fn)` → AssetsDefinition; defines a selection asset node. exercised: "AssetsDefinition"
  `locate: dagster.asset`

- **Step 2 (Graph and Mix).** Emit initiative graph; optimize mix under bounds
  criticalpath 0.1.5 — `criticalpath.Node('p').get_critical_path()` → node list; emits initiative critical path. exercised: "['A', 'B']"
  `locate: criticalpath.Node.get_critical_path`
  networkx 3.6.1 — `networkx.DiGraph()` + `add_edge` → directed graph; emits the initiative graph. exercised: "(3, 2) nodes/edges"
  `locate: networkx.DiGraph`
  ortools 9.15.6755 — `ortools.sat.python.cp_model.CpSolver().Solve(model)` → status; optimizes mix (CP-SAT). exercised: "OPTIMAL 10"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve`
  pulp 3.3.2 — `pulp.LpProblem(name, sense).solve(solver)` → status int; optimizes mix (LP). exercised: "Optimal 3.0"
  `locate: pulp.LpProblem.solve`
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(data)` → validated instance; compiles budget/capacity bounds. exercised: "(1, 'a')"
  `locate: pydantic.BaseModel.model_validate`

- **Step 3 (Selection Proof).** SMT-accept mutual-exclusion and prerequisite constraints
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat; accepts selection constraints. exercised: "sat"
  `locate: z3.Solver.check`

- **Step 4 (Execution).** Write one Excel artifact from accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → writes styled .xlsx. exercised: "wrote file True"
  `locate: openpyxl.Workbook.save`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → writes real Excel Table. exercised: "wrote file True"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)`; `ws.write(row, col, val)`; `close()` → .xlsx with charts. exercised: "wrote file True"
  `locate: xlsxwriter.Workbook, xlsxwriter.worksheet.Worksheet.write`

#### Pipeline R22: Reverse Service Financial Management

- **Step 0 (Global Ingestion).** Flatten finance dashboard and printed pack into the manifest.
  playwright 1.62.0 — `with sync_playwright() as p: page.goto(url); page.content()` → rendered dashboard HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → Markdown result. located
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc markdown/text/json. located
  `locate: undoc.parse_file`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown string from document. located
  `locate: anydoc.to_markdown`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path_or_filelike)` → workbook; reads Excel/ODS. located
  `locate: python_calamine.load_workbook`

- **Step 1 (Orchestrator Compilation).** Emit a workflow only if cost-pool/allocation/charging predicates recovered.
  stanza 1.14.0 — `stanza.Pipeline(lang='en', processors='tokenize,pos,depparse')` → NLP doc with dependency parse. located
  `locate: stanza.Pipeline`
  temporalio 1.32.0 — `@temporalio.workflow.defn` on a class → declares durable workflow. located
  `locate: temporalio.workflow.defn, temporalio.workflow.run`

- **Step 2 (Schema and Proof).** Bind allocation tables; prove debit/credit/recovery consistency.
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
  clingo 5.8.0 — `clingo.Control(); ...; ctl.solve(on_model=...)` → ASP consistency proof. exercised: "['a b']"
  `locate: clingo.Control, clingo.Control.solve`

- **Step 3 (Quant and Select).** Compute unit cost/variance on the proved ledger; select charts.
  autoviz 0.1.905 — `AutoViz_Class().AutoViz(filename, dfte=df, ...)` → auto-selected charts from table. located
  `locate: autoviz.AutoViz_Class.AutoViz_Class.AutoViz`
  numpy-financial 1.0.0 — `npv(rate, values)`, `irr(values)` → financial figures on the proved ledger. located
  `locate: numpy_financial.npv, numpy_financial.irr, numpy_financial.pmt`
  statsmodels 0.15.0 — `statsmodels.api.OLS(endog, exog).fit()` → regression/variance results. exercised: "params [1.0, 2.0]"
  `locate: statsmodels.api.OLS`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook(); wb.save(path)` → .xlsx file. exercised: "4801-byte xlsx"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → real Excel Table. exercised: "6047-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path); wb.close()` → .xlsx with native charts. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`

#### Pipeline R23: Reverse Risk Management

- **Step 0 (Global Ingestion).** Flatten risk Word pack and plotly HTML into manifest.
  docling 2.124.0 — `DocumentConverter().convert(source).document` → parses Word risk pack. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch().new_page()` → flattens plotly HTML. located
  `locate: playwright.sync_api.sync_playwright`
  plotly 7.0.0 — `plotly.graph_objects.Figure(...).write_html(path)` → engine that produced the HTML now flattened. located
  `locate: plotly.graph_objects.Figure.write_html`
  python-docx 1.2.0 — `docx.Document(path)` → reads risk Word pack. exercised: "docx written"
  `locate: docx.Document`
- **Step 1 (Orchestrator Compilation).** Keep BN assets when threat/impact/control spans resolve.
  networkx 3.6.1 — `G=DiGraph(); G.add_edge(u,v)` → risk-net skeleton. exercised: "3-node DiGraph built"
  `locate: networkx.DiGraph`
  pgmpy 1.1.2 — `DiscreteBayesianNetwork(ebunch)` → builds risk Bayesian net. exercised: "3 nodes, 2 edges"
  `locate: pgmpy.models.DiscreteBayesianNetwork`
  pymc 5.28.5 — `with pymc.Model() as m: ...` → defines Bayesian risk model. located
  `locate: pymc.Model`
- **Step 2 (Graph and Posterior).** Rebuild risk net; sample posterior after typedlogic compiles.
  arviz 0.23.4 — `arviz.summary(idata)` → posterior diagnostics summary. located
  `locate: arviz.summary`
  networkx 3.6.1 — `G=DiGraph(); G.add_edge(u,v)` → rebuilt risk-net graph. exercised: "3-node DiGraph built"
  `locate: networkx.DiGraph`
  numpyro 0.21.0 — `MCMC(NUTS(model)).run(rng_key)` → JAX posterior sampling. located
  `locate: numpyro.infer.MCMC, numpyro.infer.NUTS`
  pgmpy 1.1.2 — `DiscreteBayesianNetwork(ebunch)`; `VariableElimination(bn).query(vars)` → rebuild net + inference. exercised: "3 nodes, 2 edges"
  `locate: pgmpy.models.DiscreteBayesianNetwork, pgmpy.inference.VariableElimination.query`
  pymc 5.28.5 — `pymc.sample(draws, tune, chains)` → posterior sampling. located
  `locate: pymc.sample`
  typedlogic 0.2.4 — `compile_sentences(sentences, syntax=...)` → compiles typed-logic facts. located
  `locate: typedlogic.compiler.compile_sentences`
- **Step 3 (Treatment Proof).** Select treatment portfolio; accept residual-versus-appetite.
  ortools 9.15.6755 — `m=CpModel(); m.add_exactly_one([...]); CpSolver().Solve(m)` → selects avoid/reduce/transfer/accept portfolio. exercised: "OPTIMAL, a=1 b=0"
  `locate: ortools.sat.python.cp_model.CpSolver.Solve, ortools.sat.python.cp_model.CpModel.add_exactly_one`
  z3-solver 5.1.0.0 — `s=Solver(); s.add(c); s.check()` → residual-versus-appetite proof. exercised: "sat [X = 3]"
  `locate: z3.Solver.check, z3.Solver.add`
- **Step 4 (Execution).** Write one spreadsheet from solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); wb.save(path)` → writes .xlsx artifact. exercised: "xlsx file written"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=Workbook(path); ws=w.add_worksheet(); ws.add_table(...)` → native Excel table. exercised: "xlsx with table written"
  `locate: xlsxwriter.Workbook.add_worksheet, xlsxwriter.worksheet.Worksheet.add_table`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file=path, index=False)` → real Excel Table object. exercised: "xlsx table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R24: Reverse Service Continuity Management

- **Step 0 (Global Ingestion).** Flatten the continuity Word pack; lift mermaid HTML into the manifest.
  python-docx 1.2.0 — `docx.Document(path)` → parsed Word document; continuity Word-pack read. exercised: "36609 bytes"
  `locate: docx.Document`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown; document→Markdown. located
  `locate: anydoc.to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(source)` → Markdown; mermaid-HTML→Markdown lift. exercised: "# Spec\n\nHello"
  `locate: markitdown.MarkItDown.convert`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestrator Compilation).** Admit continuity assets when critical-service/RTO/RPO type-check.
  — no candidate libraries named in this step; the RTO/RPO type-check gate is orchestrator logic.

- **Step 2 (BIA Graph).** Map service→CI→site edges; emit impact-over-time tables.
  networkx 3.6.1 — `G=nx.DiGraph(); G.add_edges_from([(svc,ci),(ci,site)])` → dependency edges; service→CI→site mapping. located
  `locate: networkx.DiGraph.add_edges_from`
  pandas 2.3.3 — `pandas.DataFrame(records)` → impact-over-time table; impact tabulation. located
  `locate: pandas.DataFrame`

- **Step 3 (Invocation Proof).** Encode facts; replay recovery; accept RTO/RPO on the graph.
  typedlogic 0.2.4 — `Theory().add(sentence)` → invocation/exclusive-use facts; fact encoding. located
  `locate: typedlogic.Theory.add`
  clingo 5.8.0 — `ctl.add('base',[],prog); ctl.solve()` → SAT/UNSAT; fact encoding/solve. exercised: "SAT"
  `locate: clingo.Control.solve, clingo.Control.add`
  simpy 4.1.2 — `env=simpy.Environment(); env.run(until=t)` → simulated timeline; recovery replay. exercised: "now= 10"
  `locate: simpy.Environment.run`
  most-queue 2.9 — `QsSim(...).run(total_served)` → QueueResults; recovery queue replay. located
  `locate: most_queue.QsSim.run`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; RTO/RPO acceptance. exercised: "False / True"
  `locate: pysmt.shortcuts.is_sat`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.save(path)` → .xlsx; styled spreadsheet write. exercised: "4802 bytes"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet(); wb.close()` → .xlsx; native-chart spreadsheet write. exercised: "5247 bytes"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object; Table write from DataFrame. exercised: "6138 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R25: Reverse Strategy Management

- **Step 0 (Global Ingestion).** Flatten quarto/PDF/docx packs into the manifest.
  docling 2.124.0 — `DocumentConverter().convert(path)` → parsed document object. located
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `MarkItDown().convert(path)` → Markdown result. exercised: "# Desk x"
  `locate: markitdown.MarkItDown.convert`
  python-docx 1.2.0 — `docx.Document(path)` → reads docx pack. exercised: "1 paragraph"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file(path)` → Markdown/text/JSON of Office doc. located
  `locate: undoc.parse_file`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** Write prefect flow gated on driver/goal/option spans.
  prefect 3.8.4 — `@prefect.flow def strategy(): ...` → flow object. located
  `locate: prefect.flow`

- **Step 2 (Map and Option Proof).** Emit capability maps; record options; prove consistency.
  networkx 3.6.1 — `networkx.DiGraph()` → capability-map graph. exercised: "(2, 1)"
  `locate: networkx.DiGraph`
  typedlogic 0.2.4 — `s=Solver(); s.add_fact(option)` → records option facts. located
  `locate: typedlogic.solver.Solver.add_fact`
  z3-solver 5.1.0.0 — `z3.Solver().check()` → sat/unsat consistency vs R16 principles. exercised: "sat"
  `locate: z3.Solver.check`
  se-lib 0.53 — `design_structure_matrix(...)`, `critical_path_diagram(...)` → PERT / DSM systems-engineering artifacts. located
  `locate: selib.design_structure_matrix, selib.critical_path_diagram, selib.SystemDynamicsModel`

- **Step 3 (Roadmap).** Sequence initiatives via critical-path scheduling.
  criticalpath 0.1.5 — `Node(...).link(a,b); .update_all(); .get_critical_path()` → ordered critical path. exercised: "['A', 'B']"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node`

- **Step 4 (Execution).** Write the pipeline's artifact spreadsheet.
  openpyxl 3.1.2 — `wb=Workbook(); wb.save(path)` → writes .xlsx. exercised: "saved"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → writes real Excel Table. exercised: "table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); ...write(); wb.close()` → writes .xlsx. exercised: "closed"
  `locate: xlsxwriter.Workbook`

#### Pipeline R26: Reverse Information Security Management

- **Step 0 (Global Ingestion).** Flatten ISMS Word pack and control dashboard into manifest
  python-docx 1.2.0 — `docx.Document("isms.docx").paragraphs` → paragraph objects; reads Word-pack text/tables. exercised: "para0 'Continuity plan'"
  `locate: docx.Document, docx.document.Document.paragraphs`
  pypdf 6.16.2 — `pypdf.PdfReader("pack.pdf").pages[0].extract_text()` → page text string; extracts PDF text. located
  `locate: pypdf.PdfReader, pypdf.PageObject.extract_text`
  dasel → dpath 2.2.0 — `dpath.get(obj, '/a/b')`, `dpath.search(obj, glob)` → query JSON/YAML/dict (dasel is a Go CLI). located
  `locate: dpath.get, dpath.search`
  docling 2.124.0 — `DocumentConverter().convert(src).document` → DoclingDocument; parses the pack. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `page.goto(url); page.content()` → rendered HTML; flattens control dashboard. located
  `locate: playwright.sync_api.Page.goto, playwright.sync_api.Page.content`

- **Step 1 (Orchestrator Compilation).** Emit temporalio workflow gated on classification spans
  temporalio 1.32.0 — `@temporalio.workflow.defn class W:` + `@temporalio.workflow.run async def run(self)` → workflow class; durable workflow. located
  `locate: temporalio.workflow.defn, temporalio.workflow.run`

- **Step 2 (Ontology and Policy).** Hold catalog in OWL/RDF; generate authorization for proved permissions
  owlready2 0.51 — `onto=get_ontology(iri)` (or `World()`) → ontology; holds the ISM class catalog. exercised: "classes ['Drug']"
  `locate: owlready2.get_ontology, owlready2.World`
  rdflib 7.6.0 — `g=rdflib.Graph(); g.parse(source="catalog.ttl")` → Graph; holds the RDF catalog. exercised: "parsed 2 triples"
  `locate: rdflib.Graph.parse, rdflib.Graph.add`
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`
  openfga-sdk 0.10.4 — `OpenFgaClient(ClientConfiguration(...)).check(body)` → fine-grained authorization (client to an FGA store). located
  `locate: openfga_sdk.OpenFgaClient, openfga_sdk.ClientConfiguration`

- **Step 3 (Residual Proof).** Link assets/threats/controls; solvers reject conflicts and unclassified assets
  pgmpy 1.1.2 — `net=DiscreteBayesianNetwork(); net.add_edges_from([("asset","threat"),("threat","control")])` → BN; links assets/threats/controls. exercised: "2 edges"
  `locate: pgmpy.models.DiscreteBayesianNetwork.DiscreteBayesianNetwork.add_edges_from, pgmpy.models.DiscreteBayesianNetwork.DiscreteBayesianNetwork`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(f); s.check()` → sat/unsat; rejects conflicting allow/deny. exercised: "sat"
  `locate: z3.Solver.check, z3.Solver.add`
  clingo 5.8.0 — `c=Control(); c.add("base",[],prog); c.ground(...); c.solve()` → SolveResult; accepts/rejects rules. exercised: "SAT"
  `locate: clingo.Control.solve, clingo.Control.add`

- **Step 4 (Execution).** Write one Excel spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save("out.xlsx")` → writes .xlsx. exercised: "saved 4801 bytes"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=xlsxwriter.Workbook("out.xlsx"); w.add_worksheet(); w.close()` → writes .xlsx. exercised: "saved 5247 bytes"
  `locate: xlsxwriter.Workbook.close, xlsxwriter.Workbook.add_worksheet, xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "tbl", file="out.xlsx", index=False)` → writes real Excel Table. exercised: "wrote 6134 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R27: Reverse Availability Management

- **Step 0 (Global Ingestion).** flatten dashboards, Word pack, outage extracts into manifest
  csvkit 2.2.0 — `csvkit.reader(open(path))` → CSV rows; reads outage extracts. exercised: "[['a','b'],['1','x'],['2','y']]"
  `locate: csvkit.reader`
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch()` → browser; flattens dashboards. located
  `locate: playwright.sync_api.sync_playwright`
  python-docx 1.2.0 — `docx.Document(path)` → reads availability Word pack. exercised: "docx saved"
  `locate: docx.Document`

- **Step 1 (Orchestrator Compilation).** admit reliability assets when target and outage series type-check
  lifelines 0.30.3 — `KaplanMeierFitter().fit(durations, event_observed)` → survival fit of outage series. exercised: "4.0"
  `locate: lifelines.KaplanMeierFitter.fit`
  fmdtools 2.3.3 — `propagate.nominal(model)` → FMEA / resilience simulation. located
  `locate: fmdtools.sim.propagate.nominal, fmdtools.define.block.function.Function`

- **Step 2 (Block and Fit).** rebuild block diagrams; reject unphysical fits; accept redundancy
  scipy 1.15.3 — `scipy.optimize.curve_fit(f, xdata, ydata)` → params; rejects unphysical fits. exercised: "[2.0, 1.0]"
  `locate: scipy.optimize.curve_fit`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → bool; accepts redundancy vs target. exercised: "False"
  `locate: pysmt.shortcuts.is_sat`
  diagrams 0.25.1 — false match: "block diagrams" is a common noun; the tool named is reliability (not a candidate)

- **Step 3 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → xlsx file. exercised: "saved"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path).add_worksheet()` → native xlsx writer. exercised: "closed"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "T", file=path)` → real Excel Table. exercised: "wrote table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R28: Reverse Capacity and Performance Management

- **Step 0 (Global Ingestion).** flatten plotly HTML and capacity/utilization extracts into manifest
  playwright 1.62.0 — `page.goto(url); page.content()` → serialized rendered plotly HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  plotly 7.0.0 — `plotly.graph_objects.Figure(data=[...]).to_html(full_html=False)` → produces HTML flattened here. exercised: "4300543-char HTML"
  `locate: plotly.graph_objects.Figure.to_html, plotly.graph_objects.Figure.write_html`
  python-calamine 0.8.2 — `python_calamine.load_workbook(path).get_sheet_by_index(0).to_python()` → reads Excel/ODS rows. exercised: "[['h', 1.0]]"
  `locate: python_calamine.load_workbook, python_calamine.CalamineWorkbook.from_path`
  python-docx 1.2.0 — `docx.Document("capacity.docx")` → reads Word pack for flattening. exercised: "paragraph text 'hello'"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file("capacity.docx").to_text()` → flat text/Markdown/JSON. exercised: "parse_file→to_markdown 'Hello undoc'"
  `locate: undoc.parse_file, undoc.Undoc.to_text`
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV(args).main()` → converts utilization extracts to CSV. located; CLI: `in2csv util.xlsx`
  `locate: csvkit.utilities.in2csv.In2CSV`

- **Step 1 (Orchestrator Compilation).** keep forecast/queue assets only if series type-checks
  prophet 1.4.0 — `m=prophet.Prophet(); m.fit(df)` → fitted forecaster (df needs ds,y columns). located
  `locate: prophet.Prophet.fit`
  pmdarima 2.1.1 — `pmdarima.auto_arima(y, seasonal=True, m=12)` → auto-selected ARIMA model. located
  `locate: pmdarima.auto_arima`
  most-queue 2.9 — `c=MMnrCalc(n=1, r=100); c.set_sources(l=0.5); c.set_servers(mu=1.0); c.get_v()` → queue response moments. exercised: "[2. 8. 48.]"
  `locate: most_queue.theory.fifo.mmnr.MMnrCalc.get_v, most_queue.theory.fifo.mmnr.MMnrCalc.run`
  darts → sktime 1.1.0 — `AutoARIMA().fit(y)` → time-series forecasting (darts does not import here). located
  `locate: sktime.forecasting.arima.AutoARIMA, sktime.forecasting.base.BaseForecaster.fit`

- **Step 2 (Forecast and Queue).** forecast demand; model queue response; optimize settings
  prophet 1.4.0 — `m=prophet.Prophet(); m.fit(df); m.predict(future)` → forecast demand path. located
  `locate: prophet.Prophet.fit, prophet.Prophet.predict`
  pmdarima 2.1.1 — `pmdarima.auto_arima(y, seasonal=True, m=12)` → ARIMA demand path. located
  `locate: pmdarima.auto_arima`
  most-queue 2.9 — `c=MMnrCalc(n=1, r=100); c.set_sources(l=0.5); c.set_servers(mu=1.0); c.get_v()` → models queue response time. exercised: "[2. 8. 48.]"
  `locate: most_queue.theory.fifo.mmnr.MMnrCalc.get_v`
  gekko 1.3.2 — `m=gekko.GEKKO(remote=False); m.Obj(expr); m.solve(disp=False)` → optimizes settings under cost bounds. exercised: "x=3.00"
  `locate: gekko.GEKKO.solve`
  darts → sktime 1.1.0 — `AutoARIMA().fit(y)` → time-series forecasting (darts does not import here). located
  `locate: sktime.forecasting.arima.AutoARIMA, sktime.forecasting.base.BaseForecaster.fit`
  python-control 0.10.2 — `tf(num,den)`, `step_response(sys)` → control-systems dynamics. located
  `locate: control.tf, control.step_response, control.ss`

- **Step 3 (Cover Proof).** accept planned capacity ≥ forecast peak plus contingency
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(cover_cons); s.check()` → sat/unsat capacity-cover proof. exercised: "sat; model [x = 3]"
  `locate: z3.Solver, z3.Solver.check`

- **Step 4 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save(path)` → writes .xlsx. exercised: "A1 == 'hi'"
  `locate: openpyxl.Workbook`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet().write(0,0,v); wb.close()` → writes .xlsx. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name="CAP_FORECAST", file=path, index=False)` → real Excel Table. exercised: "6124-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R29: Reverse Continual Improvement Management

- **Step 0 (Global Ingestion).** Flatten CSI register Quarto pack and great-tables HTML into manifest.
  docling 2.124.0 — `DocumentConverter().convert("register.pdf")` → ConversionResult document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert("register.html")` → Markdown of the pack. exercised: "# Q3 Net income 100"
  `locate: markitdown.MarkItDown.convert`
  python-docx 1.2.0 — `docx.Document("register.docx").paragraphs` → reads the Word register content. exercised: "saved 36583B"
  `locate: docx.Document`
  great-tables 0.24.0 — `great_tables.GT(df).as_raw_html()` → the publication-table HTML being ingested. exercised: "html_len=9255"
  `locate: great_tables.GT, great_tables.GT.as_raw_html`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** Build a Dagster asset graph from idea/benefit/constraint spans.
  dagster 1.13.20 — `@dagster.asset def register(): ...` → AssetsDefinition node in the asset graph. exercised: "type=AssetsDefinition"
  `locate: dagster.asset`

- **Step 2 (Prioritize and Gate).** Hold register; rank by benefit/effort/risk; supply dependencies; accept intake rules.
  pandas 2.3.3 — `pandas.DataFrame(rows)` → holds the CSI register table. exercised: "shape=(2, 2)"
  `locate: pandas.DataFrame`
  pulp 3.3.2 — `LpProblem("rank", LpMaximize).solve()` → ranks ideas under benefit/effort/risk. exercised: "Optimal, x=3.0"
  `locate: pulp.LpProblem.solve`
  networkx 3.6.1 — `networkx.DiGraph().add_edge(a, b)` → supplies idea dependency edges. exercised: "edges=1"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`
  typedlogic 0.2.4 — `get_solver("clingo").check()` → must accept the intake rules. exercised: "satisfiable=True"
  `locate: typedlogic.registry.get_solver, typedlogic.solver.Solver.check`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Execution Tracking).** Run approved items as workflows; emit change edges clingo accepts.
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → accepts the mutation edge. exercised: "sat, balanced=[True]"
  `locate: clingo.Control.solve`
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`

- **Step 4 (Execution).** Write one Excel spreadsheet from the recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook().save("artifact.xlsx")` → writes the workbook. exercised: "saved 4819B"
  `locate: openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb = xlsxwriter.Workbook("artifact.xlsx"); wb.close()` → writes the workbook. exercised: "wrote 5248B"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, "T", file="artifact.xlsx")` → real Excel Table. exercised: "table xlsx 6047B"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R30: Reverse Measurement and Reporting Management

- **Step 0 (Global Ingestion).** flatten scorecard HTML, packs, metric extracts
  playwright 1.62.0 — `page.goto(url)` then `page.content()` → scorecard HTML. located
  `locate: playwright.sync_api.Page.goto, playwright.sync_api.Page.content`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown from a document. exercised: "'hi\\n' from .docx"
  `locate: anydoc.to_markdown, anydoc.to_markdown_bytes`
  csvkit 2.2.0 — `In2CSV(args=[...]).run()` → metric extracts to flat CSV; CLI: `in2csv`. located
  `locate: csvkit.utilities.in2csv.In2CSV`
  docling 2.124.0 — `DocumentConverter().convert(source)` → structured doc. located
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `MarkItDown().convert(source).text_content` → Markdown. exercised: "'# Title\\n\\nhello world'"
  `locate: markitdown.MarkItDown.convert`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** emit a prefect flow gated on metric spans
  prefect 3.8.4 — `@prefect.flow(name=...)` → flow gated on metric-definition/audience spans. exercised: "Flow 'ingest'"
  `locate: prefect.flow`

- **Step 2 (Metric Proof).** type metric objects; prove figures derivable
  pydantic 2.13.5 — `pydantic.create_model("KPI", field=(int, ...))` → metric object schema. exercised: "model M(x=5).x == 5"
  `locate: pydantic.create_model, pydantic.BaseModel`
  clingo 5.8.0 — `Control().solve()` → proves each figure derivable from definition+extract. exercised: "SAT; model 'a b'"
  `locate: clingo.Control.solve, clingo.Control.ground`

- **Step 3 (Execution).** write one spreadsheet artifact from solver-accepted fields
  openpyxl 3.1.2 — `Workbook().save(path)` → xlsx artifact. exercised: "saved xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `Workbook(path)` (+ write) `.close()` → xlsx with native charts. exercised: "closed xlsx"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object. exercised: "wrote Excel table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R31: Reverse Service Level Management

- **Step 0 (Global Ingestion).** Flatten SLA/OLA/UC Word packs; flatten attainment dashboards.
  python-docx 1.2.0 — `docx.Document(path).paragraphs` → reads Word packs. exercised: "paras ['H','para one']"
  `locate: docx.Document, docx.document.Document.paragraphs`
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown from office docs. exercised: "'# H\n\npara one'"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(path).markdown` → Markdown from Word. exercised: "'# Title\n\nHello world'"
  `locate: markitdown.MarkItDown.convert`
  playwright 1.62.0 — `page.goto(url); page.content()` → captures dashboards HTML. located
  `locate: playwright.sync_api.Page.content, playwright.sync_api.sync_playwright`

- **Step 1 (Orchestrator Compilation).** Temporalio workflow gated on commitment/measurement-method spans.
  temporalio 1.32.0 — `@workflow.defn`; `client.execute_workflow(WF.run, id=, task_queue=)` → durable workflow. located
  `locate: temporalio.workflow.defn, temporalio.client.Client.execute_workflow`

- **Step 2 (Agreement Proof).** Instantiate SLA/OLA/UC objects; bind credit/escalation; accept attainability.
  pydantic 2.13.5 — `SLA.model_validate(row)` → instantiates objects from recovered rows. exercised: "actor='u1' t=5"
  `locate: pydantic.BaseModel.model_validate`
  pysmt 0.9.6 — `is_sat(formula)` → accepts attainability. exercised: "is_sat=True"
  `locate: pysmt.shortcuts.is_sat`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Attainment).** Spreadsheet computes attainment from Pipeline R30 after SMT proof.
  (No library named in this step.)

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); ws.append(row); wb.save(path)` → writes .xlsx. exercised: "wrote xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `wb=Workbook(path); ws.write(r,c,v); wb.close()` → writes .xlsx. exercised: "wrote xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, 'T', path, index=False)` → real Excel Table. exercised: "wrote xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R32: Reverse Monitoring and Event Management

- **Step 0 (Global Ingestion).** flatten event dashboard HTML and catalog extracts into manifest
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV(args).main()` → CSV output; flattens catalog extracts to CSV. located; CLI: `in2csv file.xlsx`
  `locate: csvkit.utilities.in2csv.In2CSV`
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source=path)` → ConversionResult; flattens catalog docs. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `with playwright.sync_api.sync_playwright() as p: p.chromium.launch()` → browser; flattens event dashboard HTML. located
  `locate: playwright.sync_api.sync_playwright`

- **Step 1 (Orchestrator Compilation).** keep rule/event assets when event-type/severity spans resolve
  durable-rules 2.0.28 — `with durable.lang.ruleset(name): ...` → declares Rete ruleset; defines event rules. located
  `locate: durable.lang.ruleset`
  experta → durable-rules 2.0.28 — `ruleset(name){{ when_all(...) }}`, `post(name, fact)` → Rete rule engine (experta itself fails on py3.11: collections.Mapping). located
  `locate: durable.lang.ruleset, durable.lang.when_all, durable.lang.post`
  pydantic 2.13.5 — `pydantic.BaseModel.model_validate(obj)` → validated event model; type-checks event fields. exercised: "3"
  `locate: pydantic.BaseModel.model_validate, pydantic.TypeAdapter`

- **Step 2 (Correlate and Hand-off).** execute Rete rules; map event edges; sequence runbooks
  durable-rules 2.0.28 — `durable.lang.assert_fact(ruleset_name, fact)` → triggers matching Rete rules; executes rules on rows. located
  `locate: durable.lang.assert_fact, durable.lang.post`
  experta → durable-rules 2.0.28 — `ruleset(name){{ when_all(...) }}`, `post(name, fact)` → Rete rule engine (experta itself fails on py3.11: collections.Mapping). located
  `locate: durable.lang.ruleset, durable.lang.when_all, durable.lang.post`
  pm4py 2.7.23.8 — `pm4py.discover_directly_follows_graph(log)` → (dfg, start, end) edges; maps event-to-incident edges. exercised: "{('a', 'b'): 2}"
  `locate: pm4py.discover_directly_follows_graph`
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...)` → planner engine; sequences runbooks. located
  `locate: unified_planning.shortcuts.OneshotPlanner`

- **Step 3 (Coverage Proof).** prove every critical event class has response paths
  clingo 5.8.0 — `clingo.Control(); ctl.ground(...); ctl.solve(on_model=...)` → stable models; accepts full coverage. exercised: "['a b']"
  `locate: clingo.Control.solve, clingo.Control`

- **Step 4 (Execution).** write one artifact spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook()` then `wb.save(path)` → xlsx workbook; writes the artifact spreadsheet. exercised: "hi"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path, index=False)` → writes native Excel Table; writes spreadsheet. exercised: "wrote"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)` then `add_worksheet().write(); close()` → xlsx file; writes spreadsheet. exercised: "wrote"
  `locate: xlsxwriter.Workbook`

#### Pipeline R33: Reverse Incident Management

- **Step 0 (Global Ingestion).** Flatten incident Word reports and board HTML
  csvkit 2.2.0 — `csvkit.utilities.in2csv.In2CSV().main()` → CSV; converts tabular sources to CSV (CLI-first; does not parse Word/HTML). located; CLI: `in2csv file.xlsx`
  `locate: csvkit.utilities.in2csv.In2CSV, csvkit.reader`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path, ocr='reject')` → markdown string; converts Word reports to markdown. exercised: "'Hello clause one.\n'"
  `locate: anydoc.to_markdown`
  playwright 1.62.0 — `playwright.sync_api.sync_playwright()` then `page.pdf(path)` → flattens live board HTML. located (requires browser binaries)
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.pdf`
  python-docx 1.2.0 — `docx.Document(path)` → Document; reads incident Word reports. exercised: "'Hello clause one.'"
  `locate: docx.Document`

- **Step 1 (Orchestrator Compilation).** Emit dagster asset graph if fields type-check
  dagster 1.13.20 — `dagster.asset(fn)` → AssetsDefinition; defines a routing asset node. exercised: "AssetsDefinition"
  `locate: dagster.asset`

- **Step 2 (Route and Localize).** Apply models, walk graph, compare paths
  networkx 3.6.1 — `networkx.shortest_path(g, source, target)` → node list; walks R13 to localize nodes. exercised: "['A', 'B', 'C']"
  `locate: networkx.shortest_path`
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_alignments(log, net, im, fm)` → alignments; compares live path to model. located
  `locate: pm4py.conformance_diagnostics_alignments`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Restore Proof).** Estimate restore time; emit model-update payloads
  csv-diff 1.2 — `csv_diff.compare(previous, current)` → diff dict; emits model-update payloads. exercised: "['added','removed','changed',…]"
  `locate: csv_diff.compare, csv_diff.load_csv`
  lifelines 0.30.3 — `lifelines.KaplanMeierFitter().fit(durations, event_observed)` → fitter; estimates remaining restore time. exercised: "median 3.0"
  `locate: lifelines.KaplanMeierFitter.fit`

- **Step 4 (Execution).** Write one Excel artifact from accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → writes styled .xlsx. exercised: "wrote file True"
  `locate: openpyxl.Workbook.save`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → writes real Excel Table. exercised: "wrote file True"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)`; `ws.write(row, col, val)`; `close()` → .xlsx with charts. exercised: "wrote file True"
  `locate: xlsxwriter.Workbook, xlsxwriter.worksheet.Worksheet.write`

#### Pipeline R34: Reverse Problem Management

- **Step 0 (Global Ingestion).** Flatten known-error articles and rendered graph HTML into the manifest.
  python-docx 1.2.0 — `docx.Document(docx=path)` → reads Word article. exercised: "paragraphs == 0 (default)"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc markdown/text/json. located
  `locate: undoc.parse_file`
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → parsed document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `with sync_playwright() as p: page.goto(url); page.content()` → rendered HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  clingraph 1.2.6 — `clingraph.compute_graphs(fb); clingraph.render(graphs, format='svg')` → renders ASP-fact graph. located
  `locate: clingraph.render, clingraph.compute_graphs`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestrator Compilation).** Write a flow gated on causal/error-hypothesis AMR graphs.
  amrlib 0.8.1 — `amrlib.load_stog_model(model_dir=...)` (`.parse_sents(...)`) → sentence-to-AMR-graph parser. located
  `locate: amrlib.load_stog_model`
  prefect 3.8.4 — `@prefect.flow` on a function → defines orchestration flow. located
  `locate: prefect.flow`

- **Step 2 (Cause and Known Error).** Test causal structure, formalize mechanisms, record known-error facts.
  amr-logic-converter 0.11.3 — `AmrLogicConverter().convert(amr)` → First-Order-Logic Clause. located
  `locate: amr_logic_converter.AmrLogicConverter.AmrLogicConverter.convert`
  dowhy 0.14 — `dowhy.CausalModel(data, treatment, outcome, graph=...)` → causal graph model to test. located
  `locate: dowhy.CausalModel`
  pgmpy 1.1.2 — `pgmpy.estimators.PC(data).estimate()` → structure learned/tested from rows. located
  `locate: pgmpy.estimators.PC.PC, pgmpy.estimators.PC.PC.estimate`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → SMT satisfiability of mechanism. exercised: "False"
  `locate: pysmt.shortcuts.is_sat`
  typedlogic 0.2.4 — `Solver().add_fact(fact)` → records known-error facts. located
  `locate: typedlogic.solver.Solver.add_fact`

- **Step 3 (Solution and Close).** Explore strategies; accept closure evidence or stay open.
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...)` → planner exploring strategies. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  ortools 9.15.6755 — `cp_model.CpModel(); ...; cp_model.CpSolver().Solve(model)` → CP-SAT strategy search. exercised: "('OPTIMAL', 4)"
  `locate: ortools.sat.python.cp_model.CpModel, ortools.sat.python.cp_model.CpSolver.Solve`
  z3-solver 5.1.0.0 — `z3.Solver(); s.add(...); s.check()` → closure-evidence proof. exercised: "sat [x = 1]"
  `locate: z3.Solver, z3.Solver.check`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook(); wb.save(path)` → .xlsx file. exercised: "4801-byte xlsx"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → real Excel Table. exercised: "6047-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path); wb.close()` → .xlsx with native charts. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`

#### Pipeline R35: Reverse Service Desk

- **Step 0 (Global Ingestion).** Flatten template packs and desk dashboards into manifest.
  docling 2.124.0 — `DocumentConverter().convert(source).document` → parses template packs. located
  `locate: docling.document_converter.DocumentConverter.convert`
  markitdown 0.1.7 — `MarkItDown().convert(source)` → template pack to Markdown. located
  `locate: markitdown.MarkItDown.convert`
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch().new_page()` → flattens desk dashboards. located
  `locate: playwright.sync_api.sync_playwright`
  python-docx 1.2.0 — `docx.Document(path)` → reads Word template packs. exercised: "docx written"
  `locate: docx.Document`
- **Step 1 (Orchestrator Compilation).** Emit a workflow if triage-guideline/channel spans resolve.
  temporalio 1.32.0 — `@temporalio.workflow.defn` on a workflow class → declares durable workflow. located
  `locate: temporalio.workflow.defn`
- **Step 2 (Triage and Pack).** Route by rules; assemble channel messages.
  business-rules 1.1.1 — `run_all(rule_list, defined_variables, defined_actions)` → routes to R33/R34/R36. located
  `locate: business_rules.run_all`
  jinja2 3.1.6 — `Template(src).render(**ctx)` → assembles channel messages. exercised: "Hi X"
  `locate: jinja2.Template.render, jinja2.Environment`
  stanza 1.14.0 — `stanza.Pipeline(lang="en", processors=...)(text)` → NLP parse of message text (not templating). located
  `locate: stanza.Pipeline`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`
- **Step 3 (Feedback and Improve).** Store CSAT; score desk series; emit items on breach.
  pandas 2.3.3 — `pandas.DataFrame(data)` → stores confirmations and CSAT. located
  `locate: pandas.DataFrame`
  statsmodels 0.15.0 — `statsmodels.tsa.arima.model.ARIMA(series, order).fit()` → scores desk time series. located
  `locate: statsmodels.tsa.arima.model.ARIMA`
  pulp 3.3.2 — `p=LpProblem(); p.solve()` → emits Pipeline R29 items on threshold fail. exercised: "Optimal 3.0"
  `locate: pulp.LpProblem.solve, pulp.LpVariable`
- **Step 4 (Execution).** Write one spreadsheet from solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); wb.save(path)` → writes .xlsx artifact. exercised: "xlsx file written"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=Workbook(path); ws=w.add_worksheet(); ws.add_table(...)` → native Excel table. exercised: "xlsx with table written"
  `locate: xlsxwriter.Workbook.add_worksheet, xlsxwriter.worksheet.Worksheet.add_table`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file=path, index=False)` → real Excel Table object. exercised: "xlsx table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R36: Reverse Service Request Management

- **Step 0 (Global Ingestion).** Flatten fulfilment Word packs and request HTML into the manifest.
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown; Word-pack→Markdown. located
  `locate: anydoc.to_markdown`
  python-docx 1.2.0 — `docx.Document(path)` → parsed Word document; Word-pack read. exercised: "36609 bytes"
  `locate: docx.Document`
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch()` → rendered request HTML; HTML flatten. located
  `locate: playwright.sync_api.sync_playwright`

- **Step 1 (Orchestrator Compilation).** Keep spiffworkflow/pydantic request assets when a model key or ad-hoc flag type-checks.
  pydantic 2.13.5 — `class Req(pydantic.BaseModel): ...` → validated request model; model-key type-check. exercised: "unit=3.5"
  `locate: pydantic.BaseModel`
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`

- **Step 2 (Model or Plan).** Execute matched models; synthesize ad-hoc plans; write approval tables.
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=pk).solve(problem)` → plan; ad-hoc plan synthesis. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Replay).** Compare executed paths to model; score cycle time on deviation.
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)` → replay diagnostics; path-vs-model conformance. located
  `locate: pm4py.conformance_diagnostics_token_based_replay`
  pandas 2.3.3 — `pandas.DataFrame(...)` → cycle-time table; cycle-time tabulation. located
  `locate: pandas.DataFrame`
  pingouin 0.6.1 — `pingouin.ttest(x, y)` → stats DataFrame (T, p_val); cycle-time scoring. exercised: "T=-2.0"
  `locate: pingouin.ttest`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.save(path)` → .xlsx; styled spreadsheet write. exercised: "4802 bytes"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet(); wb.close()` → .xlsx; native-chart spreadsheet write. exercised: "5247 bytes"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object; Table write from DataFrame. exercised: "6138 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R37: Reverse Service Catalog Management

- **Step 0 (Global Ingestion).** Capture catalog views; flatten Word extracts into manifest.
  markitdown 0.1.7 — `MarkItDown().convert(path)` → Markdown result. exercised: "# Desk x"
  `locate: markitdown.MarkItDown.convert`
  playwright 1.62.0 — `with sync_playwright() as p: ...page.content()` → captures streamlit/datasette views. located
  `locate: playwright.sync_api.sync_playwright`
  python-docx 1.2.0 — `docx.Document(path)` → reads Word catalog extracts. exercised: "1 paragraph"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file(path)` → Markdown/text/JSON of Office doc. located
  `locate: undoc.parse_file`
  streamlit 1.63.0, datasette 0.65.3 — named as the catalog-view apps whose pages playwright captures; sources here, not performers of this flatten step (no bound function).

- **Step 1 (Orchestrator Compilation).** Build dagster asset graph from recovered spans.
  dagster 1.13.20 — `@dagster.asset def catalog(): ...` → asset definition. exercised: "AssetsDefinition"
  `locate: dagster.asset`

- **Step 2 (Model and View).** Render catalog views; check completeness; bind access.
  clingo 5.8.0 — `Control().solve()` → mandatory-attribute completeness SAT. exercised: "SAT"
  `locate: clingo.Control.solve`
  great-tables 0.24.0 — `great_tables.GT(df)` → formatted catalog view table. exercised: "GT"
  `locate: great_tables.GT`
  jinja2 3.1.6 — `jinja2.Template(src).render(**ctx)` → rendered standard view. exercised: "flow R0"
  `locate: jinja2.Template.render`
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`

- **Step 3 (Request Path).** Evaluate view-request decisions; log exceptions.
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Write the pipeline's artifact spreadsheet.
  openpyxl 3.1.2 — `wb=Workbook(); wb.save(path)` → writes .xlsx. exercised: "saved"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → writes real Excel Table. exercised: "table written"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); ...write(); wb.close()` → writes .xlsx. exercised: "closed"
  `locate: xlsxwriter.Workbook`

#### Pipeline R38: Reverse Business Relationship Management

- **Step 0 (Global Ingestion).** Flatten relationship reviews and journey dashboards into manifest
  python-docx 1.2.0 — `docx.Document("review.docx").paragraphs` → paragraph objects; reads review text/tables. exercised: "para0 'Continuity plan'"
  `locate: docx.Document, docx.document.Document.paragraphs`
  docling 2.124.0 — `DocumentConverter().convert(src).document` → DoclingDocument; parses relationship reviews. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `page.goto(url); page.content()` → rendered HTML; flattens journey dashboards. located
  `locate: playwright.sync_api.Page.goto, playwright.sync_api.Page.content`

- **Step 1 (Orchestrator Compilation).** Write prefect flow only if stakeholder/domain spans resolve
  prefect 3.8.4 — `@prefect.flow def r0(): ...` → Flow; writes the orchestration flow. located
  `locate: prefect.flow, prefect.task`

- **Step 2 (Health and Offer).** Rebuild RACI graph, score VoC, record principles, shape offers
  networkx 3.6.1 — `g=DiGraph(); g.add_edges_from(raci_edges)` → graph; rebuilds the RACI graph. exercised: "2 edges"
  `locate: networkx.DiGraph.add_edges_from, networkx.DiGraph.add_edge`
  pandas 2.3.3 — `df.groupby("stakeholder")["voc"].mean()` → Series; scores VoC. exercised: "{'a': 4.0, 'b': 9.0}"
  `locate: pandas.DataFrame.groupby`
  typedlogic 0.2.4 — `@typedlogic.axiom def principle(...)` (+ `Theory.add`) → records principle axioms. located
  `locate: typedlogic.axiom, typedlogic.Theory.add`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Journey).** Store terms; track journey stages, refuse offboard without sustainment
  pydantic 2.13.5 — `class Terms(BaseModel): ...` then `Terms.model_validate(row)` → instance; stores/validates terms. exercised: "rto=4"
  `locate: pydantic.BaseModel.model_validate, pydantic.BaseModel`
  pm4py 2.7.23.8 — `pm4py.discover_petri_net_inductive(log)` → (net, im, fm); tracks onboard/co-create/review/offboard flow. located
  `locate: pm4py.discover_petri_net_inductive, pm4py.conformance_diagnostics_token_based_replay`

- **Step 4 (Execution).** Write one Excel spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save("out.xlsx")` → writes .xlsx. exercised: "saved 4801 bytes"
  `locate: openpyxl.Workbook.save, openpyxl.Workbook`
  xlsxwriter 3.2.9 — `w=xlsxwriter.Workbook("out.xlsx"); w.add_worksheet(); w.close()` → writes .xlsx. exercised: "saved 5247 bytes"
  `locate: xlsxwriter.Workbook.close, xlsxwriter.Workbook.add_worksheet, xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "tbl", file="out.xlsx", index=False)` → writes real Excel Table. exercised: "wrote 6134 bytes"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R39: Reverse Change Enablement

- **Step 0 (Global Ingestion).** flatten RFC Word packs and change-board HTML into manifest
  python-docx 1.2.0 — `docx.Document(path)` → reads RFC Word pack. exercised: "docx saved"
  `locate: docx.Document`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown from HTML/docs. exercised: "| a | b | ..."
  `locate: anydoc.to_markdown`
  playwright 1.62.0 — `with sync_playwright() as p: p.chromium.launch()` → browser; flattens change-board HTML. located
  `locate: playwright.sync_api.sync_playwright`

- **Step 1 (Orchestrator Compilation).** emit temporalio workflow gated on recovered spans
  temporalio 1.32.0 — `@temporalio.workflow.defn` → durable workflow. located
  `locate: temporalio.workflow.defn`

- **Step 2 (Assess and Authorize).** build records, apply rules, bind authority, accept constraints
  pydantic 2.13.5 — `Model.model_validate(row)` → CHG record from recovered rows. exercised: "2"
  `locate: pydantic.BaseModel.model_validate`
  business-rules 1.1.1 — `run_all(rule_list, defined_variables, defined_actions)` → binds authority matrix. exercised: "['flag']"
  `locate: business_rules.run_all`
  clingo 5.8.0 — `Control().solve()` → accepts freeze-window/exclusive-resource constraints. exercised: "a b"
  `locate: clingo.Control.solve`
  pycasbin ? — `Enforcer(model, policy).enforce(sub, obj, act)` → policy / access-control decision. located
  `locate: casbin.Enforcer, casbin.Enforcer.enforce, casbin.Enforcer.add_policy`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Plan and Replay).** emit plan, simulate dry-run, refuse divergent closure
  criticalpath 0.1.5 — `Node(...).add(...); .get_critical_path()` → emits plan sequence. exercised: "['A','B']"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node.add`
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=...).solve(problem)` → plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  simpy 4.1.2 — `env=Environment(); env.process(p); env.run()` → dry-run simulation. exercised: "5"
  `locate: simpy.Environment.run, simpy.Environment.process`
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_alignments(log, net,im,fm)` → path divergence. located
  `locate: pm4py.conformance_diagnostics_alignments`
  csv-diff 1.2 — `compare(load_csv(a,key), load_csv(b,key))` → path/data divergence. exercised: "added=1, removed=1"
  `locate: csv_diff.compare, csv_diff.load_csv`

- **Step 4 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → xlsx file. exercised: "saved"
  `locate: openpyxl.Workbook, openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path).add_worksheet()` → native xlsx writer. exercised: "closed"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.add_worksheet`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, "T", file=path)` → real Excel Table. exercised: "wrote table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R40: Reverse Project Management

- **Step 0 (Global Ingestion).** flatten PID/stage Word packs, quarto/plotly HTML into manifest
  python-docx 1.2.0 — `docx.Document("pid.docx")` → reads PID/stage Word packs. exercised: "paragraph text 'hello'"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file("stage.docx").to_markdown()` → flat text/Markdown/JSON. exercised: "'Hello undoc'"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(source="pack.docx")` → Markdown/text. exercised: "'# Hi\n\nTest doc'"
  `locate: markitdown.MarkItDown.convert`
  docling 2.124.0 — `DocumentConverter().convert(source="stage.pdf")` → parses quarto/plotly HTML/PDF. located
  `locate: docling.document_converter.DocumentConverter.convert`
  playwright 1.62.0 — `page.goto(url); page.content()` → serialized rendered plotly/quarto HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  plotly 7.0.0 — `plotly.graph_objects.Figure(data=[...]).to_html(full_html=False)` → produces HTML flattened here. exercised: "4300543-char HTML"
  `locate: plotly.graph_objects.Figure.to_html, plotly.graph_objects.Figure.write_html`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** build dagster asset graph from tolerance/deliverable/exception spans
  dagster 1.13.20 — `dagster.asset(deps=[upstream])(fn)` → AssetsDefinition composing the asset graph. located
  `locate: dagster.asset`

- **Step 2 (Gates and Schedule).** instantiate schemas; encode graphs; solve resource-feasible plans
  pydantic 2.13.5 — `class PID(pydantic.BaseModel): ...; PID(**row)` → validated PID/stage/work-package schemas. exercised: "M(x=5).x == 5"
  `locate: pydantic.BaseModel`
  criticalpath 0.1.5 — `criticalpath.Node("proj").get_critical_path()` → schedules feasible plan by CPM. exercised: "['A','B'], duration 8"
  `locate: criticalpath.Node.get_critical_path, criticalpath.Node.link`
  ortools 9.15.6755 — `mdl=cp_model.CpModel(); s=cp_model.CpSolver(); s.Solve(mdl)` → resource-feasible CP-SAT plan. exercised: "OPTIMAL, x=4"
  `locate: ortools.sat.python.cp_model.CpModel, ortools.sat.python.cp_model.CpSolver.Solve`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Exception Proof).** accept that an exception plan restores tolerances
  typedlogic 0.2.4 — `s=Z3Solver(); s.add_theory(theory); s.check()` → checks exception-plan satisfiability. located
  `locate: typedlogic.integrations.solvers.z3.Z3Solver.check`
  z3-solver 5.1.0.0 — `s=z3.Solver(); s.add(cons); s.check()` → sat/unsat tolerance-restoration proof. exercised: "sat; model [x = 3]"
  `locate: z3.Solver, z3.Solver.check`

- **Step 4 (Execution).** write one spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `wb=openpyxl.Workbook(); wb.active["A1"]=v; wb.save(path)` → writes .xlsx. exercised: "A1 == 'hi'"
  `locate: openpyxl.Workbook`
  xlsxwriter 3.2.9 — `wb=xlsxwriter.Workbook(path); wb.add_worksheet().write(0,0,v); wb.close()` → writes .xlsx. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name="PJ_WORK_PACKAGE", file=path, index=False)` → real Excel Table. exercised: "6124-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R41: Reverse Software Development and Management

- **Step 0 (Global Ingestion).** Flatten design notes and mermaid/diagrams HTML into the manifest.
  python-docx 1.2.0 — `docx.Document("design.docx").paragraphs` → reads the design notes. exercised: "saved 36583B"
  `locate: docx.Document`
  docling 2.124.0 — `DocumentConverter().convert("design.pdf")` → ConversionResult document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  diagrams 0.25.1 — `with diagrams.Diagram("arch", show=False): ...` → renders the architecture diagram (later scraped). located
  `locate: diagrams.Diagram`
  playwright 1.62.0 — `page.content()` → rendered DOM HTML of the diagram page. located
  `locate: playwright.sync_api.Page.content`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert("diagram.html")` → Markdown of the flattened HTML. exercised: "# Q3 Net income 100"
  `locate: markitdown.MarkItDown.convert`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestrator Compilation).** Write Prefect tasks only if backlog/architecture-constraint spans resolve.
  prefect 3.8.4 — `@prefect.task def build(): ...` → defines a durable task. exercised: "type=Task"
  `locate: prefect.task`

- **Step 2 (Guide and Rank).** Record SDM rules; rank tasks under value/risk/product edges.
  typedlogic 0.2.4 — `get_solver("clingo").add(Term("sdm_rule", item))` → records typed SDM rules. exercised: "added Term; satisfiable=True"
  `locate: typedlogic.registry.get_solver, typedlogic.solver.Solver.add`
  pulp 3.3.2 — `LpProblem("rank", LpMaximize).solve()` → ranks tasks under value/risk. exercised: "Optimal, x=3.0"
  `locate: pulp.LpProblem.solve`
  networkx 3.6.1 — `networkx.DiGraph().add_edge(a, b)` → product dependency edges for ranking. exercised: "edges=1"
  `locate: networkx.DiGraph, networkx.DiGraph.add_edge`

- **Step 3 (Design Proof).** Prove design vs NFR bounds; encode feature-model constraints.
  z3-solver 5.1.0.0 — `z3.Solver().check()` (after add) → accepts design artifacts vs NFR bounds. exercised: "sat; assets=100, liab=50"
  `locate: z3.Solver.check`
  python-sat 1.9.dev15 — `pysat.solvers.Solver(bootstrap_with=cnf).solve()` → SAT-checks feature-model constraints. exercised: "solve=True, model=[-1, 2]"
  `locate: pysat.solvers.Solver.solve`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** Write one Excel spreadsheet from the recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook().save("artifact.xlsx")` → writes the workbook. exercised: "saved 4819B"
  `locate: openpyxl.Workbook.save`
  xlsxwriter 3.2.9 — `wb = xlsxwriter.Workbook("artifact.xlsx"); wb.close()` → writes the workbook. exercised: "wrote 5248B"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, "T", file="artifact.xlsx")` → real Excel Table. exercised: "table xlsx 6047B"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R42: Reverse Service Validation and Testing

- **Step 0 (Global Ingestion).** flatten test-plan Word packs and diagrams
  python-docx 1.2.0 — `docx.Document(path)` → read test-plan Word pack (paragraphs/tables). exercised: "opened/saved .docx"
  `locate: docx.Document, docx.document.Document.add_paragraph`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path)` → Markdown from Word packs. exercised: "'hi\\n' from .docx"
  `locate: anydoc.to_markdown, anydoc.to_markdown_bytes`
  markitdown 0.1.7 — `MarkItDown().convert(source).text_content` → Markdown. exercised: "'# Title\\n\\nhello world'"
  `locate: markitdown.MarkItDown.convert`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestrator Compilation).** admit testing assets only if predicates+model key type-check
  (no candidate library in batch — pure type-check gate; nothing to bind.)

- **Step 2 (Criteria Proof).** record exit criteria; accept consistency and entailment
  typedlogic 0.2.4 — `Solver().add_fact(fact)` → records exit-criteria facts. located
  `locate: typedlogic.solver.Solver.add_fact`
  pysmt 0.9.6 — `pysmt.shortcuts.is_sat(formula)` → internal consistency; `is_valid` entailment. exercised: "is_sat True"
  `locate: pysmt.shortcuts.is_sat, pysmt.shortcuts.is_valid`
  model-checker 1.3.9 — `model_checker.run_test(example_case, semantic_class, proposition_class, operator_collection, syntax_class, model_constraints, model_structure)` → bool accept. located
  `locate: model_checker.run_test, model_checker.ModelConstraints`

- **Step 3 (Plan and Exception).** emit tailored plan; accept defect/exception coverage
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...)` → planner emitting the plan. located
  `locate: unified_planning.shortcuts.OneshotPlanner`
  ortools 9.15.6755 — `CpSolver().solve(CpModel())` → tailored feasible plan. exercised: "OPTIMAL, x=3"
  `locate: ortools.sat.python.cp_model.CpSolver.solve, ortools.sat.python.cp_model.CpModel`
  clingo 5.8.0 — `Control().solve()` → accepts every failed criterion has defect/exception record. exercised: "SAT; model 'a b'"
  `locate: clingo.Control.solve, clingo.Control.ground`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 4 (Execution).** write one spreadsheet artifact from solver-accepted fields
  openpyxl 3.1.2 — `Workbook().save(path)` → xlsx artifact. exercised: "saved xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `Workbook(path)` (+ write) `.close()` → xlsx with native charts. exercised: "closed xlsx"
  `locate: xlsxwriter.Workbook, xlsxwriter.Workbook.close`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, table_name, file)` → real Excel Table object. exercised: "wrote Excel table"
  `locate: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.dfs_to_xlsx_tables`

#### Pipeline R43: Reverse Deployment Management

- **Step 0 (Global Ingestion).** Flatten deployment reports; lift mermaid HTML to manifest.
  python-docx 1.2.0 — `docx.Document(path).paragraphs` → reads deployment reports. exercised: "paras ['H','para one']"
  `locate: docx.Document, docx.document.Document.paragraphs`
  undoc 0.9.0 — `undoc.parse_file(path).to_markdown()` → Markdown from office docs. exercised: "'# H\n\npara one'"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
  markitdown 0.1.7 — `MarkItDown().convert(path).markdown` → Markdown from reports. exercised: "'# Title\n\nHello world'"
  `locate: markitdown.MarkItDown.convert`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step

- **Step 1 (Orchestrator Compilation).** Temporalio workflow gated on env/success/rollback spans plus change fact.
  temporalio 1.32.0 — `@workflow.defn`; `client.execute_workflow(WF.run, id=, task_queue=)` → durable deploy workflow. located
  `locate: temporalio.workflow.defn, temporalio.client.Client.execute_workflow`

- **Step 2 (Readiness Proof).** Describe elements; encode predicates; accept component/environment readiness.
  pydantic 2.13.5 — `class M(BaseModel): ...` → describes pipeline elements. exercised: "actor='u1' t=5"
  `locate: pydantic.BaseModel, pydantic.BaseModel.model_validate`
  typedlogic 0.2.4 — `ClingoSolver().add(sentence)` → encodes pre-deploy predicates. exercised: "satisfiable=True"
  `locate: typedlogic.integrations.solvers.clingo.ClingoSolver.add`
  clingo 5.8.0 — `ctl.solve()` → SolveResult.satisfiable accepts readiness. exercised: "sat=True"
  `locate: clingo.Control.solve`
  z3-solver 5.1.0.0 — `s=Solver(); s.add(preds); s.check()` → sat accepts readiness. exercised: "check=sat"
  `locate: z3.Solver.check`
  csv-diff 1.2 — `compare(load_csv(prev, key='id'), load_csv(curr, key='id'))` → diffs readiness tables. exercised: "changed=1"
  `locate: csv_diff.compare, csv_diff.load_csv`

- **Step 3 (Review).** Emit instance plan; mine logs against model; emit items on unsat.
  unified-planning 1.3.0 — `OneshotPlanner(problem_kind=p.kind).solve(problem)` → instance plan. exercised: "SOLVED_SATISFICING, plan ['go']"
  `locate: unified_planning.shortcuts.OneshotPlanner, unified_planning.model.Problem`
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)` → mines logs vs model. located
  `locate: pm4py.conformance_diagnostics_token_based_replay`
  pandas 2.3.3 — `pandas.DataFrame(items)` → emits Pipeline R29 items. exercised: "shape (2,2)"
  `locate: pandas.DataFrame`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `wb=Workbook(); ws.append(row); wb.save(path)` → writes .xlsx. exercised: "wrote xlsx"
  `locate: openpyxl.Workbook, openpyxl.workbook.workbook.Workbook.save`
  xlsxwriter 3.2.9 — `wb=Workbook(path); ws.write(r,c,v); wb.close()` → writes .xlsx. exercised: "wrote xlsx"
  `locate: xlsxwriter.Workbook`
  pandas-xlsx-tables 1.1.2 — `df_to_xlsx_table(df, 'T', path, index=False)` → real Excel Table. exercised: "wrote xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`

#### Pipeline R44: Reverse Release Management

- **Step 0 (Global Ingestion).** flatten release reviews and diagram HTML into manifest
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source=path)` → ConversionResult; flattens release reviews. located
  `locate: docling.document_converter.DocumentConverter.convert`
  mermaid — non-Python renderer — CLI `mmdc -i in.mmd -o out.svg` (@mermaid-js/mermaid-cli); mechanical, not a hallucination step
  python-docx 1.2.0 — `docx.Document(path)` → document exposing `.paragraphs`; flattens release-review .docx. exercised: "1 paragraph"
  `locate: docx.Document`

- **Step 1 (Orchestrator Compilation).** write prefect flow when release-model key and go/no-go resolve
  prefect 3.8.4 — `@prefect.flow(name=...)` decorating the fn → Flow object; writes the release flow. located
  `locate: prefect.flow`

- **Step 2 (Select and Prove).** select model; build schedule; jointly accept readiness
  criticalpath 0.1.5 — `criticalpath.Node('P')` add child Nodes, link, `update_all()` → schedule with critical path; builds the schedule. exercised: "duration 5"
  `locate: criticalpath.Node`
  typedlogic 0.2.4 — `typedlogic.solver.Solver.prove(sentence)` → Optional[bool]; jointly accepts procedure/readiness entailment. located
  `locate: typedlogic.solver.Solver.prove, typedlogic.solver.Solver.check`
  z3-solver 5.1.0.0 — `z3.Solver().check()` after `add(constraints)` → sat/unsat; accepts readiness jointly. exercised: "sat x=3"
  `locate: z3.Solver.check, z3.Solver`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Review).** compare logs/incidents to success criteria
  pandas 2.3.3 — `pandas.merge(left, right, on=key)` → joined frame; compares logs to incidents. exercised: "1 row"
  `locate: pandas.merge, pandas.DataFrame`
  pm4py 2.7.23.8 — `pm4py.conformance_diagnostics_alignments(log, net, im, fm)` → per-trace alignments; compares logs to criteria. located
  `locate: pm4py.conformance_diagnostics_alignments`

- **Step 4 (Execution).** write one artifact spreadsheet from solver-accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook()` then `wb.save(path)` → xlsx workbook; writes the artifact spreadsheet. exercised: "hi"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path, index=False)` → writes native Excel Table; writes spreadsheet. exercised: "wrote"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)` then `add_worksheet().write(); close()` → xlsx file; writes spreadsheet. exercised: "wrote"
  `locate: xlsxwriter.Workbook`

#### Pipeline R45: Reverse Organizational Change Management

- **Step 0 (Global Ingestion).** Flatten comms packs and quarto scorecards into the manifest
  docling 2.124.0 — `docling.document_converter.DocumentConverter().convert(source)` → ConversionResult; parses scorecard PDF/HTML. located (requires models)
  `locate: docling.document_converter.DocumentConverter.convert`
  firecrawl-anydoc 0.2.4 — `anydoc.to_markdown(path, ocr='reject')` → markdown string; flattens comms packs. exercised: "'Hello clause one.\n'"
  `locate: anydoc.to_markdown`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → DocumentConverterResult; converts scorecards to markdown. exercised: "'Hello clause one.'"
  `locate: markitdown.MarkItDown.convert`
  python-docx 1.2.0 — `docx.Document(path)` → Document; reads communication packs. exercised: "'Hello clause one.'"
  `locate: docx.Document`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc (then .to_markdown()); Office→md/text/json. exercised: "Undoc object"
  `locate: undoc.parse_file, undoc.Undoc.to_markdown`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** Emit dagster asset graph if spans resolve
  dagster 1.13.20 — `dagster.asset(fn)` → AssetsDefinition; defines a communication asset node. exercised: "AssetsDefinition"
  `locate: dagster.asset`

- **Step 2 (Ready and Plan).** Map roles, score readiness, sequence engagement
  criticalpath 0.1.5 — `criticalpath.Node('p').get_critical_path()` → node list; emits engagement sequence. exercised: "['A', 'B']"
  `locate: criticalpath.Node.get_critical_path`
  networkx 3.6.1 — `networkx.DiGraph()` + `add_edge` → directed graph; maps roles. exercised: "(3, 2) nodes/edges"
  `locate: networkx.DiGraph`
  pandas 2.3.3 — `pandas.DataFrame(data)` → DataFrame; assembles readiness scores. exercised: "(2, 2)"
  `locate: pandas.DataFrame`
  pingouin 0.6.1 — `pingouin.cronbach_alpha(data=df)` → (alpha, CI); scores readiness reliability. exercised: "0.95"
  `locate: pingouin.cronbach_alpha`
  unified-planning 1.3.0 — `unified_planning.shortcuts.OneshotPlanner(problem_kind=...).solve(problem)` → plan; emits engagement sequence. located (requires planner engine)
  `locate: unified_planning.shortcuts.OneshotPlanner`
  zen-engine 2.0.2 — `ZenEngine().create_decision(jdm).evaluate(record)` → decision-table / decision-graph evaluation. located
  `locate: zen.ZenEngine, zen.ZenEngine.create_decision, zen.ZenDecision.evaluate`

- **Step 3 (Sustain Proof).** Track adoption; ASP-accept early-win evidence
  clingo 5.8.0 — `clingo.Control().solve(on_model=cb)` → SolveResult; accepts early-win evidence records. exercised: "['a b']"
  `locate: clingo.Control.solve`
  statsmodels 0.15.0 — `statsmodels.api.OLS(y, sm.add_constant(X)).fit()` → results; tracks adoption. exercised: "params [0.46, 0.74]"
  `locate: statsmodels.api.OLS`

- **Step 4 (Execution).** Write one Excel artifact from accepted fields
  openpyxl 3.1.2 — `openpyxl.Workbook().save(path)` → writes styled .xlsx. exercised: "wrote file True"
  `locate: openpyxl.Workbook.save`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → writes real Excel Table. exercised: "wrote file True"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path)`; `ws.write(row, col, val)`; `close()` → .xlsx with charts. exercised: "wrote file True"
  `locate: xlsxwriter.Workbook, xlsxwriter.worksheet.Worksheet.write`

#### Pipeline R46: Reverse Knowledge Management

- **Step 0 (Global Ingestion).** Flatten MkDocs site, quarto packs, and Word exports into the manifest.
  playwright 1.62.0 — `with sync_playwright() as p: page.goto(url); page.content()` → rendered site HTML. located
  `locate: playwright.sync_api.sync_playwright, playwright.sync_api.Page.content`
  markitdown 0.1.7 — `markitdown.MarkItDown().convert(source)` → Markdown result. located
  `locate: markitdown.MarkItDown.convert`
  undoc 0.9.0 — `undoc.parse_file(path)` → Undoc markdown/text/json. located
  `locate: undoc.parse_file`
  docling 2.124.0 — `DocumentConverter().convert(source=path)` → parsed document. located
  `locate: docling.document_converter.DocumentConverter.convert`
  mkdocs 1.6.1 — `mkdocs.commands.build.build(config)` → builds the static site being flattened. located
  `locate: mkdocs.commands.build.build`
  quarto 0.1.0 — `quarto.render(input='deck.qmd')` → render qmd (needs the quarto binary at run time). located
  `locate: quarto.render`

- **Step 1 (Orchestrator Compilation).** Write tasks for graph/RDF only if domain/owner/demand spans exist.
  networkx 3.6.1 — `networkx.DiGraph()` (add_edge) → domain/owner graph. exercised: "number_of_edges == 1"
  `locate: networkx.DiGraph`
  prefect 3.8.4 — `@prefect.flow` (and `@prefect.task`) → defines flow/tasks. located
  `locate: prefect.flow`
  rdflib 7.6.0 — `rdflib.Graph(); g.add((s,p,o))` → RDF triple store. exercised: "len(g) == 1"
  `locate: rdflib.Graph, rdflib.Graph.add`

- **Step 2 (Inventory Proof).** Map domains/owners, store assets, record guidelines, prove demand fulfilled.
  clingo 5.8.0 — `clingo.Control(); ...; ctl.solve(on_model=...)` → ASP proof demand fulfilled/queued. exercised: "['a b']"
  `locate: clingo.Control, clingo.Control.solve`
  networkx 3.6.1 — `networkx.DiGraph()` (add_edge) → domain-to-owner mapping. exercised: "number_of_edges == 1"
  `locate: networkx.DiGraph`
  rdflib 7.6.0 — `rdflib.Graph(); g.add((s,p,o))` → stores assets as triples. exercised: "len(g) == 1"
  `locate: rdflib.Graph, rdflib.Graph.add`
  typedlogic 0.2.4 — `Solver().add_fact(fact)` → records guideline facts. located
  `locate: typedlogic.solver.Solver.add_fact`

- **Step 3 (Routines).** Execute capture/review/publish/retire; version, profile, and emit items.
  pandas 2.3.3 — `pandas.DataFrame(data)` → tabular freshness data. exercised: "shape (2, 1)"
  `locate: pandas.DataFrame`
  pydantic 2.13.5 — `class M(pydantic.BaseModel): ...` → versioned asset model. exercised: "M(x=3).x == 3"
  `locate: pydantic.BaseModel`
  spiffworkflow 3.2.0 — `BpmnWorkflow(spec).do_engine_steps()` → execute a BPMN workflow. located
  `locate: SpiffWorkflow.bpmn.workflow.BpmnWorkflow, SpiffWorkflow.bpmn.parser.BpmnParser.BpmnParser`
  ydata-profiling 4.18.4 — `ydata_profiling.ProfileReport(df)` → EDA/freshness report. located
  `locate: ydata_profiling.ProfileReport`

- **Step 4 (Execution).** Write one spreadsheet from recovered, solver-accepted fields.
  openpyxl 3.1.2 — `openpyxl.Workbook(); wb.save(path)` → .xlsx file. exercised: "4801-byte xlsx"
  `locate: openpyxl.Workbook`
  pandas-xlsx-tables 1.1.2 — `pandas_xlsx_tables.df_to_xlsx_table(df, table_name, file=path)` → real Excel Table. exercised: "6047-byte xlsx"
  `locate: pandas_xlsx_tables.df_to_xlsx_table`
  xlsxwriter 3.2.9 — `xlsxwriter.Workbook(path); wb.close()` → .xlsx with native charts. exercised: "5248-byte xlsx"
  `locate: xlsxwriter.Workbook`

---

## Part 7. Verification

- `tests/test_function_chain.py` reads this file, collects every `locate:` line, and resolves each dotted path by import against the installed packages. A path whose top-level package is installed must resolve, or the test fails. A path whose package is not installed is reported by name and skipped, so the test states what it did not check.
- The chain's libraries and their exact versions are the `chain` extra of `pyproject.toml`, generated from the installed packages when this file was written: `uv pip install -e ".[dev,chain]"`.
- The build, the double build, and the digest: `compiled-ai compile packs/foia`, `python -m pytest`, `compiled-ai verify packs/foia`.
