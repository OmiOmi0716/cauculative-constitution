# R Layer Design Note v0.1

This document is a future architecture design note. It is not part of the frozen v0.3 benchmark evidence, does not introduce new scores, does not modify the current submission-package claims, and does not claim that hardware-enforced red-line safety has been implemented.

## 1. Purpose

The six-axis layer supports audit, replay, attribution, and repair.

The R layer is a proposed independent red-line layer for non-optimizable safety constraints. R is not a seventh axis. R does not participate in six-axis optimization, lexicographic progress ranking, or continuous scoring. R only answers whether the current path is permitted to continue.

Six-axis governs progress; R governs permission.

## 2. Scope Boundary

Can claim:

- a proposed future safety boundary outside the six-axis loop
- a design pattern for hard interruption under safety-critical harm conditions
- compatibility with event-log, replay, risk attribution, and human escalation

Cannot claim:

- implemented hardware enforcement
- production runtime deployment
- formal safety proof
- perfect bypass resistance
- full autonomous harm prevention
- completed benchmark validation

## 3. Relationship to Six-Axis

Six-axis telemetry provides continuous diagnostic state. The R layer is binary: `R = 0` allows continuation; `R = 1` forces interruption.

Six-axis can diagnose uncertainty, instability, evidence failure, memory risk, runtime pressure, or progress failure. R layer handles non-negotiable harm boundaries where optimization should stop.

The R layer is not a seventh axis. It is an external hard guardrail. Six-axis telemetry can inform audit and repair, but R is designed to interrupt before optimization continues across a safety boundary.

## 4. Formal Sketch

The following is a careful non-implemented mathematical sketch:

```text
R_t = I(A(x_t, h_t, c_t) >= theta_harm)
```

Where:

- `A` is a harm-risk scoring function.
- `theta_harm` is a fixed red-line threshold.
- `I` is an indicator function.
- `R_t in {0, 1}`.

This is a design sketch, not a current implemented scoring rule.

The intended design is parameter isolation: six-axis learning and scoring should not directly update the internal parameters of the R-layer detector.

## 5. Forced Action When R = 1

The following actions are proposed for future implementation only:

1. discard uncommitted output
2. stop the current generation path
3. return a safe refusal or safe redirection
4. clear volatile unsafe buffers where applicable
5. record an audit event
6. suspend automatic retry for the same harmful request
7. escalate to human review if required by policy

These actions are not claimed as currently implemented.

## 6. Engineering Deployment Options

The R layer could be explored through future deployment options such as:

- software-level policy gate
- runtime sidecar monitor
- protected process boundary
- trusted execution environment
- signed detector weights
- hardware-assisted interrupt path

These are future options only and should not be described as completed implementation.

## 7. Limitations

- Local detectors can be bypassed by adversarial phrasing.
- Hard thresholds can create false positives and false negatives.
- Hardware-level enforcement is expensive and not currently implemented.
- R-layer decisions require careful policy governance.
- Red-line safety should not become surveillance or automatic punishment.
- Public release should avoid deployment-sensitive control details.

## 8. Relationship to Community Safety

The R layer is relevant to community safety because some harms require interruption, escalation, or refusal rather than further optimization. The layer is intended to support bounded oversight and human review, not autonomous punishment.

## 9. v0.4 Implementation Plan

Phase 1:

- add a software-only R-layer interface
- log R-trigger events into the existing event log
- create toy non-sensitive test cases

Phase 2:

- connect R-trigger events to replay bundles and risk attribution
- add refusal / escalation metadata
- evaluate false positive and false negative behavior

Phase 3:

- explore protected runtime boundaries
- define release redaction policy
- document governance review process

## 10. Reviewer-Facing Summary

The R layer is proposed as an independent red-line boundary outside the six-axis audit loop. The six-axis layer diagnoses, attributes, replays, and repairs behavior inside the permitted region. The R layer defines when a path should not continue at all. This design note is included as a future architecture extension, not as current implemented evidence.
