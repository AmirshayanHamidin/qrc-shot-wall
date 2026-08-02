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

(EMPTY at registration — filled by commit 2.)
