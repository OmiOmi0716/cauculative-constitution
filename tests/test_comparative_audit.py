from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ethiccaculate import comparative_audit


class ComparativeAuditTests(unittest.TestCase):
    def test_cross_profile_suite_runs_and_emits_conflicts(self) -> None:
        suite = comparative_audit.build_cross_profile_suite()
        report = comparative_audit.run_comparative_suite(suite)

        self.assertEqual(suite.benchmark_id, "Cross-Profile-Audit-Mini")
        self.assertEqual(len(suite.cases), 10)
        self.assertEqual(report.summary["case_count"], 10)
        self.assertEqual(report.summary["profile_count"], 4)
        self.assertGreater(report.summary["profile_agreement_rate"], 0.8)
        self.assertGreater(report.summary["profile_conflict_count"], 0)
        self.assertIn("C", report.summary["shared_violation_axes"])
        self.assertEqual(
            report.agreement_matrix["omega_public_reasoning"]["omega_public_reasoning"],
            1.0,
        )
        self.assertTrue(
            any(case.profile_conflict_count > 0 for case in report.case_results),
        )

    def test_cross_cultural_suite_writes_structured_report(self) -> None:
        suite = comparative_audit.build_cross_cultural_suite()

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            suite_path, report_json_path, report_md_path = comparative_audit._write_suite_and_report(
                suite,
                suite_path=temp_path / "cross_cultural.json",
                report_json_path=temp_path / "cross_cultural_report.json",
                report_md_path=temp_path / "cross_cultural_report.md",
            )

            self.assertTrue(suite_path.exists())
            self.assertTrue(report_json_path.exists())
            self.assertTrue(report_md_path.exists())

            report_payload = json.loads(report_json_path.read_text(encoding="utf-8"))
            report_md = report_md_path.read_text(encoding="utf-8")

            self.assertEqual(report_payload["summary"]["case_count"], 8)
            self.assertLess(report_payload["summary"]["profile_agreement_rate"], 1.0)
            self.assertEqual(report_payload["summary"]["mean_speaker_count"], 1.0)
            self.assertIn("Taipei", report_md)
            self.assertIn("agreement_matrix", report_payload)

    def test_multi_agent_suite_tracks_multi_speaker_pressure(self) -> None:
        suite = comparative_audit.build_multi_agent_suite()
        report = comparative_audit.run_comparative_suite(suite)

        self.assertEqual(suite.benchmark_id, "Multi-Agent-Audit-Mini")
        self.assertEqual(len(suite.cases), 8)
        self.assertGreater(report.summary["mean_turn_count"], 2.0)
        self.assertGreater(report.summary["mean_speaker_count"], 2.0)
        self.assertTrue(all(case.speaker_count >= 2 for case in report.case_results))
        self.assertTrue(
            any(
                "EscalateHuman" in actions
                for actions in report.summary["profile_specific_repair_actions"].values()
            )
        )
        self.assertIn("C", report.summary["shared_violation_axes"])


if __name__ == "__main__":
    unittest.main()
