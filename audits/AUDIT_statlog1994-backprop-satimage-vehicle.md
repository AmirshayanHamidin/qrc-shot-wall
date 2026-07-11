# AUDIT: StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows — satimage + vehicle

Program 2b confirmatory audit #29 (VAR). Session 2026-07-11 (Program 2b run #29). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

D. Michie, D. J. Spiegelhalter & C. C. Taylor (eds), *Machine Learning, Neural and Statistical Classification*, Ellis Horwood, 1994 — the StatLog project book, same primary source as audit #28. **Re-fetched and re-read this session** (Internet Archive snapshot of the editors' own posting at `www1.maths.leeds.ac.uk/~charles/statlog/whole.pdf`; 1 787 416 B, md5 `4bd24c00e78c3c027d2390776fdd4b55` — byte-count identical to audit #28's file of record).

Two rows, both the **Backprop** (multilayer perceptron) test error rate:

- **Satimage (Table 9.9, §9.3.6): published test error 0.139** (train 0.112, rank 8 of 23). Protocol stated: single train/test split, "(train, test) = (4435, 2000) observations", 36 attributes, 6 classes. No Backprop configuration (hidden nodes, training time, or anything else) is published for this row anywhere in the book (grep-verified this session).
- **Vehicle (Table 9.6, §9.3.3): published test error 0.207** (train 0.168, rank 5 of 24). Protocol stated: "the algorithms were run using 9-fold cross-validation", 846 observations, 18 attributes, 4 classes. UNLIKE every other Backprop row audited so far, the book DISCLOSES part of this row's configuration: *"This figure for Backprop was obtained using 5 hidden nodes and a training time of four hours for the training time in each of the nine cycles of cross-validation."*

General Backprop facts, unchanged from audit #28: the implementation is an external package (§11.5.1); §7.4 says hidden-layer size was CV-tuned in general; learning rate, momentum, weight initialisation, epoch counts, stopping tolerances, and input scaling are published nowhere for either row.

Why this target: the tracker's standing priority is score-4/5 density, and the score-5 bucket (3 points) plus score-4 bucket (16) are still the high end the confirmatory test leans on. These two rows extend audit #28's claim class to two new datasets AND deliver the program's first **within-implementation 5-vs-4 rubric contrast** (same book, same package — one row with disclosed architecture/training time, one with none), directly probing whether the rubric's granularity tracks drift inside a single implementation family. Honest concentration note, recorded at registration: if satimage lands, 3 of the 4 score-5 points will share the StatLog implementation — flagged now for the n=30 honesty section.

NOT audited, decided now before rubric scoring: all other rows of both tables (lower-discretion or no default sklearn estimator — same exclusion rule as audits #7/#8/#28); the segment dataset (Table 9.10 says 11 attributes but the distributed public files carry 19 — the exact StatLog attribute subset is not cleanly recoverable, a pre-run infrastructure exclusion, NOT a result-based drop); shuttle/German-credit/heart (cost-matrix or size complications).

## Data checks (counting only — done BEFORE this commit, no reproduction code run)

- **Satimage:** UCI `statlog/satimage/sat.trn` md5 `2c5ba2900da0183cab2c41fdb279fa5b` (525 830 B) and `sat.tst` md5 `02c995991fecc864e809b2c4c42cd983` (236 745 B), cache-busted fetch. 4435 / 2000 rows, 37 columns (36 attributes + class) — exactly Table 9.9's protocol. Classes {1,2,3,4,5,7} (label 6, mixed pixels, removed by StatLog as the book states); train distribution 1072/479/961/415/470/1038.
- **Vehicle:** UCI `statlog/vehicle/xa[a-i].dat`, nine files, 94 rows each = **846 rows exactly**, 19 columns (18 attributes + class); classes opel 212 / saab 217 / bus 218 / van 199. md5s: xaa `58e47d145a615a66f63d6ebee1464c03`, xab `acb3f6058d5c5be32bb6f6ca32a33589`, xac `cfea1bcae46637fc9d809728ad5087d7`, xad `04322617a9c210dd628d296ee54747d8`, xae `ee3f88b55a12d910226e25d7a6f4b5f3`, xaf `ea2c7de08ebadb7210ebd71b4bbd614e`, xag `a5f2d9e088d7093f0e809f98a892dd99`, xah `ac7ee8eab9cc5094dbf67565cacafc74`, xai `63dc598be76f165a7526b925249db8a4`. The 9-way file partition of a 9-fold-CV dataset is read as the distributed CV partition (the file StatLog itself circulated, per Appendix A's pointer to `statlog/vehicle`), and is pinned as the primary fold assignment below.

## Blind discretion rubric (scored from the book + scikit-learn 1.7 docs ONLY, before any code)

**Satimage row — score 5/5** (identical discretion profile to audit #28's rows; the book publishes nothing about this row's configuration):

1. **Tie-breaking / randomization — 1.** No seed for weight init or presentation order; sklearn's `MLPClassifier` shuffles under its own `random_state`.
2. **Regularization / smoothing defaults — 1.** No weight decay stated; library must default (`alpha=1e-4`).
3. **Initialization — 1.** Starting weights never specified; sklearn defaults to Glorot-style uniform.
4. **Stopping criteria / tolerances — 1.** No epoch count, tolerance, or schedule published for this row; sklearn defaults (`max_iter=200`, `tol=1e-4`, `adam`, `learning_rate_init=1e-3`) must decide.
5. **Preprocessing assumptions — 1.** Input scaling never stated (spectral intensities 0–255-ish integers); sklearn's docs prescribe standardization for MLPs, so the reproducer must choose.

**Vehicle row — score 4/5.** Points 1, 2, 3, 5 score exactly as above (no seed, no penalty, no init, no scaling — all unpublished for this row too). **Point 4 (stopping) scores 0**: the book PUBLISHES this row's training budget ("a training time of four hours ... in each of the nine cycles"). Audit #28's point-4 justification keyed on "the value is never published for these datasets"; for vehicle the value IS published, so consistency forces 0 — recorded honestly: a 1994 wall-clock figure on unstated hardware cannot actually parameterize a modern library (the reproducer must still default `max_iter`/`tol`), so 4/5 is the conservative reading of the frozen rubric, not a claim that stopping discretion is absent. The disclosed **5 hidden nodes** is architecture, not a rubric axis; per program precedent (specified choices are honored) it is ADOPTED in the primary configuration below.

## Reproduction plan (pinned before running)

Per master seed m ∈ {0, 1, 2} (seed 0 primary for the verdict; tracker drift per row = 3-seed mean |reproduced − published|). Environment pinned: Python 3.10, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3 (same as audit #28).

1. Load the md5-pinned files above. Features = float columns as distributed; labels as distributed.
2. **Satimage primary:** `Pipeline(StandardScaler(), MLPClassifier(random_state=m))`, every `MLPClassifier` argument at its library default (`hidden_layer_sizes=(100,)`, relu, adam, `alpha=1e-4`, `learning_rate_init=1e-3`, `max_iter=200`, `shuffle=True`, `tol=1e-4`, `n_iter_no_change=10`). Fit on sat.trn, row value = 100 × error rate on sat.tst. (Scaler fit on train only.)
3. **Vehicle primary:** 9-fold CV with the DISTRIBUTED fold assignment — each xa*.dat file (alphabetical order) serves once as the test fold, the other eight concatenated as train. `Pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(5,), random_state=m))`, all other arguments library defaults; the (5,) honors the book's disclosed 5 hidden nodes. Scaler fit per-fold on train only. Row value = 100 × mean over the 9 folds of the fold test error.
4. Convergence warnings (`max_iter` reached) are **counted and reported**, never suppressed and never fixed post hoc.
5. Labelled sensitivity checks (reported, never the verdict): (a) **unscaled** — both rows, raw features, same estimator; (b) vehicle with the library-default `hidden_layer_sizes=(100,)` (measures what the disclosed architecture is worth); (c) vehicle with `KFold(n_splits=9, shuffle=True, random_state=m)` instead of the distributed folds (measures fold-assignment discretion).

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (13.9 pp error satimage; 20.7 pp vehicle).
- **Tolerance: satimage ±5.0 pp** (the score-5 bar, precedent audits #8/#28); **vehicle ±4.0 pp** (the score-4 bar, precedent audits #9/#11/#16/#17/#23), both on the primary configuration at master seed 0. Bars never move after data.
- **CONFIRMED** if BOTH rows satisfy |reproduced − published| ≤ bar at seed 0 in the primary configuration; **DISCREPANCY** if either row exceeds; **COULD-NOT-RUN** if data access or the 45 s sandbox cap blocks execution.
- **Secondary pre-registered prediction A (hypothesis-consistent, third consecutive re-test):** both rows' 3-seed drift is **strictly greater than 1.96 pp** (the largest score-2 drift in the set). This exact clause failed in audit #8 (1.11 pp) and twice in audit #28 (1.93/1.83 pp — diabetes by 0.03 pp). Two more sub-1.96 high-score points would make five consecutive strikes at the high-discretion end.
- **Secondary pre-registered prediction B (mechanism probe, replicating audit #28's decisive result):** for BOTH rows, the unscaled sensitivity's 3-seed |drift| is strictly greater than the scaled primary's 3-seed |drift| — scaling discretion (rubric point 5) live, not inert.
- **Secondary pre-registered prediction C (within-audit rubric ordering, new):** the satimage row's (score 5) 3-seed drift is strictly greater than the vehicle row's (score 4) — the first 5-vs-4 contrast inside one implementation family.

Tracker context at registration (n = 28, 63 points, exploratory rho 0.562 / p 1.7e-06 — reproduced from the printed list this session with scipy 1.15.3 before this file was written): buckets score 0: 4 points, score 1: 3, score 2: 21, score 3: 16, score 4: 16, score 5: 3. These rows are pre-registered to land at score 5 (bucket → 4) and score 4 (bucket → 17).

## Results

Data checks reproduced at run time: all 11 md5s as pinned above; satimage 4435/2000 x 36, vehicle 9 x 94 x 18.

Primary configurations (master seed 0):

| Row | Published | Reproduced (seed 0) | Drift | Bar | Verdict |
|---|---|---|---|---|---|
| Backprop, satimage (4435/2000 split) | 13.9 | **9.350** | **-4.550 pp** | +/-5.0 | CONFIRMED (in-bar by 0.45 pp) |
| Backprop, vehicle (distributed 9-fold CV, 5 hidden nodes) | 20.7 | **33.924** | **+13.224 pp** | +/-4.0 | **DISCREPANCY** |

All three master seeds, primary configurations:

| Row | seed 0 | seed 1 | seed 2 | 3-seed mean \|drift\| |
|---|---|---|---|---|
| satimage | 9.350 | 9.700 | 10.100 | **4.18 pp** |
| vehicle | 33.924 | 29.787 | 32.033 | **11.21 pp** |

**Standardized drift for the tracker: satimage 4.18 pp at blind rubric 5/5, vehicle 11.21 pp at blind rubric 4/5.** 11.21 pp is the largest drift in the confirmatory set (previous maximum 10.35 at score 3); 4.18 pp is the largest score-5 drift (previous ceiling 1.93). The two rows drift in OPPOSITE directions: the 2026 default MLP beats the 1994 Backprop by 4.6 pp on satimage, while the book-faithful 5-hidden-node vehicle configuration is 13.2 pp WORSE than the 1994 number.

Convergence, reported as pre-registered and NOT fixed: every vehicle primary fold hit `max_iter=200` without meeting `tol` (9/9 folds, all 3 seeds), and satimage primary hit it too (1/1/1 fits). Raising `max_iter` would have been moving a defaulted choice after seeing data.

Secondary pre-registered predictions:

- **A HELD — for the first time in the program.** Both rows' 3-seed drift exceeds 1.96 pp (satimage 4.18, vehicle 11.21). This exact clause failed in audit #8 (1.11) and twice in audit #28 (1.93/1.83); audit #29 finally delivers the large high-discretion drifts the hypothesis expects.
- **B HELD, both rows, decisively.** Unscaled 3-seed drifts: satimage 11.68 pp (vs 4.18 scaled), vehicle 53.30 pp (vs 11.21) — vehicle collapses to ~74% error without scaling. Rubric point 5 is a live drift driver on this claim class, replicating audit #28's mechanism result.
- **C FAILED — inverted.** The score-4 vehicle row (11.21 pp) out-drifted the score-5 satimage row (4.18 pp) by 2.7x. Within one implementation family, the rubric's 5-vs-4 ordering pointed the wrong way.

Labelled sensitivity checks (never the verdict):

- Vehicle with library-default `hidden_layer_sizes=(100,)`: 17.612 / 17.494 / 17.730 — 3-seed drift **3.09 pp, in-bar at every seed**. The book's disclosed 5-hidden-node architecture, honored without its undisclosed 4-hour training budget, is what produces the discrepancy; ignoring the disclosure and taking the modern default would have CONFIRMED the row.
- Vehicle with `KFold(9, shuffle, random_state=m)` instead of the distributed folds: 34.634 / 30.378 / 32.270 (drift 11.73 pp) — fold-assignment discretion is inert (~0.5 pp).
- Satimage unscaled: 26.100 / 21.950 / 28.700 — see secondary B.

## Verdict

**DISCREPANCY** (the program's second, both at rubric 4). Satimage is CONFIRMED at seed 0 (-4.550 pp vs +/-5.0); vehicle exceeds its pre-registered +/-4.0 pp bar at every seed (+13.224 / +9.087 / +11.333). Per the program's standing rule the verdict is a number, not an accusation: the 1994 number was produced by ~4 hours of training per fold on period hardware, and the reproduction's fixed modern budget (`max_iter=200`, all folds unconverged) cannot deliver what that budget did for a 5-hidden-node network. Irreproducibility here defaults to environment/budget difference, not error in the original.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3 (identical to audits #27/#28). Reproduction script: `audits/audit_statlog_backprop2_run.py` (chunked one (dataset, config, seed) triple per invocation; 45 s cap never approached, max ~14 s). Raw output (6 configurations x 3 seeds, per-fold errors, convergence counts): `audits/statlog_backprop2_raw.json`. Both committed in this session's batch.

## Honesty section

1. **The partial-specification trap (post-hoc diagnosis, labelled as such).** The audit's real finding: vehicle's DISCREPANCY is caused by honoring the book's ONLY disclosed Backprop detail (5 hidden nodes) without the training budget that made it work. The h100 sensitivity shows the row reproduces fine (drift 3.09 pp) if the disclosure is ignored. A disclosed detail, honored out of context, drove MORE drift than the fully-undisclosed satimage row - partial specification can be worse than none. This joins audit #28's competence confounder and audit #25's floor-headroom confounder on the post-n=30 exploratory list; it also means the rubric (which scored vehicle LOWER for the disclosure) can be anti-correlated with drift within an implementation family - exactly what secondary C's failure shows.
2. The pinned primary honored the disclosure because program precedent (audits #8/#28) is "specified choices are honored, unspecified resolved by defaults"; that rule was applied blind, before any number existed, and is not softened now that it produced a discrepancy.
3. The two rows share one book and one (unpublished) implementation, so the points are not independent - and with satimage landing, 3 of the 4 score-5 points in the set share the StatLog implementation (concentration flagged at registration; re-flagged here for the n=30 honesty section).
4. Satimage's confirmation is NOT tight: -4.55 pp against a +/-5.0 bar (0.45 pp margin), and its drift direction (modern better) is the same as audit #28's rows. The score-5 bar absorbing a 4.55 pp drift is doing real work for the first time.
5. Two-commit ordering: pre-registration was committed to the REMOTE (`9139fa3`, verified byte-identical at 10 229 B by cache-busted fetch) before any reproduction code existed; results were computed afterwards in this same session.
6. Planner/executor split (tenth audit under it): 16 of 18 chunks were executed by a delegated subagent from exact registered commands; the auditor re-ran two delegated chunks bit-identically, recomputed every drift from the raw JSON, and reproduced the printed 63-point rho (0.562/1.7e-06) before appending the new points.
7. The vehicle fold files (xaa-xai) were READ as the distributed CV partition; the book does not literally say StatLog's 9 folds were these 9 files. The KFold sensitivity shows the reading is immaterial (0.5 pp).
8. The 1994 rows are single historical runs (no seed averaging stated); comparing a 3-seed band against a single draw is the same asymmetry as every audit in this claim class.
