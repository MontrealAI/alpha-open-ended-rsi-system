# ASCENSION TRACE MATRIX (bounded local/devnet runtime)

This matrix maps the public Ascension organism to repo-native implementation surfaces for `demos/ascension-runtime/`.

| Layer | Public role | Repo role | Artifact | Current implementation | Status class | What remains unproven |
|---|---|---|---|---|---|---|
| α‑AGI Insight | discovers AGI Alpha opportunities | opportunity / wedge selector | `insight_packet.json` | protocol-correctness wedge + frontier queue | implemented, local/devnet | external foresight quality and market acceptance are unproven |
| Nova-Seeds | sealed venture blueprints / foresight genomes / FusionPlans | capability genome and seed packet | `nova_seed_packet.json` (+ `out/nova_seeds/*.json`) | five deterministic local seed packets + aggregate packet | implemented, local/devnet | live economic performance and real settlement outcomes are unproven |
| MARK | foresight DEX / risk oracle / selection and capital allocation | deterministic seed scoring and allocation simulation | `mark_selection_report.json` | weighted local scorer + bundle selector | implemented, simulated | local risk/selection oracle; not live DEX |
| Sovereign | autonomous enterprise transformation | bounded operating lineage formed from selected seed | `sovereign_manifest.json` | α‑AGI Protocol Cybersecurity Sovereign candidate manifest | implemented, local/devnet | local/devnet/synthetic sovereign candidate |
| Business | decomposes Sovereign mandate into AGI Jobs | business operating plan and mandate decomposition | `business_operating_plan.json` | deterministic decomposition into two jobs | implemented, local/devnet | external demand capture and live operating execution are unproven |
| Marketplace | global job router / agent competition / validator settlement | local marketplace round | `marketplace_round.json` | local job posting, bidding, assignment, escrow placeholders | implemented, simulated | local/devnet simulation unless contracts/events are fully implemented |
| AGI Jobs | autonomous missions carrying goal, success metric, bounty | proof-bound work units | `agi_job_receipt.json` (+ `out/jobs/*`) | deterministic specs/completions/receipts for two jobs | implemented, local/devnet | local deterministic receipts |
| Agents | adaptive executors | competing deterministic local agents | `agent_execution_log.json` | deterministic fast_low_cost, evidence_heavy, balanced competition | implemented, local/devnet | bounded local agents, not unrestricted autonomy |
| Validators / Council | guardians of integrity | validation attestations and council rulings | `validation_round.json`, `council_ruling.json` | artifact/hash/boundary checks with approval+quarantine path | implemented, local/devnet | local validation unless human/external reviewers are provided |
| Value Reservoir | captures success and funds next cycles | validated value accounting ledger | `reservoir_ledger.json` | local validated/rejected accounting + reinvestment guidance | implemented, simulated | local accounting, not real token economy |
| Architect | continuous meta-optimizer | next-loop recommendation engine | `architect_recommendation.json` | deterministic next-loop recommendations | implemented, local/devnet | deterministic local recommender |
| Nodes | runtime / infrastructure nodes | local runtime profile / worker-validator execution environment | `node_runtime_profile.json` | worker, validator, sentinel profiles with constraints | implemented, local/devnet | local/devnet profile, not live node network |
| Archive | reusable memory / stepping-stone preservation | frozen capability lineage and proof archive | `archive_lineage.json` | lineage, package manifest, archive index outputs | implemented, local/devnet | implemented as local lineage artifacts |

## Explicit status separation

- **Implemented:** all listed layers emit machine-readable artifacts.
- **Local/devnet:** Insight, Nova-Seeds, Sovereign, Business, AGI Jobs, Agents, Validators/Council, Architect, Nodes, Archive.
- **Simulated:** MARK market behavior, Marketplace settlement rails, Reservoir token economics.
- **Pending:** contract-backed event mirror for the full runtime loop and external reviewer integrations.
- **Unproven:** live external-market validity, mainnet settlement, audited-final production safety, completed live Ascension.
