"""Program 2b audit #2: Gorman & Sejnowski (1988) sonar backprop network,
aspect-angle-independent rows (12 and 24 hidden units -> published 84.7 / 84.5 %).

Pre-registered in audits/AUDIT_gorman1988-sonar-mlp.md BEFORE this script ran
(session-local prereg commit c37f42b; remote ordering caveat disclosed in the
audit file's honesty section). Procedure: per master seed (0 primary, 1, 2),
RandomState(master) permutes the 208 OpenML sonar cases into 13 unstratified folds
of 16; per fold, train on the remaining 192 and test on the 16, repeated 10 times
with distinct weight-init seeds; row value = 100 * mean over 130 evaluations. MLP
honors everything the paper specifies that sklearn can honor (logistic units,
lr 2.0, momentum 0.0, 300 epochs, hidden width); library defaults fill the rest.
Chunked for the sandbox's 45 s per-process cap:
    python3 audit_mlp_sonar_run.py fetch        # cache data to /tmp/sonar.npz
    python3 audit_mlp_sonar_run.py run <seed>   # one master seed -> /tmp/mlp_seed<seed>.json
    python3 audit_mlp_sonar_run.py summarize    # aggregate + drift vs published
    python3 audit_mlp_sonar_run.py pack         # -> mlp_sonar_raw.json (published raw file)

Deterministic given the master seed: fold assignment comes from RandomState(master);
each fit's random_state = master*100000 + fold*100 + run.
"""
import json, sys, hashlib, warnings
import numpy as np

PUB = {12: 84.7, 24: 84.5}   # sonar.names, aspect-angle-independent test-set column
CACHE = "/tmp/sonar.npz"

def fetch():
    from sklearn.datasets import fetch_openml
    d = fetch_openml(data_id=40, as_frame=False, parser="liac-arff")
    X = d.data.astype(float); y = (d.target == d.target[0]).astype(int)
    md5 = hashlib.md5(np.ascontiguousarray(X)).hexdigest()
    np.savez(CACHE, X=X, y=y)
    print(json.dumps({"shape": list(X.shape), "classes": np.bincount(y).tolist(), "X_md5": md5}))

def run(master):
    from sklearn.neural_network import MLPClassifier
    warnings.filterwarnings("ignore")  # fixed 300-epoch budget: ConvergenceWarning expected
    z = np.load(CACHE); X, y = z["X"], z["y"]
    perm = np.random.RandomState(master).permutation(208)
    folds = [perm[16 * k:16 * (k + 1)] for k in range(13)]
    rows = []
    for h in (12, 24):
        for f, test_idx in enumerate(folds):
            tr = np.setdiff1d(np.arange(208), test_idx)
            for r in range(10):
                clf = MLPClassifier(hidden_layer_sizes=(h,), activation="logistic",
                                    solver="sgd", learning_rate="constant",
                                    learning_rate_init=2.0, momentum=0.0,
                                    nesterovs_momentum=False, batch_size=192,
                                    max_iter=300, n_iter_no_change=300, tol=1e-12,
                                    random_state=master * 100000 + f * 100 + r)
                clf.fit(X[tr], y[tr])
                rows.append({"h": h, "fold": f, "run": r,
                             "acc": float(clf.score(X[test_idx], y[test_idx]))})
    out = {"master_seed": master, "rows": rows}
    for h in (12, 24):
        a = [r["acc"] for r in rows if r["h"] == h]
        out[f"mean_h{h}"] = 100 * float(np.mean(a))
        out[f"std_h{h}"] = 100 * float(np.std(a))
    json.dump(out, open(f"/tmp/mlp_seed{master}.json", "w"))
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}))

def summarize():
    seeds = [json.load(open(f"/tmp/mlp_seed{s}.json")) for s in (0, 1, 2)]
    for h, pub in PUB.items():
        vals = [s[f"mean_h{h}"] for s in seeds]
        drift3 = float(np.mean([abs(v - pub) for v in vals]))
        print(json.dumps({"h": h, "published": pub,
                          "reproduced_by_seed": [round(v, 2) for v in vals],
                          "seed0_drift_pp": round(abs(vals[0] - pub), 2),
                          "drift3_pp": round(drift3, 2),
                          "seed0_within_5pp_bar": abs(vals[0] - pub) <= 5.0}))

def pack():
    seeds = [json.load(open(f"/tmp/mlp_seed{s}.json")) for s in (0, 1, 2)]
    json.dump({"published": PUB, "seeds": seeds},
              open("mlp_sonar_raw.json", "w"))
    print("packed", sum(len(s["rows"]) for s in seeds), "rows")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fetch": fetch()
    elif cmd == "run": run(int(sys.argv[2]))
    elif cmd == "summarize": summarize()
    elif cmd == "pack": pack()
