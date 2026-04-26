# DESIGN NOTES

This flagship demo uses deterministic rule-based issue extraction from synthetic Solidity fixtures.

Design goals:

- keep outputs replayable on a clean machine
- keep business narrative operator-readable
- make package promotion and adjacent test explicit
- keep safety regression checks fail-closed

Why deterministic:

- no random sampling
- no external service dependencies
- fixed synthetic fixture set and ground truth
