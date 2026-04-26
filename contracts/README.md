# Nova-Seeds contracts map (v2.6 RC posture)

This package contains Solidity surfaces for Nova-Seeds on-chain anchors.

Doctrine alignment:

1. **identity**
2. **proof**
3. **settlement**
4. **governance**

This is a **verifiable release candidate** surface, not an audited final deployment claim.

## Contract roles

- `AlphaNovaSeedV25.sol` — seed identity NFT anchor.
- `NovaSeedRegistryV25.sol` — lifecycle registry and review transitions.
- `SignedAttestationVerifierV25.sol` — EIP-712 digest/signature verification.
- `ThresholdNetworkAdapterV25.sol` — threshold-network request lifecycle.
- `NovaSeedWorkflowAdapterV25.sol` — workflow bridge for assay jobs.
- `ChallengePolicyModuleV25.sol` — challenge adjudication policy.
- `ReviewerRewardTreasuryV25.sol` — reviewer reward accounting.
- `CouncilGovernanceV25.sol` — council terms, seats, delegation, bonded challenges.

## Tooling in this workspace

The package intentionally keeps the existing Hardhat deployment stack and adds security testing layers:

- **Hardhat**: deployment scripts and TypeScript integration tests.
- **Foundry**: Solidity unit, fuzz, and invariant tests in `foundry-test/`.
- **Slither**: static analysis with fail-loud severity gates.
- **Echidna**: sequence/property fuzzing harnesses in `echidna/harnesses/`.

## Commands

From repository root:

```bash
npm run contracts:build
npm run contracts:test
npm run test:contracts:unit
npm run test:contracts:fuzz
npm run test:contracts:invariant
npm run analyze:slither
npm run test:contracts:echidna
```

Or from `contracts/` directly:

```bash
npm run build
npm run test
npm run test:contracts:unit
npm run test:contracts:fuzz
npm run test:contracts:invariant
npm run analyze:slither
npm run test:contracts:echidna
```

## What each layer proves

- **Hardhat tests**: integration wiring and deployment posture checks.
- **Foundry unit tests**: revert-path and lifecycle guardrails for each contract.
- **Foundry fuzz/invariant tests**: arithmetic, identity-validation, signature-shape, and state-coherence boundaries.
- **Echidna harnesses**: adversarial transaction-sequence properties for treasury, governance, threshold, registry, and workflow interactions.
- **Slither**: static detector sweep to catch common anti-patterns/regressions.

Contract-by-contract risk classification, mapped invariants, and explicitly out-of-scope audit items are documented in `docs/contracts-risk-matrix.md`.

## Out of scope

This layer increases testable evidence but does **not** prove:

- economic game-theory robustness under all external actors,
- cryptographic implementation correctness of external threshold networks,
- production-final audit status.

Use this package with operator review, threat-model review, and independent audit processes.
