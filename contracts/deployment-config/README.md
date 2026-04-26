# Deployment configuration profiles

This folder stores operator-reviewed configuration profiles used by deployment scripts.

## Posture

- Fail-closed defaults.
- No automatic activation of creators, signers, threshold profiles, or challenge policies.
- Ownership is set to `ADMIN_OWNER_ADDRESS` at deploy time, then re-checked in postcheck.

## Files

- `mainnet.example.json` — conservative reference values.
- `sepolia.example.json` — testnet reference values.

## Usage

1. Copy the network example to a concrete operator-reviewed file:
   - `cp contracts/deployment-config/mainnet.example.json contracts/deployment-config/mainnet.json`
   - `cp contracts/deployment-config/sepolia.example.json contracts/deployment-config/sepolia.json`
2. Replace placeholder addresses under `roles` and `dependencies`.
3. Keep `defaults` empty unless governance has approved a specific activation list.
4. Optionally set `DEPLOYMENT_CONFIG_PATH` in `contracts/.env` to target an alternate config location.

Deployment scripts fail closed if `<network>.json` is missing or malformed.
Deployment scripts also fail closed when the config `network` field does not match the active deploy target.
