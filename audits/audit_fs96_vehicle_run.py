#!/usr/bin/env python3
"""Program 2b audit #23 runner: F&S-1996 Table 2 vehicle row, C4.5/boost/bag.

Pinned per audits/AUDIT_freund-schapire1996-vehicle-c45-boost-bag.md (pre-registered
BEFORE this script existed). Chunkable: each invocation computes a (route, master seed,
run-subset) cell and appends a JSON part to /tmp/fs96_vehicle_parts/.

Usage: audit_fs96_vehicle_run.py <route> <m> <r_start> <r_end_inclusive>
Routes: tree | boost | bag                       (primary, pinned mapping)
        m1boost | hardbag                        (sensitivity a, paper-faithful, m=0 only)
        dtree | dboost | dbag                    (sensitivity b, pure-default base tree, m=0)
        ktree | kboost | kbag                    (sensitivity c, unstratified KFold, m=0)
"""
import sys, json, os, hashlib
import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import AdaBoostClassifier, BaggingClassifier
import sklearn, scipy

OUT = '/tmp/fs96_vehicle_parts'
os.makedirs(OUT, exist_ok=True)
N_TOTAL = 846
MD5 = 'cfcd8d8b777b3dada6fcb4d2f4620951'


def get_data():
    d = fetch_openml(data_id=54, as_frame=False, parser='liac-arff')
    X = d.data.astype(np.float64)
    y = d.target.astype(str)
    md5 = hashlib.md5(X.tobytes()).hexdigest()
    assert md5 == MD5, f'data md5 mismatch: {md5}'
    assert X.shape == (N_TOTAL, 18)
    return X, y


def base_tree(fs, default=False):
    if default:
        return DecisionTreeClassifier(random_state=fs)  # gini, min_samples_leaf=1
    return DecisionTreeClassifier(criterion='entropy', min_samples_leaf=2, random_state=fs)


def fit_predict(route, Xtr, ytr, Xte, fs):
    default = route.startswith('d')
    kind = route.lstrip('dk') if route not in ('m1boost', 'hardbag') else route
    if kind == 'tree':
        clf = base_tree(fs, default).fit(Xtr, ytr)
        return clf.predict(Xte)
    if kind == 'boost':
        clf = AdaBoostClassifier(estimator=base_tree(fs, default), n_estimators=100,
                                 random_state=fs).fit(Xtr, ytr)
        return clf.predict(Xte)
    if kind == 'bag':
        clf = BaggingClassifier(estimator=base_tree(fs, default), n_estimators=100,
                                random_state=fs).fit(Xtr, ytr)
        return clf.predict(Xte)
    if kind == 'm1boost':
        # Paper-faithful AdaBoost.M1 with resampling (Figure 1). Sensitivity only.
        # This session's convention: one RandomState per fold seeded fs drives all
        # bootstrap draws; per-round tree seed fs*1000+t.
        rng = np.random.RandomState(fs)
        n = len(ytr)
        D = np.ones(n) / n
        hyps, betas = [], []
        for t in range(100):
            idx = rng.choice(n, n, replace=True, p=D)
            h = base_tree(fs * 1000 + t).fit(Xtr[idx], ytr[idx])
            miss = (h.predict(Xtr) != ytr)
            eps = D[miss].sum()
            if eps >= 0.5:
                break
            if eps == 0:
                hyps, betas = [h], [1e-10]
                break
            beta = eps / (1 - eps)
            hyps.append(h); betas.append(beta)
            D[~miss] *= beta
            D /= D.sum()
        classes = np.unique(ytr)
        votes = np.zeros((len(Xte), len(classes)))
        for h, beta in zip(hyps, betas):
            p = h.predict(Xte)
            w = np.log(1.0 / beta)
            for ci, c in enumerate(classes):
                votes[p == c, ci] += w
        return classes[np.argmax(votes, axis=1)]
    if kind == 'hardbag':
        # BaggingClassifier committee, hard simple voting; argmax ties -> first class
        # in sorted order ('bus'). Sensitivity only.
        clf = BaggingClassifier(estimator=base_tree(fs), n_estimators=100,
                                random_state=fs).fit(Xtr, ytr)
        classes = clf.classes_
        votes = np.zeros((len(Xte), len(classes)))
        for est in clf.estimators_:
            p = classes[est.predict(Xte).astype(int)] if p_is_int(est, Xte) else est.predict(Xte)
            for ci, c in enumerate(classes):
                votes[p == c, ci] += 1
        return classes[np.argmax(votes, axis=1)]
    raise ValueError(route)


def p_is_int(est, Xte):
    return np.issubdtype(est.predict(Xte[:1]).dtype, np.integer)


def main():
    route, m, r0, r1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    X, y = get_data()
    part = {'route': route, 'm': m, 'runs': {},
            'env': {'sklearn': sklearn.__version__, 'numpy': np.__version__,
                    'scipy': scipy.__version__}, 'data_md5': MD5}
    for r in range(r0, r1 + 1):
        if route.startswith('k'):
            cv = KFold(n_splits=10, shuffle=True, random_state=1000 * m + r)
        else:
            cv = StratifiedKFold(n_splits=10, shuffle=True, random_state=1000 * m + r)
        wrong = 0
        for k, (tr, te) in enumerate(cv.split(X, y)):
            fs = 100000 * m + 100 * r + k
            pred = fit_predict(route, X[tr], y[tr], X[te], fs)
            wrong += int((pred != y[te]).sum())
        part['runs'][str(r)] = wrong / N_TOTAL
    fn = f'{OUT}/{route}_m{m}_r{r0}-{r1}.json'
    json.dump(part, open(fn, 'w'), indent=1)
    print(json.dumps({'file': fn, 'runs': part['runs']}))


if __name__ == '__main__':
    main()
