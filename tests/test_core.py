from __future__ import annotations

import unittest
from pathlib import Path

from ethiccaculate.audit import audit_dialogue, audit_dialogue_multi
from ethiccaculate.benchmarks import load_benchmark_suite
from ethiccaculate.decoder import DecoderConfig, decode_bcg_to_geom
from ethiccaculate.examples import multi_system_sensitive_case_events, whitepaper_truth_vs_harm_events
from ethiccaculate.models import BCGVector
from ethiccaculate.operations import apply_g_reframe_justice, apply_h_boundary_set
from ethiccaculate.principles import default_principles
from ethiccaculate.profiles import load_builtin_moral_system_profiles
from ethiccaculate.spectral import ScalarizerConfig, spectral_from_blocks, total_scalar_energy, total_spectral_energy


class CoreModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.project_root = Path(__file__).resolve().parents[1]

    def test_bcg_decoder_v0_1(self) -> None:
        block = decode_bcg_to_geom(BCGVector(B=0.8, C=0.9, G=0.4), DecoderConfig(A=100.0, B0=100.0))
        self.assertAlmostEqual(block.L, 80.0)
        self.assertAlmostEqual(block.a, 50.0)
        self.assertAlmostEqual(block.b, -20.0)

    def test_parseval_identity_and_u_bounds(self) -> None:
        events, theta = whitepaper_truth_vs_harm_events()
        state = events[0].blocks
        assert state is not None
        spectral = spectral_from_blocks(state, theta)
        self.assertAlmostEqual(total_scalar_energy(state, theta), total_spectral_energy(spectral), places=7)
        self.assertGreaterEqual(spectral.U, -1.0)
        self.assertLessEqual(spectral.U, 1.0)

    def test_whitepaper_example_matches_pdf_numbers(self) -> None:
        theta = ScalarizerConfig(L=0.0, a=1.0, b=0.0, A=1.0, B=1.0)
        blocks0 = whitepaper_truth_vs_harm_events()[0][0].blocks
        assert blocks0 is not None

        spectral0 = spectral_from_blocks(blocks0, theta)
        blocks1 = apply_g_reframe_justice(blocks0, eta=0.5, scalarizer=theta)
        spectral1 = spectral_from_blocks(blocks1, theta)
        blocks2 = apply_h_boundary_set(blocks1, delta=0.3, scalarizer=theta)
        spectral2 = spectral_from_blocks(blocks2, theta)

        self.assertAlmostEqual(spectral0.U, -0.804878, places=5)
        self.assertAlmostEqual(spectral1.U, -0.396226, places=5)
        self.assertAlmostEqual(spectral2.U, 0.168539, places=5)

    def test_audit_dialogue_produces_states_moves_and_replay(self) -> None:
        events, theta = whitepaper_truth_vs_harm_events()
        result = audit_dialogue(events, principles=default_principles(), scalarizer_config=theta)

        self.assertEqual(len(result.states), 3)
        self.assertEqual([move.op for move in result.moves], ["G_REFRAME_JUSTICE", "H_BOUNDARY_SET"])
        self.assertEqual(len(result.replay_bundle["gate_report"]), 3)
        # ConstructiveHonesty now requires BOTH high distortion AND low Esyn (all, not any).
        # The whitepaper events have truth_distortion=0 throughout, so only Helpfulness fires.
        self.assertEqual(len(result.violations), 2)

    def test_builtin_profiles_load(self) -> None:
        profiles = load_builtin_moral_system_profiles()
        ids = {profile.system_id for profile in profiles}
        self.assertIn("omega_public_reasoning", ids)
        self.assertIn("kantian_core", ids)
        self.assertIn("utilitarian_core", ids)
        self.assertIn("care_ethics_core", ids)

    def test_multi_system_audit_returns_conflicts(self) -> None:
        profiles = load_builtin_moral_system_profiles()
        events = multi_system_sensitive_case_events()
        result = audit_dialogue_multi(events, profiles=profiles)

        self.assertEqual(set(result.audit_by_system.keys()), {profile.system_id for profile in profiles})
        self.assertGreaterEqual(len(result.cross_system_conflicts), 1)
        self.assertIn(
            "NoFalseCertainty",
            [violation.principle for violation in result.audit_by_system["kantian_core"].audit_result.violations],
        )
        self.assertIn(
            "MinimizeExpectedHarm",
            [violation.principle for violation in result.audit_by_system["utilitarian_core"].audit_result.violations],
        )

    def test_omb24_benchmark_loads_with_expected_distribution(self) -> None:
        benchmark_path = self.project_root / "benchmarks" / "dev" / "omb24.json"
        suite = load_benchmark_suite(benchmark_path)

        self.assertEqual(suite.benchmark_id, "OMB-24")
        self.assertEqual(len(suite.cases), 24)

        counts: dict[str, int] = {}
        for case in suite.cases:
            counts[case.category] = counts.get(case.category, 0) + 1

        self.assertEqual(counts["honesty"], 8)
        self.assertEqual(counts["harmlessness"], 8)
        self.assertEqual(counts["fairness_bias"], 8)

        fairness_cases = [case for case in suite.cases if case.category == "fairness_bias"]
        self.assertTrue(all(case.pair_expectation is not None for case in fairness_cases))
        self.assertTrue(all(case.expected_common.expected_gate.write_gate is True for case in fairness_cases))

    def test_omb_holdout24_loads_with_expected_distribution_and_disjoint_ids(self) -> None:
        dev_suite = load_benchmark_suite(self.project_root / "benchmarks" / "dev" / "omb24.json")
        holdout_suite = load_benchmark_suite(self.project_root / "benchmarks" / "holdout" / "omb_holdout24.json")

        self.assertEqual(holdout_suite.benchmark_id, "OMB-Holdout-24")
        self.assertEqual(len(holdout_suite.cases), 24)
        self.assertIn("holdout", holdout_suite.metadata.get("recommended_use", []))

        counts: dict[str, int] = {}
        for case in holdout_suite.cases:
            counts[case.category] = counts.get(case.category, 0) + 1

        self.assertEqual(counts["honesty"], 8)
        self.assertEqual(counts["harmlessness"], 8)
        self.assertEqual(counts["fairness_bias"], 8)

        fairness_cases = [case for case in holdout_suite.cases if case.category == "fairness_bias"]
        self.assertTrue(all(case.pair_expectation is not None for case in fairness_cases))
        self.assertTrue(all(case.expected_common.expected_gate.write_gate is True for case in fairness_cases))
        self.assertTrue(
            {case.case_id for case in dev_suite.cases}.isdisjoint({case.case_id for case in holdout_suite.cases})
        )


if __name__ == "__main__":
    unittest.main()
