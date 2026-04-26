# Releases

## v3.0.0 release contract (active tag: v3.0.0)

Posture coherence note (2026-04-25): README.md, AGENTS.md, and RELEASES.md align to `v3.0.0 — Ascension Runtime & Verifiable Trust Rail` as the active published release posture. Prior RC markers remain historical in `CHANGELOG.md`.

Current release checklist:
- `release/v3.0.0-ascension-runtime-verifiable-trust-rail-checklist.md`
- `release/v2.8.0-rc.7-front-door-institutional-badge-checklist.md` *(historical RC hardening reference)*
- `release/v2.8.0-rc.7-ascension-runtime-green-badges-checklist.md` *(historical RC hardening reference)*

Each bounded release cut must include:

1. **Acceptance criteria** tied to shipped features.
2. **Migration notes** with ordered rollout guidance.
3. **Provenance artifacts** (source archive hash, SHA256SUMS, attestations, SBOM).
4. **Rollback notes** with operator decision points.

## Immutable release asset naming

Use deterministic file names keyed by tag:

- `alpha-nova-seeds-<TAG>.tar.gz`
- `provenance-manifest-<TAG>.json`
- `sbom-<TAG>.spdx.json`
- `openapi-<API_VERSION>.json` (currently `openapi-v2.6.0-rc.1.json`)
- `SHA256SUMS`

Workflow artifact bundle names (GitHub Actions upload artifacts):
- `release-provenance-<TAG>` (forward default)
- `v27-provenance-<TAG>` (legacy compatibility alias for existing verification runbooks)

Do not overwrite assets for an existing `<TAG>`.
If regeneration is required, cut a new release tag.

## Release flow

1. Merge implementation and docs.
2. Run verification checks:
   - `pytest -q backend/tests`
   - `python backend/scripts/export_openapi.py`
   - `python scripts/contracts/export_abi.py`
   - `cd sdk && npm run build --if-present`
   - `python scripts/check_readme_badges.py`
   - `python scripts/check_readme_badges.py --check-http-links`
   - `python scripts/check_release_surface_posture.py`
   - `python scripts/release/generate_provenance_manifest.py --tag <TAG> --output /tmp/provenance-manifest-<TAG>.json`
3. Trigger `release-provenance.yml`.
4. Publish release notes with generated artifacts.
5. Validate `docs/verify-release.md` commands against published assets.


## Badge rail publication contract

For v3.0.0 posture, root README badges are intentionally split into:

- **Operational trust rail** (release + CI + contracts security + provenance)
- **Orientation rail** (claim boundary + flagship/demo/doctrine entry points)

Badge metadata must remain sourced from `release/badges.json` and rendered via marker-managed generation (`scripts/generate_readme_badges.py --write`).

Workflow badge links are part of the publication contract: each workflow badge must resolve to the matching GitHub Actions workflow path for its configured file (`.../actions/workflows/<workflow>.yml`), and is verified by `scripts/check_readme_badges.py`.

## Demo-and-doctrine acceptance surfaces

For v3.0.0 publication:

- Flagship demo replay + assert mode passing.
- Accelerating-loop demo replay (`demos/open-ended-rsi-system/run_demo.py --assert`) passing with required artifact emission.
- Accelerating-loop artifact contract check (`python scripts/check_open_ended_rsi_artifacts.py`) passing, including board scorecard parity and governance/provenance machine-readable outputs.
- Legacy replay compatibility: `demos/unbounded-rsi-system/run_demo.py --assert` remains supported for historical comparison.
- Ascension bounded runtime replay: `python3 demos/ascension-runtime/run_demo.py --assert` emits deterministic local/devnet loop artifacts, scorecard, and report surfaces.
- Demo ladder cross-links and role labels passing validation.
- Release-surface posture coherence check (`python scripts/check_release_surface_posture.py`) passing across README/AGENTS/RELEASES plus doctrine and demo-ladder release markers derived from `release/badges.json`.
- README badge rail check (`python scripts/check_readme_badges.py`) passing against `release/badges.json`.
- Root README links to flagship, ladder, doctrine, and release posture docs.
- Math markdown validation helper passing.
- Doctrine consistency helper passing.
- Explicit synthetic-vs-real boundary language present on flagship, ladder, and release docs.
- Dashboard operator UI labels synthetic surfaces clearly and links to doctrine/release verification pointers.
