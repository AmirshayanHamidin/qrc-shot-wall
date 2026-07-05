"""Program 2 audit #4 reproduction script (VAR rule 3).

Target: Breiman (2001) "Random Forests", Table 2, ionosphere row (Forest-RI).
  Published: Single Input (F=1) 7.5% test error; Selection 7.1% test error.
Pre-registered plan (see audits/AUDIT_breiman2001-rf-ionosphere.md, commit 717ce63):
  100 iterations; each: unstratified random 10% holdout (test_size=0.10 -> 36/315);
  two forests of 100 trees (max_features=1 and 6), oob_score=True, gini, bootstrap;
  Single Input column = mean F=1 test error; Selection column = per-iteration test
  error of the forest with the LOWER OOB error estimate. Primary master seed 0;
  seed sensitivity with master seeds 1, 2.
Chunked to respect the sandbox's 45 s per-process cap:
  python3 audit_rf_ionosphere_run.py fetch
  python3 audit_rf_ionosphere_run.py run <master_seed> <start> <end>
  python3 audit_rf_ionosphere_run.py summarize
"""
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "ionosphere.npz")


def fetch():
    from sklearn.datasets import fetch_openml
    ds = fetch_openml(data_id=59, as_frame=False, parser="liac-arff")
    X = np.asarray(ds.data, dtype=np.float64)
    y = np.asarray(ds.target)
    md5 = hashlib.md5(np.ascontiguousarray(X).tobytes()).hexdigest()
    np.savez(DATA, X=X, y=y)
    classes, counts = np.unique(y, return_counts=True)
    print("shape", X.shape, "classes", dict(zip(classes.tolist(), counts.tolist())),
          "X md5", md5)


def run(master, start, end):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    d = np.load(DATA, allow_pickle=True)
    X, y = d["X"], d["y"]
    out_path = os.path.join(HERE, f"rf_iono_seed{master}.json")
    rows = json.load(open(out_path)) if os.path.exists(out_path) else []
    done = {r["i"] for r in rows}
    for i in range(start, end):
        if i in done:
            continue
        rs = master * 100003 + i
        Xtr, Xte, ytr, yte = train_test_split(
            X, y, test_size=0.10, random_state=rs, shuffle=True, stratify=None)
        errs, oobs = {}, {}
        for F, off in ((1, 1), (6, 2)):
            clf = RandomForestClassifier(
                n_estimators=100, max_features=F, criterion="gini",
                bootstrap=True, oob_score=True, random_state=rs + off, n_jobs=-1)
            clf.fit(Xtr, ytr)
            errs[F] = 1.0 - clf.score(Xte, yte)
            oobs[F] = 1.0 - clf.oob_score_
        sel = 1 if oobs[1] <= oobs[6] else 6  # tie -> F=1 (declared convention)
        rows.append({"i": i, "err_F1": errs[1], "err_F6": errs[6],
                     "oob_F1": oobs[1], "oob_F6": oobs[6],
                     "sel_F": sel, "err_sel": errs[sel]})
    json.dump(sorted(rows, key=lambda r: r["i"]), open(out_path, "w"))
    print(f"seed {master}: {len(rows)} iterations stored")


def summarize():
    import sklearn
    for master in (0, 1, 2):
        p = os.path.join(HERE, f"rf_iono_seed{master}.json")
        if not os.path.exists(p):
            continue
        rows = json.load(open(p))
        e1 = 100 * np.mean([r["err_F1"] for r in rows])
        esel = 100 * np.mean([r["err_sel"] for r in rows])
        e6 = 100 * np.mean([r["err_F6"] for r in rows])
        n6 = sum(r["sel_F"] == 6 for r in rows)
        sem1 = 100 * np.std([r["err_F1"] for r in rows], ddof=1) / np.sqrt(len(rows))
        semsel = 100 * np.std([r["err_sel"] for r in rows], ddof=1) / np.sqrt(len(rows))
        print(f"master seed {master} (n={len(rows)}): "
              f"SingleInput F=1 {e1:.2f}% (SEM {sem1:.2f}) | "
              f"Selection {esel:.2f}% (SEM {semsel:.2f}) | "
              f"F=6 always {e6:.2f}% | F=6 chosen {n6}/{len(rows)}")
    print("sklearn", sklearn.__version__, "numpy", np.__version__,
          "python", sys.version.split()[0])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fetch":
        fetch()
    elif cmd == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        summarize()
