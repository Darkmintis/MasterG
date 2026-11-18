# Inputs

Record every input in `draft.inputs` with a stable `id` (`i1`, `i2`, …). Cite evidence via that id.

## Codebase

1. Read manifests/config first: `pubspec.yaml`, `package.json`, `AndroidManifest.xml`, `Info.plist`, `Cargo.toml`, etc.
2. Then entry points (`main.dart`, `main.ts`, `App.tsx`, …).
3. Then a sample of feature files — never claim full coverage on large repos.
4. Set `coverage.files_reviewed` and `coverage.files_total` honestly (estimate total if needed; say so in `notes`).
5. Use the matching stack checklist: `references/stacks/`.

## Screenshots

1. For each image: name the screen, then describe what is visible.
2. Apply `references/design-review.md`.
3. Cite as `<filename> - <area>` (e.g. `home.png - primary CTA`).
4. No vision available → do not invent UI; leave `visual`/`ux` unverified or low confidence and say so in coverage.

## Store / analytics exports

1. Inspect headers first.
2. Map columns to canonical ids in `references/metrics.md`.
3. Ignore unknown columns; document the mapping in the metric `note` or coverage notes.
4. Mapping unclear → ask **one** question; if unanswered, skip those columns.
5. Put raw files under `MasterG/inputs/vN/exports/` (gitignored).

## Listing text & URLs

- Use for `growth`, `trust`, `differentiation`.
- Quote short excerpts (≤200 chars). Never invent store stats.

## Unsupported type

Say so in coverage `notes` and continue with the rest. Do not fake a score from missing input.
