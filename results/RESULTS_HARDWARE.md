# Benchmark 4: Surviving a real device — same model, 0.50 → 0.86

Benchmarks 1–3 used sampling noise only. This benchmark adds the rest of a real machine: gate errors, readout errors, and decoherence, using IBM Torino's calibration data (Qiskit `FakeTorino` noise model, transpiled circuits, fixed qubit layouts). Task: temporal parity-3, the coarse-output task from benchmark 3. Code: `src/qrc_hw.py` (windowed reformulation), `src/qrc_hw4.py` / `src/qrc_hw5.py` (final architecture), `src/run_qpu.py` (live-QPU runner, token required). Raw numbers: `results/hardware_results.json`.

## Why the model had to be rebuilt first

The simulation reservoir carries quantum state across all timesteps, but hardware measurement destroys state. Fading memory fixes this: features at time t depend only on the last K inputs, so each timestep becomes one standalone circuit — K reset-and-inject cycles, then measure (the standard windowed formulation). A K=6 window with 3 extra readout circuits reproduced benchmark 3's behavior: **0.886 accuracy at 12k shots/circuit**, vs 1.00 with perfect readout.

## The result: an engineering ladder out of the noise floor

All rows: same task, same shot budget (3 × 12k per timestep), same 150-step dataset, logistic readout.

| Architecture | Transpiled depth | Parity accuracy |
|---|---|---|
| Generic reservoir, depth-3, ring coupling | ~1,500–2,300 | 0.500 (chance) |
| Shallow variant, still ring-coupled | 361–525 (SWAP routing) | 0.455 (chance) |
| **Topology-native**: couplings match the chain, no routing | 94–138 | 0.636 |
| + **calibration-aware qubit choice** + **readout mitigation** | 94–138 | **0.864** |
| Reference: shot noise only (no gate error) | — | 0.886 |
| Reference: perfect readout | — | 1.000 |

Three design moves carried all the recovery, and none changed the logical model:

1. **Match the topology.** The ring coupling looked harmless (one extra gate) but forced SWAP routing that tripled transpiled depth and doubled the active qubits. Restricting the reservoir to the device's native linear chain cut depth ~15× with zero loss of exact-readout accuracy (still 1.00).
2. **Choose qubits by calibration.** The first chain we picked had an accumulated error score of 2.65 (it contained effectively dead qubits); the best chain on the same device scored 0.11. Same circuit, different qubits: 0.64 → mid-0.8s.
3. **Mitigate readout.** Two calibration circuits per job (all-zeros, all-ones prep) give per-qubit confusion matrices; applying the tensored inverse to measured distributions recovers the remaining gap to 0.864.

Final architecture: 4-input window, 1-layer chain-coupled reservoir, 3 readout nodes, full-range encoding, mid-circuit resets — 63 features, transpiled depth under 140 on ibm_torino's best 6-qubit path.

## What this adds to the shot-wall story

Benchmark 3 showed coarse-output tasks survive *measurement* noise. This benchmark shows they can also survive *device* noise — but only if the reservoir is co-designed with the machine: its topology, its calibration data, and its readout errors. A device-agnostic design at the same logical size produced exactly chance. The design principle from benchmark 3 (information-per-shot) generalizes to information-per-shot-*on-this-device*.

## Live QPU run: ibm_marrakesh

The identical experiment executed on **real hardware** (IBM Heron, 156 qubits, `ibm_marrakesh`, 2026-07-03): 2 readout nodes × 148 circuits × 6,000 shots on the live-calibration-selected chain [14, 15, 19, 35, 34, 33], with mid-circuit resets and per-job readout mitigation. Total quantum time: 484 seconds, inside the free Open Plan budget.

**Result: 0.8864 parity accuracy (39/44)** — matching the noiseless-simulation ceiling at this shot budget (0.886) and *above* the FakeTorino device-model prediction (0.864). The topology-native design left so little room for gate error that the real device performed at the shot-noise limit. Raw numbers: `results/qpu_final.json`; runner scripts: `src/qpu_submit.py`-style flow in `src/run_qpu.py`.

## Honest boundaries

Parity remains classically easy (poly-3 solves it); the claim is about what survives the hardware interface, not quantum advantage. Single device, single task, 44-point test set (above chance at p < 10⁻⁶); the live run used 2 of 3 readout nodes to stay inside the free quantum-time budget. Error rates drift between calibration snapshots, so exact numbers will vary run to run.
