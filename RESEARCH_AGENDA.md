# Standing Research Agenda — qrc-shot-wall autonomous program

## AUTHORITATIVE STATE (2026-07-03 ~13:55 — supersedes any older copy)

**READ THE LIVE REPO README FIRST. It is ground truth.** This agenda was once out of date
and caused near-duplicate work; if this file disagrees with the README, trust the README
and push a corrected agenda.

Completed and pushed (see README + results/ for details):
- B1-B4: shot wall, gap strategies, task-shaped wall, hardware run (0.886 on ibm_marrakesh).
- B5: parameter-free measurement-wall law (R2=0.991, 150 cells) - RESULTS_LAW.md
- B6: gate noise as effective-shot reduction S_eff=S*c(gamma)^2 (420 cells, R2=0.927) - RESULTS_GATENOISE.md
- B7: per-node/covariance refinement - HONEST NEGATIVE (residual is shot-irreducible) - RESULTS_PERNODE.md
- B8: beyond depolarizing - scalar factor insufficient; T1 damping is the shot-irreducible case - RESULTS_BEYONDNOISE.md
- B9: margin estimation at scale - plug-in bias +41% trap; parameter-free debias to <=0.8% - RESULTS_MARGINEST.md
- B10: the law is a retrained-readout law; retraining recovers mean 24.5pp - RESULTS_RETRAIN.md
- B11: external validity on Mackey-Glass family - wall harsher, law calibrated (MAE 2.2pp),
  pre-registered R2>0.9 bar FAILED at 0.79 and reported honestly - RESULTS_TASKFAM.md
- SUPPLEMENTARY (13:10 run, executed off a STALE agenda copy — see Log): self-calibrated
  budget prediction from a single noisy pilot. H refuted (split-pilot+debias 5.7pt MAE);
  post-hoc smoothing predictor Phi(g_hat/sqrt(sigma_S^2+v_pilot)) reaches 3.8pt MAE /
  R2=0.915 at S_pilot=8000; downward budget extrapolation ~solved (<=2.2pt), upward
  (S>>S_pilot) open. Files: results/RESULTS_SELFCAL.md, results/b6_selfcal.json,
  figures/b6_selfcal.png, src/b6_selfcal.py (+aggregate/fig). NOTE: overlaps B9 (margin
  debiasing) and B10 (fixed-vs-retrained readout); needs a reconciliation pass — its
  "B6" label refers to the stale numbering, not RESULTS_GATENOISE B6.

## HARD GUARDRAILS (never violate)

1. NEVER submit to real IBM hardware; never read/use any token file. Simulation only.
2. Touch nothing but this GitHub repo and your own session workspace.
3. Pre-registered hypotheses; failures reported as failures; honesty section in every writeup.
4. All bash calls <=45s (chunk + partial .npy).
5. If push impossible, log under Pending push.
6. ALWAYS push the updated agenda in the same commit batch as results.
7. raw.githubusercontent.com can serve STALE content (CDN cache, observed 2x on 07-03).
   Before acting, cross-check freshness: fetch https://github.com/AmirshayanHamidin/qrc-shot-wall/commits/main
   (or the README) and confirm this agenda's latest Log entry matches the newest
   agenda-touching commit. If mismatch, fetch the file at the exact commit SHA instead.

## Queue (top-down)

- [ ] B12 - Encoding-gain sweep (queued by B10's caveat). How does the fixed-vs-retrained
      readout gap close as exact separation degrades? Sweep encoding gain (and/or feature
      dropout) to move exact accuracy from 1.00 toward the floor; measure fixed-readout
      accuracy, retrained accuracy, and law prediction at each point. Pre-register thresholds:
      hypothesis is that retraining gain shrinks monotonically with exact margin and the law
      tracks the retrained readout within ~3pp outside the perfect-separation regime.
      (Note: RESULTS_SELFCAL's frozen-pilot-readout data may be reusable here.)
- [ ] B12b - Reconciliation pass: compare RESULTS_SELFCAL vs RESULTS_MARGINEST (B9) and
      RESULTS_RETRAIN (B10); fold any genuinely novel piece (pilot->budget accuracy
      prediction, the gauss smoothing identity) into the preprint narrative; mark the rest
      as duplicate. Small, do together with or right after B12.
- [ ] B13 - Consolidate: PREPRINT.md. Full arXiv skeleton: abstract, B1-B12 narrative
      (wall -> law -> gate-noise extension -> limits (B7/B8) -> usability at scale (B9/B10) ->
      external validity (B11) -> design guidance), derivation sketch, limitations, future work.
- [ ] B14 - Related-work pass. Web-search the QRC/QML literature (exponential concentration,
      shot-budget analyses, QRC hardware demos); write RELATED_WORK.md mapping which findings
      are known, adjacent, or novel, with specific citations. This decides the preprint's claims.

## Log

- 07-03 03:00 agenda created; 04:15-11:15 runs delivered B6-B11 (see above).
- 07-03 12:30 stale agenda pushed by main session (its error), corrected 13:40. Rule 6 added.
- 07-03 13:10-13:55 scheduled run: STEP-1 raw fetch returned the stale 12:30 agenda (CDN
  cache), so the run executed the outdated "B6 self-calibration" item and briefly overwrote
  the 13:40 authoritative agenda. Detected via commit history during verification; this
  commit restores the authoritative state, files the self-cal work as SUPPLEMENTARY, adds
  guardrail 7 (freshness check), and queues B12b (reconciliation). The self-cal science
  itself is sound and fully pushed (4 commits, 1e98b50..52bd507).

## Pending push
(none)
