export type Hex = `0x${string}`

export interface ManifestAttestation {
  seedId: Hex
  manifestHash: Hex
  ciphertextHash: Hex
  termId: bigint
  deadline: bigint
}

export interface DecryptionAttestation {
  requestId: Hex
  seedId: Hex
  plaintextHash: Hex
  completionHash: Hex
  termId: bigint
  deadline: bigint
}

export interface ThresholdBindingProfile {
  profileId: Hex
  provider: "lit" | "taco"
  networkName: string
  threshold: number
  committeeSize: number
  timeoutSeconds: number
  policyHash: Hex
}

export interface V26ThresholdBindingProfile {
  schemaVersion: "2.6"
  profileId: Hex
  seedId: Hex
  network: string
  policy: {
    requiredShares: number
    totalShares: number
    authorizedViewersRoot: Hex
  }
  createdAt: string
}

export interface V26DecryptionAttestation {
  schemaVersion: "2.6"
  seedId: Hex
  requestId: Hex
  profileId: Hex
  ciphertextHash: Hex
  plaintextHash: Hex
  threshold: {
    requiredShares: number
    collectedShares: number
  }
  signers: Array<{
    nodeId: string
    signature: string
  }>
  completedAt: string
}
