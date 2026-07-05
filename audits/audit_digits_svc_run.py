"""Program 2 audit #3 reproduction script (VAR rule 3).

Reproduces scikit-learn docs example "Recognizing hand-written digits"
(https://scikit-learn.org/1.8/auto_examples/classification/plot_digits_classification.html)
verbatim, minus the plotting code. Zero-discretion pipeline: no seed, no shuffle.
Pre-registered in audits/AUDIT_sklearn-digits-svc.md (commit b22be5d) BEFORE this ran.
Observed output (2026-07-05, Python 3.10.12, sklearn 1.7.2, numpy 2.2.6, CPU):
exact accuracy 0.9688542825 (871/899); printed report identical to the published one.
"""
import hashlib, platform, sys
import numpy as np
import sklearn
from sklearn import datasets, metrics, svm
from sklearn.model_selection import train_test_split

digits = datasets.load_digits()
n_samples = len(digits.images)
data = digits.images.reshape((n_samples, -1))
print("dataset shape:", data.shape,
      "md5(data,target):",
      hashlib.md5(data.tobytes() + digits.target.tobytes()).hexdigest())

clf = svm.SVC(gamma=0.001)
X_train, X_test, y_train, y_test = train_test_split(
    data, digits.target, test_size=0.5, shuffle=False
)
clf.fit(X_train, y_train)
predicted = clf.predict(X_test)

acc = metrics.accuracy_score(y_test, predicted)
n_correct = int((predicted == y_test).sum())
print(f"exact accuracy: {acc:.10f}  ({n_correct}/{len(y_test)})")
print(metrics.classification_report(y_test, predicted))
print("python", sys.version.split()[0], "| sklearn", sklearn.__version__,
      "| numpy", np.__version__, "|", platform.platform())
