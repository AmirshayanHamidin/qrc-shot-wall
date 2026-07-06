# AUDIT: LeCun, Bottou, Bengio & Haffner (1998) — MNIST linear-classifier baseline, Fig. 9 "Linear" row

Program 2b (VAR) replication audit — **confirmatory audit #4 (n=4 toward 30)** under `audits/PREREG_DRIFT.md`. Session 2026-07-06. Two-commit rule: this file is committed with rubric + pre-registration and an EMPTY results section BEFORE any experiment runs (guardrail from run #2: the pre-registration is web-committed to the remote before any reproduction code executes); results land in a separate later commit.

## Claim under audit

Y. LeCun, L. Bottou, Y. Bengio & P. Haffner, "Gradient-Based Learning Applied to Document Recognition", Proceedings of the IEEE 86(11):2278–2324, November 1998. Section VI.C.1 ("Linear Classifier, and Pairwise Linear Classifier") and Figure 9 (test-set error rates for all compared methods):

- **Linear classifier on the regular MNIST database: test error rate 12.0%** (Figure 9 bar labeled "Linear", off-scale marker "—— 12.0 ——>"; the section text states the error rate on the regular data and notes the classifier has 7,850 free parameters).

Verified this session from a public course mirror of the paper (vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf, fetched 2026-07-06): the extracted Figure 9 labels read "—— 12.0 ——>" for "Linear" (with 8.4 for [deslant] Linear and 7.6 for Pairwise, not audited here). The paper describes the classifier as a single layer, one output unit per class, each input pixel contributing to a weighted sum, highest sum (incl. bias) wins; trained by gradient descent on an MSE criterion, and explicitly notes that "various combinations of sigmoid units, linear units, gradient descent learning and learning by directly solving linear systems gave similar results". Figure 9's caption puts the uncertainty in the quoted error rates at about 0.1%.

Pre-registered scope: ONE column — the regular-data "Linear" row, 12.0% test error. This is a new algorithm family for the confirmatory set (single-layer linear model / MSE) and a deliberately HIGH-discretion target per the tracker's coverage note (confirmatory scores so far {1, 2, 3}; this target is scored 5/5 below).

## Blind discretion rubric (PREREG_DRIFT.md; scored from the paper + scikit-learn 1.7 SGDClassifier docs BEFORE any code ran)

| # | Item | Score | Justification (one line) |
|---|---|---|---|
| 1 | Tie-breaking / randomization | **1** | Training-example order, shuffling and any seed are nowhere specified for the linear net; the reproducing library shuffles per epoch (sklearn `shuffle=True`) with a seed the reproducer must fix. |
| 2 | Regularization / smoothing defaults | **1** | No weight decay / penalty is stated anywhere for the linear classifier; sklearn must default it (`penalty='l2'`, `alpha=1e-4`). |
| 3 | Initialization | **1** | Starting weights of the gradient-trained single-layer net are unspecified; the library fixes them (sklearn initializes coefficients to zeros). |
| 4 | Stopping criteria / tolerances | **1** | Number of passes / convergence rule for the linear net is not given (epoch counts are quoted only for LeNet); sklearn must default (`max_iter=1000`, `tol=1e-3`, `n_iter_no_change=5`). |
| 5 | Preprocessing assumptions | **1** | Pixel-value scaling and target encoding for the linear experiment are unspecified (the [-0.1, 1.175]-style input normalization is described for the LeNet experiments); the reproducer must choose the input range. |

**Discretion score: 5/5.** Recorded here before any reproduction code ran, per PREREG_DRIFT.md order of operations. Highest-discretion confirmatory point so far.

## Data

The four canonical MNIST idx files fetched pre-registration (cache-busted) from the public PyTorch-infra mirror `ossci-datasets.s3.amazonaws.com/mnist/`: train 60,000 / test 10,000, 28×28 grayscale. MD5s (gzipped) match the canonical values: `train-images f68b3c2dcbeaaa9fbdd348bbdeb94873`, `train-labels d53e105ee54ea40749a09fcbcd1e9432`, `t10k-images 9fb629c4189551a2d022fa330f9573f3`, `t10k-labels ec29112dd5afa0611ce80d1b7f02629c`. The regular MNIST distribution IS the paper's "regular database" (20×20 digits centered by center of mass in a 28×28 field). No reproduction code has touched the data at pre-registration time.

## Reproduction plan (pinned before running)

scikit-learn 1.7.2 `SGDClassifier(loss='squared_error', random_state=<master seed>)`, native one-vs-rest, matching the paper's description (linear units, gradient descent, MSE criterion). ALL other parameters are library defaults — that is the point of the audit: the five rubric items are resolved by sklearn's defaults (`penalty='l2'`, `alpha=1e-4`, `learning_rate='optimal'`, `eta0=0.0`, `shuffle=True`, `max_iter=1000`, `tol=1e-3`, `n_iter_no_change=5`, zero-init coefficients). Declared preprocessing choice (rubric item 5): pixels cast to float64 and scaled to [0, 1] by /255; labels used as the 10 raw classes. Metric: test-set error rate % on the 10,000 regular test images — the paper's own metric. Master seeds 0, 1, 2 thread through `random_state` (this pipeline IS stochastic via per-epoch shuffling, so seed spread is expected and will be reported); standardized drift = 3-seed mean |reproduced − published| pp. Environment: CPU only, Python 3.10.12, numpy 2.2.6, scipy 1.15.3, Ubuntu 22.04 sandbox.

## Pre-registered expected value, tolerance and verdict rule

- **Published value: 12.0% test error** (paper's quoted uncertainty ≈ 0.1%; binomial SEM at p=0.12, n=10,000 is ≈ 0.32 pp).
- **Tolerance: ±2.0 pp absolute** (same bar as confirmatory audits #1–#3; not moved after data).
- **CONFIRMED** if |reproduced − 12.0| ≤ 2.0 pp with seed 0 primary; **DISCREPANCY** if outside; **COULD-NOT-RUN** if data access or the 45 s per-call cap blocks execution (mitigation pre-declared: the fit runs as a background process polled across calls; a 60,000×784 linear SGD fit is expected to finish in minutes).
- **Secondary (Program 2b, exploratory until n=30):** the hypothesis predicts LARGE |drift| at score 5 — of the order of the score-3 MLP points (8.95/10.35 pp) or larger, far above the score-1–2 points (0.00–0.94 pp). If instead the reproduction lands within ~1 pp of 12.0, that is evidence AGAINST the hypothesis at the high-discretion end and will be reported as such.

## Results

**Verdict: COULD-NOT-RUN** (pre-run infrastructure block, per the pre-registered clause; contributes NO drift point and does NOT count toward n, per PREREG_DRIFT.md).

No reproduced value for the pinned configuration was ever observed; the block is purely computational and independent of the reproduction outcome, so this drop is unbiased:

- The pre-declared mitigation (background process polled across 45 s calls) failed: this sandbox kills ALL user processes at the end of each tool call (verified twice: a `nohup` fit and a `setsid nohup sleep 60` sentinel were both dead at the next call).
- The pinned fit is atomic and exceeds the cap: 1 epoch over all 10 OvR classes = 1.2 s; a truncated binary probe (`max_iter=230`) ran 26.1 s with `n_iter_=230` — the default `tol=1e-3` never triggered, so the default trajectory runs to `max_iter=1000` ≈ 113 s **per class**, inside a single un-checkpointable Cython call (`fit_binary`/`_plain_sgd`); even one class per call exceeded the cap (timeout at 42 s).
- A faithful decomposition exists per class (sklearn `_fit_multiclass` pre-draws per-class seeds), and was implemented and verified — but the per-class unit itself is ≥113 s, so no faithful chunking fits the cap.

## Honesty section

- Timing/feasibility probes that DID run (none is the audited quantity): (a) `max_iter=1` full fit, 1.2 s; (b) binary class-0 probe truncated at `max_iter=230` (26.1 s, no tol stop); (c) a CSR-sparse probe, ~10x faster (100 epochs in 3.0 s) — but a 5,000-sample dense-vs-sparse comparison at `max_iter=20` produced coefficient differences up to ~2.4e12 with only 48.5% prediction agreement, i.e. the defaults sit in a numerically unstable regime (squared loss + `learning_rate='optimal'`, coefficient magnitudes ~1e12 in truncated runs) where input representation changes the result materially. Switching the pinned dense representation to sparse post-hoc to beat the cap would therefore have silently changed the measurand and was rejected.
- The observed instability of the truncated runs is an observation about the default regime, NOT a reproduced error rate; no error rate for the pinned configuration was computed at any truncation.
- The rubric score (5/5) and this claim remain available to a future runner in an environment without the 45 s cap; the pinned plan in this file is complete and executable as written (`audits/audit_mnist_linear_run.py`).
- Same-session follow-up: a SECOND audit of the same published claim via the paper's other stated training route ("directly solving linear systems"), which is cap-feasible and has a different (lower) discretion profile, is pre-registered separately in `audits/AUDIT_lecun1998-mnist-linear-lsq.md` BEFORE its reproduction ran. Its rubric was scored before any least-squares code ran; no least-squares number was observed at pre-registration time.
