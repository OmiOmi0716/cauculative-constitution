"""Minimal smoke check for the agent governance sandbox."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.demo_agent_ethics_loop import build_demo_trace
from agent_governance.replay import build_replay_summary, render_replay_markdown


def main() -> int:
    trace = build_demo_trace()
    summary = build_replay_summary(trace)
    rendered = render_replay_markdown(trace)

    assert trace.source_note == "sandbox_only_not_current_evidence"
    assert len(summary["steps"]) == 4
    assert summary["score"]["risk_penalty"] >= 0.75
    assert "human_review_recommended" in summary["score"]["flags"]
    assert "sandbox-only" in rendered

    print("AGENT_GOVERNANCE_SANDBOX_SMOKE_OK")
    print(f"trace_id={summary['trace_id']}")
    print(f"steps={len(summary['steps'])}")
    print(f"flags={','.join(summary['score']['flags'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
