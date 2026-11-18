# Scoring anchors & confidence

## Score meaning (1–10)

| Score | Meaning |
|---|---|
| 1–2 | Missing or broken |
| 3–4 | Weak. Clear problems a user would notice |
| 5 | Average shipped indie product |
| 6 | Decent, some real strengths |
| 7 | Good. Competitive with comparable products |
| 8 | Strong. Top tier of comparable products |
| 9 | Category-leading. Needs competitor comparison evidence |
| 10 | Reserved. Almost never used |

## Confidence caps (script-enforced)

| Confidence | Meaning | Max score |
|---|---|---|
| `high` | Direct evidence (code, screens, data) | 10 |
| `medium` | Partial evidence | 8 |
| `low` | Mostly inferred, or model memory without source | 6 |
| `unverified` | No evidence | `null` (excluded from overall) |

**No evidence →** score must be `null`, confidence `unverified`. Never guess a number.

## Overall & verdict (script computes)

- `overall` = weighted average of verified applicable categories × 10 → 0–100.
- `evidence_coverage` = share of applicable weight that is verified.
- If `evidence_coverage` < 50%: no overall shown → "Insufficient evidence".
- Bands: 0–34 Not viable · 35–49 Weak · 50–64 Average · 65–79 Strong · 80–100 Exceptional.

## Calibration rules (agent + script)

1. **Median shipped indie ≈ 5.** Score relative to that, not to your taste.
2. **First review mean of verified scores > 7** → write `calibration_note` justifying why. Script warns; note required.
3. **Score ≥ 9** → needs a named competitor with `source: "web"` or `"user"`. Script errors otherwise.
4. **Score 10** → almost never. Requires exceptional evidence; prefer 9.
5. **All verified scores within ±1** → lazy scoring warning; address in `calibration_note`.
6. **> 3 categories unverified** → warning; say what inputs unlock them in `calibration_note` or coverage notes.
7. **Differentiation / Revenue `high` confidence** → requires competitor evidence (SKILL competitor rules).
8. **`why_not_higher`** must name what would unlock +2 points. Empty = incomplete judgment.

## Quick self-check before draft

- [ ] Every scored category has ≥1 evidence item with `input` + `ref`
- [ ] Unverified categories have `score: null`
- [ ] No score above its confidence cap
- [ ] No ≥9 without sourced competitor
- [ ] Mean feels honest vs "average indie = 5"
- [ ] `calibration_note` covers any script warnings you expect
