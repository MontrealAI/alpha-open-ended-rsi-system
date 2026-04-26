import { expect } from "chai";
import hre from "hardhat";
import { deployComposite } from "../scripts/lib/contracts";

describe("Composite deployment smoke", function () {
  it("deploys and wires core registry graph", async function () {
    const [owner] = await hre.ethers.getSigners();

    const rewardToken = await hre.ethers.deployContract("MockERC20", ["AGI", "AGI", hre.ethers.parseEther("1000000")]);
    const agiJobs = await hre.ethers.deployContract("MockAGIJobManagerWorkflowV25", []);

    const deployed = await deployComposite({
      initialOwner: owner.address,
      rewardToken: await rewardToken.getAddress(),
      agiJobManager: await agiJobs.getAddress()
    });

    expect(await (deployed.alphaNovaSeed as any).registry()).to.equal((deployed.novaSeedRegistry as any).target);
    expect(await (deployed.reviewerRewardTreasury as any).distributors((deployed.novaSeedRegistry as any).target)).to.equal(true);
    expect(await (deployed.novaSeedRegistry as any).owner()).to.equal(owner.address);
    expect(await (deployed.signedAttestationVerifier as any).trustedSigners(owner.address)).to.equal(false);
  });
});
