"""
Benchmark 6: A device-fidelity factor for the measurement-wall law.

Benchmark 5 gave a parameter-free law predicting a shot-noise-limited QRC
classifier's accuracy from noiseless quantities -- but for SHOT noise only. Its
stated next step: "gate noise shrinks margins -> extend the law with a device
fidelity factor." This benchmark does exactly that, and tests it.

PHYSICS / PRE-STATED HYPOTHESIS (H0, parameter-free):
A global depolarizing channel  rho -> (1-gamma) rho + gamma I/dim  multiplies
every non-identity Pauli expectation (the Z_i and Z_iZ_j readout features) by a
contraction factor. Because the linear readout's decision margins are linear in
those expectations, gate noise contracts every margin by a NOISELESS-computable
factor
    c(gamma) = ||mu1(gamma) - mu0(gamma)|| / ||mu1(0) - mu0(0)||
(the ratio of between-class mean-feature separations, measured on exact/noiseless
features). Since shot noise on each feature scales as 1/sqrt(S) roughly
independently of gamma, class SNR ~ separation * sqrt(S). Equal SNR therefore
predicts that gate noise is exactly equivalent to reducing the effective shot
budget by c(gamma)^2:
    acc(gamma, S)  ==  acc(0,  S * c(gamma)^2).
So a single design-time noiseless quantity c(gamma) should COLLAPSE every
gate-noise accuracy-vs-shots curve onto the gamma=0 curve.

FALSIFICATION (H1): after rescaling the shot axis by c(gamma)^2 the curves do
NOT collapse -> gate noise does something beyond margin contraction (e.g. it
also reshapes the shot-noise covariance or the achievable readout direction),
and a scalar fidelity factor is insufficient.

Achievable accuracy = logistic readout (C=1) RETRAINED on the noisy features at
each budget (the honest "reachable" accuracy, as in benchmark 3), mean over
sample seeds. Simulation only: numpy + qiskit unitary; gate + shot noise only.

Chunked:  python3 qrc_gatenoise.py <arch_id>   -> gn_part<arch>.json
Aggregate:python3 qrc_gatenoise.py agg          -> gate_noise_law.json
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
GAMMAS = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20]
BUDGETS = [500, 1000, 2000, 4000, 8000, 16000, 32000]
SAMPLE_SEEDS = [1, 2, 3]
C_READOUT = 1.0

ARCHS = {
    0: dict(nq=6, K=4, nodes=3, layers=1, gain=1.0, seed=3),
    1: dict(nq=6, K=5, nodes=2, layers=1, gain=1.0, seed=7),
}

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

def build_P(arch_id, gamma):
    a = ARCHS[arch_id]; nq = a['nq']; dim = 2**nq
    U = chain_U(nq, a['layers'], a['seed']); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * a['gain']
    bits, u = make_inputs(); K, nodes = a['K'], a['nodes']
    Imix = np.eye(dim) / dim
    def reset_inject(rho, uu):
        th = gmax*uu; psi = np.array([np.cos(th), np.sin(th)])
        r4 = rho.reshape(dim//2, 2, dim//2, 2)
        rest = np.trace(r4, axis1=1, axis2=3)
        return np.einsum('a,b,ij->iajb', psi, psi, rest).reshape(dim, dim)
    def step(rho):
        rho = U @ rho @ Ud
        if gamma > 0: rho = (1-gamma)*rho + gamma*Imix
        return rho
    P = np.zeros((T, nodes, dim))
    for t in range(K, T):
        rho = np.zeros((dim, dim), complex); rho[0, 0] = 1
        for uu in u[t-K+1:t+1]:
            rho = reset_inject(rho, uu); rho = step(rho)
        for v in range(nodes):
            if v > 0: rho = step(rho)
            P[t, v] = np.real(np.diag(rho)).clip(0); P[t, v] /= P[t, v].sum()
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

def class_sep(Xexact, y01):
    """||mu1 - mu0|| in raw exact-feature space (post-wash training portion)."""
    X = Xexact[WASH:]; y = y01[WASH:]
    sp = int(0.7*len(y)); X, y = X[:sp], y[:sp]
    return float(np.linalg.norm(X[y==1].mean(0) - X[y==0].mean(0)))

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

def run_arch(arch_id):
    bits, u = make_inputs(); labels = task_labels(bits)
    Z = zdiags(ARCHS[arch_id]['nq']); res = []
    # separation at gamma=0 per task (denominator of c)
    P0 = build_P(arch_id, 0.0); Xex0 = feats_exact(P0, Z)
    sep0 = {t: class_sep(Xex0, labels[t]) for t in CLF_TASKS}
    for gamma in GAMMAS:
        P = build_P(arch_id, gamma); Xex = feats_exact(P, Z)
        for tname in CLF_TASKS:
            y01 = labels[tname]
            c = class_sep(Xex, y01) / sep0[tname]
            for S in BUDGETS:
                acc = achievable_acc(P, Z, y01, S)
                res.append(dict(arch=arch_id, task=tname, gamma=gamma, shots=S,
                                c=c, S_eff=S*c*c, acc=acc,
                                exact_sep=class_sep(Xex, y01)))
            print(f'a{arch_id} g={gamma:.2f} {tname:10s} c={c:.3f}', flush=True)
    json.dump(res, open(f'gn_part{arch_id}.json', 'w'), indent=1)
    print(f'arch {arch_id}: {len(res)} cells saved', flush=True)

def agg():
    import numpy as np
    res = []
    for a in ARCHS:
        f = f'gn_part{a}.json'
        if os.path.exists(f): res += json.load(open(f))
    # Collapse test: predict acc(gamma,S) from the gamma=0 curve at S_eff=S*c^2.
    # Build per (arch,task) monotone interpolator of acc0 vs log10(S).
    from bisect import bisect
    curves = {}
    for r in res:
        if r['gamma'] == 0.0:
            curves.setdefault((r['arch'], r['task']), []).append((r['shots'], r['acc']))
    for k in curves: curves[k].sort()
    def interp(key, Seff):
        pts = curves[key]; xs = [np.log10(s) for s, _ in pts]; ys = [a for _, a in pts]
        x = np.log10(max(Seff, 1e-9))
        if x <= xs[0]: return ys[0]
        if x >= xs[-1]: return ys[-1]
        i = bisect(xs, x); x0, x1 = xs[i-1], xs[i]; y0, y1 = ys[i-1], ys[i]
        return y0 + (y1-y0)*(x-x0)/(x1-x0)
    preds, obss, gtag = [], [], []
    for r in res:
        if r['gamma'] == 0.0:  # exclude the fitted-in curve itself
            continue
        p = interp((r['arch'], r['task']), r['S_eff'])
        r['pred_collapse'] = float(p)
        preds.append(p); obss.append(r['acc']); gtag.append(r['gamma'])
    preds = np.array(preds); obss = np.array(obss); gtag = np.array(gtag)
    r2 = 1 - np.sum((obss-preds)**2)/np.sum((obss-obss.mean())**2)
    mae = float(np.mean(np.abs(obss-preds)))
    # baseline: naive (no fidelity factor) -> predict from gamma=0 curve at raw S
    naive = []
    for r in res:
        if r['gamma'] == 0.0: continue
        naive.append(interp((r['arch'], r['task']), r['shots']))
    naive = np.array(naive)
    r2_naive = 1 - np.sum((obss-naive)**2)/np.sum((obss-obss.mean())**2)
    mae_naive = float(np.mean(np.abs(obss-naive)))
    perg = {}
    for g in GAMMAS:
        if g == 0.0: continue
        m = gtag == g
        perg[f'{g}'] = dict(n=int(m.sum()),
                            mae_law=float(np.mean(np.abs(obss[m]-preds[m]))),
                            mae_naive=float(np.mean(np.abs(obss[m]-naive[m]))),
                            mean_c=float(np.mean([r['c'] for r in res
                                        if r['gamma']==g])))
    out = dict(n_cells=len(res), n_pred=len(preds),
               collapse_r2=float(r2), collapse_mae=mae,
               naive_r2=float(r2_naive), naive_mae=mae_naive,
               archs=list(ARCHS.keys()), gammas=GAMMAS, budgets=BUDGETS,
               tasks=CLF_TASKS, C_readout=C_READOUT,
               noise_model='global depolarizing per unitary step; multinomial shot noise',
               fidelity_factor='c(gamma)=||mu1-mu0||_gamma / ||mu1-mu0||_0 (noiseless); S_eff=S*c^2',
               per_gamma=perg, cells=res)
    json.dump(out, open('gate_noise_law.json', 'w'), indent=1)
    print(json.dumps(dict(n_cells=len(res), collapse_r2=float(r2), collapse_mae=mae,
                          naive_r2=float(r2_naive), naive_mae=mae_naive,
                          per_gamma=perg), indent=1))

if __name__ == '__main__':
    if sys.argv[1] == 'agg': agg()
    else: run_arch(int(sys.argv[1]))
