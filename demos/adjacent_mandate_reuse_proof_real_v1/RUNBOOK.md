# Runbook

For blinded adjacent-transfer execution scaffolding, initialize:

```bash
python3 07_scripts/setup_blinded_adjacent_transfer_v1.py
```

This creates:

- public-safe result workspace: `results_blinded_adjacent_transfer_v1/`
- private local-only workspace: `local_private_blinding_materials/results_blinded_adjacent_transfer_v1/`

## Phase 0 — Freeze
Complete:
- `00_manifest/experiment_manifest.template.json`
- `00_manifest/environment_lock.template.json`
- `00_manifest/package_hash_record.template.json` (initial placeholders only)
- `02_execution/run_register.template.csv`
- private answer key + blinded assignment map
- private commitment hashes (`07_scripts/generate_private_commitment_hashes.py`)

## Phase 1 — Mandate 1
Use:
- `01_mandate_specs/mandate_1_governance_dispute_correctness.md`
- `03_review/reviewer_form_mandate_1.template.md`

Output:
- accepted findings
- accepted harnesses/tests
- `GovernanceValidationPack-v1`
- settlement receipts
- chronicle entry draft

## Phase 2 — Freeze package
Record:
- package hash
- exact included files
- no-edit attestation

## Phase 3 — Mandate 2
Run both:
- control lane with `02_execution/control_lane_instructions.md`
- treatment lane with `02_execution/treatment_lane_instructions.md`

## Phase 4 — Review
Use:
- `03_review/reviewer_form_mandate_2_control.template.md`
- `03_review/reviewer_form_mandate_2_treatment.template.md`
- `03_review/adjudication_form.template.md`

## Phase 5 — Score
Fill:
- `04_scorecard/run_costs.template.csv`
- `04_scorecard/output_scoring.template.csv`

Then run:

```bash
python3 07_scripts/calculate_q2_scorecard.py
```

## Phase 6 — Publish
Complete the proof docket templates in `06_proof_docket/` using the calculated outputs.


## Deterministic orchestration (recommended)

From this folder:

```bash
python3 07_scripts/run_blinded_adjacent_transfer.py prepare
python3 07_scripts/run_blinded_adjacent_transfer.py freeze-package
python3 07_scripts/run_blinded_adjacent_transfer.py build-kits
python3 07_scripts/run_blinded_adjacent_transfer.py validate-readiness
python3 07_scripts/run_blinded_adjacent_transfer.py assert
```

For post-human steps, use:

- `python3 07_scripts/run_blinded_adjacent_transfer.py lock-score`
- `python3 07_scripts/run_blinded_adjacent_transfer.py reveal`
- `python3 07_scripts/run_blinded_adjacent_transfer.py assemble-public-docket`

Safety note: rerunning `prepare` after an advanced run state is blocked by default to avoid overwriting revealed/locked artifacts. Use `--force-reset` only when intentionally reinitializing.
