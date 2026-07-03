"""
The measurement-wall law: does retained quantum benefit collapse onto a
universal curve in feature SNR = std_t(feature) * sqrt(total shots)?

Phase build:   python3 qrc_law.py build <arch_id>      (stores distributions)
Phase eval:    python3 qrc_law.py eval                  (samples all budgets)
"""
import sys, os, json
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

T = 400
WASH = 60

# ---------------- tasks (shared input bit stream) ----------------
def make_inputs(seed=0):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, T)
    return bits, 0.05 + 0.10 * bits

def task_labels(bits):
    """dict name -> (labels, kind)"""
    b = bits
    L = {}
    L['parity2']  = (np.array([b[t]^b[t-1] if t>=1 else 0 for t in range(T)]), 'clf')
    L['parity3']  = (np.array([b[t]^b[t-1]^b[t-2] if t>=2 else 0 for t in range(T)]), 'clf')
    L['parity4']  = (np.array([b[t]^b[t-1]^b[t-2]^b[t-3] if t>=3 else 0 for t in range(T)]), 'clf')
    L['delay_xor']= (np.array([b[t]^b[t-3] if t>=3 else 0 for t in range(T)]), 'clf')
    L['majority3']= (np.array([1 if b[t]+b[t-1]+b[t-2]>=2 else 0 for t in range(T)]), 'clf')
    # precise-output task: NARMA2 driven by the same bits (regression)
    u = 0.05 + 0.10*b
    y = np.zeros(T)
    for t in range(1, T-1):
        y[t+1] = 0.4*y[t] + 0.4*y[t]*y[t-1] + 0.6*u[t]**3 + 0.1
    L['narma2_reg'] = (y, 'reg')
    return L

# ---------------- architectures ----------------
ARCHS = {
    0: dict(nq=6, K=4, nodes=3, layers=1, gain=1.0, seed=3),   # our hw design
    1: dict(nq=6, K=5, nodes=2, layers=1, gain=1.0, seed=7),
    2: dict(nq=6, K=4, nodes=3, layers=2, gain=1.0, seed=5),
    3: dict(nq=6, K=6, nodes=3, layers=1, gain=0.5, seed=3),   # weak encoding
    4: dict(nq=5, K=4, nodes=3, layers=1, gain=1.0, seed=11),  # smaller register
    5: dict(nq=6, K=4, nodes=4, layers=1, gain=1.0, seed=13),
}

def chain_U(nq, layers, seed):
    r = np.random.default_rng(seed)
    qc = QuantumCircuit(nq)
    for _ in range(layers):
        for q in range(nq):
            qc.rx(r.uniform(0, 2*np.pi), q)
            qc.rz(r.uniform(0, 2*np.pi), q)
        for q in range(0, nq-1, 2):
            qc.rzz(r.uniform(0, np.pi), q, q+1)
        for q in range(1, nq-1, 2):
            qc.rzz(r.uniform(0, np.pi), q, q+1)
    return Operator(qc).data

def build(arch_id):
    a = ARCHS[arch_id]
    nq = a['nq']; dim = 2**nq
    U = chain_U(nq, a['layers'], a['seed']); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * a['gain']
    bits, u = make_inputs()
    K, nodes = a['K'], a['nodes']

    def reset_inject(rho, uu):
        th = gmax*uu
        psi = np.array([np.cos(th), np.sin(th)])
        r4 = rho.reshape(dim//2, 2, dim//2, 2)
        rest = np.trace(r4, axis1=1, axis2=3)
        return np.einsum('a,b,ij->iajb', psi, psi, rest).reshape(dim, dim)

    P = np.zeros((T, nodes, dim))          # measurement distributions
    for t in range(K, T):
        rho = np.zeros((dim, dim), complex); rho[0, 0] = 1
        for uu in u[t-K+1:t+1]:
            rho = reset_inject(rho, uu)
            rho = U @ rho @ Ud
        for v in range(nodes):
            if v > 0:
                rho = U @ rho @ Ud
            P[t, v] = np.real(np.diag(rho)).clip(0)
            P[t, v] /= P[t, v].sum()
    np.savez_compressed(f'law_arch{arch_id}.npz', P=P, nq=nq, K=K, nodes=nodes)
    print(f'arch {arch_id} built', flush=True)

# ---------------- features / eval ----------------
def zdiags(nq):
    dim = 2**nq
    bi = ((np.arange(dim)[:, None] >> np.arange(nq)[None, :]) & 1)
    z1 = [1-2*bi[:, i].astype(float) for i in range(nq)]
    z2 = [(1-2*bi[:, i])*(1-2*bi[:, j]) for i, j in combinations(range(nq), 2)]
    return np.array(z1 + z2)               # (F, dim)

def feats_from_P(P, Z, shots, rng=None):
    """(T, nodes, dim) -> (T, nodes*F). shots=0 -> exact."""
    Tn, nodes, dim = P.shape
    out = np.zeros((Tn, nodes*Z.shape[0]))
    for t in range(Tn):
        for v in range(nodes):
            p = P[t, v]
            if shots:
                p = rng.multinomial(shots, p) / shots
            out[t, v*Z.shape[0]:(v+1)*Z.shape[0]] = Z @ p
    return out

def perf(X, y, kind, K):
    from sklearn.linear_model import LogisticRegression, Ridge
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    Xs, ys = X[WASH:], y[WASH:]
    split = int(0.7*len(ys))
    best = -1e9
    if kind == 'clf':
        for C in (0.1, 1, 10, 100):
            m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, C=C))
            m.fit(Xs[:split], ys[:split])
            best = max(best, m.score(Xs[split:], ys[split:]))
    else:
        for al in (1e-4, 1e-2, 1.0):
            m = make_pipeline(StandardScaler(), Ridge(alpha=al))
            m.fit(Xs[:split], ys[:split])
            pred = m.predict(Xs[split:])
            best = max(best, 1 - np.mean((pred-ys[split:])**2)/np.var(ys[split:]))  # R^2
    return best

def evaluate_all(budgets=(250, 1000, 4000, 16000, 64000), sample_seeds=(1, 2)):
    bits, u = make_inputs()
    labels = task_labels(bits)
    results = []
    for arch_id in ARCHS:
        f = f'law_arch{arch_id}.npz'
        if not os.path.exists(f):
            continue
        d = np.load(f)
        P, nq, K, nodes = d['P'], int(d['nq']), int(d['K']), int(d['nodes'])
        Z = zdiags(nq)
        Fex = feats_from_P(P, Z, 0)
        sig = np.median(Fex[WASH:].std(axis=0))       # median feature signal std
        for tname, (y, kind) in labels.items():
            floor = perf(np.zeros((T, 1)) + u[:, None], y, kind, K)  # inputs-only linear-ish floor proxy
            pex = perf(Fex, y, kind, K)
            for S in budgets:
                accs = []
                for ss in sample_seeds:
                    rng = np.random.default_rng(ss)
                    Fn = feats_from_P(P, Z, S, rng)
                    accs.append(perf(Fn, y, kind, K))
                pn = float(np.mean(accs))
                snr = float(sig * np.sqrt(S))
                denom = (pex - floor)
                R = float((pn - floor)/denom) if abs(denom) > 0.02 else None
                results.append(dict(arch=arch_id, task=tname, kind=kind, shots=S,
                                    snr=snr, floor=float(floor), exact=float(pex),
                                    noisy=pn, retained=R))
                print(f'a{arch_id} {tname:10s} S={S:>6} snr={snr:6.2f} '
                      f'floor={floor:.3f} exact={pex:.3f} noisy={pn:.3f}', flush=True)
    json.dump(results, open('law_results.json', 'w'), indent=1)
    print(f'{len(results)} cells saved')

if __name__ == '__main__':
    if sys.argv[1] == 'build':
        build(int(sys.argv[2]))
    else:
        evaluate_all()
