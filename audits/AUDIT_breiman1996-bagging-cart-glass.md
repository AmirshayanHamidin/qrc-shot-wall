# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, glass rows — e_S and e_B
## Program 2b confirmatory audit #14 (run #13) — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: PRE-REGISTERED, results pending.** This file is committed to the remote with an
EMPTY results section BEFORE any reproduction code runs (two-commit rule + run #2 guardrail).

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

*(empty at pre-registration — filled in a separate commit after the runs)*

## Environment

*(filled with results)*

## Honesty section

*(filled with results; one item is pre-declared: a synthetic-shape timing probe — random
labels, 193×9 — ran before this pre-registration to establish 45-s-cap feasibility, per the
run #3 precedent; it produced no glass numbers.)*
