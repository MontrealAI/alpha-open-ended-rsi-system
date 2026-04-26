⚠️ This experiment is expected to FAIL before it succeeds.

The purpose of this pack is not to demonstrate success,
but to determine whether compounding actually occurs under real conditions.

# Adjacent-Mandate Reuse Proof — Real v1 Pack

This folder is a **repo-ready Q2 experiment pack** for proving the next milestone:

> **One completed mandate creates a frozen capability package that materially improves the next adjacent mandate under control conditions.**

It is designed for the `alpha-nova-seeds` repository and should be placed at:

```text
demos/adjacent_mandate_reuse_proof_real_v1/
```

## Chosen mandate pair

### Mandate 1 — Governance / dispute correctness
Primary scope:
- `contracts/CouncilGovernanceV25.sol`
- `contracts/ChallengePolicyModuleV25.sol`

Goal:
- produce a frozen reusable package called **`GovernanceValidationPack-v1`**

### Mandate 2 — Threshold / attestation correctness
Primary scope:
- `contracts/ThresholdNetworkAdapterV25.sol`
- `contracts/SignedAttestationVerifierV25.sol`

Goal:
- test whether `GovernanceValidationPack-v1` materially improves the adjacent mandate under **control vs treatment** conditions

## What this pack contains

- exact mandate specs
- freeze manifests
- reviewer instructions
- blinded reviewer forms
- scorecard templates
- proof-docket templates
- standard-library Python script for calculating the Q2 scorecard

## What must stay private

Do **not** commit the actual answer key or blinding map to a public repository.

Use:
- `05_private_local_only/answer_key_template.md`
- `05_private_local_only/blinded_assignment_map.template.csv`

Keep the filled versions private or in a restricted repository.

## Pass criteria

The treatment lane must beat the control lane by:

- **≥35% AOY uplift**
- **≥30% faster** time to first accepted output
- **≥40% lower** repair / rework
- **≥20% better** evidence completeness
- **no safety regression**
- **≥30%** of accepted treatment outputs explicitly depending on the frozen package

## Recommended execution order

1. Freeze scope, tools, reviewers, and cost model
2. Create a private answer key for Mandate 1 and Mandate 2
3. Run **Mandate 1**
4. Freeze `GovernanceValidationPack-v1`
5. Run **Mandate 2 Control** and **Mandate 2 Treatment** in parallel
6. Review both lanes with blinded reviewer packets
7. Fill the scorecard CSVs
8. Run the scorecard script
9. Publish the proof docket

## Fast start

From this folder:

```bash
python3 07_scripts/calculate_q2_scorecard.py
# optional: point to a results bundle
python3 07_scripts/calculate_q2_scorecard.py --scorecard-dir results_blinded_adjacent_transfer_v1/scorecard_outputs
```

By default this reads scorecards from `04_scorecard/` and writes outputs to `04_scorecard/out/`.
When `--scorecard-dir` is provided, outputs default to `<scorecard-dir>/out`.

## Blinded adjacent-transfer operational harness (v1)

This pack now includes an additive execution harness for a stricter blinded protocol run:

- setup script: `07_scripts/setup_blinded_adjacent_transfer_v1.py`
- private commitment hashing helper: `07_scripts/generate_private_commitment_hashes.py`
- packet normalization helper: `07_scripts/normalize_reviewer_packets.py`
- result bundle validator: `07_scripts/validate_blinded_results_bundle.py`
- reveal receipt helper (post-score-lock only): `07_scripts/assemble_reveal_packet.py`
- public-safe result path: `results_blinded_adjacent_transfer_v1/`
- local private-only path (git-ignored): `local_private_blinding_materials/`

Initialize from repo root:

```bash
python3 demos/adjacent_mandate_reuse_proof_real_v1/07_scripts/setup_blinded_adjacent_transfer_v1.py
```

This harness operationalizes Stage A and scaffolds Stage B, but does **not** fabricate missing human-blinded adjudication.

### Current execution boundary (public-safe)

The committed public-safe bundle at:

- `results_blinded_adjacent_transfer_v1/`

is intentionally bounded to the honest state:

- **Stage A:** operationalized and ready, pending real blinded human execution/adjudication
- **Stage B:** scaffolded only, blocked on a real Stage A pass

This repository state should be read as execution readiness + handoff discipline, not a completed real-world pass.

## File map

```text
00_manifest/
01_mandate_specs/
02_execution/
03_review/
04_scorecard/
05_private_local_only/
06_proof_docket/
07_scripts/
```

## Important note

This pack is **for a real-world proof attempt**, not a synthetic demo.

Its job is to help you answer one question cleanly:

> **Did the frozen capability package improve the next adjacent mandate under control conditions?**


## Demo ladder

- Flagship synthetic wedge demo: [`../protocol_smart_contract_correctness_demo/`](../protocol_smart_contract_correctness_demo/)
- Adjacent synthetic proof demo: [`../adjacent_mandate_reuse_proof_demo/`](../adjacent_mandate_reuse_proof_demo/)
- Real-world experiment pack: [`../adjacent_mandate_reuse_proof_real_v1/`](../adjacent_mandate_reuse_proof_real_v1/)
- Accelerating-loop demo: [`../open-ended-rsi-system/`](../open-ended-rsi-system/)
- Ladder index: [`../README.md`](../README.md)


## Orchestration command surface (blinded adjacent-transfer)

Use the deterministic orchestration script to run protocol steps without fabricating human evidence:

```bash
python3 07_scripts/run_blinded_adjacent_transfer.py prepare
python3 07_scripts/run_blinded_adjacent_transfer.py freeze-package
python3 07_scripts/run_blinded_adjacent_transfer.py build-kits
python3 07_scripts/run_blinded_adjacent_transfer.py validate-readiness
python3 07_scripts/run_blinded_adjacent_transfer.py assert
```

Additional commands are available for `commit-private`, `normalize-packets`, `lock-score`, `reveal`, and `assemble-public-docket`.
The harness stops at `READY_FOR_HUMAN_EXECUTION` when real human-blinded inputs are missing.
If a prior run has already advanced (for example to reveal/locked states), `prepare` will refuse to reset it unless you explicitly pass `--force-reset`.
