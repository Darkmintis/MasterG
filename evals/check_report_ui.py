#!/usr/bin/env python3
"""Assert report.template.html has the premium UI contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tpl = (ROOT / "skills/masterg/assets/report.template.html").read_text(encoding="utf-8")

required = [
    ('data-theme toggle', 'data-theme'),
    ("theme-light button", 'id="theme-light"'),
    ("theme-dark button", 'id="theme-dark"'),
    ("sticky topbar", "class=\"topbar\""),
    ("custom dropdown", "class=\"dd\""),
    ("dropdown menu", "dd-menu"),
    ("no native select", None),  # special
    ("custom scrollbar", "::-webkit-scrollbar"),
    ("scrollbar-color", "scrollbar-color"),
    ("table horizontal scroll", "table-scroll"),
    ("skip link", "skip-link"),
    ("reduced motion", "prefers-reduced-motion"),
    ("print stylesheet", "@media print"),
    ("serif scores", "--serif"),
    ("light paper bg", "#F6F0E6"),
    ("dark espresso bg", "#1A120D"),
    ("no em dash", None),
    ("export pdf button", 'id="btn-export-pdf"'),
    ("category bars chart", "chart-category-bars"),
    ("overall line chart", "chart-overall-line"),
    ("findings donut", "chart-findings-donut"),
    ("chart grow animation", "animateChartsIn"),
]

fails = []
for name, needle in required:
    if name == "no native select":
        if re.search(r"<select\b", tpl):
            fails.append("native <select> still present")
    elif name == "no em dash":
        if "—" in tpl or "–" in tpl:
            fails.append("em/en dash found in report template")
    elif needle not in tpl:
        fails.append(f"missing: {name}")

if fails:
    print("FAIL:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"OK: report UI contract ({len(required)} checks)")
