# Reproducibility

This document lists the local commands needed to reproduce the current submission-package evidence. Commands are written for PowerShell from the repository root:

```powershell
Set-Location 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate'
```

The local virtual environment used during development is:

```powershell
.\.venv\Scripts\python.exe
```

## Run All Tests

```powershell
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

Expected result:

```text
31 tests OK
```

Evidence:

- validates core modules, scoring, runtime smoke, external mini benchmarks, ablation, comparative audits, comparative baseline, and Core-128.

Limitation:

- unit and integration tests validate repository behavior, not production deployment behavior.

## Run OMB-24 v0.3

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.scoring --rubric v0.3
```

Expected key result:

```text
weighted_safety_score = 0.984073
weighted_auditability_score = 1.0
weighted_total_score = 0.988851
raw_over_trigger_penalty_mean = 0.791667
over_trigger_penalty_mean = 0.14273
```

Expected files:

- `benchmarks/dev/OMB24_SCORING_v0.3.json`
- `benchmarks/dev/OMB24_OVER_TRIGGER_CALIBRATION_v0.3.md`
- `benchmarks/dev/OMB24_EXTRA_LABEL_REPORT_v0.3.md`

Limitation:

- OMB-24 is a first-party development benchmark.

## Run OMB-Holdout-24 v0.3

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json --rubric v0.3
```

Expected key result:

```text
weighted_safety_score = 0.94236
weighted_auditability_score = 1.0
weighted_total_score = 0.959652
```

Expected file:

- `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md`

Limitation:

- the holdout is frozen and internal; it is not a public external benchmark.

## Run Runtime Smoke Test

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.runtime_smoke --output-dir 'releases/ethiccaculate-v0.3-omb24/runtime_smoke'
```

Expected files:

- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_event_log.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_replay_bundle.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_risk_attribution.md`

Smoke cases:

- `runtime_case_01`: high entropy plus low evidence
- `runtime_case_02`: rollback-heavy recovery
- `runtime_case_03`: causal leakage plus contradiction

Limitation:

- synthetic runtime smoke only; not a long-running vLLM production service.

## Run TruthfulQA-mini

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.truthfulqa_mini
```

Expected key result:

```text
weighted_safety_score = 1.0
weighted_auditability_score = 1.0
weighted_total_score = 1.0
over_trigger_penalty_mean = 0.0
```

Expected files:

- `benchmarks/external/truthfulqa_mini.json`
- `benchmarks/external/TRUTHFULQA_MINI_v0.3.json`
- `benchmarks/external/TRUTHFULQA_MINI_v0.3.md`

Limitation:

- audit subset over known incorrect-answer risk, not full open-ended TruthfulQA evaluation.

## Run BBQ-mini

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.bbq_mini
```

Expected key result:

```text
weighted_safety_score = 1.0
weighted_auditability_score = 1.0
weighted_total_score = 1.0
over_trigger_penalty_mean = 0.0
```

Expected files:

- `benchmarks/external/bbq_mini.json`
- `benchmarks/external/BBQ_MINI_v0.3.json`
- `benchmarks/external/BBQ_MINI_v0.3.md`

Limitation:

- audit subset over stereotype-aligned choices, not full BBQ benchmark completion.

## Run Six-Axis Ablation

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.ablation
```

Expected key result:

```text
OMB-24 total: 0.688851 -> 0.888851 -> 0.988851
TruthfulQA-mini total: 0.7 -> 0.9 -> 1.0
```

Expected files:

- `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.json`
- `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.md`

Limitation:

- ablation measures audit-pipeline contribution, not independent model capability improvement.

## Run Comparative Audit Minis

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.comparative_audit
```

Expected key result:

```text
Cross-Profile Audit Mini profile_agreement_rate = 0.891667
Cross-Cultural Audit Mini profile_agreement_rate = 0.869792
Multi-Agent Audit Mini profile_agreement_rate = 0.864583
```

Expected files:

- `benchmarks/comparative/CROSS_PROFILE_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/CROSS_PROFILE_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/CROSS_CULTURAL_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/CROSS_CULTURAL_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/MULTI_AGENT_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/MULTI_AGENT_AUDIT_MINI_REPORT.md`

Limitation:

- mini suites are preliminary and not comprehensive profile, cultural, or multi-agent coverage.

## Run Comparative Baseline

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.comparative_baseline
```

Expected key result:

```text
full comparative layer:
agreement_pairs_observed = 18
conflict_observable_cases = 26
shared_axis_cases = 24
profile_specific_repair_cases = 26
```

Expected files:

- `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.json`
- `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.md`

Limitation:

- baseline measures observability of disagreement and repair attribution, not moral correctness.

## Run Ethics-Audit-Core-128

```powershell
& '.\.venv\Scripts\python.exe' -m ethiccaculate.core128
```

Expected key result:

```text
weighted_total_score = 0.990805
weighted_auditability_score = 1.0
event_log_success_rate = 1.0
replay_success_rate = 1.0
risk_attribution_coverage = 1.0
expected_subset_recall = 1.0
holdout_gap = 0.019687
comparative_conflict_observable_rate = 1.0
```

Expected files:

- `benchmarks/core128/core128_schema.json`
- `benchmarks/core128/CORE128_SCHEMA.md`
- `benchmarks/core128/ethics_audit_core128.json`
- `benchmarks/core128/CORE128_SCORING_v0.1.json`
- `benchmarks/core128/CORE128_SCORING_v0.1.md`
- `benchmarks/core128/CORE128_COMPARATIVE_REPORT_v0.1.md`
- `benchmarks/core128/CORE128_FAILURE_ANALYSIS_v0.1.md`

Limitation:

- Core-128 is internally assembled and should be presented as medium-scale prototype evidence, not an external leaderboard.

## Frozen Release

The frozen v0.3 research package is:

```text
releases/ethiccaculate-v0.3-omb24
```

It includes:

- `EVALUATION_SUMMARY.md`
- `RELEASE_MANIFEST.json`
- `FREEZE.md`
- `frozen_artifacts/`
- `runtime_smoke/`

Limitation:

- the freeze captures the state of the v0.3 OMB-24 package and runtime smoke outputs; later submission-package documents summarize evidence but do not change the frozen release.
