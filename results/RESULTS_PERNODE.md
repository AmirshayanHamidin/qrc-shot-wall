# Benchmark 7: A per-node + shot-noise-covariance fidelity factor — and why it barely helps (honest negative result)

**Claim (calibrated, and the pre-registered hypothesis is FALSIFIED).** Benchmark 6 established that depolarizing gate noise enters the measurement-wall law, to leading order, as a single scalar effective-shot reduction `S_eff = S·c(γ)²`, and left a ~3 pp residual that grows with γ. B6 named two suspected causes: (i) each virtual node sees a **different** number of noisy steps, so a single scalar contraction is only an average, and (ii) depolarizing flattens the measurement distribution and thus **changes the shot-noise covariance** the `S_eff` trick assumes γ-independent. B7 built a parameter-free correction that fixes **both** and pre-registered success as *cutting the collapse MAE by >30%*. **It does not.** On the identical 350 held-out accuracy cells from B6, the per-node + covariance factor reduces MAE from 2.89 pp (B6 scalar) to only 2.82 pp — a **2.5% reduction, far below the 30% threshold**. The hypothesis is falsified: the residual is *not* dominated by either suspected mechanism. Instead the residual is a **shot-budget-irreducible negative bias** — gate noise moves the reservoir *off* the noiseless accuracy-vs-shots curve, not merely along it, so no rescaling of the shot axis can remove it. Code: `src/qrc_pernode.py`, `src/qrc_pernode_fig.py`; raw output: `results/pernode_law.json` (+ `pn_part{0,1}.json`); figure: `figures/qrc_pernode.png`.

## Pre-stated hypothesis (stated before running)

For a linear readout the class-discrimination SNR² is additive over independent feature blocks (virtual nodes):

```
SNR(γ,S)²  =  Σ_v  S · ‖Δμ_v(γ)‖² / σ_v²(γ)
```

where node block `v` has between-class separation `Δμ_v` and mean single-shot feature variance `σ_v² = mean_j (1 − m_{v,j}²)` (exact, noiseless-computable; `m` are the exact expectation values, and each Z_i / Z_iZ_j observable has eigenvalues ±1 so its single-shot variance is `1 − m²`). Matching total SNR² to the γ=0 curve gives a single effective budget

```
S_eff_pn = S · [ Σ_v ‖Δμ_v(γ)‖² / σ_v²(γ) ] / [ Σ_v ‖Δμ_v(0)‖² / σ_v²(0) ].
```

This reduces to B6's `S·c²` when `σ_v` is γ-independent and all nodes contract equally. Because `σ_v²` **rises** with γ (distributions flatten toward uniform), the per-node factor predicts a **smaller** effective budget than B6, i.e. it should remove B6's suspected high-γ over-prediction.

> **H0:** `S_eff_pn` collapses the γ>0 curves with **>30% lower MAE** than B6's `S·c²`.
> **H1 (falsification):** it does not → the residual is dominated by something else (readout-direction rotation / off-curve degradation), and the extra machinery is not worth it.

## Method

Identical reservoirs, tasks, noise model, and budgets as B6 (architectures 0 and 1; parity-2/3/4, delay-XOR, majority-3; γ ∈ {0, 0.02, 0.05, 0.10, 0.15, 0.20}; budgets 500–32,000). **Crucially, B7 reuses B6's measured achievable accuracies verbatim** (`gate_noise_law.json` cells) — only the *design-time predictor* changes, so the comparison is exactly apples-to-apples on one accuracy dataset. We recompute the noiseless per-node quantities `Δμ_v(γ)` and `σ_v²(γ)` from the same density-matrix reservoirs, form `S_eff_pn`, and re-run B6's log-S interpolation of each cell's own γ=0 curve. Four predictors are compared on the 350 held-out (γ>0) cells: **naive** (`S`), **B6 scalar** (`S·c²`, reproduced), **scalar-cov** (`S·c²·κ`, κ = σ̄²(0)/σ̄²(γ) over the whole vector), and **B7 per-node** (`S_eff_pn`). Simulation only (numpy + qiskit unitary); no hardware, no runtime service.

## Result

| predictor | R² | MAE (pp) | MAE reduction vs B6 |
|---|---|---|---|
| naive (no fidelity factor) | 0.851 | 4.16 | — |
| **B6 scalar** `S·c²` | 0.927 | 2.89 | (baseline) |
| + shot-noise covariance | 0.930 | 2.82 | 2.4% |
| **B7 per-node + covariance** | 0.930 | 2.82 | **2.5%** |

The per-node structure B7 was built to exploit is genuinely there (Panel A): later nodes, which pass through more noisy steps, contract more, and the spread between nodes grows from 0.04 at γ=0.02 to **0.17** at γ=0.20. The shot-noise variance also rises exactly as predicted (σ² ≈ 0.87→0.98 as γ: 0→0.20). Both mechanisms are real — yet correcting for both moves the aggregate MAE by only 0.07 pp (Panel B). Per γ, the correction helps most at the strongest noise (γ=0.20: 4.64→4.48 pp) but never approaches the 30% pre-registered bar.

**Why it fails is the actual finding (Panel C).** Decomposing the residual shows B6 does not scatter symmetrically about the truth — it carries a **systematic negative bias**: mean(observed − predicted) = −0.9, −1.5, −3.9 pp at γ = 0.05, 0.10, 0.20. The reservoir's *observed* accuracy is consistently **lower** than any point on its own γ=0 curve. The per-node/covariance correction pushes `S_eff` down (the right direction) and shaves the bias only slightly (−3.9→−3.7 pp at γ=0.20). A bias that survives every shot-budget rescaling cannot be a shot-budget effect: gate noise degrades the *achievable readout geometry* itself (the retrained logistic direction on flattened, noise-mixed features is worse than the γ=0 direction at the matched SNR), pushing the operating point **off** the noiseless curve rather than sliding it along.

## What it means

B6's scalar fidelity factor is not merely a convenient approximation that finer bookkeeping would improve — it is **near-optimal within the entire class of "effective-shot" corrections.** Adding per-node contraction and covariance terms, the two most physically-motivated refinements, buys essentially nothing (2.5%). The measurement wall's response to depolarizing noise therefore decomposes into (a) a large, cleanly-scalar shot-budget contraction that B6 already captures, plus (b) a smaller, **irreducibly off-curve** degradation that no shot-axis rescaling can absorb. For a practitioner this is good news wrapped in a caveat: keep B6's one-number `c(γ)` recipe (the extra machinery isn't worth it), but treat its high-γ predictions as a mild **over-estimate** — at γ=0.20 the true accuracy sits ~3–4 pp below the fidelity-corrected curve, and that gap is structural, not a budgeting error.

## Honest limitations

This is a negative result and is reported as one: H0 was pre-registered at 30% and the observed 2.5% is a clear falsification, not a near-miss to be spun. The `σ_v² = 1 − m²` variance proxy is a diagonal (per-feature) approximation that ignores cross-feature shot-noise covariance within a node; a full covariance-whitened SNR could in principle do better, but the persistent *bias* (not variance) in Panel C strongly suggests the ceiling is set by readout-geometry change, which no second-moment shot-noise model addresses. The off-curve bias is measured, but not yet *derived* — a mechanistic model of how depolarizing rotates/shrinks the achievable linear-readout direction (e.g. via the noisy feature Gram matrix) is the natural B8+ follow-up. Same two caveats as B6 persist: one noise model (global depolarizing) and two architectures. The reused accuracies inherit B6's 3-seed readout-training noise, which contributes part of the irreducible floor.

## Scale of evidence

350 held-out cells (2 architectures × 5 tasks × 5 nonzero γ × 7 budgets), four nested predictors on one shared accuracy dataset, per-node quantities computed for all 6 γ across both architectures, zero fitted parameters in any fidelity factor. Pre-registered threshold 30% MAE reduction; observed 2.5% ⇒ hypothesis falsified, B6's scalar factor confirmed near-optimal among effective-shot corrections.
