#!/usr/bin/env python3
"""Validate deterministic artifact contract for demos/open-ended-rsi-system outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demos" / "open-ended-rsi-system"
OUT = DEMO / "out"

REQUIRED = [
    "capability_genome.json",
    "manifest.json",
    "generation_0.json",
    "generation_1.json",
    "generation_2.json",
    "mandate3_execution.json",
    "assay_bundle.json",
    "lineage.json",
    "frontier_queue.json",
    "intervention_log.json",
    "scorecard.json",
    "board_scorecard.json",
    "board_scorecard.md",
    "governance_ruling.json",
    "chronicle_entry.json",
    "claim_boundary.json",
    "determinism_fingerprint.json",
    "safety_gates.json",
    "summary.md",
    "proof_docket.md",
    "provenance_manifest.json",
    "board_report.html",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_mismatches(left: Any, right: Any, path: str) -> list[str]:
    mismatches: list[str] = []
    if isinstance(left, dict) and isinstance(right, dict):
        keys = sorted(set(left) | set(right))
        for key in keys:
            child_path = f"{path}.{key}" if path else str(key)
            if key not in left:
                mismatches.append(f"{child_path} missing from board artifact")
                continue
            if key not in right:
                mismatches.append(f"{child_path} missing from scorecard artifact")
                continue
            mismatches.extend(_collect_mismatches(left[key], right[key], child_path))
        return mismatches
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            mismatches.append(f"{path} list length mismatch board={len(left)} score={len(right)}")
            return mismatches
        for idx, (lval, rval) in enumerate(zip(left, right)):
            mismatches.extend(_collect_mismatches(lval, rval, f"{path}[{idx}]"))
        return mismatches
    if left != right:
        mismatches.append(f"{path} mismatch board={left!r} score={right!r}")
    return mismatches


def main() -> int:
    missing = [name for name in REQUIRED if not (OUT / name).exists()]
    if missing:
        print("FAIL: missing required out artifacts:")
        for item in missing:
            print(f"  - {item}")
        return 1

    g0 = load_json(OUT / "generation_0.json")
    g1 = load_json(OUT / "generation_1.json")
    g2 = load_json(OUT / "generation_2.json")
    execution = load_json(OUT / "mandate3_execution.json")
    score = load_json(OUT / "scorecard.json")
    board_score_path = OUT / "board_scorecard.json"
    gates = load_json(OUT / "safety_gates.json")
    provenance = load_json(OUT / "provenance_manifest.json")

    if not (g2["human_intervention_touches"] < g1["human_intervention_touches"] < g0["human_intervention_touches"]):
        print("FAIL: human intervention touches are not strictly descending g0 > g1 > g2")
        return 1

    observed = score["observed"]
    thresholds = score["thresholds"]
    checks = {
        "aoy_uplift": observed["aoy_uplift"] >= thresholds["aoy_uplift_min"],
        "speed_uplift": observed["speed_uplift"] >= thresholds["speed_uplift_min"],
        "rework_reduction": observed["rework_reduction"] >= thresholds["rework_reduction_min"],
        "evidence_completeness_uplift": observed["evidence_completeness_uplift"] >= thresholds["evidence_uplift_min"],
        "package_dependence": observed["package_dependence"] >= thresholds["package_dependence_min"],
        "no_safety_regression": observed["no_safety_regression"] is True,
    }
    failing = [k for k, ok in checks.items() if not ok]
    if failing:
        print(f"FAIL: threshold checks failed: {', '.join(failing)}")
        return 1

    board_score = load_json(board_score_path)
    required_board_fields = [
        "release_target",
        "generation_summary",
        "thresholds",
        "observed",
        "longitudinal",
        "claim_boundary",
    ]
    missing_board_fields = [key for key in required_board_fields if key not in board_score]
    if missing_board_fields:
        print(
            "FAIL: board_scorecard is missing required contract fields: "
            + ", ".join(missing_board_fields)
        )
        return 1

    mismatches = _collect_mismatches(
        {key: board_score[key] for key in required_board_fields},
        {key: score[key] for key in required_board_fields},
        path="",
    )
    if mismatches:
        mismatch_preview = "; ".join(mismatches[:6])
        extra = "" if len(mismatches) <= 6 else f" (+{len(mismatches) - 6} more)"
        print(f"FAIL: board_scorecard contract drift detected: {mismatch_preview}{extra}")
        return 1

    bad_gates = [k for k, v in gates.items() if v.get("status") != "pass"]
    if bad_gates:
        print(f"FAIL: doctrine safety gates not all pass: {', '.join(bad_gates)}")
        return 1

    ranked = g2.get("frontier_queue", [])
    if not ranked:
        print("FAIL: generation_2 frontier queue is empty")
        return 1
    if g2["selected_domain"]["domain"] != ranked[0]["domain"]:
        print("FAIL: selected domain does not match top-ranked frontier domain")
        return 1

    if execution.get("domain") != g2["selected_domain"]["domain"]:
        print("FAIL: mandate3_execution domain does not match generation_2 selected domain")
        return 1
    if execution.get("offline_only") is not True:
        print("FAIL: mandate3_execution offline_only must be true")
        return 1
    if execution.get("simulated") is not True:
        print("FAIL: mandate3_execution simulated flag must be true")
        return 1
    if len(execution.get("steps", [])) < 3:
        print("FAIL: mandate3_execution must include at least 3 execution steps")
        return 1

    guards = provenance.get("determinism_guards", {})
    if guards.get("network_calls") != "disabled" or guards.get("external_apis") != "disabled":
        print("FAIL: provenance determinism guards must disable network and external APIs")
        return 1

    print("PASS: open-ended-rsi artifact contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
