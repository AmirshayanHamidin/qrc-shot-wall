# Program 2 Audit #2 — Fashion-MNIST paper benchmark, Table 3 (LogisticRegression row)

Scheduled Program 2 session, 2026-07-05. Follows VAR PROTOCOL.md v1.0 and the Program 2
method rules (two-commit pre-registration, adopted 2026-07-05). **This file is committed
with the Results section empty BEFORE any experiment runs; results land in a separate
later commit. Ordering is provable from commit history alone.**

## Claim under audit

- **Source:** Xiao, Rasul, Vollgraf, *Fashion-MNIST: a Novel Image Dataset for Benchmarking
  Machine Learning Algorithms*, arXiv:1708.07747, Table 3; reproduction pipeline
  `benchmark/runner.py` in github.com/zalandoresearch/fashion-mnist (MIT license).
- **Claim:** `LogisticRegression(C=1, multi_class=ovr, penalty=l1)` achieves
  **0.842** test accuracy on Fashion-MNIST.
- **Why this row (queue rationale):** audit #1 found reproducibility tracked the
  implementation discretion the algorithm leaves the library (k-NN: 0.15 pp drift;
  GaussianNB: 5.9 pp). Logistic regression sits between: the paper-era sklearn 0.19
  default solver (liblinear) still exists but is no longer the default, and `multi_class`
  has since been removed from the API entirely — moderate discretion.

## Pre-registration (written before any run)

- **Pipeline (from `benchmark/runner.py`):** load 60k train / 10k test idx files;
  `StandardScaler().fit(X_train)`, transform train and test; shuffle train; fit; `score`
  on the 10k test set. Paper reports the mean over shuffle repeats.
- **Reproduction spec, fixed now:** sklearn 1.7.2 (sandbox), numpy 2.2.6,
  `LogisticRegression(penalty='l1', C=1.0, solver='liblinear')`, all other parameters
  library defaults (max_iter=100, tol=1e-4, fit_intercept=True). Solver rationale:
  liblinear was the sklearn 0.19 default at publication time and is inherently
  one-vs-rest, matching the published `multi_class=ovr`; the modern default (lbfgs)
  cannot fit l1 at all. This choice is itself an instance of the discretion being tested,
  and it is made here, before results exist.
- **Repeats:** 2 shuffle repeats (numpy seeds 0 and 1), primary number = their mean
  (mirrors `runner.py` num_repeat=2). If the compute budget forces a single repeat, the
  single number is reported and labelled as such.
- **Primary tolerance:** |reproduced − 0.842| ≤ **0.005** → CONFIRMED, else DISCREPANCY
  (same bar as audit #1). COULD-NOT-RUN if the pipeline cannot complete.
- **Secondary pre-registered prediction (discretion hypothesis from audit #1):** the
  absolute drift will fall strictly between audit #1's two anchors — larger than k-NN's
  0.0015 and smaller than GaussianNB's 0.059. Direction not registered.
- **Data integrity:** the four idx files must match the README MD5s
  (8d4fb7e6c68d591d4c3dfef9ec88bf0d, 25c81989df183df01b3e8a0aad5dffbe,
  bef4ecab320f06d8554ea6380940ec79, bb300cfdad3c16e7a12a480ee83cd310) or the run aborts.

## Results

*(empty at pre-registration commit; filled in a separate commit after the run)*

## Environment

*(filled with results)*

## Honesty section

*(filled with results)*
