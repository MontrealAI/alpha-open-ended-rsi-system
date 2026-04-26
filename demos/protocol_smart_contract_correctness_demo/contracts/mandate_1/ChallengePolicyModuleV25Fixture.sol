// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ChallengePolicyModuleV25Fixture {
    mapping(address => uint256) public lockedReviewerBond;
    mapping(bytes32 => bool) public challengePassed;

    function lockBond() external payable {
        lockedReviewerBond[msg.sender] += msg.value;
    }

    function markChallengePassed(bytes32 challengeId) external {
        challengePassed[challengeId] = true;
    }

    // synthetic fixture: missing decrement causes accounting drift
    function refundBond(address payable reviewer, uint256 amount) external {
        (bool ok,) = reviewer.call{value: amount}("");
        require(ok, "refund failed");
    }

    // synthetic fixture: value release with weak validation semantics
    function settleChallengeReward(bytes32 challengeId, address payable reviewer, uint256 amount) external {
        require(challengePassed[challengeId], "challenge not passed");
        (bool ok,) = reviewer.call{value: amount}("");
        require(ok, "reward failed");
    }

    receive() external payable {}
}
