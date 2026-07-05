"""Figure for B13 (small-margin topology sweep). Reads ../results/smallmargin_topology.json."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('../results/smallmargin_topology.json'))
cells = d['cells']
ph = d['post_hoc']
TASKS = ['updown', 'accel', 'prodmed']
TOPOS = ['chain', 'ring', 'star', 'all2all']
BUD = [250, 1000, 4000, 16000, 64000]
TC = {'updown': '#1f77b4', 'accel': '#d62728', 'prodmed': '#2ca02c'}

fig, ax = plt.subplots(2, 2, figsize=(11.5, 9))
fig.suptitle('B13 - Small-margin regime: IPS is a within-task design rule, '
             'not a cross-task scale', fontsize=13)

# A: scatter log IPS vs acc@250 per task
a = ax[0, 0]
for tn in TASKS:
    sub = [r for r in cells if r['task'] == tn and r['shots'] == 250]
    x = np.log10([r['ips'] for r in sub]); y = [r['noisy'] for r in sub]
    a.scatter(x, y, c=TC[tn], s=45,
              label=f"{tn} (rho={ph['within_task_rho'][tn]['250']['rho']:+.2f})")
    # within-task trend line
    z = np.polyfit(x, y, 1)
    xs = np.linspace(min(x), max(x), 10)
    a.plot(xs, np.polyval(z, xs), c=TC[tn], lw=1, ls='--', alpha=0.7)
a.set_xlabel('log10 IPS (design-time, noiseless)')
a.set_ylabel('accuracy @ 250 shots (retrained readout)')
a.set_title(f"A. Pooled rho = {d['summary']['H1_rho_by_budget']['250']['rho']:+.2f} (pre-reg FAIL)\n"
            'but strong within every task', fontsize=10)
a.legend(fontsize=8)

# B: pooled vs stratified rho across budgets, + B12 reference
b = ax[0, 1]
pooled = [d['summary']['H1_rho_by_budget'][str(S)]['rho'] for S in BUD]
strat = [ph['stratified_rho'][str(S)]['rho'] for S in BUD]
b12 = [0.90, 0.84, 0.57, 0.48, 0.37]
b.plot(BUD, pooled, 'o-', c='#d62728', label='B13 pooled (pre-registered test)')
b.plot(BUD, strat, 's-', c='#1f77b4', label='B13 within-task (post-hoc)')
b.plot(BUD, b12, '^--', c='grey', label='B12 pooled (parity family)')
b.axhline(0.5, c='k', lw=0.5, ls=':')
b.text(BUD[0], 0.51, 'H1 pass bar (+0.5)', fontsize=7)
b.set_xscale('log'); b.set_xlabel('shots per timestep')
b.set_ylabel('Spearman rho(log IPS, accuracy)')
b.set_title('B. The lever survives within-task;\npooling across tasks kills it', fontsize=10)
b.legend(fontsize=8)

# C: topology ranking per task @250
c = ax[1, 0]
w = 0.2
for i, topo in enumerate(TOPOS):
    vals = [ph['per_task_winner_250'][tn][topo] for tn in TASKS]
    c.bar(np.arange(3) + (i-1.5)*w, vals, width=w, label=topo)
for j, tn in enumerate(TASKS):
    win = ph['per_task_winner_250'][tn]['winner']
    c.text(j, max(ph['per_task_winner_250'][tn][t] for t in TOPOS)+0.008,
           f'* {win}', ha='center', fontsize=8)
c.set_xticks(range(3)); c.set_xticklabels(TASKS)
c.set_ylim(0.6, 0.92)
c.set_ylabel('mean accuracy @ 250 shots')
c.set_title('C. Star wins 2/3 tasks (and on average);\nchain takes accel', fontsize=10)
c.legend(fontsize=8)

# D: IPS by topology and depth (log)
dax = ax[1, 1]
for i, L in enumerate([1, 2]):
    vals = []
    for topo in TOPOS:
        vals.append(np.mean([r['ips'] for r in cells
                             if r['topo'] == topo and r['layers'] == L and r['shots'] == 250]))
    dax.bar(np.arange(4) + (i-0.5)*0.35, vals, width=0.35, label=f'depth {L}',
            color=['#1f77b4', '#ff7f0e'][i])
dax.set_yscale('log')
dax.set_xticks(range(4)); dax.set_xticklabels(TOPOS)
dax.set_ylabel('mean IPS (log scale)')
dax.set_title('D. IPS spread 14-39x across reservoirs;\ndepth 2 collapses IPS ~6x and costs ~5pp @250', fontsize=10)
dax.legend(fontsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('../figures/qrc_smallmargin.png', dpi=130)
print('figure saved')
