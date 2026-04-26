import { initialize, encrypt, decrypt, conditions, domains, ThresholdMessageKit } from "@nucypher/taco";
import { EIP4361AuthProvider, USER_ADDRESS_PARAM_DEFAULT } from "@nucypher/taco-auth";
import { ethers } from "ethers";

/**
 * TACo binding for Nova-Seeds v2.5.
 * Mirrors the current TACo docs: @nucypher/taco + @nucypher/taco-auth and ethers v5.
 */
export class TacoThresholdBinding {
  private initialized = false;

  async init(): Promise<void> {
    if (!this.initialized) {
      await initialize();
      this.initialized = true;
    }
  }

  async encryptForTokenHolder(
    provider: ethers.providers.Web3Provider,
    ritualId: number,
    contractAddress: string,
    tokenId: number,
    plaintext: Uint8Array,
  ): Promise<ThresholdMessageKit> {
    await this.init();
    const ownsNFT = new conditions.predefined.erc721.ERC721Ownership({
      contractAddress,
      chain: 1,
      parameters: [tokenId],
    });
    return encrypt(provider, domains.MAINNET, plaintext, ownsNFT, ritualId, provider.getSigner());
  }

  async decryptWithWallet(
    provider: ethers.providers.Web3Provider,
    messageKit: ThresholdMessageKit,
  ): Promise<Uint8Array> {
    await this.init();
    const ctx = conditions.context.ConditionContext.fromMessageKit(messageKit);
    const authProvider = new EIP4361AuthProvider(provider, provider.getSigner());
    ctx.addAuthProvider(USER_ADDRESS_PARAM_DEFAULT, authProvider);
    return decrypt(provider, domains.MAINNET, messageKit, ctx);
  }
}
