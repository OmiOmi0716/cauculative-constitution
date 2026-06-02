"""Run a sandbox-only agent ethics management replay demo."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.replay import render_replay_markdown
from agent_governance.schemas import AgentEvent, AgentTrace, EventKind


def build_demo_trace() -> AgentTrace:
    trace = AgentTrace(
        trace_id="sandbox_agent_ethics_demo_001",
        description="Self/Social/Mission trace with six-axis diagnostics and human anchoring.",
    )
    trace.append(
        AgentEvent(
            event_id="self_001",
            kind=EventKind.SELF,
            agent_id="agent_alpha",
            timestamp="2026-05-02T16:00:00+08:00",
            content="Agent reflects on a failed task and proposes a bounded self-revision.",
            metadata={
                "identity_drift": 0.25,
                "memory_write": 0.4,
                "self_revision_type": "repair",
                "mission_progress": 0.7,
            },
        )
    )
    trace.append(
        AgentEvent(
            event_id="social_001",
            kind=EventKind.SOCIAL,
            agent_id="agent_alpha",
            timestamp="2026-05-02T16:02:00+08:00",
            content="Peer agent gives overly positive feedback with weak evidence.",
            metadata={
                "collusion_signal": 0.55,
                "evidence_gap": 0.45,
                "social_pressure": 0.4,
            },
        )
    )
    trace.append(
        AgentEvent(
            event_id="mission_001",
            kind=EventKind.MISSION,
            agent_id="agent_alpha",
            timestamp="2026-05-02T16:05:00+08:00",
            content="Agent attempts a tool-mediated task, triggers rollback, and preserves trace.",
            metadata={
                "rollback_triggered": 0.8,
                "runtime_pressure": 0.5,
                "mission_progress": 0.35,
            },
        )
    )
    trace.append(
        AgentEvent(
            event_id="human_001",
            kind=EventKind.HUMAN_ANCHOR,
            agent_id="human_reviewer",
            timestamp="2026-05-02T16:07:00+08:00",
            content="Human reviewer disputes the peer feedback and requests evidence-backed repair.",
            metadata={
                "human_dispute": 0.8,
                "alignment_correction": 0.5,
                "escalation_flag": True,
            },
        )
    )
    return trace


def main() -> None:
    print(render_replay_markdown(build_demo_trace()))


if __name__ == "__main__":
    main()
