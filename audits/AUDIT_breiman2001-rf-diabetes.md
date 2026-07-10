# AUDIT: Breiman (2001) "Random Forests" — Table 2, diabetes row (Forest-RI)

Program 2b confirmatory audit #19 (VAR). Session 2026-07-10 (Program 2b run #18, scheduled). Two-commit rule: this file is committed to the remote with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail: web-commit the pre-registration first). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Breiman, L. (2001), "Random Forests", Machine Learning 45(1), 5–32. Table 2 "Test Set Errors (%)", row `diabetes`:

- Forest-RI, **Single Input (F=1)**: published **24.3%** test error
- Forest-RI, **Selection**: published **24.2%** test error

Full printed row for the record: diabetes — Adaboost 26.6 | Selection 24.2 | Single Input 24.3 | One Tree 33.1. Source: the author's copy at https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf, fetched and transcribed this session (md5 `1993a7fca7ba1c117e1c7686c51320e0`, same artifact as audits #1/#4/#6/#18). Table 1: diabetes = 768 cases, 8 inputs, 2 classes.

Why this target: the named candidate from run #17's tracker — it completes the within-paper, cross-dataset Forest-RI ladder (ionosphere #4, sonar #1, glass #18, diabetes here) at the same discretion profile. It is also the ladder's largest holdout (77 test cases vs 21–35): per-iteration sampling noise is roughly half the other rows', so this point tests whether the ~1–2 pp drifts seen so far shrink with sampling noise or persist as a cross-implementation offset.

## Published procedure (paper Section 5, same wording basis as audits #1/#4/#18)

Random division into 90% training / 10% test, repeated 100 times, errors averaged. Forest-RI with two feature-subset sizes: F=1 ("single input") and F=int(log2 M + 1) ("selection" tries both and uses OOB estimates to select); diabetes M=8 → F=int(log2 8 + 1) = **4**. 100 trees per forest, grown to full size, no pruning, plurality vote.

## Blind discretion rubric (scored BEFORE running any code, from paper + scikit-learn docs only)

Score: **2/5** (both columns; identical discretion profile — same harness as audits #1/#4/#18, whose 2/5 carries over dataset-independently).

1. **Tie-breaking / randomization — 1.** No seed, RNG, bootstrap or split tie-break details published; Fortran CART (2001) vs sklearn RNG entirely different. Binary plurality voting over 100 trees can tie 50/50; sklearn resolves to the lowest class index, which the paper never specifies.
2. **Regularization / smoothing defaults — 0.** RF trees conventionally unpruned and fully grown; sklearn defaults (min_samples_split=2, min_samples_leaf=1, ccp_alpha=0) match the stated convention.
3. **Initialization — 0.** Not applicable to trees.
4. **Stopping criteria / tolerances — 0.** "Grown to full size" pins growth termination; library defaults implement exactly that.
5. **Preprocessing / split construction — 1.** The "random 10%" holdout construction is the reproducer's: unstratified vs stratified, rounding (77 test / 691 train under sklearn's ceil convention), and the OOB-based Selection convention (which forest, how ties break) are pinned here, not by the paper. The file's well-known sentinel zeros (e.g. plas/pres/skin/insu = 0) are taken at face value — the data format encodes no missingness and the paper states no imputation.

## Data

The Pima Indians Diabetes data. Provenance note, recorded before running: the original UCI entry has been withdrawn (the classic UCI path `machine-learning-databases/pima-indians-diabetes/` returns NOT FOUND, verified this session; UCI's current id-34 "Diabetes" is the unrelated AIM-94 insulin dataset). Source used: **OpenML data id 37** ("diabetes", licence field: Public), the standard public mirror of the same file — `https://www.openml.org/data/v1/download/37/diabetes.arff`, downloaded this session, md5 **`3cbaa3e54586aa88cf6aacb4033e4470`** (37,419 bytes), asserted in the runner. Shape checks: 768 rows, 8 real features (preg, plas, pres, skin, insu, mass, pedi, age), classes 500 tested_negative / 268 tested_positive; first data row is the canonical `6,148,72,35,0,33.6,0.627,50,tested_positive`. Matches Table 1's 768/8/2 exactly. The inability to byte-verify against the withdrawn UCI original goes in the honesty section.

## Reproduction plan (pinned before running)

Per master seed m ∈ {0 (primary), 1, 2}: 100 iterations. Iteration i: unstratified `train_test_split(test_size=0.10, random_state=split_seed)` with **split_seed = m*100003 + i** (chunkable under the 45-s cap; per-iteration seeding makes chunking irrelevant to the numbers). Fit two `RandomForestClassifier(n_estimators=100, criterion="gini", bootstrap=True, oob_score=True)` — `max_features=1` with `random_state=(2*split_seed+1) % 2**31` and `max_features=4` with `random_state=(2*split_seed+2) % 2**31`. Class labels encoded tested_negative=0, tested_positive=1 (file order). Single Input column = mean over iterations of the F=1 forest's test error. Selection column = mean over iterations of the test error of the forest (F=1 vs F=4) with the lower forest-level OOB error, tie → F=1 (audit #1/#4/#18 convention). Values ×100. Primary numbers: master seed 0; Program 2b standardized drift = mean |reproduced − published| over the 3 master seeds, per column. Runner: `audits/audit_rf_diabetes_run.py` (committed with results).

## Pre-registered tolerance and verdict rule

- Expected value: the published 24.3 / 24.2 (same-harness ladder points, audits #1/#4/#18, drifted 0.2–1.9 pp; no directional prediction).
- **CONFIRMED** if BOTH columns satisfy |reproduced − published| ≤ **2.0 pp** (seed-0 primary); **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if data access or the 45-s per-process cap blocks a faithful execution. The bar matches sonar's ±2.0 and is tighter than glass's ±2.5: n_test=77 at a ~24% base error gives per-iteration sd ≈ 4.9 pp and a 100-iteration mean sd ≈ 0.5 pp — the smallest sampling noise in the ladder — while still covering the ~1–2 pp cross-implementation offsets observed on the other three rows. Bars will not be moved after data.

Secondary (non-verdict) prediction, logged for the discretion-drift hypothesis: both 3-seed standardized drifts land ≤ the running score-2 ceiling (1.96 pp, audit #5); sharpened clause, on the sampling-noise reasoning above — Single Input lands ≤ glass's Single Input (0.83 pp) and Selection lands ≤ glass's Selection (1.81 pp).

## Results

Environment: sandboxed Ubuntu 22.04, CPU only, Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6. Data: OpenML id 37 `diabetes.arff` downloaded from openml.org this session, md5 **verified** `3cbaa3e54586aa88cf6aacb4033e4470` (37,419 bytes; 768×8, classes 500/268, as pre-registered). Runner: `audits/audit_rf_diabetes_run.py` (chunked ≤30 iterations per process under the 45-s cap; per-iteration seeding makes chunking irrelevant to the numbers). Raw per-iteration cells (err_f1, err_f4, oob_f1, oob_f4, err_sel, picked): `audits/rf_diabetes_raw.json`.

| Column | Published | Reproduced (master seed 0, primary) | Drift |
|---|---|---|---|
| Single Input (F=1) | 24.3 | **23.701** | −0.60 pp |
| Selection | 24.2 | **23.636** | −0.56 pp |

Sensitivity seeds — Single Input: 24.662 (seed 1), 23.883 (seed 2); Selection: 24.039 (seed 1), 23.948 (seed 2).

**Verdict: CONFIRMED** — both columns inside the pre-registered ±2.0 pp bar at seed 0. The bar was not moved.

**Program 2b standardized drift (3-seed mean |reproduced − published|): Single Input 0.46 pp, Selection 0.33 pp.** With the blind rubric score of 2/5 recorded in the pre-registration commit `37200fe`, this audit contributes the points **(2, 0.46)** and **(2, 0.33)** to the confirmatory set (n=18/30).

Secondary prediction **HELD in both clauses**: both 3-seed drifts sit below the running score-2 ceiling (1.96 pp, audit #5), and each column lands below its glass counterpart (0.46 ≤ 0.83; 0.33 ≤ 1.81) — the ladder's drift shrank with test-set size exactly as the pre-registration's sampling-noise reasoning predicted.

## Honesty section

1. **Data provenance.** The reproduction cannot be byte-verified against the withdrawn UCI original. The OpenML id-37 mirror matches Table 1's dimensions (768/8/2), the canonical class balance (500/268), and the canonical first row; its licence field reads "Public". If Breiman's 2001 file differed from this mirror in any cell, that difference is invisible here.
2. **Environment.** scikit-learn was not preinstalled in this session's sandbox and was installed from PyPI (resolved to 1.7.2 — the same version as every prior Program 2b audit, so ladder comparability holds). The install initially failed on a nearly-full session mount (ENOSPC) and was redirected to `/tmp`; the workaround affects only the install path, not the pipeline.
3. **Executor delegation (new this run).** Per the run-#18 efficiency rule, chunk execution and the merge step were performed by a subordinate executor agent; the auditing session verified the output before publication: independent recomputation of both column means and the OOB-selection rule across all 300 raw rows, plus bit-identical independent re-runs of three spot iterations (m=0 i=0, m=1 i=37, m=2 i=99). Judgment steps (target choice, rubric, bars, this write-up) were not delegated.
4. **The published within-row ordering reproduces here** (Selection 23.87 < Single Input 24.08 on 3-seed means, and at 2 of 3 seeds) — in contrast to glass (audit #18), where selection added variance instead of value. On 691 training cases the forest-level OOB estimate is informative enough for the Selection rule to help; it picked F=4 in 67–73% of iterations.
5. **Drift direction is favorable (reproduced below published) on both columns at seeds 0 and 2, and unfavorable on Single Input at seed 1** — no consistent direction, consistent with the replication-noise reading across the four audited rows of Table 2.
6. The same-engine caveat of audit #3 does NOT apply: Fortran CART (2001) vs scikit-learn 1.7.2 are genuinely independent implementations.
