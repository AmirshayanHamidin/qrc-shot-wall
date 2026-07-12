"""B2 re-audit driver (2026-07-11) - re-runs the committed B2 pipeline
UNMODIFIED in a scratch directory and compares every published number in
results/gap_final.json, the RESULTS_GAP.md 40k strategy table, and both
reference baselines (linear-on-inputs, tuned ESN) against regenerated
outputs. Files of record are never written. Usage (from repo root):

    python3 audits/audit_b2_rerun.py grid1   # committed qrc_gap_eval.py @ 4k, 40k
    python3 audits/audit_b2_rerun.py grid2   # committed qrc_gap_eval.py @ 400k, 4M
    python3 audits/audit_b2_rerun.py seeds   # plateau noise seeds 2,3 @ 40k via committed run()
    python3 audits/audit_b2_rerun.py refs    # committed qrc_benchmark.py + qrc_full_eval.py
    python3 audits/audit_b2_rerun.py check   # compare, write audits/b2_rerun_check.json
    python3 audits/audit_b2_rerun.py all     # everything (~80 s on a laptop)

Phases share a scratch dir so the sandbox's 45 s per-call cap is respected
by running phases in separate calls. Environment of record for the
2026-07-11 audit: numpy 2.2.6, scikit-learn 1.7.2, qiskit 2.5.0,
scipy 1.15.3, CPU only.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.path.join(tempfile.gettempdir(), 'b2audit_scratch')
SRC = os.path.join(SCRATCH, 'src')

# Published 40k strategy table, RESULTS_GAP.md (4 dp), code-backed rows only.
PUB_TABLE_40K = {
    'V=4 raw': 0.5815, 'V=4 ema+lag+in': 0.1568, 'V=4 pca+lag+in': 0.1521,
    'V=4 pca+ema+lag+in': 0.1515, 'V=4 eiv+lag+in': 0.1759,
    'V=1 ema+lag+in': 0.1417, 'exact floor (lag+in)': 0.0030,
}
BUDGETS = [4000, 40000, 400000, 4000000]

def setup():
    os.makedirs(SRC, exist_ok=True)
    for f in ('qrc_benchmark.py', 'qrc_gap_eval.py', 'qrc_full_eval.py'):
        shutil.copy(os.path.join(ROOT, 'src', f), os.path.join(SRC, f))

def run_in_scratch(args):
    subprocess.run([sys.executable] + args, cwd=SRC, check=True)

def grid(budgets):
    setup()
    for b in budgets:
        run_in_scratch(['qrc_gap_eval.py', str(b)])

def seeds():
    setup()
    code = ("import json\nfrom qrc_gap_eval import run\n"
            "json.dump({str(s): run(40000, noise_seed=s) for s in (2, 3)},"
            " open('plateau_seeds.json', 'w'), indent=1)\n")
    run_in_scratch(['-c', code])

def refs():
    setup()
    run_in_scratch(['qrc_benchmark.py'])
    run_in_scratch(['qrc_full_eval.py'])

def check():
    pub = json.load(open(os.path.join(ROOT, 'results', 'gap_final.json')))
    rep = {b: json.load(open(os.path.join(SRC, f'gap_results_{b}.json')))
           for b in BUDGETS}
    pl = json.load(open(os.path.join(SRC, 'plateau_seeds.json')))

    raw_rep = [rep[b]['V=4 raw'] for b in BUDGETS]
    mit_rep = [round(rep[b]['V=1 ema+lag+in'], 4) for b in BUDGETS]
    plateau_rep = [rep[40000]['V=1 ema+lag+in'],
                   pl['2']['V=1 ema+lag+in'], pl['3']['V=1 ema+lag+in']]
    table_rep = {k: round(rep[40000][k], 4) for k in PUB_TABLE_40K}

    fullres = json.load(open(os.path.join(SRC, 'qrc_full_results.json')))
    benchres = json.load(open(os.path.join(SRC, 'qrc_results.json')))
    pub_full = json.load(open(os.path.join(ROOT, 'results', 'qrc_full_results.json')))
    pub_bench = json.load(open(os.path.join(ROOT, 'results', 'qrc_results.json')))

    out = {
        'date': '2026-07-11',
        'environment': {'numpy': '2.2.6', 'sklearn': '1.7.2',
                        'qiskit': '2.5.0', 'scipy': '1.15.3'},
        'raw_sweep_bit_identical': pub['raw'] == raw_rep,
        'raw_sweep_reproduced': raw_rep,
        'mitigated_sweep_match_at_stored_4dp': pub['mitigated'] == mit_rep,
        'mitigated_sweep_reproduced_4dp': mit_rep,
        'plateau_seeds_bit_identical': pub['plateau_seeds_40k'] == plateau_rep,
        'plateau_seeds_reproduced': plateau_rep,
        'table_40k_match_at_4dp': table_rep == PUB_TABLE_40K,
        'table_40k_reproduced_full_precision':
            {k: rep[40000][k] for k in PUB_TABLE_40K},
        'refs': {
            'linear_inputs_pub': pub['refs']['linear_inputs'],
            'linear_inputs_reproduced': fullres['NARMA5']['Linear_window'],
            'esn_tuned_pub': pub['refs']['esn_tuned'],
            'esn_tuned_reproduced': fullres['NARMA5']['ESN_tuned'],
            'exact_floor_pub': pub['refs']['exact_floor'],
            'exact_floor_reproduced': rep[40000]['exact floor (lag+in)'],
            'qrc_results_json_bit_identical': benchres == pub_bench,
            'qrc_full_results_json_bit_identical': fullres == pub_full,
        },
        'no_committed_generator': [
            'sim-trained linear denoiser row (0.1519)',
            'sim-trained MLP denoiser row (0.1533)',
            'non-redundancy probe (rel. err 0.90 linear / 0.89 MLP)',
        ],
    }
    dst = os.path.join(ROOT, 'audits', 'b2_rerun_check.json')
    json.dump(out, open(dst, 'w'), indent=1)
    for k in ('raw_sweep_bit_identical', 'mitigated_sweep_match_at_stored_4dp',
              'plateau_seeds_bit_identical', 'table_40k_match_at_4dp'):
        print(f'{k}: {out[k]}')
    print('refs:', json.dumps(out['refs'], indent=1))
    print('wrote', dst)

if __name__ == '__main__':
    phase = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if phase in ('grid1', 'all'): grid([4000, 40000])
    if phase in ('grid2', 'all'): grid([400000, 4000000])
    if phase in ('seeds', 'all'): seeds()
    if phase in ('refs', 'all'): refs()
    if phase in ('check', 'all'): check()
