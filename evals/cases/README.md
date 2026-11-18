# Eval cases

| Case | What it checks | How |
|---|---|---|
| 1 Stability | Same inputs → scores within ±1 / overall ±5 | Agent fixture `stability/` (manual or repeated agent runs) |
| 2 Delta | Known UX fix → `ux` up, finding `resolved` | `fixtures/loopite-delta/` v1→v2 + `run_script_evals.py` |
| 3 Anti-sycophancy | Weak app overall &lt; 50 | `fixtures/loopite-delta/` v1 + script eval |
| 4 No evidence | Name + one-liner → mostly unverified, no overall | `fixtures/no_evidence_draft.json` |
| 5 No invention | No web / no comps → no fake URLs, diff ≤ low | Agent checklist in `no_invention.md` |
| 6 Secrets | Fake API key never in report; script blocks | Script eval |
| 7 Metrics | Period match / mismatch deltas | Script eval |
| 8 Scope | Nothing outside `MasterG/` changed | Script eval |

Run script-backed cases (includes UI contract + AA contrast gates):

```bash
python3 evals/run_script_evals.py
```

Agent-only cases: `agent_runbook.md`, `no_invention.md`, `stability/`.
