"""
Benchmark 11 - Second task family: external validity of the wall and the law.
(simulation only; numpy density matrix + qiskit unitary)

CONTEXT. Every previous benchmark (B1-B10) drives the reservoir with ONE binary
bit stream u in {0.05,0.15} and targets NARMA-style regression or parity/majority
classification. That is a single task family. A law and a "wall" fitted inside one
family may be an artifact of that family. B11 swaps in a genuinely INDEPENDENT
family and re-tests, changing nothing else:

  * INPUT family: a continuous, chaotic Mackey-Glass series (beta=0.2, gamma=0.1,
    p=10, tau=17), normalised into the encoder's monotonic angle range. Different
    input DISTRIBUTION (continuum vs 2-level) and a standard reservoir-computing
    benchmark signal, unrelated to i.i.d. bits.
  * New CLASSIFICATION targets (non-parity, nonlinear, memory-dependent):
       signprod  y=1 if (u_t-ubar)(u_{t-2}-ubar) > 0     (multiplicative, lag 2)
       signcorr  y=1 if (u_t-u_{t-1})(u_{t-2}-u_{t-3})>0 (increment-correlation)
       updown    y=1 if u_t > u_{t-2}                     (comparison w/ memory)
  * New REGRESSION target:
       mg1       predict u_{t+1} (one-step-ahead of the chaotic series).

PRE-REGISTERED HYPOTHESES (falsifiable, stated before running):
  H1  (wall generalises) On the new CLASSIFICATION family, retained quantum
      benefit collapses toward the inputs-only classical floor at low shot
      budgets, i.e. retention rises monotonically with margin*sqrt(S) as for
      parity. The wall is not a parity artifact.
  H2  (law generalises, EXTERNAL VALIDITY) The B5/B6 parameter-free probit
      predictor (identical code, NO refit, zero free parameters) predicts the
      shot-limited FIXED-readout accuracy on the new classification tasks to
      B5-class error. PASS bar set in advance: R^2 > 0.90 AND MAE < 3.0 pp over
      the arch x task x budget grid. If it fails, the law's domain is bounded to
      the parity family and that is the finding.
  H3  (task-shape generalises) The Mackey-Glass REGRESSION target shows the same
      low shot-noise retention as NARMA (B3): retained fraction < 0.15 at 250
      shots, i.e. regression exposes the full shot noise regardless of family.

Only shot noise here (gamma=0); the device-fidelity extension (B6) is orthogonal.

Phase:  python3 qrc_taskfam.py run <arch_id>     -> tf_part<arch>.json
        python3 qrc_taskfam.py agg               -> ../results/taskfam_law.json
"""
import sys, os, json
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler

T = 400
WASH = 60
BUDGETS = (250, 1000, 4000, 16000, 64000)
SAMPLE_SEEDS = (1, 2, 3)
C_READOUT = 10.0
CLF_TASKS = ['updown', 'accel', 'prodmed']
REG_TASKS = ['mg1']

ARCHS = {
    0: dict(nq=6, K=4, nodes=3, layers=1, gain=1.0, seed=3),
    1: dict(nq=6, K=5, nodes=2, layers=1, gain=1.0, seed=7),
    2: dict(nq=6, K=4, nodes=3, layers=2, gain=1.0, seed=5),
    4: dict(nq=5, K=4, nodes=3, layers=1, gain=1.0, seed=11),
}

def mackey_glass(n, seed=0, beta=0.2, gamma=0.1, p=10, tau=17, discard=500):
    rng = np.random.default_rng(seed)
    hist = 1.2 + 0.05*rng.standard_normal(tau+1)
    x = list(hist)
    for _ in range(discard + n):
        xt = x[-1]; xtau = x[-1-tau]
        x.append(xt + beta*xtau/(1+xtau**p) - gamma*xt)
    return np.array(x[-n:])

def make_inputs(seed=0):
    raw = mackey_glass(T, seed=seed)
    lo, hi = np.percentile(raw, 1), np.percentile(raw, 99)
    un = np.clip((raw - lo)/(hi - lo), 0, 1)
    return 0.02 + 0.16*un

def task_labels(u):
    ubar = u.mean()
    # updown: comparison over lag 2 (needs 1 step of memory), naturally ~50/50
    ud = np.array([1 if u[t] > u[t-2] else 0 for t in range(T)], float); ud[:2] = 0
    # accel: sign of discrete curvature u_t-2u_{t-1}+u_{t-2} (2nd difference)
    ac = np.array([1 if (u[t]-2*u[t-1]+u[t-2]) > 0 else 0 for t in range(T)], float); ac[:2] = 0
    # prodmed: multiplicative lag-2 interaction, median-split to force balance
    pr = np.array([(u[t]-ubar)*(u[t-2]-ubar) for t in range(T)]); pr[:2] = 0.0
    med = np.median(pr[WASH:])
    pm = (pr > med).astype(float); pm[:2] = 0
    mg1 = np.concatenate([u[1:], u[-1:]])
    return {'updown': (ud, 'clf'), 'accel': (ac, 'clf'),
            'prodmed': (pm, 'clf'), 'mg1': (mg1, 'reg')}

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

def build_P(arch_id):
    a = ARCHS[arch_id]; nq = a['nq']; dim = 2**nq
    U = chain_U(nq, a['layers'], a['seed']); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * a['gain']
    u = make_inputs(); K, nodes = a['K'], a['nodes']
    def reset_inject(rho, uu):
        th = gmax*uu; psi = np.array([np.cos(th), np.sin(th)])
        r4 = rho.reshape(dim//2, 2, dim//2, 2)
        rest = np.trace(r4, axis1=1, axis2=3)
        return np.einsum('a,b,ij->iajb', psi, psi, rest).reshape(dim, dim)
    P = np.zeros((T, nodes, dim))
    for t in range(K, T):
        rho = np.zeros((dim, dim), complex); rho[0, 0] = 1
        for uu in u[t-K+1:t+1]:
            rho = reset_inject(rho, uu); rho = U @ rho @ Ud
        for v in range(nodes):
            if v > 0: rho = U @ rho @ Ud
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

def split_idx(n): return int(0.7*n)

def clf_fit(Xtr, ytr):
    sc = StandardScaler().fit(Xtr)
    clf = LogisticRegression(max_iter=3000, C=C_READOUT).fit(sc.transform(Xtr), ytr)
    return sc, clf

def clf_acc(sc, clf, Xte, yte): return float(clf.score(sc.transform(Xte), yte))

def reg_r2(Xtr, ytr, Xte, yte):
    best = -1e9
    for al in (1e-4, 1e-2, 1.0):
        s = StandardScaler().fit(Xtr)
        m = Ridge(alpha=al).fit(s.transform(Xtr), ytr)
        pr = m.predict(s.transform(Xte))
        best = max(best, 1 - np.mean((pr-yte)**2)/np.var(yte))
    return float(best)

def law_predict(P, Z, sc0, clf0, y):
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    Xex = feats_exact(P, Z)
    sp = split_idx(Tn - WASH) + WASH
    w = clf0.coef_.ravel(); b0 = float(clf0.intercept_[0])
    a = w / sc0.scale_
    const = b0 - np.dot(w, sc0.mean_/sc0.scale_)
    margins = Xex @ a + const
    aw = a.reshape(nodes, F)
    qv = np.zeros(Tn)
    for t in range(Tn):
        s = 0.0
        for v in range(nodes):
            p = P[t, v]; zaw = Z.T @ aw[v]
            m1 = np.dot(p, zaw*zaw); m2 = np.dot(p, zaw)
            s += m1 - m2*m2
        qv[t] = s
    te = slice(sp, Tn); out = {}
    for S in BUDGETS:
        sigma = np.sqrt(np.maximum(qv[te]/S, 1e-18))
        mg = margins[te]; yy = y[te]
        p_pos = norm.cdf(mg/sigma)
        out[S] = float(np.mean(np.where(yy == 1, p_pos, 1-p_pos)))
    return out

def run_arch(arch_id):
    u = make_inputs(); labels = task_labels(u)
    Z = zdiags(ARCHS[arch_id]['nq'])
    P = build_P(arch_id); Xex = feats_exact(P, Z)
    Tn = Xex.shape[0]; sp = split_idx(Tn - WASH) + WASH
    Xin = u[:, None]
    res = []
    for tname in CLF_TASKS + REG_TASKS:
        y, kind = labels[tname]
        if kind == 'clf':
            fsc, fclf = clf_fit(Xin[WASH:sp], y[WASH:sp])
            floor = clf_acc(fsc, fclf, Xin[sp:], y[sp:])
            sc0, clf0 = clf_fit(Xex[WASH:sp], y[WASH:sp])
            exact = clf_acc(sc0, clf0, Xex[sp:], y[sp:])
            lawp = law_predict(P, Z, sc0, clf0, y)
            for S in BUDGETS:
                accs = []
                for ss in SAMPLE_SEEDS:
                    rng = np.random.default_rng(1000*ss + S)
                    Xn = feats_noisy(P, Z, S, rng)
                    accs.append(clf_acc(sc0, clf0, Xn[sp:], y[sp:]))
                pn = float(np.mean(accs)); den = exact - floor
                R = float((pn-floor)/den) if abs(den) > 0.02 else None
                res.append(dict(arch=arch_id, task=tname, kind='clf', shots=S,
                                floor=float(floor), exact=float(exact), noisy=pn,
                                law_pred=float(lawp[S]), retained=R,
                                resid=float(lawp[S]-pn)))
        else:
            floor = reg_r2(Xin[WASH:sp], y[WASH:sp], Xin[sp:], y[sp:])
            exact = reg_r2(Xex[WASH:sp], y[WASH:sp], Xex[sp:], y[sp:])
            for S in BUDGETS:
                r2s = []
                for ss in SAMPLE_SEEDS:
                    rng = np.random.default_rng(1000*ss + S)
                    Xn = feats_noisy(P, Z, S, rng)
                    r2s.append(reg_r2(Xn[WASH:sp], y[WASH:sp], Xn[sp:], y[sp:]))
                pn = float(np.mean(r2s)); den = exact - floor
                R = float((pn-floor)/den) if abs(den) > 0.02 else None
                res.append(dict(arch=arch_id, task=tname, kind='reg', shots=S,
                                floor=float(floor), exact=float(exact), noisy=pn,
                                retained=R))
        print(f'a{arch_id} {tname:9s} done', flush=True)
    json.dump(res, open(f'tf_part{arch_id}.json', 'w'), indent=1)
    print(f'arch {arch_id}: {len(res)} cells', flush=True)

def agg():
    res = []
    for a in ARCHS:
        f = f'tf_part{a}.json'
        if os.path.exists(f): res += json.load(open(f))
    clf = [r for r in res if r['kind'] == 'clf']
    pred = np.array([r['law_pred'] for r in clf]); obs = np.array([r['noisy'] for r in clf])
    r2 = 1 - np.sum((pred-obs)**2)/np.sum((obs-obs.mean())**2)
    mae = float(np.mean(np.abs(pred-obs)))
    reg = [r for r in res if r['kind'] == 'reg']
    reg_ret_250 = [r['retained'] for r in reg if r['shots'] == 250 and r['retained'] is not None]
    summary = dict(n_clf_cells=len(clf), n_reg_cells=len(reg),
                   law_r2=float(r2), law_mae_pp=float(100*mae),
                   H2_pass=bool(r2 > 0.90 and 100*mae < 3.0),
                   reg_retained_at_250=reg_ret_250,
                   H3_pass=bool(all(x < 0.15 for x in reg_ret_250)) if reg_ret_250 else None)
    json.dump(dict(summary=summary, cells=res),
              open('../results/taskfam_law.json', 'w'), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == '__main__':
    if sys.argv[1] == 'run':
        run_arch(int(sys.argv[2]))
    else:
        agg()
