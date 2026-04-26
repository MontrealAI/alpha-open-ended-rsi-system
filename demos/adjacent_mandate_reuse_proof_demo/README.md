# Adjacent-Mandate Reuse Proof Demo

This is the **compact synthetic adjacent proof demo** in the ladder.

It is intentionally small, local, and reproducible.

## What it demonstrates

- Parent sector: **Protocol and smart-contract correctness**
- Mandate 1: review a first batch of smart-contract mandates
- Freeze the resulting reusable package as:
  - `ProtocolCybersecurityPack-v1` (legacy alias: `ProtocolAssurancePack-v1`)
- Mandate 2: review an **adjacent** batch twice:
  - **control** without the package
  - **treatment** with the frozen package
- Score the result against the adjacent-mandate proof gate

## How to run

```bash
python3 run_demo.py
```

No extra dependencies are required.

## Best files to open

- `demo_output/reports/report.html`
- `demo_output/reports/report.md`
- `demo_output/proof_docket/06_scorecard.md`

## Important note

This is a **synthetic local demo**, not a real-world proof.
It shows the structure of the milestone:
one completed mandate can create a frozen capability package that materially improves the next adjacent mandate under control conditions.

## Current synthetic result

- Adjacent-mandate proof: **PASS**
- Package hash: `b9365fcdaff0141af0c27aa20a458c20ea25582220887735438d645144accef0`

## Demo ladder

- Flagship synthetic wedge demo: [`../protocol_smart_contract_correctness_demo/`](../protocol_smart_contract_correctness_demo/)
- Adjacent synthetic proof demo: [`../adjacent_mandate_reuse_proof_demo/`](../adjacent_mandate_reuse_proof_demo/)
- Real-world experiment pack: [`../adjacent_mandate_reuse_proof_real_v1/`](../adjacent_mandate_reuse_proof_real_v1/)
- Accelerating-loop demo: [`../unbounded-rsi-system/`](../unbounded-rsi-system/)
- Ladder index: [`../README.md`](../README.md)

## Claim boundary

This compact synthetic demo supports only a narrow claim: frozen package reuse can be measured in an adjacent mandate under deterministic control-vs-treatment conditions.

It does **not** claim that the broader 👑 α‑AGI Cybersecurity Sovereign 🔱✨ is already proven.
