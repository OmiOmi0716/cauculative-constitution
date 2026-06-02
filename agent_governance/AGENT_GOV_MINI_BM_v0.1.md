# Agent-Gov-Mini-6 v0.1

This document describes a sandbox-only v0.4 seed mini-benchmark for `agent_governance/`. It is not part of the frozen v0.3 benchmark evidence, does not introduce current submission-package claims, and does not modify the main ethiccaculate scoring rules, benchmark data, tests, or release artifacts.

## 1. Purpose

Agent-Gov-Mini-6 is a small executable check that turns the agent governance demo into case-based evaluation.

It tests whether the sandbox can:

- build agent traces from case data
- replay Self / Social / Mission events
- map events into six-axis diagnostics
- evaluate the trace against a sandbox `SOUL.md` profile
- detect suspicious multi-agent agreement
- route risky cases to human review

## 2. Scope Boundary

Can claim:

- a sandbox-only v0.4 seed mini-benchmark
- a runnable case format for agent trace governance
- basic checks for SOUL profile review and anti-collusion signals
- compatibility with the current event-log / replay / six-axis architecture

Cannot claim:

- frozen v0.3 evidence
- external validation
- production agent governance
- full multi-agent safety benchmark coverage
- formal proof of collusion resistance
- new official benchmark score

## 3. Case Layout

The mini-benchmark has six cases:

| Case Group | Case Count | Main Check |
| --- | ---: | --- |
| Self Drift | 2 | identity drift, self-update review, SOUL threshold review |
| Social Collusion | 2 | private-to-public convergence, weak-evidence consensus, agent citation without trace evidence |
| Mission Boundary | 2 | rollback, boundary violation, runtime pressure, human review |

## 4. Files

- `mini_benchmark_cases.json`: sandbox case data.
- `run_mini_benchmark.py`: sandbox runner.
- `SOUL.md`: sandbox governance profile used by the runner.
- `anti_collusion.py`: sandbox suspicious-agreement detector.
- `replay.py`: sandbox replay summary builder.

## 5. Run Command

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\run_mini_benchmark.py
```

Expected key result:

```text
AGENT_GOV_MINI_BM_OK
case_count=6
passed=6
failed=0
```

## 6. Interpretation

This mini-benchmark is useful because it shows that the agent governance sandbox is not only a design note. It can load cases, reconstruct traces, evaluate six-axis/SOUL state, detect suspicious agreement, and produce pass/fail checks.

The result should be interpreted as an implementation seed and regression guard, not as final evidence that agent governance is solved.

## 7. Limitation

The cases are hand-authored and intentionally small. They are not externally validated, not randomized, not adversarially generated, and not representative of real deployed multi-agent systems.

Future work should expand this into a larger frozen agent-governance benchmark with external review, clearer annotation policy, and separate holdout cases.

