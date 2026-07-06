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

Data check: `ionosphere.data` md5 `85649e5fb5b15fb9dab726c400be61fe`, 351 rows; train rows 1-200 = 101 good / 99 bad (paper: 101/99); test rows 201-350 = 123 good / 27 bad (paper: 123/27); rows 201-351 = 124 good / 27 bad. Split reading confirmed exactly as pinned.

Primary configurations (library defaults, master seed 0):

| Row | Published | Reproduced | Drift | Correct (repro vs implied) |
|---|---|---|---|---|
| Linear perceptron (test rows 201-350) | 90.67 | **91.333** | +0.663 pp | 137/150 vs 136/150 |
| 1NN (test rows 201-351) | 92.1 | **92.053** | -0.047 pp | 139/151 vs 139/151 |

Master seeds 1 and 2: perceptron 92.667 / 91.333 (SGD shuffle order is the only live RNG; `n_iter_` = 12/12/14 of max 1000 - default tol=1e-3 stops training early); 1NN bit-identical across all three seeds, as expected for a no-RNG pipeline (verified). **Standardized drift for the tracker (3-seed mean |reproduced - published|): perceptron 1.11 pp, 1NN 0.05 pp.**

The 1NN row reproduces the implied published correct count EXACTLY (139 of 151) - strong evidence that Aha used precisely this split and Euclidean metric on the raw features. The perceptron row lands one test case above the paper's 136/150.

Labelled sensitivity checks:

- Perceptron, penalty=None: identical to primary at every seed (91.333 / 92.667 / 91.333) - the defaulted l2 (alpha=1e-4) is numerically inert here.
- Perceptron on all 151 remaining rows: 91.391 / 92.715 / 91.391 - within 0.06 pp of primary; the 150-vs-151 ambiguity is immaterial for this row.
- 1NN on the 150-row test: 92.000 (138/150; the extra 151st case is a correctly-classified "good") - under this alternate reading the drift would be 0.10 pp, still far inside the bar.
- 1NN on z-scored features: identical to primary (92.053) - scaling discretion inert on this already-normalized data.
- Side observation (not part of the verdict): reproduced TRAINING accuracy 84.5 / 85.5 / 85.0 vs the paper's reported training convergence 87.5 - the modern default stops after ~12 epochs vs the paper's ~400 presentations, i.e. the reproduction is systematically less trained yet slightly EXCEEDS the published test number.

Secondary pre-registered prediction: **FAILED** (it was a conjunction and one clause failed). Clause 1 held: perceptron 3-seed drift 1.11 pp > 1NN 0.05 pp (score 5 > score 2 within the audit). Clause 2 failed: 1.11 pp is NOT greater than 1.96 pp (the largest score-2 drift in the set). The first executable score-5 point therefore lands BELOW the score-2 ceiling - evidence against the hypothesis at the high-discretion end, reported with the same prominence as the confirmations.

## Verdict

**CONFIRMED.** Both rows land within their pre-registered bars at master seed 0 in the primary configurations (perceptron +0.663 pp vs +/-5.0; 1NN -0.047 pp vs +/-2.0), robust across all 3 master seeds (worst perceptron seed: +2.00 pp). A 1989 gradient-trained linear unit and a 1980s nearest-neighbor number both reproduce under 2026 library defaults; the 1NN correct count is exact.

## Environment

Sandbox Linux (Ubuntu 22.04, CPU only), Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3. Reproduction script: `audits/audit_iono_perc1nn_run.py` (single pass, seconds - the 45 s cap never approached). Raw output (all configurations x 3 seeds + data check): `audits/iono_perc1nn_raw.json`. Both committed in this session's batch.

## Honesty section

1. Estimator mapping: the paper's "linear perceptron" is a linear output unit trained by iterative steepest descent on squared error - `SGDRegressor` + 0.5 threshold is the faithful modern-default route, but sklearn's schedule (invscaling eta0=0.01) and tol-based stop (n_iter_ ~ 12 epochs vs the paper's ~400 presentations) mean the reproduction is far less trained than the original. That this discretion barely moved the number (~1 pp) is the audit's finding, not an assumption.
2. Split reading: the paper never says WHICH 200 rows are the training set; "first 200" comes from ionosphere.names, and the docs' own counting error leaves a 150-vs-151 test ambiguity. Both pinned readings were resolved before running (paper-composition 150 for the perceptron; the only-arithmetically-consistent 151 for 1NN) and the sensitivity checks show the choice moves nothing materially (max 0.10 pp).
3. Provenance split: the perceptron number was verified against the fetched primary source (JHU APL Technical Digest PDF, read this session); the 1NN number exists only in the dataset documentation with no stated protocol (same claim class as audit #7's wine rows) - the exact 139/151 match is post-hoc corroboration of the protocol guess, not pre-registered knowledge.
4. The two (score, drift) points share one dataset and one split, so they are not independent - same caveat as every prior multi-row audit in the set.
5. Two-commit ordering: pre-registration was committed to the REMOTE (`e5decc2`, verified byte-identical at 8333 B by SHA-pinned fetch) before any reproduction code existed; results were computed afterwards in this same session.
6. Commit-dialog autofill: GitHub's Copilot pre-filled a commit message and extended description for the prereg commit; both were replaced/cleared and DOM-verified before submitting (the committed message is the registered one, with no appended description).
7. The secondary prediction's failure is informative, not embarrassing: at rubric 5/5 the hypothesis expects large drift, and this target delivered 1.11 pp. One low-drift score-5 point does not refute the hypothesis (the confirmatory test waits for n=30), but it now bounds the high end from below.
8. The paper's 90.67% is itself a single training run of one network (no seed averaging in the original); comparing a 3-seed band (91.3-92.7) against a single historical draw is an unavoidable asymmetry of this claim class.
