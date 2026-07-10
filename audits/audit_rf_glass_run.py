#!/usr/bin/env python3
"""Program 2b audit #18 runner: Breiman (2001) Random Forests, Table 2, glass row (Forest-RI).

Reproduces Single Input (F=1) and Selection (F in {1,4}, lower forest OOB error, tie -> F=1)
test errors. 100 iterations of an unstratified 90/10 split per master seed.

Pinned per the pre-registration (audits/AUDIT_breiman2001-rf-glass.md, commit 80faaa4):
split_seed = m*100003 + i; RF(n_estimators=100, gini, bootstrap, oob_score=True);
F=1 forest random_state=(2*split_seed+1)%2**31, F=4 forest random_state=(2*split_seed+2)%2**31.
Chunkable: any [start,end) iteration range reproduces identically.

Usage:
    python3 audit_rf_glass_run.py run <master_seed> <iter_start> <iter_end> <out_json>
    python3 audit_rf_glass_run.py merge <out_raw_json>   # merge /tmp/rfglass_m*_*.json partials
"""
import sys, json, glob, hashlib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

DATA = "/tmp/glass.data"
PUB = {"single_input": 21.2, "selection": 20.6}

def load():
    raw = open(DATA, "rb").read()
    md5 = hashlib.md5(raw).hexdigest()
    assert md5 == "2732c9170bf8c483f33da3c58929c067", md5
    M = np.loadtxt(DATA, delimiter=",")
    X, y = M[:, 1:10], M[:, 10].astype(int)
    assert X.shape == (214, 9) and len(np.unique(y)) == 6
    return X, y, md5

def run(m, start, end, out):
    X, y, md5 = load()
    rows = []
    for i in range(start, end):
        ss = m * 100003 + i
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.10, random_state=ss)
        rf1 = RandomForestClassifier(n_estimators=100, criterion="gini", bootstrap=True,
                                     oob_score=True, max_features=1,
                                     random_state=(2 * ss + 1) % 2**31).fit(Xtr, ytr)
        rf4 = RandomForestClassifier(n_estimators=100, criterion="gini", bootstrap=True,
                                     oob_score=True, max_features=4,
                                     random_state=(2 * ss + 2) % 2**31).fit(Xtr, ytr)
        e1 = 1.0 - rf1.score(Xte, yte)
        e4 = 1.0 - rf4.score(Xte, yte)
        oob1, oob4 = 1.0 - rf1.oob_score_, 1.0 - rf4.oob_score_
        esel = e1 if oob1 <= oob4 else e4   # tie -> F=1
        rows.append({"iter": i, "split_seed": ss, "err_f1": e1, "err_f4": e4,
                     "oob_f1": oob1, "oob_f4": oob4, "err_sel": esel,
                     "picked": 1 if oob1 <= oob4 else 4})
    json.dump({"master_seed": m, "start": start, "end": end, "data_md5": md5, "rows": rows},
              open(out, "w"))
    print(json.dumps({"m": m, "chunk": [start, end], "n": len(rows)}))

def merge(out_raw):
    import sklearn
    seeds = {}
    for f in sorted(glob.glob("/tmp/rfglass_m*_*.json")):
        d = json.load(open(f))
        seeds.setdefault(d["master_seed"], []).extend(d["rows"])
    summary, raw = {}, {"published": PUB, "sklearn": sklearn.__version__,
                        "numpy": np.__version__, "seeds": {}}
    for m, rows in sorted(seeds.items()):
        rows = sorted(rows, key=lambda r: r["iter"])
        assert len(rows) == 100 and [r["iter"] for r in rows] == list(range(100)), m
        si = 100 * float(np.mean([r["err_f1"] for r in rows]))
        sel = 100 * float(np.mean([r["err_sel"] for r in rows]))
        summary[m] = {"single_input_pct": si, "selection_pct": sel,
                      "picked_f1_count": sum(1 for r in rows if r["picked"] == 1)}
        raw["seeds"][str(m)] = {"single_input_pct": round(si, 6), "selection_pct": round(sel, 6),
                                "rows": [[r["iter"], r["split_seed"], round(r["err_f1"], 6),
                                          round(r["err_f4"], 6), round(r["oob_f1"], 6),
                                          round(r["oob_f4"], 6), round(r["err_sel"], 6),
                                          r["picked"]] for r in rows]}
    drift = {c: float(np.mean([abs(summary[m][k] - PUB[c]) for m in (0, 1, 2)]))
             for c, k in [("single_input", "single_input_pct"), ("selection", "selection_pct")]}
    raw["summary"] = {str(m): summary[m] for m in summary}
    raw["drift_pp_3seed_mean"] = drift
    json.dump(raw, open(out_raw, "w"), indent=1)
    print(json.dumps({"summary": summary, "drift": drift}))

if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])
    else:
        merge(sys.argv[2])
