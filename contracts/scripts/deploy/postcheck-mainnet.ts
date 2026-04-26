import { readdirSync } from "node:fs";
import { join } from "node:path";
import hre from "hardhat";
import { getEnv } from "../lib/env";
import { readDeploymentConfig } from "../lib/config";
import { readManifest } from "../lib/deployment";
import { postcheckMarkdown } from "../lib/report";
import { writeText } from "../lib/io";

function latestDeploymentDir(network: string): string {
  const networkDir = join("deployments", network);
  const stamps = readdirSync(networkDir).sort();
  if (stamps.length === 0) {
    throw new Error(`No deployment folders found in ${networkDir}`);
  }
  return join(networkDir, stamps[stamps.length - 1]);
}

function addressByName(manifestPath: string): Record<string, string> {
  const manifest = readManifest(manifestPath);
  return Object.fromEntries(manifest.contracts.map((c) => [c.name, c.address]));
}

async function main(): Promise<void> {
  const env = getEnv();
  const config = readDeploymentConfig(hre.network.name as "mainnet" | "sepolia" | "mainnet-fork", env.DEPLOYMENT_CONFIG_PATH);
  const deploymentDir = process.argv[2] || latestDeploymentDir(hre.network.name);
  const addresses = addressByName(join(deploymentDir, "manifest.json"));

  const alphaNovaSeed = await hre.ethers.getContractAt("AlphaNovaSeedV25", addresses.AlphaNovaSeedV25);
  const signedAttestationVerifier = await hre.ethers.getContractAt("SignedAttestationVerifierV25", addresses.SignedAttestationVerifierV25);
  const thresholdNetworkAdapter = await hre.ethers.getContractAt("ThresholdNetworkAdapterV25", addresses.ThresholdNetworkAdapterV25);
  const reviewerRewardTreasury = await hre.ethers.getContractAt("ReviewerRewardTreasuryV25", addresses.ReviewerRewardTreasuryV25);
  const councilGovernance = await hre.ethers.getContractAt("CouncilGovernanceV25", addresses.CouncilGovernanceV25);
  const challengePolicy = await hre.ethers.getContractAt("ChallengePolicyModuleV25", addresses.ChallengePolicyModuleV25);
  const novaSeedRegistry = await hre.ethers.getContractAt("NovaSeedRegistryV25", addresses.NovaSeedRegistryV25);
  const workflowAdapter = await hre.ethers.getContractAt("NovaSeedWorkflowAdapterV25", addresses.NovaSeedWorkflowAdapterV25);

  const chain = await hre.ethers.provider.getNetwork();
  const report = await postcheckMarkdown({
    networkName: hre.network.name,
    chainId: chain.chainId,
    contracts: {
      alphaNovaSeed,
      signedAttestationVerifier,
      thresholdNetworkAdapter,
      reviewerRewardTreasury,
      councilGovernance,
      challengePolicy,
      novaSeedRegistry,
      workflowAdapter
    },
    expectedOwner: config.roles.adminOwner,
    rewardToken: config.dependencies.agiToken,
    agiJobManager: config.dependencies.agiJobManager
  });

  writeText(join(deploymentDir, "postcheck-report.md"), report);
  console.log(`Postcheck report written to ${join(deploymentDir, "postcheck-report.md")}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
