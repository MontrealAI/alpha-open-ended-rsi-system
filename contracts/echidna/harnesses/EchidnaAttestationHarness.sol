// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../../SignedAttestationVerifierV25.sol";

contract AttestationAttacker {
    function setTrustedSigner(SignedAttestationVerifierV25 verifier, address signer, bool trusted) external {
        verifier.setTrustedSigner(signer, trusted);
    }
}

contract EchidnaAttestationHarness {
    SignedAttestationVerifierV25 internal verifier;
    AttestationAttacker internal attacker;

    address internal constant SIGNER = address(0xBEEF);

    bytes32 internal lastManifestDigest;
    bytes32 internal lastDecryptDigest;
    bytes32 internal lastChallengeDigest;
    address internal replaySigner;

    constructor() {
        verifier = new SignedAttestationVerifierV25(address(this));
        attacker = new AttestationAttacker();
    }

    function trustSigner(bool trusted) external {
        verifier.setTrustedSigner(SIGNER, trusted);
    }

    function bindReplaySignerTrust(bool trusted) external {
        if (lastManifestDigest == bytes32(0)) {
            return;
        }

        bytes memory canonicalSig = abi.encodePacked(bytes32(uint256(1)), bytes32(uint256(2)), bytes1(uint8(27)));
        (bool ok, bytes memory data) = address(verifier).staticcall(
            abi.encodeWithSelector(verifier.verify.selector, lastManifestDigest, canonicalSig)
        );
        if (!ok || data.length == 0) {
            return;
        }

        (address signer,) = abi.decode(data, (address, bool));
        replaySigner = signer;
        verifier.setTrustedSigner(signer, trusted);
    }

    function hashAll(bytes32 seedId, bytes32 requestId, bytes32 manifestHash, bytes32 ciphertextHash, bytes32 completionHash) external {
        if (seedId == bytes32(0)) {
            seedId = bytes32(uint256(1));
        }
        if (requestId == bytes32(0)) {
            requestId = bytes32(uint256(2));
        }

        lastManifestDigest = verifier.hashManifestAttestation(seedId, manifestHash, ciphertextHash, 1, block.timestamp + 1 days);
        lastDecryptDigest = verifier.hashDecryptAttestation(requestId, seedId, manifestHash, completionHash, 1, block.timestamp + 1 days);
        lastChallengeDigest = verifier.hashChallengeEvidence(requestId, seedId, manifestHash, 1, block.timestamp + 1 days);
        replaySigner = address(0);
    }

    function echidna_signer_trust_is_owner_only() external returns (bool) {
        (bool ok,) = address(attacker).call(
            abi.encodeWithSelector(attacker.setTrustedSigner.selector, verifier, address(attacker), true)
        );
        return !ok && !verifier.trustedSigners(address(attacker));
    }

    function echidna_domain_separation_between_attestation_types() external view returns (bool) {
        if (lastManifestDigest == bytes32(0) || lastDecryptDigest == bytes32(0) || lastChallengeDigest == bytes32(0)) {
            return true;
        }
        return lastManifestDigest != lastDecryptDigest
            && lastManifestDigest != lastChallengeDigest
            && lastDecryptDigest != lastChallengeDigest;
    }

    function echidna_malformed_signature_never_verifies() external view returns (bool) {
        bytes memory malformed = hex"0102";
        (bool ok,) = address(verifier).staticcall(abi.encodeWithSelector(verifier.verify.selector, keccak256("digest"), malformed));
        return !ok;
    }

    function echidna_no_replay_unsafe_auto_trust() external view returns (bool) {
        if (lastManifestDigest == bytes32(0)) return true;

        bytes memory canonicalSig = abi.encodePacked(bytes32(uint256(1)), bytes32(uint256(2)), bytes1(uint8(27)));

        (bool ok1, bytes memory data1) = address(verifier).staticcall(
            abi.encodeWithSelector(verifier.verify.selector, lastManifestDigest, canonicalSig)
        );
        if (!ok1 || data1.length == 0) return false;

        (address signer1, bool trusted1) = abi.decode(data1, (address, bool));

        (bool ok2, bytes memory data2) = address(verifier).staticcall(
            abi.encodeWithSelector(verifier.verify.selector, lastManifestDigest, canonicalSig)
        );
        if (!ok2 || data2.length == 0) return false;

        (address signer2, bool trusted2) = abi.decode(data2, (address, bool));
        bool expectedTrust = verifier.trustedSigners(signer1);

        if (replaySigner != address(0) && signer1 != replaySigner) {
            return false;
        }

        return signer1 == signer2 && trusted1 == trusted2 && trusted1 == expectedTrust;
    }
}
