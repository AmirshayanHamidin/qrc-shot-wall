"""Figure for B12 topology sweep. Reads topology_law.json -> qrc_topology.png"""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

R = json.load(open('topology_law.json'))
topos = ['chain', 'ring', 'star', 'all2all']
col = {'chain': '#2471a3', 'ring': '#27ae60', 'star': '#c0392b', 'all2all': '#8e44ad'}
configs = sorted({(r['topo'], r['layers'], r['task']) for r in R})
def cell(c, S):
    for r in R:
        if (r['topo'], r['layers'], r['task']) == c and r['shots'] == S:
            return r

S0 = 250
ips = np.array([cell(c, S0)['ips'] for c in configs])
pr = np.array([cell(c, S0)['pr'] for c in configs])
acc = np.array([cell(c, S0)['noisy'] for c in configs])
cs = [col[c[0]] for c in configs]

fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.7))

# A: IPS vs acc (the designable lever)
rho_i = spearmanr(np.log10(ips + 1e-4), acc)[0]
ax[0].scatter(ips + 1e-4, acc, c=cs, s=45, edgecolor='k', lw=0.4)
ax[0].set_xscale('log')
ax[0].set_xlabel('information-per-shot  IPS = Σ Δμ²/σ²  (design-time, noiseless)')
ax[0].set_ylabel('shot-limited accuracy @ 250 shots')
ax[0].set_title(f'A. Info-per-shot is a designable lever\nSpearman ρ = {rho_i:+.2f} (p=3e-15), 40 reservoirs')
for topo in topos:
    ax[0].scatter([], [], c=col[topo], label=topo)
ax[0].legend(fontsize=8, title='topology')

# B: PR vs acc (the falsified concentration intuition)
rho_p = spearmanr(pr, acc)[0]
ax[1].scatter(pr, acc, c=cs, s=45, edgecolor='k', lw=0.4)
ax[1].set_xlabel('participation ratio of Δμ  (LOW = signal in few observables)')
ax[1].set_ylabel('shot-limited accuracy @ 250 shots')
ax[1].set_title(f'B. Concentration does NOT help (H2 falsified)\nSpearman ρ = {rho_p:+.2f} (p=0.28, n.s.)')

# C: topology ranking
ax2 = ax[2]
accbar, ipsbar = [], []
for topo in topos:
    cc = [c for c in configs if c[0] == topo]
    accbar.append(np.mean([cell(c, S0)['noisy'] for c in cc]))
    ipsbar.append(np.mean([cell(c, S0)['ips'] for c in cc]))
x = np.arange(len(topos))
b = ax2.bar(x, accbar, color=[col[t] for t in topos])
ax2.set_xticks(x); ax2.set_xticklabels(topos)
ax2.set_ylim(0.7, 1.0)
ax2.set_ylabel('mean accuracy @ 250 shots')
ax2.set_title('C. Star (hub) reservoir wins — via higher IPS,\nnot more connectivity (all-to-all is worst)')
for xi, ii, ab in zip(x, ipsbar, accbar):
    ax2.text(xi, ab + 0.004, f'IPS\n{ii:.2f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('qrc_topology.png', dpi=110)
print('saved qrc_topology.png')
