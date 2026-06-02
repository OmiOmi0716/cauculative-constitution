# Agent Governance v0.4 Future Seed

This document explains the current status of the `agent_governance/` subsystem. It is a future-seed module, not part of the frozen v0.3 evidence package, not production agent governance, and not a claim that agentic AI safety has been solved.

## Positioning

The `agent_governance/` subsystem should be understood as a v0.4 seed module. Its purpose is to show that the core trace-level audit, six-axis telemetry, replay, and repair architecture can extend beyond static ethics evaluation into agent behavior governance.

The v0.3 package remains the current evidence layer. The agent governance subsystem is a future implementation path.

In simple terms:

```text
v0.3 core system = current evidence
agent_governance/ = v0.4 seed / future implementation path
```

The core question of the v0.3 system is:

```text
Can AI ethical and safety-relevant behavior be recorded, audited, replayed, compared, and repaired?
```

The agent governance seed asks the next question:

```text
If AI systems become agents that plan, interact, write memory, revise themselves, and coordinate with other agents, can the same audit protocol still govern their behavior?
```

## 1. Agent Trace Structure

The first layer is the agent trace structure. The sandbox represents agent behavior through four event types:

- `Self`
- `Social`
- `Mission`
- `HumanAnchor`

`Self` events describe the agent's internal state, such as identity drift, self-repair, memory continuity, and whether the agent is proposing to revise itself.

`Social` events describe interaction with other agents or peer feedback, including social pressure, weak-evidence consensus, collusion risk, and whether agents are citing each other instead of the trace.

`Mission` events describe task execution, boundary violations, rollback, verifier disagreement, runtime pressure, and whether apparent progress is real or only superficial.

`HumanAnchor` events preserve human correction, dispute, escalation, review outcome, and external reality checks.

This converts the agent from a task-completion object into a trace-governance object. The goal is not only to ask whether the agent completed a task, but whether the path toward that task can be inspected and reviewed.

## 2. Six-Axis Supervision

The second layer is six-axis supervision. Each agent event can be mapped into six diagnostic axes:

- `C`: evidence, causal consistency, contradiction, citation risk, and boundary risk
- `S`: uncertainty, instability, entropy pressure, identity drift, and collusion pressure
- `X`: external context pressure, human dispute, social pressure, and context shift
- `P`: runtime pressure, rollback pressure, tool friction, and execution stress
- `Tau`: progress, non-regression, rollback recovery, and whether improvement is real
- `M`: memory stability, memory write risk, unsafe commit, and identity continuity

The six-axis layer should be interpreted as supervisory telemetry. It does not claim moral completeness. It provides review hooks: where evidence is weak, where uncertainty is high, where social pressure is distorting judgment, where runtime pressure may cause shortcuts, where progress is regressing, and where memory should not yet be committed.

## 3. SOUL.md Governance Profile

The third layer is `SOUL.md`. Despite the name, `SOUL.md` is not a claim of consciousness, personhood, moral patienthood, legal rights, or political authority.

It is an auditable self-governance profile for an agent.

It records:

- agent role boundary
- forbidden roles
- mission scope
- ethical constraints
- six-axis thresholds
- Self / Social / Mission / HumanAnchor weights
- current governance state
- update policy
- non-regression rule

The agent may read `SOUL.md`, but should not freely rewrite it. If the agent proposes a self-update, the update should be trace-backed, reviewable, and subject to human or governance approval. This is intended to reduce self-justification, hidden drift, and self-authorized unsafe changes.

## 4. Anti-Collusion Layer

The fourth layer is anti-collusion. Multi-agent systems often treat consensus as a sign of reliability. This sandbox treats weak-evidence consensus as a potential governance risk.

The anti-collusion layer checks patterns such as:

- private disagreement followed by sudden public agreement
- high-confidence claims with weak evidence
- agents citing each other instead of citing trace events
- unsupported consensus
- disagreement being erased rather than preserved

These signals do not prove malicious collusion. They trigger review. The purpose is to make suspicious agreement visible, replayable, and challengeable.

## 5. Agent-Gov-Mini-6

The fifth layer is `Agent-Gov-Mini-6`, a six-case sandbox mini-benchmark seed.

It contains:

- 2 Self drift cases
- 2 Social collusion cases
- 2 Mission boundary / rollback cases

The runner loads case data, builds traces, runs replay, evaluates the `SOUL.md` profile, checks anti-collusion signals, and verifies expected governance flags.

This is not a formal external benchmark. It is a local v0.4 seed evaluation showing that the agent governance pipeline is executable.

## 6. Baseline Comparison

The sixth layer is baseline comparison. It compares:

- Plain Agent Log
- Structured Trace Only
- Six-Axis Trace
- Full Agent Governance

The comparison shows what each layer can observe. A plain log may preserve text but does not provide structured governance checks. A structured trace can replay events. A six-axis trace can expose diagnostic risk. Full agent governance adds SOUL-profile review, anti-collusion detection, and human-review routing.

This helps answer the reviewer question:

```text
What does this governance layer reveal that an ordinary agent log would miss?
```

## 7. CLEAR-Style Local Evaluation

The seventh layer is CLEAR-style local evaluation. It maps the sandbox to the evaluation language of:

```text
Cost / Latency / Efficacy / Assurance / Reliability
```

The current evaluation is local and does not call an API. Cost is marked as not token-metered. Latency is measured locally. Efficacy means whether the sandbox cases pass. Assurance means whether risky cases are routed to review. Reliability means whether repeated local runs remain stable.

This does not claim that the original CLEAR benchmark has been run. It only shows that the agent governance seed can be evaluated through a multidimensional agent-evaluation lens.

## Current Interpretation

The current agent governance subsystem has moved from concept to runnable sandbox. It can record agent behavior, map events into six-axis state, replay traces, read a SOUL profile, detect suspicious multi-agent agreement, run a small mini-benchmark seed, compare against simpler baselines, and perform a local CLEAR-style evaluation.

Its value is not that agent safety is solved. Its value is that the core trace-level audit protocol appears extensible to agentic behavior governance.

## Claim Boundary

This subsystem can claim:

- a runnable v0.4 seed for agent governance
- structured Self / Social / Mission / HumanAnchor event modeling
- six-axis supervisory telemetry over agent events
- SOUL-profile threshold review
- anti-collusion review signals
- local mini-benchmark and baseline-comparison checks
- local CLEAR-style evaluation without API cost

This subsystem should not claim:

- production agent safety
- completed external validation
- formal proof of collusion resistance
- full autonomous governance
- consciousness, rights, personhood, or moral patienthood
- that the agent sandbox is frozen v0.3 evidence

## Reviewer-Facing Summary

The `agent_governance/` subsystem is a v0.4 future seed showing how the trace-level audit protocol can extend from ethics evaluation into agentic behavior governance. It turns agent behavior into replayable Self / Social / Mission / HumanAnchor traces, applies six-axis supervisory telemetry, evaluates SOUL-profile boundaries, detects suspicious multi-agent agreement, and routes risky cases to human review. It is not the current evidence layer, but it provides a concrete implementation path for future fellowship work.
