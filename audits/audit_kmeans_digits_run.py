"""Program 2b confirmatory audit #12 - reproduction runner.

Target: scikit-learn stable (1.9.0) docs example
"A demo of K-Means clustering on the handwritten digits data"
https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_digits.html

Replicates the example's benchmark EXACTLY (same estimators, same pinned seeds,
same metric calls, same execution order - the unseeded silhouette subsample
consumes the global NumPy RNG in row order, as in the original script).

Usage: python3 audit_kmeans_digits_run.py <master_seed>
The master seed ONLY sets the global NumPy RNG state before the benchmark
(the published run's process state is unknowable); every KMeans call is seeded
by the example code itself (random_state=0) or deterministic (explicit init array).

Pre-registration (committed before this file existed): audits/AUDIT_sklearn-kmeans-digits.md
"""
import json
import sys

import numpy as np
from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def bench_k_means(kmeans, name, data, labels):
    """Verbatim logic of the example's bench (timing kept but not audited)."""
    from time import time

    t0 = time()
    estimator = make_pipeline(StandardScaler(), kmeans).fit(data)
    fit_time = time() - t0

    row = {
        "init": name,
        "fit_time_s": fit_time,
        "inertia": float(estimator[-1].inertia_),
        "homo": float(metrics.homogeneity_score(labels, estimator[-1].labels_)),
        "compl": float(metrics.completeness_score(labels, estimator[-1].labels_)),
        "v_meas": float(metrics.v_measure_score(labels, estimator[-1].labels_)),
        "ARI": float(metrics.adjusted_rand_score(labels, estimator[-1].labels_)),
        "AMI": float(metrics.adjusted_mutual_info_score(labels, estimator[-1].labels_)),
    }
    # The example computes silhouette on the SCALED data (estimator[-1] is the
    # KMeans step; the pipeline scaled `data` before fitting). NOTE: the example
    # passes the raw `data` variable here - see the audit's honesty section for
    # the faithful reading. We pass exactly what the example passes: `data`.
    row["silhouette"] = float(
        metrics.silhouette_score(
            data, estimator[-1].labels_, metric="euclidean", sample_size=300
        )
    )
    return row


def main(master_seed: int):
    np.random.seed(master_seed)  # feeds ONLY the unseeded silhouette subsamples

    data, labels = load_digits(return_X_y=True)
    (n_samples, n_features), n_digits = data.shape, np.unique(labels).size

    rows = []
    kmeans = KMeans(init="k-means++", n_clusters=n_digits, n_init=4, random_state=0)
    rows.append(bench_k_means(kmeans, "k-means++", data, labels))

    kmeans = KMeans(init="random", n_clusters=n_digits, n_init=4, random_state=0)
    rows.append(bench_k_means(kmeans, "random", data, labels))

    pca = PCA(n_components=n_digits).fit(data)
    kmeans = KMeans(init=pca.components_, n_clusters=n_digits, n_init=1)
    rows.append(bench_k_means(kmeans, "PCA-based", data, labels))

    import sklearn, scipy

    out = {
        "master_seed": master_seed,
        "n_samples": int(n_samples),
        "n_features": int(n_features),
        "n_digits": int(n_digits),
        "rows": rows,
        "env": {
            "python": sys.version.split()[0],
            "sklearn": sklearn.__version__,
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]))
