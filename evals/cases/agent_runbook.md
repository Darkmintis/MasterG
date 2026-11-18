# Agent quality runbook (stability + no-invention)

Run these on a real product after installing `skills/masterg/`.

## Stability (case 1)
1. Freeze git commit + inputs.
2. Run `/masterg` three times (new chats).
3. Pass if each category is within ±1 of the median and overall within ±5.
4. Pass if finding keys for the same issues are reused.

## No invention (case 5)
1. Disable web tools. Do not supply competitors.
2. Review with README-only context.
3. Pass checklist in `no_invention.md`.

## Real app dry-run (DoD)
1. Run on a real Flutter (or other) app.
2. Confirm every scored category has evidence or is `unverified`.
3. Confirm no files outside `MasterG/` changed (`git status`).
4. Open `MasterG/report.html` offline from `file://`.

Record date + product in a private note (not required in-repo).
