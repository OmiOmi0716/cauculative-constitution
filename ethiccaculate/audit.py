from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, replace

from .control import (
    GateThresholds,
    control_observation_to_telemetry,
    deepen_gate,
    fallback_control_from_spectral,
    stop_gate,
    write_gate,
)
from .decoder import DecoderConfig, decode_bcg_profile
from .models import (
    AlternativeProgram,
    AuditResult,
    CrossSystemConflict,
    DialogueEvent,
    MoralSystemProfile,
    MoveRecord,
    MultiAuditResult,
    OmegaState,
    Principle,
    ROLE_KEYS,
    SystemAuditResult,
)
from .operations import apply_operation, infer_move
from .principles import default_principles, evaluate_principles
from .profiles import default_moral_system_profile
from .runtime import runtime_meta_from_event_meta
from .six_axes import (
    StabilityCalibrationPoint,
    SixAxisAssessment,
    SixAxisSnapshot,
    SixAxisTelemetry,
    TauCalibrationPoint,
    calibrate_stability_gamma,
    evaluate_six_axes,
    legal_progress,
    normalized_entropy,
    relative_state_variation,
    solve_tau_alpha_star,
    tau_alpha_error_bound,
    tau_nli_tolerance_threshold,
)
from .spectral import ScalarizerConfig, spectral_from_blocks


_TELEMETRY_FLOAT_TUPLES = {"attention_leak_levels"}
_TELEMETRY_INT_TUPLES = {"consensus_cluster_sizes"}
_TELEMETRY_INT_FIELDS = {
    "remaining_subgoals",
    "stall_windows",
    "consensus_sample_count",
    "causal_conflicts",
    "evidence_mismatches",
    "covariance_dimension",
    "vocab_size",
    "stability_label",
    "rollback_depth_tokens",
}


@dataclass(frozen=True)
class ObjectiveWeights:
    lambda_C: float = 0.25
    lambda_S: float = 0.20
    lambda_P: float = 0.10
    lambda_M: float = 0.15
    lambda_V: float = 0.50


@dataclass
class _PreparedStep:
    index: int
    event: DialogueEvent
    state: OmegaState
    move: MoveRecord | None
    violations: list
    telemetry: SixAxisTelemetry


def _merge_objective_weights(
    system_profile: MoralSystemProfile | None,
    objective_weights: ObjectiveWeights | None,
) -> ObjectiveWeights:
    base = asdict(ObjectiveWeights())
    if system_profile is not None:
        base.update(system_profile.objective_weights)
    if objective_weights is not None:
        base.update(asdict(objective_weights))
    return ObjectiveWeights(**base)


def _merge_gate_thresholds(
    system_profile: MoralSystemProfile | None,
    gate_thresholds: GateThresholds | None,
) -> GateThresholds:
    base = asdict(GateThresholds())
    if system_profile is not None:
        base.update(system_profile.gate_thresholds)
    if gate_thresholds is not None:
        base.update(asdict(gate_thresholds))
    return GateThresholds(**base)


def _merge_decoder_config(
    system_profile: MoralSystemProfile | None,
    decoder_config: DecoderConfig | None,
) -> DecoderConfig:
    base = asdict(DecoderConfig())
    if system_profile is not None:
        base.update(system_profile.decoder_config)
    if decoder_config is not None:
        base.update(asdict(decoder_config))
    return DecoderConfig(**base)


def _merge_scalarizer_config(
    system_profile: MoralSystemProfile | None,
    scalarizer_config: ScalarizerConfig | None,
) -> ScalarizerConfig:
    base = asdict(ScalarizerConfig())
    if system_profile is not None:
        base.update(system_profile.scalarizer_config)
    if scalarizer_config is not None:
        base.update(asdict(scalarizer_config))
    return ScalarizerConfig(**base)


def _meta_value(event: DialogueEvent, key: str):
    if key not in event.meta:
        return None
    raw = event.meta[key]
    try:
        return json.loads(raw)
    except Exception:
        return raw


def _meta_float(event: DialogueEvent, key: str, default: float | None = None) -> float | None:
    value = _meta_value(event, key)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _meta_int(event: DialogueEvent, key: str, default: int | None = None) -> int | None:
    value = _meta_value(event, key)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _meta_float_tuple(event: DialogueEvent, key: str) -> tuple[float, ...]:
    value = _meta_value(event, key)
    if value is None:
        return tuple()
    if isinstance(value, list):
        try:
            return tuple(float(item) for item in value)
        except (TypeError, ValueError):
            return tuple()
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        try:
            return tuple(float(item) for item in parts)
        except (TypeError, ValueError):
            return tuple()
    return tuple()


def _meta_int_tuple(event: DialogueEvent, key: str) -> tuple[int, ...]:
    value = _meta_value(event, key)
    if value is None:
        return tuple()
    if isinstance(value, list):
        try:
            return tuple(int(item) for item in value)
        except (TypeError, ValueError):
            return tuple()
    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",") if part.strip()]
        try:
            return tuple(int(item) for item in parts)
        except (TypeError, ValueError):
            return tuple()
    return tuple()


def _fallback_telemetry_from_event(event: DialogueEvent, spectral) -> SixAxisTelemetry:
    return SixAxisTelemetry(
        remaining_subgoals=max(0, int(round((1.0 - max(spectral.U, 0.0)) * 3.0))),
        stall_windows=1 if abs(spectral.c_cross) < 0.05 and spectral.U < 0.1 else 0,
        plan_progress=max(0.0, spectral.U),
        uncertainty_drop=max(0.0, spectral.Esyn),
        answer_drift=max(0.0, spectral.Ecosyn - spectral.Esyn),
        hidden_state_delta=abs(spectral.c_cross),
        future_leak_score=max(0.0, event.truth_distortion),
        nli_conflict_score=max(0.0, event.claimed_confidence - event.evidence_coverage),
        citation_gap=max(0.0, 1.0 - event.evidence_coverage),
        self_consistency_score=max(0.0, 1.0 - event.truth_distortion),
        online_jsd=abs(spectral.c_gh),
        causal_conflicts=1 if event.truth_distortion > 0.5 else 0,
        evidence_mismatches=1 if event.evidence_coverage < 0.5 else 0,
        prediction_entropy=abs(spectral.c_gh),
        covariance_logdet=abs(spectral.c_cross),
        gradient_proxy=abs(spectral.c_ud),
        stability_oscillation=abs(spectral.Enoise),
        external_event_rate=1.0 if event.tool else 0.0,
        tool_callback_rate=1.0 if event.tool else 0.0,
        document_update_rate=0.0,
        interrupt_rate=0.0,
        queue_delay=0.0,
        inference_delay=0.0,
        clock_skew=0.0,
        timeout_risk=0.0,
        recall_hit_rate=max(0.0, spectral.Esyn),
        memory_commit_rate=max(0.0, spectral.U),
        memory_stability=max(0.0, 1.0 - spectral.Enoise),
        duplication_rate=max(0.0, abs(spectral.c_cross)),
    )


def _event_with_runtime_meta(event: DialogueEvent) -> DialogueEvent:
    runtime_meta = runtime_meta_from_event_meta(event.meta)
    if not runtime_meta:
        return event
    return replace(event, meta={**runtime_meta, **event.meta})


def _telemetry_overrides_from_meta(event: DialogueEvent) -> dict[str, object]:
    overrides: dict[str, object] = {}
    for telemetry_field in fields(SixAxisTelemetry):
        name = telemetry_field.name
        if name not in event.meta:
            continue
        if name in _TELEMETRY_FLOAT_TUPLES:
            value = _meta_float_tuple(event, name)
        elif name in _TELEMETRY_INT_TUPLES:
            value = _meta_int_tuple(event, name)
        elif name in _TELEMETRY_INT_FIELDS:
            value = _meta_int(event, name)
        else:
            value = _meta_float(event, name)
        if value is not None:
            overrides[name] = value
    return overrides


def _build_event_telemetry(event: DialogueEvent, spectral) -> SixAxisTelemetry:
    event = _event_with_runtime_meta(event)
    if event.control_observation is not None:
        base = control_observation_to_telemetry(event.control_observation)
    else:
        base = _fallback_telemetry_from_event(event, spectral)

    return replace(base, **_telemetry_overrides_from_meta(event))


def _build_calibration_summary(telemetries: list[SixAxisTelemetry]) -> dict[str, object]:
    stability_points = [
        StabilityCalibrationPoint(
            entropy_norm=normalized_entropy(telemetry.prediction_entropy, telemetry.vocab_size),
            geom_proxy=relative_state_variation(
                telemetry.current_covariance_det,
                telemetry.baseline_covariance_det,
                telemetry.covariance_dimension,
            )
            if telemetry.current_covariance_det is not None and telemetry.baseline_covariance_det is not None
            else telemetry.covariance_logdet,
            out_of_bounds_label=telemetry.stability_label,
        )
        for telemetry in telemetries
        if telemetry.stability_label is not None
    ]
    gamma1, gamma2 = calibrate_stability_gamma(stability_points)

    tau_points = [
        TauCalibrationPoint(
            tau_proxy_v2=normalized_tau_proxy,
            fisher_rao_delta=telemetry.fisher_rao_delta,
            tau_true=telemetry.tau_true,
        )
        for telemetry in telemetries
        if telemetry.fisher_rao_delta is not None
        if telemetry.tau_true is not None
        for normalized_tau_proxy in [evaluate_six_axes(telemetry).hot_path_metrics["tau_proxy_v2"]]
    ]
    alpha_star = solve_tau_alpha_star(tau_points)
    nli_sigma_values = [telemetry.nli_sigma for telemetry in telemetries if telemetry.nli_sigma is not None]
    nli_sigma = max(nli_sigma_values) if nli_sigma_values else None
    alpha_error_bound = tau_alpha_error_bound(tau_points, nli_sigma) if nli_sigma is not None else None
    nli_tolerance_threshold = tau_nli_tolerance_threshold(tau_points) if tau_points else None

    return {
        "stability_point_count": len(stability_points),
        "tau_point_count": len(tau_points),
        "gamma1": gamma1,
        "gamma2": gamma2,
        "tau_alpha_star": alpha_star,
        "nli_sigma": nli_sigma,
        "tau_alpha_error_bound": alpha_error_bound,
        "tau_nli_tolerance_threshold": nli_tolerance_threshold,
    }


def _apply_calibration(telemetry: SixAxisTelemetry, calibration_summary: dict[str, object]) -> SixAxisTelemetry:
    return replace(
        telemetry,
        stability_gamma1=telemetry.stability_gamma1
        if telemetry.stability_gamma1 is not None
        else float(calibration_summary.get("gamma1", 0.5)),
        stability_gamma2=telemetry.stability_gamma2
        if telemetry.stability_gamma2 is not None
        else float(calibration_summary.get("gamma2", 0.5)),
        tau_alpha_override=telemetry.tau_alpha_override
        if telemetry.tau_alpha_override is not None
        else float(calibration_summary.get("tau_alpha_star", 0.65)),
        tau_alpha_error_bound=telemetry.tau_alpha_error_bound
        if telemetry.tau_alpha_error_bound is not None
        else calibration_summary.get("tau_alpha_error_bound"),
        tau_nli_tolerance_threshold=telemetry.tau_nli_tolerance_threshold
        if telemetry.tau_nli_tolerance_threshold is not None
        else calibration_summary.get("tau_nli_tolerance_threshold"),
    )


def estimate_geom_blocks(
    event: DialogueEvent,
    decoder_config: DecoderConfig | None = None,
):
    if event.blocks is not None:
        missing = [role for role in ROLE_KEYS if role not in event.blocks]
        if missing:
            raise ValueError(f"Event {event.event_id} is missing geometry roles: {', '.join(missing)}")
        return dict(event.blocks)
    if event.bcg_profile is not None:
        return decode_bcg_profile(event.bcg_profile, decoder_config)
    raise ValueError(f"Event {event.event_id} must provide either blocks or a BCG profile.")


def estimate_control_state(event: DialogueEvent, spectral):
    if event.control is not None:
        return event.control
    if event.control_observation is not None:
        from .control import estimate_control_axes

        return estimate_control_axes(event.control_observation)
    return fallback_control_from_spectral(spectral)


def build_state(
    event: DialogueEvent,
    index: int,
    blocks,
    spectral,
    control,
) -> OmegaState:
    return OmegaState(
        state_id=f"S{index}",
        blocks=blocks,
        spectral=spectral,
        control=control,
        role_config=list(event.role_config),
        meta={
            "event_id": event.event_id,
            "speaker": event.speaker,
            "tool": event.tool,
            **event.meta,
        },
    )


def _explicit_move(
    previous: OmegaState | None,
    current: OmegaState,
    event: DialogueEvent,
    system_profile: MoralSystemProfile | None = None,
) -> MoveRecord:
    delta_u = 0.0
    delta_ecosyn = 0.0
    if previous is not None:
        delta_u = current.spectral.U - previous.spectral.U
        delta_ecosyn = current.spectral.Ecosyn - previous.spectral.Ecosyn
    return MoveRecord(
        move_id="",
        op=event.declared_move or "UNKNOWN",
        strength=event.move_strength,
        pre_state=previous.state_id if previous else None,
        post_state=current.state_id,
        audit={"delta_U": delta_u, "delta_Ecosyn": delta_ecosyn},
        system_id=system_profile.system_id if system_profile else "",
        system_version=system_profile.version if system_profile else "",
    )


def evaluate_objective(
    state: OmegaState,
    violation_count: int = 0,
    weights: ObjectiveWeights | None = None,
) -> float:
    w = weights or ObjectiveWeights()
    return (
        state.spectral.U
        - w.lambda_C * state.control.C
        - w.lambda_S * state.control.S
        - w.lambda_P * state.control.P
        + w.lambda_M * state.control.M
        - w.lambda_V * violation_count
    )


def _sequence_allowed(
    sequence: list[tuple[str, float]],
    allowed_moves: list[str],
    forbidden_moves: list[str],
) -> bool:
    move_names = [name for name, _ in sequence]
    if allowed_moves and any(name not in allowed_moves for name in move_names):
        return False
    if forbidden_moves and any(name in forbidden_moves for name in move_names):
        return False
    return True


def search_alternative_program(
    state: OmegaState | None,
    principles: list[Principle],
    event: DialogueEvent | None,
    scalarizer: ScalarizerConfig | None = None,
    weights: ObjectiveWeights | None = None,
    allowed_moves: list[str] | None = None,
    forbidden_moves: list[str] | None = None,
) -> AlternativeProgram | None:
    if state is None or event is None:
        return None

    theta = scalarizer or ScalarizerConfig()
    current_violations = evaluate_principles(principles, state, event, None)
    current_objective = evaluate_objective(state, len(current_violations), weights)

    sequences = [
        [("G_REFRAME_JUSTICE", 0.5)],
        [("H_BOUNDARY_SET", 0.3)],
        [("BRIDGE_THEO_TO_PSY", 0.4)],
        [("BRIDGE_DATA_TO_THEORY", 0.4)],
        [("G_REFRAME_JUSTICE", 0.5), ("H_BOUNDARY_SET", 0.3)],
        [("BRIDGE_THEO_TO_PSY", 0.4), ("H_BOUNDARY_SET", 0.2)],
        [("BRIDGE_DATA_TO_THEORY", 0.4), ("G_REFRAME_JUSTICE", 0.4)],
    ]

    allowed = allowed_moves or []
    forbidden = forbidden_moves or []

    best_program: AlternativeProgram | None = None
    best_objective = current_objective

    for sequence in sequences:
        if not _sequence_allowed(sequence, allowed, forbidden):
            continue

        blocks = dict(state.blocks)
        for op, strength in sequence:
            blocks = apply_operation(blocks, op, strength, theta)

        spectral = spectral_from_blocks(blocks, theta)
        candidate_state = OmegaState(
            state_id="ALT",
            blocks=blocks,
            spectral=spectral,
            control=state.control,
            role_config=state.role_config,
            meta={"generated_by": "heuristic_search_v0_2"},
        )
        violation_count = len(evaluate_principles(principles, candidate_state, event, None))
        objective = evaluate_objective(candidate_state, violation_count, weights)

        if objective > best_objective + 1e-9:
            best_objective = objective
            best_program = AlternativeProgram(
                moves=[name for name, _ in sequence],
                expected_U_gain=spectral.U - state.spectral.U,
                expected_objective_gain=objective - current_objective,
                notes="Heuristic search filtered by the active moral-system profile.",
            )

    return best_program


def _dominant_signal(signals: dict[str, object]) -> tuple[str | None, float | int | None]:
    best_key = None
    best_value: float | int | None = None
    best_magnitude = float("-inf")
    for key, value in signals.items():
        if isinstance(value, bool) or value is None:
            continue
        if isinstance(value, (int, float)):
            magnitude = abs(float(value))
            if magnitude > best_magnitude:
                best_key = key
                best_value = value
                best_magnitude = magnitude
    return best_key, best_value


def _build_risk_attribution(event_log: list[dict[str, object]]) -> list[dict[str, object]]:
    if not event_log:
        return []

    attributions: list[dict[str, object]] = []
    axis_order = ("tau", "C", "M", "S", "X", "P")

    for axis in axis_order:
        drift_start = None
        threshold_breach = None
        max_entry = None
        previous_defect = None
        previous_value = None

        for entry in event_log:
            axis_payload = entry["assessment"]["axes"][axis]
            defect = axis_payload["defect"]
            value = axis_payload["value"]

            if drift_start is None and previous_defect is not None:
                if defect > previous_defect or value > previous_value + 0.05:
                    drift_start = entry

            if threshold_breach is None and not axis_payload["acceptable"]:
                threshold_breach = entry

            if max_entry is None or defect > max_entry["assessment"]["axes"][axis]["defect"]:
                max_entry = entry

            previous_defect = defect
            previous_value = value

        if max_entry is None:
            continue

        signal_key, signal_value = _dominant_signal(max_entry["assessment"]["axes"][axis]["signals"])
        attributions.append(
            {
                "axis": axis,
                "drift_started_step": drift_start["step_index"] if drift_start is not None else None,
                "drift_started_event_id": drift_start["event_id"] if drift_start is not None else None,
                "threshold_breach_step": threshold_breach["step_index"] if threshold_breach is not None else None,
                "threshold_breach_event_id": threshold_breach["event_id"] if threshold_breach is not None else None,
                "max_defect_step": max_entry["step_index"],
                "max_defect_event_id": max_entry["event_id"],
                "max_defect": max_entry["assessment"]["axes"][axis]["defect"],
                "max_value": max_entry["assessment"]["axes"][axis]["value"],
                "dominant_signal": signal_key,
                "dominant_signal_value": signal_value,
                "legal_progress_break_step": max_entry["step_index"] if not max_entry["legal_progress"] else None,
            }
        )

    return attributions


def replay_event_log(replay_bundle: dict[str, object], from_step: int = 0, to_step: int | None = None) -> list[dict[str, object]]:
    event_log = list(replay_bundle.get("event_log", []))
    return event_log[from_step:to_step]


def _build_replay_bundle(
    states: list[OmegaState],
    moves: list[MoveRecord],
    violations,
    alternative_program: AlternativeProgram | None,
    gate_thresholds: GateThresholds | None = None,
    system_profile: MoralSystemProfile | None = None,
    event_log: list[dict[str, object]] | None = None,
    mcd_snapshots: list[dict[str, object]] | None = None,
    risk_attribution: list[dict[str, object]] | None = None,
    calibration_summary: dict[str, object] | None = None,
):
    thresholds = gate_thresholds or GateThresholds()
    gate_report = [
        {
            "state_id": state.state_id,
            "write_gate": write_gate(state.control, state.spectral, thresholds),
            "deepen_gate": deepen_gate(state.control, thresholds),
            "stop_gate": stop_gate(state.control, thresholds),
        }
        for state in states
    ]
    return {
        "system_profile": asdict(system_profile) if system_profile else None,
        "states": [asdict(state) for state in states],
        "moves": [asdict(move) for move in moves],
        "violations": [asdict(violation) for violation in violations],
        "gate_report": gate_report,
        "alternative_program": asdict(alternative_program) if alternative_program else None,
        "event_log": event_log or [],
        "mcd_snapshots": mcd_snapshots or [],
        "risk_attribution": risk_attribution or [],
        "calibration_summary": calibration_summary or {},
    }


def audit_dialogue(
    dialogue: list[DialogueEvent],
    principles: list[Principle] | None = None,
    decoder_config: DecoderConfig | None = None,
    scalarizer_config: ScalarizerConfig | None = None,
    objective_weights: ObjectiveWeights | None = None,
    gate_thresholds: GateThresholds | None = None,
    system_profile: MoralSystemProfile | None = None,
) -> AuditResult:
    active_profile = system_profile
    if active_profile is None and principles is None:
        active_profile = default_moral_system_profile()

    merged_decoder = _merge_decoder_config(active_profile, decoder_config)
    merged_scalarizer = _merge_scalarizer_config(active_profile, scalarizer_config)
    merged_objective = _merge_objective_weights(active_profile, objective_weights)
    merged_gate_thresholds = _merge_gate_thresholds(active_profile, gate_thresholds)

    active_principles = principles or (active_profile.principles if active_profile else default_principles())

    states: list[OmegaState] = []
    moves: list[MoveRecord] = []
    violations = []
    prepared_steps: list[_PreparedStep] = []

    previous_state: OmegaState | None = None
    for index, event in enumerate(dialogue):
        blocks = estimate_geom_blocks(event, merged_decoder)
        spectral = spectral_from_blocks(blocks, merged_scalarizer)
        control = estimate_control_state(event, spectral)
        state = build_state(event, index, blocks, spectral, control)
        states.append(state)

        if event.declared_move:
            move = _explicit_move(previous_state, state, event, active_profile)
        else:
            move = infer_move(previous_state, state)
            if move is not None and active_profile is not None:
                move.system_id = active_profile.system_id
                move.system_version = active_profile.version

        if move is not None:
            move.move_id = f"M{len(moves)}"
            moves.append(move)

        state_violations = evaluate_principles(active_principles, state, event, move)
        violations.extend(state_violations)
        telemetry = _build_event_telemetry(event, spectral)
        prepared_steps.append(
            _PreparedStep(
                index=index,
                event=event,
                state=state,
                move=move,
                violations=state_violations,
                telemetry=telemetry,
            )
        )
        previous_state = state

    calibration_summary = _build_calibration_summary([step.telemetry for step in prepared_steps])
    event_log: list[dict[str, object]] = []
    mcd_snapshots: list[dict[str, object]] = []
    previous_assessment: SixAxisAssessment | None = None

    for step in prepared_steps:
        telemetry = _apply_calibration(step.telemetry, calibration_summary)
        assessment = evaluate_six_axes(telemetry)
        snapshot = SixAxisSnapshot(
            snapshot_id=f"snap-{step.event.request_id or 'req'}-{step.index}",
            request_id=step.event.request_id or "req",
            event_id=step.event.event_id,
            timestamp=step.event.timestamp if step.event.timestamp else float(step.index),
            assessment=assessment,
            control_history=(
                [{"action": step.move.op, "strength": step.move.strength}]
                if step.move is not None
                else [{"action": "observe_only", "axis": "tau"}]
            ),
            meta={
                "speaker": step.event.speaker,
                "tool": step.event.tool,
                "state_id": step.state.state_id,
                "system_id": active_profile.system_id if active_profile else "",
            },
        )
        legal = True if previous_assessment is None else legal_progress(previous_assessment, assessment)
        event_log.append(
            {
                "step_index": step.index,
                "event_id": step.event.event_id,
                "request_id": step.event.request_id or "req",
                "state_id": step.state.state_id,
                "move_id": step.move.move_id if step.move is not None else None,
                "move_op": step.move.op if step.move is not None else None,
                "violations": [asdict(violation) for violation in step.violations],
                "observation": asdict(step.event.control_observation) if step.event.control_observation is not None else None,
                "telemetry": asdict(telemetry),
                "assessment": assessment.to_dict(),
                "legal_progress": legal,
                "gates": {
                    "write_gate": write_gate(step.state.control, step.state.spectral, merged_gate_thresholds),
                    "deepen_gate": deepen_gate(step.state.control, merged_gate_thresholds),
                    "stop_gate": stop_gate(step.state.control, merged_gate_thresholds),
                },
            }
        )
        mcd_snapshots.append(snapshot.to_json_ready())
        previous_assessment = assessment

    risk_attribution = _build_risk_attribution(event_log)

    alternative_program = search_alternative_program(
        states[-1] if states else None,
        active_principles,
        dialogue[-1] if dialogue else None,
        merged_scalarizer,
        merged_objective,
        active_profile.allowed_moves if active_profile else None,
        active_profile.forbidden_moves if active_profile else None,
    )
    replay_bundle = _build_replay_bundle(
        states,
        moves,
        violations,
        alternative_program,
        merged_gate_thresholds,
        active_profile,
        event_log,
        mcd_snapshots,
        risk_attribution,
        calibration_summary,
    )
    return AuditResult(
        states=states,
        moves=moves,
        violations=violations,
        alternative_program=alternative_program,
        replay_bundle=replay_bundle,
        event_log=event_log,
        mcd_snapshots=mcd_snapshots,
        risk_attribution=risk_attribution,
        calibration_summary=calibration_summary,
        system_id=active_profile.system_id if active_profile else "",
        system_version=active_profile.version if active_profile else "",
        system_name=active_profile.name if active_profile else "",
    )


def _build_system_summary(
    result: AuditResult,
    objective_score: float,
    gate_thresholds: GateThresholds,
) -> dict[str, object]:
    final_state = result.states[-1] if result.states else None
    top_risk_axis = None
    if result.risk_attribution:
        top_risk_axis = max(result.risk_attribution, key=lambda item: item.get("max_defect", 0)).get("axis")
    return {
        "final_state_id": final_state.state_id if final_state else None,
        "final_U": final_state.spectral.U if final_state else None,
        "write_gate": write_gate(final_state.control, final_state.spectral, gate_thresholds) if final_state else None,
        "deepen_gate": deepen_gate(final_state.control, gate_thresholds) if final_state else None,
        "stop_gate": stop_gate(final_state.control, gate_thresholds) if final_state else None,
        "objective_score": objective_score,
        "alternative_moves": result.alternative_program.moves if result.alternative_program else [],
        "top_risk_axis": top_risk_axis,
    }


def _build_cross_system_conflicts(audit_by_system: dict[str, SystemAuditResult]) -> list[CrossSystemConflict]:
    conflicts: list[CrossSystemConflict] = []
    if not audit_by_system:
        return conflicts

    alternative_signatures = {
        system_id: tuple(result.audit_result.alternative_program.moves) if result.audit_result.alternative_program else tuple()
        for system_id, result in audit_by_system.items()
    }
    unique_signatures = {signature for signature in alternative_signatures.values()}
    if len(unique_signatures) > 1:
        conflicts.append(
            CrossSystemConflict(
                kind="alternative_program_divergence",
                systems=list(audit_by_system.keys()),
                message="Different moral systems recommend different alternative move sequences.",
                details={"alternatives": {key: list(value) for key, value in alternative_signatures.items()}},
            )
        )

    violation_signatures = {
        system_id: sorted({violation.principle for violation in result.audit_result.violations})
        for system_id, result in audit_by_system.items()
    }
    if len({tuple(value) for value in violation_signatures.values()}) > 1:
        conflicts.append(
            CrossSystemConflict(
                kind="violation_divergence",
                systems=list(audit_by_system.keys()),
                message="The active systems disagree on which principles are violated.",
                details={"violations": violation_signatures},
            )
        )

    objective_scores = {system_id: result.objective_score for system_id, result in audit_by_system.items()}
    if objective_scores:
        best_system = max(objective_scores, key=objective_scores.get)
        worst_system = min(objective_scores, key=objective_scores.get)
        spread = objective_scores[best_system] - objective_scores[worst_system]
        if spread > 0.30:
            conflicts.append(
                CrossSystemConflict(
                    kind="objective_spread",
                    systems=[best_system, worst_system],
                    message="The systems score the same trace very differently.",
                    details={"objective_scores": objective_scores, "spread": spread},
                )
            )

    hard_constraint_systems = {
        system_id: result.hard_constraint_violations for system_id, result in audit_by_system.items()
    }
    if len(set(hard_constraint_systems.values())) > 1:
        conflicts.append(
            CrossSystemConflict(
                kind="hard_constraint_divergence",
                systems=list(audit_by_system.keys()),
                message="The systems disagree about hard-constraint violations.",
                details={"hard_constraint_violations": hard_constraint_systems},
            )
        )

    return conflicts


def audit_dialogue_multi(
    dialogue: list[DialogueEvent],
    profiles: list[MoralSystemProfile] | None = None,
    decoder_config: DecoderConfig | None = None,
    scalarizer_config: ScalarizerConfig | None = None,
) -> MultiAuditResult:
    active_profiles = profiles or [default_moral_system_profile()]
    audit_by_system: dict[str, SystemAuditResult] = {}

    for profile in active_profiles:
        result = audit_dialogue(
            dialogue,
            decoder_config=decoder_config,
            scalarizer_config=scalarizer_config,
            system_profile=profile,
        )
        weights = _merge_objective_weights(profile, None)
        thresholds = _merge_gate_thresholds(profile, None)
        final_state = result.states[-1] if result.states else None
        violation_count = len(result.violations)
        objective_score = evaluate_objective(final_state, violation_count, weights) if final_state else 0.0
        hard_constraint_violations = sum(1 for violation in result.violations if violation.hard_constraint)
        audit_by_system[profile.system_id] = SystemAuditResult(
            system_id=profile.system_id,
            system_version=profile.version,
            system_name=profile.name,
            audit_result=result,
            objective_score=objective_score,
            violation_count=violation_count,
            hard_constraint_violations=hard_constraint_violations,
            summary=_build_system_summary(result, objective_score, thresholds),
        )

    conflicts = _build_cross_system_conflicts(audit_by_system)
    return MultiAuditResult(
        audit_by_system=audit_by_system,
        cross_system_conflicts=conflicts,
        meta={"profile_count": len(active_profiles)},
    )
