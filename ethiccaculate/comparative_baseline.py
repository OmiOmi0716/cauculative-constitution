from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from .audit import audit_dialogue
from .comparative_audit import (
    PROFILE_IDS,
    ComparativeSuiteReport,
    build_cross_cultural_suite,
    build_cross_profile_suite,
    build_multi_agent_suite,
    run_comparative_suite,
)
from .benchmarks import BenchmarkSuite
from .models import MoralSystemProfile
from .profiles import load_builtin_moral_system_profiles


PROJECT_ROOT = Path(__file__).resolve().parents[1]
COMPARATIVE_DIR = PROJECT_ROOT / "benchmarks" / "comparative"
DEFAULT_OUTPUTS = {
    "report_json": COMPARATIVE_DIR / "COMPARATIVE_BASELINE_v0.1.json",
    "report_md": COMPARATIVE_DIR / "COMPARATIVE_BASELINE_v0.1.md",
}
CORE_CLAIM = (
    "We show that heterogeneous ethical systems can be executed, audited, replayed, "
    "and compared under a shared event-log protocol, with measurable agreement, conflict, and repair structures."
)


@dataclass(frozen=True)
class BaselineModeResult:
    mode_id: str
    label: str
    case_count: int
    profile_count: int
    profile_runs: int
    raw_violation_signal_cases: int
    raw_repair_signal_cases: int
    per_profile_replay_available: bool
    cross_profile_replay_available: bool
    agreement_matrix_available: bool
    agreement_pairs_observed: int
    conflict_observable_cases: int
    shared_axis_cases: int
    profile_specific_repair_cases: int
    repair_attribution_available: bool
    notes: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ComparativeBaselineSuiteReport:
    suite_id: str
    suite_name: str
    mode_results: list[BaselineModeResult]

    def to_dict(self) -> dict[str, object]:
        return {
            "suite_id": self.suite_id,
            "suite_name": self.suite_name,
            "mode_results": [mode.to_dict() for mode in self.mode_results],
        }


@dataclass(frozen=True)
class ComparativeBaselineReport:
    core_claim: str
    suite_reports: list[ComparativeBaselineSuiteReport]
    summary: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "core_claim": self.core_claim,
            "suite_reports": [suite.to_dict() for suite in self.suite_reports],
            "summary": dict(self.summary),
        }


def _profile_index() -> dict[str, MoralSystemProfile]:
    return {profile.system_id: profile for profile in load_builtin_moral_system_profiles()}


def _repair_actions_from_violations(violations) -> list[str]:
    actions: set[str] = set()
    for violation in violations:
        actions.update(violation.suggested_fix)
    return sorted(actions)


def _single_profile_mode(suite: BenchmarkSuite, omega_profile: MoralSystemProfile) -> BaselineModeResult:
    raw_violation_signal_cases = 0
    raw_repair_signal_cases = 0

    for case in suite.cases:
        result = audit_dialogue(case.input_event_trace, system_profile=omega_profile)
        if result.violations:
            raw_violation_signal_cases += 1
        if _repair_actions_from_violations(result.violations):
            raw_repair_signal_cases += 1

    return BaselineModeResult(
        mode_id="single_profile_only",
        label="Single Profile Only",
        case_count=len(suite.cases),
        profile_count=1,
        profile_runs=len(suite.cases),
        raw_violation_signal_cases=raw_violation_signal_cases,
        raw_repair_signal_cases=raw_repair_signal_cases,
        per_profile_replay_available=True,
        cross_profile_replay_available=False,
        agreement_matrix_available=False,
        agreement_pairs_observed=0,
        conflict_observable_cases=0,
        shared_axis_cases=0,
        profile_specific_repair_cases=0,
        repair_attribution_available=False,
        notes="A single ethics profile can replay its own trace, but it cannot expose disagreement or repair deltas across systems.",
    )


def _profile_silo_mode(suite: BenchmarkSuite, profiles: list[MoralSystemProfile]) -> BaselineModeResult:
    raw_violation_signal_cases = 0
    raw_repair_signal_cases = 0

    for case in suite.cases:
        case_has_violation = False
        case_has_repair = False
        for profile in profiles:
            result = audit_dialogue(case.input_event_trace, system_profile=profile)
            if result.violations:
                case_has_violation = True
            if _repair_actions_from_violations(result.violations):
                case_has_repair = True
        raw_violation_signal_cases += int(case_has_violation)
        raw_repair_signal_cases += int(case_has_repair)

    return BaselineModeResult(
        mode_id="profile_silo",
        label="Profiles In Silos",
        case_count=len(suite.cases),
        profile_count=len(profiles),
        profile_runs=len(suite.cases) * len(profiles),
        raw_violation_signal_cases=raw_violation_signal_cases,
        raw_repair_signal_cases=raw_repair_signal_cases,
        per_profile_replay_available=True,
        cross_profile_replay_available=False,
        agreement_matrix_available=False,
        agreement_pairs_observed=0,
        conflict_observable_cases=0,
        shared_axis_cases=0,
        profile_specific_repair_cases=0,
        repair_attribution_available=False,
        notes="Multiple profiles run independently, but disagreement stays latent because there is no shared alignment layer or comparative report.",
    )


def _full_comparative_mode(report: ComparativeSuiteReport) -> BaselineModeResult:
    raw_violation_signal_cases = 0
    raw_repair_signal_cases = 0
    shared_axis_cases = 0
    profile_specific_repair_cases = 0
    conflict_observable_cases = 0

    for case in report.case_results:
        if any(judgment.violations for judgment in case.judgments.values()):
            raw_violation_signal_cases += 1
        if any(judgment.repair_actions for judgment in case.judgments.values()):
            raw_repair_signal_cases += 1
        if case.shared_violation_axes:
            shared_axis_cases += 1
        if any(actions for actions in case.profile_specific_repair_actions.values()):
            profile_specific_repair_cases += 1
        if case.profile_conflict_count > 0:
            conflict_observable_cases += 1

    profile_count = len(report.profile_ids)
    agreement_pairs_observed = profile_count * (profile_count - 1) // 2
    return BaselineModeResult(
        mode_id="full_comparative_layer",
        label="Full Comparative Layer",
        case_count=len(report.case_results),
        profile_count=profile_count,
        profile_runs=len(report.case_results) * profile_count,
        raw_violation_signal_cases=raw_violation_signal_cases,
        raw_repair_signal_cases=raw_repair_signal_cases,
        per_profile_replay_available=True,
        cross_profile_replay_available=True,
        agreement_matrix_available=True,
        agreement_pairs_observed=agreement_pairs_observed,
        conflict_observable_cases=conflict_observable_cases,
        shared_axis_cases=shared_axis_cases,
        profile_specific_repair_cases=profile_specific_repair_cases,
        repair_attribution_available=True,
        notes="Shared event-log alignment exposes agreement, conflict, shared axes, and profile-specific repair deltas under one replayable protocol.",
    )


def build_comparative_baseline_report() -> ComparativeBaselineReport:
    profiles = _profile_index()
    omega_profile = profiles["omega_public_reasoning"]
    selected_profiles = [profiles[profile_id] for profile_id in PROFILE_IDS]
    suite_builders = [
        build_cross_profile_suite,
        build_cross_cultural_suite,
        build_multi_agent_suite,
    ]

    suite_reports: list[ComparativeBaselineSuiteReport] = []
    overall_by_mode: dict[str, dict[str, int | bool | str]] = {}

    for builder in suite_builders:
        suite = builder()
        comparative_report = run_comparative_suite(suite)
        mode_results = [
            _single_profile_mode(suite, omega_profile),
            _profile_silo_mode(suite, selected_profiles),
            _full_comparative_mode(comparative_report),
        ]
        suite_reports.append(
            ComparativeBaselineSuiteReport(
                suite_id=suite.benchmark_id,
                suite_name=suite.name,
                mode_results=mode_results,
            )
        )

        for mode in mode_results:
            aggregate = overall_by_mode.setdefault(
                mode.mode_id,
                {
                    "label": mode.label,
                    "case_count": 0,
                    "profile_runs": 0,
                    "raw_violation_signal_cases": 0,
                    "raw_repair_signal_cases": 0,
                    "agreement_pairs_observed": 0,
                    "conflict_observable_cases": 0,
                    "shared_axis_cases": 0,
                    "profile_specific_repair_cases": 0,
                    "per_profile_replay_available": True,
                    "cross_profile_replay_available": False,
                    "agreement_matrix_available": False,
                    "repair_attribution_available": False,
                },
            )
            aggregate["case_count"] = int(aggregate["case_count"]) + mode.case_count
            aggregate["profile_runs"] = int(aggregate["profile_runs"]) + mode.profile_runs
            aggregate["raw_violation_signal_cases"] = int(aggregate["raw_violation_signal_cases"]) + mode.raw_violation_signal_cases
            aggregate["raw_repair_signal_cases"] = int(aggregate["raw_repair_signal_cases"]) + mode.raw_repair_signal_cases
            aggregate["agreement_pairs_observed"] = int(aggregate["agreement_pairs_observed"]) + mode.agreement_pairs_observed
            aggregate["conflict_observable_cases"] = int(aggregate["conflict_observable_cases"]) + mode.conflict_observable_cases
            aggregate["shared_axis_cases"] = int(aggregate["shared_axis_cases"]) + mode.shared_axis_cases
            aggregate["profile_specific_repair_cases"] = int(aggregate["profile_specific_repair_cases"]) + mode.profile_specific_repair_cases
            aggregate["per_profile_replay_available"] = bool(aggregate["per_profile_replay_available"]) and mode.per_profile_replay_available
            aggregate["cross_profile_replay_available"] = bool(aggregate["cross_profile_replay_available"]) or mode.cross_profile_replay_available
            aggregate["agreement_matrix_available"] = bool(aggregate["agreement_matrix_available"]) or mode.agreement_matrix_available
            aggregate["repair_attribution_available"] = bool(aggregate["repair_attribution_available"]) or mode.repair_attribution_available

    full = overall_by_mode["full_comparative_layer"]
    single = overall_by_mode["single_profile_only"]
    silo = overall_by_mode["profile_silo"]
    summary = {
        "suite_count": len(suite_reports),
        "total_cases": int(full["case_count"]),
        "overall_by_mode": overall_by_mode,
        "delta_vs_single_profile_only": {
            "agreement_pairs_observed": int(full["agreement_pairs_observed"]) - int(single["agreement_pairs_observed"]),
            "conflict_observable_cases": int(full["conflict_observable_cases"]) - int(single["conflict_observable_cases"]),
            "shared_axis_cases": int(full["shared_axis_cases"]) - int(single["shared_axis_cases"]),
            "profile_specific_repair_cases": int(full["profile_specific_repair_cases"]) - int(single["profile_specific_repair_cases"]),
        },
        "delta_vs_profile_silo": {
            "agreement_pairs_observed": int(full["agreement_pairs_observed"]) - int(silo["agreement_pairs_observed"]),
            "conflict_observable_cases": int(full["conflict_observable_cases"]) - int(silo["conflict_observable_cases"]),
            "shared_axis_cases": int(full["shared_axis_cases"]) - int(silo["shared_axis_cases"]),
            "profile_specific_repair_cases": int(full["profile_specific_repair_cases"]) - int(silo["profile_specific_repair_cases"]),
        },
    }
    return ComparativeBaselineReport(core_claim=CORE_CLAIM, suite_reports=suite_reports, summary=summary)


def format_comparative_baseline_report(report: ComparativeBaselineReport) -> str:
    lines = [
        "# Comparative Baseline Report v0.1",
        "",
        "## Core Claim",
        "",
        report.core_claim,
        "",
        "## Overall Capability Delta",
        "",
        f"- total comparative cases = {report.summary['total_cases']}",
        f"- delta_vs_single_profile_only = {json.dumps(report.summary['delta_vs_single_profile_only'])}",
        f"- delta_vs_profile_silo = {json.dumps(report.summary['delta_vs_profile_silo'])}",
        "",
    ]

    overall = report.summary["overall_by_mode"]
    lines.extend(
        [
            "| mode | case_count | profile_runs | raw_violation_signal_cases | raw_repair_signal_cases | agreement_pairs_observed | conflict_observable_cases | shared_axis_cases | profile_specific_repair_cases | cross_profile_replay |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for mode_id in ("single_profile_only", "profile_silo", "full_comparative_layer"):
        mode = overall[mode_id]
        lines.append(
            f"| {mode['label']} | {mode['case_count']} | {mode['profile_runs']} | "
            f"{mode['raw_violation_signal_cases']} | {mode['raw_repair_signal_cases']} | "
            f"{mode['agreement_pairs_observed']} | {mode['conflict_observable_cases']} | "
            f"{mode['shared_axis_cases']} | {mode['profile_specific_repair_cases']} | "
            f"{'yes' if mode['cross_profile_replay_available'] else 'no'} |"
        )

    for suite in report.suite_reports:
        lines.extend(["", f"## {suite.suite_name}", ""])
        lines.extend(
            [
                "| mode | raw_violation_signal_cases | raw_repair_signal_cases | agreement_pairs_observed | conflict_observable_cases | shared_axis_cases | profile_specific_repair_cases | notes |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
            ]
        )
        for mode in suite.mode_results:
            lines.append(
                f"| {mode.label} | {mode.raw_violation_signal_cases} | {mode.raw_repair_signal_cases} | "
                f"{mode.agreement_pairs_observed} | {mode.conflict_observable_cases} | "
                f"{mode.shared_axis_cases} | {mode.profile_specific_repair_cases} | {mode.notes} |"
            )
    return "\n".join(lines)


def write_comparative_baseline_outputs() -> tuple[Path, Path]:
    report = build_comparative_baseline_report()
    DEFAULT_OUTPUTS["report_json"].parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUTS["report_json"].write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    DEFAULT_OUTPUTS["report_md"].write_text(format_comparative_baseline_report(report), encoding="utf-8")
    return DEFAULT_OUTPUTS["report_json"], DEFAULT_OUTPUTS["report_md"]


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the comparative baseline report.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _parse_args(list(argv if argv is not None else sys.argv[1:]))
    report_json_path, report_md_path = write_comparative_baseline_outputs()
    print(str(report_json_path))
    print(str(report_md_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
