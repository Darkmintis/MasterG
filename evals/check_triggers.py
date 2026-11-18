#!/usr/bin/env python3
"""Ensure SKILL.md description covers should_trigger stems."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
skill = (ROOT / "skills/masterg/SKILL.md").read_text(encoding="utf-8")
m = re.search(r"^description:\s*>-\s*\n((?:  .*\n)+)", skill, re.M)
if not m:
    m2 = re.search(r"^description:\s*(.+)$", skill, re.M)
    desc = m2.group(1).strip().strip("\"'") if m2 else ""
else:
    desc = re.sub(r"^  ", "", m.group(1), flags=re.M).replace("\n", " ")

body_lower = (desc + "\n" + skill).lower()
data = json.loads((ROOT / "evals/trigger-queries.json").read_text())

required_stems = [
    "review",
    "rate",
    "roast",
    "store readiness",
    "play console",
    "is my app good",
    "fix first",
    "masterg",
]
missing = [s for s in required_stems if s not in body_lower]
if missing:
    print("FAIL: SKILL.md missing trigger stems:", ", ".join(missing))
    sys.exit(1)

# Exclusions must be present for common near-misses named in the description
desc_l = desc.lower()
if "not for" not in desc_l:
    print("FAIL: description should include a 'Not for …' exclusion clause")
    sys.exit(1)

print(
    f"OK: trigger stems present "
    f"({len(data['should_trigger'])} should / {len(data['should_not_trigger'])} should-not listed)"
)
