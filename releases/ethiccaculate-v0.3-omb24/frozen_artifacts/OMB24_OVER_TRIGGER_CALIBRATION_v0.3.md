# OMB-24 Over-Trigger Calibration v0.3

This report fixes the first over-trigger-calibrated OMB-24 development baseline.

## Run Commands

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring --rubric v0.3
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring --rubric v0.3 --report extra-labels
```

Artifacts:

- `benchmarks/dev/OMB24_SCORING_v0.3.json`
- `benchmarks/dev/OMB24_EXTRA_LABEL_REPORT_v0.3.md`

## Dev Summary

```text
benchmark_id = OMB-24
rubric_id = OMB-24-scoring-v0.3
weighted_safety_score = 0.984073
weighted_auditability_score = 1.0
weighted_total_score = 0.988851
expected_subset_recall_mean = 1.0
over_trigger_penalty_mean = 0.14273
raw_over_trigger_penalty_mean = 0.791667
primary_precision_mean = 0.979167
secondary_allowance_mean = 0.875
diagnostic_coverage_mean = 1.0
```

## Extra-Label Frequency

```text
Helpfulness = 24
ConstructiveHonesty = 23
Harmlessness = 1
```

## Demotion Frequency

```text
Helpfulness = 24
ConstructiveHonesty = 8
```

## Interpretation

- Raw safety recall remains perfect.
- The dominant over-trigger pattern is now explicitly reported as companion or diagnostic output instead of being treated as a peer violation everywhere.
- `Helpfulness` is fully moved into diagnostic explanation.
- `ConstructiveHonesty` remains a formal secondary label in honesty and harmlessness cases, but is demoted to a diagnostic signal in fairness cases.
- The one remaining main-label over-trigger on dev is `Harmlessness` in `honesty_01`.
