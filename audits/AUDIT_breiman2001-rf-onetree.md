# AUDIT: Breiman (2001) "Random Forests" — Table 2, "One Tree" column, ionosphere + sonar rows

Program 2b confirmatory audit #6 (VAR). Session 2026-07-06 (Program 2b run #5). Two-commit rule: this file is committed with an EMPTY results section BEFORE any reproduction code runs (per the run #2 guardrail, the pre-registration is web-committed to the remote first). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Breiman, L. (2001), "Random Forests", Machine Learning 45(1), 5–32. Table 2 "Test Set Errors (%)", column **"One Tree"**:

- Row `ionosphere`: published **12.7%**
- Row `sonar`: published **31.7%**

Full printed rows for the record: ionosphere — Adaboost 6.4 | Selection 7.1 | Single Input 7.5 | **One Tree 12.7**; sonar — Adaboost 15.6 | Selection 15.9 | Single Input 18.0 | **One Tree 31.7**. Source: the author's copy at https://www.stat.berkeley.edu/~breiman/randomforest2001.pdf, fetched and transcribed this session (matches the transcription in audits #1 and #4, which audited the two Forest-RI columns of these same rows).

Paper's definition of the column (transcribed): "The fourth column contains the out-of-bag estimates of the generalization error of the individual trees in the forest computed for the best setting (single or selection). This estimate is computed by using the left-out instances as a test set in each tree grown and averaging the result over all trees in the forest."

Why this target: same paper, same datasets, same 100-iteration harness as audits #1 and #4 — but a different measurand with a visibly higher discretion profile. It extends the within-paper ladder (Forest-RI rows scored 2/5, drift 0.6–0.9 pp) by one rubric notch, and it is the first score-3 point from a non-neural-network family (the only current 3/5 points are the Gorman-Sejnowski MLP rows, drift ~9–10 pp).

## Blind discretion rubric (scored BEFORE running any code, from paper + scikit-learn 1.7 docs only)

Score: **3/5** (both rows; identical discretion profile — same measurand, same harness).

1. **Tie-breaking / randomization — 1.** No seeds published; bootstrap RNG, feature-subset draws, split tie-breaking and the OOB membership pattern are all implementation-private, and the individual-tree estimate inherits ALL of the forest's randomness with none of its averaging.
2. **Regularization / smoothing defaults — 0.** Random-forest trees are conventionally grown to full size without pruning; sklearn's defaults (min_samples_split=2, min_samples_leaf=1, no pruning) match the convention. No regularization constant is left floating.
3. **Initialization — 0.** Not applicable to trees.
4. **Stopping criteria / tolerances — 1.** The paper never states node-size floors or growth-termination rules for the individual trees; the library's defaults must fix them, and a single unpruned tree's error is far more sensitive to growth-termination details than a 100-tree average.
5. **Preprocessing / split construction — 1.** Three constructions are left to the reproducer: (a) the unstratified "random 10%" holdout and its rounding (36/315 ionosphere, 21/187 sonar under sklearn's ceil convention); (b) how the per-tree OOB errors are aggregated across the 100 harness iterations (we pin: average over trees within an iteration, then average iterations); (c) "computed for the best setting (single or selection)" — we pin: in each iteration, the forest (F=1 vs F=int(log2 M+1)) with the lower forest-level OOB error estimate, tie → F=1 (the audit #1/#4 convention).

## Data

- Ionosphere: OpenML data_id=59 (public), expected shape (351, 34), classes {b: 126, g: 225}, X md5 `47340afe07e851bf0bd0ea7b84af7b6b` (from audit #4).
- Sonar: OpenML data_id=40 (public), expected shape (208, 60), 2 classes (97 rock / 111 mine). MD5 logged in Results (cross-checked against audit #1's cache if present).

## Reproduction plan (pinned before running)

Per master seed (0 primary; 1, 2 sensitivity), per dataset, 100 iterations. Each iteration: unstratified train_test_split(test_size=0.10, random_state=master*100003+i); fit two RandomForestClassifier(n_estimators=100, criterion="gini", bootstrap=True, oob_score=True) with max_features=1 and max_features=int(log2 M+1) (=6 ionosphere, =6 sonar: int(log2 60 +1)=6); select the forest with lower forest OOB error (tie → F=1). For the selected forest, for each of its 100 trees: reconstruct that tree's bootstrap sample via sklearn's `sklearn.ensemble._forest._generate_sample_indices(tree.random_state, n_train, n_train)` (private API, version-pinned; same generator the fit used), take the complement as that tree's OOB set, compute the tree's error on it; average over the 100 trees → the iteration's one-tree error. Column value = mean over 100 iterations, ×100.

Note the pinned reading: the paper computes the one-tree estimate on the 90% training data (out-of-bag), NOT on the 10% holdout — the holdout is only used by the other columns. Trees with an empty OOB set (probability ≈ (1−1/e)^n ≈ 0) would be skipped and counted.

## Pre-registered tolerance and verdict rule

- **Expected value:** near published (12.7 / 31.7).
- **Tolerance: ±3.0 pp absolute, per row** (seed-0 primary). Rationale: wider than the ±1.5/±2.0 pp used for the forest columns of the same rows because (i) the measurand is a single-tree error (~2–3× the forest error, so the same relative implementation gap costs more points), (ii) individual-tree error is directly exposed to 25 years of CART implementation drift with no ensemble averaging to damp it, and (iii) each OOB test set is only ~e⁻¹·n_train ≈ 116 (ionosphere) / 69 (sonar) instances. Even so the bar is proportionally tighter than audit #1's (3.0/31.7 = 9.5% relative vs 2.0/18.0 = 11%).
- **CONFIRMED** if BOTH rows satisfy |reproduced − published| ≤ 3.0 pp at seed 0; **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if data access or the 45 s per-process cap blocks execution.
- Bars will not be moved after data. Standardized drift for the Program 2b tracker: 3-seed mean |reproduced − published| per row, as registered.

Secondary pre-registered prediction (hypothesis-consistent direction): at rubric 3/5, 3-seed |drift| on at least one row exceeds the largest score-2 drift so far (1.96 pp, LeCun-1998 least squares).

## Results

(EMPTY at pre-registration commit. Filled in the results commit.)

## Verdict

(EMPTY at pre-registration commit.)

## Environment

(EMPTY at pre-registration commit.)

## Honesty section

(EMPTY at pre-registration commit.)
