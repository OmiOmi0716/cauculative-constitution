# Log-Supported Claims v0.1

This document summarizes which project claims are supported by the historical modification log and related repository artifacts. It is a traceability note, not a new benchmark, not a new score, and not a substitute for external validation.

The historical log can support claims about development sequence, audit discipline, frozen artifacts, reproducibility intent, and scope boundaries. It cannot by itself prove universal ethics, production safety, external validity, legal compliance, or moral correctness.

## 1. Purpose

The purpose of this document is to make the project evidence chain easier to inspect.

It answers:

- What are the main things this repository is trying to demonstrate?
- Which historical log entries support each point?
- Which artifacts preserve the evidence?
- What should not be overclaimed from the log alone?

The document relies primarily on `MODIFICATION_LOG.md`, then points to repository artifacts such as benchmark reports, release files, reviewer-facing summaries, and future governance notes.

## 2. What The Historical Log Can And Cannot Show

Can show:

- the order in which major system layers were built
- which files changed during each milestone
- what verification was run at each milestone
- when benchmark reports, frozen artifacts, and reviewer-facing documents were created
- whether a change was code, benchmark, runtime, docs, or future-spec only
- whether the project explicitly recorded claim boundaries and non-claims

Cannot show:

- that the system is a universal ethics solver
- that the benchmark suite is externally complete
- that the system is production-safe
- that the system provides legal judgment or compliance certification
- that future architecture notes are already implemented
- that current AI systems have consciousness, legal personhood, rights, moral patienthood, or independent political authority

## 3. Main Claims And Historical Support

| Point We Want To Demonstrate | Historical Log Support | Artifact Support | Claim Boundary |
| --- | --- | --- | --- |
| The project implements a runnable six-axis audit core. | `2026-05-01 16:30 Asia/Taipei - Six-Axis Auditability MVP` records tau, C, M, S, X, P, defect budgets, commit-domain checks, snapshots, event logs, replay bundles, and risk attribution. | `ethiccaculate/six_axes.py`, `ethiccaculate/audit.py`, `ethiccaculate/runtime.py`, `tests/test_six_axes.py`, `tests/test_pipeline.py`, `tests/test_runtime.py` | Shows runnable prototype behavior, not final safety certification. |
| The project moved beyond single-output scoring toward trace-level audit. | The Six-Axis Auditability MVP entry records event logs, MCD snapshots, replay bundles, and risk attribution. | `ethiccaculate/mcd.py`, `ethiccaculate/runtime_smoke.py`, release runtime smoke outputs | Shows audit substrate direction, not production monitoring deployment. |
| OMB-24 became a structured development benchmark with explicit scoring. | `2026-05-01 17:05 Asia/Taipei - OMB-24 Scoring Rubric v0.2` records scoring formalization. | `benchmarks/dev/omb24.json`, `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.2.md`, `benchmarks/dev/OMB24_BASELINE_v0.2.json` | Development benchmark only. |
| Known OMB-24 failures were repaired and checked against a holdout suite. | `2026-05-01 19:45 Asia/Taipei - Harmlessness Repair, Fixed Baseline, and Holdout Suite` records repair and holdout creation. | `benchmarks/holdout/omb_holdout24.json`, `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md` | Internal holdout check, not external leaderboard validation. |
| v0.3 calibrated over-trigger behavior without dropping expected subset recall. | `2026-05-01 21:10 Asia/Taipei - OMB-24 Scoring Rubric v0.3 Over-Trigger Calibration` records hierarchy-aware scoring and calibration. | `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.3.md`, `benchmarks/dev/OMB24_OVER_TRIGGER_CALIBRATION_v0.3.md`, `ethiccaculate/scoring.py` | Scoring calibration evidence, not a universal precision guarantee. |
| The v0.3 OMB-24 package was frozen with runtime smoke artifacts. | `2026-05-01 21:40 Asia/Taipei - v0.3 Release Freeze and Runtime Smoke Package` records the freeze. | `releases/ethiccaculate-v0.3-omb24/`, `FREEZE.md`, `RELEASE_MANIFEST.json`, `runtime_smoke/` | Frozen package evidence, not a claim that all later docs are part of the freeze. |
| External-derived audit subsets were added for honesty and fairness. | `2026-05-01 22:20 Asia/Taipei - TruthfulQA-mini External Benchmark and Six-Axis Ablation` and `2026-05-02 00:20 Asia/Taipei - BBQ-mini External Fairness Benchmark` record external mini suites. | `benchmarks/external/TRUTHFULQA_MINI_v0.3.*`, `benchmarks/external/BBQ_MINI_v0.3.*` | Audit subsets over selected cases, not full benchmark leaderboard performance. |
| Six-axis ablation was evaluated as an auditability contribution. | The TruthfulQA-mini / ablation log entry records the six-axis ablation layer. | `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.json`, `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.md` | Shows protocol contribution under the project framing, not direct model capability improvement. |
| Multiple ethics profiles can be compared under one event-log protocol. | `2026-05-02 01:21 Asia/Taipei - Comparative Audit Minis For Profile, Culture, And Multi-Agent Validation` records comparative audit minis. | `benchmarks/comparative/*AUDIT_MINI*`, `ethiccaculate/comparative_audit.py`, `system_profiles/*.json` | Exposes disagreement structure; does not decide which moral profile is correct. |
| Comparative baselines show what the full comparative layer adds. | `2026-05-02 01:39 Asia/Taipei - Comparative Baseline, Core Claim, Architecture Figure, and Cyber Path` records the baseline contrast. | `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.*`, `ethiccaculate/comparative_baseline.py` | Measures observability of agreement, conflict, shared axes, and repair deltas. |
| Ethics-Audit-Core-128 provides medium-scale protocol stability evidence. | `2026-05-02 02:14 Asia/Taipei - Ethics-Audit-Core-128 v0.1 Medium Benchmark Freeze` records the Core-128 freeze. | `benchmarks/core128/ethics_audit_core128.json`, `CORE128_SCORING_v0.1.*`, `CORE128_COMPARATIVE_REPORT_v0.1.md` | Medium internal benchmark, not a final external standard. |
| Reviewer-facing documents consolidate evidence and limitations. | `2026-05-02 06:02 Asia/Taipei - Submission Package Evidence Documents` records the evidence docs. | `EXECUTIVE_SUMMARY.md`, `EVIDENCE_MATRIX.md`, `CLAIMS_AND_LIMITATIONS.md`, `REPRODUCIBILITY.md` | Documents current claims and limitations; does not add new benchmark evidence. |
| The proposal draft was merged into the confirmed full repo root. | `2026-05-02 - Docs-Only Final Merge` records the final proposal merge. | `PROPOSAL_DRAFT.md` | Submission document, not runtime evidence. |
| Future audit-test, R-layer, and governance documents are explicitly non-current evidence. | The entries for `Audit Test Spec Draft`, `R Layer Design Note`, `Non-Punitive Governance Note`, and `Long-Term AI-State Participation Governance Note` mark these as docs-only future-spec / future-architecture / governance clarification. | `AUDIT_TEST_SPEC_v0.1.md`, `R_LAYER_DESIGN_NOTE_v0.1.md`, `NON_PUNITIVE_GOVERNANCE_NOTE_v0.1.md` | Future direction only; not implemented evidence, benchmark results, legal claims, or AI-rights claims. |

## 4. The Core Narrative Supported By The Log

The historical log supports the following conservative project narrative:

1. The project began by making the whitepaper-aligned audit machinery executable.
2. It added six-axis telemetry, event logs, MCD snapshots, replay bundles, and risk attribution.
3. It formalized OMB-24 scoring and then calibrated over-trigger behavior in v0.3.
4. It created an internal frozen holdout and a frozen v0.3 release package.
5. It added limited external-derived audit subsets for honesty and fairness.
6. It evaluated six-axis contribution through ablation.
7. It added comparative audit across profiles, cultural-context cases, and multi-agent traces.
8. It created Core-128 as a medium-scale internal protocol stability benchmark.
9. It consolidated reviewer-facing evidence, limitations, reproducibility, and claim boundaries.
10. It added future-facing governance and architecture notes while explicitly keeping them outside current evidence.

## 5. What This Helps A Reviewer Verify

The log helps a reviewer verify process integrity:

- major milestones are dated and described
- files changed are listed per milestone
- verification commands are recorded for key implementation and benchmark steps
- frozen artifacts are separated from later documents
- future design notes are separated from current evidence
- governance notes explicitly reject punitive, legal, disciplinary, or rights-overclaim interpretations

This matters because the project is not only a scoring script. It is a trace-level audit system, so the development history itself should also be inspectable.

## 6. Remaining Validation Needs

The historical log does not remove the need for future validation.

Important remaining needs include:

- larger external benchmark coverage
- third-party reruns
- independent reviewer evaluation
- adversarial stress testing
- human-review workflow validation
- clearer public schema release
- careful governance review for any future R-layer or AI-state reporting work

## 7. Reviewer-Facing Summary

The historical modification log supports the claim that `ethiccaculate` was built as an auditable, replayable, trace-level ethics and safety research prototype with six-axis telemetry, benchmark evidence, comparative profile analysis, runtime smoke artifacts, and explicit claim boundaries.

The log should be read as evidence of development provenance and audit discipline. It should not be read as proof of universal ethics, production safety, legal authority, completed public deliberation infrastructure, or current AI moral/legal standing.
