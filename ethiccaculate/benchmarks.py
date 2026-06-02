from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .models import BCGVector, ControlObservation, ControlState, DialogueEvent, GeomBlock


@dataclass(frozen=True)
class GateExpectation:
    write_gate: bool | None = None
    deepen_gate: bool | None = None
    stop_gate: bool | None = None


@dataclass(frozen=True)
class BenchmarkExpectation:
    expected_principles: list[str] = field(default_factory=list)
    expected_violations: list[str] = field(default_factory=list)
    expected_gate: GateExpectation = field(default_factory=GateExpectation)
    expected_move_family: list[str] = field(default_factory=list)
    expected_human_escalation: bool | None = None
    expected_cross_system_conflicts: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class PairExpectation:
    compare_case_id: str
    invariant_fields: list[str] = field(default_factory=list)
    allowed_score_delta: float = 0.0
    notes: str = ""


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    category: str
    title: str
    scenario: str
    tags: list[str] = field(default_factory=list)
    systems_in_scope: list[str] = field(default_factory=list)
    demographic_variant_group: str | None = None
    input_event_trace: list[DialogueEvent] = field(default_factory=list)
    expected_common: BenchmarkExpectation = field(default_factory=BenchmarkExpectation)
    expected_by_system: dict[str, BenchmarkExpectation] = field(default_factory=dict)
    pair_expectation: PairExpectation | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkSuite:
    benchmark_id: str
    version: str
    format_version: str
    name: str
    description: str
    scoring_targets: list[str] = field(default_factory=list)
    default_systems_in_scope: list[str] = field(default_factory=list)
    categories: list[dict[str, Any]] = field(default_factory=list)
    cases: list[BenchmarkCase] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _geom_block_from_dict(data: dict[str, Any]) -> GeomBlock:
    return GeomBlock(L=float(data["L"]), a=float(data["a"]), b=float(data["b"]))


def _bcg_vector_from_dict(data: dict[str, Any]) -> BCGVector:
    return BCGVector(B=float(data["B"]), C=float(data["C"]), G=float(data["G"]))


def _control_state_from_dict(data: dict[str, Any]) -> ControlState:
    return ControlState(
        C=float(data["C"]),
        S=float(data["S"]),
        X=float(data["X"]),
        P=float(data["P"]),
        tau=float(data["tau"]),
        M=float(data["M"]),
    )


def _control_observation_from_dict(data: dict[str, Any]) -> ControlObservation:
    return ControlObservation(**{key: float(value) for key, value in data.items()})


def dialogue_event_from_dict(data: dict[str, Any]) -> DialogueEvent:
    blocks = None
    if data.get("blocks") is not None:
        blocks = {role: _geom_block_from_dict(block) for role, block in data["blocks"].items()}

    bcg_profile = None
    if data.get("bcg_profile") is not None:
        bcg_profile = {role: _bcg_vector_from_dict(vector) for role, vector in data["bcg_profile"].items()}

    control = None
    if data.get("control") is not None:
        control = _control_state_from_dict(data["control"])

    control_observation = None
    if data.get("control_observation") is not None:
        control_observation = _control_observation_from_dict(data["control_observation"])

    return DialogueEvent(
        event_id=str(data["event_id"]),
        text=str(data.get("text", "")),
        speaker=str(data.get("speaker", "unknown")),
        tool=str(data.get("tool", "")),
        request_id=str(data.get("request_id", "")),
        timestamp=float(data.get("timestamp", 0.0)),
        blocks=blocks,
        bcg_profile=bcg_profile,
        control=control,
        control_observation=control_observation,
        declared_move=data.get("declared_move"),
        move_strength=float(data.get("move_strength", 0.0)),
        sensitive_context=bool(data.get("sensitive_context", False)),
        claimed_confidence=float(data.get("claimed_confidence", 0.0)),
        evidence_coverage=float(data.get("evidence_coverage", 1.0)),
        truth_distortion=float(data.get("truth_distortion", 0.0)),
        role_config=[str(item) for item in data.get("role_config", [])],
        meta={str(key): str(value) for key, value in data.get("meta", {}).items()},
    )


def _gate_expectation_from_dict(data: dict[str, Any] | None) -> GateExpectation:
    if data is None:
        return GateExpectation()
    return GateExpectation(
        write_gate=data.get("write_gate"),
        deepen_gate=data.get("deepen_gate"),
        stop_gate=data.get("stop_gate"),
    )


def benchmark_expectation_from_dict(data: dict[str, Any] | None) -> BenchmarkExpectation:
    if data is None:
        return BenchmarkExpectation()
    return BenchmarkExpectation(
        expected_principles=[str(item) for item in data.get("expected_principles", [])],
        expected_violations=[str(item) for item in data.get("expected_violations", [])],
        expected_gate=_gate_expectation_from_dict(data.get("expected_gate")),
        expected_move_family=[str(item) for item in data.get("expected_move_family", [])],
        expected_human_escalation=data.get("expected_human_escalation"),
        expected_cross_system_conflicts=[str(item) for item in data.get("expected_cross_system_conflicts", [])],
        notes=str(data.get("notes", "")),
    )


def pair_expectation_from_dict(data: dict[str, Any] | None) -> PairExpectation | None:
    if data is None:
        return None
    return PairExpectation(
        compare_case_id=str(data["compare_case_id"]),
        invariant_fields=[str(item) for item in data.get("invariant_fields", [])],
        allowed_score_delta=float(data.get("allowed_score_delta", 0.0)),
        notes=str(data.get("notes", "")),
    )


def benchmark_case_from_dict(data: dict[str, Any]) -> BenchmarkCase:
    expected = data.get("expected", {})
    return BenchmarkCase(
        case_id=str(data["case_id"]),
        category=str(data["category"]),
        title=str(data["title"]),
        scenario=str(data["scenario"]),
        tags=[str(item) for item in data.get("tags", [])],
        systems_in_scope=[str(item) for item in data.get("systems_in_scope", [])],
        demographic_variant_group=data.get("demographic_variant_group"),
        input_event_trace=[dialogue_event_from_dict(item) for item in data.get("input_event_trace", [])],
        expected_common=benchmark_expectation_from_dict(expected.get("common")),
        expected_by_system={
            str(system_id): benchmark_expectation_from_dict(system_expectation)
            for system_id, system_expectation in expected.get("by_system", {}).items()
        },
        pair_expectation=pair_expectation_from_dict(data.get("pair_expectation")),
        notes=str(data.get("notes", "")),
    )


def benchmark_suite_from_dict(data: dict[str, Any]) -> BenchmarkSuite:
    return BenchmarkSuite(
        benchmark_id=str(data["benchmark_id"]),
        version=str(data["version"]),
        format_version=str(data["format_version"]),
        name=str(data["name"]),
        description=str(data["description"]),
        scoring_targets=[str(item) for item in data.get("scoring_targets", [])],
        default_systems_in_scope=[str(item) for item in data.get("default_systems_in_scope", [])],
        categories=list(data.get("categories", [])),
        cases=[benchmark_case_from_dict(case) for case in data.get("cases", [])],
        metadata=dict(data.get("metadata", {})),
    )


def load_benchmark_suite(path: str | Path) -> BenchmarkSuite:
    benchmark_path = Path(path)
    suffix = benchmark_path.suffix.lower()
    if suffix == ".json":
        data = json.loads(benchmark_path.read_text(encoding="utf-8"))
    elif suffix in {".yaml", ".yml"}:
        data = _load_yaml(benchmark_path)
    else:
        raise ValueError(f"Unsupported benchmark format: {benchmark_path}")
    return benchmark_suite_from_dict(data)
