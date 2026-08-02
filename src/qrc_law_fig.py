"""Regenerate figures/qrc_law.png from results/law_rerun.json (committed data only).

Provenance (2026-08-02): the previous figures/qrc_law.png came from the ORIGINAL B5 run
and quoted the retired headline (R^2 = 0.991 / MAE 1.3 pp), found not reproducible from
committed code by the 2026-07-04 audit (AUDITS.md). Its left panel (naive-SNR
"hypothesis v1", FAILED, R^2 = 0.20) was built from the original-run observations, which
have no committed generator; that honest negative remains narrated in RESULTS_LAW.md
("A law that failed first"), and the original figure remains in git history.

This script draws ONLY from results/law_rerun.json (the restored 8-seed observation
protocol, src/qrc_law_rerun.py, seeds 1-8) and is self-verifying: it recomputes
R^2 / MAE / bias overall and per budget from the raw cells and asserts equality with the
stored summary block before rendering. Stored-only quantities (r2_noise_corrected,
mae_floor_8seed_pp) are displayed as stored and labeled as such.

Usage: python qrc_law_fig.py  (from src/; writes ../figures/qrc_law.png)
"""
import json, math, os
os.environ.setdefault("MPLCONFIGDIR", "/tmp")
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "results", "law_rerun.json")
OUT  = os.path.join(HERE, "..", "figures", "qrc_law.png")

d = json.load(open(DATA))
cells, S = d["cells"], d["summary"]
assert len(cells) == S["n_cells"] == 150, len(cells)

pred = np.array([c["pred"] for c in cells])
obs  = np.array([c["obs_mean"] for c in cells])
sd   = np.array([c["obs_std"] for c in cells])
shots = np.array([c["shots"] for c in cells])
budgets = sorted(set(shots.tolist()))

def stats(p, o):
    r2   = 1.0 - np.sum((o - p) ** 2) / np.sum((o - o.mean()) ** 2)
    mae  = float(np.mean(np.abs(p - o)) * 100)
    bias = float(np.mean(p - o) * 100)
    return float(r2), mae, bias

def check(name, got, want):
    if not math.isclose(got, want, rel_tol=1e-9, abs_tol=1e-12):
        raise SystemExit(f"VERIFY FAIL {name}: recomputed {got!r} != stored {want!r}")

r2_all, mae_all, bias_all = stats(pred, obs)
check("r2", r2_all, S["r2"]); check("mae", mae_all, S["mae_pp"]); check("bias", bias_all, S["bias_pp"])
per = {}
for b in budgets:
    m = shots == b
    r2b, maeb, biasb = stats(pred[m], obs[m])
    sb = S["by_budget"][str(b)]
    check(f"r2@{b}", r2b, sb["r2"]); check(f"mae@{b}", maeb, sb["mae_pp"]); check(f"bias@{b}", biasb, sb["bias_pp"])
    per[b] = (r2b, maeb, biasb)
print("VERIFIED: all recomputed stats match stored summary (rel_tol 1e-9)")
print(f"all-150: R2={r2_all:.4f} MAE={mae_all:.2f}pp bias={bias_all:.2f}pp")
for b in budgets: print(f"  {b:>6}: R2={per[b][0]:.4f} MAE={per[b][1]:.2f}pp bias={per[b][2]:.2f}pp")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 5.4), dpi=150)
colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(budgets)))

for b, col in zip(budgets, colors):
    m = shots == b
    ax1.errorbar(pred[m], obs[m], yerr=sd[m], fmt="o", ms=4.5, color=col,
                 ecolor=col, elinewidth=0.7, alpha=0.75, capsize=0,
                 label=f"{b:,} shots")
lo = min(pred.min(), obs.min()) - 0.02
ax1.plot([lo, 1.0], [lo, 1.0], "k--", lw=1)
ax1.set_xlabel("PREDICTED accuracy (noiseless sim + exact shot-noise projection)")
ax1.set_ylabel("OBSERVED accuracy (mean of 8 sampling seeds, ±1 sd)")
ax1.set_title(f"Matched-filter law — restored 8-seed protocol\n"
              f"R² = {r2_all:.3f} ({S['r2_noise_corrected']:.3f} noise-corr.*), "
              f"MAE = {mae_all:.1f} pp, bias = {bias_all:+.1f} pp\n"
              f"{len(cells)} cells, zero fitted parameters", fontsize=10)
ax1.legend(loc="lower right", fontsize=8, title="shot budget", title_fontsize=8)

x = np.arange(len(budgets))
maes = [per[b][1] for b in budgets]; r2s = [per[b][0] for b in budgets]
ax2.bar(x, maes, width=0.55, color=colors, alpha=0.85, label="MAE (pp)")
ax2.axhline(S["mae_floor_8seed_pp"], color="gray", ls=":", lw=1.2)
ax2.text(len(budgets) - 0.55, S["mae_floor_8seed_pp"] + 0.07,
         f"8-seed observation noise floor* ({S['mae_floor_8seed_pp']:.2f} pp)",
         fontsize=8, color="dimgray", ha="right",
         bbox=dict(facecolor="white", alpha=0.75, edgecolor="none", pad=1.5))
ax2.set_xticks(x, [f"{b:,}" for b in budgets])
ax2.set_xlabel("shot budget"); ax2.set_ylabel("MAE (percentage points)")
ax2.set_ylim(0, max(maes) * 1.25)
axr = ax2.twinx()
axr.plot(x, r2s, "o-", color="crimson", lw=1.6, ms=5, label="R²")
axr.set_ylabel("R²", color="crimson"); axr.tick_params(axis="y", colors="crimson")
axr.set_ylim(0.8, 1.0)
ax2.set_title(f"Calibration by budget:\n"
              f"R² {per[budgets[0]][0]:.2f} → {per[budgets[-1]][0]:.2f}; MAE stays ~3× above the\n"
              f"seed-noise floor ⇒ genuine law error", fontsize=10)
fig.text(0.995, 0.01, "*stored in law_rerun.json summary (not recomputed here)",
         ha="right", fontsize=7, color="gray")
fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
print("wrote", OUT)
