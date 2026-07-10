#!/usr/bin/env python3
"""Program 2b audit #24 runner: Breiman (1996) Bagging Predictors, Table 2, diabetes rows.

Dataset swap of the audit #14/#22 runner (audits/audit_breiman96_bag_iono_run.py); the
methodology, pinned choices, and per-iteration seeding are byte-identical to that
committed convention. Reproduces e_S (single CART, 10-fold-CV pruned) and e_B (bagging,
50 bootstrap trees, pruned against the original learning set L per Sec. 4.3, plurality
vote, ties -> lowest class label). 100 iterations of a random 90/10 split; means over
iterations.

Chunkable under the 45-s sandbox cap: per-iteration RNG is seeded as
seed_i = master_seed*100000 + iteration_index, so any [start,end) chunk reproduces
identically regardless of chunking. Pinned choices are pre-registered in the audit file:
gini, min_samples_leaf=1, alpha candidates = geometric midpoints of the pruning path,
min-error selection with ties -> larger alpha, unstratified split, |test|=77, |L_B|=691,
classes encoded by np.unique ('tested_negative' < 'tested_positive').

Data: OpenML id 37 ARFF (Pima; original UCI entry withdrawn), md5-pinned to the same
file audit #19 used (3cbaa3e54586aa88cf6aacb4033e4470).

Usage: audit_breiman96_bag_diabetes_run.py <master_seed> <iter_start> <iter_end> <out_json>
"""
import json, sys, hashlib
import numpy as np
from sklearn.tree import DecisionTreeClassifier

DATA = "/tmp/diabetes37.arff"
MD5 = "3cbaa3e54586aa88cf6aacb4033e4470"
N_BOOT = 50
N_FOLDS = 10
N_TEST = 77  # round(0.1*768)

def load(path):
    raw = open(path, "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    lines = raw.decode().splitlines()
    di = next(i for i, l in enumerate(lines) if l.lower().startswith("@data"))
    rows = [l.split(",") for l in lines[di + 1:] if l.strip() and not l.startswith("%")]
    X = np.array([[float(v) for v in r[:8]] for r in rows])
    y = np.array([r[8].strip() for r in rows])  # tested_negative / tested_positive
    return X, y, md5

def candidate_alphas(path):
    a = path.ccp_alphas
    if len(a) <= 1:
        return np.array([0.0])
    mids = np.sqrt(a[:-1] * np.maximum(a[1:], 0))
    return np.concatenate(([0.0], mids))

def best_pruned(Xtr, ytr, Xev, yev, tree_seed):
    """Grow on (Xtr,ytr); pick ccp_alpha minimising error on (Xev,yev); ties -> larger alpha.
    Returns fitted tree at chosen alpha."""
    base = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1, random_state=tree_seed)
    p = base.cost_complexity_pruning_path(Xtr, ytr)
    cands = candidate_alphas(p)
    best_err, best_a, best_t = None, None, None
    for a in cands:  # ascending; >= keeps larger alpha on ties
        t = DecisionTreeClassifier(criterion="gini", min_samples_leaf=1,
                                   random_state=tree_seed, ccp_alpha=a).fit(Xtr, ytr)
        err = float(np.mean(t.predict(Xev) != yev))
        if best_err is None or err <= best_err:
            best_err, best_a, best_t = err, a, t
    return best_t, best_a

def cv_pruned(XL, yL, rng, tree_seed):
    """CART-style: alpha grid from full-L path; 10-fold CV picks alpha; refit on L."""
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
    j = int(np.max(np.where(errs == errs.min())[0]))  # tie -> larger alpha
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
    # Row A: single tree, 10-fold CV pruning
    tS, aS = cv_pruned(XL, yL, rng, seed_i)
    eS = float(np.mean(tS.predict(XT) != yT)) * 100.0
    # Row B: bagging, 50 bootstrap trees pruned on L (Sec 4.3), plurality vote
    votes = np.zeros((len(yT), len(classes)), int)
    for b in range(N_BOOT):
        bidx = rng.randint(0, len(yL), len(yL))
        tB, _ = best_pruned(XL[bidx], yL[bidx], XL, yL, seed_i)
        pred = tB.predict(XT)
        for ci, c in enumerate(classes):
            votes[:, ci] += (pred == c)
    agg = classes[np.argmax(votes, axis=1)]  # argmax first max -> lowest class label on ties
    eB = float(np.mean(agg != yT)) * 100.0
    return eS, eB

if __name__ == "__main__":
    ms, i0, i1, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    X, y, md5 = load(DATA)
    assert md5 == MD5, md5
    assert X.shape == (768, 8) and (y == "tested_positive").sum() == 268 \
        and (y == "tested_negative").sum() == 500
    from multiprocessing import Pool
    with Pool(2) as pool:  # 2-core sandbox; iterations independently seeded, order preserved
        pairs = pool.starmap(one_iteration, [(X, y, ms, it) for it in range(i0, i1)])
    res = {"master_seed": ms, "iter_start": i0, "iter_end": i1, "data_md5": md5,
           "e_S": [p[0] for p in pairs], "e_B": [p[1] for p in pairs]}
    json.dump(res, open(out, "w"))
    print(json.dumps({"seed": ms, "chunk": [i0, i1],
                      "mean_e_S": float(np.mean(res["e_S"])), "mean_e_B": float(np.mean(res["e_B"]))}))
