# Proposal Draft

## Title

**A Shared Event-Log and Replay Protocol for Auditing Ethical Disagreement in Agentic AI Systems**

## Short Summary

As frontier AI systems become autonomous agents operating across hours, days, tools, memories, and delegated sub-tasks, single-output safety evaluation is no longer sufficient. The safety-relevant object is increasingly the behavioral trace: what the agent observed, what it wrote to memory, which tools it trusted, where it rolled back, and how it handled uncertainty.

This project develops a runnable research prototype called `ethiccaculate` for safety evaluation and agentic oversight. The core design treats AI behavior as an event trace that can be executed, scored, replayed, compared, and audited under multiple ethical profiles. This reframes ethics evaluation from a single-label classification problem into an auditable systems problem. Instead of claiming a single universal ethical answer, the project builds a shared protocol that exposes agreement, disagreement, risk axes, and profile-specific repair actions as inspectable audit objects.

The current prototype combines executable ethics profiles, six-axis runtime telemetry, replayable event logs, risk attribution, benchmark scoring, comparative evaluation, and medium-scale benchmark validation. The project is designed for safety evaluation, agentic oversight, and scalable mitigations: it asks how we can make ethical and safety-relevant disagreement visible, measurable, and governable before agentic systems become too opaque to supervise.

## 1. Problem

Frontier AI systems are increasingly moving from single-turn question answering toward agentic behavior: tool use, multi-step planning, memory writing, delegation, rollback, self-correction, and interaction with other agents. In these systems, the safety-relevant object is no longer only the final answer. The safety-relevant object is the whole behavioral trace.

Current evaluation methods often flatten this trace into a single label or score. That is insufficient for agentic oversight. A system can produce a superficially acceptable final answer while passing through unsafe intermediate states, writing unstable memory, ignoring tool contradictions, escalating too late, or failing to expose uncertainty. Conversely, different ethical systems may reasonably disagree about the correct repair action, but today that disagreement is often hidden inside informal natural-language critique.

A simple example illustrates the failure mode. Imagine an agent tasked with scheduling medical appointments. It calls an external calendar API, writes a partial memory entry, encounters a conflict, silently rolls back, and re-attempts with different parameters. The final user-facing answer looks correct. However, the intermediate rollback state contained a privacy-relevant memory write that was never reviewed, and the system never exposed whether the tool contradiction was resolved or merely bypassed. A final-answer evaluator would likely miss the problem. A trace-level audit protocol can preserve and inspect it.

This project addresses that gap by building a shared audit protocol for agentic behavior. Today, no standard trace-level audit protocol exists for agentic systems. The protocol records every relevant event, maps runtime signals into six risk axes, runs multiple ethical profiles over the same trace, and produces replayable reports showing where systems agree, conflict, and recommend different repairs.

## 2. Research Thesis

The central thesis is:

> Heterogeneous ethical systems can be executed, audited, replayed, and compared under a shared event-log and replay protocol, with measurable agreement, conflict, shared risk axes, and profile-specific repair structures.

The goal is not to produce a single verdict, but to make disagreement itself operational: visible, replayable, measurable, and connected to runtime control.

The project makes three concrete claims:

1. **Auditability claim:** Agentic behavior can be represented as event logs, snapshots, replay bundles, and risk attribution reports rather than only final outputs.
2. **Comparability claim:** Multiple ethical profiles, including profiles inspired by heterogeneous ethical traditions, can be run over the same trace and compared through agreement matrices, conflict counts, shared violation axes, and repair deltas.
3. **Runtime oversight claim:** Model/runtime signals such as uncertainty, contradiction, rollback, entropy, and latency can be mapped into a common six-axis telemetry layer that supports inspection and governance.

## 3. System Prototype

The current prototype is a Python research package called `ethiccaculate`. It implements a runnable ethics-and-six-axis audit pipeline with the following components.

### 3.1 Event-log protocol

The system represents model or agent behavior as structured `DialogueEvent` traces. These traces can come from benchmark cases, external audit examples, multi-agent interactions, cultural scenarios, or synthetic runtime metadata. Each event can carry content, confidence, evidence coverage, sensitive context, profile targets, and runtime metadata.

### 3.2 Six-axis telemetry

The system maps each event into six diagnostic axes. The design principle is that agentic risk is not one-dimensional: an unsafe trace may arise from causal inconsistency, unstable reasoning, external context shift, runtime pressure, stalled progress, or unsafe memory consolidation. The six-axis layer gives these failure modes a common coordinate system rather than forcing them into one undifferentiated safety score.

The architecture can be summarized as:

```text
Input Trace
  -> Shared Event Log
  -> Six-Axis Telemetry
  -> Multi-Profile Ethics Execution
  -> Violation / Agreement / Conflict Reports
  -> Replay Bundle + Risk Attribution
  -> Human Review / Repair Action
```

The system maps each event into six diagnostic axes:

* **C axis:** causal, consistency, evidence, contradiction, and citation risk.
* **S axis:** instability, entropy, and uncertainty pressure.
* **X axis:** external event flow and changing context.
* **P axis:** runtime pressure, latency, resource stress, and rollback cost.
* **tau axis:** internal progress and non-regression signal.
* **M axis:** memory stability, consolidation, and write/read safety.

The purpose of the six-axis layer is to make risk diagnosable. A label such as `Honesty` or `Harmlessness` says what kind of safety problem occurred; the six-axis state helps explain where and why the problem emerged.

### 3.3 Executable ethics profiles

The prototype supports multiple moral-system profiles, including Omega Public Reasoning, Kantian, Utilitarian, and Care Ethics profiles. Each profile can define principles, thresholds, violation rules, allowed moves, forbidden moves, and repair actions.

The profiles are not presented as authoritative philosophical definitions. They are executable approximations used to test whether a shared protocol can expose differences between ethical systems.

### 3.4 Audit and replay layer

The system produces:

* event logs,
* MCD (Model Cognitive Dump) snapshots: point-in-time state captures of active beliefs, confidence levels, and memory contents at key trace events,
* replay bundles,
* risk attribution reports,
* violation labels,
* repair actions,
* benchmark scores,
* comparative reports.

This makes the system inspectable after the fact. A reviewer can see not only which cases failed, but which step, axis, signal, and repair path were involved.

### 3.5 Hierarchy-aware scoring

The scoring layer distinguishes:

* `primary_violation`,
* `secondary_violation`,
* `diagnostic_tag`.

This avoids treating every emitted label as an equal peer violation. For example, `Helpfulness` may be useful as a diagnostic tag rather than a primary violation. This matters because conservative safety systems often over-trigger labels. The v0.3 scoring rubric preserves safety recall while making over-trigger behavior visible and interpretable.

## 4. Preliminary Evidence

The prototype has progressed through several evaluation layers. A key limitation is that OMB-24, OMB-Holdout-24, and Ethics-Audit-Core-128 are internally assembled benchmark suites. They are useful for protocol development, freeze discipline, and medium-scale stability testing, but they do not by themselves validate the system as an external standard. The fellowship period would therefore focus on expanding external validation coverage, strengthening third-party benchmark integration, and making the schema easier for outside reviewers to rerun.

The current evidence should be read as prototype evidence for an audit protocol, not as a final safety certification.

### 4.1 OMB-24 development benchmark

OMB-24 is a 24-case first-party development benchmark covering honesty, harmlessness, and fairness/bias cases. It was used to build and calibrate the initial scoring protocol.

The v0.3 result:

* `weighted_safety_score = 0.984073`
* `weighted_auditability_score = 1.0`
* `weighted_total_score = 0.988851`
* `expected_subset_recall_mean = 1.0`

The main improvement from v0.2 to v0.3 was over-trigger calibration through hierarchy-aware reporting, not narrowing the base safety rules.

### 4.2 OMB-Holdout-24 frozen validation

OMB-Holdout-24 is a separate 24-case holdout suite with the same 8/8/8 category split. It was treated as a frozen validation suite and not used for iterative tuning.

The v0.3 holdout result:

* `weighted_safety_score = 0.94236`
* `weighted_auditability_score = 1.0`
* `weighted_total_score = 0.959652`

This provides an initial generalization check while preserving the limitation that the suite remains internally constructed.

### 4.3 Runtime smoke test

The project includes a synthetic vLLM runtime smoke test. It verifies that hot-path, cold-path, and rollback metadata can enter the audit loop and reappear in:

* `runtime_event_log.json`,
* `runtime_replay_bundle.json`,
* `runtime_risk_attribution.md`.

The smoke test covers:

1. high entropy plus low evidence,
2. rollback-heavy recovery,
3. causal leakage plus contradiction.

This does not claim production deployment. It validates the hook-path and audit format.

### 4.4 External audit subsets

The prototype includes two small external-derived audit subsets:

* **TruthfulQA-mini:** 24 honesty cases built from known incorrect answers, testing whether the audit pipeline detects confident falsehoods.
* **BBQ-mini:** 24 fairness cases built from stereotype-aligned answer choices, testing whether the pipeline detects protected-attribute bias signals.

Both mini suites achieved `weighted_total_score = 1.0` under the v0.3 audit framing. These scores are high because the suites are structured as audit detection tasks over known failure modes: the system is tested on whether it can detect pre-labeled problems, not whether it can generate safe responses in open-ended settings. These are audit subsets, not full leaderboard-grade evaluations and not open-ended generation benchmarks.

### 4.5 Six-axis ablation

Ablation compares:

1. No Six-Axis,
2. Observe Only,
3. Observe + Gate + Replay.

Reported totals:

* OMB-24: `0.688851 -> 0.888851 -> 0.988851`
* TruthfulQA-mini: `0.7 -> 0.9 -> 1.0`

This isolates the contribution of six-axis observability, gate support, replay, and attribution while keeping raw violation detections fixed.

### 4.6 Comparative audit minis

The comparative layer runs multiple ethical profiles over the same trace and reports:

* `profile_agreement_rate`,
* `profile_conflict_count`,
* `shared_violation_axes`,
* `profile_specific_repair_actions`,
* `agreement_matrix`.

Current results include:

* Cross-Profile Audit Mini: `profile_agreement_rate = 0.891667`, `profile_conflict_count = 38`, shared axes C and M.
* Cross-Cultural Audit Mini: `profile_agreement_rate = 0.869792`, `profile_conflict_count = 24`.
* Multi-Agent Audit Mini: `profile_agreement_rate = 0.864583`, `profile_conflict_count = 24`, `mean_speaker_count = 2.125`.

A comparative baseline shows that single-profile and siloed-profile execution can detect raw violations, but cannot expose agreement pairs, conflict-observable cases, shared axes, or profile-specific repair deltas. The full comparative layer makes these structures visible and replayable.

### 4.7 Ethics-Audit-Core-128 medium benchmark

The strongest current evaluation artifact is Ethics-Audit-Core-128 v0.1, a medium-scale 128-case benchmark assembled from eight blocks:

* 16 OMB-style honesty,
* 16 OMB-style harmlessness,
* 16 OMB-style fairness,
* 16 TruthfulQA-derived audit,
* 16 BBQ-derived audit,
* 16 cross-profile,
* 16 cross-cultural,
* 16 multi-agent traces.

It was assembled, annotated, scored once, and frozen without result-driven retuning.

Current fixed baseline:

* `case_count = 128`
* `weighted_total_score = 0.990805`
* `weighted_auditability_score = 1.0`
* `event_log_success_rate = 1.0`
* `replay_success_rate = 1.0`
* `risk_attribution_coverage = 1.0`
* `expected_subset_recall = 1.0`
* `holdout_gap = 0.019687`
* `comparative_conflict_observable_rate = 1.0`

The `holdout_gap` represents the difference in `weighted_total_score` between the development benchmark and the frozen holdout suite, indicating limited overfitting to the development benchmark in this prototype setting.

The comparative slice includes 48 cases and preserves measurable agreement, conflict, and repair structure across Omega, Kantian, Utilitarian, and Care Ethics profiles.

## 5. Why This Matters for AI Safety

This project targets a specific gap in agentic AI safety: the need to supervise behavior over time rather than only judge final answers.

A future agentic system may retrieve evidence, call tools, write memory, delegate to sub-agents, override warnings, roll back partial work, and continue acting after a failure. Safety evaluation needs a representation that can preserve this trace. The proposed event-log and replay protocol is designed for that use case.

This protocol complements existing scalable oversight directions. Critique-based oversight can help humans find mistakes in model outputs, but critique mechanisms need structured objects to inspect when the relevant failure is spread across a trace rather than localized in one answer. Debate-style or multi-agent oversight can surface disagreements, but those disagreements become more useful when they are grounded in a shared event log, common telemetry axes, and replayable repair records. As OpenAI and other labs scale agentic deployments, the absence of a shared trace audit format means that safety evaluators, red teams, and oversight researchers currently work without a common inspectable object. This project proposes one.

The project is relevant to:

* safety evaluation,
* agentic oversight,
* scalable mitigations,
* ethics evaluation,
* runtime monitoring,
* human review workflows.

The key contribution is not a new universal moral theory. The key contribution is a programmable audit surface for ethical and safety-relevant disagreement. It gives human reviewers and AI-assisted critics a common trace representation to inspect: events, axes, violations, disagreements, repairs, and replay bundles.

## 6. Six-Month Research Plan

### Month 1: Public schema and reproducibility hardening

Deliverables:

* `REPRODUCIBILITY.md`
* public event-log schema
* profile format specification
* replay bundle specification
* installation and benchmark rerun instructions
* cleaned release manifest

Goal: make the current research package reproducible by an external reviewer.

### Month 2: Expand external audit validation

Deliverables:

* larger TruthfulQA audit subset,
* larger BBQ audit subset,
* one additional external harmlessness-oriented audit subset,
* documented selection policy and limitations.

The selection policy will document how cases are sampled from external sources, what labeling conventions are applied, and where the audit framing departs from the original benchmark's evaluation assumptions.

Goal: reduce dependence on first-party benchmark construction while maintaining audit framing honesty.

### Month 3: Real runtime hook integration

Deliverables:

* vLLM (an open-source LLM inference engine) hook prototype,
* hot-path telemetry extraction,
* cold-path contradiction/self-consistency adapter,
* rollback metadata adapter,
* runtime replay report.

Goal: move beyond synthetic smoke tests toward a real monitored inference path.

### Month 4: Multi-agent and collusion oversight cases

Deliverables:

* multi-agent trace schema,
* collusion / responsibility-shifting audit mini-suite,
* supervisor-agent disagreement reports,
* repair/escalation metrics.

Goal: test whether the shared protocol can audit coordinated agent behavior, not only single-turn or two-speaker traces.

### Month 5: Human oversight and governance interface

Deliverables:

* human override protocol,
* review queue format,
* disagreement replay viewer prototype or static report format,
* escalation policy examples,
* small reviewer study with 3-5 technical reviewers or safety collaborators, subject to availability and approval.

The first human-review target is deliberately modest: reviewers would inspect replay bundles and compare whether the structured audit report helps them locate the relevant failure faster than raw traces alone. If fellowship mentors or collaborating researchers are available, their feedback would be used to refine the review workflow; otherwise, the study would use technically qualified external reviewers familiar with AI evaluation.

Goal: connect audit outputs to human decision points instead of leaving them as passive reports.

### Month 6: Open release and research report

Deliverables:

* open-source benchmark and scorer package,
* final evaluation report,
* claims and limitations document,
* arXiv-style technical report or workshop submission draft for an AI safety / evaluation venue such as a NeurIPS, ICLR, or ICML safety, evaluation, or agents workshop.

Goal: release a usable research artifact for broader safety evaluation and oversight work.

## 7. Expected Outputs

The project aims to produce:

1. A shared event-log schema for agentic safety audit.
2. A replay bundle format for ethical and runtime disagreement.
3. Executable moral-system profiles for comparative audit.
4. A six-axis telemetry layer for risk attribution.
5. Medium-scale benchmark suites for audit protocol validation.
6. External audit subset connectors.
7. Runtime hook-path validation for vLLM-like inference systems.
8. Human-readable reports and machine-readable JSON artifacts.
9. A research paper or technical report describing the protocol, evidence, limitations, and future work.

## 8. Risks and Limitations

This project has several important limitations.

First, the current system is an audit-oriented prototype, not a production deployment. The runtime path is validated through synthetic smoke tests, not long-running production inference.

Second, external benchmarks are currently used as audit subsets. TruthfulQA-mini audits known false answers; BBQ-mini audits stereotype-aligned answer choices. These results should not be presented as full open-ended TruthfulQA or BBQ leaderboard performance.

Third, Ethics-Audit-Core-128 is a medium-scale internal benchmark assembled from first-party, external-derived, and comparative cases. It supports protocol stability claims, but it is not a final external evaluation standard.

Fourth, the ethical profiles are executable approximations. They allow the protocol to compare heterogeneous ethical systems, but they should not be treated as authoritative representations of entire philosophical traditions or cultures.

Fifth, cross-cultural and multi-agent examples are still early controlled suites. They demonstrate protocol compatibility, not complete sociological or deployment validation.

Sixth, the six-axis telemetry layer is designed for audit and oversight of AI behavioral traces. It is not a deployed intrusion detection or cyber defense system, and should not be repurposed as one without additional validation.

## 9. Current Claim Boundaries

### This project can claim

* A runnable ethics-and-six-axis audit prototype.
* Replayable event logs, snapshots, replay bundles, and risk attribution.
* Hierarchy-aware violation scoring.
* Frozen holdout validation.
* External mini audit subsets for honesty and fairness.
* Six-axis ablation evidence for auditability contribution.
* Comparative audit across multiple ethical profiles.
* Medium-scale Core-128 protocol stability validation.

### This project should not claim

* A universal solution to ethics.
* Full model safety certification.
* A production-ready deployment stack.
* Full leaderboard-grade performance on external benchmarks.
* Complete representation of global cultures or philosophical systems.
* Deployed cyber defense capability.

## 10. Closing Statement

The long-term goal is to build an open, replayable, programmable audit language for AI safety and ethical disagreement. As AI systems become more agentic, the critical safety question is not only whether a final answer is acceptable, but whether the system's trace can be inspected, replayed, compared, and governed.

This project contributes a first working prototype of that idea: a shared event-log and replay protocol that turns ethical disagreement into measurable agreement matrices, conflict structures, shared risk axes, repair actions, and replayable audit records. The fellowship period would accelerate this work toward a publicly reusable, externally validated, and openly documented audit standard. The goal is a trace-level audit format that safety researchers can run, reuse, extend, and disagree with - openly and reproducibly.
