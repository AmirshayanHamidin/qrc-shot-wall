# AUDIT: Aeberhard, Coomans & de Vel (1992) — wine dataset leave-one-out results (LDA / QDA / 1NN)

Program 2b confirmatory audit #7 (VAR). Session 2026-07-06 (Program 2b run #6). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

S. Aeberhard, D. Coomans and O. de Vel, "Comparison of Classifiers in High Dimensional Settings", Tech. Rep. no. 92-02 (1992), Dept. of Computer Science and Dept. of Mathematics and Statistics, James Cook University of North Queensland — as transcribed in the UCI ML Repository's `wine.names` documentation and reproduced verbatim in scikit-learn's bundled dataset description (load_wine DESCR; live copy verified this session, cache-busted, at https://scikit-learn.org/stable/datasets/toy_dataset.html#wine-recognition-dataset):

> "The classes are separable, though only RDA has achieved 100% correct classification. (RDA : 100%, QDA 99.4%, LDA 98.9%, 1NN 96.1% (z-transformed data)) (All results using the leave-one-out technique)"

Rows audited (percent correct, leave-one-out, wine dataset, 178 × 13):

- **LDA: published 98.9%**
- **QDA: published 99.4%**
- **1NN: published 96.1%**

The RDA row (100%) is NOT audited: Friedman-style regularized discriminant analysis has no scikit-learn estimator, and substituting an implementation would change the measurand (the same reason audit #4 rejected the sparse-CSR shortcut). Skipping it is a selection decision made now, before any run.

Why this target: first confirmatory points from the discriminant-analysis family and the first 1990s dataset-documentation claim; first fully deterministic (no-RNG) pipeline in the set — probes the hypothesis at the low-discretion end, where the last two audits leaned against it. Same-harness rows, one audit file, per PREREG_DRIFT multi-row rules.

Note on claim class: the published numbers come from a technical-report summary preserved in dataset documentation (UCI `wine.names`), not a peer-reviewed table fetched directly — the original Tech. Rep. 92-02 is not freely fetchable this session. The transcription is identical in the UCI file and the scikit-learn DESCR, which is the strongest public provenance available; recorded as honesty item 1.

## Blind discretion rubric (scored BEFORE running any code, from the claim + scikit-learn 1.7 docs only)

**LDA row — score 2/5.**

1. Tie-breaking / randomization — 0. LOO is deterministic and LDA is closed-form; no RNG anywhere.
2. Regularization / smoothing defaults — 1. The claim fixes neither the covariance convention (pooled MLE vs unbiased), the class priors (empirical vs equal), nor the svd solver tolerance; sklearn defaults must decide.
3. Initialization — 0. Closed form.
4. Stopping criteria / tolerances — 0. None.
5. Preprocessing assumptions — 1. "(z-transformed data)" leaves open (a) whether the parenthetical qualifies all rows or only 1NN, and (b) whether the transform is fit on the full dataset or inside each LOO fold. (LDA is affine-invariant, so this discretion should be numerically inert here — the rubric scores discretion, not expected impact.)

**QDA row — score 2/5.**

1. Tie-breaking / randomization — 0. Deterministic, closed form.
2. Regularization / smoothing defaults — 1. Per-class covariance convention, priors, sklearn's `reg_param` (default 0.0) and rank tolerance all unspecified.
3. Initialization — 0. 4. Stopping — 0.
5. Preprocessing assumptions — 1. Same z-transform ambiguity as LDA (QDA is likewise invariant to invertible affine feature maps, so again expected inert).

**1NN row — score 2/5.**

1. Tie-breaking / randomization — 1. Distance ties among candidate nearest neighbours are handled implementation-privately (sklearn: lowest index); no other randomness.
2. Regularization / smoothing defaults — 0. None.
3. Initialization — 0. 4. Stopping — 0.
5. Preprocessing assumptions — 1. The z-transform scope (full-dataset vs per-fold) is NOT inert for 1NN, and the distance metric itself is unstated (Euclidean assumed; recorded under this point as a representation assumption).

## Data

`sklearn.datasets.load_wine()` — documented by scikit-learn as a copy of UCI ML Wine (`wine.data`). Expected shape (178, 13), class counts {0: 59, 1: 71, 2: 48}. X md5 to be recorded in Results and cross-checked against the UCI file's documented statistics (min/max/mean table in the same DESCR).

## Reproduction plan (pinned before running)

Per master seed (0 primary; 1, 2 sensitivity — the pipeline contains no RNG, so bit-identical results across seeds are the expectation and will be verified rather than assumed):

1. Load wine (178 × 13). **Primary preprocessing (pinned): z-transform fit on the full dataset** (StandardScaler defaults, ddof=0), applied to all three classifiers — the most natural 1992 reading of "(z-transformed data)". Labelled sensitivity check: scaler fit inside each LOO fold on the 177 training rows.
2. Leave-one-out (sklearn `LeaveOneOut`, 178 folds). In each fold fit, on the 177 training rows:
   - `LinearDiscriminantAnalysis()` — all defaults (solver="svd", priors=empirical).
   - `QuadraticDiscriminantAnalysis()` — all defaults (reg_param=0.0, priors=empirical).
   - `KNeighborsClassifier(n_neighbors=1)` — defaults (minkowski p=2 = Euclidean, uniform weights).
3. Row value = 100 × (correct LOO predictions)/178.
4. Labelled sensitivity checks (reported, not primary): per-fold scaler (all rows); priors=uniform (LDA/QDA); unscaled raw features (all rows, since the parenthetical may qualify only 1NN).

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (98.9 / 99.4 / 96.1 — consistent with 2, 1 and 7 LOO errors out of 178; one LOO case = 0.562 pp).
- **Tolerance: ±1.5 pp absolute per row** (primary configuration, master seed 0) — i.e. at most ~2.7 flipped LOO cases per row against a 34-year-old implementation stack. Tighter than any prior multi-row bar in the set, as befits a deterministic closed-form pipeline.
- **CONFIRMED** if ALL THREE rows satisfy |reproduced − published| ≤ 1.5 pp in the primary configuration; **DISCREPANCY** if any row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution.
- Bars will not be moved after data. Standardized drift for the tracker: 3-seed mean |reproduced − published| per row (expected degenerate across seeds; reported as such if bit-identical).

Secondary pre-registered prediction (hypothesis-consistent direction): all three 3-seed drifts are ≤ 1.96 pp (the largest score-2 drift in the set, LeCun-1998 least squares) — i.e. score-2 stays below the current score-2 ceiling.

## Results

Data check: `load_wine()` → shape (178, 13), class counts {0: 59, 1: 71, 2: 48}, X md5 `147ca82876256d95a75226daa8900712`. Summary statistics match the min/max/mean/sd table published alongside the claim (same DESCR).

Primary configuration (full-dataset z-transform, library defaults, master seed 0):

| Row | Published | Reproduced | Drift | LOO errors (repro vs implied) |
|---|---|---|---|---|
| LDA | 98.9 | **98.876** | −0.024 pp | 2 vs 2 |
| QDA | 99.4 | **99.438** | +0.038 pp | 1 vs 1 |
| 1NN | 96.1 | **95.506** | −0.594 pp | 8 vs 7 |

Master seeds 1 and 2: bit-identical to seed 0 in every configuration (verified by equality of all outputs, as expected for a no-RNG pipeline). **Standardized drift for the tracker (3-seed mean |reproduced − published|): LDA 0.02 pp, QDA 0.04 pp, 1NN 0.59 pp.**

LDA and QDA reproduce the published error counts EXACTLY (2 and 1 leave-one-out errors out of 178); 1NN differs by exactly one LOO case (8 vs 7 errors).

Labelled sensitivity checks (seed 0):

- Per-fold scaler: identical to primary on all three rows (98.876 / 99.438 / 95.506) — the z-transform-scope discretion turned out numerically inert even for 1NN on this dataset.
- Raw (unscaled) features: LDA/QDA unchanged (98.876 / 99.438), empirically confirming the affine-invariance argument in the rubric; 1NN collapses to 76.966 — the "(z-transformed data)" qualifier is load-bearing for 1NN exactly as the rubric's preprocessing point anticipated.
- Uniform priors (LDA/QDA): identical to primary (98.876 / 99.438) — the priors discretion is inert here.

Secondary pre-registered prediction: **HELD.** All three 3-seed drifts (0.02 / 0.04 / 0.59 pp) are ≤ 1.96 pp, the largest score-2 drift in the set.

## Verdict

**CONFIRMED.** All three rows land within the pre-registered ±1.5 pp in the primary configuration — two of them exactly on the published error counts across a 34-year implementation gap (1992 tech-report software → scikit-learn 1.7.2). The largest deviation is a single flipped leave-one-out case on 1NN.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_wine_loo_run.py` (single pass, seconds — no chunking needed). Raw output (all configurations × 3 seeds + data check): `audits/wine_loo_raw.json` (md5 `6aa7803c8990886346d14efd8507972b`). Both committed in this session's batch.

## Honesty section

1. Claim provenance: the audited numbers come from the UCI `wine.names` documentation quoting Tech. Rep. 92-02 — the original report was not fetched this session (no free copy found via the tools available; the UCI fetch itself returned an unusable payload, so the verbatim quote was taken from scikit-learn's bundled DESCR, cross-checked against the live scikit-learn 1.9 docs page, cache-busted). This is a dataset-documentation claim, one step removed from the primary source — a different provenance class from audits #1–#6 and flagged as such.
2. The published values are quoted to 1 decimal (98.9/99.4/96.1). Implied error counts (2/1/7 of 178) are unique within rounding, so drift in pp is well-defined; the LDA/QDA "exact" statements mean exact error counts, with sub-0.05 pp differences purely from decimal rounding of the published figures.
3. The RDA row (100%) was excluded before running because sklearn has no RDA estimator; excluding it was a measurand-integrity decision, not a result-based drop. Its omission slightly narrows the audited claim relative to the full published sentence.
4. All three sensitivity discretions (scaler scope, priors, and scaling for LDA/QDA) proved numerically inert, and the rubric still charges them as discretion points — by design (the rubric scores what the implementation must decide, blind to impact). Noted so readers do not mistake rubric points for observed causes of drift.
5. The three (score, drift) points share one dataset, one LOO harness and identical preprocessing, so they are not fully independent — same caveat as the multi-row points of audits #1–#3 and #6.
6. Two-commit ordering: pre-registration was committed to the REMOTE (`d60a39f`, verified byte-identical at 7080 B) before any reproduction code ran; results were computed only afterwards, in this same session.
7. The pipeline contains no RNG, so the pre-registered "3 master seeds" reduce to a bit-identity check (verified true). The seed-average drift is therefore degenerate; reported per PREREG_DRIFT rules, which anticipated this ("identical procedure").
