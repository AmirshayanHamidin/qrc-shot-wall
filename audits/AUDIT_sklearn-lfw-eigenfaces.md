# AUDIT: scikit-learn 1.9.0 docs — "Faces recognition example using eigenfaces and SVMs" (LFW), printed classification report

Program 2b confirmatory audit #20 (VAR). Session 2026-07-10, interactive continuation of run #18 (human present; same session as audit #19). Two-commit rule: this file is committed to the remote with an EMPTY results section BEFORE any reproduction code runs. Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

scikit-learn **1.9.0** stable documentation, example `auto_examples/applications/plot_face_recognition.html` ("Faces recognition example using eigenfaces and SVMs"), fetched this session (page md5 `e064b2810f18158d6b660dfb55d2ca17`, 120,168 bytes; page states "scikit-learn 1.9.0"). Pre-registered columns from the printed classification report (322 test samples):

- **Accuracy: published 0.84** (84 pp)
- **Weighted-avg F1: published 0.84** (84 pp)

Full printed report for the record — per-class (precision/recall/f1/support): Ariel Sharon 0.75/0.69/0.72/13, Colin Powell 0.72/0.87/0.79/60, Donald Rumsfeld 0.77/0.63/0.69/27, George W Bush 0.88/0.95/0.91/146, Gerhard Schroeder 0.95/0.80/0.87/25, Hugo Chavez 0.90/0.60/0.72/15, Tony Blair 0.93/0.75/0.83/36; accuracy 0.84/322; macro avg 0.84/0.75/0.79; weighted avg 0.85/0.84/0.84. Printed best estimator: SVC(C=76823.03433306457, class_weight='balanced', gamma=0.0034189458230957995).

Why this target: it is BOTH open named candidates from run #18's tracker at once — the LFW eigenfaces docs table (open queue item since run #3) AND a score-0/1 anchor outside the certified-values class (the tracker's #1 coverage gap; the two existing score-≤1 points are svmguide1's fully-pinned column and the NIST certified values). It is also the largest dataset in the program so far (233 MB archive, 13,233-image corpus, 1,288 used) — the feasibility risk (download vs the 45-s cap) was probed BEFORE this registration: 4.5 MB/s measured, resumable chunked download pre-declared.

## Published procedure (transcribed from the example page)

`fetch_lfw_people(min_faces_per_person=70, resize=0.4)` → stated printout: n_samples 1288, n_features 1850, n_classes 7. `train_test_split(test_size=0.25, random_state=42)` → 966 train / 322 test. `StandardScaler()` fit on train. `PCA(n_components=150, svd_solver="randomized", whiten=True)` fit on train (**no random_state**). `RandomizedSearchCV(SVC(kernel="rbf", class_weight="balanced"), {"C": loguniform(1e3, 1e5), "gamma": loguniform(1e-4, 1e-1)}, n_iter=10)` (**no random_state**, default 5-fold CV), fit on the 150-dim PCA features; `classification_report` on the test set.

## Blind discretion rubric (scored BEFORE running any code, from the example page + scikit-learn docs only)

Score: **1/5** (both columns; identical profile — the report's two summary numbers share one pipeline).

1. **Tie-breaking / randomization — 1.** The two stochastic components are UNSEEDED in the published code: the randomized-SVD PCA and RandomizedSearchCV's 10 hyperparameter draws both consume the global numpy RNG, whose state at docs build time is unrecoverable. The printed best (C, gamma) is one unreproducible draw; a reproducer must choose the RNG realization.
2. **Regularization / smoothing defaults — 0.** C and gamma are searched over fully specified distributions; SVC's remaining defaults (tol=1e-3, shrinking) are stable across the version gap.
3. **Initialization — 0.** PCA's randomized-solver initialization is the same RNG draw counted in point 1; SVC has no initialization.
4. **Stopping criteria / tolerances — 0.** libsvm's stopping rule and default tol pinned by the library, unchanged 1.7→1.9.
5. **Preprocessing / split construction — 0.** Everything is pinned by the published code: dataset selector (min_faces_per_person=70), resize=0.4, seeded split (random_state=42, test_size=0.25), StandardScaler, n_components=150. The split and class supports are fully deterministic.

## Data

LFW funneled archive, scikit-learn's own pinned source: figshare file **5976015** (`lfw-funneled.tgz`, ~233 MB), sha256 **`b47c8422c8cded889dc5a13418c4bc2abbda121092b3533a83306f90d900100a`** — this is the checksum hard-coded in `sklearn.datasets._lfw.FUNNELED_ARCHIVE`, and the runner asserts the downloaded file against it (the library's pin, not ours). Download in resumable chunks (`curl -C -`) under the 45-s cap, pre-extracted with tar before fetching; `fetch_lfw_people(..., download_if_missing=False)` then loads from disk.

## Reproduction plan (pinned before running)

The unseeded global-RNG realization is the ONLY free choice; it is pinned as: per master seed m ∈ {0 (primary), 1, 2}, call `np.random.seed(m)` once, immediately before the PCA fit, then run the example's pipeline exactly as printed (PCA then RandomizedSearchCV both drawing from the global stream). Report per seed: test accuracy and weighted-avg F1 (×100, pp), plus the drawn (C, gamma) candidates and the best. Program 2b standardized drift = mean over the 3 seeds of |reproduced − 84| pp, per column. Parallelism (`n_jobs`) may be used for the CV fits if the 45-s cap requires it — it changes scheduling only, not draws or results; if used it will be disclosed. Environment: scikit-learn 1.7.2 (1.9.0 requires a newer Python than this sandbox's 3.10 — the pip index tops out at 1.7.2; pre-declared version gap, same class as audits #3 and #12, both of which reproduced docs tables across gaps at ≈0 drift). Runner: `audits/audit_lfw_eigenfaces_run.py` (committed with results).

**Deterministic anchors (non-verdict, must match EXACTLY or the run is invalid rather than drifted):** n_samples 1288, n_features 1850, n_classes 7, 966 train / 322 test, per-class test supports (13, 60, 27, 146, 25, 15, 36). These are seed-independent given the pinned split.

## Pre-registered tolerance and verdict rule

- Expected value: the published 84 / 84 pp (no directional prediction).
- **CONFIRMED** if BOTH columns satisfy |reproduced − published| ≤ **3.0 pp** (seed-0 primary); **DISCREPANCY** if either exceeds; **COULD-NOT-RUN** if the download, the 45-s cap, or a deterministic-anchor mismatch blocks a faithful execution. Bar rationale: the sole discretion point is run-to-run randomization variance of an unseeded 10-draw search over wide loguniform ranges plus randomized SVD — plausibly worth 1–3 pp on a 322-sample test set (1 test case = 0.31 pp), larger than the near-zero drift of the fully-pinned docs targets (#3, #12) but bounded by CV's protection against bad draws. Bars will not be moved after data.

Secondary (non-verdict) prediction, logged for the discretion-drift hypothesis: at score 1, both 3-seed standardized drifts land ≤ the running score-2 ceiling (**1.96 pp**, audit #5). This is a real test of the low end of the hypothesis: unlike the existing score-1 point (svmguide1, 0.00 pp), this target's single rubric point is live randomization, so a FAIL here would say one unseeded search can out-drift all pinned-seed discretion — worth knowing either way.

## Results

(EMPTY at pre-registration — filled only in the results commit.)

## Honesty section

(EMPTY at pre-registration — filled only in the results commit.)
