"""
PREREG_B3_GEN reconstruction generator (audits/PREREG_B3_GEN.md, registered 2026-08-02).

Reconstructs the B3 task-shape artifacts -- the parity-3 accuracy curve and its four
reference values (stored in results/task_shape.json, which is a file of record and is NOT
overwritten) -- from committed machinery only: qrc_design.reservoir_U / .feats (reservoir and
sampled features), qrc_benchmark.esn_features / .window_features (classical baselines),
qrc_law.perf (logistic readout; WASH set to the pinned B1/B2 washout constant 100). No
reservoir or readout logic is reimplemented here. All free choices are pinned in the
registration; this file only mechanizes them.

Chunked CLI (45 s bash-call limit):
  python3 qrc_taskshape_gen.py curve <budget> [bitseed]   # 3 noise seeds at one budget
  python3 qrc_taskshape_gen.py exact [bitseed]            # exact-readout reference
  python3 qrc_taskshape_gen.py classical [bitseed]        # linear + poly3 references
  python3 qrc_taskshape_gen.py esn <rho_sr> [bitseed]     # ESN tuning slice (one rho_sr)
  python3 qrc_taskshape_gen.py assemble                   # partials -> task_shape_recon.json + bars
  python3 qrc_taskshape_gen.py fig                        # figure from the assembled JSON
Partials are written to taskshape_parts/ in the working directory; assemble and fig
read/write repo-relative results/ and figures/ paths.
"""
import sys, os, json, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
REPO = os.path.dirname(HERE)
import qrc_law
from qrc_design import reservoir_U, feats
from qrc_benchmark import esn_features, window_features

qrc_law.WASH = 100   # pinned B1/B2 washout (registration); qrc_law's own module constant is 60
perf = qrc_law.perf

T = 1200             # pinned: committed qrc_gap_eval.T
BUDGETS = [400, 1200, 4000, 12000, 40000, 120000]
NOISE_SEEDS = (1, 2, 3)
GAIN = 0.5 * np.pi   # bits map to |0>/|1>: theta in {0, pi/2}
RHO_GRID = (0.5, 0.7, 0.9, 1.1, 1.3)
LEAK_GRID = (0.1, 0.3, 0.5, 0.7, 1.0)
PART = 'taskshape_parts'

def bits_and_labels(bitseed=5):
    b = np.random.default_rng(bitseed).integers(0, 2, T)
    y = np.array([b[t] ^ b[t-1] ^ b[t-2] if t >= 2 else 0 for t in range(T)])
    return b.astype(float), y

def save(name, obj):
    os.makedirs(PART, exist_ok=True)
    json.dump(obj, open(os.path.join(PART, name), 'w'), indent=1)
    print('saved', name, flush=True)

def cmd_curve(budget, bitseed=5):
    b, y = bits_and_labels(bitseed)
    U = reservoir_U(depth=3, coup=1.0, seed=7)
    accs = [perf(feats(b, U, GAIN, budget // 4, noise_seed=s), y, 'clf', 0)
            for s in NOISE_SEEDS]
    save(f'curve_b{budget}_s{bitseed}.json',
         dict(budget=budget, bitseed=bitseed, noise_seeds=list(NOISE_SEEDS), accs=accs))

def cmd_exact(bitseed=5):
    b, y = bits_and_labels(bitseed)
    U = reservoir_U(depth=3, coup=1.0, seed=7)
    acc = perf(feats(b, U, GAIN, 0, exact=True), y, 'clf', 0)
    save(f'exact_s{bitseed}.json', dict(bitseed=bitseed, qrc_exact=acc))

def cmd_classical(bitseed=5):
    from sklearn.preprocessing import PolynomialFeatures
    b, y = bits_and_labels(bitseed)
    W = window_features(b, 10)
    lin = perf(W, y, 'clf', 0)
    poly = perf(PolynomialFeatures(degree=3, include_bias=False).fit_transform(W), y, 'clf', 0)
    save(f'classical_s{bitseed}.json', dict(bitseed=bitseed, linear=lin, poly3_classical=poly))

def cmd_esn(rho_sr, bitseed=5):
    b, y = bits_and_labels(bitseed)
    rows = [dict(rho_sr=rho_sr, leak=leak,
                 acc=perf(esn_features(b, 84, seed=3, rho_sr=rho_sr, leak=leak), y, 'clf', 0))
            for leak in LEAK_GRID]
    save(f'esn_r{rho_sr}_s{bitseed}.json', rows)

def load(name):
    return json.load(open(os.path.join(PART, name)))

def block(bitseed):
    curve = {b: load(f'curve_b{b}_s{bitseed}.json') for b in BUDGETS
             if os.path.exists(os.path.join(PART, f'curve_b{b}_s{bitseed}.json'))}
    esn_rows = sum((load(f'esn_r{r}_s{bitseed}.json') for r in RHO_GRID
                    if os.path.exists(os.path.join(PART, f'esn_r{r}_s{bitseed}.json'))), [])
    best = max(esn_rows, key=lambda r: r['acc'])
    out = dict(
        bitseed=bitseed,
        budgets=sorted(curve),
        acc_mean=[float(np.mean(curve[b]['accs'])) for b in sorted(curve)],
        acc_std=[float(np.std(curve[b]['accs'])) for b in sorted(curve)],
        per_seed={str(b): curve[b]['accs'] for b in sorted(curve)},
        refs=dict(esn_tuned=best['acc'],
                  poly3_classical=load(f'classical_s{bitseed}.json')['poly3_classical'],
                  linear=load(f'classical_s{bitseed}.json')['linear'],
                  qrc_exact=load(f'exact_s{bitseed}.json')['qrc_exact']),
        esn_grid=esn_rows, esn_best=dict(rho_sr=best['rho_sr'], leak=best['leak']))
    return out

def cmd_assemble():
    stored = json.load(open(os.path.join(REPO, 'results', 'task_shape.json')))
    main = block(5)
    sens = block(6)
    am, refs = dict(zip(main['budgets'], main['acc_mean'])), main['refs']
    ret40 = (am[40000] - refs['linear']) / (refs['qrc_exact'] - refs['linear'])
    bars = dict(
        A1=dict(deltas={str(b): abs(am[b] - s) for b, s in zip(stored['budgets'], stored['acc_mean'])},
                bar='<=0.05 at every budget'),
        A2=dict(value=abs(refs['esn_tuned'] - stored['refs']['esn_tuned']), bar='<=0.05'),
        A3=dict(value=abs(refs['linear'] - stored['refs']['linear']), bar='<=0.04'),
        A4=dict(qrc_exact=refs['qrc_exact'], poly3=refs['poly3_classical'], bar='both >=0.995'),
        B1=dict(retention_40k=ret40, bar='>=0.80'),
        B2=dict(acc_4k=am[4000], esn=refs['esn_tuned'], acc_40k=am[40000],
                bar='acc(4k) < esn < acc(40k)'),
        B3=dict(acc_120k=am[120000], bar='>=0.97'))
    bars['A1']['pass'] = all(d <= 0.05 for d in bars['A1']['deltas'].values())
    bars['A2']['pass'] = bars['A2']['value'] <= 0.05
    bars['A3']['pass'] = bars['A3']['value'] <= 0.04
    bars['A4']['pass'] = refs['qrc_exact'] >= 0.995 and refs['poly3_classical'] >= 0.995
    bars['B1']['pass'] = ret40 >= 0.80
    bars['B2']['pass'] = am[4000] < refs['esn_tuned'] < am[40000]
    bars['B3']['pass'] = am[120000] >= 0.97
    import sklearn, qiskit, matplotlib
    out = dict(registration='audits/PREREG_B3_GEN.md', reconstruction=main,
               sensitivity_bitseed6=sens, bars=bars,
               stored_for_reference=stored,
               environment=dict(numpy=np.__version__, sklearn=sklearn.__version__,
                                qiskit=qiskit.__version__, matplotlib=matplotlib.__version__))
    json.dump(out, open(os.path.join(REPO, 'results', 'task_shape_recon.json'), 'w'), indent=1)
    for k in ('A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3'):
        print(k, 'PASS' if bars[k]['pass'] else 'FAIL', flush=True)
    print('retention_40k = %.4f' % ret40)

def cmd_fig():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    d = json.load(open(os.path.join(REPO, 'results', 'task_shape_recon.json')))
    g = json.load(open(os.path.join(REPO, 'results', 'gap_final.json')))
    # regression bar: audited rounded-input convention (AUDITS.md B3 flag 4): 3-dp inputs
    lin, mit, flo = round(g['refs']['linear_inputs'], 3), round(g['mitigated'][1], 3), round(g['refs']['exact_floor'], 3)
    reg_pct = 100 * (lin - mit) / (lin - flo)
    m, r = d['reconstruction'], d['reconstruction']['refs']
    cls_pct = 100 * d['bars']['B1']['retention_40k']
    fig, ax = plt.subplots(1, 2, figsize=(13, 5))
    ax[0].bar(['Regression\n(NARMA5)', 'Classification\n(temporal parity)'],
              [reg_pct, cls_pct], color=['#e85d5d', '#1a8a7a'], width=0.55)
    for i, v in enumerate([reg_pct, cls_pct]):
        ax[0].text(i, v + 2, f'{v:.0f}%', ha='center', fontweight='bold', fontsize=13)
    ax[0].set_ylim(0, 112)
    ax[0].set_yticks(range(0, 101, 20))
    ax[0].set_ylabel('% of quantum benefit surviving measurement')
    ax[0].set_title('Same reservoir, same budget (40k shots/step)')
    ax[1].axhline(r['qrc_exact'], color='gray', ls=':', label='QRC exact readout')
    ax[1].axhline(r['esn_tuned'], color='#2b4b8f', ls='--', label='tuned classical ESN')
    ax[1].axhline(r['linear'], color='#e85d5d', ls='--', label='linear on inputs (chance)')
    ax[1].errorbar(m['budgets'], m['acc_mean'], yerr=m['acc_std'], marker='s',
                   color='#1a8a7a', capsize=3, label='QRC (noisy readout)')
    ax[1].set_xscale('log')
    ax[1].set_xlabel('total shots per timestep')
    ax[1].set_ylabel('parity accuracy')
    ax[1].set_title('Classification climbs out of the noise (reconstruction)')
    ax[1].legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(REPO, 'figures', 'qrc_task_shape_recon.png'), dpi=120)
    print('figure written', flush=True)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'curve':
        cmd_curve(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 5)
    elif cmd == 'exact':
        cmd_exact(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    elif cmd == 'classical':
        cmd_classical(int(sys.argv[2]) if len(sys.argv) > 2 else 5)
    elif cmd == 'esn':
        cmd_esn(float(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 5)
    elif cmd == 'assemble':
        cmd_assemble()
    elif cmd == 'fig':
        cmd_fig()
