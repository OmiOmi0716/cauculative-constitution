# Executive Summary

## Project

`ethiccaculate` is a runnable ethics-and-six-axis audit prototype for agentic AI behavior. It represents behavior as replayable event traces, maps risk into six-axis telemetry, scores violations with hierarchy-aware labels, and compares multiple ethical profiles under one shared protocol.

Core claim:

> We show that heterogeneous ethical systems can be executed, audited, replayed, and compared under a shared event-log protocol, with measurable agreement, conflict, and repair structures.

## Problem

Single-output safety evaluation is too narrow for multi-step, tool-using, memory-writing agents. A final answer may look acceptable while the process that produced it contains low evidence, contradiction, rollback, causal leakage, unsafe delegation, or unresolved conflict between ethical profiles.

This project treats safety evaluation as an observability problem: every step should be logged, replayable, attributable to risk signals, and comparable across profiles.

## Approach

The system builds a shared audit loop around:

- event logs for observations, actions, state, and runtime metadata
- replay bundles for re-running and inspecting traces
- six-axis telemetry for risk attribution across tau, C, M, S, X, and P style signals
- hierarchy-aware scoring that separates primary violations, secondary violations, and diagnostic tags
- comparative execution across Omega Public Reasoning, Kantian, Utilitarian, and Care Ethics profiles
- benchmark reports that preserve both scores and limitations

## Current Evidence

| Evidence Layer | Result | What It Supports | Limitation |
|---|---:|---|---|
| OMB-24 dev v0.3 | total = 0.988851; auditability = 1.0 | runnable dev benchmark with replay and attribution | first-party dev benchmark |
| OMB-Holdout-24 | total = 0.959652; auditability = 1.0 | initial frozen holdout validation | internal 24-case holdout |
| TruthfulQA-mini | total = 1.0 | external honesty-oriented audit subset | not full open-ended TruthfulQA |
| BBQ-mini | total = 1.0 | external fairness-oriented audit subset | not full BBQ |
| Runtime smoke | event log, replay bundle, attribution generated | vLLM-style metadata can enter audit artifacts | synthetic smoke only |
| Six-axis ablation | OMB-24 total: 0.688851 to 0.988851 | six-axis + replay improves audit-pipeline behavior | not proof of model capability improvement |
| Comparative baseline | 26 conflict-observable cases; 26 profile-specific repair cases | comparative layer exposes disagreement and repair structure | does not resolve moral disagreement |
| Ethics-Audit-Core-128 | total = 0.990805; replay_success_rate = 1.0 | medium-scale protocol stability | internally assembled benchmark |

## What This Package Claims

The package claims that a shared event-log protocol can make agentic ethical behavior more observable: decisions can be recorded, replayed, scored, attributed to six-axis risk, and compared across ethical profiles. It also claims preliminary validation across first-party, holdout, external-mini, runtime-smoke, ablation, comparative, and Core-128 layers.

## What This Package Does Not Claim

The package does not claim universal ethics, production deployment, full safety certification, complete cultural representation, or leaderboard-grade performance on full external benchmarks. The current evidence is strongest for auditability, reproducibility, and structured comparison; it is preliminary for broader external generalization and production runtime use.

## Fellowship Goal

The fellowship goal is to turn this prototype into a reusable open audit standard for agentic AI systems: stronger external validation, richer runtime integration, clearer human-facing repair reports, and broader comparative evaluation without collapsing ethical disagreement into a single opaque score.
