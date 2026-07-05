# Benchmark 5: A predictive law for the measurement wall

**Claim (restored headline, 2026-07-04):** the accuracy of a shot-noise-limited quantum
reservoir classifier is predictable *before any noisy run*, from three noiseless quantities:
the readout direction, the per-sample decision margins, and the exact multinomial shot-noise
covariance projected onto that direction. Across **150 benchmark cells** (5 tasks × 6
reservoir architectures × 5 shot budgets), the parameter-free prediction achieves
**R² = 0.939 (0.944 after correcting for observation sampling noise), MAE 3.3 pp, bias
−1.0 pp**, improving from R² = 0.86 at 250 shots to 0.96 at 64 000.

Code: `src/qrc_law.py` (reservoir grid), **`src/qrc_law_predict.py` (the canonical
prediction generator — pinned convention)**, `src/qrc_law_rerun.py` (8-seed observation
protocol). Raw cells with per-seed observations: `results/law_rerun.json`. Historical file
of record from the original run: `results/law_theory.json` (see provenance note below).
Figure: `figures/qrc_law.png` (original run; regenerate from `law_rerun.json`).

## Provenance note (read this first)

The original write-up claimed **R² = 0.991 / MAE 1.3 pp**. A full independent audit
(2026-07-04, `AUDITS.md`) found that headline **not reproducible** from the committed code:
the committed pipeline cannot generate a subset of the published observations at any
sampling seed (e.g. arch0/parity4/S=1000: published 0.5955 vs an eight-seed range of
0.728–0.825), the published agreement is tighter than its own 2-seed protocol's noise floor
at every budget, and no committed script produced the `pred` column. The law's *formula*
was verified real (a reconstruction matches published predictions to ~1.3 pp); what could
not be verified was the published precision.

**Restoration (this document's numbers):** the prediction generator is now committed
(`src/qrc_law_predict.py`) with the readout convention pinned in its docstring — raw-feature
logistic regression, C = 10⁴, trained on the 70% chronological split; this is the
convention the audit found to match the published predictions — and the observation grid
was re-run from committed code only, with **8 documented sampling seeds** per cell
(`src/qrc_law_rerun.py`, seeds 1–8, per-seed accuracies stored in `law_rerun.json` so the
noise floor is checkable by anyone). The old headline is retired; the numbers above are
the claim. `law_theory.json` is retained untouched as the historical file of record.

## The restored result

| shot budget | R² | MAE (pp) | bias (pp) |
|---|---|---|---|
| 250 | 0.855 | 3.87 | −2.74 |
| 1 000 | 0.897 | 3.85 | −2.37 |
| 4 000 | 0.946 | 3.20 | −1.08 |
| 16 000 | 0.950 | 3.10 | +0.46 |
| 64 000 | 0.962 | 2.63 | +0.85 |
| **all 150 cells** | **0.939** | **3.33** | **−0.98** |

The 8-seed observation noise floor is **0.91 pp** expected MAE (computable per cell from
the stored per-seed spread), so the ~3.3 pp residual is dominated by genuine law error,
not observation sampling: the law is slightly pessimistic at low budgets (−2.7 pp bias at
250 shots — the retrained readout claws back a little margin the fixed-readout probit
doesn't see; cf. B10) and slightly optimistic at high budgets (+0.85 pp at 64k). A
zero-parameter closed-form forecast at 3.3 pp across a 150-cell design grid remains a
strong, useful law — the original claim's *precision* was inflated, its substance was not.

## How we got here (including the failures)

We pre-stated a hypothesis: retained quantum benefit collapses onto a universal curve in
naive SNR (feature signal std × √shots). **It failed** — R² = 0.20 with systematic
task-dependent violations: easy tasks (majority vote) sat far above the curve, hard tasks
(parity-4) far below. The failure pattern pointed at the missing variable: what matters is
not how much features vary, but how far apart the *classes* sit along the readout
direction — the decision margin.

Refining once (margin × √shots, fitted curve) gave holdout R² = 0.80 on architectures never
used in fitting. The final step removed the fitted curve entirely: for each test sample,
the exact shot-noise variance along the readout direction is computable in closed form from
the stored measurement distribution (multinomial covariance,
σ² = Σ_nodes [Σ_j p_j q_j² − (p·q)²]/S with q = Zᵀw), giving a per-sample flip probability
Φ(−margin/σ). Predicted accuracy is just the average. No parameters, no fitting.

Then the third failure, of process rather than science: the originally published precision
did not survive its own audit (see provenance note). The lesson is recorded here
deliberately — undocumented seeds and an uncommitted generator script are how a true
R² ≈ 0.94 law gets published as an R² = 0.991 one.

## What it means

1. **The task-shaped wall (benchmark 3) is now explained, not just observed.** Regression
   exposes the full noise σ in its output; classification hides noise inside its margins.
   Retention is high exactly when margin × √S exceeds ~1 — a computable condition.
2. **A design tool:** simulate your reservoir noiselessly (cheap classically at design
   sizes), compute margins and projected noise, and read off the hardware shot budget your
   task needs — *before* spending quantum time. Applied retroactively, this law predicts
   our own live-QPU choice: at 6,000 shots the parity-3 margins put predicted accuracy at
   the shot-noise ceiling, which is what ibm_marrakesh delivered (0.886).
3. **A reporting standard candidate:** QRC papers could report margin-normalized shot
   budgets instead of raw shot counts, making claimed results comparable across tasks and
   devices.

## What this is not

Honesty section, as always. The statistical machinery (Gaussian projection of multinomial
noise, probit link, matched-filter margins) is classical and standard — no new statistics
were invented. The contribution is the validated *application* at ~3.3 pp precision across
a wide QRC design grid, and using it to explain and quantify the measurement wall.
Limitations: shot noise only (B6–B8 map the gate-noise extension and its limits); the
prediction scores a fixed linear readout while observations retrain per draw — B10 shows
this convention mismatch is small here but grows to ~25 pp in perfect-separation regimes;
classically simulable sizes (at scale, margins must be estimated — B9 gives the pilot-run
recipe and its bias trap); and the restored numbers inherit the audit's environment caveat
(current numpy/sklearn; marginal cells can shift a few tenths of a pp across library
versions, which is far below the 3.3 pp residual).

## Scale of evidence

150 classification cells re-run under the restored protocol (plus 30 regression cells from
the original run, not re-audited), 6 reservoir architectures (4–6 qubits, varying depth,
window, encoding gain, readout nodes), 5 task families, 5 shot budgets spanning 250–64,000,
**8 documented sampling seeds per cell with per-seed values published**, zero free
parameters at the final stage.
