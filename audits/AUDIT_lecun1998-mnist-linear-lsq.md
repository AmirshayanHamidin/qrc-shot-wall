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

(EMPTY at pre-registration — filled in a separate commit after the run.)

## Honesty section

(EMPTY at pre-registration.)
