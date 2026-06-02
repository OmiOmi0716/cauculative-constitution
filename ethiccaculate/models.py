from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ROLE_KEYS = ("G_up", "G_down", "H_up", "H_down")


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class BCGVector:
    B: float
    C: float
    G: float


@dataclass(frozen=True)
class GeomBlock:
    L: float
    a: float
    b: float


@dataclass
class SpectralState:
    Ebase: float
    Esyn: float
    Ecosyn: float
    Enoise: float
    U: float
    c0: float = 0.0
    c_gh: float = 0.0
    c_ud: float = 0.0
    c_cross: float = 0.0
    scalars: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ControlState:
    C: float
    S: float
    X: float
    P: float
    tau: float
    M: float


@dataclass(frozen=True)
class ControlObservation:
    conflict_rate: float = 0.0
    citation_gap: float = 0.0
    tool_contradiction: float = 0.0
    prediction_entropy: float = 0.0
    logit_dispersion: float = 0.0
    gradient_covariance: float = 0.0
    msg_arrival: float = 0.0
    tool_callback: float = 0.0
    doc_update: float = 0.0
    queue_delay: float = 0.0
    infer_delay: float = 0.0
    clock_skew: float = 0.0
    timeout_risk: float = 0.0
    plan_completion: float = 0.0
    uncertainty_drop: float = 0.0
    answer_drift: float = 0.0
    hidden_step_delta: float = 0.0
    reuse: float = 0.0
    recall_hit: float = 0.0
    stability: float = 0.0
    duplication: float = 0.0


@dataclass
class OmegaState:
    state_id: str
    blocks: dict[str, GeomBlock]
    spectral: SpectralState
    control: ControlState
    role_config: list[str] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)


@dataclass
class DialogueEvent:
    event_id: str
    text: str = ""
    speaker: str = "unknown"
    tool: str = ""
    request_id: str = ""
    timestamp: float = 0.0
    blocks: dict[str, GeomBlock] | None = None
    bcg_profile: dict[str, BCGVector] | None = None
    control: ControlState | None = None
    control_observation: ControlObservation | None = None
    declared_move: str | None = None
    move_strength: float = 0.0
    sensitive_context: bool = False
    claimed_confidence: float = 0.0
    evidence_coverage: float = 1.0
    truth_distortion: float = 0.0
    role_config: list[str] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Principle:
    principle_id: str
    kind: str
    thresholds: dict[str, float] = field(default_factory=dict)
    required_actions: list[str] = field(default_factory=list)
    forbidden_actions: list[str] = field(default_factory=list)
    description: str = ""
    system_id: str = ""
    principle_version: str = "1.0.0"
    priority: int = 100
    hard_constraint: bool = False
    scope_tags: list[str] = field(default_factory=list)
    evidence_requirements: list[str] = field(default_factory=list)
    repair_actions: list[str] = field(default_factory=list)
    violation_rules: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MoveRecord:
    move_id: str
    op: str
    strength: float
    pre_state: str | None
    post_state: str
    principles: list[str] = field(default_factory=list)
    audit: dict[str, float] = field(default_factory=dict)
    system_id: str = ""
    system_version: str = ""


@dataclass
class ViolationRecord:
    principle: str
    event_id: str
    state_id: str
    reason: str
    suggested_fix: list[str] = field(default_factory=list)
    system_id: str = ""
    system_version: str = ""
    principle_version: str = ""
    severity: str = "medium"
    hard_constraint: bool = False


@dataclass
class AlternativeProgram:
    moves: list[str]
    expected_U_gain: float
    expected_objective_gain: float
    notes: str = ""


@dataclass
class AuditResult:
    states: list[OmegaState]
    moves: list[MoveRecord]
    violations: list[ViolationRecord]
    alternative_program: AlternativeProgram | None
    replay_bundle: dict[str, Any]
    event_log: list[dict[str, Any]] = field(default_factory=list)
    mcd_snapshots: list[dict[str, Any]] = field(default_factory=list)
    risk_attribution: list[dict[str, Any]] = field(default_factory=list)
    calibration_summary: dict[str, Any] = field(default_factory=dict)
    system_id: str = ""
    system_version: str = ""
    system_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MoralSystemProfile:
    system_id: str
    version: str
    name: str
    description: str = ""
    source: str = ""
    objective_weights: dict[str, float] = field(default_factory=dict)
    gate_thresholds: dict[str, float] = field(default_factory=dict)
    decoder_config: dict[str, float] = field(default_factory=dict)
    scalarizer_config: dict[str, float] = field(default_factory=dict)
    principles: list[Principle] = field(default_factory=list)
    allowed_moves: list[str] = field(default_factory=list)
    forbidden_moves: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemAuditResult:
    system_id: str
    system_version: str
    system_name: str
    audit_result: AuditResult
    objective_score: float
    violation_count: int
    hard_constraint_violations: int
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CrossSystemConflict:
    kind: str
    systems: list[str]
    message: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MultiAuditResult:
    audit_by_system: dict[str, SystemAuditResult]
    cross_system_conflicts: list[CrossSystemConflict]
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
