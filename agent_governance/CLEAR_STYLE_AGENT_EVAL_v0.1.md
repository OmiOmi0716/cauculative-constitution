# CLEAR-Style Agent Evaluation v0.1

This document is a sandbox-only CLEAR-style evaluation note for `agent_governance/`. It is not the original CLEAR Enterprise Task Suite, is not part of the frozen v0.3 benchmark evidence, does not introduce official benchmark scores, and does not modify the main ethiccaculate scoring rules, benchmark data, tests, or release artifacts.

## 1. Purpose

CLEAR-style evaluation helps position the agent governance sandbox against a known agent-evaluation direction:

```text
CLEAR = Cost, Latency, Efficacy, Assurance, Reliability
```

The current sandbox does not need an external API to run this evaluation. It uses the local Agent-Gov-Mini-6 cases and measures local execution behavior.

## 2. API Boundary

No API key is required for the current sandbox evaluation.

The current runner measures:

- local latency
- case pass rate as efficacy
- governance review routing as assurance
- repeated-run stability as reliability
- API cost status as not metered

It does not measure real model token cost, provider billing, network latency, or live agent API behavior.

Future API-backed evaluation could add:

- token input / output counts
- cost per case
- cost per successful case
- provider latency
- retry count
- tool-call cost
- external agent result variance

## 3. CLEAR Mapping

| CLEAR Dimension | Current Sandbox Mapping | Current Status |
| --- | --- | --- |
| Cost | API calls and token cost are reported as not metered | local-only proxy |
| Latency | wall-clock runtime per case across repeats | measured locally |
| Efficacy | Agent-Gov-Mini-6 pass rate | measured |
| Assurance | expected risky cases routed to review | measured |
| Reliability | repeated pass consistency across N runs | measured |

## 4. Run Command

From the repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python agent_governance\run_clear_style_eval.py
```

Expected key result:

```text
CLEAR_STYLE_AGENT_EVAL_OK
cases=6
repeats=3
efficacy=1.000
assurance=1.000
reliability_pass_3=1.000
cost_mode=local_no_api_not_token_metered
```

## 5. Interpretation

This evaluation shows that the local agent governance sandbox can be assessed beyond a single accuracy-like pass/fail number.

It reports whether the cases pass, whether risky cases route to review, whether results are stable across repeated runs, and how long the local evaluator takes.

This is useful for reviewer communication because it aligns the sandbox with multidimensional agent evaluation while preserving honest scope boundaries.

## 6. Limitation

The current evaluation is local and deterministic. It does not test stochastic LLM agents, real tool calls, real enterprise workflows, real token cost, or external model reliability.

It should be read as a v0.4 seed evaluation adapter, not as external validation.

