from __future__ import annotations

from pathlib import Path

from .utils import write_json


WEIGHTS = {
    "expected_aoy": 0.20,
    "evidence_density": 0.16,
    "verification_strength": 0.16,
    "archive_reuse_potential": 0.14,
    "safety_authority_risk": -0.10,
    "operator_cost": -0.08,
    "adjacent_transfer_potential": 0.10,
    "proof_burden": -0.06,
}


SCORES = {
    "audit_factory_seed": [0.87, 0.92, 0.95, 0.85, 0.22, 0.41, 0.80, 0.71],
    "invariant_library_seed": [0.83, 0.89, 0.91, 0.93, 0.18, 0.37, 0.86, 0.58],
    "fuzz_harness_seed": [0.79, 0.85, 0.88, 0.82, 0.24, 0.34, 0.81, 0.55],
    "exploit_replay_seed": [0.88, 0.78, 0.86, 0.74, 0.39, 0.45, 0.77, 0.80],
    "governance_parameter_simulator_seed": [0.76, 0.83, 0.84, 0.79, 0.20, 0.31, 0.75, 0.50],
}


def run(cfg: dict, out: Path, seeds: list[dict], claim_boundary: str) -> dict:
    ranked = []
    keys = list(WEIGHTS.keys())
    for seed in seeds:
        seed_id = seed["id"]
        vals = SCORES[seed_id]
        scored = dict(zip(keys, vals))
        score = sum(scored[k] * WEIGHTS[k] for k in keys)
        ranked.append({"seed_id": seed_id, **scored, "score": round(score, 4)})

    ranked.sort(key=lambda r: r["score"], reverse=True)
    selected = [ranked[0]["seed_id"], ranked[1]["seed_id"]]

    selection = {
        "runtime_id": cfg["runtime_id"],
        "oracle_mode": "deterministic_local_risk_selection",
        "ranked": ranked,
        "selected_bundle": selected,
        "selection_reason": "Top two seeds maximize weighted score under bounded risk and proof burden.",
        "status": "local risk/selection oracle; not live DEX",
        "claim_boundary": claim_boundary,
    }
    risk = {
        "runtime_id": cfg["runtime_id"],
        "selected_bundle": selected,
        "risk_controls": [
            "validation-before-settlement",
            "authority boundary checks",
            "quarantine path on claim drift",
        ],
        "highest_risk_seed": ranked[-1]["seed_id"],
        "claim_boundary": claim_boundary,
    }
    orderbook = {
        "runtime_id": cfg["runtime_id"],
        "book_id": "mark-local-book-001",
        "simulated_orders": [
            {"seed_id": row["seed_id"], "alloc_units": int(100 * row["score"]), "unit": cfg["bounty_unit"]}
            for row in ranked
        ],
        "status": "simulation only; no live price discovery",
        "claim_boundary": claim_boundary,
    }
    write_json(out / "mark_selection_report.json", selection)
    write_json(out / "mark_risk_report.json", risk)
    write_json(out / "mark_orderbook_snapshot.json", orderbook)
    return selection
