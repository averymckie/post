## Volume ladder: 25,000 cases (genv-2.1.0, second batch)

The same generator, dictionary and programs, run at 25,000 with a fresh seed drawn from the operating system and recorded (`build/seed.txt`). No vocabulary expansion took place: the generator reported no exhausted strata, so under its own policy no setup revision was due. Counts: 30373 attempted, 25,000 admitted, 512 contradictions rejected, 1205 unresolved searches, 3656 diverted to review, 24983 distinct idea keys (the generator's first 17 idea-key collisions), 0 full keys and 2 idea keys shared with the first batch. Generation 61 seconds, checking 13 seconds, 25,000 of 25,000 checker-clean.

Gate: all eight pass (floors scaled by five; cross-regime cases 4,446 against a floor of 2,500; byte-identical rerun of 25,000 cases; 20 of 20 broken variants caught). New bridge atoms needed for this batch: 0 per thousand cases, because the vocabulary is frozen at this version and every ingredient it can emit was already judged; the metric can only move when the generator expands its vocabulary in a new version.

Reference readings (revised bridge, recursive suppliers), with the first batch's rates beside them:

| verdict | 25,000 strict | rate | 5,000 strict rate | 25,000 lenient | rate | 5,000 lenient rate |
|---|---|---|---|---|---|---|
| COVERED | 8193 | 32.8% | 32.8% | 22835 | 91.3% | 91.1% |
| PARTIAL | 406 | 1.6% | 1.4% | 1135 | 4.5% | 4.8% |
| UNEXPLAINED | 16401 | 65.6% | 65.8% | 1030 | 4.1% | 4.0% |

The rates are the same to within a point at five times the volume, so the first batch was already representative of this vocabulary. Strict UNEXPLAINED decomposes into vocabulary only 14644, both 1299, structural only 458; the vocabulary items are the same 18, led by undocumented local knowledge held by practitioners (4590), customary authority not recorded in statute (2894), a site with contested claims or access (2850), an uncontrolled public space (2471), a controlled clean or sterile area (2072). Lenient UNEXPLAINED decomposes into structural only 1027, both 3; the structural residual is configurators (731 cases, F37 with no family specification), then F27 97, F09 65, F35 53, F32 46, F17 32, F14 26, F33 21, F22 17, F29 16, F16 14, F21 12, F19 8, F10 6, F34 6, F02 6, F30 .

Proof layer (strict): F29 1037, F30 152, F12 15, in proportion to the first batch. Never reached (strict): families F26, F38; the volume reached F18, F20 and F36 that the first batch missed. Product-level invariance: by regime STRAINS 12, HOLDS 50 of 62 products; by scale band HOLDS 41, STRAINS 21 of 62. Strains by regime: a costed delivery plan; a periodic clinic where people bring problems; an interactive decision aid; a holding arrangement that releases on a condition; a written field procedure with roles and steps; a governance process with named decision points; a quality and limitation label carried with every figure; a public register with a revision history; a low-cost sensing kit with its calibration procedure; a settlement mechanism with compensating actions; a test rig that measures a stated property; a validator that reports per-record verdicts with reasons.

Files: `coverage/runs/genv-2.1.0-25k/` (canonical cases gzipped, derivations gzipped, analyses, gate report, generation record, seed, plain one-line rendering gzipped). The 491 MB generator output and the 76 MB review pool regenerate byte-identically from the seed.

