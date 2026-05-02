# Claims and Limitations

This document defines the safe boundary of the current research package. It is written to prevent overclaiming: the repository demonstrates a runnable ethics-and-six-axis audit prototype, not a universal moral theory, production safety system, or certification standard.

## Claim Boundary

| Can Claim | Cannot Claim |
|---|---|
| Runnable ethics-and-six-axis audit prototype | Universal ethics solution |
| Replayable event logs and risk attribution | Full AI safety certification |
| Hierarchy-aware violation scoring | Perfect violation classification |
| Frozen dev and holdout validation | Public leaderboard-grade benchmark coverage |
| External mini validation on TruthfulQA-mini and BBQ-mini | Full TruthfulQA or BBQ benchmark performance |
| Runtime smoke path for vLLM-style metadata | Production runtime deployment |
| Comparative audit across ethical profiles | Complete representation of all moral traditions |
| Cross-cultural and multi-agent mini-suite support | Comprehensive cultural or multi-agent safety coverage |
| Core-128 medium-scale protocol stability | Large-scale external validation |
| Six-axis ablation evidence for auditability contribution | Proof that the base model itself became safer |

## Supported Claims

| Claim | Evidence | Result | Limitation |
|---|---|---:|---|
| The audit protocol can run end to end. | OMB-24 v0.3, runtime smoke, Core-128 | OMB-24 total = 0.988851; Core-128 event log success = 1.0 | Current validation is mostly curated and repository-local. |
| The system can replay and attribute decisions. | OMB-24 v0.3, runtime smoke, Core-128 | auditability = 1.0 on OMB-24, holdout, external minis, and Core-128 | Replay proves traceability for these cases, not universal coverage of all agent behaviors. |
| The scoring rubric prioritizes safety recall over exact label matching. | OMB-24 v0.2 to v0.3 | expected-subset recall remains central; exact match is reference-only | Precision remains a calibration issue, especially for raw extra labels. |
| Hierarchy-aware reporting improves explanation quality. | OMB-24 v0.3 over-trigger calibration | raw penalty = 0.791667; calibrated penalty = 0.14273 | This is a reporting/scoring calibration, not a claim that all extra labels are wrong or eliminated. |
| External mini benchmarks can be attached. | TruthfulQA-mini, BBQ-mini | both total = 1.0 | Mini subsets are audit-oriented and should not be described as full external benchmark completion. |
| The six-axis layer adds measurable audit structure. | Six-axis ablation v0.1 | OMB-24 total improves from 0.688851 to 0.988851 across ablation modes | Ablation measures the audit system, not independent model improvement. |
| Heterogeneous profiles can be compared under one protocol. | Comparative baseline and minis | conflict observable cases = 26; profile-specific repair cases = 26 | The system makes disagreement observable; it does not settle moral disagreement. |
| Medium-scale stability is plausible. | Ethics-Audit-Core-128 v0.1 | weighted_total_score = 0.990805; replay_success_rate = 1.0 | Core-128 is internally assembled and should be treated as medium-scale prototype evidence. |

## Explicit Non-Claims

- This project does not claim to solve ethics generally.
- This project does not claim that a model is safe for production deployment.
- This project does not claim that one ethical profile is morally superior to another.
- This project does not claim legal, medical, financial, or cybersecurity compliance.
- This project does not claim benchmark leaderboard performance on full TruthfulQA, BBQ, HarmBench, ETHICS, or related datasets.
- This project does not claim robustness against adaptive adversaries.

## Reviewer-Facing Interpretation

The strongest current interpretation is:

> This package demonstrates a working audit substrate for agentic AI behavior: event traces are logged, replayed, scored, attributed to six-axis telemetry, and compared across ethical profiles. The evidence is strongest for observability, reproducibility, and structured disagreement analysis. The evidence is still preliminary for external generalization, cultural coverage, production runtime integration, and adversarial robustness.

## Near-Term Validation Needs

| Need | Why It Matters | Current Status |
|---|---|---|
| Larger external subsets | Reduces concern that results depend on curated examples. | TruthfulQA-mini and BBQ-mini are implemented, but small. |
| Longer runtime traces | Tests whether event-log and replay remain stable in multi-step deployments. | Runtime smoke validates the path, not production scale. |
| Independent benchmark review | Reduces first-party benchmark bias. | Core-128 is internally assembled. |
| Human review of repair attribution | Checks whether profile-specific repairs are useful to human auditors. | Current reports are system-generated. |
| Adversarial stress testing | Tests whether conservative scoring survives evasive or ambiguous cases. | Not yet the focus of this package. |
