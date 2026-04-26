import { expect } from "chai";
import hre from "hardhat";

describe("AlphaNovaSeedV25 identity controls", function () {
  it("enforces owner/registry authorization and token URI lifecycle", async function () {
    const [owner, registry, outsider, receiver] = await hre.ethers.getSigners();
    const nft = await hre.ethers.deployContract("AlphaNovaSeedV25", [owner.address]);

    await expect(nft.connect(outsider).setRegistry(registry.address)).to.be.revertedWithCustomError(nft, "OwnableUnauthorizedAccount").withArgs(outsider.address);
    await expect(nft.connect(owner).setRegistry(hre.ethers.ZeroAddress)).to.be.revertedWith("BAD_REGISTRY");

    await nft.connect(owner).setRegistry(registry.address);
    await expect(nft.connect(outsider).mint(receiver.address, "ipfs://seed/1")).to.be.revertedWith("NOT_REGISTRY");

    await nft.connect(registry).mint(receiver.address, "ipfs://seed/1");
    expect(await nft.ownerOf(1n)).to.equal(receiver.address);
    expect(await nft.tokenURI(1n)).to.equal("ipfs://seed/1");

    await expect(nft.connect(outsider).setTokenURI(1n, "ipfs://seed/other")).to.be.revertedWith("NOT_REGISTRY");
    await nft.connect(registry).setTokenURI(1n, "ipfs://seed/updated");
    expect(await nft.tokenURI(1n)).to.equal("ipfs://seed/updated");

    await expect(nft.connect(registry).setTokenURI(9999n, "missing")).to.be.revertedWith("NO_TOKEN");
    await expect(nft.tokenURI(9999n)).to.be.revertedWith("NO_TOKEN");
  });
});
