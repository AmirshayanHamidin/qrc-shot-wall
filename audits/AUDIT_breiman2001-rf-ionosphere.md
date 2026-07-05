# AUDIT: Breiman (2001) "Random Forests" — Table 2, ionosphere row (Forest-RI)

Program 2 (VAR) third-party replication audit #4. Session 2026-07-05. Two-commit rule: this file is committed with EMPTY results sections BEFORE any experiment runs; results land in a separate later commit.

## Claim under audit

Breiman, L. (2001), "Random Forests", Machine Learning 45(1), 5–32. Table 2 "Test Set Errors (%)", row `ionosphere`:

- Forest-RI, **Single Input (F=1)**: published **7.5%** test error
- Forest-RI, **Selection**: published **7.1%** test error

Full printed row for the record: Adaboost 6.4 | Selection 7.1 | Single Input 7.5 | One Tree 12.7. Only the two Forest-RI columns are audited (Adaboost and One Tree out of scope). Source: the author's copy at https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf, fetched and transcribed this session. This is one of the most-cited ML papers in existence; the row has never been checked by this program.

## Published procedure (paper wording, transcribed)

"On each of the 13 smaller sized data sets, the following procedure was used: a random 10% of the data was set aside. On the remaining data, random forest was run twice, growing and combining 100 trees — once with F=1, and the second time with F=int(log2M+1). The set aside 10% was then put down each forest to get a test set error for both. The test set error selected corresponded to the lower value of the out-of-bag estimate in the two runs. This was repeated 100 times and the test set errors averaged."

Reading pinned BEFORE running: the "Single Input" column is the mean test error of the F=1 forest over the 100 iterations; the "Selection" column is the mean test error where, in each iteration, the forest (F=1 vs F=int(log2 34 + 1) = 6) with the lower OOB estimate is chosen. Ionosphere: 351 instances, 34 inputs, 2 classes (paper Table 1 row matches UCI).

## Data

UCI Ionosphere via OpenML data_id=59 (public). Shape, class counts (expected 225 good / 126 bad) and an MD5 of the design matrix will be logged in Results.

## Reproduction plan (pinned before running)

scikit-learn RandomForestClassifier: n_estimators=100, criterion=gini, bootstrap=True, oob_score=True, max_features=1 (Single Input) and 6 (second forest), trees fully grown (min_samples_split=2, min_samples_leaf=1 defaults). 100 iterations; each iteration an unstratified random holdout, train_test_split(test_size=0.10) → 36 test / 315 train (paper says "a random 10%"; sklearn ceil convention, declared here). Primary numbers: master seed 0 (seeds per-iteration derived from it). Seed sensitivity reported secondarily with master seeds 1 and 2 — the published procedure is itself stochastic with no published seed.

Declared implementation gaps: Breiman's 2001 Fortran CART vs scikit-learn trees; different RNG, bootstrap and tie-breaking details; 25 years of library evolution. Pricing exactly this discretion is the point of the audit.

## Pre-registered tolerance and verdict rule

- Tolerance: **±1.5 pp absolute, per column.** Rationale: even an exact reimplementation has ~0.9 pp of two-sided 95% replication noise here (per-iteration test error SD ≈ 4.3 pp at p≈0.07 with n_test=36; SEM over 100 reps ≈ 0.43 pp), and the target is cross-implementation. Wider than the ±0.5 pp used for the deterministic-protocol Fashion-MNIST rows because the published procedure itself is unseeded and stochastic.
- **CONFIRMED** if BOTH columns satisfy |reproduced − published| ≤ 1.5 pp (seed-0 primary numbers); **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if data or the 45 s per-process cap blocks execution.
- Bars will not be moved after data.

Secondary pre-registered prediction (discretion-predicts-drift, point #5): this is the highest-discretion target audited so far (cross-implementation + seed + split randomness), so predicted |drift| > 0.25 pp (the LogReg anchor) on at least one column. Current ladder: docs-SVC ~0.00 < k-NN 0.15 < LogReg 0.25 < GaussianNB 5.9 (pp).

## Results

(EMPTY at pre-registration — filled in a separate later commit.)

## Verdict

(EMPTY at pre-registration.)

## Environment

(EMPTY at pre-registration.)

## Honesty section

(EMPTY at pre-registration.)
