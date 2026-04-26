import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]


def _load(name: str):
    return json.loads((ROOT / name).read_text())


def test_decryption_attestation_example_roundtrip():
    schema = _load('schemas/v2.6/decryption-attestation.schema.json')
    validator = Draft202012Validator(schema)

    sample = {
        'schemaVersion': '2.6',
        'seedId': '0x' + '11' * 32,
        'requestId': '0x' + '22' * 32,
        'profileId': '0x' + '33' * 32,
        'ciphertextHash': '0x' + '44' * 32,
        'plaintextHash': '0x' + '55' * 32,
        'threshold': {'requiredShares': 2, 'collectedShares': 3},
        'signers': [{'nodeId': 'lit-node-1', 'signature': '0xabcdef1234567890'}],
        'completedAt': '2026-04-18T00:00:00Z',
    }

    errors = list(validator.iter_errors(sample))
    assert not errors
    encoded = json.dumps(sample, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded == sample


def test_threshold_binding_example_roundtrip():
    schema = _load('schemas/v2.6/threshold-binding-profile.schema.json')
    validator = Draft202012Validator(schema)

    sample = {
        'schemaVersion': '2.6',
        'profileId': '0x' + '66' * 32,
        'seedId': '0x' + '77' * 32,
        'network': 'ethereum-sepolia',
        'policy': {
            'requiredShares': 2,
            'totalShares': 4,
            'authorizedViewersRoot': '0x' + '88' * 32,
        },
        'createdAt': '2026-04-18T00:00:00Z',
    }

    errors = list(validator.iter_errors(sample))
    assert not errors
    encoded = json.dumps(sample, sort_keys=True)
    decoded = json.loads(encoded)
    assert decoded == sample
