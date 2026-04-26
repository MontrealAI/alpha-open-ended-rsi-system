// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../AlphaNovaSeedV25.sol";
import "../NovaSeedRegistryV25.sol";
import "../ChallengePolicyModuleV25.sol";
import "../CouncilGovernanceV25.sol";
import "../ReviewerRewardTreasuryV25.sol";
import "../SignedAttestationVerifierV25.sol";
import "../ThresholdNetworkAdapterV25.sol";
import "../NovaSeedWorkflowAdapterV25.sol";
import "../mocks/MockERC20.sol";
import "../mocks/MockAGIJobManagerWorkflowV25.sol";
import "../mocks/MockRegistryViewV25.sol";

contract ExternalCaller {
    function callSetRegistry(AlphaNovaSeedV25 seed, address registry) external {
        seed.setRegistry(registry);
    }

    function callMint(AlphaNovaSeedV25 seed, address to, string calldata uri) external {
        seed.mint(to, uri);
    }

    function callSetCreator(NovaSeedRegistryV25 registry, address creator, bool allowed) external {
        registry.setCreator(creator, allowed);
    }

    function callFinalize(NovaSeedRegistryV25 registry, bytes32 seedId) external {
        registry.finalizeReview(seedId);
    }

    function callSetPolicy(ChallengePolicyModuleV25 module, bytes32 id) external {
        module.setPolicy(id, 1, 1, 1, true);
    }

    function callResolve(CouncilGovernanceV25 gov, bytes32 challengeId) external {
        gov.resolveSeatChallenge(challengeId, false);
    }

    function callSetDistributor(ReviewerRewardTreasuryV25 t, address d, bool allowed) external {
        t.setDistributor(d, allowed);
    }

    function callAccrue(ReviewerRewardTreasuryV25 t, address reviewer, uint256 amount, bytes32 ref) external {
        t.accrue(reviewer, amount, ref);
    }

    function callSetTrustedSigner(SignedAttestationVerifierV25 v, address signer, bool trusted) external {
        v.setTrustedSigner(signer, trusted);
    }

    function callSetBinding(ThresholdNetworkAdapterV25 a, ThresholdNetworkAdapterV25.BindingProfile calldata p) external {
        a.setBindingProfile(p);
    }

    function callSetMark(NovaSeedWorkflowAdapterV25 workflow, INovaSeedMARKV25 mark) external {
        workflow.setMARK(mark);
    }

    function callCreateAssay(NovaSeedWorkflowAdapterV25 workflow, bytes32 seedId, bytes32 assaySpecHash, uint256 reward)
        external
    {
        workflow.createAssay(seedId, assaySpecHash, reward);
    }

    function callFinalizeAssay(NovaSeedWorkflowAdapterV25 workflow, bytes32 seedId, uint256 jobId) external {
        workflow.finalizeAssay(seedId, jobId);
    }
}


contract ReviewSubmitter {
    function submit(
        NovaSeedRegistryV25 registry,
        bytes32 seedId,
        uint96 weight,
        NovaSeedRegistryV25.ReviewDecision decision,
        bytes32 reasonHash
    ) external {
        registry.submitReview(seedId, weight, decision, reasonHash);
    }
}

contract ContractsSecurityTest {
    struct RegistryGraph {
        AlphaNovaSeedV25 nft;
        SignedAttestationVerifierV25 verifier;
        ThresholdNetworkAdapterV25 adapter;
        ReviewerRewardTreasuryV25 treasury;
        CouncilGovernanceV25 governance;
        ChallengePolicyModuleV25 challenge;
        NovaSeedRegistryV25 registry;
    }

    function _deployRegistryGraph() internal returns (RegistryGraph memory g) {
        MockERC20 token = new MockERC20("R", "R", 1e24);
        g.nft = new AlphaNovaSeedV25(address(this));
        g.verifier = new SignedAttestationVerifierV25(address(this));
        g.adapter = new ThresholdNetworkAdapterV25(address(this), g.verifier);
        g.treasury = new ReviewerRewardTreasuryV25(address(this), token);
        g.governance = new CouncilGovernanceV25(address(this));
        g.challenge = new ChallengePolicyModuleV25(address(this));
        g.registry = new NovaSeedRegistryV25(address(this), g.nft, g.adapter, g.treasury, g.governance, g.challenge);

        g.nft.setRegistry(address(g.registry));
        g.treasury.setDistributor(address(g.registry), true);
        g.registry.setCreator(address(this), true);
        g.governance.openTerm();
    }

    function _expectRevert(address target, bytes memory data) internal returns (bool) {
        (bool ok,) = target.call(data);
        return !ok;
    }

    function test_alpha_seed_registry_and_uri_guards() external {
        AlphaNovaSeedV25 seed = new AlphaNovaSeedV25(address(this));
        ExternalCaller outsider = new ExternalCaller();

        require(_expectRevert(address(seed), abi.encodeWithSelector(seed.setRegistry.selector, address(0))), "zero registry");
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetRegistry.selector, seed, address(outsider))), "owner gate");
        seed.setRegistry(address(this));

        uint256 tokenId = seed.mint(address(0xBEEF), "ipfs://seed");
        require(tokenId == 1, "mint id");
        require(keccak256(bytes(seed.tokenURI(tokenId))) == keccak256(bytes("ipfs://seed")), "uri");

        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetRegistry.selector, seed, address(0))), "set registry outsider");
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callMint.selector, seed, address(this), "x")), "mint outsider");
        require(_expectRevert(address(seed), abi.encodeWithSelector(seed.tokenURI.selector, 999)), "missing token");
    }

    function test_registry_lifecycle_happy_and_revert_paths() external {
        RegistryGraph memory g = _deployRegistryGraph();

        bytes32 seedId = keccak256("seed");
        bytes32 h = keccak256("h");
        require(
            _expectRevert(
                address(g.registry),
                abi.encodeWithSelector(g.registry.draftSeed.selector, bytes32(0), h, h, h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token")
            ),
            "zero seed id"
        );
        require(
            _expectRevert(
                address(g.registry),
                abi.encodeWithSelector(
                    g.registry.draftSeed.selector, keccak256("bad-manifest"), h, bytes32(0), h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token"
                )
            ),
            "manifest required"
        );
        g.registry.draftSeed(seedId, h, h, h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token");
        require(_expectRevert(address(g.registry), abi.encodeWithSelector(g.registry.openReview.selector, seedId)), "bad state");
        g.registry.sealSeed(seedId);
        g.registry.openReview(seedId);
        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callFinalize.selector, g.registry, seedId)), "finalize auth");
        ReviewSubmitter reviewerA = new ReviewSubmitter();
        ReviewSubmitter reviewerB = new ReviewSubmitter();
        reviewerA.submit(g.registry, seedId, 3, NovaSeedRegistryV25.ReviewDecision.GREENLIGHT, h);
        reviewerB.submit(g.registry, seedId, 2, NovaSeedRegistryV25.ReviewDecision.APPROVE, h);
        g.registry.finalizeReview(seedId);

        require(
            _expectRevert(
                address(g.registry), abi.encodeWithSelector(g.registry.registerSovereign.selector, seedId, bytes32(0), "ipfs://bad", address(this))
            ),
            "package hash required"
        );
        require(
            _expectRevert(
                address(g.registry), abi.encodeWithSelector(g.registry.registerSovereign.selector, seedId, h, "ipfs://bad", address(0))
            ),
            "sovereign contract required"
        );
        g.registry.registerSovereign(seedId, h, "ipfs://sovereign", address(this));
        require(_expectRevert(address(g.registry), abi.encodeWithSelector(g.registry.openReview.selector, seedId)), "terminal state");

        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetCreator.selector, g.registry, address(outsider), true)), "set creator auth");
        require(_expectRevert(address(g.registry), abi.encodeWithSelector(g.registry.draftSeed.selector, seedId, h, h, h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token")), "duplicate id");
    }

    function test_challenge_policy_math_and_finalization() external {
        ChallengePolicyModuleV25 module = new ChallengePolicyModuleV25(address(this));
        bytes32 policyId = keccak256("policy");
        bytes32 challengeId = keccak256("challenge");
        module.setPolicy(policyId, 2, 4, 2, true);
        module.setAdjudicator(address(this), true);

        module.recordVote(challengeId, policyId, true, 2, false);
        module.recordVote(challengeId, policyId, true, 2, false);
        ChallengePolicyModuleV25.Outcome outcome = module.finalize(challengeId);
        require(uint256(outcome) == uint256(ChallengePolicyModuleV25.Outcome.UPHELD), "upheld");

        bytes32 warningPolicyId = keccak256("warning-policy");
        bytes32 warningChallengeId = keccak256("warning-challenge");
        module.setPolicy(warningPolicyId, 5, 5, 1, true);
        module.recordVote(warningChallengeId, warningPolicyId, false, 0, true);
        ChallengePolicyModuleV25.Outcome warningOutcome = module.finalize(warningChallengeId);
        require(uint256(warningOutcome) == uint256(ChallengePolicyModuleV25.Outcome.WARNED), "warned");

        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetPolicy.selector, module, policyId)), "owner only");
        require(
            _expectRevert(address(module), abi.encodeWithSelector(module.recordVote.selector, challengeId, warningPolicyId, true, 1, false)),
            "policy mismatch"
        );
        require(
            _expectRevert(
                address(module),
                abi.encodeWithSelector(module.recordVote.selector, keccak256("inactive-challenge"), keccak256("inactive-policy"), true, 1, false)
            ),
            "inactive policy"
        );
        require(_expectRevert(address(module), abi.encodeWithSelector(module.finalize.selector, challengeId)), "double finalize");
    }

    function test_governance_seat_lifecycle_and_challenges() external {
        CouncilGovernanceV25 gov = new CouncilGovernanceV25(address(this));
        gov.setElectionAdmin(address(this), true);
        uint64 termId = gov.openTerm();
        require(termId == 1, "term");

        gov.assignSeat(0, address(0xAA), 4, true);
        gov.assignSeat(0, address(0xBB), 3, true);
        require(gov.seatCount() == 2, "seat count");

        gov.delegate(address(0xCC), 9);
        CouncilGovernanceV25.DelegationSnapshot[] memory snapshots = gov.delegationSnapshots(termId);
        require(snapshots.length == 1, "delegation snapshot");

        (bool opened, bytes memory data) = address(gov).call{value: 1 ether}(abi.encodeWithSelector(gov.openSeatChallenge.selector, 2, keccak256("r")));
        require(opened, "open challenge");
        bytes32 challengeId = abi.decode(data, (bytes32));
        gov.resolveSeatChallenge(challengeId, true);
        (,,bool active) = gov.seats(2);
        require(!active, "deactivate seat");
        require(_expectRevert(address(gov), abi.encodeWithSelector(gov.resolveSeatChallenge.selector, challengeId, true)), "double resolve");
        require(_expectRevert(address(gov), abi.encodeWithSelector(gov.resolveSeatChallenge.selector, keccak256("missing"), false)), "unknown challenge");
        require(_expectRevert(address(gov), abi.encodeWithSelector(gov.openSeatChallenge.selector, 2, keccak256("no-bond"))), "bond required");

        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callResolve.selector, gov, challengeId)), "resolve auth");
    }

    function test_treasury_access_and_accounting_paths() external {
        MockERC20 reward = new MockERC20("R", "R", 1e24);
        ReviewerRewardTreasuryV25 treasury = new ReviewerRewardTreasuryV25(address(this), reward);

        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetDistributor.selector, treasury, address(outsider), true)), "only owner");

        treasury.setDistributor(address(this), true);
        treasury.accrue(address(this), 100, keccak256("x"));
        treasury.clawback(address(this), 40, keccak256("slash"));
        require(treasury.accrued(address(this)) == 60, "accrued");
        require(_expectRevert(address(treasury), abi.encodeWithSelector(treasury.clawback.selector, address(this), 100, keccak256("over-slash"))), "slash bound");

        reward.transfer(address(treasury), 60);
        treasury.claim();
        require(treasury.accrued(address(this)) == 0, "post claim");
        require(treasury.claimed(address(this)) == 60, "claimed");
        require(_expectRevert(address(treasury), abi.encodeWithSelector(treasury.claim.selector)), "no double claim");
    }

    function test_attestation_verifier_signer_controls() external {
        SignedAttestationVerifierV25 verifier = new SignedAttestationVerifierV25(address(this));
        bytes32 seedId = keccak256("seed");
        bytes32 manifestHash = keccak256("manifest");
        bytes32 ciphertextHash = keccak256("cipher");
        bytes32 manifestDigest = verifier.hashManifestAttestation(seedId, manifestHash, ciphertextHash, 1, 1000);
        bytes32 challengeDigest = verifier.hashChallengeEvidence(keccak256("challenge"), seedId, keccak256("evidence"), 1, 1000);
        require(manifestDigest != challengeDigest, "domain separation");

        address signer = address(0xBEEF);
        verifier.setTrustedSigner(signer, true);
        require(verifier.trustedSigners(signer), "trusted signer");
        bytes memory malformedSig = hex"0102";
        require(_expectRevert(address(verifier), abi.encodeWithSelector(verifier.verify.selector, manifestDigest, malformedSig)), "malformed sig");

        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetTrustedSigner.selector, verifier, address(outsider), true)), "owner only");
    }

    function test_threshold_adapter_lifecycle_and_rejections() external {
        SignedAttestationVerifierV25 verifier = new SignedAttestationVerifierV25(address(this));
        ThresholdNetworkAdapterV25 adapter = new ThresholdNetworkAdapterV25(address(this), verifier);

        ThresholdNetworkAdapterV25.BindingProfile memory p = ThresholdNetworkAdapterV25.BindingProfile({
            profileId: keccak256("p"),
            provider: "lit",
            networkName: "datil",
            committeeRoot: keccak256("c"),
            relayerRoot: keccak256("r"),
            committeeSize: 3,
            threshold: 2,
            timeoutSeconds: 100,
            policyHash: keccak256("pol"),
            active: true
        });

        adapter.setBindingProfile(p);
        bytes32 requestId = adapter.openRequest(keccak256("seed"), p.profileId, keccak256("cipher"), keccak256("manifest"));
        adapter.challengeRequest(requestId, keccak256("challenge"));
        adapter.cancelRequest(requestId);
        require(
            _expectRevert(
                address(adapter),
                abi.encodeWithSelector(adapter.completeRequest.selector, requestId, keccak256("p"), keccak256("c"), 1, block.timestamp + 1, hex"0102")
            ),
            "cannot finalize cancelled"
        );
        require(_expectRevert(address(adapter), abi.encodeWithSelector(adapter.openRequest.selector, keccak256("seed2"), keccak256("missing"), keccak256("cipher2"), keccak256("manifest2"))), "inactive profile");

        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetBinding.selector, adapter, p)), "set profile auth");
        require(_expectRevert(address(adapter), abi.encodeWithSelector(adapter.cancelRequest.selector, requestId)), "cancel twice");
    }

    function test_workflow_adapter_integration_paths() external {
        MockRegistryViewV25 registryView = new MockRegistryViewV25();
        MockAGIJobManagerWorkflowV25 workflowEngine = new MockAGIJobManagerWorkflowV25();
        NovaSeedWorkflowAdapterV25 adapter = new NovaSeedWorkflowAdapterV25(address(this), registryView, workflowEngine);

        bytes32 seedId = keccak256("seed");
        registryView.setState(seedId, 4);
        uint256 jobId = adapter.createAssay(seedId, keccak256("assay"), 10);
        adapter.finalizeAssay(seedId, jobId);
        (, , , bool finalized) = workflowEngine.jobs(jobId);
        require(finalized, "job finalized");

        ExternalCaller outsider = new ExternalCaller();
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callSetMark.selector, adapter, INovaSeedMARKV25(address(0xABCD)))), "set mark auth");
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callCreateAssay.selector, adapter, seedId, keccak256("assay3"), 1)), "workflow owner create");
        require(_expectRevert(address(outsider), abi.encodeWithSelector(outsider.callFinalizeAssay.selector, adapter, seedId, jobId)), "workflow owner finalize");

        registryView.setState(seedId, 2);
        require(_expectRevert(address(adapter), abi.encodeWithSelector(adapter.createAssay.selector, seedId, keccak256("assay2"), 1)), "state restricted");
    }

    function test_integration_seed_review_and_governance_challenge_path() external {
        RegistryGraph memory g = _deployRegistryGraph();

        bytes32 seedId = keccak256("seed-integration");
        bytes32 h = keccak256("integration-hash");
        g.registry.draftSeed(seedId, h, h, h, h, h, h, h, h, h, h, "payload", "summary", "fusion", "token");
        g.registry.sealSeed(seedId);
        g.registry.openReview(seedId);
        ReviewSubmitter reviewerA = new ReviewSubmitter();
        ReviewSubmitter reviewerB = new ReviewSubmitter();
        reviewerA.submit(g.registry, seedId, 5, NovaSeedRegistryV25.ReviewDecision.GREENLIGHT, h);
        reviewerB.submit(g.registry, seedId, 3, NovaSeedRegistryV25.ReviewDecision.APPROVE, h);
        g.registry.finalizeReview(seedId);
        g.registry.registerSovereign(seedId, h, "ipfs://seed-integration", address(this));
        require(_expectRevert(address(g.registry), abi.encodeWithSelector(g.registry.registerSovereign.selector, seedId, h, "ipfs://double", address(this))), "terminal sovereign");

        g.governance.assignSeat(1, address(0x1111), 4, true);
        (bool opened, bytes memory data) =
            address(g.governance).call{value: 1 ether}(abi.encodeWithSelector(g.governance.openSeatChallenge.selector, 1, h));
        require(opened, "challenge open");
        bytes32 challengeId = abi.decode(data, (bytes32));
        g.governance.resolveSeatChallenge(challengeId, true);
        (,,bool active) = g.governance.seats(1);
        require(!active, "seat disabled after upheld challenge");
    }

    receive() external payable {}

    function onERC721Received(address, address, uint256, bytes calldata) external pure returns (bytes4) {
        return this.onERC721Received.selector;
    }
}
