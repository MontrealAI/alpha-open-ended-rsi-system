# v2.6.0-rc.1 release checklist

## Acceptance criteria

- [ ] Backend proof and governance endpoints return deterministic data.
- [ ] Threshold schemas validate canonical examples/tests.
- [ ] Release provenance bundle generated (source archive + SHA256SUMS + SBOM + attestation).
- [ ] Dashboard shows seeds/rounds/reviewer ledger/council seats/lineage/provenance/alerts + green-path guidance.

## Migration notes

1. Apply `backend/migrations/001_init.sql`.
2. Apply `backend/migrations/002_v26_hardening.sql`.
3. Restart API and indexer workers.
4. Run deterministic backfill (`python -m app.backfill --from-block <START> --to-block <END>`).
5. Validate `/ready`, `/proof/summary`, and `/metrics`.

## Provenance artifacts

- `alpha-nova-seeds-<TAG>.tar.gz`
- `provenance-manifest-<TAG>.json`
- `sbom-<TAG>.spdx.json`
- `SHA256SUMS`
- GitHub build attestation

## Rollback notes

1. Stop indexer/API.
2. Drop additive v2.6 tables/views only:
   - `indexer_state`
   - `reviewer_stake_ledger`
   - `council_seat_lifecycle`
   - `reviewer_stake_balances`
   - `council_active_seat_count`
3. Deploy previous backend image.
4. Re-run indexer from previous stable cursor.
