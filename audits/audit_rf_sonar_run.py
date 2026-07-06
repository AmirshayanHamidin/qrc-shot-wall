"""Program 2b audit #1: Breiman (2001) Table 2, sonar row (Forest-RI).

Pre-registered in audits/AUDIT_breiman2001-rf-sonar.md (commit babcc6a) BEFORE this
script ran. Procedure: 100 iterations; each draws an unstratified 10% holdout
(train_test_split, test_size=0.10 -> 21 test / 187 train, sklearn ceil convention),
fits two RandomForestClassifier(n_estimators=100, oob_score=True, bootstrap=True)
forests with max_features=1 (Single Input) and max_features=6 (F=int(log2 60+1)),
records both test errors; Selection = test error of the forest with the lower OOB
error (tie -> F=1). Columns = means over the 100 iterations. Repeated for master
seeds 0 (primary), 1, 2. Chunked to respect the sandbox's 45 s per-process cap:
    python3 audit_rf_sonar_run.py fetch          # cache data to /tmp/sonar.npz
    python3 audit_rf_sonar_run.py run <seed>     # one master seed -> /tmp/sonar_seed<seed>.json
    python3 audit_rf_sonar_run.py summarize      # aggregate + drift vs published
    python3 audit_rf_sonar_run.py pack           # -> rf_sonar_raw.json (published raw file)

The procedure is fully deterministic given the master seed (per-iteration split seeds are
drawn from np.random.RandomState(master_seed)), so any run reproduces the published rows.
"""
import json, sys, hashlib
import numpy as np

PUB_SINGLE, PUB_SELECT = 18.0, 15.9  # Breiman 2001 Table 2, sonar row (percent)
CACHE = "/tmp/sonar.npz"

def fetch():
    from sklearn.datasets import fetch_openml
    d = fetch_openml(data_id=40, as_frame=False, parser="liac-arff")
    X = d.data.astype(float); y = (d.target == d.target[0]).astype(int)
    md5 = hashlib.md5(np.ascontiguousarray(X)).hexdigest()
    np.savez(CACHE, X=X, y=y)
    print(json.dumps({"shape": list(X.shape), "classes": np.bincount(y).tolist(), "X_md5": md5}))

def run(master_seed):
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    z = np.load(CACHE); X, y = z["X"], z["y"]
    rng = np.random.RandomState(master_seed)
    rows = []
    for it in range(100):
        s = int(rng.randint(0, 2**31 - 1))
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.10, random_state=s)
        errs, oobs = {}, {}
        for F in (1, 6):
            rf = RandomForestClassifier(n_estimators=100, max_features=F,
                                        bootstrap=True, oob_score=True, random_state=s)
            rf.fit(Xtr, ytr)
            errs[F] = 1.0 - rf.score(Xte, yte)
            oobs[F] = 1.0 - rf.oob_score_
        sel = errs[1] if oobs[1] <= oobs[6] else errs[6]  # tie -> F=1 (pre-registered)
        rows.append({"iter": it, "split_seed": s, "err_F1": errs[1], "err_F6": errs[6],
                     "oob_F1": oobs[1], "oob_F6": oobs[6], "err_selection": sel})
    out = {"master_seed": master_seed,
           "single_input_pct": 100 * float(np.mean([r["err_F1"] for r in rows])),
           "selection_pct": 100 * float(np.mean([r["err_selection"] for r in rows])),
           "rows": rows}
    with open(f"/tmp/sonar_seed{master_seed}.json", "w") as f:
        json.dump(out, f)
    print(json.dumps({k: out[k] for k in ("master_seed", "single_input_pct", "selection_pct")}))

def summarize():
    seeds = {}
    for s in (0, 1, 2):
        seeds[s] = json.load(open(f"/tmp/sonar_seed{s}.json"))
    si = [seeds[s]["single_input_pct"] for s in (0, 1, 2)]
    se = [seeds[s]["selection_pct"] for s in (0, 1, 2)]
    out = {"published": {"single_input": PUB_SINGLE, "selection": PUB_SELECT},
           "per_seed": {s: {"single_input": si[s], "selection": se[s]} for s in (0, 1, 2)},
           "drift_pp_3seed_mean": {"single_input": float(np.mean([abs(v - PUB_SINGLE) for v in si])),
                                    "selection": float(np.mean([abs(v - PUB_SELECT) for v in se]))}}
    print(json.dumps(out, indent=1))

def pack():
    """Combine the three seed files into the published raw file. Rows are arrays
    (see 'columns'); float fields rounded to 6 dp (errors are exact multiples of
    1/21 and OOB of 1/187, so full precision is recoverable)."""
    cols = ["iter", "split_seed", "err_F1", "err_F6", "oob_F1", "oob_F6", "err_selection"]
    out = {"published_pct": {"single_input": PUB_SINGLE, "selection": PUB_SELECT},
           "columns": cols, "seeds": {}}
    for s in (0, 1, 2):
        d = json.load(open(f"/tmp/sonar_seed{s}.json"))
        out["seeds"][str(s)] = {
            "single_input_pct": round(d["single_input_pct"], 6),
            "selection_pct": round(d["selection_pct"], 6),
            "rows": [[r["iter"], r["split_seed"]] + [round(r[c], 6) for c in cols[2:]]
                     for r in d["rows"]]}
    with open("rf_sonar_raw.json", "w") as f:
        json.dump(out, f)
    print("wrote rf_sonar_raw.json,", len(open("rf_sonar_raw.json").read()), "bytes")

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fetch": fetch()
    elif cmd == "run": run(int(sys.argv[2]))
    elif cmd == "summarize": summarize()
    elif cmd == "pack": pack()
