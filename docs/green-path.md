# Green path operator runbook (v2.6 RC)

The green path is the minimum successful operation flow from ingest to proof visibility.

## Steps

1. Run DB migrations in order (`001_init.sql`, then `002_v26_hardening.sql`).
2. Start API and indexer with the same RPC/network config.
3. Execute deterministic backfill command.
4. Check readiness endpoint.
5. Open dashboard green-path page and verify no critical alerts.
6. Verify release provenance artifacts before tagging/deploying.

## Success criteria

- `/health` and `/ready` return success.
- `/metrics` exposes ingestion and ledger counters.
- Reviewer ledger and council seat lifecycle pages are populated.
- Threshold schema validation tests pass.
