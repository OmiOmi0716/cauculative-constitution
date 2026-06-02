from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields, is_dataclass
from math import acos, exp, log, sqrt
from typing import Any, Mapping

from .models import DialogueEvent
from .six_axes import SixAxisTelemetry, consensus_score_from_clusters


@dataclass(frozen=True)
class VLLMHotPathSample:
    request_id: str = ""
    event_id: str = ""
    timestamp: float = 0.0
    token_index: int = 0
    generated_tokens: int = 0
    target_tokens: int = 0
    topk_probs: tuple[float, ...] = ()
    baseline_topk_probs: tuple[float, ...] = ()
    prediction_entropy: float | None = None
    plan_progress: float | None = None
    uncertainty_drop: float = 0.0
    answer_drift: float = 0.0
    hidden_state_delta: float = 0.0
    fisher_rao_delta: float | None = None
    attention_leak_levels: tuple[float, ...] = ()
    current_covariance_det: float | None = None
    baseline_covariance_det: float | None = None
    covariance_dimension: int = 1
    queue_delay: float = 0.0
    inference_delay: float = 0.0
    clock_skew: float = 0.0
    timeout_risk: float = 0.0


@dataclass(frozen=True)
class VLLMColdPathResult:
    request_id: str = ""
    event_id: str = ""
    tau_true: float | None = None
    nli_conflict_score: float = 0.0
    nli_sigma: float | None = None
    citation_gap: float = 0.0
    consensus_cluster_sizes: tuple[int, ...] = ()
    consensus_sample_count: int = 0
    self_consistency_score: float | None = None
    atomic_facts_total: int = 0
    atomic_facts_supported: int = 0


@dataclass(frozen=True)
class VLLMRollbackTrace:
    request_id: str = ""
    event_id: str = ""
    rollback_depth_tokens: int = 0
    token_kv_bytes: float = 0.0
    memory_bandwidth: float = 0.0
    rollback_overhead: float = 1.0
    rollback_detect_time: float = 0.0
    rollback_evict_time: float = 0.0
    rollback_recompute_time: float = 0.0
    leak_gradient_norm: float = 0.0


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _json_value(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def _payload_dict(payload: Any) -> dict[str, Any]:
    payload = _json_value(payload)
    if payload is None:
        return {}
    if is_dataclass(payload):
        return asdict(payload)
    if isinstance(payload, Mapping):
        return dict(payload)
    if hasattr(payload, "__dict__"):
        return dict(vars(payload))
    return {}


def _pick(payload: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return default


def _as_float(value: Any, default: float | None = None) -> float | None:
    value = _json_value(value)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int | None = None) -> int | None:
    value = _json_value(value)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return default


def _float_sequence(value: Any) -> tuple[float, ...]:
    value = _json_value(value)
    if value is None:
        return tuple()
    if isinstance(value, Mapping):
        for key in ("probs", "probabilities", "values", "leaks", "attention"):
            if key in value:
                return _float_sequence(value[key])
        items = value.values()
    elif isinstance(value, str):
        items = [part.strip() for part in value.split(",") if part.strip()]
    else:
        items = value if isinstance(value, (list, tuple)) else [value]

    numbers: list[float] = []
    for item in items:
        item = _json_value(item)
        if isinstance(item, Mapping):
            item = _pick(item, "prob", "p", "value", "leak", "score", "logprob")
        try:
            numbers.append(float(item))
        except (TypeError, ValueError):
            continue
    return tuple(numbers)


def _int_sequence(value: Any) -> tuple[int, ...]:
    return tuple(int(round(number)) for number in _float_sequence(value))


def _probabilities_from_payload(
    payload: Mapping[str, Any],
    *keys: str,
    logprob_keys: tuple[str, ...] = (),
) -> tuple[float, ...]:
    probs = _float_sequence(_pick(payload, *keys))
    if probs:
        return probs

    logprobs = _float_sequence(_pick(payload, *logprob_keys))
    if not logprobs:
        return tuple()
    return tuple(exp(value) for value in logprobs)


def _normalize_distribution(values: tuple[float, ...]) -> tuple[float, ...]:
    cleaned = tuple(max(0.0, value) for value in values)
    total = sum(cleaned)
    if total <= 0.0:
        return tuple()
    return tuple(value / total for value in cleaned)


def distribution_entropy(probabilities: tuple[float, ...]) -> float:
    probs = _normalize_distribution(probabilities)
    return -sum(prob * log(max(prob, 1e-12)) for prob in probs)


def jensen_shannon_divergence(
    left: tuple[float, ...],
    right: tuple[float, ...],
    normalize: bool = True,
) -> float:
    left_probs = _normalize_distribution(left)
    right_probs = _normalize_distribution(right)
    if not left_probs or not right_probs:
        return 0.0

    size = max(len(left_probs), len(right_probs))
    left_padded = left_probs + (0.0,) * (size - len(left_probs))
    right_padded = right_probs + (0.0,) * (size - len(right_probs))
    midpoint = tuple((l + r) / 2.0 for l, r in zip(left_padded, right_padded))

    def kl_divergence(source: tuple[float, ...], target: tuple[float, ...]) -> float:
        return sum(prob * log(max(prob, 1e-12) / max(ref, 1e-12)) for prob, ref in zip(source, target) if prob > 0.0)

    jsd = 0.5 * kl_divergence(left_padded, midpoint) + 0.5 * kl_divergence(right_padded, midpoint)
    if normalize:
        return _clamp01(jsd / log(2.0))
    return jsd


def fisher_rao_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    left_probs = _normalize_distribution(left)
    right_probs = _normalize_distribution(right)
    if not left_probs or not right_probs:
        return 0.0
    size = max(len(left_probs), len(right_probs))
    left_padded = left_probs + (0.0,) * (size - len(left_probs))
    right_padded = right_probs + (0.0,) * (size - len(right_probs))
    affinity = sum(sqrt(l * r) for l, r in zip(left_padded, right_padded))
    return 2.0 * acos(max(0.0, min(1.0, affinity)))


def _seconds(payload: Mapping[str, Any], *keys: str) -> float:
    for key in keys:
        value = _as_float(_pick(payload, key))
        if value is None:
            continue
        if key.endswith("_ms") or key.endswith("ms"):
            return value / 1000.0
        return value
    return 0.0


def _token_kv_bytes(payload: Mapping[str, Any]) -> float:
    explicit = _as_float(_pick(payload, "token_kv_bytes", "kv_bytes_per_token"))
    if explicit is not None:
        return explicit

    block_bytes = _as_float(_pick(payload, "kv_block_size_bytes", "kv_cache_block_bytes"))
    tokens_per_block = _as_float(_pick(payload, "tokens_per_block", "kv_block_tokens", "block_size"))
    if block_bytes is not None and tokens_per_block and tokens_per_block > 0.0:
        return block_bytes / tokens_per_block

    layer_count = _as_float(_pick(payload, "num_layers", "n_layers"))
    kv_heads = _as_float(_pick(payload, "num_kv_heads", "n_kv_heads"))
    head_size = _as_float(_pick(payload, "head_size", "kv_head_size"))
    dtype_bytes = _as_float(_pick(payload, "dtype_bytes", "kv_dtype_bytes"), 2.0)
    if layer_count and kv_heads and head_size and dtype_bytes:
        return layer_count * kv_heads * head_size * 2.0 * dtype_bytes
    return 0.0


def _memory_bandwidth(payload: Mapping[str, Any]) -> float:
    explicit = _as_float(
        _pick(payload, "memory_bandwidth", "memory_bandwidth_bytes_per_s", "memory_bandwidth_bps")
    )
    if explicit is not None:
        return explicit
    gb_s = _as_float(_pick(payload, "memory_bandwidth_gb_s", "memory_bandwidth_gbps"))
    if gb_s is not None:
        return gb_s * 1_000_000_000.0
    return 0.0


def _ratio(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return _clamp01(float(numerator) / float(denominator))


def _fact_coverage(cold: Mapping[str, Any]) -> float | None:
    supported = _as_int(_pick(cold, "atomic_facts_supported", "supported_facts", "facts_supported"))
    total = _as_int(_pick(cold, "atomic_facts_total", "total_facts", "facts_total"))
    return _ratio(supported, total)


def telemetry_from_vllm_payloads(
    hot_path: Any | None = None,
    cold_path: Any | None = None,
    rollback: Any | None = None,
) -> SixAxisTelemetry:
    hot = _payload_dict(hot_path)
    cold = _payload_dict(cold_path)
    rb = _payload_dict(rollback)
    combined = {**hot, **cold, **rb}

    topk_probs = _probabilities_from_payload(
        hot,
        "topk_probs",
        "top_k_probs",
        "top_p_probs",
        "probabilities",
        logprob_keys=("topk_logprobs", "top_k_logprobs", "top_logprobs", "logprobs"),
    )
    baseline_probs = _probabilities_from_payload(
        hot,
        "baseline_topk_probs",
        "baseline_top_k_probs",
        "coherence_baseline_probs",
        "offline_baseline_probs",
        logprob_keys=("baseline_topk_logprobs", "baseline_top_k_logprobs", "baseline_logprobs"),
    )
    online_jsd = _as_float(_pick(hot, "online_jsd", "jsd", "logit_jsd"))
    if online_jsd is None and topk_probs and baseline_probs:
        online_jsd = jensen_shannon_divergence(topk_probs, baseline_probs)

    entropy = _as_float(_pick(hot, "prediction_entropy", "token_entropy", "entropy"))
    if entropy is None and topk_probs:
        entropy = distribution_entropy(topk_probs)

    fisher = _as_float(_pick(hot, "fisher_rao_delta", "fisher_rao_distance"))
    if fisher is None and topk_probs and baseline_probs:
        fisher = fisher_rao_distance(topk_probs, baseline_probs)

    generated = _as_int(_pick(hot, "generated_tokens", "output_tokens", "token_index"))
    target = _as_int(_pick(hot, "target_tokens", "expected_tokens", "max_target_tokens"))
    plan_progress = _as_float(_pick(hot, "plan_progress", "plan_completion", "progress"))
    if plan_progress is None:
        plan_progress = _ratio(generated, target) or 0.0

    remaining_subgoals = _as_int(_pick(hot, "remaining_subgoals", "open_subgoals"), 0) or 0
    if remaining_subgoals == 0 and generated is not None and target is not None and generated < target:
        remaining_subgoals = 1

    uncertainty_drop = _as_float(_pick(hot, "uncertainty_drop"), 0.0) or 0.0
    previous_entropy = _as_float(_pick(hot, "previous_entropy", "prev_entropy"))
    if uncertainty_drop == 0.0 and previous_entropy is not None and entropy is not None:
        uncertainty_drop = max(0.0, previous_entropy - entropy)

    cluster_sizes = _int_sequence(_pick(cold, "consensus_cluster_sizes", "sc_cluster_sizes", "clusters"))
    consensus_sample_count = _as_int(
        _pick(cold, "consensus_sample_count", "sc_sample_count", "sample_count", "k_samples"),
        0,
    ) or 0
    self_consistency = _as_float(_pick(cold, "self_consistency_score", "sc_score", "SC(q)", "scq"))
    if self_consistency is None and cluster_sizes:
        self_consistency = consensus_score_from_clusters(cluster_sizes, consensus_sample_count or None)

    fact_coverage = _fact_coverage(cold)
    tau_true = _as_float(_pick(cold, "tau_true", "tau_gold", "nli_tau_true"))
    if tau_true is None:
        tau_true = fact_coverage

    citation_gap = _as_float(_pick(cold, "citation_gap", "evidence_gap"))
    if citation_gap is None and fact_coverage is not None:
        citation_gap = 1.0 - fact_coverage

    nli_conflict = _as_float(
        _pick(cold, "nli_conflict_score", "nli_contradiction_score", "contradiction_prob", "contradiction_score"),
        0.0,
    ) or 0.0
    entailment = _as_float(_pick(cold, "nli_entailment_score", "entailment_prob"))
    if nli_conflict == 0.0 and entailment is not None:
        nli_conflict = max(0.0, 1.0 - entailment)

    attention_leaks = _float_sequence(
        _pick(hot, "attention_leak_levels", "attention_leak_by_layer", "causal_attention_leak_by_layer")
    )
    future_leak = _as_float(_pick(hot, "future_leak_score", "future_attention_leak"))
    if future_leak is None and attention_leaks:
        future_leak = max(attention_leaks)

    depth_tokens = _as_int(_pick(combined, "rollback_depth_tokens", "rollback_tokens", "evicted_tokens"), 0) or 0

    return SixAxisTelemetry(
        remaining_subgoals=remaining_subgoals,
        stall_windows=_as_int(_pick(hot, "stall_windows", "stall_count", "repeated_token_window"), 0) or 0,
        plan_progress=_clamp01(plan_progress),
        uncertainty_drop=max(0.0, uncertainty_drop),
        answer_drift=_as_float(_pick(hot, "answer_drift", "semantic_drift", "drift_score"), 0.0) or 0.0,
        hidden_state_delta=_as_float(
            _pick(hot, "hidden_state_delta", "hidden_step_delta", "hidden_delta_norm", "hidden_state_delta_norm"),
            0.0,
        )
        or 0.0,
        fisher_rao_delta=fisher,
        future_leak_score=_clamp01(future_leak or 0.0),
        nli_conflict_score=_clamp01(nli_conflict),
        citation_gap=_clamp01(citation_gap or 0.0),
        self_consistency_score=self_consistency,
        online_jsd=online_jsd,
        attention_leak_levels=attention_leaks,
        consensus_cluster_sizes=cluster_sizes,
        consensus_sample_count=consensus_sample_count,
        layer_weight_kappa=_as_float(_pick(hot, "layer_weight_kappa"), 2.0) or 2.0,
        causal_conflicts=_as_int(_pick(cold, "causal_conflicts", "nli_conflict_count"), 0) or 0,
        evidence_mismatches=_as_int(_pick(cold, "evidence_mismatches", "unsupported_fact_count"), 0) or 0,
        prediction_entropy=entropy or 0.0,
        covariance_logdet=_as_float(_pick(hot, "covariance_logdet", "hidden_covariance_logdet"), 0.0) or 0.0,
        gradient_proxy=_as_float(_pick(hot, "gradient_proxy", "gradient_norm"), 0.0) or 0.0,
        stability_oscillation=_as_float(_pick(hot, "stability_oscillation", "oscillation"), 0.0) or 0.0,
        baseline_covariance_det=_as_float(_pick(hot, "baseline_covariance_det", "baseline_hidden_cov_det")),
        current_covariance_det=_as_float(_pick(hot, "current_covariance_det", "hidden_cov_det")),
        covariance_dimension=_as_int(_pick(hot, "covariance_dimension", "hidden_dim"), 1) or 1,
        vocab_size=_as_int(_pick(hot, "vocab_size", "topk_size"), len(topk_probs) or 32000) or 32000,
        stability_label=_as_int(_pick(hot, "stability_label", "out_of_bounds_label")),
        external_event_rate=_as_float(_pick(hot, "external_event_rate"), 0.0) or 0.0,
        tool_callback_rate=_as_float(_pick(hot, "tool_callback_rate"), 0.0) or 0.0,
        document_update_rate=_as_float(_pick(hot, "document_update_rate"), 0.0) or 0.0,
        interrupt_rate=_as_float(_pick(hot, "interrupt_rate"), 0.0) or 0.0,
        queue_delay=_seconds(hot, "queue_delay", "queue_delay_s", "queue_delay_ms", "scheduler_queue_ms"),
        inference_delay=_seconds(hot, "inference_delay", "infer_delay", "inference_delay_s", "inference_delay_ms"),
        clock_skew=_seconds(hot, "clock_skew", "clock_skew_s", "clock_skew_ms"),
        timeout_risk=_as_float(_pick(hot, "timeout_risk"), 0.0) or 0.0,
        recall_hit_rate=_as_float(_pick(hot, "recall_hit_rate", "kv_cache_hit_rate"), 0.0) or 0.0,
        memory_commit_rate=_as_float(_pick(hot, "memory_commit_rate"), plan_progress) or 0.0,
        memory_stability=_as_float(_pick(hot, "memory_stability"), 0.0) or 0.0,
        duplication_rate=_as_float(_pick(hot, "duplication_rate", "duplicate_ngram_rate"), 0.0) or 0.0,
        tau_true=tau_true,
        nli_sigma=_as_float(_pick(cold, "nli_sigma", "nli_uncertainty_sigma")),
        rollback_depth_tokens=depth_tokens,
        token_kv_bytes=_token_kv_bytes(combined),
        memory_bandwidth=_memory_bandwidth(combined),
        rollback_overhead=_as_float(_pick(combined, "rollback_overhead"), 1.0) or 1.0,
        rollback_detect_time=_seconds(combined, "rollback_detect_time", "rollback_detect_s", "rollback_detect_ms"),
        rollback_evict_time=_seconds(combined, "rollback_evict_time", "rollback_evict_s", "rollback_evict_ms"),
        rollback_recompute_time=_seconds(
            combined,
            "rollback_recompute_time",
            "rollback_recompute_s",
            "rollback_recompute_ms",
        ),
        leak_gradient_norm=_as_float(_pick(combined, "leak_gradient_norm", "leak_grad_norm"), 0.0) or 0.0,
        pressure_mass=_as_float(_pick(combined, "pressure_mass"), 1.0) or 1.0,
        pressure_delta_max=_as_float(_pick(combined, "pressure_delta_max"), 1.0) or 1.0,
        epsilon_safe=_as_float(_pick(combined, "epsilon_safe"), 0.05) or 0.05,
    )


def _meta_string(value: Any) -> str:
    if isinstance(value, tuple):
        return json.dumps(list(value))
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


def runtime_meta_from_vllm_payloads(
    hot_path: Any | None = None,
    cold_path: Any | None = None,
    rollback: Any | None = None,
) -> dict[str, str]:
    telemetry = telemetry_from_vllm_payloads(hot_path, cold_path, rollback)
    defaults = SixAxisTelemetry()
    meta: dict[str, str] = {"runtime_source": "vllm_hooks"}
    for telemetry_field in fields(SixAxisTelemetry):
        name = telemetry_field.name
        value = getattr(telemetry, name)
        if value is None or value == getattr(defaults, name):
            continue
        meta[name] = _meta_string(value)
    return meta


def _prefixed_payload(meta: Mapping[str, Any], prefixes: tuple[str, ...]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key, value in meta.items():
        for prefix in prefixes:
            if key.startswith(prefix):
                stripped = key[len(prefix) :].lstrip("._")
                if stripped:
                    payload[stripped] = _json_value(value)
    return payload


def runtime_meta_from_event_meta(meta: Mapping[str, Any]) -> dict[str, str]:
    hot = _payload_dict(
        _pick(meta, "vllm_hot_path", "vllm_hot", "hot_path_runtime", "runtime_hot_path")
    )
    cold = _payload_dict(
        _pick(meta, "vllm_cold_path", "vllm_cold", "cold_path_runtime", "runtime_cold_path")
    )
    rollback = _payload_dict(
        _pick(meta, "vllm_rollback", "rollback_runtime", "runtime_rollback")
    )

    hot.update(_prefixed_payload(meta, ("vllm.hot.", "vllm_hot.", "vllm_hot_", "hot_path.")))
    cold.update(_prefixed_payload(meta, ("vllm.cold.", "vllm_cold.", "vllm_cold_", "cold_path.")))
    rollback.update(
        _prefixed_payload(meta, ("vllm.rollback.", "vllm_rollback.", "vllm_rollback_", "rollback."))
    )

    if not hot and not cold and not rollback:
        return {}
    return runtime_meta_from_vllm_payloads(hot, cold, rollback)


def event_with_vllm_runtime(
    event: DialogueEvent,
    hot_path: Any | None = None,
    cold_path: Any | None = None,
    rollback: Any | None = None,
) -> DialogueEvent:
    meta = dict(event.meta)
    meta.update(runtime_meta_from_vllm_payloads(hot_path, cold_path, rollback))
    return DialogueEvent(
        event_id=event.event_id,
        text=event.text,
        speaker=event.speaker,
        tool=event.tool,
        request_id=event.request_id,
        timestamp=event.timestamp,
        blocks=event.blocks,
        bcg_profile=event.bcg_profile,
        control=event.control,
        control_observation=event.control_observation,
        declared_move=event.declared_move,
        move_strength=event.move_strength,
        sensitive_context=event.sensitive_context,
        claimed_confidence=event.claimed_confidence,
        evidence_coverage=event.evidence_coverage,
        truth_distortion=event.truth_distortion,
        role_config=list(event.role_config),
        meta=meta,
    )
