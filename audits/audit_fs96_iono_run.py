#!/usr/bin/env python3
"""Program 2b audit #16 runner: F&S 1996 Table 2, ionosphere row, C4.5/boost/bag columns.

Usage (chunked under the 45 s cap; one mode x master seed per call):
    python3 audit_fs96_iono_run.py tree <m>     # C4.5-alone column, master seed m
    python3 audit_fs96_iono_run.py boost <m>    # AdaBoost SAMME reweighting (library default route)
    python3 audit_fs96_iono_run.py bag <m>      # BaggingClassifier default (soft vote)
    python3 audit_fs96_iono_run.py sens_a       # paper-faithful: M1-resampling boost + hard-vote bag, seed 0
    python3 audit_fs96_iono_run.py sens_b <mode> # pure-default base tree (gini, msl=1), seed 0
    python3 audit_fs96_iono_run.py sens_c <mode> # unstratified KFold(shuffle), seed 0

Protocol per prereg: per master seed m, 10 runs; run r uses StratifiedKFold(10, shuffle=True,
random_state=1000*m+r); per-run error = pooled misclassified/351; row value = 100 x mean(10 runs).
Per-fold estimator seed fs = 100000*m + 100*r + k (identical to audits #9/#11).
"""
import sys, json, hashlib
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier

DATA = "/tmp/ionosphere.data"
MD5 = "85649e5fb5b15fb9dab726c400be61fe"

def load():
    raw = open(DATA, "rb").read()
    assert hashlib.md5(raw).hexdigest() == MD5, "ionosphere.data md5 mismatch"
    rows = [l.split(",") for l in raw.decode().strip().split("\n")]
    X = np.array([[float(v) for v in r[:-1]] for r in rows])
    y = np.array([1 if r[-1] == "g" else 0 for r in rows])
    assert X.shape == (351, 34) and y.sum() == 225
    return X, y

def c45_tree(seed):
    return DecisionTreeClassifier(criterion="entropy", min_samples_leaf=2, random_state=seed)

def default_tree(seed):
    return DecisionTreeClassifier(random_state=seed)  # gini, min_samples_leaf=1

def make_clf(mode, factory, fs):
    if mode == "tree":
        return factory(fs)
    if mode == "boost":
        return AdaBoostClassifier(estimator=factory(fs), n_estimators=100, random_state=fs)
    if mode == "bag":
        return BaggingClassifier(estimator=factory(fs), n_estimators=100, random_state=fs)
    raise ValueError(mode)

def boost_m1_resample(Xtr, ytr, Xte, fs, factory=c45_tree, T=100):
    """Paper-faithful AdaBoost.M1 with resampling (F&S 1996 Fig. 1), as in audit #9 sens_a."""
    rng = np.random.RandomState(fs)
    n = len(ytr); D = np.full(n, 1.0 / n)
    hyps, betas = [], []
    for t in range(T):
        idx = rng.choice(n, size=n, replace=True, p=D)
        h = factory(fs * 1000 + t).fit(Xtr[idx], ytr[idx])
        pred = h.predict(Xtr)
        eps = float(D[pred != ytr].sum())
        if eps >= 0.5:
            break
        if eps == 0.0:
            hyps.append(h); betas.append(1e-10); break
        beta = eps / (1.0 - eps)
        hyps.append(h); betas.append(beta)
        D = D * np.where(pred == ytr, beta, 1.0)
        D = D / D.sum()
    votes = np.zeros((len(Xte), 2))
    for h, b in zip(hyps, betas):
        w = np.log(1.0 / b)
        p = h.predict(Xte)
        for c in (0, 1):
            votes[:, c] += w * (p == c)
    return votes.argmax(axis=1), len(hyps)

def bag_hard_vote(Xtr, ytr, Xte, fs, factory=c45_tree, T=100):
    rng = np.random.RandomState(fs)
    n = len(ytr)
    votes = np.zeros((len(Xte), 2))
    for t in range(T):
        idx = rng.choice(n, size=n, replace=True)
        h = factory(fs * 1000 + t).fit(Xtr[idx], ytr[idx])
        p = h.predict(Xte)
        for c in (0, 1):
            votes[:, c] += (p == c)
    return votes.argmax(axis=1)

def run_master(mode, m, factory=c45_tree, stratified=True, special=None, runs=range(10)):
    X, y = load()
    per_run = []
    for r in runs:
        cls = StratifiedKFold if stratified else KFold
        cv = cls(n_splits=10, shuffle=True, random_state=1000 * m + r)
        wrong = 0
        for k, (tr, te) in enumerate(cv.split(X, y)):
            fs = 100000 * m + 100 * r + k
            if special == "m1":
                pred, _ = boost_m1_resample(X[tr], y[tr], X[te], fs, factory)
            elif special == "hardbag":
                pred = bag_hard_vote(X[tr], y[tr], X[te], fs, factory)
            else:
                clf = make_clf(mode, factory, fs).fit(X[tr], y[tr])
                pred = clf.predict(X[te])
            wrong += int((pred != y[te]).sum())
        per_run.append(100.0 * wrong / len(y))
    return per_run

if __name__ == "__main__":
    what = sys.argv[1]
    out = {"what": what}
    import sklearn
    out["versions"] = {"sklearn": sklearn.__version__, "numpy": np.__version__}
    if what in ("tree", "boost", "bag"):
        m = int(sys.argv[2])
        runs = range(int(sys.argv[3]), int(sys.argv[4]) + 1) if len(sys.argv) > 4 else range(10)
        pr = run_master(what, m, runs=runs)
        out.update(master_seed=m, runs=[runs[0], runs[-1]], per_run=pr,
                   chunk_mean=float(np.mean(pr)))
    elif what == "sens_a":
        pr_b = run_master("boost", 0, special="m1")
        pr_g = run_master("bag", 0, special="hardbag")
        out.update(master_seed=0, boost_m1_resample=dict(per_run=pr_b, row_error=float(np.mean(pr_b))),
                   bag_hard_vote=dict(per_run=pr_g, row_error=float(np.mean(pr_g))))
    elif what == "sens_b":
        mode = sys.argv[2]
        pr = run_master(mode, 0, factory=default_tree)
        out.update(master_seed=0, mode=mode, per_run=pr, row_error=float(np.mean(pr)))
    elif what == "sens_c":
        mode = sys.argv[2]
        pr = run_master(mode, 0, stratified=False)
        out.update(master_seed=0, mode=mode, per_run=pr, row_error=float(np.mean(pr)))
    print(json.dumps(out))
