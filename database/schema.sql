-- ================================================================
-- THE LOST ALGORITHM — Supabase PostgreSQL Schema
-- Run this in the Supabase SQL Editor (project → SQL Editor)
-- ================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── 1. Teams ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_code TEXT UNIQUE NOT NULL,
    team_name TEXT UNIQUE NOT NULL,
    captain_name TEXT NOT NULL,
    captain_email TEXT NOT NULL,
    college_id TEXT NOT NULL,
    member_names TEXT[] NOT NULL DEFAULT '{}',
    num_participants INTEGER NOT NULL DEFAULT 1,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- ── 2. Game sessions ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS game_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_code TEXT NOT NULL REFERENCES teams(team_code) ON DELETE CASCADE,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deadline TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'active',
    current_round INTEGER NOT NULL DEFAULT 1,
    total_score INTEGER NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    hints_used INTEGER NOT NULL DEFAULT 0,
    treasure_code TEXT,
    puzzle_seed BIGINT NOT NULL,
    CONSTRAINT valid_status CHECK (status IN ('active', 'completed', 'expired'))
);

-- ── 3. Question attempts ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS question_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_code TEXT NOT NULL,
    session_id UUID NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL CHECK (round_number BETWEEN 1 AND 10),
    question_index INTEGER NOT NULL CHECK (question_index BETWEEN 0 AND 2),
    submitted_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    points_awarded INTEGER NOT NULL DEFAULT 0,
    hint_used BOOLEAN NOT NULL DEFAULT FALSE,
    attempt_number INTEGER NOT NULL DEFAULT 1,
    attempted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_code, round_number, question_index, attempt_number)
);

-- ── 4. Completed rounds ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS completed_rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_code TEXT NOT NULL,
    session_id UUID NOT NULL REFERENCES game_sessions(id) ON DELETE CASCADE,
    round_number INTEGER NOT NULL CHECK (round_number BETWEEN 1 AND 10),
    round_score INTEGER NOT NULL DEFAULT 0,
    fragment TEXT,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(team_code, round_number)
);

-- ── 5. Leaderboard results ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS leaderboard_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_code TEXT UNIQUE NOT NULL,
    team_name TEXT NOT NULL,
    final_score INTEGER NOT NULL DEFAULT 0,
    correct_answers INTEGER NOT NULL DEFAULT 0,
    rounds_completed INTEGER NOT NULL DEFAULT 0,
    hints_used INTEGER NOT NULL DEFAULT 0,
    completion_time_seconds INTEGER,
    status TEXT NOT NULL DEFAULT 'active',
    finished_at TIMESTAMPTZ,
    rank INTEGER
);

-- ── 6. Event settings ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS event_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Default event settings ───────────────────────────────────────
INSERT INTO event_settings (key, value) VALUES
  ('duration_minutes', '60'),
  ('max_attempts', '3'),
  ('hint_penalty', '5'),
  ('speed_bonus_enabled', 'true'),
  ('event_active', 'true')
ON CONFLICT (key) DO NOTHING;

-- ── Indexes ──────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_attempts_team_round
    ON question_attempts(team_code, round_number);

CREATE INDEX IF NOT EXISTS idx_sessions_team
    ON game_sessions(team_code);

CREATE INDEX IF NOT EXISTS idx_completed_rounds_team
    ON completed_rounds(team_code);

CREATE INDEX IF NOT EXISTS idx_leaderboard_rank
    ON leaderboard_results(final_score DESC, completion_time_seconds ASC NULLS LAST);

-- ── Row-Level Security (RLS) ──────────────────────────────────────
-- Enable RLS on all tables (use service role key in the app)
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE game_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE question_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE completed_rounds ENABLE ROW LEVEL SECURITY;
ALTER TABLE leaderboard_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_settings ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (the app uses service role key)
-- Public read on leaderboard (safe fields only)
CREATE POLICY "Public leaderboard read" ON leaderboard_results
    FOR SELECT USING (true);

-- Public read on event settings
CREATE POLICY "Public settings read" ON event_settings
    FOR SELECT USING (true);

-- Service role can do everything (via service_role_key — no policy needed,
-- service role bypasses RLS by default in Supabase)

