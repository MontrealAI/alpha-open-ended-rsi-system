# Repo integration note

## Recommended path

Place this folder at:

```text
demos/adjacent_mandate_reuse_proof_real_v1/results_internal_rerun_clean_v1/
```

That keeps the evidence update attached to the real-world proof pack and avoids widening the root README claim boundary prematurely.

## Recommended link addition in `demos/README.md`

Add a fourth item directly after the real-world proof pack:

```md
## 4) Internal evidence update — adjacent reuse rerun clean v1

- Path: `adjacent_mandate_reuse_proof_real_v1/results_internal_rerun_clean_v1/`
- Role: replicated internal evidence update for the real-world proof pack
- Shows: same frozen package passing on the original adjacent pair and a second adjacent pair under a fixed rubric
- Does not prove: independent blinded public-grade proof
```

## Optional note in `demos/adjacent_mandate_reuse_proof_real_v1/README.md`

Suggested addition near the end of the file:

```md
## Internal evidence updates

- `results_internal_rerun_clean_v1/` — stronger replicated internal evidence from a stricter rerun of the real-world pack. This is not final blinded public proof.
```

## Recommended commit message

```text
docs(demos): add adjacent reuse internal rerun evidence update
```

## Recommended PR title

```text
Add repo-ready internal evidence update for adjacent reuse rerun clean v1
```

## Recommended PR description

This PR adds a repo-ready evidence update for the stricter internal rerun of the adjacent-mandate reuse proof pack.

What it adds:
- a GitHub-readable summary of the rerun
- machine-readable summary metrics
- explicit claim boundary and best-practice limits
- integration guidance that preserves the repo's current release posture

What it does not do:
- widen the root repo claim boundary
- represent the rerun as independent blinded public proof
- reframe the repo as already fully proven compounding infrastructure
