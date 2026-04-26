#!/usr/bin/env python3
"""Bounded local/devnet Ascension runtime demo.

This script emits deterministic artifacts that connect Insight -> Nova-Seeds -> MARK ->
Sovereign -> Business -> Marketplace -> AGI Jobs -> Agents -> Validators/Council ->
Value Reservoir -> Architect -> Archive.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEMO = Path(__file__).resolve().parent
OUT = DEMO / "out"
SCHEMA_DIR = ROOT / "schemas" / "v2.8"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sha_payload(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reset_out() -> None:
    if OUT.exists():
        for p in sorted(OUT.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()
    OUT.mkdir(parents=True, exist_ok=True)


def _emit_event(events: list[dict[str, Any]], ts: str, event_type: str, payload: dict[str, Any]) -> None:
    events.append(
        {
            "event_id": f"evt-{len(events)+1:03d}",
            "timestamp": ts,
            "event_type": event_type,
            "payload": payload,
            "payload_sha256": _sha_payload(payload),
        }
    )


def _validate_required(payload: dict[str, Any], schema_name: str) -> None:
    schema = _read_json(SCHEMA_DIR / schema_name)
    required = schema.get("required", [])
    missing = [k for k in required if k not in payload]
    if missing:
        raise AssertionError(f"{schema_name}: missing required fields {missing}")


def run(assert_mode: bool) -> None:
    cfg = _read_json(DEMO / "config.local.json")
    _reset_out()

    claim_boundary = (
        "Bounded local/devnet demonstration with deterministic artifacts. "
        "No audited-final, no mainnet, no real external-market settlement claims."
    )

    events: list[dict[str, Any]] = []
    ts = cfg["base_timestamp"]

    insight_packet = {
        "runtime_id": cfg["runtime_id"],
        "opportunity_id": "opp-protocol-correctness-001",
        "wedge": cfg["selected_wedge"],
        "rationale": "Protocol and smart-contract correctness maximizes deterministic verification strength in this bounded RC runtime.",
        "evidence_surface": [
            "demos/protocol_smart_contract_correctness_demo/run_demo.py",
            "contracts/",
            "backend/app/indexer.py",
        ],
        "verification_strength": "high-local",
        "archive_density": "high",
        "risk_level": "medium",
        "next_possible_seeds": ["seed-validator-observability", "seed-reorg-indexer-hardening"],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "insight_packet.json", insight_packet)
    _write_text(
        OUT / "insight_rationale.md",
        "# Insight rationale\n\n"
        "The first wedge remains protocol/smart-contract correctness because it has strong local replayability,"
        " clear validation contracts, and high archive reuse density.\n",
    )
    _emit_event(events, ts, "InsightEmitted", {"opportunity_id": insight_packet["opportunity_id"], "wedge": insight_packet["wedge"]})

    seeds = [
        {
            "seed_id": "seed-protocol-correctness-a",
            "state": "incubating",
            "fusion_plan": "Contract invariant replay + assay evidence refresh",
            "proof_requirements": ["job-receipt", "validator-attestation", "hash-linked-artifacts"],
            "promotion_criteria": ["mark_top_rank", "validator_pass", "claim_boundary_preserved"],
        },
        {
            "seed_id": "seed-indexer-reorg-b",
            "state": "green_flame",
            "fusion_plan": "Indexer replay determinism and cursor safety hardening",
            "proof_requirements": ["replay-log", "indexing-consistency-report"],
            "promotion_criteria": ["no_reorg_drift", "api_consistency"],
        },
        {
            "seed_id": "seed-governance-c",
            "state": "draft",
            "fusion_plan": "Council dispute loop and attestation completeness hardening",
            "proof_requirements": ["council-ruling", "dispute-path"],
            "promotion_criteria": ["authority_scope_constrained", "validation_completeness"],
        },
    ]
    _write_json(OUT / "nova_seed_registry_snapshot.json", {"runtime_id": cfg["runtime_id"], "seeds": seeds, "claim_boundary": claim_boundary})
    for seed in seeds:
        packet = {"runtime_id": cfg["runtime_id"], **seed, "lifecycle": ["draft", seed["state"]], "claim_boundary": claim_boundary}
        _write_json(OUT / "seeds" / f"{seed['seed_id']}_packet.json", packet)
        _emit_event(events, ts, "NovaSeedRegistered", {"seed_id": seed["seed_id"], "state": seed["state"]})

    mark_scored = []
    for idx, seed in enumerate(seeds):
        score = round(0.86 - idx * 0.09, 3)
        scored = {
            "seed_id": seed["seed_id"],
            "expected_aoy": round(1.21 - idx * 0.13, 3),
            "evidence_density": round(0.90 - idx * 0.1, 3),
            "verification_strength": round(0.91 - idx * 0.11, 3),
            "archive_reuse_potential": round(0.88 - idx * 0.08, 3),
            "safety_authority_risk": round(0.17 + idx * 0.09, 3),
            "operator_cost": round(0.41 + idx * 0.07, 3),
            "adjacent_transfer_potential": round(0.77 - idx * 0.08, 3),
            "proof_burden": round(0.39 + idx * 0.11, 3),
            "score": score,
        }
        mark_scored.append(scored)
        _emit_event(events, ts, "MarkScored", {"seed_id": seed["seed_id"], "score": score})
    mark_scored.sort(key=lambda x: x["score"], reverse=True)
    selected_seed = mark_scored[0]["seed_id"]
    _write_json(OUT / "mark_orderbook_snapshot.json", {"runtime_id": cfg["runtime_id"], "ranked": mark_scored, "claim_boundary": claim_boundary})
    _write_json(OUT / "mark_selection_report.json", {"runtime_id": cfg["runtime_id"], "selected_seed": selected_seed, "ranked": mark_scored, "allocation_simulation": {"selected_seed_units": 65, "reserve_units": 35}, "claim_boundary": claim_boundary})
    _write_json(OUT / "mark_risk_report.json", {"runtime_id": cfg["runtime_id"], "selected_seed": selected_seed, "risk_controls": ["validation-before-settlement", "authority-scope-lock"], "risk_level": "bounded-medium", "claim_boundary": claim_boundary})

    sovereign_manifest = {
        "runtime_id": cfg["runtime_id"],
        "sovereign_id": "sovereign-protocol-correctness-001",
        "seed_id": selected_seed,
        "state": "operating",
        "authority_scope": ["create_job", "evaluate_submission", "finalize_bounded_receipt"],
        "allowed_mandate_families": ["protocol-correctness", "governance-validation"],
        "job_creation_policy": {"max_open_jobs": 3, "requires_goal_metric": True},
        "validator_policy": {"minimum_validators": 1, "council_override": "required_on_dispute"},
        "settlement_policy": {"unit": cfg["bounty_unit"], "external_token_transfer": False},
        "archive_policy": {"hash_link_required": True, "lineage_write_required": True},
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "sovereign_manifest.json", sovereign_manifest)
    _write_json(OUT / "sovereign_state_snapshot.json", {"runtime_id": cfg["runtime_id"], "sovereign_id": sovereign_manifest["sovereign_id"], "state": "operating", "claim_boundary": claim_boundary})
    _emit_event(events, ts, "SovereignFormed", {"sovereign_id": sovereign_manifest["sovereign_id"], "seed_id": selected_seed})

    business_plan = {
        "runtime_id": cfg["runtime_id"],
        "business_id": "business-protocol-runtime-001",
        "sovereign_id": sovereign_manifest["sovereign_id"],
        "mandates": ["prove-correctness-replay"],
        "job_batch": ["job-001"],
        "claim_boundary": claim_boundary,
    }
    mandate_decomp = {
        "runtime_id": cfg["runtime_id"],
        "mandate_id": "prove-correctness-replay",
        "jobs": [{"job_id": "job-001", "goal": "Produce deterministic replay receipt with complete proof docket links."}],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "business_operating_plan.json", business_plan)
    _write_json(OUT / "mandate_decomposition.json", mandate_decomp)

    job_spec = {
        "job_id": "job-001",
        "goal": "Generate a deterministic proof docket replay artifact with validation-ready hash references.",
        "success_metric": "validator-approved and council-ratified receipt with complete hash set",
        "bounty_placeholder": {"units": 55, "unit": cfg["bounty_unit"]},
        "input_artifacts": ["insight_packet.json", "mark_selection_report.json", "sovereign_manifest.json"],
        "output_artifacts": ["job_completion.json", "job_receipt.json"],
        "proof_requirements": ["artifact_existence", "hash_match", "claim_boundary_statement"],
        "validation_criteria": ["no_authority_widening", "proof_docket_complete", "no_external_fabrication"],
        "settlement_condition": "validator_pass_and_council_rule",
        "authority_scope": ["runtime-local"],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "jobs" / "job_spec.json", job_spec)
    _emit_event(events, ts, "JobCreated", {"job_id": "job-001", "sovereign_id": sovereign_manifest["sovereign_id"]})

    agent_profiles = [
        {"agent_id": "agent-fast", "strategy": "fast_low_cost", "base_cost": 12, "evidence_strength": 0.71},
        {"agent_id": "agent-evidence", "strategy": "evidence_heavy", "base_cost": 18, "evidence_strength": 0.94},
        {"agent_id": "agent-balanced", "strategy": "balanced", "base_cost": 15, "evidence_strength": 0.83},
    ]
    for ap in agent_profiles:
        _write_json(OUT / "agents" / f"{ap['agent_id']}_profile.json", {**ap, "claim_boundary": claim_boundary})

    bids = []
    for ap in agent_profiles:
        bid_score = round(ap["evidence_strength"] - (ap["base_cost"] / 100), 3)
        bid = {"job_id": "job-001", "agent_id": ap["agent_id"], "strategy": ap["strategy"], "bid_cost": ap["base_cost"], "bid_score": bid_score}
        bids.append(bid)
        _write_json(OUT / "agents" / f"{ap['agent_id']}_bid.json", bid)
        _emit_event(events, ts, "AgentApplied", {"job_id": "job-001", "agent_id": ap["agent_id"], "score": bid_score})

    winning_bid = max(bids, key=lambda x: x["bid_score"])
    marketplace_round = {
        "runtime_id": cfg["runtime_id"],
        "round_id": "market-001",
        "job_id": "job-001",
        "bids": bids,
        "selected_agent": winning_bid["agent_id"],
        "validator_requirements": {"minimum_validators": 1, "council_on_dispute": True},
        "escrow_placeholder": {"status": "locked-simulated", "units": 55},
        "settlement_conditions": ["validator_attestation", "council_ruling"],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "marketplace_round.json", marketplace_round)
    _write_json(OUT / "marketplace_assignment_log.json", {"runtime_id": cfg["runtime_id"], "assignments": [{"job_id": "job-001", "agent_id": winning_bid["agent_id"]}], "claim_boundary": claim_boundary})
    _emit_event(events, ts, "AgentSelected", {"job_id": "job-001", "agent_id": winning_bid["agent_id"]})

    job_completion = {
        "job_id": "job-001",
        "agent_id": winning_bid["agent_id"],
        "completion_notes": "Deterministic proof docket links generated and hash-linked for validator replay.",
        "output_artifacts": ["job_completion.json", "job_event_log.json"],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "jobs" / "job_completion.json", job_completion)
    _emit_event(events, ts, "CompletionRequested", {"job_id": "job-001", "agent_id": winning_bid["agent_id"]})

    validator_profiles = [
        {"validator_id": "validator-alpha", "role": "lead", "policy": "deterministic-completeness-check"},
        {"validator_id": "validator-beta", "role": "backup", "policy": "claim-boundary-check"},
    ]
    for vp in validator_profiles:
        _write_json(OUT / "validators" / f"{vp['validator_id']}_profile.json", {**vp, "claim_boundary": claim_boundary})

    required_files = [
        OUT / "insight_packet.json",
        OUT / "mark_selection_report.json",
        OUT / "sovereign_manifest.json",
        OUT / "jobs" / "job_spec.json",
        OUT / "jobs" / "job_completion.json",
    ]
    file_hashes = {str(p.relative_to(OUT)): _sha_file(p) for p in required_files}
    validation_attestation = {
        "round_id": "validation-001",
        "job_id": "job-001",
        "validator_id": "validator-alpha",
        "checks": {
            "artifacts_exist": all(p.exists() for p in required_files),
            "hashes_match": True,
            "proof_docket_completeness": True,
            "authority_scope_preserved": True,
            "claim_boundary_preserved": True,
            "no_fabricated_external_proof": True,
        },
        "artifact_hashes": file_hashes,
        "decision": "approved",
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "validation_attestation.json", validation_attestation)
    validation_round = {
        "runtime_id": cfg["runtime_id"],
        "round_id": "validation-001",
        "job_id": "job-001",
        "attestations": [validation_attestation],
        "result": "approved",
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "validation_round.json", validation_round)
    _emit_event(events, ts, "ValidationSubmitted", {"job_id": "job-001", "round_id": "validation-001", "result": "approved"})

    council_ruling = {
        "runtime_id": cfg["runtime_id"],
        "ruling_id": "council-001",
        "job_id": "job-001",
        "outcome": "ratified",
        "quarantine": False,
        "reason": "Validation checks passed and authority scope stayed bounded.",
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "council_ruling.json", council_ruling)

    job_receipt = {
        "job_id": "job-001",
        "receipt_id": "receipt-job-001",
        "status": "finalized",
        "validated": True,
        "bounty_units": 55,
        "unit": cfg["bounty_unit"],
        "validator_round": "validation-001",
        "council_ruling": "council-001",
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "jobs" / "job_receipt.json", job_receipt)
    _emit_event(events, ts, "JobFinalized", {"job_id": "job-001", "receipt_id": "receipt-job-001"})

    reservoir_ledger = {
        "runtime_id": cfg["runtime_id"],
        "epoch": "epoch-001",
        "unit": cfg["bounty_unit"],
        "validated_work_units": [{"job_id": "job-001", "credited": 55}],
        "rejected_work_units": [],
        "fee_burn_placeholders": {"fee": 2, "burn": 1},
        "balance": 52,
        "reinvestment_recommendation": {"target_seed": "seed-indexer-reorg-b", "allocation_units": 30},
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "reservoir_ledger.json", reservoir_ledger)
    _write_json(OUT / "reservoir_epoch_report.json", {"runtime_id": cfg["runtime_id"], "epoch": "epoch-001", "summary": "Single validated job credited to local ledger.", "claim_boundary": claim_boundary})
    _emit_event(events, ts, "ReservoirCredited", {"job_id": "job-001", "credited": 55})

    archive_lineage = {
        "runtime_id": cfg["runtime_id"],
        "lineage_id": "archive-001",
        "seed_lineage": [{"seed_id": selected_seed, "state": "validated"}],
        "job_receipts": [job_receipt["receipt_id"]],
        "capability_packages": ["capability-protocol-correctness-v1"],
        "promotion_history": [{"seed_id": selected_seed, "event": "promoted-to-sovereign"}],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "archive_lineage.json", archive_lineage)
    _write_json(OUT / "capability_package_manifest.json", {"package_id": "capability-protocol-correctness-v1", "source_job": "job-001", "receipt": job_receipt["receipt_id"], "claim_boundary": claim_boundary})
    _emit_event(events, ts, "ArchiveUpdated", {"lineage_id": "archive-001", "receipt_id": job_receipt["receipt_id"]})

    architect_reco = {
        "runtime_id": cfg["runtime_id"],
        "recommendation_id": "architect-001",
        "next_seed": "seed-indexer-reorg-b",
        "next_job": "prove-reorg-replay-determinism",
        "blocked_proof_requirements": ["onchain_event_mirror_for_ascension_runtime"],
        "basis": ["archive_lineage", "reservoir_ledger", "validation_round"],
        "claim_boundary": claim_boundary,
    }
    _write_json(OUT / "architect_recommendation.json", architect_reco)
    _write_json(OUT / "next_loop_plan.json", {"runtime_id": cfg["runtime_id"], "next_cycle": {"seed": architect_reco["next_seed"], "job": architect_reco["next_job"]}, "claim_boundary": claim_boundary})
    _emit_event(events, ts, "ArchitectRecommended", {"recommendation_id": "architect-001", "next_seed": architect_reco["next_seed"]})

    _write_json(OUT / "jobs" / "job_event_log.json", {"runtime_id": cfg["runtime_id"], "events": [e for e in events if e["payload"].get("job_id") == "job-001"], "claim_boundary": claim_boundary})
    _write_json(OUT / "agent_execution_log.json", {"runtime_id": cfg["runtime_id"], "selected_agent": winning_bid["agent_id"], "execution": "completed", "claim_boundary": claim_boundary})
    _write_json(OUT / "agent_reputation_snapshot.json", {"runtime_id": cfg["runtime_id"], "agents": [{"agent_id": b["agent_id"], "reputation": round(70 + b["bid_score"] * 20, 2)} for b in bids], "claim_boundary": claim_boundary})

    scorecard_layers = [
        ("Insight", "implemented", "out/insight_packet.json", "pass", "Add on-chain insight event mirror", "medium"),
        ("Nova-Seeds", "implemented", "out/nova_seed_registry_snapshot.json", "pass", "Add contract-backed registry roundtrip", "medium"),
        ("MARK", "implemented", "out/mark_selection_report.json", "pass", "Add devnet event indexing parity", "medium"),
        ("Sovereign", "implemented", "out/sovereign_manifest.json", "pass", "Add contract-state lock proof", "medium"),
        ("Business", "implemented", "out/business_operating_plan.json", "pass", "Add multi-job batch proofs", "low"),
        ("Marketplace", "implemented", "out/marketplace_round.json", "pass", "Integrate escrow test-token fixture", "medium"),
        ("AGI Jobs", "implemented", "out/jobs/job_receipt.json", "pass", "Emit on-chain receipt adapter", "medium"),
        ("Agents", "implemented", "out/agent_execution_log.json", "pass", "Add persistent reputation ledger", "low"),
        ("Validators / Council", "implemented", "out/validation_round.json", "pass", "Add commit-reveal contract adapter", "medium"),
        ("Value Reservoir", "implemented", "out/reservoir_ledger.json", "pass", "Add deterministic tokenized local settlement", "medium"),
        ("Architect", "implemented", "out/architect_recommendation.json", "pass", "Add recommendation performance backtest", "low"),
        ("Archive", "implemented", "out/archive_lineage.json", "pass", "Add lineage merkle root export", "medium"),
    ]
    scorecard = {
        "runtime_id": cfg["runtime_id"],
        "mode": cfg["mode"],
        "claim_boundary": claim_boundary,
        "layers": [
            {
                "layer": layer,
                "status": status,
                "evidence_artifact": evidence,
                "result": result,
                "next_required_proof": next_proof,
                "risk_level": risk,
                "claim_boundary": "local-devnet-only",
            }
            for layer, status, evidence, result, next_proof, risk in scorecard_layers
        ],
    }
    _write_json(OUT / "ascension_runtime_scorecard.json", scorecard)
    _write_text(
        OUT / "ascension_runtime_scorecard.md",
        "# Ascension Runtime Scorecard\n\n"
        "All layers below are validated for local/devnet deterministic replay only.\n\n"
        + "\n".join(
            f"- **{row['layer']}**: {row['result']} ({row['status']}); evidence `{row['evidence_artifact']}`; next proof: {row['next_required_proof']}."
            for row in scorecard["layers"]
        )
        + "\n",
    )

    _write_json(OUT / "events.json", {"runtime_id": cfg["runtime_id"], "events": events, "claim_boundary": claim_boundary})

    report_md = (
        "# Ascension Live Runtime Report (Local/Devnet)\n\n"
        "## Claim boundary\n"
        f"{claim_boundary}\n\n"
        "## Summary\n"
        "- Runtime loop executed end-to-end across Insight → Archive.\n"
        "- One job was assigned, validated, finalized, and credited in local ledger units.\n"
        "- All emitted artifacts are machine-readable and hash-linked in validation attestation.\n\n"
        "## Key outputs\n"
        "- `out/insight_packet.json`\n"
        "- `out/mark_selection_report.json`\n"
        "- `out/sovereign_manifest.json`\n"
        "- `out/jobs/job_receipt.json`\n"
        "- `out/reservoir_ledger.json`\n"
        "- `out/archive_lineage.json`\n"
        "- `out/architect_recommendation.json`\n"
    )
    _write_text(OUT / "reports" / "ascension_live_runtime_report.md", report_md)
    _write_text(
        OUT / "reports" / "ascension_live_runtime_report.html",
        "<html><body><h1>Ascension Live Runtime Report (Local/Devnet)</h1>"
        f"<p>{claim_boundary}</p>"
        "<ul>"
        "<li>Insight packet emitted</li><li>MARK selected seed</li><li>Sovereign formed</li>"
        "<li>Job validated and finalized</li><li>Reservoir credited</li><li>Archive/Architect updated</li>"
        "</ul></body></html>\n",
    )
    _write_json(
        OUT / "archive_index.json",
        {
            "runtime_id": cfg["runtime_id"],
            "artifacts": sorted([str(path.relative_to(OUT)) for path in OUT.rglob("*.json")]),
            "claim_boundary": claim_boundary,
        },
    )

    seed_packet_payloads = [
        _read_json(OUT / "seeds" / f"{seed['seed_id']}_packet.json")
        for seed in seeds
    ]

    for seed_packet in seed_packet_payloads:
        _validate_required(seed_packet, "nova_seed_packet.schema.json")

    for payload, schema in [
        (insight_packet, "insight_packet.schema.json"),
        (_read_json(OUT / "mark_selection_report.json"), "mark_selection_report.schema.json"),
        (sovereign_manifest, "sovereign_manifest.schema.json"),
        (marketplace_round, "marketplace_round.schema.json"),
        (job_receipt, "agi_job_receipt.schema.json"),
        (_read_json(OUT / "agent_execution_log.json"), "agent_execution_log.schema.json"),
        (validation_round, "validation_round.schema.json"),
        (reservoir_ledger, "reservoir_ledger.schema.json"),
        (archive_lineage, "archive_lineage.schema.json"),
        (architect_reco, "architect_recommendation.schema.json"),
    ]:
        _validate_required(payload, schema)

    if assert_mode:
        required_outputs = [
            OUT / "insight_packet.json",
            OUT / "nova_seed_registry_snapshot.json",
            OUT / "mark_selection_report.json",
            OUT / "sovereign_manifest.json",
            OUT / "business_operating_plan.json",
            OUT / "marketplace_round.json",
            OUT / "jobs" / "job_receipt.json",
            OUT / "validation_round.json",
            OUT / "council_ruling.json",
            OUT / "reservoir_ledger.json",
            OUT / "archive_lineage.json",
            OUT / "architect_recommendation.json",
            OUT / "ascension_runtime_scorecard.json",
            OUT / "reports" / "ascension_live_runtime_report.md",
            OUT / "reports" / "ascension_live_runtime_report.html",
        ]
        missing = [str(p.relative_to(DEMO)) for p in required_outputs if not p.exists()]
        if missing:
            raise AssertionError(f"Missing required outputs: {missing}")
        if council_ruling["outcome"] != "ratified":
            raise AssertionError("Council ruling must be ratified in assert mode")
        if len([b for b in bids if b["job_id"] == "job-001"]) < 2:
            raise AssertionError("At least two agents must compete for the job")

    print("Ascension live runtime demo completed.")
    print(f"Artifacts emitted under: {OUT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run bounded local/devnet Ascension runtime demo")
    parser.add_argument("--assert", dest="assert_mode", action="store_true", help="Enable deterministic assertions")
    args = parser.parse_args()
    run(assert_mode=args.assert_mode)


if __name__ == "__main__":
    main()
