import "dotenv/config";
import { z } from "zod";

const blankToUndefined = (value: unknown): unknown =>
  typeof value === "string" && value.trim() === "" ? undefined : value;

const optionalUrl = z.preprocess(blankToUndefined, z.string().url().optional());
const optionalAddress = z.preprocess(blankToUndefined, z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional());
const optionalString = z.preprocess(blankToUndefined, z.string().min(1).optional());

const envSchema = z.object({
  MAINNET_RPC_URL: optionalUrl,
  MAINNET_RPC_URL_SECONDARY: optionalUrl,
  MAINNET_FORK_RPC_URL: optionalUrl,
  SEPOLIA_RPC_URL: optionalUrl,
  ETHERSCAN_API_KEY: optionalString,
  DEPLOYER_PRIVATE_KEY: optionalString,
  DEPLOYMENT_CONFIG_PATH: optionalString,
  ADMIN_OWNER_ADDRESS: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
  PAUSER_ADDRESS: optionalAddress,
  EMERGENCY_GUARDIAN_ADDRESS: optionalAddress,
  TREASURY_ADDRESS: optionalAddress,
  REVIEWER_REWARD_TREASURY_ADDRESS: optionalAddress,
  COUNCIL_ADMIN_ADDRESS: optionalAddress,
  ENS_REGISTRY_ADDRESS: optionalAddress,
  NAMEWRAPPER_ADDRESS: optionalAddress,
  PUBLIC_RESOLVER_ADDRESS: optionalAddress,
  ENS_NAME: optionalString,
  AGI_TOKEN_ADDRESS: optionalAddress,
  AGIJOBMANAGER_ADDRESS: optionalAddress,
  ALLOW_DEPLOY_TO_SEPOLIA: z.enum(["true", "false"]).default("false"),
  ALLOW_DEPLOY_TO_MAINNET: z.enum(["true", "false"]).default("false"),
  ALLOW_OWNERSHIP_TRANSFER: z.enum(["true", "false"]).default("false"),
  ALLOW_ENS_PUBLISH: z.enum(["true", "false"]).default("false")
});

export type DeployEnv = z.infer<typeof envSchema>;

export function getEnv(): DeployEnv {
  const parsed = envSchema.safeParse(process.env);
  if (!parsed.success) {
    const details = parsed.error.issues
      .map((issue) => `- ${issue.path.join(".") || "env"}: ${issue.message}`)
      .join("\n");
    throw new Error(`Environment validation failed:\n${details}`);
  }
  return parsed.data;
}

export function assertSafetyFlag(flag: keyof Pick<DeployEnv, "ALLOW_DEPLOY_TO_MAINNET" | "ALLOW_DEPLOY_TO_SEPOLIA" | "ALLOW_OWNERSHIP_TRANSFER" | "ALLOW_ENS_PUBLISH">, context: string): void {
  const env = getEnv();
  if (env[flag] !== "true") {
    throw new Error(`${context} blocked: set ${flag}=true to continue.`);
  }
}
