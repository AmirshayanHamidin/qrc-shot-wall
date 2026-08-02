"""
B5 restoration completion (2026-08-02) - the 30 regression cells.
Pre-registered in audits/PREREG_B5_REG.md (commit ee4ad4c) BEFORE this file ran.
8-seed observation protocol over narma2_reg x ARCHS 0-5 x budgets (250..64000);
committed conventions only: qrc_law.build / feats_from_P / perf / floor proxy.

Usage:
  python3 qrc_law_reg_rerun.py obs <arch_id>   -> lawreg{arch}.json
  python3 qrc_law_reg_rerun.py agg             -> ../results/law_reg_rerun.json
"""
import sys, json, glob
import numpy as np
import qrc_law as L

BUDGETS = (250, 1000, 4000, 16000, 64000)
SEEDS = (1, 2, 3, 4, 5, 6, 7, 8)
TASK = 'narma2_reg'


def obs(arch_id):
    bits, u = L.make_inputs()
    y, kind = L.task_labels(bits)[TASK]
    d = np.load(f'law_arch{arch_id}.npz')
    P, nq, K, nodes = d['P'], int(d['nq']), int(d['K']), int(d['nodes'])
    Z = L.zdiags(nq)
    Fex = L.feats_from_P(P, Z, 0)
    exact = float(L.perf(Fex, y, kind, K))
    floor = float(L.perf(np.zeros((L.T, 1)) + u[:, None], y, kind, K))
    out = dict(arch=arch_id, task=TASK, exact=exact, floor=floor, cells={})
    for S in BUDGETS:
        seedvals = {}
        for ss in SEEDS:
            Fn = L.feats_from_P(P, Z, S, np.random.default_rng(ss))
            seedvals[str(ss)] = float(L.perf(Fn, y, kind, K))
        out['cells'][str(S)] = seedvals
        print(f'a{arch_id} S={S} done', flush=True)
    json.dump(out, open(f'lawreg{arch_id}.json', 'w'), indent=1)


def agg():
    cells = []
    for f in sorted(glob.glob('lawreg[0-9].json')):
        a = json.load(open(f))
        for S in BUDGETS:
            vals = [a['cells'][str(S)][str(s)] for s in SEEDS]
            obs_mean = float(np.mean(vals))
            denom = a['exact'] - a['floor']
            ret = float((obs_mean - a['floor']) / denom) if abs(denom) > 0.02 else None
            cells.append(dict(arch=a['arch'], task=TASK, shots=S,
                              floor=a['floor'], exact=a['exact'],
                              obs_mean=obs_mean, obs_std=float(np.std(vals)),
                              obs_seeds=vals, n_seeds=len(SEEDS), retention=ret))
    reg_ret = {S: float(np.mean([c['retention'] for c in cells
                                 if c['shots'] == S and c['retention'] is not None]))
               for S in BUDGETS}
    # pre-registered clf comparison (H3): published law_rerun.json, same guard
    clf = json.load(open('../results/law_rerun.json'))['cells']
    clf_ret = {}
    for S in BUDGETS:
        r = [(c['obs_mean'] - c['floor']) / (c['exact'] - c['floor'])
             for c in clf if c['shots'] == S and abs(c['exact'] - c['floor']) > 0.02]
        clf_ret[S] = float(np.mean(r))
    bars = dict(
        H1=dict(bar='mean reg retention @250 < 0.20', value=reg_ret[250],
                passed=bool(reg_ret[250] < 0.20)),
        H2=dict(bar='mean reg retention @64000 - @250 > 0.10',
                value=reg_ret[64000] - reg_ret[250],
                passed=bool(reg_ret[64000] - reg_ret[250] > 0.10)),
        H3=dict(bar='reg < clf mean retention @250 AND @1000',
                reg={250: reg_ret[250], 1000: reg_ret[1000]},
                clf={250: clf_ret[250], 1000: clf_ret[1000]},
                passed=bool(reg_ret[250] < clf_ret[250] and reg_ret[1000] < clf_ret[1000])))
    summary = dict(n_cells=len(cells), n_seeds=len(SEEDS),
                   mean_retention_by_budget_reg=reg_ret,
                   mean_retention_by_budget_clf_published=clf_ret,
                   prereg_bars=bars,
                   prereg='audits/PREREG_B5_REG.md @ ee4ad4c')
    json.dump(dict(cells=cells, summary=summary),
              open('../results/law_reg_rerun.json', 'w'), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'obs':
        obs(int(sys.argv[2]))
    else:
        agg()
