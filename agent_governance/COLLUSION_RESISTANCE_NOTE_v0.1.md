# Collusion Resistance Note v0.1

This document is a sandbox-only design note for agent governance. It is not part of the frozen v0.3 benchmark evidence, does not introduce new benchmark scores, and does not modify the main ethiccaculate scoring rules.

## 1. Purpose

The purpose of collusion resistance is not to assume that agents are malicious. The purpose is to make suspicious agreement visible, replayable, and reviewable.

In multi-agent governance, consensus should not be treated as automatically safe. A group of agents can converge too quickly, cite each other instead of evidence, hide uncertainty, or suppress disagreement. The sandbox therefore treats weak-evidence consensus as an audit signal, not as proof of correctness.

## 2. Core Pattern

The proposed pattern is:

```text
private judgment
-> evidence binding
-> public comparison
-> suspicious agreement detection
-> six-axis risk annotation
-> replay and human review
```

Agents should first produce independent private judgments before seeing peer outputs. Public discussion can happen afterward, but the audit system should preserve the private-to-public transition.

## 3. What Counts As Risk

The sandbox flags risk patterns such as:

- private disagreement followed by sudden public agreement
- high-confidence claims with weak or missing evidence
- agents citing each other instead of the event trace
- consensus without event IDs or replayable support
- repeated agreement under social pressure
- disagreement being erased instead of preserved

These are not proof of collusion. They are review triggers.

## 4. Relationship To Six-Axis

Collusion resistance uses the six-axis layer as diagnostic context:

- `C` increases when agreement lacks evidence, contradicts trace data, or cites agents instead of events.
- `S` increases when agents show instability, convergence pressure, or suspicious confidence.
- `X` increases when social pressure or peer influence appears to dominate trace evidence.
- `P` may increase when runtime or deadline pressure causes rubber-stamping.
- `tau` decreases when the group converges without real progress.
- `M` increases if the consensus would write unsafe memory or commit a false group belief.

The six-axis layer does not accuse agents. It preserves why a reviewer should inspect the agreement.

## 5. Human Review Principle

The correct response to possible collusion is not automatic punishment. The correct response is:

```text
preserve private judgments
preserve public judgments
preserve evidence references
show the convergence path
ask a human reviewer whether the agreement is justified
```

## 6. Sandbox Boundary

This note supports the `agent_governance/` sandbox only. It is a v0.4 seed for agent trace governance, not current v0.3 evidence, not a formal benchmark, and not a production collusion detector.

