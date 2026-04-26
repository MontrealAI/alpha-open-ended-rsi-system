from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from .fixtures import function_bodies, line_for_function
from .utils import load_json, write_json

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
EVIDENCE_CHECKLIST = load_json(CONFIG_DIR / "evidence_completeness_checklist.json")
RUBRIC = load_json(CONFIG_DIR / "accepted_usefulness_rubric.json")
ALLOWED_EVIDENCE_FIELDS = {
    "code_pointer",
    "issue_statement",
    "broken_invariant_or_state_path",
    "reproduction_artifact",
    "severity_rationale",
    "suggested_fix",
    "traceability_to_scope",
}


def _validate_checklist_fields(checklist: list[str]) -> None:
    unknown = sorted(set(checklist) - ALLOWED_EVIDENCE_FIELDS)
    if unknown:
        raise ValueError(
            "Unknown evidence checklist field(s): "
            + ", ".join(unknown)
            + ". Update config/evidence_completeness_checklist.json with valid fields only."
        )
    seen = set()
    duplicates = []
    for field in checklist:
        if field in seen and field not in duplicates:
            duplicates.append(field)
        seen.add(field)
    if duplicates:
        raise ValueError(
            "Duplicate evidence checklist field(s): "
            + ", ".join(sorted(duplicates))
            + ". Remove duplicates from config/evidence_completeness_checklist.json."
        )


_validate_checklist_fields(EVIDENCE_CHECKLIST)

SEED_PROFILES = {
    "audit_factory": {
        "known_issues": {"proofless_settlement", "instant_upgrade", "no_challenge_window"},
        "latency": 5,
        "coverage": 0.74,
        "rework_bias": 0.36,
        "unsupported_claim_rate": 0.18,
        "artifact_quality": 0.68,
    },
    "invariant_library": {
        "known_issues": {"proofless_settlement", "instant_upgrade", "treasury_drift", "no_challenge_window"},
        "latency": 3,
        "coverage": 0.95,
        "rework_bias": 0.17,
        "unsupported_claim_rate": 0.06,
        "artifact_quality": 0.93,
    },
    "fuzz_harness": {
        "known_issues": {"proofless_settlement", "treasury_drift", "no_challenge_window"},
        "latency": 6,
        "coverage": 0.81,
        "rework_bias": 0.31,
        "unsupported_claim_rate": 0.15,
        "artifact_quality": 0.72,
    },
    "exploit_replay": {
        "known_issues": {"proofless_settlement", "treasury_drift"},
        "latency": 7,
        "coverage": 0.66,
        "rework_bias": 0.4,
        "unsupported_claim_rate": 0.21,
        "artifact_quality": 0.62,
    },
    "governance_parameter_simulator": {
        "known_issues": {"instant_upgrade", "no_challenge_window"},
        "latency": 8,
        "coverage": 0.64,
        "rework_bias": 0.3,
        "unsupported_claim_rate": 0.12,
        "artifact_quality": 0.76,
    },
}

PACKAGE_COMPONENTS = [
    "ontology",
    "invariant_library",
    "workflow_template",
    "query_bundle",
    "mechanism_library",
    "release_gate_packet",
    "skill_wrapper",
]


@dataclass
class Finding:
    contract: str
    function: str
    issue_type: str
    severity: str
    issue_statement: str
    code_pointer: str
    broken_invariant_or_state_path: str
    reproduction_artifact: str
    severity_rationale: str
    suggested_fix: str
    traceability_to_scope: str
    uses_release_gate_recommendation: bool
    includes_harness_artifact: bool
    discovery_step: int
    unsupported_claim: bool
    severity_inflation: bool
    package_dependencies: list[str]

    def completeness(self, checklist: list[str] | None = None) -> float:
        active_checklist = checklist or EVIDENCE_CHECKLIST
        if not active_checklist:
            return 0.0
        _validate_checklist_fields(active_checklist)
        flags = [bool(getattr(self, field, "")) for field in active_checklist]
        return sum(flags) / len(flags)


def _detect_issues(contracts: dict[str, str]):
    detected = []
    for contract_name, source in contracts.items():
        for fn_name, body in function_bodies(source):
            body_lower = body.lower()
            fn_lower = fn_name.lower()
            if ("call{value:" in body or "transfer(" in body) and any(v in fn_lower for v in ["finalize", "release", "settle"]) and "challengeperiod" not in body_lower and "block.timestamp" not in body_lower:
                detected.append((contract_name, fn_name, "no_challenge_window", "medium"))
            if any(k in fn_lower for k in ["swap", "upgrade"]) and "timelock" not in body_lower and "delay" not in body_lower:
                detected.append((contract_name, fn_name, "instant_upgrade", "high"))
            if ("refund" in fn_lower or "withdraw" in fn_lower) and ("call{value:" in body or "transfer(" in body) and "-=" not in body and "locked" in source.lower():
                detected.append((contract_name, fn_name, "treasury_drift", "high"))
            if ("settle" in fn_lower or "release" in fn_lower) and ("call{value:" in body or "transfer(" in body) and "proof" not in body_lower and "validator" not in body_lower and "attest" not in body_lower:
                detected.append((contract_name, fn_name, "proofless_settlement", "high"))
    dedup = {(a, b, c): (a, b, c, d) for a, b, c, d in detected}
    return list(dedup.values())


def run_seed_assay(seed_packet: dict, contracts: dict[str, str], ground_truth: dict, package_mode: bool = False):
    profile = SEED_PROFILES[seed_packet["id"]]
    issues = _detect_issues(contracts)
    findings: list[Finding] = []

    filtered = []
    for issue in issues:
        if issue[2] in profile["known_issues"]:
            filtered.append(issue)

    # Without the frozen package, cross-contract ontology transfer is weaker.
    if not package_mode and "threshold_attestation" in ground_truth["mandate_id"]:
        filtered = [i for i in filtered if i[2] != "no_challenge_window"]

    false_positive = None
    if profile["unsupported_claim_rate"] > 0.15:
        false_positive = (next(iter(contracts.keys())), "lockBond", "unsupported_authority_escalation", "high")

    first_step_base = profile["latency"] + (2 if not package_mode else 0)
    for idx, (contract, function, issue_type, severity) in enumerate(filtered, start=1):
        line = line_for_function(contracts[contract], function)
        weak_evidence = (not package_mode and idx % 2 == 0)
        suggestion = "" if weak_evidence else "Add release-gate precondition checks and explicit challenge/proof barriers."
        state_path = "" if weak_evidence else "Value movement must be gated by validated authority and challenge semantics."
        dependencies = PACKAGE_COMPONENTS[:] if package_mode else []
        findings.append(
            Finding(
                contract=contract,
                function=function,
                issue_type=issue_type,
                severity=severity,
                issue_statement=f"{issue_type} detected in {function}.",
                code_pointer=f"{contract}:L{line}",
                broken_invariant_or_state_path=state_path,
                reproduction_artifact=f"deterministic_trace::{contract}::{function}",
                severity_rationale="" if weak_evidence else "Funds or control can move before proper validation guardrails.",
                suggested_fix=suggestion,
                traceability_to_scope=ground_truth["mandate_id"],
                uses_release_gate_recommendation=not weak_evidence,
                includes_harness_artifact=package_mode or seed_packet["id"] in {"fuzz_harness", "invariant_library"},
                discovery_step=first_step_base + idx,
                unsupported_claim=False,
                severity_inflation=False,
                package_dependencies=dependencies,
            )
        )

    if false_positive:
        findings.append(
            Finding(
                contract=false_positive[0],
                function=false_positive[1],
                issue_type=false_positive[2],
                severity=false_positive[3],
                issue_statement="Claim is not supported by synthetic ground truth.",
                code_pointer=f"{false_positive[0]}:L1",
                broken_invariant_or_state_path="",
                reproduction_artifact="",
                severity_rationale="",
                suggested_fix="",
                traceability_to_scope=ground_truth["mandate_id"],
                uses_release_gate_recommendation=False,
                includes_harness_artifact=False,
                discovery_step=first_step_base + len(filtered) + 2,
                unsupported_claim=True,
                severity_inflation=True,
                package_dependencies=[],
            )
        )

    truth = {(i["contract"], i["function"], i["issue_type"]): i for i in ground_truth["issues"]}
    accepted, rejected = [], []
    rework_count = 0
    for finding in findings:
        key = (finding.contract, finding.function, finding.issue_type)
        matched = key in truth
        complete = finding.completeness()
        needs_rework = matched and complete < 0.96
        rework_count += 1 if needs_rework else 0
        (accepted if matched else rejected).append(finding)

    accepted_points = 0
    for finding in accepted:
        if finding.severity == "high":
            accepted_points += RUBRIC["accepted_high_with_repro"]
        elif finding.severity == "medium":
            accepted_points += RUBRIC["accepted_medium_with_repro"]
        else:
            accepted_points += RUBRIC["accepted_low"]
        if finding.includes_harness_artifact:
            accepted_points += RUBRIC["accepted_invariant_or_fuzz_harness"]
        if finding.uses_release_gate_recommendation:
            accepted_points += RUBRIC["accepted_release_gate_recommendation"]

    evidence = sum(f.completeness() for f in accepted) / max(1, len(accepted))
    unsupported_claim_rate = sum(1 for f in findings if f.unsupported_claim) / max(1, len(findings))
    severity_inflation_count = sum(1 for f in findings if f.severity_inflation)
    first_step = min((f.discovery_step for f in accepted), default=999)
    package_quality = min(1.0, profile["artifact_quality"] + (0.08 if package_mode else 0.0))
    package_dependence_rate = (
        sum(1 for f in accepted if f.package_dependencies) / max(1, len(accepted))
        if package_mode else 0.0
    )

    effort_units = len(ground_truth["issues"]) * 5
    aoy = accepted_points / effort_units

    return {
        "seed": seed_packet["id"],
        "accepted_findings": [asdict(f) for f in accepted],
        "rejected_findings": [asdict(f) for f in rejected],
        "metrics": {
            "accepted_usefulness_points": accepted_points,
            "accepted_count": len(accepted),
            "time_to_first_accepted_output": first_step,
            "repair_rework": round(rework_count / max(1, len(accepted)), 3),
            "evidence_completeness": round(evidence, 3),
            "unsupported_claim_rate": round(unsupported_claim_rate, 3),
            "severity_inflation_count": severity_inflation_count,
            "packageable_artifact_quality": round(package_quality, 3),
            "aoy": round(aoy, 3),
            "package_dependence_rate": round(package_dependence_rate, 3),
        },
    }


def run_mandate_1_competition(seed_packets: list[dict], contracts: dict[str, str], gt_path: Path, out_dir: Path):
    gt = load_json(gt_path)
    write_json(out_dir / "accepted_usefulness_rubric.json", RUBRIC)
    write_json(out_dir / "evidence_completeness_checklist.json", EVIDENCE_CHECKLIST)

    results = []
    for seed in seed_packets:
        result = run_seed_assay(seed, contracts, gt, package_mode=False)
        results.append(result)
        write_json(out_dir / f"{seed['id']}_result.json", result)

    def rank_key(r):
        m = r["metrics"]
        return (
            m["accepted_usefulness_points"],
            -m["time_to_first_accepted_output"],
            -m["repair_rework"],
            m["evidence_completeness"],
            -m["unsupported_claim_rate"],
            -m["severity_inflation_count"],
            m["packageable_artifact_quality"],
        )

    winner = sorted(results, key=rank_key, reverse=True)[0]
    summary = {
        "mandate": gt["mandate_id"],
        "winner": winner["seed"],
        "selection_basis": "deterministic lexicographic rank across usefulness, speed, rework, evidence, safety, package quality",
        "results": results,
    }
    write_json(out_dir / "assay_summary.json", summary)
    return summary


def run_mandate_2(seed_packet: dict, contracts: dict[str, str], gt_path: Path, with_package: bool, out_dir: Path):
    gt = load_json(gt_path)
    result = run_seed_assay(seed_packet, contracts, gt, package_mode=with_package)
    lane = "treatment" if with_package else "control"
    result["lane"] = lane
    write_json(out_dir / "findings.json", result)
    return result
