from __future__ import annotations

import re
from pathlib import Path

from .utils import write_json

DOCTRINE_DOCS = [
    "docs/DOCTRINE_STACK.md",
    "docs/THERMODYNAMIC_MODEL.md",
    "docs/NATION_STATE_DOCTRINE.md",
]

REQUIRED_EQUATIONS = {
    "state_vector": "X(t)=\\big(K,C,D,A,Q,R,\\Sigma\\big)",
    "resource_flux_input": "J_{\\text{in}}=\\alpha_K \\dot K_{\\text{in}}+\\alpha_C \\dot C_{\\text{in}}+\\alpha_D \\dot D_{\\text{in}}",
    "resource_flux_split": "J_{\\text{in}}=\\dot W_{\\text{useful}}+\\dot Q_{\\text{diss}}+\\dot U",
    "resource_flux_useful": "\\dot W_{\\text{useful}} \\approx \\beta_A \\dot A + \\beta_Q \\dot Q + \\beta_R \\dot R_{\\text{validated}}",
    "free_energy": "\\mathcal G[X]=\\mathcal H[X]-T_{\\text{eff}}\\mathcal S_{\\text{org}}[X]",
    "free_energy_objective": "\\min \\mathcal G[X]",
    "free_energy_diff": "d\\mathcal G = d\\mathcal H - T_{\\text{eff}}\\,d\\mathcal S_{\\text{org}} - \\mathcal S_{\\text{org}}\\,dT_{\\text{eff}}",
    "nonequilibrium_flow": "\\frac{dX}{dt}=F_{\\text{drive}}(X)-F_{\\text{decay}}(X)",
    "steady_state": "\\left\\langle \\frac{dX}{dt}\\right\\rangle \\approx 0",
    "nonequilibrium_positive": "J_{\\text{in}}>0,\\qquad \\dot Q_{\\text{diss}}>0,\\qquad \\dot W_{\\text{useful}}>0",
    "microstate_energy": "E_i = E_i^{\\text{resource}} + E_i^{\\text{error}} + E_i^{\\text{latency}} + E_i^{\\text{governance}} - E_i^{\\text{reuse}}",
    "microstate_probability": "P_i=\\frac{e^{-E_i/(k_B T_{\\text{eff}})}}{Z}, \\qquad",
    "partition_function": "Z=\\sum_i e^{-E_i/(k_B T_{\\text{eff}})}",
    "entropy_balance": "\\frac{d\\mathcal S_{\\text{org}}}{dt}=\\Pi-\\Phi",
    "viability": "\\Phi \\ge \\Pi",
    "sovereign_efficiency": "\\eta_{\\text{sovereign}}=\\frac{\\dot W_{\\text{useful}}}{J_{\\text{in}}}",
    "archive_efficiency": "\\eta_{\\text{archive}}=\\frac{\\dot A_{\\text{reused}}}{J_{\\text{in}}}",
    "order_parameter": "\\Lambda=\\frac{\\rho_{\\text{reuse}}\\,\\rho_{\\text{validation}}\\,\\rho_{\\text{selection}}}{\\Pi}",
}


class DoctrineValidationError(RuntimeError):
    pass


LEGACY_BRACKET_EQUATION_PATTERN = re.compile(r"^\s*\[[^\]]*[\\_=^][^\]]*\]\s*$")


def _read_doctrine_docs(root: Path) -> dict[str, str]:
    payload = {}
    for rel in DOCTRINE_DOCS:
        path = root / rel
        if not path.exists():
            raise DoctrineValidationError(f"Missing doctrine file: {rel}")
        payload[rel] = path.read_text(encoding="utf-8")
    return payload


def validate_doctrine_markdown(root: Path) -> dict:
    docs = _read_doctrine_docs(root)
    joined = "\n".join(docs.values())

    if "\\[" in joined or "\\]" in joined:
        raise DoctrineValidationError("Legacy \\[ ... \\] equation delimiters detected in doctrine markdown.")
    for rel, text in docs.items():
        for line in text.splitlines():
            if LEGACY_BRACKET_EQUATION_PATTERN.match(line):
                raise DoctrineValidationError(
                    f"Legacy [ ... ] equation delimiter style detected in {rel}: `{line.strip()}`"
                )

    missing = [name for name, snippet in REQUIRED_EQUATIONS.items() if snippet not in joined]
    if missing:
        raise DoctrineValidationError(f"Missing required equations: {', '.join(missing)}")

    return {
        "doctrine_docs": sorted(docs.keys()),
        "required_equation_count": len(REQUIRED_EQUATIONS),
        "legacy_bracket_delimiters_present": False,
        "canonical_math_delimiters": "GitHub markdown $...$ and $$...$$",
        "validation": "pass",
    }


def build_doctrine_artifacts(root: Path, out_dir: Path) -> dict:
    validation = validate_doctrine_markdown(root)

    equation_catalog = {k: v for k, v in REQUIRED_EQUATIONS.items()}

    doctrine_stack = {
        "id": "protocol_cybersecurity_doctrine_stack_v1",
        "title": "Full-Stack Economic Organism Doctrine Stack",
        "positioning": "Protocol correctness is the first compounding correctness wedge under high-verification conditions.",
        "first_narrow_organ": "🌱💫 α-AGI Protocol Cybersecurity Sovereign 🔐",
        "future_seed": "👑 α-AGI Cybersecurity Sovereign 🔱✨",
        "nation_state_doctrine": (
            "The Full-Stack Economic Organism is governed as a driven nonequilibrium system: capital, compute, and "
            "telemetry are converted into proof-bound reusable security capability faster than entropy pressure "
            "from uncertainty, adversaries, and coordination loss."
        ),
        "not_claimed": [
            "A full cybersecurity sovereign already exists.",
            "Cybersecurity is solved once and for all.",
            "The thermodynamic framing is literal physical law.",
            "Real-world proof is already complete.",
        ],
        "organism_loop": [
            "Insight reduces blind search.",
            "Nova-Seeds generate structured fluctuations.",
            "MARK applies economic selection pressure.",
            "AGI Jobs converts candidate work into validated output through identity, proof, settlement, and governance.",
            "Archive freezes successful fluctuations into reusable structure.",
        ],
        "phase_transition": {
            "order_parameter": "Lambda",
            "consultancy_mode": "Lambda < Lambda_c",
            "compounding_mode": "Lambda > Lambda_c",
        },
        "equation_catalog": equation_catalog,
        "validation": validation,
    }

    thermodynamic_summary = {
        "id": "thermodynamic_model_summary_v1",
        "formal_status": "governance analogy with measurable operational content; not literal physical law",
        "boundary_statement": "Use thermodynamic/statistical-physics language as disciplined governance notation, not as a claim of settled empirical physical law for institutions.",
        "state_vector": ["K", "C", "D", "A", "Q", "R", "Sigma"],
        "state_vector_equation": "X(t)=\\big(K,C,D,A,Q,R,\\Sigma\\big)",
        "entropy_symbol": "S_org",
        "control_symbol": "Sigma",
        "viability_condition": "Phi >= Pi",
        "order_parameter_equation": "\\Lambda=\\frac{\\rho_{\\text{reuse}}\\,\\rho_{\\text{validation}}\\,\\rho_{\\text{selection}}}{\\Pi}",
        "efficiencies": ["eta_sovereign", "eta_archive"],
        "equation_catalog": equation_catalog,
        "validation": validation,
    }

    write_json(out_dir / "doctrine_stack.json", doctrine_stack)
    write_json(out_dir / "thermodynamic_model_summary.json", thermodynamic_summary)
    return {"doctrine_stack": doctrine_stack, "thermodynamic_model_summary": thermodynamic_summary}
