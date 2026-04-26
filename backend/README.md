# Nova-Seeds v2.6 RC backend

FastAPI + Postgres indexer backend focused on proof/readiness hardening.

## Capabilities

- Versioned SQL migrations (`001_init.sql`, `002_v26_hardening.sql`)
- Idempotent + reorg-safe event ingestion cursor
- Health + readiness endpoints (`/health`, `/ready`)
- Governance accounting APIs (`/governance/reviewer-ledger`, `/governance/council-seats`)
- Proof summary API (`/proof/summary`)
- Metrics endpoint (`/metrics`)
- OpenAPI export (`/openapi.json`)
- Deterministic backfill command (`python -m app.backfill`)

## Quick start

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Deterministic backfill

```bash
python -m app.backfill --from-block 0 --to-block 100000
```

## Migration order

1. `backend/migrations/001_init.sql`
2. `backend/migrations/002_v26_hardening.sql`

## Rollback note

To roll back v2.6 read models, drop only additive v2.6 objects (`indexer_state`, `reviewer_stake_ledger`, `council_seat_lifecycle`, `reviewer_stake_balances`, `council_active_seat_count`) and restart with v2.5 API/indexer behavior.
