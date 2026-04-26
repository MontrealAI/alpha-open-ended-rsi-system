from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(cfg: dict, out: Path, jobs: list[dict], agent_data: dict, claim_boundary: str) -> dict:
    assignments = []
    rounds = []
    for job in jobs:
        job_bids = [b for b in agent_data["bids"] if b["job_id"] == job["job_id"]]
        selected = max(job_bids, key=lambda b: b["bid_score"])
        assignments.append({"job_id": job["job_id"], "selected_agent": selected["agent_id"]})
        rounds.append(
            {
                "job_id": job["job_id"],
                "candidate_agents": [b["agent_id"] for b in job_bids],
                "bids_scores": job_bids,
                "selected_agent": selected["agent_id"],
                "validator_requirements": ["artifact hash check", "claim boundary check"],
                "escrow_placeholder": {"unit": cfg["bounty_unit"], "status": "locked-simulated"},
                "settlement_conditions": ["validator approved", "council ruling"],
            }
        )

    round_payload = {
        "runtime_id": cfg["runtime_id"],
        "round_id": "marketplace-round-001",
        "jobs_posted": [j["job_id"] for j in jobs],
        "rounds": rounds,
        "status": "local/devnet simulation unless contracts/events are fully implemented",
        "claim_boundary": claim_boundary,
    }
    write_json(out / "marketplace_round.json", round_payload)
    write_json(out / "marketplace_assignment_log.json", {"assignments": assignments, "claim_boundary": claim_boundary})
    return {"assignments": assignments}
