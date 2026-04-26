# RUNBOOK — Ascension Runtime

1. Run deterministic demo:
   - `python3 demos/ascension-runtime/run_demo.py --assert`
2. Verify full artifact contract:
   - `python3 scripts/check_ascension_runtime_artifacts.py`
3. Inspect key outputs under `demos/ascension-runtime/out/`:
   - `out/insight_packet.json`
   - `out/nova_seeds/*.json`
   - `out/mark_selection_report.json`
   - `out/sovereign_manifest.json`
   - `out/jobs/job_001_receipt.json`
   - `out/jobs/job_002_receipt.json`
   - `out/validation_round.json`
   - `out/council_ruling.json`
   - `out/reservoir_ledger.json`
   - `out/archive_lineage.json`
   - `out/architect_recommendation.json`
   - `out/ascension_runtime_scorecard.json`
4. Verify claim boundaries in:
   - `out/ascension_runtime_scorecard.md`
   - `out/reports/ascension_runtime_report.md`
5. Use this runtime as a local replay surface only.
