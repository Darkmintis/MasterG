# Generic / other (CLI, extension, package, library)

Use when the product is not a mobile app, web app, site, or game.

## Usual applicability
Often `applicable: false`:
- `visual` — no UI
- `ux` — if no interactive user surface (library-only)
- `growth` — if not distributed via store/SEO (optional; keep if npm/PyPI listing matters)
- `retention` — if one-shot tool with no loop (judge carefully)

Usually keep: `idea`, `differentiation`, `revenue` (if goal is earn), `technical`, `trust`, `polish`.

Decide once in v1. Document in assumptions.

## Checklist
- [ ] Clear problem + audience in README
- [ ] Install / quickstart works as documented
- [ ] API surface stable or versioned
- [ ] Tests for critical paths
- [ ] No secrets in repo
- [ ] License present
- [ ] Security hygiene at trust boundaries (input validation)
- [ ] Packaging metadata (npm/PyPI/VS Code marketplace) accurate if published
