// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ProoflessEscrow {
    address public owner;
    bool public completed;
    mapping(address => uint256) public balances;

    constructor() { owner = msg.sender; balances[address(this)] = 10 ether; }

    function finalize(address payable agent, uint256 amount) external {
        require(msg.sender == owner, "owner only");
        require(balances[address(this)] >= amount, "insufficient");
        agent.transfer(amount);
        completed = true;
    }
}
