# Canonical metrics

Use only these `metrics[].name` ids. Unknown export columns → ignore or ask one mapping question.

| id | Meaning | Typical units |
|---|---|---|
| `installs` | New installs in period | count |
| `uninstalls` | Uninstalls in period | count |
| `dau` | Daily active users | count |
| `mau` | Monthly active users | count |
| `retention_d1` | Day-1 retention | percent 0–100 |
| `retention_d7` | Day-7 retention | percent 0–100 |
| `retention_d30` | Day-30 retention | percent 0–100 |
| `rating_avg` | Average store rating | 1–5 |
| `rating_count` | Number of ratings | count |
| `crash_free_users_pct` | Crash-free users | percent 0–100 |
| `anr_rate_pct` | ANR rate | percent |
| `store_listing_conversion` | Store listing conversion | percent 0–100 |
| `revenue` | Total revenue | currency amount |
| `ad_revenue` | Ad revenue | currency amount |
| `ecpm` | Effective CPM | currency amount |
| `session_length` | Avg session length | seconds |

## Mapping hints

**Play Console:** Installs → `installs`; Uninstalls → `uninstalls`; Ratings → `rating_avg` / `rating_count`; Store listing conversion → `store_listing_conversion`; Crashes / ANRs → `crash_free_users_pct` / `anr_rate_pct`.

**App Store Connect:** Units / downloads → `installs`; Sessions; Retention; Ratings and reviews.

**Firebase / GA:** `activeUsers` (1 day) → `dau`; 28/30 day → `mau`; engagement time → `session_length`.

**AdMob:** Estimated earnings → `ad_revenue`; eCPM → `ecpm`; impressions (supporting only, not a canonical id).

## Period & comparability

- Always set `period` (e.g. `2026-10`, `2026-10-01..2026-10-31`).
- Same metric name + same period shape + same source type → comparable.
- Different periods or incompatible sources → script marks `not_comparable`.
- Never claim causation. Use "coincides with".
- Never invent benchmarks. Cite a source or say "no reliable benchmark available".
