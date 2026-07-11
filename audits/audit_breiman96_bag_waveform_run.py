#!/usr/bin/env python3
"""Program 2b audit #27 runner — Breiman (1996) Table 2, waveform rows e_S + e_B.

Pinned convention: byte-identical to the committed Breiman-1996 family lineage
(audit_breiman96_bag_iono_run.py -> _diabetes_ -> _breastcancer_), except where the
simulated dataset forces a choice, exactly as pinned in the pre-registration
(audits/AUDIT_breiman1996-bagging-cart-waveform.md, commit b7af1a5f):

- Generator: faithful numpy port of the pinned waveform.c model (md5
  0b5ed5efdc3200c95f959938b9bae15f) at FULL precision: 21 attributes, three
  triangular base waves h(i) = max(6 - |i - peak|, 0) with 0-indexed peaks
  h1@6, h2@14, h3@10; class c ~ Uniform{0,1,2} i.i.d.; class->pair mapping
  0->(h1,h2), 1->(h1,h3), 2->(h2,h3); u ~ U(0,1) continuous; x = u*h_a +
  (1-u)*h_b + N(0,1) per attribute. No u-quantization, no 2-dp rounding
  (those are sensitivity probes only, not this registered pipeline).
- Per iteration: 1800 fresh cases, iteration RNG call order pinned:
  classes, then u vector, then noise matrix. L = first 300, T = remaining 1500.
- Row A (e_S): 10-fold CV cost-complexity pruning on L (CV fold permutation is
  the iteration RNG's next draw after generation), min-error, ties -> larger alpha.
- Row B (e_B): 50 bootstrap replicates, each tree's best pruned subtree selected
  on the ORIGINAL L (Section 4.3), plurality vote, ties -> lowest class label.
- gini, min_samples_leaf=1; alpha candidates = geometric midpoints of the
  pruning path plus 0.
- seed_i = master_seed*100000 + iteration_index; master seeds 0,1,2; 100
  iterations each; any [start,end) chunking reproduces identically.

Usage: audit_breiman96_bag_waveform_run.py <master_seed> <iter_start> <iter_end> <out_json>
"""
import json, sys
import numpy as np
from sklearn.tree import DecisionTreeClassifier

N_GEN = 1800
N_LEARN = 300
N_BOOT = 50
N_FOLDS = 10
IDX = np.arange(21)
H1 = np.maximum(6 - np.abs(IDX - 6), 0).astype(float)
H2 = np.maximum(6 - np.abs(IDX - 14), 0).astype(float)
H3 = np.maximum(6 - np.abs(IDX - 10), 0).astype(float)
WAVE_A = np.stack([H1, H1, H2])  # class -> first wave of the pair
WAVE_B = np.stack([H2, H3, H3])  # class -> second wave of the pair


def generate(rng, n=N_GEN):
    cls = rng.randint(0, 3, n)          # 1) classes
    u = rng.rand(n)                     # 2) mixing weights, continuous U(0,1)
    noise = rng.randn(n, 21)            # 3) noise matrix
    X = u[:, None] * WAVE_A[cls] + (1.0 - u[:, None]) * WAVE_B[cls] + noise
    return X, cls


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


def one_iteration(master_seed, it):
    seed_i = master_seed * 100000 + it
    rng = np.random.RandomState(seed_i)
    X, y = generate(rng)                          # pinned call order inside
    XL, yL = X[:N_LEARN], y[:N_LEARN]             # L = first 300
    XT, yT = X[N_LEARN:], y[N_LEARN:]             # T = remaining 1500
    classes = np.unique(y)                        # [0,1,2]; argmax ties -> lowest label
    tS, aS = cv_pruned(XL, yL, rng, seed_i)       # CV perm = next rng draw
    eS = float(np.mean(tS.predict(XT) != yT)) * 100.0
    votes = np.zeros((len(yT), len(classes)), int)
    for b in range(N_BOOT):
        bidx = rng.randint(0, len(yL), len(yL))
        tB, _ = best_pruned(XL[bidx], yL[bidx], XL, yL, seed_i)  # prune on ORIGINAL L
        pred = tB.predict(XT)
        for ci, c in enumerate(classes):
            votes[:, ci] += (pred == c)
    agg = classes[np.argmax(votes, axis=1)]
    eB = float(np.mean(agg != yT)) * 100.0
    return eS, eB


if __name__ == "__main__":
    ms, i0, i1, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    # generator self-check (deterministic, independent of iteration seeds)
    _rng = np.random.RandomState(12345)
    _X, _y = generate(_rng, 6)
    assert _X.shape == (6, 21) and set(np.unique(_y)) <= {0, 1, 2}
    assert H1[6] == 6 and H2[14] == 6 and H3[10] == 6 and H1[0] == 0 and H1[12] == 0
    from multiprocessing import Pool
    with Pool(2) as pool:
        pairs = pool.starmap(one_iteration, [(ms, it) for it in range(i0, i1)])
    res = {"master_seed": ms, "iter_start": i0, "iter_end": i1,
           "e_S": [p[0] for p in pairs], "e_B": [p[1] for p in pairs]}
    json.dump(res, open(out, "w"))
    print(json.dumps({"seed": ms, "chunk": [i0, i1],
                      "mean_e_S": float(np.mean(res["e_S"])), "mean_e_B": float(np.mean(res["e_B"]))}))
