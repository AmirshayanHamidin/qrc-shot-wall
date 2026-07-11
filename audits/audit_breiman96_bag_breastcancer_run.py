#!/usr/bin/env python3
"""Audit #26 runner (independent reconstruction from the committed diabetes/iono convention).
Usage: mine.py <master_seed> <iter_start> <iter_end> <out_json>"""
import json, sys, hashlib
import numpy as np
from sklearn.tree import DecisionTreeClassifier

DATA = "/tmp/bcw.data"
MD5 = "52b89051b9bd37a91a54e8570b963719"
N_BOOT = 50
N_FOLDS = 10
N_TEST = 70  # round(0.1*699)

def load(path):
    raw = open(path, "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    rows = [l.split(",") for l in raw.decode().splitlines() if l.strip()]
    X = np.array([[np.nan if v.strip() == "?" else float(v) for v in r[1:10]] for r in rows])
    y = np.array([int(r[10]) for r in rows])  # 2 = benign, 4 = malignant
    return X, y, md5

def candidate_alphas(path):
    a = path.ccp_alphas
    if len(a) <= 1:
        return np.array([0.0])
    mids = np.sqrt(a[:-1] * np.maximum(a[1:], 0))
    return np.concatenate(([0.0], mids))

def best_pruned(Xtr, ytr, Xev, yev, tree_seed):
    base = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1, random_state=tree_seed)
    p = base.cost_complexity_pruning_path(Xtr, ytr)
    cands = candidate_alphas(p)
    best_err, best_a, best_t = None, None, None
    for a in cands:
        t = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1,
                                   random_state=tree_seed, ccp_alpha=a).fit(Xtr, ytr)
        err = float(np.mean(t.predict(Xev) != yev))
        if best_err is None or err <= best_err:
            best_err, best_a, best_t = err, a, t
    return best_t, best_a

def cv_pruned(XL, yL, rng, tree_seed):
    base = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1, random_state=tree_seed)
    p = base.cost_complexity_pruning_path(XL, yL)
    cands = candidate_alphas(p)
    n = len(yL)
    order = rng.permutation(n)
    folds = np.array_split(order, N_FOLDS)
    errs = np.zeros(len(cands))
    for f in folds:
        mask = np.ones(n, bool); mask[f] = False
        Xtr, ytr, Xv, yv = XL[mask], yL[mask], XL[f], yL[f]
        for j, a in enumerate(cands):
            t = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1,
                                       random_state=tree_seed, ccp_alpha=a).fit(Xtr, ytr)
            errs[j] += np.sum(t.predict(Xv) != yv)
    errs /= n
    j = int(np.max(np.where(errs == errs.min())[0]))
    t = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1,
                               random_state=tree_seed, ccp_alpha=cands[j]).fit(XL, yL)
    return t, float(cands[j])

def one_iteration(X, y, master_seed, it):
    seed_i = master_seed * 100000 + it
    rng = np.random.RandomState(seed_i)
    perm = rng.permutation(len(y))
    test_idx, learn_idx = perm[:N_TEST], perm[N_TEST:]
    XT, yT, XL, yL = X[test_idx], y[test_idx], X[learn_idx], y[learn_idx]
    classes = np.unique(y)
    tS, aS = cv_pruned(XL, yL, rng, seed_i)
    eS = float(np.mean(tS.predict(XT) != yT)) * 100.0
    votes = np.zeros((len(yT), len(classes)), int)
    for b in range(N_BOOT):
        bidx = rng.randint(0, len(yL), len(yL))
        tB, _ = best_pruned(XL[bidx], yL[bidx], XL, yL, seed_i)
        pred = tB.predict(XT)
        for ci, c in enumerate(classes):
            votes[:, ci] += (pred == c)
    agg = classes[np.argmax(votes, axis=1)]
    eB = float(np.mean(agg != yT)) * 100.0
    return eS, eB

if __name__ == "__main__":
    ms, i0, i1, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    X, y, md5 = load(DATA)
    assert md5 == MD5, md5
    assert X.shape == (699, 9) and (y == 2).sum() == 458 and (y == 4).sum() == 241
    assert np.isnan(X).sum() == 16 and list(np.unique(np.where(np.isnan(X))[1])) == [5]
    from multiprocessing import Pool
    with Pool(2) as pool:
        pairs = pool.starmap(one_iteration, [(X, y, ms, it) for it in range(i0, i1)])
    res = {"master_seed": ms, "iter_start": i0, "iter_end": i1, "data_md5": md5,
           "e_S": [p[0] for p in pairs], "e_B": [p[1] for p in pairs]}
    json.dump(res, open(out, "w"))
    print(json.dumps({"seed": ms, "chunk": [i0, i1],
                      "mean_e_S": float(np.mean(res["e_S"])), "mean_e_B": float(np.mean(res["e_B"]))}))
