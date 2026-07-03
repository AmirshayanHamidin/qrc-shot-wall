"""
Benchmark 7: Closing the gate-noise residual with a per-node + shot-noise-
covariance correction to the measurement-wall fidelity factor.

Benchmark 6 showed depolarizing gate noise enters the measurement-wall law, to
leading order, as a single scalar effective-shot reduction  S_eff = S * c(gamma)^2,
with c(gamma) = ||mu1-mu0||_gamma / ||mu1-mu0||_0 measured on noiseless features
over the WHOLE concatenated readout vector. It left a ~3 pp residual that grows
with gamma, and named two suspected causes:
  (i)  each virtual node sees a DIFFERENT number of noisy steps, so a single
       scalar contraction over the concatenated vector is only an average, and
  (ii) depolarizing pushes the measurement distribution toward uniform, which
       changes the multinomial shot-noise variance the S_eff trick assumes to be
       gamma-independent.
B7 supplies a parameter-free correction that addresses BOTH and tests whether it
tightens the collapse.

PRE-STATED HYPOTHESIS (H0):
The right design-time scalar is not the raw separation ratio but a per-node,
noise-variance-weighted SNR ratio. For a linear readout the class-discrimination
SNR^2 is additive over independent feature blocks:
    SNR(gamma,S)^2  =  sum_v  S * ||dmu_v(gamma)||^2 / sigma_v^2(gamma)
where node block v has between-class separation dmu_v and mean single-shot
feature variance sigma_v^2 = mean_j (1 - m_{v,j}^2) (exact, noiseless-computable;
m are the exact expectation values). Matching total SNR^2 to the gamma=0 curve
gives a single effective budget
    S_eff_pn = S * [ sum_v ||dmu_v(gamma)||^2 / sigma_v^2(gamma) ]
                  / [ sum_v ||dmu_v(0)||^2     / sigma_v^2(0)     ].
This reduces to B6's S*c^2 when sigma_v is gamma-independent and all nodes
contract equally. Because sigma_v^2 grows with gamma (distributions flatten) the
per-node factor predicts a SMALLER effective budget than B6 -> B6 systematically
over-predicts accuracy at high gamma, and the correction should remove part of
that bias.

  H0: S_eff_pn collapses the gamma>0 curves onto the gamma=0 curve with lower
      MAE than B6's S*c^2; pre-registered success = collapse MAE cut by >30%.
  H1 (falsification): the per-node/covariance factor does NOT beat the scalar
      factor by >30% -> the residual is dominated by something else (readout-
      direction rotation, finite-sample readout training), and the extra
      machinery is not worth it. Reported honestly either way.

We REUSE benchmark 6's measured achievable accuracies (results/gate_noise_law.json
cells: acc, c per arch/task/gamma/shots) so only the *predictor* changes -- an
exact apples-to-apples comparison on identical accuracy data. We recompute the
noiseless per-node quantities here from the same reservoirs.

Simulation only (numpy + qiskit unitary). No hardware, no runtime service.

Run:  python3 qrc_pernode.py <arch_id>   -> pn_part<arch>.json  (per-node noiseless quantities)
      python3 qrc_pernode.py agg          -> pernode_law.json   (collapse comparison)
"""
import sys, json, os, warnings
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator
warnings.filterwarnings('ignore')

T = 400
WASH = 60
CLF_TASKS = ['parity2', 'parity3', 'parity4', 'delay_xor', 'majority3']
GAMMAS = [0.0, 0.02, 0.05, 0.10, 0.15, 0.20]
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

def node_features(P, Z):
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    out = np.zeros((Tn, nodes, F))
    for t in range(Tn):
        for v in range(nodes):
            out[t, v] = Z @ P[t, v]
    return out

def per_node_quantities(arch_id, gamma):
    bits, u = make_inputs(); labels = task_labels(bits)
    nq = ARCHS[arch_id]['nq']; nodes = ARCHS[arch_id]['nodes']
    Z = zdiags(nq)
    P = build_P(arch_id, gamma)
    NF = node_features(P, Z)
    out = {}
    for tname in CLF_TASKS:
        y = labels[tname]
        Xt = NF[WASH:]; yt = y[WASH:]
        sp = int(0.7*len(yt))
        Xtr = Xt[:sp]; ytr = yt[:sp]
        m1 = Xtr[ytr == 1].mean(0)
        m0 = Xtr[ytr == 0].mean(0)
        dmu = m1 - m0
        var_feat = 1.0 - (Xtr.mean(0))**2
        var_feat = np.clip(var_feat, 1e-6, None)
        sep_v = [float(np.linalg.norm(dmu[v])) for v in range(nodes)]
        sig_v = [float(np.mean(var_feat[v])) for v in range(nodes)]
        whole = float(np.linalg.norm(dmu.reshape(-1)))
        out[tname] = dict(sep_v=sep_v, sig_v=sig_v, whole_sep=whole, nodes=nodes)
    return out

def run_arch(arch_id):
    res = {}
    for gamma in GAMMAS:
        res[f'{gamma}'] = per_node_quantities(arch_id, gamma)
        print(f'a{arch_id} g={gamma:.2f} done', flush=True)
    json.dump(dict(arch=arch_id, quantities=res), open(f'pn_part{arch_id}.json', 'w'), indent=1)
    print(f'arch {arch_id} saved', flush=True)

def _interp(pts, Sq):
    xs = [np.log10(s) for s, _ in pts]; ys = [a for _, a in pts]
    x = np.log10(max(Sq, 1e-9))
    if x <= xs[0]: return ys[0]
    if x >= xs[-1]: return ys[-1]
    from bisect import bisect
    i = bisect(xs, x); x0, x1 = xs[i-1], xs[i]; y0, y1 = ys[i-1], ys[i]
    return y0 + (y1-y0)*(x-x0)/(x1-x0)

def agg():
    b6 = json.load(open('gate_noise_law.json'))
    cells = b6['cells']
    Q = {}
    for a in ARCHS:
        f = f'pn_part{a}.json'
        if not os.path.exists(f):
            print(f'MISSING {f}'); return
        d = json.load(open(f))
        Q[d['arch']] = d['quantities']
    curves = {}
    for c in cells:
        if c['gamma'] == 0.0:
            curves.setdefault((c['arch'], c['task']), []).append((c['shots'], c['acc']))
    for k in curves: curves[k].sort()

    def node_snr_sum(arch, task, gamma):
        q = Q[arch][f'{gamma}'][task]
        return sum(sep*sep/sig for sep, sig in zip(q['sep_v'], q['sig_v']))
    def whole_c(arch, task, gamma):
        q0 = Q[arch]['0.0'][task]; qg = Q[arch][f'{gamma}'][task]
        return qg['whole_sep']/q0['whole_sep'] if q0['whole_sep'] > 0 else 1.0
    def scalar_cov_kappa(arch, task, gamma):
        q0 = Q[arch]['0.0'][task]; qg = Q[arch][f'{gamma}'][task]
        s0 = np.mean(q0['sig_v']); sg = np.mean(qg['sig_v'])
        return s0/sg if sg > 0 else 1.0

    preds = {'naive': [], 'b6_scalar': [], 'scalar_cov': [], 'pernode': []}
    obs = []; gtag = []; outcells = []
    for c in cells:
        if c['gamma'] == 0.0: continue
        arch, task, g, S, acc = c['arch'], c['task'], c['gamma'], c['shots'], c['acc']
        key = (arch, task)
        cc = whole_c(arch, task, g); kap = scalar_cov_kappa(arch, task, g)
        r_pn = node_snr_sum(arch, task, g)/node_snr_sum(arch, task, 0.0)
        p_naive = _interp(curves[key], S)
        p_b6 = _interp(curves[key], S*cc*cc)
        p_scov = _interp(curves[key], S*cc*cc*kap)
        p_pn = _interp(curves[key], S*r_pn)
        preds['naive'].append(p_naive); preds['b6_scalar'].append(p_b6)
        preds['scalar_cov'].append(p_scov); preds['pernode'].append(p_pn)
        obs.append(acc); gtag.append(g)
        outcells.append(dict(arch=arch, task=task, gamma=g, shots=S, acc=acc,
                             c=cc, kappa=kap, r_pernode=r_pn,
                             S_b6=S*cc*cc, S_pernode=S*r_pn,
                             pred_b6=p_b6, pred_pernode=p_pn))
    obs = np.array(obs); gtag = np.array(gtag)
    def stats(pred):
        pred = np.array(pred)
        r2 = 1 - np.sum((obs-pred)**2)/np.sum((obs-obs.mean())**2)
        return float(r2), float(np.mean(np.abs(obs-pred)))
    summary = {m: dict(r2=stats(preds[m])[0], mae=stats(preds[m])[1]) for m in preds}
    per_gamma = {}
    for g in GAMMAS:
        if g == 0.0: continue
        mm = gtag == g
        per_gamma[f'{g}'] = {m: float(np.mean(np.abs(obs[mm]-np.array(preds[m])[mm]))) for m in preds}
        per_gamma[f'{g}']['n'] = int(mm.sum())
    imp = (summary['b6_scalar']['mae']-summary['pernode']['mae'])/summary['b6_scalar']['mae']
    imp_cov = (summary['b6_scalar']['mae']-summary['scalar_cov']['mae'])/summary['b6_scalar']['mae']
    out = dict(
        benchmark='B7 per-node + shot-noise-covariance fidelity factor',
        n_pred=len(obs), models=summary,
        pernode_vs_b6_mae_reduction=float(imp),
        scalarcov_vs_b6_mae_reduction=float(imp_cov),
        pre_registered_threshold=0.30, per_gamma=per_gamma,
        note='Reuses B6 achievable accuracies (identical acc data); only the '
             'design-time predictor changes. sigma_v^2 = mean_j(1 - m_j^2) exact '
             'single-shot feature variance; S_eff_pernode = S * '
             'sum_v(sep_v^2/sig_v^2)|gamma / sum_v(sep_v^2/sig_v^2)|0.',
        archs=list(ARCHS.keys()), gammas=GAMMAS, tasks=CLF_TASKS, cells=outcells)
    json.dump(out, open('pernode_law.json', 'w'), indent=1)
    print(json.dumps(dict(models=summary, pernode_vs_b6_mae_reduction=imp,
                          scalarcov_vs_b6_mae_reduction=imp_cov, per_gamma=per_gamma), indent=1))

if __name__ == '__main__':
    if sys.argv[1] == 'agg': agg()
    else: run_arch(int(sys.argv[1]))
