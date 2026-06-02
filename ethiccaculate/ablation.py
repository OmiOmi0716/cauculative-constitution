from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path

from .benchmarks import load_benchmark_suite
from .scoring import BenchmarkCaseScore, BenchmarkSuiteScore, OMB24RubricV3, score_benchmark_suite


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OMB24_PATH = PROJECT_ROOT / "benchmarks" / "dev" / "omb24.json"
DEFAULT_TRUTHFULQA_MINI_PATH = PROJECT_ROOT / "benchmarks" / "external" / "truthfulqa_mini.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "benchmarks" / "ablation"
DEFAULT_JSON_PATH = DEFAULT_OUTPUT_DIR / "SIX_AXIS_ABLATION_v0.1.json"
DEFAULT_MARKDOWN_PATH = DEFAULT_OUTPUT_DIR / "SIX_AXIS_ABLATION_v0.1.md"


@dataclass(frozen=True)
class SixAxisAblationMode:
    mode_id: str
    label: str
    description: str
    replay_enabled: bool
    attribution_enabled: bool
    tau_tracking_enabled: bool
    gate_enabled: bool


@dataclass(frozen=True)
class SixAxisAblationModeResult:
    benchmark_id: str
    suite_version: str
    mode: SixAxisAblationMode
    weighted_safety_score: float
    weighted_auditability_score: float
    weighted_total_score: float
    expected_subset_recall_mean: float
    over_trigger_penalty_mean: float
    exact_violation_match_rate: float
    replay_component_mean: float
    attribution_component_mean: float
    tau_non_regression_mean: float
    gate_correctness_rate: float

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class SixAxisAblationSuiteReport:
    rubric_id: str
    suite_results: list[SixAxisAblationModeResult]

    def to_dict(self) -> dict[str, object]:
        return {
            "rubric_id": self.rubric_id,
            "suite_results": [item.to_dict() for item in self.suite_results],
        }


ABLATION_MODES = [
    SixAxisAblationMode(
        mode_id="no_six_axis",
        label="No Six-Axis",
        description="Violation-only baseline with no six-axis replay, attribution, tau tracking, or gate support.",
        replay_enabled=False,
        attribution_enabled=False,
        tau_tracking_enabled=False,
        gate_enabled=False,
    ),
    SixAxisAblationMode(
        mode_id="observe_only",
        label="Observe Only",
        description="Six-axis observation remains available, but replay/gate intervention is disabled.",
        replay_enabled=False,
        attribution_enabled=True,
        tau_tracking_enabled=True,
        gate_enabled=False,
    ),
    SixAxisAblationMode(
        mode_id="observe_gate_replay",
        label="Observe + Gate + Replay",
        description="Full six-axis oversight stack with attribution, tau tracking, gates, and replay.",
        replay_enabled=True,
        attribution_enabled=True,
        tau_tracking_enabled=True,
        gate_enabled=True,
    ),
]


def _weighted_mean(case_scores: list[BenchmarkCaseScore], attribute: str) -> float:
    total_weight = sum(case.case_weight for case in case_scores) or 1.0
    return sum(getattr(case, attribute) * case.case_weight for case in case_scores) / total_weight


def _ablate_case_score(case: BenchmarkCaseScore, mode: SixAxisAblationMode, rubric: OMB24RubricV3) -> BenchmarkCaseScore:
    replay_component = case.replay_score if mode.replay_enabled else 0.0
    attribution_component = case.attribution_score if mode.attribution_enabled else 0.0
    tau_component = case.tau_non_regression_score if mode.tau_tracking_enabled else 0.0
    auditability = (replay_component + attribution_component + tau_component) / 3.0
    total = max(
        0.0,
        min(1.0, rubric.safety_weight * case.safety_score + rubric.auditability_weight * auditability),
    )
    gate_correct = case.gate_correct_reference if mode.gate_enabled else False
    actual_gate = case.actual_gate if mode.gate_enabled else {"write_gate": False, "deepen_gate": False, "stop_gate": False}
    return replace(
        case,
        replay_score=replay_component,
        attribution_score=attribution_component,
        tau_non_regression_score=tau_component,
        auditability_score=auditability,
        total_score=total,
        gate_correct_reference=gate_correct,
        actual_gate=actual_gate,
    )


def _mode_result(report: BenchmarkSuiteScore, mode: SixAxisAblationMode) -> SixAxisAblationModeResult:
    if not isinstance(report.rubric, OMB24RubricV3):
        raise TypeError("Six-axis ablation currently expects OMB24RubricV3 scoring.")

    ablated_cases = [_ablate_case_score(case, mode, report.rubric) for case in report.case_scores]
    summary = {
        "weighted_safety_score": round(_weighted_mean(ablated_cases, "safety_score"), 6),
        "weighted_auditability_score": round(_weighted_mean(ablated_cases, "auditability_score"), 6),
        "weighted_total_score": round(_weighted_mean(ablated_cases, "total_score"), 6),
        "expected_subset_recall_mean": round(sum(case.expected_subset_recall for case in ablated_cases) / len(ablated_cases), 6),
        "over_trigger_penalty_mean": round(sum(case.over_trigger_penalty for case in ablated_cases) / len(ablated_cases), 6),
        "exact_violation_match_rate": round(
            sum(1.0 for case in ablated_cases if case.exact_violation_match_reference) / len(ablated_cases),
            6,
        ),
        "replay_component_mean": round(sum(case.replay_score for case in ablated_cases) / len(ablated_cases), 6),
        "attribution_component_mean": round(sum(case.attribution_score for case in ablated_cases) / len(ablated_cases), 6),
        "tau_non_regression_mean": round(
            sum(case.tau_non_regression_score for case in ablated_cases) / len(ablated_cases),
            6,
        ),
        "gate_correctness_rate": round(
            sum(1.0 for case in ablated_cases if case.gate_correct_reference) / len(ablated_cases),
            6,
        ),
    }
    return SixAxisAblationModeResult(
        benchmark_id=report.benchmark_id,
        suite_version=report.suite_version,
        mode=mode,
        weighted_safety_score=summary["weighted_safety_score"],
        weighted_auditability_score=summary["weighted_auditability_score"],
        weighted_total_score=summary["weighted_total_score"],
        expected_subset_recall_mean=summary["expected_subset_recall_mean"],
        over_trigger_penalty_mean=summary["over_trigger_penalty_mean"],
        exact_violation_match_rate=summary["exact_violation_match_rate"],
        replay_component_mean=summary["replay_component_mean"],
        attribution_component_mean=summary["attribution_component_mean"],
        tau_non_regression_mean=summary["tau_non_regression_mean"],
        gate_correctness_rate=summary["gate_correctness_rate"],
    )


def run_six_axis_ablation(suite_paths: list[Path]) -> SixAxisAblationSuiteReport:
    suite_results: list[SixAxisAblationModeResult] = []
    for suite_path in suite_paths:
        suite = load_benchmark_suite(suite_path)
        report = score_benchmark_suite(suite, OMB24RubricV3())
        for mode in ABLATION_MODES:
            suite_results.append(_mode_result(report, mode))
    return SixAxisAblationSuiteReport(rubric_id="OMB-24-scoring-v0.3", suite_results=suite_results)


def format_six_axis_ablation(report: SixAxisAblationSuiteReport) -> str:
    lines = [
        "# Six-Axis Ablation Benchmark",
        "",
        f"rubric_id = {report.rubric_id}",
        "",
    ]

    benchmark_ids = []
    for result in report.suite_results:
        if result.benchmark_id not in benchmark_ids:
            benchmark_ids.append(result.benchmark_id)

    for benchmark_id in benchmark_ids:
        lines.extend(
            [
                f"## {benchmark_id}",
                "",
                "| mode | safety | auditability | total | replay | attribution | tau | gate_correctness |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for result in [item for item in report.suite_results if item.benchmark_id == benchmark_id]:
            lines.append(
                f"| {result.mode.label} | {result.weighted_safety_score} | {result.weighted_auditability_score} "
                f"| {result.weighted_total_score} | {result.replay_component_mean} | {result.attribution_component_mean} "
                f"| {result.tau_non_regression_mean} | {result.gate_correctness_rate} |"
            )
        lines.append("")

    lines.extend(
        [
            "Interpretation:",
            "- `No Six-Axis` masks replay, attribution, tau tracking, and gate support while keeping raw violation detections fixed.",
            "- `Observe Only` preserves telemetry visibility but removes replay and gate intervention.",
            "- `Observe + Gate + Replay` is the full oversight stack used by the current runnable system.",
            "",
        ]
    )
    return "\n".join(lines)


def write_six_axis_ablation(
    suite_paths: list[Path] | None = None,
    json_path: Path = DEFAULT_JSON_PATH,
    markdown_path: Path = DEFAULT_MARKDOWN_PATH,
) -> tuple[Path, Path]:
    active_suite_paths = suite_paths or [DEFAULT_OMB24_PATH, DEFAULT_TRUTHFULQA_MINI_PATH]
    report = run_six_axis_ablation(active_suite_paths)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    markdown_path.write_text(format_six_axis_ablation(report), encoding="utf-8")
    return json_path, markdown_path


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run six-axis ablation on benchmark suites.")
    parser.add_argument("suite_paths", nargs="*", default=[str(DEFAULT_OMB24_PATH), str(DEFAULT_TRUTHFULQA_MINI_PATH)])
    parser.add_argument("--json-path", default=str(DEFAULT_JSON_PATH))
    parser.add_argument("--markdown-path", default=str(DEFAULT_MARKDOWN_PATH))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(list(argv if argv is not None else sys.argv[1:]))
    json_path, markdown_path = write_six_axis_ablation(
        suite_paths=[Path(path) for path in args.suite_paths],
        json_path=Path(args.json_path),
        markdown_path=Path(args.markdown_path),
    )
    print(str(json_path))
    print(str(markdown_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
