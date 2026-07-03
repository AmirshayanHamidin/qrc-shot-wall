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
- [x] **B10 — Readout retraining under noise** (`RESULTS_RETRAIN.md`). *This run.* The B5/B6 probit is an almost-exact model of the **fixed** noiseless-design readout (R²=0.948, MAE 0.74pp / 0.14pp on gate-noisy cells) but that readout collapses ~24.5pp below the **retrained**-on-noisy reachable accuracy. 99.5% of the law-vs-reachable residual is the retraining gain (corr −0.9997). Retraining is load-bearing; the law is really a retrained-readout law. Caveat: perfect-exact-separation regime (arch0/1). 160 cells.

## QUEUE — next work (B11 onward)
- [ ] **B11 — Second task family beyond NARMA/parity.** Whole program is one task family. Add an independent family (e.g. Mackey-Glass regression + a non-parity classification, e.g. sign-of-correlation) to test external validity of the wall and the law.
- [ ] **B12 — Reservoir topology sweep.** One topology throughout. Sweep connectivity/depth to see whether "information-per-shot" can be designed to concentrate task signal in few high-magnitude observables (the README's redirected question).
- [ ] *(open sub-question from B9)* cheap estimation of the full **per-sample margin distribution** (not just D₀), where the same bias-correction logic applies but is noisier per sample.
- [ ] *(follow-up from B10)* **encoding-gain sweep**: vary encoding strength from perfect exact separation down to the wall, mapping retraining gain vs exact-margin headroom — does the fixed/retrained readout gap close smoothly as exact separation degrades (reconciling B10's 25pp with B5's tiny residual)?

## INFRASTRUCTURE
- [x] **B-INFRA — agenda pushed to repo root** so state survives outputs-folder clears. Keep updating the repo copy each run.

## LOG
- 2026-07-03 (run A): Recovered state from GitHub (outputs empty). Discovered B6 gate-noise compute existed unpushed with no write-up. Authored `RESULTS_GATENOISE.md`, reconstructed agenda, pushed B6 + agenda. (Later runs then added B7 pernode + B8 beyondnoise, pushed, but did NOT update README/agenda.)
- 2026-07-03 (run B, this run): Found outputs empty again; a *stale* local clone made B6 look unfinished, but a fresh clone showed the remote is at B8 (B6/B7/B8 all pushed). Verified B6 data independently (reproduced collapse R²=0.927/naive 0.851 exactly). Picked the genuinely-undone, B5-flagged "cheap margin estimator" open question as **B9**. Built it on `qrc_law.py`: 60 configs (3 arch × 5 clf tasks × 4 pilot budgets) × 40 seeds. Pre-registered H_bias + H_fix both **confirmed** (naive optimistically biased, pilot-only correction removes it). Wrote `RESULTS_MARGINEST.md` + `results/marginest_law.json` + `figures/qrc_marginest.png` + `src/qrc_marginest{,_fig}.py`; updated README with a benchmarks 7–9 section (README had been stuck at 5–6) and this agenda. Next run: **B10 (readout retraining under noise)**.
- 2026-07-03 (run C, this run): Outputs empty again; a stale `/tmp` clone (B5-era) again made B6 look unpushed — **caught before pushing** by checking the live remote, which is at **B9** (40 commits). Discarded the stale reconstruction (did NOT push it — would have regressed the repo). Fresh-cloned, executed the queued **B10**. Pre-registered H0/H1; **H0 confirmed decisively**: closed-form probit predicts the fixed noiseless-design readout to 0.14pp on gate-noisy cells (R²=0.948 overall), but the fixed readout collapses ~24.5pp below retrained reachable accuracy; 99.5% of the B6-style residual is the retraining gain (corr −0.9997). Wrote `RESULTS_RETRAIN.md` + `results/retrain_law.json` + `figures/qrc_retrain.png` + `src/qrc_retrain{,_fig}.py`; updated README (benchmark-10 line) and this agenda. Honest caveat recorded: perfect-exact-separation regime; encoding-gain sweep queued to reconcile with B5. Next run: **B11 (second task family)**.

## PENDING PUSH
- B10 bundle, to push to github.com/AmirshayanHamidin/qrc-shot-wall via logged-in Chrome web-upload flow:
  - `results/RESULTS_RETRAIN.md`, `results/retrain_law.json`
  - `figures/qrc_retrain.png`
  - `src/qrc_retrain.py`, `src/qrc_retrain_fig.py`
  - `README.md` (adds benchmark-10 line), `RESEARCH_AGENDA.md` (this file)
- Push method: logged-in Chrome → folder-scoped GitHub "Add file → Upload files" page per target folder → commit. Verify each file appears on `main` after commit.
