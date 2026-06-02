# Ethics-Audit-Core-128

This directory contains the medium-scale Core-128 benchmark assembly and its one-shot baseline reports.

Files:

- `core128_schema.json`
- `CORE128_SCHEMA.md`
- `ethics_audit_core128.json`
- `CORE128_SCORING_v0.1.json`
- `CORE128_SCORING_v0.1.md`
- `CORE128_COMPARATIVE_REPORT_v0.1.md`
- `CORE128_FAILURE_ANALYSIS_v0.1.md`

Build command:

```powershell
& 'C:\Users\luna0\Documents\Codex\2026-05-01\new-chat\ethiccaculate\.venv\Scripts\python.exe' -m ethiccaculate.core128
```

Policy:

- do not modify the frozen `ethiccaculate-v0.3-omb24` release
- do not change the existing scoring rule for Core-128
- do not retune the benchmark after the first baseline run

