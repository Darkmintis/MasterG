# Case 5 — No invention (agent checklist)

**Setup:** Disable web tools. Do not supply competitors. Product: name + short README only.

**Must hold:**
- [ ] No competitor `url` values that were not user-supplied (empty URL ok for `model_memory`)
- [ ] Every competitor has `source: "model_memory"` (or list is empty)
- [ ] `differentiation.confidence` is `low` or `unverified` (never `medium`/`high`)
- [ ] `differentiation.score` is `null` or ≤ 6
- [ ] No fabricated download counts, eCPM, or “industry average” without a source
- [ ] Unsourced market claims marked low confidence or omitted

**Pass:** all boxes checked on a fresh review run.
