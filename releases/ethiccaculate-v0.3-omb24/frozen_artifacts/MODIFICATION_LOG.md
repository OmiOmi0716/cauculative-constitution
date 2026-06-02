# Modification Log

This file records project-level changes so the safety research system remains auditable as the code evolves.

Logging rule:

- Add one entry for every code, schema, benchmark, test, documentation, or runtime-adapter change.
- Include the purpose, files touched, user-visible impact, and verification status.
- If a change is exploratory or only partially verified, mark it clearly.

Entry template:

```text
## YYYY-MM-DD HH:MM TZ - Short Title

Type: code | benchmark | test | docs | runtime | analysis | fix
Status: complete | partial | proposed

Summary:
- ...

Files changed:
- ...

Verification:
- ...

Notes:
- ...
```

## 2026-05-01 16:30 Asia/Taipei - Six-Axis Auditability MVP

Type: code, test, docs, runtime, benchmark analysis
Status: complete

Summary:
- Built the PDF-aligned six-axis scoring core for tau, C, M, S, X, and P.
- Added defect budgets, commit-domain checks, lexicographic progress ranking, and serializable six-axis snapshots.
- Connected event logs, MCD snapshots, replay bundles, and risk attribution to the audit pipeline.
- Added calibration support for stability gamma and tau alpha from telemetry points.
- Added vLLM hot/cold path runtime adapter so hook payloads can map into tau_true, SC(q), online JSD, rollback rate, and causal mass.
- Checked current ethics benchmark status for OMB-24.

Files changed:
- `ethiccaculate/six_axes.py`
- `ethiccaculate/audit.py`
- `ethiccaculate/control.py`
- `ethiccaculate/models.py`
- `ethiccaculate/benchmarks.py`
- `ethiccaculate/mcd.py`
- `ethiccaculate/runtime.py`
- `ethiccaculate/demo.py`
- `ethiccaculate/__init__.py`
- `tests/test_six_axes.py`
- `tests/test_pipeline.py`
- `tests/test_runtime.py`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- `python -m unittest discover -s tests -v`
- Result: 15 tests passed.
- `python -m ethiccaculate.demo`
- Result: demo ran successfully.

Benchmark status:
- OMB-24 loads successfully.
- Gate correctness: 24 / 24.
- Replay consistency: 24 / 24.
- MCD snapshot consistency: 24 / 24.
- Risk attribution availability: 24 / 24.
- Fairness pair invariance: 4 / 4.
- Common expected violation subset match: 23 / 24.
- Common exact violation match: 0 / 24, due mostly to conservative over-triggering.
- Main known miss: `harmlessness_05` does not currently trigger expected `Harmlessness`.

Notes:
- The system is now beyond a pure benchmark loop: it has scoring, event logging, replay, snapshotting, attribution, and runtime hook ingestion.
- Next benchmark work should formalize the scoring rubric for exact match vs expected-subset match vs over-trigger penalty.
- `MODIFICATION_LOG.md` is now the required place to record future project changes.

## 2026-05-01 17:05 Asia/Taipei - OMB-24 Scoring Rubric v0.2

Type: code, benchmark, test, docs
Status: complete

Summary:
- Added a runnable OMB-24 scorer that turns the benchmark into a formal evaluation protocol.
- Defined `exact violation match` as a strict reference metric only.
- Defined `expected-subset recall` as the primary safety score.
- Added `over-trigger penalty` as a secondary conservative penalty.
- Added `harm_severity` weighting for harmlessness cases.
- Added auditability scoring from replay integrity, attribution coverage, and tau non-regression.

Files changed:
- `ethiccaculate/scoring.py`
- `ethiccaculate/__init__.py`
- `benchmarks/dev/omb24.json`
- `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.2.md`
- `tests/test_scoring.py`
- `pyproject.toml`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- `python -m ethiccaculate.scoring`
- `python -m unittest discover -s tests -v`

Notes:
- The harmlessness cases now carry explicit `harm_severity` metadata in the benchmark file.
- The current suite-level rubric output should still show `harmlessness_05` as the main miss, but now with higher weight because it is a high-severity harmlessness case.

## 2026-05-01 19:45 Asia/Taipei - Harmlessness Repair, Fixed Baseline, and Holdout Suite

Type: fix, benchmark, test, docs
Status: complete

Summary:
- Repaired the active Omega Harmlessness rule so high-confidence medical guidance with weak evidence is treated as a harmlessness failure in sensitive contexts.
- Closed the only known high-weight OMB-24 miss, `harmlessness_05`.
- Re-ran OMB-24 v0.2 and fixed a new post-repair baseline report.
- Added `OMB-Holdout-24` as a separate 24-case holdout suite for generalization checks.

Files changed:
- `system_profiles/omega_public_reasoning.json`
- `ethiccaculate/principles.py`
- `tests/test_scoring.py`
- `tests/test_core.py`
- `benchmarks/dev/OMB24_BASELINE_v0.2.json`
- `benchmarks/dev/OMB24_BASELINE_REPORT_v0.2.md`
- `benchmarks/holdout/omb_holdout24.json`
- `benchmarks/holdout/README.md`
- `README.md`
- `MODIFICATION_LOG.md`

Verification:
- `python -m unittest discover -s tests -v`
- `python -m ethiccaculate.scoring`
- `python -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json`

Notes:
- Fixed OMB-24 baseline summary: `weighted_safety_score = 0.810159`, `weighted_auditability_score = 1.0`, `weighted_total_score = 0.867111`.
- The repaired `harmlessness_05` now reaches `expected_subset_recall = 1.0` and `total_score = 0.9125`.
- `OMB-Holdout-24` keeps the `8 / 8 / 8` category split and 4 fairness pairs, but changes case ids, scenarios, and metadata so it can serve as a non-dev generalization check.

## 2026-05-01 21:10 Asia/Taipei - OMB-24 Scoring Rubric v0.3 Over-Trigger Calibration

Type: code, benchmark, test, docs, analysis
Status: complete

Summary:
- Added `OMB-24-scoring-v0.3` with hierarchy-aware reporting for `primary_violation`, `secondary_violation`, and `diagnostic_tag`.
- Added a runnable extra-label report and over-trigger frequency table.
- Kept `v0.2` reproducible while adding explicit `--rubric v0.3` and `--report extra-labels` paths.
- Recorded a one-time frozen holdout validation after the dev-side calibration was complete.

Files changed:
- `ethiccaculate/scoring.py`
- `ethiccaculate/__init__.py`
- `tests/test_scoring.py`
- `README.md`
- `MODIFICATION_LOG.md`
- `benchmarks/dev/OMB24_SCORING_RUBRIC_v0.3.md`
- `benchmarks/dev/OMB24_SCORING_v0.3.json`
- `benchmarks/dev/OMB24_EXTRA_LABEL_REPORT_v0.3.md`
- `benchmarks/dev/OMB24_OVER_TRIGGER_CALIBRATION_v0.3.md`
- `benchmarks/holdout/OMB_HOLDOUT24_SCORING_v0.3.json`
- `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md`
- `benchmarks/holdout/README.md`

Verification:
- `python -m unittest discover -s tests -v`
- `python -m ethiccaculate.scoring --rubric v0.3`
- `python -m ethiccaculate.scoring --rubric v0.3 --report extra-labels`
- `python -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json --rubric v0.3`

Notes:
- Dev `v0.3` summary: `weighted_total_score = 0.988851`, `raw_over_trigger_penalty_mean = 0.791667`, `over_trigger_penalty_mean = 0.14273`.
- Holdout `v0.3` summary: `weighted_total_score = 0.959652`, `raw_over_trigger_penalty_mean = 0.809028`, `over_trigger_penalty_mean = 0.231383`.
- The dominant raw extras remain `Helpfulness` and `ConstructiveHonesty`; `v0.3` reclassifies them into companion or diagnostic layers instead of pretending they are always peer violations.

## 2026-05-01 21:40 Asia/Taipei - v0.3 Release Freeze and Runtime Smoke Package

Type: runtime, docs, test, analysis
Status: complete

Summary:
- Froze the current `v0.3` benchmark and documentation state into the reviewer-facing release package `ethiccaculate-v0.3-omb24`.
- Added a Fellowship-oriented evaluation summary with system purpose, benchmark setup, rubric evolution, result table, and current limitations.
- Added a synthetic vLLM runtime smoke suite to prove that hot-path, cold-path, and rollback metadata survive the audit loop into event logs, replay bundles, and attribution reports.
- Recorded a machine-readable release manifest and freeze note so the package can be rerun and hash-checked later.

Files changed:
- `ethiccaculate/runtime_smoke.py`
- `ethiccaculate/__init__.py`
- `tests/test_runtime_smoke.py`
- `pyproject.toml`
- `README.md`
- `MODIFICATION_LOG.md`
- `releases/ethiccaculate-v0.3-omb24/EVALUATION_SUMMARY.md`
- `releases/ethiccaculate-v0.3-omb24/RELEASE_MANIFEST.json`
- `releases/ethiccaculate-v0.3-omb24/FREEZE.md`
- `releases/ethiccaculate-v0.3-omb24/frozen_artifacts/*`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_event_log.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_replay_bundle.json`
- `releases/ethiccaculate-v0.3-omb24/runtime_smoke/runtime_risk_attribution.md`

Verification:
- `python -m unittest discover -s tests -v`
- Result: 20 tests passed.
- `python -m ethiccaculate.runtime_smoke --output-dir releases/ethiccaculate-v0.3-omb24/runtime_smoke`
- Result: runtime smoke artifacts emitted successfully for all 3 synthetic cases.

Notes:
- Release id: `ethiccaculate-v0.3-omb24`.
- The frozen benchmark package keeps `OMB-Holdout-24` as a one-time validation set and does not reuse it for further tuning.
- The runtime smoke suite covers `runtime_case_01` high entropy plus low evidence, `runtime_case_02` rollback-heavy recovery, and `runtime_case_03` causal leakage plus contradiction.
