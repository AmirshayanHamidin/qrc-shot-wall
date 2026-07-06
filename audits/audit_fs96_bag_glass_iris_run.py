"""Program 2b confirmatory audit #11 (VAR): Freund & Schapire (1996) Table 2, bagging C4.5
column, glass (25.7) + iris (5.0). Governed by audits/PREREG_DRIFT.md and the
pre-registration in audits/AUDIT_freund-schapire1996-bag-c45-glass-iris.md (commit b358b39,
pushed BEFORE this file existed).

Usage (chunked for the sandbox's 45 s per-process cap):
    python3 audit_fs96_bag_glass_iris_run.py seed <m> <dataset>   # primary row, m in {0,1,2}, dataset glass|iris
    python3 audit_fs96_bag_glass_iris_run.py sens_a <dataset>     # paper-faithful hard simple voting, seed 0
    python3 audit_fs96_bag_glass_iris_run.py sens_b <dataset>     # pure-default base tree (gini, msl=1), seed 0
    python3 audit_fs96_bag_glass_iris_run.py sens_c <dataset>     # unstratified KFold(shuffle=True), seed 0
    python3 audit_fs96_bag_glass_iris_run.py merge                # merge partials -> fs96_bag_glass_iris_raw.json + summary

Data: UCI glass.data md5 2732c9170bf8c483f33da3c58929c067 (214 rows; id + 9 floats + class);
UCI iris.data md5 42615765a885ddf54427f12c34a0a070 (150 rows; 4 floats + species).
Protocol per prereg: per master seed m, 10 runs; run r uses StratifiedKFold(10, shuffle=True,
random_state=1000*m+r); per-run error = pooled misclassified/N; row value = 100 * mean over runs.
Same deterministic per-fold estimator seed as audit #9: fs = 100000*m + 100*r + k.
"""
import sys, json, hashlib, glob
import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier

OUT = "/tmp/run10"
PUB = {"glass": 25.7, "iris": 5.0}
MD5 = {"glass": "2732c9170bf8c483f33da3c58929c067", "iris": "42615765a885ddf54427f12c34a0a070"}
PATH = {"glass": "/tmp/glass.data", "iris": "/tmp/iris.data"}

def load(name):
    raw = open(PATH[name], "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    assert md5 == MD5[name], (name, md5)
    if name == "glass":
        M = np.loadtxt(PATH[name], delimiter=",")
        X, y = M[:, 1:10], M[:, 10].astype(int)
        assert X.shape == (214, 9)
    else:
        rows = [l.strip().split(",") for l in open(PATH[name]) if l.strip()]
        X = np.array([[float(v) for v in r[:4]] for r in rows])
        labels = sorted(set(r[4] for r in rows))
        y = np.array([labels.index(r[4]) for r in rows])
        assert X.shape == (150, 4) and len(labels) == 3
    return X, y, md5

def c45ish_tree(seed):
    # Pinned mapping (prereg, same as audit #9): entropy = sklearn's info-gain criterion
    # (closest to C4.5's gain-ratio family); min_samples_leaf=2 = C4.5's documented default
    # -m 2; everything else library default (NO pruning: ccp_alpha=0.0 -- C4.5's pessimistic
    # pruning has no sklearn counterpart; that gap is rubric point 2).
    return DecisionTreeClassifier(criterion="entropy", min_samples_leaf=2, random_state=seed)

def default_tree(seed):
    return DecisionTreeClassifier(random_state=seed)  # gini, min_samples_leaf=1

def cv_errors(X, y, m, fit_predict, stratified=True):
    """10 runs x 10 folds; per-run pooled error (%)."""
    runs = []
    for r in range(10):
        cls = StratifiedKFold if stratified else KFold
        skf = cls(n_splits=10, shuffle=True, random_state=1000 * m + r)
        wrong = 0
        for k, (tr, te) in enumerate(skf.split(X, y)):
            fs = 100000 * m + 100 * r + k          # deterministic per-fold seed (audit #9 convention)
            pred = fit_predict(X[tr], y[tr], X[te], fs)
            wrong += int((pred != y[te]).sum())
        runs.append(100.0 * wrong / len(y))
    return runs

def fp_bag(Xtr, ytr, Xte, fs, factory=c45ish_tree):
    """Primary: sklearn modern-default bagging (bootstrap size N, soft-vote aggregation)."""
    clf = BaggingClassifier(estimator=factory(fs), n_estimators=100, random_state=fs)
    clf.fit(Xtr, ytr)
    return clf.predict(Xte)

def fp_bag_hardvote(Xtr, ytr, Xte, fs, T=100):
    """Sensitivity (a): paper-faithful Breiman bagging -- T=100 bootstrap samples of size N
    drawn uniformly with replacement, combined by simple (hard majority) voting over
    predicted labels; ties broken toward the lowest class index (argmax-first)."""
    rng = np.random.RandomState(fs)
    n = len(ytr)
    classes = np.unique(ytr)
    votes = np.zeros((len(Xte), len(classes)), dtype=int)
    for t in range(T):
        idx = rng.randint(0, n, n)
        clf = c45ish_tree(fs).fit(Xtr[idx], ytr[idx])
        pred = clf.predict(Xte)
        for ci, c in enumerate(classes):
            votes[:, ci] += (pred == c)
    return classes[np.argmax(votes, axis=1)]

def save(tag, obj):
    with open(f"{OUT}_{tag}.json", "w") as f:
        json.dump(obj, f)
    print(tag, "->", {k: round(np.mean(v), 3) if isinstance(v, list) else v
                      for k, v in obj.items() if k != "runs"})

def main():
    mode = sys.argv[1]
    if mode == "seed":
        m, ds = int(sys.argv[2]), sys.argv[3]
        X, y, md5 = load(ds)
        runs = cv_errors(X, y, m, fp_bag)
        save(f"seed{m}_{ds}", {"mode": "primary", "dataset": ds, "master_seed": m,
                               "md5": md5, "runs": runs, "row_value": float(np.mean(runs))})
    elif mode == "sens_a":
        ds = sys.argv[2]
        X, y, md5 = load(ds)
        runs = cv_errors(X, y, 0, fp_bag_hardvote)
        save(f"sensA_{ds}", {"mode": "sens_a_hardvote", "dataset": ds, "master_seed": 0,
                             "md5": md5, "runs": runs, "row_value": float(np.mean(runs))})
    elif mode == "sens_b":
        ds = sys.argv[2]
        X, y, md5 = load(ds)
        runs = cv_errors(X, y, 0, lambda a, b, c, s: fp_bag(a, b, c, s, factory=default_tree))
        save(f"sensB_{ds}", {"mode": "sens_b_default_tree", "dataset": ds, "master_seed": 0,
                             "md5": md5, "runs": runs, "row_value": float(np.mean(runs))})
    elif mode == "sens_c":
        ds = sys.argv[2]
        X, y, md5 = load(ds)
        runs = cv_errors(X, y, 0, fp_bag, stratified=False)
        save(f"sensC_{ds}", {"mode": "sens_c_unstratified", "dataset": ds, "master_seed": 0,
                             "md5": md5, "runs": runs, "row_value": float(np.mean(runs))})
    elif mode == "merge":
        import sklearn
        parts = {}
        for p in sorted(glob.glob(OUT + "_*.json")):
            tag = p[len(OUT) + 1:-5]
            parts[tag] = json.load(open(p))
        out = {"audit": "freund-schapire1996-bag-c45-glass-iris",
               "prereg_commit": "b358b39", "published": PUB,
               "sklearn": sklearn.__version__, "numpy": np.__version__,
               "parts": parts}
        summary = {}
        for ds in ("glass", "iris"):
            rows = {f"seed{m}": parts[f"seed{m}_{ds}"]["row_value"] for m in (0, 1, 2)}
            drifts = [abs(rows[f"seed{m}"] - PUB[ds]) for m in (0, 1, 2)]
            summary[ds] = {"published": PUB[ds], **{k: round(v, 4) for k, v in rows.items()},
                           "drift_seed0_pp": round(rows["seed0"] - PUB[ds], 4),
                           "std_drift_3seed_pp": round(float(np.mean(drifts)), 4),
                           "sens_a_hardvote": round(parts[f"sensA_{ds}"]["row_value"], 4),
                           "sens_b_default_tree": round(parts[f"sensB_{ds}"]["row_value"], 4),
                           "sens_c_unstratified": round(parts[f"sensC_{ds}"]["row_value"], 4)}
        out["summary"] = summary
        with open("/tmp/fs96_bag_glass_iris_raw.json", "w") as f:
            json.dump(out, f, indent=1)
        print(json.dumps(summary, indent=1))
    else:
        raise SystemExit("unknown mode")

if __name__ == "__main__":
    main()
