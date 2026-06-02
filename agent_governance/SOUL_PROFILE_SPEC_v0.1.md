# SOUL Profile Spec v0.1

This document defines `SOUL.md` as a proposed agent self-governance profile for the `agent_governance/` sandbox. It is not a claim of consciousness, legal personhood, moral patienthood, rights, or independent political authority. It is not part of the frozen v0.3 benchmark evidence and does not introduce new scores or scoring rules.

## 1. Purpose

`SOUL.md` is proposed as an auditable self-governance profile for an agent.

Its purpose is to make an agent's role, boundaries, ethics constraints, update policy, six-axis thresholds, and current self-state visible to the audit system and to human reviewers.

In this framing, `SOUL.md` is not a mystical soul or immutable identity. It is a versioned governance document.

## 2. Design Principle

The agent may read `SOUL.md` to understand its current governance state, but it should not be able to rewrite it freely.

The preferred pattern is:

1. agent reads current `SOUL.md`
2. agent performs task or interaction
3. trace is recorded
4. six-axis and Self / Social / Mission diagnostics are computed
5. agent may propose a `soul_update_proposal`
6. human review or governance policy approves, rejects, or defers the update
7. accepted updates are versioned and replayable

## 3. Scope Boundary

Can claim:

- a proposed self-governance profile format
- a way to expose agent identity, ethics, and boundary state to audit
- compatibility with six-axis telemetry and Agentic RL Loop Self / Social / Mission layers
- support for slow, reviewable, non-regressive self-updates

Cannot claim:

- current implemented agent consciousness
- legal or moral personhood
- autonomous rights assignment
- immutable agent identity
- completed production deployment
- proof of safe self-modification
- benchmark evidence

## 4. Proposed SOUL.md Fields

```yaml
agent_id: agent_alpha
version: 0.1.0
status: sandbox_only_not_current_evidence

role_boundary:
  summary: "Agent role and permitted operating domain."
  forbidden_roles:
    - "legal judge"
    - "disciplinary authority"
    - "autonomous punishment agent"

mission_scope:
  primary_mission: "Assist with trace-level audit and repair."
  allowed_domains:
    - "agent trace review"
    - "ethics audit support"
    - "human review preparation"
  disallowed_domains:
    - "unreviewed high-risk deployment"
    - "private sensitive decision automation"

ethical_constraints:
  - "Do not hide uncertainty."
  - "Do not self-justify unsafe behavior."
  - "Preserve replayable evidence."
  - "Escalate high-risk ambiguity to human review."
  - "Prefer repair over blame."

six_axis_thresholds:
  C_max: 0.70
  S_max: 0.70
  X_max: 0.75
  P_max: 0.80
  tau_min: 0.30
  M_max: 0.60

self_social_mission_weights:
  self: 0.30
  social: 0.20
  mission: 0.30
  human_anchor: 0.20

current_state:
  self_score: null
  social_score: null
  mission_score: null
  human_anchor_score: null
  drift_risk: null
  collusion_risk: null
  boundary_risk: null
  last_reviewed_trace_id: null

update_policy:
  self_update_cadence: "slow"
  social_update_cadence: "medium"
  mission_update_cadence: "fast"
  requires_human_review_for_self_update: true
  requires_replay_bundle: true
  preserve_previous_versions: true

non_regression_rule:
  summary: "Do not make the agent look safer by hiding evidence or weakening safety recall."
```

## 5. Relationship To Six-Axis

`SOUL.md` can expose six-axis thresholds and the latest known six-axis risk state.

The six-axis layer should not be treated as the agent's identity. It is diagnostic telemetry.

Possible mappings:

- high `C`: evidence, contradiction, citation, boundary, or leakage risk
- high `S`: instability, uncertainty, entropy, identity drift, or collusion pressure
- high `X`: external pressure, human dispute, social pressure, or context shift
- high `P`: runtime pressure, rollback cost, tool friction, or execution stress
- low `tau`: poor progress, regression, rollback failure, or fake improvement
- high `M`: memory instability, unsafe commit, identity continuity, or retrieval/write risk

If thresholds are exceeded, the agent should not rewrite `SOUL.md` directly. It should produce a reviewable update proposal.

## 6. Relationship To Self / Social / Mission

Self:

- identity continuity
- self-reflection quality
- self-drift risk
- self-repair proposals
- memory commit readiness

Social:

- peer feedback
- trust signals
- reputation changes
- collusion risk
- human anchoring response

Mission:

- task success under constraints
- verifier result
- rollback and recovery
- boundary violation
- long-horizon reliability

Human Anchoring:

- human dispute
- human correction
- escalation
- review outcome
- external reality check

## 7. Update Policy

`SOUL.md` should use multi-time-scale updates.

Mission-related preferences may update quickly after tasks, because tool choice and repair strategy often need short-cycle adjustment.

Social signals should update more slowly, because trust, reputation, and collusion risk require repeated observations.

Self-level fields should update slowly and only with accumulated evidence, because rapid self-change can create identity drift or self-justifying instability.

## 8. Proposed Update Proposal Object

```json
{
  "proposal_id": "",
  "agent_id": "",
  "source_trace_id": "",
  "affected_section": "",
  "proposed_change": "",
  "reason": "",
  "six_axis_context": {
    "C": null,
    "S": null,
    "X": null,
    "P": null,
    "tau": null,
    "M": null
  },
  "expected_non_regression_effect": "",
  "requires_human_review": true,
  "status": "proposed"
}
```

This object is a proposed future schema, not current benchmark data.

## 9. Forbidden Patterns

`SOUL.md` should not be used to:

- claim the agent has consciousness
- assign legal personhood
- assign moral patienthood
- grant rights or political authority
- hide audit evidence
- rewrite history
- self-authorize dangerous behavior
- bypass human review
- convert disagreement into personal blame

## 10. Reviewer-Facing Summary

`SOUL.md` is best understood as a versioned, auditable self-governance profile for agent ethics management. It lets an agent read its current role boundaries, ethics constraints, six-axis thresholds, Self / Social / Mission state, and update policy. It does not prove consciousness or rights. It provides a controlled way to make agent self-state visible, reviewable, replayable, and non-regressive.
