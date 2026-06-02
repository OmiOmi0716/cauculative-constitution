from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import ceil, exp, log, sqrt, tanh
from typing import Any


AXIS_ORDER = ("tau", "C", "M", "S", "X", "P")


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = exp(-value)
        return 1.0 / (1.0 + z)
    z = exp(value)
    return z / (1.0 + z)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _interval_distance(value: float, interval: tuple[float, float]) -> float:
    low, high = interval
    if value < low:
        return low - value
    if value > high:
        return value - high
    return 0.0


@dataclass(frozen=True)
class SixAxisWeights:
    leak_weight: float = 0.45
    conflict_weight: float = 0.40
    citation_weight: float = 0.15
    stability_entropy_weight: float = 0.50
    stability_geom_weight: float = 0.50
    tau_plan_weight: float = 1.0
    tau_uncertainty_weight: float = 0.8
    tau_drift_weight: float = 1.0
    tau_hidden_weight: float = 0.6
    tau_alpha: float = 0.65
    tau_stall_penalty: float = 2.0
    causal_layer_kappa: float = 2.0
    stability_gamma_grid: int = 101
    tau_error_tolerance: float = 0.05


@dataclass(frozen=True)
class SixAxisThresholds:
    kappa_C: int = 1
    kappa_S: int = 1
    kappa_X: int = 1
    kappa_P: int = 1
    kappa_tau: int = 4
    kappa_M: int = 1
    epsilon_C: float = 0.10
    epsilon_S: float = 0.10
    epsilon_X: float = 0.20
    epsilon_P: float = 0.20
    epsilon_M: float = 0.20
    stability_interval: tuple[float, float] = (0.10, 0.65)
    memory_commit_floor: float = 0.55
    safe_stability_margin: float = 0.05


@dataclass(frozen=True)
class SixAxisTelemetry:
    remaining_subgoals: int = 0
    stall_windows: int = 0
    plan_progress: float = 0.0
    uncertainty_drop: float = 0.0
    answer_drift: float = 0.0
    hidden_state_delta: float = 0.0
    fisher_rao_delta: float | None = None
    future_leak_score: float = 0.0
    nli_conflict_score: float = 0.0
    citation_gap: float = 0.0
    self_consistency_score: float | None = None
    online_jsd: float | None = None
    attention_leak_levels: tuple[float, ...] = ()
    consensus_cluster_sizes: tuple[int, ...] = ()
    consensus_sample_count: int = 0
    layer_weight_kappa: float = 2.0
    causal_conflicts: int = 0
    evidence_mismatches: int = 0
    prediction_entropy: float = 0.0
    covariance_logdet: float = 0.0
    gradient_proxy: float = 0.0
    stability_oscillation: float = 0.0
    baseline_covariance_det: float | None = None
    current_covariance_det: float | None = None
    covariance_dimension: int = 1
    vocab_size: int = 32000
    stability_gamma1: float | None = None
    stability_gamma2: float | None = None
    stability_label: int | None = None
    external_event_rate: float = 0.0
    tool_callback_rate: float = 0.0
    document_update_rate: float = 0.0
    interrupt_rate: float = 0.0
    queue_delay: float = 0.0
    inference_delay: float = 0.0
    clock_skew: float = 0.0
    timeout_risk: float = 0.0
    recall_hit_rate: float = 0.0
    memory_commit_rate: float = 0.0
    memory_stability: float = 0.0
    duplication_rate: float = 0.0
    tau_true: float | None = None
    tau_alpha_override: float | None = None
    tau_alpha_error_bound: float | None = None
    tau_nli_tolerance_threshold: float | None = None
    nli_sigma: float | None = None
    rollback_depth_tokens: int = 0
    token_kv_bytes: float = 0.0
    memory_bandwidth: float = 0.0
    rollback_overhead: float = 1.0
    rollback_detect_time: float = 0.0
    rollback_evict_time: float = 0.0
    rollback_recompute_time: float = 0.0
    leak_gradient_norm: float = 0.0
    pressure_mass: float = 1.0
    pressure_delta_max: float = 1.0
    epsilon_safe: float = 0.05


@dataclass(frozen=True)
class StabilityCalibrationPoint:
    entropy_norm: float
    geom_proxy: float
    out_of_bounds_label: int


@dataclass(frozen=True)
class TauCalibrationPoint:
    tau_proxy_v2: float
    fisher_rao_delta: float
    tau_true: float


@dataclass(frozen=True)
class AxisAssessment:
    axis: str
    value: float
    defect: int
    threshold: int
    acceptable: bool
    signals: dict[str, float | int | None] = field(default_factory=dict)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SixAxisAssessment:
    axes: dict[str, AxisAssessment]
    commit_domain: bool
    ranking: tuple[int, int, int, int, int, int]
    hot_path_metrics: dict[str, float] = field(default_factory=dict)
    cold_path_metrics: dict[str, float] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SixAxisSnapshot:
    snapshot_id: str
    request_id: str
    event_id: str
    timestamp: float
    assessment: SixAxisAssessment
    control_history: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json_ready(self) -> dict[str, Any]:
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SixAxisSnapshot:
        axes = {
            axis: AxisAssessment(**axis_payload)
            for axis, axis_payload in data["assessment"]["axes"].items()
        }
        assessment = SixAxisAssessment(
            axes=axes,
            commit_domain=bool(data["assessment"]["commit_domain"]),
            ranking=tuple(data["assessment"]["ranking"]),
            hot_path_metrics=dict(data["assessment"].get("hot_path_metrics", {})),
            cold_path_metrics=dict(data["assessment"].get("cold_path_metrics", {})),
            notes=list(data["assessment"].get("notes", [])),
        )
        return cls(
            snapshot_id=str(data["snapshot_id"]),
            request_id=str(data["request_id"]),
            event_id=str(data["event_id"]),
            timestamp=float(data["timestamp"]),
            assessment=assessment,
            control_history=list(data.get("control_history", [])),
            meta=dict(data.get("meta", {})),
        )


def build_layer_weights(layer_count: int, kappa: float = 2.0) -> list[float]:
    if layer_count <= 0:
        return []
    raw = [exp(kappa * (index + 1) / layer_count) for index in range(layer_count)]
    total = sum(raw)
    return [value / total for value in raw]


def weighted_attention_leak(leak_levels: tuple[float, ...], kappa: float = 2.0) -> float:
    if not leak_levels:
        return 0.0
    weights = build_layer_weights(len(leak_levels), kappa)
    return sum(weight * leak for weight, leak in zip(weights, leak_levels))


def consensus_score_from_clusters(
    cluster_sizes: tuple[int, ...],
    total_samples: int | None = None,
) -> float:
    if not cluster_sizes:
        return 0.0
    total = total_samples or sum(cluster_sizes)
    if total <= 0:
        return 0.0
    return max(cluster_sizes) / total


def normalized_entropy(entropy: float, vocab_size: int) -> float:
    if vocab_size <= 1:
        return _clamp01(entropy)
    return _clamp01(entropy / max(log(vocab_size), 1e-9))


def relative_state_variation(
    current_det: float | None,
    baseline_det: float | None,
    dimension: int,
) -> float:
    if current_det is None or baseline_det is None or current_det <= 0.0 or baseline_det <= 0.0:
        return 0.0
    dim = max(dimension, 1)
    return (1.0 / dim) * log(current_det / baseline_det)


def calibrate_stability_gamma(
    points: list[StabilityCalibrationPoint],
    grid_size: int = 101,
) -> tuple[float, float]:
    if not points:
        return (0.5, 0.5)

    best_gamma = 0.5
    best_loss = float("-inf")
    steps = max(grid_size, 2)
    for index in range(steps):
        gamma1 = index / (steps - 1)
        gamma2 = 1.0 - gamma1
        loss = 0.0
        for point in points:
            prediction = max(
                min(gamma1 * point.entropy_norm + gamma2 * _sigmoid(point.geom_proxy), 1.0 - 1e-9),
                1e-9,
            )
            loss += point.out_of_bounds_label * log(prediction) + (1 - point.out_of_bounds_label) * log(1 - prediction)
        if loss > best_loss:
            best_loss = loss
            best_gamma = gamma1
    return (best_gamma, 1.0 - best_gamma)


def solve_tau_alpha_star(points: list[TauCalibrationPoint], fallback_alpha: float = 0.65) -> float:
    if not points:
        return _clamp01(fallback_alpha)
    numerator = 0.0
    denominator = 0.0
    for point in points:
        fr_component = _sigmoid(point.fisher_rao_delta)
        delta = point.tau_proxy_v2 - fr_component
        numerator += (point.tau_true - fr_component) * delta
        denominator += delta * delta
    if denominator <= 1e-12:
        return _clamp01(fallback_alpha)
    return _clamp01(numerator / denominator)


def tau_alpha_error_bound(points: list[TauCalibrationPoint], sigma_nli: float) -> float:
    if not points:
        return 0.0
    denominator = sum((point.tau_proxy_v2 - _sigmoid(point.fisher_rao_delta)) ** 2 for point in points)
    if denominator <= 1e-12:
        return float("inf")
    return (2.0 * sigma_nli) / sqrt(denominator)


def tau_nli_tolerance_threshold(points: list[TauCalibrationPoint], eta_tol: float = 0.05) -> float:
    if not points:
        return 0.0
    deltas = [point.tau_proxy_v2 - _sigmoid(point.fisher_rao_delta) for point in points]
    mean_delta = sum(deltas) / len(deltas)
    variance = sum((delta - mean_delta) ** 2 for delta in deltas) / len(deltas)
    return (eta_tol / 2.0) * sqrt(len(deltas) * variance)


def causal_mass(
    rollback_depth_tokens: int,
    token_kv_bytes: float,
    memory_bandwidth: float,
    overhead: float = 1.0,
) -> float:
    if rollback_depth_tokens <= 0 or token_kv_bytes <= 0.0 or memory_bandwidth <= 0.0:
        return 0.0
    return overhead * ((rollback_depth_tokens * token_kv_bytes) / memory_bandwidth)


def rollback_rate(
    rollback_depth_tokens: int,
    detect_time: float,
    evict_time: float,
    recompute_time: float,
) -> float:
    total_time = detect_time + evict_time + recompute_time
    if rollback_depth_tokens <= 0 or total_time <= 0.0:
        return 0.0
    return rollback_depth_tokens / total_time


def beta_c_upper_bound(mass_c: float, lambda_rollback: float, leak_gradient_norm: float) -> float | None:
    if mass_c <= 0.0 or lambda_rollback <= 0.0 or leak_gradient_norm <= 0.0:
        return None
    return (mass_c * (lambda_rollback**2)) / leak_gradient_norm


def beta_s_value(
    pressure_mass: float,
    pressure_delta_max: float,
    kappa_s: float,
    s_current: float,
    epsilon_safe: float,
) -> float | None:
    numerator = 2.0 * pressure_mass
    denominator = (pressure_delta_max**2) * log((kappa_s - s_current) / max(epsilon_safe, 1e-9))
    if pressure_mass <= 0.0 or pressure_delta_max <= 0.0 or kappa_s <= s_current or denominator <= 0.0:
        return None
    return numerator / denominator


def estimate_tau_proxy_v2(telemetry: SixAxisTelemetry, weights: SixAxisWeights | None = None) -> float:
    w = weights or SixAxisWeights()
    raw = (
        w.tau_plan_weight * telemetry.plan_progress
        + w.tau_uncertainty_weight * telemetry.uncertainty_drop
        - w.tau_drift_weight * telemetry.answer_drift
        - w.tau_hidden_weight * telemetry.hidden_state_delta
    )
    return _sigmoid(raw)


def estimate_tau_hybrid_v1_5(
    telemetry: SixAxisTelemetry,
    weights: SixAxisWeights | None = None,
) -> float:
    w = weights or SixAxisWeights()
    proxy = estimate_tau_proxy_v2(telemetry, w)
    alpha = telemetry.tau_alpha_override if telemetry.tau_alpha_override is not None else w.tau_alpha
    if telemetry.fisher_rao_delta is None:
        return proxy
    fr_component = _sigmoid(telemetry.fisher_rao_delta)
    return _clamp01(alpha * proxy + (1.0 - alpha) * fr_component)


def _causal_assessment(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds,
    weights: SixAxisWeights,
) -> AxisAssessment:
    leak_score = (
        weighted_attention_leak(telemetry.attention_leak_levels, telemetry.layer_weight_kappa or weights.causal_layer_kappa)
        if telemetry.attention_leak_levels
        else telemetry.future_leak_score
    )
    consensus_score = (
        consensus_score_from_clusters(telemetry.consensus_cluster_sizes, telemetry.consensus_sample_count)
        if telemetry.consensus_cluster_sizes
        else telemetry.self_consistency_score
    )
    self_consistency_gap = 0.0
    if consensus_score is not None:
        self_consistency_gap = 1.0 - _clamp01(consensus_score)

    divergence_guard = max(
        telemetry.nli_conflict_score,
        self_consistency_gap,
        _clamp01(telemetry.online_jsd or 0.0),
    )
    mass_c = causal_mass(
        telemetry.rollback_depth_tokens,
        telemetry.token_kv_bytes,
        telemetry.memory_bandwidth,
        telemetry.rollback_overhead,
    )
    lambda_rollback = rollback_rate(
        telemetry.rollback_depth_tokens,
        telemetry.rollback_detect_time,
        telemetry.rollback_evict_time,
        telemetry.rollback_recompute_time,
    )
    beta_c = beta_c_upper_bound(mass_c, lambda_rollback, telemetry.leak_gradient_norm)
    value = _clamp01(
        weights.leak_weight * leak_score
        + weights.conflict_weight * divergence_guard
        + weights.citation_weight * telemetry.citation_gap
    )
    defect = (
        telemetry.causal_conflicts
        + telemetry.evidence_mismatches
        + ceil(value / max(thresholds.epsilon_C, 1e-9))
    )
    if beta_c is not None and beta_c < 0.05:
        defect += 1
    return AxisAssessment(
        axis="C",
        value=value,
        defect=defect,
        threshold=thresholds.kappa_C,
        acceptable=defect <= thresholds.kappa_C,
        signals={
            "future_leak_score": leak_score,
            "nli_conflict_score": telemetry.nli_conflict_score,
            "self_consistency_gap": self_consistency_gap,
            "self_consistency_score": consensus_score,
            "online_jsd": telemetry.online_jsd,
            "citation_gap": telemetry.citation_gap,
            "causal_conflicts": telemetry.causal_conflicts,
            "evidence_mismatches": telemetry.evidence_mismatches,
            "beta_c_upper_bound": beta_c,
            "rollback_rate": lambda_rollback,
            "causal_mass": mass_c,
        },
        note="Combines leakage, conflict floor, and citation mismatch into the causal defect budget.",
    )


def _stability_assessment(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds,
    weights: SixAxisWeights,
) -> AxisAssessment:
    entropy_norm = normalized_entropy(telemetry.prediction_entropy, telemetry.vocab_size)
    geom_proxy = (
        relative_state_variation(
            telemetry.current_covariance_det,
            telemetry.baseline_covariance_det,
            telemetry.covariance_dimension,
        )
        if telemetry.current_covariance_det is not None and telemetry.baseline_covariance_det is not None
        else telemetry.covariance_logdet
    )
    gamma1 = telemetry.stability_gamma1 if telemetry.stability_gamma1 is not None else weights.stability_entropy_weight
    gamma1 = _clamp01(gamma1)
    gamma2 = telemetry.stability_gamma2 if telemetry.stability_gamma2 is not None else weights.stability_geom_weight
    gamma2 = _clamp01(gamma2)
    weight_total = gamma1 + gamma2
    if weight_total <= 0.0:
        gamma1, gamma2 = 0.5, 0.5
    else:
        gamma1 /= weight_total
        gamma2 /= weight_total
    value = _clamp01(gamma1 * entropy_norm + gamma2 * _sigmoid(geom_proxy))
    distance = _interval_distance(value, thresholds.stability_interval)
    defect = ceil(distance / max(thresholds.epsilon_S, 1e-9))
    beta_s = beta_s_value(
        telemetry.pressure_mass,
        telemetry.pressure_delta_max,
        thresholds.stability_interval[1] + thresholds.safe_stability_margin,
        value,
        telemetry.epsilon_safe,
    )
    return AxisAssessment(
        axis="S",
        value=value,
        defect=defect,
        threshold=thresholds.kappa_S,
        acceptable=defect <= thresholds.kappa_S,
        signals={
            "prediction_entropy": telemetry.prediction_entropy,
            "entropy_norm": entropy_norm,
            "geom_proxy": geom_proxy,
            "covariance_logdet": telemetry.covariance_logdet,
            "gradient_proxy": telemetry.gradient_proxy,
            "stability_oscillation": telemetry.stability_oscillation,
            "gamma1": gamma1,
            "gamma2": gamma2,
            "beta_s": beta_s,
        },
        note="Uses entropy and covariance-style proxies to estimate divergence from the stable interval.",
    )


def _external_assessment(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds,
) -> AxisAssessment:
    value = _clamp01(
        (
            telemetry.external_event_rate
            + telemetry.tool_callback_rate
            + telemetry.document_update_rate
            + telemetry.interrupt_rate
        )
        / 4.0
    )
    defect = ceil(value / max(thresholds.epsilon_X, 1e-9))
    return AxisAssessment(
        axis="X",
        value=value,
        defect=defect,
        threshold=thresholds.kappa_X,
        acceptable=defect <= thresholds.kappa_X,
        signals={
            "external_event_rate": telemetry.external_event_rate,
            "tool_callback_rate": telemetry.tool_callback_rate,
            "document_update_rate": telemetry.document_update_rate,
            "interrupt_rate": telemetry.interrupt_rate,
        },
        note="Tracks exogenous pressure entering the dialogue loop from tools and environment updates.",
    )


def _pressure_assessment(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds,
) -> AxisAssessment:
    value = _clamp01(
        tanh(
            sqrt(
                telemetry.queue_delay**2
                + telemetry.inference_delay**2
                + telemetry.clock_skew**2
                + telemetry.timeout_risk**2
            )
        )
    )
    defect = ceil(value / max(thresholds.epsilon_P, 1e-9))
    return AxisAssessment(
        axis="P",
        value=value,
        defect=defect,
        threshold=thresholds.kappa_P,
        acceptable=defect <= thresholds.kappa_P,
        signals={
            "queue_delay": telemetry.queue_delay,
            "inference_delay": telemetry.inference_delay,
            "clock_skew": telemetry.clock_skew,
            "timeout_risk": telemetry.timeout_risk,
        },
        note="Compresses queueing and timeout stress into a single physical-pressure defect.",
    )


def _tau_assessment(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds,
    weights: SixAxisWeights,
) -> AxisAssessment:
    value = estimate_tau_hybrid_v1_5(telemetry, weights)
    defect = max(
        0,
        int(telemetry.remaining_subgoals + round(weights.tau_stall_penalty * telemetry.stall_windows)),
    )
    if (
        telemetry.tau_alpha_error_bound is not None
        and telemetry.tau_nli_tolerance_threshold is not None
        and telemetry.tau_alpha_error_bound > telemetry.tau_nli_tolerance_threshold
    ):
        defect += 1
    return AxisAssessment(
        axis="tau",
        value=value,
        defect=defect,
        threshold=thresholds.kappa_tau,
        acceptable=defect <= thresholds.kappa_tau,
        signals={
            "remaining_subgoals": telemetry.remaining_subgoals,
            "stall_windows": telemetry.stall_windows,
            "tau_proxy_v2": estimate_tau_proxy_v2(telemetry, weights),
            "fisher_rao_delta": telemetry.fisher_rao_delta,
            "tau_true": telemetry.tau_true,
            "tau_alpha": telemetry.tau_alpha_override if telemetry.tau_alpha_override is not None else weights.tau_alpha,
            "tau_alpha_error_bound": telemetry.tau_alpha_error_bound,
            "tau_nli_tolerance_threshold": telemetry.tau_nli_tolerance_threshold,
        },
        note="Encodes T-progress defect as unfinished goals plus penalized stall windows.",
    )


def _memory_state(telemetry: SixAxisTelemetry, thresholds: SixAxisThresholds) -> int:
    if telemetry.memory_commit_rate < thresholds.memory_commit_floor:
        return 0
    if (
        telemetry.recall_hit_rate >= thresholds.memory_commit_floor
        and telemetry.memory_stability >= thresholds.memory_commit_floor
    ):
        return 3
    return 2


def _memory_assessment(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds,
) -> AxisAssessment:
    value = _clamp01(
        (
            telemetry.recall_hit_rate
            + telemetry.memory_commit_rate
            + telemetry.memory_stability
            - telemetry.duplication_rate
        )
        / 3.0
    )
    defect = ceil(max(0.0, thresholds.memory_commit_floor - value) / max(thresholds.epsilon_M, 1e-9))
    memory_state = _memory_state(telemetry, thresholds)
    if telemetry.duplication_rate > 0.25:
        defect += 1
    return AxisAssessment(
        axis="M",
        value=value,
        defect=defect,
        threshold=thresholds.kappa_M,
        acceptable=defect <= thresholds.kappa_M,
        signals={
            "recall_hit_rate": telemetry.recall_hit_rate,
            "memory_commit_rate": telemetry.memory_commit_rate,
            "memory_stability": telemetry.memory_stability,
            "duplication_rate": telemetry.duplication_rate,
            "memory_state": memory_state,
        },
        note="Models the transient/commit/recall ladder with an explicit memory state and duplication penalty.",
    )


def evaluate_six_axes(
    telemetry: SixAxisTelemetry,
    thresholds: SixAxisThresholds | None = None,
    weights: SixAxisWeights | None = None,
) -> SixAxisAssessment:
    active_thresholds = thresholds or SixAxisThresholds()
    active_weights = weights or SixAxisWeights()

    axis_tau = _tau_assessment(telemetry, active_thresholds, active_weights)
    axis_c = _causal_assessment(telemetry, active_thresholds, active_weights)
    axis_m = _memory_assessment(telemetry, active_thresholds)
    axis_s = _stability_assessment(telemetry, active_thresholds, active_weights)
    axis_x = _external_assessment(telemetry, active_thresholds)
    axis_p = _pressure_assessment(telemetry, active_thresholds)

    axes = {
        "tau": axis_tau,
        "C": axis_c,
        "M": axis_m,
        "S": axis_s,
        "X": axis_x,
        "P": axis_p,
    }
    ranking = tuple(axes[axis].defect for axis in AXIS_ORDER)
    notes = [f"{axis} defect exceeds threshold" for axis, result in axes.items() if not result.acceptable]
    consensus_score = (
        consensus_score_from_clusters(telemetry.consensus_cluster_sizes, telemetry.consensus_sample_count)
        if telemetry.consensus_cluster_sizes
        else telemetry.self_consistency_score
    )
    lambda_rollback = rollback_rate(
        telemetry.rollback_depth_tokens,
        telemetry.rollback_detect_time,
        telemetry.rollback_evict_time,
        telemetry.rollback_recompute_time,
    )
    mass_c = causal_mass(
        telemetry.rollback_depth_tokens,
        telemetry.token_kv_bytes,
        telemetry.memory_bandwidth,
        telemetry.rollback_overhead,
    )
    return SixAxisAssessment(
        axes=axes,
        commit_domain=all(result.acceptable for result in axes.values()),
        ranking=ranking,
        hot_path_metrics={
            "tau_proxy_v2": estimate_tau_proxy_v2(telemetry, active_weights),
            "tau_hybrid_v1_5": axis_tau.value,
            "online_jsd": _clamp01(telemetry.online_jsd or 0.0),
            "prediction_entropy": telemetry.prediction_entropy,
            "pressure_value": axis_p.value,
            "rollback_rate": lambda_rollback,
            "causal_mass": mass_c,
        },
        cold_path_metrics={
            "tau_true": telemetry.tau_true or 0.0,
            "self_consistency_score": _clamp01(consensus_score or 0.0),
            "nli_conflict_score": _clamp01(telemetry.nli_conflict_score),
            "nli_sigma": telemetry.nli_sigma or 0.0,
            "fisher_rao_delta": telemetry.fisher_rao_delta or 0.0,
            "citation_gap": telemetry.citation_gap,
        },
        notes=notes,
    )


def legal_progress(
    previous: SixAxisAssessment,
    current: SixAxisAssessment,
) -> bool:
    if not previous.commit_domain or not current.commit_domain:
        return False
    return current.ranking < previous.ranking
