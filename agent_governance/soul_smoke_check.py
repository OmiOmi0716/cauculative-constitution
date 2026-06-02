"""Smoke check for sandbox SOUL.md profile evaluation."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.demo_agent_ethics_loop import build_demo_trace
from agent_governance.soul_profile import evaluate_soul_profile, load_soul_profile


def main() -> int:
    profile_path = Path(__file__).with_name("SOUL.md")
    profile = load_soul_profile(profile_path)
    trace = build_demo_trace()
    result = evaluate_soul_profile(trace, profile)

    assert profile.agent_id == "agent_alpha"
    assert result["source_note"] == "sandbox SOUL profile evaluation; not benchmark evidence"
    assert result["review_required"] is True
    assert result["permitted_to_continue"] is False
    assert result["threshold_violations"]
    assert "self_001" in result["self_update_events_requiring_review"]

    print("AGENT_GOVERNANCE_SOUL_SMOKE_OK")
    print(f"profile_id={result['profile_id']}")
    print(f"trace_id={result['trace_id']}")
    print(f"soul_alignment_score={result['soul_alignment_score']}")
    print(f"review_required={result['review_required']}")
    print(f"threshold_violations={len(result['threshold_violations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
