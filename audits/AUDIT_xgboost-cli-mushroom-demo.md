# AUDIT — dmlc/xgboost CLI demo README (pinned v1.7.6): mushroom binary classification, printed eval log (4 numbers)

**Program 2b confirmatory audit #15 · 2026-07-07 · status at this commit: PRE-REGISTERED, results EMPTY**
Two-commit rule: this file is web-committed to the remote BEFORE any reproduction code exists.

## Claim

Source: https://github.com/dmlc/xgboost/blob/v1.7.6/demo/CLI/binary_classification/README.md
(fetched raw, cache-busted, read in full this session; the CLI demo was removed from the repo in
xgboost 2.0, so the claim is pinned at the v1.7.6 tag, where README, conf and data coexist).
Claim class: **repo-README printed-numbers row — the program's open queue item**, entering the
confirmatory set for the first time (the exploratory Fashion-MNIST audits were this class; the
confirmatory set has zero points from it). Also the set's first boosting-*library* target
(audits #9/#11/#14 audited boosting/bagging *paper tables* re-implemented in sklearn; this one
audits the library's own shipped demo across a decade of its releases).

The README's "Monitoring Progress" section prints, for the shipped mushroom demo:

```
[0]     test-error:0.016139     trainname-error:0.014433
[1]     test-error:0.000000     trainname-error:0.001228
```

Pinned by the shipped `mushroom.conf`: booster=gbtree, objective=binary:logistic, eta=1.0,
gamma=1.0, min_child_weight=1, max_depth=3, num_round=2; eval sets = the shipped
`demo/data/agaricus.txt.test` (1611 rows) and `agaricus.txt.train` (6513 rows; also the training
set). Everything else falls to library defaults. Data artifacts pinned by the tag and fetched
this session BEFORE this pre-registration as a feasibility probe only (no model trained):
md5 `a88a94251c2969849ee603701cd4878e` (train), `e13c43414be35bb0c7d40b09e1ad34ad` (test).
The row counts exactly rationalize the printed numbers — 26/1611 = 0.016139,
94/6513 = 0.014433, 8/6513 = 0.001228 — so the shipped files are the claim's own split.

The reproduction maps the conf onto the python API of the modern library (xgboost-cpu 3.2.0),
which is precisely the implementation discretion this program measures.

## Blind discretion rubric — scored BEFORE any reproduction code ran

Scored from the README + shipped `mushroom.conf` + xgboost 3.x parameter docs only.

| Item | Score | Justification |
|---|---|---|
| (1) tie-breaking / randomization | 0 | no stochastic component in play: `subsample`/`colsample_*` default 1.0, the train/test split is shipped as fixed files, split enumeration is deterministic at nthread=1; `seed` is inert |
| (2) regularization / smoothing defaults | 1 | `lambda` (L2 on leaf weights, default 1.0) is NOT set by the conf — left to the library across a CLI-era→3.2.0 gap; ditto the split-enumeration discretization defaults (`tree_method`, `max_bin`) the conf never pins |
| (3) initialization | 1 | `base_score` (the boosting starting prediction) is NOT set by the conf; CLI-era default 0.5, while xgboost ≥2.0 *auto-estimates* it from the training data when unset — a documented default change squarely inside this rubric item |
| (4) stopping criteria / tolerances | 0 | `num_round=2` pinned; no early stopping, no convergence tolerances |
| (5) preprocessing | 0 | canonical data artifacts shipped in-repo (md5s above); LIBSVM sparse semantics fixed by the format plus xgboost's documented missing-value handling |

**Blind discretion score: 2/5, all four numbers.**

## Pre-registration

- **Primary measurand (verdict-bearing): all four printed error values × 100, in pp** —
  test r0 **1.6139**, test r1 **0.0000**, train r0 **1.4433**, train r1 **0.1228**.
- **Reproduction:** xgboost-cpu 3.2.0 python API; params exactly the conf's pinned set above,
  everything else left at library defaults; `nthread=1`; `seed` = master seed {0, 1, 2}
  (expected inert — pre-registered expectation: bit-identical numbers across master seeds).
  DMatrix built from the shipped LIBSVM files.
- **Tolerance: ±1.0 pp per number** (deliberately tighter than the score-2 ±2.0 precedent: the
  claim is a deterministic integer-count ratio; the bar will not move). Verdict **CONFIRMED**
  iff all four numbers land inside the bar at master seed 0; **DISCREPANCY** otherwise.
- **Standardized drift (Program 2b):** 3-master-seed mean |reproduced − published| pp per
  number → contributes **4 points at blind score 2**.
- **Secondary prediction (hypothesis-relevant):** all four drifts ≤ 1.96 pp (the program's
  current score-2 ceiling).
- **Secondary sensitivity (descriptive, no verdict weight):** mechanism table over
  {`tree_method`: 3.2.0 default vs `"exact"` (the CLI-era default)} × {`base_score`: unset
  (3.x auto-estimate) vs pinned 0.5 (CLI-era default)} — attributes any drift to the two
  scored discretion items.
- **Pre-declared risk:** the ≥2.0 auto-`base_score` and the `hist` default could shift the
  round-0 errors; if any number exits the ±1.0 pp bar that is a **DISCREPANCY** at rubric 2/5,
  reported as such, with the mechanism hunt in the honesty section.
- **Environment:** CPU-only sandbox, Python 3.10.12, xgboost-cpu 3.2.0, numpy 2.2.6,
  scipy 1.15.3 (installed this session).
- Reproduction script to be published as `audits/audit_xgb_mushroom_run.py`, raw output as
  `audits/xgb_mushroom_raw.json`, in the results commit(s), per VAR rule 3.

## Results

*(empty at pre-registration commit)*
