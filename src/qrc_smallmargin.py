"""
B13 - The small-margin regime sweep: does B12's design rule survive leaving the
maximal-headroom regime?  (simulation only; numpy density matrix + qiskit unitary)

CONTEXT. B12 found that information-per-shot (IPS = Sum dmu^2/sigma^2, a noiseless
design-time quantity) is a designable lever: coupling topology moves it 14-56x and it
predicts shot-limited accuracy at Spearman rho=+0.90 @ 250 shots, with the star (hub)
reservoir winning. But B12 ran on the parity family where EVERY topology reaches exact
accuracy 1.00 - the maximal-headroom regime. B11 showed the Mackey-Glass family lives
at the opposite extreme: exact separation is high (0.94-0.98) but on razor-thin margins,
where the fixed readout collapses below the classical floor. B13 repeats the B12 sweep
- same 8 reservoirs (chain/ring/star/all2all x depth 1,2), same design metrics, same
retrained-readout evaluation (qrc_law.perf) - on B11's three Mackey-Glass classification
tasks (updown / accel / prodmed). Nothing else changes.

PRE-REGISTERED HYPOTHESES (stated before running; bars fixed in advance):
  H1 (IPS survives the small-margin regime). Pooled over the 24 (topology x depth x
      task) configurations, Spearman rho(log IPS, retrained noisy accuracy) at S=250
      satisfies rho >= +0.5 with p < 0.01, and the correlation decays with budget as
      accuracy saturates (B12's wall signature).
      Caveat pre-registered: unlike B12, exact accuracy is NOT matched across
      reservoirs here, so rho(log IPS, retention (noisy-floor)/(exact-floor)) is the
      pre-registered secondary endpoint and the exact-accuracy spread is reported.
  H2 (the star rule transfers). Star has the highest topology-mean accuracy at 250
      shots on the Mackey-Glass family, as it did on parity.
  FALSIFIERS: rho < 0.5 or p >= 0.01 at 250 shots -> IPS as a design objective is
      regime-bound to large-margin tasks, and B12's practical advice does not
      generalise - reported as a negative. Star not first -> the topology ranking is
      task-family-dependent; report the new ranking honestly.

Grid: 4 topologies x 2 depths x 3 clf tasks x 5 budgets (250..64000) x 3 sample seeds
      -> 120 cells. Design metrics (IPS, PR, top3, |dmu|) computed noiselessly per
      (reservoir, task) exactly as in B12 (qrc_topology.design_metrics).

Usage:
  python3 qrc_smallmargin.py build <topo> <layers>   -> smtopo_<topo>_L<layers>.npz
  python3 qrc_smallmargin.py eval <topo> <layers>    -> sm_part_<topo>_L<layers>.json
  python3 qrc_smallmargin.py agg                     -> smallmargin_law.json (+summary)
"""
import sys, os, json
import numpy as np
from itertools import combinations

T = 400
WASH = 60
NQ = 6
NODES = 3
K = 4
GAIN = 1.0
U_SEED = 3                     # same reservoir-parameter seed as B12
BUDGETS = (250, 1000, 4000, 16000, 64000)
SAMPLE_SEEDS = (1, 2, 3)
CLF_TASKS = ['updown', 'accel', 'prodmed']
TOPOS = ('chain', 'ring', 'star', 'all2all')
LAYERS = (1, 2)

# ---------- Mackey-Glass input family (identical to qrc_taskfam.py, B11) ----------
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
    ud = np.array([1 if u[t] > u[t-2] else 0 for t in range(T)], float); ud[:2] = 0
    ac = np.array([1 if (u[t]-2*u[t-1]+u[t-2]) > 0 else 0 for t in range(T)], float); ac[:2] = 0
    pr = np.array([(u[t]-ubar)*(u[t-2]-ubar) for t in range(T)]); pr[:2] = 0.0
    med = np.median(pr[WASH:])
    pm = (pr > med).astype(float); pm[:2] = 0
    return {'updown': (ud, 'clf'), 'accel': (ac, 'clf'), 'prodmed': (pm, 'clf')}

# ---------- topologies (identical to qrc_topology.py, B12) ----------
def edges(topo, nq):
    if topo == 'chain':
        return [(i, i+1) for i in range(nq-1)]
    if topo == 'ring':
        return [(i, i+1) for i in range(nq-1)] + [(nq-1, 0)]
    if topo == 'star':
        return [(0, i) for i in range(1, nq)]
    if topo == 'all2all':
        return list(combinations(range(nq), 2))
    raise ValueError(topo)

def build_U(topo, layers, seed):
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator
    r = np.random.default_rng(seed)
    qc = QuantumCircuit(NQ)
    E = edges(topo, NQ)
    for _ in range(layers):
        for q in range(NQ):
            qc.rx(r.uniform(0, 2*np.pi), q)
            qc.rz(r.uniform(0, 2*np.pi), q)
        for (a, b) in E:
            qc.rzz(r.uniform(0, np.pi), a, b)
    return Operator(qc).data

def build(topo, layers):
    dim = 2**NQ
    U = build_U(topo, layers, U_SEED); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * GAIN
    u = make_inputs()

    def reset_inject(rho, uu):
        th = gmax*uu
        psi = np.array([np.cos(th), np.sin(th)])
        r4 = rho.reshape(dim//2, 2, dim//2, 2)
        rest = np.trace(r4, axis1=1, axis2=3)
        return np.einsum('a,b,ij->iajb', psi, psi, rest).reshape(dim, dim)

    P = np.zeros((T, NODES, dim))
    for t in range(K, T):
        rho = np.zeros((dim, dim), complex); rho[0, 0] = 1
        for uu in u[t-K+1:t+1]:
            rho = reset_inject(rho, uu)
            rho = U @ rho @ Ud
        for v in range(NODES):
            if v > 0:
                rho = U @ rho @ Ud
            P[t, v] = np.real(np.diag(rho)).clip(0)
            P[t, v] /= P[t, v].sum()
    np.savez_compressed(f'smtopo_{topo}_L{layers}.npz', P=P)
    print(f'built {topo} L{layers}', flush=True)

# ---------- features / readout (identical to qrc_law.py) ----------
def zdiags(nq):
    dim = 2**nq
    bi = ((np.arange(dim)[:, None] >> np.arange(nq)[None, :]) & 1)
    z1 = [1-2*bi[:, i].astype(float) for i in range(nq)]
    z2 = [(1-2*bi[:, i])*(1-2*bi[:, j]) for i, j in combinations(range(nq), 2)]
    return np.array(z1 + z2)

def feats_from_P(P, Z, shots, rng=None):
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
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    Xs, ys = X[WASH:], y[WASH:]
    split = int(0.7*len(ys))
    best = -1e9
    for C in (0.1, 1, 10, 100):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, C=C))
        m.fit(Xs[:split], ys[:split])
        best = max(best, m.score(Xs[split:], ys[split:]))
    return best

# ---------- design metrics (identical to qrc_topology.py) ----------
def design_metrics(Fex, y):
    X = Fex[WASH:]; yy = y[WASH:]
    mu1 = X[yy == 1].mean(0); mu0 = X[yy == 0].mean(0)
    dmu = mu1 - mu0
    sig2 = np.clip(1.0 - (X**2).mean(0), 1e-6, None)
    ips = float(np.sum(dmu**2 / sig2))
    w = dmu**2
    pr = float((w.sum()**2) / np.sum(w**2)) if np.sum(w**2) > 0 else float(len(w))
    order = np.sort(w)[::-1]
    top3 = float(order[:3].sum() / w.sum()) if w.sum() > 0 else 0.0
    return ips, pr, top3, float(np.linalg.norm(dmu))

# ---------- evaluation ----------
def evaluate(topo, L):
    u = make_inputs()
    labels = task_labels(u)
    Z = zdiags(NQ)
    P = np.load(f'smtopo_{topo}_L{L}.npz')['P']
    Fex = feats_from_P(P, Z, 0)
    Xin = u[:, None]
    results = []
    for tname in CLF_TASKS:
        y, kind = labels[tname]
        ips, pr, top3, dnorm = design_metrics(Fex, y)
        floor = perf(Xin, y, kind, K)
        pex = perf(Fex, y, kind, K)
        for S in BUDGETS:
            accs = []
            for ss in SAMPLE_SEEDS:
                rng = np.random.default_rng(ss)
                Fn = feats_from_P(P, Z, S, rng)
                accs.append(perf(Fn, y, kind, K))
            pn = float(np.mean(accs))
            denom = pex - floor
            R = float((pn - floor)/denom) if abs(denom) > 0.02 else None
            results.append(dict(topo=topo, layers=L, task=tname, shots=S,
                                ips=ips, pr=pr, top3=top3, dnorm=dnorm,
                                floor=float(floor), exact=float(pex),
                                noisy=pn, retained=R))
        print(f'{topo:8s} L{L} {tname:8s} IPS={ips:8.3f} PR={pr:5.2f} '
              f'floor={floor:.3f} exact={pex:.3f}', flush=True)
    json.dump(results, open(f'sm_part_{topo}_L{L}.json', 'w'), indent=1)
    print(f'{len(results)} cells saved', flush=True)

# ---------- aggregation + hypothesis verdicts ----------
def agg():
    from scipy.stats import spearmanr
    cells = []
    for topo in TOPOS:
        for L in LAYERS:
            f = f'sm_part_{topo}_L{L}.json'
            if os.path.exists(f):
                cells += json.load(open(f))
    corr = {}
    for S in BUDGETS:
        cs = [c for c in cells if c['shots'] == S]
        li = np.log([c['ips'] for c in cs])
        acc = [c['noisy'] for c in cs]
        rho, p = spearmanr(li, acc)
        # secondary: retention (skip None)
        rs = [(np.log(c['ips']), c['retained']) for c in cs if c['retained'] is not None]
        rho_r, p_r = spearmanr([x[0] for x in rs], [x[1] for x in rs]) if len(rs) > 4 else (None, None)
        # PR check (B12's falsified H2, re-tested out of regime)
        rho_pr, p_pr = spearmanr([c['pr'] for c in cs], acc)
        corr[S] = dict(rho_ips=float(rho), p_ips=float(p),
                       rho_ret=None if rho_r is None else float(rho_r),
                       p_ret=None if p_r is None else float(p_r),
                       rho_pr=float(rho_pr), p_pr=float(p_pr), n=len(cs))
    rank = {}
    for topo in TOPOS:
        cs = [c['noisy'] for c in cells if c['shots'] == 250 and c['topo'] == topo]
        ex = [c['exact'] for c in cells if c['shots'] == 250 and c['topo'] == topo]
        ip = [c['ips'] for c in cells if c['shots'] == 250 and c['topo'] == topo]
        rank[topo] = dict(acc250=float(np.mean(cs)), exact=float(np.mean(ex)),
                          mean_ips=float(np.mean(ip)))
    exacts = [c['exact'] for c in cells if c['shots'] == 250]
    h1 = bool(corr[250]['rho_ips'] >= 0.5 and corr[250]['p_ips'] < 0.01)
    star_first = max(rank, key=lambda t: rank[t]['acc250']) == 'star'
    ipsvals = {}
    for tname in CLF_TASKS:
        v = [c['ips'] for c in cells if c['shots'] == 250 and c['task'] == tname]
        ipsvals[tname] = dict(min=float(np.min(v)), max=float(np.max(v)),
                              ratio=float(np.max(v)/np.min(v)))
    summary = dict(n_cells=len(cells), correlations=corr, ranking=rank,
                   exact_spread=dict(min=float(np.min(exacts)), max=float(np.max(exacts)),
                                     std=float(np.std(exacts))),
                   ips_range_by_task=ipsvals,
                   H1_pass=h1, H2_star_first=bool(star_first))
    json.dump(dict(summary=summary, cells=cells),
              open('smallmargin_law.json', 'w'), indent=1)
    print(json.dumps(summary, indent=1))

if __name__ == '__main__':
    if sys.argv[1] == 'build':
        build(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == 'eval':
        evaluate(sys.argv[2], int(sys.argv[3]))
    else:
        agg()
