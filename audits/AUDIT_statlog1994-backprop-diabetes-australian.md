# AUDIT: StatLog (Michie, Spiegelhalter & Taylor 1994) Backprop rows — diabetes + Australian credit

Program 2b confirmatory audit #28 (VAR). Session 2026-07-11 (Program 2b run #28). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

D. Michie, D. J. Spiegelhalter & C. C. Taylor (eds), *Machine Learning, Neural and Statistical Classification*, Ellis Horwood, 1994 — the StatLog project book. **Primary source fetched and read this session** (the book is out of print; copyright reverted to the editors, who placed the full text online at `www1.maths.leeds.ac.uk/~charles/statlog/` — legally public, retrieved via the Internet Archive snapshot of `whole.pdf`, 1 787 416 B, and text-extracted locally).

Two rows, both the **Backprop** (multilayer perceptron) test error rate:

- **Diabetes (Table 9.20, §9.5.2): published test error 0.248** (train 0.198, rank 7 of 23). Protocol stated: *"Twelve–fold cross validation was used to estimate prediction accuracy"*; 768 observations, 8 attributes, 2 classes.
- **Australian credit (Table 9.3, §9.2.2): published test error 0.154** (train 0.087, rank 11 of 22). Protocol stated: 690 observations, 14 attributes, 2 classes, **10-fold cross-validation**; StatLog states it *"replaced the missing values by the overall medians or means (5% of the examples had some missing information)"* and distributed the imputed file.

What the book says about its Backprop implementation (all of it, verbatim in substance): it is an external neural-network software package (§11.5.1) providing "a special purpose 3-layer MLP ... and general MLP with architecture specified at runtime"; and (§7.4) *"cross-validation was used by Backprop in finding the optimal number of nodes in the hidden layer"*. The chosen hidden-node count is **never published for either row**. Learning rate, momentum, weight initialisation, epoch count, stopping rule, and input scaling are **not stated anywhere for either row**.

Why this target: **the score-5 bucket is the program's single thinnest cell — it holds exactly ONE point** (audit #8's Sigillito perceptron, 1.11 pp), and the tracker's standing priority is score-4/5 density. Backprop-in-StatLog is the cleanest genuinely-5/5 claim class available: a published point estimate produced by an unpublished neural-network configuration, on two small CPU-scale public datasets, under a fully-specified resampling protocol. Two rows from one paper give two score-5 points in one audit. New claim class (multi-lab benchmark-consortium table) and new decade anchor (1994) for the set.

NOT audited, decided now before rubric scoring: every other row of both tables (Discrim, Quadisc, Logdisc, CART, k-NN, NaiveBay, ... ) — they are lower-discretion rows and the tracker does not need more score-2/3 points; and RBF/LVQ/Kohonen/DIPOL92/ALLOC80/SMART/CASTLE/ITrule/Cal5/CN2/NewID/Baytree/IndCART/C4.5, which have no scikit-learn default estimator without inventing one (same exclusion rule as audits #7 and #8).

## Data checks (counting only — done BEFORE this commit, no reproduction code run)

- **Diabetes:** OpenML id 37 ARFF, md5 `3cbaa3e54586aa88cf6aacb4033e4470` — **byte-identical to the file audits #19/#24 already pinned** in this repo. 768 rows; 500 `tested_negative` / 268 `tested_positive` — exactly StatLog's stated "500 examples of class 1 and 268 of class 2".
- **Australian credit:** UCI `statlog/australian/australian.dat`, md5 `b6fe154b62a8eb00277acec95b608590`, 28 735 B. 690 rows × 15 columns (14 attributes + class), no missing values (consistent with StatLog's stated median/mean imputation, i.e. this IS the distributed imputed file); class distribution 383 / 307.
- Pre-run arithmetic note (flagged now, not after data): StatLog's "Default" (majority-class) rows are 0.350 for diabetes and 0.440 for Australian, while the whole-file majority-class error rates are 268/768 = **0.349** and 307/690 = **0.445**. Both differ from the published Default in the 3rd decimal, which suggests the book's Default row — like every other row — is a **mean over the CV folds**, not a whole-file figure. This is a consistency check on the datasets, and it corroborates that these are the StatLog files.

## Blind discretion rubric (scored from the book + scikit-learn 1.7 docs ONLY, before any code)

**Both rows — score 5/5.** The rows share one algorithm and one (unpublished) implementation, so the discretion profile is identical; each row still contributes its own (score, |drift|) point per `PREREG_DRIFT.md`.

1. **Tie-breaking / randomization — 1.** No seed is given for anything: not the CV fold assignment (the book states only the number of folds), not the weight-init RNG, not the presentation/shuffle order. sklearn's `MLPClassifier` shuffles each epoch under its own `random_state`, and `KFold` needs a `random_state` to partition.
2. **Regularization / smoothing defaults — 1.** No weight decay, penalty, or early-stopping-as-regularization is stated. The library must default (`alpha=1e-4`).
3. **Initialization — 1.** Starting weights never specified — no distribution, no scheme, and the package's own default is not documented in the book. sklearn defaults to Glorot-style uniform.
4. **Stopping criteria / tolerances — 1.** No epoch count, no tolerance, no learning-rate schedule for either row. The book says training time was one of Backprop's "essentially two free parameters" and was tuned — but the value is never published for these datasets. sklearn defaults (`max_iter=200`, `tol=1e-4`, `n_iter_no_change=10`, `solver='adam'`, `learning_rate_init=1e-3`) must decide.
5. **Preprocessing assumptions — 1.** Input scaling is never stated, and it is the single most consequential unstated choice for an MLP (sklearn's own docs: *"Multi-layer Perceptron is sensitive to feature scaling"*). Additionally: for Australian credit, the integer-coded categorical attributes (A1, A4, A5, A6, A8, A9, A11, A12) are distributed as integers and whether Backprop consumed them raw or one-hot-encoded is unstated; for diabetes, the handling of the biologically-impossible zeros (glucose/pressure/skinfold/insulin/BMI) is unstated.

Discretion axis NOT captured by the frozen 5-point rubric, recorded for honesty: the **hidden-layer size** was CV-tuned by StatLog but never published, so architecture is a sixth free axis here. The rubric is fixed by `PREREG_DRIFT.md` and is NOT extended post hoc; this axis is simply noted, and it means 5/5 is if anything an *under*-count of this target's discretion.

## Reproduction plan (pinned before running)

Per master seed m ∈ {0, 1, 2} (seed 0 primary for the verdict; tracker drift per row = 3-seed mean |reproduced − published|):

1. Load the md5-pinned files above. Diabetes: 8 float features, y = the two class strings. Australian: 14 features as distributed (integer-coded categoricals kept as numeric — the file StatLog itself circulated), y = last column.
2. **Primary configuration — the faithful modern default:** `Pipeline(StandardScaler(), MLPClassifier(random_state=m))`, every other `MLPClassifier` argument left at its library default (`hidden_layer_sizes=(100,)`, `activation='relu'`, `solver='adam'`, `alpha=1e-4`, `learning_rate_init=1e-3`, `max_iter=200`, `shuffle=True`, `tol=1e-4`, `n_iter_no_change=10`). The scaler is fit on the **training fold only** (no leakage). Rationale, pinned now: the rubric permits consulting the library's docs, and scikit-learn's MLP documentation explicitly prescribes standardization — so scaler+defaults, not bare defaults, is the honest "what a competent modern reproducer would run" pipeline. The bare-defaults (unscaled) variant is run as a **labelled sensitivity check**, never as the verdict.
3. **Resampling:** `KFold(n_splits=12, shuffle=True, random_state=m)` for diabetes and `KFold(n_splits=10, shuffle=True, random_state=m)` for Australian — unstratified, because the book states a fold count and nothing else. Row value = 100 × mean over folds of the fold test error rate.
4. Convergence warnings (if `max_iter=200` is hit) are **counted and reported**, not suppressed and not fixed by raising `max_iter` — raising it would be moving a defaulted choice after seeing data.
5. Labelled sensitivity checks (reported, never the verdict): (a) **no scaler** — raw features into `MLPClassifier` defaults; (b) `StratifiedKFold` instead of `KFold`; (c) Australian with the 8 categorical columns **one-hot encoded**; (d) diabetes with the impossible zeros treated as missing and median-imputed (train-fold medians).

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (24.8 pp error for diabetes; 15.4 pp for Australian).
- **Tolerance: ±5.0 pp on both rows** (primary configuration, master seed 0). This is the score-5 bar set by precedent in audit #8 (Sigillito perceptron, also 5/5): bars in this program are priced by the blind rubric score, declared before data, and never moved after.
- **CONFIRMED** if BOTH rows satisfy |reproduced − published| ≤ 5.0 pp at seed 0 in the primary configuration; **DISCREPANCY** if either row exceeds; **COULD-NOT-RUN** if data access or the 45 s sandbox cap blocks execution.
- **Secondary pre-registered prediction A (hypothesis-consistent, direct re-test of the clause that FAILED in audit #8):** both rows' 3-seed drift is **strictly greater than 1.96 pp**, the largest score-2 drift currently in the confirmatory set. Audit #8 — the only prior score-5 point — failed exactly this clause at 1.11 pp. If these two rows also land below 1.96 pp, that is a second and third independent strike against the hypothesis at the high-discretion end, and it will be reported as such.
- **Secondary pre-registered prediction B (mechanism probe):** for BOTH rows, the **unscaled** sensitivity configuration's |drift| is strictly greater than the scaled primary's |drift|. This tests whether rubric point 5 (preprocessing discretion) is a *live* drift driver on this target or an inert checkbox — the rubric counts unspecified choices, but only choices that actually move the number can produce the correlation the program is testing.

Tracker context at registration (n = 27, 61 points, exploratory rho 0.532): score 5 holds **1** point, scores 4–5 together hold 21, score 2 holds 18, score 3 holds 16. These two rows are pre-registered to land at score 5 and will take that bucket from 1 point to 3.

## Results

*(EMPTY — to be filled in commit 2, after the reproduction runs. Nothing below this line exists at the time of the pre-registration commit.)*

## Verdict

*(EMPTY — commit 2.)*

## Environment

*(EMPTY — commit 2.)*

## Honesty section

*(EMPTY — commit 2.)*
