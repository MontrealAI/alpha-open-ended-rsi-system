// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./SignedAttestationVerifierV25.sol";

contract ThresholdNetworkAdapterV25 is Ownable {
    enum RequestStatus { NONE, OPEN, FULFILLED, CHALLENGED, CANCELLED }

    struct BindingProfile {
        bytes32 profileId;
        string provider;
        string networkName;
        bytes32 committeeRoot;
        bytes32 relayerRoot;
        uint16 committeeSize;
        uint16 threshold;
        uint64 timeoutSeconds;
        bytes32 policyHash;
        bool active;
    }

    struct DecryptionRequest {
        bytes32 requestId;
        bytes32 seedId;
        bytes32 profileId;
        address requester;
        bytes32 ciphertextHash;
        bytes32 manifestHash;
        uint64 openedAt;
        uint64 deadline;
        RequestStatus status;
        bytes32 completionHash;
        bytes32 plaintextHash;
    }

    SignedAttestationVerifierV25 public immutable verifier;
    mapping(bytes32 => BindingProfile) public profiles;
    mapping(bytes32 => DecryptionRequest) public requests;

    event BindingProfileSet(bytes32 indexed profileId, string provider, string networkName, uint16 threshold, uint64 timeoutSeconds, bool active);
    event DecryptionRequested(bytes32 indexed requestId, bytes32 indexed seedId, bytes32 indexed profileId, address requester);
    event DecryptionCompleted(bytes32 indexed requestId, bytes32 plaintextHash, bytes32 completionHash);
    event DecryptionChallenged(bytes32 indexed requestId, bytes32 indexed challengeId);
    event DecryptionCancelled(bytes32 indexed requestId);

    constructor(address initialOwner, SignedAttestationVerifierV25 _verifier) Ownable(initialOwner) {
        verifier = _verifier;
    }

    function setBindingProfile(BindingProfile calldata p) external onlyOwner {
        require(p.profileId != bytes32(0), "BAD_PROFILE_ID");
        require(p.threshold > 0 && p.threshold <= p.committeeSize, "BAD_THRESHOLD");
        profiles[p.profileId] = p;
        emit BindingProfileSet(p.profileId, p.provider, p.networkName, p.threshold, p.timeoutSeconds, p.active);
    }

    function openRequest(bytes32 seedId, bytes32 profileId, bytes32 ciphertextHash, bytes32 manifestHash) external returns (bytes32 requestId) {
        BindingProfile memory p = profiles[profileId];
        require(p.active, "PROFILE_INACTIVE");
        requestId = keccak256(abi.encodePacked(block.chainid, seedId, profileId, msg.sender, ciphertextHash, manifestHash, block.timestamp));
        requests[requestId] = DecryptionRequest({
            requestId: requestId,
            seedId: seedId,
            profileId: profileId,
            requester: msg.sender,
            ciphertextHash: ciphertextHash,
            manifestHash: manifestHash,
            openedAt: uint64(block.timestamp),
            deadline: uint64(block.timestamp) + p.timeoutSeconds,
            status: RequestStatus.OPEN,
            completionHash: bytes32(0),
            plaintextHash: bytes32(0)
        });
        emit DecryptionRequested(requestId, seedId, profileId, msg.sender);
    }

    function completeRequest(
        bytes32 requestId,
        bytes32 plaintextHash,
        bytes32 completionHash,
        uint256 termId,
        uint256 deadline,
        bytes calldata signature
    ) external {
        DecryptionRequest storage r = requests[requestId];
        require(r.status == RequestStatus.OPEN, "NOT_OPEN");
        require(block.timestamp <= r.deadline, "TIMED_OUT");
        require(block.timestamp <= deadline, "ATTESTATION_EXPIRED");
        bytes32 digest = verifier.hashDecryptAttestation(requestId, r.seedId, plaintextHash, completionHash, termId, deadline);
        (address signer, bool trusted) = verifier.verify(digest, signature);
        require(signer != address(0) && trusted, "BAD_SIGNATURE");
        r.status = RequestStatus.FULFILLED;
        r.plaintextHash = plaintextHash;
        r.completionHash = completionHash;
        emit DecryptionCompleted(requestId, plaintextHash, completionHash);
    }

    function challengeRequest(bytes32 requestId, bytes32 challengeId) external onlyOwner {
        DecryptionRequest storage r = requests[requestId];
        require(r.status == RequestStatus.FULFILLED || r.status == RequestStatus.OPEN, "BAD_STATE");
        r.status = RequestStatus.CHALLENGED;
        emit DecryptionChallenged(requestId, challengeId);
    }

    function cancelRequest(bytes32 requestId) external onlyOwner {
        DecryptionRequest storage r = requests[requestId];
        require(r.status == RequestStatus.OPEN || r.status == RequestStatus.CHALLENGED, "BAD_STATE");
        r.status = RequestStatus.CANCELLED;
        emit DecryptionCancelled(requestId);
    }
}
