#!/usr/bin/env python3
"""Program 2b audit #25 runner: Freund & Schapire (1996) Table 2, segmentation row,
C4.5-alone / boosting-C4.5 / bagging-C4.5 columns (published 3.6 / 1.4 / 2.7 % test error).

Pinned plan (see audits/AUDIT_freund-schapire1996-segmentation-c45-boost-bag.md, committed
EMPTY first, commit 2beb905b): per master seed m in {0,1,2}: 10 runs; run r uses
StratifiedKFold(10, shuffle=True, random_state=1000*m+r); per-run error = pooled
misclassified/2310; row value = 100*mean(10 runs). Per-fold estimator seed
fs = 100000*m + 100*r + k. Base tree = DecisionTreeClassifier(criterion='entropy',
min_samples_leaf=2, random_state=fs) — the audits #9/#11/#16/#17/#23 mapping.
boost = AdaBoostClassifier(estimator=base, n_estimators=100, random_state=fs);
bag = BaggingClassifier(estimator=base, n_estimators=100, random_state=fs).
Labels: integers 0-6 in sorted class-name order (brickface..window).
Sensitivities (seed 0 only, labelled, never the verdict): m1resample (paper-faithful
AdaBoost.M1 with resampling, 7-class votes), baghard (simple hard voting, 7-way majority,
ties to lowest class index), defaulttree (gini, min_samples_leaf=1, all rows),
unstrat (KFold(shuffle=True), all rows).

Chunk-safe under the 45 s cap: invoke as
  python3 audit_fs96_segmentation_run.py <column> <master_seed> <run_lo> <run_hi> [sens]
appends per-run cells to fs96_segmentation_raw.json (flat chunk log; aggregation at the end).
"""
import sys, json, os, hashlib
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier

RAW = os.environ.get('FS96_SEG_RAW', 'fs96_segmentation_raw.json')
PUBLISHED = {'tree': 3.6, 'boost': 1.4, 'bag': 2.7}
DATA_MD5 = '6bde54879753df9c397f892f6621ed6e'
N, K_CLASSES = 2310, 7


def load_data():
    import pickle
    cache = os.path.expanduser('~/w/segment.pkl')
    if os.path.exists(cache):
        X, y = pickle.load(open(cache, 'rb'))
    else:
        d = fetch_openml(data_id=36, as_frame=False,
                         data_home=os.path.expanduser('~/w/openml'))
        X, y = d.data.astype(np.float64), d.target
        pickle.dump((X, y), open(cache, 'wb'))
    md5 = hashlib.md5(np.ascontiguousarray(X)).hexdigest()
    assert md5 == DATA_MD5, md5
    assert X.shape == (N, 19)
    classes = np.unique(y)  # sorted: brickface..window
    assert len(classes) == K_CLASSES
    y = np.searchsorted(classes, y).astype(int)
    return X, y


def base_tree(fs, default=False):
    if default:
        return DecisionTreeClassifier(random_state=fs)  # gini, min_samples_leaf=1
    return DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)


class M1Resample:
    """Paper-faithful AdaBoost.M1 with resampling (audit #9 sensitivity route),
    votes generalized to K classes."""

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
        votes = np.zeros((len(Xte), K_CLASSES))
        for h, beta in zip(hs, betas):
            w = np.log(1.0 / beta)
            p = h.predict(Xte)
            for c in range(K_CLASSES):
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
                                  for i, e in enumerate(clf.estimators_)]).astype(int)
                # simple hard voting, 7-way majority; np.bincount argmax -> tie to lowest index
                pred = np.array([np.argmax(np.bincount(votes[:, j], minlength=K_CLASSES))
                                 for j in range(votes.shape[1])])
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
                      'data_md5': DATA_MD5, 'n': N, 'n_classes': K_CLASSES,
                      'class_count_each': 330, 'published': PUBLISHED}
    for r in range(lo, hi):
        err = run_cell(X, y, column, m, r, sens)
        log['cells'].append({'column': column, 'sens': sens, 'm': m, 'r': r,
                             'error_pct': err})
        print(f"{column} sens={sens} m={m} r={r}: {err:.6f}")
    json.dump(log, open(RAW, 'w'), indent=1)


if __name__ == '__main__':
    main()
