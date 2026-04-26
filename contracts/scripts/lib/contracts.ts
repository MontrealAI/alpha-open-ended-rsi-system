import hre from "hardhat";
import type { BaseContract } from "ethers";
import CompositeMainnetModule from "../../ignition/modules/CompositeMainnet.module";

export type CoreContracts = {
  alphaNovaSeed: BaseContract;
  signedAttestationVerifier: BaseContract;
  thresholdNetworkAdapter: BaseContract;
  reviewerRewardTreasury: BaseContract;
  councilGovernance: BaseContract;
  challengePolicy: BaseContract;
  novaSeedRegistry: BaseContract;
  workflowAdapter: BaseContract;
};

export async function deployComposite(parameters: {
  initialOwner: string;
  rewardToken: string;
  agiJobManager: string;
}): Promise<CoreContracts> {
  const deployed = await hre.ignition.deploy(CompositeMainnetModule, { parameters });
  return deployed as unknown as CoreContracts;
}

export async function roleStateSummary(contracts: CoreContracts, owner: string): Promise<string> {
  const registryOwner = await (contracts.novaSeedRegistry as any).owner();
  const treasuryOwner = await (contracts.reviewerRewardTreasury as any).owner();
  const governanceOwner = await (contracts.councilGovernance as any).owner();
  const challengeOwner = await (contracts.challengePolicy as any).owner();
  const nftOwner = await (contracts.alphaNovaSeed as any).owner();
  const workflowOwner = await (contracts.workflowAdapter as any).owner();
  const verifierOwner = await (contracts.signedAttestationVerifier as any).owner();
  const thresholdOwner = await (contracts.thresholdNetworkAdapter as any).owner();

  const lines = [
    `- expected owner: ${owner}`,
    `- NovaSeedRegistryV25.owner: ${registryOwner}`,
    `- ReviewerRewardTreasuryV25.owner: ${treasuryOwner}`,
    `- CouncilGovernanceV25.owner: ${governanceOwner}`,
    `- ChallengePolicyModuleV25.owner: ${challengeOwner}`,
    `- AlphaNovaSeedV25.owner: ${nftOwner}`,
    `- NovaSeedWorkflowAdapterV25.owner: ${workflowOwner}`,
    `- SignedAttestationVerifierV25.owner: ${verifierOwner}`,
    `- ThresholdNetworkAdapterV25.owner: ${thresholdOwner}`
  ];

  return lines.join("\n");
}

export async function assertOwnership(contracts: CoreContracts, owner: string): Promise<void> {
  const checks: Array<[string, string]> = [
    ["NovaSeedRegistryV25", await (contracts.novaSeedRegistry as any).owner()],
    ["ReviewerRewardTreasuryV25", await (contracts.reviewerRewardTreasury as any).owner()],
    ["CouncilGovernanceV25", await (contracts.councilGovernance as any).owner()],
    ["ChallengePolicyModuleV25", await (contracts.challengePolicy as any).owner()],
    ["AlphaNovaSeedV25", await (contracts.alphaNovaSeed as any).owner()],
    ["NovaSeedWorkflowAdapterV25", await (contracts.workflowAdapter as any).owner()],
    ["SignedAttestationVerifierV25", await (contracts.signedAttestationVerifier as any).owner()],
    ["ThresholdNetworkAdapterV25", await (contracts.thresholdNetworkAdapter as any).owner()]
  ];

  const mismatched = checks.filter(([, actual]) => actual.toLowerCase() !== owner.toLowerCase());
  if (mismatched.length > 0) {
    throw new Error(`Ownership mismatch: ${JSON.stringify(mismatched)}`);
  }
}

export function getAddressMap(contracts: CoreContracts): Record<string, string> {
  return {
    AlphaNovaSeedV25: (contracts.alphaNovaSeed as any).target as string,
    SignedAttestationVerifierV25: (contracts.signedAttestationVerifier as any).target as string,
    ThresholdNetworkAdapterV25: (contracts.thresholdNetworkAdapter as any).target as string,
    ReviewerRewardTreasuryV25: (contracts.reviewerRewardTreasury as any).target as string,
    CouncilGovernanceV25: (contracts.councilGovernance as any).target as string,
    ChallengePolicyModuleV25: (contracts.challengePolicy as any).target as string,
    NovaSeedRegistryV25: (contracts.novaSeedRegistry as any).target as string,
    NovaSeedWorkflowAdapterV25: (contracts.workflowAdapter as any).target as string
  };
}
