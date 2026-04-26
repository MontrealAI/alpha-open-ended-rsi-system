# Contributing to alpha-nova-seeds

Thanks for helping ship Nova-Seeds v2.6 as a **verifiable release candidate**.

## Contribution contract

1. Keep implementation aligned to: **identity → proof → settlement → governance**.
2. Preserve stack choices: **Solidity contracts**, **FastAPI + Postgres backend**.
3. Prefer additive hardening and release engineering over rewrites.
4. Keep claims testable. Do not label changes as audited or production-final.

## Pull request checklist

- [ ] Acceptance criteria are explicit and testable.
- [ ] Migration notes are included when schema or API changes occur.
- [ ] Provenance artifacts are updated (manifest + SHA256SUMS + attestation workflow).
- [ ] Rollback notes are included for operators.
- [ ] Tests/lint checks were run locally and listed in PR body.

## Development flow

1. Create a focused branch.
2. Implement small, reviewable commits.
3. Run local checks before opening PR:
   - backend unit tests
   - schema validation tests
   - SDK type checks
4. Update docs in plain English first.

## Non-goals for v2.6 RC

- Final security audit claims.
- Mainnet deployment guarantees.
- Architectural rewrites.
