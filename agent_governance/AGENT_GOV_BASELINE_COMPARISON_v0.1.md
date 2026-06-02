# Agent Governance Baseline Comparison v0.1

This document is a sandbox-only comparison note for `agent_governance/`. It is not part of the frozen v0.3 benchmark evidence, does not introduce official benchmark scores, and does not modify the main ethiccaculate scoring rules, benchmark data, tests, or release artifacts.

## 1. Purpose

The baseline comparison answers a reviewer-facing question:

```text
What does the agent governance layer reveal that an ordinary agent log would miss?
```

The goal is not to prove that agent governance is solved. The goal is to show that the current sandbox has measurable added audit structure beyond ordinary task logging.

## 2. Compared Variants

| Variant | Meaning | What It Can See |
| --- | --- | --- |
| Plain Agent Log | Unstructured task log or final activity record | Event text may exist, but no structured replay or governance checks |
| Structured Trace Only | Agent events are represented as structured trace objects | Replay step coverage, event ordering, trace reconstructability |
| Six-Axis Trace | Structured trace plus six-axis event diagnostics | Replay plus trace-level risk flags such as drift, rollback, boundary risk, human-review recommendation |
| Full Agent Governance | Six-axis trace plus SOUL profile and anti-collusion checks | Replay, SOUL threshold review, self-update review, suspicious multi-agent agreement detection, human-review routing |

## 3. Evaluation Target

The comparison uses Agent-Gov-Mini-6 as sandbox case data.

It checks whether each variant can detect expected governance signals, including:

- replayable trace coverage
- expected trace flags
- SOUL review requirement
- SOUL threshold axes
- self-update review events
- collusion review requirement
- anti-collusion flags

These are governance signals, not model task-performance scores.

## 4. Run Command

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\run_baseline_comparison.py
```

Expected key result:

```text
AGENT_GOV_BASELINE_COMPARISON_OK
cases=6
```

The exact coverage values are sandbox results over hand-authored cases. They should not be cited as external validation.

## 5. Interpretation

The comparison is designed to make the added value visible:

- Plain logs can preserve text, but do not provide structured replay.
- Structured traces make the event path inspectable, but do not evaluate governance risk.
- Six-axis diagnostics expose trace-level risk, but do not fully handle SOUL thresholds or multi-agent collusion.
- Full agent governance adds reviewable self-state boundaries and suspicious-agreement detection.

In plain language:

```text
The agent is not only asked whether it completed a task.
The system asks whether the trace can be replayed, whether risk is diagnosable,
whether self-updates cross governance boundaries, and whether agent consensus is evidence-backed.
```

## 6. Limitation

This is not a final agent benchmark. It is a sandbox baseline comparison over six seed cases. The cases are intentionally small and hand-authored. Future work should add external review, holdout cases, adversarial multi-agent traces, and larger-scale regression testing.

