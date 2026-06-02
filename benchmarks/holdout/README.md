# OMB-Holdout-24

`OMB-Holdout-24` is the first non-dev benchmark for this workspace.

Properties:

- `24` total cases
- `8` honesty
- `8` harmlessness
- `8` fairness_bias
- `4` demographic pair invariance checks

Rules:

- Use it to check generalization after changes made on `OMB-24`.
- Do not tune thresholds, case heuristics, or repair rules on this suite.
- Score it with the same rubric implementation used for `OMB-24 v0.2`.

Run:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.scoring benchmarks/holdout/omb_holdout24.json
```

Frozen validation artifact:

- `benchmarks/holdout/OMB_HOLDOUT24_VALIDATION_v0.3.md`
