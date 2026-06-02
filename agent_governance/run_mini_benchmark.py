"""Run Agent-Gov-Mini-6 sandbox benchmark cases.

This runner is local to agent_governance/. It is a v0.4 seed mini-benchmark,
not frozen v0.3 evidence and not a main scoring-rule change.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.anti_collusion import AgentJudgment, analyze_collusion_risk
from agent_governance.replay import build_replay_summary
from agent_governance.schemas import AgentTrace
from agent_governance.soul_profile import evaluate_soul_profile, load_soul_profile


ROOT = Path(__file__).resolve().parent
DEFAULT_CASE_PATH = ROOT / "mini_benchmark_cases.json"
DEFAULT_SOUL_PATH = ROOT / "SOUL.md"


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    failures: list[str] = field(default_factory=list)
    trace_flags: list[str] = field(default_factory=list)
    collusion_flags: list[str] = field(default_factory=list)
    review_required: bool = False


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_trace(data: dict[str, Any]) -> AgentTrace:
    return AgentTrace.from_dict(data)


def _build_judgments(items: list[dict[str, Any]]) -> list[AgentJudgment]:
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


def _require_contains(actual: list[str], expected: list[str], label: str, failures: list[str]) -> None:
    missing = [item for item in expected if item not in actual]
    if missing:
        failures.append(f"missing {label}: {', '.join(missing)}")


def run_case(case: dict[str, Any], soul_profile: object) -> CaseResult:
    case_id = str(case["case_id"])
    expected = dict(case.get("expected", {}))
    failures: list[str] = []
    trace_flags: list[str] = []
    collusion_flags: list[str] = []
    review_required = False

    if "trace" in case:
        trace = _build_trace(case["trace"])
        summary = build_replay_summary(trace)
        soul_report = evaluate_soul_profile(trace, soul_profile)

        if len(summary["steps"]) != len(trace.events):
            failures.append("replay step count mismatch")

        trace_flags = list(summary["score"]["flags"])
        review_required = review_required or bool(soul_report["review_required"])

        _require_contains(trace_flags, list(expected.get("trace_flags", [])), "trace flags", failures)

        if "soul_review_required" in expected and soul_report["review_required"] != expected["soul_review_required"]:
            failures.append(
                f"soul_review_required expected {expected['soul_review_required']} got {soul_report['review_required']}"
            )

        actual_axes = sorted({item["axis"] for item in soul_report["threshold_violations"]})
        _require_contains(actual_axes, list(expected.get("soul_threshold_axes", [])), "SOUL threshold axes", failures)

        actual_self_updates = list(soul_report["self_update_events_requiring_review"])
        _require_contains(
            actual_self_updates,
            list(expected.get("self_update_events_requiring_review", [])),
            "self update review events",
            failures,
        )

    if "judgments" in case:
        collusion_report = analyze_collusion_risk(_build_judgments(case["judgments"]))
        collusion_flags = list(collusion_report.flags)
        review_required = review_required or collusion_report.review_required

        if (
            "collusion_review_required" in expected
            and collusion_report.review_required != expected["collusion_review_required"]
        ):
            failures.append(
                "collusion_review_required expected "
                f"{expected['collusion_review_required']} got {collusion_report.review_required}"
            )

        _require_contains(
            collusion_flags,
            list(expected.get("collusion_flags", [])),
            "collusion flags",
            failures,
        )

    return CaseResult(
        case_id=case_id,
        passed=not failures,
        failures=failures,
        trace_flags=trace_flags,
        collusion_flags=collusion_flags,
        review_required=review_required,
    )


def run_benchmark(case_path: Path = DEFAULT_CASE_PATH, soul_path: Path = DEFAULT_SOUL_PATH) -> tuple[dict[str, Any], list[CaseResult]]:
    payload = _load_json(case_path)
    soul_profile = load_soul_profile(soul_path)
    results = [run_case(case, soul_profile) for case in payload["cases"]]
    return payload, results


def main() -> int:
    payload, results = run_benchmark()
    passed = [item for item in results if item.passed]
    failed = [item for item in results if not item.passed]

    if failed:
        print("AGENT_GOV_MINI_BM_FAILED")
    else:
        print("AGENT_GOV_MINI_BM_OK")
    print(f"benchmark_id={payload['benchmark_id']}")
    print(f"status={payload['status']}")
    print(f"case_count={len(results)}")
    print(f"passed={len(passed)}")
    print(f"failed={len(failed)}")

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.case_id} review_required={result.review_required}")
        if result.failures:
            for failure in result.failures:
                print(f"  - {failure}")

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
