# RESEARCH_AGENDA.md — qrc-shot-wall overnight program

> **NOTE:** the canonical agenda lives BOTH in the session outputs folder (cleared between
> scheduled runs) and in the repo root (durable). Always trust the repo copy on `main`;
> the outputs copy is scratch. **Re-numbering note (2026-07-03):** benchmark numbers now
> follow the repo's actual write-up sequence B1..B9, which had drifted from an older queue
> that labelled the margin-estimator study "B7". They have been reconciled below.

Local repo copy: `outputs/qrc-shot-wall/` · Remote: github.com/AmirshayanHamidin/qrc-shot-wall

## HARD GUARDRAILS (never violate)
- **Simulation only.** numpy + qiskit-aer (or numpy density matrix + qiskit unitary). NEVER submit to real IBM quantum hardware. NEVER read or use `ibm_token.txt`. Do not use qiskit-ibm-runtime's live service.
- **No other accounts/services.** The only external write allowed is pushing files to the GitHub repo above via the logged-in-Chrome web upload flow. Touch nothing else.
- **45-second shell limit.** Chunk long runs, save partial `.npy`/`.json`, aggregate in a later call. Never launch a computation that can't finish (or checkpoint) within one call.
- **Honesty.** Every benchmark states a hypothesis before running and reports negative results / residuals plainly. No result inflation.
- **Env note (2026-07-03):** the sandbox python did NOT have qiskit/sklearn preinstalled this run; installed via `pip install qiskit scikit-learn matplotlib --break-system-packages`. Budget ~1 call for this if the env is fresh again.

## METHOD RULES
- Each benchmark: pre-stated falsifiable hypothesis → rigorous eval (multi-seed, error bars, holdout where relevant) → `RESULTS_<NAME>.md` + JSON + figure → update this Log + checkboxes → push.
- Reusable code: `src/qrc_law.py` (density-matrix engine + tasks + architectures + `zdiags`, `feats_from_P`, `perf`, `build`), `src/qrc_gatenoise.py` (c(γ) collapse), `src/qrc_pernode.py`, `src/qrc_beyondnoise.py`, `src/qrc_marginest.py`, `qrc_hw*.py`.

## STATUS — completed benchmarks
- [x] **B1 — QRC vs tuned classical baselines** (`RESULTS.md`). ESN ties QRC once tuned.
- [x] **B2 — Eight gap-closing strategies / the shot wall** (`RESULTS_GAP.md`). All readout-side fixes plateau at the no-quantum classical baseline.
- [x] **B3 — The task-shaped wall** (`RESULTS_TASKSHAPE.md`). Classification retains ~86% of quantum benefit where regression retains ~4%.
- [x] **B4 — Hardware noise benchmark + live QPU** (`RESULTS_HARDWARE.md`). (Historical live ibm_marrakesh 0.886 predates this agenda; **guardrails now forbid any new hardware runs — simulation only.**)
- [x] **B5 — Parameter-free measurement-wall law** (`RESULTS_LAW.md`). R²=0.991, MAE 1.3pp, 150 cells, zero fitted params.
- [x] **B6 — Device-fidelity factor (gate noise)** (`RESULTS_GATENOISE.md`). Global depolarizing → margin contraction c(γ); S_eff=S·c² collapses curves, R²=0.927 vs 0.851 naive, 420 cells.
- [x] **B7 — Per-node + covariance refinement** (`RESULTS_PERNODE.md`, *honest negative*). Pre-registered >30% MAE cut; delivered 2.5% (2.89→2.82 pp). B6's residual is a shot-irreducible *off-curve* bias, not per-node/covariance error.
- [x] **B8 — Beyond depolarizing** (`RESULTS_BEYONDNOISE.md`). Scalar c(η) is depolarizing-specific: fails R²>0.9 bar on coherent/amp-damping/dephasing. Coherent errors *rotate* the readout (recoverable by retraining); non-unital amplitude damping (T₁) is the shot-irreducible case.
- [x] **B9 — Cheap margin/separation estimation at scale** (`RESULTS_MARGINEST.md`). *This run.* Naive plug-in `‖μ̂₁−μ̂₀‖` optimistically biased (up to +41% on hardest task @250-shot pilot); parameter-free pilot-only variance-subtraction correction removes it to ≤0.8% bias, ~3% RMSE @1k pilot shots (≈6% budget error). The margin-based law survives estimation, not just computation. 60 configs × 40 seeds.

## QUEUE — next work (B10 onward)
- [ ] **B10 — Readout retraining under noise (dedicated study).** B5/B6 fix the noiseless readout; B8 retrains per-channel as a side effect. Quantify systematically how much retraining the linear readout on noisy features recovers the law's residual, and whether the residual is mostly a suboptimal-readout artifact. **Recommended next.**
- [ ] **B11 — Second task family beyond NARMA/parity.** Whole program is one task family. Add an independent family (e.g. Mackey-Glass regression + a non-parity classification, e.g. sign-of-correlation) to test external validity of the wall and the law.
- [ ] **B12 — Reservoir topology sweep.** One topology throughout. Sweep connectivity/depth to see whether "information-per-shot" can be designed to concentrate task signal in few high-magnitude observables (the README's redirected question).
- [ ] *(open sub-question from B9)* cheap estimation of the full **per-sample margin distribution** (not just D₀), where the same bias-correction logic applies but is noisier per sample.

## INFRASTRUCTURE
- [x] **B-INFRA — agenda pushed to repo root** so state survives outputs-folder clears. Keep updating the repo copy each run.

## LOG
- 2026-07-03 (run A): Recovered state from GitHub (outputs empty). Discovered B6 gate-noise compute existed unpushed with no write-up. Authored `RESULTS_GATENOISE.md`, reconstructed agenda, pushed B6 + agenda. (Later runs then added B7 pernode + B8 beyondnoise, pushed, but did NOT update README/agenda.)
- 2026-07-03 (run B, this run): Found outputs empty again; a *stale* local clone made B6 look unfinished, but a fresh clone showed the remote is at B8 (B6/B7/B8 all pushed). Verified B6 data independently (reproduced collapse R²=0.927/naive 0.851 exactly). Picked the genuinely-undone, B5-flagged "cheap margin estimator" open question as **B9**. Built it on `qrc_law.py`: 60 configs (3 arch × 5 clf tasks × 4 pilot budgets) × 40 seeds. Pre-registered H_bias + H_fix both **confirmed** (naive optimistically biased, pilot-only correction removes it). Wrote `RESULTS_MARGINEST.md` + `results/marginest_law.json` + `figures/qrc_marginest.png` + `src/qrc_marginest{,_fig}.py`; updated README with a benchmarks 7–9 section (README had been stuck at 5–6) and this agenda. Next run: **B10 (readout retraining under noise)**.

## PENDING PUSH
- Files staged in `outputs/b9_push/` this run, to push to github.com/AmirshayanHamidin/qrc-shot-wall via logged-in Chrome web-upload flow:
  - `results/RESULTS_MARGINEST.md`, `results/marginest_law.json`
  - `figures/qrc_marginest.png`
  - `src/qrc_marginest.py`, `src/qrc_marginest_fig.py`
  - `README.md` (adds benchmarks 7–9 section), `RESEARCH_AGENDA.md` (this file)
- Push method: logged-in Chrome → folder-scoped GitHub "Add file → Upload files" page per target folder → commit. Verify each file appears on `main` after commit.
