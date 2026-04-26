import hre from "hardhat";
import { assertSafetyFlag, getEnv } from "./env";
import { assertOwnership, deployComposite, getAddressMap, type CoreContracts, roleStateSummary } from "./contracts";
import { EXPECTED_RELEASE, artifactHint, deployedBytecodeHash, deploymentOutputDir, newBaseManifest, writeDeploymentArtifacts } from "./deployment";
import { postcheckMarkdown } from "./report";
import { readDeploymentConfig } from "./config";

export async function runDeployment(networkName: "mainnet" | "sepolia" | "mainnet-fork", options?: { enforceGate?: boolean; outputNetworkName?: string; }): Promise<{ outDir: string; addresses: Record<string, string>; contracts: CoreContracts; }> {
  const env = getEnv();
  const config = readDeploymentConfig(networkName, env.DEPLOYMENT_CONFIG_PATH);
  if (config.release !== EXPECTED_RELEASE) {
    throw new Error(`Deployment config release mismatch: expected ${EXPECTED_RELEASE} but got ${config.release}.`);
  }
  const [deployer] = await hre.ethers.getSigners();
  const chain = await hre.ethers.provider.getNetwork();

  if (options?.enforceGate !== false) {
    if (networkName === "mainnet") {
      assertSafetyFlag("ALLOW_DEPLOY_TO_MAINNET", "Mainnet deployment");
    }
    if (networkName === "sepolia") {
      assertSafetyFlag("ALLOW_DEPLOY_TO_SEPOLIA", "Sepolia deployment");
    }
  }

  const contracts = await deployComposite({
    initialOwner: config.roles.adminOwner,
    rewardToken: config.dependencies.agiToken,
    agiJobManager: config.dependencies.agiJobManager
  });

  await assertOwnership(contracts, config.roles.adminOwner);

  const addresses = getAddressMap(contracts);

  const constructorArgsByName: Record<string, unknown[]> = {
    AlphaNovaSeedV25: [config.roles.adminOwner],
    SignedAttestationVerifierV25: [config.roles.adminOwner],
    ThresholdNetworkAdapterV25: [config.roles.adminOwner, addresses.SignedAttestationVerifierV25],
    ReviewerRewardTreasuryV25: [config.roles.adminOwner, config.dependencies.agiToken],
    CouncilGovernanceV25: [config.roles.adminOwner],
    ChallengePolicyModuleV25: [config.roles.adminOwner],
    NovaSeedRegistryV25: [
      config.roles.adminOwner,
      addresses.AlphaNovaSeedV25,
      addresses.ThresholdNetworkAdapterV25,
      addresses.ReviewerRewardTreasuryV25,
      addresses.CouncilGovernanceV25,
      addresses.ChallengePolicyModuleV25
    ],
    NovaSeedWorkflowAdapterV25: [config.roles.adminOwner, addresses.NovaSeedRegistryV25, config.dependencies.agiJobManager]
  };

  const manifest = newBaseManifest({
    release: config.release,
    network: options?.outputNetworkName ?? networkName,
    chainId: Number(chain.chainId),
    deployer: deployer.address,
    adminOwner: config.roles.adminOwner,
    pauserAddress: config.roles.pauser,
    treasuryAddress: config.roles.treasury,
    agiTokenAddress: config.dependencies.agiToken,
    agiJobManagerAddress: config.dependencies.agiJobManager
  });
  manifest.notes.push(...config.notes);

  for (const [name, address] of Object.entries(addresses)) {
    const bytecodeHash = await deployedBytecodeHash(hre, address);
    const hint = artifactHint(name);
    manifest.contracts.push({
      name,
      address,
      constructorArgs: constructorArgsByName[name] ?? [],
      deployedBytecodeHash: bytecodeHash,
      artifactPath: hint.artifactPath,
      buildInfoHint: hint.buildInfoHint,
      verificationStatus: "pending"
    });
  }

  const roleSummary = await roleStateSummary(contracts, config.roles.adminOwner);
  const postcheck = await postcheckMarkdown({
    networkName: options?.outputNetworkName ?? networkName,
    chainId: chain.chainId,
    contracts,
    expectedOwner: config.roles.adminOwner,
    rewardToken: config.dependencies.agiToken,
    agiJobManager: config.dependencies.agiJobManager
  });

  const handoff = `# Ownership and role handoff status\n\n${roleSummary}\n\n` +
    `## Transfer status\n` +
    `- Initial owner set at deployment: ${config.roles.adminOwner}\n` +
    `- Additional transfer required: only if temporary owner deployment path was used.\n`;

  const outDir = deploymentOutputDir(options?.outputNetworkName ?? networkName);
  writeDeploymentArtifacts(outDir, manifest, addresses, postcheck, handoff);

  return { outDir, addresses, contracts };
}
