// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../../NovaSeedRegistryV25.sol";
import "../../AlphaNovaSeedV25.sol";
import "../../SignedAttestationVerifierV25.sol";
import "../../ThresholdNetworkAdapterV25.sol";
import "../../ReviewerRewardTreasuryV25.sol";
import "../../CouncilGovernanceV25.sol";
import "../../ChallengePolicyModuleV25.sol";
import "../../mocks/MockERC20.sol";

contract RegistryAttacker {
    function setCreator(NovaSeedRegistryV25 registry, address creator, bool allowed) external {
        registry.setCreator(creator, allowed);
    }

    function draftSeed(NovaSeedRegistryV25 registry, bytes32 id, bytes32 h) external {
        registry.draftSeed(id, h, h, h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token");
    }

    function registerSovereign(NovaSeedRegistryV25 registry, bytes32 id, bytes32 h) external {
        registry.registerSovereign(id, h, "ipfs://package", address(this));
    }
}

contract EchidnaRegistryHarness {
    NovaSeedRegistryV25 internal registry;
    mapping(bytes32 => bool) internal drafted;
    bytes32 internal lastDraftedSeedId;
    RegistryAttacker internal attacker;

    constructor() {
        MockERC20 token = new MockERC20("R", "R", 1e24);
        AlphaNovaSeedV25 nft = new AlphaNovaSeedV25(address(this));
        SignedAttestationVerifierV25 verifier = new SignedAttestationVerifierV25(address(this));
        ThresholdNetworkAdapterV25 adapter = new ThresholdNetworkAdapterV25(address(this), verifier);
        ReviewerRewardTreasuryV25 treasury = new ReviewerRewardTreasuryV25(address(this), token);
        CouncilGovernanceV25 governance = new CouncilGovernanceV25(address(this));
        ChallengePolicyModuleV25 challenge = new ChallengePolicyModuleV25(address(this));
        registry = new NovaSeedRegistryV25(address(this), nft, adapter, treasury, governance, challenge);
        nft.setRegistry(address(registry));
        treasury.setDistributor(address(registry), true);
        registry.setCreator(address(this), true);
        attacker = new RegistryAttacker();
    }

    function draft(bytes32 seedId) external {
        bytes32 h = keccak256("h");
        if (!drafted[seedId]) {
            registry.draftSeed(seedId, h, h, h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token");
            drafted[seedId] = true;
            lastDraftedSeedId = seedId;
        }
    }

    function echidna_no_illegal_terminal_state_from_none() external returns (bool) {
        if (!drafted[lastDraftedSeedId]) return true;

        (bool ok,) = address(registry).call(
            abi.encodeWithSelector(
                registry.registerSovereign.selector,
                lastDraftedSeedId,
                keccak256("pkg"),
                "ipfs://package",
                address(this)
            )
        );

        return !ok;
    }

    function echidna_no_registry_mutation_without_authority() external returns (bool) {
        bytes32 h = keccak256("unauthorized");
        (bool creatorSet,) = address(attacker).call(abi.encodeWithSelector(attacker.setCreator.selector, registry, address(attacker), true));
        (bool draftedByUnauthorized,) = address(attacker).call(abi.encodeWithSelector(attacker.draftSeed.selector, registry, h, h));
        (bool registerUnauthorized,) = address(attacker).call(abi.encodeWithSelector(attacker.registerSovereign.selector, registry, h, h));
        return !creatorSet && !draftedByUnauthorized && !registerUnauthorized;
    }
}
