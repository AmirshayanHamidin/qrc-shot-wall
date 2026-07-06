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

*(empty before reproduction — commit 1 of 2)*

## Verdict

*(empty before reproduction — commit 1 of 2)*

## Environment

*(empty before reproduction — commit 1 of 2)*

## Honesty section

*(empty before reproduction — commit 1 of 2; item 1 reserved for the claim-provenance note above)*
