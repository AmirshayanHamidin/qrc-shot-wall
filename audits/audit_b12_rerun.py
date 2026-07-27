"""
AUDIT (2026-07-27, second session): B12 re-run driver. Executes the committed
src/qrc_topology.py via its OWN CLI / its own evaluate_all(), unmodified -- no
reimplementation. The only non-committed code is this thin phaser: build uses the
committed CLI verbatim; eval calls the committed evaluate_all() restricted to one
(topology, depth) slice per call so every process fits the 45 s sandbox cap; concat
joins the 8 slice outputs in the committed loop order (topo-major, then depth), which
reproduces the file of record exactly.

Phases (run from a scratch dir, never from results/):

  python3 audit_b12_rerun.py build             -> 8x topo_<t>_L<L>.npz  (committed CLI, ~1 s each)
  python3 audit_b12_rerun.py eval <topo> <L>   -> part_<topo>_L<L>.json (committed evaluate_all, ~7 s)
  python3 audit_b12_rerun.py concat            -> topology_law.json     (committed order)
  python3 audit_b12_rerun.py fig               -> qrc_topology.png      (committed fig script)
  python3 audit_b12_rerun.py check             -> b12_rerun_check.json  (comparison)

Audit environment: numpy 2.2.6, sklearn 1.7.2, qiskit 2.5.0, scipy 1.15.3,
matplotlib 3.10.9, CPU (same stack as all prior audits).

Result: results/topology_law.json reproduces BYTE-IDENTICALLY (md5 da7077bc..., all
200 cells, max |delta| = 0 on every stored field) and figures/qrc_topology.png
regenerates BYTE-IDENTICALLY (md5 a63f68c4...). Every headline claim of
RESULTS_TOPOLOGY.md and the README B12 paragraph recomputes to its published value
(rho table +0.90/-15 ... +0.37/0.018; ranking star 0.924/0.63; IPS spans 56x/46x/14x;
H2 rho -0.18 p 0.28, PR~IPS -0.25 p 0.12; exact = 1.000 for all 40 configs). One
wording-level flag, no number challenged: "|rho| < 0.1 at all larger budgets" misses
at S=1000, where rho(PR, acc) = -0.1015 (p = 0.53). See AUDITS.md 2026-07-27.
"""
import sys, os, json, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..'))
SRC = os.path.join(REPO, 'src')
TOPOS = ('chain', 'ring', 'star', 'all2all')
LAYERS = (1, 2)
BUDGETS = (250, 1000, 4000, 16000, 64000)
TASKS = ('parity2', 'parity3', 'parity4', 'delay_xor', 'majority3')

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def build():
    for t in TOPOS:
        for L in LAYERS:
            subprocess.run([sys.executable, os.path.join(SRC, 'qrc_topology.py'),
                            'build', t, str(L)], check=True)

def eval_slice(topo, L):
    sys.path.insert(0, SRC)
    import qrc_topology as QT
    QT.evaluate_all(topos=(topo,), layers_list=(L,))
    os.replace('topology_law.json', f'part_{topo}_L{L}.json')

def concat():
    allr = []
    for t in TOPOS:
        for L in LAYERS:
            allr += json.load(open(f'part_{t}_L{L}.json'))
    json.dump(allr, open('topology_law.json', 'w'), indent=1)
    print(f'{len(allr)} cells concatenated')

def fig():
    subprocess.run([sys.executable, os.path.join(SRC, 'qrc_topology_fig.py')], check=True)

def check():
    import numpy as np
    from scipy.stats import spearmanr
    ref_p = os.path.join(REPO, 'results', 'topology_law.json')
    fig_p = os.path.join(REPO, 'figures', 'qrc_topology.png')
    out = {'audit': 'B12 re-run 2026-07-27', 'head': None,
           'env': {}, 'md5': {}, 'cells': {}, 'claims': {}}
    import numpy, scipy, sklearn, qiskit
    out['env'] = {'numpy': numpy.__version__, 'scipy': scipy.__version__,
                  'sklearn': sklearn.__version__, 'qiskit': qiskit.__version__}
    try:
        import matplotlib; out['env']['matplotlib'] = matplotlib.__version__
    except ImportError:
        pass
    a, b = md5('topology_law.json'), md5(ref_p)
    out['md5']['topology_law.json'] = {'rerun': a, 'committed': b, 'byte_identical': a == b}
    if os.path.exists('qrc_topology.png'):
        fa, fb = md5('qrc_topology.png'), md5(fig_p)
        out['md5']['qrc_topology.png'] = {'rerun': fa, 'committed': fb, 'byte_identical': fa == fb}
    new, ref = json.load(open('topology_law.json')), json.load(open(ref_p))
    out['cells']['n'] = [len(new), len(ref)]
    fields = ['ips', 'pr', 'top3', 'dnorm', 'floor', 'exact', 'noisy', 'retained']
    mx = {f: 0.0 for f in fields}
    keymatch = True
    for rn, rr in zip(new, ref):
        keymatch &= all(rn[k] == rr[k] for k in ('topo', 'layers', 'task', 'shots'))
        for f in fields:
            x, y = rn[f], rr[f]
            if x is None or y is None:
                if x is not y:
                    mx[f] = float('inf')
                continue
            mx[f] = max(mx[f], abs(x - y))
    out['cells']['key_order_identical'] = keymatch
    out['cells']['max_abs_delta'] = mx
    # ---- headline claims, recomputed from the re-run file ----
    R = new
    configs = sorted({(r['topo'], r['layers'], r['task']) for r in R})
    def cell(c, S):
        return next(r for r in R if (r['topo'], r['layers'], r['task']) == c and r['shots'] == S)
    ex = [cell(c, 250)['exact'] for c in configs]
    out['claims']['exact_all_1.000'] = {'n_configs': len(configs),
                                        'all_exactly_1.0': all(e == 1.0 for e in ex)}
    spans = {}
    for t in TASKS:
        v = [cell(c, 250)['ips'] for c in configs if c[2] == t]
        spans[t] = {'min': min(v), 'max': max(v), 'span_x': max(v) / min(v)}
    out['claims']['ips_spans'] = spans   # published: parity3 56x, majority3 46x, delay_xor 14x
    rho_tab = {}
    for S in BUDGETS:
        ips = np.array([cell(c, S)['ips'] for c in configs])
        acc = np.array([cell(c, S)['noisy'] for c in configs])
        rho, p = spearmanr(np.log10(ips), acc)
        rho_tab[str(S)] = {'rho': round(float(rho), 4), 'p': float(p)}
    out['claims']['rho_logIPS_acc'] = rho_tab  # published: +0.90/+0.84/+0.57/+0.48/+0.37
    rank = {}
    for topo in TOPOS:
        rank[topo] = {'acc_250': round(float(np.mean([cell(c, 250)['noisy'] for c in configs if c[0] == topo])), 4),
                      'mean_ips': round(float(np.mean([cell(c, 250)['ips'] for c in configs if c[0] == topo])), 4)}
    out['claims']['ranking_250'] = rank  # published: star .924/.63 ring .828/.42 all2all .790/.33 chain .789/.46
    pr = np.array([cell(c, 250)['pr'] for c in configs])
    ips = np.array([cell(c, 250)['ips'] for c in configs])
    h2 = {}
    for S in BUDGETS:
        acc = np.array([cell(c, S)['noisy'] for c in configs])
        rho, p = spearmanr(pr, acc)
        h2[str(S)] = {'rho': round(float(rho), 4), 'p': round(float(p), 4)}
    rho, p = spearmanr(pr, ips)
    out['claims']['rho_PR_acc'] = h2  # published: -0.18 p 0.28 @250; write-up says |rho|<0.1 above
    out['claims']['rho_PR_IPS'] = {'rho': round(float(rho), 4), 'p': round(float(p), 4)}  # published -0.25/0.12
    out['claims']['flag_wording'] = ('"|rho| < 0.1 at all larger budgets" misses at S=1000: '
                                     'rho(PR,acc) = %.4f (p = %.2f); harmlessly non-significant, '
                                     'no number of record affected' % (h2['1000']['rho'], h2['1000']['p']))
    json.dump(out, open('b12_rerun_check.json', 'w'), indent=1)
    print(json.dumps(out['md5'], indent=1))
    print('max_abs_delta:', mx)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'build':
        build()
    elif cmd == 'eval':
        eval_slice(sys.argv[2], int(sys.argv[3]))
    elif cmd == 'concat':
        concat()
    elif cmd == 'fig':
        fig()
    elif cmd == 'check':
        check()
