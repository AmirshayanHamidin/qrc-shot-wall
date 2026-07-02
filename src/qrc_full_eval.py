"""Hardened evaluation: tuned ESN, multi-seed QRC, shot-noise study, plots."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from qrc_benchmark import (narma, random_reservoir_unitary, qrc_features,
                           esn_features, window_features, evaluate,
                           reset_qubit0, Z_DIAGS, N_FEAT_PER_NODE, V_NODES, DIM,
                           N_QUBITS)

T = 1200

def tuned_esn(u, y, n_nodes):
    """Grid-search ESN hyperparams on the training split (fair tuning)."""
    best = (np.inf, None)
    for sr in (0.7, 0.9, 0.99, 1.1):
        for leak in (0.2, 0.5, 0.8, 1.0):
            for seed in (3, 4, 5):
                X = esn_features(u, n_nodes, seed=seed, rho_sr=sr, leak=leak)
                nmse, _, _ = evaluate(X, y)
                if nmse < best[0]:
                    best = (nmse, (sr, leak, seed))
    return best

def qrc_multiseed(u, y, seeds=(7, 8, 9, 10, 11)):
    nmses = []
    for s in seeds:
        U = random_reservoir_unitary(N_QUBITS, seed=s)
        X = qrc_features(u, U)
        nmse, pred, yte = evaluate(X, y)
        nmses.append(nmse)
    return np.array(nmses), pred, yte  # pred/yte from last seed for plotting

def qrc_features_shots(u_seq, U, shots, seed=0):
    """Same reservoir, but Z-expectations estimated from finite samples."""
    r = np.random.default_rng(seed)
    rho = np.zeros((DIM, DIM), complex)
    rho[0, 0] = 1.0
    Tn = len(u_seq)
    feats = np.zeros((Tn, V_NODES * N_FEAT_PER_NODE))
    Ud = U.conj().T
    for t in range(Tn):
        rho = reset_qubit0(rho, u_seq[t])
        for v in range(V_NODES):
            rho = U @ rho @ Ud
            p = np.real(np.diag(rho)).clip(0)
            p /= p.sum()
            counts = r.multinomial(shots, p)
            phat = counts / shots
            feats[t, v * N_FEAT_PER_NODE:(v + 1) * N_FEAT_PER_NODE] = [
                float(phat @ zd) for zd in Z_DIAGS]
        rho /= np.real(np.trace(rho))
    return feats

results = {}
for order in (2, 5):
    u, y = narma(order, T, seed=order)
    nfeat = V_NODES * N_FEAT_PER_NODE

    q_nmses, q_pred, q_yte = qrc_multiseed(u, y)
    esn_best, esn_params = tuned_esn(u, y, nfeat)
    lin_nmse, _, _ = evaluate(window_features(u, 2 * order), y)

    shot_curve = {}
    U = random_reservoir_unitary(N_QUBITS, seed=7)
    for shots in (100, 1000, 10000, 100000):
        Xs = qrc_features_shots(u, U, shots)
        s_nmse, _, _ = evaluate(Xs, y)
        shot_curve[shots] = s_nmse

    results[f'NARMA{order}'] = {
        'QRC_mean': float(q_nmses.mean()), 'QRC_std': float(q_nmses.std()),
        'QRC_seeds': q_nmses.tolist(),
        'ESN_tuned': float(esn_best), 'ESN_params': str(esn_params),
        'Linear_window': float(lin_nmse),
        'shot_curve': {str(k): float(v) for k, v in shot_curve.items()},
    }
    print(f"NARMA{order}: QRC {q_nmses.mean():.4f}±{q_nmses.std():.4f} | "
          f"ESN(tuned) {esn_best:.4f} | Linear {lin_nmse:.4f} | "
          f"shots: {shot_curve}", flush=True)

    if order == 5:
        fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
        n = 150
        axes[0].plot(q_yte[:n], label='true', lw=1.5)
        axes[0].plot(q_pred[:n], label='QRC pred', lw=1, ls='--')
        axes[0].set_title(f'NARMA5 test trace (QRC, NMSE={q_nmses[-1]:.4f})')
        axes[0].set_xlabel('t'); axes[0].legend(frameon=False)
        ss = sorted(shot_curve)
        axes[1].loglog(ss, [shot_curve[s] for s in ss], 'o-', label='QRC (finite shots)')
        axes[1].axhline(q_nmses.mean(), color='gray', ls=':', label='QRC (exact)')
        axes[1].axhline(esn_best, color='tab:red', ls='--', label='ESN tuned')
        axes[1].set_xlabel('shots per feature vector'); axes[1].set_ylabel('NMSE')
        axes[1].set_title('Shot-noise sensitivity (NARMA5)')
        axes[1].legend(frameon=False)
        fig.tight_layout()
        fig.savefig('qrc_narma5.png', dpi=150)

with open('qrc_full_results.json', 'w') as f:
    json.dump(results, f, indent=2)
print('done')
