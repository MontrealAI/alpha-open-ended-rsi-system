# Security testing posture (contracts)

This repository is a **verifiable release candidate** and should be treated as hardening-in-progress.

## Security test stack

The contracts subsystem uses layered testing:

1. Hardhat integration tests for deployment posture and integration wiring.
2. Foundry Solidity tests for unit, fuzz, and invariant checks.
3. Echidna transaction-sequence property tests for high-risk surfaces.
4. Slither static analysis for detector-based regression catching.

## Risk surfaces covered

- unauthorized lifecycle mutation,
- reviewer reward accounting regressions,
- threshold profile misconfiguration,
- governance seat/challenge lifecycle misuse,
- registry lifecycle ordering failures,
- expired decryption attestation rejection,
- policy-mismatch challenge voting rejection,
- attestation trust/replay boundary regressions.

## What this does not claim

This testing layer does not claim the contracts are:

- audited,
- production-final,
- proven under all adversarial market conditions.

Independent review and formal audit remain required for high-stakes deployment decisions.


## CI gates

`.github/workflows/contracts-security.yml` enforces compile + Foundry unit/fuzz/invariant + Slither on pushes/PRs touching contracts, runs Echidna smoke campaigns on PR/push to catch harness/config regressions, and runs full Echidna campaigns on schedule/dispatch for deeper sequence-level adversarial pressure (treasury, governance, threshold, registry, workflow, attestation verifier trust boundaries).

`docs/contracts-risk-matrix.md` is the contract-by-contract source of truth for covered invariants, mapped tests, and residual audit-only risk.
