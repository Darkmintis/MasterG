# Flutter stack checklist

Use for `technical`, `trust`, `polish`. Cite file:line.

## Dependencies & structure
- [ ] `pubspec.yaml`: outdated/critical deps, unused bloat, SDK constraint
- [ ] State management consistent (one primary approach)
- [ ] Clear feature folders vs spaghetti `lib/`

## Ads & consent
- [ ] Ads SDK present and initialized once
- [ ] Frequency caps / placement not adjacent to primary CTAs
- [ ] UMP / consent flow before personalized ads where required

## Permissions & platforms
- [ ] AndroidManifest / Info.plist permissions match actual features
- [ ] minSdk / targetSdk sensible for store
- [ ] Signing configs / keystores not committed

## Release hygiene
- [ ] Debug vs release flags (logging, test ads, banners)
- [ ] Crash reporting present (Crashlytics, Sentry, etc.)
- [ ] Analytics present if retention/growth claims need it

## Quality
- [ ] Tests exist for critical logic (or honest absence)
- [ ] Error / empty / loading widgets on main flows
- [ ] Offline / no-network behavior
- [ ] Localization: hardcoded strings only? `gen-l10n` used?
- [ ] Accessibility: Semantics, text scaling, contrast in themes

## Performance
- [ ] Long lists: ListView.builder / slivers, not unbounded Column of children
- [ ] Rebuild hotspots (unnecessary setState / Riverpod watch scope)
- [ ] Image sizes / caching

## Trust
- [ ] Secrets / API keys not in repo
- [ ] Privacy policy link reachable from app or store listing
- [ ] Data safety / permission claims align with code
