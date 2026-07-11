#!/usr/bin/env python3
"""Program 2b confirmatory audit #30 — StatLog (1994) Backprop rows: letters + shuttle.

Reproduces, exactly as pre-registered in audits/AUDIT_statlog1994-backprop-letter-shuttle.md
(commit 1, EMPTY results, landed on the remote before this file existed):

  letters  (Table 9.7,  test error 0.327) : (train,test) = (15000, 5000), file-order split
  shuttle  (Table 9.19, test error 0.43 %): distributed shuttle.trn / shuttle.tst

Primary configuration (identical to audits #28/#29 for cross-audit comparability):
  Pipeline(StandardScaler(), MLPClassifier(random_state=m))   -- all other args library default
  scaler fit on the TRAINING set only.

Convergence failures are COUNTED and REPORTED, never suppressed and never fixed by raising
max_iter (that would move a defaulted choice after seeing data).

Usage:  python3 audit_statlog_backprop3_run.py <dataset> <seed> <config> <out.json>
  dataset : letter | shuttle
  seed    : 0 | 1 | 2          (master seed; seed 0 is the verdict seed)
  config  : primary | noscale | minmax | randsplit | h5
              primary   -- StandardScaler + MLP defaults          (THE VERDICT)
              noscale   -- raw features into MLP defaults         (sensitivity a / secondary C)
              minmax    -- MinMaxScaler instead of StandardScaler (sensitivity c)
              randsplit -- letters only: seeded stratified 15000/5000 split (sensitivity b)
              h5        -- shuttle only: hidden_layer_sizes=(5,)  (sensitivity d)

Data (md5-pinned in the pre-registration):
  letter/letter-recognition.data  6a2d740def5d13ea6096272546f6d41e   (UCI id 59)
  shuttle/shuttle.trn             53cbd0c3ae4986fdf48b0570978b92bc   (UCI id 148)
  shuttle/shuttle.tst             279c252ee3b56ae6016825afd6821ee7
"""
import hashlib
import json
import sys
import time
import warnings

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, StandardScaler

DATA = "/tmp/a30"

PUBLISHED = {"letter": 32.7, "shuttle": 0.43}  # StatLog Table 9.7 / Table 9.19, percentage points

MD5 = {
    "letter/letter-recognition.data": "6a2d740def5d13ea6096272546f6d41e",
    "shuttle/shuttle.trn": "53cbd0c3ae4986fdf48b0570978b92bc",
    "shuttle/shuttle.tst": "279c252ee3b56ae6016825afd6821ee7",
}


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def check_md5(rel):
    got = md5(f"{DATA}/{rel}")
    assert got == MD5[rel], f"md5 mismatch for {rel}: {got} != {MD5[rel]}"
    return got


def load_letter(seed, config):
    check_md5("letter/letter-recognition.data")
    rows = [l.strip().split(",") for l in open(f"{DATA}/letter/letter-recognition.data") if l.strip()]
    assert len(rows) == 20000 and len(rows[0]) == 17
    X = np.array([[int(v) for v in r[1:]] for r in rows], dtype=float)
    y = np.array([r[0] for r in rows])
    assert X.min() == 0 and X.max() == 15 and len(set(y)) == 26
    if config == "randsplit":  # labelled sensitivity check (b), never the verdict
        Xtr, Xte, ytr, yte = train_test_split(
            X, y, train_size=15000, test_size=5000, random_state=seed, stratify=y
        )
    else:  # PRE-REGISTERED PRIMARY: file-order split
        Xtr, Xte, ytr, yte = X[:15000], X[15000:], y[:15000], y[15000:]
    assert Xtr.shape[0] == 15000 and Xte.shape[0] == 5000
    return Xtr, Xte, ytr, yte


def load_shuttle(seed, config):
    check_md5("shuttle/shuttle.trn")
    check_md5("shuttle/shuttle.tst")
    def rd(p):
        rows = [l.split() for l in open(p) if l.strip()]
        a = np.array(rows, dtype=float)
        return a[:, :-1], a[:, -1].astype(int)
    Xtr, ytr = rd(f"{DATA}/shuttle/shuttle.trn")
    Xte, yte = rd(f"{DATA}/shuttle/shuttle.tst")
    assert Xtr.shape == (43500, 9) and Xte.shape == (14500, 9)
    return Xtr, Xte, ytr, yte


def build(config, seed):
    """Every MLPClassifier argument except random_state is left at its library default."""
    kw = {"random_state": seed}
    if config == "h5":  # sensitivity (d): the only hidden count the book ever discloses
        kw["hidden_layer_sizes"] = (5,)
    mlp = MLPClassifier(**kw)
    if config == "noscale":
        return Pipeline([("mlp", mlp)])
    if config == "minmax":
        return Pipeline([("sc", MinMaxScaler()), ("mlp", mlp)])
    return Pipeline([("sc", StandardScaler()), ("mlp", mlp)])  # primary / randsplit / h5


def main():
    dataset, seed, config, out = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    assert dataset in ("letter", "shuttle")
    assert config in ("primary", "noscale", "minmax", "randsplit", "h5")

    Xtr, Xte, ytr, yte = (load_letter if dataset == "letter" else load_shuttle)(seed, config)

    t0 = time.time()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model = build(config, seed).fit(Xtr, ytr)
        n_conv_warn = sum(1 for w in caught if issubclass(w.category, ConvergenceWarning))
    elapsed = time.time() - t0

    err = 100.0 * (1.0 - model.score(Xte, yte))
    pub = PUBLISHED[dataset]
    mlp = model.named_steps["mlp"]

    rec = {
        "audit": 30,
        "dataset": dataset,
        "seed": seed,
        "config": config,
        "published_pp": pub,
        "reproduced_pp": round(err, 4),
        "drift_pp": round(err - pub, 4),
        "abs_drift_pp": round(abs(err - pub), 4),
        "n_train": int(Xtr.shape[0]),
        "n_test": int(Xte.shape[0]),
        "n_features": int(Xtr.shape[1]),
        "n_classes": int(len(set(ytr))),
        "n_iter": int(mlp.n_iter_),
        "max_iter": int(mlp.max_iter),
        "converged": bool(mlp.n_iter_ < mlp.max_iter),
        "n_convergence_warnings": int(n_conv_warn),
        "hidden_layer_sizes": list(mlp.hidden_layer_sizes)
        if isinstance(mlp.hidden_layer_sizes, tuple)
        else [mlp.hidden_layer_sizes],
        "fit_seconds": round(elapsed, 2),
        "sklearn": __import__("sklearn").__version__,
    }
    with open(out, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps(rec))


if __name__ == "__main__":
    main()
