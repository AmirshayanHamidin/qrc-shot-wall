# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, diabetes rows — e_S and e_B
## Program 2b confirmatory audit #24 — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: PRE-REGISTERED, results pending.** This file is committed with an EMPTY results
section BEFORE any reproduction code runs (two-commit rule + run #2 guardrail).

## Claim

Breiman, L. (1996). "Bagging Predictors", *Machine Learning* 24, 123–140, Table 2
(Misclassification Rates %), diabetes dataset rows:

- **Row A — e_S = 25.3** : single classification tree, grown on the learning set and pruned
  by 10-fold cross-validation (Section 2.1 step ii).
- **Row B — e_B = 23.9** : bagging, 50 bootstrap replicates, each tree grown on the replicate
  and its best pruned subtree selected using the ORIGINAL learning set L as test set
  (Section 4.3); plurality vote, ties broken toward the lowest class label (step iv).

Procedure (Section 2.1): the 768-case diabetes data is divided at random into 10% test /
90% learning; e_S and e_B are measured on the test set; the random division is repeated 100
times and the reported numbers are means over the 100 iterations. Published SEs (Table 3):
0.4 (e_S), 0.4 (e_B). Published decrease: 6% — the paper's smallest, which Breiman
conjectures is because bagging is already "pushing close to the minimal attainable error
rate" (he cites 22.3% as the best of 22 classifiers in Michie et al. 1994). Min node size 1
"throughout" (p. 126). Primary source: Springer PDF
(link.springer.com/content/pdf/10.1007/BF00058655.pdf), fetched and read this session
(NOTE: the Berkeley TR-421 PDF at stat.berkeley.edu/~breiman/bagging.pdf is a DIFFERENT
version — no ionosphere row, diabetes duplicated to 1036 cases with a 250-case test set,
e_S 23.4 / e_B 18.8. The journal version audited here uses the raw 768 cases; the two must
not be mixed).

Dataset: Pima Indians diabetes (Smith et al. 1988), 768 cases, 8 features, 2 classes
(positive 268 / negative 500 — counts stated in the paper's Appendix). The original UCI
entry is withdrawn; per audit #19's pinned provenance, the OpenML id 37 ARFF (licence
Public) is used, expected md5 **3cbaa3e54586aa88cf6aacb4033e4470** — verified identical at
download this session, and class counts verified at load (268 tested_positive /
500 tested_negative).

Cross-paper anchors (recorded, not bars): audits #14/#22 reproduced this paper's glass and
ionosphere rows at 0.95/1.37 and 0.32/0.39 pp drift; audit #19 reproduced Breiman-2001
Forest-RI on this same diabetes data at 0.46/0.33 pp drift (test sets of this size were the
ladder's quietest).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the paper + scikit-learn 1.7.2 docs only. Same discretion profile as audits
#14/#22 (same paper, same §2.1/§4.3 procedure; only the dataset changes). Both rows: **3/5**.

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
   rounding of "10% of 768" (76 vs 77) unspecified, class-label ordering for the vote
   tie-break unspecified (the paper says "lowest class label" but never numbers the
   positive/negative classes); the Pima data's physiologically impossible zeros (glucose,
   blood pressure, BMI) are famously treated as either valid values or missing codes by
   different reproductions — the paper says nothing, and the raw-values reading is adopted
   here as the least-intervention default.

## Pre-registration (numeric bars, never moved after data)

- Expected values: **e_S = 25.3**, **e_B = 23.9** (percentage points, misclassification).
- **Tolerance: ±2.5 pp** on each row, seed-0 primary — scaled to this row's published SEs
  (0.4/0.4) by the same reasoning that set ionosphere's ±3.0 at SEs 0.5/0.4 and glass's
  ±4.0 at 1.1/0.9; tighter than both because diabetes has the family's largest test set
  (77 cases) and smallest published SEs.
- Standardized drift per PREREG_DRIFT.md: 3-master-seed mean |reproduced − published| pp
  (master seeds 0, 1, 2 seed the entire 100-iteration loop: splits, bootstraps, CV folds;
  per-iteration seed = master_seed·100000 + iteration index, identical to audits #14/#22).
- Verdict rule: CONFIRMED iff all 3 master seeds land inside the bar on a row; rows judged
  separately; DISCREPANCY otherwise; COULD-NOT-RUN only for pre-run infrastructure blocks.
- **Secondary prediction** (exploratory, from the hypothesis + tracker state): at rubric
  3/5, at least one diabetes row drifts above the score-2 ceiling (1.96 pp). This
  prediction has failed at score 3 in audits #6, #13, #14, and #22; it does not affect
  the verdict.
- Pinned implementation choices (recorded because rubric points 1, 2, 5 require the
  implementation to choose; all identical to audits #14/#22's committed convention):
  sklearn 1.7.2 DecisionTreeClassifier, criterion=gini, min_samples_leaf=1; alpha
  candidates = {0} ∪ geometric means of consecutive cost_complexity_pruning_path alphas;
  selection = min error (CV mean for Row A, score on L for Row B), ties toward the larger
  alpha (simpler tree); 90/10 split unstratified with test = round(0.1·768) = 77 cases;
  bootstrap size = |L| = 691; classes encoded by np.unique ('tested_negative' <
  'tested_positive'), so vote ties break to tested_negative; runner =
  `audits/audit_breiman96_bag_diabetes_run.py`, an audit-#22 dataset swap. Infra probe
  (outcome-independent, synthetic same-shape data, run-#3 precedent): ~9.8 s/iteration
  single-process → 100 iterations chunked ≤5 per call (Pool(2)) under the 45 s cap.

## Results

(EMPTY at pre-registration — to be filled in a separate commit after the runs.)

## Honesty section

(EMPTY at pre-registration — to be filled with the results commit.)
