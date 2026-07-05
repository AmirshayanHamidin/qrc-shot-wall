# AUDIT: scikit-learn docs — "Recognizing hand-written digits" (digits SVC report)

**Program 2, audit #3 — 2026-07-05, scheduled session (run #3).**
Two-commit pre-registration (Program 2 method rule, adopted 2026-07-05): THIS commit contains the pre-registration and an EMPTY results section. Results land in a separate later commit. Ordering is provable from git history alone.

## Claim under audit

Source of record: scikit-learn documentation, example *"Recognizing hand-written digits"*, version-pinned page https://scikit-learn.org/1.8/auto_examples/classification/plot_digits_classification.html (identical content fetched today from /stable/, which currently serves the 1.8.0 docs).

Pipeline (from the example code, verbatim): `load_digits()` -> flatten to (n, 64) -> `SVC(gamma=0.001)` (all other params default) -> `train_test_split(data, target, test_size=0.5, shuffle=False)` -> fit on train half, predict test half. No scaling, no seed, no shuffling: **zero-discretion pipeline.**

Published classification report (support 899):

| class | precision | recall | f1 |
|---|---|---|---|
| 0 | 1.00 | 0.99 | 0.99 |
| 1 | 0.99 | 0.97 | 0.98 |
| 2 | 0.99 | 0.99 | 0.99 |
| 3 | 0.98 | 0.87 | 0.92 |
| 4 | 0.99 | 0.96 | 0.97 |
| 5 | 0.95 | 0.97 | 0.96 |
| 6 | 0.99 | 0.99 | 0.99 |
| 7 | 0.96 | 0.99 | 0.97 |
| 8 | 0.94 | 1.00 | 0.97 |
| 9 | 0.93 | 0.98 | 0.95 |

**Headline: accuracy 0.97** (as printed, 2 dp), macro avg 0.97/0.97/0.97, weighted avg 0.97/0.97/0.97.

## Pre-registration (written BEFORE any experiment ran)

1. **Primary bar (consistent with audits #1-2):** reproduced test accuracy within **±0.005** of the published 0.97 -> CONFIRMED, else DISCREPANCY.
2. **Strict deterministic bar:** every one of the 33 printed report numbers (30 per-class + 3 accuracy/macro/weighted rows) matches at the printed 2-dp precision.
3. **Secondary prediction (discretion -> drift, point #4):** this pipeline leaves the library *zero* numerical discretion (fixed dataset, fixed non-shuffled split, no seed, deterministic SVC solve). Predicted |drift| **< 0.15 pp** — strictly below the smallest drift measured so far (k-NN, 0.15 pp), extending the discretion-predicts-drift ordering to a fourth point at the zero-discretion extreme. Expected drift: exactly 0.00 pp unless libsvm/numerics changed between sklearn 1.7.2 and 1.8.0.

**Pre-declared environment gap (part of the test):** the docs page was generated with scikit-learn **1.8.0**; the sandbox package index caps at **1.7.2** (verified before running), so the reproduction runs one minor version behind the publication. If the strict bar fails but the primary bar holds, the default explanation is this version gap, stated as such.

**Pre-declared session note:** the queue's first candidate (Fashion-MNIST Table 3 DecisionTree row, 0.798) was found infra-blocked before pre-registration: a synthetic-data timing probe (15k x 784, depth-10 entropy: 32.4 s) extrapolates to over 2 min for the full 60k fit — a single unchunkable single-threaded process under the sandbox's hard 45 s cap, with no claim-preserving amendment (trees have no warm start; subsampling changes the number). No real Fashion-MNIST data was touched. The row stays queued for an environment without the cap.

## Results

(empty — results land in the next commit)

## Verdict

(empty)

## Environment

(empty)

## Honesty section

(empty)
