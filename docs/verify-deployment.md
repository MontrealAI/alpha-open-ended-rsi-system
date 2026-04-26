# Verify deployment artifacts and contract publication

## 1) Validate manifest structure

Inspect `contracts/deployments/<network>/<timestamp>/manifest.json` for:

- `chainId`
- `commitSha`
- `contracts[]` names and addresses
- `constructorArgs`
- `deployedBytecodeHash`
- artifact/build-info hints
- verification status entries

## 2) Validate checksums

```bash
cd contracts/deployments/<network>/<timestamp>
sha256sum -c checksums.txt
```

## 3) Verify on Etherscan

From repository root:

```bash
npm run deploy:verify
```

Or pass an explicit deployment directory:

```bash
npm --prefix contracts run deploy:verify -- -- deployments/mainnet/<timestamp>
```

Verification script behavior:

- re-computes deployed runtime bytecode hash for each contract
- fails closed if runtime hash differs from manifest
- attempts verification with manifest constructor arguments
- writes updated verification status back to `manifest.json`
- uses deployment-config role/dependency expectations for postcheck parity

## 4) Cross-check runtime wiring

Review `postcheck-report.md` to confirm:

- release metadata endpoint is coherent
- registry ↔ NFT and registry ↔ treasury wiring are correct
- ownership targets match operator intent
- fail-closed defaults remain closed

## 5) Record provenance

Archive together:

- deployment packet files
- `git rev-parse HEAD` output
- contract build-info references
- release provenance manifest from `scripts/release/generate_provenance_manifest.py`
