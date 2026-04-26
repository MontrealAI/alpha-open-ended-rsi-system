// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "../../NovaSeedWorkflowAdapterV25.sol";
import "../../mocks/MockRegistryViewV25.sol";
import "../../mocks/MockAGIJobManagerWorkflowV25.sol";

contract WorkflowAttacker {
    function setMark(NovaSeedWorkflowAdapterV25 workflow, INovaSeedMARKV25 mark) external {
        workflow.setMARK(mark);
    }

    function createAssay(NovaSeedWorkflowAdapterV25 workflow, bytes32 seedId, bytes32 assaySpecHash, uint256 reward)
        external
        returns (uint256)
    {
        return workflow.createAssay(seedId, assaySpecHash, reward);
    }

    function finalizeAssay(NovaSeedWorkflowAdapterV25 workflow, bytes32 seedId, uint256 jobId) external {
        workflow.finalizeAssay(seedId, jobId);
    }
}

contract EchidnaWorkflowHarness {
    MockRegistryViewV25 internal registry;
    MockAGIJobManagerWorkflowV25 internal jobs;
    NovaSeedWorkflowAdapterV25 internal workflow;
    WorkflowAttacker internal attacker;

    bytes32 internal lastSeedId;
    uint256 internal lastJobId;

    constructor() {
        registry = new MockRegistryViewV25();
        jobs = new MockAGIJobManagerWorkflowV25();
        workflow = new NovaSeedWorkflowAdapterV25(address(this), registry, jobs);
        attacker = new WorkflowAttacker();
    }

    function setSeedState(bytes32 seedId, uint8 state) external {
        lastSeedId = seedId;
        registry.setState(seedId, state);
    }

    function ownerCreate(bytes32 seedId, bytes32 assaySpecHash, uint256 reward) external {
        lastSeedId = seedId;
        uint8 state = registry.states(seedId);
        if (state != 4 && state != 5) {
            return;
        }

        lastJobId = workflow.createAssay(seedId, assaySpecHash, reward);
    }

    function ownerFinalizeLast() external {
        if (lastJobId == 0) return;
        workflow.finalizeAssay(lastSeedId, lastJobId);
    }

    function echidna_unauthorized_workflow_mutations_blocked() external returns (bool) {
        bytes32 seedId = keccak256("attacker-seed");
        registry.setState(seedId, 4);

        (bool setMarkOk,) =
            address(attacker).call(abi.encodeWithSelector(attacker.setMark.selector, workflow, INovaSeedMARKV25(address(0xBEEF))));
        (bool createOk,) =
            address(attacker).call(abi.encodeWithSelector(attacker.createAssay.selector, workflow, seedId, keccak256("assay"), 1));

        uint256 jobId = jobs.nextJobId();
        if (jobId == 0) {
            jobId = 1;
        }
        (bool finalizeOk,) =
            address(attacker).call(abi.encodeWithSelector(attacker.finalizeAssay.selector, workflow, seedId, jobId));

        return !setMarkOk && !createOk && !finalizeOk;
    }

    function echidna_create_assay_requires_greenlit_or_blooming() external returns (bool) {
        if (lastSeedId == bytes32(0)) return true;

        uint8 state = registry.states(lastSeedId);
        if (state == 4 || state == 5) return true;

        (bool ok,) =
            address(workflow).call(abi.encodeWithSelector(workflow.createAssay.selector, lastSeedId, keccak256("bad-assay"), 1));
        return !ok;
    }

    function echidna_unauthorized_finalize_cannot_flip_job() external returns (bool) {
        if (lastJobId == 0) return true;
        (,,, bool beforeFinalized) = jobs.jobs(lastJobId);
        (bool ok,) =
            address(attacker).call(abi.encodeWithSelector(attacker.finalizeAssay.selector, workflow, lastSeedId, lastJobId));
        (,,, bool afterFinalized) = jobs.jobs(lastJobId);
        return !ok && beforeFinalized == afterFinalized;
    }
}
