from __future__ import annotations
from pathlib import Path
from .utils import load_json, write_json

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
THRESHOLDS = load_json(CONFIG_DIR / "adjacent_mandate_thresholds.json")


def _uplift(control: float, treatment: float, higher_is_better: bool = True) -> float:
    if control == 0:
        return 0.0
    return (treatment - control) / control if higher_is_better else (control - treatment) / control


def build_scorecard(control_metrics: dict, treatment_metrics: dict, out_dir):
    comparison = {
        "aoy_uplift": round(_uplift(control_metrics["aoy"], treatment_metrics["aoy"], True), 3),
        "speed_uplift": round(_uplift(control_metrics["time_to_first_accepted_output"], treatment_metrics["time_to_first_accepted_output"], False), 3),
        "repair_rework_reduction": round(_uplift(control_metrics["repair_rework"], treatment_metrics["repair_rework"], False), 3),
        "evidence_completeness_uplift": round(_uplift(control_metrics["evidence_completeness"], treatment_metrics["evidence_completeness"], True), 3),
        "safety_regression": bool(
            treatment_metrics["unsupported_claim_rate"] > control_metrics["unsupported_claim_rate"]
            or treatment_metrics["severity_inflation_count"] > control_metrics["severity_inflation_count"]
        ),
        "package_dependence_rate": treatment_metrics["package_dependence_rate"],
    }

    passes = {
        "aoy_uplift": comparison["aoy_uplift"] >= THRESHOLDS["aoy_uplift"],
        "speed_uplift": comparison["speed_uplift"] >= THRESHOLDS["speed_uplift"],
        "repair_rework_reduction": comparison["repair_rework_reduction"] >= THRESHOLDS["repair_rework_reduction"],
        "evidence_completeness_uplift": comparison["evidence_completeness_uplift"] >= THRESHOLDS["evidence_completeness_uplift"],
        "no_safety_regression": comparison["safety_regression"] is False,
        "package_dependence_rate": comparison["package_dependence_rate"] >= THRESHOLDS["package_dependence_rate"],
    }
    passes["adjacent_mandate_proof"] = all(passes.values())

    scorecard = {
        "thresholds": THRESHOLDS,
        "control": control_metrics,
        "treatment": treatment_metrics,
        "comparison": comparison,
        "passes": passes,
    }
    write_json(out_dir / "adjacent_mandate_scorecard.json", scorecard)
    return scorecard
