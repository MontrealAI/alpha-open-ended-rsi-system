# Mainnet deployment runbook (v2.6.0-rc.1)

> Warning: this repository is a **verifiable release candidate**. It is experimental software and requires operator review before any production action.

This runbook covers a fail-closed contract deployment flow for the existing `contracts/` Hardhat 3 workspace.

## Doctrine and operating constraints

- identity → proof → settlement → governance
- no value without evidence
- no autonomy without authority
- no settlement without validation

Operational defaults in this repo:

- fail-closed scripts and explicit safety gates
- reproducible deployment packets (`manifest.json`, checksums, postcheck)
- no automatic unpause/activation of permissive policy
- no automatic mainnet broadcast

## 1) Configure environment

```bash
cp contracts/.env.example contracts/.env
```

Required for deployment flow:

- `MAINNET_RPC_URL`
- `MAINNET_RPC_URL_SECONDARY` (recommended failover)
- `MAINNET_FORK_RPC_URL` (recommended fork source)
- `SEPOLIA_RPC_URL`
- `DEPLOYER_PRIVATE_KEY`
- `ADMIN_OWNER_ADDRESS`
- `ETHERSCAN_API_KEY` (required for verification)

Create network config files first:

```bash
cp contracts/deployment-config/mainnet.example.json contracts/deployment-config/mainnet.json
cp contracts/deployment-config/sepolia.example.json contracts/deployment-config/sepolia.json
```

Fill `roles` and `dependencies` with operator-reviewed addresses. Scripts fail closed if these files are missing.

Safety gates (all default `false`):

- `ALLOW_DEPLOY_TO_SEPOLIA`
- `ALLOW_DEPLOY_TO_MAINNET`
- `ALLOW_OWNERSHIP_TRANSFER`
- `ALLOW_ENS_PUBLISH`

## 2) Install and compile

```bash
npm --prefix contracts install
npm run contracts:build
npm --prefix contracts run test:unit
npm run contracts:test
npm run contracts:test:fork
```

## 3) Preflight checklist

```bash
npm run deploy:checklist
```

This validates environment shape and prints fail-closed reminders.

## 4) Required dry-run on mainnet fork

```bash
npm run deploy:fork
```

Writes an auditable packet to:

- `contracts/deployments/mainnet-fork/<timestamp>/manifest.json`
- `contracts/deployments/mainnet-fork/<timestamp>/addresses.json`
- `contracts/deployments/mainnet-fork/<timestamp>/checksums.txt`
- `contracts/deployments/mainnet-fork/<timestamp>/postcheck-report.md`
- `contracts/deployments/mainnet-fork/<timestamp>/operator-handoff.md`

## 5) Optional sepolia rehearsal

```bash
npm run deploy:sepolia
```

## 6) Explicit mainnet deployment

```bash
npm run deploy:mainnet -- --broadcast
```

This script is guarded and requires:

- `ALLOW_DEPLOY_TO_MAINNET=true`
- explicit `--broadcast` flag

## 7) Verify and postcheck

```bash
npm run deploy:verify
npm run deploy:postcheck
```

## 8) Ownership handoff

```bash
npm run deploy:handoff
```

Behavior:

- uses the latest `contracts/deployments/mainnet/<timestamp>/manifest.json` by default
- supports optional explicit path override:
  - `npm --prefix contracts run deploy:handoff -- -- deployments/mainnet/<timestamp>`
- explicit path is fail-closed: script errors if `<path>/manifest.json` is missing
- requires `ALLOW_OWNERSHIP_TRANSFER=true`

## 9) Optional ENS metadata publishing

```bash
npm --prefix contracts run deploy:ens
```

Requires `ALLOW_ENS_PUBLISH=true`, `ENS_NAME`, and `ENS_REGISTRY_ADDRESS` (`PUBLIC_RESOLVER_ADDRESS` / `NAMEWRAPPER_ADDRESS` are optional metadata hints).

## What remains closed by default

Deployment scripts do **not** auto-enable:

- registry creator allowlists
- attestation trusted signers
- threshold decryption profiles
- challenge policy opening steps

These remain manual, governance-reviewed actions.

## Manual review gates before any activation

1. Confirm admin owner/multisig control on all contracts.
2. Confirm external dependency addresses (`AGI_TOKEN_ADDRESS`, `AGIJOBMANAGER_ADDRESS`).
3. Validate manifest + checksum consistency.
4. Validate Etherscan verification status for each contract.
5. Record governance approval for each post-deploy activation action.
