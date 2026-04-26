// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SignedAttestationVerifierV25Fixture {
    mapping(bytes32 => bool) public attested;
    uint256 public lockedAttestorBond;

    function registerAttestation(bytes32 digest) external {
        attested[digest] = true;
    }

    // synthetic fixture: value-moving path without verifier-level challenge delay
    function finalizeAttestation(bytes32 digest, address payable recipient, uint256 amount) external {
        require(attested[digest], "not attested");
        (bool ok,) = recipient.call{value: amount}("");
        require(ok, "finalize failed");
    }

    // synthetic fixture: bond accounting drift due to missing decrement
    function withdrawBond(address payable attestor, uint256 amount) external {
        (bool ok,) = attestor.call{value: amount}("");
        require(ok, "withdraw failed");
    }

    receive() external payable {}
}
