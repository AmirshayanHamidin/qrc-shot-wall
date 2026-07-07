# AUDIT — dmlc/xgboost CLI demo README (pinned v1.7.6): mushroom binary classification, printed eval log (4 numbers)

**Program 2b confirmatory audit #15 · 2026-07-07 · status: RESULTS PUBLISHED (prereg commit `f85c810`, byte-verified on the remote via git fetch + md5 before any reproduction code existed)**

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

**Verdict: CONFIRMED** — all four numbers reproduce the published log **exactly, to every printed
digit**, at every master seed (bit-identical across seeds 0/1/2, as pre-registered), trivially
inside the ±1.0 pp bar.

| number | published (pp) | reproduced (pp, all 3 seeds) | drift (pp, 3-seed mean) |
|---|---|---|---|
| test, round 0 | 1.6139 | 1.613904 (= 26/1611) | 0.0000 |
| test, round 1 | 0.0000 | 0.000000 | 0.0000 |
| train, round 0 | 1.4433 | 1.443268 (= 94/6513) | 0.0000 |
| train, round 1 | 0.1228 | 0.122831 (= 8/6513) | 0.0000 |

(Full-precision drifts are rounding residue of the README's own 6-dp printing, ≤ 4.5e-05 pp;
under the tracker's printed-2-dp convention all four points enter as **(2, 0.00)**.)

- **Secondary prediction HELD:** all four drifts ≤ 1.96 pp.
- **Mechanism table (pre-registered): null result.** All four cells of
  {`tree_method`: hist-default vs `exact`} × {`base_score`: 3.x auto-estimate vs pinned 0.5}
  print the identical four numbers. Neither scored discretion item manifests on this data:
  mushroom is nearly separable, the all-binary one-hot features bin losslessly at `max_bin=256`
  (hist ≡ exact here), and at eta=1.0 the round-0 leaf values dominate any base-score shift at
  the 0.5 decision threshold.
- Raw per-seed values and the mechanism grid: `audits/xgb_mushroom_raw.json`; runner:
  `audits/audit_xgb_mushroom_run.py`.

## Honesty section

1. `eval_metric="error"` was set explicitly. The modern default for `binary:logistic` is
   logloss (changed since the CLI era, whose default eval was error). This is not counted as
   scored discretion: PREREG_DRIFT.md defines drift *on the paper's own metric*, and error is
   the metric the README prints — the setting selects the measurand, it cannot move the model.
2. The LIBSVM files are parsed manually to CSR so absent entries stay *missing* (the CLI
   DMatrix semantics); the deprecated `DMatrix("file?format=libsvm")` URI path was avoided.
   Feature count inferred as max index + 1 = 127 across both files.
3. Data files were downloaded (md5-pinned to the v1.7.6 tag) BEFORE the pre-registration
   commit as a feasibility probe; row counts appeared in the prereg. No model was trained
   before the prereg was byte-verified on the remote.
4. Four points at (2, 0.00) from one audit share one environment and are correlated — same
   caveat as every multi-row audit in the set. They also sit at the score-2 low end, echoing
   the library-shipped-artifact pattern (exploratory audit #3, confirmatory audit #12): claims
   whose data + config ship inside the repo reproduce near-exactly even a decade later.
5. Installed `xgboost-cpu` 3.2.0 (the plain `xgboost` wheel bundles CUDA/NCCL and exceeded
   the sandbox disk); CPU-only either way. `nthread=1` throughout.
6. The mechanism table's null result does NOT retroactively lower the blind rubric score:
   scores are pre-run by construction and never revised after data. If anything the null
   illustrates the rubric's role as an *upper bound* on discretion that can fire.
7. The verdict is a number, not an endorsement: it says the v1.7.6 demo log is exactly
   recoverable from the shipped artifacts under xgboost 3.2.0 defaults on this dataset —
   nothing more.
