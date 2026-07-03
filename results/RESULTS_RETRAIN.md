# Benchmark 10: Readout retraining under noise — the law scores a fixed readout, reachable accuracy needs retraining

**Claim (calibrated):** the measurement-wall law's closed-form probit is an almost
exact model of a *fixed* noiseless-design readout run on a noisy device (R² = 0.948,
MAE 0.74 pp over 160 cells; 0.14 pp over the 120 gate-noisy cells) — but that fixed
readout is catastrophically non-robust, collapsing a mean **24.5 percentage points**
below the accuracy reachable by *retraining* the linear readout on the noisy features.
The gap between the fixed-readout law and reachable accuracy (mean 26.8 pp) is almost
entirely the retraining gain: **99.5 %** of it is explained by retraining, and the
per-cell retraining gain correlates with the "law-vs-reachable" residual at −0.9997.
Retraining is therefore load-bearing, not a side effect. Code: `src/qrc_retrain.py`,
`src/qrc_retrain_fig.py`; raw cells: `results/retrain_law.json`; figure:
`figures/qrc_retrain.png`.

## The pre-registered question

B5/B6 predict a QRC classifier's noisy accuracy from *noiseless* quantities: the
readout direction trained on exact features, the exact per-sample margins, and the
shot-noise covariance projected onto that direction. That is a **fixed noiseless-design
readout**. Yet every "reachable" accuracy in B3/B6/B8 was measured with the readout
**retrained on the noisy features** at each budget, and B6/B8 reported the law's ~2.9 pp
residual against *that* retrained accuracy. B7 attributed the residual to a
shot-irreducible off-curve bias. This benchmark isolates the competing explanation the
agenda flagged: **is the residual mostly a suboptimal-readout artifact — i.e. is it just
the retraining gain?**

**H0 (residual is a readout artifact):** retraining yields a systematic positive gain,
and the probit predicts the fixed-readout accuracy far better than it predicts reachable
accuracy — `MAE(law−fixed) ≤ 0.5·MAE(law−retrain)` — so the reported residual is
dominated by the retraining gain, not by intrinsic law error.

**H1 (falsification):** retraining gain ≈ 0 or non-systematic, or the residual survives
against the law's own fixed-readout target — i.e. it is intrinsic.

Setup: 2 architectures × 5 classification tasks × 4 gate-noise levels (γ = 0, 0.05,
0.10, 0.15) × 4 shot budgets (500–32,000) = 160 cells. Three accuracies per cell —
`acc_fixed` (readout fit on γ=0 exact features, scored on the gate-noisy shot-sampled
features), `acc_retrain` (readout refit on the noisy features), and `law_pred` (the
B5/B6 fixed-readout probit) — averaged over 3 sample seeds. Simulation only: numpy
density matrix + qiskit unitary, global depolarizing gate noise + multinomial shot
noise. No hardware, no credentials.

## Result: H0 confirmed, decisively, in this regime

The probit tracks the fixed readout tightly and non-trivially — `acc_fixed` spans
0.37–0.59 (std 0.069) and the prediction follows it at R² = 0.948, MAE 0.74 pp (0.14 pp
on the gate-noisy subset). It is not predicting a constant: the correlation between
prediction and measured fixed accuracy is 0.974. So the closed-form model is validated
*as a model of the fixed readout*.

But the fixed readout is non-robust. Trained on exact features that separate the classes
perfectly (exact accuracy ≈ 1.00), its decision margins live along directions that any
realistic sampling destroys; `acc_fixed` averages 0.46 and never resolves the task even
at 32,000 shots. Retraining the readout on the noisy features finds a different,
noise-robust direction and recovers reachable accuracy of 0.44–0.97 (mean 0.71),
consistent with the task-shaped wall of B3 (majority-3 mean 0.87, parity-4 mean 0.62).

| gate noise γ | mean retrain gain | MAE(law − fixed) | MAE(law − reachable) |
|---|---|---|---|
| 0.05 | 25.9 pp | 0.28 pp | 28.2 pp |
| 0.10 | 24.8 pp | 0.06 pp | 26.7 pp |
| 0.15 | 23.4 pp | 0.07 pp | 25.5 pp |
| 0 (shot only) | 23.9 pp | — | — |

`MAE(law−fixed)` = 0.14 pp is **190× smaller** than `MAE(law−reachable)` = 26.8 pp on
the noisy cells — far past the H0 bar of a 2× gap. The entire discrepancy between the
fixed-readout law and reachable accuracy is the retraining gain.

## What it means

1. **The measurement-wall law is a *retrained-readout* law.** Its small residual in
   B5/B6 holds only because "reachable" accuracy already retrains the readout. Fed the
   fixed noiseless-design readout it was literally derived from, the law predicts near-
   total collapse — and that prediction is correct (0.14 pp). The design-time readout and
   the reachable readout are different objects separated by ~25 pp; a QRC practitioner
   must retrain on device.

2. **This bounds B7's "intrinsic residual."** B7's off-curve bias is a property of the
   *retrained* curve; it is not what separates the law from reachable accuracy at the
   readout level. The dominant readout effect (25 pp) swamps the intrinsic residual
   (~3 pp), so in the perfect-separation regime the residual studied by B6/B7 is not the
   binding term — the readout choice is.

3. **Reporting standard implication (feeds B11).** Any margin-normalized budget must be
   computed from the *retrained* readout; margins from the exact-trained readout describe
   an unreachable, non-robust operating point.

## What this is not — honesty

This result lives in the **perfect-exact-separation regime**: arch 0/1 with strong
encoding classify the parity/majority tasks perfectly on exact features, so the
noiseless-trained readout is maximally overfit to noise-fragile directions and the
collapse is maximal. B5 reported R² = 0.991 for its law *against reachable accuracy*
across six architectures including weak-encoding ones; that is only consistent with the
present finding if B5's cells sat where fixed and retrained readouts nearly coincide
(imperfect exact separation, so the design readout is already noise-robust), **or** if
B5's law was in practice applied with the reachable readout. Either way, B10's
contribution is to make the dependence explicit and quantify it: the law's accuracy as a
*fixed*-readout model is excellent (0.14–0.74 pp), and the price of not retraining is
~25 pp in this regime. We did **not** test whether the gap shrinks smoothly as exact
separation degrades — the natural follow-up is a sweep of encoding gain from
perfect-separation down to the wall, mapping retraining gain vs exact-margin headroom.
Limitations otherwise inherited: two architectures, one global-depolarizing gate model,
classification only, classically simulable sizes.

## Scale of evidence

160 cells (2 arch × 5 tasks × 4 γ × 4 budgets), 3 sample seeds each; three accuracy
protocols per cell; the probit prediction uses zero fitted parameters (exact margins +
closed-form multinomial covariance along the fixed readout). Aggregate flags:
`frac_residual_explained_by_retraining = 0.995`, `corr_gain_vs_officialresidual =
−0.9997`, `H0_readout_artifact_supported = true`.
