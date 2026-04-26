// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../../ReviewerRewardTreasuryV25.sol";
import "../../mocks/MockERC20.sol";

contract EchidnaTreasuryHarness {
    MockERC20 internal token;
    ReviewerRewardTreasuryV25 internal treasury;

    address internal constant REVIEWER = address(0x1234);
    uint256 internal reviewerAccruedTotal;
    uint256 internal reviewerSlashedTotal;
    uint256 internal selfAccruedTotal;
    uint256 internal totalClaimed;

    constructor() {
        token = new MockERC20("R", "R", 1e24);
        treasury = new ReviewerRewardTreasuryV25(address(this), token);
        treasury.setDistributor(address(this), true);
    }

    function accrue(uint128 amount) external {
        treasury.accrue(REVIEWER, amount, keccak256("accrue"));
        reviewerAccruedTotal += amount;
    }

    function slash(uint128 amount) external {
        uint256 bal = treasury.accrued(REVIEWER);
        if (bal == 0) return;
        uint256 bounded = amount % (bal + 1);
        if (bounded == 0) return;
        treasury.clawback(REVIEWER, bounded, keccak256("slash"));
        reviewerSlashedTotal += bounded;
    }

    function accrueSelf(uint128 amount) external {
        treasury.accrue(address(this), amount, keccak256("self-accrue"));
        selfAccruedTotal += amount;
    }

    function claimSelf() external {
        uint256 claimable = treasury.accrued(address(this));
        if (claimable == 0) return;
        token.transfer(address(treasury), claimable);
        treasury.claim();
        totalClaimed += claimable;
    }

    function echidna_clawback_not_exceeding_accrued() external view returns (bool) {
        uint256 accruedNow = treasury.accrued(REVIEWER);
        uint256 clawedNow = treasury.clawedBack(REVIEWER);
        return clawedNow == reviewerSlashedTotal && accruedNow + clawedNow == reviewerAccruedTotal;
    }

    function echidna_no_double_claim() external view returns (bool) {
        return treasury.claimed(address(this)) <= selfAccruedTotal && treasury.claimed(address(this)) == totalClaimed;
    }
}
