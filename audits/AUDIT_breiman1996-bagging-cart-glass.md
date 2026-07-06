# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, glass rows — e_S and e_B
## Program 2b confirmatory audit #14 (run #13) — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: COMPLETE — verdict CONFIRMED on both rows.** Pre-registration commit `475742c`
landed on the remote (verified byte-identical, md5 fe975cb8) BEFORE any reproduction code
ran; results below were added in a separate commit (two-commit rule + run #2 guardrail).

## Claim

Breiman, L. (1996). "Bagging Predictors", *Machine Learning* 24, 123–140, Table 2
(Misclassification Rates %), glass dataset rows:

- **Row A — e_S = 30.4** : single classification tree, grown on the learning set and pruned
  by 10-fold cross-validation (Section 2.1 step ii).
- **Row B — e_B = 23.6** : bagging, 50 bootstrap replicates, each tree grown on the replicate
  and its best pruned subtree selected using the ORIGINAL learning set L as test set
  (Section 4.3); plurality vote, ties broken toward the lowest class label (step iv).

Procedure (Section 2.1): the 214-case glass data is divided at random into 10% test / 90%
learning; e_S and e_B are measured on the test set; the random division is repeated 100
times and the reported numbers are means over the 100 iterations. Published SEs (Table 3):
1.1 (e_S), 0.9 (e_B). Min node size 1 "throughout" (p. 127). Primary source: Springer PDF
(link.springer.com/content/pdf/10.1007/BF00058655.pdf), fetched and read this session.

Dataset: UCI glass identification, 214 cases, 9 features, 6 classes
(archive.ics.uci.edu, same file as audits #9/#11; expected md5
2732c9170bf8c483f33da3c58929c067, re-verified at download).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the paper + scikit-learn 1.7.2 docs only. Same profile for both rows: **3/5**.

1. **Tie-breaking / randomization — 1**: the 90/10 division, the bootstrap draws, and the
   CV fold construction are all unseeded and unspecified. (Vote ties ARE specified: lowest
   class label — so voting contributes no point, but split/bootstrap RNG does.)
2. **Regularization / smoothing defaults — 1**: pruning method is named (minimal
   cost-complexity) but the selection rule is only "best" subtree — min-error vs the CART
   book's 1-SE rule is left open; candidate-alpha convention (raw path alphas vs geometric
   midpoints) and the split criterion default (gini vs twoing, CART offers both) fall to
   the implementation.
3. **Initialization — 0**: none for deterministic tree growing.
4. **Stopping criteria / tolerances — 0**: minimum node size stated as 1 "throughout";
   trees grown large then pruned — growth is pinned by the paper.
5. **Preprocessing assumptions — 1**: nothing stated: stratification of the 90/10 split
   unspecified, rounding of "10% of 214" (21 vs 22) unspecified, missing-value handling
   moot (glass has none) but split construction is the implementation's.

## Pre-registration (numeric bars, never moved after data)

- Expected values: **e_S = 30.4**, **e_B = 23.6** (percentage points, misclassification).
- **Tolerance: ±4.0 pp** on each row, seed-0 primary, consistent with the tree-family bars
  of audits #9/#11 on this same dataset and >3× the published SEs.
- Standardized drift per PREREG_DRIFT.md: 3-master-seed mean |reproduced − published| pp
  (master seeds 0, 1, 2 seed the entire 100-iteration loop: splits, bootstraps, CV folds).
- Verdict rule: CONFIRMED iff all 3 master seeds land inside the bar on a row; rows judged
  separately; DISCREPANCY otherwise; COULD-NOT-RUN only for pre-run infrastructure blocks.
- **Secondary prediction** (exploratory, from the hypothesis + tracker state): at rubric
  3/5, at least one glass row drifts above the score-2 ceiling (1.96 pp). This prediction
  is falsifiable and has failed before (audit #6); it does not affect the verdict.
- Pinned implementation choices (recorded here because rubric points 1, 2, 5 require the
  implementation to choose): sklearn DecisionTreeClassifier, criterion=gini,
  min_samples_leaf=1; alpha candidates = geometric means of consecutive
  cost_complexity_pruning_path alphas; selection = min error (CV mean for Row A, score on L
  for Row B), ties toward the larger alpha (simpler tree); 90/10 split unstratified with
  test = round(0.1·214) = 21 cases; bootstrap size = |L| = 193.

## Results

Published (Table 2) vs reproduced (100-iteration means, per master seed):

| Row | Published | seed 0 | seed 1 | seed 2 | 3-seed drift (pp) | bar | verdict |
|---|---|---|---|---|---|---|---|
| A: e_S single CV-pruned tree | 30.4 | 32.143 | 31.048 | 30.857 | **0.95** | ±4.0 | **CONFIRMED** |
| B: e_B bagged 50 trees | 23.6 | 25.667 | 24.190 | 25.048 | **1.37** | ±4.0 | **CONFIRMED** |

- All 3 master seeds inside the pre-registered bar on both rows; seed-0 (primary) drifts
  1.74 / 2.07 pp. Largest single-seed excursion: seed-0 e_B at 2.07 pp (52% of the bar).
- Per-seed empirical SEs over the 100 iterations: 0.91–1.02 (e_S), 0.81–0.94 (e_B) —
  bracketing the published SEs of 1.1 / 0.9 (Table 3): the reproduction's iteration noise
  matches the paper's.
- The paper's headline effect reproduces: bagging improves the single tree by 5.8–6.5 pp
  across seeds (published decrease: 6.8 pp, "22%").
- **Secondary prediction FAILED**: both standardized drifts (0.95, 1.37) sit BELOW the
  score-2 ceiling of 1.96 pp. Judged on the pre-registered standardized (3-seed) measure;
  the seed-0 e_B point alone (2.07) would have cleared it, but that is not the registered
  measure. Fifth failure of the mid/high-score secondary prediction in seven attempts —
  consistent, honest evidence that within the 0–2 pp regime the rubric does not order
  drifts finely; the rho signal is carried by the score-3 MLP outliers (audit #2).

Standardized drift points contributed to the Program 2b set: **(3, 0.95), (3, 1.37)**.
Tracker: n = 13/30; exploratory rho over 28 printed-2dp points = 0.653, p = 0.0002.

## Environment

Python 3.11 / scikit-learn 1.7.2 / numpy 2.x, Linux sandbox, 2 cores, CPU only.
Data: UCI glass.data, md5 2732c9170bf8c483f33da3c58929c067 (verified, = audits #9/#11).
Runner: `audits/audit_breiman96_bag_glass_run.py`; raw per-iteration cells:
`audits/breiman96_bag_glass_raw.json`. Chunked under the 45-s cap; per-iteration seeding
(seed_i = master_seed*100000 + iteration) makes chunking irrelevant to the numbers.

## Honesty section

1. **Pre-declared timing probe**: a synthetic-shape probe (random labels, 193×9) ran before
   pre-registration to establish 45-s-cap feasibility (run #3 precedent); it produced no
   glass numbers. A 2-iteration seed-0 probe ran AFTER the prereg was verified on the
   remote (commit 475742c), as the first chunk of the real run.
2. **CART vs sklearn**: the paper used Breiman's own CART. sklearn's
   DecisionTreeClassifier implements the same greedy gini growth + minimal cost-complexity
   pruning, but is not the same code; surrogate splits and twoing are absent (moot here:
   no missing values; gini pinned in prereg). This is exactly the discretion the rubric
   prices — same-family, different implementation, 30-year-old published numbers land
   within ~1–2 pp.
3. **Selection-rule discretion (rubric point 2)**: min-error with ties to larger alpha was
   pinned in the prereg. The CART-book 1-SE alternative was NOT run, to keep the published
   number the only measurand; a sensitivity run remains open for a future session.
4. **Vote-tie convention**: np.argmax returns the first (lowest-label) maximum, matching
   the paper's stated tie rule exactly; no discretion exercised.
5. **Copilot commit-message autofill** recurred on the prereg commit dialog and was
   replaced via the DOM before committing (message verified msgOk=true); recurring
   incident class from runs #1, #10.
6. The reproduced e_S (31.0–32.1) sits slightly ABOVE published on all seeds and e_B
   likewise — a small systematic offset (sklearn's unstratified splits and pruning-grid
   convention are candidate mechanisms), not seed noise. It is well inside the bar and
   consistent with audits #9/#11's glass drifts (0.23–2.43 pp).

*Program 2b confirmatory audit #14 — VAR protocol, github.com/AmirshayanHamidin/qrc-shot-wall.*
