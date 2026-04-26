# Public proof docket template

Use this folder as a starter shell for publishing proof evidence with each RC.

## Required files

- `manifest.json` — top-level docket manifest.
- `artifacts.json` — hashes, SBOM link, attestation metadata.
- `governance.json` — council/challenge evidence pointers.
- `threshold.json` — threshold binding + decryption attestation pointers.

## Usage

1. Copy template files.
2. Fill in release tag + hashes.
3. Link to workflow run IDs and signed attestations.
4. Publish alongside release notes.
