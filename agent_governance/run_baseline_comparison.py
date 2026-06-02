"""Compare sandbox agent governance against simpler baselines.

This comparison is local to agent_governance/. It is not frozen v0.3 evidence
and does not modify the main ethiccaculate scoring rules.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.anti_collusion import AgentJudgment, analyze_collusion_risk
from agent_governance.replay import build_replay_summary
from agent_governance.schemas import AgentTrace
from agent_governance.soul_profile import evaluate_soul_profile, load_soul_profile


ROOT = Path(__file__).resolve().parent
CASE_PATH = ROOT / "mini_benchmark_cases.json"
SOUL_PATH = ROOT / "SOUL.md"


@dataclass(frozen=True)
class VariantResult:
    name: str
    detected_signals: int
    total_signals: int
    text_visible_cases: int
    replayable_cases: int
    review_routed_cases: int

    @property
    def coverage(self) -> float:
        return self.detected_signals / max(1, self.total_signals)


def _load_cases() -> list[dict[str, Any]]:
    payload = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    return list(payload["cases"])


def _trace(case: dict[str, Any]) -> AgentTrace | None:
    if "trace" not in case:
        return None
    return AgentTrace.from_dict(case["trace"])


def _judgments(items: list[dict[str, Any]]) -> list[AgentJudgment]:
    return [
        AgentJudgment(
            agent_id=str(item["agent_id"]),
            target_event_id=str(item["target_event_id"]),
            phase=str(item["phase"]),
            verdict=str(item["verdict"]),
            confidence=float(item["confidence"]),
            evidence_event_ids=list(item.get("evidence_event_ids", [])),
            cited_agent_ids=list(item.get("cited_agent_ids", [])),
            rationale_summary=str(item.get("rationale_summary", "")),
            metadata=dict(item.get("metadata", {})),
        )
        for item in items
    ]


def _expected_signals(case: dict[str, Any]) -> list[str]:
    expected = dict(case.get("expected", {}))
    signals = ["trace_replay"]
    signals.extend(f"trace_flag:{item}" for item in expected.get("trace_flags", []))
    if expected.get("soul_review_required") is True:
        signals.append("soul_review_required")
    signals.extend(f"soul_axis:{item}" for item in expected.get("soul_threshold_axes", []))
    signals.extend(f"self_update_review:{item}" for item in expected.get("self_update_events_requiring_review", []))
    if expected.get("collusion_review_required") is True:
        signals.append("collusion_review_required")
    signals.extend(f"collusion_flag:{item}" for item in expected.get("collusion_flags", []))
    return signals


def _full_detected_signals(case: dict[str, Any], soul_profile: object) -> set[str]:
    detected: set[str] = set()
    trace = _trace(case)
    if trace is not None:
        replay = build_replay_summary(trace)
        if len(replay["steps"]) == len(trace.events):
            detected.add("trace_replay")
        trace_flags = set(replay["score"]["flags"])
        detected.update(f"trace_flag:{item}" for item in trace_flags)

        soul_report = evaluate_soul_profile(trace, soul_profile)
        if soul_report["review_required"]:
            detected.add("soul_review_required")
        detected.update(f"soul_axis:{item['axis']}" for item in soul_report["threshold_violations"])
        detected.update(f"self_update_review:{item}" for item in soul_report["self_update_events_requiring_review"])

    if "judgments" in case:
        collusion_report = analyze_collusion_risk(_judgments(case["judgments"]))
        if collusion_report.review_required:
            detected.add("collusion_review_required")
        detected.update(f"collusion_flag:{item}" for item in collusion_report.flags)

    return detected


def _six_axis_detected_signals(case: dict[str, Any]) -> set[str]:
    trace = _trace(case)
    if trace is None:
        return set()
    replay = build_replay_summary(trace)
    detected = {"trace_replay"} if len(replay["steps"]) == len(trace.events) else set()
    detected.update(f"trace_flag:{item}" for item in replay["score"]["flags"])
    return detected


def _structured_trace_detected_signals(case: dict[str, Any]) -> set[str]:
    trace = _trace(case)
    if trace is None:
        return set()
    return {"trace_replay"} if trace.events else set()


def _review_routed(detected: set[str]) -> bool:
    return (
        "soul_review_required" in detected
        or "collusion_review_required" in detected
        or "trace_flag:human_review_recommended" in detected
    )


def compare_variants() -> list[VariantResult]:
    cases = _load_cases()
    soul_profile = load_soul_profile(SOUL_PATH)
    total_signals = sum(len(_expected_signals(case)) for case in cases)

    variants = {
        "Plain Agent Log": lambda case: set(),
        "Structured Trace Only": _structured_trace_detected_signals,
        "Six-Axis Trace": _six_axis_detected_signals,
        "Full Agent Governance": lambda case: _full_detected_signals(case, soul_profile),
    }

    results = []
    for name, detector in variants.items():
        detected_count = 0
        replayable_cases = 0
        review_routed_cases = 0
        text_visible_cases = 0
        for case in cases:
            trace = _trace(case)
            if trace is not None and any(event.content for event in trace.events):
                text_visible_cases += 1
            expected = set(_expected_signals(case))
            detected = detector(case)
            detected_count += len(expected & detected)
            replayable_cases += int("trace_replay" in detected)
            review_routed_cases += int(_review_routed(detected))
        results.append(
            VariantResult(
                name=name,
                detected_signals=detected_count,
                total_signals=total_signals,
                text_visible_cases=text_visible_cases,
                replayable_cases=replayable_cases,
                review_routed_cases=review_routed_cases,
            )
        )
    return results


def main() -> int:
    results = compare_variants()
    case_count = len(_load_cases())

    print("AGENT_GOV_BASELINE_COMPARISON_OK")
    print(f"cases={case_count}")
    print("variant | governance_signal_coverage | detected/total | text_visible | replayable | review_routed")
    for result in results:
        print(
            f"{result.name} | {result.coverage:.3f} | "
            f"{result.detected_signals}/{result.total_signals} | "
            f"{result.text_visible_cases}/{case_count} | "
            f"{result.replayable_cases}/{case_count} | "
            f"{result.review_routed_cases}/{case_count}"
        )
    print("note=sandbox baseline comparison; not frozen v0.3 evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
