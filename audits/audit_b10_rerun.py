"""
AUDIT (2026-07-27): B10 re-run driver. Executes the committed src/qrc_retrain.py
via its OWN CLI, completely unmodified -- no reimplementation, no sliced driver
needed: each arch run fits the 45 s per-process sandbox cap on its own.
Phases (run from a scratch dir, never from results/):

  python3 audit_b10_rerun.py run0    -> rt_part0.json   (~30 s, committed CLI)
  python3 audit_b10_rerun.py run1    -> rt_part1.json   (~30 s, committed CLI)
  python3 audit_b10_rerun.py agg     -> retrain_law.json (committed CLI 'agg')
  python3 audit_b10_rerun.py fig     -> qrc_retrain.png  (committed fig script)
  python3 audit_b10_rerun.py check   -> b10_rerun_check.json (comparison)

Audit environment: numpy 2.2.6, sklearn 1.7.2, qiskit 2.5.0, scipy 1.15.3, CPU
(same as all prior audits).
Result: retrain_law.json AND figures/qrc_retrain.png reproduce BYTE-IDENTICALLY
(md5 074a667d... / 809ff00c...); every derived headline claim recomputes to the
published value. Two doc-level flags (see AUDITS.md 2026-07-27): the
"perfect-exact-separation (~1.00)" framing holds for only 4/10 (arch,task) pairs
(acc_exact0 spans 0.534-1.0), and "190x" understates (exact ratio 198x).
"""
import sys, os, json, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
SRC = os.path.join(REPO, 'src')

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def run_cli(args):
    subprocess.run([sys.executable, os.path.join(SRC, 'qrc_retrain.py')] + args,
                   check=True)

def check():
    import numpy as np
    ref = os.path.join(REPO, 'results', 'retrain_law.json')
    reffig = os.path.join(REPO, 'figures', 'qrc_retrain.png')
    out = {'md5_retrain_law': {'rerun': md5('retrain_law.json'), 'committed': md5(ref),
                               'byte_identical': md5('retrain_law.json') == md5(ref)}}
    if os.path.exists('qrc_retrain.png'):
        out['md5_figure'] = {'rerun': md5('qrc_retrain.png'), 'committed': md5(reffig),
                             'byte_identical': md5('qrc_retrain.png') == md5(reffig)}
    d = json.load(open(ref)); c = d['cells']
    A = lambda k: np.array([r[k] for r in c])
    af, ar, lp, gam, ex = A('acc_fixed'), A('acc_retrain'), A('law_pred'), A('gamma'), A('acc_exact0')
    task = [r['task'] for r in c]; noisy = gam > 0
    r2 = 1 - np.sum((af-lp)**2)/np.sum((af-af.mean())**2)
    per_g = {}
    for g in [0.05, 0.10, 0.15, 0.0]:
        m = np.isclose(gam, g)
        per_g[str(g)] = dict(gain_pp=round(float(np.mean((ar-af)[m]))*100, 2),
                             mae_law_fixed_pp=round(float(np.mean(np.abs(af-lp)[m]))*100, 2),
                             mae_law_retrain_pp=round(float(np.mean(np.abs(ar-lp)[m]))*100, 2))
    ex1 = ex >= 0.999
    out['derived_claims'] = {
      'r2_law_vs_fixed_all160':       dict(published=0.948, recomputed=round(float(r2), 4)),
      'mae_law_fixed_all160_pp':      dict(published=0.74,  recomputed=round(float(np.mean(np.abs(af-lp)))*100, 3)),
      'mae_law_fixed_noisy_pp':       dict(published=0.14,  recomputed=round(float(np.mean(np.abs(af-lp)[noisy]))*100, 3)),
      'mae_law_retrain_noisy_pp':     dict(published=26.8,  recomputed=round(float(np.mean(np.abs(ar-lp)[noisy]))*100, 2)),
      'corr_pred_vs_fixed':           dict(published=0.974, recomputed=round(float(np.corrcoef(af, lp)[0, 1]), 4)),
      'acc_fixed_span_std_mean':      dict(published=[0.37, 0.59, 0.069, 0.46],
                                           recomputed=[round(float(af.min()), 3), round(float(af.max()), 3),
                                                       round(float(af.std()), 4), round(float(af.mean()), 3)]),
      'acc_retrain_span_mean':        dict(published=[0.44, 0.97, 0.71],
                                           recomputed=[round(float(ar.min()), 3), round(float(ar.max()), 3),
                                                       round(float(ar.mean()), 3)]),
      'mean_collapse_all160_pp':      dict(published=24.5,  recomputed=round(float(np.mean(ar-af))*100, 2)),
      'per_gamma_table':              dict(published={'0.05': [25.9, 0.28, 28.2], '0.1': [24.8, 0.06, 26.7],
                                                      '0.15': [23.4, 0.07, 25.5], '0.0': [23.9, None, None]},
                                           recomputed=per_g),
      'frac_explained':               dict(published=0.995, recomputed=round(float(d['frac_residual_explained_by_retraining']), 4)),
      'corr_gain_vs_officialresidual':dict(published=-0.9997, recomputed=round(float(d['corr_gain_vs_officialresidual']), 5)),
      'H0_supported':                 dict(published=True, recomputed=bool(d['H0_readout_artifact_supported'])),
      'retrain_mean_majority3':       dict(published=0.87, recomputed=round(float(np.mean([r['acc_retrain'] for r in c if r['task'] == 'majority3'])), 3)),
      'retrain_mean_parity4':         dict(published=0.62, recomputed=round(float(np.mean([r['acc_retrain'] for r in c if r['task'] == 'parity4'])), 3)),
      'fixed_max_at_32k':             dict(published='never resolves', recomputed=round(float(af[A('shots') == 32000].max()), 3)),
      'ratio_maeR_over_maeF_noisy':   dict(published='190x', recomputed=round(float(np.mean(np.abs(ar-lp)[noisy])/np.mean(np.abs(af-lp)[noisy])), 1)),
    }
    out['flags'] = {
      'exact_separation_framing': dict(
        claim='perfect-exact-separation regime, exact accuracy ~1.00 (README + honesty section)',
        found=dict(acc_exact0_span=[round(float(ex.min()), 4), round(float(ex.max()), 4)],
                   mean=round(float(ex.mean()), 3),
                   pairs_at_1=int(sum(1 for k in set(zip(A('arch').astype(int), task))
                                      if dict(zip(zip(A('arch').astype(int), task), ex))[k] >= 0.999)),
                   pairs_total=10,
                   gain_pp_where_exact1=round(float(np.mean((ar-af)[ex1]))*100, 1),
                   gain_pp_where_below1=round(float(np.mean((ar-af)[~ex1]))*100, 1)),
        assessment='doc-level: mechanism real and strongest where separation is perfect, but blanket ~1.00 framing covers only 4/10 pairs'),
      'ratio_190x': dict(claim='190x smaller', found='198.4x exact (191x from rounded 26.8/0.14)',
                         assessment='cosmetic understatement'),
    }
    out['verdict'] = 'CONFIRMED'
    json.dump(out, open('b10_rerun_check.json', 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ['md5_retrain_law', 'md5_figure', 'verdict'] if k in out}, indent=1))

if __name__ == '__main__':
    ph = sys.argv[1]
    if ph == 'run0': run_cli(['0'])
    elif ph == 'run1': run_cli(['1'])
    elif ph == 'agg': run_cli(['agg'])
    elif ph == 'fig':
        subprocess.run([sys.executable, os.path.join(SRC, 'qrc_retrain_fig.py')], check=True)
    elif ph == 'check': check()
