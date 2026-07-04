"""AUDIT (2026-07-04): reconstruct the B5 probit prediction from the formula
documented in results/RESULTS_LAW.md, since the pred-generator script is not
in src/. pred = mean_test Phi(y_signed * f(x) / sigma), with
sigma^2 = sum_nodes [sum_j p_j q_j^2 - (p.q)^2]/S, q = Z^T w  (raw feature space).
Readout: StandardScaler+LogisticRegression trained on EXACT features
(best C on test acc, same grid as qrc_law.perf).
Usage: python3 audit_law_theory.py <arch_id>
"""
import sys, json
import numpy as np
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import qrc_law as L

arch_id = int(sys.argv[1])
bits, u = L.make_inputs()
labels = L.task_labels(bits)
d = np.load(f'law_arch{arch_id}.npz')
P, nq, K, nodes = d['P'], int(d['nq']), int(d['K']), int(d['nodes'])
Z = L.zdiags(nq)
F = Z.shape[0]
Fex = L.feats_from_P(P, Z, 0)

out = []
for tname, (y, kind) in labels.items():
    if kind != 'clf':
        continue
    Xs, ys = Fex[L.WASH:], y[L.WASH:]
    split = int(0.7 * len(ys))
    best, bm = -1, None
    for C in (0.1, 1, 10, 100):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=4000, C=C))
        m.fit(Xs[:split], ys[:split])
        s = m.score(Xs[split:], ys[split:])
        if s > best:
            best, bm = s, m
    sc, lr = bm.named_steps['standardscaler'], bm.named_steps['logisticregression']
    w_raw = (lr.coef_[0] / sc.scale_)
    b_raw = lr.intercept_[0] - np.dot(lr.coef_[0], sc.mean_ / sc.scale_)
    # signed decision score on exact test features
    idx_test = np.arange(L.WASH + split, L.T)
    f_ex = Fex[idx_test] @ w_raw + b_raw
    ysgn = 2 * y[idx_test] - 1
    # projected multinomial variance per test sample (per unit 1/S)
    var1 = np.zeros(len(idx_test))
    for i, t in enumerate(idx_test):
        v = 0.0
        for vn in range(nodes):
            q = Z.T @ w_raw[vn * F:(vn + 1) * F]
            p = P[t, vn]
            v += p @ q**2 - (p @ q)**2
        var1[i] = v
    for S in (250, 1000, 4000, 16000, 64000):
        sig = np.sqrt(var1 / S)
        pred = float(np.mean(norm.cdf(ysgn * f_ex / np.maximum(sig, 1e-300))))
        out.append(dict(arch=arch_id, task=tname, shots=S, pred=pred,
                        exact_acc=float(best)))
        print(f'a{arch_id} {tname:10s} S={S:>6} pred={pred:.4f}', flush=True)
json.dump(out, open(f'audit_theory{arch_id}.json', 'w'))
