// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../../CouncilGovernanceV25.sol";

contract EchidnaGovernanceHarness {
    CouncilGovernanceV25 internal gov;
    bytes32 internal lastChallengeId;
    uint32 internal lastSeatId;

    constructor() {
        gov = new CouncilGovernanceV25(address(this));
        gov.setElectionAdmin(address(this), true);
        gov.openTerm();
    }

    function assign(uint32 seatId, uint96 weight) external {
        uint32 bounded = (seatId % 16) + 1;
        uint32 beforeCount = gov.seatCount();
        gov.assignSeat(bounded, address(uint160(uint256(keccak256(abi.encodePacked(seatId, weight))))), weight, true);
        if (bounded == 0 || bounded > beforeCount) {
            lastSeatId = gov.seatCount();
        } else {
            lastSeatId = bounded;
        }
    }

    function openChallenge(bytes32 reason) external payable {
        if (lastSeatId == 0) return;
        (bool ok, bytes memory data) = address(gov).call{value: 1 wei}(abi.encodeWithSelector(gov.openSeatChallenge.selector, lastSeatId, reason));
        if (ok) {
            lastChallengeId = abi.decode(data, (bytes32));
        }
    }

    function echidna_seat_count_coherent() external view returns (bool) {
        for (uint32 i = 1; i <= gov.seatCount(); i++) {
            (address occupant,,) = gov.seats(i);
            if (occupant == address(0)) return false;
        }
        return true;
    }

    function echidna_unknown_challenge_cannot_resolve() external returns (bool) {
        (bool ok,) = address(gov).call(abi.encodeWithSelector(gov.resolveSeatChallenge.selector, keccak256("missing"), true));
        return !ok;
    }

    function echidna_upheld_challenge_deactivates_seat() external returns (bool) {
        if (lastChallengeId == bytes32(0)) return true;

        (,, , uint32 challengedSeatId, , , bool alreadyResolved, ) = gov.challenges(lastChallengeId);
        if (challengedSeatId == 0 || alreadyResolved) return true;

        (bool resolved,) = address(gov).call(abi.encodeWithSelector(gov.resolveSeatChallenge.selector, lastChallengeId, true));
        if (!resolved) return false;

        (,, bool active) = gov.seats(challengedSeatId);
        return !active;
    }

    receive() external payable {}
}
