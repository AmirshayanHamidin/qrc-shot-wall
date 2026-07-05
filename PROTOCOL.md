# The Verified Autonomous Research (VAR) Protocol — v1.0

*Status: category-defining spec, first published 2026-07-05. Case study #1: this repository
(13 benchmarks, live QPU validation, 40+ autonomous sessions, full audit trail below in
AUDITS.md and the commit history).*

## The problem

AI systems now generate research end-to-end (Sakana AI Scientist, Google Co-Scientist,
AI-Researcher). Independent evaluations consistently flag the same gap: uneven rigor and
unverifiable claims. As AI-generated papers scale, the scarce commodity is no longer
producing results — it is trusting them. VAR is a protocol for making autonomous research
*audit-proof by construction*.

## The six rules

1. **Pre-register or it didn't happen.** Every benchmark states one falsifiable hypothesis
   with numeric success bars BEFORE any experiment runs. Bars are never moved after data.
2. **Failures are results.** Negative outcomes are published with the same prominence and
   format as positives (see RESULTS_PERNODE.md — a pre-registered correction that didn't
   work, reported as such).
3. **The repo is the lab notebook.** Public git is the only memory. Every run of the
   autonomous loop reads the live remote as ground truth, publishes its increment (writeup +
   raw numbers + code + figure) in one batch, and never leaves work half-published.
4. **Honest baselines.** Comparison methods get the same tuning effort as the proposed
   method, plus a no-method floor. An untuned baseline is treated as a protocol violation.
5. **Audit mode is mandatory.** When the queue empties, the loop switches from generating to
   auditing: re-running published numbers from published code, logging confirmations and
   discrepancies to AUDITS.md. Incidents (state loss, overwrites, stale caches) are logged,
   repaired, and turned into new guardrails — see the Log in RESEARCH_AGENDA.md.
6. **Human sign-off gate.** Nothing leaves the repo (preprint submission, external claims)
   without a named human reviewing and owning every claim.

## Why this beats "AI scientist" systems at trust

A VAR repository is self-prosecuting: any reader can re-run any claim, see what was
predicted before data arrived, and read the loop's own incident reports. The credibility
does not come from the model that generated the work — it comes from the trail the
protocol forces. Replication happened here by accident (a stale-cache incident re-executed
benchmark B13 blind and reproduced every verdict) and the protocol turned even that into
evidence.

## Adopt it

The protocol is model-agnostic and domain-agnostic (this instance: quantum ML on a consumer
laptop at ~$0 infrastructure). A portable skill implementing the loop is available from the
author. Next program under this protocol: autonomous audit of published third-party ML
results — replication as a routine, logged, public pass.

*Amirshayan Hamidin, 2026. Contact: hamideinamirshayan@gmail.com*
