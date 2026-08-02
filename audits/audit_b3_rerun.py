"""
B3 audit re-run (2026-08-02): regenerate the code-backed portion of benchmark 3
(RESULTS_TASKSHAPE.md) from committed code and re-derive every published claim
from the stored raw JSON files.

Part 1 — byte-identity: runs the committed CLI `src/qrc_design.py 40000`
unmodified in a scratch dir and requires the output to be byte-identical
(md5) to the committed `results/design_sweep_40000.json`.

Part 2 — derived claims: recomputes every number quoted in
RESULTS_TASKSHAPE.md from `results/task_shape.json` + `results/gap_final.json`
and hard-fails on any mismatch at published precision.

NOTE (provenance, found by this audit): `results/task_shape.json` and
`figures/qrc_task_shape.png` themselves have NO committed generator — the
write-up's "experiment blocks reproduced below" are absent from the file.
This script verifies internal consistency of those stored numbers and the
byte-reproducibility of the design sweep; it cannot regenerate the headline
parity curve. See the 2026-08-02 (fourth session) AUDITS.md entry.

Run from repo root: PYTHONPATH=<libs> python3 audits/audit_b3_rerun.py
"""
import hashlib, json, math, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()

def check(name, cond, detail=''):
    print(('PASS' if cond else 'FAIL'), name, detail)
    if not cond:
        sys.exit(1)

# ---- Part 1: byte-identical regeneration of the design sweep ----
with tempfile.TemporaryDirectory() as td:
    for f in ('qrc_design.py', 'qrc_benchmark.py', 'qrc_gap_eval.py'):
        shutil.copy(os.path.join(ROOT, 'src', f), td)
    subprocess.run([sys.executable, 'qrc_design.py', '40000'], cwd=td,
                   check=True, capture_output=True)
    new = os.path.join(td, 'design_sweep_40000.json')
    pub = os.path.join(ROOT, 'results', 'design_sweep_40000.json')
    check('design_sweep_40000.json byte-identical', md5(new) == md5(pub),
          md5(pub))

# ---- Part 2: derived claims from stored raw ----
ts = json.load(open(os.path.join(ROOT, 'results', 'task_shape.json')))
gf = json.load(open(os.path.join(ROOT, 'results', 'gap_final.json')))
ds = json.load(open(pub))

m, s, r = ts['acc_mean'], ts['acc_std'], ts['refs']
# accuracy-vs-budget line: 400->0.55, 1.2k->0.59, 4k->0.70, 12k->0.80, 40k->0.93, 120k->0.99
pub_curve = [0.55, 0.59, 0.70, 0.80, 0.93, 0.99]
check('budget curve rounds as printed',
      [round(x, 2) for x in m] == pub_curve and ts['budgets'] == [400, 1200, 4000, 12000, 40000, 120000])
check('40k accuracy 0.93 +/- 0.02', round(m[4], 2) == 0.93 and round(s[4], 2) == 0.02)
# headline table, regression row: 0.003 | 0.142 | vs 0.148
i40 = gf['budgets'].index(40000)
check('regression row 0.003/0.142/0.148',
      round(gf['refs']['exact_floor'], 3) == 0.003 and
      round(gf['mitigated'][i40], 3) == 0.142 and
      round(gf['refs']['linear_inputs'], 3) == 0.148)
# headline table, classification row: 1.00 | 0.93 | chance 0.51 | ESN 0.767->0.77
check('classification row refs', r['qrc_exact'] == 1.0 and r['linear'] == 0.51
      and round(r['esn_tuned'], 2) == 0.77 and r['poly3_classical'] == 1.0)
# retention: ~86% recomputes at full precision; stored 86.0
clf = 100 * (m[4] - r['linear']) / (r['qrc_exact'] - r['linear'])
check('clf retention ~86%% (full-prec %.1f, stored %s)' % (clf, ts['retained_pct']['classification_40k']),
      abs(clf - 86.1) < 0.1 and ts['retained_pct']['classification_40k'] == 86.0)
# regression retention: stored 4.1 comes from ROUNDED inputs; full precision 4.5
reg_rounded = 100 * (0.148 - 0.142) / (0.148 - 0.003)
reg_full = 100 * (gf['refs']['linear_inputs'] - gf['mitigated'][i40]) / (gf['refs']['linear_inputs'] - gf['refs']['exact_floor'])
check('reg retention stored 4.1 = rounded-input convention (full-prec %.2f)' % reg_full,
      abs(reg_rounded - 4.14) < 0.01 and ts['retained_pct']['regression_40k'] == 4.1
      and abs(reg_full - 4.54) < 0.01)
# ESN crossing bracket: acc(4k) < esn_tuned < acc(12k)
check('ESN crossing near 12k', m[2] < r['esn_tuned'] < m[3])
# secondary finding cells: 0.157 (base d3); full-range best 0.1331 (-15.1%); printed 0.130
b3 = ds['g=base(0.09rad max) depth=3']['noisy']
fullcol = [ds[f'g=full(pi/2 max) depth={d}']['noisy'] for d in (1, 3, 6)]
x25 = ds['g=2.5x depth=1']['noisy']
check('secondary 0.157 base cell', round(b3, 3) == 0.157)
check('full-range best 0.133 (-%.1f%%), printed 0.130 matches 2.5x d1 (%.4f) not any full cell'
      % (100 * (1 - min(fullcol) / b3), x25),
      round(min(fullcol), 3) == 0.133 and round(x25, 3) == 0.130
      and all(round(v, 3) != 0.130 for v in fullcol))
# exact-readout degradation at the extreme
base_ex = [ds[f'g=base(0.09rad max) depth={d}']['exact'] for d in (1, 3, 6)]
full_ex = [ds[f'g=full(pi/2 max) depth={d}']['exact'] for d in (1, 3, 6)]
check('full gain degrades exact readout', all(f > b for f, b in zip(full_ex, base_ex)))
# label/wording flags (documented, not challenged): theta_max at base gain
import numpy as np
sys.path.insert(0, os.path.join(ROOT, 'src'))
from qrc_benchmark import narma
u, _ = narma(5, 1200, seed=5)
th = 0.5 * np.pi * u.max()
check('base theta_max = 0.314 rad = 18 deg = 20%% of 90deg (write-up says 6%%; JSON key says 0.09rad)',
      abs(th - 0.314) < 0.001 and abs(math.degrees(th) - 18.0) < 0.1)
print('ALL CHECKS PASSED')
