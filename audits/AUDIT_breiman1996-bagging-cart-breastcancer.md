# AUDIT: Breiman (1996) "Bagging Predictors", Table 2, breast cancer rows — e_S and e_B
## Program 2b confirmatory audit #26 — PRE-REGISTRATION FIRST, per audits/PREREG_DRIFT.md

**Status: PRE-REGISTERED — results pending.** This commit lands the rubric + numeric bars
with an EMPTY results section; the reproduction numbers are added only in a separate later
commit (two-commit rule + run #2 guardrail: prereg web-committed and byte-verified BEFORE
any reproduction code runs on the real data).

## Claim

Breiman, L. (1996). "Bagging Predictors", *Machine Learning* 24, 123–140, Table 2
(Misclassification Rates %), breast cancer (Wisconsin) dataset rows:

- **Row A — e_S = 5.9** : single classification tree, grown on the learning set and pruned
  by 10-fold cross-validation (Section 2.1 step ii).
- **Row B — e_B = 3.7** : bagging, 50 bootstrap replicates, each tree grown on the replicate
  and its best pruned subtree selected using the ORIGINAL learning set L as test set
  (Section 4.3); plurality vote, ties broken toward the lowest class label (step iv).

Procedure (Section 2.1): the 699-case breast cancer data is divided at random into 10% test /
90% learning; e_S and e_B are measured on the test set; the random division is repeated 100
times and the reported numbers are means over the 100 iterations. Published SEs (Table 3):
0.3 (e_S), 0.2 (e_B) — the family's smallest. Published decrease: 37%. Min node size 1
"throughout" (p. 126). Primary source: Springer PDF
(link.springer.com/content/pdf/10.1007/BF00058655.pdf), fetched and read this session;
Appendix confirms 699 cases, 458 benign / 241 malignant, 9 cellular features.

Dataset: Breast Cancer Wisconsin (Original) (Wolberg & Mangasarian 1990; UCI
`breast-cancer-wisconsin.data`), 699 cases, 9 features (values 1–10), 2 classes
(benign 458 / malignant 241 — counts stated in the paper's Appendix and verified at load).
Column 0 is a sample-code ID (dropped); column 10 is the class (2 = benign, 4 = malignant).
The file has **16 missing values** (`?`), all in feature 6 (Bare Nuclei). md5 of the pinned
raw UCI file: **52b89051b9bd37a91a54e8570b963719** — verified identical at download this
session, and class counts (458/241) verified at load.

Cross-paper anchors (recorded, not bars): audits #14/#22/#24 reproduced this paper's glass,
ionosphere, and diabetes rows at 0.95/1.37, 0.32/0.39, and 0.64/0.28 pp drift respectively;
the Breiman-1996 CART-bagging ladder has been the program's most portable family. This row
adds the ladder's lowest published error (5.9/3.7), a stated run-#23 priority
(a low-published-error score-3 target to probe the floor-headroom confounder).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the paper + scikit-learn 1.7.2 docs only. Same discretion profile as audits
#14/#22/#24 (same paper, same §2.1/§4.3 procedure; only the dataset changes — plus this
dataset's 16 missing cells, which fall under preprocessing point 5, already scored 1).
Both rows: **3/5**.

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
5. **Preprocessing assumptions — 1**: stratification of the 90/10 split unspecified;
   rounding of "10% of 699" (69 vs 70) unspecified; **missing-value handling unspecified** —
   the paper describes filling soybean's missing values with modal values but says nothing
   about breast cancer's 16 missing Bare-Nuclei cells; drop-rows vs impute (mean/median/
   modal) is left entirely to the implementation. Class-label ordering for the vote
   tie-break is stated ("lowest class label") but the numbers assigned to benign/malignant
   are not; the raw UCI codes (2 < 4) are the least-intervention reading.

## Pre-registration (numeric bars, never moved after data)

- Expected values: **e_S = 5.9**, **e_B = 3.7** (percentage points, misclassification).
- **Tolerance: ±2.0 pp** on each row, seed-0 primary — the family's tightest bar, scaled to
  this row's published SEs (0.3/0.2, the smallest in Table 3) by the same monotone reasoning
  that set glass ±4.0 (SE 1.1/0.9), ionosphere ±3.0 (SE 0.5/0.4), and diabetes ±2.5
  (SE 0.4/0.4). Floor-headroom note (recorded pre-data, per run #23 honesty item 2): the low
  published errors (5.9/3.7) mechanically bound |drift| from below by distance to the 0 %
  floor, a candidate confounder the drift study will examine at n=30 — logged here because
  this target was chosen partly to add such a point.
- Standardized drift per PREREG_DRIFT.md: 3-master-seed mean |reproduced − published| pp
  (master seeds 0, 1, 2 seed the entire 100-iteration loop: splits, bootstraps, CV folds;
  per-iteration seed = master_seed·100000 + iteration index, identical to audits #14/#22/#24).
- Verdict rule: CONFIRMED iff all 3 master seeds land inside the bar on a row; rows judged
  separately; DISCREPANCY otherwise; COULD-NOT-RUN only for pre-run infrastructure blocks.
- **Secondary prediction** (exploratory, from the hypothesis + tracker state): at rubric
  3/5, at least one breast-cancer row drifts above the score-2 ceiling (1.96 pp). This
  prediction has failed at score 3 in audits #6, #13, #14, #22, and #24; it does not affect
  the verdict.
- Pinned implementation choices (recorded because rubric points 1, 2, 5 require the
  implementation to choose; all identical to audits #14/#22/#24's committed convention
  except the dataset-specific missing-value rule): sklearn 1.7.2 DecisionTreeClassifier,
  criterion=gini, min_samples_leaf=1; alpha candidates = {0} ∪ geometric means of
  consecutive cost_complexity_pruning_path alphas; selection = min error (CV mean for Row A,
  score on L for Row B), ties toward the larger alpha (simpler tree); 90/10 split
  unstratified with test = round(0.1·699) = 70 cases; bootstrap size = |L| = 629; classes
  encoded by np.unique ('2' < '4'), so vote ties break to benign. **Missing values:** all
  699 cases retained (matches the paper's Table 1 N); the 16 '?' Bare-Nuclei cells are
  median-imputed per iteration using the median of that feature over the LEARNING set L only
  (no test-set peeking) — the least-intervention default. Runner =
  `audits/audit_breiman96_bag_bcw_run.py`, an audit-#24 dataset swap. Infra probe
  (outcome-independent, synthetic same-shape random data, run-#3 precedent): ~8.4 s/iteration
  single-process → 100 iterations chunked ≤5 per call (Pool(2)) under the 45 s cap.

## Results

*(empty — to be filled in the second commit, after the run)*

## Honesty section

*(empty — to be filled in the second commit, after the run)*
