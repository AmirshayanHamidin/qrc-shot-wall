#!/usr/bin/env python3
"""Program 2b audit #20 runner: sklearn 1.9.0 docs LFW eigenfaces example, classification report.

Pinned per the pre-registration (audits/AUDIT_sklearn-lfw-eigenfaces.md, commit a81500f):
the example's pipeline exactly as printed, with the single free choice (the unseeded global
numpy RNG realization) pinned as np.random.seed(m) immediately before the PCA fit.
Data: lfw-funneled.tgz pre-placed at <DATA_HOME>/lfw_home/, sha256-asserted against
sklearn's own FUNNELED_ARCHIVE pin. n_jobs=-1 on the CV search (scheduling only; the 10
(C, gamma) draws come from ParameterSampler on the global RNG, independent of n_jobs).

Usage:
    python3 audit_lfw_eigenfaces_run.py load                     # fetch/caches arrays + print anchors
    python3 audit_lfw_eigenfaces_run.py run <m> <out_json>       # one master seed
    python3 audit_lfw_eigenfaces_run.py merge <out_raw_json>     # merge /tmp/lfwrep_m*.json
"""
import sys, json, glob, hashlib, os
import numpy as np

DATA_HOME = "/tmp/sklearn_lfw"
PUB = {"accuracy": 84.0, "weighted_f1": 84.0}
SUPPORTS = [13, 60, 27, 146, 25, 15, 36]

def check_archive():
    from sklearn.datasets._lfw import FUNNELED_ARCHIVE
    p = os.path.join(DATA_HOME, "lfw_home", "lfw-funneled.tgz")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    assert h.hexdigest() == FUNNELED_ARCHIVE.checksum, h.hexdigest()
    return h.hexdigest()

def load():
    from sklearn.datasets import fetch_lfw_people
    lfw_people = fetch_lfw_people(data_home=DATA_HOME, min_faces_per_person=70,
                                  resize=0.4, download_if_missing=False)
    n_samples, h, w = lfw_people.images.shape
    X = lfw_people.data
    y = lfw_people.target
    target_names = lfw_people.target_names
    assert (n_samples, X.shape[1], target_names.shape[0]) == (1288, 1850, 7), \
        (n_samples, X.shape[1], target_names.shape[0])
    return X, y, target_names

def split_scale(X, y):
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    assert X_train.shape[0] == 966 and X_test.shape[0] == 322
    counts = np.bincount(y_test, minlength=7).tolist()
    assert counts == SUPPORTS, counts
    scaler = StandardScaler()
    return scaler.fit_transform(X_train), scaler.transform(X_test), y_train, y_test

def run(m, out):
    from sklearn.decomposition import PCA
    from sklearn.model_selection import RandomizedSearchCV
    from sklearn.svm import SVC
    from sklearn.metrics import classification_report, accuracy_score, f1_score
    from scipy.stats import loguniform
    sha = check_archive()
    X, y, target_names = load()
    X_train, X_test, y_train, y_test = split_scale(X, y)
    np.random.seed(m)  # pinned realization of the example's unseeded global RNG
    pca = PCA(n_components=150, svd_solver="randomized", whiten=True).fit(X_train)
    X_train_pca = pca.transform(X_train)
    X_test_pca = pca.transform(X_test)
    param_grid = {"C": loguniform(1e3, 1e5), "gamma": loguniform(1e-4, 1e-1)}
    clf = RandomizedSearchCV(SVC(kernel="rbf", class_weight="balanced"), param_grid,
                             n_iter=10, n_jobs=-1)
    clf = clf.fit(X_train_pca, y_train)
    y_pred = clf.predict(X_test_pca)
    acc = 100 * accuracy_score(y_test, y_pred)
    wf1 = 100 * f1_score(y_test, y_pred, average="weighted")
    cands = [[float(p["C"]), float(p["gamma"])] for p in clf.cv_results_["params"]]
    json.dump({"master_seed": m, "archive_sha256": sha,
               "accuracy_pct": acc, "weighted_f1_pct": wf1,
               "best_C": float(clf.best_params_["C"]), "best_gamma": float(clf.best_params_["gamma"]),
               "best_cv_score": float(clf.best_score_), "candidates": cands,
               "report": classification_report(y_test, y_pred, target_names=target_names)},
              open(out, "w"))
    print(json.dumps({"m": m, "accuracy_pct": round(acc, 4), "weighted_f1_pct": round(wf1, 4),
                      "best_C": round(float(clf.best_params_["C"]), 2),
                      "best_gamma": float(clf.best_params_["gamma"])}))

def merge(out_raw):
    import sklearn, scipy
    seeds = {}
    for f in sorted(glob.glob("/tmp/lfwrep_m*.json")):
        d = json.load(open(f))
        seeds[str(d["master_seed"])] = d
    assert sorted(seeds.keys()) == ["0", "1", "2"], sorted(seeds.keys())
    drift = {c: float(np.mean([abs(seeds[m][k] - PUB[c]) for m in ("0", "1", "2")]))
             for c, k in [("accuracy", "accuracy_pct"), ("weighted_f1", "weighted_f1_pct")]}
    raw = {"published": PUB, "sklearn": sklearn.__version__, "numpy": np.__version__,
           "scipy": scipy.__version__, "seeds": seeds, "drift_pp_3seed_mean": drift}
    json.dump(raw, open(out_raw, "w"), indent=1)
    print(json.dumps({"summary": {m: {"acc": seeds[m]["accuracy_pct"], "wf1": seeds[m]["weighted_f1_pct"]}
                                  for m in seeds}, "drift": drift}))

if __name__ == "__main__":
    if sys.argv[1] == "load":
        X, y, t = load()
        print(json.dumps({"n_samples": int(X.shape[0]), "n_features": int(X.shape[1]),
                          "n_classes": int(t.shape[0])}))
    elif sys.argv[1] == "run":
        run(int(sys.argv[2]), sys.argv[3])
    else:
        merge(sys.argv[2])
