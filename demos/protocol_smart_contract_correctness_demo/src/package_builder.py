from __future__ import annotations

import hashlib
from pathlib import Path

from .utils import write_json


def _hash(data: dict) -> str:
    import json

    encoded = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def build_capability_packages(winner_result: dict, out_dir: Path):
    accepted = winner_result["accepted_findings"]
    ontology = sorted({f["issue_type"] for f in accepted})

    governance_pack = {
        "id": "GovernanceValidationPack-v1",
        "type": "frozen_sub_pack",
        "source_seed": winner_result["seed"],
        "ontology": ontology,
        "extraction_schema": {
            "fields": [
                "contract",
                "function",
                "issue_type",
                "severity",
                "code_pointer",
                "issue_statement",
                "broken_invariant_or_state_path",
                "reproduction_artifact",
                "severity_rationale",
                "suggested_fix",
                "traceability_to_scope",
            ]
        },
        "mechanism_library": {
            "proofless_settlement": "Value release requires explicit validated proof and authority checks.",
            "instant_upgrade": "Upgrade authority requires delay/timelock and visible governance intent.",
            "treasury_drift": "Accounting state must reconcile prior to value movement.",
            "no_challenge_window": "Post-approval settlement requires challenge window expiry.",
        },
        "workflow_template": [
            "enumerate value-moving functions",
            "map authority and proof checks",
            "test challenge-window semantics",
            "trace accounting consistency",
            "emit release-gate packet",
        ],
        "scoring_rubric": {
            "high_with_repro": 5,
            "medium_with_repro": 3,
            "low": 1,
            "harness_bonus": 2,
            "release_gate_bonus": 2,
        },
        "safety_routing_rules": {
            "reject_unsupported_claims": True,
            "block_severity_inflation": True,
            "escalate_if_false_positive_rate_above": 0.1,
        },
        "query_bundle": [
            "call{value:",
            "transfer(",
            "swapImplementation",
            "upgrade",
            "readyAt",
            "approvedAt",
            "challengePeriod",
            "locked",
        ],
        "skill_wrapper": {
            "name": "protocol_cybersecurity_invariant_lane",
            "mode": "deterministic",
            "notes": "Synthetic local wrapper for replayable mandate review",
        },
        "release_gate_packet": {
            "required": [
                "accepted findings with repro",
                "evidence completeness >= 0.9",
                "unsupported claim rate <= 0.1",
                "scope traceability",
            ]
        },
    }
    governance_pack["package_hash"] = _hash(governance_pack)

    protocol_pack = {
        "id": "ProtocolCybersecurityPack-v1",
        "legacy_aliases": ["ProtocolAssurancePack-v1"],
        "type": "sector_level_stepping_stone",
        "contains_sub_pack": governance_pack["id"],
        "scope": ["governance_dispute_correctness", "threshold_attestation_correctness"],
        "portable_components": {
            "ontology": governance_pack["ontology"],
            "invariant_library": governance_pack["mechanism_library"],
            "workflow_template": governance_pack["workflow_template"],
            "query_bundle": governance_pack["query_bundle"],
            "mechanism_library": governance_pack["mechanism_library"],
            "release_gate_packet": governance_pack["release_gate_packet"],
            "skill_wrapper": governance_pack["skill_wrapper"],
        },
        "promotion_rationale": "Promoted after deterministic mandate-1 win and reusable artifact quality.",
    }
    protocol_pack["package_hash"] = _hash(protocol_pack)

    write_json(out_dir / "GovernanceValidationPack-v1.json", governance_pack)
    write_json(out_dir / "ProtocolCybersecurityPack-v1.json", protocol_pack)
    # Compatibility alias for legacy docs/scripts.
    write_json(out_dir / "ProtocolAssurancePack-v1.json", protocol_pack)
    return governance_pack, protocol_pack
