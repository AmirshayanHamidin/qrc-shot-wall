#!/usr/bin/env python3
"""Program 2b confirmatory audit #13 — Joulin et al. (2016) fastText, Table 1, AG News.

Published: row A (h=10) 91.5 ; row B (h=10, bigram) 92.5  [test accuracy %].
Procedure pinned in audits/AUDIT_joulin2016-fasttext-agnews.md (prereg commit f6c0417).
Chunked stages (45 s per-process sandbox cap): prep | lrsel <lr> | rowA <seed> | rowB <seed> | summary
"""
import sys, os, re, json, random, hashlib

D = os.environ.get("AUDIT_DIR", "/tmp/audit13")
CSV = os.environ.get("AG_DIR", "/tmp/ag_news_csv")
GRID = [0.05, 0.1, 0.25, 0.5]
PUB = {"rowA": 91.5, "rowB": 92.5}
SEEDS = [0, 1, 2]

def normalize_line(s):
    # Exact translation of normalize_text from facebookresearch/fastText
    # classification-results.sh, operations in script order; myshuf handled
    # separately with a seeded shuffle (labelled amendment, see prereg).
    s = s.rstrip("\n").lower()               # tr '[:upper:]' '[:lower:]'
    s = "__label__" + s                      # sed 's/^/__label__/g'
    s = s.replace("'", " ' ")
    s = s.replace('"', "")
    s = s.replace(".", " . ")
    s = s.replace("<br />", " ")
    s = s.replace(",", " , ")
    s = s.replace("(", " ( ")
    s = s.replace(")", " ) ")
    s = s.replace("!", " ! ")
    s = s.replace("?", " ? ")
    s = s.replace(";", " ")
    s = s.replace(":", " ")
    s = re.sub(" +", " ", s)                 # tr -s " "
    return s

def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def prep():
    with open(f"{CSV}/train.csv", encoding="utf-8") as f:
        train = [normalize_line(l) for l in f]
    with open(f"{CSV}/test.csv", encoding="utf-8") as f:
        test = [normalize_line(l) for l in f]
    assert len(train) == 120000 and len(test) == 7600
    for s in SEEDS:
        lines = list(train)
        random.Random(s).shuffle(lines)
        with open(f"{D}/ag.train.seed{s}.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    with open(f"{D}/ag.test.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(test) + "\n")
    # lr-selection split from the seed-0 shuffle (prereg step 3)
    with open(f"{D}/ag.train.seed0.txt", encoding="utf-8") as f:
        s0 = f.read().splitlines()
    with open(f"{D}/ag.lrsel.train.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(s0[:108000]) + "\n")
    with open(f"{D}/ag.lrsel.val.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(s0[108000:]) + "\n")
    info = {"csv_md5": {"train": md5(f"{CSV}/train.csv"), "test": md5(f"{CSV}/test.csv")},
            "norm_md5": {f"train_seed{s}": md5(f"{D}/ag.train.seed{s}.txt") for s in SEEDS} |
                        {"test": md5(f"{D}/ag.test.txt")}}
    json.dump(info, open(f"{D}/prep.json", "w"), indent=1)
    print(json.dumps(info, indent=1))

def train_eval(train_file, test_file, lr, ngrams, seed, bucket=None):
    import fasttext
    kw = dict(input=train_file, dim=10, lr=lr, wordNgrams=ngrams, minCount=1,
              epoch=5, thread=4, seed=seed, verbose=0)
    if bucket is not None:
        kw["bucket"] = bucket
    m = fasttext.train_supervised(**kw)
    n, p, r = m.test(test_file)
    return n, p

def lrsel(lr):
    n, p = train_eval(f"{D}/ag.lrsel.train.txt", f"{D}/ag.lrsel.val.txt", lr, 1, 0)
    path = f"{D}/lrsel.json"
    d = json.load(open(path)) if os.path.exists(path) else {}
    d[str(lr)] = {"n_val": n, "val_p1": p}
    json.dump(d, open(path, "w"), indent=1)
    print(f"lr={lr}: val P@1 = {p:.6f} (n={n})")

def chosen_lr():
    d = json.load(open(f"{D}/lrsel.json"))
    assert len(d) == len(GRID), f"lr grid incomplete: {sorted(d)}"
    # highest val P@1 wins, ties to the lower lr (prereg step 3)
    return min(GRID, key=lambda lr: (-d[str(lr)]["val_p1"], lr))

def run_row(row, seed):
    if row == "rowA":
        lr, ngrams, bucket = chosen_lr(), 1, None
    else:
        lr, ngrams, bucket = 0.25, 2, 10000000
    n, p = train_eval(f"{D}/ag.train.seed{seed}.txt", f"{D}/ag.test.txt", lr, ngrams, seed, bucket)
    path = f"{D}/{row}.json"
    d = json.load(open(path)) if os.path.exists(path) else {}
    d[str(seed)] = {"n_test": n, "acc_pct": 100.0 * p, "lr": lr}
    json.dump(d, open(path, "w"), indent=1)
    print(f"{row} seed={seed} lr={lr}: test acc = {100.0*p:.4f} % (n={n})")

def summary():
    out = {"published": PUB, "lr_selection": json.load(open(f"{D}/lrsel.json")),
           "chosen_lr_rowA": chosen_lr(), "prep": json.load(open(f"{D}/prep.json")), "rows": {}}
    for row in ("rowA", "rowB"):
        d = json.load(open(f"{D}/{row}.json"))
        accs = [d[str(s)]["acc_pct"] for s in SEEDS]
        drifts = [abs(a - PUB[row]) for a in accs]
        out["rows"][row] = {"per_seed": d, "accs": accs,
                            "drift_3seed_mean_pp": sum(drifts) / 3,
                            "all_seeds_within_2pp": all(dr <= 2.0 for dr in drifts)}
    json.dump(out, open(f"{D}/summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in out["rows"].items()}, indent=1))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep": prep()
    elif cmd == "lrsel": lrsel(float(sys.argv[2]))
    elif cmd in ("rowA", "rowB"): run_row(cmd, int(sys.argv[2]))
    elif cmd == "summary": summary()
