from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(out: Path, selected_bundle: list[str], receipts: list[dict], mark_ranked: list[dict], claim_boundary: str) -> dict:
    lineage = {
        "seed_lineage": selected_bundle,
        "package_lineage": ["capability_pkg_protocol_a", "capability_pkg_invariant_b"],
        "job_receipt_lineage": [r["receipt_id"] for r in receipts],
        "score_history": [{"seed_id": row["seed_id"], "score": row["score"]} for row in mark_ranked],
        "reusable_assets": ["job specs", "validation attestations", "scorecard"],
        "promotion_rejection_history": [
            {"seed_id": selected_bundle[0], "state": "promoted"},
            {"seed_id": mark_ranked[-1]["seed_id"], "state": "pending"},
        ],
        "next_recommended_mutations": ["increase fuzz corpus diversity", "tighten governance simulation envelope"],
        "status": "implemented as local lineage artifacts",
        "claim_boundary": claim_boundary,
    }
    write_json(out / "archive_lineage.json", lineage)
    write_json(
        out / "capability_package_manifest.json",
        {
            "packages": [
                {"id": "capability_pkg_protocol_a", "source": selected_bundle[0]},
                {"id": "capability_pkg_invariant_b", "source": selected_bundle[1]},
            ],
            "claim_boundary": claim_boundary,
        },
    )
    return lineage


def write_archive_index(out: Path, claim_boundary: str) -> None:
    artifacts = sorted(set(str(p.relative_to(out)) for p in out.rglob("*.json")) | {"archive_index.json"})
    write_json(
        out / "archive_index.json",
        {
            "json_artifacts": artifacts,
            "claim_boundary": claim_boundary,
        },
    )
