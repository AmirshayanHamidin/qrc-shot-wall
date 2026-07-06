# AUDIT: Sigillito et al. (1989) ionosphere linear perceptron + Aha 1NN (ionosphere.names)

Program 2b confirmatory audit #8 (VAR). Session 2026-07-06 (Program 2b run #7). Two-commit rule: this file is committed to the REMOTE with an EMPTY results section BEFORE any reproduction code runs (run #2 guardrail). Governed by `audits/PREREG_DRIFT.md`.

## Claim under audit

Sigillito, V. G., Wing, S. P., Hutton, L. V., & Baker, K. B. (1989), "Classification of Radar Returns from the Ionosphere Using Neural Networks", *Johns Hopkins APL Technical Digest* 10(3), 262-266 — **primary source fetched and read this session** (jhuapl.edu techdigest, V10-N03) — plus the UCI `ionosphere.names` Past Usage section (fetched this session from archive.ics.uci.edu, 3116 B), which transcribes the paper's number and adds David Aha's follow-up.

From the paper (verbatim facts): training set = 200 returns (101 good, 99 bad); testing set = 150 returns (123 good, 27 bad); inputs = 34 values normalized to [-1, 1]; one output node, 1 = good, 0 = bad, decision threshold 0.5; the "linear" perceptron (no hidden units, identity output) is trained by "an iterative steepest-descent method (i.e., back propagation)" minimizing mean squared error; **"The linear perceptron was able to correctly classify 90.67% from the testing set."** From `ionosphere.names`: the split uses "the first 200 instances for training"; the file has 351 instances ("There was a counting error or some mistake somewhere; there are a total of 351 rather than 350 instances"); and **"He [David Aha] found that nearest neighbor attains an accuracy of 92.1%"** (no further protocol stated).

Rows audited (test-set percent correct, ionosphere, first-200 train):

- **Linear perceptron: published 90.67%** (paper; 118/123 good + 18/27 bad = 136/150).
- **Nearest neighbor (1NN): published 92.1%** (ionosphere.names, dataset-documentation claim class per the audit #7 wine precedent).

NOT audited, decided now before rubric scoring: the nonlinear perceptron 92% (sigmoid-output single unit — no matching sklearn default estimator without inventing one); backprop MLFN "average of over 96%, range 94-98%" (a bound/range, not a point measurand); Aha's C4 94.0% and IB3 96.7% (no scikit-learn C4/IB3; substituting would change the measurand — same reason audit #7 excluded RDA).

Why this target: the first EXECUTABLE high-discretion target (the only prior score-5, audit #4, was infrastructure-blocked) — training-set-size 200 makes every fit millisecond-scale, so the 45 s cap is irrelevant; adds a score-5/score-2 contrast inside one file; new family point (gradient-trained linear unit thresholded for classification, 1989); tracker priority is score-0/4/5 after score-2 oversampling.

## Split reading (pinned from claim arithmetic BEFORE any run)

Data file: canonical UCI `ionosphere.data` (351 rows, md5 `85649e5fb5b15fb9dab726c400be61fe`). Data checks done before this commit (counting only, no reproduction): rows 1-200 = 101 good / 99 bad — EXACTLY the paper's training composition; rows 201-350 = 123 good / 27 bad — EXACTLY the paper's testing composition; row 351 (class "good") is the counting-error extra the docs flag.

- **Perceptron row primary test set: rows 201-350** (150 instances; matches the paper's stated composition exactly). Sensitivity: all 151 remaining rows.
- **1NN row primary test set: rows 201-351** (all 151 remaining). Reason: 92.1% is arithmetically achievable only on 151 (139/151 = 92.05 -> 92.1); on 150 the nearest values are 92.00 and 92.67. Sensitivity: rows 201-350.

## Blind discretion rubric (scored from the paper + ionosphere.names + sklearn 1.7 docs ONLY, before any code)

**Linear perceptron row — score 5/5.**

1. Tie-breaking / randomization — **1**. No seeds anywhere; presentation order and update scheme (per-pattern vs batch) unspecified; sklearn's SGD shuffles each epoch with its own RNG.
2. Regularization / smoothing defaults — **1**. No penalty/weight decay stated; the library must default (sklearn SGDRegressor: penalty='l2', alpha=1e-4).
3. Initialization — **1**. Starting weights never specified for the perceptrons (the MLFN section says only "10 different starting networks", no distribution; sklearn defaults to zeros).
4. Stopping criteria / tolerances — **1**. "Eventually converged", learning curves drawn to 400 presentations — no epoch count, tolerance, or learning-rate schedule stated; library defaults (max_iter=1000, tol=1e-3, n_iter_no_change=5, invscaling eta0=0.01) must decide.
5. Preprocessing assumptions — **1**. The [-1,1] normalization is specified, but the mapping of the published train/test compositions onto file rows is not in the paper (the "first 200" reading comes from the dataset docs, and the docs' own counting error leaves a 150-vs-151 test ambiguity) — split construction requires implementation decisions.

**1NN row — score 2/5.**

1. Tie-breaking / randomization — **1**. Distance ties among candidate nearest neighbours are handled implementation-privately (sklearn: lowest index); no other randomness.
2. Regularization / smoothing defaults — **0**. None.
3. Initialization — **0**. 4. Stopping — **0**.
5. Preprocessing assumptions — **1**. Aha's evaluation protocol is not restated (same-split assumption), the 150-vs-151 ambiguity applies, and the distance metric is unstated (Euclidean assumed).

## Reproduction plan (pinned before running)

Per master seed m in {0, 1, 2} (seed 0 primary for the verdict; drift for the tracker = 3-seed mean |reproduced - published| per row):

1. Load `ionosphere.data` (md5 above). X = 34 float features as-is (already [-1,1] per the paper and the file), y = 1 for "g", 0 for "b" (the paper's coding). Train = rows 1-200.
2. **Perceptron row:** `sklearn.linear_model.SGDRegressor(random_state=m)` — ALL defaults (loss='squared_error', penalty='l2', alpha=1e-4, learning_rate='invscaling', eta0=0.01, max_iter=1000, tol=1e-3, shuffle=True). This is the faithful modern default for the paper's specified procedure (linear output unit, squared error, iterative steepest descent); prediction = (y_hat >= 0.5) per the paper's threshold. Row value = 100 x accuracy on rows 201-350.
3. **1NN row:** `sklearn.neighbors.KNeighborsClassifier(n_neighbors=1)` — all defaults (minkowski p=2 = Euclidean, uniform weights). No RNG: bit-identity across seeds will be verified, not assumed. Row value = 100 x accuracy on rows 201-351.
4. Labelled sensitivity checks (reported, never the verdict): perceptron with penalty=None (removes the defaulted l2); perceptron on the 151-row test; 1NN on the 150-row test; 1NN on StandardScaler(z) features; perceptron training-set accuracy vs the paper's reported training convergence 87.5% (side observation only).

## Pre-registered tolerance and verdict rule

- **Expected values:** near published (90.67 for the perceptron; 92.1 for 1NN). One test case = 0.667 pp (150) / 0.662 pp (151).
- **Tolerance: perceptron row +/-5.0 pp; 1NN row +/-2.0 pp** (primary configuration, master seed 0). The wide perceptron bar prices a score-5 discretion profile (as the Gorman audit's +/-5.0 did for score 3); the 1NN bar allows ~3 flipped test cases.
- **CONFIRMED** if BOTH rows satisfy |reproduced - published| <= bar at seed 0 in the primary configuration; **DISCREPANCY** if either row exceeds; **COULD-NOT-RUN** if data access or the 45 s cap blocks execution. Bars never move after data.
- Secondary pre-registered prediction (hypothesis-consistent direction): the perceptron row's 3-seed drift (score 5) is STRICTLY GREATER than the 1NN row's 3-seed drift (score 2), and greater than 1.96 pp (the current largest score-2 drift in the set).

## Results

(EMPTY at pre-registration commit. Filled only after the runs, in a separate commit.)

## Verdict

(EMPTY at pre-registration commit.)

## Environment

(To be recorded with results.)

## Honesty section

(To be completed with results; will include at minimum: the estimator-mapping decision — SGDRegressor as the modern default for a squared-error linear unit; the split-reading decisions above, which rest partly on dataset-doc glosses and claim arithmetic rather than the paper alone; the 1NN row's dataset-documentation provenance class; and the non-independence of two rows sharing one dataset and split.)
