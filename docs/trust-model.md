# Trust model (v2.6 RC)

## Objective

Define who must be trusted for Nova-Seeds identity and proof flows to function.

## Trust boundaries

1. **Identity layer**
   - Seed IDs and metadata hashes are trusted from signed on-chain transactions.
2. **Proof layer**
   - Threshold attestations are trusted when signer quorum + schema validation pass.
3. **Settlement layer**
   - Reward/slash accounting is trusted from deterministic event indexing and unique `(tx_hash, log_index)` keys.
4. **Governance layer**
   - Council lifecycle is trusted from governance events plus challenge resolution outcomes.

## Assumptions

- RPC endpoint returns canonical chain data for finalized blocks.
- Operators run indexer with configured confirmation depth.
- Release provenance artifacts are checked before deployment.

## Unknowns

- External signer key management practices are out of scope for this RC.
