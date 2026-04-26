import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import SeedRegistryModule from "./SeedRegistry.module";

const CompositeMainnetModule = buildModule("CompositeMainnetModule", (m) => {
  const initialOwner = m.getParameter("initialOwner");
  const rewardToken = m.getParameter("rewardToken");
  const agiJobManager = m.getParameter("agiJobManager");

  const deployed = m.useModule(SeedRegistryModule, {
    parameters: {
      initialOwner,
      rewardToken,
      agiJobManager
    }
  });

  return deployed;
});

export default CompositeMainnetModule;
