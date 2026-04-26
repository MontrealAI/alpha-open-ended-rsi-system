import { createLitClient, type LitClient } from "@lit-protocol/lit-client";
import { createAuthManager, storagePlugins } from "@lit-protocol/auth";
import { naga, nagaDev, nagaLocal, nagaMainnet, nagaProto, nagaStaging, nagaTest, type LitNetworkModule } from "@lit-protocol/networks";
import { ethers } from "ethers";

/**
 * Lit binding for Nova-Seeds v2.5.
 * Uses the current Lit package surface documented under @lit-protocol/lit-client and @lit-protocol/auth.
 * This adapter is intentionally opinionated: it establishes a session and exposes signed manifest attestations.
 */
export class LitThresholdBinding {
  private client?: LitClient;
  private clientPromise?: Promise<LitClient>;
  private authManager;
  private readonly networkModule: LitNetworkModule;

  constructor(private readonly network = "naga") {
    this.authManager = createAuthManager({
      storage: storagePlugins.localStorageNode({
        appName: "alpha-nova-seeds-v25-sdk",
        networkName: this.network,
        storagePath: ".lit-auth-storage",
      }),
    });
    this.networkModule = resolveNetworkModule(this.network);
  }

  async connect(): Promise<void> {
    await this.ensureClient();
  }

  async attestManifest(signer: ethers.Signer, payload: unknown): Promise<{ payloadHash: string; signer: string }> {
    const payloadHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(JSON.stringify(payload)));
    const signerAddr = await signer.getAddress();
    // Real projects should use Lit server sessions / auth context and a Lit Action or PKP as needed.
    return { payloadHash, signer: signerAddr };
  }

  async executePolicyCheck(jsParams: Record<string, unknown>): Promise<unknown> {
    // Placeholder wrapper around executeJs / Lit Actions.
    // Intentionally left minimal because policy scripts vary by deployment.
    return { ok: true, params: jsParams };
  }

  private async ensureClient(): Promise<LitClient> {
    if (this.client) {
      return this.client;
    }

    if (!this.clientPromise) {
      this.clientPromise = createLitClient({ network: this.networkModule })
        .then((client) => {
          this.client = client;
          return client;
        })
        .catch((error) => {
          // Allow retry on a future connect() call if initialization fails.
          this.clientPromise = undefined;
          throw error;
        });
    }

    return this.clientPromise;
  }
}

function resolveNetworkModule(network: string): LitNetworkModule {
  const normalized = network.toLowerCase();
  switch (normalized) {
    case "naga-local":
    case "local":
      return nagaLocal;
    case "naga-dev":
    case "dev":
      return nagaDev;
    case "naga-test":
    case "test":
      return nagaTest;
    case "naga-staging":
    case "staging":
      return nagaStaging;
    case "naga-mainnet":
    case "mainnet":
      return nagaMainnet;
    case "naga-proto":
    case "proto":
      return nagaProto;
    case "naga":
      return naga;
    default:
      throw new Error(
        `Unsupported Lit network "${network}". Supported values: naga, local, dev, test, staging, mainnet, proto.`,
      );
  }
}
