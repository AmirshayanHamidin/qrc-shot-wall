# The Shot Wall: How Measurement Noise Erases Quantum Reservoir Computing's Advantage

A small, fully reproducible benchmark study of **quantum reservoir computing (QRC)** under realistic measurement budgets — ending in a clean, quantified negative result and a redirected research question.

**TL;DR.** A 6-qubit quantum reservoir predicts a standard chaotic time-series benchmark (NARMA5) extremely well *if you could read its state perfectly* (NMSE 0.003). But quantum states are read by repeated sampling ("shots"), and at any realistic shot budget the sampling noise erases essentially **all** of the quantum features' added value — eight different mitigation strategies all plateau at the accuracy a classical linear model gets from the raw inputs alone, with no quantum device. Closing the gap by brute force needs ~10⁹ shots per timestep, 4–5 orders of magnitude beyond practice.

![The shot wall](figures/qrc_shot_wall.png)

## Start here

1. **New to this?** Read the two-page story: [`results/RESULTS.md`](results/RESULTS.md) (benchmark 1: QRC vs classical baselines, and why shot noise — not expressivity — is the bottleneck).
2. **Then the main result:** [`results/RESULTS_GAP.md`](results/RESULTS_GAP.md) (benchmark 2: eight gap-closing strategies, the plateau, and what it means).
3. **Then the twist:** [`results/RESULTS_TASKSHAPE.md`](results/RESULTS_TASKSHAPE.md) (benchmark 3: the wall is task-shaped — classification retains ~86% of the quantum benefit at budgets where regression retains ~4%).
4. **Want to run it?** See below — everything runs on a laptop CPU in under a minute. No quantum hardware or account needed.

## Quickstart

```bash
pip install -r requirements.txt
cd src
python qrc_benchmark.py          # benchmark 1: QRC vs tuned classical baselines  (~5 s)
python qrc_full_eval.py          # multi-seed eval + shot-noise study             (~20 s)
python qrc_gap_eval.py 40000     # benchmark 2: gap-closing strategies @ 40k shots (~6 s)
```

## What's in the box

| Path | Contents |
|---|---|
| `src/qrc_benchmark.py` | Core: 6-qubit gate-based reservoir (Qiskit unitary, reset-based input injection, Pauli-Z features, ridge readout), NARMA tasks, classical ESN + linear baselines |
| `src/qrc_full_eval.py` | Fair-comparison hardening: ESN hyperparameter grid, multi-seed error bars, finite-shot sampling |
| `src/qrc_gap_eval.py` | The gap study: PCA denoising, errors-in-variables ridge, shot reallocation across virtual nodes, sim-trained denoisers |
| `results/` | Write-ups and raw JSON numbers |
| `figures/` | Plots |

## The three findings

1. **Fair baselines matter.** QRC "beats" a classical echo state network by 14× — until you tune the ESN, after which they tie. 
2. **The shot wall.** With exact expectation values QRC is excellent; with realistic sampling, every readout-side fix (smoothing, lag stacking, PCA, noise-covariance-corrected regression, learned denoisers, shot reallocation) plateaus at the no-quantum classical baseline.
3. **The information is real but unreachable.** The reservoir's features are *not* classically redundant — neither a linear map nor an MLP can reproduce them from input history. The quantum advantage exists in the state and dies at the measurement interface.

## The redirected question

Post-processing can't fix this; the loss happens at measurement. The live question is **information-per-shot as a design criterion**: can reservoir dynamics and data encodings be designed so task-relevant signal concentrates in a few high-magnitude observables?

**Benchmark 3 answered the secondary question** (`src/qrc_design.py`, [`results/RESULTS_TASKSHAPE.md`](results/RESULTS_TASKSHAPE.md)): the wall is a property of output precision, not of the quantum device. On temporal parity — where a linear model on inputs is provably at chance — the same reservoir at the same 40k-shot budget keeps 93% accuracy (86% of its exact-readout benefit), crossing the tuned classical ESN near 12k shots/step. Shot noise destroys precision, not information class: coarse-output tasks sit below the wall.

## Latest: benchmarks 5–6 (a predictive law, and its hardware extension)

**Benchmark 5 — a parameter-free measurement-wall law** (`results/RESULTS_LAW.md`). Across 150 cells (5 tasks × 6 architectures × 5 shot budgets), a shot-noise-limited QRC classifier's accuracy is predicted *before any noisy run* from three noiseless quantities — readout direction, per-sample decision margins, and the exact multinomial shot-noise covariance projected onto the readout — at R² = 0.991, MAE 1.3 pp, with zero fitted parameters.

**Benchmark 6 — a device-fidelity factor** (`results/RESULTS_GATENOISE.md`). The law is extended from shot noise to *gate* noise. A global depolarizing channel contracts every decision margin by a noiselessly-computable factor `c(γ)`, so gate noise acts, to leading order, as a pure effective-shot reduction: rescaling the shot axis by `c(γ)²` collapses every gate-noisy accuracy curve back onto the noiseless one (420 cells, collapse R² = 0.927 vs 0.851 for ignoring gate noise, advantage growing with noise strength). A QRC practitioner can now estimate the hardware shot budget a classification task needs — accounting for both sampling and gate fidelity — before spending any quantum time. Honest residual: the collapse is ~3 pp, not exact, so gate noise is *approximately* but not perfectly "just fewer shots." ![Gate-noise collapse](figures/qrc_gate_noise.png)

## Benchmarks 7–9 (probing the law's limits: a negative result, a scope boundary, and a usability test)

**Benchmark 7 — per-node + covariance refinement of the gate-noise factor** (`results/RESULTS_PERNODE.md`, *honest negative*). B6's ~3 pp residual was hypothesized to come from (i) virtual nodes seeing different noisy depths and (ii) depolarizing changing the shot-noise covariance. A parameter-free correction fixing both was pre-registered to cut collapse MAE by >30%. **It cut it by 2.5%** (2.89 → 2.82 pp). The residual is not either suspected mechanism: gate noise moves the reservoir *off* the noiseless accuracy-vs-shots curve, a small shot-budget-irreducible negative bias that no rescaling of the shot axis can remove.

**Benchmark 8 — beyond depolarizing: is the scalar factor enough?** (`results/RESULTS_BEYONDNOISE.md`). B6's clean `S_eff = S·c²` collapse used global *depolarizing* noise — the most favourable case, where every readout feature is multiplied by the same scalar. Against three physically distinct channels the scalar factor falls short of its R²=0.927 depolarizing benchmark on all of them (dephasing 0.90, amplitude-damping/coherent worse), and none clears the pre-registered R²>0.9 bar. The mechanism separates cleanly: **coherent (unitary) errors *rotate* the readout direction** — information-preserving, largely recovered by a retrained readout, so the scalar factor has the wrong sign — while **non-unital amplitude damping (T₁) is the genuinely shot-irreducible case.** For hardware, relaxation matters more than coherent/calibration error under a fixed shot budget. ![Beyond depolarizing](figures/qrc_beyondnoise.png)

**Benchmark 9 — can the law be used at scale?** (`results/RESULTS_MARGINEST.md`). The law needs the design-time separation `D₀ = ‖μ₁−μ₀‖`, computed on the *noiseless* reservoir — impossible at unsimulable sizes, where it must be *estimated* from a pilot run. The obvious plug-in `‖μ̂₁−μ̂₀‖` is **optimistically biased** (shot noise inflates each class mean), worst exactly where it hurts: up to **+41%** on the hardest low-margin task at a 250-shot pilot, which would badly under-budget the shots needed to clear the wall. A parameter-free correction subtracting the pilot-estimated shot-noise variance removes the bias to ≤0.8% at every budget using only the same pilot data, recovering `D₀` to ~3% RMSE at 1,000 pilot shots (≈6% predicted-budget error). The margin-based budgeting recipe survives the transition from *computing* margins to *estimating* them — with a stated price and a named trap. ![Cheap margin estimation](figures/qrc_marginest.png)

**Benchmark 10 — the law scores a *fixed* readout; reachable accuracy needs retraining** (`results/RESULTS_RETRAIN.md`). The B5/B6 prediction takes the readout trained on *noiseless* features. That closed-form probit turns out to be an almost-exact model of that **fixed** design readout run on a noisy device (R²=0.948, MAE 0.74 pp; 0.14 pp on the gate-noisy cells) — but the fixed readout is not noise-robust: in the perfect-exact-separation regime it collapses a mean **24.5 pp** below the accuracy reachable by **retraining** the linear readout on the noisy features. **99.5%** of the law-vs-reachable residual is exactly this retraining gain (per-cell correlation −0.9997). So the measurement-wall law is really a *retrained*-readout law, and retraining on-device is load-bearing rather than a side effect. Honest caveat: this is the maximal-collapse regime (exact accuracy ≈ 1.00); an encoding-gain sweep is queued to map how the fixed/retrained gap closes as exact separation degrades. ![Retraining under noise](figures/qrc_retrain.png)

## Honest limitations

Single task family (NARMA), one reservoir topology, sampling noise only — real hardware adds gate errors, so the wall here is *optimistic*. Feature-count-matched (not wall-clock-matched) classical comparisons. Details and seeds in the write-ups.

---
*Amirshayan Hamidin, 2026. Built as a scoping study for an independent-study research project.*
