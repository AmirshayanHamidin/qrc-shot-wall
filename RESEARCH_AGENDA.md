# RESEARCH_AGENDA.md — qrc-shot-wall overnight program

> **NOTE (reconstructed 2026-07-03):** the original agenda lived only in the session
> outputs folder, which is cleared between scheduled runs, so it was lost. This file was
> rebuilt from the GitHub remote (git log + README + results/) during the 2026-07-03 run.
> **To survive future clears, this agenda should itself be pushed to the repo** (see B-INFRA below).

Local repo copy: `outputs/qrc-shot-wall/` · Remote: github.com/AmirshayanHamidin/qrc-shot-wall

## HARD GUARDRAILS (never violate)
- **Simulation only.** numpy + qiskit-aer. NEVER submit to real IBM quantum hardware. NEVER read or use `ibm_token.txt`. Do not use qiskit-ibm-runtime's live service.
- **No other accounts/services.** The only external write allowed is pushing files to the GitHub repo above via the logged-in-Chrome web upload flow. Touch nothing else.
- **45-second shell limit.** Chunk long runs, save partial `.npy`/`.json`, aggregate in a later call. Never launch a computation that can't finish (or checkpoint) within one call.
- **Honesty.** Every benchmark states a hypothesis before running and reports negative results / residuals plainly. No result inflation.

## METHOD RULES
- Each benchmark: pre-stated falsifiable hypothesis → rigorous eval (multi-seed, error bars, holdout where relevant) → `RESULTS_<NAME>.md` + JSON + figure → update this Log + checkboxes → push.
- Reusable code: `src/qrc_law.py` (density-matrix engine + tasks + architectures), `src/law_eval_arch.py`, `src/qrc_gatenoise.py`, `qrc_hw*.py` patterns.
- Env has qiskit, qiskit-aer, scikit-learn, matplotlib preinstalled.

## STATUS — completed benchmarks
- [x] **B1 — QRC vs tuned classical baselines** (`RESULTS.md`). Fair-baseline hardening; ESN ties QRC once tuned.
- [x] **B2 — Eight gap-closing strategies / the shot wall** (`RESULTS_GAP.md`). All readout-side fixes plateau at the no-quantum classical baseline.
- [x] **B3 — The task-shaped wall** (`RESULTS_TASKSHAPE.md`). Classification retains ~86% of quantum benefit where regression retains ~4%.
- [x] **B4 — Hardware noise benchmark + live QPU** (`RESULTS_HARDWARE.md`). (Historical live ibm_marrakesh result 0.886 predates this agenda; **guardrails now forbid any new hardware runs — simulation only.**)
- [x] **B5 — Parameter-free measurement-wall law** (`RESULTS_LAW.md`). R²=0.991, MAE 1.3pp, 150 cells, zero fitted params.
- [x] **B6 — Device-fidelity factor (gate noise)** (`RESULTS_GATENOISE.md`). Global depolarizing → margin contraction c(γ); S_eff=S·c² collapses curves, R²=0.927 vs 0.851 naive, 420 cells. **Results write-up authored 2026-07-03 this run; compute + figure + JSON were from a prior run.**

## QUEUE — next work (B7 onward)
- [ ] **B7 — Cheap margin estimator at scale.** B5's open question: at classically-unsimulable sizes the decision margins must be *estimated*, not computed. Test whether a cheap estimator (few-shot margin probing, or a low-rank/stabilizer surrogate) predicts the shot budget well enough to keep the law useful. Pre-hypothesis: a small pilot shot budget spent on margin estimation pays for itself. **Recommended next.**
- [ ] **B8 — Gate-local / coherent noise vs the global depolarizing idealization.** B6 used a global depolarizing channel; does the c(γ) collapse survive gate-local depolarizing or coherent (over/under-rotation) noise, or does coherent error break the "just fewer shots" picture?
- [ ] **B9 — Readout retraining under noise.** B5/B6 fix the noiseless readout. Quantify how much retraining the linear readout on noisy features recovers, and whether the law's residual is mostly a suboptimal-readout artifact.
- [ ] **B10 — Second task family beyond NARMA/parity.** Whole program is one task family. Add an independent family (e.g. Mackey-Glass regression + a non-parity classification) to test external validity of the wall and the law.
- [ ] **B11 — Reservoir topology sweep.** One topology throughout. Sweep connectivity/depth to see whether "information-per-shot" can be designed to concentrate task signal in few high-magnitude observables (the README's redirected question).

## INFRASTRUCTURE
- [ ] **B-INFRA — Push this agenda to the repo** (e.g. `RESEARCH_AGENDA.md` at repo root or in `docs/`) so state survives outputs-folder clears. Currently the agenda is the single point of failure.

## LOG
- 2026-07-03 (this run): Recovered program state from GitHub after outputs folder was found empty (agenda + local repo lost to session clear). Re-cloned repo. Discovered B6 (gate noise) compute/figure/JSON existed as **uncommitted, unpushed** working-tree files with **no results write-up**. Authored `results/RESULTS_GATENOISE.md` from `results/gate_noise_law.json` (all numbers cross-checked against the JSON). Reconstructed this agenda. Next run: push the B6 files + this agenda, then start B7.

## PENDING PUSH (files created/modified locally, not yet on GitHub as of 2026-07-03)
- `results/RESULTS_GATENOISE.md` — NEW (this run)
- `results/gate_noise_law.json` — untracked (prior run)
- `figures/qrc_gate_noise.png` — untracked (prior run)
- `src/qrc_gatenoise.py`, `src/qrc_gatenoise_fig.py` — untracked (prior run)
- `README.md` — modified (benchmark-6 section, prior run)
- `RESEARCH_AGENDA.md` — NEW, recommend adding to repo (this run)
- Push method: logged-in Chrome → github.com/AmirshayanHamidin/qrc-shot-wall folder-scoped "Add file → Upload files" pages + commit. Could not confirm a logged-in Chrome session this run; left pending.
