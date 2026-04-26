# Threat model (v2.6 RC)

## In-scope threats

- Event replay causing duplicate accounting entries.
- Short chain reorgs causing stale/non-canonical projections.
- Malformed threshold attestation payloads.
- Operator misconfiguration during release rollout.

## Mitigations in this RC

- Idempotent insertion with `(tx_hash, log_index)` uniqueness.
- Reorg-safe ingestion window + confirmation depth cursor.
- Canonical JSON Schemas with automated validation tests.
- Release provenance workflow with checksums/SBOM/attestation.

## Out-of-scope threats

- Economic game theory analysis of council capture.
- Full cryptographic audit of threshold signer implementations.
- Final production deployment hardening.
