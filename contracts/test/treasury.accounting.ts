import { expect } from "chai";
import hre from "hardhat";

describe("ReviewerRewardTreasuryV25 accounting", function () {
  it("enforces distributor access and blocks double-claim", async function () {
    const [owner, distributor, reviewer] = await hre.ethers.getSigners();
    const rewardToken = await hre.ethers.deployContract("MockERC20", ["AGI", "AGI", hre.ethers.parseEther("1000000")]);
    const treasury = await hre.ethers.deployContract("ReviewerRewardTreasuryV25", [owner.address, await rewardToken.getAddress()]);

    await expect(treasury.connect(distributor).accrue(reviewer.address, 10n, hre.ethers.id("x"))).to.be.revertedWith("NOT_DISTRIBUTOR");
    await treasury.connect(owner).setDistributor(distributor.address, true);
    await treasury.connect(distributor).accrue(reviewer.address, 100n, hre.ethers.id("x"));
    await treasury.connect(distributor).clawback(reviewer.address, 40n, hre.ethers.id("slash"));
    expect(await treasury.accrued(reviewer.address)).to.equal(60n);

    await rewardToken.connect(owner).transfer(await treasury.getAddress(), 60n);
    await treasury.connect(reviewer).claim();
    expect(await treasury.accrued(reviewer.address)).to.equal(0n);
    expect(await treasury.claimed(reviewer.address)).to.equal(60n);
    await expect(treasury.connect(reviewer).claim()).to.be.revertedWith("NO_REWARD");
  });

  it("fails closed when treasury is underfunded", async function () {
    const [owner, distributor, reviewer] = await hre.ethers.getSigners();
    const rewardToken = await hre.ethers.deployContract("MockERC20", ["AGI", "AGI", hre.ethers.parseEther("1000000")]);
    const treasury = await hre.ethers.deployContract("ReviewerRewardTreasuryV25", [owner.address, await rewardToken.getAddress()]);

    await treasury.connect(owner).setDistributor(distributor.address, true);
    await treasury.connect(distributor).accrue(reviewer.address, 100n, hre.ethers.id("insufficient-liquidity"));
    await expect(treasury.connect(reviewer).claim())
      .to.be.revertedWithCustomError(rewardToken, "ERC20InsufficientBalance")
      .withArgs(await treasury.getAddress(), 0n, 100n);
  });
});
