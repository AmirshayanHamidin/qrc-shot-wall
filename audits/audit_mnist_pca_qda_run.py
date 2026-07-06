import numpy as np, struct, json, sys, time
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis as QDA

def load(imgf, lblf):
    with open(imgf,'rb') as f:
        magic,n,r,c = struct.unpack('>IIII', f.read(16))
        X = np.frombuffer(f.read(), np.uint8).reshape(n, r*c).astype(np.float64)
    with open(lblf,'rb') as f:
        magic,n = struct.unpack('>II', f.read(8))
        y = np.frombuffer(f.read(), np.uint8)
    return X, y

Xtr,ytr = load('mnist/train-images-idx3-ubyte','mnist/train-labels-idx1-ubyte')
Xte,yte = load('mnist/t10k-images-idx3-ubyte','mnist/t10k-labels-idx1-ubyte')
Xtr/=255.0; Xte.=255.0
print("shapes", Xtr.shape, Xte.shape, "labels", len(np.unique(ytr)))

def run(seed):
    t=time.time()
    pca = PCA(n_components=40, svd_solver='randomized', random_state=seed)
    Ztr = pca.fit_transform(Xtr)
    Zte = pca.transform(Xte)
    clf = QDA()  # reg_param=0.0 default
    clf.fit(Ztr, ytr)
    pred = clf.predict(Zte)
    err = int((pred != yte).sum())
    return {"seed":seed, "test_errors":err, "test_error_pct": 100.0*err/len(yte),
            "evr_sum": float(pca.explained_variance_ratio_.sum()), "secs": round(time.time()-t,1)}

seeds = [int(x) for x in sys.argv[1:]] or [0]
res=[run(s) for s in seeds]
for r in res: print(r)
json.dump(res, open(f"res_{'_'.join(map(str,seeds))}.json","w"), indent=2)
