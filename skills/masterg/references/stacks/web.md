# Web / site checklist

Use for `technical`, `trust`, `polish`, and partly `growth`. Cite file:line or URL.

## Meta & growth
- [ ] Title, description, Open Graph / Twitter cards
- [ ] Canonical URL; robots; sitemap if site-scale
- [ ] Favicon / app icons

## Performance
- [ ] Obvious render-blocking weight (huge JS/CSS without need)
- [ ] Images sized/compressed; lazy load below fold
- [ ] Fonts: no unnecessary blocking web-font stack (report template rule is separate)

## Accessibility
- [ ] Semantic HTML / landmarks
- [ ] Keyboard focus visible
- [ ] Alt text on meaningful images
- [ ] Form labels; contrast AA on key UI

## Security & trust
- [ ] No secrets in client bundles
- [ ] HTTPS assumed for live URLs
- [ ] Privacy policy / cookie consent if tracking
- [ ] Auth flows: no tokens in URLs/logs (if present)

## Quality
- [ ] Error / empty / loading states
- [ ] Mobile viewport usable (not desktop-only)
- [ ] Broken links / placeholder pages on critical paths
