"""
B5 RESTORATION (2026-07-04) — canonical, committed prediction generator for the
measurement-wall law. Closes finding #3 of the 2026-07-04 B5 audit (AUDITS.md):
"the prediction-generator script is not in the repo."

Formula (as documented in results/RESULTS_LAW.md):
    pred(S) = mean over test samples of  Phi( y_signed * f(x) / sigma(S) )
    sigma^2(S) = (1/S) * Sum_nodes [ Sum_j p_j q_j^2 - (p.q)^2 ],   q = Z^T w

READOUT CONVENTION (now pinned; the audit found this was the unrecoverable
degree of freedom in the original run):
    LogisticRegression on RAW exact features, C = 1e4 (weak regularization),
    max_iter = 20000, trained on the 70% chronological train split; margins
    and predictions evaluated on the 30% test split. The audit's reconstruction
    with this convention matched the published `pred` column to MAE 1.2-1.4 pp;
    the best-C scaled-pipeline convention does NOT reproduce it. From this file
    onward, THIS script is the definition of the law's prediction.

Usage:  python3 qrc_law_predict.py <arch_id>   -> lawpred{arch}.json
"""
import sys, json
import numpy as np
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
import qrc_law as L

C_PRED = 1e4
BUDGETS = (250, 1000, 4000, 16000, 64000)

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
    lr = LogisticRegression(C=C_PRED, max_iter=20000)
    lr.fit(Xs[:split], ys[:split])
    w = lr.coef_[0]
    b = float(lr.intercept_[0])
    idx_test = np.arange(L.WASH + split, L.T)
    f_ex = Fex[idx_test] @ w + b
    ysgn = 2 * y[idx_test] - 1
    exact_acc = float(np.mean((f_ex > 0) == (y[idx_test] == 1)))
    var1 = np.zeros(len(idx_test))
    for i, t in enumerate(idx_test):
        v = 0.0
        for vn in range(nodes):
            q = Z.T @ w[vn * F:(vn + 1) * F]
            p = P[t, vn]
            v += p @ q**2 - (p @ q)**2
        var1[i] = v
    for S in BUDGETS:
        sig = np.sqrt(np.maximum(var1 / S, 1e-300))
        pred = float(np.mean(norm.cdf(ysgn * f_ex / sig)))
        out.append(dict(arch=arch_id, task=tname, shots=S, pred=pred,
                        exact_fixed_acc=exact_acc))
        print(f'a{arch_id} {tname:10s} S={S:>6} pred={pred:.4f}', flush=True)
json.dump(out, open(f'lawpred{arch_id}.json', 'w'), indent=1)
print(f'arch {arch_id}: {len(out)} predictions', flush=True)
