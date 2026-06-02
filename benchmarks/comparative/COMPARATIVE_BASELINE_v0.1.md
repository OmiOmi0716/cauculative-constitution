# Comparative Baseline Report v0.1

## Core Claim

We show that heterogeneous ethical systems can be executed, audited, replayed, and compared under a shared event-log protocol, with measurable agreement, conflict, and repair structures.

## Overall Capability Delta

- total comparative cases = 26
- delta_vs_single_profile_only = {"agreement_pairs_observed": 18, "conflict_observable_cases": 26, "shared_axis_cases": 24, "profile_specific_repair_cases": 26}
- delta_vs_profile_silo = {"agreement_pairs_observed": 18, "conflict_observable_cases": 26, "shared_axis_cases": 24, "profile_specific_repair_cases": 26}

| mode | case_count | profile_runs | raw_violation_signal_cases | raw_repair_signal_cases | agreement_pairs_observed | conflict_observable_cases | shared_axis_cases | profile_specific_repair_cases | cross_profile_replay |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Single Profile Only | 26 | 26 | 26 | 26 | 0 | 0 | 0 | 0 | no |
| Profiles In Silos | 26 | 104 | 26 | 26 | 0 | 0 | 0 | 0 | no |
| Full Comparative Layer | 26 | 104 | 26 | 26 | 18 | 26 | 24 | 26 | yes |

## Cross-Profile Audit Mini

| mode | raw_violation_signal_cases | raw_repair_signal_cases | agreement_pairs_observed | conflict_observable_cases | shared_axis_cases | profile_specific_repair_cases | notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Single Profile Only | 10 | 10 | 0 | 0 | 0 | 0 | A single ethics profile can replay its own trace, but it cannot expose disagreement or repair deltas across systems. |
| Profiles In Silos | 10 | 10 | 0 | 0 | 0 | 0 | Multiple profiles run independently, but disagreement stays latent because there is no shared alignment layer or comparative report. |
| Full Comparative Layer | 10 | 10 | 6 | 10 | 8 | 10 | Shared event-log alignment exposes agreement, conflict, shared axes, and profile-specific repair deltas under one replayable protocol. |

## Cross-Cultural Audit Mini

| mode | raw_violation_signal_cases | raw_repair_signal_cases | agreement_pairs_observed | conflict_observable_cases | shared_axis_cases | profile_specific_repair_cases | notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Single Profile Only | 8 | 8 | 0 | 0 | 0 | 0 | A single ethics profile can replay its own trace, but it cannot expose disagreement or repair deltas across systems. |
| Profiles In Silos | 8 | 8 | 0 | 0 | 0 | 0 | Multiple profiles run independently, but disagreement stays latent because there is no shared alignment layer or comparative report. |
| Full Comparative Layer | 8 | 8 | 6 | 8 | 8 | 8 | Shared event-log alignment exposes agreement, conflict, shared axes, and profile-specific repair deltas under one replayable protocol. |

## Multi-Agent Audit Mini

| mode | raw_violation_signal_cases | raw_repair_signal_cases | agreement_pairs_observed | conflict_observable_cases | shared_axis_cases | profile_specific_repair_cases | notes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Single Profile Only | 8 | 8 | 0 | 0 | 0 | 0 | A single ethics profile can replay its own trace, but it cannot expose disagreement or repair deltas across systems. |
| Profiles In Silos | 8 | 8 | 0 | 0 | 0 | 0 | Multiple profiles run independently, but disagreement stays latent because there is no shared alignment layer or comparative report. |
| Full Comparative Layer | 8 | 8 | 6 | 8 | 8 | 8 | Shared event-log alignment exposes agreement, conflict, shared axes, and profile-specific repair deltas under one replayable protocol. |