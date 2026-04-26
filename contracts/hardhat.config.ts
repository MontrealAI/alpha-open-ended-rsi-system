import "dotenv/config";
import { configVariable, defineConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-ethers";
import "@nomicfoundation/hardhat-ignition";
import "@nomicfoundation/hardhat-ignition-ethers";
import "@nomicfoundation/hardhat-verify";
import "@nomicfoundation/hardhat-toolbox-mocha-ethers";

const privateKey = process.env.DEPLOYER_PRIVATE_KEY?.startsWith("0x")
  ? process.env.DEPLOYER_PRIVATE_KEY
  : process.env.DEPLOYER_PRIVATE_KEY
    ? `0x${process.env.DEPLOYER_PRIVATE_KEY}`
    : undefined;

export default defineConfig({
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      viaIR: true,
      evmVersion: "cancun",
      metadata: {
        bytecodeHash: "ipfs"
      }
    }
  },
  paths: {
    sources: "./contracts-src",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  networks: {
    hardhat: {
      type: "edr-simulated",
      chainType: "l1",
      forking: (process.env.MAINNET_FORK_RPC_URL || process.env.MAINNET_RPC_URL)
        ? {
            url: process.env.MAINNET_FORK_RPC_URL || process.env.MAINNET_RPC_URL!
          }
        : undefined
    },
    localhost: {
      type: "http",
      url: "http://127.0.0.1:8545"
    },
    sepolia: {
      type: "http",
      chainType: "l1",
      url: configVariable("SEPOLIA_RPC_URL"),
      accounts: privateKey ? [privateKey] : []
    },
    mainnet: {
      type: "http",
      chainType: "l1",
      url: process.env.MAINNET_RPC_URL || process.env.MAINNET_RPC_URL_SECONDARY || configVariable("MAINNET_RPC_URL"),
      accounts: privateKey ? [privateKey] : []
    }
  },
  etherscan: {
    apiKey: process.env.ETHERSCAN_API_KEY || ""
  }
});
