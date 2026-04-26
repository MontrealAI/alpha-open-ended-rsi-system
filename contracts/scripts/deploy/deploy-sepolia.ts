import hre from "hardhat";
import { runDeployment } from "../lib/run-deployment";

async function main(): Promise<void> {
  if (hre.network.name !== "sepolia") {
    throw new Error(`Refusing to run: expected --network sepolia, got ${hre.network.name}`);
  }

  const result = await runDeployment("sepolia");
  console.log(`Sepolia deployment complete. Artifacts: ${result.outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
