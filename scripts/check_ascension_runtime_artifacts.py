#!/usr/bin/env python3
"""Validate required ascension-runtime artifact contract for local/devnet replay."""

from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "demos" / "ascension-runtime" / "out"
RUN_DEMO = ROOT / "demos" / "ascension-runtime" / "run_demo.py"

REQUIRED_ARTIFACTS = [
    "insight_packet.json",
    "insight_rationale.md",
    "nova_seed_packet.json",
    "nova_seeds/audit_factory_seed.json",
    "nova_seeds/invariant_library_seed.json",
    "nova_seeds/fuzz_harness_seed.json",
    "nova_seeds/exploit_replay_seed.json",
    "nova_seeds/governance_parameter_simulator_seed.json",
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
    "jobs/job_001_spec.json",
    "jobs/job_001_completion.json",
    "jobs/job_001_receipt.json",
    "jobs/job_001_event_log.json",
    "jobs/job_002_spec.json",
    "jobs/job_002_completion.json",
    "jobs/job_002_receipt.json",
    "jobs/job_002_event_log.json",
    "agents/agent_profiles.json",
    "agent_execution_log.json",
    "agent_reputation_snapshot.json",
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
]


def _extract_run_demo_required_artifacts() -> list[str]:
    """Parse run_demo.py and extract the assert-mode `required = [...]` artifact list."""
    tree = ast.parse(RUN_DEMO.read_text(encoding="utf-8"), filename=str(RUN_DEMO))

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "required":
                    if not isinstance(node.value, ast.List):
                        continue
                    values: list[str] = []
                    for elt in node.value.elts:
                        if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                            raise ValueError("run_demo.py assert-mode required list contains non-string entries")
                        values.append(elt.value)
                    return values

    raise ValueError("unable to locate assert-mode required artifact list in run_demo.py")


def _validate_contract_parity() -> list[str]:
    runtime_required = sorted(_extract_run_demo_required_artifacts())
    checker_required = sorted(REQUIRED_ARTIFACTS)

    errors: list[str] = []
    runtime_only = sorted(set(runtime_required) - set(checker_required))
    checker_only = sorted(set(checker_required) - set(runtime_required))

    if runtime_only:
        errors.append(
            "checker missing artifacts required by demos/ascension-runtime/run_demo.py: "
            + ", ".join(runtime_only)
        )
    if checker_only:
        errors.append(
            "checker includes artifacts not required by demos/ascension-runtime/run_demo.py: "
            + ", ".join(checker_only)
        )

    return errors


def main() -> int:
    errors = _validate_contract_parity()
    if errors:
        print("FAIL: ascension runtime checker contract parity failed")
        for err in errors:
            print(f"- {err}")
        return 1

    missing = [path for path in REQUIRED_ARTIFACTS if not (OUT / path).exists()]
    if missing:
        print("FAIL: ascension runtime artifact check failed")
        for path in missing:
            print(f"- missing: demos/ascension-runtime/out/{path}")
        return 1

    print("PASS: ascension runtime required artifacts are present")
    print("PASS: checker artifact contract matches run_demo.py --assert required list")
    print(f"Checked {len(REQUIRED_ARTIFACTS)} artifacts under {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
