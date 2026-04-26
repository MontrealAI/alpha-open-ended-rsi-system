from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(cfg: dict, out: Path, receipts: list[dict], validation: dict, claim_boundary: str) -> dict:
    approved = {a["job_id"] for a in validation["attestations"] if a["decision"] == "approved"}
    validated = [r for r in receipts if r["job_id"] in approved]
    rejected = [r for r in receipts if r["job_id"] not in approved]

    ledger = {
        "epoch": "reservoir_epoch_001",
        "unit": cfg["bounty_unit"],
        "validated_work_units": [{"job_id": r["job_id"], "units": r["bounty_units"]} for r in validated],
        "rejected_work_units": [{"job_id": r["job_id"], "units": r["bounty_units"]} for r in rejected],
        "archive_contribution": {"units": len(validated) * 10, "basis": "validated receipts"},
        "simulated_fee_burn": {"fee_units": 3, "burn_units": 1},
        "reinvestment_recommendation": "allocate to invariant_library_seed mutation",
        "status": "local accounting, not real token economy",
        "claim_boundary": claim_boundary,
    }
    epoch = {
        "epoch": "reservoir_epoch_001",
        "summary": f"{len(validated)} validated, {len(rejected)} rejected/quarantined work units.",
        "claim_boundary": claim_boundary,
    }
    write_json(out / "reservoir_ledger.json", ledger)
    write_json(out / "reservoir_epoch_report.json", epoch)
    return ledger
