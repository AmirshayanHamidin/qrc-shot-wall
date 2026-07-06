"""Program 2b confirmatory audit #7 — Aeberhard, Coomans & de Vel (1992) wine LOO results.

Reproduces the LDA / QDA / 1NN leave-one-out percent-correct numbers quoted in UCI
wine.names / sklearn load_wine DESCR: LDA 98.9, QDA 99.4, 1NN 96.1 ("z-transformed data",
"all results using the leave-one-out technique").

Pinned plan (see audits/AUDIT_aeberhard1992-wine-loo.md, pre-registered at d60a39f
BEFORE this script ran):
- data: sklearn.datasets.load_wine() (copy of UCI wine.data), 178 x 13
- primary: z-transform (StandardScaler, ddof=0) fit on the FULL dataset
- LOO (178 folds); defaults: LinearDiscriminantAnalysis(), QuadraticDiscriminantAnalysis(),
  KNeighborsClassifier(n_neighbors=1)
- row value = 100 * correct / 178
- sensitivities (labelled, not primary): per-fold scaler; priors=uniform (LDA/QDA); raw features
- master seeds 0/1/2 formally looped; pipeline has no RNG — bit-identity verified, not assumed

CPU only. Runs in seconds; well inside the 45 s cap.
"""
import json, hashlib
import numpy as np
from sklearn.datasets import load_wine
from sklearn.discriminant_analysis import (LinearDiscriminantAnalysis,
                                           QuadraticDiscriminantAnalysis)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import LeaveOneOut
from sklearn.preprocessing import StandardScaler
import sklearn

PUBLISHED = {"LDA": 98.9, "QDA": 99.4, "1NN": 96.1}

def models():
    return {"LDA": LinearDiscriminantAnalysis(),
            "QDA": QuadraticDiscriminantAnalysis(),
            "1NN": KNeighborsClassifier(n_neighbors=1)}

def models_uniform_priors():
    return {"LDA": LinearDiscriminantAnalysis(priors=[1/3]*3),
            "QDA": QuadraticDiscriminantAnalysis(priors=[1/3]*3)}

def loo_percent_correct(X, y, model_factory, scale_mode):
    """scale_mode: 'full' (scaler fit on all rows, pre-registered primary),
    'fold' (scaler fit on the 177 training rows), 'raw' (no scaling)."""
    names = list(model_factory().keys())
    correct = {m: 0 for m in names}
    if scale_mode == "full":
        Xs = StandardScaler().fit_transform(X)
    for tr, te in LeaveOneOut().split(X):
        if scale_mode == "full":
            Xtr, Xte = Xs[tr], Xs[te]
        elif scale_mode == "fold":
            sc = StandardScaler().fit(X[tr])
            Xtr, Xte = sc.transform(X[tr]), sc.transform(X[te])
        else:
            Xtr, Xte = X[tr], X[te]
        for name, mdl in model_factory().items():
            mdl.fit(Xtr, y[tr])
            correct[name] += int(mdl.predict(Xte)[0] == y[te][0])
    n = len(y)
    return {m: 100.0 * c / n for m, c in correct.items()}

def main():
    d = load_wine()
    X, y = d.data, d.target
    data_check = {"shape": list(X.shape),
                  "class_counts": np.bincount(y).tolist(),
                  "X_md5": hashlib.md5(X.tobytes()).hexdigest()}
    out = {"data_check": data_check,
           "sklearn": sklearn.__version__, "numpy": np.__version__,
           "published": PUBLISHED, "seeds": {}}
    for seed in (0, 1, 2):  # no RNG in the pipeline; loop verifies bit-identity
        np.random.seed(seed)
        res = {"primary_full_scaler": loo_percent_correct(X, y, models, "full"),
               "sens_fold_scaler":    loo_percent_correct(X, y, models, "fold"),
               "sens_raw_features":   loo_percent_correct(X, y, models, "raw"),
               "sens_uniform_priors_full": loo_percent_correct(X, y, models_uniform_priors, "full")}
        out["seeds"][str(seed)] = res
    prim = out["seeds"]["0"]["primary_full_scaler"]
    out["drift_pp_primary_seed0"] = {m: round(abs(prim[m] - PUBLISHED[m]), 4) for m in PUBLISHED}
    ident = all(out["seeds"]["0"] == out["seeds"][s] for s in ("1", "2"))
    out["bit_identical_across_seeds"] = ident
    with open("wine_loo_raw.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({k: out[k] for k in ("data_check", "drift_pp_primary_seed0",
                                          "bit_identical_across_seeds")}, indent=1))
    print("primary:", {m: round(v, 4) for m, v in prim.items()})
    for k in ("sens_fold_scaler", "sens_raw_features", "sens_uniform_priors_full"):
        print(k, {m: round(v, 4) for m, v in out["seeds"]["0"][k].items()})

if __name__ == "__main__":
    main()
