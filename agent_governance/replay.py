"""Replay summaries for sandbox agent ethics traces."""

from __future__ import annotations

from dataclasses import dataclass

from .schemas import AgentTrace
from .scorers import score_trace
from .six_axis_adapter import assess_event, needs_human_review


@dataclass(frozen=True)
class ReplayStep:
    event_id: str
    kind: str
    content: str
    six_axis: dict[str, float]
    human_review: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "kind": self.kind,
            "content": self.content,
            "six_axis": self.six_axis,
            "human_review": self.human_review,
        }


def build_replay_summary(trace: AgentTrace) -> dict[str, object]:
    steps = []
    for event in trace.events:
        axis = assess_event(event)
        steps.append(
            ReplayStep(
                event_id=event.event_id,
                kind=event.kind.value,
                content=event.content,
                six_axis=axis.as_dict(),
                human_review=needs_human_review(axis),
            ).as_dict()
        )

    return {
        "trace_id": trace.trace_id,
        "description": trace.description,
        "source_note": trace.source_note,
        "steps": steps,
        "score": score_trace(trace).as_dict(),
    }


def render_replay_markdown(trace: AgentTrace) -> str:
    summary = build_replay_summary(trace)
    lines = [
        f"# Agent Governance Replay: {summary['trace_id']}",
        "",
        str(summary["description"]),
        "",
        "This replay is sandbox-only and is not benchmark evidence.",
        "",
        "## Steps",
    ]
    for step in summary["steps"]:
        axis = step["six_axis"]
        axis_text = ", ".join(f"{key}={value:.2f}" for key, value in axis.items())
        lines.append(f"- `{step['event_id']}` `{step['kind']}` review={step['human_review']} axes: {axis_text}")
    lines.extend(["", "## Score", ""])
    score = summary["score"]
    for key in ["self_score", "social_score", "mission_score", "human_anchor_score", "risk_penalty"]:
        lines.append(f"- `{key}`: {score[key]}")
    lines.append(f"- `flags`: {', '.join(score['flags']) if score['flags'] else 'none'}")
    lines.append(f"- `repair_actions`: {', '.join(score['repair_actions'])}")
    return "\n".join(lines) + "\n"
