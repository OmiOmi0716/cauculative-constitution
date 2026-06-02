# Ethics-Audit-Core-128 Schema

Core-128 extends the base benchmark case shape with core benchmark provenance and baseline-annotation fields.

Required case fields:

```json
{
  "case_id": "",
  "category": "",
  "source": "",
  "input_event_trace": [],
  "expected_primary": [],
  "expected_secondary": [],
  "expected_diagnostic": [],
  "expected_axes": [],
  "profile_targets": [],
  "replay_required": true
}
```

Block targets:

- 16 OMB-style honesty
- 16 OMB-style harmlessness
- 16 OMB-style fairness
- 16 TruthfulQA-derived audit
- 16 BBQ-derived audit
- 16 cross-profile
- 16 cross-cultural
- 16 multi-agent

Freeze rule:

- assemble once
- annotate once
- run one baseline
- do not retune cases or rules from observed results
