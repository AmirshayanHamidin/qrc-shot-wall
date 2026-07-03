"""
Benchmark 10: Readout retraining under noise -- is the measurement-wall law's
residual a suboptimal-readout artifact, or intrinsic?

CONTEXT. The B5/B6 measurement-wall law predicts a shot-noise-limited QRC
classifier's accuracy from NOISELESS quantities: it takes the readout direction
w0 TRAINED ON NOISELESS features, projects the exact per-sample decision margins,
and adds the closed-form shot-noise (and, in B6, gate-noise-contracted) covariance
along w0 via a probit. So the law's native prediction target is the accuracy of
the FIXED noiseless-design readout run on the noisy device. But every "reachable"
accuracy in B3/B6/B8 was measured with the readout RETRAINED on the noisy
features at each budget. B6/B8 reported the law's residual (~2.9 pp) against that
RETRAINED accuracy. B7 attributed the residual to a shot-irreducible off-curve
bias. This benchmark isolates a competing explanation the agenda flagged:

  Is the residual mostly because the law scores a suboptimal (fixed) readout while
  reachable accuracy retrains? I.e. is residual = retraining gain?

DECOMPOSITION (per cell = arch x task x gamma x shots):
  acc_fixed(g,S)   : readout pipeline fit on gamma=0 EXACT features, applied to
                     the gate-noisy shot-sampled features. (The law's target.)
  acc_retrain(g,S) : readout refit on the gamma-noisy shot-sampled features. (B6.)
  law_pred(g,S)    : B5/B6 probit prediction for the FIXED w0 -- exact margins on
                     the gamma-contracted mean features + multinomial shot
                     covariance along w0.
  retrain_gain     = acc_retrain - acc_fixed
  resid_fixed      = law_pred - acc_fixed     (law vs its OWN target)
  resid_retrain    = law_pred - acc_retrain   (the "official" B6-style residual)

PRE-REGISTERED HYPOTHESIS (H0, "residual is a readout artifact"): retraining
yields a SYSTEMATIC POSITIVE gain, and the law predicts acc_fixed materially
better than acc_retrain -- MAE(resid_fixed) <= 0.5 * MAE(resid_retrain) -- so the
bulk of the reported residual is the retraining gain, not intrinsic error.

FALSIFICATION (H1): retrain_gain ~ 0 or non-systematic, OR MAE(resid_fixed) is not
materially below MAE(resid_retrain) -- the residual survives against the law's own
fixed-readout target, i.e. it is intrinsic (consistent with B7's off-curve bias).

Achievable/retrained accuracy: logistic (C=1) as in B3/B6/B8. Simulation only:
numpy density matrix + qiskit unitary; global depolarizing gate noise + multinomial
shot noise. NEVER hardware; never touch credentials.

Run one arch:  python3 qrc_retrain.py <arch_id>   -> rt_part<arch>.json
Aggregate:     python3 qrc_retrain.py agg          -> retrain_law.json
"""
import sys, json, os, warnings
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from scipy.stats import norm
warnings.filterwarnings('ignore')

T = 400
WASH = 60
CLF_TASKS = ['parity2', 'parity3', 'parity4', 'delay_xor', 'majority3']
GAMMAS = [0.0, 0.05, 0.10, 0.15]
BUDGETS = [500, 2000, 8000, 32000]
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

def split_idx(n):
    return int(0.7*n)

def fit_readout(Xtr, ytr):
    sc = StandardScaler().fit(Xtr)
    clf = LogisticRegression(max_iter=3000, C=C_READOUT).fit(sc.transform(Xtr), ytr)
    return sc, clf

def acc_of(sc, clf, Xte, yte):
    return float(clf.score(sc.transform(Xte), yte))

def law_predict(P, Z, sc0, clf0, y01):
    """B5/B6 probit prediction of FIXED-readout acc under multinomial shot noise.
    Uses exact (gamma-contracted) mean features for margins; multinomial shot
    covariance along the readout in raw feature space for sigma. Returns dict of
    predicted accuracy per shot budget."""
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    Xex = feats_exact(P, Z)
    sp = split_idx(Tn - WASH) + WASH  # absolute split index over t>=WASH
    # raw-feature linear functional g(x) = a . x + const from scaler+logistic
    w = clf0.coef_.ravel(); b0 = float(clf0.intercept_[0])
    a = w / sc0.scale_                        # raw-space weights (F*nodes,)
    const = b0 - np.dot(w, sc0.mean_/sc0.scale_)
    margins = Xex @ a + const                 # signed decision value, noiseless
    # per-node raw weights
    aw = a.reshape(nodes, F)
    # per-sample shot-noise variance of margin (per unit 1/S): quad form of Z-cov
    # Cov(Z p_hat) = Z (diag(p) - p p^T) Z^T / S ; margin var = sum_v aw_v^T Cov aw_v
    qv = np.zeros(Tn)                         # variance * S (S-independent part)
    for t in range(Tn):
        s = 0.0
        for v in range(nodes):
            p = P[t, v]
            zp = Z @ p                         # (F,)
            zaw = Z.T @ aw[v]                  # (dim,) = Z^T a_v
            # a_v^T Z (diag(p)-pp^T) Z^T a_v = sum_j p_j zaw_j^2 - (sum_j p_j zaw_j)^2
            m1 = np.dot(p, zaw*zaw); m2 = np.dot(p, zaw)
            s += m1 - m2*m2
        qv[t] = s
    y = y01
    te = slice(sp, Tn)
    out = {}
    for S in BUDGETS:
        sigma = np.sqrt(np.maximum(qv[te]/S, 1e-18))
        mg = margins[te]; yy = y[te]
        # P(decision>0) = Phi(mg/sigma); correct prob depends on true label
        p_pos = norm.cdf(mg/sigma)
        p_correct = np.where(yy == 1, p_pos, 1-p_pos)
        out[S] = float(np.mean(p_correct))
    return out

def run_arch(arch_id):
    bits, u = make_inputs(); labels = task_labels(bits)
    Z = zdiags(ARCHS[arch_id]['nq']); res = []
    P0 = build_P(arch_id, 0.0); Xex0 = feats_exact(P0, Z)
    Tn = Xex0.shape[0]; sp = split_idx(Tn - WASH) + WASH
    Pcache = {g: build_P(arch_id, g) for g in GAMMAS}
    for tname in CLF_TASKS:
        y = labels[tname]
        # noiseless design readout trained on gamma=0 exact features
        sc0, clf0 = fit_readout(Xex0[WASH:sp], y[WASH:sp])
        acc_exact0 = acc_of(sc0, clf0, Xex0[sp:], y[sp:])
        for g in GAMMAS:
            P = Pcache[g]
            lawp = law_predict(P, Z, sc0, clf0, y)
            for S in BUDGETS:
                af, ar = [], []
                for ss in SAMPLE_SEEDS:
                    rng = np.random.default_rng(1000*ss + int(1000*g))
                    Xn = feats_noisy(P, Z, S, rng)
                    # fixed readout (design-time, gamma=0-trained) on noisy test
                    af.append(acc_of(sc0, clf0, Xn[sp:], y[sp:]))
                    # retrained readout on noisy features
                    sc, clf = fit_readout(Xn[WASH:sp], y[WASH:sp])
                    ar.append(acc_of(sc, clf, Xn[sp:], y[sp:]))
                acc_fixed = float(np.mean(af)); acc_retrain = float(np.mean(ar))
                lp = float(lawp[S])
                res.append(dict(arch=arch_id, task=tname, gamma=g, shots=S,
                                acc_fixed=acc_fixed, acc_retrain=acc_retrain,
                                law_pred=lp, acc_exact0=float(acc_exact0),
                                retrain_gain=acc_retrain-acc_fixed,
                                resid_fixed=lp-acc_fixed,
                                resid_retrain=lp-acc_retrain))
            print(f'a{arch_id} {tname:10s} g={g:.2f} done', flush=True)
    json.dump(res, open(f'rt_part{arch_id}.json', 'w'), indent=1)
    print(f'arch {arch_id}: {len(res)} cells saved', flush=True)

def agg():
    res = []
    for a in ARCHS:
        f = f'rt_part{a}.json'
        if os.path.exists(f): res += json.load(open(f))
    A = np.array
    noisy = [r for r in res if r['gamma'] > 0.0]  # noise-present cells
    rg = A([r['retrain_gain'] for r in noisy])
    rf = A([abs(r['resid_fixed']) for r in noisy])
    rr = A([abs(r['resid_retrain']) for r in noisy])
    mae_fixed = float(np.mean(rf)); mae_retrain = float(np.mean(rr))
    # signed means
    sf = float(np.mean([r['resid_fixed'] for r in noisy]))
    sr = float(np.mean([r['resid_retrain'] for r in noisy]))
    # per gamma
    perg = {}
    for g in GAMMAS:
        if g == 0.0: continue
        m = [r for r in noisy if r['gamma'] == g]
        perg[f'{g}'] = dict(
            n=len(m),
            mean_retrain_gain=float(np.mean([r['retrain_gain'] for r in m])),
            mae_resid_fixed=float(np.mean([abs(r['resid_fixed']) for r in m])),
            mae_resid_retrain=float(np.mean([abs(r['resid_retrain']) for r in m])),
        )
    # also gamma=0 (pure shot noise) retrain gain, for reference
    shot0 = [r for r in res if r['gamma'] == 0.0]
    gain0 = float(np.mean([r['retrain_gain'] for r in shot0]))
    # fraction of the official residual explained by retraining gain
    frac_explained = float(1 - mae_fixed/mae_retrain) if mae_retrain > 0 else None
    # correlation between retrain_gain and resid_retrain (if gain explains residual,
    # they should track: larger gain -> larger official residual)
    corr = float(np.corrcoef(rg, A([r['resid_retrain'] for r in noisy]))[0,1])
    H0 = bool(mae_fixed <= 0.5*mae_retrain and np.mean(rg) > 0.005)
    out = dict(
        n_cells=len(res), n_noisy=len(noisy),
        archs=list(ARCHS.keys()), gammas=GAMMAS, budgets=BUDGETS, tasks=CLF_TASKS,
        mean_retrain_gain_noisy=float(np.mean(rg)),
        mean_retrain_gain_shotonly=gain0,
        mae_resid_fixed=mae_fixed, mae_resid_retrain=mae_retrain,
        signed_resid_fixed=sf, signed_resid_retrain=sr,
        frac_residual_explained_by_retraining=frac_explained,
        corr_gain_vs_officialresidual=corr,
        H0_readout_artifact_supported=H0,
        per_gamma=perg,
        note='acc_fixed=gamma0-trained readout on noisy test; acc_retrain=refit on '
             'noisy; law_pred=B5/B6 probit for fixed readout. resid=law-acc.',
        cells=res)
    json.dump(out, open('retrain_law.json', 'w'), indent=1)
    print(json.dumps({k: out[k] for k in
        ['n_cells','n_noisy','mean_retrain_gain_noisy','mean_retrain_gain_shotonly',
         'mae_resid_fixed','mae_resid_retrain','frac_residual_explained_by_retraining',
         'corr_gain_vs_officialresidual','H0_readout_artifact_supported']}, indent=1))

if __name__ == '__main__':
    if sys.argv[1] == 'agg':
        agg()
    else:
        run_arch(int(sys.argv[1]))
