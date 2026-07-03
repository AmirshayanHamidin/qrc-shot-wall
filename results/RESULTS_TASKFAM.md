# Benchmark 11: A second, independent task family — external validity of the wall and the law

**Question.** Every prior benchmark (B1–B10) drives the reservoir with a single binary
bit stream (`u ∈ {0.05, 0.15}`) and targets NARMA-style regression or parity/majority
classification. A "measurement wall" and a parameter-free law fitted *inside one task
family* could be an artifact of that family. B11 replaces the family wholesale and
re-tests, changing nothing else in the pipeline.

**New family.**
- **Input:** a continuous, chaotic **Mackey-Glass** series (β=0.2, γ=0.1, p=10, τ=17),
  normalised into the encoder's monotone angle range `[0.02, 0.18]` (341 distinct input
  levels vs the old 2). A different input *distribution* and a standard reservoir-computing
  signal, unrelated to i.i.d. bits.
- **Classification (non-parity, nonlinear, memory-dependent, all balanced ~50/50):**
  `updown` (u_t > u_{t−2}), `accel` (sign of the discrete curvature u_t−2u_{t−1}+u_{t−2}),
  `prodmed` (median-split of the lag-2 product (u_t−ū)(u_{t−2}−ū)).
- **Regression:** `mg1` — one-step-ahead prediction of the chaotic series (u_{t+1}).

Grid: 4 architectures × 4 tasks × 5 shot budgets (250–64 000) × 3 sample seeds → **60
classification cells + 20 regression cells.** Simulation only, shot noise only (γ=0).
Code: `src/qrc_taskfam.py`, `src/qrc_taskfam_fig.py`. Raw cells: `results/taskfam_law.json`.
Figure: `figures/qrc_taskfam.png`.

## Pre-registered hypotheses and verdicts

| | Hypothesis (stated before running) | Pre-set bar | Verdict |
|---|---|---|---|
| **H1** | The wall generalises: retained quantum benefit collapses toward the classical (inputs-only) floor at low shots on the new classification family. | retention → 0 at low S | **Confirmed (stronger than expected).** |
| **H2** | The B5/B6 parameter-free probit predictor, *identical code, no refit, zero free parameters*, predicts shot-limited fixed-readout accuracy on the new tasks to B5-class error. | R² > 0.90 **and** MAE < 3.0 pp | **Split: MAE passes (2.24 pp), R² fails (0.79).** |
| **H3** | Task-shape generalises (B3): Mackey-Glass regression shows the same low shot-noise retention as NARMA. | retained < 0.15 @ 250 shots | **Confirmed.** |

## H1 — the wall is not a parity artifact (and is more severe here)

The noiseless reservoir separates all three new classification tasks almost perfectly
(exact accuracy 0.94–0.98 vs classical floors 0.54–0.68). But that separation lives in
**razor-thin, high-order feature margins.** Under shot noise the fixed design-time readout
collapses to near chance and **stays there across the entire practical budget** — fixed-
readout accuracy averages 0.49 at 250 shots and only 0.56 at 64 000 shots, *below* the
inputs-only classical floor (0.62). So on this family the quantum-featured readout is, at
realistic shot counts, worse than throwing the reservoir away and regressing on the raw
input. The wall reproduces; if anything it is harsher than for parity, because continuous-
input tasks carry more instantaneous linear signal (raising the floor) while their
learnable quantum structure sits at smaller margins.

## H2 — the law's calibration generalises; the R² bar fails for a benign reason

The parameter-free probit (per-sample noiseless margins projected through the exact
multinomial shot covariance) predicts the observed fixed-readout accuracy with **MAE = 2.24
percentage points and near-zero bias (+0.6 pp)** — squarely B5-class (B5 MAE was 1.33 pp).
It correctly forecasts *both* the near-chance collapse of most cells *and* the single
exception (architecture 4 partially recovers to ≈0.75 at 64 000 shots; the law predicts
≈0.71). Cell by cell, the law works.

The pre-registered **R² > 0.90 bar nonetheless fails (R² = 0.79)** — and this is the honest,
informative part. R² is variance-explained, and on this family the observed accuracies
cluster tightly near chance (range 0.434–0.770, std 0.063) versus the parity family's wide
spread (0.427–1.000, std 0.198, the same metric giving R² = 0.991). With ~3× less signal
variance, the same small absolute error consumes far more of it. Decomposed by task, the
two tasks that retain real dynamic range confirm the law (`updown` R²=0.87, `prodmed`
R²=0.89, both MAE ~1.9 pp); the near-unlearnable `accel` (exact only 0.94, observed range
0.434–0.583) has essentially no signal variance for R² to explain and drags the pooled
number down (R²=0.14 at MAE 2.8 pp). **Conclusion:** external validity holds in the sense
that matters for a design tool — the law's *predicted number is right to ~2 pp on an
unseen task family* — but "R² of a universal collapse" is not a portable pass/fail target
when a family's tasks live in a narrow accuracy band. We report the failed bar rather than
moving it.

## H3 — the task-shaped wall generalises

Mackey-Glass regression retention rises monotonically with budget (−1.06, −0.02, 0.57,
0.78, 0.86 at 250 → 64 000 shots). At 250 shots it is **negative** — the shot-noisy
reservoir predicts the chaotic series *worse than the raw input alone*, exactly B3's point
that regression exposes the full shot-noise variance in its output. Same signature as
NARMA, new family.

## Corroboration of B10 on an independent family

B11 was designed to test the law, but it independently reproduces B10's central finding.
Retraining the readout on the noisy features recovers most of the loss the fixed readout
suffers: at 64 000 shots fixed-readout accuracy averages 0.56 while **retrained** accuracy
averages 0.86 (per-cell, e.g. arch 0 `updown`: fixed 0.52 → retrained 0.88). The wall the
law predicts is the *fixed design-time readout* wall (the law's native target); retraining
on-device claws much of it back. B11 thus lands squarely in the "perfect-exact-separation /
tiny-margin" regime B10 flagged as its own caveat — now confirmed on a second family, with
an even larger fixed-vs-retrained gap (~30–40 pp here vs ~24.5 pp in B10).

## What this is and is not

This is external-validity evidence: swapping the entire input distribution and target
functions, the wall and the task-shape law both reproduce, and the parameter-free predictor
stays calibrated to ~2 pp. It is **not** a clean R²>0.9 replication of the universal-collapse
figure — that bar fails on low-dynamic-range tasks, and we keep the failure on the record.
Limitations: 4 architectures, one chaotic input source, exact separations are high (small-
margin regime) so several tasks are near-chance under any realistic budget; a lower-encoding
sweep (queued as the B10 follow-up) would populate the mid-margin band where R² is a fairer
test of the collapse.
