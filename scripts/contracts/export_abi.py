#!/usr/bin/env python3
"""Export ABI snapshots from checked-in JSON files.

This repository does not bundle a Solidity compiler toolchain by default.
For v2.6 RC provenance we export canonical ABI/event JSON snapshots from tracked files.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABI_DIR = ROOT / 'contracts' / 'abi'
ABI_DIR.mkdir(parents=True, exist_ok=True)

source = ROOT / 'backend' / 'app' / 'abi' / 'NovaSeedRegistryV25.events.json'
target = ABI_DIR / 'NovaSeedRegistryV25.events.abi.json'

data = json.loads(source.read_text())
target.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

metadata_abi = [
    {
        'inputs': [],
        'name': 'releaseMetadata',
        'outputs': [
            {'internalType': 'string', 'name': 'version', 'type': 'string'},
            {'internalType': 'bytes32', 'name': 'metadataHash', 'type': 'bytes32'},
        ],
        'stateMutability': 'pure',
        'type': 'function',
    },
    {
        'inputs': [],
        'name': 'RELEASE_VERSION',
        'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}],
        'stateMutability': 'view',
        'type': 'function',
    },
]

(ROOT / 'contracts' / 'abi' / 'NovaSeedRegistryV25.release-metadata.abi.json').write_text(
    json.dumps(metadata_abi, indent=2) + '\n',
    encoding='utf-8',
)

print(f'Wrote {target.relative_to(ROOT)} and release metadata ABI snapshot')
