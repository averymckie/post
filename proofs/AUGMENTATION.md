# Function Chain augmentation

Zero LLM reasoning intervention between functions or chains is a runtime requirement. LLM reasoning belongs in upstream ideation. The runtime executes fixed functions, explicit data contracts, and defined handoffs.

This pass starts with usability and presentation of the existing deliverables. It adds five focused interfaces and a combined workbench, then extends the same outputs into checked print documents. All interface copy uses US English. Source quotations retain their original wording.

## Delivered chains

| Proof | Deliverable | Functions and checks |
| --- | --- | --- |
| P65 | Policy explorer | Zen and DMN evaluation agree with all 19 stored truth-table rows; eight recorded meetings remain intact. |
| P66 | Process explorer | NetworkX topological layers arrange 42 nodes and 21 edges across two processes; IDs, endpoints, labels, and cited text remain intact. |
| P67 | Searchable workbook views | openpyxl reads 370 rows; fixed JavaScript handlers search, sort, and paginate the original values. |
| P68 | Reading view | python-docx reads 27 ordered paragraph/table blocks from two documents; headings and navigation improve reading. |
| P69 | Discussion map | python-pptx reads eight text shapes and two explicitly attached connectors; SVG and a transcript preserve the source content. |
| P70 | Combined workbench | Jinja2 assembles the five views into one standalone HTML file with inline assets. |
| P71 | Execution evidence | Registered input hashes, typed readback, package versions, and model/network boundary results are recorded. |
| P72 | Interaction evidence | jsdom runs 824 assertions without external resources; DOM snapshots carry hashes. |
| P73 | Print documents | WeasyPrint renders nine states across 15 pages; all 183 document/table text blocks checked survive PDF extraction. Embedded font timestamps are canonicalized. |
| P74 | Operations model | Nine independently read workbooks and one registered policy produce 1,434 exact case joins; all 105 stored open-case risk decisions agree with Zen. |
| P75 | Operations desk | Fixed handlers expose case filters, source details, JSON exports, 116 ordered activity paths, and 385 connections; 5,273 offline DOM assertions passed. Inline SVG IDs and references have a separate scope per chart. |
| P76 | Performance atlas | Plotly specifications feed Matplotlib PNG/SVG charts and a standalone Plotly atlas; 55 numeric marks and 36 missing cells are preserved. |
| P77 | Case briefs | Three one-page briefs preserve flagged, unflagged, and unassessed cases; 62 printed values and each case's original fields were checked. |
| P78 | Operations print collection | Ten checked interface states become ten numbered pages; 288 printed values survive extraction, including connection filter context. |
| P79 | Deliverable collection | A searchable entry page links 16 deliverables and 19 distinct registered files; 142 DOM assertions check filters, keyboard controls, and links. The complete augmentation workflow uses fixed handoffs. |

Open `proofs/out/augmentation/workbench.html` after downloading it. The HTML views require JavaScript. They contain no external scripts, stylesheets, fonts, or service calls. The browser content security policy disables connections.

The policy example uses the recorded 18-member roster and the stored historical attendance counts. It does not establish the actual roster at each historical meeting. Process arrows retain the previously recorded forced-precedence model. Activity measures describe gaps since prior events. These presentation chains preserve the existing source semantics.

## Reproduce the presentation pass

Use Python 3.12 and Node.js 24. The full function catalog and the presentation runner have separate environments so their exact package pins can coexist.

```bash
uv venv .venv-presentation --python 3.12
uv pip install --python .venv-presentation/bin/python -r proofs/requirements-augmentation.txt
npm ci
.venv-presentation/bin/python -m proofs.augment
node tests/test_augmentation_ui.mjs
.venv-presentation/bin/python -m proofs.presentation_pdf
.venv-presentation/bin/python -m pytest tests/test_augmentation.py
```

WeasyPrint also needs the native font and text libraries described in its [installation documentation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html). The supplied PDFs and HTML files can be reviewed without installing Python.

After a successful run, append the resulting evidence:

```bash
.venv-presentation/bin/python -m proofs.augment --record
.venv-presentation/bin/python -m proofs.record_presentation_checks
```

Changed presentation output hashes are appended as amendments before the register advances. Existing core evidence is preserved. Repeating the same checked pass should append nothing.

## Full declared toolchain

`uv.lock` resolves 422 distributions across its supported markers. The tested Linux environment installed 415 distributions, including all 80 declared `chain` extras. The inventory is in `proofs/out/augmentation/toolchain.json`.

```bash
CC=gcc CXX=g++ AR=ar RANLIB=ranlib LDSHARED='gcc -shared' UV_PROJECT_ENVIRONMENT=.venv-full uv sync --all-extras --locked
.venv-full/bin/python -m pytest --ignore=tests/test_function_chain.py
```

The GCC environment settings were needed because this runtime's Python configuration referenced unavailable LLVM tools. The package metadata now allows the repository's existing pinned PredPatt Git reference, includes the three previously undeclared imports used by the proof runner, and uses PyYAML 6.0.3 to resolve the declared profiling dependency. The repository's existing NetworkX override for the unused `concrete` dependency remains explicit.

Installation is distinct from a successful callable test. Optional packages can still require native binaries, external services, or additional input/model assets. No optional model package is used by the new presentation execution path.

## Validation and limits

The core and augmentation suite passed 19 tests. The separate interface tests passed 824 assertions, and the print checks passed 183 text-block comparisons. HTML generation was compared across independent processes and hash seeds. The nine print samples were rendered and visually reviewed. Details are in the JSON evidence files.

Browser layout and responsive behavior remain unverified: the supported preview service was unavailable, and browser policy rejected local-file access. jsdom checks behavior without performing browser layout or paint. WeasyPrint checks print rendering.

The optional function-catalog test was blocked by automatic approval review when a dependency attempted to contact a Microsoft telemetry endpoint. That test is not recorded as passed. The original P1-P64 runner also could not complete in this runtime because PM4Py inspected an unavailable parent process through psutil. Original registered outputs were used as inputs to this presentation pass; all 13 selected inputs matched their registered hashes.

An inventory check found one pre-existing mismatch among the 240 original register entries: `proofs/out/P17/all/digests.json`. Its bytes match the base commit, but its stored register digest differs. This pass preserves that file and does not silently repair the historical record.

## Continuing from this pass

Advance the interface work through browser verification when the supported environment is available, then extend native deliverable presentation and additional visual capabilities. Each proposal should identify its actual input, named functions, output contract, preservation check, and runtime requirements before implementation.

| Next candidate | Open-source function match | Required check before claiming a proof |
| --- | --- | --- |
| Richer offline activity charts | [Plotly `to_html` / `write_html`](https://plotly.com/python/interactive-html-export/) with an inline bundle and fixed IDs | Recover plotted values and labels; verify no external assets; test controls in an authorized browser. |
| Denser process diagrams | [Graphviz `dot`](https://graphviz.org/docs/layouts/dot/) for layered directed graphs | Install and pin the native executable; preserve every node and edge; verify readable labels. |
| Better print layouts for more outputs | [WeasyPrint `HTML.write_pdf`](https://doc.courtbouillon.org/weasyprint/stable/api_reference.html) | Compare extracted content, check pagination, render pages, and record deterministic packaging. |
| Workbook presentation | XlsxWriter formatting, filters, frozen panes, and charts | Preserve values/formulas and compare workbook readback before registering styled copies. |
| More policy interfaces | Existing Zen/DMN evaluators, typed forms, and explicit truth tables | Define each complete input domain or test partition; preserve rule provenance and invalid-input behavior. |

These are candidates for subsequent passes. They do not authorize LLM reasoning at runtime or imply that unexecuted functions have been proven.

## Operations checkpoint P76

Open `proofs/out/augmentation/operations.html` for the new operations desk. Its four views provide an overview, case exploration, activity paths, and connections. The record panel preserves full timestamps, the original calendar calculation, and the exact stored risk decision. JSON exports contain the filtered records and their source hashes. Export bytes passed offline tests; the browser file dialog remains unverified.

The data describes a historical receipt-phase log whose last event is January 23, 2012. The 94 flagged and 11 unflagged records are the 105 open cases assessed by the stored department-mean rule. Closed cases remain unassessed. These flags do not predict current outcomes or establish statutory deadlines. Source calendar values remain labeled as the original Netherlands working-day calculation.

`performance-atlas.html` includes Plotly locally for pan/zoom/hover support when opened in a browser. The same figure specifications generate the three reviewed PNG/SVG charts used in the operations desk. The specification and static rendering checks passed; Plotly browser rendering has not been verified in this environment.

```bash
.venv-presentation/bin/python -m proofs.operations
node tests/test_operations_ui.mjs
.venv-presentation/bin/python -m pytest tests/test_operations.py
PROOFS_AMEND_REASON='Record completed operations checkpoint' .venv-presentation/bin/python -m proofs.record_operations
```

Eleven operations tests cover independent-process reproducibility, complete source preservation, repeated activities, null/zero chart semantics, invalid joins, UTC normalization, and scoped SVG identifiers/references. Each of the ten selected original files matched its registered digest. All source reads, joins, policy evaluation, and rendering occurred under the model/network guard; native plotting initialization occurs before that guard.

The function matches were checked against the primary [Plotly HTML export documentation](https://plotly.com/python/interactive-html-export/), [Plotly heatmap documentation](https://plotly.com/python/heatmaps/), and [Matplotlib savefig reference](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html). Exact locally executed versions are Plotly 7.0.0, Matplotlib 3.10.8, and NumPy 2.3.5. Pins are included in `proofs/requirements-augmentation.txt`.

Checkpoints are cumulative and immutable once shared. Each contains three packages with disjoint file paths and one complete bundle. Continue development separately from the shared snapshot; finish all three package uploads from the same checkpoint before reviewing or running them together.

## Complete workflow through P79

Open `proofs/out/augmentation/index.html` to browse the collection. The gallery needs its neighboring deliverable files for links; its styles, controls, and thumbnails are embedded. The delivery bundle includes the complete collection in `preview`.

After installing the pinned Python dependencies and running `npm ci`, reproduce all augmentation chains, behavior checks, print checks, and evidence registration with one command:

```bash
.venv-presentation/bin/python -m proofs.run_augmentation
```

The coordinator executes a fixed list of 14 worker commands and stops on the first failure. It blocks model-client imports and network calls and permits only its named worker subprocesses. Transformation and rendering workers retain their own stricter boundaries. There is no LLM reasoning step between functions, proofs, checks, or registrations. Dependency installation and upstream design work precede this runtime sequence.

The workflow runs 19 presentation and operations tests and 6,239 offline DOM assertions across the workbench, operations desk, and collection. The new brief and operations print chains check 350 text values over 13 pages. The previous presentation print checks remain separate in their own report. `workflow-verification.json` binds the run to the hashes of all nine evidence reports.

The case briefs use explicit field mappings and retain complete typed records in `case-briefs.json`. The print collection keeps the chosen connection filters visible and labels handover weights separately from directly-follows counts. The dense heatmap receives a full-page chart layout. Checked embedded PNG data is decoded locally; external resource fetching stays forbidden.

The P79 pass corrected reused SVG element IDs and singular/plural activity-path labels. The changes are recorded as amendments and a P75 chain revision. The frozen P76 download remains unchanged.

The next useful pass is native workbook presentation: styled copies with filters, frozen headers, meaningful number formats, and original-value readback. This candidate remains unexecuted. Browser verification remains an open check in an authorized environment.
