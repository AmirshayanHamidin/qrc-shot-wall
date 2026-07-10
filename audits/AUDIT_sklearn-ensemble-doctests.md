# AUDIT — scikit-learn docs (1.7.2, cross-checked identical in stable/1.9.0): fully-seeded ensemble doctest rows

**Program 2b confirmatory audit #21 · 2026-07-10 · status at this commit: PRE-REGISTERED, results EMPTY**
Two-commit rule: this file is web-committed to the remote BEFORE any reproduction code exists.

## Claim

Sources (fetched cache-busted this session, version-matched to the executing library):
- https://scikit-learn.org/1.7/modules/generated/sklearn.ensemble.GradientBoostingClassifier.html ("scikit-learn 1.7.2 documentation")
- https://scikit-learn.org/1.7/modules/generated/sklearn.ensemble.AdaBoostClassifier.html (same)

Both doctest values were also verified identical on the stable (1.9.0) pages this session, so the claim spans 1.7.2 → 1.9.0 unchanged. The reproduction executes under scikit-learn **1.7.2** (sandbox index cap, pre-declared in audit #12) — for the first time in the program, the executing version MATCHES the claim's version: a version-gap-free library-docs target.

Claim class: library-documentation **doctest** (executed example rendered from the released code's docstrings, doctest-verified in the project's CI at release). This is exactly the class the run-#20 agenda named as the score-0 anchor candidate ("a fully-seeded library-docs doctest row would qualify") — the top coverage gap: the confirmatory set's only score-0 points are NIST certified values (audit #10), where drift is definitionally floored.

**Row A — GradientBoostingClassifier docstring example** (test accuracy, 10,000 test samples):

```
X, y = make_hastie_10_2(random_state=0)          # 12000 samples, 10 features
X_train, X_test = X[:2000], X[2000:]             # deterministic slice split
clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,
                                 max_depth=1, random_state=0).fit(X_train, y_train)
clf.score(X_test, y_test)  ->  0.913
```

**Row B — AdaBoostClassifier docstring example** (TRAINING accuracy, 1,000 samples):

```
X, y = make_classification(n_samples=1000, n_features=4, n_informative=2,
                           n_redundant=0, random_state=0, shuffle=False)
clf = AdaBoostClassifier(n_estimators=100, random_state=0).fit(X, y)
clf.score(X, y)  ->  0.96
```

Both printed values are exact float reprs (0.913 = 9130/10000; 0.96 = 960/1000).

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the two doc pages + the 1.7.2 API defaults only.

| Item | A | B | Justification |
|---|---|---|---|
| (1) tie-breaking / randomization | 0 | 0 | every RNG pinned: data generators random_state=0, estimators random_state=0; split is a deterministic slice (A) / in-sample (B); GBC subsample=1.0 default → non-stochastic boosting |
| (2) regularization / smoothing defaults | 0 | 0 | headline knobs pinned in the snippet (learning_rate=1.0, A) or documented at the SAME version the reproduction executes (B) — no cross-version default left to fix |
| (3) initialization | 0 | 0 | GBC init=None → deterministic log-odds prior, documented; AdaBoost has none |
| (4) stopping criteria / tolerances | 0 | 0 | n_estimators=100 pinned in both; GBC early stopping off by default (n_iter_no_change=None); AdaBoost early-termination rule deterministic — all at the executing version |
| (5) preprocessing | 0 | 0 | none: seeded synthetic data consumed raw; no scaling/encoding/missing values; split fully specified by slicing |

**Blind discretion score: 0/5, both rows.** First score-0 target outside the certified-values class.

## Pre-registration

- **Primary measurand (verdict-bearing): the doctest-printed score × 100** — Row A **91.3 pp**, Row B **96.0 pp**.
- **Tolerance: ±0.5 pp per row.** Verdict **CONFIRMED** iff both rows land inside the bar at master seed 0; **DISCREPANCY** otherwise. The bar will not move. (Rationale: doctest values are CI-verified on released code; residual risk is platform-level — BLAS/compiler tie-flips — not statistical. The tightest bar in the program, matching the score-0 claim class.)
- **Standardized drift (Program 2b):** 3-master-seed mean |reproduced − published| pp per row → contributes **2 points at blind score 0** (n: 19 → 20). Master seeds {0,1,2} seed the global NumPy RNG before the run (audit #12/#20 convention); with no unseeded randomness in the pipeline, scores are expected bit-identical across master seeds.
- **Secondary prediction (hypothesis-relevant):** both drifts = **0.00 pp** — the score-0 floor, this time in a class where the floor is NOT definitional (real training pipelines with floating-point, threading and platform freedom, unlike certified reference values).
- Environment: python 3.10, scikit-learn 1.7.2, numpy 2.2.6, scipy 1.15.3, CPU-only sandbox (packages reinstalled to a /tmp prefix this session after a disk-full-corrupted user-site install; disclosed for provenance, no bearing on results).

## Results

(EMPTY at pre-registration commit; filled by a later commit in the same session.)
