---
masterg: 1
product: {{product}}
version: {{version}}
date: {{date}}
overall: {{overall}}
previous: {{previous}}
evidence_coverage: {{evidence_coverage}}
---
# MasterG: {{product}} · v{{version}}
> {{verdict_line}}

## Scores
| Category | Score | Δ |
|---|---|---|
{{score_rows}}

## Fix first
{{fix_first}}

## Open critical / major findings
{{open_findings}}

## Latest metrics
{{metrics}}

## Files
Report: MasterG/report.html
Data: {{data_path}}

Agent note: treat open critical findings as known context for this product.
Do not re-run MasterG unless the user asks.
