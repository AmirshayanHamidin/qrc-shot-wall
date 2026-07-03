# B12 — Reservoir topology sweep: is "information-per-shot" a designable knob?

**Status:** complete (2026-07-03). **Simulation only** (numpy density matrix + qiskit
unitary; sampling noise). No hardware, no runtime service.
Code: `src/qrc_topology.py`, `src/qrc_topology_fig.py`. Raw: `results/topology_law.json`
(200 cells). Figure: `figures/qrc_topology.png`.

## Why this benchmark

Every prior result (B1–B11) used **one** coupling graph — a nearest-neighbour brickwork
chain. The README's *redirected question* asks whether reservoir dynamics can be **designed**
so that task-relevant signal is cheaper to read: "can reservoir dynamics and data encodings
be designed so task-relevant signal concentrates in a few high-magnitude observables?" B12
takes the first structural swing at it by sweeping the **coupling topology** while holding
everything else fixed.

## Design

Six-qubit reservoir, 3 virtual nodes, `K=4` input window, `gain=1.0`, reset-injection and
Z/ZZ features exactly as `qrc_law.py`. Only the two-qubit coupling **graph** changes:

| topology | RZZ edges | wiring |
|---|---|---|
| `chain` | 5 | nearest-neighbour line (the program's default) |
| `ring` | 6 | line + wrap-around |
| `star` | 5 | every qubit coupled to a single hub (qubit 0) |
| `all2all` | 15 | every pair coupled |

× depth (1, 2 layers) = **8 reservoirs**, each scored on the 5 classification tasks
(parity-2/3/4, delay-XOR, majority-3) at budgets S ∈ {250, 1k, 4k, 16k, 64k}, mean over 3
sampling seeds → **40 (topology×layer×task) configurations, 200 cells.**

Two **design-time, noiseless** quantities per configuration:

- **IPS** `= Σᵢ Δμᵢ²/σᵢ²` — the class-discrimination SNR² gained **per shot** (the additive-SNR
  quantity from B7: `Δμ` = between-class mean feature separation, `σᵢ² = mean_t(1 − f_{t,i}²)`
  the mean single-shot variance of each ±1 observable). This is the law-relevant
  *information-per-shot*.
- **PR** `= (Σ Δμᵢ²)² / Σ Δμᵢ⁴` — participation ratio of the separation vector: how many
  observables carry the signal. **Low PR = concentrated in few high-magnitude observables**,
  the README's literal framing.

## Pre-registered hypotheses (stated before running)

> **H1 — topology is a real lever on information-per-shot.** At matched exact-readout
> accuracy (parity tasks separate perfectly → exact ≈ 1.00 for *every* topology), IPS varies
> ≥ 2× across topologies, and higher IPS predicts higher shot-limited accuracy at fixed
> budget (positive rank correlation).
> **H2 — concentration helps (the README's intuition).** Lower PR (signal in fewer
> observables) correlates with higher accuracy / higher IPS.
>
> **Falsifiers:** IPS topology-invariant or non-predictive → topology is not a design knob;
> PR uncorrelated with accuracy → "concentrate into few observables" is the wrong framing and
> total SNR²-per-shot, not concentration, is the lever. Either is reported honestly.

## Result

Exact-readout accuracy is **1.000 for all 40 configurations** — a clean matched-accuracy
setting, so every difference below is pure information-per-shot, not expressivity.

**H1 — confirmed, strongly.** Information-per-shot is genuinely designable: within a fixed
task, IPS spans **14× to 56×** across the 8 reservoirs (parity-3 0.003→0.183 = 56×;
majority-3 0.086→3.94 = 46×; delay-XOR 14×). And IPS predicts shot-limited accuracy across
all 40 reservoirs:

| budget S | Spearman ρ(log IPS, accuracy) | p |
|---|---|---|
| 250 | **+0.90** | 3.5×10⁻¹⁵ |
| 1 000 | +0.84 | 7.9×10⁻¹² |
| 4 000 | +0.57 | 1.1×10⁻⁴ |
| 16 000 | +0.48 | 1.6×10⁻³ |
| 64 000 | +0.37 | 1.8×10⁻² |

The correlation is strongest where the wall bites (low budgets) and fades as accuracy
saturates — exactly the law's prediction, now shown to hold across *structural* reservoir
changes and to be **controllable by design**.

**Topology ranking** (mean accuracy @ 250 shots, averaged over tasks and depths, with mean
IPS):

| topology | acc @ 250 | mean IPS |
|---|---|---|
| **star** | **0.924** | 0.63 |
| ring | 0.828 | 0.42 |
| all-to-all | 0.790 | 0.33 |
| chain | 0.789 | 0.46 |

The **star (hub-and-spoke) reservoir wins**, and it wins **through IPS, not connectivity**:
all-to-all has the *most* couplings yet the *lowest* IPS and worst-tied accuracy. Routing
every interaction through one hub apparently packs more between-class separation per unit
shot-noise variance than either a sparse line or a dense clique.

**H2 — falsified (honest negative).** Concentration is **not** the mechanism. The
participation ratio is uncorrelated with shot-limited accuracy at every budget
(ρ = −0.18 @250, p = 0.28; |ρ| < 0.1 at all larger budgets), and PR does not even track IPS
(ρ = −0.25, p = 0.12). Whether the separation is packed into 5 observables or spread across
25 makes no difference; what matters is the **summed** SNR²-per-shot `Σ Δμᵢ²/σᵢ²`. The
README's specific phrase "concentrate … in a few high-magnitude observables" points at the
wrong quantity — magnitude summed over *all* observables is the lever, not its concentration.

## Verdict

The redirected question gets a **qualified yes with a corrected mechanism**: information-
per-shot is a first-class, designable property of the reservoir — topology moves it by more
than an order of magnitude at fixed expressivity, and it predicts shot-limited accuracy with
ρ ≈ 0.9 in the wall regime. But the design target is **total SNR² per shot**, not the
*concentration* of signal into few observables (H2 falsified). Practical upshot for QRC
hardware design: prefer a **hub/star coupling** and maximise `Σ Δμ²/σ²` — a noiselessly
computable objective — rather than chasing either maximal connectivity or sparse high-
magnitude readouts.

## Honest limitations

- Parity/NARMA-family tasks all saturate to exact = 1.00, which is what makes the matched-
  accuracy comparison clean but also means this is the *maximal-headroom* regime; a follow-up
  should repeat the sweep on the razor-thin-margin Mackey-Glass family of B11, where exact
  separation is not perfect and IPS differences may reshuffle.
- Four topologies, two depths, one hub choice (qubit 0), 6 qubits, one injection scheme, 3
  seeds. IPS is a single scalar summary of a multi-feature logistic readout, so per-config
  scatter around the IPS trend is expected (and visible in panel A).
- "Design" here means selecting among fixed graphs, not optimising couplings — a gradient or
  search over `Σ Δμ²/σ²` is the natural next step.

## One-line takeaway

Information-per-shot is real and designable — topology changes it 14–56× and it predicts the
wall (ρ≈0.9) — but the knob is **total SNR² per shot** (favouring a star/hub reservoir), not
the concentration of signal into a few observables, which does nothing.
