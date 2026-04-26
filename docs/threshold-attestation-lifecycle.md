# Threshold attestation lifecycle (v2.6 RC)

This document defines the operator lifecycle for threshold encryption/decryption attestations.

## Lifecycle steps

1. **Bind profile**
   - Create a threshold binding profile tied to a seed and access policy.
   - Store it using `schemas/v2.6/threshold-binding-profile.schema.json`.
2. **Open decryption request**
   - Record request id, ciphertext hash, and requester identity.
3. **Collect shares**
   - Threshold network signers submit partial signatures.
4. **Finalize attestation**
   - Produce a decryption attestation using `schemas/v2.6/decryption-attestation.schema.json`.
5. **Index + verify**
   - Backend indexes the event and surfaces status in proof endpoints and dashboard.

## Validation requirements

- `schemaVersion` must be `2.6`.
- Hash fields must be 32-byte hex values.
- Collected shares must meet or exceed required shares.
- Attestation must include at least one signer entry.

## Non-goal

This RC does not claim cryptographic audit completeness; it standardizes data contracts and verification flow.
