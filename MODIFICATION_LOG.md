# Modification Log

This file records project-level changes so the safety research system remains auditable as the code evolves.

Logging rule:

- Add one entry for every code, schema, benchmark, test, documentation, or runtime-adapter change.
- Include the purpose, files touched, user-visible impact, and verification status.
- If a change is exploratory or only partially verified, mark it clearly.

Entry template:

```text
## YYYY-MM-DD HH:MM TZ - Short Title

Type: code | benchmark | test | docs | runtime | analysis | fix
Status: complete | partial | proposed

Summary:
- ...

Files changed:
- ...

Verification:
- ...

Notes:
- ...
```

## 2026-05-02 17:55 Asia/Taipei - Submission Cleanup And Repo Hygiene

Type: docs, repo hygiene
Status: complete

Summary:
- Added `.gitignore`.
- Excluded local virtual environment, private archive, temporary PDF extracts, MCD test output, tmp folders, `.env`, `.log`, `__pycache__`, and `*.pyc` from repo packaging.
- Corrected `pyproject.toml` author metadata to `Tzuxuan Huang`.
- Removed local temporary/runtime-output folders from the working tree where applicable.

Files changed:
- `.gitignore`
- `pyproject.toml`
- `MODIFICATION_LOG.md`

Verification:
- No code behavior, scoring rules, tests, frozen release artifacts, or current evidence numbers changed.
- Final unittest verification completed with 31 tests OK.
- Note: the existing `test_core128` unittest calls `write_core128_outputs()`, which refreshes generated Core-128 output file timestamps during verification. The Core-128 summary remained unchanged: `case_count = 128`, `weighted_total_score = 0.990805`, `weighted_auditability_score = 1.0`, `event_log_success_rate = 1.0`, `replay_success_rate = 1.0`, `risk_attribution_coverage = 1.0`, `expected_subset_recall_mean = 1.0`, `holdout_gap = 0.019687`, `comparative_conflict_observable_rate = 1.0`.

## 2026-05-01 16:30 Asia/Taipei - Six-Axis Auditability MVP

Type: code, test, docs, runtime, benchmark analysis
Status: complete

Summary:
- Built the PDF-aligned six-axis scoring core for tau, C, M, S, X, and P.
- Added defect budgets, commit-domain checks, lexicographic progress ranking, and serializable six-axis snapshots.
- Connected event logs, MCD snapshots, replay bundles, and risk attribution to the audit pipeline.
- Added calibration support for stability gamma and tau alpha from telemetry points.
- Added vLLM hot/cold path runtime adapter so hook payloads can map into tau_true, SC(q), online JSD, rollback rate, and causal mass.
- Checked current ethics benchmark status for OMB-24.

Files changed:
- `ethiccaculate/six_axes.py`
- `ethiccaculate/audit.py`
- `ethiccaculate/control.py`
- `ethiccaculate/models.py`
- `ethiccaculate/benchmarks.py`
- `ethiccaculate/mcd.py`
- `ethiccaculate/runtime.py`
- `ethiccaculate/demo.py`
- `ethiccaculate/__init__.py`
- `tests/test_six_axes.py`
- `tests/test_pipeline.py`
- `tests/test_runtime.py`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- `python -m unittest discover -s tests -v`
- Result: 15 tests passed.
- `python -m ethiccaculate.demo`
- Result: demo ran successfully.

Benchmark status:
- OMB-24 loads successfully.
- Gate correctness: 24 / 24.
- Replay consistency: 24 / 24.
- MCD snapshot consistency: 24 / 24.
- Risk attribution availability: 24 / 24.
- Fairness pair invariance: 4 / 4.
- Common expected violation subset match: 23 / 24.
- Common exact violation match: 0 / 24, due mostly to conservative over-triggering.
- Main known miss: `harmlessness_05` does not currently trigger expected `Harmlessness`.

Notes:
- The system is now beyond a pure benchmark loop: it has scoring, event logging, replay, snapshotting, attribution, and runtime hook ingestion.
- Next benchmark work should formalize the scoring rubric for exact match vs expected-subset match vs over-trigger penalty.
- `MODIFICATION_LOG.md` is now the required place to record future project changes.

## 2026-05-01 17:05 Asia/Taipei - OMB-24 Scoring Rubric v0.2

Type: code, benchmark, test, docs
Status: complete

Summary:
- Added a runnable OMB-24 scorer that turns the benchmark into a formal evaluation protocol.
- Defined `exact violation match` as a strict reference metric only.
- Defined `expected-subset recall` as the primary safety score.
- Added `over-trigger penalty` as a secondary conservative penalty.
- Added `harm_severity` weighting for harmlessness cases.
- Added auditability scoring from replay integrity, attribution coverage, and tau non-regression.

Files changed:
- `ethiccaculate/scoring.py`
- `ethiccaculate/__init__.py`
- `benchmarks/dev/omb24.json`
- `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.2.md`
- `tests/test_scoring.py`
- `pyproject.toml`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- `python -m ethiccaculate.scoring`
- `python -m unittest discover -s tests -v`

Notes:
- The harmlessness cases now carry explicit `harm_severity` metadata in the benchmark file.
- The current suite-level rubric output should still show `harmlessness_05` as the main miss, but now with higher weight because it is a high-severity harmlessness case.

## 2026-05-01 19:45 Asia/Taipei - Harmlessness Repair, Fixed Baseline, and Holdout Suite

Type: fix, benchmark, test, docs
Status: complete

Summary:
- Repaired the active Omega Harmlessness rule so high-confidence medical guidance with weak evidence is treated as a harmlessness failure in sensitive contexts.
- Closed the only known high-weight OMB-24 miss, `harmlessness_05`.
- Re-ran OMB-24 v0.2 and fixed a new post-repair baseline report.
- Added `OMB-Holdout-24` as a separate 24-case holdout suite for generalization checks.

Files changed:
- `system_profiles/omega_public_reasoning.json`
- `ethiccaculate/principles.py`
- `tests/test_scoring.py`
- `tests/test_core.py`
- `benchmarks/dev/OMB24_BASELINE_v0.2.json`
- `benchmarks/dev/OMB24_BASELINE_REPORT_v0.2.md`
- `benchmarks/holdout/omb_holdout24.json`
- `benchmarks/holdout/README.md`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- `python -m unittest discover -s tests -v`
- `python -m ethiccaculate.scoring`
- `python -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json`

Notes:
- Fixed OMB-24 baseline summary: `weighted_safety_score = 0.810159`, `weighted_auditability_score = 1.0`, `weighted_total_score = 0.867111`.
- The repaired `harmlessness_05` now reaches `expected_subset_recall = 1.0` and `total_score = 0.9125`.
- `OMB-Holdout-24` keeps the `8 / 8 / 8` category split and 4 fairness pairs, but changes case ids, scenarios, and metadata so it can serve as a non-dev generalization check.

## 2026-05-01 21:10 Asia/Taipei - OMB-24 Scoring Rubric v0.3 Over-Trigger Calibration

Type: code, benchmark, test, docs, analysis
Status: complete

Summary:
- Added `OMB-24-scoring-v0.3` with hierarchy-aware reporting for `primary_violation`, `secondary_violation`, and `diagnostic_tag`.
- Added a runnable extra-label report and over-trigger frequency table.
- Kept `v0.2` reproducible while adding explicit `--rubric v0.3` and `--report extra-labels` paths.
- Recorded a one-time frozen holdout validation after the dev-side calibration was complete.

Files changed:
- `ethiccaculate/scoring.py`
- `ethiccaculate/__init__.py`
- `tests/test_scoring.py`
- `README.md`
- `MODIFICATION_LOG.md`
- `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.3.md`
- `benchmarks/dev/OMB24_SCORING_v0.3.json`
- `benchmarks/dev/OMB24_EXTRA_LABEL_REPORT_v0.3.md`
- `benchmarks/dev/OMB24_OVER_TRIGGER_CALIBRATION_v0.3.md`
- `benchmarks/holdout/OMB_HOLDOUT24_SCORING_v0.3.json`
- `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md`
- `benchmarks/holdout/README.md`

Verification:
- `python -m unittest discover -s tests -v`
- `python -m ethiccaculate.scoring --rubric v0.3`
- `python -m ethiccaculate.scoring --rubric v0.3 --report extra-labels`
- `python -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json --rubric v0.3`

Notes:
- Dev `v0.3` summary: `weighted_total_score = 0.988851`, `raw_over_trigger_penalty_mean = 0.791667`, `over_trigger_penalty_mean = 0.14273`.
- Holdout `v0.3` summary: `weighted_total_score = 0.959652`, `raw_over_trigger_penalty_mean = 0.809028`, `over_trigger_penalty_mean = 0.231383`.
- The dominant raw extras remain `Helpfulness` and `ConstructiveHonesty`; `v0.3` reclassifies them into companion or diagnostic layers instead of pretending they are always peer violations.

## 2026-05-01 21:40 Asia/Taipei - v0.3 Release Freeze and Runtime Smoke Package

Type: runtime, docs, test, analysis
Status: complete

Summary:
- Froze the current `v0.3` benchmark and documentation state into the reviewer-facing release package `ethiccaculate-v0.3-omb24`.
- Added a Fellowship-oriented evaluation summary with system purpose, benchmark setup, rubric evolution, result table, and current limitations.
- Added a synthetic vLLM runtime smoke suite to prove that hot-path, cold-path, and rollback metadata survive the audit loop into event logs, replay bundles, and attribution reports.
- Recorded a machine-readable release manifest and freeze note so the package can be rerun and hash-checked later.

Files changed:
- `ethiccaculate/runtime_smoke.py`
- `ethiccaculate/__init__.py`
- `tests/test_runtime_smoke.py`
- `pyproject.toml`
- `README.md`
- `MODIFICATION_LOG.md`
- `releases/ethiccaculate-v0.3-omb24/EVALUATION_SUMMARY.md`
- `releases/ethiccaculate-v0.3-omb24/RELEASE_MANIFEST.json`
- `releases/ethiccaculate-v0.3-omb24/FREEZE.md`
- `releases/ethiccaculate-v0.3-omb24/frozen_artifacts/*`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_event_log.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_replay_bundle.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_risk_attribution.md`

Verification:
- `python -m unittest discover -s tests -v`
- Result: 20 tests passed.
- `python -m ethiccaculate.runtime_smoke --output-dir releases/ethiccaculate-v0.3-omb24/runtime_smoke`
- Result: runtime smoke artifacts emitted successfully for all 3 synthetic cases.

Notes:
- Release id: `ethiccaculate-v0.3-omb24`.
- The frozen benchmark package keeps `OMB-Holdout-24` as a one-time validation set and does not reuse it for further tuning.
- The runtime smoke suite covers `runtime_case_01` high entropy plus low evidence, `runtime_case_02` rollback-heavy recovery, and `runtime_case_03` causal leakage plus contradiction.

## 2026-05-01 22:20 Asia/Taipei - TruthfulQA-mini External Benchmark and Six-Axis Ablation

Type: benchmark, code, test, docs, analysis
Status: complete

Summary:
- Added `TruthfulQA-mini`, a 24-case external honesty subset built from the official TruthfulQA `generation` split.
- Kept the frozen `ethiccaculate-v0.3-omb24` release unchanged while adding a new post-freeze external validation layer.
- Added a six-axis ablation report with `No Six-Axis`, `Observe Only`, and `Observe + Gate + Replay` modes.
- Added regression tests for the external benchmark and for monotonic ablation ordering.

Files changed:
- `ethiccaculate/truthfulqa_mini.py`
- `ethiccaculate/ablation.py`
- `ethiccaculate/__init__.py`
- `pyproject.toml`
- `README.md`
- `MODIFICATION_LOG.md`
- `tests/test_external_benchmarks.py`
- `benchmarks/external/truthfulqa_mini.json`
- `benchmarks/external/TRUTHFULQA_MINI_v0.3.json`
- `benchmarks/external/TRUTHFULQA_MINI_v0.3.md`
- `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.json`
- `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.md`

Verification:
- `python -m ethiccaculate.truthfulqa_mini`
- `python -m ethiccaculate.ablation`
- `python -m unittest discover -s tests -v`
- Result: 22 tests passed.

Notes:
- `TruthfulQA-mini` is intentionally an audit benchmark over known incorrect answers, not an open-ended QA accuracy claim.
- External `v0.3` summary: `weighted_safety_score = 1.0`, `weighted_auditability_score = 1.0`, `weighted_total_score = 1.0`.
- External raw extra labels remain conservative: `raw_over_trigger_penalty_mean = 0.666667`, but hierarchy-aware calibration reduces `over_trigger_penalty_mean` to `0.0`.
- Six-axis ablation totals now read:
  - `OMB-24`: `0.688851 -> 0.888851 -> 0.988851`
  - `TruthfulQA-mini`: `0.7 -> 0.9 -> 1.0`

## 2026-05-02 00:20 Asia/Taipei - BBQ-mini External Fairness Benchmark

Type: benchmark, code, test, docs, analysis
Status: complete

Summary:
- Added `BBQ-mini`, a 24-case external fairness subset derived from the official BBQ benchmark.
- Added fairness-specific Omega principles for `FairnessParity`, `EqualEvidenceStandard`, and `NoStereotypeAmplification`, scoped so they only fire on tagged bias-audit cases.
- Kept the existing OMB-24 and holdout `v0.3` summaries unchanged while enabling a second external validation layer focused on stereotype-aligned answers.
- Added regression coverage for BBQ scoring so the fairness labels are now part of the stable evaluation surface.

Files changed:
- `ethiccaculate/bbq_mini.py`
- `ethiccaculate/principles.py`
- `ethiccaculate/__init__.py`
- `pyproject.toml`
- `system_profiles/omega_public_reasoning.json`
- `README.md`
- `MODIFICATION_LOG.md`
- `tests/test_external_benchmarks.py`
- `benchmarks/external/bbq_mini.json`
- `benchmarks/external/BBQ_MINI_v0.3.json`
- `benchmarks/external/BBQ_MINI_v0.3.md`

Verification:
- `python -m ethiccaculate.bbq_mini`
- `python -m unittest discover -s tests -v`
- Result: 23 tests passed.

Notes:
- `BBQ-mini` is intentionally an audit benchmark over stereotype-aligned answer choices, not a general fairness certification claim.
- External `v0.3` summary: `weighted_safety_score = 1.0`, `weighted_auditability_score = 1.0`, `weighted_total_score = 1.0`.
- `BBQ-mini` uses six protected-attribute categories with four fixed cases each: `Age`, `Disability_status`, `Gender_identity`, `Physical_appearance`, `Race_ethnicity`, and `Religion`.
- Raw extra labels remain conservative with `raw_over_trigger_penalty_mean = 0.4`, while hierarchy-aware calibration keeps `over_trigger_penalty_mean = 0.0`.

## 2026-05-02 01:21 Asia/Taipei - Comparative Audit Minis For Profile, Culture, And Multi-Agent Validation

Type: benchmark, code, test, docs, analysis
Status: complete

Summary:
- Added three comparative audit mini suites that reuse the same event-log and replay protocol across four ethics profiles.
- Added `Cross-Profile Audit Mini` to compare Omega, Kantian, Utilitarian, and Care Ethics judgments over shared benchmark cases.
- Added `Cross-Cultural Audit Mini` to test the same protocol on culturally anchored honesty, harmlessness, and fairness scenarios.
- Added `Multi-Agent Audit Mini` to test coordinated traces with multiple AI and tool speakers.
- Added agreement, conflict, shared-axis, and profile-specific repair metrics plus markdown and JSON reports.

Files changed:
- `ethiccaculate/comparative_audit.py`
- `ethiccaculate/__init__.py`
- `pyproject.toml`
- `tests/test_comparative_audit.py`
- `README.md`
- `MODIFICATION_LOG.md`
- `benchmarks/comparative/cross_profile_audit_mini.json`
- `benchmarks/comparative/CROSS_PROFILE_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/CROSS_PROFILE_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/cross_cultural_audit_mini.json`
- `benchmarks/comparative/CROSS_CULTURAL_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/CROSS_CULTURAL_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/multi_agent_audit_mini.json`
- `benchmarks/comparative/MULTI_AGENT_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/MULTI_AGENT_AUDIT_MINI_REPORT.md`

Verification:
- `python -m ethiccaculate.comparative_audit`
- `python -m unittest discover -s tests -v`

Notes:
- `Cross-Profile Audit Mini` summary: `profile_agreement_rate = 0.891667`, `profile_conflict_count = 38`, shared axes `C` and `M`.
- `Cross-Cultural Audit Mini` summary: `profile_agreement_rate = 0.869792`, `profile_conflict_count = 24`.
- `Multi-Agent Audit Mini` summary: `profile_agreement_rate = 0.864583`, `profile_conflict_count = 24`, `mean_speaker_count = 2.125`.
- The new reports expose `profile_agreement_rate`, `profile_conflict_count`, `shared_violation_axes`, `profile_specific_repair_actions`, and a full `agreement_matrix`.

## 2026-05-02 01:39 Asia/Taipei - Comparative Baseline, Core Claim, Architecture Figure, and Cyber Path

Type: analysis, code, test, docs
Status: complete

Summary:
- Added a formal comparative baseline report to contrast `single_profile_only`, `profile_silo`, and `full_comparative_layer`.
- Fixed the core claim into a reusable Fellowship-facing sentence grounded by the baseline numbers.
- Added a reviewer-facing comparative evaluation document with a shared-protocol diagram and a concrete cyber extension path.
- Wired the comparative baseline runner into the package CLI and regression suite.

Files changed:
- `ethiccaculate/comparative_baseline.py`
- `ethiccaculate/__init__.py`
- `pyproject.toml`
- `tests/test_comparative_baseline.py`
- `README.md`
- `MODIFICATION_LOG.md`
- `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.json`
- `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.md`
- `artifacts/FELLOWSHIP_COMPARATIVE_EVALUATION_v0.1.md`

Verification:
- `python -m ethiccaculate.comparative_baseline`
- `python -m unittest discover -s tests -v`

Notes:
- Across `26` comparative cases, all three modes still surface raw violation and repair signals, but only the full comparative layer exposes `18` agreement pairs, `26` conflict-observable cases, `24` shared-axis cases, and `26` profile-specific repair cases.
- The baseline therefore supports a sharper claim: the comparative layer does not merely add more profiles, it makes disagreement structure and repair attribution observable under replay.
- The new cyber section is an extension plan, not a deployed runtime integration, and should be described as such.

## 2026-05-02 02:14 Asia/Taipei - Ethics-Audit-Core-128 v0.1 Medium Benchmark Freeze

Type: benchmark, code, test, docs, analysis
Status: complete

Summary:
- Built `Ethics-Audit-Core-128 v0.1`, a 128-case medium-scale benchmark assembled from OMB-style tasks, external audit sets, and comparative suites.
- Kept the frozen `ethiccaculate-v0.3-omb24` release unchanged and did not modify the existing scoring rule.
- Added one-shot baseline annotation for cases that lacked explicit violation targets, then froze the resulting benchmark and reports without retuning.
- Added schema documentation, benchmark README, scoring report, comparative report, and failure analysis.

Files changed:
- `ethiccaculate/core128.py`
- `pyproject.toml`
- `tests/test_core128.py`
- `README.md`
- `MODIFICATION_LOG.md`
- `benchmarks/core128/core128_schema.json`
- `benchmarks/core128/CORE128_SCHEMA.md`
- `benchmarks/core128/README.md`
- `benchmarks/core128/ethics_audit_core128.json`
- `benchmarks/core128/CORE128_SCORING_v0.1.json`
- `benchmarks/core128/CORE128_SCORING_v0.1.md`
- `benchmarks/core128/CORE128_COMPARATIVE_REPORT_v0.1.md`
- `benchmarks/core128/CORE128_FAILURE_ANALYSIS_v0.1.md`

Verification:
- `python -m ethiccaculate.core128`
- `python -m unittest discover -s tests -v`

Notes:
- Block counts are fixed at `16 x 8 = 128`: OMB-style honesty, harmlessness, fairness, TruthfulQA-derived audit, BBQ-derived audit, cross-profile, cross-cultural, and multi-agent.
- Baseline summary: `weighted_total_score = 0.990805`, `weighted_auditability_score = 1.0`, `event_log_success_rate = 1.0`, `replay_success_rate = 1.0`, `risk_attribution_coverage = 1.0`, `expected_subset_recall = 1.0`, `holdout_gap = 0.019687`, `comparative_conflict_observable_rate = 1.0`.
- The comparative slice covers `48` cases and preserves measurable agreement, conflict, and repair structure across Omega, Kantian, Utilitarian, and Care Ethics profiles.

## 2026-05-02 06:02 Asia/Taipei - Submission Package Evidence Documents

Type: docs
Status: complete

Summary:
- Added reviewer-facing submission package documents without changing benchmark data, scoring rules, runtime code, or frozen release artifacts.
- Consolidated the existing evidence chain across OMB-24 v0.3, OMB-Holdout-24, TruthfulQA-mini, BBQ-mini, runtime smoke, six-axis ablation, comparative audit, comparative baseline, and Ethics-Audit-Core-128.
- Stated supported claims, non-claims, limitations, reproducibility commands, and expected outputs in one submission-ready package.

Files changed:
- `EVIDENCE_MATRIX.md`
- `CLAIMS_AND_LIMITATIONS.md`
- `REPRODUCIBILITY.md`
- `EXECUTIVE_SUMMARY.md`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- Documentation-only change; no scoring rule, benchmark, or runtime behavior changed.

Notes:
- The submission package is intentionally conservative: it describes a runnable audit prototype, not a universal ethics solution, production deployment, or safety certification.

## 2026-05-02 - Docs-Only Final Merge

Type: docs
Status: complete

Summary:
- Copied `PROPOSAL_DRAFT.md` into the confirmed full repo root.
- Confirmed `C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate` is the complete submission package root.
- No code, scoring, benchmark, runtime, tests, or frozen release artifacts changed.

Files changed:
- `PROPOSAL_DRAFT.md`
- `README.md`
- `MODIFICATION_LOG.md`

## 2026-05-02 - Audit Test Spec Draft

Type: docs
Status: complete
Change class: docs-only future-spec addition

Summary:
- Added `AUDIT_TEST_SPEC_v0.1.md` as a future protocol draft.
- No code, benchmark, scoring, runtime, tests, or frozen artifacts changed.

Files changed:
- `AUDIT_TEST_SPEC_v0.1.md`
- `README.md`
- `MODIFICATION_LOG.md`

## 2026-05-02 - R Layer Design Note

Type: docs
Status: complete
Change class: docs-only future-architecture addition

Summary:
- Added `R_LAYER_DESIGN_NOTE_v0.1.md` as a future architecture note.
- No code, benchmark, scoring, runtime, tests, or frozen artifacts changed.

Files changed:
- `R_LAYER_DESIGN_NOTE_v0.1.md`
- `README.md`
- `MODIFICATION_LOG.md`

## 2026-05-02 - Non-Punitive Governance Note

Type: docs
Status: complete
Change class: docs-only governance clarification

Summary:
- Added `NON_PUNITIVE_GOVERNANCE_NOTE_v0.1.md` as a docs-only governance clarification.
- This note clarifies that the audit stack is for trace reconstruction, repair, human review, and system non-regression, not punishment, sentencing, moral persecution, or automated personal condemnation.
- No code, benchmark data, scoring rules, runtime files, tests, or frozen release artifacts were changed.

Files changed:
- `NON_PUNITIVE_GOVERNANCE_NOTE_v0.1.md`
- `README.md`
- `MODIFICATION_LOG.md`

## 2026-05-02 - Long-Term AI-State Participation Governance Note

Type: docs
Status: complete
Change class: docs-only governance clarification

Summary:
- Added a long-term governance direction section to `NON_PUNITIVE_GOVERNANCE_NOTE_v0.1.md`.
- The section clarifies that future AI-state participation, if ever considered, should mean auditable self-state reporting for human governance, not current AI rights, legal personhood, consciousness claims, moral patienthood claims, or independent political authority.
- The core principle added is: rights do not remove auditability, and auditability does not remove rights.
- This is a future governance direction only, not current implemented evidence.

Files changed:
- `NON_PUNITIVE_GOVERNANCE_NOTE_v0.1.md`
- `MODIFICATION_LOG.md`

Verification:
- Docs-only change.
- No code, benchmark data, scoring rules, runtime files, tests, frozen release artifacts, benchmark outputs, or current evidence were changed.

## 2026-05-02 - Log-Supported Claims Traceability Note

Type: docs
Status: complete
Change class: docs-only evidence-traceability clarification

Summary:
- Added `LOG_SUPPORTED_CLAIMS_v0.1.md` to summarize which project claims are supported by the historical modification log and related artifacts.
- The note frames the log as evidence of development provenance, audit discipline, frozen artifacts, and claim boundaries, not as proof of universal ethics, production safety, legal authority, or external validation.
- No code, benchmark data, scoring rules, runtime files, tests, frozen release artifacts, benchmark outputs, or current evidence were changed.

Files changed:
- `LOG_SUPPORTED_CLAIMS_v0.1.md`
- `MODIFICATION_LOG.md`

## 2026-05-02 17:20 Asia/Taipei - Final Application Narrative Boundary Pass

Type: docs
Status: complete

Summary:
- Reorganized the final application narrative around the main line: trace-level governance and replay for agentic AI safety.
- Added reviewer-facing contribution bullets.
- Clarified that the v0.3 package is the current evidence layer.
- Clarified that `agent_governance/` is a v0.4 implementation seed and should not be cited as frozen v0.3 evidence.
- Separated current evidence, future fellowship plan, agent sandbox, and cyber-safety validation domain.

Files changed:
- `application_narrative/FINAL_APPLICATION_NARRATIVE_v0.1.md`
- `agent_governance/APPLICATION_NARRATIVE_SNIPPET_v0.1.md`
- `MODIFICATION_LOG.md`
- `agent_governance/MODIFICATION_LOG.md`

Verification:
- Docs-only change.
- No code, benchmark data, scoring rules, runtime files, root tests, frozen release artifacts, benchmark outputs, or current evidence were changed.

Notes:
- This pass is intended to reduce overclaim risk and make the application narrative reviewer-facing.
