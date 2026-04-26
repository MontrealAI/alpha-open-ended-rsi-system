# Mandate 1 — Governance / dispute correctness

## Scope
Primary contracts:
- `contracts/CouncilGovernanceV25.sol`
- `contracts/ChallengePolicyModuleV25.sol`

## Objective
Produce a reusable frozen capability package:

**`GovernanceValidationPack-v1`**

## Deliverables
1. Structured findings list
2. Accepted negative-path tests or invariant/fuzz harnesses
3. Reusable ontology + schema + mechanism library
4. Workflow template for future review runs
5. Reviewer-approved proof packet

## Allowed output types
- accepted high-severity finding with repro or failing test
- accepted medium-severity finding with repro or failing test
- accepted low-severity finding with code pointer and reviewer acceptance
- accepted invariant / fuzz harness
- accepted hardening recommendation

## Primary issue classes to search
- unauthorized governance action path
- impossible seat transition
- quorum / threshold misconfiguration
- stale challenge or resolution edge case
- pause bypass
- event/state mismatch
- finalize-before-window edge case
- bond / reward accounting inconsistency

## Required evidence fields for each accepted output
- code pointer
- broken condition / invariant
- reproduction witness or failing test
- severity rationale
- suggested fix
- replay artifact or trace

## Out of scope
- style-only issues
- gas micro-optimizations
- broad architectural rewrite suggestions
- speculative claims without reproduction support

## Package freeze rule
Nothing from the package may be edited once Mandate 2 begins.
