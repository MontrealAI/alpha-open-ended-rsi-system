#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from src import agents, archive, architect, business, insight, jobs, mark, marketplace, nodes, nova_seed, report, reservoir, scorecard, sovereign, validators
from src.utils import read_json, reset_dir, validate_json_schema

DEMO = Path(__file__).resolve().parent
OUT = DEMO / "out"


def run(assert_mode: bool) -> None:
    cfg = read_json(DEMO / "config.local.json")
    claim_boundary = (
        "The repository now contains a bounded local/devnet Minimum Viable Ascension Runtime that demonstrates "
        "the Ascension organism's proof-first economic loop. It does not claim completed live Ascension or "
        "mainnet production readiness."
    )
    reset_dir(OUT)

    insight.run(cfg, OUT, claim_boundary)
    seeds = nova_seed.run(cfg, OUT, claim_boundary)
    selection = mark.run(cfg, OUT, seeds, claim_boundary)
    sovereign_manifest = sovereign.run(cfg, OUT, selection, claim_boundary)
    decomp = business.run(cfg, OUT, sovereign_manifest, claim_boundary)
    agent_data = agents.run(OUT, decomp["jobs"], claim_boundary)
    market = marketplace.run(cfg, OUT, decomp["jobs"], agent_data, claim_boundary)
    receipts = jobs.run(cfg, OUT, decomp["jobs"], market["assignments"], claim_boundary)
    validation = validators.run(OUT, receipts, claim_boundary)
    reservoir.run(cfg, OUT, receipts, validation, claim_boundary)
    nodes.run(OUT, claim_boundary)
    archive.run(OUT, selection["selected_bundle"], receipts, selection["ranked"], claim_boundary)
    architect.run(OUT, claim_boundary)
    scorecard.run(cfg, OUT, claim_boundary)
    report.run(OUT, claim_boundary)
    archive.write_archive_index(OUT, claim_boundary)

    if assert_mode:
        required = [
            "insight_packet.json",
            "insight_rationale.md",
            "nova_seed_packet.json",
            "mark_selection_report.json",
            "mark_risk_report.json",
            "mark_orderbook_snapshot.json",
            "sovereign_manifest.json",
            "sovereign_state_snapshot.json",
            "business_operating_plan.json",
            "mandate_decomposition.json",
            "marketplace_round.json",
            "marketplace_assignment_log.json",
            "agi_job_receipt.json",
            "agent_execution_log.json",
            "agent_reputation_snapshot.json",
            "agents/agent_profiles.json",
            "validation_round.json",
            "validation_attestations.json",
            "council_ruling.json",
            "reservoir_ledger.json",
            "reservoir_epoch_report.json",
            "node_runtime_profile.json",
            "archive_lineage.json",
            "capability_package_manifest.json",
            "archive_index.json",
            "architect_recommendation.json",
            "next_loop_plan.json",
            "ascension_runtime_scorecard.json",
            "ascension_runtime_scorecard.md",
            "reports/ascension_runtime_report.md",
            "reports/ascension_runtime_report.html",
            "jobs/job_001_spec.json",
            "jobs/job_001_completion.json",
            "jobs/job_001_receipt.json",
            "jobs/job_001_event_log.json",
            "jobs/job_002_spec.json",
            "jobs/job_002_completion.json",
            "jobs/job_002_receipt.json",
            "jobs/job_002_event_log.json",
            "nova_seeds/audit_factory_seed.json",
            "nova_seeds/invariant_library_seed.json",
            "nova_seeds/fuzz_harness_seed.json",
            "nova_seeds/exploit_replay_seed.json",
            "nova_seeds/governance_parameter_simulator_seed.json",
        ]
        missing = [p for p in required if not (OUT / p).exists()]
        if missing:
            raise AssertionError(f"Missing required outputs: {missing}")

        execution = read_json(OUT / "agent_execution_log.json")
        if len({e["selected_agent"] for e in execution["executions"]}) < 1:
            raise AssertionError("No selected agents found")
        for job_id in {"job_001", "job_002"}:
            if len([b for b in execution["bids"] if b["job_id"] == job_id]) < 2:
                raise AssertionError(f"At least two agents must compete for {job_id}")

        validation_round = read_json(OUT / "validation_round.json")
        if validation_round.get("result") != "approved":
            raise AssertionError("Validation round must be approved in --assert mode")
        if not validation_round.get("attestations"):
            raise AssertionError("Validation round must include attestations")
        if any(a.get("decision") != "approved" for a in validation_round["attestations"]):
            raise AssertionError("All attestations must be approved in --assert mode")

        council_ruling = read_json(OUT / "council_ruling.json")
        if council_ruling.get("result") != "approve":
            raise AssertionError("Council ruling must be approve in --assert mode")
        if not council_ruling.get("approved_jobs"):
            raise AssertionError("Council ruling must approve at least one job")

        reservoir_ledger = read_json(OUT / "reservoir_ledger.json")
        validated_units = reservoir_ledger.get("validated_work_units", [])
        if len(validated_units) < 1:
            raise AssertionError("Reservoir must contain validated work units in --assert mode")

        schema_checks = {
            "insight_packet.json": "insight_packet.schema.json",
            "nova_seed_packet.json": "nova_seed_bundle.schema.json",
            "mark_selection_report.json": "mark_bundle_selection_report.schema.json",
            "sovereign_manifest.json": "sovereign_manifest.schema.json",
            "marketplace_round.json": "marketplace_round.schema.json",
            "agi_job_receipt.json": "agi_job_receipt_bundle.schema.json",
            "agent_execution_log.json": "agent_execution_round.schema.json",
            "validation_round.json": "validation_round.schema.json",
            "reservoir_ledger.json": "reservoir_ledger.schema.json",
            "archive_lineage.json": "archive_lineage.schema.json",
            "architect_recommendation.json": "architect_runtime_recommendation.schema.json",
            "ascension_runtime_scorecard.json": "ascension_runtime_scorecard.schema.json",
        }
        schema_root = DEMO.parent.parent / "schemas" / "v2.8"
        for artifact, schema_name in schema_checks.items():
            validate_json_schema(read_json(OUT / artifact), schema_root / schema_name)

    print("Ascension runtime demo completed.")
    print(f"Artifacts emitted under: {OUT}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run bounded local/devnet Ascension runtime demo")
    parser.add_argument("--assert", dest="assert_mode", action="store_true")
    args = parser.parse_args()
    run(args.assert_mode)


if __name__ == "__main__":
    main()
