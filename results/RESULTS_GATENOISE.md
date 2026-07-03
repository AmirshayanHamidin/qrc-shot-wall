# Benchmark 6: A device-fidelity factor for the measurement-wall law

**Claim (calibrated).** Benchmark 5's measurement-wall law was validated for *shot* noise only. Its own stated next step was that "gate noise shrinks margins, so extending the law with a device-fidelity factor is the natural next step." This benchmark supplies and tests that factor. **To leading order, depolarizing gate noise enters the law as nothing more than an effective-shot reduction:** a single, *parameter-free, noiselessly-computable* contraction factor `c(γ)` rescales the shot axis by `c(γ)²` and collapses every gate-noisy accuracy-vs-shots curve back onto the noiseless one. Across **420 benchmark cells** (2 architectures × 5 classification tasks × 6 gate-noise strengths × 7 shot budgets), predicting gate-noisy achievable accuracy from the noiseless curve at `S_eff = S·c(γ)²` gives **R² = 0.927, mean absolute error 2.9 pp**, versus **R² = 0.851, MAE 4.2 pp** for the naive prediction that ignores gate noise. The fidelity factor's advantage grows monotonically with gate-noise strength, nearly halving the error at the strongest noise tested (γ = 0.20: 7.2 pp → 4.6 pp). Code: `src/qrc_gatenoise.py`, `src/qrc_gatenoise_fig.py`; raw cells: `results/gate_noise_law.json`; figure: `figures/qrc_gate_noise.png`.

## Pre-stated hypothesis (stated before running)

A global depolarizing channel `ρ → (1−γ)ρ + γ·I/d` applied at each reservoir step multiplies every non-identity Pauli expectation — i.e. every Z_i and Z_iZ_j readout feature — by a contraction factor. Because a linear readout's decision margins are linear in those expectations, gate noise contracts every margin by the noiseless-computable quantity

```
c(γ) = ‖μ₁(γ) − μ₀(γ)‖ / ‖μ₁(0) − μ₀(0)‖
```

(the ratio of between-class mean-feature separations, measured on *exact/noiseless* features). Shot noise on each feature scales as `1/√S` roughly independently of γ, so class SNR ∝ separation·√S. Equal SNR then predicts gate noise is exactly equivalent to reducing the effective shot budget by `c(γ)²`:

> **H0:** `acc(γ, S) = acc(0, S·c(γ)²)`. One noiseless number per γ collapses all curves.
>
> **H1 (falsification):** after rescaling by `c(γ)²` the curves do *not* collapse → gate noise does something beyond scalar margin contraction (reshapes the shot-noise covariance or the achievable readout direction), and a scalar fidelity factor is insufficient.

## Method

Same 6-qubit gate-based reservoirs as benchmarks 3–5 (architectures 0 and 1 from `qrc_law.py`), density-matrix simulation in numpy with the qiskit-built reservoir unitary. Gate noise is a global depolarizing channel applied after every unitary step; readout noise is exact multinomial sampling of the measurement distributions. "Achievable accuracy" is a logistic readout (C = 1) **retrained on the noisy features at each budget** — the honest reachable accuracy used in benchmark 3, averaged over 3 sampling seeds. Five temporal classification tasks (parity-2/3/4, delay-XOR, majority-3), six gate strengths γ ∈ {0, 0.02, 0.05, 0.10, 0.15, 0.20}, seven budgets 500–32,000. The contraction `c(γ)` is computed once per (arch, task, γ) from noiseless features only. The collapse test predicts each γ>0 cell from a log-S interpolation of that cell's own γ=0 curve evaluated at `S·c(γ)²`; the naive baseline evaluates the same interpolation at raw `S`.

## Result

The measured contraction factors are smooth and monotone (arch 0: c = 0.93, 0.82, 0.68, 0.57, 0.53 at γ = 0.02…0.20), and gate noise visibly translates the accuracy-vs-shots curve rightward (Panel A) — the wall moves, the reservoir simply needs more shots. Rescaling the shot axis by the noiseless `c(γ)²` pulls the curves back together (Panel B), and the aggregate prediction error confirms it (Panel C):

| γ | mean c(γ) | naive MAE (pp) | law+fidelity MAE (pp) |
|---|---|---|---|
| 0.02 | 0.92 | 2.1 | 1.8 |
| 0.05 | 0.82 | 2.7 | 2.0 |
| 0.10 | 0.68 | 3.9 | 2.8 |
| 0.15 | 0.57 | 4.9 | 3.2 |
| 0.20 | 0.48 | 7.2 | 4.6 |

The fidelity factor helps everywhere and helps *more* as gate noise grows, exactly as H0 predicts: at weak noise the correction is small (both predictions are good), and at strong noise, where ignoring gate error costs 7 pp, the parameter-free factor recovers most of it. Overall the fidelity-corrected law explains the gate-noisy accuracy at R² = 0.927 with no fitted parameters.

## What it means

The measurement-wall law extends to noisy hardware with a single design-time number. You simulate your reservoir noiselessly *with the depolarizing channel switched on* (cheap classically at design sizes), read off `c(γ)` as a feature-separation ratio, and multiply your required shot budget by `1/c(γ)²`. Combined with benchmark 5, a QRC practitioner can now estimate the hardware shot budget a classification task needs **before spending any quantum time**, accounting for both readout sampling and gate fidelity. It also sharpens the benchmark-3 story: gate noise does not change *which* tasks sit below the wall (coarse-output classification), it only raises the shot price of staying below it, by a computable factor.

## Honest limitations and the residual

This is a *leading-order* result, and the residual matters. H0 is confirmed but not exactly: even after the `c(γ)²` rescaling the collapse MAE is ~2.9 pp, not driven to the shot-noise floor, and the residual grows with γ (1.8 pp at γ=0.02 to 4.6 pp at γ=0.20). So gate noise is *not* a perfectly scalar effective-shot reduction — the contraction is slightly task- and node-dependent (each virtual-node readout sees a different number of noisy steps, so a single scalar `c` per cell is an approximation), and depolarizing also mildly reshapes the multinomial covariance the shot-noise term assumes to be γ-independent. A per-node contraction or a covariance correction would likely close part of the gap; whether that is worth the extra machinery over the scalar factor is the natural follow-up. Further caveats: one noise model (global depolarizing — real devices add coherent and correlated errors that need not contract margins so cleanly), two architectures, sampling+gate noise only, and `c(γ)` measured from a class-mean separation rather than the exact per-sample margin used in benchmark 5's tighter predictor. The honest headline is therefore: **a scalar, parameter-free depolarizing fidelity factor captures the majority of gate noise's effect on the measurement wall, increasingly dominating the prediction as noise grows — but a few points of residual show the wall's response to gate noise is approximately, not exactly, "just fewer shots."**

## Scale of evidence

420 cells (2 architectures × 5 tasks × 6 gate strengths × 7 shot budgets), 3 sampling seeds each, gate strengths spanning fidelity contraction c = 1.0 → 0.48, budgets 500–32,000, zero free parameters in the fidelity factor (measured from noiseless features), with the γ=0 curve used only as the interpolation reference and every γ>0 cell held out from it.
