from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_migration_uses_postgres_compatible_view_statements():
    sql = (ROOT / 'backend/migrations/002_v26_hardening.sql').read_text()
    assert 'CREATE VIEW IF NOT EXISTS' not in sql
    assert 'DROP VIEW IF EXISTS reviewer_stake_balances;' in sql
    assert 'DROP VIEW IF EXISTS council_active_seat_count;' in sql
    assert "WHERE latest.event_type IN ('assigned', 'reassigned', 'challenged');" in sql


def test_indexer_reorg_rewind_deletes_derived_rows():
    source = (ROOT / 'backend/app/indexer.py').read_text()
    assert 'DELETE FROM chain_events WHERE block_number >= :start_block' in source
    assert 'DELETE FROM reviewer_stake_ledger WHERE block_number >= :start_block' in source
    assert 'DELETE FROM council_seat_lifecycle WHERE block_number >= :start_block' in source
    assert 'DELETE FROM seat_challenges WHERE block_number >= :start_block' in source
    assert "SET resolved = true, upheld = :upheld, resolved_block_number = :resolved_block_number, updated_at = now()" in source
    assert "WHERE resolved_block_number >= :start_block" in source


def test_indexer_uses_causal_order_and_bounded_occupant_lookups():
    source = (ROOT / 'backend/app/indexer.py').read_text()
    assert "ordered_logs.sort(key=lambda x: (x[0], x[1]))" in source
    assert "block_number < :block_number" in source
    assert "(block_number = :block_number AND log_index <= :log_index)" in source
    assert "_seat_occupant_at_or_before(conn, seat_id, payload['block_number'], payload['log_index'])" in source


def test_fastapi_main_imports_list_typing():
    source = (ROOT / 'backend/app/main.py').read_text()
    assert 'from typing import List' in source
    assert 'response_model=List[ReviewerStakeRow]' in source
    assert 'response_model=List[CouncilSeatRow]' in source


def test_event_abis_include_governance_and_review_events():
    registry_abi = (ROOT / 'backend/app/abi/NovaSeedRegistryV25.events.json').read_text()
    governance_abi = (ROOT / 'backend/app/abi/CouncilGovernanceV25.events.json').read_text()
    assert 'ReviewSubmitted' in registry_abi
    assert 'SeedQuarantined' in registry_abi
    assert 'SeatAssigned' in governance_abi
    assert 'ChallengeOpened' in governance_abi
    assert 'ChallengeResolved' in governance_abi


def test_release_workflow_archives_requested_tag_not_head():
    workflow = (ROOT / '.github/workflows/release-provenance.yml').read_text()
    assert 'refs/tags/${{ inputs.release_tag }}' in workflow
    assert 'ref: refs/tags/${{ inputs.release_tag }}' in workflow
    assert 'git archive --format=tar.gz' in workflow
    assert 'HEAD > dist/alpha-nova-seeds-${{ inputs.release_tag }}.tar.gz' not in workflow


def test_release_workflow_exports_openapi_surface():
    workflow = (ROOT / '.github/workflows/release-provenance.yml').read_text()
    assert 'python backend/scripts/export_openapi.py' in workflow
    assert 'dist/openapi-v2.6.0-rc.1.json' in workflow


def test_sdk_version_tracks_v26_rc_but_eip712_domain_matches_verifier_surface():
    package = (ROOT / 'sdk/package.json').read_text()
    eip712 = (ROOT / 'sdk/shared/eip712.ts').read_text()
    verifier = (ROOT / 'contracts/SignedAttestationVerifierV25.sol').read_text()

    assert '"name": "alpha-nova-seeds-v26-sdk"' in package
    assert '"version": "2.6.0-rc.1"' in package
    assert 'version: "2.5"' in eip712
    assert 'EIP712("NovaSeedAttestations", "2.5")' in verifier
