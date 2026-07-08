#!/usr/bin/env python3
"""Program 2b audit #17 runner: Freund & Schapire (1996) Table 2, sonar row,
C4.5-alone / boosting-C4.5 / bagging-C4.5 columns (published 28.9 / 19.0 / 24.3 % test error).

Pinned plan (see audits/AUDIT_freund-schapire1996-sonar-c45-boost-bag.md, committed EMPTY first):
per master seed m in {0,1,2}: 10 runs; run r uses StratifiedKFold(10, shuffle=True,
random_state=1000*m+r); per-run error = pooled misclassified/208; row value = 100*mean(10 runs).
Per-fold estimator seed fs = 100000*m + 100*r + k. Base tree = DecisionTreeClassifier(
criterion='entropy', min_samples_leaf=2, random_state=fs) — the audits #9/#11/#16 mapping.
boost = AdaBoostClassifier(estimator=base, n_estimators=100, random_state=fs);
bag = BaggingClassifier(estimator=base, n_estimators=100, random_state=fs).
Sensitivities (seed 0 only, labelled, never the verdict): m1resample (paper-faithful
AdaBoost.M1 with resampling), baghard (simple hard voting), defaulttree (gini,
min_samples_leaf=1, all rows), unstrat (KFold(shuffle=True), all rows).

Chunk-safe under the 45 s cap: invoke as
  python3 audit_fs96_sonar_run.py <column> <master_seed> <run_lo> <run_hi> [sens]
appends per-run cells to fs96_sonar_raw.json (flat chunk log; aggregation at the end).
"""
import sys, json, os, hashlib
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier

RAW = os.environ.get('FS96_SONAR_RAW', 'fs96_sonar_raw.json')
PUBLISHED = {'tree': 28.9, 'boost': 19.0, 'bag': 24.3}


def load_data():
    import pickle
    cache = '/tmp/sonar.pkl'
    if os.path.exists(cache):
        X, y = pickle.load(open(cache, 'rb'))
    else:
        d = fetch_openml(data_id=40, as_frame=False, parser='liac-arff')
        X, y = d.data, d.target
        pickle.dump((X, y), open(cache, 'wb'))
    md5 = hashlib.md5(X.tobytes()).hexdigest()
    assert md5 == 'e5f03fedbe063c500c22a7be8c4fe878', md5
    assert X.shape == (208, 60)
    y = (np.asarray(y) == 'Mine').astype(int)
    return X, y


def base_tree(fs, default=False):
    if default:
        return DecisionTreeClassifier(random_state=fs)  # gini, min_samples_leaf=1
    return DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)


class M1Resample:
    """Paper-faithful AdaBoost.M1 with resampling (audit #9 sensitivity route)."""

    def __init__(self, T, rng, default=False):
        self.T, self.rng, self.default = T, rng, default

    def fit_predict(self, Xtr, ytr, Xte):
        n = len(ytr)
        D = np.full(n, 1.0 / n)
        hs, betas = [], []
        for t in range(self.T):
            idx = self.rng.choice(n, size=n, replace=True, p=D)
            h = base_tree(int(self.rng.integers(2**31 - 1)), self.default)
            h.fit(Xtr[idx], ytr[idx])
            pred = h.predict(Xtr)
            eps = float(np.sum(D * (pred != ytr)))
            if eps >= 0.5:
                break
            if eps == 0:  # pseudocode leaves this undefined; standard practice: keep, tiny beta
                eps = 1e-10
            beta = eps / (1 - eps)
            D = D * np.where(pred != ytr, 1.0, beta)
            D = D / D.sum()
            hs.append(h)
            betas.append(beta)
        if not hs:
            h = base_tree(int(self.rng.integers(2**31 - 1)), self.default)
            h.fit(Xtr, ytr)
            return h.predict(Xte)
        votes = np.zeros((len(Xte), 2))
        for h, beta in zip(hs, betas):
            w = np.log(1.0 / beta)
            p = h.predict(Xte)
            for c in (0, 1):
                votes[p == c, c] += w
        return np.argmax(votes, axis=1)


def run_cell(X, y, column, m, r, sens=None):
    unstrat = sens == 'unstrat'
    default = sens == 'defaulttree'
    KF = KFold if unstrat else StratifiedKFold
    kf = KF(n_splits=10, shuffle=True, random_state=1000 * m + r)
    wrong = 0
    for k, (tr, te) in enumerate(kf.split(X, y)):
        fs = 100000 * m + 100 * r + k
        Xtr, ytr, Xte, yte = X[tr], y[tr], X[te], y[te]
        if column == 'tree':
            clf = base_tree(fs, default)
            clf.fit(Xtr, ytr)
            pred = clf.predict(Xte)
        elif column == 'boost':
            if sens == 'm1resample':
                pred = M1Resample(100, np.random.default_rng(fs)).fit_predict(Xtr, ytr, Xte)
            else:
                clf = AdaBoostClassifier(estimator=base_tree(fs, default),
                                         n_estimators=100, random_state=fs)
                clf.fit(Xtr, ytr)
                pred = clf.predict(Xte)
        elif column == 'bag':
            clf = BaggingClassifier(estimator=base_tree(fs, default),
                                    n_estimators=100, random_state=fs)
            clf.fit(Xtr, ytr)
            if sens == 'baghard':
                votes = np.stack([e.predict(Xte[:, clf.estimators_features_[i]])
                                  for i, e in enumerate(clf.estimators_)])
                pred = (votes.mean(axis=0) > 0.5).astype(int)  # simple hard voting; tie -> class 0
            else:
                pred = clf.predict(Xte)
        wrong += int((pred != yte).sum())
    return 100.0 * wrong / len(y)


def main():
    column, m, lo, hi = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    sens = sys.argv[5] if len(sys.argv) > 5 else None
    X, y = load_data()
    log = json.load(open(RAW)) if os.path.exists(RAW) else {'cells': [], 'env': None}
    if log['env'] is None:
        import sklearn, scipy
        log['env'] = {'sklearn': sklearn.__version__, 'numpy': np.__version__,
                      'scipy': scipy.__version__,
                      'data_md5': 'e5f03fedbe063c500c22a7be8c4fe878', 'n': 208,
                      'classes': {'Mine': 111, 'Rock': 97}, 'published': PUBLISHED}
    for r in range(lo, hi):
        err = run_cell(X, y, column, m, r, sens)
        log['cells'].append({'column': column, 'sens': sens, 'm': m, 'r': r,
                             'error_pct': err})
        print(f"{column} sens={sens} m={m} r={r}: {err:.4f}")
    json.dump(log, open(RAW, 'w'), indent=1)


if __name__ == '__main__':
    main()
