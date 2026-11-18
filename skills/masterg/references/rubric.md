# Rubric (v1.0.0)

Weights sum to 100. Machine copy: `assets/rubric.json` — keep in sync.

| id | Category | Weight | Question |
|---|---|---|---|
| `idea` | Idea & Problem | 10 | Is the problem real and painful? Who exactly has it? |
| `differentiation` | Differentiation | 12 | Why this over what exists? Is it generic? |
| `revenue` | Revenue Model | 12 | Believable path to money for this product and creator? |
| `visual` | UI & Visual Design | 10 | Color, contrast, type, spacing, hierarchy, consistency |
| `ux` | UX & Onboarding | 10 | Time to first value, friction, flows, states |
| `retention` | Retention & Engagement | 12 | Why come back? Is there a loop? |
| `growth` | Growth & Distribution | 10 | Store listing / SEO, channels, virality |
| `technical` | Technical Quality | 10 | Architecture, performance, tests, security |
| `trust` | Trust & Compliance | 6 | Privacy, permissions, store policy, consent |
| `polish` | Polish & Store Readiness | 8 | Completeness, bugs, edge cases, ship-ready? |

**Applicability:** set `applicable: false` once in v1 for categories that do not apply (e.g. CLI → no `visual`). Script renormalizes weights. Do not flip later unless product type changes.

---

## idea — Idea & Problem (10)

**3:** Vague problem, no clear sufferer, or solution looking for a problem.  
**5:** Recognizable problem for a named audience; pain plausible but unproven.  
**7:** Clear ICP, painful JTBD, evidence from users/store/reviews or sourced domain knowledge.  
**9:** Narrow urgent problem; named competitors; proof people pay or churn without a fix.

**Verified by:** code, listing, url, text, export, screenshot

---

## differentiation — Differentiation (12)

**3:** Feature-parity clone; no named reason to switch.  
**5:** One real angle (niche, UX, price, platform) but easy to copy or weakly said.  
**7:** Clear defensible difference vs ≥3 named competitors with sources.  
**9:** Hard-to-copy wedge proven against named peers.

**Verified by:** listing, url, text, code, screenshot  
**Confidence:** cannot be `high` without competitor evidence (see SKILL competitor rules).

---

## revenue — Revenue Model (12)

**3:** No model, or model creator cannot collect, or ads with no placement plan.  
**5:** Model exists but unit economics / fit are hand-wavy.  
**7:** Fits audience + creator constraints; placement/pricing/consent have evidence.  
**9:** Credible ceiling math with labeled assumptions; matches comparable products with sources.

**Verified by:** code, export, listing, text, screenshot  
**Confidence:** cannot be `high` without competitor evidence.  
**Read:** `references/monetization-review.md` before scoring.

---

## visual — UI & Visual Design (10)

**3:** Clashing palette, illegible text, inconsistent components.  
**5:** Readable and consistent enough to ship; some hierarchy/density issues.  
**7:** Tight system; AA contrast on reviewed screens; one primary action.  
**9:** Distinctive polish that still passes a11y and consistency checks.

**Verified by:** screenshot, code  
**Read:** `references/design-review.md` before scoring.

---

## ux — UX & Onboarding (10)

**3:** Long path to value; permission walls; missing empty/error/offline.  
**5:** Core value reachable with friction; happy path works.  
**7:** Fast first value; clear flows; good state coverage.  
**9:** Onboarding and recovery intentional; friction justified/measured.

**Verified by:** screenshot, code, export, text

---

## retention — Retention & Engagement (12)

**3:** One-shot; no reason to return.  
**5:** A loop exists but weak or unmeasured.  
**7:** Clear return loop with triggers; backed by code or metrics.  
**9:** Loop + proof (metrics or strong design) vs comparables.

**Verified by:** code, export, screenshot, text

---

## growth — Growth & Distribution (10)

**3:** Weak listing/SEO; no channels; nothing shareable.  
**5:** Basic listing/landing; one plausible channel.  
**7:** Strong assets; clear channels; some share/referral surface.  
**9:** Listing + channels + measurable conversion/virality with sources.

**Verified by:** listing, url, export, screenshot, text

---

## technical — Technical Quality (10)

**3:** Fragile structure; secrets in repo; no tests; obvious perf footguns.  
**5:** Readable for stage; some tests or crash reporting; no glaring secrets.  
**7:** Consistent patterns; meaningful tests; release + security hygiene.  
**9:** Strong architecture/observability for stage; perf/reliability evidence.

**Verified by:** code, export  
**Read:** matching `references/stacks/*.md`.

---

## trust — Trust & Compliance (6)

**3:** Missing privacy policy; over-broad permissions; no required consent.  
**5:** Policy + permissions present; gaps vs data collected.  
**7:** Policy, consent, permissions, data-safety align with code.  
**9:** Tight alignment + store-policy awareness with evidence.

**Verified by:** code, listing, url, screenshot, text

---

## polish — Polish & Store Readiness (8)

**3:** Placeholders, broken edges, not shippable.  
**5:** Core flows work; rough edges; maybe soft-launchable.  
**7:** Store assets ready; edges handled on reviewed paths; release config sane.  
**9:** Ship-ready; strong store assets; few open critical/major findings.

**Verified by:** code, screenshot, listing, export
