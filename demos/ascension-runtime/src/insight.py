from __future__ import annotations

from pathlib import Path

from .utils import write_json, write_text


def run(cfg: dict, out: Path, claim_boundary: str) -> dict:
    packet = {
        "runtime_id": cfg["runtime_id"],
        "id": "insight-protocol-correctness-001",
        "public_role": "discovers AGI Alpha opportunities",
        "repo_role": "opportunity / wedge selector",
        "selected_wedge": "protocol and smart-contract correctness",
        "wedge_basis": [
            "verification is strongest",
            "replay is strong",
            "review is fast",
            "evidence is objective",
            "archive density builds fastest",
            "buyers already pay for this category",
        ],
        "frontier_queue": [
            "formal verification automation",
            "fuzz harness hardening",
            "governance parameter simulation",
        ],
        "repo_evidence": [
            "demos/protocol_smart_contract_correctness_demo/README.md",
            "demos/adjacent_mandate_reuse_proof_demo/README.md",
            "demos/adjacent_mandate_reuse_proof_real_v1/README.md",
            "demos/open-ended-rsi-system/README.md",
        ],
        "status": "deterministic local artifact; external foresight not proven",
        "claim_boundary": claim_boundary,
    }
    rationale = """# Insight rationale

The first wedge is protocol and smart-contract correctness.

Why this wedge is selected first:
- verification is strongest,
- replay is strong,
- review is fast,
- evidence is objective,
- archive density builds fastest,
- buyers already pay for this category.

This rationale is anchored to repo-native evidence surfaces and remains bounded to local/devnet replay.
"""
    write_json(out / "insight_packet.json", packet)
    write_text(out / "insight_rationale.md", rationale)
    return packet
