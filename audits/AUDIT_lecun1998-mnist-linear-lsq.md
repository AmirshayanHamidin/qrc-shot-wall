# AUDIT: LeCun et al. (1998) — MNIST linear classifier via direct linear-system solve (Fig. 9 "Linear" = 12.0%)

Program 2b (VAR) replication audit — **confirmatory audit #5 (n=4 toward 30)** under `audits/PREREG_DRIFT.md`. Session 2026-07-06. Two-commit rule: this file is committed with rubric + pre-registration and EMPTY results BEFORE the reproduction runs (remote-first, per the run #2 guardrail). Companion to `audits/AUDIT_lecun1998-mnist-linear.md` (same published claim, gradient-descent route, COULD-NOT-RUN under the sandbox's 45 s per-call cap — see its honesty section; no reproduced number was observed there).

## Claim under audit

Same source as audit #4: LeCun, Bottou, Bengio & Haffner, Proc. IEEE 86(11), Nov 1998, Section VI.C.1 + Figure 9: **linear classifier on the regular MNIST test set, error 12.0%** (Fig. 9 marker "—— 12.0 ——>"; caption uncertainty ≈ 0.1%). The section states that "various combinations of sigmoid units, linear units, gradient descent learning and learning by **directly solving linear systems** gave similar results" — this audit reproduces the claim via that second published route: a regularized least-squares (one-vs-rest) linear classifier, the modern library's direct-solve linear classifier.

## Blind discretion rubric (scored from the paper + scikit-learn 1.7 RidgeClassifier docs BEFORE any least-squares code ran)

| # | Item | Score | Justification (one line) |
|---|---|---|---|
| 1 | Tie-breaking / randomization | 0 | Closed-form solve on the fixed published train/test split; no RNG anywhere in the pipeline. |
| 2 | Regularization / smoothing defaults | **1** | The paper states no ridge/damping term for the linear-systems solution; sklearn must default it (`RidgeClassifier` `alpha=1.0`). |
| 3 | Initialization | 0 | A direct solve has no initialization. |
| 4 | Stopping criteria / tolerances | 0 | Dense input under `solver='auto'` resolves to the Cholesky direct solver — no iteration cap or tolerance to default. |
| 5 | Preprocessing assumptions | **1** | Pixel scaling and target encoding are unspecified; the reproducer must choose (declared: float64 /255, library's ±1 one-vs-rest label binarization). |

**Discretion score: 2/5.** Recorded before the reproduction ran.

## Data

Identical to audit #4 (fetched and MD5-verified pre-registration there): canonical MNIST idx files from `ossci-datasets.s3.amazonaws.com/mnist/`, 60,000 train / 10,000 test, canonical MD5s listed in `AUDIT_lecun1998-mnist-linear.md`. No least-squares code has touched the data at pre-registration time.

## Reproduction plan (pinned before running)

scikit-learn 1.7.2 `RidgeClassifier()` — ALL parameters library defaults (`alpha=1.0`, `fit_intercept=True`, `solver='auto'` → Cholesky on dense input), one-vs-rest via the library's internal ±1 label binarization, matching the paper's "one output unit per class, highest sum incl. bias wins". Declared preprocessing (rubric item 5): pixels float64 /255. Metric: test error % on the 10,000 regular test images. The pipeline has no stochastic component; per PREREG_DRIFT.md it is executed identically under master seeds 0, 1, 2 (no API accepts a seed) and the standardized drift is the 3-run mean |reproduced − published| pp; identical outputs across seeds are expected and reported as procedural replicates. Environment: CPU only, Python 3.10.12, sklearn 1.7.2, numpy 2.2.6, scipy 1.15.3, Ubuntu 22.04 sandbox; single fit expected well under the 45 s cap.

## Pre-registered expected value, tolerance and verdict rule

- **Published value: 12.0% test error.**
- **Tolerance: ±2.0 pp absolute** (the bar used by confirmatory audits #1, #3, #4; not moved after data).
- **CONFIRMED** if |reproduced − 12.0| ≤ 2.0 pp (seed-0 primary); **DISCREPANCY** if outside; **COULD-NOT-RUN** on infrastructure block (not anticipated: one Cholesky solve of a 784×784 system).
- Honest prior, stated pre-run: plain one-vs-rest least squares on raw MNIST pixels is commonly reported around 13–15% error, so the reproduction may plausibly land 1–3 pp ABOVE the published 12.0 — i.e. this audit has a real chance of DISCREPANCY. The bar stays ±2.0 pp regardless.
- **Secondary (Program 2b, exploratory until n=30):** at score 2 the hypothesis predicts LOW drift (score-2 points so far: 0.00–0.94 pp). If drift lands near or above 2 pp, that is evidence AGAINST the hypothesis at the low-discretion end and will be reported as such.

## Results

Data check: idx files parsed to train (60000, 784) / test (10000, 784), classes 0–9; MD5s as pre-registered in audit #4's file.

| Published | Reproduced (replicates 0/1/2, bit-identical) | Drift |
|---|---|---|
| 12.0% test error | **13.96%** (1,396 / 10,000 test errors) | **1.96 pp** |

All three procedural replicates are bit-identical, as pre-registered for a deterministic pipeline (Cholesky solve; fit 1.1–3.4 s, far under the 45 s cap). **Program 2b standardized drift (3-run mean): 1.96 pp.**

**Verdict: CONFIRMED** — |13.96 − 12.0| = 1.96 pp ≤ 2.0 pp (pre-registered bar, not moved). This audit contributes the point **(2, 1.96)** to the confirmatory set (n=4 audits toward 30; 8 (score, drift) points total).

## Honesty section

- **The confirmation is marginal: drift is 98% of the bar.** A result 0.05 pp worse would have flipped the verdict to DISCREPANCY. The bar was fixed pre-run at ±2.0 pp (consistency with audits #1/#3/#4) and was not moved; the near-bar landing is reported with the same prominence as the verdict.
- The pre-run prior stated in the pre-registration ("commonly reported around 13–15%, real chance of DISCREPANCY") is consistent with the observed 13.96%; the CONFIRMED verdict reflects bar mechanics, not strong portability of the 1998 number to modern defaults.
- **Secondary reading (against the hypothesis at the low end):** 1.96 pp is the LARGEST score-2 drift in the confirmatory set (prior score-2 points: 0.00, 0.00, 0.59, 0.94). Under the pre-registered secondary note this counts as mild evidence AGAINST "discretion predicts drift" at the low-discretion end, and is logged as such in the tracker.
- Route caveat: the paper's primary training route for this claim was gradient descent on MSE (audit #4, COULD-NOT-RUN here); this audit reproduces the paper's own equally-claimed alternative ("directly solving linear systems gave similar results"). The 1.96 pp prices the modern default-resolved least-squares route (ridge alpha=1.0, /255 scaling, ±1 OvR targets) against the paper's 12.0%; the paper's linear-systems variant was itself under-specified (no ridge term stated).
- Environment: Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3, Ubuntu 22.04 sandbox, CPU only, 2 cores. Raw per-replicate rows in `audits/mnist_linear_lsq_raw.json`; runner script `audits/audit_mnist_linear_lsq_run.py` (executed inline this session with identical code; data paths as in audit #4).
- The 1998 claim itself is not challenged: 12.0% was presumably correct for the paper's implementation. As with audit #2, the drift prices the claim's *portability* to a modern library's defaults.
