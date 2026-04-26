#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if ! command -v echidna >/dev/null 2>&1; then
  echo "echidna binary not found in PATH; install echidna to run property campaigns." >&2
  exit 1
fi

echidna "echidna/harnesses/EchidnaTreasuryHarness.sol" --config echidna/config/treasury.yaml
echidna "echidna/harnesses/EchidnaGovernanceHarness.sol" --config echidna/config/governance.yaml
echidna "echidna/harnesses/EchidnaThresholdHarness.sol" --config echidna/config/threshold.yaml
echidna "echidna/harnesses/EchidnaRegistryHarness.sol" --config echidna/config/registry.yaml
echidna "echidna/harnesses/EchidnaWorkflowHarness.sol" --config echidna/config/workflow.yaml
echidna "echidna/harnesses/EchidnaAttestationHarness.sol" --config echidna/config/attestation.yaml
