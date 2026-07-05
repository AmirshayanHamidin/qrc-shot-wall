"""Program 2 audit #2 reproduction script (see audits/AUDIT_fashion-mnist-logreg.md).

Claim: Fashion-MNIST paper (arXiv:1708.07747) Table 3,
LogisticRegression(C=1, multi_class=ovr, penalty=l1) -> 0.842 test accuracy.

Pipeline mirrors zalandoresearch/fashion-mnist benchmark/runner.py:
StandardScaler fit on train, transform train+test, shuffle train, fit, score on test.

This is the single-machine version of what the sandboxed session actually executed.
Because the session enforced a hard 45 s per-process cap, the multiclass fit was run
there as ten per-class one-vs-rest binary fits (equivalent scheme; validated in the
audit file) at tol=1e-2. On unconstrained hardware you can set TOL = 1e-4 (the
registered library default) and PER_CLASS = False to run the plain multiclass call.

Data: the four official idx .gz files in ./data (MD5s in the audit file).
Env of record: Python 3.10.12, scikit-learn 1.7.2, numpy 2.2.6.
"""
import gzip
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.utils import shuffle

TOL = 1e-2        # session value; registered default is 1e-4
PER_CLASS = True  # session value; False = plain multiclass call
SEEDS = (0, 1)
DATA = "data"


def load_mnist(kind):
    with gzip.open(f"{DATA}/{kind}-labels-idx1-ubyte.gz", "rb") as f:
        y = np.frombuffer(f.read(), dtype=np.uint8, offset=8)
    with gzip.open(f"{DATA}/{kind}-images-idx3-ubyte.gz", "rb") as f:
        X = np.frombuffer(f.read(), dtype=np.uint8, offset=16).reshape(len(y), 784)
    return X, y


def fit_score(X, Y, Xt, Yt):
    if not PER_CLASS:
        clf = LogisticRegression(penalty="l1", C=1.0, solver="liblinear", tol=TOL)
        return clf.fit(X, Y).score(Xt, Yt)
    W = np.zeros((10, 784)); B = np.zeros(10)
    for c in range(10):
        b = LogisticRegression(penalty="l1", C=1.0, solver="liblinear", tol=TOL)
        b.fit(X, (Y == c).astype(np.uint8))
        W[c] = b.coef_[0]; B[c] = b.intercept_[0]
    return float((np.argmax(Xt @ W.T + B, axis=1) == Yt).mean())


def main():
    X, Y = load_mnist("train")
    Xt, Yt = load_mnist("t10k")
    sc = StandardScaler().fit(X)
    X, Xt = sc.transform(X), sc.transform(Xt)
    accs = []
    for seed in SEEDS:
        Xs, Ys = shuffle(X, Y, random_state=seed)
        acc = fit_score(Xs, Ys, Xt, Yt)
        accs.append(acc)
        print(f"seed {seed}: {acc:.4f}", flush=True)
    print(f"mean: {np.mean(accs):.4f}  (published: 0.842)")


if __name__ == "__main__":
    main()
