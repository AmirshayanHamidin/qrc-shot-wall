#!/usr/bin/env python3
"""Program 2b confirmatory audit #10 (VAR run #9): NIST StRD LLS certified R-squared,
Longley + Filip. Pre-registered in audits/AUDIT_nist-strd-lls-longley-filip.md
(commit 4ad15b8) BEFORE this script existed.

Primary route (pinned): float64 design matrix exactly as the stated model
(ones column + raw predictors; Filip: ones + x**k, k=1..10, raw x), solved with
numpy.linalg.lstsq(rcond=None); R2 = 1 - SS_res/SS_tot (intercept model,
total sum corrected for the mean). Deterministic pipeline: executed as 3
independent replicate invocations; bit-identity checked across replicates.

Usage: python3 audit_nist_lls_run.py <replicate_id> <outdir>
Data:  Longley.dat, Filip.dat fetched from itl.nist.gov/div898/strd/lls/data/LINKS/DATA/
"""
import sys, json, hashlib
import numpy as np
import scipy.linalg

CERT = {
    "Longley": {"r2": 0.995479004577296,
                "coef": [-3482258.63459582, 15.0618722713733, -0.358191792925910E-01,
                         -2.02022980381683, -1.03322686717359, -0.511041056535807E-01,
                         1829.15146461355]},
    "Filip":   {"r2": 0.996727416185620,
                "coef": [-1467.48961422980, -2772.17959193342, -2316.37108160893,
                         -1127.97394098372, -354.478233703349, -75.1242017393757,
                         -10.8753180355343, -1.06221498588947, -0.670191154593408E-01,
                         -0.246781078275479E-02, -0.402962525080404E-04]},
}

def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()

def load(path, first, last):
    rows = []
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if first <= i <= last:
                rows.append([float(v) for v in line.split()])
    return np.array(rows, dtype=np.float64)

def r2(y, yhat):
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot

def fit_all(X, y, cert_coef):
    out = {}
    # primary: numpy lstsq (SVD), rcond=None
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    out["primary_numpy_lstsq"] = {"r2": r2(y, X @ b),
        "max_rel_coef_err": float(np.max(np.abs((b - cert_coef) / cert_coef)))}
    # sensitivity a: scipy lstsq (LAPACK gelsd)
    bs = scipy.linalg.lstsq(X, y, lapack_driver="gelsd")[0]
    out["sens_scipy_gelsd"] = {"r2": r2(y, X @ bs),
        "max_rel_coef_err": float(np.max(np.abs((bs - cert_coef) / cert_coef)))}
    # sensitivity b: normal equations (the route NIST warns about)
    try:
        bn = np.linalg.solve(X.T @ X, X.T @ y)
        out["sens_normal_equations"] = {"r2": r2(y, X @ bn),
            "max_rel_coef_err": float(np.max(np.abs((bn - cert_coef) / cert_coef)))}
    except np.linalg.LinAlgError as e:
        out["sens_normal_equations"] = {"error": str(e)}
    # sensitivity d: plug-in certified coefficients (harness validation)
    out["sens_certified_plugin"] = {"r2": r2(y, X @ np.array(cert_coef))}
    return out

def main():
    rep, outdir = int(sys.argv[1]), sys.argv[2]
    res = {"replicate": rep,
           "data_md5": {"Longley.dat": md5("/tmp/Longley.dat"), "Filip.dat": md5("/tmp/Filip.dat")}}

    # Longley: lines 61-76, columns y x1..x6
    L = load("/tmp/Longley.dat", 61, 76)
    assert L.shape == (16, 7)
    yL, XLr = L[:, 0], L[:, 1:]
    XL = np.column_stack([np.ones(16), XLr])
    res["Longley"] = fit_all(XL, yL, np.array(CERT["Longley"]["coef"]))
    res["Longley"]["published_r2"] = CERT["Longley"]["r2"]

    # Filip: lines 61-142, columns y x
    F = load("/tmp/Filip.dat", 61, 142)
    assert F.shape == (82, 2)
    yF, xF = F[:, 0], F[:, 1]
    XF = np.column_stack([xF ** k for k in range(11)])
    res["Filip"] = fit_all(XF, yF, np.array(CERT["Filip"]["coef"]))
    res["Filip"]["published_r2"] = CERT["Filip"]["r2"]

    # sensitivity c: Filip centered-predictor refit (NIST's suggested remedy),
    # R2 recomputed on the equivalent model
    xc = xF - np.mean(xF)
    XFc = np.column_stack([xc ** k for k in range(11)])
    bc, *_ = np.linalg.lstsq(XFc, yF, rcond=None)
    res["Filip"]["sens_centered_refit"] = {"r2": r2(yF, XFc @ bc)}

    # drifts in pp on the primary route
    for name in ("Longley", "Filip"):
        rr = res[name]["primary_numpy_lstsq"]["r2"]
        res[name]["reproduced_r2_pp"] = 100.0 * rr
        res[name]["published_r2_pp"] = 100.0 * res[name]["published_r2"]
        res[name]["drift_pp"] = 100.0 * rr - 100.0 * res[name]["published_r2"]

    path = f"{outdir}/nist_rep{rep}.json"
    with open(path, "w") as f:
        json.dump(res, f, indent=2, sort_keys=True)
    print(json.dumps({k: res[k].get("drift_pp") for k in ("Longley", "Filip")}))

if __name__ == "__main__":
    main()
