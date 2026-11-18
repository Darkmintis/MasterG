# Versioning

## Numbering
- Versions are `v1`, `v2`, `v3`, … under `MasterG/reports/`.
- `python scripts/masterg.py status` returns the next version number.
- Root `report.html` and `MasterG.md` always reflect the latest finalize.

## Immutability
- Never edit `reports/vN/` after finalize.
- Corrections → new version.
- `draft.json` is kept for audit; do not rewrite old drafts.

## Finding keys
- Format: `<category-id>/<kebab-slug>` (e. and `revenue/no-ad-frequency-cap`).
- Same issue across versions → **reuse the same key**.
- New issue → new key. Do not rename old keys.

## `previous_findings_review` (required on v2+)
Every key that appears in the previous version's findings must appear here with:
- `resolved` — evidence shows fixed
- `persisting` — still present
- `regressed` — was resolved earlier or improved, now worse

Script refuses finalize if any previous key is missing.

## Metrics across versions
- Record period + source per metric.
- Script computes absolute and percent deltas when comparable.
- Mismatched periods/sources → `not_comparable`.
- Never claim causation ("coincides with" only).

## Rubric version changes
- Each `data.json` stores `rubric_version`.
- If a category definition changed between rubric versions, treat that category's score delta as `not_comparable` and say so in coverage/notes.
- Do not rewrite old reports to the new rubric.
