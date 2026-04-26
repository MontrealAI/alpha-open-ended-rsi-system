#!/usr/bin/env python3
"""Check doctrine markdown for canonical GitHub math style and required equations."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "docs" / "THERMODYNAMIC_MODEL.md",
    ROOT / "demos" / "protocol_smart_contract_correctness_demo" / "docs" / "THERMODYNAMIC_MODEL.md",
]
REQUIRED = [
    r"X(t)=\big(K,C,D,A,Q,R,\Sigma\big)",
    r"J_{\text{in}}=\alpha_K \dot K_{\text{in}}+\alpha_C \dot C_{\text{in}}+\alpha_D \dot D_{\text{in}}",
    r"J_{\text{in}}=\dot W_{\text{useful}}+\dot Q_{\text{diss}}+\dot U",
    r"\dot W_{\text{useful}} \approx \beta_A \dot A + \beta_Q \dot Q + \beta_R \dot R_{\text{validated}}",
    r"\mathcal G[X]=\mathcal H[X]-T_{\text{eff}}\mathcal S_{\text{org}}[X]",
    r"\min \mathcal G[X]",
    r"d\mathcal G = d\mathcal H - T_{\text{eff}}\,d\mathcal S_{\text{org}} - \mathcal S_{\text{org}}\,dT_{\text{eff}}",
    r"\frac{dX}{dt}=F_{\text{drive}}(X)-F_{\text{decay}}(X)",
    r"\left\langle \frac{dX}{dt}\right\rangle \approx 0",
    r"J_{\text{in}}>0,\qquad \dot Q_{\text{diss}}>0,\qquad \dot W_{\text{useful}}>0",
    r"E_i = E_i^{\text{resource}} + E_i^{\text{error}} + E_i^{\text{latency}} + E_i^{\text{governance}} - E_i^{\text{reuse}}",
    r"P_i=\frac{e^{-E_i/(k_B T_{\text{eff}})}}{Z}, \qquad",
    r"Z=\sum_i e^{-E_i/(k_B T_{\text{eff}})}",
    r"\frac{d\mathcal S_{\text{org}}}{dt}=\Pi-\Phi",
    r"\Phi \ge \Pi",
    r"\eta_{\text{sovereign}}=\frac{\dot W_{\text{useful}}}{J_{\text{in}}}",
    r"\eta_{\text{archive}}=\frac{\dot A_{\text{reused}}}{J_{\text{in}}}",
    r"\Lambda=\frac{\rho_{\text{reuse}}\,\rho_{\text{validation}}\,\rho_{\text{selection}}}{\Pi}",
]
LEGACY_LINE = re.compile(r"^\s*\[[^]]*[\\_=^][^]]*\]\s*$")


def main() -> int:
    bad = []
    for path in TARGETS:
        if not path.exists():
            bad.append(f"missing: {path.relative_to(ROOT)}")
            continue
        text = path.read_text(encoding="utf-8")
        if "\\[" in text or "\\]" in text:
            bad.append(f"legacy delimiters \\[ ... \\] in {path.relative_to(ROOT)}")
        for i, line in enumerate(text.splitlines(), start=1):
            if LEGACY_LINE.match(line):
                bad.append(f"legacy [ ... ] pseudo-equation in {path.relative_to(ROOT)}:{i}")
        missing = [snippet for snippet in REQUIRED if snippet not in text]
        if missing:
            bad.append(
                f"missing required equations in {path.relative_to(ROOT)}: {len(missing)}"
            )

    if bad:
        print("FAIL")
        for b in bad:
            print(f"- {b}")
        return 1

    print("PASS: doctrine math markdown checks succeeded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
