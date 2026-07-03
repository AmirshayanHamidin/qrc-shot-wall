# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-03 ~03:00)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall (local copy: `qrc-shot-wall/` in this folder).
Benchmarks 1–5 complete and pushed. Benchmark 5 established the **measurement-wall law**:
noisy classifier accuracy = mean Φ(margin_i / σ_i), with σ computed from the exact multinomial
shot-noise covariance projected on the readout direction. R²=0.991, MAE=1.3pts over 150 cells
(see results/RESULTS_LAW.md, src/qrc_law.py). Live QPU validation done (0.886 on ibm_marrakesh).

## HARD GUARDRAILS (never violate)

1. **NEVER submit jobs to real IBM hardware** — the free QPU budget is nearly spent (484/600s).
   Do not read or use `ibm_token.txt`. Simulation only (numpy engine + qiskit-aer).
2. Only work inside this outputs folder and the qrc-shot-wall GitHub repo. No other accounts,
   sites, purchases, emails, or messages.
3. Every claim gets an honesty section. Failed hypotheses are reported as failures.
4. Keep runs within the 45s bash-call limit (chunk long computations; see qrc_hw2.py pattern).
5. If GitHub push isn't possible in this session, save everything locally in
   `qrc-shot-wall/` subfolders and log it under "Pending push" below; do not retry endlessly.

## Method rules

- One pre-stated falsifiable hypothesis per benchmark; fit/holdout splits where fitting occurs.
- Reuse the engine: `qrc_law.py` (build/eval phases), density-matrix numpy for speed.
- Write results as `qrc-shot-wall/results/RESULTS_<NAME>.md` + raw JSON + figure PNG.
- Update the "Log" section of this file after each work session.

## Queue (work top-down; mark DONE with date; go deeper on whatever the results point to)

- [~] **B6 — Self-calibrating law. IN PROGRESS (live session 03:00).** v1 (naive plug-in,
      C=1000 SVM) FAILED: R²=−1.74. v2 (C=1 SVM + squared-margin debiasing f²−v/S_pilot):
      R²=0.48, MAE=6.4pts on archs {0,4} — see b6_part1.json / b6_part2.json in outputs root.
      KEY DIAGNOSIS: the limiting factor is estimating the readout direction w from noisy pilot
      features, not the margins. Next steps for scheduled runs: (a) split pilot into w-estimation
      and margin-estimation halves, (b) try shrinkage/averaged readouts (bagging over pilot
      resamples), (c) sweep S_pilot in {500, 2000, 8000} to find the pilot budget where
      prediction reaches ~3pt MAE, (d) run remaining archs {1,2,3,5}, then write
      results/RESULTS_SELFCAL.md + figure + push. Report the failure arc honestly (v1 → v2).
- [ ] **B7 — Law + gate noise.** Hypothesis: device noise enters as a margin-shrinkage factor.
      Fit a single per-device scalar λ (or per-depth λ^d) on a few FakeTorino cells, predict the
      rest. Uses qiskit-aer FakeTorino (simulation only).
- [ ] **B8 — Regression law.** Closed form: NMSE_noisy ≈ NMSE_exact + wᵀΣw/var(y). Test across
      the grid (30 regression cells exist; extend budgets). If it holds, both task regimes are
      predicted by one framework.
- [ ] **B9 — Scaling.** How do margin distributions scale with qubit count (4–8 qubits, T reduced
      for 8q feasibility)? Does margin×√S improve, worsen, or stay flat with size at fixed task?
- [ ] **B10 — Margin-aware training.** Intervention: choose readout regularization/objective to
      maximize predicted noisy accuracy (from the law) instead of clean accuracy. Measure gain.
- [ ] **B11 — Consolidate.** Draft `qrc-shot-wall/PREPRINT.md`: abstract, 5-benchmark narrative,
      law derivation sketch, limitations, future work. This is the arXiv skeleton.

## Log

- 2026-07-03 03:00 — Agenda created. B6 started in the live session.
- 2026-07-03 12:30 — Overnight runs did not execute (app closed + agenda was not reachable
  from fresh scheduled sessions). Fixed: this file now lives in the repo root; scheduled runs
  fetch it from raw.githubusercontent.com and push updates back. B6 remains the top item;
  b6_part1/2 JSONs live in the original live session and their numbers are summarized in the
  B6 queue entry — re-derive locally if needed (code: src/qrc_law.py).

## Pending push

(none)
