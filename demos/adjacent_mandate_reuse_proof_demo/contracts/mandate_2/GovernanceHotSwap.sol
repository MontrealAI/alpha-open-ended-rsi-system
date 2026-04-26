// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract GovernanceHotSwap {
    address public governor;
    address public moduleRouter;

    constructor(address initialRouter) {
        governor = msg.sender;
        moduleRouter = initialRouter;
    }

    function swapModule(address nextRouter) external {
        require(msg.sender == governor, "governor only");
        moduleRouter = nextRouter;
    }
}
