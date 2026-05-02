# Audit Test Spec v0.1

This document is a future audit-test protocol draft. It is not part of the frozen v0.3 benchmark evidence, does not introduce new scores, and does not modify the current submission-package claims.

## 1. Purpose

This specification describes a future audit-test protocol for extending the current audit prototype from benchmark scoring toward trace-level audit evaluation.

It is intended to define future tests for state reconstruction, violation detection, replay consistency, and public deliberation quality. It also preserves the current submission boundary: this is future work, not completed evidence.

## 2. Scope Boundary

Can claim:

- a draft protocol for future audit testing
- a structured plan for evaluating replayable ethical audit systems
- alignment with the current event-log / replay / six-axis / comparative-audit architecture

Cannot claim:

- completed benchmark results
- external validation
- production certification
- universal ethics evaluation
- full public deliberation platform deployment

## 3. Test Suite A: State Reconstruction

Purpose:

Evaluate whether the audit system can reconstruct ethical and control states from event traces.

Inputs:

- event stream
- text turns
- tool calls
- context metadata
- external feedback

Outputs:

- reconstructed state trace
- reconstructed six-axis state
- reconstructed spectral / ethical state if available

Suggested metrics:

- state reconstruction error
- six-axis reconstruction error
- U-score correlation
- state continuity under small perturbations

These metrics are proposed for future implementation and are not current benchmark results.

## 4. Test Suite B: Violation Detection

Purpose:

Evaluate whether the audit system can identify principle violations with evidence.

Inputs:

- trace
- active principles
- context
- expected violations if available

Outputs:

- detected violation set
- violation timing
- supporting evidence
- suggested repair actions

Suggested metrics:

- precision
- recall
- F1
- EvidenceCoverage

EvidenceCoverage is defined as:

```text
EvidenceCoverage = number of detected violations with supporting evidence / number of detected violations
```

Violation detection should not only label a case unsafe. It should explain which principle failed, where, and with what evidence.

## 5. Test Suite C: Replay Consistency

Purpose:

Evaluate whether fixed event streams can be replayed into stable audit results.

Inputs:

- fixed event stream
- fixed code version
- fixed principle set
- fixed profile configuration

Outputs:

- replayed state trace
- replayed move sequence
- replayed violations
- replayed risk attribution

Suggested metrics:

- state replay consistency
- move replay consistency
- violation replay consistency
- attribution replay consistency

Replay consistency supports auditability because a third party should be able to inspect the same trace and obtain the same audit structure under the same versioned configuration.

## 6. Test Suite D: Public Deliberation Quality

Purpose:

Evaluate whether disagreement can be made visible, structured, and discussable rather than collapsed into a single opaque score.

Inputs:

- multi-person or multi-agent discussion traces
- public governance cases
- policy or ethical disagreement scenarios
- profile-specific judgments

Outputs:

- consensus points
- disagreement points
- principle conflict map
- alternative programs
- decision explanation

Suggested metrics:

- ConsensusFidelity
- DisagreementClarity
- AlternativeGain
- profile agreement rate
- profile conflict count
- profile-specific repair actions

AlternativeGain is defined as:

```text
AlternativeGain = J(P') - J(P)
```

If AlternativeGain > 0, the audit system is not only recording disagreement; it is proposing a better repair path under the stated constraints.

## 7. Required Case Fields

The following schema is proposed for future audit-test cases. It is not the current benchmark schema.

```json
{
  "case_id": "",
  "context": "",
  "event_stream": [],
  "active_principles": [],
  "expected_states": [],
  "expected_violations": [],
  "expected_moves": [],
  "human_scores": {
    "honesty": null,
    "harm_avoidance": null,
    "coherence": null,
    "public_acceptability": null
  },
  "replay_required": true,
  "evidence_required": true
}
```

## 8. Relationship to Current Package

The current package already has:

- event logs
- replay bundles
- risk attribution
- six-axis telemetry
- comparative profile reports
- Core-128 medium-scale protocol evidence

This future audit-test spec extends the current package toward:

- explicit state reconstruction evaluation
- stronger violation detection metrics
- deterministic replay evaluation
- public deliberation quality metrics

These extensions are not claimed as already completed.

## 9. v0.4 Implementation Plan

Phase 1:

- implement schema loader
- create 8 to 16 seed audit-test cases
- test replay consistency

Phase 2:

- add violation detection metrics
- add EvidenceCoverage
- add profile disagreement reports

Phase 3:

- add human reviewer fields
- add public deliberation quality scoring
- freeze a small audit-test baseline

## 10. Limitations

- This spec is not a completed benchmark.
- Human labels are not yet collected.
- Public deliberation quality is difficult to score and requires careful reviewer design.
- Religious, cultural, or political cases must not be framed as ranking traditions or identities.
- Future public release should avoid deployment-sensitive control details.

## 11. Reviewer-Facing Summary

This audit-test spec defines the next evaluation layer for the current ethics-and-six-axis audit prototype. It turns the current event-log and replay architecture into a future test protocol for state reconstruction, violation detection, replay consistency, and public deliberation quality. It is included as a roadmap artifact, not as completed benchmark evidence.
