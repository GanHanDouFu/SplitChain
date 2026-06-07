const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("SplitPayment", function () {
  let splitPayment;
  let owner, addr1, addr2, addr3;

  beforeEach(async function () {
    [owner, addr1, addr2, addr3] = await ethers.getSigners();
    const SplitPayment = await ethers.getContractFactory("SplitPayment");
    splitPayment = await SplitPayment.deploy();
  });

  it("Should create a split and execute correctly", async function () {
    const recipients = [addr1.address, addr2.address, addr3.address];
    const percentages = [30, 30, 40];
    const totalAmount = ethers.parseEther("1.0");

    // 创建分账
    await expect(
      splitPayment.createSplit(recipients, percentages, { value: totalAmount })
    ).to.emit(splitPayment, "SplitCreated");

    // 检查余额变化
    const bal1Before = await ethers.provider.getBalance(addr1.address);
    const bal2Before = await ethers.provider.getBalance(addr2.address);
    const bal3Before = await ethers.provider.getBalance(addr3.address);

    // 执行分账
    await expect(splitPayment.executeSplit(0)).to.emit(splitPayment, "SplitExecuted");

    const bal1After = await ethers.provider.getBalance(addr1.address);
    const bal2After = await ethers.provider.getBalance(addr2.address);
    const bal3After = await ethers.provider.getBalance(addr3.address);

    expect(bal1After - bal1Before).to.equal(ethers.parseEther("0.3"));
    expect(bal2After - bal2Before).to.equal(ethers.parseEther("0.3"));
    expect(bal3After - bal3Before).to.equal(ethers.parseEther("0.4"));
  });

  it("Should reject if percentages don't sum to 100", async function () {
    const recipients = [addr1.address, addr2.address];
    const percentages = [30, 30];

    await expect(
      splitPayment.createSplit(recipients, percentages, { value: ethers.parseEther("1.0") })
    ).to.be.revertedWith("Percentages must sum to 100");
  });

  it("Should reject double execution", async function () {
    const recipients = [addr1.address];
    const percentages = [100];

    await splitPayment.createSplit(recipients, percentages, { value: ethers.parseEther("1.0") });
    await splitPayment.executeSplit(0);

    await expect(splitPayment.executeSplit(0)).to.be.revertedWith("Already executed");
  });
});
