# Audit log

Verification-only entries: independent re-runs of published benchmarks against their written claims. Format per entry: what was re-run, how independently, verdict (CONFIRMED / DISCREPANCY), numbers side by side.

## 2026-07-03 — B13 (RESULTS_SMALLMARGIN.md): independent re-implementation — **CONFIRMED**

**Circumstance.** This scheduled session began with a stale CDN copy of the README (pre-B13) and, before discovering the published B13, independently re-implemented the small-margin sweep from the B11/B12 specifications alone — without ever seeing `src/qrc_smallmargin.py` or its write-up. That accident is a stronger audit than a code re-run: same design, independently written code (different sampling-seed convention: `default_rng(1000*seed + S)` vs the published run's; independently re-transcribed pipeline), so agreement tests the *result*, not the file.

**Side-by-side (120 cells each, retrained readout, 250 shots unless noted):**

| Claim in RESULTS_SMALLMARGIN.md | Published | Independent re-run | Verdict |
|---|---|---|---|
| H1 pooled ρ(IPS†, acc@250) fails the +0.5 bar | +0.069 (p=0.75) | +0.109 (p=0.61) | confirmed (fails clearly in both) |
| Within-task ρ @250: updown | +0.88 | +0.90 | confirmed |
| Within-task ρ @250: prodmed | +0.77 | +0.72 | confirmed |
| Within-task ρ @250: accel | +0.60 (p=0.12) | +0.79 (p=0.02) | confirmed direction; magnitude differs (accel is the low-dynamic-range task both write-ups flag) |
| Within-task effect decays with budget | +0.8 → +0.02 @64k | +0.80 → +0.03 @64k | confirmed |
| Star topology-mean acc @250 | 0.784 | 0.789 | confirmed (±sampling seeds) |
| Star vs all-to-all | +4.9 pp, p=0.002 | +5.0 pp, 6/6 config-level wins, p=0.03‡ | confirmed |
| Star vs chain / ring not significant | +1.9 pp, p=0.11–0.22 | +1.6 / +2.4 pp, p=0.44 / 0.56 | confirmed |
| Exact accuracy span 0.961–1.000 | yes | 0.961–1.000 | confirmed exactly |
| Depth-2 collapses IPS | 3–29× | ~6× mean (e.g. all2all updown 0.51→0.02, 25×) | confirmed |
| Fixed readout below classical floor at 250 shots | (B11-consistent) | 0.614 vs floor 0.625; retraining +15.2 pp | confirmed |

† published test uses log IPS, re-run uses raw IPS — rank correlation is nearly invariant to the monotone transform; both reported.
‡ re-run paired at config level (n=6) vs published seed level (n=18), hence the weaker p at the same effect size.

**Verdict: CONFIRMED.** Every qualitative claim and every headline number in RESULTS_SMALLMARGIN.md reproduces under an independent implementation with different sampling seeds; residual differences (≤1.6 pp in accuracies, ≤0.19 in within-task ρ on the weakest task) are consistent with 3-seed sampling variance and protocol microdifferences. No discrepancies found. The re-run's raw cells are preserved in this session's local copy but are deliberately **not** pushed over the published `smallmargin_law.json` — the published file remains the file of record.

*Audit code: independent `qrc_smallmargin.py` variant (this session); pre-registration of its own H1–H3 was written before any run, and its pooled H1/H3 also failed — consistent with the published honest negative.*
