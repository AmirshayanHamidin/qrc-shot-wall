# B8 — Beyond depolarizing: is the scalar device-fidelity factor enough?

**Status:** complete (2026-07-03). **Simulation only** (numpy density matrix +
qiskit unitary; gate + shot noise). No hardware, no external services.

## Question
B6 extended the shot-noise "measurement-wall law" with a single design-time
**scalar** device-fidelity factor
`c(η) = ||μ₁(η) − μ₀(η)|| / ||μ₁(0) − μ₀(0)||` (ratio of noiseless between-class
mean-feature separations), predicting `acc(η, S) = acc(0, S·c(η)²)` — gate noise
is exactly equivalent to fewer effective shots. That was confirmed for **global
depolarizing** noise (collapse R² = 0.927), the single *most favourable* case: a
depolarizing channel multiplies every Z_i / Z_iZ_j readout feature by the same
scalar, so a scalar factor is nearly exact by construction. B7 then showed the
depolarizing residual is a small shot-irreducible negative bias — gate noise
nudges the reservoir *off* its noiseless curve.

**B8 asks the honest generalization question:** do physically different gate
errors still contract the readout *multiplicatively*, or do they **rotate / shift**
the readout direction so a scalar factor is no longer enough?

## Method
Same arch (the 6-qubit hw design, arch 0), same 5 classification tasks
(parity2/3/4, delay_xor, majority3), same achievable-accuracy protocol as B3/B6
(logistic readout C=1 **retrained** on the noisy features at each budget, mean
over 3 sample seeds). Budgets S ∈ {500, 2000, 8000, 32000}. Three channels
applied per unitary step, strength η ∈ {0, 0.02, 0.05, 0.10, 0.15}:

| channel | physics | prediction |
|---|---|---|
| **coherent** | fixed random per-qubit over-rotation Rx(aᵢη)Rz(bᵢη). **Unitary** — rotates, doesn't shrink purity. | rotates the separation *direction* → scalar c(η) can't capture it |
| **amp_damping** | per-qubit amplitude damping toward \|0⟩ (λ=η). **Non-unital** — biases populations. | contracts *and* shifts the mean → scalar factor mis-predicts |
| **dephasing** | per-qubit phase damping (λ=η). **Unital but anisotropic** in Pauli space. | closest to depolarizing → collapse still works |

**Collapse test** (as B6): predict `acc(η,S)` from the η=0 accuracy-vs-log(S)
curve evaluated at `S·c(η)²`; compare to the naive no-factor baseline (evaluate
at raw S). **Direction diagnostic:** `cos(η) = ⟨Δμ(η),Δμ(0)⟩/(‖·‖‖·‖)` per task —
a pure scalar contraction keeps cos=1; a rotation drops it.

**Pre-registered H0:** the scalar collapse works ≈ as well as for depolarizing
(R² > 0.9 and a large MAE reduction vs the naive baseline) for **all three**
channels. **H1 (falsification):** for non-scalar channels (esp. coherent) the
collapse is materially worse — the factor is depolarizing-specific.

## Result — H0 is FALSIFIED (honest negative), channel-dependently

300 predicted cells (100 per channel). Depolarizing (B6) reference R² = 0.927.

| channel | collapse R² | naive R² | MAE-reduction from factor | mean bias (obs−pred) | min cos(η) |
|---|---|---|---|---|---|
| dephasing   | **0.836** | 0.820 | +5.9 % | −0.009 | 0.976 |
| amp_damping | **0.660** | 0.493 | +15.4 % | **−0.029** | 0.671 |
| coherent    | **0.796** | 0.806 | **−1.5 %** | **+0.019** | 0.942 |

**Every channel falls short of the depolarizing R²=0.927, and none reaches the
R²>0.9 pre-registered bar.** The scalar factor is genuinely depolarizing-specific.
The three channels fail in three *mechanistically distinct* ways, and the
direction diagnostic (Fig. panel B) cleanly separates them:

1. **Coherent (unitary) — the factor is not just insufficient, it has the wrong
   sign.** The scalar factor gives **no improvement** over ignoring gate noise
   entirely (MAE reduction −1.5 %). Reason: a unitary error *rotates* the readout
   direction (cos drops to 0.94) but **destroys no information**, so the retrained
   linear readout recovers most of the lost margin. The achievable accuracy is
   therefore *higher* than the c(η)² penalty predicts (mean bias **+0.019**,
   positive). c(η) measures a shrinking ‖Δμ‖ and over-penalizes; the honest answer
   is that coherent gate errors barely cost a *retrained* QRC classifier anything.

2. **Amplitude damping (non-unital) — the factor helps but leaves a large,
   irreducible negative bias.** Here contraction is real and strong (c → 0.65),
   so applying the factor does cut MAE by 15 %. But damping *also* biases
   populations (Z_i → +1) and rotates the direction hardest of the three
   (cos → 0.67), moving the reservoir far off its noiseless curve: a −0.029 mean
   negative bias no shot budget removes. Collapse R²=0.66 ≪ 0.93. This is B7's
   off-curve bias, amplified — non-unital noise is the worst case for the law.

3. **Dephasing (unital) — closest to depolarizing, as predicted, but still short.**
   Direction is well preserved (cos ≥ 0.98), the factor helps modestly (+5.9 %),
   R²=0.836. Anisotropy in Pauli space (coherences killed, populations kept) is
   enough to pull it below the uniform-depolarizing benchmark.

**Answer to the agenda's question — "do coherent errors rotate the readout
direction?": YES.** Both coherent *and* amplitude-damping errors rotate it
(cos < 1, panel B), while dephasing does not. The scalar B6 factor only tracks the
*magnitude* ‖Δμ‖; it is blind to this rotation, which is exactly why it degrades.

## Interpretation / takeaways
- **The measurement-wall device-fidelity factor is a depolarizing-specific
  approximation.** It is near-exact only when the channel contracts all readout
  features uniformly and preserves the readout direction. Realistic error mixes
  (coherent + amplitude/phase damping) break both assumptions.
- **Direction, not just magnitude, is the missing coordinate.** A useful next
  correction would rescale + *re-align* the separation vector (a low-rank/rotation
  correction), not just scale it. B7 showed per-node scalar corrections don't help;
  B8 explains why — the residual lives in the *direction*, not the per-node gains.
- **Coherent errors are benign for a retrained QRC classifier** (they cost far
  less than c(η)² predicts), whereas **non-unital (amplitude-damping) errors are
  the genuinely damaging, shot-irreducible case.** For hardware QRC this argues
  that T1 (relaxation) matters more than calibration/coherent error for
  classification accuracy under a fixed shot budget.

## Honesty notes / limitations
- Single architecture (arch 0) and a single fixed coherent-error axis; the coherent
  result may depend on the specific rotation axes (though the *mechanism* —
  information-preserving rotation recovered by a retrained readout — is generic).
- η is a per-step channel strength, not directly a device error rate; magnitudes
  are qualitative. The *relative* ordering (depol > dephasing > coherent-R² but
  coherent factor useless; amp_damping worst) is the robust finding.
- All results simulation-only. No claim about any specific real device.

## Files
- `src/qrc_beyondnoise.py` — engine + three channels + collapse/direction analysis
- `src/qrc_beyondnoise_fig.py` — figure
- `results/beyond_noise_law.json` — full aggregate (300 cells + per-channel summary)
- `results/bn_coherent.json`, `results/bn_amp_damping.json`, `results/bn_dephasing.json` — raw per-channel cells
- `figures/qrc_beyondnoise.png` — 4-panel summary
