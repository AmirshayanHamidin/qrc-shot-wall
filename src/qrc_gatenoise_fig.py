import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('gate_noise_law.json'))
cells = d['cells']; GAMMAS = d['gammas']; BUD = d['budgets']
def sub(arch, task, gamma):
    rs = sorted([c for c in cells if c['arch']==arch and c['task']==task
                 and abs(c['gamma']-gamma)<1e-9], key=lambda c: c['shots'])
    return rs

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
cmap = plt.cm.viridis(np.linspace(0, 0.9, len(GAMMAS)))
arch, task = 0, 'majority3'

# Panel A: raw shots -> the wall moves right with gate noise
for gi, g in enumerate(GAMMAS):
    rs = sub(arch, task, g)
    ax[0].plot([r['shots'] for r in rs], [r['acc'] for r in rs], '-o', ms=4,
               color=cmap[gi], label=f'$\\gamma$={g}')
ax[0].set_xscale('log'); ax[0].set_xlabel('shots per step  $S$')
ax[0].set_ylabel('achievable accuracy')
ax[0].set_title(f'A. Gate noise moves the wall right\n(arch {arch}, {task})')
ax[0].legend(fontsize=8, title='gate noise'); ax[0].grid(alpha=0.3)

# Panel B: rescaled by c^2 -> collapse
for gi, g in enumerate(GAMMAS):
    rs = sub(arch, task, g)
    ax[1].plot([r['S_eff'] for r in rs], [r['acc'] for r in rs], '-o', ms=4,
               color=cmap[gi], label=f'$\\gamma$={g}')
ax[1].set_xscale('log')
ax[1].set_xlabel('effective shots  $S\\cdot c(\\gamma)^2$  (parameter-free)')
ax[1].set_ylabel('achievable accuracy')
ax[1].set_title('B. Fidelity factor collapses the curves\n$c(\\gamma)$ from noiseless features')
ax[1].grid(alpha=0.3)

# Panel C: prediction error vs gamma, law vs naive (all tasks/arches aggregated)
pg = d['per_gamma']; gs = [float(k) for k in pg]
mae_law = [pg[k]['mae_law'] for k in pg]; mae_naive = [pg[k]['mae_naive'] for k in pg]
ax[2].plot(gs, np.array(mae_naive)*100, 's--', color='crimson',
           label='naive (no fidelity factor)')
ax[2].plot(gs, np.array(mae_law)*100, 'o-', color='navy',
           label='law + $c(\\gamma)^2$ factor')
ax[2].set_xlabel('gate-noise strength  $\\gamma$')
ax[2].set_ylabel('mean abs. prediction error (pp)')
ax[2].set_title(f'C. Fidelity factor wins, more so as $\\gamma$ grows\n'
                f'collapse $R^2$={d["collapse_r2"]:.3f} vs naive {d["naive_r2"]:.3f} '
                f'({d["n_pred"]} cells)')
ax[2].legend(fontsize=9); ax[2].grid(alpha=0.3); ax[2].set_ylim(0, None)

plt.tight_layout()
plt.savefig('qrc_gate_noise.png', dpi=130)
print('figure written', d['collapse_r2'], d['naive_r2'])
