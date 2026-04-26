from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(out: Path, claim_boundary: str) -> dict:
    recommendation = {
        "recommendation_id": "architect_reco_001",
        "inputs": [
            "archive_lineage.json",
            "reservoir_ledger.json",
            "validation_round.json",
            "jobs/job_001_receipt.json",
            "mark_selection_report.json",
        ],
        "next_loop_recommendations": [
            "run blinded adjacent transfer",
            "advance Stage B only if Stage A passes",
            "improve MARK only after evidence surfaces mature",
            "do not widen claims prematurely",
        ],
        "status": "deterministic local recommender",
        "claim_boundary": claim_boundary,
    }
    next_plan = {
        "loop_id": "next_loop_001",
        "stage_a": "execute blinded adjacent transfer",
        "stage_b": "conditional only on stage_a_pass",
        "mark_upgrade_gate": "evidence maturity threshold",
        "claim_boundary": claim_boundary,
    }
    write_json(out / "architect_recommendation.json", recommendation)
    write_json(out / "next_loop_plan.json", next_plan)
    return recommendation
