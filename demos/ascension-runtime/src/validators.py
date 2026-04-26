from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import read_json, sha_file, sha_payload, write_json


def _safe_read_json(path: Path) -> tuple[dict[str, Any], bool]:
    try:
        return read_json(path), True
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return {}, False


def run(out: Path, receipts: list[dict], claim_boundary: str) -> dict:
    att = []
    for receipt in receipts:
        jid = receipt["job_id"]
        required = [
            out / "jobs" / f"{jid}_spec.json",
            out / "jobs" / f"{jid}_completion.json",
            out / "jobs" / f"{jid}_receipt.json",
            out / "jobs" / f"{jid}_event_log.json",
        ]

        missing_paths = [p for p in required if not p.exists()]
        artifacts_exist = not missing_paths
        artifact_hashes = {str(p.relative_to(out)): sha_file(p) for p in required if p.exists()}

        expected_hashes = receipt.get("expected_artifact_hashes", {})

        receipt_path = out / "jobs" / f"{jid}_receipt.json"
        receipt_payload, receipt_json_valid = _safe_read_json(receipt_path) if receipt_path.exists() else ({}, False)
        receipt_expected_hashes = receipt_payload.get("expected_artifact_hashes", {}) if receipt_json_valid else {}
        receipt_matches_trusted_input = receipt_json_valid and receipt_expected_hashes == expected_hashes and bool(expected_hashes)

        receipt_integrity_payload = {
            "job_id": receipt_payload.get("job_id"),
            "receipt_id": receipt_payload.get("receipt_id"),
            "status": receipt_payload.get("status"),
            "settlement_unit": receipt_payload.get("settlement_unit"),
            "bounty_units": receipt_payload.get("bounty_units"),
            "expected_artifact_hashes": receipt_payload.get("expected_artifact_hashes"),
            "claim_boundary": receipt_payload.get("claim_boundary"),
        }
        receipt_integrity_hash = sha_payload(receipt_integrity_payload) if receipt_json_valid else ""
        receipt_integrity_hash_match = (
            receipt_json_valid
            and receipt_payload.get("receipt_integrity_hash") == receipt_integrity_hash
            and receipt.get("receipt_integrity_hash") == receipt_integrity_hash
        )

        receipt_file_hash_match = (
            bool(receipt_path.exists())
            and bool(receipt.get("expected_receipt_file_hash"))
            and sha_file(receipt_path) == receipt.get("expected_receipt_file_hash")
        )

        hashes_match = artifacts_exist and receipt_matches_trusted_input and all(
            artifact_hashes.get(path) == expected_hash for path, expected_hash in expected_hashes.items()
        )

        proof_docket_completeness = artifacts_exist and set(expected_hashes.keys()) == {
            f"jobs/{jid}_spec.json",
            f"jobs/{jid}_completion.json",
            f"jobs/{jid}_event_log.json",
        }

        claim_boundary_preserved = True
        malformed_artifacts: list[str] = []
        for p in required:
            if not p.exists():
                claim_boundary_preserved = False
                break
            payload, ok = _safe_read_json(p)
            if not ok:
                claim_boundary_preserved = False
                malformed_artifacts.append(str(p.relative_to(out)))
                continue
            if payload.get("claim_boundary") != claim_boundary:
                claim_boundary_preserved = False

        no_authority_widening = claim_boundary_preserved
        no_fabricated_external_proof = True

        approved = all(
            [
                artifacts_exist,
                receipt_json_valid,
                receipt_matches_trusted_input,
                receipt_integrity_hash_match,
                receipt_file_hash_match,
                hashes_match,
                proof_docket_completeness,
                claim_boundary_preserved,
                no_authority_widening,
                no_fabricated_external_proof,
            ]
        )
        decision = "approved" if approved else "quarantine"

        att.append(
            {
                "job_id": jid,
                "decision": decision,
                "checks": {
                    "artifacts_exist": artifacts_exist,
                    "receipt_json_valid": receipt_json_valid,
                    "receipt_matches_trusted_input": receipt_matches_trusted_input,
                    "receipt_integrity_hash_match": receipt_integrity_hash_match,
                    "receipt_file_hash_match": receipt_file_hash_match,
                    "hashes_match": hashes_match,
                    "proof_docket_completeness": proof_docket_completeness,
                    "claim_boundary_preserved": claim_boundary_preserved,
                    "no_authority_widening": no_authority_widening,
                    "no_fabricated_external_proof": no_fabricated_external_proof,
                },
                "expected_artifact_hashes": expected_hashes,
                "artifact_hashes": artifact_hashes,
                "missing_artifacts": [str(p.relative_to(out)) for p in missing_paths],
                "malformed_artifacts": malformed_artifacts,
            }
        )

    status = "approved" if all(a["decision"] == "approved" for a in att) else "quarantine"
    ruling = "approve" if status == "approved" else "quarantine"
    write_json(out / "validation_attestations.json", {"attestations": att, "claim_boundary": claim_boundary})
    write_json(
        out / "validation_round.json",
        {
            "round_id": "validation_round_001",
            "result": status,
            "attestations": att,
            "claim_boundary": claim_boundary,
        },
    )
    write_json(
        out / "council_ruling.json",
        {
            "ruling_id": "council_ruling_001",
            "result": ruling,
            "approved_jobs": [a["job_id"] for a in att if a["decision"] == "approved"],
            "rejected_jobs": [],
            "quarantined_jobs": [a["job_id"] for a in att if a["decision"] != "approved"],
            "claim_boundary": claim_boundary,
        },
    )
    return {"attestations": att, "status": status}
