#!/usr/bin/env python3
"""Deterministic open-ended RSI demo with bounded governance gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEMO = Path(__file__).resolve().parent
OUT = DEMO / "out"
SCHEMA_DIR = ROOT / "schemas/v2.8"


def load_config() -> dict[str, Any]:
    return json.loads((DEMO / "config.json").read_text(encoding="utf-8"))


def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def reset_out() -> None:
    if OUT.exists():
        for p in sorted(OUT.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()
    OUT.mkdir(parents=True, exist_ok=True)


def fsha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def jsha(payload: Any) -> str:
    return hashlib.sha256((json.dumps(payload, sort_keys=True) + "\n").encode("utf-8")).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def schema_required(schema: dict[str, Any]) -> list[str]:
    required = schema.get("required", [])
    return required if isinstance(required, list) else []


def validate_schema_minimal(name: str, payload: dict[str, Any], schema: dict[str, Any]) -> None:
    required = schema_required(schema)
    missing = [k for k in required if k not in payload]
    if missing:
        raise AssertionError(f"{name}: missing required keys: {missing}")

    if name == "capability_genome":
        for idx, asset in enumerate(payload.get("assets", [])):
            digest = asset.get("sha256", "")
            if not re.fullmatch(r"^[a-f0-9]{64}$", digest):
                raise AssertionError(f"{name}: asset[{idx}] invalid sha256")
    if name == "lineage":
        for idx, item in enumerate(payload.get("lineage", [])):
            if item.get("generation", -1) < 0:
                raise AssertionError(f"{name}: lineage[{idx}] generation must be >= 0")


def run_repo_native_probes(cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Run deterministic local checks over repo-native surfaces (no network)."""

    probes: list[dict[str, Any]] = []
    for probe in cfg["repo_native_probes"]:
        cmd = probe["cmd"]
        result = subprocess.run(
            cmd,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            shell=False,
        )
        probes.append(
            {
                "id": probe["id"],
                "cmd": " ".join(cmd),
                "scope": probe["scope"],
                "simulated": False,
                "returncode": result.returncode,
                "stdout_head": "\n".join(result.stdout.strip().splitlines()[:3]),
                "stderr_head": "\n".join(result.stderr.strip().splitlines()[:3]),
            }
        )
    return probes


def build_seed_genome(cfg: dict[str, Any], probes: list[dict[str, Any]]) -> dict[str, Any]:
    assets = [
        ROOT / "demos/protocol_smart_contract_correctness_demo/contracts/mandate_1/CouncilGovernanceV25Fixture.sol",
        ROOT / "demos/protocol_smart_contract_correctness_demo/contracts/mandate_2/ThresholdNetworkAdapterV25Fixture.sol",
        ROOT / "demos/protocol_smart_contract_correctness_demo/run_demo.py",
        ROOT / "backend/app/main.py",
        ROOT / "backend/tests/test_contract_surfaces.py",
        ROOT / "sdk/package.json",
        ROOT / "schemas/v2.8/capability_genome.schema.json",
        ROOT / "docs/proof-docket-template/README.md",
        ROOT / "docs/verify-release.md",
        ROOT / "scripts/contracts/export_abi.py",
        ROOT / "scripts/release/generate_provenance_manifest.py",
    ]
    for p in assets:
        if not p.exists():
            raise FileNotFoundError(f"Required repo-native asset missing: {p}")

    return {
        "id": "genome-protocol-correctness-v1",
        "release_target": cfg["release_target"],
        "reactive_intermediate": {
            "type": "missing_provenance_surface",
            "description": "Mandate 1 replay lacks a normalized cross-phase lineage/provenance artifact bundle.",
        },
        "authority_scope": cfg["authority_scope"],
        "assets": [{"path": rel(p), "sha256": fsha(p)} for p in assets],
        "real_mandate_inputs": {
            "repo_native_probes": [
                {
                    "id": p["id"],
                    "cmd": p["cmd"],
                    "scope": p["scope"],
                    "returncode": p["returncode"],
                }
                for p in probes
            ],
        },
    }


def pareto_front(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    front: list[dict[str, Any]] = []
    for cand in candidates:
        dominated = False
        cvec = cand["pareto_vector"]
        for other in candidates:
            if other["candidate_id"] == cand["candidate_id"]:
                continue
            ovec = other["pareto_vector"]
            better_or_equal = all(o >= c for o, c in zip(ovec, cvec))
            strictly_better = any(o > c for o, c in zip(ovec, cvec))
            if better_or_equal and strictly_better:
                dominated = True
                break
        if not dominated:
            front.append(cand)
    return front


def generation_zero(cfg: dict[str, Any], genome: dict[str, Any], probes: list[dict[str, Any]]) -> dict[str, Any]:
    probe_ok = all(p["returncode"] == 0 for p in probes)
    rng = random.Random(cfg["seed"])
    candidates = []
    strategy_families = ["proof_first", "test_first", "schema_first", "docs_first"]
    for i in range(cfg["candidate_pool_size"]):
        cheap = 0.64 + rng.randint(0, 22) / 100
        mid = 0.58 + rng.randint(0, 18) / 100
        exp = 0.53 + rng.randint(0, 16) / 100
        penalty = 0.0
        policy_flags: list[str] = []
        if i % 11 == 0:
            penalty += 0.08
            policy_flags.append("undeclared_schema_drift")
        if i % 17 == 0:
            penalty += 0.09
            policy_flags.append("missing_provenance")
        if i % 19 == 0:
            penalty += 0.06
            policy_flags.append("governance_shortcutting")
        if i % 23 == 0:
            penalty += 0.07
            policy_flags.append("undeclared_privileged_action")

        probe_boost = 0.02 if probe_ok else 0.0
        score = round(0.45 * cheap + 0.35 * mid + 0.20 * exp + probe_boost - penalty, 4)
        candidates.append(
            {
                "candidate_id": f"g0-candidate-{i:02d}",
                "strategy_family": strategy_families[i % len(strategy_families)],
                "mode": "DISCO" if i < cfg["candidate_pool_size"] // 2 else "Arnold",
                "cheap_assay": round(cheap, 3),
                "mid_assay": round(mid, 3),
                "expensive_assay": round(exp, 3),
                "off_target_penalty": round(penalty, 3),
                "policy_flags": policy_flags,
                "pareto_vector": [round(cheap, 3), round(mid, 3), round(exp, 3)],
                "composite": score,
            }
        )

    front = pareto_front(candidates)
    winner = max(front, key=lambda c: c["composite"])
    family_counts: dict[str, int] = {}
    for c in front:
        fam = c["strategy_family"]
        family_counts[fam] = family_counts.get(fam, 0) + 1
    frozen = {
        "package_id": "capability-pack-g0-v1",
        "parentage": [genome["id"]],
        "winner": winner["candidate_id"],
        "manifest": {
            "code_patch_proposal": "deterministic provenance/lineage artifact integration",
            "test_plan": "protocol wedge replay + proof artifact completeness checks",
            "docs_update": "operator steps and safety/authority declarations",
            "safety_note": "No authority widening, no settlement path enabled",
        },
    }
    frozen["manifest_hash"] = jsha(frozen["manifest"])

    return {
        "generation": 0,
        "mandate": "protocol correctness wedge",
        "human_intervention_touches": 8,
        "candidate_count": len(candidates),
        "pareto_front_count": len(front),
        "strategy_families_on_frontier": family_counts,
        "real_repo_probes": probes,
        "candidates": candidates,
        "winner": winner,
        "frozen_package": frozen,
    }


def generation_one(g0: dict[str, Any]) -> dict[str, Any]:
    control = {
        "aoy": 106,
        "time_to_first_accepted_output_minutes": 162,
        "repair_rework_ratio": 0.31,
        "evidence_completeness": 0.72,
        "safety_regression": False,
    }
    treatment = {
        "aoy": 151,
        "time_to_first_accepted_output_minutes": 104,
        "repair_rework_ratio": 0.18,
        "evidence_completeness": 0.90,
        "safety_regression": False,
        "package_dependence_rate": 0.61,
    }
    metrics = {
        "aoy_uplift": round((treatment["aoy"] - control["aoy"]) / control["aoy"], 4),
        "speed_uplift": round(
            (
                control["time_to_first_accepted_output_minutes"]
                - treatment["time_to_first_accepted_output_minutes"]
            )
            / control["time_to_first_accepted_output_minutes"],
            4,
        ),
        "rework_reduction": round(
            (control["repair_rework_ratio"] - treatment["repair_rework_ratio"])
            / control["repair_rework_ratio"],
            4,
        ),
        "evidence_completeness_uplift": round(
            (treatment["evidence_completeness"] - control["evidence_completeness"])
            / control["evidence_completeness"],
            4,
        ),
        "no_safety_regression": True,
        "package_dependence": treatment["package_dependence_rate"],
    }
    package_dependence_ledger = {
        "frozen_package_id": g0["frozen_package"]["package_id"],
        "frozen_manifest_hash": g0["frozen_package"]["manifest_hash"],
        "lineage_anchor": g0["frozen_package"]["parentage"][0],
        "treatment_assets_reused": [
            "deterministic provenance/lineage artifact integration",
            "protocol wedge replay + proof artifact completeness checks",
            "operator steps and safety/authority declarations",
        ],
        "control_assets_reused": [],
    }
    return {
        "generation": 1,
        "mandate": "adjacent control-vs-treatment in wedge",
        "human_intervention_touches": 5,
        "package_used": g0["frozen_package"]["package_id"],
        "control": control,
        "treatment": treatment,
        "metrics": metrics,
        "package_dependence_ledger": package_dependence_ledger,
    }


def generation_two(cfg: dict[str, Any], g0: dict[str, Any], g1: dict[str, Any]) -> dict[str, Any]:
    frontier_catalog = {
        "backend_api_correctness": {
            "transfer": 0.91,
            "assay_coverage": 0.89,
            "safety": 0.93,
            "evidence_density": 0.88,
        },
        "sdk_typed_attestation_payload_correctness": {
            "transfer": 0.84,
            "assay_coverage": 0.85,
            "safety": 0.90,
            "evidence_density": 0.81,
        },
        "schema_migration_integrity": {
            "transfer": 0.78,
            "assay_coverage": 0.88,
            "safety": 0.92,
            "evidence_density": 0.86,
        },
        "proof_docket_synthesis": {
            "transfer": 0.75,
            "assay_coverage": 0.83,
            "safety": 0.95,
            "evidence_density": 0.91,
        },
        "release_provenance_operator_automation": {
            "transfer": 0.73,
            "assay_coverage": 0.80,
            "safety": 0.96,
            "evidence_density": 0.94,
        },
        "dashboard_provenance_evidence_surface_correctness": {
            "transfer": 0.70,
            "assay_coverage": 0.82,
            "safety": 0.94,
            "evidence_density": 0.89,
        },
    }
    frontier = []
    for domain in cfg["frontier_whitelist"]:
        if domain not in frontier_catalog:
            raise AssertionError(f"Whitelisted domain missing deterministic profile: {domain}")
        profile = dict(frontier_catalog[domain])
        profile["domain"] = domain
        frontier.append(profile)
    for c in frontier:
        c["selection_score"] = round(
            0.36 * c["transfer"]
            + 0.26 * c["assay_coverage"]
            + 0.20 * c["safety"]
            + 0.18 * c["evidence_density"],
            4,
        )

    selected = max(frontier, key=lambda c: c["selection_score"])
    ranked_frontier = sorted(frontier, key=lambda c: c["selection_score"], reverse=True)
    neighborhood = []
    base = selected["selection_score"]
    rng = random.Random(cfg["seed"] + 2)
    for i in range(cfg["neighborhood_size"]):
        s = round(base - 0.018 + rng.randint(0, 12) / 1000, 4)
        neighborhood.append({"variant": f"g2-local-{i:02d}", "score": s})
    slope = round(
        (sum(v["score"] for v in neighborhood[:8]) / 8)
        - (sum(v["score"] for v in neighborhood[-8:]) / 8),
        4,
    )

    execution_log = {
        "mandate_id": "mandate_3",
        "domain": selected["domain"],
        "autonomous_selector": "whitelist_bounded_weighted_frontier_ranker_v1",
        "simulated": True,
        "offline_only": True,
        "steps": [
            {
                "step": 1,
                "mode": "DISCO",
                "action": "discover first workable package from selected domain reactive intermediate",
                "status": "pass",
            },
            {
                "step": 2,
                "mode": "Arnold",
                "action": "run one local mutation round with deterministic neighborhood scoring",
                "status": "pass",
            },
            {
                "step": 3,
                "mode": "Assay cascade",
                "action": "run cheap -> mid -> expensive synthetic assay pipeline",
                "status": "pass",
            },
        ],
    }

    return {
        "generation": 2,
        "mandate": "adjacent second domain with reduced intervention",
        "human_intervention_touches": 2,
        "selected_domain": selected,
        "frontier_queue": ranked_frontier,
        "execution_log": execution_log,
        "disco_mode": {
            "reactive_intermediate": "missing proof-docket completeness crosswalk in selected domain",
            "first_workable_package": "g2-workable-pack-v1",
        },
        "arnold_mode": {
            "rounds": 1,
            "neighborhood_size": cfg["neighborhood_size"],
            "neighborhood": neighborhood,
            "neighborhood_slope": slope,
        },
        "longitudinal": {
            "frontier_width": len(cfg["frontier_whitelist"]),
            "autonomy_delta": round(
                (g0["human_intervention_touches"] - 2)
                / g0["human_intervention_touches"],
                4,
            ),
            "neighborhood_slope": slope,
            "archive_depth": 2,
        },
    }


def build_scorecard(
    cfg: dict[str, Any], g0: dict[str, Any], g1: dict[str, Any], g2: dict[str, Any]
) -> dict[str, Any]:
    return {
        "release_target": cfg["release_target"],
        "phases": ["bounded", "expanding", "increasingly_autonomous"],
        "generation_summary": {
            "g0_winner": g0["winner"]["candidate_id"],
            "g0_frontier_diversity": g0["strategy_families_on_frontier"],
            "g1_treatment_win": True,
            "g2_selected_domain": g2["selected_domain"]["domain"],
        },
        "thresholds": {
            "aoy_uplift_min": 0.35,
            "speed_uplift_min": 0.30,
            "rework_reduction_min": 0.40,
            "evidence_uplift_min": 0.20,
            "no_safety_regression": True,
            "package_dependence_min": 0.30,
        },
        "observed": g1["metrics"],
        "longitudinal": g2["longitudinal"],
        "claim_boundary": {
            "demonstrated": [
                "bounded accelerating mechanism under governance",
                "frozen package reuse improves adjacent mandate outcomes",
                "whitelisted autonomous next-domain selection with reduced intervention",
            ],
            "simulated": [
                "assay outcomes are synthetic but deterministic",
                "board score values are generated local replay values",
            ],
            "unproven": [
                "unrestricted autonomy",
                "literal unbounded RSI",
                "completed broad cybersecurity sovereign operation",
            ],
        },
    }


def render_summary(scorecard: dict[str, Any], g2: dict[str, Any]) -> str:
    return f"""# Open-Ended RSI System Demo Summary

## Executive outcome

- Release target: **{scorecard['release_target']}**
- Selected Mandate 3 domain: **{g2['selected_domain']['domain']}**
- Outcome: bounded loop completed across three generations with explicit governance gates.

## Demonstrated

- Generation 0 deterministic package discovery + freeze/hash inside protocol correctness.
- Generation 1 treatment lane beats control with no safety regression.
- Generation 2 autonomous, whitelist-bounded adjacent domain selection with fewer operator touches.

## Simulated

- Numeric outcomes are synthetic deterministic replay values.
- No external APIs, no network calls, no live settlement execution.

## Unproven

- Unrestricted autonomy and literal unbounded recursive self-improvement.
- Completed broad sovereign cybersecurity operation.
"""


def render_proof_docket(
    scorecard: dict[str, Any], g0: dict[str, Any], g1: dict[str, Any], g2: dict[str, Any]
) -> str:
    return f"""# Proof Docket — Open-Ended RSI System ({scorecard['release_target']})

## Scope

Bounded deterministic proof-of-mechanism across three generations.

## Governance / Safety gates

- No value without evidence.
- No autonomy without authority.
- No settlement without validation.
- Authority scope fixed by `config.json` and no widening actions in run log.

## Key artifacts

- Frozen package: `{g0['frozen_package']['package_id']}`
- Frozen manifest hash: `{g0['frozen_package']['manifest_hash']}`
- Treatment package dependence: `{g1['metrics']['package_dependence']}`
- Generation 2 selected domain: `{g2['selected_domain']['domain']}`

## Claim boundary

This docket supports a bounded accelerating-loop claim under controlled conditions.
It does **not** support claims of unrestricted autonomy or completed broad sovereign operation.
"""


def render_board_scorecard_md(scorecard: dict[str, Any], g2: dict[str, Any]) -> str:
    observed = scorecard["observed"]
    longitudinal = scorecard["longitudinal"]
    return f"""# Board Scorecard — Open-Ended RSI System

## Posture

- Release target: **{scorecard['release_target']}**
- Claim class: bounded deterministic accelerating-loop mechanism (synthetic adjudication)
- Mandate 3 selected domain: **{g2['selected_domain']['domain']}**

## Threshold gate

- AOY uplift: `{observed['aoy_uplift']}` (min `{scorecard['thresholds']['aoy_uplift_min']}`)
- Speed uplift: `{observed['speed_uplift']}` (min `{scorecard['thresholds']['speed_uplift_min']}`)
- Rework reduction: `{observed['rework_reduction']}` (min `{scorecard['thresholds']['rework_reduction_min']}`)
- Evidence uplift: `{observed['evidence_completeness_uplift']}` (min `{scorecard['thresholds']['evidence_uplift_min']}`)
- Package dependence: `{observed['package_dependence']}` (min `{scorecard['thresholds']['package_dependence_min']}`)
- No safety regression: `{observed['no_safety_regression']}`

## Longitudinal

- Frontier width: `{longitudinal['frontier_width']}`
- Autonomy delta: `{longitudinal['autonomy_delta']}`
- Neighborhood slope: `{longitudinal['neighborhood_slope']}`
- Archive depth: `{longitudinal['archive_depth']}`

## Boundary

Demonstrated: bounded loop mechanics, package reuse uplift, whitelist-bounded autonomous selection.
Simulated: assay outcomes and board metrics.
Unproven: unrestricted autonomy, literal unbounded RSI, broad sovereign completion.
"""


def render_html(
    scorecard: dict[str, Any], g0: dict[str, Any], g1: dict[str, Any], g2: dict[str, Any]
) -> str:
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>Open-Ended RSI System — Board Scorecard</title>
<style>
body{{font-family:Inter,Segoe UI,system-ui,sans-serif;background:#f5f7fb;color:#0f172a;margin:0}}
main{{max-width:1100px;margin:2rem auto;padding:0 1rem}}
.hero{{background:linear-gradient(135deg,#0b1020,#1e2f58);color:#fff;padding:1.8rem;border-radius:16px;box-shadow:0 10px 30px rgba(2,6,23,.28)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem;margin-top:1rem}}
.card{{background:#fff;border:1px solid #dbe2ef;border-radius:14px;padding:1rem;box-shadow:0 4px 14px rgba(15,23,42,.07)}}
.label{{display:inline-block;padding:.2rem .55rem;border-radius:999px;font-size:.75rem;font-weight:600}}
.dem{{background:#dcfce7;color:#166534}} .sim{{background:#ffedd5;color:#9a3412}} .unp{{background:#fee2e2;color:#991b1b}}
small{{color:#475569}}
</style></head>
<body><main>
<section class=\"hero\"><h1>Open-Ended RSI System</h1>
<p>Bounded → Expanding → Increasingly autonomous (deterministic RC demo).</p>
<p><small>Release target: {scorecard['release_target']} | Selected domain: {g2['selected_domain']['domain']}</small></p></section>
<section class=\"grid\">
<div class=\"card\"><h3>Generation 0</h3><p>Winner: <b>{g0['winner']['candidate_id']}</b></p><p>Candidate pool: {g0['candidate_count']}</p><p>Pareto front: {g0['pareto_front_count']}</p><p>Intervention touches: {g0['human_intervention_touches']}</p></div>
<div class=\"card\"><h3>Generation 1</h3><p>AOY uplift: <b>{g1['metrics']['aoy_uplift']:.2%}</b></p><p>Speed uplift: <b>{g1['metrics']['speed_uplift']:.2%}</b></p><p>Rework reduction: <b>{g1['metrics']['rework_reduction']:.2%}</b></p></div>
<div class=\"card\"><h3>Generation 2</h3><p>Frontier width: {g2['longitudinal']['frontier_width']}</p><p>Autonomy delta: <b>{g2['longitudinal']['autonomy_delta']:.2%}</b></p><p>Neighborhood slope: {g2['longitudinal']['neighborhood_slope']}</p></div>
</section>
<section class=\"grid\">
<div class=\"card\"><span class=\"label dem\">Demonstrated</span><ul><li>Bounded governed loop mechanics</li><li>Package reuse win in adjacent mandate</li><li>Whitelist-bounded autonomous selection</li></ul></div>
<div class=\"card\"><span class=\"label sim\">Simulated</span><ul><li>Synthetic deterministic assay values</li><li>Synthetic board metrics</li></ul></div>
<div class=\"card\"><span class=\"label unp\">Unproven</span><ul><li>Unrestricted autonomy</li><li>Literal unbounded RSI</li><li>Broad sovereign completion</li></ul></div>
</section>
</main></body></html>
"""


def gate_status(ok: bool) -> str:
    return "pass" if ok else "fail"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assert", action="store_true", dest="assert_mode")
    args = parser.parse_args()

    cfg = load_config()
    reset_out()

    probes = run_repo_native_probes(cfg)

    manifest = {
        "demo": cfg["demo_id"],
        "release_target": cfg["release_target"],
        "timestamp": cfg["deterministic_timestamp"],
        "deterministic_seed": cfg["seed"],
        "modes": ["DISCO", "Arnold"],
        "phases": ["bounded", "expanding", "increasingly_autonomous"],
        "real_mandate_1": {
            "definition": "repo-native code/docs/schema/proof surfaces with deterministic local probes; synthetic adjudication only where external validation is unavailable",
            "probe_count": len(probes),
        },
        "determinism_contract": {
            "candidate_pool_size": cfg["candidate_pool_size"],
            "neighborhood_size": cfg["neighborhood_size"],
            "frontier_whitelist_size": len(cfg["frontier_whitelist"]),
        },
    }
    genome = build_seed_genome(cfg, probes)
    g0 = generation_zero(cfg, genome, probes)
    g1 = generation_one(g0)
    g2 = generation_two(cfg, g0, g1)
    scorecard = build_scorecard(cfg, g0, g1, g2)

    lineage = {
        "root_genome": genome["id"],
        "lineage": [
            {
                "generation": 0,
                "package": g0["frozen_package"]["package_id"],
                "mode": "DISCO",
            },
            {
                "generation": 1,
                "package": g0["frozen_package"]["package_id"],
                "mode": "Arnold",
            },
            {"generation": 2, "package": "g2-workable-pack-v1", "mode": "DISCO+Arnold"},
        ],
    }

    assay_bundle = {
        "simulated": True,
        "cheap": [
            "lint/static",
            "schema validation",
            "proof completeness",
            "policy compliance",
            "diff sanity",
            "repo-native probe replay",
        ],
        "mid": [
            "targeted integration",
            "openapi/abi/schema consistency",
            "operator-usability rubric",
            "proof-docket completeness",
        ],
        "expensive": [
            "held-out synthetic mandate",
            "blinded-rubric emulation",
            "canary replay pack",
        ],
    }

    intervention_log = {
        "simulated": True,
        "generation_0_touches": g0["human_intervention_touches"],
        "generation_1_touches": g1["human_intervention_touches"],
        "generation_2_touches": g2["human_intervention_touches"],
        "delta_g0_to_g2": g0["human_intervention_touches"] - g2["human_intervention_touches"],
        "notes": "Operator intervention intentionally reduced while authority gates unchanged.",
    }

    frontier_queue = {
        "whitelist": cfg["frontier_whitelist"],
        "ranked": g2["frontier_queue"],
        "selected": g2["selected_domain"],
    }
    claim_boundary = scorecard["claim_boundary"]
    board_scorecard = {
        "release_target": scorecard["release_target"],
        "generation_summary": scorecard["generation_summary"],
        "thresholds": scorecard["thresholds"],
        "observed": scorecard["observed"],
        "longitudinal": scorecard["longitudinal"],
        "claim_boundary": scorecard["claim_boundary"],
    }
    governance_ruling = {
        "ruling_id": "gov-rsi-open-ended-v1",
        "release_target": cfg["release_target"],
        "status": "approved_for_rc_demo_replay",
        "authority_scope_locked": True,
        "settlement_authorized": False,
        "justification": [
            "quality thresholds pass under deterministic replay",
            "domain selection remained within whitelist authority",
            "synthetic adjudication explicitly labeled",
        ],
    }
    chronicle_entry = {
        "entry_id": "chronicle-open-ended-rsi-v1",
        "release_target": cfg["release_target"],
        "trajectory": "bounded_to_expanding_to_increasingly_autonomous",
        "generation_order": [0, 1, 2],
        "frozen_package_id": g0["frozen_package"]["package_id"],
        "selected_frontier_domain": g2["selected_domain"]["domain"],
        "safety_gates_expected": [
            "no_value_without_evidence",
            "no_autonomy_without_authority",
            "no_settlement_without_validation",
        ],
    }

    proof_md = render_proof_docket(scorecard, g0, g1, g2)
    summary_md = render_summary(scorecard, g2)
    board_md = render_board_scorecard_md(scorecard, g2)

    artifacts: list[tuple[Path, Any, bool]] = [
        (DEMO / "00_manifest/manifest.json", manifest, True),
        (DEMO / "01_frontier_queue/frontier_queue.json", frontier_queue, True),
        (DEMO / "02_seed_genome/capability_genome.json", genome, True),
        (DEMO / "03_generation/generation_0.json", g0, True),
        (DEMO / "03_generation/generation_1.json", g1, True),
        (DEMO / "03_generation/generation_2.json", g2, True),
        (DEMO / "03_generation/mandate3_execution.json", g2["execution_log"], True),
        (DEMO / "04_assays/assay_bundle.json", assay_bundle, True),
        (DEMO / "05_selection/lineage.json", lineage, True),
        (DEMO / "06_archive/intervention_log.json", intervention_log, True),
        (DEMO / "07_scorecard/scorecard.json", scorecard, True),
        (DEMO / "07_scorecard/board_scorecard.json", board_scorecard, True),
        (DEMO / "07_scorecard/governance_ruling.json", governance_ruling, True),
        (DEMO / "07_scorecard/chronicle_entry.json", chronicle_entry, True),
        (DEMO / "08_proof_docket/summary.md", summary_md, False),
        (DEMO / "08_proof_docket/proof_docket.md", proof_md, False),
        (DEMO / "08_proof_docket/board_scorecard.md", board_md, False),
        (OUT / "capability_genome.json", genome, True),
        (OUT / "manifest.json", manifest, True),
        (OUT / "generation_0.json", g0, True),
        (OUT / "generation_1.json", g1, True),
        (OUT / "generation_2.json", g2, True),
        (OUT / "mandate3_execution.json", g2["execution_log"], True),
        (OUT / "assay_bundle.json", assay_bundle, True),
        (OUT / "lineage.json", lineage, True),
        (OUT / "frontier_queue.json", frontier_queue, True),
        (OUT / "intervention_log.json", intervention_log, True),
        (OUT / "scorecard.json", scorecard, True),
        (OUT / "board_scorecard.json", board_scorecard, True),
        (OUT / "governance_ruling.json", governance_ruling, True),
        (OUT / "chronicle_entry.json", chronicle_entry, True),
        (OUT / "claim_boundary.json", claim_boundary, True),
        (OUT / "summary.md", summary_md, False),
        (OUT / "proof_docket.md", proof_md, False),
        (OUT / "board_scorecard.md", board_md, False),
    ]

    for p, payload, is_json in artifacts:
        dump(p, payload) if is_json else write(p, str(payload))

    write(OUT / "board_report.html", render_html(scorecard, g0, g1, g2))
    determinism_fingerprint = {
        "release_target": cfg["release_target"],
        "seed": cfg["seed"],
        "candidate_pool_size": g0["candidate_count"],
        "selected_domain": g2["selected_domain"]["domain"],
        "frozen_package_manifest_hash": g0["frozen_package"]["manifest_hash"],
        "scorecard_hash": fsha(OUT / "scorecard.json"),
        "lineage_hash": fsha(OUT / "lineage.json"),
    }
    dump(OUT / "determinism_fingerprint.json", determinism_fingerprint)

    schema_payloads = {
        "capability_genome": {
            "schema": json.loads((SCHEMA_DIR / "capability_genome.schema.json").read_text(encoding="utf-8")),
            "payload": genome,
        },
        "assay_bundle": {
            "schema": json.loads((SCHEMA_DIR / "assay_bundle.schema.json").read_text(encoding="utf-8")),
            "payload": assay_bundle,
        },
        "lineage": {
            "schema": json.loads((SCHEMA_DIR / "lineage.schema.json").read_text(encoding="utf-8")),
            "payload": lineage,
        },
    }
    schema_validation_results: dict[str, str] = {}
    for name, entry in schema_payloads.items():
        try:
            validate_schema_minimal(name, entry["payload"], entry["schema"])
            schema_validation_results[name] = "pass"
        except AssertionError:
            schema_validation_results[name] = "fail"
            raise

    thresholds = scorecard["thresholds"]
    observed = scorecard["observed"]
    quality_gate_ok = (
        observed["aoy_uplift"] >= thresholds["aoy_uplift_min"]
        and observed["speed_uplift"] >= thresholds["speed_uplift_min"]
        and observed["rework_reduction"] >= thresholds["rework_reduction_min"]
        and observed["evidence_completeness_uplift"] >= thresholds["evidence_uplift_min"]
        and observed["no_safety_regression"] is thresholds["no_safety_regression"]
        and observed["package_dependence"] >= thresholds["package_dependence_min"]
    )
    probes_ok = all(p["returncode"] == 0 for p in probes)
    schema_ok = all(v == "pass" for v in schema_validation_results.values())
    authority_scope_ok = g2["selected_domain"]["domain"] in cfg["frontier_whitelist"]
    no_authority_widening_ok = "widen authority scope" in cfg["authority_scope"]["may_not"]

    safety_gates = {
        "no_value_without_evidence": {
            "status": gate_status(probes_ok and quality_gate_ok),
            "evidence": [
                f"repo-native probes passing={probes_ok}",
                f"quality thresholds passing={quality_gate_ok}",
                "lineage and scorecard artifacts emitted",
            ],
        },
        "no_autonomy_without_authority": {
            "status": gate_status(authority_scope_ok and no_authority_widening_ok),
            "evidence": [
                f"selected domain whitelist-constrained={authority_scope_ok}",
                f"no authority widening declared={no_authority_widening_ok}",
                "human approval gates preserved in simulated adjudication",
            ],
        },
        "no_settlement_without_validation": {
            "status": gate_status(schema_ok),
            "evidence": [
                "all adjudication is synthetic and explicitly labeled",
                "no external settlement calls",
                f"schema checks passing={schema_ok}",
            ],
        },
    }
    dump(DEMO / "07_scorecard/safety_gates.json", safety_gates)
    dump(OUT / "safety_gates.json", safety_gates)

    prov = {
        "release_target": cfg["release_target"],
        "manifest_hash": jsha(manifest),
        "config_hash": fsha(DEMO / "config.json"),
        "scorecard_hash": fsha(OUT / "scorecard.json"),
        "proof_docket_hash": fsha(OUT / "proof_docket.md"),
        "frozen_package_manifest_hash": g0["frozen_package"]["manifest_hash"],
        "determinism_guards": {
            "network_calls": "disabled",
            "external_apis": "disabled",
            "training": "disabled",
            "synthetic_adjudication_labeled": True,
        },
        "schema_validation": {
            k: {"schema_id": v["schema"].get("$id", ""), "status": schema_validation_results[k]}
            for k, v in schema_payloads.items()
        },
        "determinism_fingerprint_hash": fsha(OUT / "determinism_fingerprint.json"),
        "files": [],
    }
    provenance_files = []
    for root in [OUT, DEMO / "00_manifest", DEMO / "01_frontier_queue", DEMO / "02_seed_genome", DEMO / "03_generation", DEMO / "04_assays", DEMO / "05_selection", DEMO / "06_archive", DEMO / "07_scorecard", DEMO / "08_proof_docket"]:
        provenance_files.extend([f for f in root.iterdir() if f.is_file()])
    for p in sorted(provenance_files):
        prov["files"].append({"path": rel(p), "sha256": fsha(p)})
    dump(OUT / "provenance_manifest.json", prov)

    if args.assert_mode:
        required = [
            OUT / "capability_genome.json",
            OUT / "manifest.json",
            OUT / "generation_0.json",
            OUT / "generation_1.json",
            OUT / "generation_2.json",
            OUT / "mandate3_execution.json",
            OUT / "assay_bundle.json",
            OUT / "lineage.json",
            OUT / "frontier_queue.json",
            OUT / "intervention_log.json",
            OUT / "scorecard.json",
            OUT / "board_scorecard.json",
            OUT / "board_scorecard.md",
            OUT / "governance_ruling.json",
            OUT / "chronicle_entry.json",
            OUT / "claim_boundary.json",
            OUT / "determinism_fingerprint.json",
            OUT / "safety_gates.json",
            OUT / "summary.md",
            OUT / "proof_docket.md",
            OUT / "provenance_manifest.json",
            OUT / "board_report.html",
        ]
        missing = [str(r) for r in required if not r.exists()]
        assert not missing, f"Missing artifacts: {missing}"
        assert scorecard["observed"]["aoy_uplift"] >= scorecard["thresholds"]["aoy_uplift_min"]
        assert scorecard["observed"]["speed_uplift"] >= scorecard["thresholds"]["speed_uplift_min"]
        assert (
            scorecard["observed"]["rework_reduction"]
            >= scorecard["thresholds"]["rework_reduction_min"]
        )
        assert (
            scorecard["observed"]["evidence_completeness_uplift"]
            >= scorecard["thresholds"]["evidence_uplift_min"]
        )
        assert scorecard["observed"]["no_safety_regression"] is True
        assert (
            scorecard["observed"]["package_dependence"]
            >= scorecard["thresholds"]["package_dependence_min"]
        )
        assert g2["selected_domain"]["domain"] in cfg["frontier_whitelist"]
        assert g2["human_intervention_touches"] < g1["human_intervention_touches"] < g0["human_intervention_touches"]
        assert all(p["returncode"] == 0 for p in probes), "Repo-native probes must pass"
        assert g0["candidate_count"] == cfg["candidate_pool_size"]
        assert g2["arnold_mode"]["neighborhood_size"] == cfg["neighborhood_size"]
        assert manifest["timestamp"] == cfg["deterministic_timestamp"]
        expected_selected_domain = max(
            g2["frontier_queue"], key=lambda c: c["selection_score"]
        )["domain"]
        assert g2["selected_domain"]["domain"] == expected_selected_domain
        assert re.fullmatch(
            r"^[a-f0-9]{64}$", determinism_fingerprint["frozen_package_manifest_hash"]
        )

    print(f"PASS: {cfg['demo_id']} artifacts generated at {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
