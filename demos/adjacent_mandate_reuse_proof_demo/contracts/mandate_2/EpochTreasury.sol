// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract EpochTreasury {
    mapping(address => uint256) public refundable;
    uint256 public reservedEscrow;

    function reserve() external payable {
        refundable[msg.sender] += msg.value;
        reservedEscrow += msg.value;
    }

    function claimRefund() external {
        uint256 amount = refundable[msg.sender];
        require(amount > 0, "none");
        refundable[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
        // BUG: reservedEscrow never decreases
    }
}
