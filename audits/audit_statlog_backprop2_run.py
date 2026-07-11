#!/usr/bin/env python3
"""Program 2b audit #29 runner: StatLog (Michie/Spiegelhalter/Taylor 1994) Backprop rows.

Reproduces the Backprop (multilayer perceptron) TEST ERROR RATE for two StatLog tables:
  * satimage (Table 9.9, single 4435/2000 train/test split) - published 0.139
  * vehicle  (Table 9.6, 9-fold CV, 846 obs)                - published 0.207

All pinned choices are pre-registered in audits/AUDIT_statlog1994-backprop-satimage-vehicle.md
(commit 9139fa3, EMPTY results) BEFORE this script existed:

  SATIMAGE PRIMARY = Pipeline(StandardScaler(), MLPClassifier(random_state=m)), every
                     MLPClassifier argument at its sklearn default. Fit sat.trn, score sat.tst.
  VEHICLE PRIMARY  = 9-fold CV with the DISTRIBUTED fold assignment (xaa..xai each once as
                     test fold, alphabetical), Pipeline(StandardScaler(),
                     MLPClassifier(hidden_layer_sizes=(5,), random_state=m)) - the (5,)
                     honors the book's disclosed "5 hidden nodes" for this row.
  ROW VALUE = 100 x test error (satimage) / 100 x mean fold test error (vehicle).
  Convergence warnings are COUNTED and reported, never suppressed or "fixed".

Labelled SENSITIVITY configs (reported, never the verdict):
  unscaled - raw features, same estimator (both rows)
  h100     - (vehicle) library-default hidden_layer_sizes=(100,), scaled, distributed folds
  kfold    - (vehicle) KFold(9, shuffle=True, random_state=m) instead of distributed folds

Chunkable under the 45 s sandbox cap: one (dataset, config, seed) triple per invocation.

Data (md5-pinned in the prereg, fetched cache-busted from UCI statlog/):
  sat.trn 2c5ba2900da0183cab2c41fdb279fa5b   sat.tst 02c995991fecc864e809b2c4c42cd983
  xaa..xai 58e47d145a615a66f63d6ebee1464c03 acb3f6058d5c5be32bb6f6ca32a33589
           cfea1bcae46637fc9d809728ad5087d7 04322617a9c210dd628d296ee54747d8
           ee3f88b55a12d910226e25d7a6f4b5f3 ea2c7de08ebadb7210ebd71b4bbd614e
           a5f2d9e088d7093f0e809f98a892dd99 ac7ee8eab9cc5094dbf67565cacafc74
           63dc598be76f165a7526b925249db8a4

Usage: audit_statlog_backprop2_run.py <satimage|vehicle> <config> <master_seed> <out_json>
"""
import json, sys, hashlib, warnings, os
import numpy as np
from sklearn.model_selection import KFold
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.exceptions import ConvergenceWarning

DATA = os.environ.get("AUDIT29_DATA", "/tmp/w")
PUBLISHED = {"satimage": 13.9, "vehicle": 20.7}   # percentage points (test error)
MD5 = {
    "sat.trn": "2c5ba2900da0183cab2c41fdb279fa5b", "sat.tst": "02c995991fecc864e809b2c4c42cd983",
    "xaa.dat": "58e47d145a615a66f63d6ebee1464c03", "xab.dat": "acb3f6058d5c5be32bb6f6ca32a33589",
    "xac.dat": "cfea1bcae46637fc9d809728ad5087d7", "xad.dat": "04322617a9c210dd628d296ee54747d8",
    "xae.dat": "ee3f88b55a12d910226e25d7a6f4b5f3", "xaf.dat": "ea2c7de08ebadb7210ebd71b4bbd614e",
    "xag.dat": "a5f2d9e088d7093f0e809f98a892dd99", "xah.dat": "ac7ee8eab9cc5094dbf67565cacafc74",
    "xai.dat": "63dc598be76f165a7526b925249db8a4",
}

def pinned(fname):
    p = os.path.join(DATA, fname)
    h = hashlib.md5(open(p, "rb").read()).hexdigest()
    assert h == MD5[fname], f"md5 mismatch for {fname}: {h}"
    return p

def load_xy(path):
    rows = [l.split() for l in open(path) if l.strip()]
    X = np.array([[float(v) for v in r[:-1]] for r in rows])
    y = np.array([r[-1] for r in rows])
    return X, y

def make_est(hidden, scaled, seed):
    mlp = MLPClassifier(random_state=seed) if hidden is None else \
          MLPClassifier(hidden_layer_sizes=hidden, random_state=seed)
    return Pipeline([("sc", StandardScaler()), ("mlp", mlp)]) if scaled else mlp

def run(dataset, config, seed):
    out = {"dataset": dataset, "config": config, "master_seed": seed,
           "published": PUBLISHED[dataset], "conv_warnings": 0}
    with warnings.catch_warnings(record=True) as wlist:
        warnings.simplefilter("always", ConvergenceWarning)
        if dataset == "satimage":
            Xtr, ytr = load_xy(pinned("sat.trn")); Xte, yte = load_xy(pinned("sat.tst"))
            hidden = None
            scaled = {"primary": True, "unscaled": False}[config]
            est = make_est(hidden, scaled, seed)
            est.fit(Xtr, ytr)
            err = 100.0 * float(np.mean(est.predict(Xte) != yte))
            out.update(n_train=len(ytr), n_test=len(yte), test_error_pp=err)
        else:
            folds = [load_xy(pinned(f"xa{c}.dat")) for c in "abcdefghi"]
            hidden = {"primary": (5,), "unscaled": (5,), "h100": None, "kfold": (5,)}[config]
            scaled = config != "unscaled"
            fold_errs = []
            if config == "kfold":
                X = np.vstack([f[0] for f in folds]); y = np.concatenate([f[1] for f in folds])
                for tr, te in KFold(n_splits=9, shuffle=True, random_state=seed).split(X):
                    est = make_est(hidden, scaled, seed)
                    est.fit(X[tr], y[tr])
                    fold_errs.append(100.0 * float(np.mean(est.predict(X[te]) != y[te])))
            else:
                for i in range(9):
                    Xte, yte = folds[i]
                    Xtr = np.vstack([folds[j][0] for j in range(9) if j != i])
                    ytr = np.concatenate([folds[j][1] for j in range(9) if j != i])
                    est = make_est(hidden, scaled, seed)
                    est.fit(Xtr, ytr)
                    fold_errs.append(100.0 * float(np.mean(est.predict(Xte) != yte)))
            out.update(fold_errors_pp=fold_errs, test_error_pp=float(np.mean(fold_errs)))
        out["conv_warnings"] = sum(1 for w in wlist if issubclass(w.category, ConvergenceWarning))
    out["drift_pp"] = out["test_error_pp"] - out["published"]
    return out

if __name__ == "__main__":
    dataset, config, seed, out_json = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    res = run(dataset, config, seed)
    with open(out_json, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    print(json.dumps({k: res[k] for k in ("dataset", "config", "master_seed", "test_error_pp", "drift_pp", "conv_warnings")}))
