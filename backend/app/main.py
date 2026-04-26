from pathlib import Path
import json
import os
from fastapi import FastAPI, Response
from sqlalchemy import text
from typing import List
from .db import engine
from .schemas import DashboardSummary, ProofSummary, ReviewerStakeRow, CouncilSeatRow, ReadyStatus

app = FastAPI(title="Nova-Seeds v2.6 RC API", version="2.6.0-rc.1")

def _resolve_ascension_out() -> Path:
    env_path = os.getenv("ASCENSION_OUT_DIR")
    if env_path:
        return Path(env_path).expanduser().resolve()

    module = Path(__file__).resolve()
    for parent in [module.parent, *module.parents]:
        candidate = parent / "demos" / "ascension-live-runtime" / "out"
        if candidate.exists():
            return candidate

    return Path.cwd() / "demos" / "ascension-live-runtime" / "out"


ASCENSION_OUT = _resolve_ascension_out()


def _read_ascension_artifact(filename: str, fallback: dict | list) -> dict | list:
    path = ASCENSION_OUT / filename
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


@app.get('/health')
def health():
    return {'ok': True, 'version': app.version}


@app.get('/ready', response_model=ReadyStatus)
def ready():
    with engine.begin() as conn:
        chain_events = conn.execute(text('SELECT count(*) FROM chain_events')).scalar_one_or_none() or 0
        cursor_block = conn.execute(text('SELECT last_safe_block FROM indexer_state WHERE id = 1')).scalar_one_or_none() or 0
    return ReadyStatus(ok=True, chain_events=chain_events, cursor_block=cursor_block)


@app.get('/dashboard/summary', response_model=DashboardSummary)
def dashboard_summary():
    with engine.begin() as conn:
        seed_count = conn.execute(text('SELECT count(*) FROM seeds')).scalar_one_or_none() or 0
        greenlit_count = conn.execute(text('SELECT count(*) FROM seeds WHERE state = 4')).scalar_one_or_none() or 0
        sovereign_count = conn.execute(text('SELECT count(*) FROM seeds WHERE state = 6')).scalar_one_or_none() or 0
        open_decryption_requests = conn.execute(text('SELECT count(*) FROM decryption_requests WHERE status = 1')).scalar_one_or_none() or 0
        open_challenges = conn.execute(text('SELECT count(*) FROM seat_challenges WHERE resolved = false')).scalar_one_or_none() or 0
        total_delegations = conn.execute(text('SELECT count(*) FROM delegations')).scalar_one_or_none() or 0
        total_reward_events = conn.execute(text('SELECT count(*) FROM reward_events')).scalar_one_or_none() or 0
    return DashboardSummary(
        seed_count=seed_count,
        greenlit_count=greenlit_count,
        sovereign_count=sovereign_count,
        open_decryption_requests=open_decryption_requests,
        open_challenges=open_challenges,
        total_delegations=total_delegations,
        total_reward_events=total_reward_events,
    )


@app.get('/proof/summary', response_model=ProofSummary)
def proof_summary():
    with engine.begin() as conn:
        chain_event_count = conn.execute(text('SELECT count(*) FROM chain_events')).scalar_one_or_none() or 0
        reviewer_ledger_rows = conn.execute(text('SELECT count(*) FROM reviewer_stake_ledger')).scalar_one_or_none() or 0
        council_lifecycle_rows = conn.execute(text('SELECT count(*) FROM council_seat_lifecycle')).scalar_one_or_none() or 0
        open_challenges = conn.execute(text('SELECT count(*) FROM seat_challenges WHERE resolved = false')).scalar_one_or_none() or 0
    return ProofSummary(
        chain_event_count=chain_event_count,
        reviewer_ledger_rows=reviewer_ledger_rows,
        council_lifecycle_rows=council_lifecycle_rows,
        open_challenges=open_challenges,
    )


@app.get('/governance/reviewer-ledger', response_model=List[ReviewerStakeRow])
def reviewer_ledger():
    with engine.begin() as conn:
        rows = conn.execute(text('SELECT reviewer, net_delta::float8 AS net_delta FROM reviewer_stake_balances ORDER BY reviewer ASC')).mappings().all()
    return [ReviewerStakeRow(**row) for row in rows]


@app.get('/governance/council-seats', response_model=List[CouncilSeatRow])
def council_seats():
    with engine.begin() as conn:
        rows = conn.execute(text('''
            SELECT term_id, seat_id, occupant, event_type, tx_hash, block_number
            FROM council_seat_lifecycle
            ORDER BY block_number DESC, log_index DESC
            LIMIT 200
        ''')).mappings().all()
    return [CouncilSeatRow(**row) for row in rows]


@app.get('/ascension/status')
def ascension_status():
    scorecard = _read_ascension_artifact("ascension_runtime_scorecard.json", {"layers": []})
    events = _read_ascension_artifact("events.json", {"events": []})
    return {
        "available": bool(scorecard.get("layers")),
        "layer_count": len(scorecard.get("layers", [])),
        "event_count": len(events.get("events", [])),
        "claim_boundary": scorecard.get("claim_boundary", "No ascension runtime artifacts available."),
    }


@app.get('/ascension/seeds')
def ascension_seeds():
    return _read_ascension_artifact("nova_seed_registry_snapshot.json", {"seeds": []})


@app.get('/ascension/mark')
def ascension_mark():
    return {
        "selection": _read_ascension_artifact("mark_selection_report.json", {}),
        "risk": _read_ascension_artifact("mark_risk_report.json", {}),
    }


@app.get('/ascension/sovereigns')
def ascension_sovereigns():
    return {
        "manifest": _read_ascension_artifact("sovereign_manifest.json", {}),
        "state": _read_ascension_artifact("sovereign_state_snapshot.json", {}),
    }


@app.get('/ascension/jobs')
def ascension_jobs():
    return {
        "job_spec": _read_ascension_artifact("jobs/job_spec.json", {}),
        "job_completion": _read_ascension_artifact("jobs/job_completion.json", {}),
        "job_receipt": _read_ascension_artifact("jobs/job_receipt.json", {}),
        "job_events": _read_ascension_artifact("jobs/job_event_log.json", {}),
    }


@app.get('/ascension/agents')
def ascension_agents():
    return {
        "marketplace_round": _read_ascension_artifact("marketplace_round.json", {}),
        "execution_log": _read_ascension_artifact("agent_execution_log.json", {}),
        "reputation": _read_ascension_artifact("agent_reputation_snapshot.json", {}),
    }


@app.get('/ascension/validators')
def ascension_validators():
    return {
        "validation_round": _read_ascension_artifact("validation_round.json", {}),
        "attestation": _read_ascension_artifact("validation_attestation.json", {}),
        "council_ruling": _read_ascension_artifact("council_ruling.json", {}),
    }


@app.get('/ascension/reservoir')
def ascension_reservoir():
    return {
        "ledger": _read_ascension_artifact("reservoir_ledger.json", {}),
        "epoch_report": _read_ascension_artifact("reservoir_epoch_report.json", {}),
    }


@app.get('/ascension/archive')
def ascension_archive():
    return {
        "lineage": _read_ascension_artifact("archive_lineage.json", {}),
        "index": _read_ascension_artifact("archive_index.json", {}),
        "capability_manifest": _read_ascension_artifact("capability_package_manifest.json", {}),
    }


@app.get('/ascension/architect')
def ascension_architect():
    return {
        "recommendation": _read_ascension_artifact("architect_recommendation.json", {}),
        "next_loop_plan": _read_ascension_artifact("next_loop_plan.json", {}),
    }


@app.get('/ascension/scorecard')
def ascension_scorecard():
    return _read_ascension_artifact("ascension_runtime_scorecard.json", {"layers": []})


@app.get('/metrics')
def metrics():
    with engine.begin() as conn:
        chain_events = conn.execute(text('SELECT count(*) FROM chain_events')).scalar_one_or_none() or 0
        ledger_rows = conn.execute(text('SELECT count(*) FROM reviewer_stake_ledger')).scalar_one_or_none() or 0
        seats_rows = conn.execute(text('SELECT count(*) FROM council_seat_lifecycle')).scalar_one_or_none() or 0

    payload = (
        '# HELP nova_chain_events_total Indexed chain events\n'
        '# TYPE nova_chain_events_total gauge\n'
        f'nova_chain_events_total {chain_events}\n'
        '# HELP nova_reviewer_stake_rows_total Reviewer stake ledger rows\n'
        '# TYPE nova_reviewer_stake_rows_total gauge\n'
        f'nova_reviewer_stake_rows_total {ledger_rows}\n'
        '# HELP nova_council_lifecycle_rows_total Council seat lifecycle rows\n'
        '# TYPE nova_council_lifecycle_rows_total gauge\n'
        f'nova_council_lifecycle_rows_total {seats_rows}\n'
    )
    return Response(content=payload, media_type='text/plain; version=0.0.4')


@app.get('/openapi.json')
def openapi_export():
    return app.openapi()
