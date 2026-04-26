import json
from pathlib import Path
from web3 import Web3
from sqlalchemy import text
from .config import (
    RPC_URL,
    REGISTRY_ADDRESS,
    GOVERNANCE_ADDRESS,
    START_BLOCK,
    REORG_WINDOW,
    CONFIRMATIONS,
)
from .db import engine

ABI_DIR = Path(__file__).with_name('abi')

EVENT_SOURCES = [
    {
        'address': REGISTRY_ADDRESS,
        'abi': json.loads((ABI_DIR / 'NovaSeedRegistryV25.events.json').read_text()),
    },
    {
        'address': GOVERNANCE_ADDRESS,
        'abi': json.loads((ABI_DIR / 'CouncilGovernanceV25.events.json').read_text()),
    },
]


def _to_text(value):
    if hasattr(value, 'hex'):
        return value.hex()
    return str(value)


def upsert_chain_event(conn, payload: dict):
    conn.execute(text("""
        INSERT INTO chain_events (block_number, tx_hash, log_index, contract_address, event_name, payload)
        VALUES (:block_number, :tx_hash, :log_index, :contract_address, :event_name, CAST(:payload AS JSONB))
        ON CONFLICT (tx_hash, log_index) DO NOTHING
    """), payload)


def _insert_reviewer_accrual(conn, payload: dict, args: dict):
    conn.execute(text("""
        INSERT INTO reviewer_stake_ledger (reviewer, delta, kind, reason_hash, tx_hash, log_index, block_number)
        VALUES (:reviewer, :delta, :kind, :reason_hash, :tx_hash, :log_index, :block_number)
        ON CONFLICT (tx_hash, log_index) DO NOTHING
    """), {
        'reviewer': _to_text(args.get('reviewer', '')).lower(),
        'delta': 1,
        'kind': 'accrual',
        'reason_hash': _to_text(args.get('reasonHash', '')),
        'tx_hash': payload['tx_hash'],
        'log_index': payload['log_index'],
        'block_number': payload['block_number'],
    })


def _insert_council_lifecycle(conn, payload: dict, term_id, seat_id, occupant, event_type: str):
    conn.execute(text("""
        INSERT INTO council_seat_lifecycle (term_id, seat_id, occupant, event_type, tx_hash, log_index, block_number)
        VALUES (:term_id, :seat_id, :occupant, :event_type, :tx_hash, :log_index, :block_number)
        ON CONFLICT (tx_hash, log_index) DO NOTHING
    """), {
        'term_id': term_id,
        'seat_id': seat_id,
        'occupant': occupant,
        'event_type': event_type,
        'tx_hash': payload['tx_hash'],
        'log_index': payload['log_index'],
        'block_number': payload['block_number'],
    })


def _seat_occupant_at_or_before(conn, seat_id: int, block_number: int, log_index: int):
    return conn.execute(
        text('''
            SELECT occupant
            FROM council_seat_lifecycle
            WHERE seat_id = :seat_id
              AND (
                block_number < :block_number
                OR (block_number = :block_number AND log_index <= :log_index)
              )
            ORDER BY block_number DESC, log_index DESC
            LIMIT 1
        '''),
        {'seat_id': seat_id, 'block_number': block_number, 'log_index': log_index},
    ).scalar_one_or_none()


def _handle_seat_assigned(conn, payload: dict, args: dict):
    seat_id = int(args.get('seatId'))
    term_id = int(args.get('termId'))
    occupant = _to_text(args.get('occupant', '')).lower()

    prior = conn.execute(
        text('SELECT 1 FROM council_seat_lifecycle WHERE seat_id = :seat_id LIMIT 1'),
        {'seat_id': seat_id},
    ).scalar_one_or_none()

    event_type = 'reassigned' if prior else 'assigned'
    _insert_council_lifecycle(conn, payload, term_id, seat_id, occupant, event_type)


def _handle_challenge_opened(conn, payload: dict, args: dict):
    challenge_id = _to_text(args.get('challengeId'))
    term_id = int(args.get('termId'))
    seat_id = int(args.get('seatId'))
    challenger = _to_text(args.get('challenger', '')).lower()
    reason_hash = _to_text(args.get('reasonHash', ''))
    bond = int(args.get('bond', 0))

    conn.execute(text("""
        INSERT INTO seat_challenges (challenge_id, term_id, seat_id, challenger, reason_hash, bond, resolved, upheld, block_number, resolved_block_number, updated_at)
        VALUES (
          decode(replace(:challenge_id, '0x', ''), 'hex'),
          :term_id,
          :seat_id,
          :challenger,
          decode(replace(NULLIF(:reason_hash, ''), '0x', ''), 'hex'),
          :bond,
          false,
          NULL,
          :block_number,
          NULL,
          now()
        )
        ON CONFLICT (challenge_id) DO NOTHING
    """), {
        'challenge_id': challenge_id,
        'term_id': term_id,
        'seat_id': seat_id,
        'challenger': challenger,
        'reason_hash': reason_hash,
        'bond': bond,
        'block_number': payload['block_number'],
    })

    occupant = _seat_occupant_at_or_before(conn, seat_id, payload['block_number'], payload['log_index'])

    _insert_council_lifecycle(conn, payload, term_id, seat_id, occupant, 'challenged')


def _handle_challenge_resolved(conn, payload: dict, args: dict):
    challenge_id = _to_text(args.get('challengeId'))
    upheld = bool(args.get('upheld'))

    conn.execute(text("""
        UPDATE seat_challenges
        SET resolved = true, upheld = :upheld, resolved_block_number = :resolved_block_number, updated_at = now()
        WHERE challenge_id = decode(replace(:challenge_id, '0x', ''), 'hex')
    """), {'upheld': upheld, 'challenge_id': challenge_id, 'resolved_block_number': payload['block_number']})

    if upheld:
        row = conn.execute(text('''
            SELECT term_id, seat_id
            FROM seat_challenges
            WHERE challenge_id = decode(replace(:challenge_id, '0x', ''), 'hex')
            LIMIT 1
        '''), {'challenge_id': challenge_id}).mappings().first()
        if row:
            seat_id = int(row['seat_id']) if row['seat_id'] is not None else None
            occupant = (
                _seat_occupant_at_or_before(conn, seat_id, payload['block_number'], payload['log_index'])
                if seat_id is not None
                else None
            )
            _insert_council_lifecycle(
                conn,
                payload,
                int(row['term_id']) if row['term_id'] is not None else None,
                seat_id,
                occupant,
                'deactivated',
            )


def upsert_governance_views(conn, payload: dict):
    event_name = payload['event_name']
    args = payload['args']

    if event_name == 'ReviewSubmitted':
        _insert_reviewer_accrual(conn, payload, args)
    elif event_name == 'SeatAssigned':
        _handle_seat_assigned(conn, payload, args)
    elif event_name == 'ChallengeOpened':
        _handle_challenge_opened(conn, payload, args)
    elif event_name == 'ChallengeResolved':
        _handle_challenge_resolved(conn, payload, args)


def _load_cursor(conn) -> int:
    return conn.execute(text('SELECT last_safe_block FROM indexer_state WHERE id = 1')).scalar_one_or_none() or 0


def _save_cursor(conn, block_number: int):
    conn.execute(text('''
        INSERT INTO indexer_state (id, last_safe_block, updated_at)
        VALUES (1, :block_number, now())
        ON CONFLICT (id) DO UPDATE SET last_safe_block = EXCLUDED.last_safe_block, updated_at = now()
    '''), {'block_number': block_number})


def run_once(start_override: int | None = None, end_override: int | None = None):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    latest = w3.eth.block_number
    safe_tip = max(0, latest - CONFIRMATIONS)

    with engine.begin() as conn:
        cursor = _load_cursor(conn)
        start_block = max(START_BLOCK, cursor - REORG_WINDOW)
        if start_override is not None:
            start_block = start_override

        end_block = safe_tip if end_override is None else min(end_override, safe_tip)

        if end_block < start_block:
            return {'indexed_to': cursor, 'safe_tip': safe_tip, 'events': 0}

        # Reorg-safe delete for mutable tail
        conn.execute(text('DELETE FROM chain_events WHERE block_number >= :start_block'), {'start_block': start_block})
        conn.execute(text('DELETE FROM reviewer_stake_ledger WHERE block_number >= :start_block'), {'start_block': start_block})
        conn.execute(text('DELETE FROM council_seat_lifecycle WHERE block_number >= :start_block'), {'start_block': start_block})
        conn.execute(text('DELETE FROM seat_challenges WHERE block_number >= :start_block'), {'start_block': start_block})
        conn.execute(text('''
            UPDATE seat_challenges
            SET resolved = false, upheld = NULL, resolved_block_number = NULL, updated_at = now()
            WHERE resolved_block_number >= :start_block
        '''), {'start_block': start_block})

        events = 0
        for source in EVENT_SOURCES:
            address = source['address']
            if address.lower() == '0x0000000000000000000000000000000000000000':
                continue

            contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=source['abi'])
            ordered_logs = []
            for event_abi in source['abi']:
                event = contract.events[event_abi['name']]
                logs = event.get_logs(fromBlock=start_block, toBlock=end_block)
                for log in logs:
                    ordered_logs.append((log['blockNumber'], log['logIndex'], event_abi['name'], log))
            ordered_logs.sort(key=lambda x: (x[0], x[1]))

            for _, _, event_name, log in ordered_logs:
                args = dict(log['args'])
                payload = {
                    'block_number': log['blockNumber'],
                    'tx_hash': log['transactionHash'].hex(),
                    'log_index': log['logIndex'],
                    'contract_address': address,
                    'event_name': event_name,
                    'payload': json.dumps(args, default=str),
                }
                upsert_chain_event(conn, payload)
                upsert_governance_views(conn, {
                    'event_name': event_name,
                    'args': args,
                    'tx_hash': payload['tx_hash'],
                    'log_index': payload['log_index'],
                    'block_number': payload['block_number'],
                })
                events += 1

        _save_cursor(conn, end_block)

    return {'indexed_to': end_block, 'safe_tip': safe_tip, 'events': events}


def main():
    result = run_once()
    print(f"Indexed {result['events']} events through safe block {result['indexed_to']} (tip={result['safe_tip']})")


if __name__ == '__main__':
    main()
