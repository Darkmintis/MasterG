#!/usr/bin/env python3
"""MasterG finalize pipeline. Python 3.9+, stdlib only. No network."""

from __future__ import annotations

import argparse
import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CATEGORY_IDS = [
    "idea",
    "differentiation",
    "revenue",
    "visual",
    "ux",
    "retention",
    "growth",
    "technical",
    "trust",
    "polish",
]

CONFIDENCE_CAPS = {"high": 10, "medium": 8, "low": 6, "unverified": None}
SEVERITY_WEIGHT = {"critical": 4, "major": 3, "minor": 2, "nit": 1}
IMPACT_WEIGHT = {"H": 3, "M": 2, "L": 1}
EFFORT_WEIGHT = {"S": 1, "M": 2, "L": 3}
METRIC_IDS = {
    "installs",
    "uninstalls",
    "dau",
    "mau",
    "retention_d1",
    "retention_d7",
    "retention_d30",
    "rating_avg",
    "rating_count",
    "crash_free_users_pct",
    "anr_rate_pct",
    "store_listing_conversion",
    "revenue",
    "ad_revenue",
    "ecpm",
    "session_length",
}
VERDICT_BANDS = [
    (0, 34, "not_viable", "Not viable as is"),
    (35, 49, "weak", "Weak"),
    (50, 64, "average", "Average"),
    (65, 79, "strong", "Strong"),
    (80, 100, "exceptional", "Exceptional"),
]

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"(?i)(?:secret|token|passwd|password)\s*[:=]\s*['\"]?[^\s'\"]{8,}"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9\-._~+/]+=*"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
]

FINDING_KEY_RE = re.compile(
    r"^(idea|differentiation|revenue|visual|ux|retention|growth|technical|trust|polish)/"
    r"[a-z0-9]+(?:-[a-z0-9]+)*$"
)
INPUT_ID_RE = re.compile(r"^i[0-9]+$")

SKILL_ROOT = Path(__file__).resolve().parent.parent
ASSETS = SKILL_ROOT / "assets"


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def masterg_dir(project: Path) -> Path:
    return project / "MasterG"


def reports_dir(project: Path) -> Path:
    return masterg_dir(project) / "reports"


def version_dir(project: Path, version: int) -> Path:
    return reports_dir(project) / f"v{version}"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_rubric() -> Dict[str, Any]:
    return load_json(ASSETS / "rubric.json")


def existing_versions(project: Path) -> List[int]:
    """Finalized versions only (have data.json). Draft-only folders do not count."""
    rd = reports_dir(project)
    if not rd.is_dir():
        return []
    out = []
    for p in rd.iterdir():
        if p.is_dir() and p.name.startswith("v") and (p / "data.json").is_file():
            try:
                out.append(int(p.name[1:]))
            except ValueError:
                continue
    return sorted(out)


def latest_data(project: Path) -> Optional[Dict[str, Any]]:
    vers = existing_versions(project)
    if not vers:
        return None
    path = version_dir(project, vers[-1]) / "data.json"
    if not path.is_file():
        return None
    return load_json(path)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

class DraftError(Exception):
    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


def _req(obj: Dict[str, Any], keys: List[str], path: str, errors: List[str]) -> None:
    for k in keys:
        if k not in obj:
            errors.append(f"{path}: missing required field '{k}'")


def validate_evidence(items: Any, path: str, errors: List[str], input_ids: set) -> None:
    if not isinstance(items, list):
        errors.append(f"{path}: evidence must be an array")
        return
    for i, ev in enumerate(items):
        p = f"{path}[{i}]"
        if not isinstance(ev, dict):
            errors.append(f"{p}: must be an object")
            continue
        _req(ev, ["input", "ref", "quote"], p, errors)
        if "quote" in ev and isinstance(ev["quote"], str) and len(ev["quote"]) > 200:
            errors.append(f"{p}.quote: max 200 characters")
        if "input" in ev and ev["input"] not in input_ids:
            errors.append(f"{p}.input: unknown input id '{ev['input']}'")


def validate_draft(draft: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if not isinstance(draft, dict):
        return ["draft must be a JSON object"]

    _req(
        draft,
        [
            "schema",
            "product",
            "assumptions",
            "inputs",
            "coverage",
            "competitors",
            "categories",
            "findings",
            "previous_findings_review",
            "strengths",
            "metrics",
            "verdict_line",
            "calibration_note",
        ],
        "draft",
        errors,
    )
    if draft.get("schema") != "masterg.draft/1":
        errors.append("draft.schema must be 'masterg.draft/1'")

    product = draft.get("product")
    if isinstance(product, dict):
        _req(
            product,
            ["name", "type", "platforms", "stack", "one_liner", "audience", "stage", "goal", "url", "repo"],
            "product",
            errors,
        )
        if product.get("type") not in ("mobile_app", "web_app", "site", "game", "other"):
            errors.append("product.type invalid")
        if product.get("stage") not in ("idea", "prototype", "beta", "live"):
            errors.append("product.stage invalid")
        if product.get("goal") not in ("earn", "portfolio", "learning"):
            errors.append("product.goal invalid")
        if not product.get("name"):
            errors.append("product.name must be non-empty")
    else:
        errors.append("product must be an object")

    inputs = draft.get("inputs")
    input_ids: set = set()
    if isinstance(inputs, list):
        for i, inp in enumerate(inputs):
            p = f"inputs[{i}]"
            if not isinstance(inp, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(inp, ["id", "kind", "path", "note"], p, errors)
            iid = inp.get("id")
            if isinstance(iid, str):
                if not INPUT_ID_RE.match(iid):
                    errors.append(f"{p}.id: must match iN")
                if iid in input_ids:
                    errors.append(f"{p}.id: duplicate '{iid}'")
                input_ids.add(iid)
            if inp.get("kind") not in ("code", "screenshot", "export", "listing", "url", "text"):
                errors.append(f"{p}.kind invalid")
    else:
        errors.append("inputs must be an array")

    coverage = draft.get("coverage")
    if isinstance(coverage, dict):
        _req(
            coverage,
            ["files_reviewed", "files_total", "screenshots", "exports", "web_access", "notes"],
            "coverage",
            errors,
        )
    else:
        errors.append("coverage must be an object")

    comps = draft.get("competitors")
    if isinstance(comps, list):
        for i, c in enumerate(comps):
            p = f"competitors[{i}]"
            if not isinstance(c, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(c, ["name", "url", "overlap", "why_relevant", "source"], p, errors)
            if c.get("overlap") not in ("high", "medium", "low"):
                errors.append(f"{p}.overlap invalid")
            if c.get("source") not in ("web", "user", "model_memory"):
                errors.append(f"{p}.source invalid")
    else:
        errors.append("competitors must be an array")

    cats = draft.get("categories")
    if isinstance(cats, list):
        if len(cats) != 10:
            errors.append("categories: must contain exactly 10 entries")
        seen = set()
        for i, cat in enumerate(cats):
            p = f"categories[{i}]"
            if not isinstance(cat, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(
                cat,
                ["id", "applicable", "score", "confidence", "summary", "why", "why_not_higher", "evidence"],
                p,
                errors,
            )
            cid = cat.get("id")
            if cid not in CATEGORY_IDS:
                errors.append(f"{p}.id invalid")
            elif cid in seen:
                errors.append(f"{p}.id duplicate '{cid}'")
            else:
                seen.add(cid)
            conf = cat.get("confidence")
            if conf not in CONFIDENCE_CAPS:
                errors.append(f"{p}.confidence invalid")
            score = cat.get("score")
            applicable = cat.get("applicable")
            if applicable is False:
                if score is not None:
                    errors.append(f"{p}: non-applicable category must have score null")
            elif conf == "unverified":
                if score is not None:
                    errors.append(f"{p}: unverified confidence requires score null")
            else:
                if not isinstance(score, int) or not (1 <= score <= 10):
                    errors.append(f"{p}.score must be integer 1–10 when verified")
            validate_evidence(cat.get("evidence", []), f"{p}.evidence", errors, input_ids)
            if applicable and conf != "unverified":
                if not cat.get("evidence"):
                    errors.append(f"{p}: scored category needs at least one evidence item")
    else:
        errors.append("categories must be an array")

    findings = draft.get("findings")
    if isinstance(findings, list):
        keys = set()
        for i, fnd in enumerate(findings):
            p = f"findings[{i}]"
            if not isinstance(fnd, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(
                fnd,
                ["key", "category", "severity", "title", "why", "counterpoint", "evidence", "fix", "effort", "impact"],
                p,
                errors,
            )
            key = fnd.get("key")
            if isinstance(key, str):
                if not FINDING_KEY_RE.match(key):
                    errors.append(f"{p}.key: must be category/kebab-slug")
                if key in keys:
                    errors.append(f"{p}.key: duplicate '{key}'")
                keys.add(key)
                if fnd.get("category") and isinstance(key, str) and "/" in key:
                    if key.split("/", 1)[0] != fnd.get("category"):
                        errors.append(f"{p}.key category prefix must match category")
            if fnd.get("severity") not in SEVERITY_WEIGHT:
                errors.append(f"{p}.severity invalid")
            if fnd.get("effort") not in EFFORT_WEIGHT:
                errors.append(f"{p}.effort invalid")
            if fnd.get("impact") not in IMPACT_WEIGHT:
                errors.append(f"{p}.impact invalid")
            if not fnd.get("title"):
                errors.append(f"{p}.title must be non-empty")
            validate_evidence(fnd.get("evidence", []), f"{p}.evidence", errors, input_ids)
    else:
        errors.append("findings must be an array")

    pfr = draft.get("previous_findings_review")
    if not isinstance(pfr, list):
        errors.append("previous_findings_review must be an array")
    else:
        for i, row in enumerate(pfr):
            p = f"previous_findings_review[{i}]"
            if not isinstance(row, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(row, ["key", "status", "evidence"], p, errors)
            if row.get("status") not in ("resolved", "persisting", "regressed"):
                errors.append(f"{p}.status invalid")
            validate_evidence(row.get("evidence", []), f"{p}.evidence", errors, input_ids)

    strengths = draft.get("strengths")
    if isinstance(strengths, list):
        if len(strengths) > 3:
            errors.append("strengths: max 3")
        for i, s in enumerate(strengths):
            p = f"strengths[{i}]"
            if not isinstance(s, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(s, ["title", "evidence"], p, errors)
            if not s.get("evidence"):
                errors.append(f"{p}: evidence required")
            validate_evidence(s.get("evidence", []), f"{p}.evidence", errors, input_ids)
    else:
        errors.append("strengths must be an array")

    metrics = draft.get("metrics")
    if isinstance(metrics, list):
        for i, m in enumerate(metrics):
            p = f"metrics[{i}]"
            if not isinstance(m, dict):
                errors.append(f"{p}: must be an object")
                continue
            _req(m, ["name", "value", "period", "source", "note"], p, errors)
            if m.get("name") not in METRIC_IDS:
                errors.append(f"{p}.name: unknown metric id")
            if not isinstance(m.get("value"), (int, float)):
                errors.append(f"{p}.value must be a number")
            if not m.get("period"):
                errors.append(f"{p}.period required")
    else:
        errors.append("metrics must be an array")

    if not isinstance(draft.get("assumptions"), list):
        errors.append("assumptions must be an array")
    if not isinstance(draft.get("verdict_line"), str) or not draft.get("verdict_line"):
        errors.append("verdict_line must be a non-empty string")
    if not isinstance(draft.get("calibration_note"), str):
        errors.append("calibration_note must be a string (empty ok)")

    return errors


def scan_secrets(draft: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    def check(quote: str, where: str) -> None:
        for pat in SECRET_PATTERNS:
            if pat.search(quote):
                errors.append(
                    f"{where}: evidence quote looks like a secret — redact it "
                    f"(pattern matched). Quotes must never contain keys/tokens/passwords."
                )
                return

    for i, cat in enumerate(draft.get("categories") or []):
        for j, ev in enumerate(cat.get("evidence") or []):
            check(str(ev.get("quote", "")), f"categories[{i}].evidence[{j}]")
    for i, fnd in enumerate(draft.get("findings") or []):
        for j, ev in enumerate(fnd.get("evidence") or []):
            check(str(ev.get("quote", "")), f"findings[{i}].evidence[{j}]")
    for i, s in enumerate(draft.get("strengths") or []):
        for j, ev in enumerate(s.get("evidence") or []):
            check(str(ev.get("quote", "")), f"strengths[{i}].evidence[{j}]")
    for i, row in enumerate(draft.get("previous_findings_review") or []):
        for j, ev in enumerate(row.get("evidence") or []):
            check(str(ev.get("quote", "")), f"previous_findings_review[{i}].evidence[{j}]")
    return errors


def check_confidence_caps(draft: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for cat in draft.get("categories") or []:
        if not cat.get("applicable", True):
            continue
        conf = cat.get("confidence")
        score = cat.get("score")
        cap = CONFIDENCE_CAPS.get(conf)
        if cap is None:
            continue
        if isinstance(score, int) and score > cap:
            errors.append(
                f"category '{cat.get('id')}': score {score} exceeds confidence cap "
                f"for '{conf}' (max {cap})"
            )
    return errors


def check_competitor_rules(draft: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    comps = draft.get("competitors") or []
    sourced = [c for c in comps if c.get("source") in ("web", "user")]
    for cat in draft.get("categories") or []:
        if not cat.get("applicable", True):
            continue
        score = cat.get("score")
        conf = cat.get("confidence")
        cid = cat.get("id")
        if isinstance(score, int) and score >= 9 and not sourced:
            errors.append(
                f"category '{cid}': score ≥ 9 requires a competitor with source 'web' or 'user'"
            )
        if cid in ("differentiation", "revenue") and conf == "high" and not sourced:
            errors.append(
                f"category '{cid}': confidence 'high' requires competitor evidence "
                f"(source 'web' or 'user')"
            )
        # model_memory-only → differentiation capped at low
        if cid == "differentiation" and comps and not sourced:
            if conf in ("medium", "high") or (isinstance(score, int) and score > 6):
                errors.append(
                    "category 'differentiation': only model_memory competitors → "
                    "confidence must be 'low' (max score 6)"
                )
    return errors


def check_previous_findings(draft: Dict[str, Any], previous: Optional[Dict[str, Any]]) -> List[str]:
    if previous is None:
        return []
    errors: List[str] = []
    prev_keys = {f["key"] for f in previous.get("findings") or []}
    reviewed = {r["key"]: r for r in draft.get("previous_findings_review") or []}
    missing = sorted(prev_keys - set(reviewed))
    if missing:
        errors.append(
            "previous_findings_review missing keys: " + ", ".join(missing)
            + ". Every previous finding key must be resolved|persisting|regressed."
        )
    return errors


def calibration_checks(
    draft: Dict[str, Any], is_first: bool
) -> Tuple[List[str], List[str]]:
    """Returns (errors, warnings). Warnings must be addressed in calibration_note."""
    errors: List[str] = []
    warnings: List[str] = []

    verified_scores = []
    unverified = 0
    for cat in draft.get("categories") or []:
        if not cat.get("applicable", True):
            continue
        if cat.get("confidence") == "unverified" or cat.get("score") is None:
            unverified += 1
        elif isinstance(cat.get("score"), int):
            verified_scores.append(cat["score"])

    note = (draft.get("calibration_note") or "").strip().lower()

    if is_first and verified_scores:
        mean = sum(verified_scores) / len(verified_scores)
        if mean > 7:
            msg = f"first review mean verified score is {mean:.1f} (>7)"
            warnings.append(msg)
            if "mean" not in note and "average" not in note and "first review" not in note and str(int(mean)) not in note:
                # require note to mention calibration / justification
                if "calibrat" not in note and "justif" not in note and "because" not in note:
                    errors.append(
                        "calibration warning not addressed in calibration_note: " + msg
                    )

    if len(verified_scores) >= 3:
        if max(verified_scores) - min(verified_scores) <= 2 and all(
            abs(s - verified_scores[0]) <= 1 for s in verified_scores
        ):
            msg = "all verified scores within ±1 of each other (lazy scoring)"
            warnings.append(msg)
            if "lazy" not in note and "within" not in note and "similar" not in note and "tight" not in note:
                errors.append(
                    "calibration warning not addressed in calibration_note: " + msg
                )

    if unverified > 3:
        msg = f"more than 3 categories unverified ({unverified})"
        warnings.append(msg)
        if "unverified" not in note and "coverage" not in note and "evidence" not in note:
            errors.append(
                "calibration warning not addressed in calibration_note: " + msg
            )

    return errors, warnings


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def verdict_band(overall: Optional[float]) -> Tuple[Optional[str], Optional[str]]:
    if overall is None:
        return None, None
    for lo, hi, bid, label in VERDICT_BANDS:
        if lo <= overall <= hi:
            return bid, label
    return None, None


def priority_score(finding: Dict[str, Any]) -> float:
    return (
        SEVERITY_WEIGHT[finding["severity"]]
        * IMPACT_WEIGHT[finding["impact"]]
        / EFFORT_WEIGHT[finding["effort"]]
    )


def compute_data(
    draft: Dict[str, Any],
    rubric: Dict[str, Any],
    version: int,
    previous: Optional[Dict[str, Any]],
    warnings: List[str],
) -> Dict[str, Any]:
    rub_cats = {c["id"]: c for c in rubric["categories"]}
    applicable = [c for c in draft["categories"] if c.get("applicable", True)]
    total_weight = sum(rub_cats[c["id"]]["weight"] for c in applicable)
    if total_weight <= 0:
        total_weight = 100

    verified_weight = 0.0
    weighted_sum = 0.0
    scores_out = []

    prev_scores = {}
    if previous:
        for s in previous.get("scores") or []:
            prev_scores[s["id"]] = s.get("score")

    for cat in draft["categories"]:
        cid = cat["id"]
        rc = rub_cats[cid]
        weight = rc["weight"]
        renorm = (weight / total_weight) * 100 if cat.get("applicable", True) else 0
        score = cat.get("score")
        contrib = None
        delta = None
        if cat.get("applicable", True) and score is not None and cat.get("confidence") != "unverified":
            verified_weight += weight
            # contribution toward 0–100 overall
            contrib = (weight / total_weight) * score * 10
            weighted_sum += contrib
        if cid in prev_scores and score is not None and prev_scores[cid] is not None:
            if previous and previous.get("rubric_version") != rubric.get("rubric_version"):
                # same ids assumed comparable in v1.0; flag only if we add changed_defs later
                delta = score - prev_scores[cid]
            else:
                delta = score - prev_scores[cid]
        scores_out.append(
            {
                "id": cid,
                "name": rc["name"],
                "weight": weight,
                "weight_renormalized": round(renorm, 4) if cat.get("applicable", True) else 0,
                "applicable": cat.get("applicable", True),
                "score": score,
                "confidence": cat.get("confidence"),
                "summary": cat.get("summary", ""),
                "why": cat.get("why", ""),
                "why_not_higher": cat.get("why_not_higher", ""),
                "evidence": cat.get("evidence", []),
                "weighted_contribution": None if contrib is None else round(contrib, 4),
                "delta": delta,
            }
        )

    evidence_coverage = (verified_weight / total_weight) if total_weight else 0.0
    overall = None
    if evidence_coverage >= 0.5 and verified_weight > 0:
        # weighted average of scores * 10
        # weighted_sum already uses renorm weights summing to 100 * score/10 effectively
        # Recalculate cleanly:
        num = 0.0
        den = 0.0
        for cat in draft["categories"]:
            if not cat.get("applicable", True):
                continue
            if cat.get("score") is None or cat.get("confidence") == "unverified":
                continue
            w = rub_cats[cat["id"]]["weight"]
            num += w * cat["score"]
            den += w
        overall = round((num / den) * 10, 1) if den else None

    band_id, band_label = verdict_band(overall)

    prev_overall = previous.get("overall") if previous else None
    overall_delta = None
    if overall is not None and prev_overall is not None:
        overall_delta = round(overall - prev_overall, 1)

    # Finding statuses
    prev_findings = {f["key"]: f for f in (previous or {}).get("findings") or []}
    review_map = {r["key"]: r for r in draft.get("previous_findings_review") or []}
    findings_out = []
    for fnd in draft["findings"]:
        key = fnd["key"]
        if key not in prev_findings:
            status = "new"
        else:
            status = review_map.get(key, {}).get("status", "persisting")
        item = deepcopy(fnd)
        item["status"] = status
        item["priority"] = round(priority_score(fnd), 4)
        findings_out.append(item)

    # resolved findings from previous that are not in current findings
    current_keys = {f["key"] for f in draft["findings"]}
    for key, prev_f in prev_findings.items():
        if key in current_keys:
            continue
        rev = review_map.get(key)
        if not rev:
            continue
        item = deepcopy(prev_f)
        item["status"] = rev["status"]
        item["priority"] = round(priority_score(prev_f), 4) if "severity" in prev_f else 0
        # keep for history of resolved
        findings_out.append(item)

    open_findings = [f for f in findings_out if f.get("status") in ("new", "persisting", "regressed")]
    open_findings_sorted = sorted(open_findings, key=lambda f: (-f["priority"], f["key"]))
    fix_first = [
        {
            "key": f["key"],
            "title": f["title"],
            "category": f["category"],
            "severity": f["severity"],
            "effort": f["effort"],
            "impact": f["impact"],
            "priority": f["priority"],
        }
        for f in open_findings_sorted[:3]
    ]

    metric_deltas = []
    prev_metrics = {(m["name"], m.get("period")): m for m in (previous or {}).get("metrics") or []}
    prev_by_name = {}
    for m in (previous or {}).get("metrics") or []:
        prev_by_name.setdefault(m["name"], []).append(m)

    for m in draft.get("metrics") or []:
        name = m["name"]
        # comparable if same name and same period length style — require identical period string match for same-period, else compare latest previous with same name only if periods differ → not_comparable unless periods equal format? Plan: different periods → still compute if both present but mark carefully.
        # Spec: "Different periods or sources → not_comparable"
        candidates = prev_by_name.get(name) or []
        match = None
        comparable = False
        for cand in reversed(candidates):
            if cand.get("period") == m.get("period") and cand.get("source") == m.get("source"):
                match = cand
                comparable = True
                break
        if match is None and candidates:
            match = candidates[-1]
            comparable = (
                match.get("period") == m.get("period")
                and match.get("source") == m.get("source")
            )
        delta_abs = None
        delta_pct = None
        status = "new"
        if match is not None:
            status = "compared" if comparable else "not_comparable"
            if comparable:
                delta_abs = m["value"] - match["value"]
                if match["value"] != 0:
                    delta_pct = round((delta_abs / match["value"]) * 100, 2)
        metric_deltas.append(
            {
                "name": name,
                "value": m["value"],
                "period": m["period"],
                "source": m["source"],
                "previous_value": None if match is None else match["value"],
                "previous_period": None if match is None else match.get("period"),
                "delta_abs": delta_abs,
                "delta_pct": delta_pct,
                "status": status,
            }
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "schema": "masterg.data/1",
        "version": version,
        "created_at": now,
        "rubric_version": rubric["rubric_version"],
        "previous_version": None if previous is None else previous.get("version"),
        "product": draft["product"],
        "assumptions": draft.get("assumptions") or [],
        "inputs": draft.get("inputs") or [],
        "coverage": draft.get("coverage"),
        "competitors": draft.get("competitors") or [],
        "rubric": [
            {"id": c["id"], "name": c["name"], "weight": c["weight"]}
            for c in rubric["categories"]
        ],
        "categories": draft["categories"],
        "scores": scores_out,
        "overall": overall,
        "overall_delta": overall_delta,
        "evidence_coverage": round(evidence_coverage, 4),
        "verdict_band": band_id,
        "verdict_band_label": band_label,
        "verdict_line": draft["verdict_line"],
        "findings": findings_out,
        "fix_first": fix_first,
        "strengths": draft.get("strengths") or [],
        "metrics": draft.get("metrics") or [],
        "metric_deltas": metric_deltas,
        "previous_findings_review": draft.get("previous_findings_review") or [],
        "calibration_note": draft.get("calibration_note") or "",
        "warnings": warnings,
    }
    return data


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------

def render_masterg_md(data: Dict[str, Any], template: str) -> str:
    product = data["product"]["name"]
    version = data["version"]
    date = data["created_at"][:10]
    overall = data["overall"]
    band = data.get("verdict_band_label") or "Insufficient evidence"
    if overall is None:
        overall_str = "n/a (Insufficient evidence)"
    else:
        overall_str = f"{overall:g} ({band})"
    prev = data.get("previous_version")
    prev_str = "-"
    if prev is not None and data.get("overall_delta") is not None:
        d = data["overall_delta"]
        sign = "+" if d >= 0 else ""
        prev_str = f"v{prev} ({sign}{d:g})"
    elif prev is not None:
        prev_str = f"v{prev}"

    cov = f"{data['evidence_coverage'] * 100:.0f}%"

    score_rows = []
    for s in data["scores"]:
        if not s["applicable"]:
            sc = "n/a"
        elif s["score"] is None:
            sc = "unverified"
        else:
            sc = str(s["score"])
        delta = "-"
        if s.get("delta") is not None:
            d = s["delta"]
            delta = f"{'+' if d >= 0 else ''}{d}"
        score_rows.append(f"| {s['name']} | {sc} | {delta} |")

    fix_lines = []
    for i, f in enumerate(data["fix_first"], 1):
        fix_lines.append(
            f"{i}. {f['title']} ({f['category']}, effort {f['effort']}, impact {f['impact']})"
        )
    if not fix_lines:
        fix_lines = ["1. (none)"]

    open_crit = [
        f"- {f['key']}: {f['title']}"
        for f in data["findings"]
        if f.get("status") in ("new", "persisting", "regressed")
        and f.get("severity") in ("critical", "major")
    ]
    if not open_crit:
        open_crit = ["- (none)"]

    metric_lines = []
    for md in data.get("metric_deltas") or []:
        if md["status"] == "not_comparable":
            metric_lines.append(f"- {md['name']}: {md['value']} (not_comparable)")
        elif md["delta_abs"] is not None:
            sign = "+" if md["delta_abs"] >= 0 else ""
            metric_lines.append(f"- {md['name']}: {md['value']} ({sign}{md['delta_abs']})")
        else:
            metric_lines.append(f"- {md['name']}: {md['value']}")
    if not metric_lines:
        metric_lines = ["- (none)"]

    # Keep under 60 lines: truncate open findings if needed
    text = template
    replacements = {
        "{{product}}": product,
        "{{version}}": str(version),
        "{{date}}": date,
        "{{overall}}": overall_str,
        "{{previous}}": prev_str,
        "{{evidence_coverage}}": cov,
        "{{verdict_line}}": data["verdict_line"],
        "{{score_rows}}": "\n".join(score_rows),
        "{{fix_first}}": "\n".join(fix_lines),
        "{{open_findings}}": "\n".join(open_crit[:12]),
        "{{metrics}}": "\n".join(metric_lines[:8]),
        "{{data_path}}": f"MasterG/reports/v{version}/data.json",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    lines = text.strip().splitlines()
    if len(lines) > 60:
        lines = lines[:59] + ["…(truncated)"]
    return "\n".join(lines) + "\n"


def inject_report(template: str, payload: Dict[str, Any]) -> str:
    blob = json.dumps(payload, ensure_ascii=False)
    # Escape </script> in JSON strings
    blob = blob.replace("</", "<\\/")
    marker = '<script type="application/json" id="masterg-data">'
    start = template.find(marker)
    if start < 0:
        raise RuntimeError("report template missing masterg-data script tag")
    end = template.find("</script>", start)
    if end < 0:
        raise RuntimeError("report template missing closing script tag")
    return template[: start + len(marker)] + blob + template[end:]


def history_entry(data: Dict[str, Any]) -> Dict[str, Any]:
    key_metrics = {
        m["name"]: m["value"] for m in (data.get("metrics") or [])[:6]
    }
    return {
        "version": data["version"],
        "date": data["created_at"][:10],
        "overall": data["overall"],
        "evidence_coverage": data["evidence_coverage"],
        "verdict_band": data.get("verdict_band"),
        "key_metrics": key_metrics,
    }


def build_root_payload(project: Path, latest: Dict[str, Any]) -> Dict[str, Any]:
    """Embed last 12 versions in full; older as summaries."""
    vers = existing_versions(project)
    full = []
    summaries = []
    # include newly written latest
    all_v = sorted(set(vers + [latest["version"]]))
    keep_full = set(all_v[-12:])
    for v in all_v:
        path = version_dir(project, v) / "data.json"
        if path.is_file():
            d = load_json(path)
        elif v == latest["version"]:
            d = latest
        else:
            continue
        if v in keep_full:
            full.append(d)
        else:
            summaries.append(history_entry(d))
    return {
        "latest_version": latest["version"],
        "versions": full,
        "older_summaries": summaries,
        "history": [history_entry(v) for v in full] + summaries,
    }


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(project: Path) -> int:
    mg = masterg_dir(project)
    exists = mg.is_dir()
    vers = existing_versions(project)
    next_v = (vers[-1] + 1) if vers else 1
    prev = latest_data(project)
    out: Dict[str, Any] = {
        "masterg_exists": exists,
        "next_version": next_v,
        "versions": vers,
        "previous_overall": None if prev is None else prev.get("overall"),
        "previous_version": None if prev is None else prev.get("version"),
        "previous_finding_keys": [],
        "previous_metrics": [],
    }
    if prev:
        out["previous_finding_keys"] = [
            {"key": f["key"], "title": f.get("title", "")}
            for f in prev.get("findings") or []
            if f.get("status") != "resolved"
        ]
        # also include resolved keys so agent can review all previous keys
        all_keys = [
            {"key": f["key"], "title": f.get("title", ""), "status": f.get("status")}
            for f in prev.get("findings") or []
        ]
        out["previous_finding_keys_all"] = all_keys
        out["previous_metrics"] = prev.get("metrics") or []
        out["previous_scores"] = [
            {"id": s["id"], "score": s.get("score")} for s in prev.get("scores") or []
        ]
    print(json.dumps(out, indent=2))
    return 0


def cmd_finalize(project: Path, version_arg: Optional[int] = None) -> int:
    rubric = load_rubric()
    vers = existing_versions(project)
    prev = latest_data(project)
    next_v = version_arg or ((vers[-1] + 1) if vers else 1)

    # If finalizing an existing draft folder
    vdir = version_dir(project, next_v)
    draft_path = vdir / "draft.json"
    if not draft_path.is_file():
        # allow agent to have written draft for next version
        print(
            f"ERROR: missing {draft_path}. Write draft.json there first "
            f"(next version is v{next_v}).",
            file=sys.stderr,
        )
        return 1

    if (vdir / "data.json").is_file() and version_arg is None:
        print(
            f"ERROR: {vdir / 'data.json'} already exists. Old versions are immutable. "
            f"Write a new draft under v{next_v + 1} or pass an explicit unused version.",
            file=sys.stderr,
        )
        return 1

    draft = load_json(draft_path)
    errors: List[str] = []
    errors.extend(validate_draft(draft))
    errors.extend(scan_secrets(draft))
    errors.extend(check_confidence_caps(draft))
    errors.extend(check_competitor_rules(draft))
    # previous is last finalized version < next_v
    previous = None
    earlier = [v for v in vers if v < next_v]
    if earlier:
        previous = load_json(version_dir(project, earlier[-1]) / "data.json")
    errors.extend(check_previous_findings(draft, previous))
    is_first = previous is None
    cal_errors, warnings = calibration_checks(draft, is_first)
    errors.extend(cal_errors)

    if errors:
        print("FINALIZE FAILED:\n" + "\n".join(f"- {e}" for e in errors), file=sys.stderr)
        return 1

    data = compute_data(draft, rubric, next_v, previous, warnings)
    write_json(vdir / "data.json", data)

    # templates
    md_template = (ASSETS / "masterg-md.template.md").read_text(encoding="utf-8")
    html_template = (ASSETS / "report.template.html").read_text(encoding="utf-8")

    md = render_masterg_md(data, md_template)
    (masterg_dir(project) / "MasterG.md").write_text(md, encoding="utf-8")

    # per-version report
    snap = inject_report(html_template, {"latest_version": next_v, "versions": [data], "older_summaries": [], "history": [history_entry(data)]})
    (vdir / "report.html").write_text(snap, encoding="utf-8")

    # root report with history
    # ensure this version is visible to build_root_payload
    root_payload = build_root_payload(project, data)
    root_html = inject_report(html_template, root_payload)
    (masterg_dir(project) / "report.html").write_text(root_html, encoding="utf-8")

    # history.json
    hist = []
    for v in existing_versions(project):
        p = version_dir(project, v) / "data.json"
        if p.is_file():
            hist.append(history_entry(load_json(p)))
    write_json(masterg_dir(project) / "history.json", hist)

    gi = masterg_dir(project) / ".gitignore"
    if not gi.exists():
        gi.write_text("inputs/\n", encoding="utf-8")

    result = {
        "ok": True,
        "version": next_v,
        "overall": data["overall"],
        "evidence_coverage": data["evidence_coverage"],
        "verdict_band": data.get("verdict_band_label"),
        "warnings": warnings,
        "report": "MasterG/report.html",
        "agent_entry": "MasterG/MasterG.md",
    }
    print(json.dumps(result, indent=2))
    return 0


def cmd_compare(project: Path, from_v: int, to_v: int) -> int:
    a_path = version_dir(project, from_v) / "data.json"
    b_path = version_dir(project, to_v) / "data.json"
    if not a_path.is_file() or not b_path.is_file():
        print("ERROR: both versions must have data.json", file=sys.stderr)
        return 1
    a = load_json(a_path)
    b = load_json(b_path)
    a_scores = {s["id"]: s.get("score") for s in a.get("scores") or []}
    rows = []
    for s in b.get("scores") or []:
        prev = a_scores.get(s["id"])
        cur = s.get("score")
        delta = None if prev is None or cur is None else cur - prev
        rows.append({"id": s["id"], "from": prev, "to": cur, "delta": delta})

    a_keys = {f["key"] for f in a.get("findings") or []}
    b_findings = {f["key"]: f for f in b.get("findings") or []}
    resolved = [
        k for k, f in b_findings.items()
        if f.get("status") == "resolved" or (k in a_keys and k not in {x["key"] for x in b.get("findings") or [] if x.get("status") != "resolved"})
    ]
    # simpler:
    resolved = [f["key"] for f in b.get("findings") or [] if f.get("status") == "resolved"]
    new = [f["key"] for f in b.get("findings") or [] if f.get("status") == "new"]
    persisting = [f["key"] for f in b.get("findings") or [] if f.get("status") == "persisting"]

    out = {
        "from": from_v,
        "to": to_v,
        "overall": {"from": a.get("overall"), "to": b.get("overall"), "delta": None},
        "categories": rows,
        "findings": {"resolved": resolved, "new": new, "persisting": persisting},
        "metric_deltas": b.get("metric_deltas") or [],
    }
    if a.get("overall") is not None and b.get("overall") is not None:
        out["overall"]["delta"] = round(b["overall"] - a["overall"], 1)
    print(json.dumps(out, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="masterg.py", description="MasterG report pipeline")
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Project root (default: .)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("status", parents=[parent], help="Print next version and previous findings")

    fin = sub.add_parser("finalize", parents=[parent], help="Validate draft and write reports")
    fin.add_argument("--version", type=int, default=None, help="Version number to finalize")

    cmp_ = sub.add_parser("compare", parents=[parent], help="Compare two versions")
    cmp_.add_argument("--from", dest="from_v", type=int, required=True)
    cmp_.add_argument("--to", dest="to_v", type=int, required=True)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if args.command == "status":
        return cmd_status(project)
    if args.command == "finalize":
        return cmd_finalize(project, args.version)
    if args.command == "compare":
        return cmd_compare(project, args.from_v, args.to_v)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
