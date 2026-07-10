# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, ionosphere rows — e_S and e_B
## Program 2b confirmatory audit #22 — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: PRE-REGISTERED, results pending.** This file is committed with an EMPTY results
section BEFORE any reproduction code runs (two-commit rule + run #2 guardrail:
remote-first web commit).

## Claim

Breiman, L. (1996). "Bagging Predictors", *Machine Learning* 24, 123–140, Table 2
(Misclassification Rates %), ionosphere dataset rows:

- **Row A — e_S = 11.2** : single classification tree, grown on the learning set and pruned
  by 10-fold cross-validation (Section 2.1 step ii).
- **Row B — e_B = 7.9** : bagging, 50 bootstrap replicates, each tree grown on the replicate
  and its best pruned subtree selected using the ORIGINAL learning set L as test set
  (Section 4.3); plurality vote, ties broken toward the lowest class label (step iv).

Procedure (Section 2.1): the 351-case ionosphere data is divided at random into 10% test /
90% learning; e_S and e_B are measured on the test set; the random division is repeated 100
times and the reported numbers are means over the 100 iterations. Published SEs (Table 3):
0.5 (e_S), 0.4 (e_B). Published decrease: 29%. Min node size 1 "throughout" (p. 126).
Primary source: Springer PDF (link.springer.com/content/pdf/10.1007/BF00058655.pdf),
fetched and read this session.

Dataset: UCI ionosphere (Sigillito et al. 1989, JHU APL radar returns), 351 cases,
34 features, 2 classes (good 226 / bad 125 — counts stated in the paper's Appendix and
verified at load). Same file as audits #16 and the Program 2 run-#4 Breiman-2001 audit;
expected md5 **85649e5fb5b15fb9dab726c400be61fe**, re-verified at download this session.

Cross-paper anchor (recorded, not a bar): audit #14 reproduced this paper's glass rows at
0.95/1.37 pp drift; audit #16 reproduced FS96's *C4.5* bagging on this same ionosphere
dataset at 1.34 pp drift.

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the paper + scikit-learn 1.7.2 docs only. Same discretion profile as audit #14
(same paper, same §2.1/§4.3 procedure; only the dataset changes). Both rows: **3/5**.

1. **Tie-breaking / randomization — 1**: the 90/10 division, the bootstrap draws, and the
   CV fold construction are all unseeded and unspecified. (Vote ties ARE specified: lowest
   class label — voting contributes no point, but split/bootstrap/fold RNG does.)
2. **Regularization / smoothing defaults — 1**: pruning method is named (minimal
   cost-complexity via CART) but the selection rule is only "best" subtree — min-error vs
   the CART book's 1-SE rule is left open; candidate-alpha convention (raw path alphas vs
   geometric midpoints) and the split criterion default (gini vs twoing, CART offers both)
   fall to the implementation.
3. **Initialization — 0**: none for deterministic tree growing.
4. **Stopping criteria / tolerances — 0**: minimum node size stated as 1 "throughout";
   trees grown large then pruned — growth is pinned by the paper.
5. **Preprocessing assumptions — 1**: stratification of the 90/10 split unspecified,
   rounding of "10% of 351" (35 vs 36) unspecified, class-label ordering for the vote
   tie-break unspecified (the paper says "lowest class label" but never numbers the
   good/bad classes); missing values moot (ionosphere has none) but split construction is
   the implementation's.

## Pre-registration (numeric bars, never moved after data)

- Expected values: **e_S = 11.2**, **e_B = 7.9** (percentage points, misclassification).
- **Tolerance: ±3.0 pp** on each row, seed-0 primary — the tree-family bar audit #6 used on
  this dataset (±3.0), 6× the published SEs (0.5/0.4), and tighter than glass's ±4.0
  because ionosphere's published SEs are half of glass's.
- Standardized drift per PREREG_DRIFT.md: 3-master-seed mean |reproduced − published| pp
  (master seeds 0, 1, 2 seed the entire 100-iteration loop: splits, bootstraps, CV folds;
  per-iteration seed = master_seed·100000 + iteration index, identical to audit #14).
- Verdict rule: CONFIRMED iff all 3 master seeds land inside the bar on a row; rows judged
  separately; DISCREPANCY otherwise; COULD-NOT-RUN only for pre-run infrastructure blocks.
- **Secondary prediction** (exploratory, from the hypothesis + tracker state): at rubric
  3/5, at least one ionosphere row drifts above the score-2 ceiling (1.96 pp). This
  prediction has failed at score 3 before (audits #6, #13/glass-fastText, #14); it does
  not affect the verdict.
- Pinned implementation choices (recorded because rubric points 1, 2, 5 require the
  implementation to choose; all identical to audit #14's committed convention):
  sklearn 1.7.2 DecisionTreeClassifier, criterion=gini, min_samples_leaf=1; alpha
  candidates = {0} ∪ geometric means of consecutive cost_complexity_pruning_path alphas;
  selection = min error (CV mean for Row A, score on L for Row B), ties toward the larger
  alpha (simpler tree); 90/10 split unstratified with test = round(0.1·351) = 35 cases;
  bootstrap size = |L| = 316; classes encoded by np.unique ('b' < 'g'), so vote ties break
  to 'b' (bad); runner = `audits/audit_breiman96_bag_iono_run.py`, an audit-#14 dataset
  swap. Infra probe (outcome-independent, synthetic same-shape data, run-#3 precedent):
  ~8.3 s/iteration single-process → 100 iterations chunked ≤12 per call under the 45 s cap.

## Results

(EMPTY at pre-registration. To be filled in a separate commit AFTER the runs.)

## Honesty section

(EMPTY at pre-registration. To be filled with the results commit.)
