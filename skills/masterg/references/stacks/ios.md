# iOS (native / SwiftUI / UIKit) checklist

Use for `technical`, `trust`, `polish`. Cite file:line.

## Project
- [ ] Deployment target store-ready
- [ ] Capabilities match features (Push, IAP, etc.)
- [ ] Debug vs Release configs (logging, test flags)

## Privacy
- [ ] `Info.plist` usage descriptions for every sensitive API
- [ ] Privacy Manifest / tracking declarations if applicable
- [ ] ATT prompt timing: after value, not before
- [ ] Privacy policy link

## Security
- [ ] Secrets not in repo or plaintext plist
- [ ] Keychain for tokens; ATS not weakened without reason

## Quality
- [ ] Crash reporting
- [ ] Tests for critical logic
- [ ] Empty / loading / error / offline states
- [ ] Dynamic Type / VoiceOver labels
- [ ] Touch targets ≥ 44pt

## Monetization
- [ ] StoreKit / ads SDK hygiene
- [ ] Paywall clarity; restore purchases if IAP
- [ ] Ad placement policy-safe
