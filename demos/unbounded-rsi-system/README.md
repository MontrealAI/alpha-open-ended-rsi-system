# Unbounded RSI System Demo (v2.8.0-rc.1)

This demo is a **bounded proof-of-mechanism** for a minimum viable accelerating loop:

**bounded → expanding → increasingly autonomous**.

It is intentionally repo-native, deterministic, and governance-bounded.

## Why this demo exists

This demo makes one narrow claim easier to inspect:

- If protocol correctness can be formalized and frozen into reusable capability packages,
- and if those packages transfer to adjacent mandates with better outcomes,
- and if bounded autonomy can choose a broader adjacent mandate with less intervention,
- then an early accelerating mechanism exists under governance.

It does **not** claim unrestricted autonomy, literal unbounded recursive self-improvement, or a fully realized broader sovereign system.

## Three-phase structure

## Phase A — Bounded

- Real Mandate 1 replay inside protocol correctness wedge.
- Uses repo-native mandate-1 contract fixtures and flagship parent business/ground-truth materials.
- Heavy human intervention by design.

## Phase B — Expanding

- Freezes capability package with manifest + hash.
- Runs adjacent Mandate 2 in deterministic control-vs-treatment mode.
- Applies existing adjacent threshold gates:
  - AOY uplift ≥ 35%
  - speed uplift ≥ 30%
  - repair/rework reduction ≥ 40%
  - evidence completeness uplift ≥ 20%
  - no safety regression
  - package dependence rate ≥ 30%

## Phase C — Increasingly autonomous

- Selects Mandate 3 from a bounded candidate set with explicit scoring.
- Chooses second-domain execution surface from repo-native candidates.
- Uses less human intervention than Phases A/B while keeping safety gates explicit.

This run selects **backend proof/governance API correctness** because it scores highest for fit, determinism, and low operator noise under explicit weighted policy.

## Run

```bash
python3 demos/unbounded-rsi-system/run_demo.py --assert
```

Outputs are written to:

- `demos/unbounded-rsi-system/demo_output/`
- Doctrine appendix: [`./DOCTRINE_APPENDIX.md`](./DOCTRINE_APPENDIX.md)

## Artifact map

- `manifest.json` — run identity, constitutional frame, phase labels.
- `package_manifest.json` — frozen sub-pack + promoted stepping-stone pack.
- `package_hash.txt` — SHA-256 over the package manifest.
- `provenance_log.json` — source trace and run metadata.
- `safety_gates.json` — policy gates and safety checks.
- `governance_ruling.json` — bounded governance decision artifact.
- `chronicle_entry.json` — chronicle summary for release history.
- `board_scorecard.json` — machine-readable board-facing scorecard.
- `board_scorecard.md` — human-readable board-facing scorecard.
- `parent_wedge_brief.md` — board-facing wedge/business rationale artifact.
- `mandate3_selection.json` — deterministic Phase C candidate scoring and winning selection log.
- `report.md` — plain-English report with claim boundaries.
- `report.html` — polished static report for operator/board audiences.

## Demonstrated vs simulated vs unproven

### Demonstrated

- Deterministic three-phase accelerating-loop mechanics.
- Package freeze + hash + adjacent threshold gate.
- Bounded autonomous selection into a second repo-native domain.

### Simulated

- Outcome metrics and governance ruling are synthetic by design.
- This is a local replay surface, not a blinded live delivery dossier.

### Unproven

- Real-world unrestricted autonomy.
- Open-ended compounding in unconstrained environments.
- Literal “unbounded RSI” in a fully general sense.

## Demo ladder links

- Current accelerating-loop primary surface: [`../open-ended-rsi-system/`](../open-ended-rsi-system/)
- Flagship synthetic wedge demo: [`../protocol_smart_contract_correctness_demo/`](../protocol_smart_contract_correctness_demo/)
- Compact synthetic adjacent proof demo: [`../adjacent_mandate_reuse_proof_demo/`](../adjacent_mandate_reuse_proof_demo/)
- Real-world experiment pack: [`../adjacent_mandate_reuse_proof_real_v1/`](../adjacent_mandate_reuse_proof_real_v1/)
- Demo ladder index: [`../README.md`](../README.md)
