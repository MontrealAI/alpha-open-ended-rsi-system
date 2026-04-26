// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title Nova-Seed Registry read-only interface (v2.5)
/// @notice Read methods for retrieving identity and settlement-relevant seed state.
interface INovaSeedRegistryV25View {
    /// @notice Return state enum value for a seed.
    /// @param seedId Canonical seed identifier.
    function seedState(bytes32 seedId) external view returns (uint8);

    /// @notice Return NFT token identifier associated with a seed.
    /// @param seedId Canonical seed identifier.
    function seedTokenId(bytes32 seedId) external view returns (uint256);

    /// @notice Return parent seed identifier.
    /// @param seedId Canonical seed identifier.
    function parentSeed(bytes32 seedId) external view returns (bytes32);

    /// @notice Return sovereign package hash for a seed.
    /// @param seedId Canonical seed identifier.
    function sovereignPackageHash(bytes32 seedId) external view returns (bytes32);
}
