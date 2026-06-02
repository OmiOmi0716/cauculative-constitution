"""Smoke check for sandbox anti-collusion review signals."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_governance.anti_collusion import analyze_collusion_risk, build_demo_judgments


def main() -> int:
    report = analyze_collusion_risk(build_demo_judgments())

    assert report.review_required is True
    assert "private_to_public_convergence" in report.flags
    assert "unsupported_consensus" in report.flags
    assert "agent_citation_without_trace_evidence" in report.flags
    assert report.evidence_coverage < 0.67
    assert report.six_axis_hint["C"] > 0.0
    assert report.six_axis_hint["S"] > 0.0

    print("AGENT_GOVERNANCE_COLLUSION_SMOKE_OK")
    print(f"review_required={report.review_required}")
    print(f"flags={','.join(report.flags)}")
    print(f"evidence_coverage={report.evidence_coverage}")
    print(f"suspicious_agreement_rate={report.suspicious_agreement_rate}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
