"""B11 figure + retrain-check addendum. Reads results/taskfam_law.json,
adds a fixed-vs-retrained readout comparison (corroborating B10 on the new
family), writes figures/qrc_taskfam.png."""
import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import qrc_taskfam as M

d = json.load(open('../results/taskfam_law.json')); cells = d['cells']
B = list(M.BUDGETS)

# --- retrain check across all archs at all budgets (fixed vs retrained) ---
u = M.make_inputs(); L = M.task_labels(u)
rc = []
for a in M.ARCHS:
    Z = M.zdiags(M.ARCHS[a]['nq']); P = M.build_P(a)
    Xex = M.feats_exact(P, Z); Tn = Xex.shape[0]; sp = M.split_idx(Tn-M.WASH)+M.WASH
    for t in M.CLF_TASKS:
        y = L[t][0]
        sc0, clf0 = M.clf_fit(Xex[M.WASH:sp], y[M.WASH:sp])
        for S in B:
            fx, rt = [], []
            for ss in (1, 2, 3):
                rng = np.random.default_rng(1000*ss+S)
                Xn = M.feats_noisy(P, Z, S, rng)
                fx.append(M.clf_acc(sc0, clf0, Xn[sp:], y[sp:]))
                scn, clfn = M.clf_fit(Xn[M.WASH:sp], y[M.WASH:sp])
                rt.append(M.clf_acc(scn, clfn, Xn[sp:], y[sp:]))
            rc.append(dict(arch=a, task=t, shots=S,
                           fixed=float(np.mean(fx)), retrained=float(np.mean(rt))))
d['retrain_check'] = rc
json.dump(d, open('../results/taskfam_law.json', 'w'), indent=1)

# ---------------- figure ----------------
clf = [r for r in cells if r['kind'] == 'clf']
fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))

# Panel A: law calibration (pred vs observed noisy accuracy)
colors = {'updown': 'C0', 'accel': 'C1', 'prodmed': 'C2'}
for t in M.CLF_TASKS:
    sub = [r for r in clf if r['task'] == t]
    ax[0].scatter([r['law_pred'] for r in sub], [r['noisy'] for r in sub],
                  s=34, alpha=.8, color=colors[t], label=t)
ax[0].plot([.4, .8], [.4, .8], 'k--', lw=1)
pred = np.array([r['law_pred'] for r in clf]); obs = np.array([r['noisy'] for r in clf])
r2 = 1-np.sum((pred-obs)**2)/np.sum((obs-obs.mean())**2)
mae = 100*np.mean(np.abs(pred-obs))
ax[0].set_xlabel('law prediction (parameter-free probit)')
ax[0].set_ylabel('observed fixed-readout accuracy')
ax[0].set_title('A. Law external validity (new family)\nMAE=%.1fpp  R2=%.2f  (60 cells)' % (mae, r2))
ax[0].legend(fontsize=8, loc='upper left')

# Panel B: the fixed-readout wall + retraining recovery (mean over archs)
def meanby(rows, key, S): 
    v = [r[key] for r in rows if r['shots'] == S]
    return np.mean(v) if v else np.nan
floor = np.mean([r['floor'] for r in clf])
exact = np.mean([r['exact'] for r in clf])
fixed_curve = [meanby(clf, 'noisy', S) for S in B]
retr_curve = [np.mean([r['retrained'] for r in rc if r['shots'] == S]) for S in B]
ax[1].axhline(exact, color='green', ls=':', label='exact (noiseless) %.2f' % exact)
ax[1].axhline(floor, color='gray', ls='--', label='classical floor (inputs only) %.2f' % floor)
ax[1].plot(B, fixed_curve, 'o-', color='C3', label='fixed design-time readout')
ax[1].plot(B, retr_curve, 's-', color='C0', label='retrained-on-noisy readout')
ax[1].set_xscale('log'); ax[1].set_xlabel('shot budget S'); ax[1].set_ylabel('classification accuracy')
ax[1].set_title('B. The wall on the new family\n(fixed readout collapses below floor)')
ax[1].legend(fontsize=8, loc='center left')

# Panel C: task-shape -- MG regression retention vs shots
reg = [r for r in cells if r['kind'] == 'reg']
ret = [np.mean([r['retained'] for r in reg if r['shots'] == S and r['retained'] is not None]) for S in B]
ax[2].axhline(0, color='k', lw=.8); ax[2].axhline(1, color='green', ls=':', label='full benefit')
ax[2].plot(B, ret, 'o-', color='C4', label='Mackey-Glass regression')
ax[2].fill_between(B, [min(0, x) for x in ret], 0, color='C3', alpha=.15)
ax[2].set_xscale('log'); ax[2].set_xlabel('shot budget S'); ax[2].set_ylabel('retained benefit')
ax[2].set_title('C. Task-shape generalises (B3)\nregression retention <0 at low S')
ax[2].legend(fontsize=8, loc='lower right')

plt.tight_layout()
plt.savefig('../figures/qrc_taskfam.png', dpi=130)
print('figure saved; retrain_check cells:', len(rc))
print('fixed@64k mean=%.3f  retrained@64k mean=%.3f' % (fixed_curve[-1], retr_curve[-1]))
