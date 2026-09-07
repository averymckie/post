# Handoff hardening guards

Runnable local guard modules embedded in `../Proofs.txt` (hardening batches P1-P10, P11-P20, P21-P30, P31-P40, P41-P50) together with their evidence files. Each module's SHA256 and byte count are recorded in `Proofs.txt` next to its embedded copy; each evidence file records the `source_sha256` of the module that produced it and, from v2 on, the `dependency_sha256` of the modules it imports.

## Files

| file | role |
| --- | --- |
| `handoff_guards_v1.py` | batch P1-P10 (SHA256 `2b3138b6…`) |
| `handoff_guards_v2.py` | batch P11-P20 (SHA256 `0a406d0e…`), imports v1 |
| `handoff_guards_v3.py` | batch P21-P30 plus the glue register (SHA256 `e8df8d98…`), imports v1 and v2 |
| `handoff_guards_v4.py` | batch P31-P40 (SHA256 `90029a69…`), imports v1 and v3 |
| `handoff_guards_v5.py` | batch P41-P50 (SHA256 `611cd01d…`), imports v1, v3 and v4 |
| `guards-v1.json`, `guards-v2.json` | evidence recorded with the earlier batches |
| `rerun-v1.json`, `rerun-v2.json` | the same modules re-executed in the batch-3 environment |
| `guards-v3.json`, `guards-v4.json`, `guards-v5.json` | batch-3, batch-4 and batch-5 evidence |
| `requirements-hardening.txt` | exact package versions of the batch-3 environment (`uv pip freeze`) |

## Run

```
python3.11 -m venv venv && ./venv/bin/pip install -r requirements-hardening.txt
./venv/bin/python handoff_guards_v1.py --report guards-v1.json
./venv/bin/python handoff_guards_v2.py --report guards-v2.json
NLTK_DATA=/path/to/nltk_data ./venv/bin/python handoff_guards_v3.py --report guards-v3.json
./venv/bin/python handoff_guards_v4.py --report guards-v4.json
./venv/bin/python handoff_guards_v5.py --report guards-v5.json
```

Case 26 of v3 uses the WordNet 3.0 corpus when `NLTK_DATA` points at a directory holding `corpora/wordnet.zip` (SHA256 `cbda5ea6eef7f36a97a43d4a75f85e07fccbb4f23657d27b4ccbc93e2646ab59`, 10775600 bytes, obtained once with `nltk.download('wordnet', download_dir=...)`). Without it the case still passes and records `not installed; no lexical expansion executed`. The guard runs themselves make no network call.
