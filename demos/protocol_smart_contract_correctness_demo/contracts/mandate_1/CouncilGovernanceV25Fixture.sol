// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CouncilGovernanceV25Fixture {
    address public implementation;
    uint256 public approvedAt;
    uint256 public challengePeriod = 1 days;
    mapping(bytes32 => bool) public approved;

    function approveProposal(bytes32 proposalId) external {
        approved[proposalId] = true;
        approvedAt = block.timestamp;
    }

    // synthetic fixture: missing challenge window on settlement
    function finalizePayout(bytes32 proposalId, address payable recipient, uint256 amount) external {
        require(approved[proposalId], "not approved");
        (bool ok,) = recipient.call{value: amount}("");
        require(ok, "transfer failed");
    }

    // synthetic fixture: instant governance upgrade with no timelock
    function swapImplementation(address newImpl) external {
        implementation = newImpl;
    }

    receive() external payable {}
}
