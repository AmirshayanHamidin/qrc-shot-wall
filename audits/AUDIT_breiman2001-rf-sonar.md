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

Data check: OpenML data_id=40 → shape (208, 60), classes {111, 97}, X md5 `e5f03fedbe063c500c22a7be8c4fe878` — matches paper Table 1 (208 instances / 60 inputs / 2 classes).

| Column | Published | Reproduced (master seed 0, primary) | Drift |
|---|---|---|---|
| Single Input (F=1) | 18.0 | **18.19** (SEM 0.83) | +0.19 pp |
| Selection | 15.9 | **17.86** (SEM 0.86) | +1.96 pp |

Seed sensitivity (identical 100-iteration procedure, master seeds 1 and 2): Single Input 17.52 / 16.90; Selection 16.71 / 15.95. Every seed × column combination is within the pre-registered ±2.0 pp bar.

**Program 2b standardized drift (3-seed mean |reproduced − published|): Single Input 0.59 pp, Selection 0.94 pp.** With the blind rubric score of 2/5 recorded in the pre-registration commit, this audit contributes the points (2, 0.59) and (2, 0.94) to the confirmatory set (n=1 audit toward 30).

Secondary observations: the paper's Selection < Single Input ordering reproduced on all three seeds. The OOB selection picked F=6 in 59–66 of 100 iterations (ties 4–10); the always-F=6 forest averaged 16.57–17.00%.

Secondary pre-registered prediction: **held** — 3-seed |drift| 0.59–0.94 pp is above the docs-SVC anchor (~0.0), the same order as ionosphere (~0.8), and well below GaussianNB (5.9).

## Verdict

**CONFIRMED.** Both audited columns reproduce within the pre-registered ±2.0 pp on the seed-0 primary numbers (+0.19 and +1.96 pp) and on both sensitivity seeds. Honest caveat: the seed-0 Selection drift (+1.96 pp) uses 98% of the bar — see honesty items 1–2.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_rf_sonar_run.py` (chunked for the 45 s per-process cap; ~31 s per master seed); raw per-iteration rows (3 seeds × 100 iterations): `audits/rf_sonar_raw.json`. Both committed in this session's batch.

## Honesty section

1. The seed-0 Selection drift (+1.96 pp) is just inside the ±2.0 pp bar. Under the ±1.5 pp bar used for the ionosphere audit, seed 0 would have scored a DISCREPANCY on that column. The wider bar was pre-registered before any data specifically because n_test=21 roughly halves the effective sample of ionosphere's n_test=36; seeds 1 and 2 (16.71, 15.95) land much closer to the published 15.9, consistent with seed 0 being a noise draw. The bar was not moved after data.
2. Drift direction at seed 0 is *unfavorable* (reproduced error higher than published) on both columns — the opposite of the ionosphere audit's uniformly favorable drift. Across the two audits of this table there is therefore no consistent direction, which supports pricing this as replication noise rather than systematic library improvement.
3. The OOB tie convention (tie → F=1) was pre-registered this time (audit #4 had fixed it only in code). Sensitivity: tie → F=6 moves Selection by ≤ 0.38 pp (worst seed) — immaterial to the verdict.
4. Test split is 21 samples (sklearn ceil convention) vs Breiman's likely 20 (10% of 208 = 20.8); declared pre-run.
5. Class labels binarized against the first target value; error rates are invariant to the encoding.
6. Session incident (cosmetic, disclosed): GitHub's Copilot commit-message autofill collided with typed text on the PREREG_DRIFT.md commit (`ad8aa31`), garbling that commit's message. The committed file content was verified byte-identical to the local copy via a fresh `git fetch` (MD5 match). Later commit messages in this session were set programmatically to prevent recurrence. A filename-field focus miss on this audit's pre-registration commit was caught by inspecting page state before committing; the editor document was verified intact (5056 chars) before the commit was made.
7. Both commits of the two-commit rule occur in the same autonomous session; the ordering is provable from git history alone (pre-registration `babcc6a` precedes this results commit).
8. Content was injected into the web editor via the editor's own document API with length verification (4881/4881 and 5056/5056 chars), avoiding the lazy-render paste hazard that affected runs #3 and #4.
