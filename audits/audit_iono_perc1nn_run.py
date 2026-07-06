"""Program 2b confirmatory audit #8 runner (VAR).

Target: Sigillito et al. (1989) ionosphere "linear" perceptron 90.67% (JHU APL
Technical Digest 10(3) 262-266) + Aha 1NN 92.1% (UCI ionosphere.names).
Pre-registered in audits/AUDIT_sigillito1989-ionosphere-perc-1nn.md, committed
to the remote (e5decc2) BEFORE this script existed.

Data: canonical UCI ionosphere.data (md5 85649e5fb5b15fb9dab726c400be61fe).
Train = rows 1-200. Perceptron primary test = rows 201-350 (paper's 123g/27b);
1NN primary test = rows 201-351 (only reading under which 92.1 is achievable).
"""
import hashlib, json, sys
import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

DATA = "/tmp/iono.data"
PUB_PERC, PUB_1NN = 90.67, 92.1

raw = open(DATA, "rb").read()
md5 = hashlib.md5(raw).hexdigest()
rows = [l.split(",") for l in raw.decode().strip().split("\n")]
X = np.array([[float(v) for v in r[:34]] for r in rows])
y = np.array([1 if r[34] == "g" else 0 for r in rows])
assert X.shape == (351, 34) and md5 == "85649e5fb5b15fb9dab726c400be61fe"

Xtr, ytr = X[:200], y[:200]
X150, y150 = X[200:350], y[200:350]          # paper's test composition 123g/27b
X151, y151 = X[200:351], y[200:351]          # all remaining (names-file reading)
comp = dict(train_g=int(ytr.sum()), train_b=int((1-ytr).sum()),
            t150_g=int(y150.sum()), t150_b=int((1-y150).sum()),
            t151_g=int(y151.sum()), t151_b=int((1-y151).sum()))

def acc(yhat, ytrue):
    return 100.0 * float((yhat == ytrue).mean())

out = {"data_md5": md5, "composition": comp, "published": {"perceptron": PUB_PERC, "onenn": PUB_1NN},
       "seeds": {}, "sensitivity": {}}

for m in (0, 1, 2):
    reg = SGDRegressor(random_state=m).fit(Xtr, ytr.astype(float))
    p150 = acc((reg.predict(X150) >= 0.5).astype(int), y150)          # PRIMARY perceptron
    p151 = acc((reg.predict(X151) >= 0.5).astype(int), y151)          # sensitivity
    ptrain = acc((reg.predict(Xtr) >= 0.5).astype(int), ytr)          # side observation (paper: 87.5)
    regnp = SGDRegressor(penalty=None, random_state=m).fit(Xtr, ytr.astype(float))
    p150_nopen = acc((regnp.predict(X150) >= 0.5).astype(int), y150)  # sensitivity
    n_iter = int(reg.n_iter_)
    knn = KNeighborsClassifier(n_neighbors=1).fit(Xtr, ytr)
    k151 = acc(knn.predict(X151), y151)                                # PRIMARY 1NN
    k150 = acc(knn.predict(X150), y150)                                # sensitivity
    sc = StandardScaler().fit(Xtr)
    knz = KNeighborsClassifier(n_neighbors=1).fit(sc.transform(Xtr), ytr)
    k151z = acc(knz.predict(sc.transform(X151)), y151)                 # sensitivity
    out["seeds"][m] = dict(perc_150=p150, perc_151=p151, perc_train=ptrain,
                           perc_150_nopenalty=p150_nopen, perc_n_iter=n_iter,
                           knn_151=k151, knn_150=k150, knn_151_z=k151z)

s = out["seeds"]
out["drift_3seed_mean"] = {
    "perceptron": float(np.mean([abs(s[m]["perc_150"] - PUB_PERC) for m in (0, 1, 2)])),
    "onenn": float(np.mean([abs(s[m]["knn_151"] - PUB_1NN) for m in (0, 1, 2)])),
}
out["knn_bit_identical_across_seeds"] = len({(s[m]["knn_151"], s[m]["knn_150"], s[m]["knn_151_z"]) for m in (0,1,2)}) == 1
json.dump(out, open("/tmp/iono_perc1nn_raw.json", "w"), indent=1)
print(json.dumps(out, indent=1))
