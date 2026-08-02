# PRE-REGISTRATION: B5 restoration completion — the 30 regression cells

Registered 2026-08-02 (scheduled session), BEFORE any reproduction code ran. Two-commit rule
(Program 2 method rules, RESEARCH_AGENDA.md): this file is committed with an EMPTY results
section first; results land in a separate later commit. Bars are never moved after data.

## Scope and provenance finding

`results/RESULTS_LAW.md` ("Scale of evidence") counts "30 regression cells from the original
run, not re-audited", and the B5 restoration (2026-07-04) left them as an open queue item.
Pre-run search of the working tree at HEAD `2dcd4ec` finds **no committed artifact containing
these cells**: `narma2_reg` appears only in `src/qrc_law.py`; every `results/*law*.json` task
set is the five classification tasks; `law_results.json` (the only committed generator's
output for reg cells, written by `qrc_law.py evaluate_all()`) is absent from the tree.
**There is therefore no number of record to compare against.** This is a completion of the
restored 8-seed protocol over the missing cells, not a drift audit; the absence itself is the
provenance finding, consistent with the 2026-07-04 B5 audit pattern (undocumented protocol,
uncommitted outputs).

## Pinned protocol (committed code only)

- Grid: `narma2_reg` × 6 architectures (`qrc_law.ARCHS` 0–5) × budgets (250, 1000, 4000,
  16000, 64000) = **30 cells**; T=400, WASH=60 as committed.
- Build: `src/qrc_law.py build(arch_id)` unmodified (deterministic given committed seeds).
- Features: committed `feats_from_P`; sampling seeds **1–8** per cell via
  `np.random.default_rng(ss)`, one fresh generator per (seed, budget, arch) draw, identical
  stream discipline to `qrc_law_rerun.py obs()`.
- Observation metric: committed `qrc_law.perf()` for `kind='reg'` — StandardScaler + Ridge,
  alpha ∈ {1e-4, 1e-2, 1}, best holdout R² on the 30% chronological split (retrained per
  noisy draw, the restored-protocol convention).
- floor = committed inputs-only proxy (`perf` on the single-column u drive); exact = `perf`
  on exact features (S=0). Retention per cell = (mean-over-seeds obs − floor)/(exact −
  floor), with the committed guard: cells with |exact − floor| ≤ 0.02 excluded.
- Driver committed as `src/qrc_law_reg_rerun.py` (thin wrapper over the committed functions;
  no reimplementation). Raw per-seed values published in `results/law_reg_rerun.json`.

## Pre-registered falsifiable bars (numeric; failures published as failures)

- **H1 (the wall at low budget):** mean narma2_reg retention over the 6 archs at S=250 is
  **< 0.20**. (Anchors: B3 — NARMA5 retains ~4% at 40k; B11 — Mackey-Glass regression
  retention negative at 250.)
- **H2 (budget ordering):** mean retention at S=64000 exceeds mean retention at S=250 by
  **> 0.10**.
- **H3 (task shape at low budget):** at S=250 AND at S=1000, mean reg retention < mean clf
  retention at the same budget, where per-cell clf retention = (obs_mean − floor)/(exact −
  floor) computed from the published `results/law_rerun.json` at HEAD `2dcd4ec` (same
  guard), averaged over its 30 cells per budget.
- **Declared uncertainty, no bar:** reg-vs-clf at 64k is left open — B3 (NARMA5, ~4% at 40k)
  and B11 (Mackey-Glass reg 0.86 at 64k) pull in opposite directions; whatever lands is
  reported.

## Environment

Linux sandbox, CPU only; Python 3; numpy 2.2.6, scikit-learn 1.7.2, scipy 1.15.3,
qiskit 2.5.1 (note: 2.5.1 vs 2.5.0 in the 07-27 audits — qiskit touches only the
deterministic build phase). No credentials, no network beyond the repo.

## Results

(Run 2026-08-02, same session, after the registration commit `ee4ad4c` was raw-verified on
the remote. Driver: `src/qrc_law_reg_rerun.py`; raw per-seed values:
`results/law_reg_rerun.json`. This section is commit 2 of 2.)

**Mean retention by budget (30 cells, 8 seeds each), vs the published classification grid:**

| S | reg (this run) | clf (published `law_rerun.json`) |
|---|---|---|
| 250 | 0.544 | 0.146 |
| 1 000 | 0.743 | 0.298 |
| 4 000 | 0.854 | 0.448 |
| 16 000 | 0.916 | 0.540 |
| 64 000 | 0.953 | 0.616 |

**Anchors.** floor = −0.063 for every arch (the committed inputs-only proxy has no NARMA2
skill — it lacks memory), exact R² = 0.953–0.993, so denominators are 1.02–1.06 and the
|exact − floor| ≤ 0.02 guard never triggered. Retention at 250 shots spans −0.008 (arch 0)
to 0.883 (arch 4); by 64k all archs sit at 0.83–0.99.

**Pre-registered bars:**

- **H1: FAILED.** Mean retention @250 = **0.544**; the bar was < 0.20.
- **H2: PASSED.** @64k − @250 = **+0.409**; the bar was > 0.10.
- **H3: FAILED — inverted.** reg > clf at 250 (0.544 vs 0.146) and at 1000 (0.743 vs
  0.298) — and in fact at every budget.

**Verification.** Three spot cells re-run in-session reproduce bit-identically
(a2/S=1000/seed 5, a2/S=250/seed 1, a2/S=64000/seed 8); the build phase is deterministic
from committed seeds.

## Reading the failures (honesty section)

1. **The anchor mapping was wrong, and that is the finding.** H1/H3 transplanted B3's
   "regression retains ~4% at 40k" (NARMA5) and B11's negative-at-250 (Mackey-Glass) onto
   B5's committed retention convention. Those results measure retention against *tuned,
   history-aware classical baselines*; B5's committed floor is the instantaneous
   single-input column, which has zero NARMA2 skill. Against a no-skill floor, "retention"
   measures the fraction of exact-readout R² reached — a different and easier quantity.
   The bars failed largely because the convention does not transfer, and partly because
   NARMA2 (short memory, smooth target) is genuinely easier under sampling noise than
   NARMA5 or Mackey-Glass prediction. **No B3/B11 number is challenged by this inversion**
   — they are different quantities on different tasks.
2. **What the inversion does say:** under the B5 convention, a smooth regression target
   recovers with shots far faster than the margin-limited classification cells — NARMA2's
   signal rides low-order feature directions that Ridge averages across ~60–100 correlated
   features, while parity-type cells depend on fragile high-order correlators. Consistent
   with B13's scope correction: the wall is margin/feature-structure-shaped, not
   output-type-shaped. A tuned-baseline reg-vs-clf comparison on this grid would be a NEW
   pre-registration, not attempted here.
3. **The probit law makes no prediction for these cells** (margins are a classification
   quantity); they complete the grid's evidence base, not the law's test set.
4. Environment: qiskit 2.5.1 (deterministic build phase only) vs 2.5.0 in the 07-27
   audits; numpy/sklearn/scipy identical. Per-arch scratch files (`lawreg{0..5}.json`)
   are subsumed by the published aggregate (all per-seed values included) and not
   committed, matching the `law_rerun.json` precedent. Only pre-registered quantities are
   reported; the H3 comparison uses the published `law_rerun.json` at HEAD `2dcd4ec`
   exactly as registered.
