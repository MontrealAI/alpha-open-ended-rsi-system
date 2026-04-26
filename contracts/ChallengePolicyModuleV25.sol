// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";

contract ChallengePolicyModuleV25 is Ownable {
    enum Outcome { UNSET, UPHELD, REJECTED, WARNED }

    struct Policy {
        bytes32 policyId;
        uint8 requiredApprovals;
        uint8 requiredWeight;
        uint8 maxWarnings;
        bool active;
    }

    struct Adjudication {
        bytes32 challengeId;
        bytes32 policyId;
        uint8 approvals;
        uint16 approvalWeight;
        uint8 warnings;
        Outcome outcome;
        bool finalized;
    }

    mapping(bytes32 => Policy) public policies;
    mapping(bytes32 => Adjudication) public adjudications;
    mapping(address => bool) public adjudicators;

    event PolicySet(bytes32 indexed policyId, uint8 approvals, uint8 weight, uint8 warnings, bool active);
    event AdjudicatorSet(address indexed adjudicator, bool allowed);
    event VoteRecorded(bytes32 indexed challengeId, address indexed adjudicator, bool approve, uint8 weight, bool warningOnly);
    event ChallengeAdjudicated(bytes32 indexed challengeId, Outcome outcome);

    modifier onlyAdjudicator() {
        require(adjudicators[msg.sender] || msg.sender == owner(), "NOT_ADJUDICATOR");
        _;
    }

    constructor(address initialOwner) Ownable(initialOwner) {}

    function setAdjudicator(address adjudicator, bool allowed) external onlyOwner {
        adjudicators[adjudicator] = allowed;
        emit AdjudicatorSet(adjudicator, allowed);
    }

    function setPolicy(bytes32 policyId, uint8 approvals, uint8 weight, uint8 warnings, bool active) external onlyOwner {
        policies[policyId] = Policy(policyId, approvals, weight, warnings, active);
        emit PolicySet(policyId, approvals, weight, warnings, active);
    }

    function recordVote(bytes32 challengeId, bytes32 policyId, bool approve, uint8 weight, bool warningOnly) external onlyAdjudicator {
        Policy memory p = policies[policyId];
        require(p.active, "POLICY_INACTIVE");
        Adjudication storage a = adjudications[challengeId];
        if (a.challengeId == bytes32(0)) {
            a.challengeId = challengeId;
            a.policyId = policyId;
        }
        require(a.policyId == policyId, "POLICY_MISMATCH");
        require(!a.finalized, "FINALIZED");
        if (warningOnly) {
            a.warnings += 1;
        } else if (approve) {
            a.approvals += 1;
            a.approvalWeight += weight;
        }
        emit VoteRecorded(challengeId, msg.sender, approve, weight, warningOnly);
    }

    function finalize(bytes32 challengeId) external onlyAdjudicator returns (Outcome outcome) {
        Adjudication storage a = adjudications[challengeId];
        Policy memory p = policies[a.policyId];
        require(!a.finalized, "FINALIZED");
        a.finalized = true;
        if (a.approvals >= p.requiredApprovals && a.approvalWeight >= p.requiredWeight) {
            a.outcome = Outcome.UPHELD;
        } else if (a.warnings >= p.maxWarnings && p.maxWarnings > 0) {
            a.outcome = Outcome.WARNED;
        } else {
            a.outcome = Outcome.REJECTED;
        }
        outcome = a.outcome;
        emit ChallengeAdjudicated(challengeId, outcome);
    }
}
