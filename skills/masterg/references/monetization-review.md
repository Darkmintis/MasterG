# Monetization review

Read before scoring `revenue`.

## Who pays
- [ ] Who pays (user, advertiser, both)?
- [ ] Why would they pay? What evidence (code, listing, comps, metrics)?
- No evidence → do not invent willingness-to-pay

## Model fit
Pick what the product actually implements or clearly plans:
`ads` · `subscription` · `one-time` · `iap` · `pay-per-feature` · `credits` · `donations` · `crypto`

- [ ] Model matches audience and usage pattern
- [ ] Creator can actually collect (region, payment access) — use user-stated constraints only
- Recommend only collectible models

## Ads (if applicable)
- [ ] Placement vs store policy (not mimicking UI)
- [ ] Frequency caps present
- [ ] Consent / UMP (or platform equivalent) where required
- [ ] App-open ads: high accidental-tap / policy risk — flag unless carefully gated

## "No revenue model"
- Goal `earn` → finding severity **critical**
- Goal `portfolio` / `learning` → note only; not critical

## Revenue ceiling (optional, labeled)
```
installs × active_share × impressions_per_user × eCPM / 1000
```
- Show the formula
- Label every assumption
- Never present as a forecast
- No sourced eCPM → write "no reliable benchmark available"

## Confidence
`high` requires competitor evidence (named comps with source `web` or `user`).
