# Open-Ended RSI System — Determinism Replay Check (v1)

This folder records a **local deterministic replay check** for:

```text
python3 demos/open-ended-rsi-system/run_demo.py --assert
```

It documents that a second-pass rerun produced the **same determinism fingerprint** as the first pass on the same machine / same repo state.

## Why this exists

The `open-ended-rsi-system` demo claims to be a deterministic, bounded proof-of-mechanism. A replay check is therefore useful because it tests whether the demo produces stable machine-readable outputs across repeated local runs.

## What was checked

Two local runs were compared using the documented replay workflow:

```bash
python3 demos/open-ended-rsi-system/run_demo.py --assert
cp demos/open-ended-rsi-system/out/determinism_fingerprint.json /tmp/rsi-fingerprint-a.json
python3 demos/open-ended-rsi-system/run_demo.py --assert
diff -u /tmp/rsi-fingerprint-a.json demos/open-ended-rsi-system/out/determinism_fingerprint.json
```

## Outcome

- Second pass result: **PASS**
- Fingerprint diff output: **empty**
- Diff exit code: **0**
- SHA-256 digests: **identical**

## Fingerprint fields that matched exactly

- `release_target`: `v2.8.0-rc.2`
- `seed`: `2802`
- `candidate_pool_size`: `48`
- `selected_domain`: `backend_api_correctness`
- `frozen_package_manifest_hash`: `56dfb240a9b6b73c91cb4bb7b06efba543956dea0d4760a0c3f8bd41c5da0f75`
- `scorecard_hash`: `f3f2db44bb61b1e2880b21fc7ec6286fd7ae58cbe178c6eea938d0b893352d91`
- `lineage_hash`: `634e0dbd96d3cc51cc6494a2b04a76cfe8eec022eb9cd862415f1c165ed6d9c6`

## Relevant demo result snapshot

Generation 1 observed values from the current local run:

- AOY uplift: **42.45%**
- Speed uplift: **35.80%**
- Rework reduction: **41.94%**
- Evidence completeness uplift: **25.00%**
- Package dependence: **61.00%**
- Safety regression: **none observed**

Longitudinal values:

- Frontier width: **6**
- Autonomy delta: **75.00%**
- Neighborhood slope: **0.0004**
- Archive depth: **2**

## What this supports

This result supports the narrower claim that the demo's **determinism fingerprint is stable across repeated local replay** on the same machine / same repo state.

## What this does not prove

This does **not** prove:

- unrestricted autonomy
- literal or general unbounded recursive self-improvement
- independent external validation
- real-world broad sovereign operation

## Files in this folder

- `fingerprint_pass1.json` — first replay fingerprint
- `fingerprint_pass2.json` — second replay fingerprint
- `fingerprint_diff.txt` — unified diff output (empty means no drift)
- `fingerprint_sha256.txt` — matching SHA-256 digests for both fingerprints
- `second_pass.log` — second replay command result
- `summary_metrics.json` — compact summary of the replay check and key demo metrics
