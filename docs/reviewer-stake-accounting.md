# Reviewer stake accounting (v2.6 RC)

This note explains deterministic reviewer reward/slash visibility.

## Ledger model

`reviewer_stake_ledger` tracks immutable deltas by event:

- `accrual`: reviewer earned stake/reward
- `slash`: reviewer stake reduced
- `claim`: reviewer claimed reward token amount

Each row includes:
- reviewer address
- delta (signed numeric)
- reason/reference hash
- transaction hash and block number

## Determinism rule

For a given `(tx_hash, log_index)` there is at most one ledger row. Re-processing the same block range must not duplicate deltas.

## Operator checks

- Sum by reviewer should match treasury read-model expectations.
- Negative net totals indicate slash-heavy periods and should be investigated.
