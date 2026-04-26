import { getEnv } from "../lib/env";
import { readDeploymentConfig } from "../lib/config";

const validateOnly = process.argv.includes("--validate-only");

async function main(): Promise<void> {
  const env = getEnv();
  const config = readDeploymentConfig("mainnet", env.DEPLOYMENT_CONFIG_PATH);

  const checklist = [
    ["ADMIN_OWNER_ADDRESS configured", Boolean(env.ADMIN_OWNER_ADDRESS)],
    ["mainnet deployment-config JSON available", Boolean(config.roles.adminOwner)],
    ["Mainnet RPC configured", Boolean(env.MAINNET_RPC_URL)],
    ["Mainnet fork RPC configured (or fallback mainnet RPC)", Boolean(env.MAINNET_FORK_RPC_URL || env.MAINNET_RPC_URL)],
    ["Mainnet secondary RPC configured", Boolean(env.MAINNET_RPC_URL_SECONDARY)],
    ["Sepolia RPC configured", Boolean(env.SEPOLIA_RPC_URL)],
    ["Mainnet deploy gate", env.ALLOW_DEPLOY_TO_MAINNET === "true"],
    ["Sepolia deploy gate", env.ALLOW_DEPLOY_TO_SEPOLIA === "true"],
    ["Ownership transfer gate", env.ALLOW_OWNERSHIP_TRANSFER === "true"]
  ] as const;

  console.log("# Nova-Seeds deployment checklist");
  for (const [item, ok] of checklist) {
    console.log(`- [${ok ? "x" : " "}] ${item}`);
  }

  if (validateOnly) {
    console.log("\nValidation-only mode complete.");
    return;
  }

  console.log("\nFail-closed policy reminders:");
  console.log("- Contracts deploy with owner control only; no creator/signer/profile auto-activation.");
  console.log("- No script auto-unpauses or opens permissive policy flags.");
  console.log("- Review docs/mainnet-deployment.md before broadcast.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
