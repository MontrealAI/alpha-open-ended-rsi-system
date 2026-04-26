from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(out: Path, claim_boundary: str) -> dict:
    profile = {
        "worker_node_profile": {"runtime": "python3", "role": "job execution"},
        "validator_node_profile": {"runtime": "python3", "role": "artifact and claim checks"},
        "sentinel_profile": {"runtime": "python3", "role": "claim-boundary monitoring"},
        "local_runtime_constraints": ["no external API calls", "deterministic config", "local filesystem only"],
        "authority_boundary": "local/devnet profile, not live node network",
        "claim_boundary": claim_boundary,
    }
    write_json(out / "node_runtime_profile.json", profile)
    return profile
