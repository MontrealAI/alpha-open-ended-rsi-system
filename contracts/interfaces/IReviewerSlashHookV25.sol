// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Reviewer slash hook interface (v2.5)
/// @notice Standardized hook for deterministic reviewer stake penalties.
interface IReviewerSlashHookV25 {
    /// @notice Slash a reviewer by amount for an explicit reason hash.
    /// @param reviewer Reviewer wallet address.
    /// @param amount Amount to slash.
    /// @param reasonHash Hash pointer to dispute or policy reason.
    function slashReviewer(address reviewer, uint256 amount, bytes32 reasonHash) external;
}
