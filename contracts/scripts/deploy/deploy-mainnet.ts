import hre from "hardhat";
import { runDeployment } from "../lib/run-deployment";

async function main(): Promise<void> {
  if (hre.network.name !== "mainnet") {
    throw new Error(`Refusing to run: expected --network mainnet, got ${hre.network.name}`);
  }

  if (process.env.CONFIRM_MAINNET_BROADCAST !== "true") {
    throw new Error("Mainnet script is fail-closed. Re-run from repository root with: npm run deploy:mainnet -- --broadcast");
  }

  const result = await runDeployment("mainnet");
  console.log(`Mainnet deployment complete. Artifacts: ${result.outDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
