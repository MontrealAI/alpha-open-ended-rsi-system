// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Nova-Seed MARK callback interface (v2.5)
/// @notice Callback hooks invoked when seed lifecycle transitions occur.
interface INovaSeedMARKV25 {
    /// @notice Called when a seed is sealed.
    /// @param seedId Canonical seed identifier.
    function onSeedSealed(bytes32 seedId) external;

    /// @notice Called when a seed is greenlit.
    /// @param seedId Canonical seed identifier.
    function onSeedGreenlit(bytes32 seedId) external;

    /// @notice Called when a seed is quarantined.
    /// @param seedId Canonical seed identifier.
    function onSeedQuarantined(bytes32 seedId) external;

    /// @notice Called when a sovereign package is registered.
    /// @param seedId Canonical seed identifier.
    /// @param sovereignPackageHash Hash of sovereign package payload.
    function onSovereignRegistered(bytes32 seedId, bytes32 sovereignPackageHash) external;
}
