// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/INovaSeedRegistryV25View.sol";

contract MockRegistryViewV25 is INovaSeedRegistryV25View {
    mapping(bytes32 => uint8) public states;
    mapping(bytes32 => uint256) public tokenIds;
    mapping(bytes32 => bytes32) public parents;
    mapping(bytes32 => bytes32) public sovereignHashes;

    function setState(bytes32 seedId, uint8 value) external {
        states[seedId] = value;
    }

    function setTokenId(bytes32 seedId, uint256 tokenId) external {
        tokenIds[seedId] = tokenId;
    }

    function setParent(bytes32 seedId, bytes32 parentSeedId) external {
        parents[seedId] = parentSeedId;
    }

    function setSovereignHash(bytes32 seedId, bytes32 packageHash) external {
        sovereignHashes[seedId] = packageHash;
    }

    function seedState(bytes32 seedId) external view returns (uint8) {
        return states[seedId];
    }

    function seedTokenId(bytes32 seedId) external view returns (uint256) {
        return tokenIds[seedId];
    }

    function parentSeed(bytes32 seedId) external view returns (bytes32) {
        return parents[seedId];
    }

    function sovereignPackageHash(bytes32 seedId) external view returns (bytes32) {
        return sovereignHashes[seedId];
    }
}
