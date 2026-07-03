import sys, json
import numpy as np
import qrc_law as L

arch_id = int(sys.argv[1])
bits, u = L.make_inputs()
labels = L.task_labels(bits)
res = []
d = np.load(f'law_arch{arch_id}.npz')
P, nq, K, nodes = d['P'], int(d['nq']), int(d['K']), int(d['nodes'])
Z = L.zdiags(nq)
Fex = L.feats_from_P(P, Z, 0)
sig = np.median(Fex[L.WASH:].std(axis=0))
for tname, (y, kind) in labels.items():
    floor = L.perf(u[:, None]*np.ones((1, 1)), y, kind, K)
    pex = L.perf(Fex, y, kind, K)
    for S in (250, 1000, 4000, 16000, 64000):
        accs = [L.perf(L.feats_from_P(P, Z, S, np.random.default_rng(ss)), y, kind, K)
                for ss in (1, 2)]
        pn = float(np.mean(accs))
        snr = float(sig*np.sqrt(S))
        den = pex - floor
        R = float((pn-floor)/den) if abs(den) > 0.02 else None
        res.append(dict(arch=arch_id, task=tname, kind=kind, shots=S, snr=snr,
                        floor=float(floor), exact=float(pex), noisy=pn, retained=R))
json.dump(res, open(f'law_part{arch_id}.json', 'w'))
print(f'arch {arch_id}: {len(res)} cells')
