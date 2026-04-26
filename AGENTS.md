# AGENTS.md — alpha-nova-seeds

## Purpose
This repository implements **α‑AGI Nova‑Seeds** as **sealed venture blueprints for sovereign opportunity formation**. The repo now aligns to **v3.0.0 — Ascension Runtime & Verifiable Trust Rail** as the active published release tag (with prior RC history preserved in `CHANGELOG.md`/`RELEASES.md`). It remains a **bounded, verifiable release posture** focused on proof surfaces, governance hardening, and release provenance. It is **not** represented as an audited final deployment.

System framing:

**α‑AGI Insight → Nova‑Seeds → MARK → Sovereigns**

Operational doctrine:

1. **identity**
2. **proof**
3. **settlement**
4. **governance**

The repo exists to make Nova-Seeds **reviewable, verifiable, and operable** as real coordination objects — not just conceptual artifacts.

## Repository map
Treat these directories as canonical unless maintainers explicitly change the architecture.

- `contracts/` — Solidity contracts for identity, registry, governance, workflow, challenge policy, treasury, and council mechanics
- `sdk/` — threshold-cryptography bindings, typed payload helpers, signing / verification helpers
- `backend/` — FastAPI + Postgres indexer and proof / governance APIs
- `dashboard/` — operator dashboard, governance views, lineage views, snapshot/export UX
- `schemas/` — canonical versioned JSON schemas
- `docs/` — trust model, threat model, verification guides, green path, proof-docket guidance
- `release/` — release checklist, plans, provenance guidance, packaging notes
- root `example_*.json` / `*_spec.md` — examples and top-level architecture references; preserve unless superseded by versioned files

## Current release posture
The repo has moved beyond the v2.x release-candidate train and now presents a **v3.0.0 bounded release posture** centered on Ascension Runtime and verifiable trust-rail coherence. All work should reinforce that posture.

That means:

- strengthen verifiability
- strengthen provenance
- strengthen operator trust surfaces
- strengthen governance clarity
- avoid widening claims

Do **not** reframe the repo as:

- audited
- production-final
- mainnet-safe by default
- fully proven as a compounding invention substrate

Those claims require external evidence the repo does not yet contain.

## Non-negotiable doctrine
When editing code, docs, schemas, examples, dashboards, and release materials, preserve these rules:

- **No value without evidence**
- **No autonomy without authority**
- **No settlement without validation**
- **Plain-English first; technical precision second**
- **Additive hardening over architectural rewrites**
- **Proof before narrative expansion**

## Architecture constraints
Preserve the existing stack choices unless maintainers explicitly authorize a redesign.

### Do preserve
- **Solidity** for contract surfaces
- **FastAPI + Postgres** for backend/indexing
- current split between on-chain identity/governance/settlement anchors and off-chain heavier proof / indexing / dashboard surfaces
- threshold-cryptography and typed attestation approach
- operator-facing dashboard model

### Do not do
- do not replace FastAPI with another backend stack
- do not replace Solidity with another contracts stack
- do not flatten contracts/sdk/backend/dashboard into one monolith
- do not remove schemas or docs in favor of prose-only README language
- do not silently rename public-facing concepts without migration notes

## What good changes look like
Good changes do one or more of the following:

- make artifacts easier to verify
- make schemas more explicit and versioned
- make governance/accounting easier to audit
- make indexing more deterministic and reorg-safe
- make dashboard/operator surfaces more legible
- make release provenance easier to verify from a clean machine
- make docs more useful for operators, reviewers, validators, or maintainers

## What bad changes look like
Bad changes include:

- widening claims without new evidence
- adding features without trust model updates
- changing schema shape without migration/version notes
- burying critical operator behavior in code without docs
- introducing hidden defaults that affect proof, settlement, or governance semantics
- prioritizing aesthetic refactors over release trust, operator UX, or verification

## Working style for Codex or any senior contributor
1. **Inspect first.** Read the repo before changing it. Use actual file paths and current conventions.
2. **Plan before large edits.** For non-trivial work, write a short implementation plan first.
3. **Work in small batches.** Prefer reviewable commits over sweeping rewrites.
4. **Run checks after each batch.** If a check cannot run locally, document exactly why.
5. **Update docs with the code.** No hidden architecture changes.
6. **Summarize remaining gaps honestly.** Do not paper over unknowns.

## Documentation style
All user-facing and maintainer-facing docs should be:

- plain-English first
- concise but explicit
- operator-usable
- free of unnecessary hype
- consistent with repo posture

Prefer:
- “what this does”
- “why it matters”
- “how to verify it”
- “what is still not proven”

over vague marketing language.

## Contracts guidance
When touching `contracts/`:

- preserve role clarity and state clarity
- document public/external surfaces with NatSpec
- keep upgrade / lifecycle semantics explicit
- add or update tests with every behavioral change
- do not introduce hidden privileged behavior
- if governance or challenge logic changes, update docs and schemas too
- export ABIs if the existing contract workflow requires them

Minimum expectation for contract-affecting PRs:
- tests updated
- behavior described in docs
- migration notes included if any interface changes

## SDK guidance
When touching `sdk/`:

- treat typed payloads, attestor formats, and threshold-binding profiles as canonical interfaces
- version schemas explicitly
- include round-trip examples when payload shapes change
- prefer compatibility-preserving changes where possible
- if compatibility breaks, document upgrade path clearly

## Backend guidance
When touching `backend/`:

- preserve **FastAPI + Postgres**
- favor idempotent ingestion
- handle chain reorg / replay / cursor safety explicitly
- keep health/readiness endpoints current
- expose metrics useful to operators
- keep backfill deterministic and documented
- treat API stability seriously if payloads are consumed by dashboard or operators

If migrations are introduced or changed:
- version them clearly
- document forward/backfill behavior
- avoid destructive schema edits without a clear operator path

## Dashboard guidance
When touching `dashboard/`:

- optimize for operator clarity, not novelty
- make seed lifecycle, rounds, reviewer stake, council seats, lineage, provenance, and disputes easy to inspect
- keep screenshots/snapshots/export flows predictable
- label unstable or simulated data clearly
- do not imply proof where only architecture exists

## Schemas and examples
Canonical shapes belong in `schemas/`.
Examples should:
- validate against canonical schemas
- stay current with release version
- illustrate real operator or protocol behavior
- avoid fictional success evidence that could be mistaken for proof

If an example becomes obsolete:
- either update it
- or move it under an explicitly deprecated path with a note

## Trust, threat, and proof-docket surfaces
The repo should continue to strengthen:

- `docs/trust-model.md`
- `docs/threat-model.md`
- `docs/green-path.md`
- `docs/verify-release.md`
- `docs/proof-docket-template/`

When you touch proof or governance surfaces, review these docs as part of the same change.

## Release engineering rules
Every release candidate should aim to ship:

- checksums
- provenance attestations
- SBOMs
- changelog entries
- verification instructions
- a clear statement of what is and is not proven

Do not cut a tag that would confuse a serious reviewer about trust posture.

## PR checklist expectations
A good PR should include, when relevant:

- acceptance criteria
- exact files changed
- tests/checks run
- migration notes
- rollback notes
- docs updates
- security/provenance implications

If a PR changes any of these surfaces, call it out explicitly:
- schemas
- attestations
- council/reviewer accounting
- indexing semantics
- release verification
- operator workflow

## Things to avoid saying in code or docs
Do not add language claiming:
- “audited”
- “production-safe”
- “fully deployed”
- “trustless” in an absolute sense
- “proven compounding substrate”

unless the repo and public evidence clearly establish it.

## Preferred framing for maintainers
Use language like:
- “verifiable release candidate”
- “production-grade starter architecture”
- “deployable reference implementation”
- “architecture hardening”
- “proof and governance surfaces”

## Local verification guidance
Use the commands actually defined in the repo.
If commands differ from assumptions here, update this file.

Minimum command set for current RC hardening work:

- `pytest -q backend/tests`
- `python backend/scripts/export_openapi.py`
- `python scripts/contracts/export_abi.py`
- `cd sdk && npm run build --if-present`
- `python scripts/release/generate_provenance_manifest.py --tag <TAG> --output /tmp/provenance-manifest.json`

At minimum, contributors should run checks covering:
- contracts tests / static analysis
- backend tests / lint / migrations
- SDK schema validation / type checks
- dashboard build / smoke checks
- release verification docs where changed

If a command is missing, add the script or document the gap rather than silently skipping validation.

## The strategic north star
This repo is in service of one standard:

**validated work must become reusable future leverage.**

All hardening, governance, proof, release, and operator work should make that claim easier to verify — or harder to fake.
