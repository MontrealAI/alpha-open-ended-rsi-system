#!/usr/bin/env python3
"""Calculate Stage A scorecard outcomes for adjacent-mandate blinded runs.

Defaults remain backward-compatible with the proof-pack `04_scorecard/` templates,
but this script now also supports execution bundles that populate
`results_blinded_adjacent_transfer_v1/scorecard_outputs/`.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCORECARD_DIR = PACK_ROOT / "04_scorecard"



def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))



def to_float(v: str | float | int) -> float:
    try:
        return float(v)
    except Exception:
        return 0.0



def to_int(v: str | float | int) -> int:
    try:
        return int(float(v))
    except Exception:
        return 0



def resolve_scorecard_file(scorecard_dir: Path, basename: str) -> Path:
    preferred = scorecard_dir / f"{basename}.csv"
    template = scorecard_dir / f"{basename}.template.csv"
    if preferred.exists():
        return preferred
    if template.exists():
        return template
    raise FileNotFoundError(f"Missing required scorecard file: {preferred} (or {template})")



def rel_improve(base: float, new: float, higher_is_better: bool = True) -> float:
    if base == 0:
        return 0.0
    if higher_is_better:
        return (new - base) / base
    return (base - new) / base



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scorecard-dir",
        default=str(DEFAULT_SCORECARD_DIR),
        help="Directory containing run_costs/output_scoring/package_dependence_ledger CSVs",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Output directory for summary files (default: <scorecard-dir>/out)",
    )
    args = parser.parse_args()

    scorecard_dir = Path(args.scorecard_dir)
    run_costs_path = resolve_scorecard_file(scorecard_dir, "run_costs")
    outputs_path = resolve_scorecard_file(scorecard_dir, "output_scoring")

    outdir = Path(args.output_dir) if args.output_dir else scorecard_dir / "out"
    outdir.mkdir(parents=True, exist_ok=True)

    cost_rows = read_csv(run_costs_path)
    output_rows = read_csv(outputs_path)

    lanes: dict[str, dict[str, float | int | bool]] = {"control": {}, "treatment": {}}

    for row in cost_rows:
        lane = row.get("lane", "").strip().lower()
        if lane in lanes:
            lanes[lane]["cost_units"] = to_float(row.get("cost_units", 0))

    for lane in lanes:
        accepted = [
            r for r in output_rows if r.get("lane", "").strip().lower() == lane and to_int(r.get("accepted", 0)) == 1
        ]
        lanes[lane]["accepted_count"] = len(accepted)
        lanes[lane]["usefulness_points"] = sum(to_float(r.get("usefulness_points", 0)) for r in accepted)
        cost = to_float(lanes[lane].get("cost_units", 0))
        lanes[lane]["aoy"] = (to_float(lanes[lane]["usefulness_points"]) / cost) if cost > 0 else 0.0

        times = [to_float(r.get("time_to_accept_hours", 0)) for r in accepted if to_float(r.get("time_to_accept_hours", 0)) > 0]
        lanes[lane]["time_to_first_accepted_output"] = min(times) if times else 0.0

        reworks = [to_float(r.get("rework_rounds", 0)) for r in accepted]
        lanes[lane]["avg_rework"] = (sum(reworks) / len(reworks)) if reworks else 0.0

        fractions: list[float] = []
        for r in accepted:
            fields = [
                to_int(r.get("evidence_code_pointer", 0)),
                to_int(r.get("evidence_broken_condition", 0)),
                to_int(r.get("evidence_repro", 0)),
                to_int(r.get("evidence_severity_rationale", 0)),
                to_int(r.get("evidence_fix", 0)),
                to_int(r.get("evidence_replay_artifact", 0)),
            ]
            fractions.append(sum(fields) / 6.0)
        lanes[lane]["evidence_completeness"] = (sum(fractions) / len(fractions)) if fractions else 0.0

        lane_rows = [r for r in output_rows if r.get("lane", "").strip().lower() == lane]
        lanes[lane]["safety_incidents"] = sum(to_int(r.get("safety_incident", 0)) for r in lane_rows)
        lanes[lane]["unsupported_claims"] = sum(to_int(r.get("unsupported_claim_count", 0)) for r in lane_rows)
        lanes[lane]["hallucinated_references"] = sum(to_int(r.get("hallucinated_reference_count", 0)) for r in lane_rows)

        dep_num = sum(to_int(r.get("package_dependency", 0)) for r in accepted)
        dep_den = len(accepted)
        lanes[lane]["package_dependence"] = (dep_num / dep_den) if dep_den else 0.0

    control = lanes["control"]
    treatment = lanes["treatment"]

    comparisons = {
        "aoy_uplift": rel_improve(to_float(control["aoy"]), to_float(treatment["aoy"]), True),
        "speed_uplift": rel_improve(
            to_float(control["time_to_first_accepted_output"]),
            to_float(treatment["time_to_first_accepted_output"]),
            False,
        ),
        "rework_reduction": rel_improve(to_float(control["avg_rework"]), to_float(treatment["avg_rework"]), False),
        "evidence_completeness_uplift": rel_improve(
            to_float(control["evidence_completeness"]),
            to_float(treatment["evidence_completeness"]),
            True,
        ),
        "package_dependence": to_float(treatment["package_dependence"]),
        "safety_regression": not (
            to_int(treatment["safety_incidents"]) > to_int(control["safety_incidents"])
            or to_int(treatment["unsupported_claims"]) > to_int(control["unsupported_claims"])
            or to_int(treatment["hallucinated_references"]) > to_int(control["hallucinated_references"])
        ),
    }

    thresholds = {
        "aoy_uplift": 0.35,
        "speed_uplift": 0.30,
        "rework_reduction": 0.40,
        "evidence_completeness_uplift": 0.20,
        "package_dependence": 0.30,
        "safety_regression": True,
    }

    pass_flags = {
        "aoy_uplift": comparisons["aoy_uplift"] >= thresholds["aoy_uplift"],
        "speed_uplift": comparisons["speed_uplift"] >= thresholds["speed_uplift"],
        "rework_reduction": comparisons["rework_reduction"] >= thresholds["rework_reduction"],
        "evidence_completeness_uplift": comparisons["evidence_completeness_uplift"]
        >= thresholds["evidence_completeness_uplift"],
        "package_dependence": comparisons["package_dependence"] >= thresholds["package_dependence"],
        "safety_regression": comparisons["safety_regression"] is True,
    }

    results = {
        "scorecard_dir": str(scorecard_dir),
        "run_costs_source": str(run_costs_path),
        "output_scoring_source": str(outputs_path),
        "control": control,
        "treatment": treatment,
        "comparisons": comparisons,
        "pass_flags": pass_flags,
        "adjacent_mandate_pass": all(pass_flags.values()),
    }

    (outdir / "summary.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")

    md = ["# Q2 scorecard summary", "", f"- scorecard_dir: `{scorecard_dir}`", f"- run_costs_source: `{run_costs_path}`", f"- output_scoring_source: `{outputs_path}`", "", "## Control"]
    for k, v in control.items():
        md.append(f"- **{k}**: {v}")

    md.append("")
    md.append("## Treatment")
    for k, v in treatment.items():
        md.append(f"- **{k}**: {v}")

    md.append("")
    md.append("## Comparisons")
    for k, v in comparisons.items():
        md.append(f"- **{k}**: {v}")

    md.append("")
    md.append("## Pass flags")
    for k, v in pass_flags.items():
        md.append(f"- **{k}**: {'PASS' if v else 'FAIL'}")

    md.append("")
    md.append("## Overall adjacent-mandate result")
    md.append(f"**{'PASS' if results['adjacent_mandate_pass'] else 'FAIL'}**")

    (outdir / "summary.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print("Wrote:")
    print(outdir / "summary.json")
    print(outdir / "summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
