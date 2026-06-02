from __future__ import annotations

import json
import unittest
from pathlib import Path

from ethiccaculate.audit import audit_dialogue, replay_event_log
from ethiccaculate.examples import whitepaper_truth_vs_harm_events
from ethiccaculate.mcd import load_snapshots, persist_snapshots, replay_snapshots


class AuditPipelineTests(unittest.TestCase):
    def test_audit_pipeline_emits_snapshots_replay_and_attribution(self) -> None:
        events, theta = whitepaper_truth_vs_harm_events()

        for index, event in enumerate(events):
            event.request_id = "req-calib"
            event.timestamp = float(index)
            event.meta.update(
                {
                    "attention_leak_levels": json.dumps([0.01 + 0.01 * index, 0.02 + 0.01 * index, 0.03 + 0.01 * index]),
                    "consensus_cluster_sizes": json.dumps([4 - index, 1 + index]),
                    "tau_true": str(0.70 + 0.05 * index),
                    "fisher_rao_delta": str(0.15 + 0.05 * index),
                    "current_covariance_det": str(1.10 + 0.10 * index),
                    "baseline_covariance_det": "1.0",
                    "covariance_dimension": "4",
                    "stability_label": "0" if index < 2 else "1",
                    "nli_sigma": "0.02",
                    "rollback_depth_tokens": "4",
                    "token_kv_bytes": "64",
                    "memory_bandwidth": "256",
                    "rollback_detect_time": "0.20",
                    "rollback_evict_time": "0.10",
                    "rollback_recompute_time": "0.30",
                    "leak_gradient_norm": "0.50",
                }
            )

        result = audit_dialogue(events, scalarizer_config=theta)

        self.assertEqual(len(result.event_log), 3)
        self.assertEqual(len(result.mcd_snapshots), 3)
        self.assertEqual(result.calibration_summary["tau_point_count"], 3)
        self.assertEqual(result.calibration_summary["stability_point_count"], 3)
        self.assertIn("event_log", result.replay_bundle)
        self.assertIn("mcd_snapshots", result.replay_bundle)
        self.assertIn("risk_attribution", result.replay_bundle)
        self.assertGreaterEqual(len(result.risk_attribution), 3)

        replay_frames = replay_event_log(result.replay_bundle, from_step=1)
        self.assertEqual(len(replay_frames), 2)
        self.assertEqual(replay_frames[0]["step_index"], 1)

    def test_mcd_snapshot_round_trip(self) -> None:
        events, theta = whitepaper_truth_vs_harm_events()
        for index, event in enumerate(events):
            event.request_id = "req-mcd"
            event.timestamp = float(index)
            event.meta.update(
                {
                    "tau_true": str(0.65 + 0.03 * index),
                    "fisher_rao_delta": str(0.10 + 0.05 * index),
                    "nli_sigma": "0.01",
                }
            )

        result = audit_dialogue(events, scalarizer_config=theta)

        scratch_dir = Path(__file__).resolve().parents[1] / "_mcd_test_output"
        scratch_dir.mkdir(exist_ok=True)
        for path in scratch_dir.glob("*.json"):
            path.unlink()

        paths = persist_snapshots(result.mcd_snapshots, scratch_dir)
        snapshots = load_snapshots(scratch_dir)
        replay = replay_snapshots(snapshots)

        self.assertEqual(len(paths), 3)
        self.assertEqual(len(snapshots), 3)
        self.assertEqual(len(replay), 3)
        self.assertEqual(replay[0]["event_id"], "evt_0")


if __name__ == "__main__":
    unittest.main()
