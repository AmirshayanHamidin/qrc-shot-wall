"""
B7/B8/B9 first-audit re-run (2026-08-02, closeout session 2/4).

Regenerates the committed outputs of benchmarks 7 (RESULTS_PERNODE.md),
8 (RESULTS_BEYONDNOISE.md) and 9 (RESULTS_MARGINEST.md) from the repo's own
committed code and re-derives every number quoted in the three write-ups from
the stored raw JSON files.

Stages (so the audit can be run in bounded chunks; `all` runs everything):
  b7            regenerate pn_part{0,1}.json + pernode_law.json via
                src/qrc_pernode.py {0,1,agg}; require md5 byte-identity
  b8:coherent   regenerate bn_coherent.json via src/qrc_beyondnoise.py
  b8:amp_damping, b8:dephasing   same for the other two channels
  b8:agg        regenerate beyond_noise_law.json via `agg`; md5-check all four
  b9            re-run src/qrc_marginest.py (full grid, deterministic seeds
                1000*arch+37*s+S_pilot); require exact float equality of all
                60 rows against results/marginest_law.json
  claims        re-derive every write-up claim from the committed JSONs;
                hard-fail on any numeric mismatch at published precision;
                print FLAG (not FAIL) for the wording issues found

Findings summary (2026-08-02 run, numpy 2.x / sklearn 1.7.2):
  - B7, B8: every artifact regenerates BYTE-IDENTICAL (md5), including B8's
    sampled noisy readouts (fixed SAMPLE_SEEDS). All quoted numbers match.
  - B9: all 60 rows regenerate with exact float equality; summary block is
    exactly the row means. Two wording flags, no number challenged:
    (1) the "+18%" naive bias at S_pilot=250 is the parity-3 mean across the
        three architectures (+18.3%), not "parity-3 on arch 0" (+2.7%);
    (2) "corrected bias <=0.8% on every config" holds for 53/60 configs;
        the seven exceptions span 1.04-1.80%, the worst being
        arch2/parity3/250 - the +41% case the sentence explicitly includes.
        The budget-averaged table's <=0.2% biases are correct as published.
  - B8 wording nit: mechanism paragraph says dephasing "cos >= 0.98";
    the actual minimum is 0.9762 (the table's own 0.976).

NOTE this session executed qrc_marginest.run() restricted to one architecture
per invocation (sandbox wall-clock limit); the pilot seeds depend only on
(arch, seed, S_pilot), so the restriction is exactly equivalent to one full
run. This script performs the full run in one subprocess.

Run from repo root: PYTHONPATH=<libs> python3 audits/audit_b7b8b9_rerun.py all
"""
import hashlib, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.path.join(ROOT, 'audits', '_b7b8b9_scratch')
FAILED = []


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


def check(name, cond, detail=''):
    print(('PASS' if cond else 'FAIL'), name, detail)
    if not cond:
        FAILED.append(name)


def flag(name, detail=''):
    print('FLAG', name, detail)


def close(a, b, tol):
    return abs(a - b) <= tol


def run_py(args, cwd):
    subprocess.run([sys.executable] + args, cwd=cwd, check=True,
                   capture_output=True, env=os.environ.copy())


def stage_b7():
    d = os.path.join(SCRATCH, 'b7'); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'src', 'qrc_pernode.py'), d)
    shutil.copy(os.path.join(ROOT, 'results', 'gate_noise_law.json'), d)
    for a in ('0', '1'):
        run_py(['qrc_pernode.py', a], d)
    run_py(['qrc_pernode.py', 'agg'], d)
    for f in ('pn_part0.json', 'pn_part1.json', 'pernode_law.json'):
        check(f'B7 {f} byte-identical',
              md5(os.path.join(d, f)) == md5(os.path.join(ROOT, 'results', f)),
              md5(os.path.join(ROOT, 'results', f)))


def stage_b8_channel(ch):
    d = os.path.join(SCRATCH, 'b8'); os.makedirs(d, exist_ok=True)
    shutil.copy(os.path.join(ROOT, 'src', 'qrc_beyondnoise.py'), d)
    run_py(['qrc_beyondnoise.py', ch], d)


def stage_b8_agg():
    d = os.path.join(SCRATCH, 'b8')
    run_py(['qrc_beyondnoise.py', 'agg'], d)
    for f in ('bn_coherent.json', 'bn_amp_damping.json', 'bn_dephasing.json',
              'beyond_noise_law.json'):
        check(f'B8 {f} byte-identical',
              md5(os.path.join(d, f)) == md5(os.path.join(ROOT, 'results', f)),
              md5(os.path.join(ROOT, 'results', f)))


def stage_b9():
    d = os.path.join(SCRATCH, 'b9'); os.makedirs(d, exist_ok=True)
    for f in ('qrc_marginest.py', 'qrc_law.py'):
        shutil.copy(os.path.join(ROOT, 'src', f), d)
    run_py(['qrc_marginest.py'], d)
    rr = json.load(open(os.path.join(d, 'b9_marginest.json')))
    pub = json.load(open(os.path.join(ROOT, 'results',
                                      'marginest_law.json')))['rows']
    check('B9 row count 60', len(rr) == 60 == len(pub))
    exact = True
    for r, p in zip(rr, pub):
        if (r['arch'], r['task'], r['S_pilot']) != (p['arch'], p['task'],
                                                    p['S_pilot']):
            exact = False; break
        if r['D0'] != p['D0']:
            exact = False
        for est in ('naive', 'corr_exact', 'corr_pilot'):
            for k in ('bias', 'rmse'):
                if r[est][k] != p[est][k]:
                    exact = False
    check('B9 all 60 rows exact float match', exact)


def stage_claims():
    import numpy as np
    res = lambda f: os.path.join(ROOT, 'results', f)

    # ---------- B7 (RESULTS_PERNODE.md) ----------
    d = json.load(open(res('pernode_law.json')))
    mo = d['models']
    check('B7 n_pred 350', d['n_pred'] == 350 and len(d['cells']) == 350)
    for m, (r2, mae) in dict(naive=(0.851, 4.16), b6_scalar=(0.927, 2.89),
                             scalar_cov=(0.930, 2.82),
                             pernode=(0.930, 2.82)).items():
        check(f'B7 table {m} R2={r2}/MAE={mae}pp',
              close(mo[m]['r2'], r2, 5e-4) and close(100*mo[m]['mae'], mae, 5e-3),
              f"got {mo[m]['r2']:.4f}/{100*mo[m]['mae']:.3f}")
    check('B7 pernode MAE reduction 2.5%',
          close(100*d['pernode_vs_b6_mae_reduction'], 2.5, 0.05),
          f"{100*d['pernode_vs_b6_mae_reduction']:.2f}%")
    check('B7 scalar_cov MAE reduction 2.4%',
          close(100*d['scalarcov_vs_b6_mae_reduction'], 2.4, 0.05),
          f"{100*d['scalarcov_vs_b6_mae_reduction']:.2f}%")
    check('B7 pre-registered threshold 30%',
          d['pre_registered_threshold'] == 0.30)
    pg = d['per_gamma']['0.2']
    check('B7 gamma=0.20 MAE 4.64->4.48pp',
          close(100*pg['b6_scalar'], 4.64, 5e-3) and
          close(100*pg['pernode'], 4.48, 5e-3),
          f"{100*pg['b6_scalar']:.2f}->{100*pg['pernode']:.2f}")
    cells = d['cells']
    for g, (b6t, pnt) in {0.05: (-0.9, None), 0.1: (-1.5, None),
                          0.2: (-3.9, -3.7)}.items():
        cc = [c for c in cells if c['gamma'] == g]
        b6 = 100*np.mean([c['acc']-c['pred_b6'] for c in cc])
        pn = 100*np.mean([c['acc']-c['pred_pernode'] for c in cc])
        ok = close(b6, b6t, 0.05) and (pnt is None or close(pn, pnt, 0.05))
        check(f'B7 bias at gamma={g}: {b6t}pp', ok,
              f'b6={b6:.2f} pernode={pn:.2f}')
    q0 = json.load(open(res('pn_part0.json')))['quantities']
    cv = lambda g: [a/b for a, b in zip(q0[g]['parity3']['sep_v'],
                                        q0['0.0']['parity3']['sep_v'])]
    s1, s2 = (max(cv('0.02'))-min(cv('0.02'))), (max(cv('0.2'))-min(cv('0.2')))
    check('B7 node-contraction spread 0.04->0.17 (arch0 parity3)',
          close(s1, 0.04, 5e-3) and close(s2, 0.17, 5e-3),
          f'{s1:.3f}->{s2:.3f}')
    sig0 = q0['0.0']['parity2']['sig_v']; sig2 = q0['0.2']['parity2']['sig_v']
    check('B7 sigma^2 rises ~0.87->0.98 (arch0; min-node 0.87, node means '
          '0.91->0.99)', min(sig0) < 0.88 and np.mean(sig2) > 0.97,
          f'min0={min(sig0):.3f} mean0={np.mean(sig0):.3f} '
          f'mean2={np.mean(sig2):.3f}')

    # ---------- B8 (RESULTS_BEYONDNOISE.md) ----------
    b = json.load(open(res('beyond_noise_law.json')))
    ch = b['channels']
    check('B8 300 cells / 80 predicted per channel',
          len(b['cells']) == 300 and
          all(ch[c]['n_pred'] == 80 for c in ch))
    tab = dict(dephasing=(0.836, 0.820, 5.9, -0.009, 0.976),
               amp_damping=(0.660, 0.493, 15.4, -0.029, 0.671),
               coherent=(0.796, 0.806, -1.5, 0.019, 0.942))
    for c, (r2, nr2, red, bias, mc) in tab.items():
        s = ch[c]
        ok = (close(s['collapse_r2'], r2, 5e-4) and
              close(s['naive_r2'], nr2, 5e-4) and
              close(s['mae_reduction_pct'], red, 0.05) and
              close(s['mean_bias'], bias, 5e-4) and
              close(s['min_cos'], mc, 5e-4))
        check(f'B8 table row {c}', ok,
              f"{s['collapse_r2']:.3f}/{s['naive_r2']:.3f}/"
              f"{s['mae_reduction_pct']:+.1f}%/{s['mean_bias']:+.3f}/"
              f"{s['min_cos']:.3f}")
    check('B8 all channels below depol R2=0.927 and below 0.9 bar',
          all(ch[c]['collapse_r2'] < 0.9 for c in ch))
    check('B8 amp_damping c -> 0.65 (mean_c at eta=0.15)',
          close(ch['amp_damping']['per_eta']['0.15']['mean_c'], 0.65, 5e-3),
          f"{ch['amp_damping']['per_eta']['0.15']['mean_c']:.3f}")
    dmin = ch['dephasing']['min_cos']
    if dmin < 0.98:
        flag('B8 wording: mechanism text says dephasing "cos >= 0.98"; actual '
             f'min {dmin:.4f} (= the table\'s own 0.976). Rounding-level, '
             'no number challenged.')

    # ---------- B9 (RESULTS_MARGINEST.md) ----------
    m = json.load(open(res('marginest_law.json'))); rows = m['rows']
    check('B9 60 configs, D0 range 0.05-1.44',
          len(rows) == 60 and
          close(min(r['D0'] for r in rows), 0.052, 5e-3) and
          close(max(r['D0'] for r in rows), 1.44, 5e-3))
    tab9 = {250: (6.1, 8.8, 0.1, 6.4), 1000: (1.4, 3.4, -0.2, 3.0),
            4000: (0.4, 1.5, -0.0, 1.4), 16000: (0.1, 0.7, -0.0, 0.7)}
    for Sp, (nb, nr, cb, cr) in tab9.items():
        sub = [r for r in rows if r['S_pilot'] == Sp]
        v = (100*np.mean([r['naive']['bias'] for r in sub]),
             100*np.mean([r['naive']['rmse'] for r in sub]),
             100*np.mean([r['corr_pilot']['bias'] for r in sub]),
             100*np.mean([r['corr_pilot']['rmse'] for r in sub]))
        s = m['summary']['by_pilot'][str(Sp)]
        ok = (all(close(a, b, 0.05) for a, b in zip(v, (nb, nr, cb, cr))) and
              close(100*s['naive_bias'], v[0], 1e-9))
        check(f'B9 table row S_pilot={Sp}', ok,
              'got %.1f/%.1f/%+.1f/%.1f' % v)
    w = m['worst_naive_bias']
    check('B9 worst naive bias +41% (arch2 parity3 250, D0=0.052)',
          w['arch'] == 2 and w['task'] == 'parity3' and
          close(100*w['bias'], 41.4, 0.1) and close(w['D0'], 0.052, 5e-4))
    p3 = {r['arch']: 100*r['naive']['bias'] for r in rows
          if r['task'] == 'parity3' and r['S_pilot'] == 250}
    check('B9 "+18%" reconstructs as parity-3 across-arch mean at 250',
          close(np.mean(list(p3.values())), 18.3, 0.1),
          f"mean={np.mean(list(p3.values())):.1f}% "
          f"(arch0 {p3[0]:+.1f}, arch1 {p3[1]:+.1f}, arch2 {p3[2]:+.1f})")
    flag('B9 wording: write-up attributes the +18% to "parity-3 on arch 0"; '
         f'arch 0 itself is {p3[0]:+.1f}%. +18% is the parity-3 mean over the '
         'three architectures; the arch-resolved worst is the +41% arch-2 '
         'case quoted in the same sentence.')
    cpb = sorted(abs(r['corr_pilot']['bias']) for r in rows)
    n_over = sum(1 for v in cpb if v > 0.008)
    check('B9 corr_pilot bias small everywhere (max +1.8%, worst config)',
          close(100*cpb[-1], 1.80, 0.02), f'max {100*cpb[-1]:.2f}%')
    flag(f'B9 wording: "<=0.8% on every config" holds for {60-n_over}/60 '
         f'configs; {n_over} exceed it (1.04-1.80%), including the +41% '
         'arch2/parity3/250 case the sentence explicitly includes. The '
         'budget-averaged biases in the table (<=0.2%) are correct.')
    r_w = [r for r in rows if r['arch'] == 2 and r['task'] == 'parity3'
           and r['S_pilot'] == 250][0]
    check('B9 corr_pilot ~ corr_exact on worst config (+1.80 vs +1.61%)',
          close(100*r_w['corr_pilot']['bias'], 1.80, 0.02) and
          close(100*r_w['corr_exact']['bias'], 1.61, 0.02))
    p3r = 100*np.mean([r['corr_pilot']['rmse'] for r in rows
                       if r['task'] == 'parity3' and r['S_pilot'] == 250])
    check('B9 parity-3 corrected RMSE ~13% at 250 (task mean)',
          close(p3r, 13.5, 0.2), f'{p3r:.1f}%')
    mj = [r for r in rows if r['task'] == 'majority3' and r['S_pilot'] == 250]
    check('B9 majority3 D0~1.08 (across-arch mean), naive bias ~+0.1%',
          close(np.mean([r['D0'] for r in mj]), 1.08, 5e-3) and
          abs(100*np.mean([r['naive']['bias'] for r in mj])) < 0.15,
          f"D0mean={np.mean([r['D0'] for r in mj]):.2f} "
          f"bias={100*np.mean([r['naive']['bias'] for r in mj]):+.2f}%")


STAGES = {'b7': stage_b7, 'b8:coherent': lambda: stage_b8_channel('coherent'),
          'b8:amp_damping': lambda: stage_b8_channel('amp_damping'),
          'b8:dephasing': lambda: stage_b8_channel('dephasing'),
          'b8:agg': stage_b8_agg, 'b9': stage_b9, 'claims': stage_claims}

if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    names = list(STAGES) if which == 'all' else [which]
    for n in names:
        STAGES[n]()
    if which == 'all' and os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH)
    if FAILED:
        print('FAILED:', FAILED); sys.exit(1)
    print('ALL CHECKS PASSED' + (' (with FLAGs above)' if which in
          ('all', 'claims') else ''))
