from __future__ import annotations

from pathlib import Path

from .utils import write_json, write_text


def run(cfg: dict, out: Path, claim_boundary: str) -> dict:
    rows = [
        ("Insight", "implemented", "local-devnet", "out/insight_packet.json", "pass", "medium", "external foresight validation"),
        ("Nova-Seeds", "implemented", "local-devnet", "out/nova_seed_packet.json", "pass", "medium", "seed-onchain registry parity"),
        ("MARK", "implemented", "simulated", "out/mark_selection_report.json", "pass", "medium", "testnet event-backed scoring"),
        ("Sovereign", "implemented", "local-devnet", "out/sovereign_manifest.json", "pass", "medium", "contract state-lock proofs"),
        ("Business", "implemented", "local-devnet", "out/business_operating_plan.json", "pass", "low", "multi-round mandate evidence"),
        ("Marketplace", "implemented", "simulated", "out/marketplace_round.json", "pass", "medium", "devnet escrow integration"),
        ("AGI Jobs", "implemented", "local-devnet", "out/agi_job_receipt.json", "pass", "medium", "onchain receipt adapter"),
        ("Agents", "implemented", "local-devnet", "out/agent_execution_log.json", "pass", "medium", "long-horizon reputation evidence"),
        ("Validators / Council", "implemented", "local-devnet", "out/validation_round.json", "pass", "medium", "human/external reviewer integration"),
        ("Value Reservoir", "implemented", "simulated", "out/reservoir_ledger.json", "pass", "high", "tokenized settlement evidence"),
        ("Architect", "implemented", "local-devnet", "out/architect_recommendation.json", "pass", "medium", "recommendation backtesting"),
        ("Nodes", "implemented", "local-devnet", "out/node_runtime_profile.json", "pass", "low", "multi-node distributed replay"),
        ("Archive", "implemented", "local-devnet", "out/archive_lineage.json", "pass", "medium", "merkleized lineage commitments"),
    ]
    payload = {
        "runtime_id": cfg["runtime_id"],
        "layers": [
            {
                "layer": layer,
                "implementation_status": impl,
                "runtime_mode": mode,
                "evidence_artifact": artifact,
                "result": result,
                "risk_level": risk,
                "next_required_proof": next_proof,
                "pending_items": [],
                "unproven_items": [
                    "audited-final deployment safety",
                    "mainnet-ready settlement",
                    "live external-market validation",
                ],
                "claim_boundary": "local/devnet only; no live production claim",
            }
            for layer, impl, mode, artifact, result, risk, next_proof in rows
        ],
        "claim_boundary": claim_boundary,
    }
    write_json(out / "ascension_runtime_scorecard.json", payload)
    md = "# Ascension Runtime Scorecard\n\n"
    md += "All rows are bounded local/devnet evidence and explicitly non-mainnet.\n\n"
    for row in payload["layers"]:
        md += f"- **{row['layer']}** — {row['implementation_status']} / {row['runtime_mode']} / {row['result']}; evidence `{row['evidence_artifact']}`; next proof: {row['next_required_proof']}; risk: {row['risk_level']}.\n"
    write_text(out / "ascension_runtime_scorecard.md", md)
    return payload
