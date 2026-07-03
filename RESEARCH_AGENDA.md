# Standing Research Agenda — qrc-shot-wall overnight program

## State (updated 2026-07-03 ~13:10, scheduled run)

Repo: github.com/AmirshayanHamidin/qrc-shot-wall (local copy: `qrc-shot-wall/` in this folder).
Benchmarks 1–6 complete and pushed. Benchmark 5 established the **measurement-wall law**:
noisy classifier accuracy = mean Φ(margin_i / σ_i), with σ computed from the exact multinomial
shot-noise covariance projected on the readout direction. R²=0.991, MAE=1.3pts over 150 cells
(see results/RESULTS_LAW.md, src/qrc_law.py). Live QPU validation done (0.886 on ibm_marrakesh).
Benchmark 6 (self-calibration from a single noisy pilot): H-B6v3 REFUTED (split-pilot +
debiasing tops out at 5.7pt MAE); post-hoc v4 "gauss_full" predictor
acc = mean Φ(ĝ/√(σ_S²+v_pilot)) reaches MAE 3.8pts / R²=0.915 at S_pilot=8000
(see results/RESULTS_SELFCAL.md). Downward budget extrapolation is ~solved (≤2.2pts);
upward extrapolation S≫S_pilot is the open problem.

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

- [x] **B6 — Self-calibrating law. DONE 2026-07-03.** v1 (naive plug-in, C=1000) FAILED
      R²=−1.74. v2 (C=1 + squared-margin debiasing) R²≈0.48 on 2 archs. v3 full run (all 6
      archs, 5 tasks, S_pilot∈{500,2000,8000}, 150 cells/config): H-B6v3 refuted — splitting
      the pilot HURTS (5.7pt MAE vs 4.2 nosplit at S_pilot=8000); bagging ≈ no effect.
      Post-hoc v4 smoothing identity Φ(ĝ/√(σ_S²+v_pilot)) is the best self-calibrated
      predictor: 3.8pt MAE / R²=0.915 at S_pilot=8000; ≤2.2pt for S ≤ S_pilot/2 (downward
      extrapolation ~solved). Open: upward extrapolation S≫S_pilot saturates at pilot
      uncertainty. Files: results/RESULTS_SELFCAL.md, results/b6_selfcal.json,
      figures/b6_selfcal.png, src/b6_selfcal.py.
- [ ] **B6b — Confirmatory v4 (quick, do first).** Freeze gauss_full; fresh pilot seeds;
      pre-state: MAE ≤ 4pts AND R² ≥ 0.90 at S_pilot=8000 over 150 cells. Also try empirical-
      Bayes shrinkage prior on margins to attack the S≫S_pilot regime, and report interval
      predictions [Φ(ĝ/√(σ²+v)), Φ(ĝ/σ)] coverage. (~10 min of compute.)
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
- 2026-07-03 13:10 — Scheduled run completed B6. Rebuilt all 6 arch tensors from scratch;
  ran v3 (nosplit/split/split_bag × S_pilot {500,2000,8000} × 6 archs × 5 tasks × 5 budgets)
  plus post-hoc v4 gauss variants; 2250 measurements total. H-B6v3 refuted (splitting hurts);
  v4 gauss_full best at 3.8pt MAE / R²=0.915 (S_pilot=8000). Wrote RESULTS_SELFCAL.md +
  b6_selfcal.json + b6_selfcal.png; queued B6b confirmatory run as next item. Note: v1/v2
  numbers quoted from the 03:00 live session log were not re-derived this run.

## Pending push

(none)
