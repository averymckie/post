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
