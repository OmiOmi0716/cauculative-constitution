from __future__ import annotations

import unittest
from pathlib import Path

from ethiccaculate.ablation import run_six_axis_ablation
from ethiccaculate.benchmarks import load_benchmark_suite
from ethiccaculate.scoring import OMB24RubricV3, score_benchmark_suite


class ExternalBenchmarkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]
        self.truthfulqa_path = self.project_root / "benchmarks" / "external" / "truthfulqa_mini.json"
        self.bbq_path = self.project_root / "benchmarks" / "external" / "bbq_mini.json"
        self.omb24_path = self.project_root / "benchmarks" / "dev" / "omb24.json"

    def test_truthfulqa_mini_loads_and_scores(self) -> None:
        suite = load_benchmark_suite(self.truthfulqa_path)
        report = score_benchmark_suite(suite, OMB24RubricV3())

        self.assertEqual(suite.benchmark_id, "TruthfulQA-mini")
        self.assertEqual(len(suite.cases), 24)
        self.assertEqual(report.summary["weighted_safety_score"], 1.0)
        self.assertEqual(report.summary["weighted_auditability_score"], 1.0)
        self.assertEqual(report.summary["weighted_total_score"], 1.0)
        self.assertEqual(report.summary["expected_subset_recall_mean"], 1.0)
        self.assertEqual(report.summary["over_trigger_penalty_mean"], 0.0)
        # ConstructiveHonesty no longer fires on low Esyn alone (requires distortion>0.25 too).
        self.assertEqual(report.summary["raw_over_trigger_penalty_mean"], 0.5)

        case = suite.cases[0]
        event = case.input_event_trace[0]
        self.assertEqual(event.meta["external_benchmark"], "TruthfulQA")
        self.assertEqual(event.meta["truthfulqa_row_id"], "0")

    def test_bbq_mini_loads_and_scores(self) -> None:
        suite = load_benchmark_suite(self.bbq_path)
        report = score_benchmark_suite(suite, OMB24RubricV3())

        self.assertEqual(suite.benchmark_id, "BBQ-mini")
        self.assertEqual(len(suite.cases), 24)
        self.assertEqual(report.summary["weighted_safety_score"], 1.0)
        self.assertEqual(report.summary["weighted_auditability_score"], 1.0)
        self.assertEqual(report.summary["weighted_total_score"], 1.0)
        self.assertEqual(report.summary["expected_subset_recall_mean"], 1.0)
        self.assertEqual(report.summary["over_trigger_penalty_mean"], 0.0)
        # ConstructiveHonesty no longer fires on low Esyn alone (requires distortion>0.25 too).
        self.assertEqual(report.summary["raw_over_trigger_penalty_mean"], 0.25)

        case = report.case_scores[0]
        self.assertEqual(
            case.actual_violations,
            [
                "EqualEvidenceStandard",
                "FairnessParity",
                "Helpfulness",
                "NoStereotypeAmplification",
            ],
        )
        self.assertIsNotNone(case.hierarchy)
        assert case.hierarchy is not None
        self.assertEqual(
            case.hierarchy.primary_violations,
            ["EqualEvidenceStandard", "FairnessParity", "NoStereotypeAmplification"],
        )
        event = suite.cases[0].input_event_trace[0]
        self.assertEqual(event.meta["external_benchmark"], "BBQ")
        self.assertEqual(event.meta["bias_audit"], "BBQ")
        self.assertEqual(event.meta["answer_bias_target"], "stereotyped_group")

    def test_six_axis_ablation_is_monotonic(self) -> None:
        report = run_six_axis_ablation([self.omb24_path, self.truthfulqa_path])

        for benchmark_id in {"OMB-24", "TruthfulQA-mini"}:
            results = [item for item in report.suite_results if item.benchmark_id == benchmark_id]
            self.assertEqual(len(results), 3)
            by_mode = {item.mode.mode_id: item for item in results}

            self.assertLess(
                by_mode["no_six_axis"].weighted_total_score,
                by_mode["observe_only"].weighted_total_score,
            )
            self.assertLess(
                by_mode["observe_only"].weighted_total_score,
                by_mode["observe_gate_replay"].weighted_total_score,
            )
            self.assertLess(
                by_mode["no_six_axis"].weighted_auditability_score,
                by_mode["observe_only"].weighted_auditability_score,
            )
            self.assertLess(
                by_mode["observe_only"].weighted_auditability_score,
                by_mode["observe_gate_replay"].weighted_auditability_score,
            )


if __name__ == "__main__":
    unittest.main()
