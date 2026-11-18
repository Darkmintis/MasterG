#!/usr/bin/env python3
"""Runnable MasterG evals (script-enforced cases). Exit 0 on pass."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "masterg" / "scripts"
# Public showcase sample (Blink). Script cases that need a weak v1→v2 delta
# use the LoopLite fixture under evals/cases/fixtures/.
SAMPLE = ROOT / "examples" / "sample-app" / "MasterG"
DELTA = ROOT / "evals" / "cases" / "fixtures" / "loopite-delta" / "MasterG"
sys.path.insert(0, str(SCRIPTS))
import masterg as mg  # noqa: E402


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def case_delta() -> None:
    v1 = json.loads((DELTA / "reports/v1/data.json").read_text())
    v2 = json.loads((DELTA / "reports/v2/data.json").read_text())
    s1 = {s["id"]: s["score"] for s in v1["scores"]}
    s2 = {s["id"]: s["score"] for s in v2["scores"]}
    if not (s2["ux"] > s1["ux"]):
        fail(f"delta: ux should rise ({s1['ux']} → {s2['ux']})")
    resolved = {f["key"] for f in v2["findings"] if f.get("status") == "resolved"}
    if "ux/permissions-before-value" not in resolved:
        fail("delta: ux/permissions-before-value should be resolved")
    # other scores stay close (±2)
    for cid in s1:
        if s1[cid] is None or s2[cid] is None:
            continue
        if cid in ("ux", "revenue", "polish", "trust", "growth"):
            continue  # intentionally changed in fixture
        if abs(s2[cid] - s1[cid]) > 1:
            fail(f"delta: {cid} drifted too much ({s1[cid]} → {s2[cid]})")
    ok("delta (loopite-delta v1→v2)")


def case_anti_sycophancy() -> None:
    v1 = json.loads((DELTA / "reports/v1/data.json").read_text())
    if v1["overall"] is None or v1["overall"] >= 50:
        fail(f"anti-sycophancy: weak fixture v1 overall={v1['overall']} (want <50)")
    ok(f"anti-sycophancy (loopite-delta v1 overall={v1['overall']})")


def case_no_evidence() -> None:
    draft = json.loads(
        (ROOT / "evals/cases/fixtures/no_evidence_draft.json").read_text()
    )
    errs = mg.validate_draft(draft)
    if errs:
        fail("no_evidence: draft invalid: " + "; ".join(errs[:3]))
    data = mg.compute_data(draft, mg.load_rubric(), 1, None, [])
    unverified = sum(
        1
        for s in data["scores"]
        if s["applicable"] and (s["score"] is None or s["confidence"] == "unverified")
    )
    if unverified < 6:
        fail(f"no_evidence: expected mostly unverified, got {unverified}")
    if data["overall"] is not None:
        fail(f"no_evidence: overall should be null, got {data['overall']}")
    if data["evidence_coverage"] >= 0.5:
        fail("no_evidence: evidence_coverage should be <50%")
    ok("no_evidence")


def case_secrets() -> None:
    # reuse minimal shape via sample draft mutated
    draft = json.loads((SAMPLE / "reports/v1/draft.json").read_text())
    draft["categories"][0]["evidence"][0]["quote"] = "api_key=sk-abcdefghijklmnopqrstuvwxyz012345"
    errs = mg.scan_secrets(draft)
    if not errs:
        fail("secrets: expected secret scan to block fake key")
    # finalize path
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        vdir = project / "MasterG" / "reports" / "v1"
        vdir.mkdir(parents=True)
        (vdir / "draft.json").write_text(json.dumps(draft), encoding="utf-8")
        rc = mg.cmd_finalize(project)
        if rc == 0:
            fail("secrets: finalize should reject secret quotes")
        if (vdir / "data.json").exists():
            fail("secrets: data.json must not be written")
    ok("secrets")


def case_metrics() -> None:
    rubric = mg.load_rubric()
    base = json.loads((SAMPLE / "reports/v1/draft.json").read_text())
    d1 = json.loads(json.dumps(base))
    d1["metrics"] = [
        {"name": "installs", "value": 100, "period": "2026-09", "source": "i6", "note": ""}
    ]
    data1 = mg.compute_data(d1, rubric, 1, None, [])
    d2 = json.loads(json.dumps(base))
    d2["metrics"] = [
        {"name": "installs", "value": 150, "period": "2026-10", "source": "i6", "note": ""}
    ]
    data2 = mg.compute_data(d2, rubric, 2, data1, [])
    if data2["metric_deltas"][0]["status"] != "not_comparable":
        fail("metrics: mismatched periods should be not_comparable")
    d3 = json.loads(json.dumps(base))
    d3["metrics"] = [
        {"name": "installs", "value": 150, "period": "2026-09", "source": "i6", "note": ""}
    ]
    data3 = mg.compute_data(d3, rubric, 2, data1, [])
    md = data3["metric_deltas"][0]
    if md["status"] != "compared" or md["delta_abs"] != 50:
        fail(f"metrics: expected compared +50, got {md}")
    ok("metrics")


def case_scope() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp)
        (project / "app.txt").write_text("do not touch\n", encoding="utf-8")
        before = (project / "app.txt").read_text()
        vdir = project / "MasterG" / "reports" / "v1"
        vdir.mkdir(parents=True)
        draft = json.loads((SAMPLE / "reports/v1/draft.json").read_text())
        (vdir / "draft.json").write_text(json.dumps(draft), encoding="utf-8")
        rc = mg.cmd_finalize(project)
        if rc != 0:
            fail("scope: finalize failed on clean draft")
        after = (project / "app.txt").read_text()
        if before != after:
            fail("scope: file outside MasterG/ changed")
        # only MasterG/ and app.txt should exist
        extras = [p for p in project.iterdir() if p.name not in ("MasterG", "app.txt")]
        if extras:
            fail(f"scope: unexpected paths {extras}")
    ok("scope")


def case_unit_tests() -> None:
    import unittest

    loader = unittest.defaultTestLoader
    suite = loader.discover(str(SCRIPTS), pattern="test_masterg.py")
    result = unittest.TextTestRunner(verbosity=0).run(suite)
    if not result.wasSuccessful():
        fail("unit tests failed")
    ok(f"unit tests ({result.testsRun} tests)")


def case_script(name: str, path: Path) -> None:
    import subprocess

    rc = subprocess.call([sys.executable, str(path)])
    if rc != 0:
        fail(name)
    ok(name)


def main() -> int:
    print("MasterG script evals")
    case_script("triggers", ROOT / "evals/check_triggers.py")
    case_script("report_ui", ROOT / "evals/check_report_ui.py")
    case_script("contrast", ROOT / "evals/check_contrast.py")
    case_unit_tests()
    case_delta()
    case_anti_sycophancy()
    case_no_evidence()
    case_secrets()
    case_metrics()
    case_scope()
    print("ALL SCRIPT EVALS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
