// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract FastUpgradeController {
    address public owner;
    address public implementation;

    constructor(address impl) { owner = msg.sender; implementation = impl; }

    function upgrade(address newImpl) external {
        require(msg.sender == owner, "owner only");
        implementation = newImpl;
    }
}
