"""
B12 — Reservoir topology sweep: is "information-per-shot" a designable knob?

The README's redirected question: can reservoir dynamics be designed so task-relevant
signal concentrates in a few high-magnitude observables, buying more accuracy per shot?
Every prior benchmark used ONE coupling graph (a nearest-neighbour brickwork chain).
B12 sweeps the coupling topology (chain / ring / star / all-to-all) x depth (1,2 layers),
holding qubit count, injection, virtual nodes, feature set, tasks and readout fixed.

Two design-time (noiseless) quantities per (topology, task):
  * IPS  = Sum_i  dmu_i^2 / sigma_i^2   -- class-discrimination SNR^2 gained *per shot*
           (the additive-SNR quantity from B7; dmu = between-class mean feature
           separation, sigma_i^2 = mean single-shot feature variance = mean_t(1-f_ti^2)).
           This is the law-relevant "information per shot".
  * PR   = (Sum dmu_i^2)^2 / Sum dmu_i^4  -- participation ratio of the separation vector:
           how many observables carry the signal (LOW PR = concentrated in few features,
           the README's "few high-magnitude observables").

Pre-registered hypotheses (stated before running):
  (H1) Topology is a real lever on information-per-shot: at MATCHED exact-readout accuracy
       (parity tasks saturate to exact~1.0 for every topology), IPS varies >=2x across
       topologies, and higher IPS predicts higher shot-limited accuracy at a fixed budget
       (positive rank correlation, pooled over topology x task).
  (H2) The README's intuition -- CONCENTRATION helps: lower PR (signal in fewer
       observables) correlates with higher IPS / higher retained accuracy.
  Falsifiers: IPS is topology-invariant, or does not predict retained accuracy (=> topology
  is not a design knob); and/or PR is uncorrelated with retention (=> "concentrate into few
  observables" is the WRONG framing -- total SNR^2 per shot, not concentration, is what
  matters). Either falsifier is reported honestly.

Simulation only (numpy density matrix + qiskit unitary). No hardware, no runtime service.

Usage:
  python3 qrc_topology.py build <topo> <layers>   # -> topo_<topo>_L<layers>.npz
  python3 qrc_topology.py eval                      # -> topology_law.json
"""
import sys, os, json
import numpy as np
from itertools import combinations
from qiskit import QuantumCircuit
from qiskit.quantum_info import Operator

from qrc_law import make_inputs, task_labels, zdiags, feats_from_P, perf, WASH, T

NQ = 6
NODES = 3
K = 4
GAIN = 1.0
CLF_TASKS = ['parity2', 'parity3', 'parity4', 'delay_xor', 'majority3']

def edges(topo, nq):
    if topo == 'chain':
        return [(i, i+1) for i in range(nq-1)]
    if topo == 'ring':
        return [(i, i+1) for i in range(nq-1)] + [(nq-1, 0)]
    if topo == 'star':
        return [(0, i) for i in range(1, nq)]
    if topo == 'all2all':
        return list(combinations(range(nq), 2))
    raise ValueError(topo)

def build_U(topo, layers, seed):
    r = np.random.default_rng(seed)
    qc = QuantumCircuit(NQ)
    E = edges(topo, NQ)
    for _ in range(layers):
        for q in range(NQ):
            qc.rx(r.uniform(0, 2*np.pi), q)
            qc.rz(r.uniform(0, 2*np.pi), q)
        for (a, b) in E:
            qc.rzz(r.uniform(0, np.pi), a, b)
    return Operator(qc).data

def build(topo, layers, seed=3):
    dim = 2**NQ
    U = build_U(topo, layers, seed); Ud = U.conj().T
    gmax = 0.5*np.pi/0.2 * GAIN
    bits, u = make_inputs()

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
    np.savez_compressed(f'topo_{topo}_L{layers}.npz', P=P)
    print(f'built {topo} L{layers}', flush=True)

def design_metrics(Fex, y):
    """IPS = Sum dmu^2/sigma^2 ; PR = participation ratio of dmu^2 ; top3 fraction."""
    X = Fex[WASH:]; yy = y[WASH:]
    mu1 = X[yy == 1].mean(0); mu0 = X[yy == 0].mean(0)
    dmu = mu1 - mu0
    sig2 = np.clip(1.0 - (X**2).mean(0), 1e-6, None)   # mean single-shot variance per feat
    ips = float(np.sum(dmu**2 / sig2))
    w = dmu**2
    pr = float((w.sum()**2) / np.sum(w**2)) if np.sum(w**2) > 0 else float(len(w))
    order = np.sort(w)[::-1]
    top3 = float(order[:3].sum() / w.sum()) if w.sum() > 0 else 0.0
    return ips, pr, top3, float(np.linalg.norm(dmu))

def evaluate_all(topos=('chain', 'ring', 'star', 'all2all'), layers_list=(1, 2),
                 budgets=(250, 1000, 4000, 16000, 64000), sample_seeds=(1, 2, 3)):
    bits, u = make_inputs()
    labels = task_labels(bits)
    Z = zdiags(NQ)
    results = []
    for topo in topos:
        for L in layers_list:
            f = f'topo_{topo}_L{L}.npz'
            if not os.path.exists(f):
                continue
            P = np.load(f)['P']
            Fex = feats_from_P(P, Z, 0)
            for tname in CLF_TASKS:
                y, kind = labels[tname]
                ips, pr, top3, dnorm = design_metrics(Fex, y)
                floor = perf(np.zeros((T, 1)) + u[:, None], y, kind, K)
                pex = perf(Fex, y, kind, K)
                for S in budgets:
                    accs = []
                    for ss in sample_seeds:
                        rng = np.random.default_rng(ss)
                        Fn = feats_from_P(P, Z, S, rng)
                        accs.append(perf(Fn, y, kind, K))
                    pn = float(np.mean(accs))
                    denom = pex - floor
                    R = float((pn - floor)/denom) if abs(denom) > 0.02 else None
                    results.append(dict(topo=topo, layers=L, task=tname, shots=S,
                                        ips=ips, pr=pr, top3=top3, dnorm=dnorm,
                                        floor=float(floor), exact=float(pex),
                                        noisy=pn, retained=R))
                print(f'{topo:8s} L{L} {tname:10s} IPS={ips:7.2f} PR={pr:5.2f} '
                      f'exact={pex:.3f} noisy@4k={[r["noisy"] for r in results if r["topo"]==topo and r["layers"]==L and r["task"]==tname and r["shots"]==4000][0]:.3f}',
                      flush=True)
    json.dump(results, open('topology_law.json', 'w'), indent=1)
    print(f'{len(results)} cells saved', flush=True)

if __name__ == '__main__':
    if sys.argv[1] == 'build':
        build(sys.argv[2], int(sys.argv[3]))
    else:
        evaluate_all()
