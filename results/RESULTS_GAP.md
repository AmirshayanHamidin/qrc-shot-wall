# Benchmark 2: The Shot Wall — why the QRC gap doesn't close

Follow-up to `RESULTS.md`. Question: can the ~10× gap between shot-noisy QRC and its exact-feature floor be closed at fixed measurement budget? Answer: **no — not by any readout-side strategy tried, and the reason is quantifiable.**

Setup: NARMA5, 6-qubit reservoir, budget B = total shots/timestep (all Z/ZZ observables commute, so one computational-basis measurement per virtual node estimates all 21 features). Code: `qrc_gap_eval.py`. Reference points: exact-feature floor 0.0030 NMSE, tuned classical ESN 0.0138, classical linear on raw inputs alone 0.1483.

## What was tried at B = 40k shots/timestep

| Strategy | NMSE |
|---|---|
| Raw ridge (V=4) | 0.5815 |
| EMA + lags + input (V=4) | 0.1568 |
| PCA subspace denoising + lags + input | 0.1521 |
| PCA + EMA combo | 0.1515 |
| Errors-in-variables ridge (analytic noise covariance) | 0.1759 |
| Shot reallocation V=1 (all shots, one node) | **0.1417** |
| Sim-trained linear denoiser (noisy+inputs → exact feats) | 0.1519 |
| Sim-trained MLP denoiser (256×128) | 0.1533 |
| Classical linear on inputs only — **no quantum device** | 0.1483 |

Every strategy converges to ~0.15 (stable across noise seeds: 0.142/0.152/0.150). That number is not a coincidence — it is the NMSE of a classical linear model using only the input window. **At practical budgets, shot noise destroys essentially all information the quantum reservoir adds beyond what was classically available in the inputs.**

## Budget sweep (V=1, best mitigation)

| B (shots/timestep) | raw | mitigated |
|---|---|---|
| 4k | 0.83 | 0.151 |
| 40k | 0.58 | 0.142 |
| 400k | 0.30 | 0.128 |
| 4M | 0.14 | 0.078 |

Mitigated QRC first clearly beats the no-quantum baseline around B ≈ 4×10⁵; extrapolating the ~1/√B trend, reaching the exact floor needs B ~ 10⁹ — 4–5 orders of magnitude beyond typical hardware budgets. See [`figures/qrc_shot_wall.png`](../figures/qrc_shot_wall.png).

## Secondary findings

Diversity loses to SNR: at fixed budget, one virtual node with all shots beats 4–8 noisier nodes (0.142 vs 0.157–0.167). This predicts multi-basis measurement (splitting shots between Z and X bases) would also hurt — same diversity/SNR tradeoff.

The reservoir is not linearly redundant: a linear map from input history cannot reproduce the exact features (rel. err 0.90), and even an MLP trained on 2,300 simulated timesteps fails (0.89). The quantum features contain hard-to-learn nonlinear memory — which is precisely why losing them to shot noise matters, and why sim-trained denoisers don't rescue it.

EIV correction underperforms plain ridge: debiasing the Gram matrix increases variance more than it removes bias here.

## Implication for the 699 framing

The naive "shot-efficient QRC via better post-processing" project is dead on arrival — this benchmark kills it cleanly, which is worth knowing before pitching. The live reformulations, in order of promise:

1. **Information-per-shot as the design criterion for reservoirs.** The wall's height depends on how strongly the useful signal projects onto measured observables. Design reservoir unitaries / encodings that concentrate task-relevant information into few high-magnitude observables (connects to the group's encoding work: QPIXL, Monarq).
2. **Quantify the wall theoretically.** Fading memory time τ bounds temporal averaging; noise floor ~ 1/(B·τ) vs signal — a small theory contribution with clean experimental confirmation already in hand.
3. **Tasks where the wall sits lower.** Classification (coarse decisions tolerate noisy features) instead of regression on precise trajectories — plausibly where NISQ-era QRC actually has a niche.

## Caveats

One task (NARMA5), one reservoir topology, sampling noise only (no gate error — which makes the wall optimistic). Numbers from mostly single noise seeds except the plateau check; trends are large relative to seed variance (±0.005).
