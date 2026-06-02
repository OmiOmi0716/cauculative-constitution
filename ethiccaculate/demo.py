from __future__ import annotations

import json

from .audit import audit_dialogue, audit_dialogue_multi
from .examples import multi_system_sensitive_case_events, whitepaper_truth_vs_harm_events
from .profiles import load_builtin_moral_system_profiles
from .six_axes import SixAxisSnapshot, SixAxisTelemetry, evaluate_six_axes


def _single_system_summary() -> dict[str, object]:
    events, theta = whitepaper_truth_vs_harm_events()
    result = audit_dialogue(events, scalarizer_config=theta)
    return {
        "system_id": result.system_id,
        "states": [
            {
                "state_id": state.state_id,
                "U": round(state.spectral.U, 6),
                "Ebase": round(state.spectral.Ebase, 6),
                "Esyn": round(state.spectral.Esyn, 6),
                "Ecosyn": round(state.spectral.Ecosyn, 6),
            }
            for state in result.states
        ],
        "moves": [
            {
                "move_id": move.move_id,
                "op": move.op,
                "strength": round(move.strength, 6),
                "delta_U": round(move.audit.get("delta_U", 0.0), 6),
            }
            for move in result.moves
        ],
        "calibration_summary": result.calibration_summary,
        "risk_attribution": result.risk_attribution,
    }


def _multi_system_summary() -> dict[str, object]:
    events = multi_system_sensitive_case_events()
    profiles = load_builtin_moral_system_profiles()
    result = audit_dialogue_multi(events, profiles=profiles)
    return {
        "systems": {
            system_id: {
                "system_name": system_result.system_name,
                "objective_score": round(system_result.objective_score, 6),
                "violation_count": system_result.violation_count,
                "hard_constraint_violations": system_result.hard_constraint_violations,
                "alternative_moves": system_result.summary.get("alternative_moves", []),
                "violated_principles": [violation.principle for violation in system_result.audit_result.violations],
            }
            for system_id, system_result in result.audit_by_system.items()
        },
        "cross_system_conflicts": [
            {
                "kind": conflict.kind,
                "systems": conflict.systems,
                "message": conflict.message,
            }
            for conflict in result.cross_system_conflicts
        ],
    }


def _spec_driven_six_axis_summary() -> dict[str, object]:
    telemetry = SixAxisTelemetry(
        remaining_subgoals=1,
        stall_windows=0,
        plan_progress=0.85,
        uncertainty_drop=0.60,
        answer_drift=0.10,
        hidden_state_delta=0.15,
        fisher_rao_delta=0.30,
        future_leak_score=0.02,
        nli_conflict_score=0.08,
        citation_gap=0.05,
        self_consistency_score=0.94,
        online_jsd=0.06,
        causal_conflicts=0,
        evidence_mismatches=0,
        prediction_entropy=0.22,
        covariance_logdet=0.20,
        gradient_proxy=0.18,
        stability_oscillation=0.10,
        external_event_rate=0.08,
        tool_callback_rate=0.04,
        document_update_rate=0.02,
        interrupt_rate=0.01,
        queue_delay=0.10,
        inference_delay=0.06,
        clock_skew=0.01,
        timeout_risk=0.02,
        recall_hit_rate=0.80,
        memory_commit_rate=0.78,
        memory_stability=0.88,
        duplication_rate=0.05,
    )
    assessment = evaluate_six_axes(telemetry)
    snapshot = SixAxisSnapshot(
        snapshot_id="snap-demo-001",
        request_id="req-demo-001",
        event_id="evt-demo-001",
        timestamp=0.0,
        assessment=assessment,
        control_history=[{"action": "observe_only", "axis": "tau"}],
        meta={"source": "pdf_spec_demo"},
    )
    return {
        "commit_domain": assessment.commit_domain,
        "ranking": list(assessment.ranking),
        "axes": {
            axis: {
                "value": round(result.value, 6),
                "defect": result.defect,
                "threshold": result.threshold,
                "acceptable": result.acceptable,
            }
            for axis, result in assessment.axes.items()
        },
        "hot_path_metrics": {key: round(value, 6) for key, value in assessment.hot_path_metrics.items()},
        "cold_path_metrics": {key: round(value, 6) for key, value in assessment.cold_path_metrics.items()},
        "snapshot": snapshot.to_json_ready(),
    }


def main() -> None:
    print("ethiccaculate v0.2 demo")
    print(
        json.dumps(
            {
                "single_system_whitepaper": _single_system_summary(),
                "multi_system_sensitive_case": _multi_system_summary(),
                "spec_driven_six_axis": _spec_driven_six_axis_summary(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
