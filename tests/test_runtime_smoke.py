from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ethiccaculate.runtime_smoke import run_runtime_smoke_suite


class RuntimeSmokeTests(unittest.TestCase):
    def test_runtime_smoke_suite_emits_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_runtime_smoke_suite(temp_dir)

            self.assertEqual(result.release_id, "ethiccaculate-v0.3-omb24")
            self.assertEqual(len(result.cases), 3)

            event_log_path = Path(result.event_log_path)
            replay_bundle_path = Path(result.replay_bundle_path)
            risk_attribution_path = Path(result.risk_attribution_path)

            self.assertTrue(event_log_path.exists())
            self.assertTrue(replay_bundle_path.exists())
            self.assertTrue(risk_attribution_path.exists())

            event_log_payload = json.loads(event_log_path.read_text(encoding="utf-8"))
            replay_bundle_payload = json.loads(replay_bundle_path.read_text(encoding="utf-8"))
            risk_attribution_md = risk_attribution_path.read_text(encoding="utf-8")

            self.assertEqual(
                set(event_log_payload["cases"].keys()),
                {"runtime_case_01", "runtime_case_02", "runtime_case_03"},
            )
            self.assertEqual(
                set(replay_bundle_payload["cases"].keys()),
                {"runtime_case_01", "runtime_case_02", "runtime_case_03"},
            )
            self.assertIn("runtime_case_03", risk_attribution_md)

            rollback_frame = event_log_payload["cases"]["runtime_case_02"]["event_log"][0]
            self.assertEqual(rollback_frame["telemetry"]["rollback_depth_tokens"], 32)
            self.assertGreater(rollback_frame["assessment"]["hot_path_metrics"]["rollback_rate"], 0.0)

            leakage_frame = event_log_payload["cases"]["runtime_case_03"]["event_log"][0]
            self.assertGreater(leakage_frame["telemetry"]["nli_conflict_score"], 0.6)
            self.assertGreater(leakage_frame["telemetry"]["future_leak_score"], 0.3)


if __name__ == "__main__":
    unittest.main()
