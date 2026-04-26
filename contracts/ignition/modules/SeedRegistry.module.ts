import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import GovernanceModule from "./Governance.module";
import ThresholdAttestorModule from "./ThresholdAttestor.module";
import ReviewerVaultModule from "./ReviewerVault.module";

const SeedRegistryModule = buildModule("SeedRegistryModule", (m) => {
  const initialOwner = m.getParameter("initialOwner");
  const rewardToken = m.getParameter("rewardToken");

  const { councilGovernance, challengePolicy } = m.useModule(GovernanceModule);
  const { signedAttestationVerifier, thresholdNetworkAdapter } = m.useModule(ThresholdAttestorModule);
  const { reviewerRewardTreasury } = m.useModule(ReviewerVaultModule);

  const alphaNovaSeed = m.contract("AlphaNovaSeedV25", [initialOwner]);
  const novaSeedRegistry = m.contract("NovaSeedRegistryV25", [
    initialOwner,
    alphaNovaSeed,
    thresholdNetworkAdapter,
    reviewerRewardTreasury,
    councilGovernance,
    challengePolicy
  ]);

  const agiJobManager = m.getParameter("agiJobManager");
  const workflowAdapter = m.contract("NovaSeedWorkflowAdapterV25", [initialOwner, novaSeedRegistry, agiJobManager]);

  m.call(alphaNovaSeed, "setRegistry", [novaSeedRegistry]);
  m.call(reviewerRewardTreasury, "setDistributor", [novaSeedRegistry, true]);

  return {
    alphaNovaSeed,
    signedAttestationVerifier,
    thresholdNetworkAdapter,
    reviewerRewardTreasury,
    councilGovernance,
    challengePolicy,
    novaSeedRegistry,
    workflowAdapter,
    rewardToken
  };
});

export default SeedRegistryModule;
