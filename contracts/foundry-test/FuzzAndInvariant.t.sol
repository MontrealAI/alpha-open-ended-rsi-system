// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../ReviewerRewardTreasuryV25.sol";
import "../ThresholdNetworkAdapterV25.sol";
import "../SignedAttestationVerifierV25.sol";
import "../CouncilGovernanceV25.sol";
import "../AlphaNovaSeedV25.sol";
import "../NovaSeedRegistryV25.sol";
import "../ChallengePolicyModuleV25.sol";
import "../mocks/MockERC20.sol";

contract FuzzAndInvariantTest {
    MockERC20 internal token;
    ReviewerRewardTreasuryV25 internal treasury;
    SignedAttestationVerifierV25 internal verifier;
    ThresholdNetworkAdapterV25 internal adapter;
    CouncilGovernanceV25 internal governance;
    AlphaNovaSeedV25 internal nft;
    NovaSeedRegistryV25 internal registry;
    ChallengePolicyModuleV25 internal challenge;

    uint256 internal totalAccrued;
    uint256 internal totalClaimed;
    uint256 internal totalClawed;
    bytes32 internal lastProfileId;
    uint256 internal draftNonce;

    constructor() {
        token = new MockERC20("Reward", "RWD", 1e27);
        treasury = new ReviewerRewardTreasuryV25(address(this), token);
        treasury.setDistributor(address(this), true);

        verifier = new SignedAttestationVerifierV25(address(this));
        adapter = new ThresholdNetworkAdapterV25(address(this), verifier);

        governance = new CouncilGovernanceV25(address(this));
        governance.setElectionAdmin(address(this), true);
        governance.openTerm();

        challenge = new ChallengePolicyModuleV25(address(this));
        nft = new AlphaNovaSeedV25(address(this));
        registry = new NovaSeedRegistryV25(address(this), nft, adapter, treasury, governance, challenge);
        nft.setRegistry(address(registry));
        registry.setCreator(address(this), true);
    }

    function testFuzz_threshold_boundaries(uint16 committeeSize, uint16 threshold, uint64 timeoutSeconds) external {
        if (committeeSize == 0) committeeSize = 1;
        ThresholdNetworkAdapterV25.BindingProfile memory p = ThresholdNetworkAdapterV25.BindingProfile({
            profileId: keccak256(abi.encodePacked(committeeSize, threshold, timeoutSeconds)),
            provider: "lit",
            networkName: "network",
            committeeRoot: bytes32(uint256(1)),
            relayerRoot: bytes32(uint256(2)),
            committeeSize: committeeSize,
            threshold: threshold,
            timeoutSeconds: timeoutSeconds,
            policyHash: bytes32(uint256(3)),
            active: true
        });

        bool shouldRevert = threshold == 0 || threshold > committeeSize;
        (bool ok,) = address(adapter).call(abi.encodeWithSelector(adapter.setBindingProfile.selector, p));
        if (ok) {
            lastProfileId = p.profileId;
        }
        require(ok != shouldRevert, "threshold-boundary mismatch");
    }

    function testFuzz_treasury_arithmetic(uint128 accrueAmount, uint128 slashAmount, bool claimNow) external {
        treasury.accrue(address(this), accrueAmount, keccak256("accrue"));
        totalAccrued += accrueAmount;

        uint256 boundedSlash = slashAmount;
        if (boundedSlash > treasury.accrued(address(this))) boundedSlash = treasury.accrued(address(this));

        if (boundedSlash > 0) {
            treasury.clawback(address(this), boundedSlash, keccak256("slash"));
            totalClawed += boundedSlash;
        }

        uint256 claimable = treasury.accrued(address(this));
        uint256 available = token.balanceOf(address(this));
        if (claimNow && claimable > 0 && claimable <= available) {
            token.transfer(address(treasury), claimable);
            treasury.claim();
            totalClaimed += claimable;
        }

        require(totalAccrued == totalClaimed + totalClawed + treasury.accrued(address(this)), "value drift");
    }

    function testFuzz_governance_seat_count_coherence(uint32 seatId, uint96 weight) external {
        uint32 requestedSeatId = uint32((seatId % 10) + 1);
        governance.assignSeat(requestedSeatId, address(uint160(requestedSeatId + 100)), weight, true);

        uint32 expectedAssignedSeatId = requestedSeatId;
        if (requestedSeatId == 0 || requestedSeatId > governance.seatCount()) {
            expectedAssignedSeatId = uint32(governance.seatCount());
        }

        (address occupant,,) = governance.seats(expectedAssignedSeatId);
        require(occupant != address(0), "seat assignment missing");
        require(governance.seatCount() >= expectedAssignedSeatId, "seat count incoherent");
    }

    function testFuzz_registry_invalid_identity_rejected(bytes32 seedId, bytes32 manifestHash, bytes32 ciphertextHash) external {
        bytes32 h = keccak256("h");
        bytes32 fuzzSeedId = keccak256(abi.encode(seedId, draftNonce++));
        if (fuzzSeedId == bytes32(0)) {
            fuzzSeedId = bytes32(uint256(1));
        }
        if (manifestHash != bytes32(0) && ciphertextHash != bytes32(0)) {
            manifestHash = bytes32(0);
        }
        (bool ok,) = address(registry).call(
            abi.encodeWithSelector(
                registry.draftSeed.selector, fuzzSeedId, h, manifestHash, ciphertextHash, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token"
            )
        );
        require(!ok, "registry accepted invalid identity");
    }

    function testFuzz_attestation_rejects_malformed_signature(bytes32 digest, bytes calldata signature) external view {
        if (signature.length == 65) return;
        (bool ok,) = address(verifier).staticcall(abi.encodeWithSelector(verifier.verify.selector, digest, signature));
        require(!ok, "malformed signature accepted");
    }

    function invariant_treasury_no_negative_accounting() external view {
        require(totalAccrued == totalClaimed + totalClawed + treasury.accrued(address(this)), "underflow accounting invariant");
        require(treasury.claimed(address(this)) == totalClaimed, "claim accounting mismatch");
    }

    function invariant_governance_seatcount_nonzero_for_assigned() external view {
        for (uint32 i = 1; i <= governance.seatCount(); i++) {
            (address occupant,,) = governance.seats(i);
            require(occupant != address(0), "seat gap");
        }
    }

    function invariant_threshold_profile_respects_quorum_math() external view {
        if (lastProfileId == bytes32(0)) return;
        (,,,,, uint16 committeeSize, uint16 threshold,,,) = adapter.profiles(lastProfileId);
        require(threshold > 0 && threshold <= committeeSize, "threshold invariant broken");
    }
}
