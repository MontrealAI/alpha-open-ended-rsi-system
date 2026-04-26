# Open-Ended RSI System Demo (v3.0.0 target)

This demo is a deterministic, repo-native **bounded proof-of-mechanism** for an early accelerating loop:

**bounded → expanding → increasingly autonomous**

It demonstrates controlled compounding under governance. **Claim boundary (one sentence): this demo demonstrates bounded, deterministic, local accelerating-loop mechanics only, and does not claim unrestricted autonomy, audited-final deployment, or external real-world validation.**

## What this demo does

1. Runs a real Mandate 1 starting point in the protocol-correctness wedge.
2. Freezes a governed capability package with a manifest + hash.
3. Uses that package in an adjacent Mandate 2 treatment lane against a control lane.
4. Selects and executes Mandate 3 from a bounded frontier whitelist with less human intervention.
5. Emits board-ready scorecards, safety gates, provenance logs, and proof-docket outputs.


## Real Mandate 1 input policy

Generation 0 includes deterministic repo-native probes that replay the flagship wedge (`demos/protocol_smart_contract_correctness_demo/run_demo.py --assert`) plus release/doctrine/demo validation helpers (`check_demo_links`, `check_doctrine_consistency`, `check_math_markdown`) so the starting wedge uses real local repo surfaces, while final adjudication values remain explicitly synthetic.

## Required folders and emitted artifacts

This demo includes:

- `00_manifest/`
- `01_frontier_queue/`
- `02_seed_genome/`
- `03_generation/`
- `04_assays/`
- `05_selection/`
- `06_archive/`
- `07_scorecard/`
- `08_proof_docket/`
- `out/`

Primary machine-readable outputs in `out/`:

- `capability_genome.json`
- `manifest.json`
- `generation_0.json`
- `generation_1.json`
- `generation_2.json`
- `mandate3_execution.json`
- `assay_bundle.json`
- `lineage.json`
- `frontier_queue.json`
- `intervention_log.json`
- `scorecard.json`
- `board_scorecard.json`
- `governance_ruling.json`
- `chronicle_entry.json`
- `claim_boundary.json`
- `determinism_fingerprint.json`
- `safety_gates.json`
- `summary.md`
- `proof_docket.md`
- `board_scorecard.md`
- `provenance_manifest.json`
- `board_report.html`

The run also performs deterministic local validation against:

- `schemas/v2.8/capability_genome.schema.json`
- `schemas/v2.8/assay_bundle.schema.json`
- `schemas/v2.8/lineage.schema.json`

## Run

```bash
python3 demos/open-ended-rsi-system/run_demo.py --assert
```

For operator procedure, validation sequence, and troubleshooting, see [`./RUNBOOK.md`](./RUNBOOK.md).

Optional deterministic replay check (same machine, clean repo state):

```bash
python3 demos/open-ended-rsi-system/run_demo.py --assert
cp demos/open-ended-rsi-system/out/determinism_fingerprint.json /tmp/rsi-fingerprint-a.json
python3 demos/open-ended-rsi-system/run_demo.py --assert
diff -u /tmp/rsi-fingerprint-a.json demos/open-ended-rsi-system/out/determinism_fingerprint.json
```

`determinism_fingerprint.json` uses file digests for `scorecard_hash` and `lineage_hash` so values align directly with provenance-manifest hash semantics.

## Three generations

### Generation 0 (bounded)

- Domain: protocol correctness wedge.
- Uses a fixed reactive intermediate (`missing_provenance_surface`).
- Deterministically generates 48 candidates across DISCO + Arnold modes.
- Screens cheap → mid → expensive assays.
- Preserves a small strategy-family population (`proof_first`, `test_first`, `schema_first`, `docs_first`) on the Pareto frontier before winner freeze.
- Freezes winner as governed package with deterministic hash.

### Generation 1 (expanding)

- Domain: adjacent mandate in wedge.
- Runs explicit control vs treatment lanes.
- Emits AOY/speed/rework/evidence/safety/package-dependence metrics.
- Emits a package-dependence ledger tying treatment-lane reuse back to the frozen package manifest hash.
- Treatment lane wins and is attributable to the frozen package.

### Generation 2 (increasingly autonomous)

- Domain selection from fixed whitelist only.
- Selection scoring uses transfer, assay coverage, safety scope, evidence density, and produces a deterministic ranked frontier queue.
- Frontier selection is strictly whitelist-bounded from `config.json`.
- Runs DISCO discovery then Arnold local evolution.
- Emits a deterministic Mandate 3 execution log (`mandate3_execution.json`) that records autonomous selector policy, assay cascade completion, and offline-only constraints.
- Emits `frontier_width`, `autonomy_delta`, `neighborhood_slope`, `archive_depth`.

## Demonstrated vs simulated vs unproven

### Demonstrated

- Bounded accelerating loop mechanics under governance.
- Package freeze/reuse with attributable control-vs-treatment uplift.
- Reduced operator intervention in Generation 2 without authority widening.

### Simulated

- Assay outcomes and scorecard values are synthetic deterministic replay values.
- No network calls, no external APIs, no live settlement.

### Unproven

- Unrestricted autonomy.
- Literal or general unbounded recursive self-improvement.
- Completed real-world broad cybersecurity sovereign operation.

## Demo ladder links

- Flagship synthetic wedge demo: [`../protocol_smart_contract_correctness_demo/`](../protocol_smart_contract_correctness_demo/)
- Adjacent synthetic proof demo: [`../adjacent_mandate_reuse_proof_demo/`](../adjacent_mandate_reuse_proof_demo/)
- Real-world proof pack: [`../adjacent_mandate_reuse_proof_real_v1/`](../adjacent_mandate_reuse_proof_real_v1/)
- Legacy accelerating-loop demo: [`../unbounded-rsi-system/`](../unbounded-rsi-system/)
- Demo ladder index: [`../README.md`](../README.md)
