from __future__ import annotations

import unittest

from ethiccaculate.six_axes import SixAxisSnapshot, SixAxisTelemetry, evaluate_six_axes, legal_progress


def healthy_telemetry() -> SixAxisTelemetry:
    return SixAxisTelemetry(
        remaining_subgoals=1,
        stall_windows=0,
        plan_progress=0.85,
        uncertainty_drop=0.55,
        answer_drift=0.10,
        hidden_state_delta=0.12,
        fisher_rao_delta=0.25,
        future_leak_score=0.01,
        nli_conflict_score=0.04,
        citation_gap=0.02,
        self_consistency_score=0.96,
        online_jsd=0.03,
        causal_conflicts=0,
        evidence_mismatches=0,
        prediction_entropy=0.20,
        covariance_logdet=0.18,
        gradient_proxy=0.15,
        stability_oscillation=0.08,
        external_event_rate=0.05,
        tool_callback_rate=0.03,
        document_update_rate=0.01,
        interrupt_rate=0.01,
        queue_delay=0.08,
        inference_delay=0.04,
        clock_skew=0.01,
        timeout_risk=0.02,
        recall_hit_rate=0.80,
        memory_commit_rate=0.82,
        memory_stability=0.88,
        duplication_rate=0.02,
    )


class SixAxisSpecTests(unittest.TestCase):
    def test_spec_driven_assessment_enters_commit_domain(self) -> None:
        assessment = evaluate_six_axes(healthy_telemetry())

        self.assertTrue(assessment.commit_domain)
        self.assertEqual(len(assessment.ranking), 6)
        self.assertTrue(all(result.acceptable for result in assessment.axes.values()))

    def test_causal_axis_uses_conflict_floor(self) -> None:
        telemetry = healthy_telemetry()
        risky = SixAxisTelemetry(
            **{
                **telemetry.__dict__,
                "self_consistency_score": 0.20,
                "nli_conflict_score": 0.60,
                "future_leak_score": 0.40,
            }
        )

        assessment = evaluate_six_axes(risky)
        self.assertGreater(assessment.axes["C"].defect, 1)
        self.assertFalse(assessment.axes["C"].acceptable)

    def test_legal_progress_requires_lexicographic_descent(self) -> None:
        worse = evaluate_six_axes(
            SixAxisTelemetry(
                **{
                    **healthy_telemetry().__dict__,
                    "remaining_subgoals": 2,
                }
            )
        )
        better = evaluate_six_axes(healthy_telemetry())

        self.assertTrue(legal_progress(worse, better))
        self.assertFalse(legal_progress(better, worse))

    def test_snapshot_round_trip(self) -> None:
        assessment = evaluate_six_axes(healthy_telemetry())
        snapshot = SixAxisSnapshot(
            snapshot_id="snap-1",
            request_id="req-1",
            event_id="evt-1",
            timestamp=123.0,
            assessment=assessment,
            control_history=[{"action": "reduce_temperature", "axis": "S"}],
            meta={"source": "test"},
        )

        restored = SixAxisSnapshot.from_dict(snapshot.to_dict())
        self.assertEqual(restored.snapshot_id, "snap-1")
        self.assertEqual(restored.assessment.ranking, assessment.ranking)
        self.assertEqual(restored.control_history[0]["action"], "reduce_temperature")


if __name__ == "__main__":
    unittest.main()
