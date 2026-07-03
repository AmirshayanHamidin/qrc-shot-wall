"""Hardware QRC v4: topology-native NISQ architecture.
Reservoir couplings match the device's linear chain exactly -> no SWAP routing.
K=4 injections, 3 readout nodes, 1-layer reservoir (seed 3), full-range encoding.

Run:  python3 qrc_hw4.py <tier> <shots> <T> <node> <start> <n>
Eval: python3 qrc_hw4.py eval <shots> <T> <tier>
"""
import sys, glob
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit_aer import AerSimulator
from qrc_hw import make_task, counts_to_features, GAIN, N_Q, evaluate

K, NODES, SEED_U = 4, 3, 3
CHAIN = [41, 40, 34, 21, 20, 19]   # linear chain on ibm_torino

def chain_reservoir(qc, rng):
    for q in range(N_Q):
        qc.rx(rng.uniform(0, 2*np.pi), q)
        qc.rz(rng.uniform(0, 2*np.pi), q)
    for q in range(0, N_Q-1, 2):
        qc.rzz(rng.uniform(0, np.pi), q, q+1)
    for q in range(1, N_Q-1, 2):
        qc.rzz(rng.uniform(0, np.pi), q, q+1)

def template(node):
    ths = [Parameter(f'th{i}') for i in range(K)]
    qc = QuantumCircuit(N_Q)
    for i in range(K):
        if i > 0:
            qc.reset(0)
        qc.ry(ths[i], 0)
        chain_reservoir(qc, np.random.default_rng(SEED_U))
    for _ in range(node):
        chain_reservoir(qc, np.random.default_rng(SEED_U))
    qc.measure_all()
    return qc, ths

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
            fl = sorted(glob.glob(f'hw4_{tier}_{shots}_n{node}_*.npy'),
                        key=lambda f: int(f.split('_')[-1][:-4]))
            Fs.append(np.vstack([np.load(f) for f in fl]))
        F = np.hstack(Fs)
        acc = evaluate(list(F), lab, start=K)
        print(f'HW4 tier={tier} shots={shots} features={F.shape} parity acc = {acc:.4f}')
    else:
        tier, shots, T, node, start, n = mode, int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
        u, lab = make_task(T)
        backend = get_backend(tier)
        tmpl, ths = template(node)
        layout = None if tier == 'ideal' else CHAIN
        tt = transpile(tmpl, backend, optimization_level=1, seed_transpiler=11, initial_layout=layout)
        idx = list(range(K, T))[start:start+n]
        circs = [tt.assign_parameters({ths[i]: 2*GAIN*u[t-K+1+i] for i in range(K)}) for t in idx]
        res = backend.run(circs, shots=shots).result()
        F = np.array([counts_to_features(res.get_counts(i), shots) for i in range(len(circs))])
        np.save(f'hw4_{tier}_{shots}_n{node}_{start}.npy', F)
        print(f'HW4 {tier} node{node} chunk {start}+{len(idx)} depth={tt.depth()} ok', flush=True)
