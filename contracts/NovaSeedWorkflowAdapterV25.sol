// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IAGIJobManagerWorkflowV25.sol";
import "./interfaces/INovaSeedRegistryV25View.sol";
import "./interfaces/INovaSeedMARKV25.sol";

contract NovaSeedWorkflowAdapterV25 is Ownable {
    INovaSeedRegistryV25View public immutable registry;
    IAGIJobManagerWorkflowV25 public immutable agiJobs;
    INovaSeedMARKV25 public mark;

    event AssayJobCreated(bytes32 indexed seedId, uint256 indexed jobId, bytes32 assaySpecHash, uint256 reward);
    event AssayFinalized(bytes32 indexed seedId, uint256 indexed jobId);

    constructor(address initialOwner, INovaSeedRegistryV25View _registry, IAGIJobManagerWorkflowV25 _agiJobs) Ownable(initialOwner) {
        registry = _registry;
        agiJobs = _agiJobs;
    }

    function setMARK(INovaSeedMARKV25 _mark) external onlyOwner {
        mark = _mark;
    }

    function createAssay(bytes32 seedId, bytes32 assaySpecHash, uint256 reward) external onlyOwner returns (uint256 jobId) {
        require(registry.seedState(seedId) == 4 || registry.seedState(seedId) == 5, "NOT_GREENLIT_OR_BLOOMING");
        jobId = agiJobs.createAssayJob(seedId, assaySpecHash, reward);
        emit AssayJobCreated(seedId, jobId, assaySpecHash, reward);
    }

    function finalizeAssay(bytes32 seedId, uint256 jobId) external onlyOwner {
        agiJobs.finalizeJob(jobId);
        emit AssayFinalized(seedId, jobId);
    }
}
