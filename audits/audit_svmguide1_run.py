#!/usr/bin/env python3
"""Program 2b confirmatory audit #3: Hsu, Chang & Lin, "A Practical Guide to
Support Vector Classification", Appendix A.1 (svmguide1).

Pre-registered in audits/AUDIT_hsu2003-svmguide1-svc.md (commit 098cc566) BEFORE
this script ran. Reproduces the three printed accuracies:
  A  unscaled,  LIBSVM defaults (C=1, gamma=1/num_features)  -> published 66.925
  B  scaled [-1,1] (train ranges), same defaults             -> published 96.15
  C  scaled [-1,1], C=2 gamma=2                              -> published 96.875

Data: svmguide1 / svmguide1.t from the LIBSVM datasets page
(https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/binary/).
MD5 train 894768696209cc3a81c2dcd5589ac67a, test 1e1942c9361598fee3ed1d540e4f627a.

The pipeline is fully deterministic (fixed split, deterministic dual solver);
per PREREG_DRIFT.md it is nevertheless executed under master seeds 0, 1, 2 and
the standardized drift is the 3-run mean |reproduced - published| in pp.

CPU only. Runtime ~seconds. Usage: python3 audit_svmguide1_run.py <train> <test> <out.json>
"""
import hashlib, json, sys, time

import numpy as np
import scipy, sklearn
from sklearn.datasets import load_svmlight_file
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVC

PUBLISHED = {"A_unscaled_default": 66.925, "B_scaled_default": 96.15, "C_scaled_c2_g2": 96.875}


def run_once(seed, Xtr, ytr, Xte, yte):
    """One full replicate. `seed` is threaded per PREREG_DRIFT.md;
    no component here accepts randomness, so replicates are procedural."""
    rng = np.random.RandomState(seed)  # noqa: F841  (declared, unused: no stochastic API)
    out = {}

    # A - original sets, default parameters (LIBSVM: C=1, gamma=1/num_features)
    a = SVC(kernel="rbf", C=1.0, gamma="auto", tol=1e-3, shrinking=True, cache_size=200)
    a.fit(Xtr, ytr)
    out["A_unscaled_default"] = 100.0 * float((a.predict(Xte) == yte).mean())

    # svm-scale -l -1 -u 1 -s range1 train ; svm-scale -r range1 test
    sc = MinMaxScaler(feature_range=(-1, 1)).fit(Xtr)
    Xtr_s, Xte_s = sc.transform(Xtr), sc.transform(Xte)

    # B - scaled sets, default parameters
    b = SVC(kernel="rbf", C=1.0, gamma="auto", tol=1e-3, shrinking=True, cache_size=200)
    b.fit(Xtr_s, ytr)
    out["B_scaled_default"] = 100.0 * float((b.predict(Xte_s) == yte).mean())

    # C - scaled sets, C=2 gamma=2
    c = SVC(kernel="rbf", C=2.0, gamma=2.0, tol=1e-3, shrinking=True, cache_size=200)
    c.fit(Xtr_s, ytr)
    out["C_scaled_c2_g2"] = 100.0 * float((c.predict(Xte_s) == yte).mean())
    return out


def main():
    train_path, test_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    md5 = {p: hashlib.md5(open(p, "rb").read()).hexdigest() for p in (train_path, test_path)}

    Xtr, ytr = load_svmlight_file(train_path)
    Xte, yte = load_svmlight_file(test_path, n_features=Xtr.shape[1])
    Xtr, Xte = Xtr.toarray(), Xte.toarray()

    res = {
        "meta": {
            "python": sys.version.split()[0], "sklearn": sklearn.__version__,
            "numpy": np.__version__, "scipy": scipy.__version__,
            "train_shape": list(Xtr.shape), "test_shape": list(Xte.shape),
            "train_classes": {str(k): int(v) for k, v in zip(*np.unique(ytr, return_counts=True))},
            "test_classes": {str(k): int(v) for k, v in zip(*np.unique(yte, return_counts=True))},
            "md5": md5, "published": PUBLISHED, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        "seeds": {},
    }
    for seed in (0, 1, 2):
        res["seeds"][str(seed)] = run_once(seed, Xtr, ytr, Xte, yte)

    drift = {}
    for col, pub in PUBLISHED.items():
        vals = [res["seeds"][str(s)][col] for s in (0, 1, 2)]
        drift[col] = {
            "published": pub, "reproduced_seed0": vals[0], "all_seeds": vals,
            "mean_abs_drift_pp": float(np.mean([abs(v - pub) for v in vals])),
        }
    res["drift"] = drift
    json.dump(res, open(out_path, "w"), indent=1)
    for col, d in drift.items():
        print(f"{col}: published {d['published']} -> seed0 {d['reproduced_seed0']:.4f} "
              f"(3-seed mean |drift| {d['mean_abs_drift_pp']:.4f} pp)")


if __name__ == "__main__":
    main()
