"""B11 re-audit driver (2026-07-11) - re-runs the committed B11 pipeline
UNMODIFIED in a scratch directory and compares every published number in
results/taskfam_law.json (80 grid cells + summary + 60 retrain-check cells)
and figures/qrc_taskfam.png against the regenerated outputs. Files of record
are never written. Usage (from repo root):

    python3 audits/audit_b11_rerun.py

Writes audits/b11_rerun_check.json and prints a claim-check table covering
every headline number in results/RESULTS_TASKFAM.md and the README B11
paragraph. Environment of record for the 2026-07-11 audit: numpy 2.2.6,
scikit-learn 1.7.2, qiskit 2.5.0, scipy 1.15.3, CPU only.
"""
import json, os, shutil, subprocess, sys, hashlib, tempfile
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def main():
    scratch = tempfile.mkdtemp(prefix='b11audit_')
    for d in ('src', 'results', 'figures'):
        os.makedirs(os.path.join(scratch, d), exist_ok=True)
    for f in ('qrc_taskfam.py', 'qrc_taskfam_fig.py'):
        shutil.copy(os.path.join(ROOT, 'src', f), os.path.join(scratch, 'src', f))

    env = dict(os.environ)
    # 1) full grid, committed code, per-arch phases exactly as documented
    for a in (0, 1, 2, 4):
        subprocess.run([sys.executable, 'qrc_taskfam.py', 'run', str(a)],
                       cwd=os.path.join(scratch, 'src'), env=env, check=True)
    subprocess.run([sys.executable, 'qrc_taskfam.py', 'agg'],
                   cwd=os.path.join(scratch, 'src'), env=env, check=True)
    # 2) retrain-check addendum + figure, committed fig script unmodified
    subprocess.run([sys.executable, 'qrc_taskfam_fig.py'],
                   cwd=os.path.join(scratch, 'src'), env=env, check=True)

    pub = json.load(open(os.path.join(ROOT, 'results', 'taskfam_law.json')))
    new = json.load(open(os.path.join(scratch, 'results', 'taskfam_law.json')))

    # --- cell-level comparison, all stored float fields ---
    key = lambda r: (r['arch'], r['task'], r['shots'])
    nd = {key(r): r for r in new['cells']}
    maxdiff = {}
    for r in pub['cells']:
        q = nd[key(r)]
        for f, v in r.items():
            if isinstance(v, float):
                maxdiff[f] = max(maxdiff.get(f, 0.0), abs(v - q[f]))
            elif v is None:
                assert q[f] is None, key(r)
    rd = {key(r): r for r in new['retrain_check']}
    rc_diff = {'fixed': 0.0, 'retrained': 0.0}
    for r in pub['retrain_check']:
        q = rd[(r['arch'], r['task'], r['shots'])]
        for f in rc_diff:
            rc_diff[f] = max(rc_diff[f], abs(r[f] - q[f]))

    fig_pub = md5(os.path.join(ROOT, 'figures', 'qrc_taskfam.png'))
    fig_new = md5(os.path.join(scratch, 'figures', 'qrc_taskfam.png'))

    # --- claim checks against the write-up ---
    clf = [r for r in new['cells'] if r['kind'] == 'clf']
    reg = [r for r in new['cells'] if r['kind'] == 'reg']
    pred = np.array([r['law_pred'] for r in clf])
    obs = np.array([r['noisy'] for r in clf])
    r2 = 1 - ((pred - obs) ** 2).sum() / ((obs - obs.mean()) ** 2).sum()
    per_task = {}
    for t in ('updown', 'accel', 'prodmed'):
        p = np.array([r['law_pred'] for r in clf if r['task'] == t])
        o = np.array([r['noisy'] for r in clf if r['task'] == t])
        per_task[t] = dict(
            r2=round(float(1 - ((p - o) ** 2).sum() / ((o - o.mean()) ** 2).sum()), 3),
            mae_pp=round(float(100 * np.mean(abs(p - o))), 2),
            obs_range=[round(float(o.min()), 3), round(float(o.max()), 3)])
    task_mean_exact = {t: round(float(np.mean(
        [r['exact'] for r in clf if r['task'] == t and r['shots'] == 250])), 3)
        for t in ('updown', 'accel', 'prodmed')}
    cell_exacts = sorted({(r['arch'], r['task']): r['exact'] for r in clf}.values())
    rc64 = [r for r in new['retrain_check'] if r['shots'] == 64000]
    gaps64 = [r['retrained'] - r['fixed'] for r in rc64]
    sys.path.insert(0, os.path.join(scratch, 'src'))
    import qrc_taskfam as M
    u = M.make_inputs()

    checks = dict(
        pooled=dict(r2=round(float(r2), 4),
                    mae_pp=round(float(100 * np.mean(abs(pred - obs))), 3),
                    bias_pp=round(float(100 * np.mean(pred - obs)), 3),
                    obs_range=[round(float(obs.min()), 3), round(float(obs.max()), 3)],
                    obs_std=round(float(obs.std()), 4)),
        per_task=per_task,
        fixed_mean=dict(at_250=round(float(np.mean([r['noisy'] for r in clf if r['shots'] == 250])), 3),
                        at_64k=round(float(np.mean([r['noisy'] for r in clf if r['shots'] == 64000])), 3),
                        floor_mean=round(float(np.mean(sorted({(r['arch'], r['task']): r['floor'] for r in clf}.values()))), 3)),
        arch4_at_64k=[(r['task'], round(r['noisy'], 3), round(r['law_pred'], 3))
                      for r in clf if r['arch'] == 4 and r['shots'] == 64000],
        reg_retention_mean=[round(float(np.mean([r['retained'] for r in reg if r['shots'] == S])), 3)
                            for S in (250, 1000, 4000, 16000, 64000)],
        retrain_at_64k=dict(fixed=round(float(np.mean([r['fixed'] for r in rc64])), 3),
                            retrained=round(float(np.mean([r['retrained'] for r in rc64])), 3),
                            gap_pp=[round(100 * float(min(gaps64)), 1), round(100 * float(max(gaps64)), 1)],
                            gap_mean_pp=round(100 * float(np.mean(gaps64)), 1)),
        exact_span=dict(per_cell=[round(float(cell_exacts[0]), 3), round(float(cell_exacts[-1]), 3)],
                        per_task_means=task_mean_exact),
        input_levels=dict(raw_unique=int(len(np.unique(u))),
                          unique_rounded_4dec=int(len(np.unique(np.round(u, 4))))),
    )

    out = dict(
        date='2026-07-11',
        environment=dict(numpy=np.__version__,
                         sklearn=__import__('sklearn').__version__,
                         qiskit=__import__('qiskit').__version__,
                         scipy=__import__('scipy').__version__),
        grid_cells=dict(n=len(pub['cells']), max_abs_diff_per_field=maxdiff),
        retrain_check=dict(n=len(pub['retrain_check']), max_abs_diff=rc_diff),
        summary_identical=(pub['summary'] == new['summary']),
        figure_md5=dict(published=fig_pub, regenerated=fig_new,
                        identical=(fig_pub == fig_new)),
        claim_checks=checks,
    )
    dst = os.path.join(ROOT, 'audits', 'b11_rerun_check.json')
    json.dump(out, open(dst, 'w'), indent=1)
    print(json.dumps(out, indent=1))
    print('\nscratch dir (not cleaned, for inspection):', scratch)

if __name__ == '__main__':
    main()
