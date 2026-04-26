// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/IAGIJobManagerWorkflowV25.sol";

contract MockAGIJobManagerWorkflowV25 is IAGIJobManagerWorkflowV25 {
    struct Job {
        bytes32 seedId;
        bytes32 assaySpecHash;
        uint256 reward;
        bool finalized;
    }

    uint256 public nextJobId = 1;
    mapping(uint256 => Job) public jobs;

    function createAssayJob(bytes32 seedId, bytes32 assaySpecHash, uint256 reward) external returns (uint256 jobId) {
        jobId = nextJobId++;
        jobs[jobId] = Job(seedId, assaySpecHash, reward, false);
    }

    function requestCompletion(uint256, string calldata) external {}

    function validateJob(uint256) external {}

    function disapproveJob(uint256) external {}

    function finalizeJob(uint256 jobId) external {
        jobs[jobId].finalized = true;
    }
}
