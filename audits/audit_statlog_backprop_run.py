#!/usr/bin/env python3
"""Program 2b audit #28 runner: StatLog (Michie/Spiegelhalter/Taylor 1994) Backprop rows.

Reproduces the Backprop (multilayer perceptron) TEST ERROR RATE for two StatLog tables:
  * diabetes         (Table 9.20, 12-fold CV) - published 0.248
  * australian credit (Table 9.3,  10-fold CV) - published 0.154

All pinned choices are pre-registered in audits/AUDIT_statlog1994-backprop-diabetes-australian.md
(commit 28213ee, EMPTY results) BEFORE this script ran:

  PRIMARY  = Pipeline(StandardScaler(), MLPClassifier(random_state=m)) with every other
             MLPClassifier argument at its scikit-learn default (hidden_layer_sizes=(100,),
             relu, adam, alpha=1e-4, lr_init=1e-3, max_iter=200, shuffle=True, tol=1e-4,
             n_iter_no_change=10). Scaler fit on the TRAINING FOLD ONLY (no leakage).
  CV       = KFold(n_splits=12 diabetes / 10 australian, shuffle=True, random_state=m),
             unstratified (the book states a fold count and nothing else).
  ROW VALUE = 100 x mean over folds of the fold test error rate.
  Convergence warnings (max_iter reached) are COUNTED and reported, never suppressed and
  never "fixed" by raising max_iter (that would be moving a defaulted choice after data).

Labelled SENSITIVITY configs (reported, never the verdict):
  unscaled   - bare MLPClassifier defaults, no StandardScaler
  stratified - StratifiedKFold instead of KFold
  onehot     - (australian only) one-hot the 8 integer-coded categorical columns
  impute     - (diabetes only) biologically-impossible zeros -> train-fold median

Chunkable under the 45 s sandbox cap: one (dataset, config, seed) triple per invocation.
Each chunk is fully determined by its arguments, so any chunk reproduces identically
regardless of how the work is split.

Data (md5-pinned, checked before the pre-registration commit):
  diabetes   OpenML id 37 ARFF          md5 3cbaa3e54586aa88cf6aacb4033e4470  (768 rows)
  australian UCI statlog/australian.dat md5 b6fe154b62a8eb00277acec95b608590  (690 rows)

Usage: audit_statlog_backprop_run.py <diabetes|australian> <config> <master_seed> <out_json>
"""
import json
import sys
import hashlib
import warnings

import numpy as np
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning

DIAB = "/tmp/diabetes37.arff"
AUS = "/tmp/aus.dat"
MD5 = {
    "diabetes": "3cbaa3e54586aa88cf6aacb4033e4470",
    "australian": "b6fe154b62a8eb00277acec95b608590",
}
PUBLISHED = {"diabetes": 24.8, "australian": 15.4}   # percentage points (test error)
N_FOLDS = {"diabetes": 12, "australian": 10}
# australian.dat categorical columns (0-indexed), per UCI australian.doc: A1 A4 A5 A6 A8 A9 A11 A12
AUS_CAT = [0, 3, 4, 5, 7, 8, 10, 11]
# diabetes columns where 0 is biologically impossible (glucose, pressure, skinfold, insulin, BMI)
DIAB_ZERO = [1, 2, 3, 4, 5]


def _md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def load(dataset):
    if dataset == "diabetes":
        md5 = _md5(DIAB)
        lines = open(DIAB, "rb").read().decode().splitlines()
        di = next(i for i, l in enumerate(lines) if l.lower().startswith("@data"))
        rows = [l.split(",") for l in lines[di + 1:] if l.strip() and not l.startswith("%")]
        X = np.array([[float(v) for v in r[:8]] for r in rows])
        y = np.array([r[8].strip() for r in rows])
    else:
        md5 = _md5(AUS)
        rows = [l.split() for l in open(AUS).read().splitlines() if l.strip()]
        X = np.array([[float(v) for v in r[:14]] for r in rows])
        y = np.array([int(r[14]) for r in rows])
    assert md5 == MD5[dataset], f"md5 mismatch for {dataset}: {md5}"
    return X, y, md5


def onehot(X, cats):
    """One-hot the given integer-coded columns; levels taken from the FULL file (fixed
    encoding, not fold-dependent) so folds cannot disagree on the column space."""
    cols, cont = [], [j for j in range(X.shape[1]) if j not in cats]
    for j in cats:
        for lev in np.unique(X[:, j]):
            cols.append((X[:, j] == lev).astype(float))
    return np.column_stack([X[:, cont]] + cols) if cols else X[:, cont]


def run(dataset, config, seed):
    X, y, md5 = load(dataset)
    k = N_FOLDS[dataset]

    if config == "onehot":
        assert dataset == "australian"
        X = onehot(X, AUS_CAT)

    scale = config != "unscaled"
    splitter = (StratifiedKFold(n_splits=k, shuffle=True, random_state=seed)
                if config == "stratified"
                else KFold(n_splits=k, shuffle=True, random_state=seed))

    fold_err, n_nonconv, n_iters = [], 0, []
    for tr, te in splitter.split(X, y):
        Xtr, Xte = X[tr].copy(), X[te].copy()

        if config == "impute":                       # diabetes only
            for j in DIAB_ZERO:
                med = np.median(Xtr[Xtr[:, j] != 0, j])   # TRAIN-fold median only
                Xtr[Xtr[:, j] == 0, j] = med
                Xte[Xte[:, j] == 0, j] = med

        if scale:
            sc = StandardScaler().fit(Xtr)           # fit on TRAIN fold only
            Xtr, Xte = sc.transform(Xtr), sc.transform(Xte)

        clf = MLPClassifier(random_state=seed)       # all other args = library defaults
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always", ConvergenceWarning)
            clf.fit(Xtr, y[tr])
            if any(issubclass(x.category, ConvergenceWarning) for x in w):
                n_nonconv += 1
        n_iters.append(int(clf.n_iter_))
        fold_err.append(float(np.mean(clf.predict(Xte) != y[te])))

    err_pp = 100.0 * float(np.mean(fold_err))
    return {
        "dataset": dataset, "config": config, "master_seed": seed, "data_md5": md5,
        "n_folds": k, "n_samples": int(X.shape[0]), "n_features": int(X.shape[1]),
        "published_test_error_pp": PUBLISHED[dataset],
        "reproduced_test_error_pp": err_pp,
        "drift_pp": err_pp - PUBLISHED[dataset],
        "abs_drift_pp": abs(err_pp - PUBLISHED[dataset]),
        "fold_error_rates": fold_err,
        "fold_error_sd_pp": 100.0 * float(np.std(fold_err, ddof=1)),
        "folds_hitting_max_iter": n_nonconv,
        "n_iter_per_fold": n_iters,
        "sklearn_defaults": "hidden_layer_sizes=(100,), relu, adam, alpha=1e-4, "
                            "lr_init=1e-3, max_iter=200, shuffle=True, tol=1e-4, "
                            "n_iter_no_change=10",
    }


if __name__ == "__main__":
    ds, cfg, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    res = run(ds, cfg, seed)
    json.dump(res, open(out, "w"), indent=1)
    print(json.dumps({k: res[k] for k in
                      ("dataset", "config", "master_seed", "reproduced_test_error_pp",
                       "drift_pp", "folds_hitting_max_iter")}))
