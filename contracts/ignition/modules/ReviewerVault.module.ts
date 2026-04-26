import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const ReviewerVaultModule = buildModule("ReviewerVaultModule", (m) => {
  const initialOwner = m.getParameter("initialOwner");
  const rewardToken = m.getParameter("rewardToken");

  const reviewerRewardTreasury = m.contract("ReviewerRewardTreasuryV25", [initialOwner, rewardToken]);

  return { reviewerRewardTreasury };
});

export default ReviewerVaultModule;
