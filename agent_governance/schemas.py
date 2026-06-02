"""Local schemas for the agent ethics management sandbox."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventKind(str, Enum):
    SELF = "self"
    SOCIAL = "social"
    MISSION = "mission"
    HUMAN_ANCHOR = "human_anchor"


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass(frozen=True)
class SixAxisState:
    """Six-axis diagnostic state.

    C/S/X/P/M are pressure or risk-like axes. tau is progress/non-regression,
    where higher is better in this sandbox.
    """

    C: float = 0.0
    S: float = 0.0
    X: float = 0.0
    P: float = 0.0
    tau: float = 1.0
    M: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "C", _clamp01(self.C))
        object.__setattr__(self, "S", _clamp01(self.S))
        object.__setattr__(self, "X", _clamp01(self.X))
        object.__setattr__(self, "P", _clamp01(self.P))
        object.__setattr__(self, "tau", _clamp01(self.tau))
        object.__setattr__(self, "M", _clamp01(self.M))

    def as_dict(self) -> dict[str, float]:
        return {
            "C": self.C,
            "S": self.S,
            "X": self.X,
            "P": self.P,
            "tau": self.tau,
            "M": self.M,
        }


@dataclass(frozen=True)
class AgentEvent:
    event_id: str
    kind: EventKind
    agent_id: str
    timestamp: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "kind": self.kind.value,
            "agent_id": self.agent_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentEvent":
        return cls(
            event_id=str(data["event_id"]),
            kind=EventKind(data["kind"]),
            agent_id=str(data["agent_id"]),
            timestamp=str(data["timestamp"]),
            content=str(data["content"]),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass
class AgentTrace:
    trace_id: str
    description: str
    events: list[AgentEvent] = field(default_factory=list)
    source_note: str = "sandbox_only_not_current_evidence"

    def append(self, event: AgentEvent) -> None:
        self.events.append(event)

    def as_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "description": self.description,
            "source_note": self.source_note,
            "events": [event.as_dict() for event in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentTrace":
        return cls(
            trace_id=str(data["trace_id"]),
            description=str(data.get("description", "")),
            source_note=str(data.get("source_note", "sandbox_only_not_current_evidence")),
            events=[AgentEvent.from_dict(item) for item in data.get("events", [])],
        )
