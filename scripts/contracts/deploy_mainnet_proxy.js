#!/usr/bin/env node

const { spawnSync } = require("node:child_process");

const hasBroadcast = process.argv.slice(2).includes("--broadcast");
if (!hasBroadcast) {
  console.error("Mainnet deployment is fail-closed. Run: npm run deploy:mainnet -- --broadcast");
  process.exit(1);
}

const result = spawnSync("npm", ["--prefix", "contracts", "run", "deploy:mainnet"], {
  stdio: "inherit",
  env: {
    ...process.env,
    CONFIRM_MAINNET_BROADCAST: "true"
  }
});

process.exit(result.status ?? 1);
