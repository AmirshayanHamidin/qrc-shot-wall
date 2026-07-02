"""
Quantum Reservoir Computing benchmark on NARMA tasks.

Gate-based QRC (Fujii & Nakajima-style, adapted to circuits):
  - n-qubit reservoir, fixed random entangling unitary U built with Qiskit
  - input injection each timestep by resetting qubit 0 to
    |psi_u> = cos(theta)|0> + sin(theta)|1>, theta = (pi/2)*u_t
    (reset = dissipation -> fading memory / echo-state property)
  - density-matrix evolution in numpy (64x64 for 6 qubits)
  - features per step: <Z_i> (n) + <Z_i Z_j> (n choose 2), plus V virtual
    nodes (features sampled mid-evolution) -> richer readout
  - readout: ridge regression

Baselines:
  - linear regression on input window (memory-matched)
  - classical Echo State Network (same feature count as QRC)

Metric: NMSE = MSE / var(y) on held-out test segment.
"""
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from sklearn.linear_model import Ridge

rng = np.random.default_rng(42)

# ---------------- tasks ----------------
def narma(order, T, seed=0):
    r = np.random.default_rng(seed)
    u = r.uniform(0, 0.2, T)
    y = np.zeros(T)
    if order == 2:
        for t in range(1, T - 1):
            y[t + 1] = 0.4 * y[t] + 0.4 * y[t] * y[t - 1] + 0.6 * u[t] ** 3 + 0.1
    else:
        n = order
        for t in range(n - 1, T - 1):
            y[t + 1] = (0.3 * y[t]
                        + 0.05 * y[t] * np.sum(y[t - n + 1:t + 1])
                        + 1.5 * u[t] * u[t - n + 1] + 0.1)
    return u, y

# ---------------- quantum reservoir ----------------
N_QUBITS = 6
DIM = 2 ** N_QUBITS
V_NODES = 4          # virtual nodes: apply U in V sub-steps, read features each sub-step

def random_reservoir_unitary(n, depth=3, seed=7):
    """Fixed random Ising-like entangling circuit; returns np unitary."""
    r = np.random.default_rng(seed)
    qc = QuantumCircuit(n)
    for _ in range(depth):
        for q in range(n):
            qc.rx(r.uniform(0, 2 * np.pi), q)
            qc.rz(r.uniform(0, 2 * np.pi), q)
        for q in range(n - 1):
            qc.rzz(r.uniform(0, np.pi), q, q + 1)
        qc.rzz(r.uniform(0, np.pi), n - 1, 0)
    return Operator(qc).data

# Pauli-Z observables (diagonal -> cheap)
def z_diagonals(n):
    """Diagonals of Z_i and Z_i Z_j operators in computational basis."""
    bits = ((np.arange(2 ** n)[:, None] >> np.arange(n)[None, :]) & 1)  # (dim, n)
    z = 1 - 2 * bits  # +1/-1, qubit q = bit q (little-endian, matches qiskit)
    singles = [z[:, i].astype(float) for i in range(n)]
    pairs = [(z[:, i] * z[:, j]).astype(float) for i, j in combinations(range(n), 2)]
    return singles + pairs

Z_DIAGS = z_diagonals(N_QUBITS)
N_FEAT_PER_NODE = len(Z_DIAGS)  # 6 + 15 = 21

def reset_qubit0(rho, u):
    """Trace out qubit 0, replace with input-dependent pure state."""
    th = 0.5 * np.pi * u
    psi = np.array([np.cos(th), np.sin(th)])
    # qiskit little-endian: qubit 0 is least significant -> fastest-varying index
    rho4 = rho.reshape(DIM // 2, 2, DIM // 2, 2)      # (rest, q0, rest', q0')
    rho_rest = np.trace(rho4, axis1=1, axis2=3)        # trace over qubit 0
    out = np.einsum('a,b,ij->iajb', psi, psi, rho_rest).reshape(DIM, DIM)
    return out

def qrc_features(u_seq, U):
    """Run reservoir over input sequence, return feature matrix (T, V*21)."""
    # V-substep unitary: U_sub = principal V-th root approximated by using U each substep
    # (standard multiplexing: apply U once per substep, read after each)
    rho = np.zeros((DIM, DIM), complex)
    rho[0, 0] = 1.0
    T = len(u_seq)
    feats = np.zeros((T, V_NODES * N_FEAT_PER_NODE))
    Ud = U.conj().T
    for t in range(T):
        rho = reset_qubit0(rho, u_seq[t])
        for v in range(V_NODES):
            rho = U @ rho @ Ud
            d = np.real(np.diag(rho))
            feats[t, v * N_FEAT_PER_NODE:(v + 1) * N_FEAT_PER_NODE] = [
                float(d @ zd) for zd in Z_DIAGS]
        # renormalize to fight numerical drift
        rho /= np.real(np.trace(rho))
    return feats

# ---------------- classical baselines ----------------
def esn_features(u_seq, n_nodes, seed=3, rho_sr=0.9, leak=0.5):
    r = np.random.default_rng(seed)
    W = r.normal(size=(n_nodes, n_nodes))
    W *= rho_sr / max(abs(np.linalg.eigvals(W)))
    Win = r.uniform(-1, 1, n_nodes)
    x = np.zeros(n_nodes)
    T = len(u_seq)
    X = np.zeros((T, n_nodes))
    for t in range(T):
        x = (1 - leak) * x + leak * np.tanh(W @ x + Win * u_seq[t])
        X[t] = x
    return X

def window_features(u_seq, w):
    T = len(u_seq)
    X = np.zeros((T, w))
    for k in range(w):
        X[k:, k] = u_seq[:T - k]
    return X

# ---------------- evaluation ----------------
def evaluate(X, y, washout=100, train_frac=0.7, alpha=1e-6):
    T = len(y)
    idx = np.arange(washout, T)
    split = washout + int(train_frac * len(idx))
    Xtr, ytr = X[washout:split], y[washout:split]
    Xte, yte = X[split:], y[split:]
    model = Ridge(alpha=alpha).fit(Xtr, ytr)
    pred = model.predict(Xte)
    nmse = np.mean((pred - yte) ** 2) / np.var(yte)
    return nmse, pred, yte

def run(order, T=1200):
    u, y = narma(order, T, seed=order)
    U = random_reservoir_unitary(N_QUBITS)
    results = {}
    Xq = qrc_features(u, U)
    results['QRC (6 qubits, %d feats)' % Xq.shape[1]] = evaluate(Xq, y)
    results['Linear (window=%d)' % (2 * order)] = evaluate(window_features(u, 2 * order), y)
    results['ESN (%d nodes)' % Xq.shape[1]] = evaluate(esn_features(u, Xq.shape[1]), y)
    return u, y, results

if __name__ == '__main__':
    import json, sys
    out = {}
    for order in (2, 5):
        print(f'--- NARMA{order} ---', flush=True)
        u, y, res = run(order)
        out[f'NARMA{order}'] = {}
        for name, (nmse, pred, yte) in res.items():
            print(f'{name:38s} NMSE = {nmse:.4f}', flush=True)
            out[f'NARMA{order}'][name] = nmse
            np.save(f'pred_narma{order}_{name.split()[0]}.npy', pred)
            np.save(f'true_narma{order}.npy', yte)
    with open('qrc_results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print('saved qrc_results.json')
