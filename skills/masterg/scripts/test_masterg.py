#!/usr/bin/env python3
"""Unit tests for masterg.py — run: python3 test_masterg.py"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import masterg as mg


def minimal_draft(**overrides):
    # Varied scores avoid the "lazy scoring" calibration hard-fail on finalize.
    score_by_id = {
        "idea": 6,
        "differentiation": 4,
        "revenue": 3,
        "visual": 5,
        "ux": 5,
        "retention": 4,
        "growth": 4,
        "technical": 6,
        "trust": 5,
        "polish": 4,
    }
    cats = []
    for cid in mg.CATEGORY_IDS:
        cats.append(
            {
                "id": cid,
                "applicable": True,
                "score": score_by_id[cid],
                "confidence": "high",
                "summary": f"{cid} ok",
                "why": "evidence-backed middle of the road",
                "why_not_higher": "needs stronger proof for +2",
                "evidence": [{"input": "i1", "ref": "README.md:1", "quote": "sample app"}],
            }
        )
    draft = {
        "schema": "masterg.draft/1",
        "product": {
            "name": "Sample",
            "type": "mobile_app",
            "platforms": ["android"],
            "stack": "flutter",
            "one_liner": "A sample habit tracker",
            "audience": "indie users",
            "stage": "beta",
            "goal": "earn",
            "url": "",
            "repo": "",
        },
        "assumptions": ["Audience inferred from README"],
        "inputs": [{"id": "i1", "kind": "code", "path": "README.md", "note": "readme"}],
        "coverage": {
            "files_reviewed": 3,
            "files_total": 10,
            "screenshots": 0,
            "exports": 0,
            "web_access": False,
            "notes": "sampled",
        },
        "competitors": [
            {
                "name": "Habitica",
                "url": "https://habitica.com",
                "overlap": "high",
                "why_relevant": "same core habit loop",
                "source": "user",
            }
        ],
        "categories": cats,
        "findings": [
            {
                "key": "revenue/no-ad-frequency-cap",
                "category": "revenue",
                "severity": "major",
                "title": "No ad frequency cap",
                "why": "Interstitials can fire without limit",
                "counterpoint": "Fine if ads are rewarded-only",
                "evidence": [{"input": "i1", "ref": "lib/ads.dart:1", "quote": "showInterstitial()"}],
                "fix": "Add a 3-minute cap",
                "effort": "S",
                "impact": "H",
            }
        ],
        "previous_findings_review": [],
        "strengths": [
            {
                "title": "Clear one-liner in README",
                "evidence": [{"input": "i1", "ref": "README.md:1", "quote": "habit tracker"}],
            }
        ],
        "metrics": [],
        "verdict_line": "Average indie build with a monetization gap.",
        "calibration_note": "",
    }
    draft.update(overrides)
    return draft


class ValidateTests(unittest.TestCase):
    def test_valid_draft(self):
        errs = mg.validate_draft(minimal_draft())
        self.assertEqual(errs, [])

    def test_unverified_needs_null_score(self):
        d = minimal_draft()
        d["categories"][0]["confidence"] = "unverified"
        d["categories"][0]["score"] = 4
        d["categories"][0]["evidence"] = []
        errs = mg.validate_draft(d)
        self.assertTrue(any("unverified" in e for e in errs))

    def test_finding_key_pattern(self):
        d = minimal_draft()
        d["findings"][0]["key"] = "bad_key"
        errs = mg.validate_draft(d)
        self.assertTrue(any("kebab" in e or "key" in e for e in errs))


class CapsTests(unittest.TestCase):
    def test_confidence_cap(self):
        d = minimal_draft()
        d["categories"][0]["confidence"] = "low"
        d["categories"][0]["score"] = 8
        errs = mg.check_confidence_caps(d)
        self.assertTrue(any("cap" in e for e in errs))

    def test_score_9_needs_sourced_competitor(self):
        d = minimal_draft()
        d["competitors"] = [
            {
                "name": "X",
                "url": "",
                "overlap": "low",
                "why_relevant": "guess",
                "source": "model_memory",
            }
        ]
        d["categories"][0]["score"] = 9
        errs = mg.check_competitor_rules(d)
        self.assertTrue(any("≥ 9" in e or ">=" in e or "9" in e for e in errs))


class SecretTests(unittest.TestCase):
    def test_secret_blocked(self):
        d = minimal_draft()
        d["categories"][0]["evidence"][0]["quote"] = "api_key=sk-abcdefghijklmnopqrstuvwxyz"
        errs = mg.scan_secrets(d)
        self.assertTrue(len(errs) >= 1)


class DeltaTests(unittest.TestCase):
    def test_overall_and_finding_status(self):
        rubric = mg.load_rubric()
        d1 = minimal_draft()
        data1 = mg.compute_data(d1, rubric, 1, None, [])
        self.assertIsNotNone(data1["overall"])
        self.assertEqual(data1["findings"][0]["status"], "new")

        d2 = minimal_draft()
        d2["categories"][4]["score"] = 7  # ux up
        d2["previous_findings_review"] = [
            {
                "key": "revenue/no-ad-frequency-cap",
                "status": "persisting",
                "evidence": [{"input": "i1", "ref": "lib/ads.dart:1", "quote": "still there"}],
            }
        ]
        data2 = mg.compute_data(d2, rubric, 2, data1, [])
        self.assertEqual(data2["findings"][0]["status"], "persisting")
        ux = next(s for s in data2["scores"] if s["id"] == "ux")
        self.assertEqual(ux["delta"], 2)

    def test_metric_not_comparable(self):
        rubric = mg.load_rubric()
        d1 = minimal_draft(
            metrics=[
                {"name": "installs", "value": 100, "period": "2026-09", "source": "i1", "note": ""}
            ]
        )
        data1 = mg.compute_data(d1, rubric, 1, None, [])
        d2 = minimal_draft(
            metrics=[
                {"name": "installs", "value": 150, "period": "2026-10", "source": "i1", "note": ""}
            ]
        )
        data2 = mg.compute_data(d2, rubric, 2, data1, [])
        self.assertEqual(data2["metric_deltas"][0]["status"], "not_comparable")

    def test_metric_comparable(self):
        rubric = mg.load_rubric()
        d1 = minimal_draft(
            metrics=[
                {"name": "installs", "value": 100, "period": "2026-10", "source": "i1", "note": ""}
            ]
        )
        data1 = mg.compute_data(d1, rubric, 1, None, [])
        d2 = minimal_draft(
            metrics=[
                {"name": "installs", "value": 150, "period": "2026-10", "source": "i1", "note": ""}
            ]
        )
        data2 = mg.compute_data(d2, rubric, 2, data1, [])
        self.assertEqual(data2["metric_deltas"][0]["status"], "compared")
        self.assertEqual(data2["metric_deltas"][0]["delta_abs"], 50)


class CalibrationTests(unittest.TestCase):
    def test_first_review_high_mean_needs_note(self):
        d = minimal_draft()
        # Spread scores so only the high-mean warning fires (not lazy ±1).
        spread = [6, 7, 8, 9, 8, 9, 7, 8, 9, 8]  # mean 7.9, range 3
        for i, c in enumerate(d["categories"]):
            c["score"] = spread[i]
        errs, warnings = mg.calibration_checks(d, is_first=True)
        self.assertTrue(any("mean" in w for w in warnings))
        self.assertTrue(len(errs) >= 1)
        d["calibration_note"] = (
            "First review mean is high because of competitor parity justification."
        )
        errs2, _ = mg.calibration_checks(d, is_first=True)
        self.assertEqual(errs2, [])


class FinalizePipelineTests(unittest.TestCase):
    def test_finalize_writes_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            vdir = project / "MasterG" / "reports" / "v1"
            vdir.mkdir(parents=True)
            (vdir / "draft.json").write_text(json.dumps(minimal_draft()), encoding="utf-8")
            rc = mg.cmd_finalize(project)
            self.assertEqual(rc, 0)
            self.assertTrue((vdir / "data.json").is_file())
            self.assertTrue((project / "MasterG" / "report.html").is_file())
            self.assertTrue((project / "MasterG" / "MasterG.md").is_file())
            self.assertTrue((project / "MasterG" / "history.json").is_file())
            self.assertTrue((project / "MasterG" / ".gitignore").is_file())

    def test_previous_findings_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            v1 = project / "MasterG" / "reports" / "v1"
            v1.mkdir(parents=True)
            (v1 / "draft.json").write_text(json.dumps(minimal_draft()), encoding="utf-8")
            self.assertEqual(mg.cmd_finalize(project), 0)
            v2 = project / "MasterG" / "reports" / "v2"
            v2.mkdir(parents=True)
            d2 = minimal_draft()
            d2["previous_findings_review"] = []  # missing keys
            (v2 / "draft.json").write_text(json.dumps(d2), encoding="utf-8")
            self.assertEqual(mg.cmd_finalize(project), 1)


class InsufficientEvidenceTests(unittest.TestCase):
    def test_no_overall_when_coverage_low(self):
        rubric = mg.load_rubric()
        d = minimal_draft()
        for i, c in enumerate(d["categories"]):
            if i < 8:
                c["score"] = None
                c["confidence"] = "unverified"
                c["evidence"] = []
                c["summary"] = "unverified"
                c["why"] = ""
                c["why_not_higher"] = ""
        data = mg.compute_data(d, rubric, 1, None, [])
        self.assertLess(data["evidence_coverage"], 0.5)
        self.assertIsNone(data["overall"])


if __name__ == "__main__":
    unittest.main()
