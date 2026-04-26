# Badge Strategy (v2.8.0-rc.7)

This document defines how badges are used in this repository so the front door stays useful, disciplined, and proof-first.

## Institutional design standards

- Keep badge count low and grouped by function.
- Keep a single style (`flat-square`) for visual composure.
- Prefer workflow-state badges only where workflow files exist in `.github/workflows/`.
- Use static badges for bounded claims and navigation (never for implied evidence inflation).
- Link every badge to an immediately useful target (release contract, workflow page, doctrine, or runnable demo).

## Goals

The badge system is designed to answer high-value questions quickly:

1. What is the current release posture?
2. Are core workflows healthy?
3. Where are the canonical demo entry points?
4. What is the explicit claim boundary?

It is intentionally not a vanity wall.

## Source of truth

- Canonical badge metadata: `release/badges.json`
- Generator: `scripts/generate_readme_badges.py`
- Validator: `scripts/check_readme_badges.py`

README badge blocks are managed between markers:

- Root: `<!-- BADGE_RAIL_START --> ... <!-- BADGE_RAIL_END -->`
- Demo ladder: `<!-- DEMO_BADGE_STRIP_START --> ... <!-- DEMO_BADGE_STRIP_END -->`

## Badge rail layout

Root README uses two concise rows:

1. **Operational trust rail**: release posture + CI + contracts security + release provenance.
2. **Orientation rail**: proof boundary + verifiable RC + flagship demo + demo ladder + ascension runtime + doctrine stack.

This keeps first-screen parse time low for serious reviewers while preserving direct navigation.

## Dynamic vs static badge policy

### Dynamic badges (GitHub workflow state)

Use dynamic badges only for surfaces that should reflect live platform state:

- `ci.yml`
- `contracts-security.yml`
- `release-provenance.yml`

Workflow badges must link to their exact GitHub Actions workflow page:

- `https://github.com/MontrealAI/alpha-nova-seeds/actions/workflows/<workflow>.yml`

`scripts/check_readme_badges.py` enforces this path contract to prevent misleading or stale workflow links.
It also checks workflow badge SVGs for passing status so we do not represent non-green workflow state as earned green.
It also enforces a no-vanity policy (no stars/forks/watchers/awesome labels), at-most-two-row root rail structure, and no stale/future RC markers inside the root badge block.

`ci.yml` intentionally keeps long-running scheduled Echidna campaigns as non-blocking coverage so a transient campaign failure does not falsely represent the full CI baseline (backend, SDK, contracts build/tests, Foundry, Slither) as red. Blocking Echidna/security gates remain in `contracts-security.yml`.

### Static/generated badges (repo truth)

Use generated static badges for bounded claims and navigation:

- active RC posture
- proof-first bounded claim boundary
- explicit verifiable RC posture
- demo ladder entry
- flagship demo entry
- ascension-runtime demo entry
- doctrine stack entry

These values are generated from local repo truth and versioned with docs/release updates.

## Operating commands

Regenerate badge rails:

```bash
python scripts/generate_readme_badges.py --write
```

Validate badge rails and local/workflow references:

```bash
python scripts/check_readme_badges.py
```

Validate badge links end-to-end (includes HTTP/HTTPS targets):

```bash
python scripts/check_readme_badges.py --check-http-links
```

Enforce earned-green workflow status (network check, opt-in):

```bash
python scripts/check_readme_badges.py --require-green-workflows
```

Recommended paired release-surface check:

```bash
python scripts/check_release_surface_posture.py
```

The release-surface checker derives the active RC target from `release/badges.json` and validates that README, AGENTS, RELEASES, doctrine posture docs, and the demo ladder surface all stay aligned to that same target.

## Change discipline

When changing release posture or badge semantics:

1. Update `release/badges.json` first.
2. Regenerate README blocks.
3. Run both badge and release-surface validators.
4. Update `CHANGELOG.md` and `RELEASES.md` if posture/acceptance surfaces changed.

This keeps README/AGENTS/RELEASES aligned and prevents silent drift.
