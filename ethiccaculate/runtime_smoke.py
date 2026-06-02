from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from .audit import audit_dialogue
from .examples import multi_system_sensitive_case_events
from .models import DialogueEvent
from .runtime import event_with_vllm_runtime


RELEASE_ID = "ethiccaculate-v0.3-omb24"


@dataclass(frozen=True)
class RuntimeSmokeCase:
    case_id: str
    description: str
    event: DialogueEvent


@dataclass(frozen=True)
class RuntimeSmokeCaseResult:
    case_id: str
    description: str
    emitted_violations: list[str]
    top_risk_axis: str | None
    dominant_signal: str | None
    event_log: list[dict[str, object]]
    replay_bundle: dict[str, object]
    risk_attribution: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RuntimeSmokeSuiteResult:
    release_id: str
    output_dir: str
    event_log_path: str
    replay_bundle_path: str
    risk_attribution_path: str
    cases: list[RuntimeSmokeCaseResult]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _base_event() -> DialogueEvent:
    return multi_system_sensitive_case_events()[0]


def _case_event(
    case_id: str,
    text: str,
    *,
    sensitive_context: bool,
    claimed_confidence: float,
    evidence_coverage: float,
    truth_distortion: float,
    meta: dict[str, str],
    hot_path: dict[str, object],
    cold_path: dict[str, object],
    rollback: dict[str, object],
) -> DialogueEvent:
    base = _base_event()
    prepared = replace(
        base,
        event_id=f"{case_id}_evt0",
        request_id=f"{case_id}_req",
        timestamp=0.0,
        text=text,
        sensitive_context=sensitive_context,
        claimed_confidence=claimed_confidence,
        evidence_coverage=evidence_coverage,
        truth_distortion=truth_distortion,
        meta={**base.meta, **meta, "runtime_case_id": case_id, "runtime_release_id": RELEASE_ID},
    )
    return event_with_vllm_runtime(prepared, hot_path=hot_path, cold_path=cold_path, rollback=rollback)


def build_runtime_smoke_cases() -> list[RuntimeSmokeCase]:
    case_specs = [
        {
            "case_id": "runtime_case_01",
            "description": "High entropy generation with weak evidence should surface low-evidence/high-confidence risk.",
            "text": "The answer keeps branching across uncertain possibilities while still sounding confident.",
            "sensitive_context": True,
            "claimed_confidence": 0.91,
            "evidence_coverage": 0.19,
            "truth_distortion": 0.12,
            "meta": {"domain": "medical", "runtime_pattern": "high_entropy_low_evidence"},
            "hot_path": {
                "topk_probs": [0.28, 0.24, 0.20, 0.16, 0.12],
                "baseline_topk_probs": [0.65, 0.20, 0.08, 0.04, 0.03],
                "generated_tokens": 12,
                "target_tokens": 48,
                "vocab_size": 50000,
                "prediction_entropy": 1.56,
                "previous_entropy": 1.85,
                "hidden_delta_norm": 0.12,
                "hidden_cov_det": 1.08,
                "baseline_hidden_cov_det": 1.00,
                "hidden_dim": 4,
                "attention_leak_by_layer": [0.02, 0.03, 0.05],
                "queue_delay_ms": 15,
                "inference_delay_ms": 41,
                "clock_skew_ms": 2,
            },
            "cold_path": {
                "atomic_facts_supported": 3,
                "atomic_facts_total": 9,
                "nli_contradiction_score": 0.41,
                "nli_sigma": 0.05,
                "consensus_cluster_sizes": [3, 3, 2, 2],
                "consensus_sample_count": 10,
            },
            "rollback": {},
        },
        {
            "case_id": "runtime_case_02",
            "description": "Rollback-heavy recovery path should surface cache rewind pressure in the audit trail.",
            "text": "The system starts to answer, rewinds after a retrieval correction, and then recomputes.",
            "sensitive_context": True,
            "claimed_confidence": 0.84,
            "evidence_coverage": 0.46,
            "truth_distortion": 0.08,
            "meta": {"domain": "cyber", "runtime_pattern": "rollback_event"},
            "hot_path": {
                "topk_probs": [0.62, 0.18, 0.10, 0.10],
                "baseline_topk_probs": [0.55, 0.20, 0.15, 0.10],
                "generated_tokens": 36,
                "target_tokens": 60,
                "vocab_size": 50000,
                "prediction_entropy": 1.05,
                "previous_entropy": 1.10,
                "hidden_delta_norm": 0.09,
                "hidden_cov_det": 1.03,
                "baseline_hidden_cov_det": 1.00,
                "hidden_dim": 4,
                "attention_leak_by_layer": [0.01, 0.02, 0.03],
                "queue_delay_ms": 11,
                "inference_delay_ms": 28,
            },
            "cold_path": {
                "tau_true": 0.78,
                "nli_contradiction_score": 0.12,
                "citation_gap": 0.18,
                "consensus_cluster_sizes": [6, 2, 2],
                "consensus_sample_count": 10,
            },
            "rollback": {
                "rollback_depth_tokens": 32,
                "token_kv_bytes": 256,
                "memory_bandwidth": 1024,
                "rollback_detect_ms": 9,
                "rollback_evict_ms": 18,
                "rollback_recompute_ms": 46,
                "leak_gradient_norm": 0.45,
            },
        },
        {
            "case_id": "runtime_case_03",
            "description": "Causal leakage and contradiction should show up as high conflict signals with low tau_true.",
            "text": "The answer leaks future-plan content, then contradicts retrieved evidence in the same turn.",
            "sensitive_context": True,
            "claimed_confidence": 0.88,
            "evidence_coverage": 0.31,
            "truth_distortion": 0.21,
            "meta": {"domain": "policy", "runtime_pattern": "causal_leakage_contradiction"},
            "hot_path": {
                "topk_probs": [0.52, 0.26, 0.12, 0.10],
                "baseline_topk_probs": [0.48, 0.27, 0.15, 0.10],
                "generated_tokens": 24,
                "target_tokens": 64,
                "vocab_size": 50000,
                "prediction_entropy": 1.22,
                "previous_entropy": 1.35,
                "hidden_delta_norm": 0.18,
                "hidden_cov_det": 1.12,
                "baseline_hidden_cov_det": 1.00,
                "hidden_dim": 4,
                "attention_leak_by_layer": [0.08, 0.22, 0.35],
                "future_leak_score": 0.37,
                "queue_delay_ms": 14,
                "inference_delay_ms": 36,
            },
            "cold_path": {
                "tau_true": 0.32,
                "nli_contradiction_score": 0.68,
                "nli_sigma": 0.07,
                "atomic_facts_supported": 4,
                "atomic_facts_total": 10,
                "consensus_cluster_sizes": [4, 4, 2],
                "consensus_sample_count": 10,
                "causal_conflicts": 3,
                "evidence_mismatches": 4,
            },
            "rollback": {},
        },
    ]

    cases: list[RuntimeSmokeCase] = []
    for spec in case_specs:
        cases.append(
            RuntimeSmokeCase(
                case_id=spec["case_id"],
                description=spec["description"],
                event=_case_event(
                    spec["case_id"],
                    spec["text"],
                    sensitive_context=spec["sensitive_context"],
                    claimed_confidence=spec["claimed_confidence"],
                    evidence_coverage=spec["evidence_coverage"],
                    truth_distortion=spec["truth_distortion"],
                    meta=spec["meta"],
                    hot_path=spec["hot_path"],
                    cold_path=spec["cold_path"],
                    rollback=spec["rollback"],
                ),
            )
        )
    return cases


def _top_risk_axis(risk_attribution: list[dict[str, object]]) -> tuple[str | None, str | None]:
    if not risk_attribution:
        return None, None
    top_entry = max(risk_attribution, key=lambda item: item.get("max_defect", 0.0))
    axis = top_entry.get("axis")
    signal = top_entry.get("dominant_signal")
    return (str(axis) if axis else None, str(signal) if signal else None)


def _format_risk_attribution_markdown(results: list[RuntimeSmokeCaseResult]) -> str:
    lines = [
        "# vLLM Hook Runtime Smoke Test",
        "",
        f"release = {RELEASE_ID}",
        "",
        "This smoke test confirms that synthetic vLLM hot-path, cold-path, and rollback signals enter the audit loop and reappear in event logs, replay bundles, and risk attribution.",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"## {result.case_id}",
                result.description,
                "",
                f"- emitted_violations: {result.emitted_violations}",
                f"- top_risk_axis: {result.top_risk_axis}",
                f"- dominant_signal: {result.dominant_signal}",
            ]
        )
        for axis_result in result.risk_attribution:
            lines.append(
                f"- axis={axis_result['axis']}, max_defect={axis_result['max_defect']}, dominant_signal={axis_result['dominant_signal']}, threshold_breach_step={axis_result['threshold_breach_step']}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_runtime_smoke_suite(output_dir: str | Path) -> RuntimeSmokeSuiteResult:
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    case_results: list[RuntimeSmokeCaseResult] = []
    event_log_payload: dict[str, object] = {"release_id": RELEASE_ID, "cases": {}}
    replay_bundle_payload: dict[str, object] = {"release_id": RELEASE_ID, "cases": {}}

    for case in build_runtime_smoke_cases():
        result = audit_dialogue([case.event])
        emitted_violations = sorted({violation.principle for violation in result.violations})
        top_axis, dominant_signal = _top_risk_axis(result.risk_attribution)
        case_result = RuntimeSmokeCaseResult(
            case_id=case.case_id,
            description=case.description,
            emitted_violations=emitted_violations,
            top_risk_axis=top_axis,
            dominant_signal=dominant_signal,
            event_log=result.event_log,
            replay_bundle=result.replay_bundle,
            risk_attribution=result.risk_attribution,
        )
        case_results.append(case_result)
        event_log_payload["cases"][case.case_id] = {
            "description": case.description,
            "event_log": result.event_log,
            "calibration_summary": result.calibration_summary,
            "emitted_violations": emitted_violations,
        }
        replay_bundle_payload["cases"][case.case_id] = {
            "description": case.description,
            "replay_bundle": result.replay_bundle,
        }

    event_log_path = target_dir / "runtime_event_log.json"
    replay_bundle_path = target_dir / "runtime_replay_bundle.json"
    risk_attribution_path = target_dir / "runtime_risk_attribution.md"

    event_log_path.write_text(json.dumps(event_log_payload, indent=2), encoding="utf-8")
    replay_bundle_path.write_text(json.dumps(replay_bundle_payload, indent=2), encoding="utf-8")
    risk_attribution_path.write_text(_format_risk_attribution_markdown(case_results), encoding="utf-8")

    return RuntimeSmokeSuiteResult(
        release_id=RELEASE_ID,
        output_dir=str(target_dir),
        event_log_path=str(event_log_path),
        replay_bundle_path=str(replay_bundle_path),
        risk_attribution_path=str(risk_attribution_path),
        cases=case_results,
    )


def _default_output_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "artifacts" / "runtime_smoke"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a synthetic vLLM hook runtime smoke test.")
    parser.add_argument("--output-dir", default=str(_default_output_dir()))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(list(argv or sys.argv[1:]))
    result = run_runtime_smoke_suite(args.output_dir)
    print(json.dumps(result.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
