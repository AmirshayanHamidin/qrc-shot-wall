"""
B2 provenance restoration: pinned-convention reconstruction generator for the two
sim-trained denoiser rows (printed NMSE 0.1519 / 0.1533) and the non-redundancy
probe (printed rel. err 0.90 / 0.89) of results/RESULTS_GAP.md.

Registered BEFORE first run in audits/PREREG_B2_GEN.md (two-commit rule; all bars
and every free choice fixed there). The original in-session code is lost; this is
a reconstruction under declared conventions — the B5-restoration class — not a
bit-reproduction claim.

Pinned conventions (see the pre-registration for rationale):
  benchmark run : committed qrc_gap_eval.run() defaults — NARMA5 narma(5,1200,seed=5),
                  random_reservoir_unitary(6, seed=7), V=4, budget 40k -> 10k
                  shots/node, benchmark noise seed 1, Xin = window_features(u,10),
                  committed eval_strategy; downstream readout for denoised features
                  = hstack([lag(X_denoised), Xin]) (the committed lag+input pipeline).
  training data : second simulated sequence narma(5,2400,seed=105), training noise
                  seed 2, rows after washout 100 -> 2300 rows.
  linear        : multi-output Ridge, alpha in {1e-6,1e-4,1e-2,1,100} selected by
                  feature-reconstruction MSE on the last 30% of the training rows
                  (fit on first 70%), refit on all rows at the selected alpha.
  MLP           : MLPRegressor(hidden_layer_sizes=(256,128), random_state=0,
                  max_iter=300), other params default, fit on all training rows.
  probe         : same two recipes, input = the 10-col input window ONLY, target =
                  84 exact features; trained on the training rows, evaluated on the
                  benchmark rows after washout (1100 rows).
                  rel. err = ||pred-true||_F / ||true - colmean(true)||_F with
                  column means from the evaluation rows (= pooled sqrt(1-R^2));
                  the uncentered ratio ||pred-true||_F/||true||_F is reported as a
                  labeled sensitivity, no bar.
  sensitivity   : the two denoiser NMSEs re-run at benchmark noise seeds 2 and 3
                  (same fitted denoisers; the committed plateau-check seeds).

Stages (so every bash call stays under the 45 s cap); scratch cache dn_cache.npz
in the working directory is intermediate, not a file of record:
  python qrc_gap_denoiser.py featsA    # benchmark sequence features (exact + seed-1 noisy)
  python qrc_gap_denoiser.py featsB    # training sequence features (exact + seed-2 noisy)
  python qrc_gap_denoiser.py feats23   # benchmark noisy features at seeds 2,3 (sensitivity)
  python qrc_gap_denoiser.py linear    # linear denoiser row + linear probe
  python qrc_gap_denoiser.py mlp       # MLP denoiser row + MLP probe
  python qrc_gap_denoiser.py sens      # denoiser rows at benchmark noise seeds 2,3
  python qrc_gap_denoiser.py report    # assemble gap_denoiser.json + bar verdicts
"""
import json
import sys

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor

from qrc_benchmark import narma, random_reservoir_unitary, window_features, N_QUBITS
from qrc_gap_eval import qrc_feats, lag, eval_strategy, WASHOUT

CACHE = 'dn_cache.npz'
OUT = 'gap_denoiser.json'
BUDGET = 40000
V = 4
SHOTS = BUDGET // V
ALPHAS = (1e-6, 1e-4, 1e-2, 1.0, 100.0)
PUBLISHED = {'nmse_linear': 0.1519, 'nmse_mlp': 0.1533,
             'relerr_linear': 0.90, 'relerr_mlp': 0.89}


def load_cache():
    return dict(np.load(CACHE))


def save_cache(d):
    np.savez(CACHE, **d)


def stage_featsA():
    u, y = narma(5, 1200, seed=5)
    U = random_reservoir_unitary(N_QUBITS, seed=7)
    d = {'u': u, 'y': y}
    d['Xe_b'] = qrc_feats(u, U, V, 0, exact=True)
    d['Xn_b1'] = qrc_feats(u, U, V, SHOTS, noise_seed=1)
    save_cache(d)
    print('featsA done', d['Xe_b'].shape, d['Xn_b1'].shape)


def stage_featsB():
    d = load_cache()
    u2, _ = narma(5, 2400, seed=105)
    U = random_reservoir_unitary(N_QUBITS, seed=7)
    d['u2'] = u2
    d['Xe_t'] = qrc_feats(u2, U, V, 0, exact=True)
    d['Xn_t'] = qrc_feats(u2, U, V, SHOTS, noise_seed=2)
    save_cache(d)
    print('featsB done', d['Xe_t'].shape, d['Xn_t'].shape)


def stage_feats23():
    d = load_cache()
    U = random_reservoir_unitary(N_QUBITS, seed=7)
    for s in (2, 3):
        d[f'Xn_b{s}'] = qrc_feats(d['u'], U, V, SHOTS, noise_seed=s)
    save_cache(d)
    print('feats23 done')


def fit_linear(Xin, Xout):
    n70 = int(0.7 * len(Xin))
    best = (np.inf, None)
    for a in ALPHAS:
        r = Ridge(alpha=a).fit(Xin[:n70], Xout[:n70])
        m = float(np.mean((r.predict(Xin[n70:]) - Xout[n70:]) ** 2))
        if m < best[0]:
            best = (m, a)
    return Ridge(alpha=best[1]).fit(Xin, Xout), best[1]


def fit_mlp(Xin, Xout):
    m = MLPRegressor(hidden_layer_sizes=(256, 128), random_state=0, max_iter=300)
    m.fit(Xin, Xout)
    return m


def train_blocks(d):
    w = WASHOUT
    Xin_t = window_features(d['u2'], 10)
    den_in = np.hstack([d['Xn_t'], Xin_t])[w:]
    den_out = d['Xe_t'][w:]
    probe_in = Xin_t[w:]
    return den_in, den_out, probe_in


def denoiser_nmse(model, Xn_b, d):
    Xin_b = window_features(d['u'], 10)
    Xd = model.predict(np.hstack([Xn_b, Xin_b]))
    return eval_strategy(np.hstack([lag(Xd), Xin_b]), d['y'])


def probe_relerr(model, d):
    w = WASHOUT
    Xin_b = window_features(d['u'], 10)
    true = d['Xe_b'][w:]
    pred = model.predict(Xin_b[w:])
    num = float(np.linalg.norm(pred - true))
    cen = float(np.linalg.norm(true - true.mean(0)))
    unc = float(np.linalg.norm(true))
    return num / cen, num / unc


def stage_linear():
    d = load_cache()
    den_in, den_out, probe_in = train_blocks(d)
    dn, a_dn = fit_linear(den_in, den_out)
    nmse = denoiser_nmse(dn, d['Xn_b1'], d)
    pr, a_pr = fit_linear(probe_in, den_out)
    rel_c, rel_u = probe_relerr(pr, d)
    json.dump({'nmse_linear': nmse, 'alpha_denoiser': a_dn,
               'relerr_linear_centered': rel_c, 'relerr_linear_uncentered': rel_u,
               'alpha_probe': a_pr}, open('dn_linear.json', 'w'), indent=1)
    print('linear:', nmse, '| probe rel err (centered/uncentered):', rel_c, rel_u)


def stage_mlp():
    d = load_cache()
    den_in, den_out, probe_in = train_blocks(d)
    dn = fit_mlp(den_in, den_out)
    nmse = denoiser_nmse(dn, d['Xn_b1'], d)
    json.dump({'nmse_mlp': nmse, 'n_iter': dn.n_iter_},
              open('dn_mlp1.json', 'w'), indent=1)
    print('mlp denoiser:', nmse, 'iters', dn.n_iter_)


def stage_mlp_probe():
    d = load_cache()
    den_in, den_out, probe_in = train_blocks(d)
    pr = fit_mlp(probe_in, den_out)
    rel_c, rel_u = probe_relerr(pr, d)
    json.dump({'relerr_mlp_centered': rel_c, 'relerr_mlp_uncentered': rel_u,
               'n_iter': pr.n_iter_}, open('dn_mlp2.json', 'w'), indent=1)
    print('mlp probe rel err (centered/uncentered):', rel_c, rel_u)


def stage_sens():
    d = load_cache()
    den_in, den_out, _ = train_blocks(d)
    dn_lin, _ = fit_linear(den_in, den_out)
    dn_mlp = fit_mlp(den_in, den_out)
    out = {}
    for s in (2, 3):
        out[f'nmse_linear_seed{s}'] = denoiser_nmse(dn_lin, d[f'Xn_b{s}'], d)
        out[f'nmse_mlp_seed{s}'] = denoiser_nmse(dn_mlp, d[f'Xn_b{s}'], d)
    json.dump(out, open('dn_sens.json', 'w'), indent=1)
    print('sens:', out)


def stage_posthoc():
    """EXPLORATORY, post-hoc (written AFTER the pre-registered probe numbers were
    observed to miss the printed 0.90/0.89 badly; labeled as such per repo practice).
    Diagnosis hypothesis: the original probe's unstated 'rel. err' was the
    per-feature-STANDARDIZED (variance-equalized) error sqrt(mean_j MSE_j/var_j),
    not the pooled-Frobenius ratio pinned in the pre-registration. Under pooled
    Frobenius, high-variance & linearly-predictable features dominate; equal
    weighting exposes the unpredictable low-variance features. No bar; diagnostic
    only — the pre-registered verdicts stand on the pinned definition."""
    d = load_cache()
    den_in, den_out, probe_in = train_blocks(d)
    w = WASHOUT
    Xin_b = window_features(d['u'], 10)
    true = d['Xe_b'][w:]
    var_j = true.var(0)
    out = {'label': 'EXPLORATORY post-hoc diagnostic, not pre-registered; '
                    'see stage docstring'}
    lin, _ = fit_linear(probe_in, den_out)
    mlp = fit_mlp(probe_in, den_out)
    for name, model in (('linear', lin), ('mlp', mlp)):
        pred = model.predict(Xin_b[w:])
        mse_j = ((pred - true) ** 2).mean(0)
        ratios = mse_j / var_j
        out[f'relerr_{name}_standardized'] = float(np.sqrt(ratios.mean()))
        out[f'relerr_{name}_perfeat_median'] = float(np.median(np.sqrt(ratios)))
        out[f'relerr_{name}_perfeat_max'] = float(np.sqrt(ratios.max()))
    # Second labeled diagnostic: same linear probe with the CURRENT input u_t
    # excluded (window over u_{t-1}..u_{t-10}); tests whether the printed 0.90
    # measured the reservoir's MEMORY content, with the freshly-injected input
    # (which dominates the features) removed from the predictor set.
    def shift1(X):
        return np.vstack([np.zeros((1, X.shape[1])), X[:-1]])
    probe_in_nc = shift1(window_features(d['u2'], 10))[w:]
    lin_nc, _ = fit_linear(probe_in_nc, den_out)
    pred_nc = lin_nc.predict(shift1(Xin_b)[w:])
    num = float(np.linalg.norm(pred_nc - true))
    out['relerr_linear_nocurrent_pooled'] = num / float(np.linalg.norm(true - true.mean(0)))
    mse_j = ((pred_nc - true) ** 2).mean(0)
    out['relerr_linear_nocurrent_standardized'] = float(np.sqrt((mse_j / var_j).mean()))
    json.dump(out, open('dn_posthoc.json', 'w'), indent=1)
    print(out)


def stage_report():
    r = {}
    for f in ('dn_linear.json', 'dn_mlp1.json', 'dn_mlp2.json', 'dn_sens.json'):
        r.update(json.load(open(f)))
    bars = {
        'A1_nmse_linear_within_0.010': abs(r['nmse_linear'] - PUBLISHED['nmse_linear']) <= 0.010,
        'A2_nmse_mlp_within_0.010': abs(r['nmse_mlp'] - PUBLISHED['nmse_mlp']) <= 0.010,
        'A3_relerr_linear_within_0.05': abs(r['relerr_linear_centered'] - PUBLISHED['relerr_linear']) <= 0.05,
        'A4_relerr_mlp_within_0.05': abs(r['relerr_mlp_centered'] - PUBLISHED['relerr_mlp']) <= 0.05,
        'B1_both_nmse_in_plateau_bracket': (0.1417 <= r['nmse_linear'] <= 0.1759) and (0.1417 <= r['nmse_mlp'] <= 0.1759),
        'B2_both_relerr_ge_0.80': r['relerr_linear_centered'] >= 0.80 and r['relerr_mlp_centered'] >= 0.80,
    }
    try:
        posthoc = json.load(open('dn_posthoc.json'))
    except FileNotFoundError:
        posthoc = None
    out = {
        'protocol': 'audits/PREREG_B2_GEN.md (registered 2026-08-02, commit 217a342, '
                    'BEFORE first run; reconstruction under pinned conventions, '
                    'not a bit-reproduction claim)',
        'exploratory_posthoc_diagnostics': posthoc,
        'published': PUBLISHED,
        'pinned': {'benchmark': 'narma(5,1200,seed=5), U seed 7, V=4, 10000 shots/node, '
                                'benchmark noise seed 1, committed eval_strategy, '
                                'lag+input downstream',
                   'training': 'narma(5,2400,seed=105), noise seed 2, 2300 rows after washout',
                   'alphas': list(ALPHAS), 'mlp': '(256,128), random_state=0, max_iter=300'},
        'reconstructed': r,
        'bars': bars,
    }
    json.dump(out, open(OUT, 'w'), indent=1)
    print(json.dumps(bars, indent=1))
    print('written', OUT)


STAGES = {'featsA': stage_featsA, 'featsB': stage_featsB, 'feats23': stage_feats23,
          'linear': stage_linear, 'mlp': stage_mlp, 'mlp_probe': stage_mlp_probe,
          'sens': stage_sens, 'posthoc': stage_posthoc, 'report': stage_report}

if __name__ == '__main__':
    STAGES[sys.argv[1]]()
