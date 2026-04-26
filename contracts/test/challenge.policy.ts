import { expect } from "chai";
import hre from "hardhat";

describe("ChallengePolicyModuleV25 adjudication guards", function () {
  it("enforces policy activation, policy matching, and one-way finalization", async function () {
    const [owner, adjudicator, outsider] = await hre.ethers.getSigners();
    const challenge = await hre.ethers.deployContract("ChallengePolicyModuleV25", [owner.address]);

    const policyId = hre.ethers.id("policy/main");
    const challengeId = hre.ethers.id("challenge/1");
    const otherPolicyId = hre.ethers.id("policy/other");

    await expect(challenge.connect(outsider).recordVote(challengeId, policyId, true, 1, false)).to.be.revertedWith("NOT_ADJUDICATOR");

    await challenge.connect(owner).setAdjudicator(adjudicator.address, true);
    await challenge.connect(owner).setPolicy(policyId, 2, 5, 2, true);

    await challenge.connect(adjudicator).recordVote(challengeId, policyId, true, 3, false);
    await expect(challenge.connect(adjudicator).recordVote(challengeId, otherPolicyId, true, 3, false)).to.be.revertedWith("POLICY_INACTIVE");

    await challenge.connect(owner).setPolicy(otherPolicyId, 1, 1, 1, true);
    await expect(challenge.connect(adjudicator).recordVote(challengeId, otherPolicyId, true, 1, false)).to.be.revertedWith("POLICY_MISMATCH");

    await challenge.connect(adjudicator).recordVote(challengeId, policyId, true, 2, false);
    await challenge.connect(adjudicator).finalize(challengeId);

    const adjudication = await challenge.adjudications(challengeId);
    expect(adjudication.finalized).to.equal(true);
    expect(adjudication.outcome).to.equal(1n);

    await expect(challenge.connect(adjudicator).recordVote(challengeId, policyId, true, 1, false)).to.be.revertedWith("FINALIZED");
    await expect(challenge.connect(adjudicator).finalize(challengeId)).to.be.revertedWith("FINALIZED");
  });

  it("supports warning-only policy outcome without approvals", async function () {
    const [owner, adjudicator] = await hre.ethers.getSigners();
    const challenge = await hre.ethers.deployContract("ChallengePolicyModuleV25", [owner.address]);

    const policyId = hre.ethers.id("warning-policy");
    const challengeId = hre.ethers.id("challenge/warning");

    await challenge.connect(owner).setAdjudicator(adjudicator.address, true);
    await challenge.connect(owner).setPolicy(policyId, 3, 9, 1, true);
    await challenge.connect(adjudicator).recordVote(challengeId, policyId, false, 0, true);

    const outcomeTx = await challenge.connect(adjudicator).finalize(challengeId);
    await outcomeTx.wait();
    const adjudication = await challenge.adjudications(challengeId);
    expect(adjudication.outcome).to.equal(3n);
  });
});
