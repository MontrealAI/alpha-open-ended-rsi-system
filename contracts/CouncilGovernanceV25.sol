// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

contract CouncilGovernanceV25 is Ownable {
    struct Seat {
        address occupant;
        uint96 weight;
        bool active;
    }

    struct DelegationSnapshot {
        uint64 termId;
        address delegator;
        address delegatee;
        uint96 votingWeight;
    }

    struct Challenge {
        bytes32 challengeId;
        uint64 termId;
        address challenger;
        uint32 seatId;
        bytes32 reasonHash;
        uint256 bond;
        bool resolved;
        bool upheld;
    }

    uint64 public currentTermId;
    uint32 public seatCount;
    mapping(uint32 => Seat) public seats;
    mapping(uint64 => mapping(address => address)) public delegationOf; // delegator -> delegatee by term
    mapping(uint64 => DelegationSnapshot[]) internal _termSnapshots;
    mapping(bytes32 => Challenge) public challenges;
    mapping(address => bool) public electionAdmins;

    event TermOpened(uint64 indexed termId);
    event SeatAssigned(uint64 indexed termId, uint32 indexed seatId, address occupant, uint96 weight);
    event Delegated(uint64 indexed termId, address indexed delegator, address indexed delegatee, uint96 votingWeight);
    event ChallengeOpened(bytes32 indexed challengeId, uint64 indexed termId, uint32 indexed seatId, address challenger, bytes32 reasonHash, uint256 bond);
    event ChallengeResolved(bytes32 indexed challengeId, bool upheld);

    modifier onlyElectionAdmin() {
        require(electionAdmins[msg.sender] || msg.sender == owner(), "NOT_ELECTION_ADMIN");
        _;
    }

    /// @notice Construct governance with an initial owner/admin.
    constructor(address initialOwner) Ownable(initialOwner) {}

    /// @notice Allow or revoke election-admin authority.
    function setElectionAdmin(address admin, bool allowed) external onlyOwner {
        electionAdmins[admin] = allowed;
    }

    /// @notice Open the next governance term.
    function openTerm() external onlyElectionAdmin returns (uint64 termId) {
        termId = ++currentTermId;
        emit TermOpened(termId);
    }

    /// @notice Assign or reassign a seat for the current term.
    function assignSeat(uint32 seatId, address occupant, uint96 weight, bool active) external onlyElectionAdmin {
        if (seatId == 0 || seatId > seatCount) {
            seatCount += 1;
            seatId = seatCount;
        }
        seats[seatId] = Seat(occupant, weight, active);
        emit SeatAssigned(currentTermId, seatId, occupant, weight);
    }

    /// @notice Delegate voting weight for the current term.
    function delegate(address delegatee, uint96 votingWeight) external {
        delegationOf[currentTermId][msg.sender] = delegatee;
        _termSnapshots[currentTermId].push(DelegationSnapshot(currentTermId, msg.sender, delegatee, votingWeight));
        emit Delegated(currentTermId, msg.sender, delegatee, votingWeight);
    }

    /// @notice Read immutable delegation snapshots for a term.
    function delegationSnapshots(uint64 termId) external view returns (DelegationSnapshot[] memory) {
        return _termSnapshots[termId];
    }

    /// @notice Open a bonded challenge against a council seat.
    function openSeatChallenge(uint32 seatId, bytes32 reasonHash) external payable returns (bytes32 challengeId) {
        require(seats[seatId].occupant != address(0), "NO_SEAT");
        require(msg.value > 0, "BOND_REQUIRED");
        challengeId = keccak256(abi.encodePacked(block.chainid, currentTermId, seatId, msg.sender, reasonHash, block.timestamp));
        challenges[challengeId] = Challenge(challengeId, currentTermId, msg.sender, seatId, reasonHash, msg.value, false, false);
        emit ChallengeOpened(challengeId, currentTermId, seatId, msg.sender, reasonHash, msg.value);
    }

    /// @notice Resolve a seat challenge and route bond according to outcome.
    function resolveSeatChallenge(bytes32 challengeId, bool upheld) external onlyElectionAdmin {
        Challenge storage c = challenges[challengeId];
        require(c.challengeId != bytes32(0), "NO_CHALLENGE");
        require(!c.resolved, "ALREADY_RESOLVED");
        c.resolved = true;
        c.upheld = upheld;
        if (upheld) {
            seats[c.seatId].active = false;
            payable(c.challenger).transfer(c.bond);
        } else {
            payable(owner()).transfer(c.bond);
        }
        emit ChallengeResolved(challengeId, upheld);
    }
}
