import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { HardhatRuntimeEnvironment } from "hardhat/types";
import { ensureDir, generateChecksums, timestampTag, writeJson, writeText } from "./io";
import { getGitCommitSha } from "./git";

export type DeployedAddressMap = Record<string, string>;
export const EXPECTED_RELEASE = "2.6.0-rc.1";

export type DeploymentManifest = {
  schema: "alpha-nova-seeds/deployment-manifest/v1";
  release: string;
  generatedAt: string;
  chainId: number;
  network: string;
  commitSha: string;
  contracts: Array<{
    name: string;
    address: string;
    constructorArgs: unknown[];
    deployedBytecodeHash: string;
    artifactPath: string;
    buildInfoHint: string;
    verificationStatus: "pending" | "verified" | "failed";
  }>;
  operator: {
    deployer: string;
    adminOwner: string;
    pauserAddress: string | null;
    treasuryAddress: string | null;
  };
  externalDependencies: {
    agiTokenAddress: string;
    agiJobManagerAddress: string;
  };
  notes: string[];
  sbom: {
    status: "placeholder";
    path: "release/sbom.json";
  };
};

export async function deployedBytecodeHash(hre: HardhatRuntimeEnvironment, address: string): Promise<string> {
  const bytecode = await hre.ethers.provider.getCode(address);
  return createHash("sha256").update(bytecode).digest("hex");
}

export function artifactHint(contractName: string): { artifactPath: string; buildInfoHint: string } {
  return {
    artifactPath: `artifacts/${contractName}.sol/${contractName}.json`,
    buildInfoHint: "artifacts/build-info/*.json"
  };
}

export function deploymentOutputDir(networkName: string, stamp = timestampTag()): string {
  return join("deployments", networkName, stamp);
}

export function writeDeploymentArtifacts(baseDir: string, manifest: DeploymentManifest, addresses: DeployedAddressMap, postcheckReport: string, handoff: string): void {
  ensureDir(baseDir);
  writeJson(join(baseDir, "manifest.json"), manifest);
  writeJson(join(baseDir, "addresses.json"), addresses);
  writeText(join(baseDir, "postcheck-report.md"), postcheckReport);
  writeText(join(baseDir, "operator-handoff.md"), handoff);
  const checksums = generateChecksums(baseDir);
  writeText(join(baseDir, "checksums.txt"), `${checksums}\n`);
}

export function buildOperatorHandoff(args: {
  chainId: number;
  network: string;
  adminOwner: string;
  contracts: DeployedAddressMap;
  pauseStateSummary: string;
  allowlistSummary: string;
  thresholdSummary: string;
  verificationSummary: string;
  ensSummary: string;
}): string {
  return `# Nova-Seeds operator handoff (${args.network})\n\n` +
    `> Experimental software. Operator review is required before any unpause or activation action.\n\n` +
    `## Deployment coordinates\n` +
    `- Network: ${args.network} (chainId ${args.chainId})\n` +
    `- Admin owner target: ${args.adminOwner}\n\n` +
    `## Addresses\n` +
    Object.entries(args.contracts).map(([name, address]) => `- ${name}: ${address}`).join("\n") +
    `\n\n## Pause state\n${args.pauseStateSummary}\n\n` +
    `## Allowlist / privileged roles\n${args.allowlistSummary}\n\n` +
    `## Threshold and governance defaults\n${args.thresholdSummary}\n\n` +
    `## Verification\n${args.verificationSummary}\n\n` +
    `## ENS metadata publishing\n${args.ensSummary}\n`;
}

export function readManifest(path: string): DeploymentManifest {
  return JSON.parse(readFileSync(path, "utf8")) as DeploymentManifest;
}

export function newBaseManifest(args: {
  release: string;
  network: string;
  chainId: number;
  deployer: string;
  adminOwner: string;
  pauserAddress?: string;
  treasuryAddress?: string;
  agiTokenAddress: string;
  agiJobManagerAddress: string;
}): DeploymentManifest {
  return {
    schema: "alpha-nova-seeds/deployment-manifest/v1",
    release: args.release,
    generatedAt: new Date().toISOString(),
    chainId: args.chainId,
    network: args.network,
    commitSha: getGitCommitSha(),
    contracts: [],
    operator: {
      deployer: args.deployer,
      adminOwner: args.adminOwner,
      pauserAddress: args.pauserAddress ?? null,
      treasuryAddress: args.treasuryAddress ?? null
    },
    externalDependencies: {
      agiTokenAddress: args.agiTokenAddress,
      agiJobManagerAddress: args.agiJobManagerAddress
    },
    notes: [
      "Fail-closed posture: no script in this workspace unpauses or opens permissive policy by default.",
      "Manual operator review required before enabling creators, signers, profiles, or policy activation."
    ],
    sbom: {
      status: "placeholder",
      path: "release/sbom.json"
    }
  };
}
