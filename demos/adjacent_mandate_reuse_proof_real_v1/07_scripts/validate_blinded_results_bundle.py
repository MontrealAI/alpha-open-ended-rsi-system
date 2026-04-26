#!/usr/bin/env python3
"""Validate minimum completeness for blinded adjacent-transfer result bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PUBLIC_PATHS = [
    "README.md",
    "summary_metrics.json",
    "stage_a_scorecard.md",
    "stage_b_scorecard.md",
    "lane_blue_packet_public",
    "lane_blue_packet_public/stage_a",
    "lane_blue_packet_public/stage_b",
    "lane_gold_packet_public",
    "lane_gold_packet_public/stage_a",
    "lane_gold_packet_public/stage_b",
    "scorecard_outputs",
    "proof_docket_public.md",
    "governance_ruling_public.md",
    "provenance_manifest.json",
    "HUMAN_ACTION_REQUIRED.md",
    "prereg_experiment_manifest.json",
    "environment_lock.json",
    "run_register.csv",
    "intervention_log.csv",
    "leakage_check.csv",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        default=str(PACK_ROOT / "results_blinded_adjacent_transfer_v1"),
    )
    args = parser.parse_args()
    results_dir = Path(args.results_dir)

    if not results_dir.exists():
        raise SystemExit(f"Missing results directory: {results_dir}")

    missing: list[str] = []
    for rel in REQUIRED_PUBLIC_PATHS:
        if not (results_dir / rel).exists():
            missing.append(rel)

    summary_file = results_dir / "summary_metrics.json"
    if summary_file.exists():
        data = json.loads(summary_file.read_text(encoding="utf-8"))
        required_keys = [
            "status",
            "stage_a",
            "stage_b",
            "demonstrated",
            "pending_human_execution",
            "unproven",
        ]
        for k in required_keys:
            if k not in data:
                missing.append(f"summary_metrics.json missing key: {k}")

    if missing:
        raise SystemExit("Results bundle is incomplete:\n- " + "\n- ".join(missing))

    print("Bundle validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
