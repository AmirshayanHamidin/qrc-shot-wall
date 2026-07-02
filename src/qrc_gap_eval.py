"""
Closing the shot-noise gap in QRC: strategy comparison at fixed shot budget.

Budget convention: B = total measurement shots per timestep, split evenly
across V virtual nodes (all Z/ZZ observables commute -> one computational-
basis measurement per node estimates all 21 features simultaneously).

Readout-side strategies (zero extra quantum cost):
  raw          ridge on noisy features
  ema+lag+in   exponential smoothing + lag stacking + raw input window
  pca+lag+in   PCA subspace denoising (k chosen on validation) + lags + input
  eiv+lag+in   errors-in-variables ridge: subtract analytic multinomial noise
               covariance from the Gram matrix before solving

Architecture-side (same budget, different allocation): V in {1,2,4,8}.
"""
import json
import numpy as np
from qrc_benchmark import (narma, random_reservoir_unitary, reset_qubit0,
                           Z_DIAGS, N_FEAT_PER_NODE, DIM, N_QUBITS,
                           window_features)

WASHOUT, TRAIN_FRAC = 100, 0.7
T = 1200
LM = 4  # lag depth

def qrc_feats(u_seq, U, v_nodes, shots, noise_seed=0, exact=False):
    r = np.random.default_rng(noise_seed)
    rho = np.zeros((DIM, DIM), complex); rho[0, 0] = 1.0
    Ud = U.conj().T
    F = np.zeros((len(u_seq), v_nodes * N_FEAT_PER_NODE))
    for t, u in enumerate(u_seq):
        rho = reset_qubit0(rho, u)
        for v in range(v_nodes):
            rho = U @ rho @ Ud
            p = np.real(np.diag(rho)).clip(0); p /= p.sum()
            phat = p if exact else r.multinomial(shots, p) / shots
            F[t, v*N_FEAT_PER_NODE:(v+1)*N_FEAT_PER_NODE] = [phat @ zd for zd in Z_DIAGS]
        rho /= np.real(np.trace(rho))
    return F

def lag(X, L=LM):
    out = [X]
    for k in range(1, L + 1):
        out.append(np.vstack([np.zeros((k, X.shape[1])), X[:-k]]))
    return np.hstack(out)

def ema(X, lam=0.5):
    Y = X.copy()
    for t in range(1, len(Y)):
        Y[t] = lam * Y[t] + (1 - lam) * Y[t - 1]
    return Y

def splits(Tn):
    i0 = WASHOUT
    n = Tn - i0
    te = i0 + int(TRAIN_FRAC * n)      # test starts here
    vs = i0 + int(0.55 * n)            # validation = [vs, te)
    return i0, vs, te

def ridge_solve(X, y, alpha, N=None):
    Xm, ym = X.mean(0), y.mean()
    Xc, yc = X - Xm, y - ym
    G = Xc.T @ Xc
    if N is not None:
        G = G - N
        w_, V_ = np.linalg.eigh(G)
        G = (V_ * np.maximum(w_, 1e-8)) @ V_.T
    w = np.linalg.solve(G + alpha * np.eye(G.shape[0]), Xc.T @ yc)
    return lambda Z: (Z - Xm) @ w + ym

def eval_strategy(X, y, alphas=(1e-4, 1e-3, 1e-2, 1e-1, 1.0), N_builder=None):
    """Select alpha on validation split, report test NMSE. N_builder(nrows)->N."""
    i0, vs, te = splits(len(y))
    best = (np.inf, None)
    for a in alphas:
        N = N_builder(vs - i0) if N_builder else None
        f = ridge_solve(X[i0:vs], y[i0:vs], a, N)
        v = np.mean((f(X[vs:te]) - y[vs:te]) ** 2) / np.var(y[vs:te])
        if v < best[0]:
            best = (v, a)
    N = N_builder(te - i0) if N_builder else None
    f = ridge_solve(X[i0:te], y[i0:te], best[1], N)
    nmse = np.mean((f(X[te:]) - y[te:]) ** 2) / np.var(y[te:])
    return float(nmse)

def pca_variants(X, ks=(5, 10, 20, 40, 80)):
    i0, vs, te = splits(len(X))
    Xtr = X[i0:te]
    mu = Xtr.mean(0)
    _, _, Vt = np.linalg.svd(Xtr - mu, full_matrices=False)
    for k in ks:
        k = min(k, Vt.shape[0])
        P = Vt[:k].T @ Vt[:k]
        yield k, (X - mu) @ P + mu

def run(shots_total, order=5, noise_seed=1, seed_U=7):
    u, y = narma(order, T, seed=order)
    U = random_reservoir_unitary(N_QUBITS, seed=seed_U)
    Xin = window_features(u, 10)
    res = {}

    Xe = qrc_feats(u, U, 4, 0, exact=True)
    res['exact floor (lag+in)'] = eval_strategy(np.hstack([lag(Xe), Xin]), y)

    X_by_V = {}
    for V in (1, 2, 4, 8):
        Xv = qrc_feats(u, U, V, shots_total // V, noise_seed)
        X_by_V[V] = Xv
        res[f'V={V} raw'] = eval_strategy(Xv, y)
        res[f'V={V} ema+lag+in'] = eval_strategy(np.hstack([lag(ema(Xv)), Xin]), y)

    X4 = X_by_V[4]
    res['V=4 pca+lag+in'] = min(
        eval_strategy(np.hstack([lag(Xd), Xin]), y) for _, Xd in pca_variants(X4))
    res['V=4 pca+ema+lag+in'] = min(
        eval_strategy(np.hstack([lag(ema(Xd)), Xin]), y) for _, Xd in pca_variants(X4))

    # EIV ridge on lag(raw)+input
    Xl = np.hstack([lag(X4), Xin])
    var_base = (1 - X4 ** 2).mean(0) / (shots_total // 4)
    var_full = np.concatenate([np.tile(var_base, LM + 1), np.zeros(Xin.shape[1])])
    res['V=4 eiv+lag+in'] = eval_strategy(
        Xl, y, N_builder=lambda nrows: np.diag(var_full * nrows))
    return res

if __name__ == '__main__':
    import sys
    budget = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
    res = run(budget)
    print(f'=== NARMA5, total budget {budget} shots/timestep ===')
    for k, v in sorted(res.items(), key=lambda kv: kv[1]):
        print(f'{k:28s} {v:.4f}')
    with open(f'gap_results_{budget}.json', 'w') as f:
        json.dump(res, f, indent=2)
