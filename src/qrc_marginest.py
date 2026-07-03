"""
Benchmark 9 - Cheap margin/separation estimation at scale. (simulation only)
See RESULTS_MARGINEST.md for the framing and pre-registered hypotheses.
Estimators of the design-time separation D0 = ||mu1-mu0|| (noiseless features):
  naive      : ||muhat1-muhat0|| from a pilot of S_pilot shots/timestep
  corr_exact : naive^2 - V (V = EXACT shot-noise variance of the mean-diff)   [idealized]
  corr_pilot : naive^2 - Vhat (Vhat estimated from the SAME noisy pilot counts) [realizable]
"""
import json, time
import numpy as np
import qrc_law as L
from itertools import combinations

ARCHS = [0, 1, 2]
CLF = ['parity2','parity3','parity4','delay_xor','majority3']
PILOTS = [250, 1000, 4000, 16000]
NSEED = 40
WASH = L.WASH
bits, u = L.make_inputs()
labels = L.task_labels(bits)

def sample_feats_and_var(P, Z, shots, rng):
    """Return noisy features (T,Fn) AND plug-in 1-shot variance estimate (T,Fn) from same draw."""
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    feat = np.zeros((Tn, nodes*F)); vest = np.zeros((Tn, nodes*F))
    for t in range(Tn):
        for v in range(nodes):
            c = rng.multinomial(shots, P[t, v]); ph = c/shots
            m1 = Z @ ph; m2 = (Z*Z) @ ph
            feat[t, v*F:(v+1)*F] = m1
            vest[t, v*F:(v+1)*F] = np.maximum(m2 - m1*m1, 0.0)
    return feat, vest

def exact_var(P, Z):
    Tn, nodes, dim = P.shape; F = Z.shape[0]
    out = np.zeros((Tn, nodes*F))
    for t in range(Tn):
        for v in range(nodes):
            p = P[t, v]; m1 = Z @ p; m2 = (Z*Z) @ p
            out[t, v*F:(v+1)*F] = m2 - m1*m1
    return out

def run():
    t0 = time.time(); rows = []
    for arch_id in ARCHS:
        L.build(arch_id)
        d = np.load(f'law_arch{arch_id}.npz')
        P, nq = d['P'], int(d['nq'])
        Z = L.zdiags(nq)
        Fex = L.feats_from_P(P, Z, 0)
        var1 = exact_var(P, Z)[WASH:]
        for tname in CLF:
            y01, _ = labels[tname]; ys = y01[WASH:]
            Xs = Fex[WASH:]
            m1m, m0m = ys==1, ys==0
            N1, N0 = m1m.sum(), m0m.sum()
            D0 = float(np.linalg.norm(Xs[m1m].mean(0) - Xs[m0m].mean(0)))
            V_exact_coef = (var1[m1m].sum(0)/N1**2 + var1[m0m].sum(0)/N0**2)  # /Sp later
            for Sp in PILOTS:
                nv=[]; ce=[]; cp=[]
                for s in range(NSEED):
                    rng = np.random.default_rng(1000*arch_id+37*s+Sp)
                    Fn, Ven = sample_feats_and_var(P, Z, Sp, rng)
                    Fn=Fn[WASH:]; Ven=Ven[WASH:]
                    dn2 = float(np.sum((Fn[m1m].mean(0)-Fn[m0m].mean(0))**2))
                    Vex = float(np.sum(V_exact_coef)/Sp)
                    Vpi = float(np.sum(Ven[m1m].sum(0)/N1**2 + Ven[m0m].sum(0)/N0**2)/Sp)
                    nv.append(np.sqrt(dn2)); ce.append(np.sqrt(max(dn2-Vex,0))); cp.append(np.sqrt(max(dn2-Vpi,0)))
                nv=np.array(nv); ce=np.array(ce); cp=np.array(cp)
                def stats(a): return dict(bias=float(a.mean()/D0-1), rmse=float(np.sqrt(np.mean((a-D0)**2))/D0))
                rows.append(dict(arch=arch_id, task=tname, D0=D0, S_pilot=Sp,
                                 naive=stats(nv), corr_exact=stats(ce), corr_pilot=stats(cp)))
        print(f'arch {arch_id} {time.time()-t0:.1f}s', flush=True)
    json.dump(rows, open('b9_marginest.json','w'), indent=1)
    print(f'{len(rows)} rows {time.time()-t0:.1f}s')

if __name__=='__main__':
    run()
