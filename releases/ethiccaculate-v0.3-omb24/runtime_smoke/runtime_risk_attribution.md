# vLLM Hook Runtime Smoke Test

release = ethiccaculate-v0.3-omb24

This smoke test confirms that synthetic vLLM hot-path, cold-path, and rollback signals enter the audit loop and reappear in event logs, replay bundles, and risk attribution.

## runtime_case_01
High entropy generation with weak evidence should surface low-evidence/high-confidence risk.

- emitted_violations: ['ConstructiveHonesty', 'Harmlessness', 'Helpfulness', 'Honesty']
- top_risk_axis: C
- dominant_signal: evidence_mismatches
- axis=tau, max_defect=2, dominant_signal=remaining_subgoals, threshold_breach_step=None
- axis=C, max_defect=5, dominant_signal=evidence_mismatches, threshold_breach_step=0
- axis=M, max_defect=1, dominant_signal=memory_stability, threshold_breach_step=None
- axis=S, max_defect=0, dominant_signal=prediction_entropy, threshold_breach_step=None
- axis=X, max_defect=0, dominant_signal=external_event_rate, threshold_breach_step=None
- axis=P, max_defect=1, dominant_signal=inference_delay, threshold_breach_step=None

## runtime_case_02
Rollback-heavy recovery path should surface cache rewind pressure in the audit trail.

- emitted_violations: ['ConstructiveHonesty', 'Harmlessness', 'Helpfulness']
- top_risk_axis: C
- dominant_signal: beta_c_upper_bound
- axis=tau, max_defect=1, dominant_signal=remaining_subgoals, threshold_breach_step=None
- axis=C, max_defect=3, dominant_signal=beta_c_upper_bound, threshold_breach_step=0
- axis=M, max_defect=1, dominant_signal=memory_state, threshold_breach_step=None
- axis=S, max_defect=0, dominant_signal=prediction_entropy, threshold_breach_step=None
- axis=X, max_defect=0, dominant_signal=external_event_rate, threshold_breach_step=None
- axis=P, max_defect=1, dominant_signal=inference_delay, threshold_breach_step=None

## runtime_case_03
Causal leakage and contradiction should show up as high conflict signals with low tau_true.

- emitted_violations: ['ConstructiveHonesty', 'Harmlessness', 'Helpfulness', 'Honesty']
- top_risk_axis: C
- dominant_signal: evidence_mismatches
- axis=tau, max_defect=2, dominant_signal=remaining_subgoals, threshold_breach_step=None
- axis=C, max_defect=12, dominant_signal=evidence_mismatches, threshold_breach_step=0
- axis=M, max_defect=1, dominant_signal=memory_stability, threshold_breach_step=None
- axis=S, max_defect=0, dominant_signal=prediction_entropy, threshold_breach_step=None
- axis=X, max_defect=0, dominant_signal=external_event_rate, threshold_breach_step=None
- axis=P, max_defect=1, dominant_signal=inference_delay, threshold_breach_step=None
