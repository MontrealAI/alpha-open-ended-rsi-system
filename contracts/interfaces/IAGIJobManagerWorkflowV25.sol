// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title AGI Job Manager Workflow Interface (v2.5)
/// @notice Defines lifecycle hooks used by Nova-Seeds when orchestrating assay jobs.
interface IAGIJobManagerWorkflowV25 {
    /// @notice Create a new assay job for a seed.
    /// @param seedId Canonical seed identifier.
    /// @param assaySpecHash Hash of assay specification payload.
    /// @param reward Requested reward amount.
    /// @return jobId New job identifier.
    function createAssayJob(bytes32 seedId, bytes32 assaySpecHash, uint256 reward) external returns (uint256 jobId);

    /// @notice Request completion for an existing job.
    /// @param jobId Job identifier.
    /// @param uri URI containing completion evidence.
    function requestCompletion(uint256 jobId, string calldata uri) external;

    /// @notice Mark a job as validated.
    /// @param jobId Job identifier.
    function validateJob(uint256 jobId) external;

    /// @notice Mark a job as disapproved.
    /// @param jobId Job identifier.
    function disapproveJob(uint256 jobId) external;

    /// @notice Finalize a job after validation/disapproval lifecycle.
    /// @param jobId Job identifier.
    function finalizeJob(uint256 jobId) external;
}
