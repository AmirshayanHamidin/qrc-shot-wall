#!/usr/bin/env python3
"""ONE-SHOT confirmatory test of audits/PREREG_DRIFT.md (registered 2026-07-05).

Hypothesis: Spearman rho(blind discretion score, |drift| pp) > 0.5 with p < 0.01
over the confirmatory set, tested ONCE at n >= 30 confirmatory audits.
The set was CLOSED at n = 31 audits / 67 points by the audit #30 batch
(RESEARCH_AGENDA.md binding hand-off, commit ff7af3bd). This script consumes the
frozen dataset drift_confirmatory_points.json (verbatim transcription of the
tracker's printed points list) and adds, removes, or re-scores nothing.

Primary p: scipy.stats.spearmanr two-sided (a pre-registered option).
Cross-check: Monte Carlo permutation p (1e6 resamples, seed 0) on the same rho.
"""
import json, sys
import numpy as np
from scipy import stats

with open(sys.argv[1] if len(sys.argv) > 1 else "drift_confirmatory_points.json") as f:
    data = json.load(f)

pts = data["points"]
assert len(pts) == 67, f"set must be exactly 67 points, got {len(pts)}"
scores = np.array([p["score"] for p in pts], dtype=float)
drifts = np.array([p["drift_pp"] for p in pts], dtype=float)

rho, p_two = stats.spearmanr(scores, drifts)

# Monte Carlo permutation cross-check (two-sided, on |rho|), vectorized in chunks
rng = np.random.default_rng(0)
B = 1_000_000
ranks_d = stats.rankdata(drifts)
ranks_s = stats.rankdata(scores)
rd = (ranks_d - ranks_d.mean()) / ranks_d.std()
rs = (ranks_s - ranks_s.mean()) / ranks_s.std()
n = len(rd)
obs = abs(float(rs @ rd) / n)
count = 0
chunk = 50_000
done = 0
while done < B:
    m = min(chunk, B - done)
    idx = np.argsort(rng.random((m, n)), axis=1)  # m random permutations
    rhos = np.abs((rs[idx] @ rd) / n)
    count += int((rhos >= obs - 1e-12).sum())
    done += m
p_perm = (count + 1) / (B + 1)

supported = bool(rho > 0.5 and p_two < 0.01)
out = {
    "n_audits": data["n_audits"],
    "n_points": len(pts),
    "spearman_rho": round(float(rho), 6),
    "p_two_sided_scipy": float(p_two),
    "p_permutation_1e6_seed0": float(p_perm),
    "prereg_bar": "rho > 0.5 and p < 0.01",
    "rho_exceeds_bar": bool(rho > 0.5),
    "p_below_bar": bool(p_two < 0.01),
    "verdict": "SUPPORTED" if supported else "NOT SUPPORTED",
    "per_score_summary": {
        str(int(s)): {
            "n": int((scores == s).sum()),
            "median_drift_pp": float(np.median(drifts[scores == s])),
            "mean_drift_pp": round(float(drifts[scores == s].mean()), 4),
            "max_drift_pp": float(drifts[scores == s].max()),
        }
        for s in sorted(set(scores))
    },
}
print(json.dumps(out, indent=2))
with open("drift_confirmatory_result.json", "w") as f:
    json.dump(out, f, indent=2)
