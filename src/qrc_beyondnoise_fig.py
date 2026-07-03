"""Figure for B8: beyond-depolarizing gate noise vs the scalar fidelity factor."""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

d = json.load(open('beyond_noise_law.json'))
ch = d['channels']; cells = d['cells']; ETAS = d['etas']
order = ['dephasing', 'amp_damping', 'coherent']
nice = {'dephasing': 'dephasing\n(unital)', 'amp_damping': 'amp. damping\n(non-unital)',
        'coherent': 'coherent\n(unitary)'}
col = {'dephasing': '#2c7fb8', 'amp_damping': '#d95f0e', 'coherent': '#756bb1'}
DEPOL_R2 = 0.927  # B6 reference (global depolarizing)

def series(channel, key):
    xs, ys = [], []
    for e in ETAS:
        if e == 0.0: continue
        xs.append(e); ys.append(ch[channel]['per_eta'][f'{e}'][key])
    return np.array(xs), np.array(ys)

fig, ax = plt.subplots(2, 2, figsize=(11, 8))

# A: collapse R2 vs naive, with depolarizing reference
a = ax[0, 0]; x = np.arange(len(order)); w = 0.36
a.bar(x - w/2, [ch[c]['collapse_r2'] for c in order], w, label='with scalar factor c(eta)', color='#2c7fb8')
a.bar(x + w/2, [ch[c]['naive_r2'] for c in order], w, label='naive (no factor)', color='#bdbdbd')
a.axhline(DEPOL_R2, ls='--', color='#31a354', lw=2, label=f'depolarizing (B6) = {DEPOL_R2}')
a.set_xticks(x); a.set_xticklabels([nice[c] for c in order]); a.set_ylim(0.3, 1.0)
a.set_ylabel('collapse $R^2$'); a.set_title('A. Scalar fidelity factor is depolarizing-specific')
a.legend(fontsize=8, loc='lower left'); a.grid(axis='y', alpha=0.3)

# B: direction cosine vs eta
b = ax[0, 1]
for c in order:
    xs, ys = series(c, 'mean_cos'); b.plot(xs, ys, 'o-', color=col[c], label=nice[c].replace('\n', ' '))
b.axhline(1.0, ls=':', color='k', alpha=0.5)
b.set_xlabel('noise strength $\\eta$'); b.set_ylabel('cos(readout direction vs $\\eta{=}0$)')
b.set_title('B. Do errors ROTATE the readout direction?'); b.legend(fontsize=8); b.grid(alpha=0.3)

# C: contraction c vs eta
c_ = ax[1, 0]
for c in order:
    xs, ys = series(c, 'mean_c'); c_.plot(xs, ys, 's-', color=col[c], label=nice[c].replace('\n', ' '))
c_.set_xlabel('noise strength $\\eta$'); c_.set_ylabel('contraction $c(\\eta)=||\\Delta\\mu||_\\eta/||\\Delta\\mu||_0$')
c_.set_title('C. Margin contraction'); c_.legend(fontsize=8); c_.grid(alpha=0.3)

# D: signed residual (obs - scalar-factor prediction) vs eta
dd = ax[1, 1]
for c in order:
    xs, ys = series(c, 'mean_bias'); dd.plot(xs, ys, 'D-', color=col[c], label=nice[c].replace('\n', ' '))
dd.axhline(0, ls=':', color='k', alpha=0.6)
dd.set_xlabel('noise strength $\\eta$'); dd.set_ylabel('mean(obs $-$ factor prediction)')
dd.set_title('D. Off-curve bias (sign differs by channel)'); dd.legend(fontsize=8); dd.grid(alpha=0.3)

fig.suptitle('B8: beyond depolarizing — a scalar device-fidelity factor is not enough',
             fontsize=13, weight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.97])
fig.savefig('qrc_beyondnoise.png', dpi=130)
print('figure saved qrc_beyondnoise.png')
