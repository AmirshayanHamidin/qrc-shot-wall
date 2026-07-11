"""
AUDIT (2026-07-11): B6 re-run driver. Executes ONE (arch, gamma) slice of the
committed src/qrc_gatenoise.py -- functions used verbatim, unmodified; slicing
exists only to fit a 45 s per-process sandbox cap. The deterministic gamma=0
reference (sep0) is recomputed identically in every slice.

Usage:  python3 audit_b6_rerun.py <arch_id> <gamma>
Output: rerun_a<arch>_g<gamma>.json in the CWD (35 cells per slice; 12 slices
cover the full 420-cell grid). Comparison summary: audits/b6_rerun_check.json.
Audit environment: numpy 2.2.6, sklearn 1.7.2, qiskit 2.5.0, CPU.
Result: all 420 cells bit-identical to results/gate_noise_law.json.
"""
import sys, json, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import qrc_gatenoise as G

arch_id = int(sys.argv[1]); gamma = float(sys.argv[2])
bits, u = G.make_inputs(); labels = G.task_labels(bits)
Z = G.zdiags(G.ARCHS[arch_id]['nq'])
P0 = G.build_P(arch_id, 0.0); Xex0 = G.feats_exact(P0, Z)
sep0 = {t: G.class_sep(Xex0, labels[t]) for t in G.CLF_TASKS}
P = P0 if gamma == 0.0 else G.build_P(arch_id, gamma)
Xex = Xex0 if gamma == 0.0 else G.feats_exact(P, Z)
res = []
for tname in G.CLF_TASKS:
    y01 = labels[tname]
    c = G.class_sep(Xex, y01) / sep0[tname]
    for S in G.BUDGETS:
        acc = G.achievable_acc(P, Z, y01, S)
        res.append(dict(arch=arch_id, task=tname, gamma=gamma, shots=S,
                        c=c, S_eff=S*c*c, acc=acc,
                        exact_sep=G.class_sep(Xex, y01)))
json.dump(res, open(f'rerun_a{arch_id}_g{gamma}.json', 'w'), indent=1)
print(f'a{arch_id} g={gamma}: {len(res)} cells')
