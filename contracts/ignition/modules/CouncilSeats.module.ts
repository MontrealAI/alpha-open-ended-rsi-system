import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import GovernanceModule from "./Governance.module";

const CouncilSeatsModule = buildModule("CouncilSeatsModule", (m) => {
  const { councilGovernance } = m.useModule(GovernanceModule);

  return { councilGovernance };
});

export default CouncilSeatsModule;
