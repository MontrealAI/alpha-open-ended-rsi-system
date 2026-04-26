# Operator handoff checklist

Use this checklist after deployment artifacts are generated.

## Artifact packet to archive

From `contracts/deployments/<network>/<timestamp>/` archive:

- `manifest.json`
- `addresses.json`
- `checksums.txt`
- `postcheck-report.md`
- `operator-handoff.md`

## What operators must confirm

- Deployed addresses match expected module graph.
- Owner/admin for all contracts is the intended multisig or approved control address.
- No unauthorized signer or creator has been pre-authorized.
- Challenge and governance settings are conservative and evidence-backed.
- Verification status is recorded and reproducible from the manifest.

## Transfer and acceptance

- Run `npm run deploy:handoff` with `ALLOW_OWNERSHIP_TRANSFER=true`.
- The script prints both **before** and **after** owner values for each contract.
- By default, handoff reads the latest deployment manifest under `contracts/deployments/<network>/`.
- Optional explicit path override:
  - `npm --prefix contracts run deploy:handoff -- -- deployments/mainnet/<timestamp>`
- Explicit override is fail-closed: missing `<path>/manifest.json` throws
- Require two-person review of final owner state and checksum file.
- Store artifact packet in release provenance storage together with commit SHA.

## Caveat

This repository is a verifiable release candidate. Operator acceptance does not imply audited-final posture.
