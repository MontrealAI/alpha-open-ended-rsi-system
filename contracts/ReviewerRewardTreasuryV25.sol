// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract ReviewerRewardTreasuryV25 is Ownable {
    IERC20 public immutable rewardToken;
    mapping(address => uint256) public accrued;
    mapping(address => uint256) public claimed;
    mapping(address => uint256) public clawedBack;
    mapping(address => bool) public distributors;

    event DistributorSet(address indexed distributor, bool allowed);
    event RewardAccrued(address indexed reviewer, uint256 amount, bytes32 indexed ref);
    event RewardClaimed(address indexed reviewer, uint256 amount);
    event RewardClawedBack(address indexed reviewer, uint256 amount, bytes32 indexed reasonHash);

    modifier onlyDistributor() {
        require(distributors[msg.sender], "NOT_DISTRIBUTOR");
        _;
    }

    /// @notice Construct reviewer treasury with reward token.
    constructor(address initialOwner, IERC20 _rewardToken) Ownable(initialOwner) {
        rewardToken = _rewardToken;
    }

    /// @notice Allow or revoke a distributor that can accrue/slash rewards.
    function setDistributor(address distributor, bool allowed) external onlyOwner {
        distributors[distributor] = allowed;
        emit DistributorSet(distributor, allowed);
    }

    /// @notice Accrue reviewer stake rewards from governance-reviewed activity.
    function accrue(address reviewer, uint256 amount, bytes32 ref) external onlyDistributor {
        accrued[reviewer] += amount;
        emit RewardAccrued(reviewer, amount, ref);
    }

    /// @notice Claim accrued rewards into the caller wallet.
    function claim() external {
        uint256 amount = accrued[msg.sender];
        require(amount > 0, "NO_REWARD");
        accrued[msg.sender] = 0;
        claimed[msg.sender] += amount;
        require(rewardToken.transfer(msg.sender, amount), "TRANSFER_FAIL");
        emit RewardClaimed(msg.sender, amount);
    }

    /// @notice Apply deterministic clawback for disputes/slashing outcomes.
    function clawback(address reviewer, uint256 amount, bytes32 reasonHash) external onlyDistributor {
        require(accrued[reviewer] >= amount, "INSUFFICIENT_ACCRUED");
        accrued[reviewer] -= amount;
        clawedBack[reviewer] += amount;
        emit RewardClawedBack(reviewer, amount, reasonHash);
    }
}
