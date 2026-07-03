# Benchmark 9: Can the measurement-wall law be used at scale? Cheap estimation of the design-time separation

**Claim (calibrated, and both pre-registered hypotheses CONFIRMED).** The measurement-wall law (B5) and its device-fidelity extension (B6) predict a QRC classifier's noisy accuracy from a single design-time quantity computed on the *noiseless* reservoir: the between-class separation `D₀ = ‖μ₁ − μ₀‖` of the exact expectation-value features. B5's own honesty section flagged the catch: at classically-unsimulable reservoir sizes `D₀` cannot be computed — it must be **estimated** from a pilot experiment on the device. B9 tests whether a *cheap* pilot suffices. It does, but only with a correction: the obvious plug-in estimator `D̂_naive = ‖μ̂₁ − μ̂₀‖` is **optimistically biased** — shot noise inflates each class-mean estimate, so hard tasks look more separable than they are — and the bias is severe exactly where it hurts (up to **+41%** on the hardest task at a 250-shot pilot). A parameter-free correction that subtracts the pilot-estimated shot-noise variance of the mean-difference removes the bias to **≤0.8%** at every budget, using only the same pilot data. Code: `src/qrc_marginest.py`, `src/qrc_marginest_fig.py`; raw output: `results/marginest_law.json`; figure: `figures/qrc_marginest.png`.

## Pre-stated hypotheses (stated before running)

To *use* the law on hardware you must estimate `D₀` from a pilot of `S_pilot` shots/timestep. Each class mean `μ̂_c` is then an average of finite-shot feature estimates, so `E[‖μ̂₁ − μ̂₀‖²] = ‖μ₁ − μ₀‖² + V`, where `V` is the summed shot-noise variance of the mean-difference. By Jensen this makes `D̂_naive` an **over-estimate** — and `V` grows relative to `D₀²` as the task gets harder (small `D₀`) or the pilot gets cheaper (small `S_pilot`).

> **H_bias:** `D̂_naive` is positively biased; the bias is worst for small-`D₀` tasks and small `S_pilot`.
> **H_fix:** the corrected estimator `D̂_corr² = max(D̂_naive² − V̂, 0)`, with `V̂` the multinomial shot-noise variance of the mean-difference **estimated from the same pilot counts**, is approximately unbiased, so a modest pilot recovers `D₀` to within a few percent.
> **Falsification:** even after correction the estimator's RMSE stays large at practical `S_pilot` → cheap estimation cannot rescue the law at scale.

## Method

Simulation only, reusing the B5 engine (`qrc_law.py`): the exact per-timestep measurement distributions `P`, the Z / ZZ observable set, and the same 5 classification tasks (parity-2/3/4, delay-XOR, majority-3) on 3 reservoir architectures (arch 0/1/2). For each of the 60 (arch × task × `S_pilot`) configurations, `S_pilot ∈ {250, 1000, 4000, 16000}`, we drew 40 independent pilot experiments. From each pilot we formed `D̂_naive` and two corrections: `corr_exact` (subtracting the exact shot-noise variance — an idealized upper bound on how well correction can work) and `corr_pilot` (subtracting a variance **estimated from the noisy pilot counts themselves**, `σ̂² = Σⱼ p̂ⱼqⱼ² − (Σⱼ p̂ⱼqⱼ)²` per node block — the only version usable at scale). We report relative bias `E[D̂]/D₀ − 1` and relative RMSE against the exact `D₀`.

## Results

Averaged over all 15 arch×task configs, as a function of pilot budget:

| `S_pilot` | naive bias | naive RMSE | corr_pilot bias | corr_pilot RMSE |
|---|---|---|---|---|
| 250 | **+6.1%** | 8.8% | +0.1% | 6.4% |
| 1,000 | +1.4% | 3.4% | −0.2% | 3.0% |
| 4,000 | +0.4% | 1.5% | −0.0% | 1.4% |
| 16,000 | +0.1% | 0.7% | −0.0% | 0.7% |

**H_bias — confirmed, and it concentrates on hard tasks.** The naive bias averages +6% at a 250-shot pilot but is a task-by-task phenomenon: it is negligible for easy majority-3 (`D₀ ≈ 1.08`, bias +0.1%) and explodes for the hardest parity tasks. At `S_pilot = 250`, parity-3 on arch 0 is inflated **+18%**; on arch 2, where `D₀` is only 0.052, the naive estimate is inflated **+41%**. A practitioner using the plug-in estimate would conclude a hard task is far more separable than it is, and therefore **under-budget** the shots needed to clear the wall — the most dangerous direction of error.

**H_fix — confirmed, with no idealization.** The pilot-only correction (`corr_pilot`) removes the bias to ≤0.8% on *every* config, including the +41% parity-3 case, and is statistically indistinguishable from the exact-variance correction (`corr_exact`): the variance term can be estimated from the same cheap pilot, so nothing beyond the pilot is required. Correction also slightly lowers RMSE at small budgets.

**The falsification test fails (the good outcome), with a caveat.** After correction, RMSE is 3.0% at a 1,000-shot pilot and 1.4% at 4,000 — small enough to be useful. But the residual RMSE is irreducible variance, not bias, and it is larger for the hardest tasks (parity-3 corrected RMSE ≈ 13% at `S_pilot = 250`). So "cheap" has a floor: for the very hardest tasks you need `S_pilot ≳ 1,000–4,000` for sub-5% error.

## What it means

1. **The law survives the transition from *computing* margins to *estimating* them** — the specific worry B5 raised as "the most interesting open question." A design-time pilot, not a full classical simulation, is enough to instantiate the measurement-wall / device-fidelity budget for a task, provided you use the bias-corrected estimator.
2. **The naive estimator is a trap.** The intuitive plug-in `‖μ̂₁ − μ̂₀‖` systematically over-states separability, worst for the hard, low-margin tasks where getting the shot budget right matters most. This is a concrete, quantified caution for anyone applying margin-based QRC budgeting on hardware.
3. **A cheap budgeting recipe with a stated price.** Because required shots for a target margin scale as `1/D₀²`, a relative error ε in `D̂` propagates to ≈ 2ε in the predicted shot budget. Corrected, a **~1,000-shot pilot buys < 6% budget error on an average task**; the hardest tasks want a few thousand. The pilot cost is a small, one-time fraction of the operating budget the law then prescribes.

## What this is not (honest limitations)

- **The reservoir is still classically simulated.** B9 tests the *estimator's* statistics — bias and variance of `D̂` from finite pilots — which are governed by the pilot's multinomial sampling and are size-independent in form; it does **not** run a genuinely unsimulable device. The claim is that the estimation *procedure* is sound and cheap, not that we executed it at scale.
- **`D₀`-only.** The full B5 predictor also uses per-sample margins and the projected shot-noise covariance; B9 isolates the between-class separation `D₀`, the dominant design-time quantity. Estimating the full per-sample margin distribution cheaply is a natural follow-on (some of the same bias-correction logic applies per sample, where it is noisier).
- **Fixed noiseless readout direction**, as in B5/B6 (the pilot estimates means along a fixed observable basis, not a re-optimized readout). Carried over: one task family, one topology family, simulation only (numpy + qiskit unitary), no hardware, no external services.

## Scale of evidence

60 configurations (3 architectures × 5 classification tasks × 4 pilot budgets), 40 independent pilot experiments each (2,400 pilot draws), pilot budgets 250–16,000 shots/timestep, exact `D₀` ranging 0.05–1.44. Two correction variants (exact-variance idealization and pilot-only realizable) computed for every draw; all reported biases and RMSEs are relative to the exact simulated `D₀`, zero fitted parameters.
