// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./AlphaNovaSeedV25.sol";
import "./ThresholdNetworkAdapterV25.sol";
import "./ReviewerRewardTreasuryV25.sol";
import "./CouncilGovernanceV25.sol";
import "./ChallengePolicyModuleV25.sol";

contract NovaSeedRegistryV25 is Ownable {
    /// @notice Release string for operator-visible provenance checks.
    string public constant RELEASE_VERSION = "2.6.0-rc.1";
    /// @notice Hash that anchors the release metadata payload.
    bytes32 public constant RELEASE_METADATA_HASH = keccak256("alpha-nova-seeds:v2.6.0-rc.1");
    enum SeedState { NONE, DRAFT, SEALED, UNDER_REVIEW, GREENLIT, BLOOMING, SOVEREIGN, QUARANTINED, REJECTED, FAILED, FORKED, DEPRECATED }
    enum ReviewDecision { NONE, APPROVE, GREENLIGHT, REJECT, QUARANTINE, PROHIBIT }

    struct SeedRecord {
        bytes32 seedId;
        uint256 tokenId;
        bytes32 parentSeedId;
        SeedState state;
        bytes32 manifestHash;
        bytes32 ciphertextHash;
        bytes32 publicSummaryHash;
        bytes32 fusionPlanHash;
        bytes32 mutationMapHash;
        bytes32 evidenceHash;
        bytes32 authorizedViewersRoot;
        bytes32 envelopeKeyHash;
        bytes32 decryptionPolicyHash;
        string payloadURI;
        string publicSummaryURI;
        string fusionPlanURI;
        bytes32 sovereignPackageHash;
        string sovereignPackageURI;
        address sovereignContract;
        uint64 createdAt;
    }

    struct Review {
        address reviewer;
        uint64 termId;
        uint96 weight;
        ReviewDecision decision;
        bytes32 reasonHash;
        uint64 reviewedAt;
    }

    AlphaNovaSeedV25 public immutable seedNFT;
    ThresholdNetworkAdapterV25 public immutable thresholdAdapter;
    ReviewerRewardTreasuryV25 public immutable treasury;
    CouncilGovernanceV25 public immutable governance;
    ChallengePolicyModuleV25 public immutable challengePolicy;

    mapping(bytes32 => SeedRecord) public seeds;
    mapping(bytes32 => Review[]) public seedReviews;
    mapping(bytes32 => mapping(address => bool)) public hasReviewed;
    mapping(address => bool) public creators;

    event CreatorSet(address indexed creator, bool allowed);
    event SeedDrafted(bytes32 indexed seedId, uint256 indexed tokenId, bytes32 indexed parentSeedId);
    event SeedSealed(bytes32 indexed seedId);
    event ReviewOpened(bytes32 indexed seedId);
    event ReviewSubmitted(bytes32 indexed seedId, address indexed reviewer, uint96 weight, ReviewDecision decision);
    event SeedGreenlit(bytes32 indexed seedId);
    event SeedQuarantined(bytes32 indexed seedId);
    event SovereignRegistered(bytes32 indexed seedId, bytes32 sovereignPackageHash, address sovereignContract);

    modifier onlyCreator() {
        require(creators[msg.sender] || msg.sender == owner(), "NOT_CREATOR");
        _;
    }

    /// @notice Construct the registry with linked seed/proof/governance modules.
    constructor(
        address initialOwner,
        AlphaNovaSeedV25 _seedNFT,
        ThresholdNetworkAdapterV25 _thresholdAdapter,
        ReviewerRewardTreasuryV25 _treasury,
        CouncilGovernanceV25 _governance,
        ChallengePolicyModuleV25 _challengePolicy
    ) Ownable(initialOwner) {
        seedNFT = _seedNFT;
        thresholdAdapter = _thresholdAdapter;
        treasury = _treasury;
        governance = _governance;
        challengePolicy = _challengePolicy;
    }

    /// @notice Allow or revoke a seed creator account.
    function setCreator(address creator, bool allowed) external onlyOwner {
        creators[creator] = allowed;
        emit CreatorSet(creator, allowed);
    }

    /// @notice Create a new seed draft and mint its identity NFT.
    /// @dev Seed identity is immutable after creation except lifecycle state transitions.
    function draftSeed(
        bytes32 seedId,
        bytes32 parentSeedId,
        bytes32 manifestHash,
        bytes32 ciphertextHash,
        bytes32 publicSummaryHash,
        bytes32 fusionPlanHash,
        bytes32 mutationMapHash,
        bytes32 evidenceHash,
        bytes32 authorizedViewersRoot,
        bytes32 envelopeKeyHash,
        bytes32 decryptionPolicyHash,
        string calldata payloadURI,
        string calldata publicSummaryURI,
        string calldata fusionPlanURI,
        string calldata tokenURI
    ) external onlyCreator returns (uint256 tokenId) {
        require(seedId != bytes32(0), "BAD_SEED_ID");
        require(manifestHash != bytes32(0), "BAD_MANIFEST");
        require(ciphertextHash != bytes32(0), "BAD_CIPHERTEXT");
        require(seeds[seedId].seedId == bytes32(0), "SEED_EXISTS");

        uint256 reservedTokenId = seedNFT.nextTokenId();
        seeds[seedId] = SeedRecord({
            seedId: seedId,
            tokenId: reservedTokenId,
            parentSeedId: parentSeedId,
            state: SeedState.DRAFT,
            manifestHash: manifestHash,
            ciphertextHash: ciphertextHash,
            publicSummaryHash: publicSummaryHash,
            fusionPlanHash: fusionPlanHash,
            mutationMapHash: mutationMapHash,
            evidenceHash: evidenceHash,
            authorizedViewersRoot: authorizedViewersRoot,
            envelopeKeyHash: envelopeKeyHash,
            decryptionPolicyHash: decryptionPolicyHash,
            payloadURI: payloadURI,
            publicSummaryURI: publicSummaryURI,
            fusionPlanURI: fusionPlanURI,
            sovereignPackageHash: bytes32(0),
            sovereignPackageURI: "",
            sovereignContract: address(0),
            createdAt: uint64(block.timestamp)
        });
        tokenId = seedNFT.mint(msg.sender, tokenURI);
        require(tokenId == reservedTokenId, "TOKEN_ID_DRIFT");
        emit SeedDrafted(seedId, tokenId, parentSeedId);
    }

    /// @notice Move a seed from DRAFT to SEALED.
    function sealSeed(bytes32 seedId) external onlyCreator {
        SeedRecord storage s = seeds[seedId];
        require(s.state == SeedState.DRAFT, "BAD_STATE");
        s.state = SeedState.SEALED;
        emit SeedSealed(seedId);
    }

    /// @notice Open reviewer voting for a sealed seed.
    function openReview(bytes32 seedId) external onlyCreator {
        SeedRecord storage s = seeds[seedId];
        require(s.state == SeedState.SEALED, "BAD_STATE");
        s.state = SeedState.UNDER_REVIEW;
        emit ReviewOpened(seedId);
    }

    /// @notice Submit one governance-scoped review decision for a seed.
    function submitReview(bytes32 seedId, uint96 weight, ReviewDecision decision, bytes32 reasonHash) external {
        SeedRecord storage s = seeds[seedId];
        require(s.state == SeedState.UNDER_REVIEW, "NOT_UNDER_REVIEW");
        require(!hasReviewed[seedId][msg.sender], "ALREADY_REVIEWED");
        hasReviewed[seedId][msg.sender] = true;
        seedReviews[seedId].push(Review(msg.sender, governance.currentTermId(), weight, decision, reasonHash, uint64(block.timestamp)));
        treasury.accrue(msg.sender, 1 ether, keccak256(abi.encodePacked(seedId, msg.sender, uint8(decision))));
        emit ReviewSubmitted(seedId, msg.sender, weight, decision);
    }

    /// @notice Finalize a review round into GREENLIT, QUARANTINED, or REJECTED.
    function finalizeReview(bytes32 seedId) external onlyCreator {
        SeedRecord storage s = seeds[seedId];
        require(s.state == SeedState.UNDER_REVIEW, "BAD_STATE");
        Review[] memory rs = seedReviews[seedId];
        uint256 approveWeight = 0;
        uint256 greenWeight = 0;
        bool prohibit = false;
        bool quarantine = false;
        for (uint256 i = 0; i < rs.length; i++) {
            if (rs[i].decision == ReviewDecision.PROHIBIT) prohibit = true;
            if (rs[i].decision == ReviewDecision.QUARANTINE) quarantine = true;
            if (rs[i].decision == ReviewDecision.APPROVE) approveWeight += rs[i].weight;
            if (rs[i].decision == ReviewDecision.GREENLIGHT) greenWeight += rs[i].weight;
        }
        if (prohibit || quarantine) {
            s.state = SeedState.QUARANTINED;
            emit SeedQuarantined(seedId);
        } else if (approveWeight > 0 && greenWeight > 0) {
            s.state = SeedState.GREENLIT;
            emit SeedGreenlit(seedId);
        } else {
            s.state = SeedState.REJECTED;
        }
    }

    /// @notice Register the sovereign package emitted from a greenlit seed.
    function registerSovereign(bytes32 seedId, bytes32 sovereignPackageHash, string calldata sovereignPackageURI, address sovereignContract) external onlyCreator {
        SeedRecord storage s = seeds[seedId];
        require(s.state == SeedState.GREENLIT || s.state == SeedState.BLOOMING, "BAD_STATE");
        require(sovereignPackageHash != bytes32(0), "BAD_PACKAGE_HASH");
        require(sovereignContract != address(0), "BAD_SOVEREIGN");
        s.state = SeedState.SOVEREIGN;
        s.sovereignPackageHash = sovereignPackageHash;
        s.sovereignPackageURI = sovereignPackageURI;
        s.sovereignContract = sovereignContract;
        emit SovereignRegistered(seedId, sovereignPackageHash, sovereignContract);
    }

    /// @notice Return release metadata used by off-chain provenance checks.
    function releaseMetadata() external pure returns (string memory version, bytes32 metadataHash) {
        return (RELEASE_VERSION, RELEASE_METADATA_HASH);
    }
}
