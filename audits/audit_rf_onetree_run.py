"""Program 2b confirmatory audit #6 reproduction script (VAR rule 3).

Target: Breiman (2001) "Random Forests", Table 2, "One Tree" column.
  Published: ionosphere 12.7% | sonar 31.7%.
Pre-registered plan (see audits/AUDIT_breiman2001-rf-onetree.md, prereg commit):
  Per dataset, 100 iterations; each: unstratified random 10% holdout; two forests
  of 100 trees (max_features=1 and 6), oob_score=True, gini, bootstrap; select the
  forest with the LOWER forest OOB error (tie -> F=1); for the selected forest,
  each tree's error on ITS OWN out-of-bag training instances, averaged over trees
  -> iteration value; column = mean over 100 iterations. Master seed 0 primary;
  seeds 1, 2 sensitivity. The 10% holdout is NOT used by this column.
Chunked to respect the sandbox's 45 s per-process cap:
  python3 audit_rf_onetree_run.py fetch
  python3 audit_rf_onetree_run.py run <iono|sonar> <master_seed> <start> <end>
  python3 audit_rf_onetree_run.py summarize
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = {"iono": {"data_id": 59, "F2": 6, "published": 12.7},
        "sonar": {"data_id": 40, "F2": 6, "published": 31.7}}


def fetch():
    from sklearn.datasets import fetch_openml
    for name, s in SPEC.items():
        path = os.path.join(HERE, f"{name}.npz")
        if os.path.exists(path):
            d = np.load(path, allow_pickle=True)
            X = d["X"]
        else:
            ds = fetch_openml(data_id=s["data_id"], as_frame=False,
                              parser="liac-arff")
            X = np.asarray(ds.data, dtype=np.float64)
            y = np.asarray(ds.target)
            np.savez(path, X=X, y=y)
        md5 = hashlib.md5(np.ascontiguousarray(X).tobytes()).hexdigest()
        y = np.load(path, allow_pickle=True)["y"]
        classes, counts = np.unique(y, return_counts=True)
        print(name, "shape", X.shape,
              dict(zip(classes.tolist(), counts.tolist())), "X md5", md5)


def one_tree_oob_error(clf, Xtr, ytr):
    """Mean per-tree error on each tree's own OOB training instances."""
    from sklearn.ensemble._forest import _generate_sample_indices
    n = Xtr.shape[0]
    errs = []
    for tree in clf.estimators_:
        idx = _generate_sample_indices(tree.random_state, n, n)
        oob = np.setdiff1d(np.arange(n), idx, assume_unique=False)
        if oob.size == 0:
            continue
        pred_codes = tree.predict(Xtr[oob]).astype(int)
        pred = clf.classes_[pred_codes]
        errs.append(float(np.mean(pred != ytr[oob])))
    return float(np.mean(errs)), len(errs)


def run(name, master, start, end):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    s = SPEC[name]
    d = np.load(os.path.join(HERE, f"{name}.npz"), allow_pickle=True)
    X, y = d["X"], d["y"]
    out_path = os.path.join(HERE, f"onetree_{name}_seed{master}.json")
    rows = json.load(open(out_path)) if os.path.exists(out_path) else []
    done = {r["i"] for r in rows}
    for i in range(start, end):
        if i in done:
            continue
        rs = master * 100003 + i
        Xtr, Xte, ytr, yte = train_test_split(
            X, y, test_size=0.10, random_state=rs, shuffle=True, stratify=None)
        forests, oobs = {}, {}
        for F, off in ((1, 1), (s["F2"], 2)):
            clf = RandomForestClassifier(
                n_estimators=100, max_features=F, criterion="gini",
                bootstrap=True, oob_score=True, random_state=rs + off, n_jobs=-1)
            clf.fit(Xtr, ytr)
            forests[F] = clf
            oobs[F] = 1.0 - clf.oob_score_
        sel = 1 if oobs[1] <= oobs[s["F2"]] else s["F2"]  # tie -> F=1 (declared)
        ot, ntrees = one_tree_oob_error(forests[sel], Xtr, ytr)
        rows.append({"i": i, "sel_F": sel, "oob_F1": oobs[1],
                     "oob_F2": oobs[s["F2"]], "one_tree_err": ot,
                     "n_trees_scored": ntrees})
    json.dump(sorted(rows, key=lambda r: r["i"]), open(out_path, "w"))
    print(f"{name} seed {master}: {len(rows)} iterations stored")


def summarize():
    import sklearn
    out = {}
    for name, s in SPEC.items():
        out[name] = {"published": s["published"], "seeds": {}}
        for master in (0, 1, 2):
            p = os.path.join(HERE, f"onetree_{name}_seed{master}.json")
            if not os.path.exists(p):
                continue
            rows = json.load(open(p))
            v = [r["one_tree_err"] for r in rows]
            m = 100 * float(np.mean(v))
            sem = 100 * float(np.std(v, ddof=1) / np.sqrt(len(v)))
            n2 = sum(r["sel_F"] != 1 for r in rows)
            out[name]["seeds"][master] = {
                "n_iter": len(rows), "one_tree_pct": round(m, 4),
                "sem_pct": round(sem, 4), "drift_pp": round(m - s["published"], 4),
                "F2_chosen": n2}
            print(f"{name} seed {master} (n={len(rows)}): OneTree {m:.2f}% "
                  f"(SEM {sem:.2f}) | drift {m - s['published']:+.2f} pp | "
                  f"F2 chosen {n2}/{len(rows)}")
        drifts = [abs(sd["drift_pp"]) for sd in out[name]["seeds"].values()]
        if drifts:
            out[name]["mean_abs_drift_pp_3seed"] = round(float(np.mean(drifts)), 4)
            print(f"{name}: 3-seed mean |drift| = {np.mean(drifts):.2f} pp")
    env = {"python": sys.version.split()[0], "sklearn": sklearn.__version__,
           "numpy": np.__version__}
    out["environment"] = env
    json.dump(out, open(os.path.join(HERE, "rf_onetree_raw_summary.json"), "w"),
              indent=1)
    print(env)


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fetch":
        fetch()
    elif cmd == "run":
        run(sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
    else:
        summarize()
