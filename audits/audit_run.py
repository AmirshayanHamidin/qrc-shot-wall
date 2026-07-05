"""Program 2 audit #1: reproduce two rows of Fashion-MNIST paper Table 3 (arXiv:1708.07747).

See audits/AUDIT_fashion-mnist-benchmark.md for the pre-registration, results and verdicts.

Methodology mirrors benchmark/runner.py from zalandoresearch/fashion-mnist:
StandardScaler fit on the 60k train set, applied to train+test; classifier with only the
table's parameters set (baselines.json 'common' is empty -> sklearn defaults otherwise);
train on all 60k, score on all 10k. k-NN and GaussianNB are shuffle-invariant, so no repeats.

Chunked k-NN prediction is purely a sandbox concession (45 s per bash call, 2 cores, 3 GB RAM);
chunking cannot change predictions.

Data: the four data/fashion/*.gz files from zalandoresearch/fashion-mnist (MD5s must match
the README's published checksums), placed in ./data next to this script.

Usage:
  python3 audit_run.py gnb            # GaussianNB row, whole test set
  python3 audit_run.py knn A B        # k-NN row, predict test rows [A:B), append to preds file
  python3 audit_run.py score          # assemble k-NN chunks and print accuracy
"""
import gzip, sys, json, os
import numpy as np

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PRED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knn_preds.npy")


def load(kind):
    with gzip.open(os.path.join(DATA, f"{kind}-labels-idx1-ubyte.gz")) as f:
        y = np.frombuffer(f.read(), dtype=np.uint8, offset=8)
    with gzip.open(os.path.join(DATA, f"{kind}-images-idx3-ubyte.gz")) as f:
        X = np.frombuffer(f.read(), dtype=np.uint8, offset=16).reshape(len(y), 784)
    return X, y


def scaled():
    from sklearn.preprocessing import StandardScaler
    X, y = load("train")
    Xt, yt = load("t10k")
    sc = StandardScaler().fit(X)
    return sc.transform(X), y, sc.transform(Xt), yt


if sys.argv[1] == "gnb":
    from sklearn.naive_bayes import GaussianNB
    X, y, Xt, yt = scaled()
    acc = GaussianNB(priors=[0.1] * 10).fit(X, y).score(Xt, yt)
    print(json.dumps({"row": "GaussianNB priors=uniform", "published": 0.511, "reproduced": acc}))

elif sys.argv[1] == "knn":
    a, b = int(sys.argv[2]), int(sys.argv[3])
    import sklearn
    from sklearn.neighbors import KNeighborsClassifier
    sklearn.set_config(working_memory=256)  # keep pairwise-distance chunks small (3 GB box)
    X, y, Xt, yt = scaled()
    clf = KNeighborsClassifier(weights="distance", n_neighbors=5, p=2,
                               algorithm="brute", n_jobs=2).fit(X, y)
    p = clf.predict(Xt[a:b])
    preds = np.load(PRED) if os.path.exists(PRED) else np.full(10000, 255, np.uint8)
    preds[a:b] = p
    np.save(PRED, preds)
    print(json.dumps({"chunk": [a, b], "chunk_acc": float((p == yt[a:b]).mean()),
                      "done": int((preds != 255).sum())}))

elif sys.argv[1] == "score":
    _, yt = load("t10k")
    preds = np.load(PRED)
    assert (preds != 255).all(), f"missing {(preds == 255).sum()} predictions"
    acc = float((preds == yt).mean())
    print(json.dumps({"row": "KNN weights=distance n_neighbors=5 p=2",
                      "published": 0.852, "reproduced": acc}))
