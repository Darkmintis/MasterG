# Android (native) checklist

Use for `technical`, `trust`, `polish`. Cite file:line.

## Project
- [ ] Gradle / AGP / Kotlin versions not abandoned
- [ ] `minSdk` / `targetSdk` / `compileSdk` store-ready
- [ ] Product flavors / build types sane (debug vs release)

## Security & secrets
- [ ] No API keys in source or committed `local.properties` variants
- [ ] Network security config if cleartext used
- [ ] Signing keys not in repo

## Permissions & privacy
- [ ] Manifest permissions match features; no leftovers
- [ ] Runtime permission rationale before sensitive asks
- [ ] Privacy policy + Data safety alignment

## Quality
- [ ] Crash reporting / Play Vitals awareness
- [ ] Tests for critical paths
- [ ] Empty / loading / error / offline states
- [ ] Accessibility: contentDescription, touch targets ≥ 48dp

## Monetization
- [ ] Billing / ads SDKs correctly initialized
- [ ] Consent (UMP) before personalized ads when required
- [ ] Ad placement not mimicking UI
