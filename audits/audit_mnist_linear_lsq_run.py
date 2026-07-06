"""Program 2b audit #5 - LeCun et al. (1998) MNIST linear classifier, Fig.9 'Linear' = 12.0%,
reproduced via the paper's alternative stated route ('directly solving linear systems'):
sklearn RidgeClassifier() with ALL library defaults (alpha=1.0, solver='auto' -> cholesky on dense).
Pre-registered in audits/AUDIT_lecun1998-mnist-linear-lsq.md (commit cb9f5b7) BEFORE this ran.
Data: canonical MNIST idx files, MD5-verified (see AUDIT_lecun1998-mnist-linear.md).
Pipeline is deterministic; 3 procedural replicates stand in for the 3 master seeds per PREREG_DRIFT.md.
"""
import gzip, json, struct, time, platform
import numpy as np

def read_idx(path):
    with gzip.open(path, 'rb') as f:
        data = f.read()
    magic, = struct.unpack('>I', data[:4])
    ndim = magic & 0xFF
    dims = struct.unpack('>' + 'I'*ndim, data[4:4+4*ndim])
    return np.frombuffer(data, dtype=np.uint8, offset=4+4*ndim).reshape(dims)

def main():
    import sklearn
    from sklearn.linear_model import RidgeClassifier
    Xtr = read_idx('/tmp/train-images-idx3-ubyte.gz').reshape(60000, 784).astype(np.float64)/255.0
    ytr = read_idx('/tmp/train-labels-idx1-ubyte.gz')
    Xte = read_idx('/tmp/t10k-images-idx3-ubyte.gz').reshape(10000, 784).astype(np.float64)/255.0
    yte = read_idx('/tmp/t10k-labels-idx1-ubyte.gz')
    out = {"published_error_pct": 12.0,
           "model": "RidgeClassifier() - all sklearn defaults (alpha=1.0, fit_intercept=True, solver='auto'->cholesky)",
           "preprocessing": "float64 pixels / 255.0",
           "train_shape": list(Xtr.shape), "test_shape": list(Xte.shape),
           "env": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                   "numpy": np.__version__, "os": platform.platform()},
           "replicates": {}}
    for rep in (0, 1, 2):
        t0 = time.time()
        clf = RidgeClassifier().fit(Xtr, ytr)
        err = 100.0 * float((clf.predict(Xte) != yte).mean())
        out["replicates"][str(rep)] = {"test_error_pct": round(err, 4), "drift_pp": round(abs(err-12.0), 4),
                                       "fit_seconds": round(time.time()-t0, 1),
                                       "solver_resolved": "cholesky (dense, auto)"}
        print("rep", rep, out["replicates"][str(rep)], flush=True)
    d = [out["replicates"][s]["drift_pp"] for s in ("0", "1", "2")]
    out["mean_drift_pp_3rep"] = round(sum(d)/3.0, 4)
    json.dump(out, open('mnist_linear_lsq_raw.json', 'w'), indent=1)
    print("DONE mean drift", out["mean_drift_pp_3rep"])

if __name__ == '__main__':
    main()
