# Deviations from the master plan

Private plan lives in `.local/` (gitignored). Public repo does not ship the plan.

| Decision | Why |
|---|---|
| `--project` is a subcommand flag (`finalize --project …`), not only a global flag | argparse rejected `--project` after the verb; parent parser on each subcommand fixes it. Both `masterg.py status --project .` and docs in SKILL match. |
| `existing_versions` counts only folders with `data.json` | Draft-only `vN/` folders must not bump the next version; otherwise finalize looks for `v2` while `v1` is still a draft. |
| Evals include a runnable `evals/run_script_evals.py` for script-enforced cases | Stability / no-invention / full agent loops need a live model; script cases (secrets, metrics, coverage, anti-sycophancy on fixtures, scope) are automated. Agent cases are specified as fixtures + expected ranges. |
| Public sample is Blink (live app report mirror), not a full Flutter tree | Showcase uses a real review; full source stays in Blink-app. Weak v1→v2 delta / anti-sycophancy evals use `evals/cases/fixtures/loopite-delta/`. |
| README lists Cursor / Claude Code / Codex / Copilot paths verified Nov 2026 | Other agents exist; we document the main ones and point to Agent Skills path conventions rather than inventing unverified paths. |
| `__pycache__/` gitignored | Local test runs leave bytecode; not part of the skill. |
| Report theme: graded paper (cream / espresso) | Owner-specified palette. AA tweaks: mocha score text `#8B5230`; selected tabs use `--accent-text` `#9C4626` + cream ink; dark critical `#F07167`; minor/nit label `#5E5348` (raw `#8A7A6B` failed AA on tint). Severity chips always include a text label. |
| Theme is toggle-driven (`data-theme`) not OS-only | Sticky Light/Dark control; OS preference seeds first visit via `localStorage`. |
| Native `<select>` replaced with custom listbox | OS overlay could not be themed; custom `.dd` menu matches paper theme + keyboard a11y. |
| Export PDF is a single button (`window.print()` + print CSS) | One format = no dropdown arrow. User picks Save as PDF in the print dialog. |
| Charts are vanilla SVG/HTML | No CDN chart library (plan: offline, no network). Category bars, overall line, findings donut, sparklines, metric deltas. |
