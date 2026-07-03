"""
Benchmark 8: Beyond depolarizing -- does the measurement-wall device-fidelity
factor survive coherent, amplitude-damping and dephasing gate errors?

CONTEXT. B6 extended the shot-noise measurement-wall law with a single design-
time scalar "device-fidelity factor"
    c(eta) = ||mu1(eta) - mu0(eta)|| / ||mu1(0) - mu0(0)||       (noiseless)
measured as the ratio of between-class mean-feature separations, giving the
prediction  acc(eta, S) == acc(0, S * c(eta)^2)  (gate noise == fewer effective
shots). It was confirmed for a GLOBAL DEPOLARIZING channel, whose only effect on
the Z_i / Z_iZ_j readout features is a uniform scalar contraction, so a scalar
factor is nearly exact by construction. B7 found the residual is a shot-
irreducible NEGATIVE bias: gate noise moves the reservoir slightly OFF its
noiseless curve. Honest question B8 answers:

  Depolarizing noise is the single most favourable case for a scalar fidelity
  factor. Do physically different gate errors still contract the readout
  MULTIPLICATIVELY, or do they ROTATE / SHIFT the readout direction so a scalar
  factor is no longer enough?

THREE CHANNELS (each applied per unitary step, single-qubit, strength eta):
  * coherent    -- fixed random per-qubit over-rotation Rx(a_i*eta)Rz(b_i*eta).
                   UNITARY: does not shrink purity, it ROTATES the state.
                   Prediction: rotates the class-separation DIRECTION, which a
                   magnitude-only c(eta) cannot capture -> collapse degrades.
  * amp_damping -- per-qubit amplitude damping toward |0> (lambda=eta). NON-
                   UNITAL: biases populations (Z_i -> +1), contracts AND shifts
                   the feature mean. Prediction: scalar factor mis-predicts.
  * dephasing   -- per-qubit phase damping (lambda=eta). UNITAL but ANISOTROPIC
                   in Pauli space (kills coherences, keeps populations). Closest
                   to depolarizing; prediction: collapse still works reasonably.

PRE-REGISTERED HYPOTHESIS (H0): the B6 scalar-fidelity collapse works about as
well for all three channels as for depolarizing (collapse R^2 > 0.9 and a large
MAE reduction vs the no-factor naive baseline for each channel).
FALSIFICATION (H1): for the non-scalar channels (esp. coherent) the collapse is
materially worse -- the scalar factor is depolarizing-specific.

DIRECT DIAGNOSTIC. cos(eta) = <dmu(eta), dmu(0)> / (||.||||.||) per task: a pure
scalar contraction keeps cos=1, a rotation drops it. Directly answers "do
coherent errors rotate the readout direction?".

Achievable accuracy = logistic readout (C=1) RETRAINED on noisy features at each
budget, mean over sample seeds (same protocol as B3/B6). Simulation only:
numpy density matrix + qiskit unitary; gate + shot noise only. NEVER hardware.

Run one channel:  python3 qrc_beyondnoise.py <coherent|amp_damping|dephasing>
Aggregate:        python3 qrc_beyondnoise.py agg   -> beyond_noise_law.json
"""
import sys, json, os, warnings
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
warnings.filterwarnings('ignore')

T = 400
WASH = 60
CLF_TASKS = ['parity2', 'parity3', 'parity4', 'delay_xor', 'majority3']
ETAS = [0.0, 0.02, 0.05, 0.10, 0.15]
BUDGETS = [500, 2000, 8000, 32000]
SAMPLE_SEEDS = [1, 2, 3]
C_READOUT = 1.0
CHANNELS = ['coherent', 'amp_damping', 'dephasing']

ARCH = dict(nq=6, K=4, nodes=3, layers=1, gain=1.0, seed=3)  # the hw design (arch 0)

def make_inputs(seed=0):
    rng = np.random.default_rng(seed)
    bits = rng.integers(0, 2, T)
    return bits, 0.05 + 0.10 * bits

def task_labels(bits):
    b = bits
    return {
        'parity2':   np.array([b[t]^b[t-1] if t>=1 else 0 for t in range(T)]),
        'parity3':   np.array([b[t]^b[t-1]^b[t-2] if t>=2 else 0 for t in range(T)]),
        'parity4':   np.array([b[t]^b[t-1]^b[t-2]^b[t-3] if t>=3 else 0 for t in range(T)]),
        'delay_xor': np.array([b[t]^b[t-3] if t>=3 else 0 for t in range(T)]),
        'majority3': np.array([1 if b[t]+b[t-1]+b[t-2]>=2 else 0 for t in range(T)]),
    }

def chain_U(nq, layers, seed):
    r = np.random.default_rng(seed)
    qc = QuantumCircuit(nq)
    for _ in range(layers):
        for q in range(nq):
            qc.rx(r.uniform(0, 2*np.pi), q); qc.rz(r.uniform(0, 2*np.pi), q)
        for q in range(0, nq-1, 2):
            qc.rzz(r.uniform(0, np.pi), q, q+1)
        for q in range(1, nq-1, 2):
            qc.rzz(r.uniform(0, np.pi), q, q+1)
    return Operator(qc).data

def zdiags(nq):
    dim = 2**nq
    bi = ((np.arange(dim)[:, None] >> np.arange(nq)[None, :]) & 1)
    z1 = [1-2*bi[:, i].astype(float) for i in range(nq)]
    z2 = [(1-2*bi[:, i])*(1-2*bi[:, j]) for i, j in combinations(range(nq), 2)]
    return np.array(z1 + z2)

# ---------------- noise channels (single-qubit, per step) ----------------
def coherent_unitary(nq, eta, seed=101):
    r = np.random.default_rng(seed)
    a = r.uniform(-1, 1, nq); b = r.uniform(-1, 1, nq)
    qc = QuantumCircuit(nq)
    for q in range(nq):
        qc.rx(a[q]*eta, q); qc.rz(b[q]*eta, q)
    return Operator(qc).data

def kraus_amp_damping(lam):
    K0 = np.array([[1, 0], [0, np.sqrt(1-lam)]], complex)
    K1 = np.array([[0, np.sqrt(lam)], [0, 0]], complex)
    return [K0, K1]

def kraus_dephasing(lam):
    K0 = np.array([[1, 0], [0, np.sqrt(1-lam)]], complex)
    K1 = np.array([[0, 0], [0, np.sqrt(lam)]], complex)
    return [K0, K1]

def apply_1q_kraus_all(rho, Ks, nq):
    dim = 2**nq
    R = rho.reshape([2]*nq + [2]*nq)     # row axes 0..nq-1, col axes nq..2nq-1
    for q in range(nq):
        out = np.zeros_like(R)
        for K in Ks:
            T1 = np.tensordot(K, R, axes=([1], [q]))
            T1 = np.moveaxis(T1, 0, q)
            T1 = np.tensordot(T1, K.conj(), axes=([nq+q], [1]))
            T1 = np.moveaxis(T1, -1, nq+q)
            out += T1
        R = out
    return R.reshape(dim, dim)

def build_P(eta, channel):
    nq = ARCH['nq']; dim = 2**nq
    U = chain_U(nq, ARCH['layers'], ARCH['seed']); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * ARCH['gain']
    bits, u = make_inputs(); K, nodes = ARCH['K'], ARCH['nodes']
    E = Ed = Ks = None
    if channel == 'coherent':
        E = coherent_unitary(nq, eta); Ed = E.conj().T
    elif channel == 'amp_damping':
        Ks = kraus_amp_damping(eta) if eta > 0 else None
    elif channel == 'dephasing':
        Ks = kraus_dephasing(eta) if eta > 0 else None
    else:
        raise ValueError(channel)

    def reset_inject(rho, uu):
        th = gmax*uu; psi = np.array([np.cos(th), np.sin(th)])
        r4 = rho.reshape(dim//2, 2, dim//2, 2)
        rest = np.trace(r4, axis1=1, axis2=3)
        return np.einsum('a,b,ij->iajb', psi, psi, rest).reshape(dim, dim)

    def step(rho):
        rho = U @ rho @ Ud
        if eta > 0:
            if channel == 'coherent':
                rho = E @ rho @ Ed
            else:
                rho = apply_1q_kraus_all(rho, Ks, nq)
        return rho

    P = np.zeros((T, nodes, dim))
    for t in range(K, T):
        rho = np.zeros((dim, dim), complex); rho[0, 0] = 1
        for uu in u[t-K+1:t+1]:
            rho = reset_inject(rho, uu); rho = step(rho)
        for v in range(nodes):
            if v > 0: rho = step(rho)
            d = np.real(np.diag(rho)).clip(0)
            P[t, v] = d / d.sum()
    return P

def feats_exact(P, Z):
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    out = np.zeros((Tn, nodes*F))
    for t in range(Tn):
        for v in range(nodes):
            out[t, v*F:(v+1)*F] = Z @ P[t, v]
    return out

def feats_noisy(P, Z, shots, rng):
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    out = np.zeros((Tn, nodes*F))
    for t in range(Tn):
        for v in range(nodes):
            p = rng.multinomial(shots, P[t, v]) / shots
            out[t, v*F:(v+1)*F] = Z @ p
    return out

def sep_vector(Xexact, y01):
    X = Xexact[WASH:]; y = y01[WASH:]
    sp = int(0.7*len(y)); X, y = X[:sp], y[:sp]
    return X[y == 1].mean(0) - X[y == 0].mean(0)

def achievable_acc(P, Z, y01, S):
    yp = y01[WASH:]; sp = int(0.7*len(yp)); yte = yp[sp:]
    accs = []
    for ss in SAMPLE_SEEDS:
        rng = np.random.default_rng(ss)
        Xn = feats_noisy(P, Z, S, rng)[WASH:]
        sc = StandardScaler().fit(Xn[:sp]); Xs = sc.transform(Xn)
        clf = LogisticRegression(max_iter=2000, C=C_READOUT).fit(Xs[:sp], yp[:sp])
        accs.append(float(clf.score(Xs[sp:], yte)))
    return float(np.mean(accs))

def run_channel(channel):
    bits, u = make_inputs(); labels = task_labels(bits)
    Z = zdiags(ARCH['nq']); res = []
    P0 = build_P(0.0, channel); Xex0 = feats_exact(P0, Z)
    dmu0 = {t: sep_vector(Xex0, labels[t]) for t in CLF_TASKS}
    for eta in ETAS:
        P = build_P(eta, channel); Xex = feats_exact(P, Z)
        for tname in CLF_TASKS:
            y01 = labels[tname]
            dmu = sep_vector(Xex, y01)
            n0 = np.linalg.norm(dmu0[tname]); nn = np.linalg.norm(dmu)
            c = float(nn / n0)
            cos = float(np.dot(dmu, dmu0[tname]) / (nn*n0 + 1e-12))
            for S in BUDGETS:
                acc = achievable_acc(P, Z, y01, S)
                res.append(dict(channel=channel, task=tname, eta=eta, shots=S,
                                c=c, cos=cos, S_eff=S*c*c, acc=acc))
            print(f'{channel} eta={eta:.2f} {tname:10s} c={c:.3f} cos={cos:.3f}', flush=True)
    json.dump(res, open(f'bn_{channel}.json', 'w'), indent=1)
    print(f'{channel}: {len(res)} cells saved', flush=True)

def _interp(pts, Seff):
    from bisect import bisect
    xs = [np.log10(s) for s, _ in pts]; ys = [a for _, a in pts]
    x = np.log10(max(Seff, 1e-9))
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    i = bisect(xs, x); x0, x1 = xs[i-1], xs[i]; y0, y1 = ys[i-1], ys[i]
    return y0 + (y1-y0)*(x-x0)/(x1-x0)

def agg():
    allres = []
    for ch in CHANNELS:
        f = f'bn_{ch}.json'
        if os.path.exists(f): allres += json.load(open(f))
    summary = {}
    for ch in CHANNELS:
        res = [r for r in allres if r['channel'] == ch]
        if not res: continue
        curves = {}
        for r in res:
            if r['eta'] == 0.0:
                curves.setdefault(r['task'], []).append((r['shots'], r['acc']))
        for k in curves: curves[k].sort()
        preds, naive, obss, etag, biases = [], [], [], [], []
        for r in res:
            if r['eta'] == 0.0: continue
            p = _interp(curves[r['task']], r['S_eff'])
            n = _interp(curves[r['task']], r['shots'])
            r['pred_collapse'] = float(p); r['pred_naive'] = float(n)
            preds.append(p); naive.append(n); obss.append(r['acc']); etag.append(r['eta'])
            biases.append(r['acc'] - p)
        preds = np.array(preds); naive = np.array(naive); obss = np.array(obss)
        etag = np.array(etag); biases = np.array(biases)
        def r2(pr): return float(1 - np.sum((obss-pr)**2)/np.sum((obss-obss.mean())**2))
        perg = {}
        for e in ETAS:
            if e == 0.0: continue
            m = etag == e
            perg[f'{e}'] = dict(
                n=int(m.sum()),
                mae_law=float(np.mean(np.abs(obss[m]-preds[m]))),
                mae_naive=float(np.mean(np.abs(obss[m]-naive[m]))),
                mean_bias=float(np.mean(biases[m])),
                mean_c=float(np.mean([r['c'] for r in res if r['eta'] == e])),
                mean_cos=float(np.mean([r['cos'] for r in res if r['eta'] == e])))
        summary[ch] = dict(
            n_pred=len(preds),
            collapse_r2=r2(preds), collapse_mae=float(np.mean(np.abs(obss-preds))),
            naive_r2=r2(naive), naive_mae=float(np.mean(np.abs(obss-naive))),
            mae_reduction_pct=float(100*(1 - np.mean(np.abs(obss-preds))
                                          / max(np.mean(np.abs(obss-naive)), 1e-9))),
            mean_bias=float(np.mean(biases)),
            min_cos=float(np.min([r['cos'] for r in res if r['eta'] > 0])),
            per_eta=perg)
    out = dict(
        benchmark='B8 beyond-depolarizing gate noise',
        arch=ARCH, tasks=CLF_TASKS, etas=ETAS, budgets=BUDGETS,
        sample_seeds=SAMPLE_SEEDS, C_readout=C_READOUT,
        fidelity_factor='c(eta)=||dmu||_eta/||dmu||_0 (noiseless); S_eff=S*c^2',
        direction_diagnostic='cos(eta)=<dmu_eta,dmu_0>/(||.||||.||) per task',
        channels=summary, cells=allres)
    json.dump(out, open('beyond_noise_law.json', 'w'), indent=1)
    print(json.dumps({ch: {k: summary[ch][k] for k in
          ('collapse_r2', 'collapse_mae', 'naive_r2', 'naive_mae',
           'mae_reduction_pct', 'mean_bias', 'min_cos')} for ch in summary}, indent=1))

if __name__ == '__main__':
    if sys.argv[1] == 'agg': agg()
    else: run_channel(sys.argv[1])
