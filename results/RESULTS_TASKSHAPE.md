# Benchmark 3: The wall is task-shaped

Benchmarks 1–2 established that measurement (shot) noise erases the quantum reservoir's benefit on a regression task, and that no readout-side strategy recovers it. This benchmark asks the constructive question: **is the wall a property of the quantum device, or of the task's output precision?** Answer: the task. Code: `src/qrc_design.py` (secondary design sweep; regenerates byte-identically). The headline curve and reference values in `results/task_shape.json` have no committed generator; a pre-registered reconstruction on committed code is `src/qrc_taskshape_gen.py` → `results/task_shape_recon.json` (see the provenance note below).

## The experiment

Same 6-qubit reservoir, full-range input encoding. Two tasks, same measurement budgets:

1. **Regression** (NARMA5, from benchmarks 1–2): output is a precise real number every step.
2. **Classification** (temporal parity-3): input is a random bit stream; the label is the XOR of the last three bits. A linear model on the raw inputs is *provably* at chance here — success requires exactly the nonlinear memory the reservoir provides. Readout is logistic regression (still linear), features standardized, regularization tuned identically for every method.

## Headline result — fraction of quantum benefit surviving measurement at 40k shots/step

| Task | Exact readout | Noisy readout | Benefit retained |
|---|---|---|---|
| Regression (NARMA5, NMSE) | 0.003 | 0.142 (vs 0.148 no-quantum) | **~4%** |
| Classification (parity, accuracy) | 1.00 | 0.93 ± 0.02 (vs 0.51 chance) | **~86%** |

*Conventions and provenance: the regression retention was stored as 4.1%, computed from the rounded 3-dp printed values; full-precision inputs give 4.54% — “~4%” holds either way. The classification row quotes the stored file of record; the 2026-08-02 pre-registered reconstruction on committed code gives 99.6% retention at 40k (see the provenance note below).*

Accuracy vs budget (mean of 3 noise seeds; stored file of record): 400 shots → 0.55, 1.2k → 0.59, 4k → 0.70, 12k → 0.80, 40k → 0.93, 120k → 0.99. The stored curve places the crossing of the tuned classical ESN reference (0.77) near ~12k shots/step; the 2026-08-02 pre-registered reconstruction did not reproduce this — on committed code the curve runs higher at every budget and a feature-matched tuned ESN solves parity-3 outright, so no crossing exists (see the provenance note below). The reservoir effectively reaches its exact-readout ceiling by ~10⁵ shots/step — budgets that are routine on today's hardware. Contrast regression, where 4×10⁶ shots/step still sat far above the floor. See `figures/qrc_task_shape.png`.

## Why this happens

Shot noise is additive, zero-mean error on each feature. A regression readout passes that error straight to the output — precision is the product, and precision is what noise destroys. A classification readout only needs the noisy feature vector to stay on the correct side of a decision boundary; when the exact-feature classes are well separated, there is an error budget to spend, and 1/√S noise fits inside it at modest S.

## Honest boundaries of the claim

This is **not** a quantum-advantage result: parity-3 is a cubic polynomial in the input bits, and a classical logistic regression on degree-3 polynomial features solves it perfectly at trivial cost (we verified: 1.00). The claim is about the measurement interface, not supremacy: **for coarse-output tasks, the quantum reservoir's nonlinear memory survives realistic measurement budgets nearly intact; for precise-output tasks it does not.** Within the fixed-linear-readout reservoir paradigm, the stored files of record show the noisy quantum reservoir beating the tuned classical ESN (0.93 vs 0.77) at matched feature count; the 2026-08-02 reconstruction did not reproduce the 0.77 reference (a feature-matched tuned ESN reaches 1.00 on committed code), so this comparison rests on the stored, provenance-incomplete reference (see the provenance note below).

Secondary design finding (`design_sweep_40000.json`): re-scaling the input encoding to use the qubit's full rotation range improves noisy-regime regression by ~15% (NMSE 0.157 → 0.133; the previously printed 0.130 matches the g = 2.5×, depth-1 cell, 0.1299, not a full-range cell) at zero cost — the default injection used only 20% of the available rotation range (θ_max = 0.314 rad = 18.0° of the 90° range; 9.5% of the sin² probability range) — but it also degrades exact-readout expressivity at the extreme, so it is a trade-off knob, not a free win. (In the sweep JSON, the key label `g=base(0.09rad max)` mislabels θ_max: the actual value is 0.314 rad; 0.09 most plausibly reflects the sin² probability fraction ≈ 0.095, not a radian.)

## What would change if this holds up

Benchmark and application selection for near-term quantum ML should be filtered by output precision, not just task hardness: classification, anomaly detection, and decision tasks sit *below* the wall; trajectory regression and precise forecasting sit above it. That is a falsifiable, design-level guideline — and a much better place to look for genuine quantum value than post-processing.

## Provenance note (2026-08-02)

`results/task_shape.json` and `figures/qrc_task_shape.png` — the sources of the accuracy curve, the four reference values (esn_tuned 0.767, poly3 1.00, linear 0.51, qrc_exact 1.00) and the ~86% retention figure — have no committed generator (first audit, `AUDITS.md` 2026-08-02); they remain the untouched files of record, carrying this annotation. A reconstruction with every free choice pinned before first run (`audits/PREREG_B3_GEN.md`; generator `src/qrc_taskshape_gen.py`; raw output `results/task_shape_recon.json`; figure `figures/qrc_task_shape_recon.png`) restored the retention headline on committed code — 99.6% of the exact-readout benefit retained at 40k shots/step, against the pre-set ≥ 80% bar — but did not reproduce the stored curve (five of six budgets outside the pre-set ±0.05 band, all high) or the stored ESN reference (a feature-matched tuned ESN reaches 1.00, not 0.767), so the ESN-crossing claim has no committed-code support. The most plausible explanation is a weaker input encoding in the lost original code (see `AUDITS.md`); testing that variant would require a new pre-registration and is deferred. The secondary design sweep `design_sweep_40000.json` is unaffected: it regenerates byte-identically from `src/qrc_design.py`.

## Caveats

One classification task (parity-3) and one reservoir; sampling noise only (no gate error); parity chosen precisely because linear baselines provably fail, which makes it a clean instrument but an easy classical target for nonlinear baselines. Next: harder classification tasks where classical polynomial expansion is not trivially available, and hardware validation.
