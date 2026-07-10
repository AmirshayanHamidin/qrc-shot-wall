"""Program 2b confirmatory audit #21 runner - sklearn 1.7.2 docs, fully-seeded ensemble doctest rows.

Pre-registered in audits/AUDIT_sklearn-ensemble-doctests.md (commit 2cb4a52) BEFORE this
script existed (two-commit rule). Published values: Row A (GradientBoostingClassifier
docstring, make_hastie_10_2) test accuracy 0.913; Row B (AdaBoostClassifier docstring,
make_classification) training accuracy 0.96. Blind rubric 0/5 both rows; bar +/-0.5 pp.

Usage: python3 audit_ensemble_doctests_run.py <master_seed>
Master seed {0,1,2} seeds the global NumPy RNG only (audit #12/#20 convention); every
pipeline RNG below is pinned by the claim itself (random_state=0 everywhere), so results
are expected bit-identical across master seeds. CPU-only, runs in ~5 s.
"""
import json, sys, platform

import numpy as np
import sklearn
from sklearn.datasets import make_hastie_10_2, make_classification
from sklearn.ensemble import GradientBoostingClassifier, AdaBoostClassifier

master_seed = int(sys.argv[1])
np.random.seed(master_seed)

# Row A - GradientBoostingClassifier docstring example, verbatim procedure
X, y = make_hastie_10_2(random_state=0)
X_train, X_test = X[:2000], X[2000:]
y_train, y_test = y[:2000], y[2000:]
clf_a = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0,
                                   max_depth=1, random_state=0).fit(X_train, y_train)
acc_a = clf_a.score(X_test, y_test)

# Row B - AdaBoostClassifier docstring example, verbatim procedure
Xb, yb = make_classification(n_samples=1000, n_features=4,
                             n_informative=2, n_redundant=0,
                             random_state=0, shuffle=False)
clf_b = AdaBoostClassifier(n_estimators=100, random_state=0).fit(Xb, yb)
acc_b = clf_b.score(Xb, yb)

print(json.dumps({
    "master_seed": master_seed,
    "row_a_gbc_hastie_test_accuracy": acc_a,
    "row_b_adaboost_train_accuracy": acc_b,
    "row_a_correct_of_10000": int(round(acc_a * 10000)),
    "row_b_correct_of_1000": int(round(acc_b * 1000)),
    "published": {"row_a": 0.913, "row_b": 0.96},
    "env": {"python": platform.python_version(), "sklearn": sklearn.__version__,
            "numpy": np.__version__, "platform": platform.platform()},
}, indent=1))
