from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text()


def test_seed_identity_and_release_metadata_surface_present():
    content = _read('contracts/NovaSeedRegistryV25.sol')
    assert 'function draftSeed(' in content
    assert 'function releaseMetadata()' in content
    assert 'RELEASE_VERSION' in content


def test_governance_and_challenge_lifecycle_surface_present():
    content = _read('contracts/CouncilGovernanceV25.sol')
    assert 'function openTerm()' in content
    assert 'function openSeatChallenge(' in content
    assert 'function resolveSeatChallenge(' in content


def test_reviewer_stake_and_threshold_attestation_surface_present():
    treasury = _read('contracts/ReviewerRewardTreasuryV25.sol')
    verifier = _read('contracts/SignedAttestationVerifierV25.sol')
    assert 'function accrue(' in treasury
    assert 'function clawback(' in treasury
    assert 'function verify(' in verifier


def test_natspec_present_on_external_and_public_proof_interfaces():
    registry = _read('contracts/NovaSeedRegistryV25.sol')
    governance = _read('contracts/CouncilGovernanceV25.sol')
    treasury = _read('contracts/ReviewerRewardTreasuryV25.sol')
    verifier = _read('contracts/SignedAttestationVerifierV25.sol')

    assert '/// @notice Create a new seed draft and mint its identity NFT.' in registry
    assert '/// @notice Open a bonded challenge against a council seat.' in governance
    assert '/// @notice Apply deterministic clawback for disputes/slashing outcomes.' in treasury
    assert '/// @notice Recover signer and return trust status for a digest/signature pair.' in verifier
