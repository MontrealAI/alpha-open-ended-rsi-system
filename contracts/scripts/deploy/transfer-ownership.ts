import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import hre from "hardhat";
import { assertSafetyFlag, getEnv } from "../lib/env";
import { readDeploymentConfig } from "../lib/config";
import { readManifest } from "../lib/deployment";

const EXPECTED_CONTRACT_NAMES = [
  "AlphaNovaSeedV25",
  "SignedAttestationVerifierV25",
  "ThresholdNetworkAdapterV25",
  "ReviewerRewardTreasuryV25",
  "CouncilGovernanceV25",
  "ChallengePolicyModuleV25",
  "NovaSeedRegistryV25",
  "NovaSeedWorkflowAdapterV25"
] as const;

function latestDeploymentDir(network: string): string {
  const networkDir = join("deployments", network);
  if (!existsSync(networkDir)) {
    throw new Error(`Deployment directory not found: ${networkDir}`);
  }
  const stamps = readdirSync(networkDir).sort();
  if (stamps.length === 0) {
    throw new Error(`No deployment folders found in ${networkDir}`);
  }
  return join(networkDir, stamps[stamps.length - 1]);
}

function addressesFromManifest(manifestPath: string): Record<string, string> {
  const manifest = readManifest(manifestPath);
  const byName = Object.fromEntries(manifest.contracts.map((c) => [c.name, c.address])) as Record<string, string>;

  const missing = EXPECTED_CONTRACT_NAMES.filter((name) => !byName[name]);
  if (missing.length > 0) {
    throw new Error(`Manifest is missing expected contracts: ${missing.join(", ")}`);
  }

  return Object.fromEntries(EXPECTED_CONTRACT_NAMES.map((name) => [name, byName[name]]));
}

function deploymentOverrideFromArgs(argv: string[]): string | undefined {
  const delimiterIndex = argv.lastIndexOf("--");
  if (delimiterIndex >= 0) {
    const afterDelimiter = argv[delimiterIndex + 1];
    if (afterDelimiter && !afterDelimiter.startsWith("-")) {
      return afterDelimiter;
    }
  }

  const scriptIndex = argv.findIndex((arg) => arg.includes("transfer-ownership."));
  if (scriptIndex >= 0) {
    const next = argv[scriptIndex + 1];
    if (next && !next.startsWith("-")) {
      return next;
    }
  }

  return undefined;
}

function addressesFromEnv(): Record<string, string | undefined> {
  return {
    AlphaNovaSeedV25: process.env.ALPHA_NOVA_SEED_ADDRESS,
    SignedAttestationVerifierV25: process.env.SIGNED_ATTESTATION_VERIFIER_ADDRESS,
    ThresholdNetworkAdapterV25: process.env.THRESHOLD_NETWORK_ADAPTER_ADDRESS,
    ReviewerRewardTreasuryV25: process.env.REVIEWER_REWARD_TREASURY_ADDRESS,
    CouncilGovernanceV25: process.env.COUNCIL_GOVERNANCE_ADDRESS,
    ChallengePolicyModuleV25: process.env.CHALLENGE_POLICY_MODULE_ADDRESS,
    NovaSeedRegistryV25: process.env.NOVA_SEED_REGISTRY_ADDRESS,
    NovaSeedWorkflowAdapterV25: process.env.NOVA_SEED_WORKFLOW_ADAPTER_ADDRESS
  };
}

async function transfer(name: string, contractAddress: string, newOwner: string): Promise<void> {
  const contract = await hre.ethers.getContractAt(name, contractAddress);
  const currentOwner = await (contract as any).owner();
  console.log(`${name}: before owner=${currentOwner}`);
  if (currentOwner.toLowerCase() === newOwner.toLowerCase()) {
    console.log(`${name}: after owner=${newOwner} (unchanged)`);
    return;
  }

  const tx = await (contract as any).transferOwnership(newOwner);
  await tx.wait();

  const updatedOwner = await (contract as any).owner();
  if (updatedOwner.toLowerCase() !== newOwner.toLowerCase()) {
    throw new Error(`${name}: transfer transaction mined but owner mismatch. expected=${newOwner} actual=${updatedOwner}`);
  }

  console.log(`${name}: after owner=${updatedOwner}. tx=${tx.hash}`);
}

async function main(): Promise<void> {
  assertSafetyFlag("ALLOW_OWNERSHIP_TRANSFER", "Ownership transfer");
  const env = getEnv();
  const config = readDeploymentConfig(
    hre.network.name as "mainnet" | "sepolia" | "mainnet-fork",
    env.DEPLOYMENT_CONFIG_PATH
  );
  const expectedOwner = config.roles.adminOwner;
  if (env.ADMIN_OWNER_ADDRESS.toLowerCase() !== expectedOwner.toLowerCase()) {
    throw new Error(
      `Owner mismatch: ADMIN_OWNER_ADDRESS=${env.ADMIN_OWNER_ADDRESS} does not match deployment-config roles.adminOwner=${expectedOwner}.`
    );
  }

  const explicitDeploymentDir = deploymentOverrideFromArgs(process.argv);

  let manifestPath: string | undefined;
  if (explicitDeploymentDir) {
    manifestPath = join(explicitDeploymentDir, "manifest.json");
  } else {
    try {
      manifestPath = join(latestDeploymentDir(hre.network.name), "manifest.json");
    } catch {
      manifestPath = undefined;
    }
  }

  let addresses: Record<string, string | undefined>;
  if (manifestPath && existsSync(manifestPath)) {
    addresses = addressesFromManifest(manifestPath);
    console.log(`Using contract addresses from manifest: ${manifestPath}`);
  } else {
    if (explicitDeploymentDir) {
      throw new Error(`Explicit deployment path provided but manifest not found: ${manifestPath}`);
    }
    addresses = addressesFromEnv();
    const reason = manifestPath ? `Manifest not found at ${manifestPath}` : `No deployment directory found for network ${hre.network.name}`;
    console.log(`${reason}. Falling back to explicit *_ADDRESS environment variables.`);
  }

  for (const [name, address] of Object.entries(addresses)) {
    if (!address) {
      throw new Error(`Missing ${name} address. Provide deployment manifest path or set environment addresses.`);
    }
    await transfer(name, address, expectedOwner);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
