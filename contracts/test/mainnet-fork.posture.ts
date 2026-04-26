import { expect } from "chai";
import hre from "hardhat";
import { deployComposite } from "../scripts/lib/contracts";

describe("Mainnet-fork fail-closed posture", function () {
  it("deploys on fork with restrictive defaults and expected wiring", async function () {
    const [owner, creator] = await hre.ethers.getSigners();
    const rewardToken = await hre.ethers.deployContract("MockERC20", ["AGI", "AGI", hre.ethers.parseEther("1000000")]);
    const agiJobs = await hre.ethers.deployContract("MockAGIJobManagerWorkflowV25", []);

    const deployed = await deployComposite({
      initialOwner: owner.address,
      rewardToken: await rewardToken.getAddress(),
      agiJobManager: await agiJobs.getAddress()
    });

    const registry = deployed.novaSeedRegistry as any;
    const treasury = deployed.reviewerRewardTreasury as any;
    const verifier = deployed.signedAttestationVerifier as any;

    expect(await registry.creators(creator.address)).to.equal(false);
    expect(await verifier.trustedSigners(creator.address)).to.equal(false);
    expect(await treasury.distributors(registry.target)).to.equal(true);

    await expect(
      registry.connect(creator).draftSeed(
        hre.ethers.id("seed"),
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        hre.ethers.ZeroHash,
        "payload://",
        "summary://",
        "fusion://",
        "token://"
      )
    ).to.be.revertedWith("NOT_CREATOR");
  });
});
