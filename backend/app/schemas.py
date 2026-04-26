from pydantic import BaseModel
from typing import Optional, List

class SeedOut(BaseModel):
    seed_id: str
    token_id: Optional[int] = None
    state: Optional[int] = None
    payload_uri: Optional[str] = None
    sovereign_package_uri: Optional[str] = None
    sovereign_contract: Optional[str] = None

class DashboardSummary(BaseModel):
    seed_count: int
    greenlit_count: int
    sovereign_count: int
    open_decryption_requests: int
    open_challenges: int
    total_delegations: int
    total_reward_events: int

class ReviewerStakeRow(BaseModel):
    reviewer: str
    net_delta: float

class CouncilSeatRow(BaseModel):
    term_id: Optional[int] = None
    seat_id: Optional[int] = None
    occupant: Optional[str] = None
    event_type: str
    tx_hash: str
    block_number: int

class ProofSummary(BaseModel):
    chain_event_count: int
    reviewer_ledger_rows: int
    council_lifecycle_rows: int
    open_challenges: int

class ReadyStatus(BaseModel):
    ok: bool
    chain_events: int
    cursor_block: int
