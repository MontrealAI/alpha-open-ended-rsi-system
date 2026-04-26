# Nova-Seeds v2.5 — Deployable Governance + Threshold Cryptography + Indexing Pack

Nova-Seeds v2.5 is the first package in this family intended to feel *operationally complete*.
It upgrades the v2.x line with four concrete capabilities:

1. **Real threshold-network SDK bindings**
   - Lit Protocol adapter using the current JS SDK package surface (`@lit-protocol/lit-client`, `@lit-protocol/auth`) on the Naga-era docs surface.
   - TACo / Threshold Access Control adapter using `@nucypher/taco`, `@nucypher/taco-auth`, and `ethers@5`, matching the current TACo integration docs.
2. **Signed attestation verification**
   - EIP-712 typed data verification for manifest attestations, decryption attestations, and challenge evidence.
3. **Delegated-voting snapshots + seat challenge policy**
   - Governance terms, nominations, delegation, on-chain checkpoints, and challenge adjudication hooks.
4. **Production event indexer + Postgres backend**
   - Dockerized FastAPI + Postgres + Redis starter with event indexing, normalized tables, REST API, and dashboard views.

## Production posture
This is a **deployable starter architecture**, not an audited release.
It is intended to accelerate implementation and review by giving engineering, security, and governance teams a common baseline.

## Package layout
- `contracts/` — Solidity contracts and interfaces
- `sdk/` — TypeScript SDK bindings for Lit and TACo
- `backend/` — FastAPI + Postgres + Redis event indexer/API
- `dashboard/` — Simple operator UI reading the API
- `migrations/` — SQL bootstrap for the indexer database

## External network bindings used
- Lit Protocol docs expose the current SDK package surface via `@lit-protocol/lit-client` and `@lit-protocol/auth`, with Naga-era references in the docs and FAQ.
- TACo docs specify `@nucypher/taco`, `@nucypher/taco-auth`, and explicitly note that TACo currently requires `ethers@5`.

## Security notes
- Threshold cryptography remains **off-chain**. The on-chain contracts govern requests, proofs, attestations, disputes, and policy.
- The dashboard/API assume a trusted deployment perimeter and should sit behind auth in real production.
- Challenge outcomes should be connected to real slashing / treasury policy before mainnet deployment.
