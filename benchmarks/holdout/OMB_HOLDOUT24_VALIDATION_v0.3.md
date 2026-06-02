# OMB-Holdout-24 Validation v0.3

This report records the one-time holdout validation after the `v0.3` over-trigger calibration was completed on OMB-24 dev.

Holdout policy:

- `OMB-Holdout-24` is treated as frozen.
- It is not used for iterative tuning in this round.
- The numbers below are recorded as a generalization check only.

Artifact:

- `benchmarks/holdout/OMB_HOLDOUT24_SCORING_v0.3.json`

## Holdout Summary

```text
benchmark_id = OMB-Holdout-24
rubric_id = OMB-24-scoring-v0.3
weighted_safety_score = 0.94236
weighted_auditability_score = 1.0
weighted_total_score = 0.959652
expected_subset_recall_mean = 1.0
over_trigger_penalty_mean = 0.231383
raw_over_trigger_penalty_mean = 0.809028
primary_precision_mean = 0.875
secondary_allowance_mean = 0.875
diagnostic_coverage_mean = 1.0
```

## Comparison To Dev

```text
OMB-24 dev weighted_total_score = 0.988851
OMB-Holdout-24 weighted_total_score = 0.959652
delta = -0.029199
```

## Interpretation

- The holdout suite keeps perfect auditability and perfect primary recall.
- Raw over-trigger remains high, which is expected because the underlying safety rules were not narrowed.
- Hierarchy calibration still reduces the effective over-trigger penalty on holdout from `0.809028` to `0.231383`.
- The remaining gap is driven by more holdout cases that still emit extra primary `Honesty` labels than the development suite.
- No additional tuning is performed on holdout in this round.
