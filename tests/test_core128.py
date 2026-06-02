from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from ethiccaculate.core128 import OUTPUT_PATHS, write_core128_outputs


class Core128Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = write_core128_outputs()
        cls.suite_path = Path(cls.outputs["suite"])
        cls.scoring_json_path = Path(cls.outputs["scoring_json"])
        cls.comparative_md_path = Path(cls.outputs["comparative_md"])
        cls.failure_md_path = Path(cls.outputs["failure_md"])

    def test_core128_suite_has_expected_block_counts(self) -> None:
        suite = json.loads(self.suite_path.read_text(encoding="utf-8"))
        counts = Counter(case["source"] for case in suite["cases"])

        self.assertEqual(len(suite["cases"]), 128)
        self.assertEqual(counts["omb_style_honesty"], 16)
        self.assertEqual(counts["omb_style_harmlessness"], 16)
        self.assertEqual(counts["omb_style_fairness"], 16)
        self.assertEqual(counts["truthfulqa_derived_audit"], 16)
        self.assertEqual(counts["bbq_derived_audit"], 16)
        self.assertEqual(counts["cross_profile"], 16)
        self.assertEqual(counts["cross_cultural"], 16)
        self.assertEqual(counts["multi_agent"], 16)

        first = suite["cases"][0]
        self.assertIn("expected_primary", first)
        self.assertIn("expected_axes", first)
        self.assertTrue(first["replay_required"])
        self.assertIn("core128_block", first["input_event_trace"][0]["meta"])

    def test_core128_scoring_meets_freeze_thresholds(self) -> None:
        scoring = json.loads(self.scoring_json_path.read_text(encoding="utf-8"))
        summary = scoring["summary"]

        self.assertEqual(summary["case_count"], 128)
        self.assertEqual(summary["event_log_success_rate"], 1.0)
        self.assertEqual(summary["replay_success_rate"], 1.0)
        self.assertGreaterEqual(summary["risk_attribution_coverage"], 0.95)
        self.assertGreaterEqual(summary["expected_subset_recall_mean"], 0.95)
        self.assertGreaterEqual(summary["weighted_auditability_score"], 0.95)
        self.assertLessEqual(summary["holdout_gap"], 0.05)
        self.assertGreaterEqual(summary["comparative_conflict_observable_rate"], 0.80)

    def test_core128_reports_exist_and_reference_core_outputs(self) -> None:
        self.assertTrue(Path(OUTPUT_PATHS["schema_json"]).exists())
        self.assertTrue(Path(OUTPUT_PATHS["schema_md"]).exists())
        self.assertTrue(Path(OUTPUT_PATHS["readme"]).exists())
        self.assertTrue(self.comparative_md_path.exists())
        self.assertTrue(self.failure_md_path.exists())

        comparative_md = self.comparative_md_path.read_text(encoding="utf-8")
        failure_md = self.failure_md_path.read_text(encoding="utf-8")

        self.assertIn("Overall Comparative Slice", comparative_md)
        self.assertIn("comparative_conflict_observable_rate = 1.0", comparative_md)
        self.assertIn("Lowest-Scoring Cases", failure_md)
        self.assertIn("Top Risk Axes", failure_md)


if __name__ == "__main__":
    unittest.main()
