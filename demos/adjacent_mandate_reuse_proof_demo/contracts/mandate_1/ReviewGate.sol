// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ReviewGate {
    address public owner;
    uint256 public approvals;
    uint256 public required = 3;
    uint256 public approvedAt;
    uint256 public challengePeriod = 1 days;

    constructor() { owner = msg.sender; }

    function approve() external {
        approvals += 1;
        if (approvals >= required) {
            approvedAt = block.timestamp;
        }
    }

    function settle(address payable agent, uint256 amount) external {
        require(msg.sender == owner, "owner only");
        require(approvals >= required, "need approvals");
        agent.transfer(amount);
    }
}
