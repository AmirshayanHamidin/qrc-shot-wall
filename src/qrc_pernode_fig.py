"""B7 figure: why the per-node/covariance correction barely helps.
A: real per-node contraction heterogeneity (nodes see different noisy depths).
B: collapse MAE per model vs gamma -- corrections nearly coincide with B6 scalar.
C: shot-budget-irreducible negative bias (obs-pred) that no scalar S_eff removes.
"""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

pl = json.load(open('pernode_law.json'))
q = json.load(open('pn_part0.json'))['quantities']
cells = pl['cells']
GAMS = [0.02, 0.05, 0.10, 0.15, 0.20]

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

# Panel A: per-node contraction, arch0 parity3
base = q['0.0']['parity3']['sep_v']
nodes = len(base)
for v in range(nodes):
    cv = [q[f'{g}']['parity3']['sep_v'][v]/base[v] for g in GAMS]
    ax[0].plot(GAMS, cv, 'o-', label=f'node {v} ({["K","K+1","K+2"][v]} noisy steps)')
ax[0].set_xlabel('gate-noise strength $\\gamma$')
ax[0].set_ylabel('per-node contraction $c_v(\\gamma)$')
ax[0].set_title('A. Per-node contraction IS heterogeneous\n(deeper nodes contract more) — arch0, parity3')
ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

# Panel B: MAE per model vs gamma
pg = pl['per_gamma']
models = ['naive', 'b6_scalar', 'scalar_cov', 'pernode']
labels = ['naive (no factor)', 'B6 scalar $S c^2$', '+ shot-noise cov', 'B7 per-node+cov']
styles = ['s--', 'o-', '^-', 'D-']
for m, lab, st in zip(models, labels, styles):
    ax[1].plot(GAMS, [pg[f'{g}'][m]*100 for g in GAMS], st, label=lab)
ax[1].set_xlabel('gate-noise strength $\\gamma$')
ax[1].set_ylabel('collapse MAE (pp)')
ax[1].set_title('B. Corrections barely beat the scalar factor\n(B7 vs B6: only %.1f%% MAE reduction)'
                % (pl['pernode_vs_b6_mae_reduction']*100))
ax[1].legend(fontsize=8); ax[1].grid(alpha=0.3)

# Panel C: residual bias obs-pred vs gamma
for m, lab, col in [('b6_scalar', 'B6 scalar', 'tab:orange'),
                    ('pernode', 'B7 per-node+cov', 'tab:red')]:
    key = 'pred_b6' if m == 'b6_scalar' else 'pred_pernode'
    bias = [np.mean([c['acc']-c[key] for c in cells if c['gamma'] == g])*100 for g in GAMS]
    ax[2].plot(GAMS, bias, 'o-', color=col, label=lab)
ax[2].axhline(0, color='k', lw=0.8)
ax[2].set_xlabel('gate-noise strength $\\gamma$')
ax[2].set_ylabel('mean(obs $-$ pred) (pp)')
ax[2].set_title('C. A shot-budget-IRREDUCIBLE negative bias\n(gate noise moves you OFF the noiseless curve)')
ax[2].legend(fontsize=8); ax[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('/tmp/qrc-shot-wall/figures/qrc_pernode.png', dpi=130)
print('figure saved')
