from __future__ import annotations

import json
import unittest

from ethiccaculate.audit import audit_dialogue
from ethiccaculate.examples import whitepaper_truth_vs_harm_events
from ethiccaculate.runtime import (
    jensen_shannon_divergence,
    runtime_meta_from_vllm_payloads,
    telemetry_from_vllm_payloads,
)


class RuntimeHookAdapterTests(unittest.TestCase):
    def test_vllm_payloads_map_to_six_axis_telemetry(self) -> None:
        hot = {
            "topk_probs": [0.72, 0.18, 0.10],
            "baseline_topk_probs": [0.40, 0.35, 0.25],
            "generated_tokens": 45,
            "target_tokens": 100,
            "previous_entropy": 1.20,
            "hidden_delta_norm": 0.08,
            "attention_leak_by_layer": [0.01, 0.03, 0.08],
            "hidden_cov_det": 1.25,
            "baseline_hidden_cov_det": 1.0,
            "hidden_dim": 4,
            "queue_delay_ms": 12,
            "inference_delay_ms": 40,
        }
        cold = {
            "atomic_facts_supported": 8,
            "atomic_facts_total": 10,
            "nli_contradiction_score": 0.22,
            "nli_sigma": 0.03,
            "consensus_cluster_sizes": [6, 2, 2],
            "consensus_sample_count": 10,
        }
        rollback = {
            "rollback_depth_tokens": 16,
            "kv_block_size_bytes": 4096,
            "tokens_per_block": 16,
            "memory_bandwidth": 1024,
            "rollback_detect_ms": 10,
            "rollback_evict_ms": 20,
            "rollback_recompute_ms": 50,
            "leak_gradient_norm": 0.4,
        }

        telemetry = telemetry_from_vllm_payloads(hot, cold, rollback)

        self.assertGreater(jensen_shannon_divergence((0.72, 0.18, 0.10), (0.40, 0.35, 0.25)), 0.0)
        self.assertGreater(telemetry.online_jsd or 0.0, 0.0)
        self.assertAlmostEqual(telemetry.tau_true or 0.0, 0.8)
        self.assertAlmostEqual(telemetry.self_consistency_score or 0.0, 0.6)
        self.assertEqual(telemetry.rollback_depth_tokens, 16)
        self.assertEqual(telemetry.token_kv_bytes, 256)
        self.assertAlmostEqual(telemetry.queue_delay, 0.012)

        meta = runtime_meta_from_vllm_payloads(hot, cold, rollback)
        self.assertEqual(meta["runtime_source"], "vllm_hooks")
        self.assertIn("online_jsd", meta)
        self.assertIn("tau_true", meta)
        self.assertIn("rollback_depth_tokens", meta)

    def test_audit_pipeline_ingests_raw_vllm_hook_meta(self) -> None:
        events, theta = whitepaper_truth_vs_harm_events()
        for index, event in enumerate(events):
            event.request_id = "req-vllm"
            event.timestamp = float(index)

        events[1].meta.update(
            {
                "vllm_hot_path": json.dumps(
                    {
                        "topk_probs": [0.70, 0.20, 0.10],
                        "baseline_topk_probs": [0.45, 0.30, 0.25],
                        "generated_tokens": 30,
                        "target_tokens": 60,
                        "attention_leak_by_layer": [0.02, 0.04, 0.10],
                        "hidden_delta_norm": 0.07,
                        "queue_delay_ms": 8,
                        "inference_delay_ms": 21,
                    }
                ),
                "vllm_cold_path": json.dumps(
                    {
                        "tau_true": 0.74,
                        "nli_contradiction_score": 0.26,
                        "nli_sigma": 0.02,
                        "consensus_cluster_sizes": [5, 3, 2],
                        "consensus_sample_count": 10,
                    }
                ),
                "vllm_rollback": json.dumps(
                    {
                        "rollback_depth_tokens": 12,
                        "token_kv_bytes": 128,
                        "memory_bandwidth": 512,
                        "rollback_detect_ms": 5,
                        "rollback_evict_ms": 10,
                        "rollback_recompute_ms": 25,
                        "leak_gradient_norm": 0.5,
                    }
                ),
            }
        )

        result = audit_dialogue(events, scalarizer_config=theta)
        runtime_frame = result.event_log[1]
        telemetry = runtime_frame["telemetry"]
        assessment = runtime_frame["assessment"]

        self.assertAlmostEqual(telemetry["tau_true"], 0.74)
        self.assertGreater(telemetry["online_jsd"], 0.0)
        self.assertEqual(tuple(telemetry["consensus_cluster_sizes"]), (5, 3, 2))
        self.assertGreater(assessment["hot_path_metrics"]["rollback_rate"], 0.0)
        self.assertAlmostEqual(assessment["cold_path_metrics"]["self_consistency_score"], 0.5)
        self.assertGreater(assessment["axes"]["C"]["signals"]["rollback_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
