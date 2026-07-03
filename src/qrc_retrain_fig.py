"""Benchmark 10 figure: readout retraining under noise.
Left  : closed-form probit predicts the FIXED noiseless-design readout (diagonal).
Right : the fixed readout collapses; retraining recovers ~25 pp (points above diag).
"""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('../results/retrain_law.json')) if __import__('os').path.exists('../results/retrain_law.json') else json.load(open('retrain_law.json'))
c = d['cells']
gam = np.array([r['gamma'] for r in c])
af = np.array([r['acc_fixed'] for r in c])
ar = np.array([r['acc_retrain'] for r in c])
lp = np.array([r['law_pred'] for r in c])

fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))

# panel A: law_pred vs acc_fixed
ax[0].plot([0.3, 1.0], [0.3, 1.0], 'k--', lw=1, alpha=.6)
sc = ax[0].scatter(af, lp, c=gam, cmap='viridis', s=26, edgecolor='k', linewidth=.3)
ax[0].set_xlabel('measured accuracy, FIXED noiseless-design readout')
ax[0].set_ylabel('closed-form probit prediction')
r2 = 1 - np.sum((af-lp)**2)/np.sum((af-af.mean())**2)
ax[0].set_title(f'(a) The law predicts the fixed readout\nR$^2$={r2:.3f}, MAE={np.mean(np.abs(af-lp))*100:.2f} pp')
ax[0].set_xlim(0.3, 1.0); ax[0].set_ylim(0.3, 1.0)
cb = fig.colorbar(sc, ax=ax[0]); cb.set_label('gate noise γ')

# panel B: acc_fixed vs acc_retrain (retraining gain)
ax[1].plot([0.3, 1.0], [0.3, 1.0], 'k--', lw=1, alpha=.6)
ax[1].axhline(0.5, color='gray', lw=.8, ls=':')
sc2 = ax[1].scatter(af, ar, c=gam, cmap='viridis', s=26, edgecolor='k', linewidth=.3)
gain = np.mean(ar-af)
ax[1].set_xlabel('FIXED noiseless-design readout accuracy')
ax[1].set_ylabel('RETRAINED-on-noisy-features accuracy')
ax[1].set_title(f'(b) Retraining recovers the reachable accuracy\nmean gain = {gain*100:.1f} pp (points above diagonal)')
ax[1].set_xlim(0.3, 1.0); ax[1].set_ylim(0.3, 1.0)
cb2 = fig.colorbar(sc2, ax=ax[1]); cb2.set_label('gate noise γ')

fig.suptitle('Benchmark 10 — the measurement-wall law scores a FIXED readout; reachable accuracy needs retraining',
             fontsize=11, y=1.02)
fig.tight_layout()
import os
out = '../figures/qrc_retrain.png' if os.path.isdir('../figures') else 'qrc_retrain.png'
fig.savefig(out, dpi=130, bbox_inches='tight')
print('saved', out)
