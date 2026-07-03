"""
Live QPU runner for the HW5 parity benchmark (real IBM hardware).

Prerequisites (do these yourself; never share your token with anyone):
  1. Create a free account at https://quantum.ibm.com and copy your API token.
  2. Save the token yourself into a file named  ibm_token.txt  next to this
     script (one line, nothing else). It is read locally and never printed.
  3. pip install qiskit qiskit-ibm-runtime

Usage:
  python3 run_qpu.py            # submits ~150 windowed circuits x 3 nodes
                                # in one batched job per node, 12k shots each

Notes:
  - Uses mid-circuit reset (dynamic circuits) - supported on IBM Heron/Eagle.
  - Total quantum time is a few minutes; the free open plan allows this,
    but queue wait can be hours. The script polls and saves results to
    hw5_qpu_*.npy, then prints parity accuracy.
  - The transpiler picks the least-busy backend and the lowest-error
    6-qubit chain from that backend's live calibration data.
"""
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qrc_hw import make_task, GAIN, N_Q, evaluate
from qrc_hw4 import template
from qrc_hw5 import counts_to_p, p_to_feats, mitigation_matrix, correct, K, NODES

SHOTS, T = 12000, 150

def best_chain(backend):
    tgt = backend.target
    cz = {}
    for pair in backend.coupling_map:
        a, b = tuple(pair)
        for g in ('cz', 'ecr', 'cx'):
            if tgt.instruction_supported(g, (a, b)):
                p = tgt[g].get((a, b))
                if p and p.error:
                    cz[(a, b)] = p.error
                break
    ro = {q: (tgt['measure'].get((q,)).error or 0.02) for q in range(backend.num_qubits)}
    adj = {}
    for (a, b), e in cz.items():
        adj.setdefault(a, []).append((b, e)); adj.setdefault(b, []).append((a, e))
    best = [1e9, None]
    def dfs(path, cost):
        if len(path) == 6:
            tot = cost + sum(ro[q] for q in path)
            if tot < best[0]: best[0], best[1] = tot, list(path)
            return
        for nxt, e in adj.get(path[-1], []):
            if nxt not in path: path.append(nxt); dfs(path, cost + e); path.pop()
    for s in adj: dfs([s], 0.0)
    return best[1]

def main():
    token = open('ibm_token.txt').read().strip()
    service = QiskitRuntimeService(channel='ibm_quantum_platform', token=token)
    backend = service.least_busy(operational=True, simulator=False, min_num_qubits=20)
    chain = best_chain(backend)
    print(f'backend: {backend.name}, chain: {chain}')

    u, lab = make_task(T)
    sampler = SamplerV2(mode=backend)
    Fs = []
    for node in range(NODES):
        tmpl, ths = template(node)
        tt = transpile(tmpl, backend, optimization_level=1, initial_layout=chain,
                       seed_transpiler=11)
        c0 = QuantumCircuit(N_Q); c0.measure_all()
        c1 = QuantumCircuit(N_Q); c1.x(range(N_Q)); c1.measure_all()
        circs = [transpile(c0, backend, initial_layout=chain),
                 transpile(c1, backend, initial_layout=chain)] + \
                [tt.assign_parameters({ths[i]: 2 * GAIN * u[t - K + 1 + i] for i in range(K)})
                 for t in range(K, T)]
        print(f'node {node}: submitting {len(circs)} circuits...')
        job = sampler.run(circs, shots=SHOTS)
        res = job.result()
        def cts(i):
            return res[i].data.meas.get_counts()
        Minv = mitigation_matrix(counts_to_p(cts(0), SHOTS), counts_to_p(cts(1), SHOTS))
        F = [p_to_feats(correct(counts_to_p(cts(i), SHOTS), Minv))
             for i in range(2, len(circs))]
        F = np.array(F)
        np.save(f'hw5_qpu_{SHOTS}_n{node}_0.npy', F)
        Fs.append(F)
        print(f'node {node} done.')
    acc = evaluate(list(np.hstack(Fs)), lab, start=K)
    print(f'\nREAL-HARDWARE parity accuracy on {backend.name}: {acc:.4f}')
    print('(ideal reference 0.886, device-model reference 0.864, chance 0.50)')

if __name__ == '__main__':
    main()
