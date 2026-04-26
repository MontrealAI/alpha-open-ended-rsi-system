function main(): void {
  if (!process.env.MAINNET_FORK_RPC_URL && !process.env.MAINNET_RPC_URL) {
    throw new Error(
      "Fork rehearsal blocked: set MAINNET_FORK_RPC_URL (preferred) or MAINNET_RPC_URL before running test:fork."
    );
  }
  console.log("Fork RPC preflight check passed.");
}

main();
