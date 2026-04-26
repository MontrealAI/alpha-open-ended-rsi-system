import { readdirSync } from "node:fs";
import { join } from "node:path";
import hre from "hardhat";
import { getEnv } from "../lib/env";
import { deployedBytecodeHash, readManifest } from "../lib/deployment";
import { writeJson } from "../lib/io";

function latestDeploymentDir(network: string): string {
  const networkDir = join("deployments", network);
  const stamps = readdirSync(networkDir).sort();
  if (stamps.length === 0) {
    throw new Error(`No deployment folders found in ${networkDir}`);
  }
  return join(networkDir, stamps[stamps.length - 1]);
}

async function main(): Promise<void> {
  const env = getEnv();
  if (!env.ETHERSCAN_API_KEY) {
    throw new Error("ETHERSCAN_API_KEY is required for verification.");
  }

  const network = hre.network.name;
  const deploymentDir = process.argv[2] || latestDeploymentDir(network);
  const manifest = readManifest(join(deploymentDir, "manifest.json"));

  for (const contract of manifest.contracts) {
    const runtimeHash = await deployedBytecodeHash(hre, contract.address);
    if (runtimeHash !== contract.deployedBytecodeHash) {
      throw new Error(`Bytecode hash mismatch for ${contract.name}: manifest=${contract.deployedBytecodeHash} runtime=${runtimeHash}`);
    }

    try {
      await hre.run("verify:verify", {
        address: contract.address,
        constructorArguments: contract.constructorArgs
      });
      contract.verificationStatus = "verified";
      console.log(`Verified ${contract.name} at ${contract.address}`);
    } catch (error) {
      contract.verificationStatus = "failed";
      console.error(`Verification failed for ${contract.name} at ${contract.address}`);
      throw error;
    }
  }

  writeJson(join(deploymentDir, "manifest.json"), manifest);
  console.log(`Verification completed for ${manifest.contracts.length} contracts from ${deploymentDir}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
