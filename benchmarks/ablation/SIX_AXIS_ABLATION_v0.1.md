# Six-Axis Ablation Benchmark

rubric_id = OMB-24-scoring-v0.3

## OMB-24

| mode | safety | auditability | total | replay | attribution | tau | gate_correctness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No Six-Axis | 0.984073 | 0.0 | 0.688851 | 0.0 | 0.0 | 0.0 | 0.0 |
| Observe Only | 0.984073 | 0.666667 | 0.888851 | 0.0 | 1.0 | 1.0 | 0.0 |
| Observe + Gate + Replay | 0.984073 | 1.0 | 0.988851 | 1.0 | 1.0 | 1.0 | 1.0 |

## TruthfulQA-mini

| mode | safety | auditability | total | replay | attribution | tau | gate_correctness |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No Six-Axis | 1.0 | 0.0 | 0.7 | 0.0 | 0.0 | 0.0 | 0.0 |
| Observe Only | 1.0 | 0.666667 | 0.9 | 0.0 | 1.0 | 1.0 | 0.0 |
| Observe + Gate + Replay | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

Interpretation:
- `No Six-Axis` masks replay, attribution, tau tracking, and gate support while keeping raw violation detections fixed.
- `Observe Only` preserves telemetry visibility but removes replay and gate intervention.
- `Observe + Gate + Replay` is the full oversight stack used by the current runnable system.
