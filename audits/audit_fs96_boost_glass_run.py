"""Program 2b confirmatory audit #9 (VAR): Freund & Schapire (1996) Table 2, glass rows,
C4.5 alone (31.7) + boosting C4.5 (22.7). Governed by audits/PREREG_DRIFT.md and the
pre-registration in audits/AUDIT_freund-schapire1996-boost-c45-glass.md (commit c364bac,
pushed BEFORE this file existed).

Usage (chunked for the sandbox's 45 s per-process cap):
    python3 audit_fs96_boost_glass_run.py seed <m>     # primary rows, master seed m in {0,1,2}
    python3 audit_fs96_boost_glass_run.py sens_a       # AdaBoost.M1-with-resampling (paper route), seed 0
    python3 audit_fs96_boost_glass_run.py sens_bc      # default-tree (gini,msl=1) + unstratified KFold, seed 0
    python3 audit_fs96_boost_glass_run.py merge        # merge partials -> fs96_boost_glass_raw.json + summary

Data: UCI glass.data, md5 2732c9170bf8c483f33da3c58929c067 (214 rows; id + 9 floats + class).
Protocol per prereg: per master seed m, 10 runs; run r uses StratifiedKFold(10, shuffle=True,
random_state=1000*m+r); per-run error = pooled misclassified/214; row value = 100 * mean over runs.
"""
import sys, json, hashlib, glob
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier

DATA = "/tmp/glass.data"
OUT = "/tmp/run8"
PUB = {"tree": 31.7, "boost": 22.7}

def load():
    raw = open(DATA, "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    assert md5 == "2732c9170bf8c483f33da3c58929c067", md5
    M = np.loadtxt(DATA, delimiter=",")
    X, y = M[:, 1:10], M[:, 10].astype(int)
    assert X.shape == (214, 9)
    return X, y, md5

def c45ish_tree(seed):
    # Pinned mapping (prereg): entropy = sklearn's info-gain criterion (closest to C4.5's
    # gain-ratio family); min_samples_leaf=2 = C4.5's documented default -m 2; everything
    # else library default (NO pruning: ccp_alpha=0.0 -- C4.5's pessimistic pruning has no
    # sklearn counterpart; that gap is rubric point 2).
    return DecisionTreeClassifier(criterion="entropy", min_samples_leaf=2, random_state=seed)

def default_tree(seed):
    return DecisionTreeClassifier(random_state=seed)  # gini, min_samples_leaf=1

def cv_errors(X, y, m, fit_predict, stratified=True):
    """10 runs x 10 folds; returns per-run pooled error (%) list + per-fold extras."""
    runs, extras = [], []
    for r in range(10):
        cls = StratifiedKFold if stratified else KFold
        skf = cls(n_splits=10, shuffle=True, random_state=1000 * m + r)
        wrong = 0
        for k, (tr, te) in enumerate(skf.split(X, y)):
            fs = 100000 * m + 100 * r + k          # deterministic per-fold seed
            pred, extra = fit_predict(X[tr], y[tr], X[te], fs)
            wrong += int((pred != y[te]).sum())
            if extra is not None:
                extras.append({"run": r, "fold": k, **extra})
        runs.append(100.0 * wrong / len(y))
    return runs, extras

def fp_tree(Xtr, ytr, Xte, fs, factory=c45ish_tree):
    clf = factory(fs).fit(Xtr, ytr)
    return clf.predict(Xte), None

def fp_boost(Xtr, ytr, Xte, fs, factory=c45ish_tree):
    clf = AdaBoostClassifier(estimator=factory(fs), n_estimators=100, random_state=fs)
    clf.fit(Xtr, ytr)
    return clf.predict(Xte), {"n_est": len(clf.estimators_),
                              "first_err": float(clf.estimator_errors_[0])}

def fp_m1_resample(Xtr, ytr, Xte, fs, T=100):
    """Paper-faithful AdaBoost.M1 with resampling (F&S 1996 Fig. 1; C4.5 route used
    resampling because C4.5 expects unweighted samples). Pinned edge rules from prereg:
    stop and vote with committee so far if eps == 0 (add that tree, beta floored 1e-10)
    or eps >= 0.5 (if committee empty, use the single tree unweighted)."""
    rng = np.random.RandomState(fs)
    n = len(ytr)
    D = np.full(n, 1.0 / n)
    committee = []
    for t in range(T):
        idx = rng.choice(n, size=n, replace=True, p=D)
        tree = c45ish_tree(int(rng.randint(2**31 - 1))).fit(Xtr[idx], ytr[idx])
        pred = tree.predict(Xtr)
        eps = float(D[pred != ytr].sum())
        if eps >= 0.5:
            if not committee:
                committee.append((tree, 1.0))
            break
        beta = max(eps / (1.0 - eps), 1e-10)
        committee.append((tree, np.log(1.0 / beta)))
        if eps == 0.0:
            break
        w = D * np.where(pred == ytr, beta, 1.0)
        D = w / w.sum()
    classes = np.unique(ytr)
    votes = np.zeros((len(Xte), len(classes)))
    for tree, a in committee:
        p = tree.predict(Xte)
        for ci, c in enumerate(classes):
            votes[p == c, ci] += a
    return classes[votes.argmax(axis=1)], {"T_used": len(committee)}

def main():
    X, y, md5 = load()
    mode = sys.argv[1]
    if mode == "seed":
        m = int(sys.argv[2])
        tree_runs, _ = cv_errors(X, y, m, fp_tree)
        boost_runs, extras = cv_errors(X, y, m, fp_boost)
        out = {"mode": f"primary_seed{m}", "data_md5": md5,
               "tree_runs": tree_runs, "tree_value": float(np.mean(tree_runs)),
               "boost_runs": boost_runs, "boost_value": float(np.mean(boost_runs)),
               "boost_committee_sizes": extras}
        json.dump(out, open(f"{OUT}/partial_seed{m}.json", "w"), indent=1)
        print(json.dumps({k: out[k] for k in ("tree_value", "boost_value")}),
              "n_est uniq:", sorted({e["n_est"] for e in extras}))
    elif mode == "sens_a":
        runs, extras = cv_errors(X, y, 0, fp_m1_resample)
        out = {"mode": "sens_a_M1_resampling_seed0", "runs": runs,
               "value": float(np.mean(runs)), "T_used": extras}
        json.dump(out, open(f"{OUT}/partial_sens_a.json", "w"), indent=1)
        print(out["value"], "T uniq:", sorted({e["T_used"] for e in extras})[:8])
    elif mode == "sens_bc":
        tr_b, _ = cv_errors(X, y, 0, lambda a,b,c,d: fp_tree(a,b,c,d,default_tree))
        bo_b, ex_b = cv_errors(X, y, 0, lambda a,b,c,d: fp_boost(a,b,c,d,default_tree))
        tr_c, _ = cv_errors(X, y, 0, fp_tree, stratified=False)
        bo_c, ex_c = cv_errors(X, y, 0, fp_boost, stratified=False)
        out = {"mode": "sens_bc_seed0",
               "b_default_tree": {"tree_value": float(np.mean(tr_b)),
                                  "boost_value": float(np.mean(bo_b)),
                                  "boost_n_est": sorted({e["n_est"] for e in ex_b})},
               "c_unstratified": {"tree_value": float(np.mean(tr_c)),
                                  "boost_value": float(np.mean(bo_c)),
                                  "boost_n_est": sorted({e["n_est"] for e in ex_c})}}
        json.dump(out, open(f"{OUT}/partial_sens_bc.json", "w"), indent=1)
        print(json.dumps(out, indent=1))
    elif mode == "merge":
        merged = {"published": PUB, "data_md5": load()[2], "partials": {}}
        for f in sorted(glob.glob(f"{OUT}/partial_*.json")):
            d = json.load(open(f))
            merged["partials"][d["mode"]] = d
        p = merged["partials"]
        tv = [p[f"primary_seed{m}"]["tree_value"] for m in (0, 1, 2)]
        bv = [p[f"primary_seed{m}"]["boost_value"] for m in (0, 1, 2)]
        merged["summary"] = {
            "tree_values_seeds012": tv, "boost_values_seeds012": bv,
            "tree_drift_3seed": float(np.mean([abs(v - PUB["tree"]) for v in tv])),
            "boost_drift_3seed": float(np.mean([abs(v - PUB["boost"]) for v in bv])),
            "tree_drift_seed0": tv[0] - PUB["tree"], "boost_drift_seed0": bv[0] - PUB["boost"]}
        json.dump(merged, open(f"{OUT}/fs96_boost_glass_raw.json", "w"), indent=1)
        print(json.dumps(merged["summary"], indent=1))

if __name__ == "__main__":
    main()
