import hre from "hardhat";
import { assertSafetyFlag, getEnv } from "../lib/env";

async function main(): Promise<void> {
  assertSafetyFlag("ALLOW_ENS_PUBLISH", "ENS metadata publish");
  const env = getEnv();

  if (!env.ENS_NAME || !env.ENS_REGISTRY_ADDRESS) {
    throw new Error("ENS_NAME and ENS_REGISTRY_ADDRESS are required for ENS publishing.");
  }

  console.log("ENS publishing is operator-gated and intentionally minimal in RC posture.");
  console.log(`Configured ENS name: ${env.ENS_NAME}`);
  console.log(`Configured registry: ${env.ENS_REGISTRY_ADDRESS}`);
  console.log("Attach deployment manifest CID or URL in your ENS text records via approved operator wallet tooling.");
  console.log(`Network: ${hre.network.name}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
