"""Program 2b audit #4 - LeCun et al. (1998) MNIST linear classifier, Fig.9 'Linear' = 12.0% test error.
Reproduction per pre-registered plan (audits/AUDIT_lecun1998-mnist-linear.md, commit 515ce8d):
sklearn SGDClassifier(loss='squared_error', random_state=<master seed>), ALL other params library
defaults; pixels float64 / 255; metric = test error %% on the 10,000 regular test images; seeds 0,1,2.
Data: canonical MNIST idx files (ossci-datasets.s3.amazonaws.com/mnist), MD5-verified pre-registration.
Usage: python3 audit_mnist_linear_run.py  (expects the four .gz files in /tmp)
"""
import gzip, json, struct, time, platform
import numpy as np

def read_idx(path):
    with gzip.open(path, 'rb') as f:
        data = f.read()
    magic, = struct.unpack('>I', data[:4])
    ndim = magic & 0xFF
    dims = struct.unpack('>' + 'I'*ndim, data[4:4+4*ndim])
    a = np.frombuffer(data, dtype=np.uint8, offset=4+4*ndim)
    return a.reshape(dims)

def main():
    import sklearn
    from sklearn.linear_model import SGDClassifier
    Xtr = read_idx('/tmp/train-images-idx3-ubyte.gz').reshape(60000, 784).astype(np.float64)/255.0
    ytr = read_idx('/tmp/train-labels-idx1-ubyte.gz')
    Xte = read_idx('/tmp/mnist_t10k_img.gz').reshape(10000, 784).astype(np.float64)/255.0
    yte = read_idx('/tmp/t10k-labels-idx1-ubyte.gz')
    out = {"published_error_pct": 12.0,
           "model": "SGDClassifier(loss='squared_error', random_state=seed); all other params sklearn defaults",
           "preprocessing": "float64 pixels / 255.0",
           "train_shape": list(Xtr.shape), "test_shape": list(Xte.shape),
           "env": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                   "numpy": np.__version__, "os": platform.platform()},
           "seeds": {}}
    for seed in (0, 1, 2):
        t0 = time.time()
        clf = SGDClassifier(loss='squared_error', random_state=seed)
        clf.fit(Xtr, ytr)
        err = 100.0 * float((clf.predict(Xte) != yte).mean())
        out["seeds"][str(seed)] = {"test_error_pct": round(err, 4),
                                   "drift_pp": round(abs(err - 12.0), 4),
                                   "n_iter": int(np.max(clf.n_iter_)) if hasattr(clf, 'n_iter_') else None,
                                   "fit_seconds": round(time.time() - t0, 1)}
        with open('/tmp/run/mnist_linear_raw.json', 'w') as f:
            json.dump(out, f, indent=1)
        print("seed", seed, out["seeds"][str(seed)], flush=True)
    drifts = [out["seeds"][s]["drift_pp"] for s in ("0", "1", "2")]
    out["mean_drift_pp_3seed"] = round(sum(drifts)/3.0, 4)
    out["done"] = True
    with open('/tmp/run/mnist_linear_raw.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("DONE mean drift", out["mean_drift_pp_3seed"], flush=True)

if __name__ == '__main__':
    main()
