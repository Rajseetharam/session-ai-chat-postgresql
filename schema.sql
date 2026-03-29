-- =====================================================
-- SessionAIChat Database Schema
-- =====================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS session_management (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id UUID NOT NULL UNIQUE,
    history JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_user_id
ON session_management(user_id);

CREATE INDEX IF NOT EXISTS idx_session_session_id
ON session_management(session_id);

CREATE INDEX IF NOT EXISTS idx_history_gin
ON session_management
USING GIN (history);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_timestamp ON session_management;

CREATE TRIGGER trg_update_timestamp
BEFORE UPDATE ON session_management
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
