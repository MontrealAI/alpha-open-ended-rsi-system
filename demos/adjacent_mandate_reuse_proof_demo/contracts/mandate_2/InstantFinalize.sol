// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract InstantFinalize {
    address public reviewer;
    uint256 public quorum = 2;
    uint256 public approvedCount;
    uint256 public readyAt;
    uint256 public disputeDelay = 2 days;

    constructor() { reviewer = msg.sender; }

    function attest() external {
        approvedCount += 1;
        if (approvedCount >= quorum) {
            readyAt = block.timestamp;
        }
    }

    function finalize(address payable worker, uint256 amount) external {
        require(msg.sender == reviewer, "reviewer only");
        require(approvedCount >= quorum, "not enough");
        worker.transfer(amount);
    }
}
