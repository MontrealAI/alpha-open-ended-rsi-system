// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SignedAttestationVerifierV25 is EIP712, Ownable {
    using ECDSA for bytes32;

    bytes32 public constant MANIFEST_ATTEST_TYPEHASH = keccak256(
        "ManifestAttestation(bytes32 seedId,bytes32 manifestHash,bytes32 ciphertextHash,uint256 termId,uint256 deadline)"
    );
    bytes32 public constant DECRYPT_ATTEST_TYPEHASH = keccak256(
        "DecryptAttestation(bytes32 requestId,bytes32 seedId,bytes32 plaintextHash,bytes32 completionHash,uint256 termId,uint256 deadline)"
    );
    bytes32 public constant CHALLENGE_EVIDENCE_TYPEHASH = keccak256(
        "ChallengeEvidence(bytes32 challengeId,bytes32 seedId,bytes32 evidenceHash,uint256 termId,uint256 deadline)"
    );

    mapping(address => bool) public trustedSigners;

    /// @notice Construct verifier with EIP-712 domain for Nova-Seed attestations.
    constructor(address initialOwner) EIP712("NovaSeedAttestations", "2.5") Ownable(initialOwner) {}

    /// @notice Allow or revoke trusted signers for proof attestations.
    function setTrustedSigner(address signer, bool trusted) external onlyOwner {
        trustedSigners[signer] = trusted;
    }

    /// @notice Hash a manifest-attestation payload for off-chain signing.
    function hashManifestAttestation(
        bytes32 seedId,
        bytes32 manifestHash,
        bytes32 ciphertextHash,
        uint256 termId,
        uint256 deadline
    ) public view returns (bytes32) {
        bytes32 structHash = keccak256(abi.encode(MANIFEST_ATTEST_TYPEHASH, seedId, manifestHash, ciphertextHash, termId, deadline));
        return _hashTypedDataV4(structHash);
    }

    /// @notice Hash a decryption-attestation payload for off-chain signing.
    function hashDecryptAttestation(
        bytes32 requestId,
        bytes32 seedId,
        bytes32 plaintextHash,
        bytes32 completionHash,
        uint256 termId,
        uint256 deadline
    ) public view returns (bytes32) {
        bytes32 structHash = keccak256(abi.encode(DECRYPT_ATTEST_TYPEHASH, requestId, seedId, plaintextHash, completionHash, termId, deadline));
        return _hashTypedDataV4(structHash);
    }

    /// @notice Hash a challenge-evidence payload for off-chain signing.
    function hashChallengeEvidence(
        bytes32 challengeId,
        bytes32 seedId,
        bytes32 evidenceHash,
        uint256 termId,
        uint256 deadline
    ) public view returns (bytes32) {
        bytes32 structHash = keccak256(abi.encode(CHALLENGE_EVIDENCE_TYPEHASH, challengeId, seedId, evidenceHash, termId, deadline));
        return _hashTypedDataV4(structHash);
    }

    /// @notice Recover signer and return trust status for a digest/signature pair.
    function verify(bytes32 digest, bytes calldata signature) external view returns (address signer, bool trusted) {
        signer = ECDSA.recover(digest, signature);
        trusted = trustedSigners[signer];
    }
}
