# Changelog

## [Unreleased]

### Added
- Added `release/v3.0.1-source-coherence-checklist.md` to capture the post-v3.0.0 source-coherence patch release path (checks, claim boundaries, rollback notes, and verification expectations).

### Changed
- Documented explicit Python dependency guidance (`jsonschema`) in release verification/checklist flows before requiring `demos/ascension-runtime/run_demo.py --assert`, preventing clean-environment verification blockers.
- Tightened release verification guidance in `docs/verify-release.md` with explicit source-posture/trust-rail checks and bounded-runtime assert verification for v3.x reviewers.
- Surfaced the next empirical milestone (blinded adjacent-transfer Stage A/Stage B progression) in `README.md`, `demos/README.md`, and `docs/verify-release.md` without claiming a completed blinded pass.
- Updated `docs/FRONTIER_LAB_POSTURE.md` wording from RC-specific phrasing to release-neutral v3.0.0 posture framing.


## [v3.0.0] - 2026-04-25

### Added
- Added `release/v3.0.0-ascension-runtime-verifiable-trust-rail-checklist.md` to define acceptance criteria, checks, migration notes, rollback notes, and bounded claim boundaries for the v3.0.0 publication contract.

### Changed
- Aligned release-facing posture surfaces from active `v2.8.0-rc.7` target language to `v3.0.0 — Ascension Runtime & Verifiable Trust Rail` across `README.md`, `AGENTS.md`, `RELEASES.md`, `demos/README.md`, `docs/FRONTIER_LAB_POSTURE.md`, and `docs/DOCTRINE_STACK.md`.
- Updated `release/badges.json` and regenerated marker-managed README badge rails for `v3.0.0` while retaining bounded local/devnet claim boundaries.
- Updated `docs/verify-release.md` heading/posture framing to describe v3.0.0 verification intent without claiming audited-final or mainnet-ready status.
- Updated `scripts/check_release_surface_posture.py` to accept both stable (`vX.Y.Z`) and RC (`vX.Y.Z-rc.N`) release targets while preserving release-surface coherence checks.

### Notes
- v3.0.0 remains bounded and proof-first.
- This release does **not** claim audited final deployment, completed live Ascension, unrestricted autonomy, broad sovereign cybersecurity completion, or production/mainnet readiness.

### Added
- Added additional README badge-rail guardrails in `scripts/check_readme_badges.py` for stale/future RC marker detection inside the badge block, forbidden vanity badge labels, and enforced two-row maximum root rail structure.
- Added `scripts/check_ascension_runtime_artifacts.py` to enforce the full bounded Ascension runtime output contract (all required layer artifacts, scorecards, and report formats) after local `run_demo.py --assert` replay.
- Added release checklist `release/v2.8.0-rc.7-ascension-runtime-green-badges-checklist.md` with badge generation/validation commands, ascension-runtime assert command, workflow green requirements, artifact checks, claim boundary reminders, and rollback notes.
- Added new bounded local/devnet Ascension runtime demo at `demos/ascension-runtime/` with modular source layout (`src/`), deterministic artifact emission, two-job agent competition, validation/council rulings, reservoir ledgering, archive lineage, node profile, architect next-loop planning, and board scorecard/report outputs.
- Added bounded local/devnet Ascension runtime demo at `demos/ascension-live-runtime/` with deterministic end-to-end organism loop artifacts, event log emission, scorecard outputs, and operator reports.
- Added v2.8 Ascension artifact schemas: insight packet, seed packet, MARK report, sovereign manifest, marketplace round, AGI job receipt, agent execution log, validation round, reservoir ledger, archive lineage, and architect recommendation.
- Added Ascension implementation/status docs at `docs/ASCENSION_IMPLEMENTATION_STATUS.md` and `docs/ASCENSION_TRACE_MATRIX.md`.
- Added release checklist `release/v2.8.0-rc.7-ascension-live-runtime-checklist.md` for demo execution, schema/event checks, migration notes, rollback notes, and claim boundaries.

### Changed
- Updated `demos/ascension-runtime/RUNBOOK.md` to point operators to `scripts/check_ascension_runtime_artifacts.py` and to the current per-layer artifact paths used by the bounded local/devnet runtime contract.
- Updated `docs/BADGE_STRATEGY.md` to document the new badge checker constraints (no vanity labels, max two rows, no stale/future RC markers in root badge block).
- Updated `.github/workflows/release-provenance.yml` to include a push/pull_request provenance smoke job so the workflow badge reflects earned green status on normal branch activity while preserving the existing tag-bound release publication path under `workflow_dispatch`.
- Updated `.github/workflows/ci.yml` so scheduled/manual Echidna campaigns are non-blocking CI coverage; contract security remains fail-loud in `contracts-security.yml`, keeping the CI badge aligned to baseline deterministic gates instead of transient long-run fuzz campaign variance.

- Hardened `demos/ascension-runtime/run_demo.py --assert` to validate emitted runtime artifacts against canonical `schemas/v2.8/` Ascension schemas, including `ascension_runtime_scorecard.schema.json`.
- Restored cross-demo v2.8 schema compatibility for shared Ascension artifacts (including per-seed `nova_seed_packet` legacy shape) so `demos/ascension-live-runtime/run_demo.py --assert` remains green.
- Split Nova-Seed schema surfaces into `nova_seed_packet.schema.json` (legacy per-seed packet contract used by `ascension-live-runtime` required-key checks) and `nova_seed_bundle.schema.json` (aggregate runtime seed bundle contract used by `ascension-runtime`).
- Split AGI receipt and agent execution schema surfaces between legacy single-artifact contracts (`agi_job_receipt.schema.json`, `agent_execution_log.schema.json`) and ascension-runtime aggregate contracts (`agi_job_receipt_bundle.schema.json`, `agent_execution_round.schema.json`) so assert-mode preserves execution/receipt evidence checks without breaking legacy validation.
- Split MARK and Architect schema surfaces between legacy single-decision contracts (`mark_selection_report.schema.json`, `architect_recommendation.schema.json`) and ascension-runtime aggregate contracts (`mark_bundle_selection_report.schema.json`, `architect_runtime_recommendation.schema.json`) so selected targets and actionable next-step payloads remain mandatory in both verification paths.
- Changed Ascension runtime schema validator loading to lazy import so `python3 demos/ascension-runtime/run_demo.py` works without requiring `jsonschema` unless `--assert` path is invoked.
- Expanded v2.8 Ascension schema coverage/alignment for runtime payloads and added missing `schemas/v2.8/ascension_runtime_scorecard.schema.json` and `schemas/v2.8/ascension_trace.schema.json`.
- Updated Ascension implementation/checklist docs to reflect assert-mode schema validation as a first-class verification surface.
- Updated demo/docs release surfaces to include `demos/ascension-runtime/` as the organism reference runtime, refreshed Ascension trace/status docs, and added `release/v2.8.0-rc.3-ascension-runtime-checklist.md` for acceptance/migration/rollback boundaries.
- Added read-only backend Ascension runtime endpoints (`/ascension/status`, `/ascension/seeds`, `/ascension/mark`, `/ascension/sovereigns`, `/ascension/jobs`, `/ascension/agents`, `/ascension/validators`, `/ascension/reservoir`, `/ascension/archive`, `/ascension/architect`, `/ascension/scorecard`) backed by deterministic local artifacts.
- Updated dashboard operator surface with an Ascension Runtime tab and bound local/devnet status panels.
- Updated root and demo-ladder docs to include the new Ascension runtime path.

### Changed
- Added `.gitignore` guardrails for `demos/adjacent_mandate_reuse_proof_real_v1/local_private_blinding_materials/` so private blinding maps and answer keys stay local-only when running the real-world blinded adjacent-transfer harness.
- Added `07_scripts/assemble_reveal_packet.py` to emit a post-score-lock public reveal receipt (hash-linked to private commitment files) without exposing reviewer identities or answer keys.
- Fixed `assemble_reveal_packet.py` lane-mapping extraction to read actual assignment-map headers (`blinded_lane_id`, `kit_variant`, `actual_lane`) with compatibility fallbacks, preventing silent blank lane metadata in reveal receipts.
- `assemble_reveal_packet.py` now rejects scaffold placeholder commitment-hash files and requires real SHA-256 hash records before emitting a public reveal receipt.
- `assemble_reveal_packet.py` commitment validation now enforces hexadecimal SHA-256 digest format (not just 64-character token length) before accepting private commitment records.
- `assemble_reveal_packet.py` now fails reveal assembly when `blinded_assignment_map.private.csv` has zero data rows, preventing empty-but-apparently-valid reveal receipts.
- `assemble_reveal_packet.py` now sets public receipt `revealed_after_score_lock` rows to `true` at assembly time and preserves source CSV values separately for audit context.
- `assemble_reveal_packet.py` now accepts legacy assignment-map templates that omit `kit_variant`/`assigned_kit`, emitting `assigned_kit: UNSPECIFIED_LEGACY_TEMPLATE` instead of failing reveal publication.
- `assemble_reveal_packet.py` now triggers a full provenance hash refresh (via `normalize_reviewer_packets.refresh_public_provenance`) immediately after writing `reveal_receipt_public.json`, so scorecard summary files and other tracked outputs remain in the signed hash set.
- `normalize_reviewer_packets.py --refresh-only` now includes `scorecard_outputs/reveal_receipt_public.json` in provenance hash refreshes so reveal artifacts remain hash-linked in the public-safe manifest.
- Regenerated `results_blinded_adjacent_transfer_v1` frozen manifests so `prereg_experiment_manifest.json` and `environment_lock.json` bind to a resolvable in-repo commit SHA for reproducible replay.
- Pinned blinded-transfer frozen manifests to reachable baseline commit `c0931820d91e431abdac1b7a083e1fbf76c7fab9` and refreshed provenance hashes to keep replay anchoring verifiable by external operators.
- Regenerated `results_blinded_adjacent_transfer_v1/` from a clean setup run and refreshed prereg/environment/provenance outputs, including a public `scorecard_outputs/reveal_receipt_public.json` artifact generated behind an explicit `--confirm-score-lock` gate.
- Re-baselined `demos/adjacent_mandate_reuse_proof_real_v1/results_blinded_adjacent_transfer_v1/` to an honest public-safe boundary state (Stage A pending blinded human adjudication, Stage B not run/conditional), removing prior internal-pass-style artifacts and preserving only reproducible harness/handoff outputs.
- Expanded the real-world blinded adjacent-transfer manifest templates to include full preregistration lock fields (Stage A + conditional Stage B scope, branch binding, budgets, intervention policy, publication/stopping rules, and allowed-tool boundaries) required for honest protocol execution.
- Updated execution/review templates with stage-aware run-register rows and a dedicated reviewer leakage-check worksheet so reveal-time blinding integrity can be recorded explicitly.
- Hardened `setup_blinded_adjacent_transfer_v1.py` and `validate_blinded_results_bundle.py` to scaffold and require `leakage_check.csv` in public-safe result bundles, then regenerated `results_blinded_adjacent_transfer_v1/` from a clean local setup run.
- Restored backward-compatible release-provenance artifact download behavior by uploading both `release-provenance-<TAG>` (forward default) and `v27-provenance-<TAG>` (legacy alias) in `.github/workflows/release-provenance.yml`.
- Updated `docs/verify-release.md` to use `release-provenance-<TAG>` as the primary command and explicitly document the legacy `v27-provenance-<TAG>` fallback.
- Hardened `scripts/check_release_surface_posture.py` to require both provenance artifact names so compatibility does not regress silently.
- Added blinded adjacent-transfer execution scaffolding under `demos/adjacent_mandate_reuse_proof_real_v1/` with setup, private commitment hashing, and bundle validation helpers, plus a public-safe `results_blinded_adjacent_transfer_v1/` record and git-ignored local private blinding workspace.
- Hardened blinded adjacent-transfer execution wiring so `calculate_q2_scorecard.py` can read either template scorecards or run-specific `scorecard_outputs/`, and updated setup scaffolding to regenerate complete public-safe result bundles (including provenance and human-boundary status docs) from a clean machine.
- Extended the real-world blinded adjacent-transfer harness with matched private kit scaffolding (`Kit Blue`/`Kit Gold`), explicit Stage B placeholder scorecard status, and a reviewer packet normalization helper (`normalize_reviewer_packets.py`) so Stage A execution can proceed to the honest human boundary without leaking private assignment maps.
- Hardened blinded packet/provenance integrity by adding stage-scoped normalized packet outputs (`stage_a`/`stage_b`), automatic provenance-manifest hash refresh after packet normalization, and commitment-hash coverage for private kit contents to prevent post-freeze drift.
- Tightened `normalize_reviewer_packets.py` redaction and provenance behavior by using case-insensitive disallowed-label scrubbing and by appending hashes for newly normalized packet artifacts into `results_blinded_adjacent_transfer_v1/provenance_manifest.json`.
- `normalize_reviewer_packets.py` now fails closed when raw reviewer packet source directories/artifacts are missing, and adds a `--refresh-only` mode for provenance hash refreshes (including `scorecard_outputs/out/summary.{json,md}`) without pretending packet normalization occurred.
- `normalize_reviewer_packets.py` now validates raw source packet directories before `--force` cleanup to avoid deleting prior normalized evidence on a bad source path, and fails `--refresh-only` when `provenance_manifest.json` is absent.
- `validate_blinded_results_bundle.py` now requires stage-scoped reviewer packet directories (`lane_*_packet_public/stage_a` and `stage_b`) so incomplete stage layouts cannot pass bundle validation.
- `normalize_reviewer_packets.py` redaction now matches standalone labels/phrases (for example `operator`, `kit blue`) instead of arbitrary substrings, avoiding corruption of identifiers like `AccessControl` or `OperatorRole`.
- `setup_blinded_adjacent_transfer_v1.py` now randomizes which matched private kit (`Kit Blue`/`Kit Gold`) receives the real treatment payload by default (with optional explicit override), and records that assignment only in private local files to reduce deterministic blinding leakage.

## [v2.8.0-rc.7] - 2026-04-23

### Added
- Added `release/v2.8.0-rc.7-front-door-institutional-badge-checklist.md` for this additive RC cut, including acceptance criteria, smoke checks, migration notes, rollback notes, and claim-boundary reminders.

### Changed
- Promoted active RC posture from `v2.8.0-rc.6` to `v2.8.0-rc.7` across release-facing surfaces (`README.md`, `demos/README.md`, `AGENTS.md`, `RELEASES.md`, `docs/FRONTIER_LAB_POSTURE.md`, `docs/DOCTRINE_STACK.md`, and `docs/BADGE_STRATEGY.md`) without widening claims.
- Updated `release/badges.json` release target and release-posture badge metadata to `v2.8.0-rc.7`, then regenerated marker-managed README badge rails.
- Strengthened root README front-door orientation by adding direct first-screen links to `docs/verify-release.md` in both “Start here” and the navigation map.
- Updated `.github/workflows/release-provenance.yml` upload artifact naming from stale `v27-provenance-<TAG>` to train-neutral `release-provenance-<TAG>`.
- Extended `scripts/check_release_surface_posture.py` with a guardrail that fails if release-provenance artifact naming drifts from `release-provenance-${{ inputs.release_tag }}`.

### Notes
- This RC remains a coherence-and-presentation hardening cut.
- It preserves the verifiable, proof-first, bounded release-candidate posture.

## [v2.8.0-rc.6] - 2026-04-23

### Added
- Added `release/v2.8.0-rc.6-front-door-institutional-badge-checklist.md` to package this next additive RC cut with acceptance criteria, smoke checks, migration notes, rollback notes, and claim-boundary reminders.
- Added an institutional badge design standards section to `docs/BADGE_STRATEGY.md` so maintainers can keep badge rails concise, useful, and non-vanity.

### Changed
- Promoted active RC posture from `v2.8.0-rc.5` to `v2.8.0-rc.6` across release-facing surfaces (`README.md`, `demos/README.md`, `AGENTS.md`, `RELEASES.md`, `docs/FRONTIER_LAB_POSTURE.md`, `docs/DOCTRINE_STACK.md`, and `docs/BADGE_STRATEGY.md`) without widening claims.
- Updated `release/badges.json` release target and release-posture badge metadata to `v2.8.0-rc.6`, then regenerated marker-managed README badge rails.
- Improved root README first-screen hierarchy with a compact “first-screen navigation map” table for faster serious-reviewer orientation.
- Hardened `scripts/check_readme_badges.py` to enforce required two-row rail labels and detect duplicate badge IDs within a row.

### Notes
- This RC remains a coherence-and-presentation release cut.
- It preserves the verifiable, proof-first, bounded release-candidate posture.

## [v2.8.0-rc.5] - 2026-04-23

### Added
- Added `release/v2.8.0-rc.5-front-door-badge-coherence-checklist.md` to package the next additive RC cut with acceptance criteria, smoke checks, migration notes, rollback notes, and claim-boundary reminders.

### Changed
- Promoted active RC posture from `v2.8.0-rc.4` to `v2.8.0-rc.5` across release-facing surfaces (`README.md`, `demos/README.md`, `AGENTS.md`, `RELEASES.md`, `docs/FRONTIER_LAB_POSTURE.md`, `docs/DOCTRINE_STACK.md`, and `docs/BADGE_STRATEGY.md`) without widening claims.
- Updated `release/badges.json` release target and release-posture badge metadata to `v2.8.0-rc.5`, then regenerated marker-managed badge rails.
- Refined the root README first screen with clearer “what this is / what this is not” boundary language and tighter start-here navigation hierarchy while preserving proof-first bounded posture.

### Notes
- This RC is a coherence-and-presentation release cut for institutional front-door clarity.
- It preserves the verifiable, proof-first, bounded release-candidate posture.

## [v2.8.0-rc.4] - 2026-04-23

### Added
- Added `release/v2.8.0-rc.4-front-door-badge-coherence-checklist.md` as the next additive release checklist for badge governance, posture coherence, smoke checks, migration notes, and rollback notes.

### Changed
- Promoted active RC posture from `v2.8.0-rc.3` to `v2.8.0-rc.4` across release-facing surfaces (`README.md`, `demos/README.md`, `AGENTS.md`, `RELEASES.md`, `docs/FRONTIER_LAB_POSTURE.md`, `docs/DOCTRINE_STACK.md`, and `docs/BADGE_STRATEGY.md`) without widening claim boundaries.
- Updated `release/badges.json` release target and release-posture badge metadata to `v2.8.0-rc.4`, then regenerated marker-managed badge rails.
- `scripts/check_demo_links.py` now derives the expected RC target from `release/badges.json` instead of using a hard-coded value, eliminating demo-ladder RC marker drift when a new RC target is cut.

### Notes
- This RC is a coherence-and-presentation release cut for front-door trust surfaces.
- It preserves the verifiable, proof-first, bounded release-candidate posture.

## [v2.8.0-rc.3] - 2026-04-23

### Added
- Introduced disciplined badge governance with `release/badges.json` as a single source of truth plus `scripts/generate_readme_badges.py` and `scripts/check_readme_badges.py` for deterministic README badge generation and drift checks.
- Added `docs/BADGE_STRATEGY.md` documenting dynamic-vs-static badge policy, badge marker ownership, and release update workflow.

### Changed
- `scripts/check_release_surface_posture.py` now compares all discovered `vX.Y.Z-rc.N` markers against the active target and rejects any premature future RC marker (for example `v2.9.0-rc.2` or `v3.0.0-rc.1`).
- `scripts/check_release_surface_posture.py` now rejects same-train future markers (for example `v2.8.0-rc.4`) so premature RC posture strings cannot pass alongside required `v2.8.0-rc.3` markers.
- `scripts/check_readme_badges.py` now enforces `release_target` parity with the `release-posture` badge metadata (`message` and `alt`) so front-door release badge drift cannot pass validation.
- `scripts/check_release_surface_posture.py` now rejects stale active RC markers (including `v2.8.0-rc.2`) as disallowed drift while keeping `v2.9.0-rc.1` blocked as a future marker.
- `scripts/check_readme_badges.py` now validates all relative local badge links (including `../...` overrides used by `demos/README.md` badge entries), not only `./...` paths.
- Upgraded root README front door with an institutional badge rail, tighter orientation hierarchy, explicit “what is / what is not claimed” boundary, and direct paths to flagship demo, demo ladder, accelerating-loop demo, doctrine stack, and release posture surfaces.
- Added a compact status strip to `demos/README.md` and aligned it with the root badge strategy using marker-managed generation.
- Reconciled release-surface posture to `v2.8.0-rc.3` across README, AGENTS, RELEASES, doctrine posture docs, and release-surface validator patterns.
- Extended release acceptance surfaces to include README badge synchronization checks.

### Notes
- This release is an additive front-door and release-surface hardening cut.
- It does **not** widen proof claims beyond bounded synthetic deterministic evidence.

## [v2.8.0-rc.2] - 2026-04-22

### Added
- New deterministic accelerating-loop demo at `demos/open-ended-rsi-system/` with governed generation pipeline, DISCO/Arnold alternating modes, machine-readable artifact ladder, board-ready HTML scorecard, and `--assert` smoke mode.
- Lightweight deterministic validator `scripts/check_open_ended_rsi_artifacts.py` to verify required `demos/open-ended-rsi-system/out/` artifacts, threshold contract outcomes, intervention-touch descent, and doctrine gate pass states.
- New staged demo artifact directories under `demos/open-ended-rsi-system/` (`00_manifest` ... `08_proof_docket` + `out`) plus deterministic emission of `capability_genome.json`, `assay_bundle.json`, `lineage.json`, `frontier_queue.json`, `intervention_log.json`, `scorecard.json`, `summary.md`, `proof_docket.md`, and `provenance_manifest.json`.
- Added deterministic `claim_boundary.json` emission and schema-conformance checks for capability genome / assay bundle / lineage artifacts in `demos/open-ended-rsi-system/run_demo.py`.
- New canonical v2.8 schemas for accelerating-loop artifacts: `schemas/v2.8/capability_genome.schema.json`, `schemas/v2.8/assay_bundle.schema.json`, and `schemas/v2.8/lineage.schema.json`.
- New release checklist `release/v2.8.0-rc.2-open-ended-rsi-checklist.md` with acceptance criteria, smoke checks, provenance expectations, migration/rollback notes, and claim boundaries.
- Added deterministic replay fingerprint artifact `demos/open-ended-rsi-system/out/determinism_fingerprint.json` and corresponding assert checks for fixed selection path + configuration contract.

### Changed
- `scripts/check_release_surface_posture.py` now compares all discovered `vX.Y.Z-rc.N` markers against the active target and rejects any premature future RC marker (for example `v2.9.0-rc.2` or `v3.0.0-rc.1`).
- `scripts/check_release_surface_posture.py` now rejects same-train future markers (for example `v2.8.0-rc.4`) so premature RC posture strings cannot pass alongside required `v2.8.0-rc.3` markers.
- `scripts/check_readme_badges.py` now enforces `release_target` parity with the `release-posture` badge metadata (`message` and `alt`) so front-door release badge drift cannot pass validation.
- Root README posture updated to active target `v2.8.0-rc.2`, with the new open-ended demo as the accelerating-loop front door while retaining `demos/unbounded-rsi-system/` as a legacy compatibility surface.
- Demo ladder index now designates `demos/open-ended-rsi-system/` as the accelerating-loop demo and preserves explicit demonstrated/simulated/unproven boundaries.
- Demo/doctrine link checks now include `demos/open-ended-rsi-system/` in required release surfaces.
- Repo-level posture docs (`AGENTS.md`, `docs/FRONTIER_LAB_POSTURE.md`, `docs/DOCTRINE_STACK.md`, `RELEASES.md`) aligned to the v2.8.0-rc.2 train without widening public claims.
- Open-ended RSI Mandate 1 now logs deterministic repo-native probe execution (including `protocol_smart_contract_correctness_demo` replay `--assert`, plus demo-link/doctrine/math checks) as non-simulated evidence inputs before synthetic adjudication stages.
- Open-ended RSI Generation 2 now derives candidates directly from `config.json` whitelist entries and fails closed if a whitelisted domain lacks deterministic assay profiles.
- Open-ended RSI outputs now include `out/safety_gates.json` to make doctrine gate outcomes (`no value without evidence`, `no autonomy without authority`, `no settlement without validation`) auditable as machine-readable artifacts.
- Open-ended RSI safety-gate statuses are now computed from real run outcomes (probe return codes, threshold gates, schema validation, and authority-bound checks) rather than hardcoded pass labels.
- Open-ended RSI output tree now mirrors generation artifacts in `out/` (`manifest.json`, `generation_0.json`, `generation_1.json`, `generation_2.json`) and logs a Generation 1 package-dependence ledger keyed to the frozen manifest hash.
- Open-ended RSI real Mandate 1 seed genome now includes broader repo-native surfaces (flagship demo runner, backend tests, v2.8 schema artifact, proof-docket template, and provenance manifest script) so frozen package dependency is better rooted in code/test/schema/proof/release inputs.
- Open-ended RSI determinism fingerprint now uses artifact file digests for `scorecard_hash` and `lineage_hash` to align with provenance-manifest hash semantics.
- Open-ended RSI assert-mode frontier selection check now derives expected domain from configured deterministic scoring output instead of hardcoding one domain label.
- Open-ended RSI Generation 0 now tracks deterministic strategy-family diversity on the Pareto frontier before winner freeze, and Generation 2 now emits a deterministically ranked frontier queue for clearer autonomy auditability.

### Notes
- This RC strengthens deterministic bounded mechanism evidence and operator presentation quality.
- It does **not** claim unrestricted autonomy, literal unbounded RSI, or completed broad real-world sovereign operation.

## [v2.8.0-rc.1] - 2026-04-22

### Added
- New flagship-class accelerating-loop demo: `demos/unbounded-rsi-system/` with deterministic Phase A/B/C execution, package freeze/hash, bounded mandate-3 selector, and board-ready outputs (`board_scorecard.*`, `report.*`, governance/provenance/safety artifacts).
- Deterministic Phase C selection artifact: `demos/unbounded-rsi-system/demo_output/mandate3_selection.json` capturing bounded-candidate scoring policy and ranked outcomes.
- Parent wedge board artifact: `demos/unbounded-rsi-system/demo_output/parent_wedge_brief.md` generated from deterministic Phase A business/wedge rationale.
- New release checklist: `release/v2.8.0-rc.1-unbounded-rsi-demo-checklist.md` covering acceptance criteria, smoke checks, provenance, migration/rollback notes, and claim boundaries.
- Frontier posture doctrine doc: `docs/FRONTIER_LAB_POSTURE.md`.
- New RC release checklist: `release/v2.8.0-rc.1-frontier-ui-demo-release-checklist.md` with acceptance criteria, smoke checks, migration/rollback notes, and explicit claim boundaries.
- Demo-local doctrine appendix: `demos/unbounded-rsi-system/DOCTRINE_APPENDIX.md` with canonical GitHub-compatible math rendering and bounded claim framing.

### Changed
- `scripts/check_release_surface_posture.py` now compares all discovered `vX.Y.Z-rc.N` markers against the active target and rejects any premature future RC marker (for example `v2.9.0-rc.2` or `v3.0.0-rc.1`).
- `scripts/check_release_surface_posture.py` now rejects same-train future markers (for example `v2.8.0-rc.4`) so premature RC posture strings cannot pass alongside required `v2.8.0-rc.3` markers.
- `scripts/check_readme_badges.py` now enforces `release_target` parity with the `release-posture` badge metadata (`message` and `alt`) so front-door release badge drift cannot pass validation.
- Demo ladder index now includes four coherent roles: flagship synthetic wedge, compact adjacent synthetic replay, real-world proof pack, and accelerating-loop demo.
- Root README front-door guidance links directly to the accelerating-loop demo and its bounded claim boundary.
- Demo-link and doctrine-consistency validators enforce presence of `demos/unbounded-rsi-system/` in ladder and root front-door surfaces.
- Dashboard ladder cards and artifact/release pointers include the accelerating-loop demo as a first-class operator surface.
- Flagship demo report UX (`run_demo.py` generated HTML) improved for operator readability and artifact discoverability while preserving deterministic behavior.
- Doctrine/release positioning surfaces aligned to v2.8.0-rc.1 naming and publication posture.

### Notes
- This accelerating-loop surface is a bounded proof-of-mechanism; it does not claim unrestricted autonomy or literal unbounded recursive self-improvement.
- This release remains a **verifiable release candidate**, not an audited final deployment.
- Broader cybersecurity sovereign claims remain future-facing and conditional on controlled real-world adjacent-mandate proof.

## [v2.7.0-rc.2] - 2026-04-22

### Added
- New release checklist: `release/v2.7.0-rc.2-ui-demo-release-checklist.md` with acceptance criteria, smoke checks, migration/rollback notes, and explicit claim boundaries.
- Demo ladder validator `scripts/check_demo_links.py` to catch broken ladder links and missing role labels.

### Changed
- `scripts/check_release_surface_posture.py` now compares all discovered `vX.Y.Z-rc.N` markers against the active target and rejects any premature future RC marker (for example `v2.9.0-rc.2` or `v3.0.0-rc.1`).
- `scripts/check_release_surface_posture.py` now rejects same-train future markers (for example `v2.8.0-rc.4`) so premature RC posture strings cannot pass alongside required `v2.8.0-rc.3` markers.
- `scripts/check_readme_badges.py` now enforces `release_target` parity with the `release-posture` badge metadata (`message` and `alt`) so front-door release badge drift cannot pass validation.
- Root posture moved from `v2.7.0-rc.1` to `v2.7.0-rc.2` as the next additive RC cut.
- Dashboard UI polished for operator legibility: improved hierarchy, demo ladder cards, synthetic-vs-real labels, and RC2 snapshot naming.
- Flagship demo HTML report (`run_demo.py` output) refreshed for institutional readability with clearer wedge flow, deterministic winner criteria visibility, and operator artifact map.
- `RELEASES.md` acceptance surfaces generalized for v2.7.x RCs and now include demo ladder consistency checks.
- `demos/README.md` labeling clarified for flagship synthetic vs compact synthetic vs real-world pack roles.

### Notes
- This release remains a **verifiable release candidate**, not an audited final deployment.
- Broader cybersecurity sovereign claims remain future-facing; this RC only strengthens synthetic wedge proof surfaces and operator clarity.

## [v2.7.0-rc.1] - 2026-04-22

### Added
- Root doctrine stack docs: `docs/DOCTRINE_STACK.md`, `docs/THERMODYNAMIC_MODEL.md`, `docs/NATION_STATE_DOCTRINE.md`, `docs/DEMO_STRATEGY.md`, and `docs/RELEASE_POSITIONING.md`.
- Math validation helper `scripts/check_math_markdown.py` for canonical equation and delimiter checks.
- Doctrine consistency helper `scripts/check_doctrine_consistency.py` for README doctrine links and canonical equation drift checks between root and flagship docs.
- Release readiness checklist at `release/v2.7.0-rc.1-demo-doctrine-checklist.md`.
- Demo strategy now uses direct Markdown links to all ladder surfaces and includes smoke-run command references for release operators.

### Changed
- `scripts/check_release_surface_posture.py` now compares all discovered `vX.Y.Z-rc.N` markers against the active target and rejects any premature future RC marker (for example `v2.9.0-rc.2` or `v3.0.0-rc.1`).
- `scripts/check_release_surface_posture.py` now rejects same-train future markers (for example `v2.8.0-rc.4`) so premature RC posture strings cannot pass alongside required `v2.8.0-rc.3` markers.
- `scripts/check_readme_badges.py` now enforces `release_target` parity with the `release-posture` badge metadata (`message` and `alt`) so front-door release badge drift cannot pass validation.
- Added `demos/README.md` as a canonical demo ladder index and updated demo README cross-links to use valid relative Markdown links.
- Adjacent synthetic proof README now explicitly states ladder role (supporting compact synthetic surface) and clarifies non-claims alongside cross-links.
- Adjacent synthetic proof README demo ladder links now use clickable relative Markdown links and include explicit sovereign-boundary language.
- Flagship and adjacent demo integration language now consistently frames protocol correctness as the first wedge and distinguishes synthetic vs real-world proof surfaces.
- Public-facing naming now prefers Protocol Cybersecurity labels while retaining legacy Protocol Assurance compatibility aliases where needed.
- Root release posture and demo entry points updated to v2.7.0-rc.1 demo-and-doctrine framing.
- Doctrine consistency helper now validates root README demo-ladder links and required role labels in `demos/README.md`.
- Demo strategy doctrine references now use direct Markdown links for cleaner operator navigation.
- Release provenance workflow artifact upload name now matches v2.7 verification docs (`v27-provenance-<TAG>`), with legacy v2.6 naming noted for historical runs.

### Notes
- This release remains a **verifiable release candidate**, not an audited final deployment.
- Broader cybersecurity sovereign claims remain future-facing and conditional on real adjacent-mandate controlled proof.

## [v2.6.0-rc.1] - 2026-04-18

### Added
- Root repository contract docs: contribution, security, support, release policy, changelog, and code owners.
- Release provenance workflows for source artifacts, SHA256SUMS, SBOM generation, and artifact attestations.
- Verification guide at `docs/verify-release.md`.
- Canonical threshold schemas and validation tests for decryption attestations and threshold bindings.
- Governance accounting docs and backend query surfaces for reviewer ledger and council seat lifecycle.
- Backend hardening: versioned migration, idempotent/reorg-safe indexer cursor, readiness, metrics, OpenAPI export, and deterministic backfill command.
- Dashboard hardening with proof/governance sections, alert views, and JSON/PNG snapshot export.
- Trust/proof docs and public proof docket template shell.

### Changed
- `scripts/check_release_surface_posture.py` now compares all discovered `vX.Y.Z-rc.N` markers against the active target and rejects any premature future RC marker (for example `v2.9.0-rc.2` or `v3.0.0-rc.1`).
- `scripts/check_release_surface_posture.py` now rejects same-train future markers (for example `v2.8.0-rc.4`) so premature RC posture strings cannot pass alongside required `v2.8.0-rc.3` markers.
- `scripts/check_readme_badges.py` now enforces `release_target` parity with the `release-posture` badge metadata (`message` and `alt`) so front-door release badge drift cannot pass validation.
- `README.md` updated for v2.6 RC verification and proof-first milestone framing.
- Contracts received NatSpec interface comments and release metadata surface constants.

### Notes
- This release is a **verifiable release candidate**, not an audited final deployment.
- Follow-up fixes applied after initial RC patch:
  - CI now uses `npm install` when no lockfile is present.
  - Reorg rewind now also clears derived governance rows.
  - Migration view DDL updated for PostgreSQL compatibility.
  - FastAPI `List` typing import fixed to avoid startup error.
  - Council lifecycle indexing now records real seat identifiers from governance events.
  - Reviewer/governance read-model indexing now includes required event ABIs.
  - Provenance manifest timestamp is deterministic (commit time / SOURCE_DATE_EPOCH), not wall-clock.
  - Registry ABI snapshot export now includes review/quarantine events used by governance indexing.
  - Challenge/deactivation lifecycle attribution now uses causal seat-occupant lookups.
  - Challenge resolution rewinds now remain reorg-safe by updating resolution block markers.
  - Release provenance workflow now archives the requested release tag ref instead of branch HEAD.
  - Challenge creation block is immutable; resolution uses a separate resolved block marker for rewind safety.
  - Release provenance checkout now uses the requested tag ref so manifest/SBOM match archived source.
  - Council active seat read-model now treats challenged seats as active until deactivation.
  - Release provenance bundle now includes deterministic OpenAPI export for API-surface verification.
  - Root posture docs normalized to v2.6 RC framing; added contracts package map and CODEOWNERS baseline.
  - SDK package/version now align to v2.6.0-rc.1 metadata while EIP-712 attestation domain remains at verifier-compatible `2.5`.
