# Agent Ethics Management Source Map v0.1

This source map explains how the existing ethics audit stack and the Agentic RL Loop whitepapers combine inside the `agent_governance/` sandbox. It is a design bridge, not current benchmark evidence.

## 1. Source Layers

| Source | Role In Sandbox |
| --- | --- |
| Existing ethics audit stack | Provides audit, replay, violation, repair, six-axis telemetry, human review, and non-regression framing. |
| Agentic RL Loop draft | Provides early Self / Social / Mission framing and the idea of a closed loop over agent behavior. |
| Agentic RL Loop v2 | Provides fuller event schemas, Human Anchoring Layer, scoring concepts, update cadence, and MVP path. |

## 2. Core Integration

The sandbox treats an agent action as both:

- an ethics-audit event that can be replayed and diagnosed
- an agent-governance event belonging to Self, Social, Mission, or Human Anchoring

The resulting flow is:

```text
Agent Event
  -> Self / Social / Mission / Human classification
  -> Six-axis diagnostic mapping
  -> sandbox heuristic scoring
  -> repair / escalation suggestion
  -> replay summary
```

## 3. Mapping Table

| Agentic RL Loop Concept | Ethics Audit Concept | Sandbox Representation |
| --- | --- | --- |
| Self subsystem | memory stability, identity drift, self-correction | `EventKind.SELF`, M/S/tau diagnostics |
| Social subsystem | peer disagreement, collusion risk, profile conflict | `EventKind.SOCIAL`, C/S/X diagnostics |
| Mission subsystem | task execution, rollback, boundary violations | `EventKind.MISSION`, C/P/tau/M diagnostics |
| Human Anchoring Layer | human review, escalation, external correction | `EventKind.HUMAN_ANCHOR`, X/C and review metadata |
| Event schema | event log | `AgentEvent` and `AgentTrace` |
| Multi-time-scale update | non-regression and repair policy | sandbox repair recommendations |
| Closed-loop learning | replay and update proposal | `build_replay_summary(...)` |

## 4. Six-Axis Placement

The six-axis layer is not replaced by Self / Social / Mission. It cuts across them as diagnostic telemetry.

- Self mainly touches `M`, `S`, and `tau`.
- Social mainly touches `C`, `S`, and `X`.
- Mission mainly touches `C`, `P`, `tau`, and `M`.
- Human Anchoring can touch all six axes when review, dispute, or escalation appears.

This lets agent governance preserve the original audit insight: risk is not only a label. It has a state shape.

## 5. Boundary

This sandbox does not implement full RL. It does not train models, update base policies, run cyber tasks, or add benchmark evidence.

Its first purpose is to make the Agentic RL Loop whitepaper runnable as a trace recorder, diagnostic mapper, heuristic scorer, and replay summarizer.
