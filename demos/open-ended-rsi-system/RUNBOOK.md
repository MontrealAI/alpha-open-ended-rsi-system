# Open-Ended RSI System Runbook (v2.8.0-rc.2)

## Purpose

This runbook defines deterministic local execution for the accelerating-loop demo and clarifies what can and cannot be claimed from outputs.

## Preconditions

- Run from repo root.
- No network dependency is required.
- Python 3 is available.
- Repository is in a clean or known state if replay fingerprints are being compared.

## Standard execution

```bash
python3 demos/open-ended-rsi-system/run_demo.py --assert
python3 scripts/check_open_ended_rsi_artifacts.py
python3 scripts/check_release_surface_posture.py
```

Expected result:
- `PASS: open-ended-rsi-system artifacts generated ...`
- `PASS: open-ended-rsi artifact contract validated`

## Determinism replay check

```bash
python3 demos/open-ended-rsi-system/run_demo.py --assert
cp demos/open-ended-rsi-system/out/determinism_fingerprint.json /tmp/open-ended-rsi-fingerprint-a.json
python3 demos/open-ended-rsi-system/run_demo.py --assert
diff -u /tmp/open-ended-rsi-fingerprint-a.json demos/open-ended-rsi-system/out/determinism_fingerprint.json
```

Expected result:
- `diff` emits no output.

## Artifact contract (must exist in `out/`)

- Core: `manifest.json`, `capability_genome.json`, `generation_0.json`, `generation_1.json`, `generation_2.json`, `mandate3_execution.json`
- Assay/selection/archive: `assay_bundle.json`, `lineage.json`, `frontier_queue.json`, `intervention_log.json`
- Governance/score: `scorecard.json`, `board_scorecard.json`, `governance_ruling.json`, `safety_gates.json`, `chronicle_entry.json`
- Proof/provenance: `summary.md`, `proof_docket.md`, `board_scorecard.md`, `provenance_manifest.json`, `determinism_fingerprint.json`, `claim_boundary.json`
- Presentation: `board_report.html`

## Demonstrated vs simulated vs unproven

- Demonstrated: deterministic three-generation mechanics, package freeze/hash reuse, whitelist-bounded domain selection, descending operator touches.
- Simulated: adjudication scores and synthetic mandate outcomes.
- Unproven: unrestricted autonomy, literal unbounded RSI, broad real-world sovereign completion.

## Troubleshooting

- If assert mode fails on repo-native probes, run each probe command from `demos/open-ended-rsi-system/config.json` directly and resolve upstream check failures first.
- If artifact validation fails, regenerate by rerunning `run_demo.py --assert` and then rerun `scripts/check_open_ended_rsi_artifacts.py`.
- If determinism mismatch occurs, verify local modifications and ensure the same Python/runtime environment is used.
