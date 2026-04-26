import { expect } from "chai";
import hre from "hardhat";

describe("NovaSeedWorkflowAdapterV25 fail-closed routing", function () {
  it("only allows owner workflow actions and checks seed-state gate", async function () {
    const [owner, outsider] = await hre.ethers.getSigners();
    const registry = await hre.ethers.deployContract("MockRegistryViewV25");
    const jobs = await hre.ethers.deployContract("MockAGIJobManagerWorkflowV25");
    const mark = await hre.ethers.deployContract("MockMARKV25");
    const workflow = await hre.ethers.deployContract("NovaSeedWorkflowAdapterV25", [owner.address, await registry.getAddress(), await jobs.getAddress()]);

    const seedId = hre.ethers.id("seed/workflow");
    const assaySpecHash = hre.ethers.id("assay/spec");

    await expect(workflow.connect(outsider).setMARK(await mark.getAddress()))
      .to.be.revertedWithCustomError(workflow, "OwnableUnauthorizedAccount")
      .withArgs(outsider.address);
    await workflow.connect(owner).setMARK(await mark.getAddress());
    expect(await workflow.mark()).to.equal(await mark.getAddress());

    await registry.setState(seedId, 3);
    await expect(workflow.connect(owner).createAssay(seedId, assaySpecHash, 100n)).to.be.revertedWith("NOT_GREENLIT_OR_BLOOMING");

    await registry.setState(seedId, 4);
    await expect(workflow.connect(outsider).createAssay(seedId, assaySpecHash, 100n))
      .to.be.revertedWithCustomError(workflow, "OwnableUnauthorizedAccount")
      .withArgs(outsider.address);
    await workflow.connect(owner).createAssay(seedId, assaySpecHash, 100n);

    const created = await jobs.jobs(1n);
    expect(created.seedId).to.equal(seedId);
    expect(created.reward).to.equal(100n);

    await expect(workflow.connect(outsider).finalizeAssay(seedId, 1n))
      .to.be.revertedWithCustomError(workflow, "OwnableUnauthorizedAccount")
      .withArgs(outsider.address);
    await workflow.connect(owner).finalizeAssay(seedId, 1n);
    const finalized = await jobs.jobs(1n);
    expect(finalized.finalized).to.equal(true);
  });
});
