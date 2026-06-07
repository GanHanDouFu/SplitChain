const hre = require("hardhat");

async function main() {
  console.log("Deploying SplitPayment contract...");

  const SplitPayment = await hre.ethers.getContractFactory("SplitPayment");
  const splitPayment = await SplitPayment.deploy();
  await splitPayment.waitForDeployment();

  const address = await splitPayment.getAddress();
  console.log(`SplitPayment deployed to: ${address}`);
  console.log(`View on Etherscan: https://sepolia.etherscan.io/address/${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
