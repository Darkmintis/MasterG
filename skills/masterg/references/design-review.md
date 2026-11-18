# Design review checklist

Read before scoring `visual`. Emit a finding **only** when evidence exists (screenshot or code). Cite `<file> - <area>`.

## Palette
- [ ] 1 primary + 1 accent + neutrals
- Flag: 3+ competing accent hues, rainbow chrome, low-contrast brand color on brand color

## Contrast
- [ ] Body text ≥ 4.5:1 (WCAG AA)
- [ ] Large text / UI components ≥ 3:1
- Flag: grey-on-grey labels, icons without labels that fail contrast

## Typography
- [ ] ≤ 2 families
- [ ] ≤ 5 sizes with a clear scale
- Flag: random sizes, all-caps walls, decorative fonts for body

## Spacing & layout
- [ ] Consistent 4/8 grid
- [ ] Aligned columns; even density
- Flag: cramped clusters next to empty voids; overlapping elements

## Hierarchy
- [ ] One primary action per screen
- Flag: multiple equal-weight CTAs; no clear focal point

## Touch targets
- [ ] Android ≥ 48dp; iOS ≥ 44pt
- Flag: tiny icon-only hit areas, ads flush against CTAs

## Consistency
- [ ] Icons, corner radius, elevation, button styles match across screens
- Flag: mixed radius systems; primary button styled three ways

## States
- [ ] Empty, loading, error, offline (and dark mode if claimed)
- Flag: blank white screens; spinner-only forever; crash on offline

## Ads (if present)
- [ ] Not confusable with UI
- [ ] No accidental-tap risk next to primary actions
- Flag: fake buttons, interstitial on every navigation, app-open with no skip path where policy requires
