import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { z } from "zod";

const deployConfigSchema = z.object({
  network: z.enum(["mainnet", "sepolia", "mainnet-fork"]),
  release: z.string().min(1),
  roles: z.object({
    adminOwner: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
    pauser: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
    emergencyGuardian: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
    treasury: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
    reviewerRewardTreasury: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
    councilAdmin: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional()
  }),
  dependencies: z.object({
    agiToken: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
    agiJobManager: z.string().regex(/^0x[a-fA-F0-9]{40}$/)
  }),
  defaults: z.object({
    trustedSigners: z.array(z.string()).default([]),
    creatorAllowlist: z.array(z.string()).default([]),
    thresholdProfiles: z.array(z.string()).default([]),
    challengePolicies: z.array(z.string()).default([])
  }),
  notes: z.array(z.string()).default([])
});

export type DeploymentConfig = z.infer<typeof deployConfigSchema>;

export function resolveConfigPath(network: "mainnet" | "sepolia" | "mainnet-fork", overridePath?: string): string {
  if (overridePath) return overridePath;
  const normalizedNetwork = network === "mainnet-fork" ? "mainnet" : network;
  return join("deployment-config", `${normalizedNetwork}.json`);
}

export function readDeploymentConfig(network: "mainnet" | "sepolia" | "mainnet-fork", overridePath?: string): DeploymentConfig {
  const configPath = resolveConfigPath(network, overridePath);
  if (!existsSync(configPath)) {
    throw new Error(
      `Deployment config file not found at ${configPath}. Copy deployment-config/${network === "mainnet-fork" ? "mainnet" : network}.example.json to ${configPath} and fill operator-reviewed values.`
    );
  }
  const parsed = deployConfigSchema.safeParse(JSON.parse(readFileSync(configPath, "utf8")));
  if (!parsed.success) {
    const details = parsed.error.issues.map((issue) => `- ${issue.path.join(".")}: ${issue.message}`).join("\n");
    throw new Error(`Deployment config validation failed for ${configPath}:\n${details}`);
  }
  const acceptedNetworks = network === "mainnet-fork" ? new Set(["mainnet", "mainnet-fork"]) : new Set([network]);
  if (!acceptedNetworks.has(parsed.data.network)) {
    throw new Error(
      `Deployment config network mismatch for ${configPath}: expected "${network}" but found "${parsed.data.network}".`
    );
  }
  return parsed.data;
}
