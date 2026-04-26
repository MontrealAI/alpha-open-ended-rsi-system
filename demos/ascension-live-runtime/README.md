# Ascension Live Runtime (bounded local/devnet)

This demo implements a **bounded local/devnet Minimum Viable Ascension Runtime** that links:

Insight → Nova-Seeds → MARK → Sovereign → Business → Marketplace → AGI Jobs → Agents → Validators/Council → Value Reservoir → Architect → Archive.

## Claim boundary

This is a verifiable release-candidate runtime for local/devnet replay only.
It **does not** claim audited-final safety, mainnet readiness, real external-market proof, or completed α‑AGI Ascension.

## Run

```bash
python3 demos/ascension-live-runtime/run_demo.py --assert
```

## Key outputs

- `out/insight_packet.json`
- `out/nova_seed_registry_snapshot.json`
- `out/mark_selection_report.json`
- `out/sovereign_manifest.json`
- `out/business_operating_plan.json`
- `out/marketplace_round.json`
- `out/jobs/job_receipt.json`
- `out/validation_round.json`
- `out/council_ruling.json`
- `out/reservoir_ledger.json`
- `out/archive_lineage.json`
- `out/architect_recommendation.json`
- `out/ascension_runtime_scorecard.json`
- `out/reports/ascension_live_runtime_report.md`
- `out/reports/ascension_live_runtime_report.html`

## Verification notes

- Event log is emitted to `out/events.json` with hash-linked payloads.
- Validator attestation includes file hashes used for deterministic replay.
- Schema presence checks are enforced against `schemas/v2.8/*.schema.json`.


## Demo ladder link

- Back to ladder index: [`../README.md`](../README.md)
