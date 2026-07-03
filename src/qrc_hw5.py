"""Hardware QRC v5: topology-native + calibration-aware chain + readout mitigation.
Run:  python3 qrc_hw5.py <tier> <shots> <T> <node> <start> <n>
Eval: python3 qrc_hw5.py eval <shots> <T> <tier>
"""
import sys, glob
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qrc_hw import make_task, GAIN, N_Q, evaluate
from qrc_hw4 import template  # K=4, 3 nodes, chain reservoir seed 3

K, NODES = 4, 3
CHAIN = [8, 17, 27, 28, 29, 36]   # lowest-calibration-error path on ibm_torino

bits_idx = ((np.arange(64)[:, None] >> np.arange(6)[None, :]) & 1)
ZD = [1 - 2*bits_idx[:, i].astype(float) for i in range(6)] + \
     [(1-2*bits_idx[:, i])*(1-2*bits_idx[:, j]) for i, j in combinations(range(6), 2)]

def counts_to_p(counts, shots):
    p = np.zeros(64)
    for bstr, c in counts.items():
        p[int(bstr.replace(' ', ''), 2)] = c / shots
    return p  # index bit order: qiskit bitstring b5..b0 -> int; bit q = (idx >> q) & 1 after reverse

def p_to_feats(p):
    # careful: int(bstr,2) makes qubit0 the LSB since bstr is little-endian reversed:
    # qiskit counts keys are c5c4c3c2c1c0; int() -> qubit0 = LSB. bits_idx uses >> q, consistent.
    return np.array([p @ z for z in ZD])

def mitigation_matrix(p0, p1):
    """Tensored inverse from two calibration distributions (all-0 prep, all-1 prep)."""
    Minv = None
    for q in range(6):
        m0 = (bits_idx[:, q] == 0)
        e0 = p0[m0].sum()          # P(read qubit q = 0 | prepared 0)
        e1 = 1 - p1[m0].sum()      # P(read 1 | prepared 1)
        M = np.array([[e0, 1-e1], [1-e0, e1]])
        Mi = np.linalg.inv(M)
        Minv = Mi if Minv is None else np.kron(Mi, Minv)
    return Minv

def correct(p, Minv):
    q = Minv @ p
    q = np.clip(q, 0, None)
    return q / q.sum()

def get_backend(tier):
    if tier == 'ideal':
        return AerSimulator()
    from qiskit_ibm_runtime.fake_provider import FakeTorino
    return AerSimulator.from_backend(FakeTorino())

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'eval':
        shots, T, tier = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        u, lab = make_task(T)
        Fs = []
        for node in range(NODES):
            fl = sorted(glob.glob(f'hw5_{tier}_{shots}_n{node}_*.npy'),
                        key=lambda f: int(f.split('_')[-1][:-4]))
            Fs.append(np.vstack([np.load(f) for f in fl]))
        F = np.hstack(Fs)
        acc = evaluate(list(F), lab, start=K)
        print(f'HW5 tier={tier} shots={shots} features={F.shape} parity acc = {acc:.4f}')
    else:
        tier, shots, T, node, start, n = mode, int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        u, lab = make_task(T)
        backend = get_backend(tier)
        tmpl, ths = template(node)
        layout = None if tier == 'ideal' else CHAIN
        tt = transpile(tmpl, backend, optimization_level=1, seed_transpiler=11, initial_layout=layout)
        # calibration circuits on the same qubits
        c0 = QuantumCircuit(N_Q); c0.measure_all()
        c1 = QuantumCircuit(N_Q); c1.x(range(N_Q)); c1.measure_all()
        tc0 = transpile(c0, backend, initial_layout=layout)
        tc1 = transpile(c1, backend, initial_layout=layout)
        idx = list(range(K, T))[start:start+n]
        circs = [tc0, tc1] + [tt.assign_parameters({ths[i]: 2*GAIN*u[t-K+1+i] for i in range(K)}) for t in idx]
        res = backend.run(circs, shots=shots).result()
        p0 = counts_to_p(res.get_counts(0), shots)
        p1 = counts_to_p(res.get_counts(1), shots)
        Minv = mitigation_matrix(p0, p1)
        F = []
        for i in range(2, len(circs)):
            p = counts_to_p(res.get_counts(i), shots)
            F.append(p_to_feats(correct(p, Minv)))
        np.save(f'hw5_{tier}_{shots}_n{node}_{start}.npy', np.array(F))
        print(f'HW5 {tier} node{node} chunk {start}+{len(idx)} depth={tt.depth()} ok', flush=True)
