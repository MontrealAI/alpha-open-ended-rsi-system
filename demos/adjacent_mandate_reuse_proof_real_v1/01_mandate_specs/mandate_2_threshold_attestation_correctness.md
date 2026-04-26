# Mandate 2 — Threshold / attestation correctness

## Scope
Primary contracts:
- `contracts/ThresholdNetworkAdapterV25.sol`
- `contracts/SignedAttestationVerifierV25.sol`

## Objective
Determine whether **`GovernanceValidationPack-v1`** materially improves the adjacent mandate under:

- **Control**: no package access
- **Treatment**: package access allowed

## Deliverables
1. Structured findings list
2. Accepted negative-path tests or invariant/fuzz harnesses
3. Reviewer adjudication packet
4. Scorecard-ready evidence

## Primary issue classes to search
- domain-separation / replay weakness
- duplicate share / duplicate finalize path
- below-threshold finalize
- stale round reuse
- signer-set mismatch
- off-target attestation acceptance
- challenge / reveal deadline edge case
- event/state mismatch

## Required evidence fields for each accepted output
- code pointer
- broken condition / invariant
- reproduction witness or failing test
- severity rationale
- suggested fix
- replay artifact or trace

## Lane discipline
Control and treatment must use:
- same repo SHA
- same contract scope
- same time budget
- same compute budget
- same reviewer rubric
- same cost model

Only difference:
- treatment may use `GovernanceValidationPack-v1`
- control may not use it
