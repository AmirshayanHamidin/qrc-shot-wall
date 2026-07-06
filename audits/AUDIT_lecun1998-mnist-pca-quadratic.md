# Program 2b confirmatory audit #15 — LeCun, Bottou, Bengio & Haffner (1998), Fig. 9 "40 PCA + quadratic classifier" row, MNIST 3.3%

**Status: PRE-REGISTRATION (commit 1, empty results section).** Written and committed to the remote BEFORE any reproduction code for this audit existed, per the two-commit rule (RESEARCH_AGENDA.md, Program 2 method rules) and `audits/PREREG_DRIFT.md`.

## Claim under audit

Source: Y. LeCun, L. Bottou, Y. Bengio, P. Haffner, "Gradient-Based Learning Applied to Document Recognition," *Proc. IEEE* 86(11):2278-2324, 1998. Figure 9 ("Error rate on the test set (%) for various classification methods") lists the row **"40 PCA + quadratic" = 3.3%** test error on the regular (non-deslanted) MNIST test set (verified this session from the author PDF at yann.lecun.com/exdb/publis/pdf/lecun-98.pdf; Fig. 9 text row, grep-confirmed). The method: reduce each 28x28 = 784-pixel image to its **40 leading principal components**, then run a **quadratic (Gaussian) classifier** -- a per-class full-covariance Gaussian discriminant (QDA) -- on the 40-D features. Standard MNIST split: 60,000 train / 10,000 test.

This is the same primary source of record as Program 2b audits #4 and #5 (the "Linear" row, 12.0%); this audit takes a **different row with a different discretion profile** (dimensionality reduction + Gaussian classifier instead of a linear least-squares / SGD fit).

Measurand: **test-set error rate in percentage points** (the figure's own metric). Published value **3.3**.

## Blind discretion rubric (scored from paper + sklearn docs, BEFORE running any code)

Scoring `sklearn.decomposition.PCA` + `sklearn.discriminant_analysis.QuadraticDiscriminantAnalysis` as the reproducing implementation.

1. **Tie-breaking / randomization -- 1.** The paper specifies "40 principal components" but not the SVD algorithm. sklearn PCA `svd_solver='auto'` selects the **randomized** solver for a 60000x784 matrix with n_components=40 (n_components < 0.8*min(n,p) and max dim > 500), which draws a random projection seeded by `random_state` (and uses `n_iter=4` power iterations). So the reproducing library introduces a randomization choice the paper leaves open. **Point.**
2. **Regularization / smoothing defaults -- 1.** A quadratic/Gaussian classifier needs a per-class covariance; the paper states no covariance regularization or shrinkage. sklearn QDA exposes `reg_param` (default **0.0**) and an internal `tol` for rank; the library must default the covariance conditioning. **Point.**
3. **Initialization -- 0.** PCA (eigendecomposition/SVD) and QDA (closed-form class means + covariances) have no iterative weight initialization. No point.
4. **Stopping criteria / tolerances -- 0.** No iterative optimization loop with a convergence criterion in either stage (the randomized SVD's fixed `n_iter=4` is a solver constant, scored under point 1, not a convergence tolerance). No point.
5. **Preprocessing assumptions -- 1.** Unspecified by the paper: pixel intensity scaling (0-255 vs [0,1]), whether PCA centers only or also standardizes per feature, whether whitening is applied, and the exact training set used to fit PCA. Each materially changes the 40-D representation fed to the Gaussian classifier. **Point.**

**Blind discretion score = 3 / 5** (points 1, 2, 5).

## Pinned implementation choices (fixed now, before running; these ARE the discretion the rubric flagged)

- Data: standard MNIST, 60,000 train / 10,000 test, loaded from the canonical idx-ubyte files (ossci-datasets S3 mirror, md5-checked against the known values).
- Pixel scaling: divide by 255.0 into [0,1].
- PCA: `PCA(n_components=40, svd_solver='randomized', random_state=SEED)`, fit on the 60k training images (default centering, `whiten=False`).
- Classifier: `QuadraticDiscriminantAnalysis()` with default `reg_param=0.0`, fit on the 40-D PCA train features, evaluated on the 40-D PCA-transformed 10k test set.
- Metric: test error % = 100 * (misclassified / 10000).

## Pre-registered expected value and tolerance (NEVER moved after data)

- **Expected reproduced test error ~ 3.3%**, i.e. drift near zero, with the cross-implementation + preprocessing discretion (rubric 3/5) expected to move it modestly.
- **Pre-registered bar: +/-3.0 pp.** Verdict **CONFIRMED** if the 3-seed-mean |reproduced - 3.3| <= 3.0 pp; **DISCREPANCY** otherwise. Bar chosen a priori in line with prior score-3 audits (Breiman "One Tree" +/-3.0 pp).
- **Standardized drift** (per PREREG_DRIFT.md): |reproduced - 3.3| in pp, averaged over master seeds 0, 1, 2 (seed controls the PCA randomized-SVD `random_state`; QDA is deterministic given features).
- **Secondary prediction (recorded, not bar-moving):** the standardized drift will exceed the largest score-2 confirmatory drift so far (1.96 pp, LeCun-1998 linear-LSQ). This continues the "discretion predicts drift" ladder test at a mid score.

## Program 2b tracker context (at pre-registration time)

Confirmatory set n = 14/30 before this audit. This is a score-3 point; the confirmatory set currently holds few MNIST-scale points and this is the first PCA/dimensionality-reduction + Gaussian-classifier target. Honest note: it does NOT fill the standing score-4/5 density priority -- it was chosen for clean, deterministic, CPU-fast reproducibility from an already-cited primary source, landing one complete increment within the session's time and 45-s-per-call limits.

## RESULTS

*(empty -- to be filled in commit 2 after the 3-seed reproduction runs)*

## Honesty section

*(to be completed in commit 2: same-family/same-engine caveats, sensitivity checks on the flagged preprocessing/regularization discretion, and any bar-proximity notes)*

---
*Program 2b of the VAR initiative -- github.com/AmirshayanHamidin/qrc-shot-wall. Registered autonomously; VAR rule 6 (human sign-off) applies before any external claim.*
