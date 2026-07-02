"""
Design-for-measurement: can encoding/reservoir design move the shot wall?

Knobs at FIXED total budget B per timestep:
  gain  g : input injection angle theta = g * u  (u in [0, 0.2]).
            Baseline g = pi/2 uses only 18 deg of the 90 deg available.
            g = pi/(2*0.2) = 7.854 uses the full Bloch angle.
  depth d : entangling circuit depth (mixing strength)
  coup  c : rzz coupling angle scale (0..1 of the random draw)

Metric: NMSE on NARMA5 with mitigated readout (EMA + lags + input window),
noisy @ budget B, plus exact-feature NMSE (expressivity check).
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from qrc_benchmark import narma, window_features, DIM, N_QUBITS, N_FEAT_PER_NODE, Z_DIAGS
from qrc_gap_eval import lag, ema, eval_strategy, T

V = 4

def reservoir_U(depth=3, coup=1.0, seed=7):
    r = np.random.default_rng(seed)
    qc = QuantumCircuit(N_QUBITS)
    for _ in range(depth):
        for q in range(N_QUBITS):
            qc.rx(r.uniform(0, 2*np.pi), q)
            qc.rz(r.uniform(0, 2*np.pi), q)
        for q in range(N_QUBITS - 1):
            qc.rzz(coup * r.uniform(0, np.pi), q, q + 1)
        qc.rzz(coup * r.uniform(0, np.pi), N_QUBITS - 1, 0)
    return Operator(qc).data

def reset_q0(rho, u, gain):
    th = gain * u
    psi = np.array([np.cos(th), np.sin(th)])
    rho4 = rho.reshape(DIM//2, 2, DIM//2, 2)
    rho_rest = np.trace(rho4, axis1=1, axis2=3)
    return np.einsum('a,b,ij->iajb', psi, psi, rho_rest).reshape(DIM, DIM)

def feats(u_seq, U, gain, shots, noise_seed=1, exact=False):
    r = np.random.default_rng(noise_seed)
    rho = np.zeros((DIM, DIM), complex); rho[0, 0] = 1.0
    Ud = U.conj().T
    F = np.zeros((len(u_seq), V * N_FEAT_PER_NODE))
    for t, u in enumerate(u_seq):
        rho = reset_q0(rho, u, gain)
        for v in range(V):
            rho = U @ rho @ Ud
            p = np.real(np.diag(rho)).clip(0); p /= p.sum()
            ph = p if exact else r.multinomial(shots, p) / shots
            F[t, v*N_FEAT_PER_NODE:(v+1)*N_FEAT_PER_NODE] = [ph @ zd for zd in Z_DIAGS]
        rho /= np.real(np.trace(rho))
    return F

def score(u, y, Xin, U, gain, budget, noise_seed=1):
    Xn = feats(u, U, gain, budget // V, noise_seed)
    noisy = eval_strategy(np.hstack([lag(ema(Xn)), Xin]), y)
    return noisy

if __name__ == '__main__':
    import sys, json
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
    u, y = narma(5, T, seed=5)
    Xin = window_features(u, 10)
    base_gain = 0.5 * np.pi
    full_gain = 0.5 * np.pi / 0.2

    out = {}
    print(f'=== budget {budget} shots/timestep, NARMA5, mitigated readout ===', flush=True)
    print('ref: baseline design (g=pi/2,d=3,c=1) exact floor ~0.003 | classical-inputs 0.148', flush=True)
    for gain, gname in [(base_gain, 'g=base(0.09rad max)'), (2.5*base_gain, 'g=2.5x'),
                        (full_gain, 'g=full(pi/2 max)')]:
        for depth in (1, 3, 6):
            U = reservoir_U(depth=depth, coup=1.0, seed=7)
            n = score(u, y, Xin, U, gain, budget)
            Xe = feats(u, reservoir_U(depth=depth, seed=7), gain, 0, exact=True)
            e = eval_strategy(np.hstack([lag(Xe), Xin]), y)
            key = f'{gname} depth={depth}'
            out[key] = {'noisy': n, 'exact': e}
            print(f'{key:32s} noisy={n:.4f}  exact={e:.4f}', flush=True)
    json.dump(out, open(f'design_sweep_{budget}.json', 'w'), indent=2)
