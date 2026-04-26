// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract ValidatorRefunds {
    mapping(address => uint256) public posted;
    uint256 public lockedReviewCollateral;

    function post() external payable {
        posted[msg.sender] += msg.value;
        lockedReviewCollateral += msg.value;
    }

    function refund() external {
        uint256 amount = posted[msg.sender];
        require(amount > 0, "none");
        posted[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
        // BUG: lockedReviewCollateral never decreases
    }
}
