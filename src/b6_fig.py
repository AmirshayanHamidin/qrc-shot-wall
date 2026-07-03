import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('b6_selfcal.json'))
rows = d['rows']

fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

# left: pred vs true, gauss_full Sp=8000, colored by target budget
ax = axes[0]
cmap = plt.cm.viridis
budgets = [250, 1000, 4000, 16000, 64000]
for i, S in enumerate(budgets):
    sel = [r for r in rows if r['variant']=='gauss_full' and r['S_pilot']==8000 and r['shots']==S]
    p = [r['acc_pred'] for r in sel]; t = [r['acc_true'] for r in sel]
    ax.scatter(t, p, s=22, alpha=0.75, color=cmap(i/4), label=f'S={S}')
ax.plot([0.4, 1.0], [0.4, 1.0], 'k--', lw=1)
ax.set_xlabel('true noisy accuracy'); ax.set_ylabel('self-calibrated prediction')
ax.set_title('v4 gauss_full, $S_{pilot}$=8000\nMAE=3.8 pts, $R^2$=0.915 (150 cells)')
ax.legend(fontsize=8, loc='upper left')

# right: MAE vs S_pilot per variant
ax = axes[1]
sps = [500, 2000, 8000]
for v, style in [('nosplit','o-'), ('split','s-'), ('split_bag','^-'),
                 ('gauss_full','o--'), ('gauss_split','s--')]:
    maes = []
    for sp in sps:
        sel = [r for r in rows if r['variant']==v and r['S_pilot']==sp]
        maes.append(100*np.mean([abs(r['acc_pred']-r['acc_true']) for r in sel]))
    ax.plot(sps, maes, style, label=v)
ax.axhline(3, color='gray', lw=0.8, ls=':')
ax.text(520, 3.1, 'hypothesis target (3 pts)', fontsize=7, color='gray')
ax.set_xscale('log'); ax.set_xlabel('$S_{pilot}$ (shots per time step)')
ax.set_ylabel('MAE (accuracy points)'); ax.set_title('Self-calibration error vs pilot budget')
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig('b6_selfcal.png', dpi=150)
print('figure saved')
