"""
B6 v3 — Self-calibrating measurement-wall law.

Pre-stated hypothesis (frozen before running):
  H-B6v3: Using ONLY a single noisy pilot of S_pilot shots per time step
  (no access to exact distributions), a split-pilot self-calibration —
  half the pilot shots to fit the readout w, the other half to estimate
  debiased margins and plug-in shot-noise variances — predicts the noisy
  accuracy of that readout at unseen budgets S in {250,1000,4000,16000,64000}
  with (a) MAE <= 3 pts and R^2 >= 0.85 over all 150 cells at S_pilot=8000,
  (b) MAE decreasing monotonically in S_pilot in {500,2000,8000}, and
  (c) bagging w over pilot resamples reducing MAE at S_pilot=500.

Variants per (arch, task, S_pilot):
  nosplit    — v2 baseline: same full pilot used for w AND margins (debias)
  split      — w from pilot half A, margins/variances from half B (debias)
  split_bag  — as split, but w = average of 8 bootstrap logistic fits
  gauss_full — POST-HOC v4: full pilot, Gaussian-smoothed predictor
               acc = mean Phi(g_hat / sqrt(sigma_S^2 + v_pilot)), no debias
  gauss_split— POST-HOC v4 with split pilot

Ground truth: accuracy of the SAME frozen readout on fresh multinomial
samples at budget S (3 seeds, mean), eval split only (time points after
WASH, last 30%).

Usage: python3 b6_selfcal.py <arch_id>   -> writes b6_arch<id>.json
"""
import sys, json
import numpy as np
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from qrc_law import make_inputs, task_labels, zdiags, T, WASH

S_PILOTS = (500, 2000, 8000)
BUDGETS = (250, 1000, 4000, 16000, 64000)
TRUTH_SEEDS = (101, 102, 103)
NBAG = 8

def sample_phat(P, shots, rng):
    Tn, nodes, dim = P.shape
    out = np.zeros_like(P)
    for t in range(Tn):
        for v in range(nodes):
            out[t, v] = rng.multinomial(shots, P[t, v]) / shots
    return out

def feats(phat, Z):
    Tn, nodes, dim = phat.shape
    return np.einsum('tvd,fd->tvf', phat, Z).reshape(Tn, nodes * Z.shape[0])

def fit_w(X, y, tr_idx, rng=None, nbag=0):
    sc = StandardScaler().fit(X[tr_idx])
    Xs = sc.transform(X)
    if nbag == 0:
        m = LogisticRegression(C=1.0, max_iter=2000).fit(Xs[tr_idx], y[tr_idx])
        coef, itc = m.coef_[0], m.intercept_[0]
    else:
        coefs, itcs = [], []
        for _ in range(nbag):
            bs = rng.choice(len(tr_idx), len(tr_idx), replace=True)
            idx = tr_idx[bs]
            if len(np.unique(y[idx])) < 2:
                continue
            m = LogisticRegression(C=1.0, max_iter=2000).fit(Xs[idx], y[idx])
            coefs.append(m.coef_[0]); itcs.append(m.intercept_[0])
        coef, itc = np.mean(coefs, axis=0), np.mean(itcs)
    w_raw = coef / sc.scale_
    b_raw = itc - np.sum(coef * sc.mean_ / sc.scale_)
    return w_raw, b_raw

def unit_margin_var(phat, Z, w_raw, ev_idx):
    """Per-shot multinomial variance of w.x at each eval point."""
    Tn, nodes, dim = phat.shape
    F = Z.shape[0]
    var = np.zeros(len(ev_idx))
    for v in range(nodes):
        a = Z.T @ w_raw[v*F:(v+1)*F]
        p = phat[ev_idx, v, :]
        var += p @ (a**2) - (p @ a)**2
    return var

def run(arch_id):
    d = np.load(f'law_arch{arch_id}.npz')
    P, nq = d['P'], int(d['nq'])
    Z = zdiags(nq)
    bits, u = make_inputs()
    labels = {k: v for k, v in task_labels(bits).items() if v[1] == 'clf'}

    idx_all = np.arange(WASH, T)
    split = int(0.7 * len(idx_all))
    tr_idx, ev_idx = idx_all[:split], idx_all[split:]

    truth_feats = {}
    for S in BUDGETS:
        for ss in TRUTH_SEEDS:
            rng = np.random.default_rng(1000 + 7*S % 997 + ss)
            truth_feats[(S, ss)] = feats(sample_phat(P, S, rng), Z)

    pilots = {}
    for sp in S_PILOTS:
        rng = np.random.default_rng(50_000 + sp + 13*arch_id)
        half = sp // 2
        pA = sample_phat(P, half, rng)
        pB = sample_phat(P, half, rng)
        pF = (pA + pB) / 2
        pilots[sp] = dict(pA=pA, pB=pB, pF=pF, half=half)

    results = []
    for tname, (y, kind) in labels.items():
        y = np.asarray(y)
        ysgn = 2*y[ev_idx] - 1
        for sp in S_PILOTS:
            pl = pilots[sp]
            XA, XB, XF = feats(pl['pA'], Z), feats(pl['pB'], Z), feats(pl['pF'], Z)
            rng_bag = np.random.default_rng(777 + sp + arch_id)
            wF = fit_w(XF, y, tr_idx)
            wA = fit_w(XA, y, tr_idx)
            wBag = fit_w(XA, y, tr_idx, rng_bag, NBAG)
            variants = {}
            variants['nosplit']     = (wF, XF, pl['pF'], sp, 'debias')
            variants['split']       = (wA, XB, pl['pB'], pl['half'], 'debias')
            variants['split_bag']   = (wBag, XB, pl['pB'], pl['half'], 'debias')
            variants['gauss_full']  = (wF, XF, pl['pF'], sp, 'gauss')
            variants['gauss_split'] = (wA, XB, pl['pB'], pl['half'], 'gauss')
            for vname, ((w, b), Xm, pm, S_m, mode) in variants.items():
                g_hat = ysgn * (Xm[ev_idx] @ w + b)
                v_unit = unit_margin_var(pm, Z, w, ev_idx)
                v_pilot = v_unit / S_m
                if mode == 'debias':
                    g2 = np.maximum(g_hat**2 - v_pilot, 1e-12)
                    g = np.sign(g_hat) * np.sqrt(g2)
                for S in BUDGETS:
                    sigma2 = np.maximum(v_unit / S, 1e-18)
                    if mode == 'debias':
                        acc_pred = float(np.mean(norm.cdf(g / np.sqrt(sigma2))))
                    else:
                        acc_pred = float(np.mean(norm.cdf(g_hat / np.sqrt(sigma2 + v_pilot))))
                    accs = []
                    for ss in TRUTH_SEEDS:
                        Xf = truth_feats[(S, ss)]
                        accs.append(float(np.mean(ysgn * (Xf[ev_idx] @ w + b) > 0)))
                    acc_true = float(np.mean(accs))
                    results.append(dict(arch=arch_id, task=tname, S_pilot=sp,
                                        variant=vname, shots=S,
                                        acc_pred=acc_pred, acc_true=acc_true))
        print(f'a{arch_id} {tname:10s} done', flush=True)
    json.dump(results, open(f'b6_arch{arch_id}.json', 'w'), indent=1)
    print(f'arch {arch_id}: {len(results)} rows saved')

if __name__ == '__main__':
    run(int(sys.argv[1]))
