# AUDIT: Breiman (2001) "Random Forests" — Table 2, sonar row (Forest-RI)

Program 2b (VAR) replication audit — **confirmatory audit #1 (n=1 toward 30)** under `audits/PREREG_DRIFT.md`. Session 2026-07-05. Two-commit rule: this file is committed with rubric + pre-registration and EMPTY results sections BEFORE any experiment runs; results land in a separate later commit.

## Claim under audit

Breiman, L. (2001), "Random Forests", Machine Learning 45(1), 5–32. Table 2 "Test Set Errors (%)", row `sonar`:

- Forest-RI, **Single Input (F=1)**: published **18.0%** test error
- Forest-RI, **Selection**: published **15.9%** test error

Full printed row for the record: Adaboost 15.6 | Selection 15.9 | Single Input 18.0 | One Tree 31.7. Only the two Forest-RI columns are audited. Source: the author's copy at https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf, fetched and transcribed this session. Table 1 row: sonar, 208 train instances, 60 inputs, 2 classes. Same paper and procedure as audit #4 (ionosphere, exploratory set); different dataset, so this is a fresh row never checked by this program.

## Published procedure (same paper wording as audit #4)

"On each of the 13 smaller sized data sets ... a random 10% of the data was set aside. On the remaining data, random forest was run twice, growing and combining 100 trees — once with F=1, and the second time with F=int(log2M+1). The set aside 10% was then put down each forest to get a test set error for both. The test set error selected corresponded to the lower value of the out-of-bag estimate in the two runs. This was repeated 100 times and the test set errors averaged."

For sonar: M=60, so the second forest uses **F = int(log2 60 + 1) = 6**.

## Blind discretion rubric (PREREG_DRIFT.md; scored from paper + scikit-learn docs BEFORE any code ran)

| # | Item | Point | Justification (one line) |
|---|---|---|---|
| 1 | Tie-breaking / randomization | **1** | No seed, RNG, bootstrap or split tie-break details published; Fortran CART vs sklearn RNG entirely different. |
| 2 | Regularization / smoothing defaults | **0** | Trees grown to maximum size without pruning per paper; no regularization knob left to the library. |
| 3 | Initialization | **0** | Tree ensembles have no initialization state. |
| 4 | Stopping criteria / tolerances | **0** | 100 trees, fully grown — both pinned by the paper. |
| 5 | Preprocessing assumptions | **1** | Split construction unspecified: stratification unstated, 10% of 208 = 20.8 rounds to 20 or 21; no preprocessing statement (immaterial for trees, but the convention is ours to pick). |

**Discretion score: 2/5.** Recorded here before any reproduction code ran, per PREREG_DRIFT.md order of operations.

## Data

UCI Sonar (Gorman & Sejnowski) via OpenML `data_id=40` (public). Shape (expected 208×60), class counts and an MD5 of the design matrix will be logged in Results.

## Reproduction plan (pinned before running)

scikit-learn `RandomForestClassifier`: n_estimators=100, criterion=gini, bootstrap=True, oob_score=True, max_features=1 (Single Input) and 6 (second forest), trees fully grown (defaults min_samples_split=2, min_samples_leaf=1). 100 iterations; each iteration an unstratified `train_test_split(test_size=0.10)` → 21 test / 187 train (sklearn ceil convention, declared here). Per-iteration Selection = test error of the forest (F=1 vs F=6) with lower OOB error, tie → F=1 (same convention as audit #4, this time declared in the pre-registration). Primary numbers: master seed 0; drift for the Program 2b tracker = mean |reproduced − published| over master seeds 0, 1, 2 per PREREG_DRIFT.md.

## Pre-registered expected value, tolerance and verdict rule

- **Expected value:** Single Input ≈ 18.0%, Selection ≈ 15.9%, with a mild favorable drift up to ~1 pp considered normal (the exploratory ionosphere audit of the same table drifted −0.74 to −0.81 pp).
- **Tolerance: ±2.0 pp absolute, per column.** Rationale: n_test=21 makes each iteration noisy (per-iteration SD ≈ 8 pp at p≈0.17; SEM over 100 reps ≈ 0.8 pp, so ~1.6 pp two-sided 95% replication noise even for an exact reimplementation), plus cross-implementation discretion priced at ~0.8 pp by the exploratory ionosphere audit. Wider than ionosphere's ±1.5 pp because sonar's test split is 21 vs 36 samples.
- **CONFIRMED** if BOTH columns satisfy |reproduced − published| ≤ 2.0 pp (seed-0 primary); **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if data access or the 45 s per-process cap blocks execution. Bars will not be moved after data.
- **Secondary (Program 2b, exploratory until n=30):** with discretion score 2, the hypothesis predicts moderate drift — larger than the zero-discretion docs-SVC anchor (~0.0 pp), same order as the ionosphere point (~0.8 pp), well below GaussianNB (5.9 pp).

## Results

*(empty at pre-registration commit — filled in a separate later commit)*

## Verdict

*(empty at pre-registration commit)*

## Environment

*(empty at pre-registration commit)*

## Honesty section

*(empty at pre-registration commit)*
