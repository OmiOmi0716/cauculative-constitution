# Agent Ethics Management Sandbox Scope

This directory is an isolated sandbox for agent ethics management work. It is not part of the frozen v0.3 benchmark evidence, does not introduce new benchmark scores, does not modify current scoring rules, and does not change the main `ethiccaculate` package.

The sandbox may contain copied or lightweight re-expressed concepts from the current audit stack, including event logs, replay, risk attribution, six-axis telemetry, and non-regression framing. Those copies are local to this directory.

## Current Boundary

Can do:

- define Self / Social / Mission / Human Anchoring events
- map agent events into six-axis diagnostic telemetry
- produce sandbox-only heuristic scores
- generate replay summaries
- propose repair and human review actions

Cannot claim:

- current benchmark evidence
- production deployment
- full RL implementation
- external validation
- changes to the frozen release package
- changes to the main scoring rules

## Source Alignment

This sandbox combines two source ideas:

- the existing ethics audit stack: event log, replay, violation, repair, six-axis diagnosis, human review, non-regression
- the Agentic RL Loop whitepapers: Self / Social / Mission subsystems, Human Anchoring Layer, event schemas, multi-time-scale updates

The goal is agent ethics management: making agent behavior observable, replayable, diagnosable, repairable, and governable.
