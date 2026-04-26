# Nova-Seeds v2.6 RC SDK bindings

TypeScript adapters and shared types for threshold cryptography integration.

## Included adapters
- `lit/` — Lit Protocol integration helpers.
- `taco/` — TACo integration helpers.
- `shared/` — common typed-data and schema-aligned payload types.

## v2.6 additions

`shared/types.ts` now includes schema-aligned interfaces:
- `V26ThresholdBindingProfile`
- `V26DecryptionAttestation`

These mirror canonical schemas under `schemas/v2.6/` and support round-trip JSON validation in backend tests.

## RC posture

These SDK surfaces support proof workflows for the release candidate. They are not an audit guarantee.
