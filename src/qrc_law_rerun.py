"""
B5 RESTORATION (2026-07-04) — 8-seed observation re-run of the 150-cell grid.
Closes finding #2 of the B5 audit: published obs used an (undocumented) 2-seed
protocol whose noise floor exceeded the claimed agreement. Here: sampling seeds
1..8, documented, per-seed accuracies stored so anyone can recompute the floor.

Observation convention = law_eval_arch.py (the committed pipeline the audit used):
retrained readout per noisy draw — qrc_law.perf (StandardScaler + LogisticRegression,
best C over {0.1,1,10,100} on the 30% chronological test split).

Usage:
  python3 qrc_law_rerun.py obs <arch_id> <lo> <hi>  # seeds lo..hi inclusive
                                                    -> lawobs{arch}_{lo}_{hi}.json
  python3 qrc_law_rerun.py agg                      -> ../results/law_rerun.json
"""
import sys, os, json, glob
import numpy as np
import qrc_law as L

BUDGETS = (250, 1000, 4000, 16000, 64000)
SEEDS = (1, 2, 3, 4, 5, 6, 7, 8)
CLF_TASKS = ('parity2', 'parity3', 'parity4', 'delay_xor', 'majority3')


def obs(arch_id, lo, hi):
    bits, u = L.make_inputs()
    labels = L.task_labels(bits)
    d = np.load(f'law_arch{arch_id}.npz')
    P, nq, K, nodes = d['P'], int(d['nq']), int(d['K']), int(d['nodes'])
    Z = L.zdiags(nq)
    res = {}
    for S in BUDGETS:
        for ss in range(lo, hi + 1):
            Fn = L.feats_from_P(P, Z, S, np.random.default_rng(ss))
            for tname in CLF_TASKS:
                y, kind = labels[tname]
                res.setdefault(tname, {}).setdefault(str(S), {})[str(ss)] = \
                    float(L.perf(Fn, y, kind, K))
        print(f'a{arch_id} S={S} seeds {lo}-{hi} done', flush=True)
    json.dump(res, open(f'lawobs{arch_id}_{lo}_{hi}.json', 'w'), indent=1)


def meta(arch_id):
    """floor + exact (retrained convention) per task, computed once."""
    bits, u = L.make_inputs()
    labels = L.task_labels(bits)
    d = np.load(f'law_arch{arch_id}.npz')
    P, nq, K, nodes = d['P'], int(d['nq']), int(d['K']), int(d['nodes'])
    Z = L.zdiags(nq)
    Fex = L.feats_from_P(P, Z, 0)
    out = {}
    for tname in CLF_TASKS:
        y, kind = labels[tname]
        out[tname] = dict(floor=float(L.perf(u[:, None] * np.ones((1, 1)), y, kind, K)),
                          exact=float(L.perf(Fex, y, kind, K)))
    json.dump(out, open(f'lawmeta{arch_id}.json', 'w'), indent=1)
    print(f'a{arch_id} meta done', flush=True)


def agg():
    cells = []
    for a in range(6):
        pred = {(r['task'], r['shots']): r for r in json.load(open(f'lawpred{a}.json'))}
        mt = json.load(open(f'lawmeta{a}.json'))
        ob = {}
        for f in sorted(glob.glob(f'lawobs{a}_*.json')):
            part = json.load(open(f))
            for tname, by_s in part.items():
                for S, by_seed in by_s.items():
                    ob.setdefault(tname, {}).setdefault(S, {}).update(by_seed)
        for tname in CLF_TASKS:
            for S in BUDGETS:
                seeds = ob[tname][str(S)]
                accs = [seeds[str(ss)] for ss in SEEDS]
                p = pred[(tname, S)]
                cells.append(dict(
                    arch=a, task=tname, shots=S,
                    pred=p['pred'], exact_fixed_acc=p['exact_fixed_acc'],
                    obs_mean=float(np.mean(accs)), obs_std=float(np.std(accs, ddof=1)),
                    obs_seeds=accs, n_seeds=len(accs),
                    floor=mt[tname]['floor'], exact=mt[tname]['exact']))
    pr = np.array([c['pred'] for c in cells])
    obm = np.array([c['obs_mean'] for c in cells])
    sem2 = np.array([c['obs_std']**2 / c['n_seeds'] for c in cells])
    resid = pr - obm
    ss_tot = float(np.sum((obm - obm.mean())**2))
    r2 = 1 - float(np.sum(resid**2)) / ss_tot
    # noise-corrected R2: subtract mean obs sampling variance from the residual
    r2_corr = 1 - max(float(np.sum(resid**2)) - float(np.sum(sem2)), 0.0) / ss_tot
    mae = float(np.mean(np.abs(resid)))
    floor_mae = float(np.mean(np.sqrt(2 / np.pi) * np.sqrt(sem2)))  # E|N(0,sem)|
    by_budget = {}
    for S in BUDGETS:
        m = [c for c in cells if c['shots'] == S]
        p2 = np.array([c['pred'] for c in m]); o2 = np.array([c['obs_mean'] for c in m])
        by_budget[S] = dict(
            r2=float(1 - np.sum((p2-o2)**2) / np.sum((o2-o2.mean())**2)),
            mae_pp=float(100*np.mean(np.abs(p2-o2))),
            bias_pp=float(100*np.mean(p2-o2)))
    summary = dict(n_cells=len(cells), n_seeds=len(SEEDS),
                   r2=float(r2), r2_noise_corrected=float(r2_corr),
                   mae_pp=float(100*mae), bias_pp=float(100*np.mean(resid)),
                   mae_floor_8seed_pp=float(100*floor_mae),
                   by_budget=by_budget)
    json.dump(dict(summary=summary, cells=cells),
              open('../results/law_rerun.json', 'w'), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'obs':
        obs(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    elif sys.argv[1] == 'meta':
        meta(int(sys.argv[2]))
    else:
        agg()
