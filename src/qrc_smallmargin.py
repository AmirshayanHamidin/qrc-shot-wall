"""
B13 - Small-margin regime sweep: does the "information-per-shot" design rule
survive when exact accuracy is NOT saturated?

CONTEXT. B12 found that coupling topology moves the design-time information-per-
shot metric IPS = Sum_i dmu_i^2/sigma_i^2 by 14-56x and that IPS predicts shot-
limited accuracy (Spearman rho = +0.90 at 250 shots), with the star/hub reservoir
winning; the participation ratio PR (concentration) was uncorrelated (H2
falsified). But every B12 cell sat in parity's MAXIMAL-HEADROOM regime: exact-
readout accuracy = 1.000 for all 40 configurations, so topology could only act
through per-shot noise, never through expressivity. B12's own limitations section
and the README queue B13: repeat the sweep on the razor-thin-margin Mackey-Glass
family of B11, where exact separation is imperfect and topology may reshuffle.

DESIGN (everything identical to B12 except the input/task family):
  * Reservoirs: topology in {chain, ring, star, all2all} x depth {1, 2} layers,
    6 qubits, 3 virtual nodes, K=4, gain=1.0, unitary seed=3 - the same 8
    reservoirs as B12 (same build_U code, same seeds).
  * Family: B11's Mackey-Glass drive and its three balanced classification tasks
    (updown, accel, prodmed) - unchanged code from qrc_taskfam.py.
  * Protocol: B12's exact protocol - retrained readout per feature matrix
    (qrc_law.perf, C-grid logistic), budgets S in {250,1k,4k,16k,64k}, 3 sampling
    seeds, inputs-only floor per task. 8 x 3 = 24 configurations, 120 cells.
  * Design-time noiseless metrics per configuration: IPS, PR, top3, |dmu|
    (identical design_metrics code from qrc_topology.py).

PRE-REGISTERED HYPOTHESES (stated before any run):
  H1 (the lever survives small margins). Pooled over the 24 configurations,
      Spearman rho(log IPS, noisy accuracy) >= +0.5 with p < 0.01 at S = 250,
      and IPS still spreads >= 2x across topologies within each task.
      Falsifier: rho < +0.5 or n.s. => IPS as a design objective is an artifact
      of the matched-accuracy maximal-headroom regime and B12's design rule
      cannot be trusted off that regime.
  H2 (the design rule transfers). The star topology has the highest task-
      averaged noisy accuracy at S = 250 (averaged over depths), as in B12.
      Falsifier: any other topology wins => the hub recommendation is family-
      specific and must be demoted from a rule to an observation.
  H3 (concentration stays irrelevant). PR remains non-predictive of accuracy at
      S = 250 (p > 0.05). Falsifier: significant correlation in either direction
      => B12's negative about concentration was regime-specific.

  Pre-stated secondary analysis (because exact accuracy is NOT matched here,
  unlike B12): report rho(exact, acc@250) and the PARTIAL Spearman correlation of
  log IPS with acc@250 controlling for exact accuracy. The H1 "lever" claim is
  only meaningful if IPS carries predictive weight beyond expressivity; if the
  partial correlation collapses (< +0.3), we report that IPS @ small margins is
  confounded with expressivity and say so in the write-up.

Simulation only (numpy density matrix + qiskit unitary). No hardware, no runtime
service, no token files.

Usage (from src/):
  python3 qrc_smallmargin.py build <topo> <layers>   -> smtopo_<topo>_L<L>.npz
  python3 qrc_smallmargin.py eval <topo> <layers>    -> sm_part_<topo>_L<L>.json
  python3 qrc_smallmargin.py agg                     -> ../results/smallmargin_topology.json
"""
import sys, os, json
import numpy as np

from qrc_topology import edges, build_U, design_metrics, NQ, NODES, K, GAIN
from qrc_taskfam import make_inputs, task_labels, T, WASH
from qrc_law import zdiags, feats_from_P, perf

CLF_TASKS = ['updown', 'accel', 'prodmed']
BUDGETS = (250, 1000, 4000, 16000, 64000)
SAMPLE_SEEDS = (1, 2, 3)
TOPOS = ('chain', 'ring', 'star', 'all2all')
LAYERS = (1, 2)
USEED = 3          # same unitary seed as B12


def build(topo, layers):
    dim = 2**NQ
    U = build_U(topo, layers, USEED); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * GAIN
    u = make_inputs()                      # Mackey-Glass drive (B11 encoder)

    def reset_inject(rho, uu):
        th = gmax*uu
        psi = np.array([np.cos(th), np.sin(th)])
        r4 = rho.reshape(dim//2, 2, dim//2, 2)
        rest = np.trace(r4, axis1=1, axis2=3)
        return np.einsum('a,b,ij->iajb', psi, psi, rest).reshape(dim, dim)

    P = np.zeros((T, NODES, dim))
    for t in range(K, T):
        rho = np.zeros((dim, dim), complex); rho[0, 0] = 1
        for uu in u[t-K+1:t+1]:
            rho = reset_inject(rho, uu)
            rho = U @ rho @ Ud
        for v in range(NODES):
            if v > 0:
                rho = U @ rho @ Ud
            P[t, v] = np.real(np.diag(rho)).clip(0)
            P[t, v] /= P[t, v].sum()
    np.savez_compressed(f'smtopo_{topo}_L{layers}.npz', P=P)
    print(f'built {topo} L{layers} (Mackey-Glass drive)', flush=True)


def evaluate(topo, L):
    u = make_inputs()
    labels = task_labels(u)
    Z = zdiags(NQ)
    P = np.load(f'smtopo_{topo}_L{L}.npz')['P']
    Fex = feats_from_P(P, Z, 0)
    results = []
    for tname in CLF_TASKS:
        y, kind = labels[tname]
        ips, pr, top3, dnorm = design_metrics(Fex, y)
        floor = perf(u[:, None], y, kind, K)
        pex = perf(Fex, y, kind, K)
        for S in BUDGETS:
            accs = []
            for ss in SAMPLE_SEEDS:
                rng = np.random.default_rng(1000*ss + S)
                Fn = feats_from_P(P, Z, S, rng)
                accs.append(perf(Fn, y, kind, K))
            pn = float(np.mean(accs))
            denom = pex - floor
            R = float((pn - floor)/denom) if abs(denom) > 0.02 else None
            results.append(dict(topo=topo, layers=L, task=tname, shots=S,
                                ips=ips, pr=pr, top3=top3, dnorm=dnorm,
                                floor=float(floor), exact=float(pex),
                                noisy=pn, retained=R))
        print(f'{topo:8s} L{L} {tname:8s} IPS={ips:8.3f} PR={pr:5.2f} '
              f'floor={floor:.3f} exact={pex:.3f} '
              f'noisy@250={results[-5]["noisy"]:.3f}', flush=True)
    json.dump(results, open(f'sm_part_{topo}_L{L}.json', 'w'), indent=1)
    print(f'{topo} L{L}: {len(results)} cells', flush=True)


def _pooled(cells, S):
    sub = [r for r in cells if r['shots'] == S]
    x = np.log(np.array([r['ips'] for r in sub]))
    a = np.array([r['noisy'] for r in sub])
    p = np.array([r['pr'] for r in sub])
    e = np.array([r['exact'] for r in sub])
    return x, a, p, e


def _partial_spearman(x, y, z):
    """Spearman partial correlation of x,y controlling z (rank-transform then
    partial Pearson); t-test p-value with n-3 df."""
    from scipy.stats import rankdata, t as tdist
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    def pear(a, b):
        a = a - a.mean(); b = b - b.mean()
        return float(a @ b / np.sqrt((a @ a)*(b @ b)))
    rxy, rxz, ryz = pear(rx, ry), pear(rx, rz), pear(ry, rz)
    den = np.sqrt((1-rxz**2)*(1-ryz**2))
    if den < 1e-12:
        return 0.0, 1.0
    r = (rxy - rxz*ryz)/den
    n = len(x)
    tt = r*np.sqrt((n-3)/max(1e-12, 1-r**2))
    pv = 2*(1 - tdist.cdf(abs(tt), n-3))
    return float(r), float(pv)


def agg():
    from scipy.stats import spearmanr
    cells = []
    for topo in TOPOS:
        for L in LAYERS:
            f = f'sm_part_{topo}_L{L}.json'
            if os.path.exists(f):
                cells += json.load(open(f))
    # H1: pooled Spearman(log IPS, noisy acc) per budget
    h1 = {}
    for S in BUDGETS:
        x, a, p, e = _pooled(cells, S)
        rho, pv = spearmanr(x, a)
        h1[S] = dict(rho=float(rho), p=float(pv), n=len(x))
    # IPS spread per task
    spread = {}
    for tname in CLF_TASKS:
        ipss = sorted(set(r['ips'] for r in cells if r['task'] == tname))
        spread[tname] = float(ipss[-1]/ipss[0]) if ipss[0] > 0 else None
    # H2: topology ranking at 250 (mean over tasks and depths)
    rank250 = {}
    for topo in TOPOS:
        accs = [r['noisy'] for r in cells if r['shots'] == 250 and r['topo'] == topo]
        ipss = [r['ips'] for r in cells if r['shots'] == 250 and r['topo'] == topo]
        rank250[topo] = dict(acc=float(np.mean(accs)), ips=float(np.mean(ipss)))
    # H3: PR vs acc at each budget
    h3 = {}
    for S in BUDGETS:
        x, a, p, e = _pooled(cells, S)
        rho, pv = spearmanr(p, a)
        h3[S] = dict(rho=float(rho), p=float(pv))
    # secondary: exact-accuracy confound at 250
    x, a, p, e = _pooled(cells, 250)
    rho_e, pv_e = spearmanr(e, a)
    rho_part, pv_part = _partial_spearman(x, a, e)
    rho_ie, pv_ie = spearmanr(x, e)
    summary = dict(
        n_cells=len(cells),
        H1_rho_by_budget=h1,
        H1_ips_spread_by_task=spread,
        H1_pass=bool(h1[250]['rho'] >= 0.5 and h1[250]['p'] < 0.01 and
                     all(v is not None and v >= 2 for v in spread.values())),
        H2_rank250=rank250,
        H2_star_wins=bool(max(rank250, key=lambda k: rank250[k]['acc']) == 'star'),
        H3_pr_by_budget=h3,
        H3_pass=bool(h3[250]['p'] > 0.05),
        secondary=dict(rho_exact_acc250=float(rho_e), p=float(pv_e),
                       rho_logips_exact=float(rho_ie), p_ie=float(pv_ie),
                       partial_rho_logips_acc250_given_exact=rho_part,
                       partial_p=pv_part))
    out = dict(summary=summary, cells=cells)
    os.makedirs('../results', exist_ok=True)
    json.dump(out, open('../results/smallmargin_topology.json', 'w'), indent=1)
    print(json.dumps(summary, indent=1))


def posthoc():
    """POST-HOC (exploratory, labelled as such - run AFTER the pre-registered
    agg() verdicts were recorded): diagnose the pooled H1 failure by splitting
    the correlation within vs across tasks."""
    from scipy.stats import spearmanr, rankdata
    d = json.load(open('../results/smallmargin_topology.json'))
    cells = d['cells']
    within = {}
    for tn in CLF_TASKS:
        within[tn] = {}
        for S in BUDGETS:
            sub = [r for r in cells if r['task'] == tn and r['shots'] == S]
            rho, p = spearmanr(np.log([r['ips'] for r in sub]),
                               [r['noisy'] for r in sub])
            within[tn][S] = dict(rho=float(rho), p=float(p), n=len(sub))
    strat = {}
    for S in BUDGETS:
        xs, ys = [], []
        for tn in CLF_TASKS:
            sub = [r for r in cells if r['task'] == tn and r['shots'] == S]
            xs += list(rankdata(np.log([r['ips'] for r in sub])))
            ys += list(rankdata([r['noisy'] for r in sub]))
        rho, p = spearmanr(xs, ys)
        strat[S] = dict(rho=float(rho), p=float(p))
    pertask_winner = {}
    for tn in CLF_TASKS:
        m = {topo: float(np.mean([r['noisy'] for r in cells
                                  if r['task'] == tn and r['shots'] == 250
                                  and r['topo'] == topo])) for topo in TOPOS}
        pertask_winner[tn] = dict(m, winner=max(m, key=m.get))
    accel = [r for r in cells if r['task'] == 'accel']
    below = [r for r in accel if r['noisy'] <= r['floor']]
    ret = {}
    for S in (250, 1000):
        sub = [r for r in cells if r['shots'] == S and r['retained'] is not None]
        rho, p = spearmanr(np.log([r['ips'] for r in sub]),
                           [r['retained'] for r in sub])
        ret[S] = dict(rho=float(rho), p=float(p))
    d['post_hoc'] = dict(
        note='EXPLORATORY, computed after pre-registered verdicts. Within-task '
             'and stratified (rank-within-task) correlations diagnose the pooled '
             'H1 failure as cross-task heterogeneity, not a dead lever.',
        within_task_rho=within,
        stratified_rho=strat,
        per_task_winner_250=pertask_winner,
        accel_cells_at_or_below_floor=f'{len(below)}/{len(accel)}',
        pooled_rho_logips_retained=ret)
    json.dump(d, open('../results/smallmargin_topology.json', 'w'), indent=1)
    print(json.dumps(d['post_hoc'], indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'build':
        build(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == 'eval':
        evaluate(sys.argv[2], int(sys.argv[3]))
    elif sys.argv[1] == 'posthoc':
        posthoc()
    else:
        agg()
