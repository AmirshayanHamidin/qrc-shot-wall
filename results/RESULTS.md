# QRC Benchmark Results — first pass toward the 699 pitch

## Setup

Gate-based quantum reservoir computing (Fujii–Nakajima style, adapted to circuits): 6-qubit reservoir, fixed random Ising-like entangling unitary (built in Qiskit), input injected each timestep by resetting qubit 0 to an input-dependent state (dissipation → fading memory), 4 virtual nodes, features = ⟨Z_i⟩ and ⟨Z_iZ_j⟩ (84 total), ridge readout. Tasks: NARMA2/NARMA5, T=1200, NMSE on held-out test. Baselines: memory-matched linear regression and a hyperparameter-tuned classical echo state network with matched feature count.

Code: `qrc_benchmark.py` (core), `qrc_full_eval.py` (evaluation). Runs in ~20 s on CPU.

## Headline numbers (NMSE, lower is better)

| Model | NARMA2 | NARMA5 |
|---|---|---|
| QRC, exact expectations (5 seeds) | 0.0062 ± 0.0003 | 0.0147 ± 0.0018 |
| Classical ESN, tuned, 84 nodes | 0.0029 | 0.0138 |
| Linear on input window | 0.1735 | 0.1483 |
| QRC @ 10k shots, raw | 0.266 | 0.586 |
| QRC @ 10k shots, mitigated | — | **0.165** |
| QRC @ 1k shots, raw | 0.564 | 0.867 |
| QRC @ 1k shots, mitigated | — | **0.207** |

## Three findings

**1. Untuned baselines flatter QRC.** With default ESN settings, QRC won by 14× on NARMA5. After a fair hyperparameter grid, the tuned ESN matches QRC (0.0138 vs 0.0147). Lesson for reading QRC papers: check how hard the classical baseline was tuned.

**2. Shot noise, not expressivity, is the practical bottleneck.** With exact expectations QRC is excellent; with realistic finite sampling even 100k shots per readout degrades NMSE by ~20×. Any hardware run inherits this. Tuning readout regularization to the shot budget barely helps (0.586 → 0.579) — the noise destroys temporal information the ridge can't recover.

**3. Cheap classical post-processing recovers 3.5–4×.** Exponential smoothing of the feature stream + lagged feature stacking + appending the raw input window: 0.586 → 0.165 at 10k shots; 0.867 → 0.207 at 1k shots. Zero additional quantum cost. Still ~10× above the exact-feature floor — that gap is open.

## The 699 pitch this sets up

"Shot-efficient quantum reservoir computing": systematic study of strategies to close the shot-noise gap — adaptive shot allocation across virtual nodes/observables, noise-robust observable selection, temporal-structure-aware readouts, and validation on IBM hardware. Directly extends Shah & Bethel (IPDPS QHPC 2026) 'optimization strategies' framing; connects to the group's encoding work (which observables survive sampling noise is an encoding question).

Milestones: (1) reproduce on real IBM backend via the free tier, (2) implement + compare mitigation strategies, (3) writeup targeting the same IPDPS workshop next cycle.

## Caveats

Single task family (NARMA); no hardware noise model beyond sampling; mitigation numbers from one reservoir seed; ESN comparison at matched feature count, not matched wall-clock. All worth tightening before showing Bethel — but the phenomenon (shot-noise dominance + partial classical recovery) is robust across the settings tried.
