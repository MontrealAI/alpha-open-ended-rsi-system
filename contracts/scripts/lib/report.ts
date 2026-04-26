import hre from "hardhat";
import type { CoreContracts } from "./contracts";

export async function postcheckMarkdown(args: {
  networkName: string;
  chainId: bigint;
  contracts: CoreContracts;
  expectedOwner: string;
  rewardToken: string;
  agiJobManager: string;
}): Promise<string> {
  const registryOwner = await (args.contracts.novaSeedRegistry as any).owner();
  const registryRelease = await (args.contracts.novaSeedRegistry as any).releaseMetadata();
  const registryAddress = (args.contracts.novaSeedRegistry as any).target as string;
  const nftRegistry = await (args.contracts.alphaNovaSeed as any).registry();
  const distributorLinked = await (args.contracts.reviewerRewardTreasury as any).distributors(registryAddress);

  const expectedOwnerLower = args.expectedOwner.toLowerCase();
  const ownerMatch = registryOwner.toLowerCase() === expectedOwnerLower;

  return `# Post-deploy smoke check (${args.networkName})\n\n` +
    `- Chain ID: ${args.chainId}\n` +
    `- Registry release metadata: version=${registryRelease[0]}, hash=${registryRelease[1]}\n` +
    `- Registry owner: ${registryOwner} (${ownerMatch ? "matches expected" : "MISMATCH"})\n` +
    `- Seed NFT registry link: ${nftRegistry} (${nftRegistry.toLowerCase() === registryAddress.toLowerCase() ? "linked" : "MISMATCH"})\n` +
    `- Reviewer treasury distributor for registry: ${distributorLinked}\n` +
    `- Reward token dependency: ${args.rewardToken}\n` +
    `- AGI job manager dependency: ${args.agiJobManager}\n\n` +
    `## Fail-closed posture checks\n` +
    `- No trusted signer preloaded: ${await (args.contracts.signedAttestationVerifier as any).trustedSigners(args.expectedOwner)}\n` +
    `- No threshold profile preloaded: profile(0x0).active expected false\n` +
    `- No creators preloaded in registry for deployer: ${await (args.contracts.novaSeedRegistry as any).creators((await hre.ethers.getSigners())[0].address)}\n\n` +
    `## Manual review blockers before unpausing workflows\n` +
    `1. Confirm multisig/admin ownership target and execute handoff if still deployer-owned.\n` +
    `2. Review and set conservative challenge policy thresholds explicitly.\n` +
    `3. Add trusted signer and threshold profiles with evidence-backed governance approval.\n` +
    `4. Verify contracts on Etherscan and attach links to operator packet.\n`;
}
