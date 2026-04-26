CREATE TABLE IF NOT EXISTS seeds (
  seed_id BYTEA PRIMARY KEY,
  token_id BIGINT,
  parent_seed_id BYTEA,
  state SMALLINT,
  manifest_hash BYTEA,
  ciphertext_hash BYTEA,
  public_summary_hash BYTEA,
  payload_uri TEXT,
  sovereign_package_hash BYTEA,
  sovereign_package_uri TEXT,
  sovereign_contract TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reviews (
  id BIGSERIAL PRIMARY KEY,
  seed_id BYTEA NOT NULL,
  reviewer TEXT NOT NULL,
  term_id BIGINT NOT NULL,
  weight BIGINT NOT NULL,
  decision SMALLINT NOT NULL,
  reason_hash BYTEA,
  reviewed_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS decryption_requests (
  request_id BYTEA PRIMARY KEY,
  seed_id BYTEA NOT NULL,
  profile_id BYTEA NOT NULL,
  requester TEXT NOT NULL,
  ciphertext_hash BYTEA NOT NULL,
  manifest_hash BYTEA NOT NULL,
  status SMALLINT NOT NULL,
  plaintext_hash BYTEA,
  completion_hash BYTEA,
  opened_at TIMESTAMPTZ,
  deadline TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS delegations (
  id BIGSERIAL PRIMARY KEY,
  term_id BIGINT NOT NULL,
  delegator TEXT NOT NULL,
  delegatee TEXT NOT NULL,
  voting_weight BIGINT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS seat_challenges (
  challenge_id BYTEA PRIMARY KEY,
  term_id BIGINT NOT NULL,
  seat_id BIGINT NOT NULL,
  challenger TEXT NOT NULL,
  reason_hash BYTEA,
  bond NUMERIC NOT NULL,
  resolved BOOLEAN DEFAULT FALSE,
  upheld BOOLEAN,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS reward_events (
  id BIGSERIAL PRIMARY KEY,
  reviewer TEXT NOT NULL,
  delta NUMERIC NOT NULL,
  kind TEXT NOT NULL,
  ref_hash BYTEA,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS chain_events (
  id BIGSERIAL PRIMARY KEY,
  block_number BIGINT NOT NULL,
  tx_hash TEXT NOT NULL,
  log_index BIGINT NOT NULL,
  contract_address TEXT NOT NULL,
  event_name TEXT NOT NULL,
  payload JSONB NOT NULL,
  UNIQUE(tx_hash, log_index)
);
