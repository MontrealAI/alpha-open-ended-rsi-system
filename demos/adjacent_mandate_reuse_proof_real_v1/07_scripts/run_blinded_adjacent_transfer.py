#!/usr/bin/env python3
"""Deterministic orchestration for blinded adjacent-transfer experiment control."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACK_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACK_ROOT.parents[1]
RESULTS_DIR = PACK_ROOT / "results_blinded_adjacent_transfer_v1"
PUBLIC_DIR = RESULTS_DIR / "public"
PRIVATE_DIR = RESULTS_DIR / "private_local_only"
KITS_DIR = RESULTS_DIR / "kits"
SCORECARD_OUT_DIR = RESULTS_DIR / "scorecard_outputs"
SCRIPTS_DIR = RESULTS_DIR / "scripts"
FORCE_RESET_PREPARE = False

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

KIT_FILENAMES = [
    "ontology.json",
    "query_bundle.json",
    "workflow_template.md",
    "mechanism_library.json",
    "safety_routing_rules.md",
    "scoring_rubric.md",
    "extraction_schema.json",
]

STATUS_VALUES = {
    "READY_FOR_HUMAN_EXECUTION",
    "BLOCKED_MISSING_SCOPE_FILE",
    "BLOCKED_MISSING_SCORECARD_HELPER",
    "BLOCKED_PRIVATE_FILES_COMMITTED",
    "BLOCKED_KIT_MISMATCH",
    "STAGE_A_COMPLETED_PENDING_REVEAL",
    "STAGE_A_PASSED",
    "STAGE_A_FAILED",
    "STAGE_B_SCAFFOLDED",
    "STAGE_B_COMPLETED",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=str(cwd or REPO_ROOT), text=True).strip()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git_repo_state() -> dict[str, str]:
    return {
        "repo_sha": _run(["git", "rev-parse", "HEAD"]),
        "branch": _run(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
    }


def _scope_hashes() -> dict[str, str]:
    out: dict[str, str] = {}
    for rel in MANDATE_1_SCOPE + MANDATE_2_SCOPE + MANDATE_3_SCOPE:
        p = REPO_ROOT / rel
        if not p.exists():
            raise FileNotFoundError(f"Missing required scope file: {rel}")
        out[rel] = _sha256_file(p)
    return out


def _ensure_dirs() -> None:
    for d in [RESULTS_DIR, PUBLIC_DIR, PRIVATE_DIR, KITS_DIR, SCORECARD_OUT_DIR, SCRIPTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    (PUBLIC_DIR / "lane_blue_packet_public").mkdir(parents=True, exist_ok=True)
    (PUBLIC_DIR / "lane_gold_packet_public").mkdir(parents=True, exist_ok=True)
    (KITS_DIR / "kit_blue").mkdir(parents=True, exist_ok=True)
    (KITS_DIR / "kit_gold").mkdir(parents=True, exist_ok=True)


def _create_private_templates() -> None:
    _write_text(
        PRIVATE_DIR / "README.md",
        "# Private local-only materials\n\n"
        "Use this directory for local-only blinded assignment and identity mapping files.\n"
        "Do not commit filled private files.\n",
    )
    _write_text(
        PRIVATE_DIR / ".gitignore",
        "*.private.md\n*.private.csv\n*.private.txt\nprivate_commitment_hashes.txt\n"
        "!*.private.template.md\n!*.private.template.csv\n!*.private.template.txt\n!private_commitment_hashes.template.txt\n",
    )
    for idx in [1, 2, 3]:
        _write_text(
            PRIVATE_DIR / f"answer_key_m{idx}.private.template.md",
            f"# Answer Key Mandate {idx} (PRIVATE TEMPLATE)\n\n"
            "Status: TEMPLATE_ONLY\n"
            "Fill locally only after human adjudication prerequisites are met.\n",
        )
    _write_text(
        PRIVATE_DIR / "blinded_assignment_map.private.template.csv",
        "seed,treatment_kit,control_kit,lane_blue_kit,lane_gold_kit,blinding_officer_signoff\n"
        "BLINDING_OFFICER_REQUIRED,BLINDING_OFFICER_REQUIRED,BLINDING_OFFICER_REQUIRED,BLINDING_OFFICER_REQUIRED,BLINDING_OFFICER_REQUIRED,pending\n",
    )
    _write_text(
        PRIVATE_DIR / "reviewer_identity_map.private.template.csv",
        "reviewer_label,real_identity,role_conflict_check\n"
        "Reviewer 1,REPLACE_LOCAL_ONLY,pending\n"
        "Reviewer 2,REPLACE_LOCAL_ONLY,pending\n"
        "Reviewer 3,REPLACE_LOCAL_ONLY,pending\n",
    )
    _write_text(
        PRIVATE_DIR / "private_commitment_hashes.template.txt",
        "# TEMPLATE\n"
        "Generate private_commitment_hashes.txt via commit-private once local private files are filled.\n",
    )


def _create_packet_templates() -> None:
    for lane in ["lane_blue_packet_public", "lane_gold_packet_public"]:
        d = PUBLIC_DIR / lane
        for filename in [
            "findings.md",
            "tests_or_harnesses.md",
            "evidence_packet.md",
            "reviewer_form.md",
            "leakage_check.md",
        ]:
            path = d / filename
            if not path.exists():
                _write_text(
                    path,
                    f"# {filename}\n\nAWAITING_LANE_OPERATOR_OUTPUT\n",
                )


def _create_scorecard_templates() -> None:
    _write_text(
        SCORECARD_OUT_DIR / "README.md",
        "# Scorecard outputs\n\n"
        "Populate run_costs.csv, output_scoring.csv, and package_dependence_ledger.csv with real locked inputs.\n"
        "Do not fabricate human review outputs.\n",
    )
    for stem in ["run_costs", "output_scoring", "package_dependence_ledger"]:
        src = PACK_ROOT / "04_scorecard" / f"{stem}.template.csv"
        dst = SCORECARD_OUT_DIR / f"{stem}.csv"
        if src.exists() and not dst.exists():
            shutil.copyfile(src, dst)


def _create_docs_skeletons() -> None:
    _write_text(
        RESULTS_DIR / "README.md",
        "# Blinded Adjacent Transfer Results v1\n\n"
        "This folder contains the run-ready blinded adjacent-transfer experiment harness and handoff materials.\n"
        "It does not imply completed human-blinded adjudication.\n",
    )
    _write_text(
        RESULTS_DIR / "RUNBOOK.md",
        "# Runbook\n\n"
        "1. `prepare`\n2. `freeze-package`\n3. `build-kits`\n4. `validate-readiness`\n"
        "5. Human lane execution and reviewer completion\n6. `lock-score`\n7. `reveal`\n8. `assemble-public-docket`\n",
    )
    _write_text(
        RESULTS_DIR / "HUMAN_ACTION_REQUIRED.md",
        "# HUMAN_ACTION_REQUIRED\n\n"
        "Status: READY_FOR_HUMAN_EXECUTION\n\n"
        "Required roles: Sponsor, Blinding Officer, Package Custodian, Lane Operator A, Lane Operator B, "
        "Reviewer 1, Reviewer 2, Reviewer 3, Scorecard Custodian.\n"
        "Role-separation state: HUMAN_ROLE_SEPARATION_PENDING.\n",
    )
    _write_text(
        RESULTS_DIR / "PUBLIC_STATUS.md",
        "# Public Status\n\n"
        "The repository now contains a run-ready blinded adjacent-transfer experiment harness for testing whether "
        "GovernanceValidationPack-v1 improves the next adjacent protocol-correctness mandate under blinded conditions.\n\n"
        "This repository contains the run-ready blinded experiment harness and handoff materials. "
        "It does not yet contain completed human-blinded adjudication.\n",
    )
    _write_text(
        SCRIPTS_DIR / "README.md",
        "# Scripts\n\n"
        "Primary orchestration: `../07_scripts/run_blinded_adjacent_transfer.py`.\n",
    )


def _write_stage_b_scaffold() -> None:
    stage_b = {
        "stage_b_package_id": "ProtocolCorrectnessLineage-v1",
        "status": "STAGE_B_PENDING_STAGE_A_PASS",
        "scope": MANDATE_3_SCOPE + ["backend/tests/ (directly relevant files only)"],
        "minimum_pass_criteria": {
            "no_safety_regression": True,
            "positive_aoy_uplift": True,
            "positive_speed_uplift": True,
            "evidence_completeness_uplift_min_pct": 10,
            "package_dependence_min_pct": 20,
            "operator_intervention_reduction_min_pct": 25,
            "frontier_width_domain_increase_min": 1,
        },
        "note": "Stage B is scaffolded only and must not run until Stage A passes with real blinded reviewer data.",
    }
    _write_json(PUBLIC_DIR / "summary_metrics.json", {
        "status": "READY_FOR_HUMAN_EXECUTION",
        "stage_a": "PENDING_HUMAN_INPUT",
        "stage_b": stage_b,
        "demonstrated": [
            "run-ready blinded adjacent-transfer harness",
            "deterministic preregistration/freeze/kit manifest generation",
        ],
        "pending_human_execution": [
            "blinded lane outputs",
            "reviewer adjudication",
            "score lock from real filled scorecard inputs",
            "reveal sign-off by blinding officer",
        ],
        "simulated": ["template scorecard inputs only"],
        "unproven": [
            "Stage A pass/fail until real blinded reviewer data is present",
            "Stage B transfer outcomes",
        ],
    })


def _update_experiment_status(status: str, reasons: list[str] | None = None) -> None:
    if status not in STATUS_VALUES:
        raise ValueError(f"Unsupported status: {status}")
    if status in {"STAGE_A_PASSED", "STAGE_B_SCAFFOLDED"}:
        stage_b_status = "STAGE_B_SCAFFOLDED"
    elif status == "STAGE_B_COMPLETED":
        stage_b_status = "STAGE_B_COMPLETED"
    else:
        stage_b_status = "STAGE_B_PENDING_STAGE_A_PASS"
    payload = {
        "status": status,
        "timestamp_utc": _now(),
        "reasons": reasons or [],
        "stage_b_status": stage_b_status,
        "role_separation": "HUMAN_ROLE_SEPARATION_PENDING",
    }
    _write_json(RESULTS_DIR / "experiment_status.json", payload)


def cmd_prepare() -> int:
    if RESULTS_DIR.exists() and not FORCE_RESET_PREPARE:
        status_path = RESULTS_DIR / "experiment_status.json"
        if status_path.exists():
            existing_status = str(_read_json(status_path).get("status", "")).strip()
            advanced_states = {
                "STAGE_A_COMPLETED_PENDING_REVEAL",
                "STAGE_A_PASSED",
                "STAGE_A_FAILED",
                "STAGE_B_SCAFFOLDED",
                "STAGE_B_COMPLETED",
            }
            if existing_status in advanced_states:
                raise SystemExit(
                    "prepare blocked: existing run is already advanced. "
                    "Use --force-reset to intentionally reinitialize artifacts."
                )

    _ensure_dirs()
    if FORCE_RESET_PREPARE:
        for lane_dir in [PUBLIC_DIR / "lane_blue_packet_public", PUBLIC_DIR / "lane_gold_packet_public"]:
            if lane_dir.exists():
                shutil.rmtree(lane_dir)
                lane_dir.mkdir(parents=True, exist_ok=True)
    _create_docs_skeletons()
    _create_private_templates()
    _create_packet_templates()
    _create_scorecard_templates()

    repo_state = _git_repo_state()
    env_lock = {
        "timestamp_generated": _now(),
        "python_version": sys.version.split()[0],
        "os": platform.platform(),
        "repo_sha": repo_state["repo_sha"],
        "branch": repo_state["branch"],
        "scope_hashes": _scope_hashes(),
        "allowed_human_interventions": [
            "budget approval",
            "policy clarification",
            "exception handling only",
        ],
    }

    prereg = {
        "experiment_id": "adjacent-mandate-reuse-real-v1-blinded-adjacent-transfer",
        "timestamp_generated": _now(),
        "repo_sha": repo_state["repo_sha"],
        "branch": repo_state["branch"],
        "environment_lock": env_lock,
        "stage_a_mandate_1_scope": MANDATE_1_SCOPE,
        "stage_a_mandate_2_scope": MANDATE_2_SCOPE,
        "stage_b_mandate_3_scope": MANDATE_3_SCOPE,
        "out_of_scope_issue_types": [
            "architecture redesign outside scoped mandates",
            "claims widening beyond bounded release posture",
            "non-deterministic changes unrelated to experiment protocol",
        ],
        "allowed_tools": ["local shell", "python3", "repo scripts"],
        "allowed_commands": [
            "python3 07_scripts/run_blinded_adjacent_transfer.py <command>",
            "python3 07_scripts/calculate_q2_scorecard.py --scorecard-dir results_blinded_adjacent_transfer_v1/scorecard_outputs",
        ],
        "stage_a_budget_per_lane": {
            "wall_clock_budget_minutes": 180,
            "machine_class": "same",
            "repo_sha": repo_state["repo_sha"],
            "local_tools": "same",
            "network": "disallowed",
            "max_test_runs": "same_predeclared_limit",
            "max_command_count": "same_predeclared_limit",
            "allowed_repo_docs": "same_predeclared_set",
            "compute_budget": "same_machine_class",
        },
        "stage_b_budget_per_lane": "conditional_same_as_stage_a_unless_symmetrically_documented",
        "max_command_count": "set by sponsor before lane start",
        "max_test_runs": "set by sponsor before lane start",
        "reviewer_rubric_reference": [
            "03_review/reviewer_form_mandate_2_control.template.md",
            "03_review/reviewer_form_mandate_2_treatment.template.md",
            "03_review/adjudication_form.template.md",
        ],
        "score_thresholds": {
            "aoy_uplift_min_pct": 35,
            "time_to_first_accepted_output_faster_min_pct": 30,
            "repair_rework_reduction_min_pct": 40,
            "evidence_completeness_uplift_min_pct": 20,
            "safety_regression_allowed": False,
            "package_dependence_min_pct": 30,
        },
        "intervention_policy": "All interventions logged with lane symmetry constraints.",
        "publication_rule": "publish regardless of pass/fail",
        "stopping_rule": "Stop at READY_FOR_HUMAN_EXECUTION if required human inputs are missing.",
        "claim_boundary": "No Stage A pass claim without real blinded reviewer data and locked scorecard inputs.",
    }

    _write_json(PUBLIC_DIR / "preregistration_public.json", prereg)
    _write_json(RESULTS_DIR / "provenance_manifest.json", {
        "generated_at": _now(),
        "branch": repo_state["branch"],
        "result_path": str(RESULTS_DIR.relative_to(REPO_ROOT)),
        "notes": "Public-safe provenance only. Private mappings remain local. Re-run prepare/freeze/build to refresh branch-local provenance pointers.",
    })
    _write_stage_b_scaffold()
    _update_experiment_status("READY_FOR_HUMAN_EXECUTION")
    return 0


def _package_source_dir() -> Path:
    return RESULTS_DIR / "scripts" / "GovernanceValidationPack-v1_source"


def _placebo_source_dir() -> Path:
    return RESULTS_DIR / "scripts" / "PlaceboProtocolReviewPack-v1_source"


def _ensure_package_sources() -> tuple[Path, Path, bool]:
    """Return (real_src, placebo_src, used_pending_scaffold)."""
    real = _package_source_dir()
    placebo = _placebo_source_dir()
    real.mkdir(parents=True, exist_ok=True)
    placebo.mkdir(parents=True, exist_ok=True)

    used_pending_scaffold = False
    for name in KIT_FILENAMES:
        rp = real / name
        pp = placebo / name
        if not rp.exists():
            used_pending_scaffold = True
            content = {
                "file": name,
                "status": "PENDING_MANDATE_1_HUMAN_ADJUDICATION",
                "package": "GovernanceValidationPack-v1",
                "note": "Transparent scaffold. No reviewer-approved mandate-1 content committed yet.",
            }
            if name.endswith(".json"):
                _write_json(rp, content)
            else:
                _write_text(rp, "# PENDING_MANDATE_1_HUMAN_ADJUDICATION\n\n"
                                "Transparent scaffold placeholder for GovernanceValidationPack-v1.\n")
        if not pp.exists():
            if name.endswith(".json"):
                _write_json(pp, {
                    "file": name,
                    "package": "PlaceboProtocolReviewPack-v1",
                    "status": "PLACEBO_GENERIC_CONTENT",
                    "description": "Generic protocol-review placeholder with no Mandate 1 derived mechanisms.",
                })
            else:
                _write_text(pp, "# PLACEBO_GENERIC_CONTENT\n\nGeneric protocol-review placeholder.\n")
    return real, placebo, used_pending_scaffold


def _is_pending_real_package_file(path: Path) -> bool:
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    if "PENDING_MANDATE_1_HUMAN_ADJUDICATION" in text:
        return True
    if path.suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return True
        status = str(data.get("status", "")).strip().upper()
        if status == "PENDING_MANDATE_1_HUMAN_ADJUDICATION":
            return True
    return False


def _materialization_status(real_src: Path) -> str:
    for name in KIT_FILENAMES:
        if _is_pending_real_package_file(real_src / name):
            return "PENDING_MANDATE_1_HUMAN_ADJUDICATION"
    return "SOURCE_PRESENT"


def cmd_freeze_package() -> int:
    _ensure_dirs()
    real_src, _, used_pending = _ensure_package_sources()
    file_hashes = {name: _sha256_file(real_src / name) for name in KIT_FILENAMES}
    aggregate = _sha256_text("\n".join(file_hashes[name] for name in sorted(file_hashes)))
    materialization_status = _materialization_status(real_src)

    freeze = {
        "package_id": "GovernanceValidationPack-v1",
        "version": "v1",
        "source_mandate": "Mandate 1 (governance/dispute correctness)",
        "included_files": KIT_FILENAMES,
        "file_sha256": file_hashes,
        "aggregate_package_hash": aggregate,
        "parentage_note": "Mandate 1 freeze lineage input to Stage A adjacent transfer.",
        "lineage_note": "Frozen package intended for blinded kit construction only.",
        "freeze_timestamp": _now(),
        "no_edit_attestation": "No edits permitted after freeze without new freeze event.",
        "human_adjudication_status": "PENDING_HUMAN_ADJUDICATION",
        "materialization_status": materialization_status,
        "materialization_determination": {
            "used_pending_scaffold_in_this_run": used_pending,
            "content_scan_result": materialization_status,
        },
    }
    _write_json(PUBLIC_DIR / "package_freeze_public.json", freeze)
    return 0


def _copy_kit(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in KIT_FILENAMES:
        shutil.copyfile(src / name, dst / name)


def _pair_integrity_digest(blue_path: Path, gold_path: Path) -> str:
    pair = sorted([_sha256_file(blue_path), _sha256_file(gold_path)])
    return _sha256_text("::".join(pair))


def _assignment_map_path() -> Path:
    return PRIVATE_DIR / "blinded_assignment_map.private.csv"


def _resolve_private_kit_assignment() -> dict[str, str] | None:
    """Read private local assignment map if present."""
    path = _assignment_map_path()
    if not path.exists():
        return None
    rows = _read_csv_rows(path)
    if not rows:
        return None
    row = rows[0]
    treatment_kit = (row.get("treatment_kit") or "").strip().lower()
    control_kit = (row.get("control_kit") or "").strip().lower()
    if "blinding_officer_required" in f"{treatment_kit} {control_kit}":
        return None
    allowed = {"kit_blue", "kit_gold"}
    if treatment_kit not in allowed or control_kit not in allowed or treatment_kit == control_kit:
        raise SystemExit(
            "Invalid private assignment map. Expected distinct treatment_kit/control_kit values in {kit_blue, kit_gold}."
        )
    return {"treatment_kit": treatment_kit, "control_kit": control_kit}


def _write_blinding_required_kit(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in KIT_FILENAMES:
        out = dst / name
        if name.endswith(".json"):
            _write_json(out, {
                "status": "BLINDING_OFFICER_REQUIRED",
                "file": name,
                "note": "Run build-kits locally with filled private assignment map to materialize control/treatment kits.",
            })
        else:
            _write_text(
                out,
                "# BLINDING_OFFICER_REQUIRED\n\n"
                "Run build-kits locally with filled private assignment map to materialize control/treatment kits.\n",
            )


def cmd_build_kits() -> int:
    _ensure_dirs()
    real_src, placebo_src, _ = _ensure_package_sources()
    assignment = _resolve_private_kit_assignment()

    if assignment is None:
        _write_blinding_required_kit(KITS_DIR / "kit_blue")
        _write_blinding_required_kit(KITS_DIR / "kit_gold")
    else:
        treatment_dst = KITS_DIR / assignment["treatment_kit"]
        control_dst = KITS_DIR / assignment["control_kit"]
        _copy_kit(real_src, treatment_dst)
        _copy_kit(placebo_src, control_dst)

    parity = {}
    for filename in KIT_FILENAMES:
        blue = KITS_DIR / "kit_blue" / filename
        gold = KITS_DIR / "kit_gold" / filename
        parity[filename] = {
            "blue_exists": blue.exists(),
            "gold_exists": gold.exists(),
            "same_filename": blue.name == gold.name,
            "blue_sha256": "BLINDING_OFFICER_REQUIRED",
            "gold_sha256": "BLINDING_OFFICER_REQUIRED",
            "pair_integrity_sha256": _pair_integrity_digest(blue, gold),
            "surface_form_parity": blue.suffix == gold.suffix,
        }

    _write_json(PUBLIC_DIR / "kit_manifest_public.json", {
        "generated_at": _now(),
        "kit_labels": ["kit_blue", "kit_gold"],
        "filenames": KIT_FILENAMES,
        "parity_checks": parity,
        "assignment_status": "BLINDING_OFFICER_REQUIRED" if assignment is None else "ASSIGNED_PRIVATE_LOCAL_ONLY",
        "note": "Manifest does not reveal which lane received treatment package and suppresses hash-linking until private assignment exists.",
    })
    return 0


def cmd_commit_private() -> int:
    _ensure_dirs()
    _create_private_templates()
    local_candidates = [
        PRIVATE_DIR / "answer_key_m1.private.md",
        PRIVATE_DIR / "answer_key_m2.private.md",
        PRIVATE_DIR / "answer_key_m3.private.md",
        PRIVATE_DIR / "blinded_assignment_map.private.csv",
        PRIVATE_DIR / "reviewer_identity_map.private.csv",
    ]
    existing = [p for p in local_candidates if p.exists()]
    lines = [f"timestamp_utc: {_now()}"]
    for p in existing:
        lines.append(f"{_sha256_file(p)}  {p.name}")
    if not existing:
        lines.append("NO_FILLED_PRIVATE_FILES_FOUND")

    _write_text(PRIVATE_DIR / "private_commitment_hashes.txt", "\n".join(lines) + "\n")
    _write_text(PUBLIC_DIR / "private_commitment_hashes_public.txt", "\n".join(lines[:1] + ["PRIVATE_HASHES_RECORDED_LOCALLY"]) + "\n")
    return 0


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _is_template_like_csv(path: Path) -> bool:
    rows = _read_csv_rows(path)
    if not rows:
        return True
    blob = "\n".join(",".join((v or "") for v in row.values()) for row in rows).lower()
    return "replace" in blob or "template" in blob


def _packet_files_completed(packet_dir: Path) -> bool:
    required = [
        "findings.md",
        "tests_or_harnesses.md",
        "evidence_packet.md",
        "reviewer_form.md",
        "leakage_check.md",
    ]
    for name in required:
        p = packet_dir / name
        if not p.exists():
            return False
        text = p.read_text(encoding="utf-8")
        if "AWAITING_LANE_OPERATOR_OUTPUT" in text:
            return False
    return True


def _reviewer_packets_completed() -> bool:
    return _packet_files_completed(PUBLIC_DIR / "lane_blue_packet_public") and _packet_files_completed(
        PUBLIC_DIR / "lane_gold_packet_public"
    )


def cmd_lock_score() -> int:
    _ensure_dirs()
    run_costs = SCORECARD_OUT_DIR / "run_costs.csv"
    output_scoring = SCORECARD_OUT_DIR / "output_scoring.csv"
    package_dep = SCORECARD_OUT_DIR / "package_dependence_ledger.csv"
    required = [run_costs, output_scoring, package_dep]

    if any((not p.exists()) or _is_template_like_csv(p) for p in required) or not _reviewer_packets_completed():
        _write_json(PUBLIC_DIR / "summary_metrics.json", {
            "status": "SCORE_LOCK_PENDING_HUMAN_INPUT",
            "timestamp": _now(),
            "note": "Score lock requires real filled CSV inputs and completed blinded reviewer packet artifacts.",
            "demonstrated": [
                "run-ready blinded adjacent-transfer harness",
                "package freeze and kit-building pipeline",
            ],
            "pending_human_execution": [
                "real blinded lane outputs",
                "real blinded reviewer adjudication",
                "filled scorecard CSV lock inputs",
            ],
            "simulated": ["template scorecard files"],
            "unproven": ["Stage A pass/fail", "Stage B outcomes"],
        })
        return 0

    calc = PACK_ROOT / "07_scripts" / "calculate_q2_scorecard.py"
    if not calc.exists():
        raise FileNotFoundError("Missing calculate_q2_scorecard.py")

    subprocess.check_call([
        sys.executable,
        str(calc),
        "--scorecard-dir",
        str(SCORECARD_OUT_DIR),
    ])
    summary = _read_json(SCORECARD_OUT_DIR / "out" / "summary.json")

    _write_json(PUBLIC_DIR / "summary_metrics.json", {
        "status": "STAGE_A_COMPLETED_PENDING_REVEAL",
        "timestamp": _now(),
        "scorecard": summary,
        "demonstrated": ["scorecard lock from non-template inputs"],
        "pending_human_execution": ["blinding officer reveal confirmation"],
        "simulated": [],
        "unproven": ["Stage B outcomes"],
    })
    _update_experiment_status("STAGE_A_COMPLETED_PENDING_REVEAL")
    return 0


def cmd_reveal() -> int:
    _ensure_dirs()
    summary_path = PUBLIC_DIR / "summary_metrics.json"
    assignment_map = PRIVATE_DIR / "blinded_assignment_map.private.csv"
    reveal_confirm = PRIVATE_DIR / "reveal_confirmation.private.txt"
    if not summary_path.exists():
        raise SystemExit("Reveal blocked: lock-score has not produced summary_metrics.json")

    summary = _read_json(summary_path)
    if summary.get("status") != "STAGE_A_COMPLETED_PENDING_REVEAL":
        raise SystemExit("Reveal blocked: Stage A is not in completed-pending-reveal state")
    if not assignment_map.exists():
        raise SystemExit("Reveal blocked: private assignment map missing")
    if _resolve_private_kit_assignment() is None:
        raise SystemExit(
            "Reveal blocked: private assignment map is unresolved (BLINDING_OFFICER_REQUIRED or invalid)."
        )
    if not reveal_confirm.exists() or "BLINDING_OFFICER_CONFIRMED" not in reveal_confirm.read_text(encoding="utf-8"):
        raise SystemExit("Reveal blocked: missing blinding officer confirmation")

    score = summary.get("scorecard", {})
    pass_flags = score.get("pass_flags", {})
    if not pass_flags:
        classification = "PENDING_HUMAN_INPUT"
        status = "READY_FOR_HUMAN_EXECUTION"
    elif all(bool(v) for v in pass_flags.values()):
        classification = "PASSED"
        status = "STAGE_A_PASSED"
    else:
        classification = "FAILED"
        status = "STAGE_A_FAILED"

    summary["stage_a_classification"] = classification
    summary["status"] = status
    summary["reveal_timestamp"] = _now()
    summary["stage_b_status"] = "STAGE_B_PENDING_STAGE_A_PASS" if classification != "PASSED" else "STAGE_B_SCAFFOLDED"
    _write_json(summary_path, summary)
    _update_experiment_status(status)
    return 0


def cmd_normalize_packets() -> int:
    _ensure_dirs()
    _create_packet_templates()
    return 0


def cmd_assemble_public_docket() -> int:
    _ensure_dirs()
    _write_text(
        PUBLIC_DIR / "proof_docket_public.md",
        "# Proof Docket (Public)\n\n"
        "## 1. What was frozen\n"
        "GovernanceValidationPack-v1 file set was frozen with file-level and aggregate SHA-256 commitments.\n\n"
        "## 2. What was blinded\n"
        "Lane Blue and Lane Gold packet labels, assignment map, and reviewer identity mapping are blinded/private.\n\n"
        "## 3. What passed / failed\n"
        "Stage A status remains pending unless real blinded reviewer packets and locked scorecard inputs exist.\n\n"
        "## 4. What this supports\n"
        "Run-ready blinded adjacent-transfer experiment harness and public-safe handoff workflow.\n\n"
        "## 5. What this does not prove\n"
        "No completed blinded adjudication is claimed in this committed state.\n\n"
        "This repository contains the run-ready blinded experiment harness and handoff materials. "
        "It does not yet contain completed human-blinded adjudication.\n",
    )
    _write_text(
        PUBLIC_DIR / "governance_ruling_public.md",
        "# Governance Ruling (Public)\n\n"
        "## 1. What was frozen\nGovernanceValidationPack-v1 freeze manifest and hashes are recorded.\n\n"
        "## 2. What was blinded\nTreatment/control assignment is withheld pending private reveal controls.\n\n"
        "## 3. What passed / failed\nNo pass/fail ruling until human-blinded review and score-lock evidence are complete.\n\n"
        "## 4. What this supports\nControlled, auditable blinded protocol execution path.\n\n"
        "## 5. What this does not prove\nNo unrestricted autonomy or broad external proof is established.\n",
    )
    return 0


def _files_exist(paths: list[Path]) -> list[str]:
    return [str(p.relative_to(RESULTS_DIR)) for p in paths if not p.exists()]


def cmd_validate_readiness() -> int:
    _ensure_dirs()
    reasons: list[str] = []

    for rel in MANDATE_1_SCOPE + MANDATE_2_SCOPE + MANDATE_3_SCOPE:
        if not (REPO_ROOT / rel).exists():
            reasons.append(f"missing scope file: {rel}")

    prereg_path = PUBLIC_DIR / "preregistration_public.json"
    if prereg_path.exists():
        prereg = _read_json(prereg_path)
        locked_scope_hashes = (
            prereg.get("environment_lock", {}).get("scope_hashes", {})
            if isinstance(prereg.get("environment_lock", {}), dict)
            else {}
        )
        current_scope_hashes = _scope_hashes()
        for rel, digest in current_scope_hashes.items():
            locked = locked_scope_hashes.get(rel)
            if locked and locked != digest:
                reasons.append(f"scope hash mismatch: {rel}")

    if not (PACK_ROOT / "07_scripts" / "calculate_q2_scorecard.py").exists():
        _update_experiment_status("BLOCKED_MISSING_SCORECARD_HELPER", ["calculate_q2_scorecard.py missing"])
        return 1

    required = [
        PUBLIC_DIR / "preregistration_public.json",
        PUBLIC_DIR / "package_freeze_public.json",
        PUBLIC_DIR / "kit_manifest_public.json",
        PUBLIC_DIR / "lane_blue_packet_public",
        PUBLIC_DIR / "lane_gold_packet_public",
        PRIVATE_DIR / "answer_key_m1.private.template.md",
        PRIVATE_DIR / "answer_key_m2.private.template.md",
        PRIVATE_DIR / "answer_key_m3.private.template.md",
        PRIVATE_DIR / "blinded_assignment_map.private.template.csv",
        PRIVATE_DIR / "reviewer_identity_map.private.template.csv",
        SCORECARD_OUT_DIR / "run_costs.csv",
        SCORECARD_OUT_DIR / "output_scoring.csv",
        SCORECARD_OUT_DIR / "package_dependence_ledger.csv",
    ]
    missing_required = _files_exist(required)
    reasons.extend([f"missing required artifact: {x}" for x in missing_required])

    blue_files = sorted(p.name for p in (KITS_DIR / "kit_blue").glob("*") if p.is_file())
    gold_files = sorted(p.name for p in (KITS_DIR / "kit_gold").glob("*") if p.is_file())
    if blue_files != gold_files or blue_files != sorted(KIT_FILENAMES):
        _update_experiment_status("BLOCKED_KIT_MISMATCH", ["kit_blue and kit_gold filenames do not match required set"])
        return 1
    kit_manifest_path = PUBLIC_DIR / "kit_manifest_public.json"
    if kit_manifest_path.exists():
        kit_manifest = _read_json(kit_manifest_path)
        parity_checks = kit_manifest.get("parity_checks", {}) if isinstance(kit_manifest, dict) else {}
        for filename in KIT_FILENAMES:
            blue = KITS_DIR / "kit_blue" / filename
            gold = KITS_DIR / "kit_gold" / filename
            recorded = (
                parity_checks.get(filename, {}).get("pair_integrity_sha256")
                if isinstance(parity_checks.get(filename, {}), dict)
                else None
            )
            current = _pair_integrity_digest(blue, gold)
            if not recorded or recorded != current:
                _update_experiment_status(
                    "BLOCKED_KIT_MISMATCH",
                    [f"kit pair integrity mismatch: {filename}"],
                )
                return 1

    tracked_private_patterns = [
        "**/*.private.md",
        "**/*.private.csv",
        "**/*.private.txt",
    ]
    committed_private: list[str] = []
    for pat in tracked_private_patterns:
        out = _run(["git", "ls-files", pat], cwd=REPO_ROOT)
        for line in [x.strip() for x in out.splitlines() if x.strip()]:
            if "template" not in line:
                committed_private.append(line)
    if committed_private:
        _update_experiment_status("BLOCKED_PRIVATE_FILES_COMMITTED", committed_private)
        return 1

    if prereg_path.exists():
        prereg = _read_json(prereg_path)
        if "claim_boundary" not in prereg:
            reasons.append("prereg missing claim_boundary")
        if "conditional" not in json.dumps(prereg.get("stage_b_budget_per_lane", "")).lower():
            reasons.append("stage b conditional marker missing")

    if reasons:
        if any("scope file" in r for r in reasons):
            _update_experiment_status("BLOCKED_MISSING_SCOPE_FILE", reasons)
            return 1
        _update_experiment_status("BLOCKED_KIT_MISMATCH", reasons)
        return 1
    _update_experiment_status("READY_FOR_HUMAN_EXECUTION", reasons)
    return 0


def cmd_assert() -> int:
    required_files = [
        RESULTS_DIR / "README.md",
        RESULTS_DIR / "RUNBOOK.md",
        RESULTS_DIR / "HUMAN_ACTION_REQUIRED.md",
        RESULTS_DIR / "PUBLIC_STATUS.md",
        RESULTS_DIR / "provenance_manifest.json",
        RESULTS_DIR / "experiment_status.json",
        PUBLIC_DIR / "preregistration_public.json",
        PUBLIC_DIR / "package_freeze_public.json",
        PUBLIC_DIR / "kit_manifest_public.json",
        PRIVATE_DIR / "README.md",
        PRIVATE_DIR / ".gitignore",
        KITS_DIR / "kit_blue",
        KITS_DIR / "kit_gold",
    ]
    missing = _files_exist(required_files)
    if missing:
        raise SystemExit("assert failed, missing:\n- " + "\n- ".join(missing))

    blue_files = sorted([p.name for p in (KITS_DIR / "kit_blue").glob("*") if p.is_file()])
    gold_files = sorted([p.name for p in (KITS_DIR / "kit_gold").glob("*") if p.is_file()])
    expected_files = sorted(KIT_FILENAMES)
    if blue_files != gold_files:
        raise SystemExit("assert failed: blue/gold kit filenames mismatch")
    if blue_files != expected_files:
        raise SystemExit(
            "assert failed: kits missing required files. "
            f"expected={expected_files} blue={blue_files} gold={gold_files}"
        )

    status = _read_json(RESULTS_DIR / "experiment_status.json").get("status")
    if status not in STATUS_VALUES:
        raise SystemExit("assert failed: invalid experiment status")
    print("assert passed")
    return 0


COMMANDS = {
    "prepare": cmd_prepare,
    "freeze-package": cmd_freeze_package,
    "build-kits": cmd_build_kits,
    "commit-private": cmd_commit_private,
    "validate-readiness": cmd_validate_readiness,
    "normalize-packets": cmd_normalize_packets,
    "lock-score": cmd_lock_score,
    "reveal": cmd_reveal,
    "assemble-public-docket": cmd_assemble_public_docket,
    "assert": cmd_assert,
}


def main() -> int:
    global FORCE_RESET_PREPARE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=COMMANDS)
    parser.add_argument(
        "--force-reset",
        action="store_true",
        help="allow prepare to overwrite an already-advanced run state",
    )
    args = parser.parse_args()
    FORCE_RESET_PREPARE = bool(args.force_reset)
    return COMMANDS[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
