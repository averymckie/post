# The Function Chain

Date: 2026-09-03.

This file is the chain, written as a proof: each line is one library function applied to the output of the line before it, from the raw source file to each terminal solution. A line names the library at its pinned version, the exact call with its options, what goes in, what comes out, and the certificate the library returns. The options are data, not choices. No executor appears in the chain. The rules the solvers run are printed in this file as data.

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
- sweetviz 2.3.3 — `sweetviz.analyze(df)` → `DataframeReport`; `.show_html(path)`. `exercised` (`analyze`).
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

Each step is quoted from the pipeline documents (pipelines.txt and reverse_pipelines.txt, 2026). Under each step, `located` names the libraries of that sentence that are in the catalog of Part 6, with the functions that resolved; `not located here` names the libraries of that sentence, from the library catalog as_code.txt, that were not installed or did not resolve in the environment that wrote this file. A library named in a sentence and in neither list is not annotated. The binding of a step's operation to one function among a library's located functions is made when that pipeline is run on an instance, with the same rules as Part 2; it is not asserted here.

### Forward pipelines

Pipeline 0 is Part 1 of this file.

#### Pipeline 0: Zero-Touch Orchestrator Compiler

- **Step 0 (Global Ingestion).** docling, undoc, markitdown, firecrawl-anydoc, python-calamine, fastexcel, and csvkit crawl the raw artifact folder and emit a mixed Markdown, JSON, CSV, and workbook inventory with no predeclared schema.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); fastexcel 0.21.0 (fastexcel.read_excel, ExcelReader.load_sheet, ExcelSheet.to_pandas); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Artifact Census).** ydata-profiling, sweetviz, and dataprep profile every tabular object; dasel walks JSON, YAML, and XML; pymupdf and pypdf fingerprint remaining PDFs into a single machine-readable manifest.
  located: ydata-profiling 4.18.4 (ydata_profiling.ProfileReport, ProfileReport.to_json); sweetviz 2.3.3 (sweetviz.analyze, DataframeReport.show_html); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
  not located here: dataprep
- **Step 2 (Schema Compilation).** dasel projections are typed by pydantic at runtime, producing the only schemas the rest of the run is allowed to use.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Capability Logic).** typedlogic writes clingo facts from the manifest (file class, detected entities, units, time columns, geofields, clause markers). clingo returns the unique stable model of required libraries, banned libraries, and legal handoff edges.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Graph Compilation).** networkx and graphable turn that stable model into a directed task graph. jinja2 renders the graph into prefect flow source, dagster asset definitions, or a temporalio workflow module, including retries, result persistence, and compensation on solver unsat.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render)
  not located here: graphable
- **Step 5 (Self-Load).** the chosen orchestrator imports the file it just wrote, registers the assets, and starts the run. No flow, schedule, partition, or retry policy exists before this step.

#### Pipeline 1: Quality Engineering

- **Step 0 (Global Ingestion).** docling parses a raw unstructured global dump of manufacturing logs and PDFs directly into flat text and Markdown.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestration and Narrowing).** dagster orchestrates the workflow, piping the raw text into spacy to perform natural language processing and extract syntactic dependencies isolating failure events.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize); spacy 3.8.16 (spacy.blank, Language.add_pipe, pipeline.Sentencizer, Doc.ents)
- **Step 2 (Logic Generation).** amr-logic-converter translates the extracted natural language dependency graphs directly into First-Order Logic formulas.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter)
- **Step 3 (Mathematical Verification).** pysmt consumes these generated formulas as an SMT solver to mathematically verify the physical bounds and logic paths.
  located: PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 4 (Time-to-Event Modeling).** lifelines applies survival analysis to the verified failure events to calculate time-to-event parametric shapes.
  located: lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit)
- **Step 5 (Execution).** fmdtools executes the Failure Modes and Effects Analysis (FMEA) simulation using the mathematically verified logic and survival models.
  not located here: fmdtools

#### Pipeline 2: Financial Dashboarding

- **Step 0 (Global Ingestion).** firecrawl-anydoc acts as the document parser, flattening a raw global dump of unstructured financial reports into Markdown.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document)
- **Step 1 (Orchestration and Narrowing).** temporalio manages the pipeline state, passing the text directly to stanza to generate syntactic dependency trees that map the financial entities and their relationships.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Schema Auto-Generation).** dasel queries the structured outputs of the NLP step to programmatically extract nodes, which are then passed to datamodel-code-generator to dynamically instantiate Pydantic models from the derived JSON schemas.
  located: datamodel-code-generator 0.76.1 (datamodel_code_generator.generate, datamodel_code_generator.InputFileType); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Logic Enforcement).** zen-engine evaluates the extracted financial entities against decision graphs generated from the parsed text to enforce business logic.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
- **Step 4 (Constraint Verification).** clingo executes as an Answer Set Programming system to mathematically prove the ledger consistency of the extracted values.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 5 (Visual Selection).** autoviz acts as an automated visualization selector to programmatically generate charts strictly from the verified tabular inputs.
  not located here: autoviz
- **Step 6 (Execution).** streamlit deploys the dynamically generated charts as a rapid data dashboard framework.
  located: streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)

#### Pipeline 3: Architecture Documentation

- **Step 0 (Global Ingestion).** undoc parses a raw global dump of disparate system specification documents, emitting flat text and JSON.
  located: undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestration and Narrowing).** prefect orchestrates the data flow, piping the unstructured text into nltk to extract entity relationships and parse the natural language into logical structures.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); nltk 3.10.3 (tokenize.sent_tokenize, tokenize.PunktSentenceTokenizer, logic.LogicParser, inference.Prover9)
- **Step 2 (Network Graphing).** networkx generates a comprehensive network analysis of the extracted entities to map system dependencies programmatically.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
- **Step 3 (Logic Translation).** typedlogic serves as a translation bridge to convert the network dependencies directly into clingo facts.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Architecture Modeling).** structurizr-python maps the generated logical facts into its C4 model DSL, constructing the architecture purely from the parsed text relationships.
- **Step 5 (Verification).** z3-solver runs as a high-performance SMT solver to mathematically verify the generated architecture has no cyclical dependencies.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 6 (Execution).** mermaid acts as a diagram and flowchart generator, rendering the verified C4 DSL into final visual output.
  not located here: mermaid

#### Pipeline 5: Process Mining Control Room

- **Step 0 (Global Ingestion).** markitdown and docling flatten ERP exports, work-order PDFs, and message logs into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 runs against the manifest. clingo only admits a process-mining asset graph if actor, activity, and time fields all resolve; otherwise the run stops.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 2 (Event Log Materialization).** the generated dagster assets type tuples through pydantic and land them in duckdb.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute)
- **Step 3 (Discovery and Replay).** pm4py discovers the net; snakes and simpn replay it; typedlogic facts that fail clingo drop the trace rather than pass it downstream.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); snakes 0.9.33 (nets.PetriNet, PetriNet.add_place); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent); simpn 1.10.0 (simulator.SimProblem, SimProblem.simulate)
- **Step 4 (Execution).** the same generated assets call most-queue for bottlenecks and publish dash-cytoscape plus streamlit only if replay succeeded.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)
  not located here: dash-cytoscape

#### Pipeline 6: Causal Policy Evaluation

- **Step 0 (Global Ingestion).** docling parses evaluations, instruments, and administrative PDFs into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a prefect flow whose task set exists only if stanza recovers treatment and outcome spans. Missing identification language yields an empty flow and a halt.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Graph and Proof).** the generated flow builds the DAG in pgmpy, dowhy, and networkx, then asks z3-solver and pysmt to prove a legal adjustment set.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); dowhy 0.14 (dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Estimation and Binding).** causalpy, statsmodels, pymc, and arviz run only on proved strategies. zen-engine receives effect estimates as decision tables written by the flow, not by an operator.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
  not located here: arviz, causalpy, pymc
- **Step 4 (Execution).** panel, forestplot, altair, and great-tables render from the bound tables.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html)
  not located here: altair, forestplot, panel

#### Pipeline 7: Supply Chain Scheduling

- **Step 0 (Global Ingestion).** firecrawl-anydoc and python-calamine ingest contracts, bills of lading, and capacity workbooks into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a temporalio workflow whose activities are the clingo-selected subset of pulp, pyomo, ortools, highspy, pyjobshop, and alns.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
  not located here: alns, highspy, pyjobshop, pyomo
- **Step 2 (Model Emission).** pydantic schemas from Step 1 become the MIP/CP model inside the workflow. There is no checked-in LP file.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 3 (Solve and Repair).** ortools or highspy solves; alns runs only if the workflow’s compensation path sees a bound and no feasible incumbent.
  located: ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
  not located here: alns, highspy
- **Step 4 (Calendar Proof).** criticalpath and clingo must accept the incumbent or the workflow does not call a renderer.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 5 (Execution).** highcharts-gantt, elegantt, and taipy are invoked as terminal activities of the generated workflow.
  not located here: elegantt, highcharts-gantt, taipy

#### Pipeline 8: Geospatial Hazard Cartography

- **Step 0 (Global Ingestion).** undoc and docling parse incident reports, sidecars, and municipal PDFs into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 keeps geopandas, shapely, osmnx, and rustworkx assets only when dasel finds coordinates or resolvable toponyms. No geo fields means no map flow.
  located: dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
  not located here: geopandas, osmnx, rustworkx, shapely
- **Step 2 (Constraint Compile).** python-constraint2 and cpmpy receive exclusion and coverage predicates extracted into pydantic models by the generated assets.
  located: python-constraint2 2.7.3 (constraint.Problem, Problem.getSolutions); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
  not located here: cpmpy
- **Step 3 (Surface and Sheet).** datashader, eomaps, contextily, prettymaps, pygmt, and lonboard run in the order the compiled graph specified.
  not located here: contextily, datashader, eomaps, lonboard, prettymaps, pygmt
- **Step 4 (Execution).** folium, keplergl, and weasyprint fire as leaf assets.
  not located here: folium, keplergl, weasyprint

#### Pipeline 9: Contract Constraint Prover

- **Step 0 (Global Ingestion).** docling, pypdf, and dasel pull clauses and defined-term tables from the contract dump into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a temporalio workflow gated on amrlib producing obligation, right, or condition-precedent graphs. No deontic AMR, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); amrlib 0.8.1 (amrlib.load_stog_model, Inference.parse_sents)
- **Step 2 (Logic Emission).** amr-logic-converter and typedlogic write the FOL and ASP programs that the workflow will hand to clingo, pysmt, and cvc5.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat); cvc5 1.3.4 (cvc5.Solver, Solver.checkSat, Solver.getUnsatCore)
- **Step 3 (Policy Materialization).** pycasbin, openfga, and zen-engine are generated as downstream activities only for proved permissions.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce)
  not located here: openfga
- **Step 4 (Execution).** xclingo, clingraph, great-tables, nicegui, and python-docx run as the workflow’s terminal compensation-safe activities.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: clingraph, nicegui, xclingo

#### Pipeline 10: Specification-to-Slide Compiler

- **Step 0 (Global Ingestion).** mammoth, undoc, and markitdown turn specs, tickets, and whiteboard exports into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 builds a dagster asset graph from requirement, risk, and milestone spans. Empty claim set cancels publication assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Trace Proof).** networkx and graphedexcel supply edges; business-rules, durable-rules, and z3-solver must accept completeness and acyclicity before any slide asset is materialized.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); durable-rules 2.0.28 (lang.ruleset, lang.when_all, lang.post, lang.m); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
  not located here: graphedexcel
- **Step 3 (Grammar Selection).** lida, autoviz, mermaid, and kroki are included only for tables and relations present in the proved graph.
  not located here: autoviz, kroki, lida, mermaid
- **Step 4 (Execution).** python-pptx, md2pptx, quarto, reveal-md, marp, and weasyprint are leaf assets of that graph.
  located: python-pptx 1.0.2 (pptx.Presentation, Presentation.slides, Slide.shapes, Slide.notes_slide)
  not located here: marp, md2pptx, quarto, reveal-md, weasyprint

#### Pipeline 11: Fleet Reliability Dossier

- **Step 0 (Global Ingestion).** firecrawl-anydoc and csvkit flatten claims, manuals, and sensor files into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 admits reliability and lifelines assets only when a time-to-event column and a censoring flag both type-check in pydantic.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (Fit and Cut Sets).** scipy rejects unphysical fits; fmdtools and z3-solver run only if series/parallel language compiled into block-diagram facts.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); scipy 1.15.3 (optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog)
  not located here: fmdtools
- **Step 3 (Execution).** mqrpy, qda-toolkit, spc-plotly, plotly, kaleido, and streamlit are generated as report assets when the cut-set proof succeeds.
  located: streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: kaleido, mqrpy, qda-toolkit, spc-plotly

#### Pipeline 12: Ontology Reasoner

- **Step 0 (Global Ingestion).** undoc and markitdown dump manuals, dictionaries, and glossaries into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes prefect tasks for rdflib and owlready2 only if class/property/disjointness phrases exist in the census.
  located: owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 2 (Closure and Proof).** owlrl and pyreason close the graph; z3-solver, cvc5, and clingo must accept the TBox/ABox pair.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); owlrl 7.6.2 (owlrl.DeductiveClosure); cvc5 1.3.4 (cvc5.Solver, Solver.checkSat, Solver.getUnsatCore)
  not located here: pyreason
- **Step 3 (Execution).** duckdb, datasette, graphistry, ipysigma, and mkdocs are leaf tasks of the generated flow.
  located: duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute)
  not located here: datasette, graphistry, ipysigma, mkdocs

#### Pipeline 13: Service Configuration Management

- **Step 0 (Global Ingestion).** docling, undoc, and markitdown flatten architecture packs, portfolio registers, SCM policies, discovery exports, and prior CMDB reports into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 runs against the manifest. clingo only admits a configuration asset graph if CI-type spans, relationship language, and a lifecycle verb set all resolve; otherwise the run stops.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 2 (Model Emission).** dasel projections are typed by pydantic into CI, relationship, state, and exception records and landed in duckdb. networkx materializes the CI graph from those records.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Lifecycle Proof).** typedlogic writes transition, exception, and verification facts; clingo and z3-solver must accept state consistency and acyclicity or no corrective asset is materialized.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Verification Replay).** pm4py mines transition logs against the proved lifecycle; csv-diff and daff emit discrepancy tables only for traces that failed the stable model.
  located: pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: csv-diff, daff
- **Step 5 (Execution).** great-tables, reportlab, python-docx, and mermaid fire as leaf assets for the verification report, RFC payloads, and lifecycle diagrams.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: mermaid, reportlab

#### Pipeline 14: Service Design

- **Step 0 (Global Ingestion).** firecrawl-anydoc and undoc flatten strategy decks, blueprints, SLR packs, persona documents, and compliance manuals into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a prefect flow only if stanza recovers principle, decomposition, and operational-constraint spans. Missing principle language yields an empty flow and a halt.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Requirement Proof).** amr-logic-converter and pysmt must accept usability, cost, performance, security, and compliance bounds before any model asset exists.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Structure and Interaction).** networkx and pydsm build the service breakdown; pm4py and snakes encode interaction flows; zen-engine writes SLA/OLA tables from proved commitments.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); snakes 0.9.33 (nets.PetriNet, PetriNet.add_place); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: pydsm
- **Step 4 (Execution).** diagrams, mermaid, structurizr-python, and python-docx are leaf assets for the Service Design Package. business-rules and pycasbin bind governance checkpoints only after the SMT proof.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce)
  not located here: mermaid

#### Pipeline 15: Business Analysis

- **Step 0 (Global Ingestion).** markitdown, office-oxide, and mammoth turn charters, org charts, interview notes, workshop exports, and glossaries into the compiler manifest.
  located: office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 builds a dagster asset graph from stakeholder, requirement, and conflict spans. Empty requirement set cancels specification assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Elicitation and Model).** nltk and spacy recover raw claims; typedlogic and rdflib categorize functional, non-functional, and transition requirements; networkx holds the stakeholder influence graph.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query); spacy 3.8.16 (spacy.blank, Language.add_pipe, pipeline.Sentencizer, Doc.ents); nltk 3.10.3 (tokenize.sent_tokenize, tokenize.PunktSentenceTokenizer, logic.LogicParser, inference.Prover9)
- **Step 3 (Verify and Trace).** vampire and model-checker must accept clarity, consistency, and testability; duckdb and csv-diff keep the traceability matrix and refuse baseline drift that fails z3-solver.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute)
  not located here: csv-diff, model-checker, vampire
- **Step 4 (Execution).** zen-engine binds change-request tables; python-docx, mermaid, and great-tables fire as leaf assets for the specification, matrix, and communications.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
  not located here: mermaid

#### Pipeline 16: Architecture Management

- **Step 0 (Global Ingestion).** undoc and docling dump strategy, current-state packs, metamodel references, and framework texts into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes prefect tasks for owlready2, rdflib, and networkx only if principle and viewpoint phrases exist in the census. No principle set, no architecture flow.
  located: owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 2 (Target Graph and Roadmap).** rustworkx and pydsm assemble current-versus-target graphs; criticalpath and se-lib sequence work packages only after typedlogic facts compile.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom)
  not located here: pydsm, rustworkx, se-lib
- **Step 3 (Conformance Proof).** z3-solver must accept acyclicity; clingo must accept building-block compliance with the compiled metamodel or view assets are not materialized.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** pyArchimate, graphable, structurizr-python, mermaid, diagrams, and quarto are leaf assets for views, ARB charter, exception process, and roadmap.
  not located here: graphable, mermaid, quarto

#### Pipeline 17: Infrastructure and Platform Management

- **Step 0 (Global Ingestion).** docling and firecrawl-anydoc flatten EA standards, SDP extracts, runbooks, capacity workbooks, and decommission requests into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 keeps pydantic pattern assets and unified-planning provision assets only when standard, SLA, and recovery-objective spans type-check. Missing recovery language drops the build graph.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (Design and Constraint).** casadi and python-control emit dynamics models; cpmpy and z3-solver must accept bill-of-materials, network, and hardening predicates.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
  not located here: casadi, cpmpy, python-control
- **Step 3 (Operate and Retire).** simpy and simprocesd replay backup, patch, and health tasks; clingo must accept dependency-safe retirement against the Pipeline 13 CI graph or decommission assets halt.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); simpy 4.1.2 (simpy.Environment, Environment.run)
  not located here: simprocesd
- **Step 4 (Execution).** scipy and ortools bind tuning recommendations; streamlit, python-docx, and mermaid fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); scipy 1.15.3 (optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog)
  not located here: mermaid

#### Pipeline 18: IT Asset Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc, python-calamine, fastexcel, and csvkit flatten policies, purchase orders, license contracts, warranty sheets, and discovery inventories into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); fastexcel 0.21.0 (fastexcel.read_excel, ExcelReader.load_sheet, ExcelSheet.to_pandas); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 admits register assets only when asset-type, entitlement, and identifier columns type-check in pydantic. No entitlement table, no license flow.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (Register and Proof).** dasel projections land in duckdb; clorm writes asset facts; clingo must prove entitlement-versus-consumption under per-user, per-device, and concurrent models.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute); clorm 1.6.3 (clorm.Predicate, clorm.FactBase, clingo.Control); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Audit Repair).** daff and csv-diff emit discrepancy tables; numpy-financial scores write-off and compliance exposure only on the unsat remainder.
  not located here: csv-diff, daff, numpy-financial
- **Step 4 (Execution).** openpyxl, great-tables, qrcode, and python-barcode are leaf assets for the reconciled register, compliance report, and tags.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)
  not located here: python-barcode, qrcode

#### Pipeline 19: Workforce and Talent Management

- **Step 0 (Global Ingestion).** undoc and markitdown dump strategy, demand forecasts, workforce assessments, competency frameworks, and L&D catalogs into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a prefect flow only if role, competency, and FTE spans resolve. Missing competency language yields an empty flow and a halt.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Plan and Ontology).** pandas and polars build the gap matrix; networkx maps succession; owlready2 and typedlogic must accept a complete profile for every planned role.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
  not located here: polars
- **Step 3 (Allocation Proof).** ortools and pulp solve hiring and L&D allocation; zen-engine binds role KPIs only if the solver returns a feasible incumbent.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 4 (Execution).** statsmodels scores turnover and time-to-fill; python-docx and streamlit fire as leaf assets.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)

#### Pipeline 20: Supplier Management

- **Step 0 (Global Ingestion).** docling, pypdf, and python-calamine pull strategy, RFP/RFQ packs, proposals, clause libraries, contracts, and scorecards into the compiler manifest.
  located: python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a temporalio workflow gated on segmentation criteria and evaluation-dimension spans. No evaluation language, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Select and Bind).** pingouin and pandas score shortlists; clingo must accept mandatory policy constraints; jinja2 instantiates clause templates only for the stable model.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
  not located here: pingouin
- **Step 3 (Performance Path).** sktime forecasts supplier series; dowhy runs only if treatment and outcome spans survived identification inside this workflow.
  located: dowhy 0.14 (dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect)
  not located here: sktime
- **Step 4 (Execution).** zen-engine, pycasbin, python-docx, and streamlit are terminal activities of the generated workflow.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce)

#### Pipeline 21: Portfolio Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc and openpyxl ingest strategy, demand briefs, business cases, and current portfolio workbooks into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 builds a dagster asset graph from value, risk, dependency, and constraint spans. Empty case set cancels selection assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Graph and Mix).** networkx and criticalpath emit the initiative graph; pulp and ortools optimize mix under budget and capacity bounds compiled by pydantic.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 3 (Selection Proof).** z3-solver must accept mutual-exclusion and prerequisite constraints on the incumbent or no publication asset is materialized.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** plotly, autoviz, and quarto fire as leaf assets for the authorized portfolio and balancing views.
  located: plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: autoviz, quarto

#### Pipeline 22: Service Financial Management

- **Step 0 (Global Ingestion).** undoc, firecrawl-anydoc, and python-calamine flatten policy, cost-model workbooks, budgets, invoices, and charging catalogs into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a temporalio workflow only if stanza recovers cost-pool, allocation, and charging predicates. Missing ledger language yields a halt.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Schema and Proof).** dasel and pydantic instantiate cost schemas into duckdb; zen-engine binds allocation tables; clingo must prove debit/credit/recovery consistency.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Quant and Select).** numpy-financial and statsmodels compute unit cost and variance only on the proved ledger; autoviz may select charts only from those tables.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table)
  not located here: autoviz, numpy-financial
- **Step 4 (Execution).** plotly, finSankey, streamlit, and great-tables are terminal activities.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: finSankey

#### Pipeline 23: Risk Management

- **Step 0 (Global Ingestion).** docling parses risk policy, registers, control libraries, audit findings, and appetite statements into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 keeps pgmpy, networkx, and pymc assets only when threat, impact, and control spans resolve. No appetite bound means no treatment flow.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination)
  not located here: pymc
- **Step 2 (Graph and Posterior).** pgmpy and networkx build the risk net; pymc, numpyro, and arviz run only after typedlogic facts compile.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination)
  not located here: arviz, pymc
- **Step 3 (Treatment Proof).** ortools selects avoid/reduce/transfer/accept portfolios; z3-solver must accept residual-versus-appetite or the plan asset is not written.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
- **Step 4 (Execution).** python-docx, plotly, and great-tables fire as leaf assets.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)

#### Pipeline 24: Service Continuity Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc and markitdown flatten continuity policy, BIA worksheets, dependency maps, runbooks, and exercise reports into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 admits continuity assets only when critical-service, RTO, and RPO fields type-check in pydantic. Missing RTO/RPO cancels the flow.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (BIA Graph).** networkx maps service-to-CI-to-site edges from Pipeline 13; pandas emits impact-over-time tables.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
- **Step 3 (Invocation Proof).** typedlogic and clingo encode invocation and exclusive-use facts; simpy and most-queue replay recovery; pysmt must accept RTO/RPO on the declared graph.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); simpy 4.1.2 (simpy.Environment, Environment.run); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 4 (Execution).** reliability, mermaid, and python-docx are leaf assets for curves, flowcharts, and plans.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing)
  not located here: mermaid

#### Pipeline 25: Strategy Management

- **Step 0 (Global Ingestion).** undoc dumps corporate strategy, market analyses, capability assessments, and prior reviews into the compiler manifest.
  located: undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a prefect flow whose task set exists only if stanza recovers driver, goal, and option spans. Empty option set halts publication.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Map and Option Proof).** networkx and se-lib emit capability maps; typedlogic records options; z3-solver must accept consistency against Pipeline 16 principles.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
  not located here: se-lib
- **Step 3 (Roadmap).** criticalpath sequences initiatives onto the Pipeline 21 graph only after the option proof.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all)
- **Step 4 (Execution).** quarto and plotly fire as leaf assets.
  located: plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: quarto

#### Pipeline 26: Information Security Management

- **Step 0 (Global Ingestion).** docling, pypdf, and dasel pull policy, control catalogs, threat notes, identity models, and privacy regulations into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a temporalio workflow gated on control-objective and classification spans. No classification scheme, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Ontology and Policy).** owlready2 and rdflib hold the catalog; pycasbin and openfga are generated only for proved permissions.
  located: owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
  not located here: openfga
- **Step 3 (Residual Proof).** pgmpy links assets, threats, and controls; z3-solver and clingo must accept no conflicting allow/deny and no unclassified critical asset.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination)
- **Step 4 (Execution).** python-docx, mermaid, and streamlit are terminal compensation-safe activities.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)
  not located here: mermaid

#### Pipeline 27: Availability Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc and csvkit flatten SLRs, architecture constraints, outage histories, and maintenance windows into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 admits reliability, lifelines, and fmdtools assets only when an availability target and an outage series both type-check. Otherwise the run stops.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit)
  not located here: fmdtools
- **Step 2 (Block and Fit).** reliability builds block diagrams from Pipeline 13/14 graphs; scipy rejects unphysical fits; pysmt must accept redundancy versus target.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); scipy 1.15.3 (optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Execution).** lifelines writes restore shapes; fmdtools runs only after the cut-set proof; plotly, streamlit, and python-docx are leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: fmdtools

#### Pipeline 28: Capacity and Performance Management

- **Step 0 (Global Ingestion).** undoc, python-calamine, and csvkit ingest baselines, utilization dumps, demand forecasts, and capacity plans into the compiler manifest.
  located: python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 keeps prophet, darts, pmdarima, and most-queue assets only when a time column and a utilization field type-check. No series, no forecast flow.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim)
  not located here: darts, pmdarima, prophet
- **Step 2 (Forecast and Queue).** prophet, darts, and pmdarima emit demand paths; python-control and most-queue model response; gekko optimizes settings under compiled cost bounds.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim)
  not located here: darts, gekko, pmdarima, prophet, python-control
- **Step 3 (Cover Proof).** z3-solver must accept planned capacity versus forecast peak plus contingency or dashboard assets are not materialized.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** plotly, streamlit, and python-docx fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)

#### Pipeline 29: Continual Improvement Management

- **Step 0 (Global Ingestion).** docling flattens strategy goals, CSI registers, audit findings, feedback exports, and every later review artifact into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 builds a dagster asset graph from idea, benefit, and constraint spans. Empty idea set cancels register assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Prioritize and Gate).** pandas holds the register; pulp ranks under benefit/effort/risk; networkx supplies dependencies; zen-engine and typedlogic must accept intake rules.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 3 (Execution Tracking).** spiffworkflow runs approved items as durable workflows and may emit change payloads into Pipeline 39 only after clingo accepts the mutation edge.
  located: SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** great-tables and quarto are leaf assets for the register and benefit-realization review.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html)
  not located here: quarto

#### Pipeline 30: Measurement and Reporting Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc and csvkit flatten measurement policy, reporting requirements, KPI catalogs, and raw metric extracts into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a prefect flow only if metric-definition and audience-view spans resolve. Orphan KPI names with no formula halt publication.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Metric Proof).** pydantic types metric objects into duckdb; clingo must prove every reported figure is derivable from a registered definition and a source extract.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute)
- **Step 3 (Execution).** autoviz, plotly, great-tables, streamlit, panel, and quarto fire as leaf assets only on the proved tables.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: autoviz, panel, quarto

#### Pipeline 31: Service Level Management

- **Step 0 (Global Ingestion).** undoc and markitdown dump catalog entries, SLR/SLA/OLA/UC drafts, performance reports, and complaint logs into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a temporalio workflow gated on commitment and measurement-method spans. No commitment language, no agreement assets.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Agreement Proof).** pydantic instantiates SLA/OLA/UC objects; zen-engine binds credit and escalation tables; pysmt must accept attainability against Pipelines 27 and 28.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Attainment).** duckdb computes attainment from Pipeline 30 only after the SMT proof.
  located: duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute)
- **Step 4 (Execution).** python-docx and streamlit are terminal activities.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)

#### Pipeline 32: Monitoring and Event Management

- **Step 0 (Global Ingestion).** docling and csvkit flatten monitoring standards, event catalogs, correlation rules, and tool exports into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 keeps durable-rules, experta, and pydantic event assets only when event-type and severity spans resolve. No catalog, no correlation flow.
  located: durable-rules 2.0.28 (lang.ruleset, lang.when_all, lang.post, lang.m); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
  not located here: experta
- **Step 2 (Correlate and Hand-off).** durable-rules or experta execute compiled Rete rules; pm4py maps event-to-incident/change/request edges; unified-planning sequences runbooks.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); durable-rules 2.0.28 (lang.ruleset, lang.when_all, lang.post, lang.m); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: experta
- **Step 3 (Coverage Proof).** clingo must accept that every critical event class has filter, correlation, and response paths or dashboard assets halt.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** streamlit, plotly, and mermaid fire as leaf assets.
  located: streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: mermaid

#### Pipeline 33: Incident Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc and csvkit flatten incident models, ticket dumps, alerts, known-error articles, and major-incident reports into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a dagster asset graph only if category, impact, and urgency fields type-check. Missing model set cancels routing assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Route and Localize).** zen-engine applies compiled incident models; networkx walks Pipeline 13 to localize nodes; pm4py compares the live path to the model.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 3 (Restore Proof).** lifelines estimates remaining restore time; reliability flags major-incident risk; csv-diff may emit model-update payloads into Pipeline 29 only if exception rates breach compiled thresholds.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit)
  not located here: csv-diff
- **Step 4 (Execution).** streamlit, python-docx, and mermaid are leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)
  not located here: mermaid

#### Pipeline 34: Problem Management

- **Step 0 (Global Ingestion).** undoc and docling parse incident histories, vendor advisories, monitoring trends, configuration snapshots, and known-error articles into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a prefect flow gated on amrlib producing causal or error-hypothesis graphs from clustered incidents. No causal AMR, no workflow.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); amrlib 0.8.1 (amrlib.load_stog_model, Inference.parse_sents)
- **Step 2 (Cause and Known Error).** dowhy and pgmpy test structure; amr-logic-converter and pysmt formalize mechanisms; typedlogic records known-error facts only after the SMT proof.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); dowhy 0.14 (dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Solution and Close).** unified-planning and ortools explore strategies; zen-engine may emit a change payload into Pipeline 39; z3-solver must accept closure evidence or the record stays open in duckdb.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute)
- **Step 4 (Execution).** python-docx, mermaid, and clingraph fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: clingraph, mermaid

#### Pipeline 35: Service Desk

- **Step 0 (Global Ingestion).** docling and markitdown flatten query transcripts, eligibility rules, omnichannel policy, templates, and desk metrics into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a temporalio workflow only if triage-guideline and channel spans resolve. Empty guideline set yields a halt.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Triage and Pack).** spacy types ticket fields; zen-engine and business-rules route to Pipelines 33, 34, or 36; jinja2 and stanza assemble messages only for compiled channel constraints.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render); spacy 3.8.16 (spacy.blank, Language.add_pipe, pipeline.Sentencizer, Doc.ents)
- **Step 3 (Feedback and Improve).** pandas stores confirmations and CSAT; statsmodels scores desk series; pulp may emit Pipeline 29 items if compiled thresholds fail.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 4 (Execution).** streamlit and python-docx are terminal activities.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)

#### Pipeline 36: Service Request Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc flattens request models, catalog entries, SLA constraints, request text, and fulfilment logs into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 keeps spiffworkflow and pydantic request assets only when a matching model key or an ad-hoc flag type-checks. Neither present, no fulfilment flow.
  located: SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (Model or Plan).** spiffworkflow executes matched models; unified-planning synthesizes ad-hoc plans; zen-engine writes approval tables as artifacts, not as a human gate.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
- **Step 3 (Replay).** pm4py compares executed paths to the model; pandas and pingouin score cycle time into Pipeline 29 only on deviation.
  located: pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: pingouin
- **Step 4 (Execution).** streamlit and python-docx fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)

#### Pipeline 37: Service Catalog Management

- **Step 0 (Global Ingestion).** undoc and markitdown dump strategy, portfolio overview, current catalog extracts, contracts, and questionnaires into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 builds a dagster asset graph from granularity, view, and access-rule spans. No view definition cancels publication assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Model and View).** dasel and pydantic instantiate the catalog into duckdb; jinja2 and great-tables emit standard views; pycasbin binds access only after clingo accepts mandatory-attribute completeness.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); duckdb 1.5.5 (duckdb.connect, DuckDBPyConnection.execute); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Request Path).** zen-engine processes view requests and logs exceptions into the same store.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
- **Step 4 (Execution).** streamlit, datasette, and python-docx are leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)
  not located here: datasette

#### Pipeline 38: Business Relationship Management

- **Step 0 (Global Ingestion).** docling parses strategy, sponsor/customer data, stakeholder maps, performance reports, and prior relationship reviews into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a prefect flow only if stakeholder-group and relationship-domain spans resolve. Empty map cancels journey assets.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Health and Offer).** networkx builds the RACI graph; pandas scores VoC; typedlogic records principles; zen-engine shapes offerings only under Pipeline 21 constraints that already proved.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
- **Step 3 (Journey).** pydantic stores terms; pm4py tracks onboard/co-create/review/offboard and refuses offboard without a compiled sustainment record.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 4 (Execution).** python-docx and streamlit fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)

#### Pipeline 39: Change Enablement

- **Step 0 (Global Ingestion).** firecrawl-anydoc flattens change policy, change models, RFC text, risk notes, and post-implementation reviews into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a temporalio workflow gated on change-type, risk, and success-criteria spans. No model match and no risk span, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Assess and Authorize).** pydantic creates the record; zen-engine applies compiled models; pycasbin and business-rules bind the authority matrix; clingo must accept freeze-window and exclusive-resource constraints. Authorization is the stable model written to the record.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 3 (Plan and Replay).** criticalpath and unified-planning emit the plan; simpy dry-runs against Pipeline 13 state; pm4py and csv-diff refuse closure if executed path diverges without a compensation fact.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); criticalpath 0.1.5 (criticalpath.Node, Node.update_all); simpy 4.1.2 (simpy.Environment, Environment.run); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: csv-diff
- **Step 4 (Execution).** python-docx, mermaid, and streamlit are terminal activities. Proved mutations publish back onto the manifest edges used by Pipelines 13, 17, 18, 37, 41, 43, and 44.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)
  not located here: mermaid

#### Pipeline 40: Project Management

- **Step 0 (Global Ingestion).** undoc and markitdown dump strategy, mandates, business cases, stage reports, risk/issue logs, and work-package definitions into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 builds a dagster asset graph from tolerance, deliverable, and exception-trigger spans. Missing tolerance set cancels control assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Gates and Schedule).** pydantic instantiates PID/stage/work-package schemas; zen-engine encodes initiate/project/stage/exception/closure graphs; criticalpath and ortools solve resource-feasible plans.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
- **Step 3 (Exception Proof).** typedlogic and z3-solver must accept that an exception plan restores tolerances given updated case numbers or the next-stage asset is not materialized.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** pandas, plotly, mermaid, python-docx, and quarto fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: mermaid, quarto

#### Pipeline 41: Software Development and Management

- **Step 0 (Global Ingestion).** docling flattens strategy, architecture guidelines, backlogs, design notes, test records, and telemetry summaries into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes prefect tasks only if backlog-item and architecture-constraint spans resolve. Empty backlog cancels design assets.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Guide and Rank).** typedlogic records SDM rules against Pipeline 16; pulp ranks tasks under value, risk, and networkx product edges.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 3 (Design Proof).** z3-solver must accept design artifacts against non-functional bounds; python-sat encodes feature-model constraints where present; zen-engine may emit RFC payloads into Pipeline 39 only after that proof.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); python-sat 1.9.dev15 (solvers.Solver, rc2.RC2); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** mermaid, diagrams, and python-docx are leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: mermaid

#### Pipeline 42: Service Validation and Testing

- **Step 0 (Global Ingestion).** firecrawl-anydoc flattens test policy, acceptance-criteria drafts, model catalogs, environment sheets, and prior test records into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 admits testing assets only when acceptance predicates and a model key type-check. No predicate set, no plan flow.
- **Step 2 (Criteria Proof).** typedlogic records exit criteria; pysmt and model-checker must accept internal consistency and entailment of Pipeline 15 requirements.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
  not located here: model-checker
- **Step 3 (Plan and Exception).** unified-planning and ortools emit the tailored plan; zen-engine classifies exceptions; clingo must accept that every failed exit criterion has a defect or exception record.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** great-tables, python-docx, and mermaid fire as leaf assets.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: mermaid

#### Pipeline 43: Deployment Management

- **Step 0 (Global Ingestion).** undoc and markitdown dump deployment models, pipeline configs, DML manifests, environment inventories, and failure analyses into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a temporalio workflow gated on environment, success-criteria, and rollback spans plus a triggering Pipeline 39 change fact. No change fact, no deploy workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Readiness Proof).** pydantic describes pipeline elements; typedlogic encodes pre-deploy predicates; clingo, z3-solver, and csv-diff must accept component and environment readiness.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
  not located here: csv-diff
- **Step 3 (Review).** unified-planning emits the instance plan; pm4py mines logs against the model; pandas may emit Pipeline 29 items on recurring unsat.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 4 (Execution).** mermaid and python-docx are terminal compensation-safe activities.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: mermaid

#### Pipeline 44: Release Management

- **Step 0 (Global Ingestion).** docling flattens product/service architecture, relationship maps, release policies, change schedules, and prior reviews into the compiler manifest.
  located: docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes a prefect flow only if a release-model key and go/no-go language both resolve against Pipelines 39 and 43 facts. Missing go-criteria cancels execution assets.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Select and Prove).** zen-engine selects the model; criticalpath builds the schedule; typedlogic and z3-solver must accept procedure, component-verification, and readiness jointly.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 3 (Review).** pm4py and pandas compare logs and incidents to success criteria; reliability flags release-induced signatures into Pipeline 34.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 4 (Execution).** mermaid and python-docx fire as leaf assets and write knowledge payloads into Pipeline 46.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: mermaid

#### Pipeline 45: Organizational Change Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc and undoc flatten business architecture, culture reviews, OCM audits, change requests, and adoption metrics into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 emits a dagster asset graph only if change-vision and impacted-role spans resolve. Empty stakeholder set cancels communication assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Ready and Plan).** networkx maps roles; pandas and pingouin score readiness; unified-planning and criticalpath emit the engagement sequence; zen-engine writes the proceed certificate only if feasibility constraints compile.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); criticalpath 0.1.5 (criticalpath.Node, Node.update_all); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
  not located here: pingouin
- **Step 3 (Sustain Proof).** statsmodels tracks adoption; clingo must accept that every declared early-win has an evidence record or sustainment assets halt.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** python-docx and quarto are leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: quarto

#### Pipeline 46: Knowledge Management

- **Step 0 (Global Ingestion).** markitdown, undoc, and docling dump strategy, domain inventories, knowledge bases, roadmaps, and usage logs into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline 0 writes prefect tasks for rdflib and networkx only if domain, owner, and demand spans exist in the census. No demand item, no routine flow.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 2 (Inventory Proof).** networkx maps domains to owners; rdflib stores assets; typedlogic records guidelines; clingo must accept that every high-priority demand is fulfilled or queued.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 3 (Routines).** spiffworkflow executes capture/review/publish/retire; pydantic versions assets; ydata-profiling and pandas may emit Pipeline 29 items when freshness thresholds fail.
  located: ydata-profiling 4.18.4 (ydata_profiling.ProfileReport, ProfileReport.to_json); SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
- **Step 4 (Execution).** mkdocs, quarto, python-docx, and mermaid fire as leaf assets.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save)
  not located here: mermaid, mkdocs, quarto

### Reverse pipelines

Pipeline R0 is Part 4 of this file. Every reverse pipeline ends in one workbook written by openpyxl, XlsxWriter, and pandas-xlsx-tables (Part 3, T3).

#### Pipeline R0: Zero-Touch Invert Compiler

- **Step 0 (Global Ingestion).** docling, undoc, markitdown, firecrawl-anydoc, mammoth, office-oxide, python-pptx, python-docx, pymupdf, pypdf, pypdfium2, and playwright crawl the published folder and emit a mixed Markdown, JSON, CSV, slide-XML, document-XML, and HTML inventory with no predeclared schema.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); python-pptx 1.0.2 (pptx.Presentation, Presentation.slides, Slide.shapes, Slide.notes_slide); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); pypdfium2 5.13.0 (pypdfium2.PdfDocument, PdfPage.get_textpage, PdfTextPage.get_text_range); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Artifact Census).** ydata-profiling, sweetviz, and dataprep profile every recovered table; dasel walks JSON, YAML, and XML; python-docx and office-oxide fingerprint Word heading trees, styles, and content controls; python-pptx fingerprints slide masters, layouts, placeholders, notes, and chart caches; pymupdf and pypdf fingerprint remaining PDFs; markdownify and html2text flatten Streamlit, Dash, Panel, NiceGUI, MkDocs, Quarto, Reveal, Folium, and Kepler pages captured by playwright into a single machine-readable manifest.
  located: ydata-profiling 4.18.4 (ydata_profiling.ProfileReport, ProfileReport.to_json); office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); python-pptx 1.0.2 (pptx.Presentation, Presentation.slides, Slide.shapes, Slide.notes_slide); markdownify 1.2.3 (markdownify.markdownify); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); html2text 2025.4.15 (html2text.HTML2Text, HTML2Text.handle); sweetviz 2.3.3 (sweetviz.analyze, DataframeReport.show_html); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
  not located here: dataprep
- **Step 2 (Schema Compilation).** dasel projections are typed by pydantic at runtime, producing the only schemas the rest of the run is allowed to use. openpyxl, xlsxwriter, and pandas-xlsx-tables write those schemas as the pipeline spreadsheet.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Capability Logic).** typedlogic writes clingo facts from the manifest (mime class, heading lexicon, table shapes, deontic verbs, geo fields, SLA tokens, C4 labels, slide layout names, time-to-event columns). clingo returns the unique stable model of which forward pipeline produced the pack, which libraries are legal for invert, which libraries are legal for replay, and which output mime types must be regenerated.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Graph Compilation).** networkx and graphable turn that stable model into a directed invert graph and a directed replay graph. jinja2 renders both graphs into prefect flow source, dagster asset definitions, or a temporalio workflow module, including retries, result persistence, and compensation on solver unsat.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render)
  not located here: graphable
- **Step 5 (Self-Load).** the chosen orchestrator imports the file it just wrote, registers the assets, and starts the run. No flow, schedule, partition, or retry policy exists before this step. Every admitted reverse pipeline emits exactly one .xlsx.

#### Pipeline R1: Reverse Quality Engineering

- **Step 0 (Global Ingestion).** docling and markitdown flatten any FMEA narrative, PDF appendix, or HTML dossier emitted beside fmdtools into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: fmdtools
- **Step 1 (Orchestration and Narrowing).** dagster orchestrates the workflow, piping recovered text into spacy to isolate failure-mode, effect, and cause spans.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize); spacy 3.8.16 (spacy.blank, Language.add_pipe, pipeline.Sentencizer, Doc.ents)
- **Step 2 (Logic Generation).** amr-logic-converter translates those spans directly into First-Order Logic formulas. QE_MODE, QE_EVENT, and QE_FIT are typed by pydantic and written into that pipeline's spreadsheet.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 3 (Mathematical Verification).** pysmt consumes the formulas generated from the recovered instance to mathematically verify the physical bounds and logic paths.
  located: PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 4 (Time-to-Event Modeling).** lifelines applies survival analysis to the recovered failure events only after scipy rejects unphysical rows.
  located: lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit); scipy 1.15.3 (optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog)
- **Step 5 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R2: Reverse Financial Dashboarding

- **Step 0 (Global Ingestion).** playwright, firecrawl-anydoc, and markitdown flatten the Streamlit HTML and embedded Plotly traces into Markdown and JSON.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto)
- **Step 1 (Orchestration and Narrowing).** temporalio manages the pipeline state, passing the recovered text to stanza to map financial entities and periods.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Schema Auto-Generation).** dasel queries the structured outputs of the NLP step and datamodel-code-generator instantiates FIN_ENTITY, FIN_LEDGER, FIN_KPI, and FIN_RULE in that pipeline's spreadsheet.
  located: datamodel-code-generator 0.76.1 (datamodel_code_generator.generate, datamodel_code_generator.InputFileType); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 3 (Logic Enforcement).** zen-engine evaluates the recovered instance against the decision graph recovered from the published dashboard.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
- **Step 4 (Constraint Verification).** clingo proves debit/credit identity of the recovered ledger.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 5 (Visual Selection).** autoviz remains frozen to the recovered chart grammar and may select no new grammar.
  not located here: autoviz
- **Step 6 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R3: Reverse Architecture Documentation

- **Step 0 (Global Ingestion).** markitdown, undoc, and playwright flatten mermaid HTML, SVG titles, and sidecar Markdown into flat text and JSON.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: mermaid
- **Step 1 (Orchestration and Narrowing).** prefect orchestrates the data flow, piping recovered text into nltk to extract entity relationships.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); nltk 3.10.3 (tokenize.sent_tokenize, tokenize.PunktSentenceTokenizer, logic.LogicParser, inference.Prover9)
- **Step 2 (Network Graphing).** networkx rebuilds the published node-edge set. ARCH_NODE, ARCH_EDGE, and ARCH_VIEW land in that pipeline's spreadsheet. Diagram kind is a recovered fact.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
- **Step 3 (Logic Translation).** typedlogic converts the recovered network dependencies directly into clingo facts.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Architecture Modeling).** structurizr-python maps those facts into its C4 model DSL from the recovered instance rows.
- **Step 5 (Verification).** z3-solver verifies the recovered architecture has no cyclical dependencies.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 6 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R5: Reverse Process Mining Control Room

- **Step 0 (Global Ingestion).** playwright and markitdown flatten dash-cytoscape and streamlit pages; embedded event-log JSON lands in the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write)
  not located here: dash-cytoscape
- **Step 1 (Orchestrator Compilation).** Pipeline R0 runs against the manifest. clingo only admits a process-mining asset graph if actor, activity, and time fields all resolve in that pipeline's spreadsheet; otherwise the run stops.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 2 (Event Log Materialization).** the generated dagster assets type PM_EVENT, PM_NET, and PM_KPI through pydantic and land them in that pipeline's spreadsheet.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 3 (Discovery and Replay).** pm4py rediscovers the net from recovered events; snakes and simpn replay it; typedlogic facts that fail clingo drop the trace rather than pass it downstream.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); snakes 0.9.33 (nets.PetriNet, PetriNet.add_place); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent); simpn 1.10.0 (simulator.SimProblem, SimProblem.simulate)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R6: Reverse Causal Policy Evaluation

- **Step 0 (Global Ingestion).** playwright, markitdown, and docling flatten panel pages, forestplot tables, and printed PDFs into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: forestplot, panel
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a prefect flow whose task set exists only if treatment and outcome spans resolve from the published copy. Missing identification language yields an empty flow and a halt.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Graph and Proof).** CAUSAL_VAR, CAUSAL_EDGE, CAUSAL_ADJUSTMENT, and CAUSAL_ESTIMATE land in that pipeline's spreadsheet. The generated flow rebuilds the DAG in pgmpy, dowhy, and networkx from recovered edges, then asks z3-solver and pysmt to prove a legal adjustment set.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); dowhy 0.14 (dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Estimation and Binding).** causalpy, statsmodels, pymc, and arviz run only on proved strategies. zen-engine receives effect estimates as decision tables written from CAUSAL_ESTIMATE, not by an operator.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
  not located here: arviz, causalpy, pymc
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R7: Reverse Supply Chain Scheduling

- **Step 0 (Global Ingestion).** playwright, firecrawl-anydoc, and docling flatten Highcharts Gantt HTML, taipy pages, elegantt sidecars, and printed PDFs into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: elegantt, taipy
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a temporalio workflow whose activities are the clingo-selected subset of pulp, pyomo, ortools, highspy, pyjobshop, and alns recovered from the published schedule.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
  not located here: alns, highspy, pyjobshop, pyomo
- **Step 2 (Model Emission).** SC_TASK, SC_RESOURCE, SC_CALENDAR, SC_CONSTRAINT, and SC_OBJECTIVE land in that pipeline's spreadsheet. pydantic schemas from those tables become the MIP/CP model inside the workflow. There is no checked-in LP file.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 3 (Solve and Repair).** ortools or highspy solves the recovered instance; alns runs only if the workflow’s compensation path sees a bound and no feasible incumbent.
  located: ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
  not located here: alns, highspy
- **Step 4 (Calendar Proof).** criticalpath and clingo must accept the incumbent or the workflow does not call a renderer.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 5 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R8: Reverse Geospatial Hazard Cartography

- **Step 0 (Global Ingestion).** playwright extracts GeoJSON from Folium and Kepler HTML; undoc, docling, and pymupdf flatten weasyprint PDF map sheets into the compiler manifest.
  located: playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: weasyprint
- **Step 1 (Orchestrator Compilation).** Pipeline R0 keeps geopandas, shapely, osmnx, and rustworkx assets only when dasel finds coordinates or resolvable toponyms. No geo fields means no map flow.
  located: dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
  not located here: geopandas, osmnx, rustworkx, shapely
- **Step 2 (Constraint Compile).** GEO_FEATURE, GEO_EXCLUSION, GEO_COVERAGE, and GEO_STYLE land in that pipeline's spreadsheet. python-constraint2 and cpmpy receive exclusion and coverage predicates extracted into pydantic models from the recovered instance.
  located: python-constraint2 2.7.3 (constraint.Problem, Problem.getSolutions); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
  not located here: cpmpy
- **Step 3 (Surface and Sheet).** datashader, eomaps, contextily, prettymaps, pygmt, and lonboard run in the order the compiled graph recovered from the published pack.
  not located here: contextily, datashader, eomaps, lonboard, prettymaps, pygmt
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R9: Reverse Contract Constraint Prover

- **Step 0 (Global Ingestion).** python-docx, mammoth, office-oxide, docling, and pypdf pull clauses and defined-term tables from the published Word pack into the compiler manifest. playwright flattens nicegui proof pages.
  located: office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata)
  not located here: nicegui
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a temporalio workflow gated on amrlib producing obligation, right, or condition-precedent graphs from the recovered clauses. No deontic AMR, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); amrlib 0.8.1 (amrlib.load_stog_model, Inference.parse_sents)
- **Step 2 (Logic Emission).** LEGAL_PARTY, LEGAL_TERM, LEGAL_CLAUSE, LEGAL_OBLIGATION, and LEGAL_PERMISSION land in that pipeline's spreadsheet. amr-logic-converter and typedlogic write the FOL and ASP programs from recovered clause recovered fields that the workflow will hand to clingo, pysmt, and cvc5.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat); cvc5 1.3.4 (cvc5.Solver, Solver.checkSat, Solver.getUnsatCore)
- **Step 3 (Policy Materialization).** pycasbin, openfga, and zen-engine are generated as downstream activities only for proved permissions.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce)
  not located here: openfga
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R10: Reverse Specification-to-Slide Compiler

- **Step 0 (Global Ingestion).** python-pptx, office-oxide, undoc, and markitdown turn the published PowerPoint, speaker notes, and chart caches into the compiler manifest. playwright flattens reveal-md and marp HTML. docling and pymupdf flatten quarto and weasyprint PDFs.
  located: office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); python-pptx 1.0.2 (pptx.Presentation, Presentation.slides, Slide.shapes, Slide.notes_slide); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: marp, quarto, reveal-md, weasyprint
- **Step 1 (Orchestrator Compilation).** Pipeline R0 builds a dagster asset graph from recovered requirement, risk, and milestone spans. Empty claim set cancels publication assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Trace Proof).** DECK_META, DECK_SLIDE, DECK_BULLET, DECK_CLAIM, DECK_CHART, and DECK_IMAGE land in that pipeline's spreadsheet. template_id, aspect, layout_name, and chart grammar are recovered facts. title, body, notes, bullet text, claim text, and series_json are recovered fields. networkx and graphedexcel supply edges from DECK_CLAIM; business-rules, durable-rules, and z3-solver must accept completeness and acyclicity before any slide asset is materialized.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); durable-rules 2.0.28 (lang.ruleset, lang.when_all, lang.post, lang.m); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
  not located here: graphedexcel
- **Step 3 (Grammar Selection).** lida, autoviz, mermaid, and kroki are included only for tables and relations present in the proved graph and remain frozen to the recovered grammars.
  not located here: autoviz, kroki, lida, mermaid
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R11: Reverse Fleet Reliability Dossier

- **Step 0 (Global Ingestion).** playwright and markitdown flatten the Streamlit dossier; kaleido PDF and PNG sidecars are re-tabulated by pymupdf and csvkit into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
  not located here: kaleido
- **Step 1 (Orchestrator Compilation).** Pipeline R0 admits reliability and lifelines assets only when a time-to-event column and a censoring flag both type-check in that pipeline's spreadsheet.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit)
- **Step 2 (Fit and Cut Sets).** REL_ASSET, REL_EVENT, REL_BLOCK, and REL_FIT land in that pipeline's spreadsheet. scipy rejects unphysical fits; fmdtools and z3-solver run only if series/parallel language compiled into block-diagram facts.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); scipy 1.15.3 (optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog)
  not located here: fmdtools
- **Step 3 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R12: Reverse Ontology Reasoner

- **Step 0 (Global Ingestion).** playwright, markitdown, and firecrawl-anydoc flatten the MkDocs site and datasette pages; rdflib parses any published RDF, TTL, or JSON-LD into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
  not located here: datasette
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes prefect tasks for rdflib and owlready2 only if class, property, or disjointness phrases exist in the census.
  located: owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 2 (Closure and Proof).** ONT_CLASS, ONT_PROPERTY, ONT_AXIOM, and ONT_INDIVIDUAL land in that pipeline's spreadsheet. owlrl and pyreason close the recovered graph; z3-solver, cvc5, and clingo must accept the TBox/ABox pair.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); owlrl 7.6.2 (owlrl.DeductiveClosure); cvc5 1.3.4 (cvc5.Solver, Solver.checkSat, Solver.getUnsatCore)
  not located here: pyreason
- **Step 3 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R13: Reverse Service Configuration Management

- **Step 0 (Global Ingestion).** python-docx, mammoth, office-oxide, pymupdf, and markitdown flatten the verification Word pack and reportlab PDF; mermaid source is lifted from the HTML sidecar into the compiler manifest.
  located: office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text); PyMuPDF 1.28.2 (pymupdf.open, Page.get_text, pymupdf.open, Page.get_text)
  not located here: mermaid, reportlab
- **Step 1 (Orchestrator Compilation).** Pipeline R0 runs against the manifest. clingo only admits a configuration asset graph if CI-type spans, relationship language, and a lifecycle verb set all resolve in that pipeline's spreadsheet; otherwise the run stops.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 2 (Model Emission).** CI_RECORD, CI_RELATION, CI_STATE, CI_TRANSITION, and CI_EXCEPTION are typed by pydantic and written into that pipeline's spreadsheet. networkx materializes the CI graph from those records.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
- **Step 3 (Lifecycle Proof).** typedlogic writes transition, exception, and verification facts from the recovered instance; clingo and z3-solver must accept state consistency and acyclicity or no corrective asset is materialized.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Verification Replay).** pm4py mines transition logs against the proved lifecycle; csv-diff and daff emit discrepancy tables only for traces that failed the stable model.
  located: pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: csv-diff, daff
- **Step 5 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R14: Reverse Service Design

- **Step 0 (Global Ingestion).** python-docx, mammoth, undoc, and firecrawl-anydoc flatten the Service Design Package and any diagrams, mermaid, or structurizr HTML into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a prefect flow only if stanza recovers principle, decomposition, and operational-constraint spans from the published pack. Missing principle language yields an empty flow and a halt.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Requirement Proof).** SD_PRINCIPLE, SD_SERVICE, SD_INTERACTION, SD_SLA, and SD_CONSTRAINT land in that pipeline's spreadsheet. amr-logic-converter and pysmt must accept usability, cost, performance, security, and compliance bounds on the recovered rows before any model asset exists.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Structure and Interaction).** networkx and pydsm rebuild the service breakdown; pm4py and snakes encode interaction flows; zen-engine writes SLA/OLA tables from proved commitments.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); snakes 0.9.33 (nets.PetriNet, PetriNet.add_place); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: pydsm
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R15: Reverse Business Analysis

- **Step 0 (Global Ingestion).** python-docx, office-oxide, mammoth, and markitdown turn the published specification, matrix, and communications pack into the compiler manifest.
  located: office-oxide 0.1.9 (office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); mammoth 1.12.1 (mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 builds a dagster asset graph from recovered stakeholder, requirement, and conflict spans. Empty requirement set cancels specification assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Elicitation and Model).** BA_STAKEHOLDER, BA_REQUIREMENT, BA_CONFLICT, and BA_TRACE land in that pipeline's spreadsheet. typedlogic and rdflib recategorize recovered functional, non-functional, and transition requirements; networkx holds the stakeholder influence graph.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 3 (Verify and Trace).** vampire and model-checker must accept clarity, consistency, and testability; the pipeline spreadsheet and csv-diff keep the traceability matrix and refuse baseline drift that fails z3-solver.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
  not located here: csv-diff, model-checker, vampire
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R16: Reverse Architecture Management

- **Step 0 (Global Ingestion).** quarto HTML, PDF, and docx packs plus mermaid, diagrams, and pyArchimate exports are flattened by docling, markitdown, python-docx, and playwright into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: mermaid, quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes prefect tasks for owlready2, rdflib, and networkx only if principle and viewpoint phrases exist in the census. No principle set, no architecture flow.
  located: owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 2 (Target Graph and Roadmap).** AM_PRINCIPLE, AM_VIEWPOINT, AM_BUILDING_BLOCK, AM_GAP, and AM_ROADMAP_ITEM land in that pipeline's spreadsheet. rustworkx and pydsm assemble current-versus-target graphs from recovered rows; criticalpath and se-lib sequence work packages only after typedlogic facts compile.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom)
  not located here: pydsm, rustworkx, se-lib
- **Step 3 (Conformance Proof).** z3-solver must accept acyclicity; clingo must accept building-block compliance with the compiled metamodel or view assets are not materialized.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R17: Reverse Infrastructure and Platform Management

- **Step 0 (Global Ingestion).** playwright flattens the Streamlit app; python-docx, undoc, and markitdown flatten the runbook and hardening Word pack into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 keeps pydantic pattern assets and unified-planning provision assets only when standard, SLA, and recovery-objective spans type-check in that pipeline's spreadsheet. Missing recovery language drops the build graph.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (Design and Constraint).** INFRA_PATTERN, INFRA_SLA, INFRA_BOM, INFRA_NODE, and INFRA_RECOVERY land in that pipeline's spreadsheet. casadi and python-control emit dynamics models from recovered settings; cpmpy and z3-solver must accept bill-of-materials, network, and hardening predicates.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
  not located here: casadi, cpmpy, python-control
- **Step 3 (Operate and Retire).** simpy and simprocesd replay backup, patch, and health tasks; clingo must accept dependency-safe retirement against the Pipeline R13 CI graph or decommission assets halt.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); simpy 4.1.2 (simpy.Environment, Environment.run)
  not located here: simprocesd
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R18: Reverse IT Asset Management

- **Step 0 (Global Ingestion).** openpyxl, python-calamine, fastexcel, and csvkit flatten the published register; markitdown flattens great-tables HTML and QR/barcode sheets into the compiler manifest.
  located: python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); fastexcel 0.21.0 (fastexcel.read_excel, ExcelReader.load_sheet, ExcelSheet.to_pandas); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 admits register assets only when asset-type, entitlement, and identifier columns type-check in that pipeline's spreadsheet. No entitlement table, no license flow.
- **Step 2 (Register and Proof).** ASSET_RECORD, ASSET_ENTITLEMENT, ASSET_CONSUMPTION, and ASSET_DISCREPANCY land in that pipeline's spreadsheet. clorm writes asset facts from the recovered instance; clingo must prove entitlement-versus-consumption under per-user, per-device, and concurrent models.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); clorm 1.6.3 (clorm.Predicate, clorm.FactBase, clingo.Control)
- **Step 3 (Audit Repair).** daff and csv-diff emit discrepancy tables; numpy-financial scores write-off and compliance exposure only on the unsat remainder.
  not located here: csv-diff, daff, numpy-financial
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R19: Reverse Workforce and Talent Management

- **Step 0 (Global Ingestion).** python-docx and markitdown flatten the workforce Word pack; playwright flattens the Streamlit dashboard into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a prefect flow only if role, competency, and FTE spans resolve in that pipeline's spreadsheet. Missing competency language yields an empty flow and a halt.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Plan and Ontology).** WF_ROLE, WF_COMPETENCY, WF_PERSON, WF_GAP, and WF_ALLOCATION land in that pipeline's spreadsheet. pandas and polars rebuild the gap matrix; networkx maps succession; owlready2 and typedlogic must accept a complete profile for every planned role.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
  not located here: polars
- **Step 3 (Allocation Proof).** ortools and pulp solve hiring and L&D allocation from the recovered instance; zen-engine binds role KPIs only if the solver returns a feasible incumbent.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R20: Reverse Supplier Management

- **Step 0 (Global Ingestion).** python-docx, pypdf, docling, and python-calamine pull the published contract and scorecard pack into the compiler manifest. playwright flattens the supplier dashboard.
  located: python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a temporalio workflow gated on segmentation criteria and evaluation-dimension spans recovered from the pack. No evaluation language, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Select and Bind).** SUP_SEGMENT, SUP_VENDOR, SUP_SCORE, SUP_CLAUSE, and SUP_POLICY land in that pipeline's spreadsheet. pingouin and pandas rescore shortlists from the recovered instance; clingo must accept mandatory policy constraints; jinja2 instantiates clause templates only for the stable model.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
  not located here: pingouin
- **Step 3 (Performance Path).** sktime forecasts supplier series; dowhy runs only if treatment and outcome spans survived identification inside this workflow.
  located: dowhy 0.14 (dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect)
  not located here: sktime
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R21: Reverse Portfolio Management

- **Step 0 (Global Ingestion).** quarto HTML, PDF, and docx plus plotly HTML are flattened by docling, markitdown, python-docx, and playwright into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 builds a dagster asset graph from recovered value, risk, dependency, and constraint spans. Empty case set cancels selection assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Graph and Mix).** PF_INITIATIVE, PF_VALUE, PF_RISK, PF_DEPENDENCY, PF_BUDGET, and PF_CAPACITY land in that pipeline's spreadsheet. networkx and criticalpath emit the initiative graph from recovered rows; pulp and ortools optimize mix under budget and capacity bounds compiled by pydantic.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 3 (Selection Proof).** z3-solver must accept mutual-exclusion and prerequisite constraints on the incumbent or no publication asset is materialized.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R22: Reverse Service Financial Management

- **Step 0 (Global Ingestion).** playwright, markitdown, undoc, firecrawl-anydoc, and python-calamine flatten the finance dashboard and any printed pack into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a temporalio workflow only if stanza recovers cost-pool, allocation, and charging predicates from the published copy. Missing ledger language yields a halt.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences)
- **Step 2 (Schema and Proof).** SFM_POOL, SFM_ALLOCATION, SFM_CHARGE, SFM_INVOICE, and SFM_UNIT_COST land in that pipeline's spreadsheet. zen-engine binds allocation tables from recovered rows; clingo must prove debit/credit/recovery consistency.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 3 (Quant and Select).** numpy-financial and statsmodels compute unit cost and variance only on the proved ledger; autoviz may select charts only from those tables and only inside the recovered grammar.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table)
  not located here: autoviz, numpy-financial
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R23: Reverse Risk Management

- **Step 0 (Global Ingestion).** python-docx and docling flatten the risk Word pack; playwright flattens plotly HTML into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 keeps pgmpy, networkx, and pymc assets only when threat, impact, and control spans resolve in that pipeline's spreadsheet. No appetite bound means no treatment flow.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination)
  not located here: pymc
- **Step 2 (Graph and Posterior).** RISK_ITEM, RISK_THREAT, RISK_CONTROL, RISK_IMPACT, RISK_APPETITE, and RISK_TREATMENT land in that pipeline's spreadsheet. pgmpy and networkx rebuild the risk net; pymc, numpyro, and arviz run only after typedlogic facts compile.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination)
  not located here: arviz, pymc
- **Step 3 (Treatment Proof).** ortools selects avoid/reduce/transfer/accept portfolios from recovered rows; z3-solver must accept residual-versus-appetite or the plan asset is not written.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R24: Reverse Service Continuity Management

- **Step 0 (Global Ingestion).** python-docx, firecrawl-anydoc, and markitdown flatten the continuity Word pack; mermaid HTML is lifted into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert)
  not located here: mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 admits continuity assets only when critical-service, RTO, and RPO fields type-check in that pipeline's spreadsheet. Missing RTO/RPO cancels the flow.
- **Step 2 (BIA Graph).** BCM_SERVICE, BCM_RTO, BCM_RPO, BCM_DEPENDENCY, and BCM_INVOCATION land in that pipeline's spreadsheet. networkx maps service-to-CI-to-site edges from Pipeline R13; pandas emits impact-over-time tables from the recovered instance.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
- **Step 3 (Invocation Proof).** typedlogic and clingo encode invocation and exclusive-use facts; simpy and most-queue replay recovery; pysmt must accept RTO/RPO on the declared graph.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); simpy 4.1.2 (simpy.Environment, Environment.run); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R25: Reverse Strategy Management

- **Step 0 (Global Ingestion).** quarto HTML, PDF, and docx packs are flattened by undoc, docling, markitdown, and python-docx into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a prefect flow whose task set exists only if driver, goal, and option spans resolve in that pipeline's spreadsheet. Empty option set halts publication.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Map and Option Proof).** STR_DRIVER, STR_GOAL, STR_OPTION, STR_CAPABILITY, and STR_INITIATIVE land in that pipeline's spreadsheet. networkx and se-lib emit capability maps; typedlogic records options; z3-solver must accept consistency against Pipeline R16 principles.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort)
  not located here: se-lib
- **Step 3 (Roadmap).** criticalpath sequences initiatives onto the Pipeline R21 graph only after the option proof.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R26: Reverse Information Security Management

- **Step 0 (Global Ingestion).** python-docx, pypdf, dasel, and docling flatten the ISMS Word pack; playwright flattens the control dashboard into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); pypdf 6.16.2 (pypdf.PdfReader, PdfReader.metadata); dasel 3.11.2 (dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a temporalio workflow gated on control-objective and classification spans recovered from the pack. No classification scheme, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Ontology and Policy).** ISM_ASSET, ISM_CLASSIFICATION, ISM_CONTROL, ISM_THREAT, and ISM_PERMISSION land in that pipeline's spreadsheet. owlready2 and rdflib hold the catalog; pycasbin and openfga are generated only for proved permissions.
  located: owlready2 0.51 (owlready2.get_ontology, owlready2.sync_reasoner); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
  not located here: openfga
- **Step 3 (Residual Proof).** pgmpy links assets, threats, and controls from recovered rows; z3-solver and clingo must accept no conflicting allow/deny and no unclassified critical asset.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R27: Reverse Availability Management

- **Step 0 (Global Ingestion).** playwright flattens availability dashboards; python-docx and csvkit flatten the availability Word pack and outage extracts into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 admits reliability, lifelines, and fmdtools assets only when an availability target and an outage series both type-check in that pipeline's spreadsheet. Otherwise the run stops.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit)
  not located here: fmdtools
- **Step 2 (Block and Fit).** AVAIL_TARGET, AVAIL_OUTAGE, AVAIL_BLOCK, and AVAIL_FIT land in that pipeline's spreadsheet. reliability rebuilds block diagrams from Pipeline R13 and R14 graphs; scipy rejects unphysical fits; pysmt must accept redundancy versus target.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); scipy 1.15.3 (optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R28: Reverse Capacity and Performance Management

- **Step 0 (Global Ingestion).** playwright flattens plotly HTML; undoc, python-calamine, csvkit, and python-docx flatten the capacity Word pack and utilization extracts into the compiler manifest.
  located: python-calamine 0.8.2 (CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 keeps prophet, darts, pmdarima, and most-queue assets only when a time column and a utilization field type-check in that pipeline's spreadsheet. No series, no forecast flow.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim)
  not located here: darts, pmdarima, prophet
- **Step 2 (Forecast and Queue).** CAP_SERIES, CAP_FORECAST, CAP_QUEUE, and CAP_SETTING land in that pipeline's spreadsheet. prophet, darts, and pmdarima emit demand paths from recovered series; python-control and most-queue model response; gekko optimizes settings under compiled cost bounds.
  located: most-queue 2.9 (most_queue.QsSim, most_queue.theory, most_queue.sim)
  not located here: darts, gekko, pmdarima, prophet, python-control
- **Step 3 (Cover Proof).** z3-solver must accept planned capacity versus forecast peak plus contingency or dashboard assets are not materialized.
  located: z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R29: Reverse Continual Improvement Management

- **Step 0 (Global Ingestion).** docling, markitdown, and python-docx flatten the CSI register quarto pack and great-tables HTML into the compiler manifest.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 builds a dagster asset graph from recovered idea, benefit, and constraint spans. Empty idea set cancels register assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Prioritize and Gate).** CSI_IDEA, CSI_BENEFIT, CSI_EFFORT, CSI_RISK, and CSI_STATUS land in that pipeline's spreadsheet. pandas holds the register; pulp ranks under benefit/effort/risk; networkx supplies dependencies; zen-engine and typedlogic must accept intake rules.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 3 (Execution Tracking).** spiffworkflow runs approved items as durable workflows and may emit change payloads into Pipeline R39 only after clingo accepts the mutation edge.
  located: SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R30: Reverse Measurement and Reporting Management

- **Step 0 (Global Ingestion).** playwright, firecrawl-anydoc, csvkit, docling, and markitdown flatten scorecard HTML, quarto packs, and metric extracts into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a prefect flow only if metric-definition and audience-view spans resolve in that pipeline's spreadsheet. Orphan KPI names with no formula halt publication.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Metric Proof).** KPI_DEFINITION, KPI_EXTRACT, and KPI_FIGURE land in that pipeline's spreadsheet. pydantic types metric objects from the recovered instance; clingo must prove every reported figure is derivable from a registered definition and a source extract.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 3 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R31: Reverse Service Level Management

- **Step 0 (Global Ingestion).** python-docx, undoc, and markitdown flatten SLA, OLA, and UC Word packs; playwright flattens attainment dashboards into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a temporalio workflow gated on commitment and measurement-method spans recovered from the pack. No commitment language, no agreement assets.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Agreement Proof).** SL_AGREEMENT, SL_COMMITMENT, SL_MEASURE, SL_CREDIT, and SL_ESCALATION land in that pipeline's spreadsheet. pydantic instantiates SLA/OLA/UC objects from recovered rows; zen-engine binds credit and escalation tables; pysmt must accept attainability against Pipelines R27 and R28.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Attainment).** the pipeline spreadsheet computes attainment from Pipeline R30 only after the SMT proof.
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R32: Reverse Monitoring and Event Management

- **Step 0 (Global Ingestion).** playwright, docling, and csvkit flatten the event dashboard HTML and catalog extracts into the compiler manifest.
  located: playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 keeps durable-rules, experta, and pydantic event assets only when event-type and severity spans resolve in that pipeline's spreadsheet. No catalog, no correlation flow.
  located: durable-rules 2.0.28 (lang.ruleset, lang.when_all, lang.post, lang.m); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
  not located here: experta
- **Step 2 (Correlate and Hand-off).** EV_TYPE, EV_SEVERITY, EV_RULE, and EV_RESPONSE land in that pipeline's spreadsheet. durable-rules or experta execute compiled Rete rules from recovered rows; pm4py maps event-to-incident/change/request edges; unified-planning sequences runbooks.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); durable-rules 2.0.28 (lang.ruleset, lang.when_all, lang.post, lang.m); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: experta
- **Step 3 (Coverage Proof).** clingo must accept that every critical event class has filter, correlation, and response paths or dashboard assets halt.
  located: clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R33: Reverse Incident Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc, csvkit, python-docx, and playwright flatten major-incident Word reports and live board HTML into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); csvkit 2.2.0 (csvstat.CSVStat, csvjson.CSVJSON)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a dagster asset graph only if category, impact, and urgency fields type-check in that pipeline's spreadsheet. Missing model set cancels routing assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Route and Localize).** INC_RECORD, INC_CATEGORY, INC_ROUTE, and INC_RESTORE land in that pipeline's spreadsheet. zen-engine applies compiled incident models to recovered rows; networkx walks Pipeline R13 to localize nodes; pm4py compares the live path to the model.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 3 (Restore Proof).** lifelines estimates remaining restore time; reliability flags major-incident risk; csv-diff may emit model-update payloads into Pipeline R29 only if exception rates breach compiled thresholds.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); lifelines 0.30.3 (lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit)
  not located here: csv-diff
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R34: Reverse Problem Management

- **Step 0 (Global Ingestion).** python-docx, undoc, and docling flatten known-error articles; playwright flattens mermaid and clingraph HTML into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: clingraph, mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a prefect flow gated on amrlib producing causal or error-hypothesis graphs from the published pack. No causal AMR, no workflow.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); amrlib 0.8.1 (amrlib.load_stog_model, Inference.parse_sents)
- **Step 2 (Cause and Known Error).** PRB_CLUSTER, PRB_HYPOTHESIS, PRB_CAUSE, PRB_KNOWN_ERROR, and PRB_SOLUTION land in that pipeline's spreadsheet. dowhy and pgmpy test structure against recovered rows; amr-logic-converter and pysmt formalize mechanisms; typedlogic records known-error facts only after the SMT proof.
  located: amr-logic-converter 0.11.3 (AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); dowhy 0.14 (dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect); pgmpy 1.1.2 (models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
- **Step 3 (Solution and Close).** unified-planning and ortools explore strategies; zen-engine may emit a change payload into Pipeline R39; z3-solver must accept closure evidence or the record stays open.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R35: Reverse Service Desk

- **Step 0 (Global Ingestion).** python-docx, docling, and markitdown flatten template packs; playwright flattens desk dashboards into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a temporalio workflow only if triage-guideline and channel spans resolve in that pipeline's spreadsheet. Empty guideline set yields a halt.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Triage and Pack).** SDESK_GUIDELINE, SDESK_CHANNEL, SDESK_ROUTE, and SDESK_CSAT land in that pipeline's spreadsheet. zen-engine and business-rules route to Pipelines R33, R34, or R36; jinja2 and stanza assemble messages only for compiled channel constraints.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); stanza 1.14.0 (stanza.Pipeline, stanza.download, Document.sentences); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render)
- **Step 3 (Feedback and Improve).** pandas stores confirmations and CSAT; statsmodels scores desk series; pulp may emit Pipeline R29 items if compiled thresholds fail.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R36: Reverse Service Request Management

- **Step 0 (Global Ingestion).** firecrawl-anydoc, python-docx, and playwright flatten fulfilment Word packs and request HTML into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 keeps spiffworkflow and pydantic request assets only when a matching model key or an ad-hoc flag type-checks in that pipeline's spreadsheet. Neither present, no fulfilment flow.
  located: SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model)
- **Step 2 (Model or Plan).** REQ_MODEL, REQ_ITEM, REQ_APPROVAL, and REQ_TASK land in that pipeline's spreadsheet. spiffworkflow executes matched models; unified-planning synthesizes ad-hoc plans; zen-engine writes approval tables as artifacts, not as a human gate.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
- **Step 3 (Replay).** pm4py compares executed paths to the model; pandas and pingouin score cycle time into Pipeline R29 only on deviation.
  located: pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: pingouin
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R37: Reverse Service Catalog Management

- **Step 0 (Global Ingestion).** playwright flattens streamlit and datasette catalog views; python-docx, undoc, and markitdown flatten Word catalog extracts into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); streamlit 1.63.0 (streamlit.dataframe, streamlit.plotly_chart, streamlit.write); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: datasette
- **Step 1 (Orchestrator Compilation).** Pipeline R0 builds a dagster asset graph from recovered granularity, view, and access-rule spans. No view definition cancels publication assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Model and View).** CAT_OFFERING, CAT_VIEW, CAT_ATTRIBUTE, and CAT_ACCESS land in that pipeline's spreadsheet. jinja2 and great-tables emit standard views; pycasbin binds access only after clingo accepts mandatory-attribute completeness.
  located: great-tables 0.24.0 (great_tables.GT, GT.save, GT.as_raw_html); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); Jinja2 3.1.6 (jinja2.Environment, Environment.get_template, Template.render)
- **Step 3 (Request Path).** zen-engine processes view requests and logs exceptions into the same store.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R38: Reverse Business Relationship Management

- **Step 0 (Global Ingestion).** python-docx and docling flatten relationship reviews; playwright flattens journey dashboards into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a prefect flow only if stakeholder-group and relationship-domain spans resolve in that pipeline's spreadsheet. Empty map cancels journey assets.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Health and Offer).** BRM_STAKEHOLDER, BRM_DOMAIN, BRM_VOC, BRM_OFFER, and BRM_JOURNEY land in that pipeline's spreadsheet. networkx rebuilds the RACI graph; pandas scores VoC; typedlogic records principles; zen-engine shapes offerings only under Pipeline R21 constraints that already proved.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
- **Step 3 (Journey).** pydantic stores terms; pm4py tracks onboard/co-create/review/offboard and refuses offboard without a compiled sustainment record.
  located: pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R39: Reverse Change Enablement

- **Step 0 (Global Ingestion).** python-docx, firecrawl-anydoc, and playwright flatten RFC Word packs and change-board HTML into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto)
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a temporalio workflow gated on change-type, risk, and success-criteria spans recovered from the pack. No model match and no risk span, no workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Assess and Authorize).** CHG_RECORD, CHG_TYPE, CHG_RISK, CHG_CRITERIA, CHG_WINDOW, and CHG_PLAN land in that pipeline's spreadsheet. pydantic creates the record from recovered rows; zen-engine applies compiled models; pycasbin and business-rules bind the authority matrix; clingo must accept freeze-window and exclusive-resource constraints. Authorization is the stable model written to the record.
  located: business-rules 1.1.1 (business_rules.run_all, business_rules.export_rule_data); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pycasbin 2.8.0 (casbin.Enforcer, Enforcer.enforce); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 3 (Plan and Replay).** criticalpath and unified-planning emit the plan; simpy dry-runs against Pipeline R13 state; pm4py and csv-diff refuse closure if executed path diverges without a compensation fact.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); criticalpath 0.1.5 (criticalpath.Node, Node.update_all); simpy 4.1.2 (simpy.Environment, Environment.run); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
  not located here: csv-diff
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R40: Reverse Project Management

- **Step 0 (Global Ingestion).** python-docx, undoc, and markitdown flatten PID and stage Word packs; quarto HTML/PDF and plotly HTML are flattened by docling and playwright into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); plotly 7.0.0 (graph_objects.Figure, io.write_html, express.bar); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 builds a dagster asset graph from recovered tolerance, deliverable, and exception-trigger spans. Missing tolerance set cancels control assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Gates and Schedule).** PJ_TOLERANCE, PJ_DELIVERABLE, PJ_STAGE, PJ_WORK_PACKAGE, and PJ_EXCEPTION land in that pipeline's spreadsheet. pydantic instantiates PID/stage/work-package schemas from recovered rows; zen-engine encodes initiate/project/stage/exception/closure graphs; criticalpath and ortools solve resource-feasible plans.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver)
- **Step 3 (Exception Proof).** typedlogic and z3-solver must accept that an exception plan restores tolerances given updated case numbers or the next-stage asset is not materialized.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R41: Reverse Software Development and Management

- **Step 0 (Global Ingestion).** python-docx and docling flatten design notes; mermaid and diagrams HTML are lifted by playwright and markitdown into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes prefect tasks only if backlog-item and architecture-constraint spans resolve in that pipeline's spreadsheet. Empty backlog cancels design assets.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Guide and Rank).** SDM_ITEM, SDM_CONSTRAINT, SDM_RANK, and SDM_NFR land in that pipeline's spreadsheet. typedlogic records SDM rules against Pipeline R16; pulp ranks tasks under value, risk, and networkx product edges.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pulp 3.3.2 (pulp.LpProblem, LpProblem.solve)
- **Step 3 (Design Proof).** z3-solver must accept design artifacts against non-functional bounds; python-sat encodes feature-model constraints where present; zen-engine may emit RFC payloads into Pipeline R39 only after that proof.
  located: zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); python-sat 1.9.dev15 (solvers.Solver, rc2.RC2); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R42: Reverse Service Validation and Testing

- **Step 0 (Global Ingestion).** python-docx, firecrawl-anydoc, and markitdown flatten test-plan Word packs; mermaid HTML is lifted into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert)
  not located here: mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 admits testing assets only when acceptance predicates and a model key type-check in that pipeline's spreadsheet. No predicate set, no plan flow.
- **Step 2 (Criteria Proof).** TEST_PREDICATE, TEST_MODEL, TEST_CASE, TEST_ENV, and TEST_RESULT land in that pipeline's spreadsheet. typedlogic records exit criteria from recovered rows; pysmt and model-checker must accept internal consistency and entailment of Pipeline R15 requirements.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); PySMT 0.9.6 (shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat)
  not located here: model-checker
- **Step 3 (Plan and Exception).** unified-planning and ortools emit the tailored plan; zen-engine classifies exceptions; clingo must accept that every failed exit criterion has a defect or exception record.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); ortools 9.15.6755 (cp_model.CpModel, CpSolver.Solve, pywraplp.Solver); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R43: Reverse Deployment Management

- **Step 0 (Global Ingestion).** python-docx, undoc, and markitdown flatten deployment reports; mermaid HTML is lifted into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a temporalio workflow gated on environment, success-criteria, and rollback spans plus a triggering Pipeline R39 change fact in that pipeline's spreadsheet. No change fact, no deploy workflow.
  located: temporalio 1.32.0 (workflow.defn, workflow.run, activity.defn, worker.Worker)
- **Step 2 (Readiness Proof).** DEP_ENV, DEP_COMPONENT, DEP_CRITERIA, DEP_ROLLBACK, and DEP_CHANGE_REF land in that pipeline's spreadsheet. pydantic describes pipeline elements; typedlogic encodes pre-deploy predicates; clingo, z3-solver, and csv-diff must accept component and environment readiness.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
  not located here: csv-diff
- **Step 3 (Review).** unified-planning emits the instance plan; pm4py mines logs against the model; pandas may emit Pipeline R29 items on recurring unsat.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R44: Reverse Release Management

- **Step 0 (Global Ingestion).** python-docx and docling flatten release reviews; mermaid HTML is lifted into the compiler manifest.
  located: python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all)
  not located here: mermaid
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes a prefect flow only if a release-model key and go/no-go language both resolve against Pipelines R39 and R43 facts in that pipeline's spreadsheet. Missing go-criteria cancels execution assets.
  located: prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy)
- **Step 2 (Select and Prove).** REL_MODEL, REL_COMPONENT, REL_GO_CRITERIA, and REL_SCHEDULE land in that pipeline's spreadsheet. zen-engine selects the model; criticalpath builds the schedule; typedlogic and z3-solver must accept procedure, component-verification, and readiness jointly.
  located: criticalpath 0.1.5 (criticalpath.Node, Node.update_all); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); z3-solver 5.1.0.0 (z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core)
- **Step 3 (Review).** pm4py and pandas compare logs and incidents to success criteria; reliability flags release-induced signatures into Pipeline R34.
  located: reliability 0.9.0 (Fitters.Fit_Weibull_2P, reliability.Reliability_testing); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv); pm4py 2.7.23.8 (obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R45: Reverse Organizational Change Management

- **Step 0 (Global Ingestion).** python-docx, firecrawl-anydoc, and undoc flatten communication packs; quarto HTML/PDF scorecards are flattened by docling and markitdown into the compiler manifest.
  located: firecrawl-anydoc 0.2.4 (anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document); python-docx 1.2.0 (docx.Document, Document.add_paragraph, Document.add_table, Document.save); markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 emits a dagster asset graph only if change-vision and impacted-role spans resolve in that pipeline's spreadsheet. Empty stakeholder set cancels communication assets.
  located: dagster 1.13.20 (dagster.asset, dagster.Definitions, dagster.materialize)
- **Step 2 (Ready and Plan).** OCM_VISION, OCM_ROLE, OCM_READINESS, OCM_MESSAGE, and OCM_WIN land in that pipeline's spreadsheet. networkx maps roles; pandas and pingouin score readiness; unified-planning and criticalpath emit the engagement sequence; zen-engine writes the proceed certificate only if feasibility constraints compile.
  located: unified-planning 1.3.0 (model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition); criticalpath 0.1.5 (criticalpath.Node, Node.update_all); zen-engine 2.0.2 (zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
  not located here: pingouin
- **Step 3 (Sustain Proof).** statsmodels tracks adoption; clingo must accept that every declared early-win has an evidence record or sustainment assets halt.
  located: statsmodels 0.15.0 (inter_rater.cohens_kappa, inter_rater.to_table); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)

#### Pipeline R46: Reverse Knowledge Management

- **Step 0 (Global Ingestion).** playwright, markitdown, undoc, and docling flatten the MkDocs site, quarto packs, and Word exports into the compiler manifest.
  located: markitdown 0.1.7 (markitdown.MarkItDown, MarkItDown.convert); playwright 1.62.0 (sync_api.sync_playwright, Page.content, Page.goto); docling 2.124.0 (document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all); undoc 0.9.0 (undoc.parse_file, undoc.parse_bytes, undoc.Undoc)
  not located here: quarto
- **Step 1 (Orchestrator Compilation).** Pipeline R0 writes prefect tasks for rdflib and networkx only if domain, owner, and demand spans exist in the census. No demand item, no routine flow.
  located: networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); prefect 3.8.4 (prefect.flow, prefect.task, Flow.serve, Flow.deploy); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 2 (Inventory Proof).** KM_DOMAIN, KM_OWNER, KM_ASSET, KM_DEMAND, and KM_GUIDELINE land in that pipeline's spreadsheet. networkx maps domains to owners; rdflib stores assets; typedlogic records guidelines; clingo must accept that every high-priority demand is fulfilled or queued after VALUE edits.
  located: typedlogic 0.2.4 (pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom); networkx 3.6.1 (networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort); clingo 5.8.2 (clingo.Control, Control.add, Control.ground, Control.solve); rdflib 7.6.0 (rdflib.Graph, Graph.parse, Graph.query)
- **Step 3 (Routines).** spiffworkflow executes capture/review/publish/retire; pydantic versions assets; ydata-profiling and pandas may emit Pipeline R29 items when freshness thresholds fail.
  located: ydata-profiling 4.18.4 (ydata_profiling.ProfileReport, ProfileReport.to_json); SpiffWorkflow 3.2.0 (BpmnParser.BpmnParser, workflow.BpmnWorkflow); pydantic 2.13.5 (pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model); pandas 2.3.3 (pandas.DataFrame, DataFrame.to_excel, pandas.read_csv)
- **Step 4 (Execution).** openpyxl, xlsxwriter, and pandas-xlsx-tables write one spreadsheet for this pipeline’s artifact from the recovered, solver-accepted fields.
  located: pandas-xlsx-tables 1.1.2 (pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df); XlsxWriter 3.2.9 (xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table); openpyxl 3.1.5 (openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table)


---

## Part 6. The catalog

One entry per library, from the resolution runs that produced this file. `located` lists the functions that resolved by import at the version shown; `not resolved` lists the paths tried that did not, kept so the record is complete. An entry marked `exercised` was run on the FOIA source or a fragment of it; `wired` means the repository's build calls it today. A license is stated only where it was read from the package record in the same session; otherwise it is not recorded here.

- **amr-logic-converter** 0.11.3 — located: AmrLogicConverter.convert, AmrLogicConverter.AmrLogicConverter — license: MIT
- **amrlib** 0.8.1 — located: amrlib.load_stog_model, Inference.parse_sents — parse model from GitHub release (SHA-256 ecaa2d9b6b17d6a86af54a784e9ed1dd1c879a23f79918aa68b53b4a3766cc26); tokenizer facebook/bart-base from huggingface.co, blocked here — license: MIT
- **autoviz** 0.1.905 — located: — — not resolved: autoviz.AutoViz_Class, AutoViz_Class.AutoViz — license: not recorded here
- **business-rules** 1.1.1 — located: business_rules.run_all, business_rules.export_rule_data — license: not recorded here
- **clingo** 5.8.2 — wired — located: clingo.Control, Control.add, Control.ground, Control.solve — license: MIT
- **clorm** 1.6.3 — wired — located: clorm.Predicate, clorm.FactBase, clingo.Control — license: MIT
- **conllu** 6.0.0 — exercised — located: conllu.parse, models.TokenList, models.Token — license: not recorded here
- **cpmpy** 1.0.0 — located: — — not resolved: cpmpy.Model, Model.solve — license: not recorded here
- **criticalpath** 0.1.5 — located: criticalpath.Node, Node.update_all — license: not recorded here
- **csvkit** 2.2.0 — located: csvstat.CSVStat, csvjson.CSVJSON — license: not recorded here
- **cvc5** 1.3.4 — located: cvc5.Solver, Solver.checkSat, Solver.getUnsatCore — license: not recorded here
- **dagster** 1.13.20 — located: dagster.asset, dagster.Definitions, dagster.materialize — license: not recorded here
- **dasel** 3.11.2 — exercised — located: dasel -i yaml '<selector>' < file, dasel -i json '<selector>' < file — Go binary from github.com/TomWright/dasel releases; SHA-256 5006ee3a4239ab6a3edb1bf5c932874d814f7c276117ca677352697a4f547799 — license: not recorded here
- **datamodel-code-generator** 0.76.1 — exercised — located: datamodel_code_generator.generate, datamodel_code_generator.InputFileType — license: not recorded here
- **dataprep** absent — located: — — not resolved: eda.create_report, eda.plot — license: not recorded here
- **dateparser** 1.4.2 — exercised — located: dateparser.parse, search.search_dates — license: BSD-3-Clause
- **docling** 2.124.0 — exercised — located: document_converter.DocumentConverter, DocumentConverter.convert, DocumentConverter.convert_all — license: not recorded here
- **docling-core** 2.93.0 — exercised — located: doc.DoclingDocument, DoclingDocument.iterate_items, doc.ListItem, doc.GroupItem, doc.ProvenanceItem, doc.TextItem — license: not recorded here
- **dowhy** 0.14 — located: dowhy.CausalModel, CausalModel.identify_effect, CausalModel.estimate_effect — license: not recorded here
- **duckdb** 1.5.5 — located: duckdb.connect, DuckDBPyConnection.execute — license: not recorded here
- **durable-rules** 2.0.28 — exercised — located: lang.ruleset, lang.when_all, lang.post, lang.m — license: not recorded here
- **experta** 1.9.4 — located: — — not resolved: experta.KnowledgeEngine, experta.Rule, experta.Fact, experta.DefFacts, KnowledgeEngine.run, KnowledgeEngine.declare — license: not recorded here
- **fastexcel** 0.21.0 — exercised — located: fastexcel.read_excel, ExcelReader.load_sheet, ExcelSheet.to_pandas — needs pyarrow — license: not recorded here
- **firecrawl-anydoc** 0.2.4 — located: anydoc.to_document, anydoc.to_markdown, anydoc.format_from_path, anydoc.Document — license: not recorded here
- **fmdtools** absent — located: — — not resolved: propagate.nominal, block.Block — license: not recorded here
- **great-tables** 0.24.0 — located: great_tables.GT, GT.save, GT.as_raw_html — license: not recorded here
- **highspy** 1.15.1 — located: — — not resolved: highspy.Highs, Highs.run — license: not recorded here
- **holidays** 0.103 — exercised — located: holidays.country_holidays, united_states.UnitedStates, holidays.US — license: not recorded here
- **html2text** 2025.4.15 — located: html2text.HTML2Text, HTML2Text.handle — license: not recorded here
- **Jinja2** 3.1.6 — exercised — located: jinja2.Environment, Environment.get_template, Template.render — license: not recorded here
- **kuzu** 0.11.3 — exercised — located: kuzu.Database, kuzu.Connection, Connection.execute — license: not recorded here
- **lifelines** 0.30.3 — located: lifelines.KaplanMeierFitter, lifelines.WeibullFitter, KaplanMeierFitter.fit — license: not recorded here
- **lxml** 6.1.3 — exercised — located: etree.parse, etree.fromstring, _Element.iter, _Element.xpath, _Element.sourceline — license: not recorded here
- **mammoth** 1.12.1 — located: mammoth.convert_to_html, mammoth.convert_to_markdown, mammoth.extract_raw_text — license: not recorded here
- **markdownify** 1.2.3 — located: markdownify.markdownify — license: not recorded here
- **markitdown** 0.1.7 — exercised — located: markitdown.MarkItDown, MarkItDown.convert — license: not recorded here
- **most-queue** 2.9 — located: most_queue.QsSim, most_queue.theory, most_queue.sim — license: not recorded here
- **networkx** 3.6.1 — wired — located: networkx.DiGraph, DiGraph.add_edge, networkx.transitive_reduction, networkx.lexicographical_topological_sort, networkx.find_cycle, networkx.is_directed_acyclic_graph — license: BSD
- **nltk** 3.10.3 — located: tokenize.sent_tokenize, tokenize.PunktSentenceTokenizer, logic.LogicParser, inference.Prover9 — license: not recorded here
- **numpy** 2.3.5 — exercised — located: numpy.busday_offset, numpy.busday_count, numpy.busdaycalendar, numpy.is_busday — license: not recorded here
- **office-oxide** 0.1.9 — located: office_oxide.to_markdown, office_oxide.to_html, office_oxide.extract_text, office_oxide.Document — license: not recorded here
- **openpyxl** 3.1.5 — exercised — located: openpyxl.Workbook, Workbook.save, Worksheet.append, table.Table — license: not recorded here
- **ortools** 9.15.6755 — located: cp_model.CpModel, CpSolver.Solve, pywraplp.Solver — license: not recorded here
- **owlready2** 0.51 — located: owlready2.get_ontology, owlready2.sync_reasoner — license: not recorded here
- **owlrl** 7.6.2 — located: owlrl.DeductiveClosure — license: not recorded here
- **pandas** 2.3.3 — located: pandas.DataFrame, DataFrame.to_excel, pandas.read_csv — license: not recorded here
- **pandas-xlsx-tables** 1.1.2 — exercised — located: pandas_xlsx_tables.df_to_xlsx_table, pandas_xlsx_tables.xlsx_table_to_df — license: not recorded here
- **pdfplumber** 0.11.10 — wired — located: pdfplumber.open, Page.extract_words, Page.chars — license: MIT
- **penman** 1.3.1 — located: penman.decode, penman.encode, penman.Graph — license: MIT
- **pgmpy** 1.1.2 — located: models.BayesianNetwork, models.DiscreteBayesianNetwork, inference.VariableElimination — license: not recorded here
- **playwright** 1.62.0 — located: sync_api.sync_playwright, Page.content, Page.goto — Chromium preinstalled at /opt/pw-browsers — license: not recorded here
- **plotly** 7.0.0 — located: graph_objects.Figure, io.write_html, express.bar — license: not recorded here
- **pm4py** 2.7.23.8 — exercised — located: obj.BPMN, BPMN.StartEvent, BPMN.Task, BPMN.EndEvent, BPMN.Flow, BPMN.add_node, BPMN.add_flow, pm4py.write_bpmn, pm4py.read_bpmn, pm4py.convert_to_petri_net, pm4py.discover_petri_net_inductive, pm4py.conformance_diagnostics_token_based_replay, pm4py.conformance_diagnostics_alignments, pm4py.fitness_alignments, pm4py.precision_alignments — write_bpmn(auto_layout=True) needs the graphviz dot binary; auto_layout=False does not — license: AGPL-3.0 (stated by the package on import)
- **predpatt** 1.0.1 — wired, exercised — located: predpatt.load_conllu, predpatt.PredPatt, predpatt.PredPattOpts, Predicate.format, Predicate.subj, Predicate.obj, Predicate.has_subj, Predicate.has_obj, PredPatt.pprint, rules.arg_resolve_relcl, rules.pred_resolve_relcl, rules.borrow_subj, ud.dep_v2 — license: BSD-3-Clause
- **prefect** 3.8.4 — exercised — located: prefect.flow, prefect.task, Flow.serve, Flow.deploy — license: not recorded here
- **pulp** 3.3.2 — located: pulp.LpProblem, LpProblem.solve — license: not recorded here
- **pycasbin** 2.8.0 — located: casbin.Enforcer, Enforcer.enforce — license: not recorded here
- **pydantic** 2.13.5 — wired — located: pydantic.BaseModel, BaseModel.model_validate, pydantic.create_model — license: MIT
- **PyMuPDF** 1.28.2 — located: pymupdf.open, Page.get_text, pymupdf.open, Page.get_text — not resolved: Document.metadata, Document.metadata — license: not recorded here
- **pypdf** 6.16.2 — located: pypdf.PdfReader, PdfReader.metadata — license: not recorded here
- **pypdfium2** 5.13.0 — located: pypdfium2.PdfDocument, PdfPage.get_textpage, PdfTextPage.get_text_range — license: not recorded here
- **PySMT** 0.9.6 — located: shortcuts.Solver, shortcuts.get_unsat_core, shortcuts.is_sat — license: not recorded here
- **python-calamine** 0.8.2 — exercised — located: CalamineWorkbook.from_path, CalamineWorkbook.get_sheet_by_index, CalamineSheet.to_python — license: not recorded here
- **python-constraint2** 2.7.3 — located: constraint.Problem, Problem.getSolutions — license: not recorded here
- **python-docx** 1.2.0 — exercised — located: docx.Document, Document.add_paragraph, Document.add_table, Document.save — license: not recorded here
- **python-pptx** 1.0.2 — located: pptx.Presentation, Presentation.slides, Slide.shapes, Slide.notes_slide — license: not recorded here
- **python-sat** 1.9.dev15 — located: solvers.Solver, rc2.RC2 — license: not recorded here
- **PyYAML** 6.0.2 — wired — located: yaml.safe_load — license: not recorded here
- **rdflib** 7.6.0 — located: rdflib.Graph, Graph.parse, Graph.query — license: not recorded here
- **reliability** 0.9.0 — located: Fitters.Fit_Weibull_2P, reliability.Reliability_testing — license: not recorded here
- **scipy** 1.15.3 — located: optimize.minimize, stats.weibull_min, stats.chi2_contingency, optimize.linprog — license: not recorded here
- **simpn** 1.10.0 — located: simulator.SimProblem, SimProblem.simulate — license: not recorded here
- **simpy** 4.1.2 — located: simpy.Environment, Environment.run — license: not recorded here
- **snakes** 0.9.33 — located: nets.PetriNet, PetriNet.add_place — license: not recorded here
- **spacy** 3.8.16 — exercised — located: spacy.blank, Language.add_pipe, pipeline.Sentencizer, Doc.ents, Span.start_char, Doc.sents — license: not recorded here
- **SpiffWorkflow** 3.2.0 — located: BpmnParser.BpmnParser, workflow.BpmnWorkflow — license: not recorded here
- **stanza** 1.14.0 — located: stanza.Pipeline, stanza.download, Document.sentences — models fetched from huggingface.co, blocked in the build environment — license: not recorded here
- **statsmodels** 0.15.0 — exercised — located: inter_rater.cohens_kappa, inter_rater.to_table — license: not recorded here
- **streamlit** 1.63.0 — located: streamlit.dataframe, streamlit.plotly_chart, streamlit.write — license: not recorded here
- **structurizr-python** 0.6.0 — located: — — not resolved: structurizr.Workspace, Model.add_software_system — license: not recorded here
- **sweetviz** 2.3.3 — exercised — located: sweetviz.analyze, DataframeReport.show_html — license: not recorded here
- **temporalio** 1.32.0 — located: workflow.defn, workflow.run, activity.defn, worker.Worker, Worker.run, Client.connect — license: not recorded here
- **timexy** 0.1.3 — exercised — located: nlp.add_pipe('timexy') (spaCy factory 'timexy') — no model download; runs on spacy.blank('en') — license: MIT
- **typedlogic** 0.2.4 — exercised — located: pybridge.FactMixin, datamodel.Theory, datamodel.Term, decorators.axiom, registry.get_solver, Solver.add, Solver.add_fact, Solver.model, Solver.check, clingo_solver.ClingoSolver, z3_solver.Z3Solver, python_parser.PythonParser — not resolved: Solver.add_facts — license: MIT
- **ufal.udpipe** 1.4.0.1 — wired — located: Model.load, udpipe.Pipeline, Pipeline.process, udpipe.ProcessingError — license: MPL-2.0 (models CC BY-NC-SA 4.0)
- **undoc** 0.9.0 — located: undoc.parse_file, undoc.parse_bytes, undoc.Undoc — license: not recorded here
- **unified-planning** 1.3.0 — exercised — located: model.Problem, model.Fluent, model.InstantaneousAction, InstantaneousAction.add_precondition, InstantaneousAction.add_effect, shortcuts.OneshotPlanner, plans.PartialOrderPlan, SequentialPlan.convert_to, plans.PlanKind — needs an engine package; up-pyperplan installed — license: not recorded here
- **up-pyperplan** 1.1.0 — exercised — located: shortcuts.OneshotPlanner — license: not recorded here
- **XlsxWriter** 3.2.9 — exercised — located: xlsxwriter.Workbook, Workbook.add_worksheet, Worksheet.write_row, Worksheet.add_table — license: not recorded here
- **ydata-profiling** 4.18.4 — exercised — located: ydata_profiling.ProfileReport, ProfileReport.to_json — needs setuptools<80 (pkg_resources) and numpy<2.4 (numba) — license: not recorded here
- **z3-solver** 5.1.0.0 — wired — located: z3.Solver, Solver.assert_and_track, Solver.check, Solver.unsat_core, z3.set_param, z3.Int — license: MIT
- **zen-engine** 2.0.2 — exercised — located: zen.ZenEngine, ZenEngine.create_decision, ZenDecision.evaluate, ZenEngine.evaluate — license: not recorded here

Not located, with the reason verbatim:

- **graphable** — graphable 0.7.0 requires Python >= 3.13; the environment is Python 3.11.15
- **dataprep** — install unsatisfiable: dataprep 0.4.5 depends on python-crfsuite 0.9.8, which cannot be built here
- **fmdtools** — install unsatisfiable: fmdtools 2.3.3 depends on pandas[all], which depends on psycopg2, which cannot be built here
- **experta** — experta 1.9.4 installs; `import experta` fails on Python 3.11: AttributeError: module 'collections' has no attribute 'Mapping'
- **coreferee** — coreferee 1.4.1 pins spaCy 3.5, whose wheels raise `numpy.dtype size changed, may indicate binary incompatibility` under numpy 2 here; uninstalled
- **cpmpy** — cpmpy 1.0.0 imports highspy; highspy 1.15.1's compiled extension fails to import (undefined symbol)
- **highspy** — highspy 1.15.1's compiled extension fails to import (undefined symbol)
- **autoviz** — autoviz 0.1.905 imports IPython, which is not installed
- **structurizr-python** — structurizr-python 0.6.0 imports `pydantic.types:StrBytes`, removed in pydantic v2
- **sutime** — not installed: needs Java and Stanford CoreNLP; GPL-3.0-or-later
- **py-heideltime** — not installed: needs Java and TreeTagger

Python 3.11.15 standard library, `wired`: hashlib.sha256, json.dumps, unicodedata.normalize, html.parser.HTMLParser.getpos, csv.writer, importlib.util.spec_from_file_location, importlib.util.module_from_spec.

---

## Part 7. Verification

- `tests/test_function_chain.py` reads this file, collects every `locate:` line, and resolves each dotted path by import against the installed packages. A path whose top-level package is installed must resolve, or the test fails. A path whose package is not installed is reported by name and skipped, so the test states what it did not check.
- The chain's libraries and their exact versions are the `chain` extra of `pyproject.toml`, generated from the installed packages when this file was written: `uv pip install -e ".[dev,chain]"`.
- The build, the double build, and the digest: `compiled-ai compile packs/foia`, `python -m pytest`, `compiled-ai verify packs/foia`.
