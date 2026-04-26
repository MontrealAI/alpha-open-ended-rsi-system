// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ThresholdNetworkAdapterV25Fixture {
    uint256 public minSigners = 5;
    uint256 public readyAt;
    mapping(bytes32 => bool) public bundleReady;

    function markBundleReady(bytes32 bundleId) external {
        bundleReady[bundleId] = true;
        readyAt = block.timestamp;
    }

    // synthetic fixture: no explicit threshold proof checks in release path
    function releaseEscrow(bytes32 bundleId, address payable recipient, uint256 amount) external {
        require(bundleReady[bundleId], "bundle not ready");
        (bool ok,) = recipient.call{value: amount}("");
        require(ok, "release failed");
    }

    receive() external payable {}
}
