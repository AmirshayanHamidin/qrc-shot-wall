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

Reproduced from the example code verbatim (minus plotting); script: `audits/audit_digits_svc_run.py` (committed alongside, VAR rule 3). Runtime < 5 s, CPU only.

- Exact reproduced accuracy: **0.9688542825 (871/899)**; printed report shows **0.97** — identical to the published headline.
- **All 33 printed report numbers match the published report exactly at 2 dp** (10 classes x precision/recall/f1, accuracy, macro avg, weighted avg), and all per-class supports match (88/91/86/91/92/91/91/89/88/92, total 899).
- Dataset integrity: `load_digits()` shape (1797, 64); md5(data bytes + target bytes) = `0af20a105e04dcf55c5d1bc47c958850`.

Pre-registered bars:

1. Primary bar (accuracy within ±0.005 of published 0.97): |0.96885 − 0.97| = 0.0011 → **PASS**.
2. Strict deterministic bar (33/33 printed numbers at 2 dp): **PASS**.
3. Secondary discretion prediction (|drift| < 0.15 pp): **held at observable precision** — the printed reports are identical, consistent with the predicted exact-0.00 pp drift (see honesty item 1 for what the 2-dp publication can and cannot prove).

## Verdict

**CONFIRMED.** Published 0.97 / reproduced 0.9689 (871/899); full 33-number report identity across a 1.8.0 -> 1.7.2 minor-version gap. The zero-discretion pipeline anchors the discretion-predicts-drift ordering at ~0.00 pp, now 4/4: **docs-SVC ~0.00 pp < k-NN 0.15 pp < LogReg 0.25 pp < GaussianNB 5.9 pp** (first point digits, other three Fashion-MNIST — the ordering spans datasets and claim types).

## Environment

Reproduction: Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6, Linux 6.8.0 x86_64 (glibc 2.35), CPU-only sandbox. Publication: scikit-learn docs CI, version 1.8.0. Data: `sklearn.datasets.load_digits()` (bundled with sklearn, no download).

## Honesty section

1. **Rounded publication limits what is provable.** The docs print 2 dp, so the strongest strictly provable statement is "identical printed reports". Exact drift 0.00 pp is *inferred* (deterministic pipeline + 33/33 identity), not observed: from the accuracy row alone the provable bound is ±0.5 pp. The joint identity constrains it much harder — a single flipped prediction moves one class's recall by ~1.1 pp, which at 2 dp flips a printed digit in most (not all) cases.
2. **Backward cross-version replication.** 1.8.0 was not installable (sandbox index caps at 1.7.2), so this tests docs-vs-1.7.2, not an independent rerun of 1.8.0.
3. **Low-severity target, chosen deliberately.** A docs example is auto-generated by CI from the code it documents; the audit's value is the cross-version check plus the zero-discretion anchor for the drift ordering — not adversarial scrutiny of a paper.
4. The DecisionTree infra-block estimate (>=2 min for the 60k fit) is an extrapolation from a synthetic-data probe, not a measured failure on real data.
5. **Session incidents, reported:** two editor mishaps while entering the pre-registration (a first typing pass dropped 6 leading characters after each newline and was wholesale-replaced before committing; a stray "Page_Down" literal was typed and undone). Both occurred and were repaired BEFORE the pre-registration commit; no results existed at that time.
6. Rule 6: nothing leaves the repo; claim ownership and sign-off remain with A.H.
