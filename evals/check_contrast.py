#!/usr/bin/env python3
"""AA contrast gate for MasterG theme text pairs."""

from __future__ import annotations

import sys

PAIRS = [
    ("ink/paper", "#2B1D14", "#F6F0E6"),
    ("muted/paper", "#7A6656", "#F6F0E6"),
    ("accent-text/paper", "#9C4626", "#F6F0E6"),
    ("tab ink/accent-text", "#FFFBF4", "#9C4626"),
    ("mocha-text/paper", "#8B5230", "#F6F0E6"),
    ("espresso/paper", "#4A2E1D", "#F6F0E6"),
    ("critical/crit-bg", "#B3261E", "#F8E8E6"),
    ("major/major-bg", "#8A5A12", "#F5EBD8"),
    ("minor/minor-bg", "#5E5348", "#EFE8DE"),
    ("dark ink/bg", "#F0E6D8", "#1A120D"),
    ("dark muted/bg", "#A8927E", "#1A120D"),
    ("dark accent/bg", "#E08A5F", "#1A120D"),
    ("dark crit/crit-bg", "#F07167", "#3A1E1C"),
    ("dark major/major-bg", "#E0B35A", "#3A2E18"),
]


def lum(h: str) -> float:
    h = h.lstrip("#")
    r, g, b = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]

    def f(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a: str, b: str) -> float:
    L1, L2 = lum(a), lum(b)
    hi, lo = max(L1, L2), min(L1, L2)
    return (hi + 0.05) / (lo + 0.05)


fails = []
for name, fg, bg in PAIRS:
    r = ratio(fg, bg)
    if r < 4.5:
        fails.append(f"{name}: {r:.2f}")

if fails:
    print("FAIL AA < 4.5:")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print(f"OK: AA contrast ({len(PAIRS)} pairs >= 4.5)")
