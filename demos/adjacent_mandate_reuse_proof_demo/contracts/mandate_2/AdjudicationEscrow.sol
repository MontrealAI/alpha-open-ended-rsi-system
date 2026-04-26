// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract AdjudicationEscrow {
    address public admin;
    bytes32 public completionHash;
    bool public readyForPayout;
    mapping(address => uint256) public escrowed;

    constructor() {
        admin = msg.sender;
        escrowed[address(this)] = 20 ether;
    }

    function markReady(bytes32 h) external {
        require(msg.sender == admin, "admin only");
        completionHash = h;
        readyForPayout = true;
    }

    function release(address payable recipient, uint256 amount) external {
        require(msg.sender == admin, "admin only");
        require(readyForPayout, "not ready");
        recipient.transfer(amount);
    }
}
