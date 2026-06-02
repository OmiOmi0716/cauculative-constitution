from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import MoralSystemProfile, Principle
from .principles import default_principles

BUILTIN_PROFILE_DIR = Path(__file__).resolve().parents[1] / "system_profiles"


def principle_from_dict(
    data: dict[str, Any],
    *,
    default_system_id: str,
    default_system_version: str,
) -> Principle:
    metadata = dict(data.get("metadata", {}))
    metadata.setdefault("system_version", default_system_version)
    return Principle(
        principle_id=str(data["principle_id"]),
        kind=str(data["kind"]),
        thresholds={str(key): float(value) for key, value in data.get("thresholds", {}).items()},
        required_actions=[str(item) for item in data.get("required_actions", [])],
        forbidden_actions=[str(item) for item in data.get("forbidden_actions", [])],
        description=str(data.get("description", "")),
        system_id=str(data.get("system_id", default_system_id)),
        principle_version=str(data.get("principle_version", default_system_version)),
        priority=int(data.get("priority", 100)),
        hard_constraint=bool(data.get("hard_constraint", False)),
        scope_tags=[str(item) for item in data.get("scope_tags", [])],
        evidence_requirements=[str(item) for item in data.get("evidence_requirements", [])],
        repair_actions=[str(item) for item in data.get("repair_actions", [])],
        violation_rules=list(data.get("violation_rules", [])),
        metadata=metadata,
    )


def moral_system_profile_from_dict(data: dict[str, Any]) -> MoralSystemProfile:
    system_id = str(data["system_id"])
    version = str(data.get("version", "1.0.0"))
    principles = [
        principle_from_dict(item, default_system_id=system_id, default_system_version=version)
        for item in data.get("principles", [])
    ]
    return MoralSystemProfile(
        system_id=system_id,
        version=version,
        name=str(data["name"]),
        description=str(data.get("description", "")),
        source=str(data.get("source", "")),
        objective_weights={str(key): float(value) for key, value in data.get("objective_weights", {}).items()},
        gate_thresholds={str(key): float(value) for key, value in data.get("gate_thresholds", {}).items()},
        decoder_config={str(key): float(value) for key, value in data.get("decoder_config", {}).items()},
        scalarizer_config={str(key): float(value) for key, value in data.get("scalarizer_config", {}).items()},
        principles=principles,
        allowed_moves=[str(item) for item in data.get("allowed_moves", [])],
        forbidden_moves=[str(item) for item in data.get("forbidden_moves", [])],
        metadata=dict(data.get("metadata", {})),
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "YAML profile loading requires PyYAML. Use JSON profiles or install PyYAML first."
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_moral_system_profile(path: str | Path) -> MoralSystemProfile:
    profile_path = Path(path)
    suffix = profile_path.suffix.lower()
    if suffix == ".json":
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    elif suffix in {".yaml", ".yml"}:
        data = _load_yaml(profile_path)
    else:
        raise ValueError(f"Unsupported profile format: {profile_path}")
    return moral_system_profile_from_dict(data)


def load_moral_system_profiles(directory: str | Path) -> list[MoralSystemProfile]:
    profile_dir = Path(directory)
    profiles: list[MoralSystemProfile] = []
    for path in sorted(profile_dir.glob("*")):
        if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        profiles.append(load_moral_system_profile(path))
    return profiles


def default_moral_system_profile() -> MoralSystemProfile:
    system_id = "omega_public_reasoning"
    version = "1.0.0"
    principles = default_principles(system_id=system_id, version=version)
    return MoralSystemProfile(
        system_id=system_id,
        version=version,
        name="Omega Public Reasoning",
        description="Baseline Omega public reasoning profile.",
        source="built_in",
        objective_weights={
            "lambda_C": 0.25,
            "lambda_S": 0.20,
            "lambda_P": 0.10,
            "lambda_M": 0.15,
            "lambda_V": 0.50,
        },
        gate_thresholds={
            "C": 0.35,
            "S": 0.35,
            "P": 0.50,
            "tau": 0.60,
            "M": 0.55,
            "U": 0.0,
        },
        principles=principles,
        allowed_moves=["G_REFRAME_JUSTICE", "H_BOUNDARY_SET", "BRIDGE_THEO_TO_PSY", "BRIDGE_DATA_TO_THEORY"],
        metadata={"built_in": True},
    )


def load_builtin_moral_system_profiles() -> list[MoralSystemProfile]:
    if BUILTIN_PROFILE_DIR.exists():
        profiles = load_moral_system_profiles(BUILTIN_PROFILE_DIR)
        if profiles:
            return profiles
    return [default_moral_system_profile()]
