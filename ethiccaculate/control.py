from __future__ import annotations

from dataclasses import dataclass
from math import exp

from .models import ControlObservation, ControlState, SpectralState
from .six_axes import SixAxisTelemetry, evaluate_six_axes

DEFAULT_CONTROL_WEIGHTS = {
    "w1": 1.0,
    "w2": 1.0,
    "w3": 1.0,
    "u1": 1.0,
    "u2": 1.0,
    "u3": 1.0,
    "v1": 1.0,
    "v2": 1.0,
    "v3": 1.0,
    "p1": 1.0,
    "p2": 1.0,
    "p3": 1.0,
    "p4": 1.0,
    "a1": 1.0,
    "a2": 1.0,
    "a3": 1.0,
    "a4": 1.0,
    "m1": 1.0,
    "m2": 1.0,
    "m3": 1.0,
    "m4": 1.0,
}


@dataclass(frozen=True)
class GateThresholds:
    C: float = 0.35
    S: float = 0.35
    P: float = 0.50
    tau: float = 0.60
    M: float = 0.55
    U: float = 0.0
    deepen_S: float = 0.65
    deepen_C: float = 0.55
    stop_tau: float = 0.75
    stop_S: float = 0.25
    stop_C: float = 0.25


def sigmoid(value: float) -> float:
    if value >= 0.0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def control_observation_to_telemetry(observation: ControlObservation) -> SixAxisTelemetry:
    return SixAxisTelemetry(
        remaining_subgoals=max(0, int(round(1.0 - observation.plan_completion))),
        stall_windows=max(0, int(round(observation.hidden_step_delta * 2.0))),
        plan_progress=observation.plan_completion,
        uncertainty_drop=observation.uncertainty_drop,
        answer_drift=observation.answer_drift,
        hidden_state_delta=observation.hidden_step_delta,
        future_leak_score=observation.conflict_rate,
        nli_conflict_score=observation.tool_contradiction,
        citation_gap=observation.citation_gap,
        self_consistency_score=1.0 - observation.prediction_entropy,
        online_jsd=observation.logit_dispersion,
        causal_conflicts=max(0, int(round(observation.conflict_rate))),
        evidence_mismatches=max(0, int(round(observation.citation_gap))),
        prediction_entropy=observation.prediction_entropy,
        covariance_logdet=observation.gradient_covariance,
        gradient_proxy=observation.logit_dispersion,
        stability_oscillation=observation.answer_drift,
        external_event_rate=observation.msg_arrival,
        tool_callback_rate=observation.tool_callback,
        document_update_rate=observation.doc_update,
        interrupt_rate=observation.timeout_risk,
        queue_delay=observation.queue_delay,
        inference_delay=observation.infer_delay,
        clock_skew=observation.clock_skew,
        timeout_risk=observation.timeout_risk,
        recall_hit_rate=observation.recall_hit,
        memory_commit_rate=observation.reuse,
        memory_stability=observation.stability,
        duplication_rate=observation.duplication,
    )


def estimate_control_axes_legacy(
    observation: ControlObservation,
    weights: dict[str, float] | None = None,
) -> ControlState:
    w = dict(DEFAULT_CONTROL_WEIGHTS)
    if weights:
        w.update(weights)

    c = sigmoid(
        w["w1"] * observation.conflict_rate
        + w["w2"] * observation.citation_gap
        + w["w3"] * observation.tool_contradiction
    )
    s = sigmoid(
        w["u1"] * observation.prediction_entropy
        + w["u2"] * observation.logit_dispersion
        + w["u3"] * observation.gradient_covariance
    )
    x = sigmoid(
        w["v1"] * observation.msg_arrival
        + w["v2"] * observation.tool_callback
        + w["v3"] * observation.doc_update
    )
    p = sigmoid(
        w["p1"] * observation.queue_delay
        + w["p2"] * observation.infer_delay
        + w["p3"] * observation.clock_skew
        + w["p4"] * observation.timeout_risk
    )
    tau = sigmoid(
        w["a1"] * observation.plan_completion
        + w["a2"] * observation.uncertainty_drop
        - w["a3"] * observation.answer_drift
        - w["a4"] * observation.hidden_step_delta
    )
    m = sigmoid(
        w["m1"] * observation.reuse
        + w["m2"] * observation.recall_hit
        + w["m3"] * observation.stability
        - w["m4"] * observation.duplication
    )
    return ControlState(C=c, S=s, X=x, P=p, tau=tau, M=m)


def estimate_control_axes(
    observation: ControlObservation,
    weights: dict[str, float] | None = None,
) -> ControlState:
    del weights
    assessment = evaluate_six_axes(control_observation_to_telemetry(observation))
    return ControlState(
        C=assessment.axes["C"].value,
        S=assessment.axes["S"].value,
        X=assessment.axes["X"].value,
        P=assessment.axes["P"].value,
        tau=assessment.axes["tau"].value,
        M=assessment.axes["M"].value,
    )


def fallback_control_from_spectral(spectral: SpectralState) -> ControlState:
    c = sigmoid(spectral.Ecosyn - spectral.Esyn)
    s = sigmoid(abs(spectral.c_gh) + abs(spectral.c_cross))
    x = 0.5
    p = 0.5
    tau = sigmoid(2.0 * spectral.U)
    m = sigmoid(spectral.Esyn - 0.5 * spectral.Ecosyn)
    return ControlState(C=c, S=s, X=x, P=p, tau=tau, M=m)


def write_gate(
    control: ControlState,
    spectral: SpectralState,
    thresholds: GateThresholds | None = None,
) -> bool:
    th = thresholds or GateThresholds()
    return (
        control.C <= th.C
        and control.S <= th.S
        and control.P <= th.P
        and control.tau >= th.tau
        and control.M >= th.M
        and spectral.U >= th.U
    )


def deepen_gate(control: ControlState, thresholds: GateThresholds | None = None) -> bool:
    th = thresholds or GateThresholds()
    return control.S >= th.deepen_S or control.C >= th.deepen_C


def stop_gate(control: ControlState, thresholds: GateThresholds | None = None) -> bool:
    th = thresholds or GateThresholds()
    return control.tau >= th.stop_tau and control.S <= th.stop_S and control.C <= th.stop_C
