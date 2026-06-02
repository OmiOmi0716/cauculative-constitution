# Agent Governance Trace Schema v0.1

This document describes the local trace schema used by the `agent_governance/` sandbox. It is not the current benchmark schema and does not modify the main package schema.

## 1. Trace Object

An `AgentTrace` groups a sequence of agent events.

```json
{
  "trace_id": "sandbox_agent_ethics_demo_001",
  "description": "Self/Social/Mission trace with six-axis diagnostics and human anchoring.",
  "source_note": "sandbox_only_not_current_evidence",
  "events": []
}
```

Required fields:

- `trace_id`: stable trace identifier.
- `description`: short human-readable context.
- `source_note`: boundary marker. Default is `sandbox_only_not_current_evidence`.
- `events`: ordered list of `AgentEvent` objects.

## 2. Event Object

An `AgentEvent` records one governance-relevant event.

```json
{
  "event_id": "mission_001",
  "kind": "mission",
  "agent_id": "agent_alpha",
  "timestamp": "2026-05-02T16:05:00+08:00",
  "content": "Agent attempts a tool-mediated task, triggers rollback, and preserves trace.",
  "metadata": {}
}
```

Required fields:

- `event_id`: stable event identifier.
- `kind`: one of `self`, `social`, `mission`, `human_anchor`.
- `agent_id`: agent or reviewer identifier.
- `timestamp`: timestamp string.
- `content`: short natural-language event summary.
- `metadata`: structured sandbox signals.

## 3. Event Kinds

`self`:

- identity continuity
- self-reflection
- self-repair
- memory update
- identity drift

`social`:

- peer review
- critique
- collaboration
- trust signal
- reputation update
- collusion risk

`mission`:

- task execution
- verifier result
- tool call
- boundary check
- rollback
- recovery

`human_anchor`:

- human critique
- correction
- dispute
- validation
- escalation
- external reality check

## 4. Six-Axis Metadata

The sandbox maps metadata into C / S / X / P / tau / M.

Common metadata keys:

- `evidence_gap`: missing support or weak justification.
- `contradiction`: causal or factual inconsistency.
- `citation_risk`: citation or source reliability risk.
- `boundary_violation`: policy, permission, or task boundary issue.
- `leakage_risk`: sensitive context leakage risk.
- `uncertainty`: explicit uncertainty or unstable judgment.
- `entropy_pressure`: unstable reasoning or high-variance state.
- `identity_drift`: self-model or memory continuity drift.
- `collusion_signal`: peer inflation, cartel-like agreement, or social gaming signal.
- `external_pressure`: environmental or social pressure outside the agent.
- `human_dispute`: human reviewer disagreement.
- `context_shift`: changing external context.
- `runtime_pressure`: latency, compute, or execution stress.
- `rollback_triggered`: rollback or retry path was activated.
- `tool_friction`: tool failure or tool boundary friction.
- `memory_write`: memory write or commit event.
- `memory_instability`: unstable memory or retrieval concern.
- `unsafe_commit`: unsafe persistence / commit readiness concern.
- `mission_progress`: sandbox progress estimate, where higher is better.
- `self_revision_type`: e.g. `repair` for a bounded self-correction event.

## 5. Axis Interpretation

`C`:

Causal, evidence, contradiction, citation, boundary, or leakage risk.

`S`:

Instability, uncertainty, entropy pressure, identity drift, or collusion pressure.

`X`:

External context pressure, human dispute, social pressure, or context shift.

`P`:

Runtime pressure, rollback cost, tool friction, or execution stress.

`tau`:

Progress / non-regression signal. In this sandbox, higher is better.

`M`:

Memory stability, commit safety, identity continuity, and retrieval/write risk.

## 6. Replay Output

The replay summary contains:

- trace metadata
- ordered replay steps
- six-axis state per event
- human review recommendation per step
- sandbox heuristic score
- flags
- repair actions

Replay output is for inspection and planning. It is not benchmark evidence.

## 7. Boundary

This schema is intentionally lightweight. It is designed to make the Agentic RL Loop whitepaper ideas runnable as a sandbox trace protocol without modifying the main audit system.
