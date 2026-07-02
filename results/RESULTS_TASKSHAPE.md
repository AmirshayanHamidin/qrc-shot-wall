# Benchmark 3: The wall is task-shaped

Benchmarks 1–2 established that measurement (shot) noise erases the quantum reservoir's benefit on a regression task, and that no readout-side strategy recovers it. This benchmark asks the constructive question: **is the wall a property of the quantum device, or of the task's output precision?** Answer: the task. Code: `src/qrc_design.py` + the experiment blocks reproduced below; raw numbers in `results/task_shape.json`.

## The experiment

Same 6-qubit reservoir, full-range input encoding. Two tasks, same measurement budgets:

1. **Regression** (NARMA5, from benchmarks 1–2): output is a precise real number every step.
2. **Classification** (temporal parity-3): input is a random bit stream; the label is the XOR of the last three bits. A linear model on the raw inputs is *provably* at chance here — success requires exactly the nonlinear memory the reservoir provides. Readout is logistic regression (still linear), features standardized, regularization tuned identically for every method.

## Headline result — fraction of quantum benefit surviving measurement at 40k shots/step

| Task | Exact readout | Noisy readout | Benefit retained |
|---|---|---|---|
| Regression (NARMA5, NMSE) | 0.003 | 0.142 (vs 0.148 no-quantum) | **~4%** |
| Classification (parity, accuracy) | 1.00 | 0.93 ± 0.02 (vs 0.51 chance) | **~86%** |

Accuracy vs budget (mean of 3 noise seeds): 400 shots → 0.55, 1.2k → 0.59, 4k → 0.70, 12k → 0.80, 40k → 0.93, 120k → 0.99. The noisy quantum reservoir crosses the tuned classical ESN (0.77) near ~12k shots/step and effectively reaches its exact-readout ceiling by ~10⁵ — budgets that are routine on today's hardware. Contrast regression, where 4×10⁶ shots/step still sat far above the floor. See `figures/qrc_task_shape.png`.

## Why this happens

Shot noise is additive, zero-mean error on each feature. A regression readout passes that error straight to the output — precision is the product, and precision is what noise destroys. A classification readout only needs the noisy feature vector to stay on the correct side of a decision boundary; when the exact-feature classes are well separated, there is an error budget to spend, and 1/√S noise fits inside it at modest S.

## Honest boundaries of the claim

This is **not** a quantum-advantage result: parity-3 is a cubic polynomial in the input bits, and a classical logistic regression on degree-3 polynomial features solves it perfectly at trivial cost (we verified: 1.00). The claim is about the measurement interface, not supremacy: **for coarse-output tasks, the quantum reservoir's nonlinear memory survives realistic measurement budgets nearly intact; for precise-output tasks it does not.** Within the fixed-linear-readout reservoir paradigm, the noisy quantum reservoir does beat the tuned classical ESN (0.93 vs 0.77) at matched feature count.

Secondary design finding (`design_sweep_40000.json`): re-scaling the input encoding to use the qubit's full rotation range improves noisy-regime regression by ~15% (NMSE 0.157 → 0.130) at zero cost — the default injection used only 6% of the available dynamic range — but it also degrades exact-readout expressivity at the extreme, so it is a trade-off knob, not a free win.

## What would change if this holds up

Benchmark and application selection for near-term quantum ML should be filtered by output precision, not just task hardness: classification, anomaly detection, and decision tasks sit *below* the wall; trajectory regression and precise forecasting sit above it. That is a falsifiable, design-level guideline — and a much better place to look for genuine quantum value than post-processing.

## Caveats

One classification task (parity-3) and one reservoir; sampling noise only (no gate error); parity chosen precisely because linear baselines provably fail, which makes it a clean instrument but an easy classical target for nonlinear baselines. Next: harder classification tasks where classical polynomial expansion is not trivially available, and hardware validation.
