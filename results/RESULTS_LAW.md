# Benchmark 5: A predictive law for the measurement wall

**Claim (calibrated):** the accuracy of a shot-noise-limited quantum reservoir classifier is predictable *before any noisy run*, from three noiseless quantities: the readout direction, the per-sample decision margins, and the exact multinomial shot-noise covariance projected onto that direction. Across **150 benchmark cells** (5 tasks × 6 reservoir architectures × 5 shot budgets), the parameter-free prediction achieves **R² = 0.991, mean absolute error 1.3 percentage points**. Code: `src/qrc_law.py`, `src/law_eval_arch.py`; raw cells: `results/law_theory.json`; figure: `figures/qrc_law.png`.

## How we got here (including the failure)

We pre-stated a hypothesis: retained quantum benefit collapses onto a universal curve in naive SNR (feature signal std × √shots). **It failed** — R² = 0.20 with systematic task-dependent violations: easy tasks (majority vote) sat far above the curve, hard tasks (parity-4) far below. The failure pattern pointed at the missing variable: what matters is not how much features vary, but how far apart the *classes* sit along the readout direction — the decision margin.

Refining once (margin × √shots, fitted curve) gave holdout R² = 0.80 on architectures never used in fitting. The final step removed the fitted curve entirely: for each test sample, the exact shot-noise variance along the readout direction is computable in closed form from the stored measurement distribution (multinomial covariance, σ² = Σ_nodes [Σ_j p_j q_j² − (p·q)²]/S with q = Zᵀw), giving a per-sample flip probability Φ(−margin/σ). Predicted accuracy is just the average. No parameters, no fitting.

## What it means

1. **The task-shaped wall (benchmark 3) is now explained, not just observed.** Regression exposes the full noise σ in its output; classification hides noise inside its margins. Retention is high exactly when margins × √S exceeds ~1 — a computable condition.
2. **A design tool:** simulate your reservoir noiselessly (cheap classically at design sizes), compute margins and projected noise, and read off the hardware shot budget your task needs — *before* spending quantum time. Applied retroactively, this law predicts our own live-QPU choice: at 6,000 shots the parity-3 margins put predicted accuracy at the shot-noise ceiling, which is what ibm_marrakesh delivered (0.886).
3. **A reporting standard candidate:** QRC papers could report margin-normalized shot budgets instead of raw shot counts, making claimed results comparable across tasks and devices.

## What this is not

Honesty section, as always. The statistical machinery (Gaussian projection of multinomial noise, probit link, matched-filter margins) is classical and standard — no new statistics were invented. The contribution is the validated *application*: demonstrating that this closed-form prediction is accurate at 1-point precision across a wide QRC design grid, and using it to explain and quantify the measurement wall. Limitations: shot noise only (gate noise shrinks margins — extending the law to include a device fidelity factor is the natural next step); fixed linear readout (retraining on noisy features deviates slightly); classically simulable sizes (at scale, margins must be estimated rather than computed — whether cheap margin estimators exist is an open question and the most interesting one here).

## Scale of evidence

180 grid cells run in total (150 classification + 30 regression), 6 reservoir architectures (4–6 qubits, varying depth, window, encoding gain, readout nodes), 5 task families, 5 shot budgets spanning 250–64,000, multi-seed sampling, with a fit/holdout split at the curve-fitting stage and zero free parameters at the final stage.
