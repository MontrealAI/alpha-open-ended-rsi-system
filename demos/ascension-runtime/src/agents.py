from __future__ import annotations

from pathlib import Path

from .utils import write_json


def profiles(claim_boundary: str) -> list[dict]:
    return [
        {"agent_id": "fast_low_cost", "cost_bias": 0.9, "evidence_bias": 0.6, "claim_boundary": claim_boundary},
        {"agent_id": "evidence_heavy", "cost_bias": 0.6, "evidence_bias": 0.95, "claim_boundary": claim_boundary},
        {"agent_id": "balanced", "cost_bias": 0.75, "evidence_bias": 0.8, "claim_boundary": claim_boundary},
    ]


def run(out: Path, jobs: list[dict], claim_boundary: str) -> dict:
    agent_profiles = profiles(claim_boundary)
    write_json(out / "agents" / "agent_profiles.json", {"agents": agent_profiles, "claim_boundary": claim_boundary})

    bids = []
    exec_log = []
    for job in jobs:
        for idx, agent in enumerate(agent_profiles):
            bid_score = round(agent["evidence_bias"] * 0.7 + (1 - agent["cost_bias"]) * 0.3 + (0.01 * idx), 4)
            bids.append({"job_id": job["job_id"], "agent_id": agent["agent_id"], "bid_score": bid_score})
        winner = max([b for b in bids if b["job_id"] == job["job_id"]], key=lambda b: b["bid_score"])
        exec_log.append(
            {
                "job_id": job["job_id"],
                "selected_agent": winner["agent_id"],
                "execution_status": "completed",
                "output_summary": f"{winner['agent_id']} produced deterministic local artifacts.",
            }
        )

    reputation = {
        "agents": [
            {
                "agent_id": p["agent_id"],
                "reputation": round(70 + p["evidence_bias"] * 20 - p["cost_bias"] * 5, 2),
            }
            for p in agent_profiles
        ],
        "claim_boundary": claim_boundary,
    }
    write_json(out / "agent_execution_log.json", {"executions": exec_log, "bids": bids, "claim_boundary": claim_boundary})
    write_json(out / "agent_reputation_snapshot.json", reputation)
    return {"bids": bids, "executions": exec_log, "profiles": agent_profiles}
