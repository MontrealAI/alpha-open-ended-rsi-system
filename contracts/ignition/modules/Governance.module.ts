import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

const GovernanceModule = buildModule("GovernanceModule", (m) => {
  const initialOwner = m.getParameter("initialOwner");

  const councilGovernance = m.contract("CouncilGovernanceV25", [initialOwner]);
  const challengePolicy = m.contract("ChallengePolicyModuleV25", [initialOwner]);

  return { councilGovernance, challengePolicy };
});

export default GovernanceModule;
