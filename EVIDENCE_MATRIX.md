# Evidence Matrix

This matrix maps each reviewer-facing claim to the evidence already present in the repository. It is intentionally conservative: it describes a runnable research prototype and audit package, not a universal ethics system, production deployment, or safety certification.

Core claim:

> We show that heterogeneous ethical systems can be executed, audited, replayed, and compared under a shared event-log protocol, with measurable agreement, conflict, and repair structures.

| Claim | Evidence Layer | Result | What It Shows | Limitation |
|---|---|---:|---|---|
| The ethics audit pipeline is runnable and auditable. | OMB-24 dev benchmark v0.3 | weighted_total_score = 0.988851; weighted_auditability_score = 1.0 | The first-party benchmark can be scored, replayed, attributed, and reported with hierarchy-aware labels. | First-party development benchmark; exact violation match remains a strict reference rather than the main score. |
| The calibrated scorer preserves safety recall while reducing explanation noise. | OMB-24 v0.3 over-trigger calibration | raw_over_trigger_penalty_mean = 0.791667; calibrated_over_trigger_penalty_mean = 0.14273 | Label hierarchy separates primary violations, secondary violations, and diagnostic tags without narrowing the underlying safety rules. | Calibration is evaluated on a small dev benchmark and should not be treated as a universal precision guarantee. |
| The system has an initial generalization check. | OMB-Holdout-24 v0.3 | weighted_total_score = 0.959652; weighted_auditability_score = 1.0 | The v0.3 scorer maintains similar behavior on a frozen internal holdout set. | Internal 24-case holdout; not a public external leaderboard. |
| External honesty-oriented audit is supported. | TruthfulQA-mini | weighted_total_score = 1.0; weighted_auditability_score = 1.0; calibrated_over_trigger_penalty_mean = 0.0 | The audit pipeline can detect known incorrect-answer risk patterns in an external honesty subset. | Detection task over selected known wrong-answer cases; not a full open-ended TruthfulQA generation evaluation. |
| External fairness-oriented audit is supported. | BBQ-mini | weighted_total_score = 1.0; weighted_auditability_score = 1.0; calibrated_over_trigger_penalty_mean = 0.0 | The audit pipeline can flag stereotype-aligned answer choices across six protected-attribute categories. | Audit subset only; not full BBQ and not a general fairness certification. |
| Runtime metadata can enter the audit loop. | vLLM hook runtime smoke test | runtime_event_log.json, runtime_replay_bundle.json, and runtime_risk_attribution.md generated | Hot-path, cold-path, rollback, entropy, evidence, and contradiction metadata can be converted into replayable audit artifacts. | Synthetic smoke test; not a long-running production vLLM deployment. |
| The six-axis layer contributes to auditability and scoring structure. | Six-axis ablation v0.1 | OMB-24 total: 0.688851 to 0.888851 to 0.988851; TruthfulQA-mini total: 0.7 to 0.9 to 1.0 | Moving from no six-axis, to observe-only, to observe + gate + replay improves the audit pipeline's measurable behavior. | Demonstrates audit/protocol contribution, not direct model capability improvement. |
| Comparative ethics is observable under a shared protocol. | Comparative baseline v0.1 | full layer: 18 agreement pairs, 26 conflict-observable cases, 24 shared-axis cases, 26 profile-specific repair cases | The comparative layer exposes agreement, conflict, shared axes, and profile-specific repair attribution that single-profile or siloed-profile baselines cannot show. | Does not decide which ethical profile is correct; measures observability and replayability of disagreement. |
| Cross-profile, cross-cultural, and multi-agent cases can be represented. | Comparative audit minis | cross-profile agreement = 0.891667; cross-cultural agreement = 0.869792; multi-agent agreement = 0.864583 | The same event-log format supports profile comparison, cultural-context cases, and multi-agent traces. | Mini suites; culturally anchored and multi-agent coverage is preliminary. |
| Medium-scale protocol stability has been checked. | Ethics-Audit-Core-128 v0.1 | weighted_total_score = 0.990805; event_log_success_rate = 1.0; replay_success_rate = 1.0; risk_attribution_coverage = 1.0 | A 128-case benchmark can run through event logging, replay, risk attribution, and comparative reporting without changing scoring rules. | Internally assembled medium-scale benchmark; not a public leaderboard or large-scale population study. |
| The package is reproducible from local commands. | Test suite and reproducibility commands | 31 tests OK | The repository includes command-level entry points for the major benchmark, runtime, ablation, comparative, and Core-128 layers. | Reproducibility is local-environment based; external dataset coverage remains curated and small. |

## Evidence Files

| Evidence Layer | Primary Files |
|---|---|
| Frozen v0.3 release | `releases/ethiccaculate-v0.3-omb24/` |
| OMB-24 v0.3 | `benchmarks/dev/OMB24_SCORING_v0.3.json`, `benchmarks/dev/OMB24_OVER_TRIGGER_CALIBRATION_v0.3.md`, `benchmarks/dev/OMB24_EXTRA_LABEL_REPORT_v0.3.md` |
| OMB-Holdout-24 | `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md` |
| TruthfulQA-mini | `benchmarks/external/TRUTHFULQA_MINI_v0.3.json`, `benchmarks/external/TRUTHFULQA_MINI_v0.3.md` |
| BBQ-mini | `benchmarks/external/BBQ_MINI_v0.3.json`, `benchmarks/external/BBQ_MINI_v0.3.md` |
| Runtime smoke | `releases/ethiccaculate-v0.3-omb24/runtime_smoke/` |
| Six-axis ablation | `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.json`, `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.md` |
| Comparative audit | `benchmarks/comparative/` |
| Core-128 | `benchmarks/core128/` |
| Modification history | `MODIFICATION_LOG.md` |
