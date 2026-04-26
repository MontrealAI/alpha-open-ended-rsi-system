import { ethers } from "ethers";
import type { ManifestAttestation, DecryptionAttestation } from "./types.js";

type Eip712Signer = ethers.Signer & {
  _signTypedData: (
    domain: { name: string; version: string; chainId: number; verifyingContract: string },
    types: Record<string, Array<{ name: string; type: string }>>,
    value: unknown,
  ) => Promise<string>;
};

export const domain = (chainId: number, verifyingContract: string) => ({
  name: "NovaSeedAttestations",
  version: "2.5",
  chainId,
  verifyingContract,
});

export const manifestTypes = {
  ManifestAttestation: [
    { name: "seedId", type: "bytes32" },
    { name: "manifestHash", type: "bytes32" },
    { name: "ciphertextHash", type: "bytes32" },
    { name: "termId", type: "uint256" },
    { name: "deadline", type: "uint256" },
  ],
};

export const decryptTypes = {
  DecryptAttestation: [
    { name: "requestId", type: "bytes32" },
    { name: "seedId", type: "bytes32" },
    { name: "plaintextHash", type: "bytes32" },
    { name: "completionHash", type: "bytes32" },
    { name: "termId", type: "uint256" },
    { name: "deadline", type: "uint256" },
  ],
};

export async function signManifestAttestation(
  signer: ethers.Signer,
  chainId: number,
  verifyingContract: string,
  value: ManifestAttestation,
): Promise<string> {
  return (signer as Eip712Signer)._signTypedData(domain(chainId, verifyingContract), manifestTypes, value as any);
}

export async function signDecryptAttestation(
  signer: ethers.Signer,
  chainId: number,
  verifyingContract: string,
  value: DecryptionAttestation,
): Promise<string> {
  return (signer as Eip712Signer)._signTypedData(domain(chainId, verifyingContract), decryptTypes, value as any);
}
