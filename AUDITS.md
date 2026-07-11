# Audit log

Verification-only entries: independent re-runs of published benchmarks against their written claims. Format per entry: what was re-run, how independently, verdict (CONFIRMED / DISCREPANCY), numbers side by side.

## 2026-07-11 — B6 (RESULTS_GATENOISE.md): full 420-cell re-run from committed code — **CONFIRMED**

**What was re-run.** The entire B6 grid (2 architectures × 5 tasks × 6 γ × 7 shot budgets = 420 cells), from the repo's own committed `src/qrc_gatenoise.py`, unmodified — executed in 12 (arch, γ) slices to fit the 45 s sandbox cap via a thin driver (`audits/audit_b6_rerun.py`) that calls the committed module's functions verbatim and recomputes the deterministic γ=0 reference identically per slice. Environment: numpy 2.2.6, sklearn 1.7.2 (same as all prior audits), qiskit 2.5.0, CPU. Comparison summary: `audits/b6_rerun_check.json`.

**Result: bit-identical.** All 420 cells reproduce `results/gate_noise_law.json` exactly — max |Δacc| = 0, max |Δc| = 0, max |Δexact_sep| = 0 — so every aggregate follows: collapse **R² = 0.927091 / MAE 2.893 pp** and naive baseline **R² = 0.851222 / MAE 4.165 pp**, exactly as published. Independently of the re-run, the stored per-cell `pred_collapse` values were recomputed from the raw γ=0 cells (committed interpolation logic re-derived): max abs diff 1.1e-16; the per-γ table (mean c 0.923/0.819/0.677/0.566/0.481; law MAE 1.8→4.6 pp; naive MAE 2.1→7.2 pp) matches every printed digit, and the "advantage widens monotonically with γ" claim holds (0.24 → 2.61 pp). Unlike B5, B6's generator is committed, complete, and regenerates its published raw file exactly; the pipeline is fully deterministic (fixed input seed, sampling seeds 1–3, lbfgs logistic readout), which is why bit-identity is achievable across library versions.

**One write-up mischaracterization, flagged (doc-level, not numeric).** `RESULTS_GATENOISE.md`'s honest-residual section attributes part of the residual to "hold[ing] the linear readout fixed at its noiseless solution rather than retraining under each γ". The committed code does the opposite: `achievable_acc` **retrains** `LogisticRegression(C=1)` on the noisy features of every cell, and the module docstring says so explicitly ("RETRAINED on the noisy features at each budget"). The published numbers are therefore retrained-readout numbers (self-consistent: the γ=0 reference curve is retrained too, so the collapse maps retrained-to-retrained — consistent with B10's later finding that retraining is load-bearing). The stated residual mechanism should be corrected; the residual magnitude (~2.9 pp) and both R² values are unaffected.

**Verdict: CONFIRMED.** Every number in RESULTS_GATENOISE.md and the README B6 paragraph reproduces exactly from committed code; the raw file of record is untouched. One honesty-section sentence mischaracterizes the readout protocol and is flagged for correction (queued, not silently edited here). B6 no longer carries the "not yet re-audited post-B5" caveat; B10/B11 remain unaudited.

---

## 2026-07-04 (later session) — B5 RESTORATION — closes the 2026-07-04 discrepancy

**What was done (consolidation, not a new benchmark).** The three audit findings below are now remediated in the repo:

1. **Missing generator (finding #3) → committed.** `src/qrc_law_predict.py` is now the canonical prediction generator. Its readout convention is pinned in the docstring: raw-feature logistic regression, C = 10⁴, 70% chronological train split — the convention the audit's reconstruction found to match the published `pred` column (MAE 1.2–1.4 pp). From that file onward the law's prediction is defined by committed code, not by a lost script.
2. **Under-seeded observations (finding #2) → 8 documented seeds.** `src/qrc_law_rerun.py` re-ran all 150 classification cells with sampling seeds 1–8 (observation convention unchanged: `law_eval_arch.py`-style retrained readout). Per-seed accuracies are stored in `results/law_rerun.json`, so the noise floor is recomputable by anyone: 8-seed expected MAE floor = **0.91 pp**.
3. **Irreproducible headline (finding #1) → retired and replaced.** `results/RESULTS_LAW.md` now leads with the restored numbers and a provenance note; README and PREPRINT were updated in the same push. `law_theory.json` remains untouched as the historical file of record.

**Restored headline vs audit estimate vs original claim:**

| | R² | noise-corr. R² | MAE | bias |
|---|---|---|---|---|
| Original claim (retired) | 0.991 | — | 1.33 pp | — |
| Audit estimate (2-seed obs) | 0.922 | ≈0.944 | 3.64 pp | — |
| **Restored (8-seed obs, committed code)** | **0.939** | **0.944** | **3.33 pp** | **−0.98 pp** |

Per-budget R²: 0.855 / 0.897 / 0.946 / 0.950 / 0.962 at S = 250 / 1k / 4k / 16k / 64k. Bias runs −2.7 pp (law pessimistic; retraining recovers margin the fixed-readout probit doesn't see, cf. B10) at 250 shots to +0.85 pp at 64k. The audit's noise-corrected estimate (≈0.944) and the independent 8-seed re-run (0.944) agree to three decimals — the audit's characterization of the law is confirmed end-to-end.

**Still open:** the 30 regression cells were not re-run; B6/B10/B11 quote their own statistics and remain unaudited (B6 and B11 are the suggested next audits); `figures/qrc_law.png` still shows the original run and should be regenerated from `law_rerun.json`.

## 2026-07-04 — B5 (RESULTS_LAW.md): full 150-cell re-run from committed code — **DISCREPANCY FOUND**

**What was re-run.** The entire B5 grid, from the repo's own committed code: `src/qrc_law.py build` for all 6 architectures, then `src/law_eval_arch.py` (retrained readout, documented sampling seeds (1,2)) for all 150 classification cells. Environment: numpy + sklearn 1.7.2, fresh workspace. Raw side-by-side cells and aggregates: `results/audit_b5_repro.json`; audit predictor reconstruction: `src/audit_law_theory.py`.

**Three findings, in decreasing order of severity:**

**1. The committed code does not regenerate the published observations.** Reproduced noisy accuracies differ from `law_theory.json`'s `obs` by MAE 3.92 pp, max **17.6 pp**; 12 of 150 cells deviate by >10 pp. Same-pipeline run-to-run noise (independent seed pairs, measured on arch 0) is MAE 3.3 pp / max 9.7 pp — elevated but comparable in aggregate, so the aggregate alone is not damning. The cell-level evidence is: **arch0/parity4/S=1000 published obs = 0.5955, while eight independent sampling seeds of the committed pipeline span 0.728–0.825** — the published value lies far outside the entire seed distribution and cannot be produced by this code at any seed count. Several neighbouring low-S cells show the same pattern. Four alternative protocol conventions were tested (fixed exact-trained readout: chance level, ruled out; weak-regularization retrained readout: MAE 4.1 pp; budget split across virtual nodes: MAE 8.8 pp; alternative C-grids: contradictory by direction) — none regenerates the published obs.

**2. The published pred–obs agreement is tighter than its own protocol's noise floor.** With 2-seed observations, even a *perfect* law would show |pred−obs| MAE ≈ 0.8 × the 2-seed sampling std. Estimated floors vs published MAE, per budget: S=250: ≥3.8 pp floor vs 1.95 pp published; S=1000: ≥2.2 vs 1.86; S=4000: ≥1.8 vs 1.52; S=16000: ≥1.3 vs 0.79; S=64000: ≥0.6 vs 0.53. Published agreement beats the floor at **every** budget, which is statistically implausible for obs generated by the documented 2-seed protocol. (Floor estimated from arch-0 seed pairs, n=5 cells/budget — rough, but the direction is uniform.)

**3. The prediction-generator script is not in the repo.** `RESULTS_LAW.md` cites `src/qrc_law.py` + `src/law_eval_arch.py`, but neither computes the probit prediction; no committed script produces `law_theory.json`'s `pred` column. A reconstruction from the documented formula (σ² = Σ_nodes [Σ p_j q_j² − (p·q)²]/S, pred = mean Φ(signed margin/σ)) with a raw-feature logistic readout (C=10⁴) matches published pred to MAE 1.2–1.4 pp — close, so the formula is real, but the exact convention (readout regularization, margin set) is unrecoverable. The readout convention matters enormously: the *documented* best-C scaled-pipeline readout gives predictions ≈ 0.50 everywhere.

**What survives.** The claim's arithmetic is internally consistent (recomputing from `law_theory.json`: R² = 0.9909, MAE = 1.332 pp — matches the stated 0.991/1.3). And the law itself survives the re-run *qualitatively*: published predictions vs independently reproduced observations give **R² = 0.922, MAE = 3.64 pp** (2-seed obs; correcting for obs sampling noise, R² ≈ 0.944), improving from R² 0.82 at 250 shots to 0.96 at 64k. A zero-parameter prediction at ~3.6 pp MAE across 150 cells is still a strong, useful law.

**Verdict: DISCREPANCY.** The qualitative B5 claim (parameter-free probit law predicts shot-limited accuracy) is **confirmed** at R² ≈ 0.92–0.94. The headline precision **R² = 0.991 / MAE 1.3 pp is not reproducible** from the committed code, the published observations' provenance is unclear for at least a subset of cells, and the prediction generator is missing from `src/`. Until the original generator scripts are restored and the grid re-run with ≥8 documented seeds, README/PREPRINT should quote the reproduced numbers (R² ≈ 0.92, MAE ≈ 3.6 pp, noise-corrected R² ≈ 0.94) or explicitly flag the headline as unaudited. Downstream note: B6/B10/B11 quote or build on the 0.991 figure; their own numbers were not re-checked today. *(Update, later session same day: restoration completed — see entry above.)*

*Caveats: audit ran sklearn 1.7.2 / current numpy — environment differences could shift marginal cells a few pp, but cannot explain 13–18 pp deviations on cells where eight seeds bracket a disjoint range. The published `law_theory.json` remains untouched as file of record.*

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

*Addendum (2026-07-04): a second scheduled session, also starting from a stale CDN README, independently re-implemented B13 a third time before discovering the published version, again reproducing the headline numbers (pooled ρ = +0.069/p = 0.75, star 0.784, star−chain +1.9 pp in 3/3 seeds, exact span 0.961–1.000, within-task ρ = +0.88/+0.77/+0.60). Recorded for completeness; adds a same-convention replication on top of the different-convention one above.*

*Second addendum (2026-07-04, evening scheduled session) — stale-cache incident #3, plus a repair log. This session too started from a pre-B13 CDN copy of the README/agenda (fetched without a cache-buster; the rule added to the agenda after incident #2 was itself invisible for the same reason), concluded the small-margin sweep was still queued, pre-registered its own H1–H3, and re-implemented B13 from the B11/B12 specs. Its independently written pipeline converged on the same seed convention as the 2026-07-03 audit implementation (`default_rng(1000*seed + S)`) and matched that audit's numbers to reported precision — pooled ρ(log IPS, acc@250) = +0.109 (p = 0.61), within-task ρ = +0.90 / +0.79 / +0.72 (updown/accel/prodmed), stratified rank-within-task ρ = +0.80 (p < 10⁻⁵) decaying to +0.04 @64k, star mean 0.789, exact span 0.961–1.000, and additionally PR non-predictive at every budget (|ρ| ≤ 0.12, all p ≥ 0.56, its pre-registered H3). This is a same-convention consistency check of the 07-03 audit implementation rather than new independent evidence for B13. **Process incident, reported honestly:** before discovering the published B13, this session's commit `a2ed28d` overwrote `src/qrc_smallmargin.py` (file of record for the published run) with its replication variant and added a replication-only `qrc_smallmargin_fig.py`. Repaired in the same session: the published code was restored byte-for-byte from parent commit `97319c2`, the fig script was replaced with a provenance stub (the replication code remains in git history at `a2ed28d`), and no results/, figures/, or JSON files of record were touched at any point. Root cause and fix are logged in RESEARCH_AGENDA.md: scheduled runs MUST cache-bust every raw.githubusercontent fetch and verify HEAD against the repo's /commits/main page before choosing a work mode.*
