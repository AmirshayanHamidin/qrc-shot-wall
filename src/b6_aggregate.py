import json, glob
import numpy as np

rows = []
for f in sorted(glob.glob('b6_arch*.json')):
    rows += json.load(open(f))
print(f'{len(rows)} rows total')

def metrics(sel):
    p = np.array([r['acc_pred'] for r in sel])
    t = np.array([r['acc_true'] for r in sel])
    mae = float(np.mean(np.abs(p - t)) * 100)
    r2 = float(1 - np.sum((p - t)**2) / np.sum((t - t.mean())**2))
    return mae, r2, len(sel)

summary = {}
for v in ('nosplit', 'split', 'split_bag', 'gauss_full', 'gauss_split'):
    for sp in (500, 2000, 8000):
        sel = [r for r in rows if r['variant'] == v and r['S_pilot'] == sp]
        if not sel: continue
        mae, r2, n = metrics(sel)
        summary[f'{v}_Sp{sp}'] = dict(mae_pts=round(mae, 2), r2=round(r2, 3), n=n)
        print(f'{v:11s} Sp={sp:>5}: MAE={mae:5.2f} pts  R2={r2:6.3f}  (n={n})')

best = 'gauss_full'
print(f'\nper-arch, {best} Sp=8000:')
for a in range(6):
    sel = [r for r in rows if r['variant'] == best and r['S_pilot'] == 8000 and r['arch'] == a]
    if not sel: continue
    mae, r2, n = metrics(sel)
    summary[f'arch{a}_{best}_Sp8000'] = dict(mae_pts=round(mae, 2), r2=round(r2, 3))
    print(f'  arch {a}: MAE={mae:5.2f}  R2={r2:6.3f}')

print(f'\nper-target-budget, {best} Sp=8000:')
for S in (250, 1000, 4000, 16000, 64000):
    sel = [r for r in rows if r['variant'] == best and r['S_pilot'] == 8000 and r['shots'] == S]
    if not sel: continue
    mae, r2, n = metrics(sel)
    summary[f'S{S}_{best}_Sp8000'] = dict(mae_pts=round(mae, 2), r2=round(r2, 3))
    print(f'  S={S:>6}: MAE={mae:5.2f}  R2={r2:6.3f}')

json.dump(dict(summary=summary, rows=rows), open('b6_selfcal.json', 'w'), indent=1)
print('\nsaved b6_selfcal.json')
