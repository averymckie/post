# Handoff hardening guards

Runnable local guard modules embedded in `../Proofs.txt` (hardening batches P1-P10 … P141-P150, P151-P160, P161-P170, P171-P180, P181-P190, P191-P200) together with their evidence files. Each module's SHA256 and byte count are recorded in `Proofs.txt` next to its embedded copy; each evidence file records the `source_sha256` of the module that produced it and, from v2 on, the `dependency_sha256` of the modules it imports.

## Files

| file | role |
| --- | --- |
| `handoff_guards_v1.py` | batch P1-P10 (SHA256 `2b3138b6…`) |
| `handoff_guards_v2.py` | batch P11-P20 (SHA256 `0a406d0e…`), imports v1 |
| `handoff_guards_v3.py` | batch P21-P30 plus the glue register (SHA256 `e8df8d98…`), imports v1 and v2 |
| `handoff_guards_v4.py` | batch P31-P40 (SHA256 `90029a69…`), imports v1 and v3 |
| `handoff_guards_v5.py` | batch P41-P50 (SHA256 `611cd01d…`), imports v1, v3 and v4 |
| `handoff_guards_v6.py` | batch P51-P60 (SHA256 `7dc3e6c5…`), imports v1, v3 and v5 |
| `handoff_guards_v7.py` | batch P61-P70 (SHA256 `cfc7c9a9…`), imports v1 and v3 |
| `handoff_guards_v8.py` | batch P71-P80 (SHA256 `9809d9d6…`), imports v1 and v3; DOM cases need node + jsdom |
| `handoff_guards_v9.py` | batch P81-P90 (SHA256 `c387cba5…`), imports v1 and v8 |
| `handoff_guards_v10.py` | batch P91-P100 (SHA256 `5881051f…`), imports v1 and v8 |
| `handoff_guards_v11.py` | batch P101-P110 (SHA256 `ee1e425d…`), imports v1, v6 and v8 |
| `handoff_guards_v12.py` | batch P111-P120 (SHA256 `0bc7d97c…`), imports v1, v6 and v8 |
| `handoff_guards_v13.py` | batch P121-P130 (SHA256 `63960f02…`), imports v1, v6, v8 and v12 |
| `handoff_guards_v14.py` | batch P131-P140 (SHA256 `0c617018…`), imports v1, v6, v8 and v12 |
| `handoff_guards_v15.py` | batch P141-P150 (SHA256 `a6515cdb…`), imports v1; runs pytest in a temporary directory |
| `handoff_guards_v16.py` | batch P151-P160 (SHA256 `f4d9a482…`), imports v1; renders DOCX templates and loads a Beancount journal in memory |
| `handoff_guards_v17.py` | batch P161-P170 (SHA256 `5a8a0eef…`), imports v1; pandera constraints, rapidfuzz lookup and the two researched largest-remainder libraries |
| `handoff_guards_v18.py` | glue elimination for v15-v17 (SHA256 `c5bddd02…`), imports v1; replaces 17 handwritten functions with portion, pandera, scipy, pandas, repro-zipfile, largest-remainder and rapidfuzz primitives |
| `handoff_guards_v19.py` | batch P171-P180 (SHA256 `aeddd95c…`), imports v1; numpy business-day calendar, pandas Interval closures, pandera constraints, largest-remainder split, numpy-financial |
| `handoff_guards_v20.py` | batch P181-P190 (SHA256 `0a44fac2…`), imports v1; dateutil.rrule, Pint exact rationals, merge_asof, NetworkX arborescence, DuckDB DECIMAL, python-pptx connectors |
| `handoff_guards_v21.py` | batch P191-P200 (SHA256 `0a9f91bd…`), imports v1; executes the named theoretical tests with Lark, Pydantic, Clingo, Z3, pySHACL/rdflib, NetworkX |
| `guards-v1.json`, `guards-v2.json` | evidence recorded with the earlier batches |
| `rerun-v1.json`, `rerun-v2.json` | the same modules re-executed in the batch-3 environment |
| `guards-v3.json` … `guards-v15.json` | batch-3 through batch-15 evidence |
| `requirements-hardening.txt` | exact package versions of the batch-3 environment (`uv pip freeze`) |

## Run

```
python3.11 -m venv venv && ./venv/bin/pip install -r requirements-hardening.txt
./venv/bin/python handoff_guards_v1.py --report guards-v1.json
./venv/bin/python handoff_guards_v2.py --report guards-v2.json
NLTK_DATA=/path/to/nltk_data ./venv/bin/python handoff_guards_v3.py --report guards-v3.json
./venv/bin/python handoff_guards_v4.py --report guards-v4.json
./venv/bin/python handoff_guards_v5.py --report guards-v5.json
./venv/bin/python handoff_guards_v6.py --report guards-v6.json
./venv/bin/python handoff_guards_v7.py --report guards-v7.json
npm install jsdom && ./venv/bin/python handoff_guards_v8.py --report guards-v8.json --jsdom-dir .
./venv/bin/python handoff_guards_v9.py --report guards-v9.json --jsdom-dir .
./venv/bin/python handoff_guards_v10.py --report guards-v10.json --jsdom-dir .
./venv/bin/python handoff_guards_v11.py --report guards-v11.json --jsdom-dir .
./venv/bin/python handoff_guards_v12.py --report guards-v12.json
./venv/bin/python handoff_guards_v13.py --report guards-v13.json
./venv/bin/python handoff_guards_v14.py --report guards-v14.json
./venv/bin/python handoff_guards_v15.py --report guards-v15.json
./venv/bin/python handoff_guards_v16.py --report guards-v16.json
./venv/bin/python handoff_guards_v17.py --report guards-v17.json
./venv/bin/python handoff_guards_v18.py --report guards-v18.json
./venv/bin/python handoff_guards_v19.py --report guards-v19.json
./venv/bin/python handoff_guards_v20.py --report guards-v20.json
./venv/bin/python handoff_guards_v21.py --report guards-v21.json
```

Case 26 of v3 uses the WordNet 3.0 corpus when `NLTK_DATA` points at a directory holding `corpora/wordnet.zip` (SHA256 `cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59`, 10775600 bytes, obtained once with `nltk.download('wordnet', download_dir=...)`). Without it the case still passes and records `not installed; no lexical expansion executed`. The guard runs themselves make no network call.

Cross-runtime oracle for recurrence: `rrule_oracle.php` expands an RRULE with php-rrule (https://github.com/rlanvin/php-rrule, commit 93a083db12dcb6f58e4840392a22e158ce96f1ff, cloned to /home/user/rlanvin/php-rrule) under PHP 8.4.19. php-rrule documents itself as having started as a port of python-dateutil, so its agreement corroborates the dateutil lineage in a second runtime rather than an independent reading of RFC 5545; the tests say so. The three recurrence tests in `test_library_defaults.py` skip cleanly when php or the checkout is absent.

Cross-runtime oracles for month arithmetic: `month_offset_oracle.rb` shifts a date by whole months with Ruby's `Date#>>` under ruby 3.3.6, and `month_offset_oracle.php` applies one relative modifier with `DateTime::modify` under PHP 8.4.19. Both are C implementations in their own standard libraries, unrelated to python-dateutil. Ruby's behaviour was read in `ext/date/date_core.c` at tag `v3_3_6`; PHP's was read in a clone of https://github.com/php/doc-en at commit `d8de774ae203bccf3ffe02895d8c8fc754377451` (`reference/datetime/datetime/modify.xml` and `reference/datetime/formats.xml`). Each shim parses argv, calls the library and prints one ISO date; every value compared on the Python side comes from `subprocess` output. The same two shims answer the later tests that compose and reverse an offset, which call them two, three or four times per example and therefore run under a smaller `hypothesis` settings profile than the rest of the file. The eleven month-arithmetic tests that call a shim skip cleanly when the runtime is absent; the two that do not compare pandas with dateutil inside Python.

Cross-runtime oracle for template rendering: `template_render_oracle.js` renders one template with nunjucks 3.2.4 under its own default settings and then with `autoescape` off, and `template_strict_oracle.js` renders it with `throwOnUndefined` set and exits non-zero when nunjucks refuses. nunjucks is a JavaScript implementation of the same template language; its `package.json` at tag `v3.2.4` lists `a-sync-waterfall`, `asap` and `commander` and nothing from Python, and its `docs/api.md` at that tag documents "**autoescape** *(default: true)*" and "**throwOnUndefined** *(default: false)*". Install it outside this repository and point the tests at it: `npm install --prefix ~/nunjucks-oracle nunjucks`, or set `NUNJUCKS_DIR` to another prefix; the five template tests skip cleanly when node or the checkout is absent. Each shim parses argv (the template, and the context as JSON), calls the library and prints one line per environment.

Cross-runtime oracles for case folding: `case_fold_oracle.rb` prints Ruby 3.3.6's `String#downcase(:fold)` and `String#downcase` of one string, and `case_fold_oracle.php` prints PHP 8.4.19's `mb_convert_case(..., MB_CASE_FOLD, 'UTF-8')` and `mb_strtolower(..., 'UTF-8')`. Each prints two lines and the Python side splits on the newline; neither does arithmetic or branches on a value. The Ruby shim tags its argument as UTF-8 and sets its output stream to UTF-8, because without that Ruby takes both from the locale and folds nothing outside ASCII when the reader's locale is unset -- a defect found while writing these tests, not a property of the library. Ruby's behaviour was read in `doc/case_mapping.rdoc` at tag `v3_3_6`, PHP's in the doc-en clone (`reference/mbstring/functions/mb-convert-case.xml`), and CPython's in `Doc/library/stdtypes.rst` at tag `v3.11.15`. The five case tests that call a shim skip cleanly when a runtime is absent; two more compare the standard library with the `regex` module's own Unicode tables inside Python.

Second implementation for the Beancount journal format: `beancount-parser-lima` 0.6.0, a Rust parser installed as a wheel and imported directly, so there is no shim. Its own README at tag `0.6.0` calls it "A zero-copy parser for Beancount in Rust" that "is intended to be a complete implementation of the Beancount file format"; its `Cargo.toml` at that tag depends on chumsky, logos, rust_decimal, time and pyo3 and on nothing from the Python `beancount` package, which `uv pip show` confirms with an empty `Requires:`. It parses and does not book, which is what makes it useful here: the five balance-assertion tests in `test_library_defaults.py` use it to establish that two spellings of one amount are the same number in the file, so that beancount's differing verdicts come from its inferred tolerance and not from the text.

Cross-runtime oracle for reference resolution: `url_resolve_oracle.js` resolves one reference against one base with the WHATWG `URL` parser under node v22.22.2 and prints the result. It is a different specification from the RFC 3986 resolution the standard library's `urljoin` implements, which is why the four resolution tests compare three implementations: `urljoin`, `rfc3986` 2.0.0 (whose `setup.cfg` at tag `2.0.0` declares no `install_requires`), and this shim. The shim parses argv, calls the parser and prints; the tests skip cleanly when node is absent.

Cross-runtime oracles for ISO 8601 timestamps: `iso_stamp_oracle.rb` parses one timestamp with Ruby 3.3.6's `Time.iso8601` and prints the wall clock, `usec`, `nsec` and `utc_offset`; `iso_stamp_oracle.php` parses the same text with PHP 8.4.19's `DateTimeImmutable` and prints the wall clock, the microseconds, `getOffset()` and the offset as that runtime writes it. Each shim parses argv, calls the library and prints; neither branches on a value, and a refusal is an uncaught exception, so it reaches the tests as a non-zero exit and is asserted with `pytest.raises(subprocess.CalledProcessError)`. Ruby's method is `alias iso8601 xmlschema` in `lib/time.rb` at tag `v3_3_6`, documented there as parsing "a dateTime defined by the XML Schema", "a restricted version of the format defined by ISO 8601"; PHP's accepted notations are in the doc-en clone at `reference/datetime/formats.xml` (the "ISO8601 Notations" and "Time Formats" tables, whose `tzcorrection` grammar is `"GMT"? [+-] hh ":"? MM?`); CPython's `datetime.fromisoformat` is documented in `Doc/library/datetime.rst` at tag `v3.11.15`. The six timestamp tests skip cleanly when either runtime is absent.

Second implementation for PDF text search and annotations: `pypdfium2` 5.13.0, which binds PDFium (libpdfium 153.0.7999.0 here) and is imported directly, so there is no shim. Its published metadata at tag `5.13.0` declares no runtime dependencies at all: `pyproject.toml` holds a build-system table and PEP 735 dependency groups and no `[project]` table, and the `[metadata]` section of `setup.cfg` declares none, which is what establishes that it does not wrap MuPDF. `PdfTextPage.search` and `PdfTextPage.get_text_bounded` were read in `src/pypdfium2/_helpers/textpage.py` at that tag; PyMuPDF's `Page.search_for` and `Page.get_textbox` were read in `docs/page.rst` at tag `1.28.2`. The eight tests in `test_library_defaults.py` that use it write their pages with PyMuPDF and read them with both engines; `Page.transformation_matrix` converts the rectangle between the two coordinate systems, so no coordinate arithmetic is written here. Annotations are read back a second way with `pypdf` 6.17.0, a pure-Python parser of the PDF object model whose only declared dependency is `typing_extensions` on Python below 3.11, following the `page["/Annots"]` and `annotation.get_object()` pattern in `docs/user/reading-pdf-annotations.md` at tag `6.17.0`.
