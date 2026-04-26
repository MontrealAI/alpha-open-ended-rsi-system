from __future__ import annotations

from pathlib import Path

from .utils import sha_file, sha_payload, write_json


def run(cfg: dict, out: Path, jobs: list[dict], assignments: list[dict], claim_boundary: str) -> list[dict]:
    receipts = []
    for job in jobs:
        selection = next(a for a in assignments if a["job_id"] == job["job_id"])
        spec = {**job, "claim_boundary": claim_boundary}
        completion = {
            "job_id": job["job_id"],
            "selected_agent": selection["selected_agent"],
            "status": "completed",
            "proof_docket": [
                f"jobs/{job['job_id']}_spec.json",
                f"jobs/{job['job_id']}_completion.json",
                f"jobs/{job['job_id']}_event_log.json",
                f"jobs/{job['job_id']}_receipt.json",
            ],
            "claim_boundary": claim_boundary,
        }
        log = {
            "job_id": job["job_id"],
            "events": ["created", "assigned", "completed", "pending_validation"],
            "claim_boundary": claim_boundary,
        }

        spec_path = out / "jobs" / f"{job['job_id']}_spec.json"
        completion_path = out / "jobs" / f"{job['job_id']}_completion.json"
        event_log_path = out / "jobs" / f"{job['job_id']}_event_log.json"
        receipt_path = out / "jobs" / f"{job['job_id']}_receipt.json"

        write_json(spec_path, spec)
        write_json(completion_path, completion)
        write_json(event_log_path, log)

        expected_hashes = {
            str(spec_path.relative_to(out)): sha_file(spec_path),
            str(completion_path.relative_to(out)): sha_file(completion_path),
            str(event_log_path.relative_to(out)): sha_file(event_log_path),
        }

        receipt = {
            "job_id": job["job_id"],
            "receipt_id": f"{job['job_id']}_receipt",
            "status": "pending_validation",
            "settlement_unit": cfg["bounty_unit"],
            "bounty_units": job["bounty_placeholder"]["units"],
            "expected_artifact_hashes": expected_hashes,
            "claim_boundary": claim_boundary,
        }
        receipt_integrity_payload = {
            "job_id": receipt["job_id"],
            "receipt_id": receipt["receipt_id"],
            "status": receipt["status"],
            "settlement_unit": receipt["settlement_unit"],
            "bounty_units": receipt["bounty_units"],
            "expected_artifact_hashes": receipt["expected_artifact_hashes"],
            "claim_boundary": receipt["claim_boundary"],
        }
        receipt["receipt_integrity_hash"] = sha_payload(receipt_integrity_payload)

        write_json(receipt_path, receipt)

        # trusted in-memory anchor for detecting any on-disk receipt file tampering later.
        receipt["expected_receipt_file_hash"] = sha_file(receipt_path)
        receipts.append(receipt)

    write_json(
        out / "agi_job_receipt.json",
        {
            "runtime_id": cfg["runtime_id"],
            "job_receipts": receipts,
            "claim_boundary": claim_boundary,
            "status": "local deterministic receipts",
        },
    )

    return receipts
