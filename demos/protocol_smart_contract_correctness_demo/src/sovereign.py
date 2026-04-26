from __future__ import annotations

from .utils import demo_timestamp, write_json


def emit_sovereign_or_ruling(scorecard: dict, protocol_pack: dict, out_dir):
    now = demo_timestamp()
    if scorecard["passes"]["adjacent_mandate_proof"]:
        artifact = {
            "id": "ProtocolCybersecuritySovereign-v1.synthetic.json",
            "legacy_aliases": ["ProtocolAssuranceSovereign-v1.synthetic.json"],
            "type": "synthetic_sovereign_artifact",
            "status": "emitted",
            "depends_on": protocol_pack["id"],
            "package_hash": protocol_pack["package_hash"],
            "constitutional_order": ["identity", "proof", "settlement", "governance"],
            "invariant": [
                "no value without evidence",
                "no autonomy without authority",
                "no settlement without validation",
            ],
            "timestamp": now,
            "positioning": "First narrow, high-verification production organ and compounding correctness sovereign form in synthetic demo context.",
            "future_seed": "Seed of a future broader α-AGI Cybersecurity Sovereign.",
            "not_claimed": [
                "This does NOT prove that a full cybersecurity sovereign already exists.",
                "This does NOT claim cybersecurity is solved once and for all.",
                "This does NOT claim thermodynamic framing is literal physical law.",
            ],
            "disclaimer": "Synthetic local demo artifact; not a real-world proof.",
        }
        write_json(out_dir / artifact["id"], artifact)
        write_json(out_dir / "ProtocolAssuranceSovereign-v1.synthetic.json", artifact)
        return artifact

    ruling = {
        "id": "ProtocolCybersecuritySovereign-v1.fail_closed.json",
        "legacy_aliases": ["ProtocolAssuranceSovereign-v1.fail_closed.json"],
        "type": "governance_ruling",
        "status": "blocked",
        "reason": "Adjacent-mandate proof thresholds not met.",
        "failed_thresholds": [k for k, ok in scorecard["passes"].items() if not ok],
        "timestamp": now,
        "disclaimer": "Fail-closed synthetic ruling for replayability.",
    }
    write_json(out_dir / ruling["id"], ruling)
    write_json(out_dir / "ProtocolAssuranceSovereign-v1.fail_closed.json", ruling)
    return ruling
