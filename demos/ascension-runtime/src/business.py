from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(cfg: dict, out: Path, sovereign_manifest: dict, claim_boundary: str) -> dict:
    jobs = [
        {
            "job_id": "job_001",
            "goal": "Produce deterministic protocol audit-factory receipt with full proof docket.",
            "success_metric": "validator-approved receipt with complete artifact hashes",
            "bounty_placeholder": {"units": 60, "unit": cfg["bounty_unit"]},
            "input_artifacts": ["insight_packet.json", "mark_selection_report.json", "sovereign_manifest.json"],
            "output_artifacts": ["jobs/job_001_completion.json", "jobs/job_001_receipt.json"],
            "proof_requirements": ["artifact existence", "hash matches", "claim boundary preserved"],
            "validation_criteria": ["proof docket completeness", "authority scope preserved"],
            "settlement_condition": "validator and council approval",
            "authority_scope": "bounded-local-runtime",
        },
        {
            "job_id": "job_002",
            "goal": "Generate invariant-library delta with replay-ready validation package.",
            "success_metric": "two independent agent submissions; best validated",
            "bounty_placeholder": {"units": 45, "unit": cfg["bounty_unit"]},
            "input_artifacts": ["nova_seeds/invariant_library_seed.json", "sovereign_manifest.json"],
            "output_artifacts": ["jobs/job_002_completion.json", "jobs/job_002_receipt.json"],
            "proof_requirements": ["deterministic outputs", "schema-compatible receipt"],
            "validation_criteria": ["no fabricated external evidence", "governance gate pass"],
            "settlement_condition": "approved or quarantined by council",
            "authority_scope": "bounded-local-runtime",
        },
    ]

    operating_plan = {
        "runtime_id": cfg["runtime_id"],
        "business_id": "business-protocol-correctness-001",
        "sovereign_id": sovereign_manifest["sovereign_id"],
        "mandate_selection": ["protocol-correctness", "invariant-expansion"],
        "job_definitions": [j["job_id"] for j in jobs],
        "agent_assignment_plan": "competitive bidding with deterministic scoring",
        "validation_plan": "artifact-hash + claim-boundary + authority checks",
        "proof_docket_plan": "per-job machine-readable receipts and attestations",
        "settlement_receipt_plan": "placeholder units after approval only",
        "claim_boundary": claim_boundary,
    }
    decomp = {"runtime_id": cfg["runtime_id"], "jobs": jobs, "claim_boundary": claim_boundary}
    write_json(out / "business_operating_plan.json", operating_plan)
    write_json(out / "mandate_decomposition.json", decomp)
    return decomp
