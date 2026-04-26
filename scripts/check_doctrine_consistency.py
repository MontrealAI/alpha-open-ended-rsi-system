#!/usr/bin/env python3
"""Lightweight doctrine consistency checks for v2.8.x RC surfaces."""

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

README_DOCTRINE_LINKS = [
    "docs/DOCTRINE_STACK.md",
    "docs/THERMODYNAMIC_MODEL.md",
    "docs/NATION_STATE_DOCTRINE.md",
    "docs/DEMO_STRATEGY.md",
    "docs/RELEASE_POSITIONING.md",
    "docs/FRONTIER_LAB_POSTURE.md",
]

DEMO_LADDER_LINKS = [
    "demos/protocol_smart_contract_correctness_demo/",
    "demos/adjacent_mandate_reuse_proof_demo/",
    "demos/adjacent_mandate_reuse_proof_real_v1/",
    "demos/open-ended-rsi-system/",
    "demos/unbounded-rsi-system/",
    "demos/README.md",
]

THERMO_FILES = [
    ROOT / "docs" / "THERMODYNAMIC_MODEL.md",
    ROOT / "demos" / "protocol_smart_contract_correctness_demo" / "docs" / "THERMODYNAMIC_MODEL.md",
]

CANONICAL_EQUATIONS = {
    "X(t)": r"X(t)=\big(K,C,D,A,Q,R,\Sigma\big)",
    "J_in_resource": r"J_{\text{in}}=\alpha_K \dot K_{\text{in}}+\alpha_C \dot C_{\text{in}}+\alpha_D \dot D_{\text{in}}",
    "J_in_partition": r"J_{\text{in}}=\dot W_{\text{useful}}+\dot Q_{\text{diss}}+\dot U",
    "W_useful": r"\dot W_{\text{useful}} \approx \beta_A \dot A + \beta_Q \dot Q + \beta_R \dot R_{\text{validated}}",
    "G": r"\mathcal G[X]=\mathcal H[X]-T_{\text{eff}}\mathcal S_{\text{org}}[X]",
    "minG": r"\min \mathcal G[X]",
    "dG": r"d\mathcal G = d\mathcal H - T_{\text{eff}}\,d\mathcal S_{\text{org}} - \mathcal S_{\text{org}}\,dT_{\text{eff}}",
    "dXdt": r"\frac{dX}{dt}=F_{\text{drive}}(X)-F_{\text{decay}}(X)",
    "steady": r"\left\langle \frac{dX}{dt}\right\rangle \approx 0",
    "throughputs": r"J_{\text{in}}>0,\qquad \dot Q_{\text{diss}}>0,\qquad \dot W_{\text{useful}}>0",
    "Ei": r"E_i = E_i^{\text{resource}} + E_i^{\text{error}} + E_i^{\text{latency}} + E_i^{\text{governance}} - E_i^{\text{reuse}}",
    "Pi": r"P_i=\frac{e^{-E_i/(k_B T_{\text{eff}})}}{Z}, \qquad",
    "Z": r"Z=\sum_i e^{-E_i/(k_B T_{\text{eff}})}",
    "dS": r"\frac{d\mathcal S_{\text{org}}}{dt}=\Pi-\Phi",
    "Phi": r"\Phi \ge \Pi",
    "eta_sovereign": r"\eta_{\text{sovereign}}=\frac{\dot W_{\text{useful}}}{J_{\text{in}}}",
    "eta_archive": r"\eta_{\text{archive}}=\frac{\dot A_{\text{reused}}}{J_{\text{in}}}",
    "Lambda": r"\Lambda=\frac{\rho_{\text{reuse}}\,\rho_{\text{validation}}\,\rho_{\text{selection}}}{\Pi}",
}

LEGACY_LINE = re.compile(r"^\s*\[[^\]]*[\\_=^][^\]]*\]\s*$")


def _normalize(line: str) -> str:
    return " ".join(line.strip().split())


def main() -> int:
    errors: list[str] = []

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for link in README_DOCTRINE_LINKS:
        if link not in readme:
            errors.append(f"README missing doctrine link: {link}")
        if not (ROOT / link).exists():
            errors.append(f"README doctrine link target missing: {link}")
    for link in DEMO_LADDER_LINKS:
        if link not in readme:
            errors.append(f"README missing demo ladder link: {link}")
        if not (ROOT / link).exists():
            errors.append(f"README demo ladder link target missing: {link}")

    demos_readme = (ROOT / "demos" / "README.md").read_text(encoding="utf-8")
    ladder_role_checks = [
        "Flagship synthetic wedge demo",
        "Adjacent synthetic proof demo",
        "Real-world proof pack",
        "Accelerating-loop demo",
    ]
    for phrase in ladder_role_checks:
        if phrase not in demos_readme:
            errors.append(f"demos/README.md missing ladder role phrase: {phrase}")
    for link in DEMO_LADDER_LINKS[:-1]:
        rel_link = link.replace("demos/", "./")
        if rel_link not in demos_readme:
            errors.append(f"demos/README.md missing relative demo link: {rel_link}")

    seen_by_file: dict[str, set[str]] = {}

    for thermo in THERMO_FILES:
        rel = thermo.relative_to(ROOT)
        if not thermo.exists():
            errors.append(f"missing thermodynamic file: {rel}")
            continue
        text = thermo.read_text(encoding="utf-8")
        if "\\[" in text or "\\]" in text:
            errors.append(f"legacy \\[ ... \\] delimiter in {rel}")
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if LEGACY_LINE.match(line):
                errors.append(f"legacy [ ... ] pseudo-equation in {rel}:{i}")
        found = set()
        for key, eq in CANONICAL_EQUATIONS.items():
            if eq not in text:
                errors.append(f"missing canonical equation {key} in {rel}")
            else:
                found.add(_normalize(eq))

        # conflict check: for recognizable LHS markers, a non-canonical equation line is flagged.
        lhs_markers = [
            "X(t)=",
            "J_{\\text{in}}=",
            "\\mathcal G[X]=",
            "\\frac{dX}{dt}=",
            "\\frac{d\\mathcal S_{\\text{org}}}{dt}=",
            "\\Lambda=",
        ]
        canonical_norm = {_normalize(v) for v in CANONICAL_EQUATIONS.values()}
        for i, line in enumerate(lines, start=1):
            norm = _normalize(line)
            if not norm:
                continue
            if any(marker in norm for marker in lhs_markers) and "=" in norm and norm not in canonical_norm:
                errors.append(f"potential conflicting doctrine equation in {rel}:{i}: {line.strip()}")

        seen_by_file[str(rel)] = found

    if len(seen_by_file) == len(THERMO_FILES):
        a, b = seen_by_file.values()
        if a != b:
            errors.append("thermodynamic equation sets diverge between root and flagship docs")

    if errors:
        print("FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS: doctrine consistency checks succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
