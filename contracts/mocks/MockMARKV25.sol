// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../interfaces/INovaSeedMARKV25.sol";

contract MockMARKV25 is INovaSeedMARKV25 {
    bytes32 public lastSeed;
    bytes32 public lastPackage;

    function onSeedSealed(bytes32 seedId) external {
        lastSeed = seedId;
    }

    function onSeedGreenlit(bytes32 seedId) external {
        lastSeed = seedId;
    }

    function onSeedQuarantined(bytes32 seedId) external {
        lastSeed = seedId;
    }

    function onSovereignRegistered(bytes32 seedId, bytes32 sovereignPackageHash) external {
        lastSeed = seedId;
        lastPackage = sovereignPackageHash;
    }
}
