# B13 — The small-margin regime: B12's design rule, re-tested where the margins are thin

**Status:** complete (2026-07-03, scheduled overnight run). **Simulation only** (numpy
density matrix + qiskit unitary; multinomial sampling noise). No hardware, no runtime
service, no token use.
Code: `src/qrc_smallmargin.py`. Raw: `results/smallmargin_law.json` (120 cells +
summary + post-hoc diagnostics). Figure: `figures/qrc_smallmargin.png`.

## Why this benchmark

B12 answered the redirected question in the *maximal-headroom* regime: on parity-family
tasks where every topology reaches exact accuracy 1.00, information-per-shot
(IPS = Σ Δμ²/σ², computed noiselessly at design time) varied 14–56× across coupling
graphs and predicted shot-limited accuracy at pooled Spearman **ρ = +0.90** (250 shots),
with the star (hub) reservoir decisively first (0.924 vs 0.79). B12's own limitations
section queued exactly this follow-up: repeat the sweep on B11's razor-thin-margin
Mackey-Glass family, "where exact separation is not perfect and IPS differences may
reshuffle." B13 does that and nothing else: same 8 reservoirs (chain/ring/star/all2all ×
depth 1–2, same parameter seed), same design metrics, same retrained-readout evaluation
(`qrc_law.perf`), swapped onto B11's three Mackey-Glass classification tasks
(`updown`, `accel`, `prodmed`) at S ∈ {250, 1k, 4k, 16k, 64k} × 3 sampling seeds
→ **120 cells**.

**Pipeline verification before running:** the B13 code path (unitary construction,
injection, features, design metrics) rebuilt B12's star-L1/parity-3 configuration and
reproduced the published IPS = 0.182502, PR = 13.3782 to machine precision.

## Pre-registered hypotheses (stated in the script header before any run)

> **H1 (IPS survives the small-margin regime).** Pooled over the 24 (topology × depth ×
> task) configurations, Spearman ρ(log IPS, retrained noisy accuracy) at S=250 satisfies
> **ρ ≥ +0.5 with p < 0.01**, decaying with budget (B12's wall signature). Pre-registered
> caveat: exact accuracy is not matched here, so ρ(log IPS, retention) is the secondary
> endpoint and the exact-accuracy spread is reported.
> **H2 (the star rule transfers).** Star has the highest topology-mean accuracy at 250
> shots, as on parity.
> **Falsifiers:** ρ < 0.5 or p ≥ 0.01 → IPS as a design objective is regime-bound and
> B12's practical advice does not generalise — reported as a negative.

## H1 — FALSIFIED as registered (and the diagnosis is more interesting than a pass)

The pre-registered pooled statistic **fails, and not marginally**:

| budget S | pooled ρ(log IPS, acc) | p | secondary: ρ(log IPS, retention) |
|---|---|---|---|
| 250 | **+0.069** | 0.75 | −0.02 |
| 1 000 | +0.082 | 0.70 | −0.02 |
| 4 000 | −0.133 | 0.53 | −0.19 |
| 16 000 | −0.141 | 0.51 | −0.12 |
| 64 000 | −0.232 | 0.27 | −0.22 |

By the pre-set bar (ρ ≥ 0.5, p < 0.01), **H1 is falsified**: pooled across tasks, IPS
does not predict shot-limited accuracy in the small-margin regime. The bar is reported,
not moved.

**Post-hoc diagnosis (labeled as such; computed after seeing the failure).** The pooled
number hides a strong *within-task* effect. At 250 shots, within each task separately:
`updown` ρ = **+0.88** (p = 0.004), `prodmed` ρ = **+0.77** (p = 0.03), `accel`
ρ = +0.60 (p = 0.12, n = 8 each). Standardizing log IPS and accuracy within task and
then pooling gives ρ = **+0.816 (p < 10⁻⁴)** at 250 shots, +0.81 at 1k, decaying to
+0.02 at 64k — precisely B12's wall signature (strong where the wall bites, gone at
saturation). What breaks is the *cross-task* comparison: IPS scales differ by task
(accel's IPS runs 2–4× updown's at the same accuracy cost) while floors and task
difficulty differ too (floors 0.55–0.68 here vs a uniform ~0.5 for parity), so the raw
pooled rank correlation is scrambled by between-task offsets — visible directly in
panel A of the figure. B12's pooled ρ = +0.90 was, in hindsight, partly a gift of the
parity family's uniformity (matched floors, matched exact = 1.00, huge 14–56× IPS
ranges).

**Corrected scope for the design rule:** IPS is a **within-task** design objective —
given *your* task, ranking candidate reservoirs by Σ Δμ²/σ² still picks better ones with
ρ ≈ +0.8 in the wall regime, in a second task family, with no refit. It is **not** a
task-transferable absolute score, and B12's headline pooled correlation should be read
with that scope restriction. (For actually choosing a reservoir this is the use case
that matters — a designer optimises within a fixed task — but the pre-registered pooled
claim is the one that was tested, and it failed.)

## H2 — passes literally, but the honest reading is "weakened"

Star ranks first at 250 shots (task-and-depth-mean accuracy):

| topology | acc @ 250 | mean IPS | exact |
|---|---|---|---|
| **star** | **0.784** | 0.63 | 0.982 |
| chain | 0.765 | 0.48 | 0.981 |
| ring | 0.765 | 0.41 | 0.985 |
| all-to-all | 0.735 | 0.34 | 0.985 |

But seed-level paired tests (18 paired cells per comparison) show the B12-style decisive
star advantage does not transfer: star beats **all-to-all** by +4.9 pp (Wilcoxon
p = 0.002, 16/18 wins) — robust — while star vs chain (+1.9 pp, p = 0.22) and vs ring
(+1.9 pp, p = 0.11) are **not significant** at this sample size. Per task, star is first
on `updown` and `prodmed` but drops to ~tied second on `accel`. So the transferable,
statistically solid part of the topology ranking is **"all-to-all is reliably worst in
both regimes"** (most couplings, least information per shot — again), while "star wins"
shrinks from +13 pp to a +1.9 pp trend.

## Secondary observations

- **Depth hurts here.** L2 reservoirs have 3–29× lower IPS than their L1 counterparts on
  every topology (e.g. all-to-all updown: 0.505 → 0.017), and correspondingly lower
  shot-limited accuracy. Deeper scrambling spreads the thin Mackey-Glass margins into
  less-readable observables. (In B12's parity regime, depth was roughly neutral.)
- **The matched-accuracy condition survives.** Exact retrained accuracy spans only
  0.961–1.000 (std 0.014) across all 24 configurations, so — as in B12 — the accuracy
  differences under sampling are information-per-shot differences, not expressivity
  differences.
- **The wall is harsh here, as B11 found:** mean retention at 250 shots is 0.34 with a
  retrained readout (parity-regime retention at 250 shots was far higher for the star).

## Honesty section

- H1 failed at its pre-registered bar; the within-task rescue is post-hoc and is labeled
  post-hoc both here and in the JSON (`summary.posthoc_diagnosis.note`). A confirmatory
  test of the within-task claim on a *third* family would be needed to promote it beyond
  post-hoc status.
- H2's literal pass is reported together with the paired-test non-significance against
  chain/ring; quoting "star wins" without that would overstate the result.
- 3 tasks × 8 reservoirs gives n = 8 per within-task correlation and n = 24 pooled —
  small; p-values are indicative, not decisive. 3 sampling seeds per cell.
- Same single reservoir-parameter seed as B12 (seed 3) for comparability; topology
  conclusions could shift under reseeding (unswept here, as in B12).
- `accel` is near its floor at all budgets (hard task), compressing its dynamic range;
  it contributes little signal to any correlation, echoing B11's R² lesson.

## One-line takeaway

In the small-margin regime the pre-registered pooled IPS→accuracy claim **fails**
(ρ = +0.07 vs B12's +0.90) — IPS survives only as a *within-task* design objective
(within-task ρ ≈ +0.8 at low budgets, post-hoc) — and the star advantage shrinks to a
non-significant +1.9 pp, leaving "avoid all-to-all coupling" as the only
topology rule that transfers robustly between regimes.
