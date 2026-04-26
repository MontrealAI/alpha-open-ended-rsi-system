# Ascension Runtime (bounded local/devnet)

This demo is the **Minimum Viable Ascension Runtime** for local/devnet replay.

It executes a deterministic loop:
Insight → Nova-Seeds → MARK → Sovereign → AGI Business → Marketplace → AGI Jobs → Agents → Validators/Council → Value Reservoir → Nodes → Archive → Architect/next loop.

## Claim boundary

This runtime is proof-first and bounded.
It does **not** claim audited-final deployment, mainnet readiness, real token-value settlement, or completed live α‑AGI Ascension.

## Run

```bash
python3 demos/ascension-runtime/run_demo.py --assert
```

## Demonstrated vs simulated vs unproven

### Demonstrated (deterministic local artifacts)
- Insight packet and rationale
- Five Nova-Seed packets
- MARK ranking and selection report
- Sovereign formation artifacts
- Two AGI Jobs with completion and receipts
- Agent competition and selection logs
- Validation round + council ruling
- Reservoir ledger, archive lineage, and architect recommendation
- Layer scorecard and report outputs

### Simulated (explicitly non-live)
- Marketplace order routing and escrow placeholders
- MARK allocation/orderbook behavior
- Reservoir fee/burn accounting units

### Unproven / pending
- Live DEX behavior
- Mainnet token settlement
- External-market proof
- Audited final deployment posture

## Demo ladder

- Back to demo ladder index: [`../README.md`](../README.md)
