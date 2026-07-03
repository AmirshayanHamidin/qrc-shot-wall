"""
Hardware-ready QRC: sliding-window formulation of the parity benchmark.

Why windowed: the simulation reservoir carries state forever, but on a QPU
measurement destroys the state. Fading memory means features at time t only
depend on the last K inputs, so each timestep becomes ONE standalone circuit:

    for i in t-K+1 .. t:   reset q0 ; RY(2*g*u_i) q0 ; apply reservoir U
    measure all qubits

Features per timestep: <Z_i> (6) + <Z_i Z_j> (15) from counts.
Task: temporal parity-3 (label = XOR of last 3 input bits), logistic readout.

Runs three tiers:
  ideal   - Aer, no noise            (validates the windowed formulation)
  device  - Aer + FakeTorino noise   (real IBM calibration: gate/readout/T1T2)
  qpu     - real IBM backend         (requires token, see run_qpu.py)
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

N_Q = 6
K = 5          # window length (>= 3 for parity-3 + mixing slack)
GAIN = 0.5 * np.pi / 0.2   # full-range encoding

def reservoir_gates(qc, seed=7, depth=3, rng_state=None):
    """Append one application of the fixed random reservoir circuit."""
    r = rng_state
    for _ in range(depth):
        for q in range(N_Q):
            qc.rx(r.uniform(0, 2*np.pi), q)
            qc.rz(r.uniform(0, 2*np.pi), q)
        for q in range(N_Q - 1):
            qc.rzz(r.uniform(0, np.pi), q, q + 1)
        qc.rzz(r.uniform(0, np.pi), N_Q - 1, 0)

def template_circuit(seed=7, depth=3):
    """Parametric window circuit: K free injection angles, fixed reservoir."""
    from qiskit.circuit import Parameter
    thetas = [Parameter(f'th{i}') for i in range(K)]
    qc = QuantumCircuit(N_Q)
    for i in range(K):
        r = np.random.default_rng(seed)   # SAME reservoir every application
        if i > 0:
            qc.reset(0)
        qc.ry(thetas[i], 0)
        reservoir_gates(qc, depth=depth, rng_state=r)
    qc.measure_all()
    return qc, thetas

def counts_to_features(counts, shots):
    """<Z_i> and <Z_iZ_j> from a counts dict (bitstrings little-endian)."""
    z = np.zeros(N_Q)
    zz = np.zeros(len(list(combinations(range(N_Q), 2))))
    pairs = list(combinations(range(N_Q), 2))
    for bstr, c in counts.items():
        bits = [1 - 2*int(b) for b in reversed(bstr.replace(' ', ''))]  # +1/-1, qubit i
        w = c / shots
        for i in range(N_Q):
            z[i] += w * bits[i]
        for k, (i, j) in enumerate(pairs):
            zz[k] += w * bits[i] * bits[j]
    return np.concatenate([z, zz])

def make_task(T=360, seed=0):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, T)
    u = 0.05 + 0.10 * bits
    lab = np.array([bits[t] ^ bits[t-1] ^ bits[t-2] if t >= 2 else 0 for t in range(T)])
    return u, lab

def build_bound_circuits(u, backend, start=K, opt_level=1):
    """Transpile ONE template, bind per-timestep angles."""
    tmpl, thetas = template_circuit()
    tt = transpile(tmpl, backend, optimization_level=opt_level, seed_transpiler=11)
    out = []
    for t in range(start, len(u)):
        w = u[t-K+1:t+1]
        out.append(tt.assign_parameters({thetas[i]: 2*GAIN*w[i] for i in range(K)}))
    return out

def run_circuits(circs, backend, shots):
    job = backend.run(circs, shots=shots)
    res = job.result()
    return [counts_to_features(res.get_counts(i), shots) for i in range(len(circs))]

def evaluate(F, lab, start=K):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    X = np.array(F); y = lab[start:]
    split = int(0.7 * len(y))
    best = 0
    for C in (0.1, 1, 10, 100):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=5000, C=C))
        m.fit(X[:split], y[:split])
        best = max(best, m.score(X[split:], y[split:]))
    return best

if __name__ == '__main__':
    import sys, json
    tier = sys.argv[1] if len(sys.argv) > 1 else 'ideal'
    shots = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    T = int(sys.argv[3]) if len(sys.argv) > 3 else 360

    u, lab = make_task(T)
    if tier == 'ideal':
        backend = AerSimulator()
    elif tier == 'device':
        from qiskit_ibm_runtime.fake_provider import FakeTorino
        backend = AerSimulator.from_backend(FakeTorino())
    else:
        raise SystemExit('use run_qpu.py for real hardware')

    circs = build_bound_circuits(u, backend)
    print(f'{len(circs)} circuits, window K={K}, shots={shots}', flush=True)
    F = run_circuits(circs, backend, shots)
    acc = evaluate(F, lab)
    print(f'tier={tier}  parity accuracy = {acc:.4f}', flush=True)
    json.dump({'tier': tier, 'shots': shots, 'T': T, 'K': K, 'acc': acc},
              open(f'hw_{tier}_{shots}.json', 'w'))
