from __future__ import annotations

from pathlib import Path

from .utils import write_json


def run(cfg: dict, out: Path, claim_boundary: str) -> list[dict]:
    version = cfg["artifact_version"]
    seeds = [
        {
            "id": "audit_factory_seed",
            "version": version,
            "thesis": "Automate protocol audit setup with deterministic evidence dockets.",
            "target_mandate_family": "protocol-correctness",
            "fusionplan_summary": "Static checks + deterministic repro package + review dossier",
            "expected_artifact_types": ["audit report", "invariant checklist", "receipt"],
            "success_metrics": ["high-severity issues reproduced", "receipt completeness >= 0.95"],
            "proof_burden": "high",
            "settlement_condition": "validator approval and council ratification",
            "governance_gate": "authority-scope lock",
            "mutation_axes": ["toolchain depth", "proof docket strictness"],
            "lineage_parent_ids": [],
        },
        {
            "id": "invariant_library_seed",
            "version": version,
            "thesis": "Grow reusable invariant suites for contract families.",
            "target_mandate_family": "verification",
            "fusionplan_summary": "Curate invariant templates + schema-linked outputs",
            "expected_artifact_types": ["invariant suite", "coverage report"],
            "success_metrics": ["invariant reuse >= 0.6", "false-positive rate <= 0.1"],
            "proof_burden": "medium",
            "settlement_condition": "validated invariant pack",
            "governance_gate": "no claim widening",
            "mutation_axes": ["depth", "cross-protocol applicability"],
            "lineage_parent_ids": ["audit_factory_seed"],
        },
        {
            "id": "fuzz_harness_seed",
            "version": version,
            "thesis": "Operationalize deterministic fuzz harnesses for replayable bug discovery.",
            "target_mandate_family": "testing",
            "fusionplan_summary": "Harness templates + replay corpus + minimization receipts",
            "expected_artifact_types": ["harness", "repro cases", "run log"],
            "success_metrics": ["repro determinism == 1.0", "new edge paths discovered"],
            "proof_burden": "medium",
            "settlement_condition": "validator confirms replay",
            "governance_gate": "bounded authority",
            "mutation_axes": ["input generators", "coverage strategy"],
            "lineage_parent_ids": ["invariant_library_seed"],
        },
        {
            "id": "exploit_replay_seed",
            "version": version,
            "thesis": "Maintain exploit replay corpus with governance-safe boundaries.",
            "target_mandate_family": "security-research",
            "fusionplan_summary": "Replay historical exploits against patched environments",
            "expected_artifact_types": ["replay trace", "patch delta", "risk memo"],
            "success_metrics": ["replay success on vulnerable baseline", "mitigation validated"],
            "proof_burden": "high",
            "settlement_condition": "quarantine-capable validation path",
            "governance_gate": "human council review",
            "mutation_axes": ["exploit class", "defense strategy"],
            "lineage_parent_ids": ["audit_factory_seed"],
        },
        {
            "id": "governance_parameter_simulator_seed",
            "version": version,
            "thesis": "Simulate governance parameter envelopes before deployment.",
            "target_mandate_family": "governance",
            "fusionplan_summary": "Parameter sweep + policy stress tests + bounded recommendations",
            "expected_artifact_types": ["simulation report", "policy envelope", "receipt"],
            "success_metrics": ["unsafe regions identified", "policy recommendation confidence"],
            "proof_burden": "medium",
            "settlement_condition": "council endorses bounded envelope",
            "governance_gate": "no autonomous override",
            "mutation_axes": ["quorum", "slashing ratio", "timelock"],
            "lineage_parent_ids": ["invariant_library_seed"],
        },
    ]

    for seed in seeds:
        write_json(out / "nova_seeds" / f"{seed['id']}.json", {**seed, "claim_boundary": claim_boundary})

    write_json(
        out / "nova_seed_packet.json",
        {
            "runtime_id": cfg["runtime_id"],
            "version": version,
            "seeds": [{**seed, "claim_boundary": claim_boundary} for seed in seeds],
            "claim_boundary": claim_boundary,
            "status": "implemented as deterministic local artifact",
        },
    )

    return seeds
