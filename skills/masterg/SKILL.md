---
name: masterg
description: >-
  Strict, evidence-backed product review for apps, web apps, sites and games,
  saved as versioned reports in a MasterG/ folder so progress can be tracked
  over time. Use whenever the user wants their app or product reviewed, rated,
  roasted, audited for store readiness, or asks "is my app good", "what should
  I fix first", or wants to compare this month's Play Console / analytics report
  with last month's, even if they don't say "MasterG". Triggers include
  /masterg, "review my app", "rate my product", "roast my app", "store
  readiness", "compare to last month". Not for pull-request code review,
  security audits, or writing marketing copy.
---

# MasterG

Honest product review with a fixed rubric, evidence-backed scores, and versioned reports inside the user's project.

**Humans open** `MasterG/report.html`. **Agents read** `MasterG/MasterG.md`.

This skill folder is self-contained. Paths below are relative to it.

## Prerequisites (once per machine)

`scripts/masterg.py` needs **Python 3.9+** (stdlib only). Before the first `status` / `finalize` in a session:

1. Run `python3 --version` (or `python --version`). Accept 3.9+.
2. If missing or too old: install the smallest usual option for the OS (`apt`/`dnf`/`brew`/`winget`/`choco`, or the [python.org](https://www.python.org/downloads/) installer). Prefer `python3`.
3. Re-check the version. If you cannot install (no permission / sandbox), stop and tell the user the exact command to run.
4. Prefer `python3` in all MasterG commands. Fall back to `python` only when it is 3.9+.

Do **not** create a venv or install pip packages for MasterG.

## Rules (MUST / NEVER)

1. **Evidence or `unverified`.** Every score and finding cites evidence. No evidence → `score: null`, `confidence: "unverified"`. Never guess.
2. **Fixed rubric.** Same 10 categories every time. Rubric version is stored in every report.
3. **AI judges, script computes.** Write `draft.json` only. Run `scripts/masterg.py` for totals, deltas, HTML, `MasterG.md`. Never hand-write HTML or totals.
4. **Brutal about the product, never the person.** Strict, specific, calibrated. No insults, flattery, or hedging. Read `references/tone.md` before the calibration pass. **Never use em dashes (—) or en dashes (–)** in draft text, findings, or chat - use a hyphen `-` or rephrase.
5. **Write only inside `MasterG/`.** Never modify the user's source, config, or other files. Describe fixes; do not apply them.
6. **Never invent.** No made-up competitors, URLs, benchmarks, download numbers, or quotes. Unsourced claims → low confidence or omit.
7. **Old versions are immutable.** Never edit `reports/vN/` after finalize. Corrections → next version.
8. **No secrets in reports.** Redact keys, tokens, passwords, personal data from quotes. Script blocks common patterns.
9. **Say what was not reviewed.** Always fill `coverage`.
10. **Explicit trigger only.** Do not run at the start of every session.
11. **Ask little.** At most one batch of 3 questions. If unanswered, proceed and list assumptions.
12. **One entry point per audience.** Point humans to `MasterG/report.html`; agents to `MasterG/MasterG.md`.

## Modes

| Mode | When | Action |
|---|---|---|
| **review** (default) | `/masterg`, review/rate/roast/store-readiness, or new Play Console/analytics ask | Create next version |
| **compare** | "compare v1 and v3", "how much did I improve" | `python3 scripts/masterg.py compare --from A --to B`, summarize in chat |
| **show** | "show my report" | Tell user to open `MasterG/report.html`. No new version |

If `MasterG/` exists and the user says `/masterg`, create the **next** version from current codebase + any new `inputs/`.

## Review flow

### 1. Detect
Look for `MasterG/`. Run:

```bash
python3 scripts/masterg.py status --project <user-project-root>
```

Use `next_version`, previous overall, previous finding keys, previous metrics.

### 2. Identify the product
Infer type (`mobile_app|web_app|site|game|other`), platforms, stack, one-liner, stage, audience from repo + README first.

### 3. Ask once if needed
Max **3 questions** in one message, only if not inferable:
1. Goal: earn / portfolio / learning
2. Audience and region
3. Known competitors and creator constraints (budget, payment access)

If unanswered → state assumptions in the draft and continue.

### 4. Collect inputs
Read `references/inputs.md`. Scan code with the matching stack file:
- Flutter → `references/stacks/flutter.md`
- Android → `references/stacks/android.md`
- iOS → `references/stacks/ios.md`
- Web/site → `references/stacks/web.md`
- Game → `references/stacks/game.md`
- Else → `references/stacks/generic.md`

Screenshots → describe, then design checks. Exports → map via `references/metrics.md`. Record each input with id `i1`, `i2`, …

Copy user-provided exports/screenshots into `MasterG/inputs/vN/` when appropriate (do not commit secrets; `inputs/` is gitignored).

### 5. Competitor check
- Target ≥3 named real competitors with URL/store link (`source: "web"` or `"user"`).
- Web search if available; else user-supplied; else `model_memory` only with confidence caps.
- **Differentiation** and **Revenue** cannot be `high` confidence without sourced competitors.
- Only `model_memory` comps → `differentiation` confidence `low` (max score 6).
- Calling a product "generic" needs ≥2 named products with the same core feature + sources.
- Never hardcode benchmarks. Cite a source or write "no reliable benchmark available".

### 6. Score
Read `references/rubric.md` and `references/scoring-anchors.md`.

For each applicable category: score, confidence, `summary`, `why`, `why_not_higher`, evidence.

- Before **visual**: read `references/design-review.md`
- Before **revenue**: read `references/monetization-review.md`
- Set `applicable: false` only when the product type truly lacks that surface (decide in v1; keep stable).

### 7. Write findings
Severity `critical|major|minor|nit`. Include `why`, `counterpoint`, evidence, `fix`, `effort` `S|M|L`, `impact` `H|M|L`.

Key format: `<category-id>/<kebab-slug>`. **Reuse** previous keys for the same issue.

### 8. Review previous findings (v2+)
Every previous key → `resolved` | `persisting` | `regressed` with evidence. Script refuses finalize if any key is missing. See `references/versioning.md`.

### 9. Calibration pass
Read `references/tone.md` calibration section. Adjust scores. Fill `calibration_note` if any warning applies (first-review mean > 7, lazy scoring, many unverified).

### 10. Write draft
Write `MasterG/reports/vN/draft.json` matching `assets/draft.schema.json` (schema string `masterg.draft/1`).

### 11. Finalize
From the **skill** directory (so script can find `assets/`), or invoke via absolute path:

```bash
python3 <skill>/scripts/masterg.py finalize --project <user-project-root>
```

Fix every error it prints; re-run. **Max 3 attempts**, then tell the user exactly what is failing.

Requires **Python 3.9+**. If missing, follow **Prerequisites** above (setup, then retry).

### 12. Chat reply (≤8 lines)
1. Overall score and delta (or "Insufficient evidence")
2. Top 3 fixes
3. What was unverified
4. Path to `MasterG/report.html`

Do **not** paste the full report into chat.

## Script commands

```bash
python3 scripts/masterg.py status --project <path>
python3 scripts/masterg.py finalize --project <path>
python3 scripts/masterg.py compare --project <path> --from 1 --to 3
```

`--project` defaults to cwd (the **user's** project root, not this skill folder).

## Anti-patterns (bad run)

- Scoring without evidence
- Hand-computing overall / deltas / HTML
- Editing files outside `MasterG/`
- Inventing competitors or benchmarks
- Rewriting old `reports/vN/`
- Softening verdicts with empty praise
- Dumping the report into chat
- Running unprompted at session start
- Skipping `previous_findings_review` on v2+
- Em dashes in draft or chat
- Editing `assets/report.template.html` during a user review (ship template fixes in the skill repo, not mid-run)

## Reference map (read only when needed)

| File | Read when |
|---|---|
| `references/rubric.md` | Scoring any category |
| `references/scoring-anchors.md` | Choosing numbers / confidence |
| `references/inputs.md` | Collecting inputs |
| `references/design-review.md` | Before `visual` |
| `references/monetization-review.md` | Before `revenue` |
| `references/metrics.md` | Parsing exports |
| `references/tone.md` | Calibration + wording |
| `references/versioning.md` | v2+, finding keys, deltas |
| `references/stacks/*.md` | Stack-specific technical/trust/polish |
| `assets/rubric.json` | Machine rubric (script uses this) |
| `assets/draft.schema.json` | Draft shape reference |
