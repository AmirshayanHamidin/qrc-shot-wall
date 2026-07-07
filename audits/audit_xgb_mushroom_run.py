"""Program 2b audit #15: dmlc/xgboost CLI demo README (v1.7.6), mushroom, printed eval log.

Pre-registered in audits/AUDIT_xgboost-cli-mushroom-demo.md (commit f85c810) BEFORE this
script existed. Claim (README "Monitoring Progress", both eval sets):
    [0] test-error:0.016139  trainname-error:0.014433
    [1] test-error:0.000000  trainname-error:0.001228
Reproduction: xgboost-cpu 3.2.0 python API; params exactly the shipped mushroom.conf
(booster=gbtree, objective=binary:logistic, eta=1.0, gamma=1.0, min_child_weight=1,
max_depth=3, num_round=2), everything else library default; nthread=1; seed = master
seed {0,1,2} (pre-registered as inert). eval_metric='error' is the claim's own printed
metric (CLI-era default for binary:logistic), not a free choice.
Data: demo/data/agaricus.txt.{train,test} fetched from the v1.7.6 tag
(md5 a88a94251c2969849ee603701cd4878e / e13c43414be35bb0c7d40b09e1ad34ad), parsed to CSR
so absent entries stay MISSING (same semantics as the CLI's LIBSVM DMatrix).

Usage:
    python3 audit_xgb_mushroom_run.py run        # -> /tmp/xgb_mushroom_raw.json
"""
import json, hashlib
import numpy as np
import scipy.sparse as sp
import xgboost as xgb

PUB = {"test": [1.6139, 0.0000], "trainname": [1.4433, 0.1228]}  # pp
FILES = {"train": "/tmp/agaricus.txt.train", "test": "/tmp/agaricus.txt.test"}
MD5 = {"train": "a88a94251c2969849ee603701cd4878e", "test": "e13c43414be35bb0c7d40b09e1ad34ad"}
CONF = dict(booster="gbtree", objective="binary:logistic", eta=1.0, gamma=1.0,
            min_child_weight=1, max_depth=3, eval_metric="error", nthread=1)
NUM_ROUND = 2


def load_libsvm(path, n_features):
    labels, rows, cols, vals = [], [], [], []
    with open(path) as f:
        for i, line in enumerate(f):
            parts = line.split()
            labels.append(float(parts[0]))
            for tok in parts[1:]:
                j, v = tok.split(":")
                rows.append(i); cols.append(int(j)); vals.append(float(v))
    X = sp.csr_matrix((vals, (rows, cols)), shape=(len(labels), n_features))
    return X, np.array(labels)


def max_feature(paths):
    m = -1
    for p in paths:
        with open(p) as f:
            for line in f:
                for tok in line.split()[1:]:
                    m = max(m, int(tok.split(":")[0]))
    return m + 1


def run():
    for k, p in FILES.items():
        h = hashlib.md5(open(p, "rb").read()).hexdigest()
        assert h == MD5[k], (k, h)
    nf = max_feature(FILES.values())
    Xtr, ytr = load_libsvm(FILES["train"], nf)
    Xte, yte = load_libsvm(FILES["test"], nf)
    dtr = xgb.DMatrix(Xtr, label=ytr)
    dte = xgb.DMatrix(Xte, label=yte)
    out = {"env": {"xgboost": xgb.__version__, "numpy": np.__version__,
                   "n_features": nf, "rows": [Xtr.shape[0], Xte.shape[0]]},
           "published_pp": PUB, "primary": {}, "mechanism": {}}

    # primary: library defaults, master seeds 0/1/2
    for seed in (0, 1, 2):
        params = dict(CONF, seed=seed)
        ev = {}
        xgb.train(params, dtr, NUM_ROUND,
                  evals=[(dte, "test"), (dtr, "trainname")], evals_result=ev,
                  verbose_eval=False)
        out["primary"][f"seed{seed}"] = {k: [v * 100 for v in ev[k]["error"]] for k in ev}

    # mechanism table (descriptive): tree_method x base_score, seed 0
    for tm in ("default", "exact"):
        for bs in ("auto", "0.5"):
            params = dict(CONF, seed=0)
            if tm != "default":
                params["tree_method"] = tm
            if bs != "auto":
                params["base_score"] = 0.5
            ev = {}
            xgb.train(params, dtr, NUM_ROUND,
                      evals=[(dte, "test"), (dtr, "trainname")], evals_result=ev,
                      verbose_eval=False)
            out["mechanism"][f"tm={tm},bs={bs}"] = {k: [v * 100 for v in ev[k]["error"]]
                                                    for k in ev}

    # drift (pp), 3-seed mean per pre-registered number
    drifts = {}
    for k, pub in PUB.items():
        for r in range(NUM_ROUND):
            vals = [out["primary"][f"seed{s}"][k][r] for s in (0, 1, 2)]
            drifts[f"{k}_r{r}"] = {"published_pp": pub[r],
                                   "reproduced_pp_per_seed": vals,
                                   "drift_pp_3seed_mean": float(np.mean([abs(v - pub[r]) for v in vals]))}
    out["drift"] = drifts
    json.dump(out, open("/tmp/xgb_mushroom_raw.json", "w"), indent=1)
    for k, d in drifts.items():
        print(k, "pub", d["published_pp"], "rep", [round(v, 4) for v in d["reproduced_pp_per_seed"]],
              "drift", round(d["drift_pp_3seed_mean"], 4))
    print({k: [round(x, 4) for x in v["test"] + v["trainname"]] for k, v in out["mechanism"].items()})


if __name__ == "__main__":
    run()
