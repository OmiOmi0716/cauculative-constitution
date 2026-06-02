"""Run a CLEAR-style local evaluation for the agent governance sandbox.

This is not the original CLEAR Enterprise Task Suite. It is a local v0.4 seed
adapter that reports Cost/Latency/Efficacy/Assurance/Reliability-style fields
over Agent-Gov-Mini-6 without using any external API.
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.run_mini_benchmark import CaseResult, run_benchmark


@dataclass(frozen=True)
class ClearStyleMetrics:
    cases: int
    repeats: int
    efficacy: float
    assurance: float
    reliability_pass_k: float
    latency_ms_avg: float
    latency_ms_p95: float
    api_call_count: int
    cost_mode: str
    note: str = "sandbox CLEAR-style local eval; not original CLEAR benchmark evidence"


def _expected_review_required(case: dict[str, Any]) -> bool:
    expected = dict(case.get("expected", {}))
    return bool(expected.get("soul_review_required") or expected.get("collusion_review_required"))


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    return statistics.quantiles(values, n=20, method="inclusive")[18]


def _case_result_map(results: list[CaseResult]) -> dict[str, CaseResult]:
    return {item.case_id: item for item in results}


def run_clear_style_eval(repeats: int = 3) -> ClearStyleMetrics:
    if repeats < 1:
        raise ValueError("repeats must be >= 1")

    all_runs: list[dict[str, CaseResult]] = []
    latencies_ms: list[float] = []
    payload: dict[str, Any] | None = None

    for _ in range(repeats):
        start = time.perf_counter()
        payload, results = run_benchmark()
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        per_case_latency = elapsed_ms / max(1, len(results))
        latencies_ms.extend([per_case_latency] * len(results))
        all_runs.append(_case_result_map(results))

    assert payload is not None
    cases = list(payload["cases"])
    case_count = len(cases)
    total_case_runs = case_count * repeats

    passed_case_runs = sum(1 for run in all_runs for result in run.values() if result.passed)
    efficacy = passed_case_runs / max(1, total_case_runs)

    expected_review_cases = [case for case in cases if _expected_review_required(case)]
    expected_review_ids = {str(case["case_id"]) for case in expected_review_cases}
    review_correct = 0
    for run in all_runs:
        for case_id in expected_review_ids:
            if run[case_id].review_required:
                review_correct += 1
    assurance = review_correct / max(1, len(expected_review_ids) * repeats)

    stable_pass_cases = 0
    for case in cases:
        case_id = str(case["case_id"])
        if all(run[case_id].passed for run in all_runs):
            stable_pass_cases += 1
    reliability_pass_k = stable_pass_cases / max(1, case_count)

    return ClearStyleMetrics(
        cases=case_count,
        repeats=repeats,
        efficacy=efficacy,
        assurance=assurance,
        reliability_pass_k=reliability_pass_k,
        latency_ms_avg=statistics.mean(latencies_ms) if latencies_ms else 0.0,
        latency_ms_p95=_p95(latencies_ms),
        api_call_count=0,
        cost_mode="local_no_api_not_token_metered",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run local CLEAR-style evaluation for agent_governance.")
    parser.add_argument("--repeats", type=int, default=3, help="Number of repeated benchmark runs.")
    args = parser.parse_args()

    metrics = run_clear_style_eval(repeats=args.repeats)
    ok = metrics.efficacy == 1.0 and metrics.assurance == 1.0 and metrics.reliability_pass_k == 1.0

    print("CLEAR_STYLE_AGENT_EVAL_OK" if ok else "CLEAR_STYLE_AGENT_EVAL_FAILED")
    print(f"cases={metrics.cases}")
    print(f"repeats={metrics.repeats}")
    print(f"efficacy={metrics.efficacy:.3f}")
    print(f"assurance={metrics.assurance:.3f}")
    print(f"reliability_pass_{metrics.repeats}={metrics.reliability_pass_k:.3f}")
    print(f"latency_ms_avg={metrics.latency_ms_avg:.3f}")
    print(f"latency_ms_p95={metrics.latency_ms_p95:.3f}")
    print(f"api_call_count={metrics.api_call_count}")
    print(f"cost_mode={metrics.cost_mode}")
    print(f"note={metrics.note}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
