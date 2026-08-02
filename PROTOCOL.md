# The Verified Autonomous Research (VAR) protocol — v1.0

A six-rule verification protocol for research conducted with substantial autonomous (AI) assistance. Adopted in this repository 2026-07-05; the audit history in [`AUDITS.md`](AUDITS.md), the operational log in [`RESEARCH_AGENDA.md`](RESEARCH_AGENDA.md), and the commit record show the rules in use.

## Motivation

AI systems can now run experiments and draft research end-to-end. Independent evaluations of such systems repeatedly flag the same weakness: uneven rigor and claims that are hard to verify after the fact. As AI-assisted results scale, the scarce commodity is not producing numbers but trusting them. The goal of this protocol is that the trustworthiness of a result be checkable from the public record alone, without relying on testimony about how the work was done.

## The six rules

1. **Pre-register or it didn't happen.** Every benchmark states one falsifiable hypothesis with numeric success criteria before any experiment runs. Criteria are never moved after data.
2. **Failures are results.** Negative outcomes are published with the same prominence and format as positive ones (for example `results/RESULTS_PERNODE.md`, a pre-registered correction that did not work, reported as such).
3. **The repository is the lab notebook.** Public version control is the only memory. Every working session reads the live repository as ground truth and publishes its increment — write-up, raw values, code, figure — in one batch; work is never left half-published.
4. **Honest baselines.** Comparison methods receive the same tuning effort as the proposed method, plus a no-method floor. An untuned baseline is treated as a protocol violation.
5. **Audit mode is mandatory.** When the work queue empties, effort switches from generating results to auditing them: re-running published numbers from published code and logging confirmations and discrepancies to the audit file. Incidents (state loss, overwrites, stale caches) are logged, repaired, and converted into new guardrails.
6. **Human sign-off gate.** Nothing leaves the repository — preprint submission, external claims — without a named human reviewing and taking responsibility for every claim.

## Properties

A repository following these rules is checkable by construction: any reader can re-run any claim from committed code, see what was predicted before the data arrived, and read the incident log. Credibility attaches to the trail rather than to whoever, or whatever, generated the work. The rules have been exercised here in practice: an audit found one headline result not reproducible from the committed code (B5), and the finding, the restoration from a pinned-convention generator, and the corrected numbers are all part of the public record. On two occasions an accidental duplicate session re-executed a benchmark blind and reproduced its verdicts; both incidents are logged.

The protocol is model-agnostic and domain-agnostic.

*Amirshayan Hamidin, 2026. Contact: hamideinamirshayan@gmail.com*
