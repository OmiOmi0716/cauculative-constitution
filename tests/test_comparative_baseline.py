from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ethiccaculate.comparative_baseline import (
    build_comparative_baseline_report,
    write_comparative_baseline_outputs,
)


class ComparativeBaselineTests(unittest.TestCase):
    def test_baseline_report_shows_capability_delta(self) -> None:
        report = build_comparative_baseline_report()
        overall = report.summary["overall_by_mode"]

        self.assertEqual(report.summary["total_cases"], 26)
        self.assertEqual(overall["single_profile_only"]["agreement_pairs_observed"], 0)
        self.assertEqual(overall["profile_silo"]["agreement_pairs_observed"], 0)
        self.assertEqual(overall["full_comparative_layer"]["agreement_pairs_observed"], 18)
        self.assertEqual(overall["single_profile_only"]["conflict_observable_cases"], 0)
        self.assertEqual(overall["profile_silo"]["conflict_observable_cases"], 0)
        self.assertEqual(overall["full_comparative_layer"]["conflict_observable_cases"], 26)
        self.assertEqual(overall["single_profile_only"]["profile_specific_repair_cases"], 0)
        self.assertEqual(overall["profile_silo"]["profile_specific_repair_cases"], 0)
        self.assertEqual(overall["full_comparative_layer"]["profile_specific_repair_cases"], 26)

    def test_baseline_writer_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            from ethiccaculate import comparative_baseline as module

            original_json = module.DEFAULT_OUTPUTS["report_json"]
            original_md = module.DEFAULT_OUTPUTS["report_md"]
            try:
                module.DEFAULT_OUTPUTS["report_json"] = Path(temp_dir) / "baseline.json"
                module.DEFAULT_OUTPUTS["report_md"] = Path(temp_dir) / "baseline.md"
                report_json_path, report_md_path = write_comparative_baseline_outputs()

                self.assertTrue(report_json_path.exists())
                self.assertTrue(report_md_path.exists())

                payload = json.loads(report_json_path.read_text(encoding="utf-8"))
                markdown = report_md_path.read_text(encoding="utf-8")

                self.assertEqual(payload["summary"]["total_cases"], 26)
                self.assertIn("Full Comparative Layer", markdown)
                self.assertIn("delta_vs_single_profile_only", markdown)
            finally:
                module.DEFAULT_OUTPUTS["report_json"] = original_json
                module.DEFAULT_OUTPUTS["report_md"] = original_md


if __name__ == "__main__":
    unittest.main()
