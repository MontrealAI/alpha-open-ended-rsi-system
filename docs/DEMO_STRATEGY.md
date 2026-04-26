# Demo Strategy — v2.8.0-rc.2

This repository uses a four-surface demo ladder so proof boundaries stay explicit.

## Ladder structure

### 1) Flagship synthetic wedge demo

- Path: [`../demos/protocol_smart_contract_correctness_demo/`](../demos/protocol_smart_contract_correctness_demo/)
- Role: primary public/operator walkthrough
- Proves: deterministic protocol-correctness wedge mechanics
- Does not prove: real-world external validity

### 2) Adjacent synthetic proof demo

- Path: [`../demos/adjacent_mandate_reuse_proof_demo/`](../demos/adjacent_mandate_reuse_proof_demo/)
- Role: compact replay surface
- Proves: minimal adjacent threshold gate structure
- Does not prove: institutional deployment performance

### 3) Real-world experiment pack

- Path: [`../demos/adjacent_mandate_reuse_proof_real_v1/`](../demos/adjacent_mandate_reuse_proof_real_v1/)
- Role: controlled experiment templates and scoring process
- Proves: only when run with blinded real data and published docket evidence


### 4) Accelerating-loop demo

- Path: [`../demos/open-ended-rsi-system/`](../demos/open-ended-rsi-system/)
- Role: bounded accelerating-loop demonstration (bounded → expanding → increasingly autonomous)
- Proves: deterministic package heredity, adjacent treatment advantage, and whitelist-bounded mandate-3 selection
- Does not prove: unrestricted autonomy or broad sovereign completion

## Why protocol correctness is first

The first wedge is protocol + smart-contract correctness because verification quality, replay fidelity, and evidence objectivity are strongest there.

That allows Archive density to build early and gives operators a fast review cycle.

## Naming policy

Public-facing language now prefers:

- **Protocol Cybersecurity Studio**
- **ProtocolCybersecurityPack-v1**
- **ProtocolCybersecuritySovereign-v1.synthetic.json**

Legacy “Assurance” aliases remain for compatibility where deterministic replay references already depend on them.

## Smoke-run commands

- `python3 demos/protocol_smart_contract_correctness_demo/run_demo.py --assert`
- `python3 demos/adjacent_mandate_reuse_proof_demo/run_demo.py`
- `python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/calculate_q2_scorecard.py`
- `python3 demos/open-ended-rsi-system/run_demo.py --assert`
- `python scripts/check_demo_links.py`

## Explicit boundary

This RC supports a narrow synthetic wedge claim for 🌱💫 α‑AGI Protocol Cybersecurity Sovereign 🔐.

The broader 👑 α‑AGI Cybersecurity Sovereign 🔱✨ remains future-facing and not yet claimed as proven.
