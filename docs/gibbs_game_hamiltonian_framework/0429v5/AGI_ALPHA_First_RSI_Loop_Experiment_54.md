# Experiment 54: First Real RSI Loop Replication Benchmark

**Hypothesis.** The AGI ALPHA RSI loop can be independently replayed from an Evidence Docket and produce the same accepted result, reusable compiler, and treatment/control comparison under pinned artifacts.

**Task.** Replicate `ColdChain-Energy-Loop-001`.

**Required artifacts.**
- `00_manifest.json`
- `01_seed_001.json`
- `02_mark_review_card.json`
- `03_sovereign_001.json`
- `04_job_outputs.json`
- `05_sources_used.json`
- `06_accepted_interventions.json`
- `07_coldchain_energy_compiler_v0.json`
- `08_seed_002.json`
- `09_treatment_control_comparison.json`
- `10_decision_memo.md`
- `REPLAY_INSTRUCTIONS.md`

**Baselines.**
- B0 no compiler reuse
- B1 manual reuse heuristic
- B2 single-agent compiler extraction
- B3 AGI ALPHA deterministic loop without MARK
- B4 AGI ALPHA deterministic loop with MARK and Evidence Docket

**Metrics.**
Replay success; manifest completeness; test pass rate; accepted interventions; compiler extraction success; treatment/control reuse lift; cost ledger completeness; safety ledger completeness; source snapshot completeness; independent reviewer agreement; reproducibility delta.

**Promotion rule.**
The result is promoted from deterministic scaffold evidence to replicated Evidence Docket evidence only if an independent reviewer can replay the docket, verify archived source snapshots, confirm test outcomes, reproduce the treatment/control comparison, and review cost/safety ledgers without hidden manual intervention.
