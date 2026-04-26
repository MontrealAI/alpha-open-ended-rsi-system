CREATE TABLE IF NOT EXISTS indexer_state (
  id SMALLINT PRIMARY KEY DEFAULT 1,
  last_safe_block BIGINT NOT NULL DEFAULT 0,
  updated_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO indexer_state (id, last_safe_block)
VALUES (1, 0)
ON CONFLICT (id) DO NOTHING;

ALTER TABLE seat_challenges
ADD COLUMN IF NOT EXISTS block_number BIGINT NOT NULL DEFAULT 0;

ALTER TABLE seat_challenges
ADD COLUMN IF NOT EXISTS resolved_block_number BIGINT;

CREATE TABLE IF NOT EXISTS reviewer_stake_ledger (
  id BIGSERIAL PRIMARY KEY,
  reviewer TEXT NOT NULL,
  delta NUMERIC NOT NULL,
  kind TEXT NOT NULL,
  reason_hash TEXT,
  tx_hash TEXT NOT NULL,
  log_index BIGINT NOT NULL,
  block_number BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tx_hash, log_index)
);

CREATE TABLE IF NOT EXISTS council_seat_lifecycle (
  id BIGSERIAL PRIMARY KEY,
  term_id BIGINT,
  seat_id BIGINT,
  occupant TEXT,
  event_type TEXT NOT NULL,
  tx_hash TEXT NOT NULL,
  log_index BIGINT NOT NULL,
  block_number BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tx_hash, log_index)
);

DROP VIEW IF EXISTS reviewer_stake_balances;
CREATE VIEW reviewer_stake_balances AS
SELECT reviewer, COALESCE(SUM(delta), 0) AS net_delta
FROM reviewer_stake_ledger
GROUP BY reviewer;

DROP VIEW IF EXISTS council_active_seat_count;
CREATE VIEW council_active_seat_count AS
SELECT COUNT(*)::BIGINT AS active_seats
FROM (
  SELECT DISTINCT ON (seat_id) seat_id, event_type
  FROM council_seat_lifecycle
  ORDER BY seat_id, block_number DESC, log_index DESC
) latest
WHERE latest.event_type IN ('assigned', 'reassigned', 'challenged');
