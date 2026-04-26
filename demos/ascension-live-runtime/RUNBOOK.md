# RUNBOOK — Ascension Live Runtime (bounded local/devnet)

## Preconditions

- Python 3.10+ available.
- Repository checked out locally.

## Execute

```bash
python3 demos/ascension-live-runtime/run_demo.py --assert
```

## Operator checks

1. Confirm scorecard exists: `demos/ascension-live-runtime/out/ascension_runtime_scorecard.json`.
2. Confirm at least three seeds in `out/nova_seed_registry_snapshot.json`.
3. Confirm at least two bids in `out/marketplace_round.json`.
4. Confirm validator approval in `out/validation_round.json`.
5. Confirm council ruling in `out/council_ruling.json`.
6. Confirm non-zero validated ledger entry in `out/reservoir_ledger.json`.
7. Confirm archive lineage + architect recommendation artifacts exist.

## Replayability

- Runtime event stream is in `out/events.json`.
- Job-scoped event stream is in `out/jobs/job_event_log.json`.
- Validation attestation stores file hashes for deterministic integrity checking.

## Boundary reminders

- Local/devnet bounded runtime only.
- No external APIs are required.
- No real token-value settlement is claimed.
