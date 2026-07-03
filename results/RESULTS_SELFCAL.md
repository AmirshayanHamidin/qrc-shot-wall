# B6 — Self-calibrating measurement-wall law (v3 + post-hoc v4)

**Date:** 2026-07-03 (scheduled run) · **Code:** `src/b6_selfcal.py` · **Raw data:** `results/b6_selfcal.json` · **Figure:** `figures/b6_selfcal.png`

## Question

Benchmark 5 established the law: noisy accuracy = mean Φ(margin_i/σ_i), but it used the **exact** measurement distributions to compute margins and σ. Can an experimenter predict accuracy at any shot budget S using **only one noisy pilot** of S_pilot shots per time step — no exact distributions, no extra QPU time?

## Pre-stated hypothesis (frozen before running)

**H-B6v3:** A split-pilot self-calibration — half the pilot shots to fit readout w, the other half to estimate squared-margin-debiased margins and plug-in multinomial variances — predicts noisy accuracy at S ∈ {250, 1000, 4000, 16000, 64000} with
(a) MAE ≤ 3 pts and R² ≥ 0.85 over 150 cells (6 archs × 5 clf tasks × 5 budgets) at S_pilot = 8000;
(b) MAE decreasing monotonically in S_pilot ∈ {500, 2000, 8000};
(c) bagging w over 8 pilot bootstrap resamples reducing MAE at S_pilot = 500.

## Protocol

Fresh rebuild of all six architecture distribution tensors (`qrc_law.py build`, numpy density-matrix engine, simulation only). For each (arch, task, S_pilot): pilot = two independent multinomial samples at S_pilot/2 (halves A/B; pooled = full pilot). Readout: StandardScaler + LogisticRegression(C=1) on the train split (first 70% after washout), mapped back to raw feature space. Correct-signed margins ĝ_i and plug-in per-shot variances v_unit,i (multinomial covariance of w·x under p̂, summed over nodes) computed on the eval split (last 30%). Ground truth: accuracy of the **same frozen readout** on fresh multinomial samples at budget S, mean of 3 seeds. Truth samples shared across variants for paired comparison.

Variants: `nosplit` (v2 baseline: full pilot for both w and margins), `split` (w←A, margins←B), `split_bag` (split + 8-fold bagged w). Debiased predictor: acc_pred = mean Φ(sign(ĝ)·√max(ĝ²−v_pilot, 0)/σ_S).

## Results (150 cells per config)

| variant | S_p=500 | S_p=2000 | S_p=8000 |
|---|---|---|---|
| nosplit (v2) | 8.96 / 0.57 | 6.16 / 0.76 | **4.16 / 0.90** |
| split | 8.74 / 0.54 | 7.46 / 0.69 | 5.71 / 0.81 |
| split_bag | 8.37 / 0.55 | 7.45 / 0.66 | 5.79 / 0.81 |
| gauss_full (v4, post-hoc) | 8.76 / 0.60 | 5.61 / 0.80 | **3.80 / 0.92** |
| gauss_split (v4, post-hoc) | 8.58 / 0.55 | 6.66 / 0.74 | 5.12 / 0.85 |

Cells are MAE (pts) / R².

**Verdict on H-B6v3: (a) FAIL, (b) PASS, (c) marginal.**

- (a) FAIL — the split variants reach only 5.7–5.8 pts MAE, R² ≈ 0.81 at S_pilot = 8000, far from the ≤3 pt target. Even the best variant overall (post-hoc v4 gauss_full: 3.80 pts, R² = 0.915) misses the 3 pt bar.
- (b) PASS — MAE decreases monotonically in S_pilot for every variant.
- (c) marginal — bagging helped at S_pilot = 500 (8.74 → 8.37 pts) but the effect is small (−0.4 pts) and vanishes at larger pilots.

**Surprise #1 — splitting hurts.** The live-session diagnosis ("the limiting factor is w-estimation from noisy pilots, so isolate it") predicted splitting would help. The opposite holds at every pilot budget: halving the shots behind both w and the margins costs more than the w–margin correlation bias it removes. The v1 failure (R² = −1.74) was evidently caused by the unregularized C=1000 readout, not by reuse of the pilot; with C=1, reuse is benign.

**Surprise #2 — a smoothing identity beats debiasing.** If ĝ ~ N(g, v_pilot), then E[Φ(g/σ_S)] under the flat-prior posterior g|ĝ is exactly Φ(ĝ/√(σ_S² + v_pilot)) — no debiasing, no sign heuristics. This `gauss` predictor dominates the debiased one in R² at every configuration and in MAE everywhere except S_pilot=500 nosplit (where both are poor). It is also better-behaved: the hard sign(ĝ) step in the debiased predictor is exactly what breaks near the boundary.

**Where the remaining error lives (gauss_full, S_pilot = 8000):** MAE by target budget: 1.5 pts at S=250, 2.2 at 1000, 3.5 at 4000, 5.7 at 16000, 6.1 at 64000. Predicting **cheaper** budgets than the pilot is nearly solved (≤ 2.2 pts); the hard regime is extrapolating **upward** to S ≫ S_pilot, where σ_S ≪ √v_pilot and the prediction saturates at the pilot's own uncertainty (Φ(ĝ/√v_pilot) < 1 even when the true readout is perfect — visible as under-prediction of high-accuracy cells in the figure). Per-arch (S_pilot=8000): arch 1 already meets the 3 pt bar (2.77), archs 2–4 sit at 3.1–3.7, archs 0 and 5 at ~4.8.

## Honesty section

- The headline v4 (`gauss_full`) numbers are **post-hoc**: the variant was designed after seeing the v3 failure pattern within this session. Confirmatory status requires re-testing on fresh pilot seeds; treat H-B6v3 as refuted and v4 as an exploratory finding.
- Plug-in variance uses p̂ from the pilot itself; at S_pilot = 500 many bitstring cells have zero counts and v_unit is underestimated. No correction attempted.
- Flat-prior Gaussian posterior on g is a modeling choice; margins near separability are non-Gaussian (logistic w is data-dependent).
- Ground truth uses 3 sampling seeds; residual truth noise ~0.5–1 pt inflates MAE slightly for all variants equally.
- Architecture tensors were rebuilt from scratch this run (fresh workspace); b6_part1/2 JSONs from the live session were not reused. The v1/v2 numbers cited are from the agenda log, not re-derived.
- All results are numpy/qiskit `Operator` simulation. No hardware, no IBM token.

## Next steps

1. **Confirmatory v4 run:** freeze `gauss_full` as the method, new pilot seeds, pre-state MAE ≤ 4 pts / R² ≥ 0.90 at S_pilot = 8000. Cheap (≈ 3 s/arch).
2. **Upward extrapolation fix:** the S ≫ S_pilot regime needs either a better prior on g (empirical Bayes shrinkage of margin distribution) or reporting predictions as intervals [Φ(ĝ/√(σ²+v)), Φ(ĝ/σ)].
3. Then proceed to B7 (gate noise as margin shrinkage, FakeTorino).
