from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(cfg: dict, out: Path, selection: dict, claim_boundary: str) -> dict:
    manifest = {
        "runtime_id": cfg["runtime_id"],
        "sovereign_id": "alpha-agi-protocol-cybersecurity-sovereign",
        "scope": "bounded local/devnet operating lineage formed from selected seed bundle",
        "authority_boundary": [
            "local deterministic artifacts only",
            "no autonomous authority widening",
            "no mainnet settlement authority",
        ],
        "mandate_families": ["protocol-correctness", "verification-infrastructure"],
        "allowed_jobs": ["audit package", "invariant expansion", "fuzz replay"],
        "prohibited_claims": [
            "audited final deployment",
            "mainnet production readiness",
            "completed live Ascension",
        ],
        "governance_gates": ["validator approval", "council ruling", "claim boundary check"],
        "archive_policy": "hash-linked lineage required for promotion",
        "proof_requirements": ["artifact completeness", "hash integrity", "docket completeness"],
        "settlement_ruling_policy": "placeholder-unit settlement only after validation",
        "selected_seed_bundle": selection["selected_bundle"],
        "status": "local/devnet/synthetic sovereign candidate",
        "claim_boundary": claim_boundary,
    }
    state = {
        "runtime_id": cfg["runtime_id"],
        "sovereign_id": manifest["sovereign_id"],
        "state": "formed",
        "selected_seed_bundle": selection["selected_bundle"],
        "claim_boundary": claim_boundary,
    }
    write_json(out / "sovereign_manifest.json", manifest)
    write_json(out / "sovereign_state_snapshot.json", state)
    return manifest
