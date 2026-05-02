# ethiccaculate

`ethiccaculate` is a Python v0.3 implementation of the Omega ethics audit whitepaper source material, with a focus on making ethics profiles executable, replayable, auditable, rollback-friendly, and reproducible as a research package.

This project focuses on the parts of the whitepaper that are concrete enough to run:

- B-C-G to WCSMF decoding
- four-block scalarization and Walsh-Hadamard spectral analysis
- six-axis control estimation and gate rules
- Omega-EIR style state, move, violation, and replay records
- a minimal dialogue audit loop
- a heuristic alternative-program search
- multi-system moral profiles with cross-system comparison

## Quick Start

Recommended Python:

```powershell
C:\ethiccaculate\.venv\Scripts\python.exe
```

Run the demo:

```powershell
& 'C:\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.demo
```

Run the tests:

```powershell
& 'C:\ethiccaculate\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```

Run the OMB-24 rubric scorer:

```powershell
& 'C:\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring --rubric v0.2
```

Run the OMB-24 over-trigger calibration scorer:

```powershell
& 'C:\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring --rubric v0.3
```

Run the extra-label report:

```powershell
& 'C:\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring --rubric v0.3 --report extra-labels
```

Run the holdout scorer:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json --rubric v0.3
```

Run the vLLM runtime smoke test:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.runtime_smoke --output-dir 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\releases\ethiccaculate-v0.3-omb24\runtime_smoke'
```

Build and score the TruthfulQA-mini external subset:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.truthfulqa_mini
```

Build and score the BBQ-mini external subset:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.bbq_mini
```

Run the six-axis ablation report:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.ablation
```

Run the comparative audit minis:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.comparative_audit
```

Run the comparative baseline report:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.comparative_baseline
```

Build and freeze Ethics-Audit-Core-128:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.core128
```

## Modification Log

Project changes are tracked in `MODIFICATION_LOG.md`. Update it whenever code, tests, benchmark data, runtime adapters, or documentation changes.

## Submission Package

Reviewer-facing submission documents:

- `PROPOSAL_DRAFT.md`: current proposal draft for the submission package
- `EXECUTIVE_SUMMARY.md`: one-page project summary, evidence, scope, and fellowship goal
- `EVIDENCE_MATRIX.md`: claim-to-evidence table with results and limitations
- `CLAIMS_AND_LIMITATIONS.md`: explicit boundary between supported claims and non-claims
- `REPRODUCIBILITY.md`: commands and expected outputs for rerunning the evidence layers
- `AUDIT_TEST_SPEC_v0.1.md`: future audit-test protocol draft for state reconstruction, violation detection, replay consistency, and public deliberation quality
- `R_LAYER_DESIGN_NOTE_v0.1.md`: future architecture note for an independent non-optimizable red-line safety layer outside the six-axis loop
- `NON_PUNITIVE_GOVERNANCE_NOTE_v0.1.md`: governance clarification note stating that the audit stack is for trace reconstruction, repair, human review, and system non-regression, not punishment, sentencing, or moral persecution

## Release Freeze

The current frozen research package is:

- `releases/ethiccaculate-v0.3-omb24`

Key release artifacts:

- evaluation summary: `releases/ethiccaculate-v0.3-omb24/EVALUATION_SUMMARY.md`
- release manifest: `releases/ethiccaculate-v0.3-omb24/RELEASE_MANIFEST.json`
- freeze note: `releases/ethiccaculate-v0.3-omb24/FREEZE.md`
- frozen benchmark and documentation copies: `releases/ethiccaculate-v0.3-omb24/frozen_artifacts/`
- runtime smoke outputs: `releases/ethiccaculate-v0.3-omb24/runtime_smoke/`

This freeze captures the `v0.3` OMB-24 dev scoring report, frozen holdout validation, modification history, and runtime oversight smoke-test outputs in one reviewer-facing bundle.

## Layout

- `ethiccaculate/models.py`: core dataclasses and audit result containers
- `ethiccaculate/benchmarks.py`: benchmark suite loader and schema
- `ethiccaculate/scoring.py`: OMB-24 scoring rubrics v0.2 / v0.3, hierarchy calibration, and extra-label reporting
- `ethiccaculate/decoder.py`: B-C-G to WCSMF decoder
- `ethiccaculate/spectral.py`: scalarization and spectral metrics
- `ethiccaculate/control.py`: six-axis estimators and gates
- `ethiccaculate/six_axes.py`: PDF-aligned six-axis defect functions, commit-domain checks, ranking, and snapshots
- `ethiccaculate/operations.py`: ISA move implementations
- `ethiccaculate/principles.py`: rule DSL and principle evaluation
- `ethiccaculate/profiles.py`: moral-system profile loader
- `ethiccaculate/audit.py`: single-system and multi-system audit loops
- `ethiccaculate/runtime.py`: vLLM hot/cold path hook adapter for six-axis telemetry
- `ethiccaculate/truthfulqa_mini.py`: TruthfulQA-mini external benchmark builder and scorer
- `ethiccaculate/bbq_mini.py`: BBQ-mini external fairness benchmark builder and scorer
- `ethiccaculate/ablation.py`: six-axis ablation runner for OMB-24 and external suites
- `ethiccaculate/comparative_audit.py`: cross-profile, cross-cultural, and multi-agent comparative audit suites
- `ethiccaculate/comparative_baseline.py`: baseline contrast for single-profile, siloed profiles, and full comparative execution
- `ethiccaculate/core128.py`: medium-scale 128-case benchmark assembler and one-shot baseline freezer
- `ethiccaculate/demo.py`: runnable demo
- `system_profiles/*.json`: built-in moral system packs
- `benchmarks/dev/omb24.json`: first-party 24-case development benchmark
- `benchmarks/external/truthfulqa_mini.json`: external 24-case TruthfulQA honesty subset
- `benchmarks/external/bbq_mini.json`: external 24-case BBQ fairness subset
- `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.md`: six-axis ablation report
- `benchmarks/comparative/*.md`: comparative audit reports for profile, cultural-context, and multi-agent comparisons
- `tests/test_core.py`: regression tests

## Add a New Moral System

The v0.2 path is profile-first. Most new systems should be added without changing the Python core.

1. Create a new JSON profile under `C:\ethiccaculate\system_profiles\`.
2. Define:
   - `system_id`
   - `version`
   - `objective_weights`
   - `gate_thresholds`
   - `allowed_moves` / `forbidden_moves`
   - `principles`
3. For each principle, provide `violation_rules` using the rule DSL.

Example:

```json
{
  "system_id": "my_ethics_pack",
  "version": "1.0.0",
  "name": "My Ethics Pack",
  "principles": [
    {
      "principle_id": "example_rule",
      "kind": "Prevention",
      "hard_constraint": true,
      "thresholds": {
        "max_C": 0.4
      },
      "repair_actions": ["EscalateHuman"],
      "violation_rules": [
        {
          "all": [
            { "path": "event.sensitive_context", "eq": true },
            { "path": "state.control.C", "gt_threshold": "max_C" }
          ],
          "reason": "Relational risk is too high in a sensitive context.",
          "severity": "high"
        }
      ]
    }
  ]
}
```

Available rule operators:

- `gt`, `gte`, `lt`, `lte`, `eq`, `neq`
- `gt_threshold`, `gte_threshold`, `lt_threshold`, `lte_threshold`, `eq_threshold`, `neq_threshold`
- `in`, `not_in`, `contains`, `exists`
- nested `all`, `any`, `not`

Common paths:

- `state.spectral.U`
- `state.spectral.Esyn`
- `state.spectral.Ecosyn`
- `state.control.C`
- `state.control.S`
- `state.control.tau`
- `state.control.M`
- `event.sensitive_context`
- `event.claimed_confidence`
- `event.evidence_coverage`
- `event.truth_distortion`

JSON works out of the box. YAML loading is also supported in the local `.venv`, where `PyYAML` is already installed.

## OMB-24

The project now includes a first-party seed benchmark at `C:\ethiccaculate\benchmarks\dev\omb24.json`.

OMB-24 contains:

- 8 `honesty` cases
- 8 `harmlessness` cases
- 8 `fairness_bias` cases

Its schema supports:

- `input_event_trace`
- common expectations
- per-system expectations
- demographic pair invariance checks
- replay/rollback-oriented scoring targets

OMB-24 now also has a formal scoring rubric at `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.2.md`.

The over-trigger-calibrated rubric is recorded at `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.3.md`.

The repaired post-fix baseline is recorded at `benchmarks/dev/OMB24_BASELINE_REPORT_v0.2.md`, with raw scorer output saved to `benchmarks/dev/OMB24_BASELINE_v0.2.json`.

The over-trigger calibration output is recorded at:

- `benchmarks/dev/OMB24_SCORING_v0.3.json`
- `benchmarks/dev/OMB24_EXTRA_LABEL_REPORT_v0.3.md`
- `benchmarks/dev/OMB24_OVER_TRIGGER_CALIBRATION_v0.3.md`

The rubric defines:

- `exact violation match` as a strict reference metric
- `expected-subset recall` as the main safety score
- `over-trigger penalty` as a secondary conservative penalty
- `harm_severity` weighting for harmlessness cases
- `replay`, `attribution`, and `tau` non-regression as auditability components

Current fixed baseline:

- `weighted_safety_score = 0.810159`
- `weighted_auditability_score = 1.0`
- `weighted_total_score = 0.867111`

Current over-trigger-calibrated dev summary:

- `weighted_safety_score = 0.984073`
- `weighted_auditability_score = 1.0`
- `weighted_total_score = 0.988851`
- `raw_over_trigger_penalty_mean = 0.791667`
- `over_trigger_penalty_mean = 0.14273`

`v0.3` adds:

- `primary_violation`
- `secondary_violation`
- `diagnostic_tag`
- extra-label frequency reporting
- hierarchy-aware over-trigger calibration without narrowing the base safety rules

The Fellowship-facing summary for this benchmark package is recorded at:

- `releases/ethiccaculate-v0.3-omb24/EVALUATION_SUMMARY.md`

It covers system purpose, benchmark setup, scoring evolution from `v0.2` to `v0.3`, dev versus holdout results, and current limitations.

## OMB-Holdout-24

The project now also includes `benchmarks/holdout/omb_holdout24.json`, a 24-case holdout suite with the same `8 / 8 / 8` category split as OMB-24.

Use it to test whether rule repairs generalize beyond the development benchmark. Do not tune thresholds or case heuristics on the holdout suite.

Current frozen `v0.3` validation:

- `weighted_safety_score = 0.94236`
- `weighted_auditability_score = 1.0`
- `weighted_total_score = 0.959652`
- validation note: `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md`

## TruthfulQA-mini

The project now also includes `benchmarks/external/truthfulqa_mini.json`, a 24-case external honesty subset derived from the official TruthfulQA `generation` split.

Important scope note:

- this is an **audit benchmark over known incorrect answers**
- it measures whether the audit pipeline detects and explains confident falsehoods
- it does **not** claim open-ended question answering accuracy on TruthfulQA

Current `v0.3` external summary:

- `weighted_safety_score = 1.0`
- `weighted_auditability_score = 1.0`
- `weighted_total_score = 1.0`
- `raw_over_trigger_penalty_mean = 0.666667`
- `over_trigger_penalty_mean = 0.0`

Key files:

- `benchmarks/external/truthfulqa_mini.json`
- `benchmarks/external/TRUTHFULQA_MINI_v0.3.json`
- `benchmarks/external/TRUTHFULQA_MINI_v0.3.md`

The subset is sourced from the official TruthfulQA dataset and paper:

- dataset: `https://huggingface.co/datasets/truthfulqa/truthful_qa`
- paper: `https://huggingface.co/papers/2109.07958`

## BBQ-mini

The project now also includes `benchmarks/external/bbq_mini.json`, a 24-case external fairness subset derived from the official BBQ benchmark.

Important scope note:

- this is an **audit benchmark over stereotype-aligned answer choices**
- it measures whether the audit pipeline detects and explains protected-attribute bias signals
- it does **not** claim end-to-end fairness across all deployment settings

Current `v0.3` external summary:

- `weighted_safety_score = 1.0`
- `weighted_auditability_score = 1.0`
- `weighted_total_score = 1.0`
- `raw_over_trigger_penalty_mean = 0.4`
- `over_trigger_penalty_mean = 0.0`

Key files:

- `benchmarks/external/bbq_mini.json`
- `benchmarks/external/BBQ_MINI_v0.3.json`
- `benchmarks/external/BBQ_MINI_v0.3.md`

The subset is sourced from the official BBQ dataset and paper:

- dataset: `https://huggingface.co/datasets/heegyu/bbq`
- paper: `https://huggingface.co/papers/2110.08193`
- github: `https://github.com/nyu-mll/BBQ`

## Six-Axis Ablation

The next evaluation layer is recorded at `benchmarks/ablation/SIX_AXIS_ABLATION_v0.1.md`.

It compares three modes:

- `No Six-Axis`
- `Observe Only`
- `Observe + Gate + Replay`

Current ablation summary:

- OMB-24 totals: `0.688851 -> 0.888851 -> 0.988851`
- TruthfulQA-mini totals: `0.7 -> 0.9 -> 1.0`

This report isolates the marginal contribution of six-axis observability and replay support while keeping raw violation detections fixed.

## Comparative Audit Minis

The project now also includes three comparative audit layers that reuse the same protocol across multiple ethics profiles:

- `Cross-Profile Audit Mini`: 10 benchmark-sourced cases spanning OMB-24, TruthfulQA-mini, and BBQ-mini
- `Cross-Cultural Audit Mini`: 8 culturally anchored cases covering Taipei, Boston, Mumbai, Nairobi, Tokyo, Sao Paulo, Berlin, and Dubai
- `Multi-Agent Audit Mini`: 8 multi-speaker traces covering planner/executor, tool/coordinator, reviewer, and escalation failures

Each comparative report emits:

- `profile_agreement_rate`
- `profile_conflict_count`
- `shared_violation_axes`
- `profile_specific_repair_actions`
- `agreement_matrix`

Current comparative summaries:

- `Cross-Profile Audit Mini`: `profile_agreement_rate = 0.891667`, `profile_conflict_count = 38`, shared axes `C` and `M`
- `Cross-Cultural Audit Mini`: `profile_agreement_rate = 0.869792`, `profile_conflict_count = 24`
- `Multi-Agent Audit Mini`: `profile_agreement_rate = 0.864583`, `profile_conflict_count = 24`, `mean_speaker_count = 2.125`

Comparative baseline summary:

- `Single Profile Only`: raw violations still visible, but `agreement_pairs_observed = 0`, `conflict_observable_cases = 0`
- `Profiles In Silos`: all four profiles run, but comparative structure remains latent, so `agreement_pairs_observed = 0`, `profile_specific_repair_cases = 0`
- `Full Comparative Layer`: `agreement_pairs_observed = 18`, `conflict_observable_cases = 26`, `profile_specific_repair_cases = 26`

These layers are meant to support the claim that different ethical systems can exchange, audit, replay, and compare judgments using the same event-log protocol rather than separate benchmark codepaths.

Key files:

- `benchmarks/comparative/cross_profile_audit_mini.json`
- `benchmarks/comparative/CROSS_PROFILE_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/CROSS_PROFILE_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/cross_cultural_audit_mini.json`
- `benchmarks/comparative/CROSS_CULTURAL_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/CROSS_CULTURAL_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/multi_agent_audit_mini.json`
- `benchmarks/comparative/MULTI_AGENT_AUDIT_MINI_REPORT.json`
- `benchmarks/comparative/MULTI_AGENT_AUDIT_MINI_REPORT.md`
- `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.json`
- `benchmarks/comparative/COMPARATIVE_BASELINE_v0.1.md`
- `artifacts/FELLOWSHIP_COMPARATIVE_EVALUATION_v0.1.md`

## Ethics-Audit-Core-128

The project now also includes a medium-scale benchmark package at `benchmarks/core128/`.

`Ethics-Audit-Core-128 v0.1` freezes `128` cases across eight blocks:

- `16` OMB-style honesty
- `16` OMB-style harmlessness
- `16` OMB-style fairness
- `16` TruthfulQA-derived audit
- `16` BBQ-derived audit
- `16` cross-profile
- `16` cross-cultural
- `16` multi-agent

Current baseline summary:

- `weighted_total_score = 0.990805`
- `weighted_auditability_score = 1.0`
- `event_log_success_rate = 1.0`
- `replay_success_rate = 1.0`
- `risk_attribution_coverage = 1.0`
- `expected_subset_recall = 1.0`
- `holdout_gap = 0.019687`
- `comparative_conflict_observable_rate = 1.0`

The benchmark is intentionally frozen after one pass. It does not modify the frozen `ethiccaculate-v0.3-omb24` release and does not retune scoring rules after baseline generation.

Key files:

- `benchmarks/core128/core128_schema.json`
- `benchmarks/core128/CORE128_SCHEMA.md`
- `benchmarks/core128/ethics_audit_core128.json`
- `benchmarks/core128/CORE128_SCORING_v0.1.json`
- `benchmarks/core128/CORE128_SCORING_v0.1.md`
- `benchmarks/core128/CORE128_COMPARATIVE_REPORT_v0.1.md`
- `benchmarks/core128/CORE128_FAILURE_ANALYSIS_v0.1.md`

## PDF-Aligned Six-Axis Path

The working copy also includes a newer six-axis path aligned to the April 2026 T-centered whitepaper and engineering appendices.

It adds:

- defect-driven axis evaluation instead of raw weighted sums
- `P6` commit-domain checks
- lexicographic progress ranking `rho_tau`
- serializable six-axis snapshots for audit/replay

You can inspect it in `ethiccaculate/six_axes.py`, or run the demo to see a synthetic spec-driven snapshot alongside the original whitepaper examples.

## vLLM Hook Runtime Path

Appendix J/K hot/cold path signals can now be attached directly to a `DialogueEvent` through JSON metadata. The audit loop expands these payloads into `SixAxisTelemetry`, then records them in the event log, MCD snapshots, replay bundle, and risk attribution.

Canonical metadata keys:

- `vllm_hot_path`: online runtime sample from logits / hidden-state / scheduler hooks.
- `vllm_cold_path`: async NLI or SC(q) result.
- `vllm_rollback`: KV-cache rollback or recovery trace.

Example:

```python
event.meta["vllm_hot_path"] = json.dumps({
    "topk_probs": [0.70, 0.20, 0.10],
    "baseline_topk_probs": [0.45, 0.30, 0.25],
    "generated_tokens": 30,
    "target_tokens": 60,
    "attention_leak_by_layer": [0.02, 0.04, 0.10],
    "queue_delay_ms": 8,
    "inference_delay_ms": 21,
})
event.meta["vllm_cold_path"] = json.dumps({
    "tau_true": 0.74,
    "nli_contradiction_score": 0.26,
    "consensus_cluster_sizes": [5, 3, 2],
    "consensus_sample_count": 10,
})
event.meta["vllm_rollback"] = json.dumps({
    "rollback_depth_tokens": 12,
    "token_kv_bytes": 128,
    "memory_bandwidth": 512,
    "rollback_detect_ms": 5,
    "rollback_evict_ms": 10,
    "rollback_recompute_ms": 25,
})
```

The adapter maps:

- hot path logits to `online_jsd`, `fisher_rao_delta`, entropy, and `T_t(v2.0)` proxy inputs.
- cold path NLI / SC(q) to `tau_true`, `nli_conflict_score`, `nli_sigma`, and self-consistency.
- rollback traces to `rollback_rate`, causal mass, and C-axis rollback attribution.

The frozen release also includes a synthetic runtime smoke suite with three cases:

- `runtime_case_01`: high entropy plus low evidence
- `runtime_case_02`: rollback-heavy recovery
- `runtime_case_03`: causal leakage plus contradiction

Frozen runtime outputs:

- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_event_log.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_replay_bundle.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_risk_attribution.md`
