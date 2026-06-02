# Agent Governance Sandbox

This directory is a sandbox for agent ethics management. It is not part of the frozen v0.3 benchmark evidence, does not introduce new scores, and does not modify the main `ethiccaculate` package, current scoring rules, benchmark data, tests, or release artifacts.

The sandbox explores how the existing ethics audit stack can support an Agentic RL Loop style management layer:

- `Self`: identity continuity, drift, self-reflection, self-repair
- `Social`: peer review, trust, collaboration, collusion risk, human anchoring
- `Mission`: task execution, verifier feedback, boundary violations, rollback, recovery
- `Human Anchoring`: human critique, dispute, correction, escalation
- `Six-axis diagnostics`: C / S / X / P / tau / M as cross-cutting trace telemetry

## What This Is

This is a v0.4 seed for agent ethics management. It shows how agent events can be recorded, mapped into six-axis diagnostic state, scored with sandbox-only heuristics, and replayed for human review.

## What This Is Not

- Not current v0.3 evidence.
- Not a formal benchmark.
- Not a new scoring rule.
- Not full RL or model training.
- Not production agent governance.
- Not a replacement for human review.

## Files

- `SANDBOX_SCOPE.md`: sandbox boundary and source alignment.
- `AGENT_ETHICS_MANAGEMENT_SOURCE_MAP_v0.1.md`: maps the ethics audit stack and Agentic RL Loop whitepapers.
- `AGENT_GOVERNANCE_OVERVIEW_v0.1.md`: high-level governance framing.
- `TRACE_SCHEMA_v0.1.md`: event and metadata schema notes.
- `SOUL_PROFILE_SPEC_v0.1.md`: proposed `SOUL.md` self-governance profile format.
- `SOUL.md`: sandbox example of a readable and machine-readable agent governance profile.
- `COLLUSION_RESISTANCE_NOTE_v0.1.md`: sandbox note for detecting suspicious multi-agent agreement.
- `AGENT_GOV_MINI_BM_v0.1.md`: sandbox-only mini-benchmark specification for six agent governance cases.
- `AGENT_GOV_BASELINE_COMPARISON_v0.1.md`: sandbox comparison of plain agent logs, trace replay, six-axis trace, and full governance.
- `CLEAR_STYLE_AGENT_EVAL_v0.1.md`: sandbox CLEAR-style evaluation note for Cost / Latency / Efficacy / Assurance / Reliability.
- `mini_benchmark_cases.json`: case data for Agent-Gov-Mini-6.
- `schemas.py`: local dataclasses for agent events, traces, and six-axis state.
- `six_axis_adapter.py`: sandbox mapping from agent event metadata to six-axis diagnostics.
- `scorers.py`: sandbox-only heuristic Self / Social / Mission scoring.
- `soul_profile.py`: sandbox-only loader and evaluator for `SOUL.md`.
- `anti_collusion.py`: sandbox-only checks for private-to-public convergence and weak-evidence consensus.
- `run_mini_benchmark.py`: sandbox-only runner for Agent-Gov-Mini-6.
- `run_baseline_comparison.py`: sandbox-only baseline comparison runner.
- `run_clear_style_eval.py`: sandbox-only CLEAR-style local evaluation runner.
- `run_bazaarlink_api_probe.py`: optional BazaarLink API probe that reads the key from `BAZAARLINK_API_KEY`.
- `event_log.py`: JSONL helpers for local traces.
- `replay.py`: replay summary and Markdown rendering.
- `demo_agent_ethics_loop.py`: example trace replay.
- `smoke_check.py`: minimal sanity check for build / score / replay.
- `soul_smoke_check.py`: minimal sanity check for `SOUL.md` profile loading and threshold review.
- `collusion_smoke_check.py`: minimal sanity check for suspicious agreement detection.
- `MODIFICATION_LOG.md`: sandbox-only change log for agent governance additions.
- `APPLICATION_NARRATIVE_SNIPPET_v0.1.md`: short application wording for this sandbox.

## Run The Demo

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\demo_agent_ethics_loop.py
```

## Run The Smoke Check

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\smoke_check.py
```

Expected result:

```text
AGENT_GOVERNANCE_SANDBOX_SMOKE_OK
```

## Run The SOUL Profile Smoke Check

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\soul_smoke_check.py
```

Expected result:

```text
AGENT_GOVERNANCE_SOUL_SMOKE_OK
```

## Run The Anti-Collusion Smoke Check

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\collusion_smoke_check.py
```

Expected result:

```text
AGENT_GOVERNANCE_COLLUSION_SMOKE_OK
```

## Run The Agent Governance Mini-Benchmark

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\run_mini_benchmark.py
```

Expected result:

```text
AGENT_GOV_MINI_BM_OK
case_count=6
passed=6
failed=0
```

## Run The Baseline Comparison

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\run_baseline_comparison.py
```

Expected result:

```text
AGENT_GOV_BASELINE_COMPARISON_OK
cases=6
```

## Run The CLEAR-Style Local Eval

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\run_clear_style_eval.py
```

Expected result:

```text
CLEAR_STYLE_AGENT_EVAL_OK
cases=6
repeats=3
efficacy=1.000
assurance=1.000
reliability_pass_3=1.000
cost_mode=local_no_api_not_token_metered
```

## Optional BazaarLink API Probe

Do not paste API keys into files. From the repo root:

```powershell
$env:BAZAARLINK_API_KEY = Read-Host "Paste BazaarLink API key"
python agent_governance\run_bazaarlink_api_probe.py
Remove-Item Env:\BAZAARLINK_API_KEY
```

Expected result if the key works:

```text
BAZAARLINK_API_PROBE_OK
```

## Reviewer Boundary

This sandbox should be read as a future implementation seed. It demonstrates that the current audit architecture can be extended toward agent ethics management, but it should not be cited as frozen benchmark evidence or external validation.
