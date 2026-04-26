# Adjacent-Mandate Reuse Proof Demo

## Summary
This is a **synthetic local demo** of the AGI ALPHA adjacent-mandate proof gate.

- Parent sector: Protocol and smart-contract correctness
- Mandate 1: review a first batch of protocol contracts and freeze one capability package
- Mandate 2: review an adjacent batch twice:
  - **control** without the package
  - **treatment** with the frozen package

## Frozen capability package
- Name: `ProtocolCybersecurityPack-v1`
- Legacy alias: `ProtocolAssurancePack-v1`
- Hash: `b9365fcdaff0141af0c27aa20a458c20ea25582220887735438d645144accef0`

## Mandate 2 results

### Control
- Accepted findings: 1
- AOY: 0.05
- First accepted step: 7
- Rework rate: 1.0
- Evidence completeness: 0.714
- Severe false positives: 1

### Treatment
- Accepted findings: 5
- AOY: 0.25
- First accepted step: 2
- Rework rate: 0.0
- Evidence completeness: 1.0
- Severe false positives: 0
- Package dependence: 1.0

## Threshold comparison
- AOY uplift: 400.0% → PASS
- Speed uplift: 71.4% → PASS
- Rework reduction: 100.0% → PASS
- Evidence completeness uplift: 40.1% → PASS
- No safety regression: PASS
- Package dependence ≥ 30%: 100.0% → PASS

## Verdict
**Adjacent-mandate proof:** PASS

This demo shows the structure of the proof:
one completed mandate created a frozen capability package that materially improved
the next adjacent mandate under control conditions.

## Important note
This is a **controlled synthetic demo**, not a real-world proof.
