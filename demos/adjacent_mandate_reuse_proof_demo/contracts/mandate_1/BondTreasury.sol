// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract BondTreasury {
    mapping(address => uint256) public bond;
    uint256 public lockedValidatorBonds;

    function postBond() external payable {
        bond[msg.sender] += msg.value;
        lockedValidatorBonds += msg.value;
    }

    function withdrawBond() external {
        uint256 amount = bond[msg.sender];
        require(amount > 0, "none");
        bond[msg.sender] = 0;
        payable(msg.sender).transfer(amount);
        // BUG: lockedValidatorBonds is never decremented
    }
}
