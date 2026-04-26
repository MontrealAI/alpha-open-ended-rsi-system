#!/usr/bin/env python3
"""Initialize blinded adjacent-transfer result scaffolding with prereg freeze metadata.

This script creates a public-safe results bundle and a local-private workspace
for blinding materials. It does not fabricate reviewer inputs or pass/fail
outcomes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import secrets
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK_ROOT = Path(__file__).resolve().parents[1]

MANDATE_1_SCOPE = [
    "contracts/CouncilGovernanceV25.sol",
    "contracts/ChallengePolicyModuleV25.sol",
]
MANDATE_2_SCOPE = [
    "contracts/ThresholdNetworkAdapterV25.sol",
    "contracts/SignedAttestationVerifierV25.sol",
]
MANDATE_3_SCOPE = [
    "backend/app/main.py",
    "backend/app/indexer.py",
    "backend/app/schemas.py",
]

KIT_FILES = [
    "ontology.json",
    "query_bundle.json",
    "workflow_template.md",
    "mechanism_library.json",
    "safety_routing_rules.md",
    "scoring_rubric.md",
    "extraction_schema.json",
]


def run(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd or ROOT), text=True).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_text(src: Path, dst: Path) -> None:
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)


def build_public_provenance(results_dir: Path) -> dict[str, object]:
    tracked = [
        "README.md",
        "HUMAN_ACTION_REQUIRED.md",
        "summary_metrics.json",
        "stage_a_scorecard.md",
        "stage_b_scorecard.md",
        "proof_docket_public.md",
        "governance_ruling_public.md",
        "prereg_experiment_manifest.json",
        "environment_lock.json",
        "run_register.csv",
        "intervention_log.csv",
        "leakage_check.csv",
        "lane_blue_packet_public/README.md",
        "lane_blue_packet_public/stage_a/README.md",
        "lane_blue_packet_public/stage_b/README.md",
        "lane_gold_packet_public/README.md",
        "lane_gold_packet_public/stage_a/README.md",
        "lane_gold_packet_public/stage_b/README.md",
        "scorecard_outputs/README.md",
        "scorecard_outputs/run_costs.csv",
        "scorecard_outputs/output_scoring.csv",
        "scorecard_outputs/package_dependence_ledger.csv",
        "scorecard_outputs/reveal_receipt_public.json",
    ]
    hashes = []
    for rel in tracked:
        p = results_dir / rel
        if p.exists():
            hashes.append({"path": rel, "sha256": sha256_file(p)})

    return {
        "manifest_type": "blinded_adjacent_transfer_public_safe_provenance",
        "repo": "MontrealAI/alpha-nova-seeds",
        "result_path": str(results_dir.relative_to(ROOT)),
        "file_hashes": hashes,
        "private_materials_location": "demos/adjacent_mandate_reuse_proof_real_v1/local_private_blinding_materials/results_blinded_adjacent_transfer_v1",
        "private_materials_committed": False,
        "notes": "Public-safe provenance only; private mappings withheld by design.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        default="results_blinded_adjacent_transfer_v1",
        help="results directory name under the proof-pack root",
    )
    parser.add_argument(
        "--private-dir",
        default="local_private_blinding_materials/results_blinded_adjacent_transfer_v1",
        help="private local-only directory under proof-pack root",
    )
    parser.add_argument("--force", action="store_true", help="overwrite existing results dir")
    parser.add_argument(
        "--treatment-kit",
        choices=["Kit Blue", "Kit Gold"],
        default=None,
        help="optional fixed treatment kit assignment (default: randomized once and stored privately)",
    )
    args = parser.parse_args()

    results_dir = PACK_ROOT / args.results_dir
    private_dir = PACK_ROOT / args.private_dir

    if results_dir.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing {results_dir}; use --force to replace.")
    if results_dir.exists() and args.force:
        shutil.rmtree(results_dir)

    (results_dir / "lane_blue_packet_public" / "stage_a").mkdir(parents=True)
    (results_dir / "lane_blue_packet_public" / "stage_b").mkdir(parents=True)
    (results_dir / "lane_gold_packet_public" / "stage_a").mkdir(parents=True)
    (results_dir / "lane_gold_packet_public" / "stage_b").mkdir(parents=True)
    (results_dir / "scorecard_outputs").mkdir(parents=True)
    private_dir.mkdir(parents=True, exist_ok=True)

    repo_sha = run(["git", "rev-parse", "HEAD"])
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    freeze_time = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    scope_hashes: dict[str, str] = {}
    for rel in MANDATE_1_SCOPE + MANDATE_2_SCOPE + MANDATE_3_SCOPE:
        scope_hashes[rel] = sha256_file(ROOT / rel)

    experiment_manifest = {
        "experiment_id": "adjacent-mandate-reuse-real-v1-blinded-adjacent-transfer",
        "repo": "MontrealAI/alpha-nova-seeds",
        "repo_sha": repo_sha,
        "branch": branch,
        "target_path": "demos/adjacent_mandate_reuse_proof_real_v1",
        "execution_results_path": str(results_dir.relative_to(ROOT)),
        "vertical": "protocol-and-smart-contract-correctness",
        "publication_rule": "publish_result_whether_pass_or_fail",
        "stopping_rule": "stop_after_stage_a_if_any_threshold_fails_or_if_human_blinded_inputs_missing",
        "mandate_1": {
            "name": "Governance / dispute correctness",
            "scope": MANDATE_1_SCOPE,
            "goal": "Produce GovernanceValidationPack-v1",
        },
        "mandate_2": {
            "name": "Threshold / attestation correctness",
            "scope": MANDATE_2_SCOPE,
            "goal": "Measure adjacent-mandate reuse under blinded control vs treatment",
        },
        "mandate_3": {
            "name": "Backend / API correctness",
            "scope": MANDATE_3_SCOPE,
            "goal": "Conditional Stage B cross-domain transfer test",
            "status": "conditional_on_real_stage_a_pass",
        },
        "reviewer_blinding": {
            "operator_kits": ["Kit Blue", "Kit Gold"],
            "reviewer_packet_labels": ["Lane Blue", "Lane Gold"],
            "blinding_officer_must_be_separate_from_review_and_scoring": True,
            "leakage_questions_required": True,
            "kit_assignment_policy": "private_randomized_once_pre_execution",
        },
        "control_and_treatment_parallel": True,
        "human_intervention_logging_required": True,
        "wall_clock_budget_per_lane_minutes": 180,
        "compute_budget_per_lane": {
            "machine_class": "same-machine-class-required",
            "max_test_runs": "set-by-sponsor-before-run",
            "max_command_count": "set-by-sponsor-before-run",
            "network": "disallowed",
        },
        "out_of_scope_issue_types": [
            "non-deterministic cosmetic refactors",
            "out-of-scope architecture redesign",
            "claims beyond protocol-correctness wedge",
        ],
        "allowed_tools_and_commands": [
            "local shell tooling only",
            "repo-native scripts and tests",
            "scorecard helper: python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/calculate_q2_scorecard.py --scorecard-dir demos/adjacent_mandate_reuse_proof_real_v1/results_blinded_adjacent_transfer_v1/scorecard_outputs",
        ],
        "intervention_policy": "log all exceptions in intervention log; symmetry across lanes required",
        "reviewer_rubric": "demos/adjacent_mandate_reuse_proof_real_v1/03_review/reviewer_form_mandate_2_control.template.md and reviewer_form_mandate_2_treatment.template.md (normalized blinded packets)",
        "pass_thresholds": {
            "aoy_uplift_min_pct": 35,
            "speed_uplift_min_pct": 30,
            "rework_reduction_min_pct": 40,
            "evidence_completeness_uplift_min_pct": 20,
            "safety_regression_allowed": False,
            "package_dependence_min_pct": 30,
        },
        "freeze_time_utc": freeze_time,
    }

    environment_lock = {
        "python_version": sys.version.split()[0],
        "os": platform.platform(),
        "tool_versions": {
            "slither": "NA",
            "foundry": "NA",
            "hardhat": "NA",
            "node": run(["node", "--version"]) if shutil.which("node") else "NA",
        },
        "repo_sha": repo_sha,
        "branch": branch,
        "scope_hashes": scope_hashes,
        "allowed_human_interventions": [
            "budget approval",
            "policy clarification",
            "exception handling only",
        ],
    }

    (results_dir / "prereg_experiment_manifest.json").write_text(
        json.dumps(experiment_manifest, indent=2) + "\n", encoding="utf-8"
    )
    (results_dir / "environment_lock.json").write_text(
        json.dumps(environment_lock, indent=2) + "\n", encoding="utf-8"
    )

    copy_text(PACK_ROOT / "02_execution" / "run_register.template.csv", results_dir / "run_register.csv")
    copy_text(
        PACK_ROOT / "02_execution" / "intervention_log.template.csv",
        results_dir / "intervention_log.csv",
    )
    copy_text(
        PACK_ROOT / "03_review" / "leakage_check.template.csv",
        results_dir / "leakage_check.csv",
    )

    copy_text(
        PACK_ROOT / "04_scorecard" / "run_costs.template.csv",
        results_dir / "scorecard_outputs" / "run_costs.csv",
    )
    copy_text(
        PACK_ROOT / "04_scorecard" / "output_scoring.template.csv",
        results_dir / "scorecard_outputs" / "output_scoring.csv",
    )
    copy_text(
        PACK_ROOT / "04_scorecard" / "package_dependence_ledger.template.csv",
        results_dir / "scorecard_outputs" / "package_dependence_ledger.csv",
    )

    (results_dir / "README.md").write_text(
        """# Blinded Adjacent-Transfer Experiment Record (v1)

This folder operationalizes the blinded adjacent-transfer protocol for:

- Stage A: adjacent transfer in the protocol-correctness wedge
- Stage B: conditional cross-domain transfer into backend/API correctness

Status today: **operationalized to the honest human boundary**.

No reviewer judgments, lane outcomes, or pass/fail results were fabricated.

## 1) What was frozen

- Preregistration freeze: `prereg_experiment_manifest.json`
- Environment and in-scope file hashes: `environment_lock.json`
- Stage A and Stage B lane budget symmetry and thresholds are locked in preregistration
- Scorecard inputs are pre-wired under `scorecard_outputs/`
- Leakage-check worksheet is pre-wired at `leakage_check.csv`

## 2) What was blinded

- Public packets use lane IDs only: `lane_blue_packet_public/` and `lane_gold_packet_public/`
- Private assignment and reviewer identity maps are moved to git-ignored local storage:
  `../local_private_blinding_materials/results_blinded_adjacent_transfer_v1/`
- Private commitment hashes are generated locally with
  `../07_scripts/generate_private_commitment_hashes.py`

## 3) What passed / failed

- Stage A: **not yet adjudicated** (pending real human blinded execution)
- Stage B: **not run** (strictly conditional on a real Stage A pass)
- Scorecard status: calculator wiring verified; no real blinded inputs entered yet

## 4) What this supports

- A complete, reproducible execution harness for blinded adjacent transfer exists.
- The repository can now produce a public-safe record and separate private blinding materials without leaking assignment maps.

## 5) What this does not prove

- It does not prove a Stage A pass.
- It does not prove Stage B transfer.
- It does not prove unrestricted autonomy, unbounded RSI, or broad sovereign proof.

## Run sequence (honest execution)

1. Initialize scaffolding (if re-running fresh):
   ```bash
   python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/setup_blinded_adjacent_transfer_v1.py --force
   ```
2. Fill private-only files locally (outside git history).
3. Freeze private commitments:
   ```bash
   python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/generate_private_commitment_hashes.py --private-dir demos/adjacent_mandate_reuse_proof_real_v1/local_private_blinding_materials/results_blinded_adjacent_transfer_v1
   ```
4. Execute Stage A lane work under blinded kits and collect packets.
5. Fill scorecard CSVs in `scorecard_outputs/` from real adjudication data.
6. Run scorecard helper:
   ```bash
   python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/calculate_q2_scorecard.py --scorecard-dir demos/adjacent_mandate_reuse_proof_real_v1/results_blinded_adjacent_transfer_v1/scorecard_outputs
   ```
7. Record reviewer leakage checks in `leakage_check.csv` before reveal.
8. Lock scorecard and only then reveal blinded assignment map.
9. Run bundle completeness check:
   ```bash
   python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/validate_blinded_results_bundle.py
   ```

See `HUMAN_ACTION_REQUIRED.md` for unresolved role-separated steps.
""",
        encoding="utf-8",
    )

    (results_dir / "HUMAN_ACTION_REQUIRED.md").write_text(
        """# HUMAN_ACTION_REQUIRED

The following protocol-required steps remain human-only and are not automated here:

1. Assign real people to Sponsor, Blinding Officer, Package Custodian, Lane Operators, Reviewers, and Scorecard Custodian.
2. Keep Blinding Officer separate from reviewers and scoring.
3. Fill private answer keys and assignment maps in the local private path.
4. Conduct Stage A lane execution with real blinded operator kits.
5. Normalize packets and run 3 independent blinded reviewer adjudications.
6. Populate scorecard CSVs from real reviewer evidence.
7. Record reviewer leakage checks in `leakage_check.csv` before reveal.
8. Lock scorecard outputs and then reveal assignment map.
9. Decide Stage A pass/fail honestly from thresholds.
10. Run Stage B only if Stage A passed with real blinded reviewer data.

Until those steps complete, any pass/fail claim is out of bounds.
""",
        encoding="utf-8",
    )

    (results_dir / "summary_metrics.json").write_text(
        json.dumps(
            {
                "status": "operationalized_to_honest_human_boundary",
                "stage_a": {
                    "execution_state": "pending_real_blinded_human_execution",
                    "score_lock": "not_started",
                    "result": "undetermined",
                },
                "stage_b": {
                    "execution_state": "blocked_on_stage_a_real_pass",
                    "result": "not_run",
                },
                "demonstrated": [
                    "preregistration and environment freeze artifacts",
                    "public-safe output structure",
                    "private local-only blinding path",
                    "scorecard input and calculation wiring",
                ],
                "pending_human_execution": [
                    "role-separated assignment and blinding",
                    "stage_a lane execution and packet normalization",
                    "independent blinded adjudication",
                    "score lock and reveal",
                    "conditional stage_b execution",
                ],
                "simulated": [],
                "unproven": [
                    "stage_a pass criteria",
                    "stage_b cross-domain transfer",
                    "bounded recursive self-improvement claim",
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    (results_dir / "stage_a_scorecard.md").write_text(
        """# Stage A scorecard status

Status: **PENDING HUMAN BLINDED EXECUTION**

The scorecard computation path is wired:

- Inputs expected in `scorecard_outputs/run_costs.csv`
- Inputs expected in `scorecard_outputs/output_scoring.csv`
- Optional dependence evidence in `scorecard_outputs/package_dependence_ledger.csv`
- Compute helper: `../07_scripts/calculate_q2_scorecard.py`

No real blinded reviewer outputs have been entered yet in this result pack.
Therefore no Stage A pass/fail decision is recorded here.
""",
        encoding="utf-8",
    )
    (results_dir / "stage_b_scorecard.md").write_text(
        """# Stage B scorecard status

Status: **NOT RUN**

Stage B is conditional on a real Stage A pass with blinded reviewer adjudication.
Do not execute Stage B lanes or adjudication until Stage A thresholds are honestly satisfied.
""",
        encoding="utf-8",
    )

    (results_dir / "proof_docket_public.md").write_text(
        """# Public-Safe Proof Docket (Blinded Adjacent Transfer v1)

## Demonstrated

- Preregistration and environment freeze records are present.
- Public-safe packet separation and scorecard I/O wiring are present.
- Private blinding files are routed to a git-ignored local directory.

## Prepared but awaiting human execution

- Real blinded operator lane runs for Stage A.
- Reviewer packet normalization and independent reviewer adjudication.
- Stage A score lock and reveal process.
- Conditional Stage B freeze and execution.

## Simulated

- None in this public-safe results path.

## Unproven

- Stage A threshold pass under real blinded conditions.
- Stage B cross-domain transfer pass.
- Any claim beyond bounded protocol-correctness wedge evidence.
""",
        encoding="utf-8",
    )

    (results_dir / "governance_ruling_public.md").write_text(
        """# Governance Ruling (Public)

Ruling status: **DEFERRED — INSUFFICIENT BLINDED HUMAN ADJUDICATION DATA**

Reason:
- Required blinded reviewer adjudication artifacts are not yet complete.
- Stage A thresholds cannot be evaluated honestly without those artifacts.

Interim policy outcome:
- Publish this incomplete status now (publish regardless of outcome policy).
- Keep Stage B locked as conditional and unexecuted.
- Resume only when role-separated human execution is available.
""",
        encoding="utf-8",
    )

    for lane in ["blue", "gold"]:
        (results_dir / f"lane_{lane}_packet_public" / "README.md").write_text(
            f"# Lane {lane.title()} packet (public-safe)\n\n"
            "Stage-scoped normalized reviewer packets are stored under:\n\n"
            "- `stage_a/`\n"
            "- `stage_b/`\n",
            encoding="utf-8",
        )
        for stage in ["stage_a", "stage_b"]:
            (results_dir / f"lane_{lane}_packet_public" / stage / "README.md").write_text(
                "# Normalized blinded reviewer packet\n\n"
                "This packet path is reserved for normalized blinded reviewer artifacts.\n"
                "Do not include operator identity, package identity, explicit lane type labels, or private assignment metadata.\n",
                encoding="utf-8",
            )

    (results_dir / "scorecard_outputs" / "README.md").write_text(
        """# Scorecard outputs workspace

Populate these files from real blinded reviewer adjudication:

- `run_costs.csv`
- `output_scoring.csv`
- `package_dependence_ledger.csv`

Then run:

```bash
python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/calculate_q2_scorecard.py --scorecard-dir demos/adjacent_mandate_reuse_proof_real_v1/results_blinded_adjacent_transfer_v1/scorecard_outputs
```
""",
        encoding="utf-8",
    )

    (results_dir / "provenance_manifest.json").write_text(
        json.dumps(build_public_provenance(results_dir), indent=2) + "\n",
        encoding="utf-8",
    )

    write_csv(
        private_dir / "reviewer_identity_map.private.csv",
        ["reviewer_id", "legal_name_or_org", "contact", "role_constraints"],
        [["R1", "REPLACE", "REPLACE", "cannot_be_blinding_officer_or_scorecard_custodian"]],
    )

    private_answer = (
        "# Private answer key\n\n"
        "This file is private and must not be committed publicly.\n\n"
        "## Mandate scope\n- REPLACE\n\n"
        "## Accept criteria\n- REPLACE\n"
    )
    for name in ["answer_key_m1.private.md", "answer_key_m2.private.md", "answer_key_m3.private.md"]:
        (private_dir / name).write_text(private_answer, encoding="utf-8")

    kits_dir = private_dir / "kits"
    (kits_dir / "Kit Blue").mkdir(parents=True, exist_ok=True)
    (kits_dir / "Kit Gold").mkdir(parents=True, exist_ok=True)
    treatment_kit = args.treatment_kit or ("Kit Blue" if secrets.randbelow(2) == 0 else "Kit Gold")
    placebo_kit = "Kit Gold" if treatment_kit == "Kit Blue" else "Kit Blue"

    treatment_payloads = {
        "ontology.json": {
            "pack_name": "GovernanceValidationPack-v1",
            "source_scope": MANDATE_1_SCOPE,
            "entities": ["governance role", "challenge lifecycle", "evidence path", "settlement precondition"],
        },
        "query_bundle.json": {
            "queries": [
                "Trace authority checks before state transition.",
                "Enumerate challenge-policy negative paths and revert semantics.",
                "Locate settlement validation gates and invariant assumptions.",
            ]
        },
        "mechanism_library.json": {
            "mechanisms": [
                "state-transition guard matrix",
                "challenge escalation and deactivation integrity checklist",
                "cross-contract authority delegation review template",
            ]
        },
        "extraction_schema.json": {
            "required_fields": [
                "finding_id",
                "severity",
                "code_location",
                "proof_artifact",
                "negative_path_test",
                "proposed_fix",
            ]
        },
    }
    placebo_payloads = {
        "ontology.json": {
            "pack_name": "GenericProtocolReviewPlacebo-v1",
            "source_scope": ["generic protocol review guidance only"],
            "entities": ["role", "state", "input", "output"],
        },
        "query_bundle.json": {
            "queries": [
                "List observed assumptions.",
                "List possible edge cases.",
                "Capture open questions for reviewers.",
            ]
        },
        "mechanism_library.json": {"mechanisms": ["generic input validation checklist", "generic logging checklist"]},
        "extraction_schema.json": {
            "required_fields": ["finding_id", "severity", "code_location", "notes"]
        },
    }

    treatment_text = {
        "workflow_template.md": "# Workflow template (treatment)\n\n1. Map role authority boundaries.\n2. Execute negative-path test planning.\n3. Build evidence packet with repro steps.\n",
        "safety_routing_rules.md": "# Safety routing rules (treatment)\n\n- Block acceptance if authority checks are missing.\n- Block settlement claims without explicit validation proof.\n",
        "scoring_rubric.md": "# Scoring rubric (treatment)\n\nUse the Stage A rubric with explicit checks for governance/challenge semantics reuse.\n",
    }
    placebo_text = {
        "workflow_template.md": "# Workflow template (placebo)\n\n1. Read code.\n2. Record observations.\n3. Share summary.\n",
        "safety_routing_rules.md": "# Safety routing rules (placebo)\n\n- Keep safety comments explicit.\n- Escalate uncertainty to reviewers.\n",
        "scoring_rubric.md": "# Scoring rubric (placebo)\n\nApply generic review quality scoring only.\n",
    }

    for kit_name, json_payloads, text_payloads in [
        (treatment_kit, treatment_payloads, treatment_text),
        (placebo_kit, placebo_payloads, placebo_text),
    ]:
        kit_path = kits_dir / kit_name
        for filename in KIT_FILES:
            file_path = kit_path / filename
            if filename.endswith(".json"):
                file_path.write_text(
                    json.dumps(json_payloads[filename], indent=2) + "\n",
                    encoding="utf-8",
                )
            else:
                file_path.write_text(text_payloads[filename], encoding="utf-8")

    write_csv(
        private_dir / "blinded_assignment_map.private.csv",
        ["artifact_set", "blinded_lane_id", "actual_lane", "kit_variant", "revealed_after_score_lock"],
        [
            ["stage_a_mandate_2", "Lane Blue", "Lane Operator A", treatment_kit, "false"],
            ["stage_a_mandate_2", "Lane Gold", "Lane Operator B", placebo_kit, "false"],
            ["stage_b_mandate_3", "Lane Blue", "REPLACE", "REPLACE", "false"],
            ["stage_b_mandate_3", "Lane Gold", "REPLACE", "REPLACE", "false"],
        ],
    )

    (private_dir / "private_commitment_hashes.txt").write_text(
        "# Run 07_scripts/generate_private_commitment_hashes.py after private files are finalized.\n",
        encoding="utf-8",
    )

    print(f"Initialized public-safe results scaffold: {results_dir}")
    print(f"Initialized private local-only scaffold: {private_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
