# QRC "Shot Wall" — Overnight Research Agenda

Persistent state for the `qrc-overnight-research` scheduled task. **This file is
committed to the repo root** (github.com/AmirshayanHamidin/qrc-shot-wall) so it
survives sandbox resets — the session `outputs/` folder does NOT reliably persist
between runs (it was empty at the start of the 2026-07-03 run). **Every run:
`git clone` the repo first and read this file from there.**

## Program in one paragraph
A reproducible benchmark study of quantum reservoir computing (QRC) under
realistic measurement budgets. Established the "measurement wall": with exact
readout a 6-qubit reservoir is excellent, but shot noise erases the quantum
benefit for precise-output (regression) tasks while coarse-output
(classification) tasks survive. Culminated in a parameter-free *law* predicting
shot-noise-limited classifier accuracy from noiseless quantities, now extended
to gate noise.

## HARD GUARDRAILS (never violate)
1. **Simulation only** — numpy + qiskit-aer / density-matrix. NEVER submit to
   real IBM quantum hardware. NEVER read or use `ibm_token.txt`.
2. Touch **no account or service** other than pushing to this GitHub repo.
3. Every shell computation must fit **45-second** calls — chunk long runs, save
   partial `.npy`/JSON, aggregate separately.
4. **Report negative results honestly.** Pre-state a hypothesis; include failures.
5. Land a **complete** increment each run (never leave a benchmark half-written);
   then update this file and stop with a 3-sentence summary.

## Method rules
- Reuse `src/qrc_law.py` (density-matrix engine, tasks, architectures),
  `law_eval_arch.py`, and the `qrc_gatenoise.py` pattern.
- Each benchmark: `RESULTS_<NAME>.md` + raw JSON + one figure, into
  `results/` and `figures/`. Add code to `src/`.
- Push via the GitHub web-upload flow (folder-scoped `/upload/main/<folder>`
  pages, then Commit) if a logged-in Chrome session is available.
- Sandbox note: `pip install qiskit scikit-learn --break-system-packages` may be
  needed at the start of a run (the base image did not have them on 2026-07-03).

## Completed benchmarks
- [x] **B1** QRC vs tuned classical baselines; shot noise is the bottleneck. `RESULTS.md`
- [x] **B2** Eight gap-closing strategies all plateau at the classical floor. `RESULTS_GAP.md`
- [x] **B3** The wall is task-shaped: classification survives, regression doesn't. `RESULTS_TASKSHAPE.md`
- [x] **B4** Hardware-noise benchmark + one live QPU point (0.886, ibm_marrakesh, historical). `RESULTS_HARDWARE.md`
- [x] **B5** Parameter-free measurement-wall law, R²=0.991 / MAE 1.3pp, 150 cells. `RESULTS_LAW.md`
- [x] **B6** Device-fidelity factor: gate noise ≈ effective-shot reduction c(γ)².
      Collapse R²=0.927 vs naive 0.851 over 420 cells; advantage grows with γ;
      honest ~3pp residual. `RESULTS_GATENOISE.md` (done 2026-07-03).
- [x] **B7** Per-node + shot-noise-covariance fidelity factor — **pre-registered
      hypothesis FALSIFIED (honest negative)**: correction cuts collapse MAE only
      2.5% vs the 30% bar (2.89→2.82pp over 350 cells). Per-node contraction is
      real (spread 0.04→0.17) and σ² does rise with γ, but the residual is a
      shot-budget-IRREDUCIBLE negative bias (−3.9pp at γ=0.20): gate noise moves
      the reservoir OFF the noiseless curve. B6's scalar factor is near-optimal
      among effective-shot corrections. `RESULTS_PERNODE.md` (done 2026-07-03).

## Work queue (reconstructed 2026-07-03 — original B6..B11 list was lost with the
## non-persisted outputs folder; these are the natural next steps from the B5/B6
## write-ups, reprioritized)
- [ ] **B8** **Beyond depolarizing:** coherent / amplitude-damping / correlated
      gate errors. Do they still contract margins multiplicatively, or do coherent
      errors *rotate* the readout direction (breaking the scalar-fidelity picture)?
      This is the honest stress-test of B6's single-noise-model caveat.
- [ ] **B9** **Harder classification tasks** where classical polynomial expansion
      is not trivially available (e.g. temporal tasks over larger alphabets,
      non-polynomial nonlinear memory), to check the task-shaped wall isn't an
      artifact of parity's easy classical baseline.
- [ ] **B10** **Cheap margin estimators at scale** (B5's flagged "most interesting
      open question"): at classically-hard sizes the margins can't be computed
      exactly — do inexpensive stochastic margin estimators preserve the law's
      predictive power?
- [ ] **B11** **Information-per-shot as a design objective:** optimize encoding /
      reservoir dynamics to concentrate task signal into a few high-magnitude
      observables, and verify via the law that the required shot budget drops.

## Pending push
(none — all B7 files pushed to GitHub on 2026-07-03 run 2 across 4 verified
commits: results [1c3ce8e], src code [c98d735], figure [05026f1], agenda [d9719d6].)

## Log
- 2026-07-03 — **Run recovered from empty outputs folder.** Cloned repo from
  GitHub to restore state (RESEARCH_AGENDA.md had not persisted). Installed
  qiskit + scikit-learn in sandbox. Executed **B6** (device-fidelity factor for
  the measurement-wall law): added `src/qrc_gatenoise.py` + `qrc_gatenoise_fig.py`,
  `results/gate_noise_law.json`, `results/RESULTS_GATENOISE.md`,
  `figures/qrc_gate_noise.png`. Hypothesis (gate noise enters the law only via a
  noiseless contraction factor c(γ), so acc(γ,S)=acc(0,S·c(γ)²)) was **largely
  confirmed**: 420 cells, collapse R²=0.927 vs 0.851 for ignoring gate noise, the
  fidelity factor's advantage growing monotonically with γ (at γ=0.20 it nearly
  halves prediction error, 7.2→4.6 pp). Honest residual ~3pp shows the contraction
  is approximately, not exactly, scalar. Committed all files + README update to
  GitHub (4 verified commits). **Next run: start B7** (per-node / covariance-
  corrected fidelity factor to close the residual). Remember to clone first and
  `pip install qiskit scikit-learn --break-system-packages`.

- 2026-07-03 (run 2) — **Recovered from empty outputs again; cloned repo to
  restore state.** Executed **B7** (per-node + shot-noise-covariance fidelity
  factor). Reused B6's 350 held-out achievable accuracies so only the design-time
  predictor changed (exact apples-to-apples). Added `src/qrc_pernode.py` +
  `qrc_pernode_fig.py`, `results/RESULTS_PERNODE.md`, `results/pernode_law.json`
  (+ `pn_part0/1.json`), `figures/qrc_pernode.png`. **Pre-registered hypothesis
  (per-node/covariance factor cuts collapse MAE by >30%) was FALSIFIED:** MAE fell
  only 2.89→2.82pp (2.5%). Diagnosis (the real finding): per-node contraction is
  genuinely heterogeneous (node spread 0.04→0.17 over γ) and σ² rises with γ, yet
  both corrections barely help because the dominant residual is a shot-budget-
  IRREDUCIBLE systematic negative bias (mean obs−pred = −3.9pp at γ=0.20) — gate
  noise degrades the achievable readout geometry, moving the reservoir OFF its
  noiseless curve rather than along it. Conclusion: B6's scalar c(γ) is near-
  optimal among effective-shot corrections; its high-γ predictions are a mild
  over-estimate. Files pushed to GitHub if a logged-in Chrome session was
  available (see Pending push). **Next run: start B8** (beyond-depolarizing noise
  — coherent / amplitude-damping / correlated errors; do coherent errors *rotate*
  the readout direction, matching B7's off-curve bias diagnosis?). Remember to
  clone first and `pip install qiskit qiskit-aer scikit-learn --break-system-packages`.
