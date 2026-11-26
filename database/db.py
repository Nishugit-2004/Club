"""
database/db.py — SQLite database layer for The Lost Algorithm.
Stores all game sessions, attempts, scores, leaderboard data, team member profiles,
and faculty coordinator profiles in a persistent local SQLite database file: treasure_hunt.db
"""
from __future__ import annotations

import json
import os
import sqlite3
import hashlib
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional, Any
from contextlib import contextmanager

# ── Local database path & asset directories ─────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "treasure_hunt.db")
TEAM_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "team")
FACULTY_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "faculty")

# Ensure assets directories exist
os.makedirs(TEAM_ASSETS_DIR, exist_ok=True)
os.makedirs(FACULTY_ASSETS_DIR, exist_ok=True)


@contextmanager
def get_db():
    """Thread-safe context manager for SQLite database connection."""
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def is_db_available() -> bool:
    """Always True for SQLite since the local file is auto-created."""
    try:
        init_db()
        return True
    except Exception:
        return False


# ── Database Initialization & Migrations ────────────────────────────────────

def init_db() -> None:
    """Initialize database tables, apply schema migrations, and sync default data."""
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_code TEXT UNIQUE NOT NULL,
            team_name TEXT UNIQUE NOT NULL,
            captain_name TEXT NOT NULL,
            captain_email TEXT NOT NULL,
            college_id TEXT NOT NULL,
            member_names TEXT NOT NULL DEFAULT '[]',
            num_participants INTEGER NOT NULL DEFAULT 1,
            registered_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_code TEXT UNIQUE NOT NULL,
            started_at TEXT NOT NULL,
            deadline TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            current_round INTEGER NOT NULL DEFAULT 1,
            total_score INTEGER NOT NULL DEFAULT 0,
            correct_answers INTEGER NOT NULL DEFAULT 0,
            hints_used INTEGER NOT NULL DEFAULT 0,
            treasure_code TEXT,
            puzzle_seed INTEGER NOT NULL,
            FOREIGN KEY (team_code) REFERENCES teams(team_code) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS question_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_code TEXT NOT NULL,
            session_id INTEGER NOT NULL,
            round_number INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            submitted_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            points_awarded INTEGER NOT NULL DEFAULT 0,
            hint_used INTEGER NOT NULL DEFAULT 0,
            attempt_number INTEGER NOT NULL DEFAULT 1,
            attempted_at TEXT NOT NULL,
            UNIQUE(team_code, round_number, question_index, attempt_number),
            FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS completed_rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_code TEXT NOT NULL,
            session_id INTEGER NOT NULL,
            round_number INTEGER NOT NULL,
            round_score INTEGER NOT NULL DEFAULT 0,
            fragment TEXT,
            completed_at TEXT NOT NULL,
            UNIQUE(team_code, round_number),
            FOREIGN KEY (session_id) REFERENCES game_sessions(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS leaderboard_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_code TEXT UNIQUE NOT NULL,
            team_name TEXT NOT NULL,
            final_score INTEGER NOT NULL DEFAULT 0,
            correct_answers INTEGER NOT NULL DEFAULT 0,
            rounds_completed INTEGER NOT NULL DEFAULT 0,
            hints_used INTEGER NOT NULL DEFAULT 0,
            completion_time_seconds INTEGER,
            status TEXT NOT NULL DEFAULT 'active',
            finished_at TEXT,
            rank INTEGER
        );

        CREATE TABLE IF NOT EXISTS event_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS club_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            bio TEXT,
            usn TEXT DEFAULT '',
            photo_path TEXT DEFAULT '',
            display_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS faculty_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT NOT NULL,
            description TEXT,
            expertise TEXT,
            photo_path TEXT DEFAULT '',
            display_order INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_attempts_team_round ON question_attempts(team_code, round_number);
        CREATE INDEX IF NOT EXISTS idx_sessions_team ON game_sessions(team_code);
        CREATE INDEX IF NOT EXISTS idx_completed_rounds_team ON completed_rounds(team_code);
        """)

        # Migration: Ensure 'usn' column exists in club_members
        cursor = conn.execute("PRAGMA table_info(club_members);")
        columns = [col[1] for col in cursor.fetchall()]
        if "usn" not in columns:
            conn.execute("ALTER TABLE club_members ADD COLUMN usn TEXT DEFAULT '';")

        # Default event settings
        defaults = [
            ("duration_minutes", "60"),
            ("max_attempts", "3"),
            ("hint_penalty", "5"),
            ("speed_bonus_enabled", "true"),
            ("event_active", "true"),
        ]
        now_iso = datetime.now(timezone.utc).isoformat()
        for k, v in defaults:
            conn.execute(
                "INSERT OR IGNORE INTO event_settings (key, value, updated_at) VALUES (?, ?, ?)",
                (k, v, now_iso),
            )

        # ── 1. Faculty Profiles (Department of CSE) ──────────────────────────
        faculty_specs = [
            {
                "order": 1,
                "name": "Dr. Varun E",
                "aliases": ["Varun E", "Dr. Varun E"],
                "designation": "Associate Professor",
                "default_photo": "assets/faculty/dr_varun_e.jpg",
                "description": "Passionate about algorithms and competitive programming. Guides students through complex problem-solving strategies and mentors the coding club's technical initiatives.",
                "expertise": "Algorithms · Data Structures · Competitive Programming",
            },
            {
                "order": 2,
                "name": "Prof Ramanjinamma G",
                "aliases": ["Ramanjinamma G", "Prof Ramanjinamma G"],
                "designation": "Assistant Professor",
                "default_photo": "assets/faculty/prof_ramanjinamma_g.jpg",
                "description": "Brings deep expertise in computer networks and systems programming. Champions hands-on learning and advocates for open-source contribution among students.",
                "expertise": "Computer Networks · Systems Programming · Open Source",
            },
            {
                "order": 3,
                "name": "Prof Lalitha K",
                "aliases": ["Lalitha K", "Prof Lalitha K"],
                "designation": "Assistant Professor",
                "default_photo": "assets/faculty/prof_lalitha_k.jpg",
                "description": "Specialises in machine learning and data-driven approaches to problem-solving. Inspires students to explore the intersection of mathematics and computing.",
                "expertise": "Machine Learning · Mathematics · Data Science",
            },
        ]

        for spec in faculty_specs:
            placeholders = ",".join("?" for _ in spec["aliases"])
            existing_fac = conn.execute(
                f"SELECT * FROM faculty_profiles WHERE name IN ({placeholders}) OR display_order = ? LIMIT 1",
                (*spec["aliases"], spec["order"]),
            ).fetchone()

            if existing_fac:
                # Update name & designation, preserving any customized descriptions or uploaded photos
                cur_photo = existing_fac["photo_path"] or spec["default_photo"]
                cur_desc = existing_fac["description"] or spec["description"]
                cur_exp = existing_fac["expertise"] or spec["expertise"]
                conn.execute(
                    """UPDATE faculty_profiles
                       SET name = ?, designation = ?, description = ?, expertise = ?, photo_path = ?, display_order = ?, updated_at = ?
                       WHERE id = ?""",
                    (
                        spec["name"],
                        spec["designation"],
                        cur_desc,
                        cur_exp,
                        cur_photo,
                        spec["order"],
                        now_iso,
                        existing_fac["id"],
                    ),
                )
            else:
                conn.execute(
                    """INSERT INTO faculty_profiles (name, designation, description, expertise, photo_path, display_order, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        spec["name"],
                        spec["designation"],
                        spec["description"],
                        spec["expertise"],
                        spec["default_photo"],
                        spec["order"],
                        now_iso,
                        now_iso,
                    ),
                )

        # ── 2. Student Team Members (9 Coordinators) ─────────────────────────
        # Clean up old generic placeholders if present
        placeholder_names = [
            "Aarav Patel", "Sneha Sharma", "Rohan Verma", "Ananya Reddy",
            "Vikram Rao", "Priya Nair", "Karthik Iyer", "Meera Joshi",
            "[Member 1]", "[Member 2]", "[Member 3]", "[Member 4]",
            "[Member 5]", "[Member 6]", "[Member 7]", "[Member 8]"
        ]
        conn.execute(
            f"DELETE FROM club_members WHERE name IN ({','.join('?' for _ in placeholder_names)})",
            placeholder_names,
        )

        student_coordinators = [
            (1, "President", "Mahima K", "1VA23CS092", "Leads the coding club's initiatives, technical events, and student engagement."),
            (2, "Vice President", "Samyak D Karekar", "1VA24CS0121", "Oversees operational planning, technical contests, and team coordination."),
            (3, "Joint Secretary", "Shalini M Gowda", "1VA24CS125", "Coordinates between department faculty and student club committees."),
            (4, "Social Media", "Shankar SB", "1VA23CS145", "Manages club outreach, design branding, and digital announcements."),
            (5, "Treasurer", "Aadita Nag", "1VA23CS001", "Manages event budgets, resources, prize distribution, and sponsorships."),
            (6, "Documentation Lead", "Kavyashree SN", "1VA24CS064", "Maintains records, event reports, challenge documentation, and archives."),
            (7, "Membership Coordinator", "Harshitha N", "1VA24CS055", "Facilitates student onboarding, member engagement, and participation."),
            (8, "Membership Coordinator", "Suhail D Tamboli", "1VA23CS195", "Assists member drives, club communications, and workshop logistics."),
            (9, "Secretary", "Jagadeesha", "1VA23CS065", "Oversees meeting records, administrative logistics, and club correspondence."),
        ]

        for order, role, name, usn, bio in student_coordinators:
            # Check by USN or Name to prevent duplicates
            existing_m = conn.execute(
                "SELECT * FROM club_members WHERE usn = ? OR name = ? LIMIT 1",
                (usn, name),
            ).fetchone()

            if existing_m:
                cur_photo = existing_m["photo_path"] or ""
                cur_bio = existing_m["bio"] or bio
                conn.execute(
                    """UPDATE club_members
                       SET name = ?, role = ?, usn = ?, bio = ?, photo_path = ?, display_order = ?, updated_at = ?
                       WHERE id = ?""",
                    (name, role, usn, cur_bio, cur_photo, order, now_iso, existing_m["id"]),
                )
            else:
                conn.execute(
                    """INSERT INTO club_members (name, role, bio, usn, photo_path, display_order, created_at, updated_at)
                       VALUES (?, ?, ?, ?, '', ?, ?, ?)""",
                    (name, role, bio, usn, order, now_iso, now_iso),
                )


# Auto-initialize on import
init_db()


# ── Team operations ─────────────────────────────────────────────────────────

def generate_team_code() -> str:
    """Generate a unique 8-character team code."""
    charset = string.ascii_uppercase + string.digits
    return "TLA-" + "".join(secrets.choice(charset) for _ in range(6))


def register_team(
    team_name: str,
    captain_name: str,
    captain_email: str,
    college_id: str,
    member_names: list[str],
    num_participants: int,
) -> dict:
    """Register a new team in SQLite."""
    try:
        with get_db() as conn:
            existing = conn.execute(
                "SELECT id FROM teams WHERE team_name = ?", (team_name,)
            ).fetchone()
            if existing:
                return {"success": False, "error": f"Team name '{team_name}' is already registered."}

            # Generate unique code
            code = ""
            for _ in range(10):
                c = generate_team_code()
                chk = conn.execute("SELECT id FROM teams WHERE team_code = ?", (c,)).fetchone()
                if not chk:
                    code = c
                    break
            if not code:
                return {"success": False, "error": "Could not generate a unique team code. Please try again."}

            now_iso = datetime.now(timezone.utc).isoformat()
            members_json = json.dumps(member_names)

            conn.execute(
                """INSERT INTO teams (team_code, team_name, captain_name, captain_email, college_id, member_names, num_participants, registered_at, is_active)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (code, team_name, captain_name, captain_email, college_id, members_json, num_participants, now_iso),
            )

            return {"success": True, "team_code": code}
    except Exception as e:
        return {"success": False, "error": f"Registration failed: {str(e)}"}


def get_team(team_code: str) -> Optional[dict]:
    """Fetch team by code."""
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM teams WHERE team_code = ?", (team_code,)).fetchone()
            if not row:
                return None
            data = dict(row)
            try:
                data["member_names"] = json.loads(data["member_names"])
            except Exception:
                data["member_names"] = []
            return data
    except Exception:
        return None


# ── Game session operations ─────────────────────────────────────────────────

def get_or_create_session(team_code: str) -> Optional[dict]:
    """Get the existing game session or create a new one."""
    try:
        with get_db() as conn:
            existing = conn.execute(
                "SELECT * FROM game_sessions WHERE team_code = ?", (team_code,)
            ).fetchone()
            if existing:
                return dict(existing)

            # Get duration from event settings
            dur_row = conn.execute(
                "SELECT value FROM event_settings WHERE key = 'duration_minutes'"
            ).fetchone()
            duration_minutes = int(dur_row["value"]) if dur_row else 60

            now = datetime.now(timezone.utc)
            deadline = now + timedelta(minutes=duration_minutes)

            # Deterministic puzzle seed from team code
            seed = int(hashlib.md5(team_code.encode()).hexdigest()[:8], 16)

            conn.execute(
                """INSERT INTO game_sessions (team_code, started_at, deadline, status, current_round, total_score, correct_answers, hints_used, puzzle_seed)
                   VALUES (?, ?, ?, 'active', 1, 0, 0, 0, ?)""",
                (team_code, now.isoformat(), deadline.isoformat(), seed),
            )

            row = conn.execute(
                "SELECT * FROM game_sessions WHERE team_code = ?", (team_code,)
            ).fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def get_session(team_code: str) -> Optional[dict]:
    """Get existing game session."""
    try:
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM game_sessions WHERE team_code = ?", (team_code,)
            ).fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def update_session(team_code: str, updates: dict) -> bool:
    """Update game session fields."""
    if not updates:
        return True
    try:
        with get_db() as conn:
            set_clauses = [f"{k} = ?" for k in updates.keys()]
            values = list(updates.values())
            values.append(team_code)
            sql = f"UPDATE game_sessions SET {', '.join(set_clauses)} WHERE team_code = ?"
            conn.execute(sql, values)
            return True
    except Exception:
        return False


def expire_session_if_needed(session: dict) -> dict:
    """Check if the session deadline has passed and mark it expired."""
    if session.get("status") != "active":
        return session

    deadline_str = session.get("deadline", "")
    if not deadline_str:
        return session

    try:
        deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if now > deadline and session["status"] == "active":
            update_session(session["team_code"], {"status": "expired"})
            session["status"] = "expired"
    except Exception:
        pass

    return session


# ── Attempt operations ───────────────────────────────────────────────────────

def get_attempt_count(team_code: str, round_number: int, question_index: int) -> int:
    """Get number of attempts for a question."""
    try:
        with get_db() as conn:
            row = conn.execute(
                """SELECT COUNT(*) FROM question_attempts
                   WHERE team_code = ? AND round_number = ? AND question_index = ?""",
                (team_code, round_number, question_index),
            ).fetchone()
            return row[0] if row else 0
    except Exception:
        return 0


def is_question_solved(team_code: str, round_number: int, question_index: int) -> bool:
    """Check if a question was already correctly answered."""
    try:
        with get_db() as conn:
            row = conn.execute(
                """SELECT id FROM question_attempts
                   WHERE team_code = ? AND round_number = ? AND question_index = ? AND is_correct = 1""",
                (team_code, round_number, question_index),
            ).fetchone()
            return bool(row)
    except Exception:
        return False


def record_attempt(
    team_code: str,
    session_id: int,
    round_number: int,
    question_index: int,
    submitted_answer: str,
    is_correct: bool,
    points_awarded: int,
    hint_used: bool,
) -> dict:
    """Record an answer attempt."""
    try:
        if is_question_solved(team_code, round_number, question_index):
            return {"already_solved": True}

        attempt_num = get_attempt_count(team_code, round_number, question_index) + 1
        now_iso = datetime.now(timezone.utc).isoformat()

        with get_db() as conn:
            conn.execute(
                """INSERT INTO question_attempts (team_code, session_id, round_number, question_index, submitted_answer, is_correct, points_awarded, hint_used, attempt_number, attempted_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    team_code,
                    session_id,
                    round_number,
                    question_index,
                    submitted_answer[:500],
                    1 if is_correct else 0,
                    points_awarded,
                    1 if hint_used else 0,
                    attempt_num,
                    now_iso,
                ),
            )

            if is_correct:
                sess_row = conn.execute(
                    "SELECT total_score, correct_answers FROM game_sessions WHERE team_code = ?",
                    (team_code,),
                ).fetchone()
                if sess_row:
                    new_score = sess_row["total_score"] + points_awarded
                    new_correct = sess_row["correct_answers"] + 1
                    conn.execute(
                        "UPDATE game_sessions SET total_score = ?, correct_answers = ? WHERE team_code = ?",
                        (new_score, new_correct, team_code),
                    )

        return {"attempt_number": attempt_num, "already_solved": False}
    except Exception as e:
        return {"error": str(e)}


def record_hint_used(team_code: str) -> bool:
    """Increment hint counter in session."""
    try:
        with get_db() as conn:
            conn.execute(
                "UPDATE game_sessions SET hints_used = hints_used + 1 WHERE team_code = ?",
                (team_code,),
            )
            return True
    except Exception:
        return False


# ── Round operations ─────────────────────────────────────────────────────────

def get_completed_rounds(team_code: str) -> list[dict]:
    """Get all completed rounds for a team."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM completed_rounds WHERE team_code = ? ORDER BY round_number ASC",
                (team_code,),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def get_completed_round_numbers(team_code: str) -> set[int]:
    """Get set of completed round numbers."""
    rounds = get_completed_rounds(team_code)
    return {r["round_number"] for r in rounds}


def complete_round(
    team_code: str, session_id: int, round_number: int, round_score: int, fragment: str
) -> bool:
    """Mark a round as complete."""
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            chk = conn.execute(
                "SELECT id FROM completed_rounds WHERE team_code = ? AND round_number = ?",
                (team_code, round_number),
            ).fetchone()
            if chk:
                return True

            conn.execute(
                """INSERT INTO completed_rounds (team_code, session_id, round_number, round_score, fragment, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (team_code, session_id, round_number, round_score, fragment, now_iso),
            )

            new_round = round_number + 1 if round_number < 10 else 10
            sess = conn.execute(
                "SELECT current_round FROM game_sessions WHERE team_code = ?", (team_code,)
            ).fetchone()
            if sess and sess["current_round"] <= round_number:
                conn.execute(
                    "UPDATE game_sessions SET current_round = ? WHERE team_code = ?",
                    (new_round, team_code),
                )
        return True
    except Exception:
        return False


def get_round_attempts(team_code: str, round_number: int) -> list[dict]:
    """Get all attempts for a specific round."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM question_attempts WHERE team_code = ? AND round_number = ?",
                (team_code, round_number),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def get_question_attempts(team_code: str, round_number: int, question_index: int) -> list[dict]:
    """Get all attempts for a specific question."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                """SELECT * FROM question_attempts
                   WHERE team_code = ? AND round_number = ? AND question_index = ?
                   ORDER BY attempt_number ASC""",
                (team_code, round_number, question_index),
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


# ── Leaderboard ──────────────────────────────────────────────────────────────

def upsert_leaderboard(team_code: str, team_name: str, session: dict) -> bool:
    """Upsert the leaderboard entry for this team."""
    try:
        completed_rounds_count = len(get_completed_round_numbers(team_code))
        completion_time = None
        if session.get("completed_at") and session.get("started_at"):
            start = datetime.fromisoformat(session["started_at"].replace("Z", "+00:00"))
            end = datetime.fromisoformat(session["completed_at"].replace("Z", "+00:00"))
            completion_time = int((end - start).total_seconds())

        with get_db() as conn:
            conn.execute(
                """INSERT INTO leaderboard_results
                   (team_code, team_name, final_score, correct_answers, rounds_completed, hints_used, completion_time_seconds, status, finished_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(team_code) DO UPDATE SET
                   team_name = excluded.team_name,
                   final_score = excluded.final_score,
                   correct_answers = excluded.correct_answers,
                   rounds_completed = excluded.rounds_completed,
                   hints_used = excluded.hints_used,
                   completion_time_seconds = excluded.completion_time_seconds,
                   status = excluded.status,
                   finished_at = excluded.finished_at""",
                (
                    team_code,
                    team_name,
                    session.get("total_score", 0),
                    session.get("correct_answers", 0),
                    completed_rounds_count,
                    session.get("hints_used", 0),
                    completion_time,
                    session.get("status", "active"),
                    session.get("completed_at"),
                ),
            )
        return True
    except Exception:
        return False


def get_leaderboard(limit: int = 50) -> list[dict]:
    """
    Get leaderboard ordered by: score DESC, completion_time ASC, hints ASC.
    Ties on all three criteria share the same rank (dense ranking).
    """
    try:
        with get_db() as conn:
            rows = conn.execute(
                """SELECT team_code, team_name, final_score, correct_answers,
                          rounds_completed, hints_used, completion_time_seconds,
                          status, finished_at
                   FROM leaderboard_results
                   ORDER BY final_score DESC,
                            COALESCE(completion_time_seconds, 999999) ASC,
                            hints_used ASC
                   LIMIT ?""",
                (limit,),
            ).fetchall()

            res = [dict(r) for r in rows]
            # Dense ranking: tied entries share a rank
            prev_key = None
            current_rank = 0
            position = 0
            for r in res:
                position += 1
                key = (
                    r["final_score"],
                    r["completion_time_seconds"] or 999999,
                    r["hints_used"],
                )
                if key != prev_key:
                    current_rank = position
                    prev_key = key
                r["rank"] = current_rank
            return res
    except Exception:
        return []


def sync_all_active_sessions_to_leaderboard() -> int:
    """
    Sync every team that has an active game session into the leaderboard_results
    table so their current in-progress scores appear on the live leaderboard.
    Returns the number of teams synced.
    """
    synced = 0
    try:
        with get_db() as conn:
            # Fetch all sessions joined with team names
            sessions = conn.execute(
                """SELECT gs.team_code, gs.total_score, gs.correct_answers,
                          gs.hints_used, gs.status, gs.started_at, gs.completed_at,
                          t.team_name
                   FROM game_sessions gs
                   JOIN teams t ON t.team_code = gs.team_code"""
            ).fetchall()

            now_iso = datetime.now(timezone.utc).isoformat()

            for s in sessions:
                team_code = s["team_code"]
                team_name = s["team_name"]
                score = s["total_score"] or 0
                correct = s["correct_answers"] or 0
                hints = s["hints_used"] or 0
                status = s["status"] or "active"
                completed_at = s["completed_at"]
                started_at = s["started_at"]

                # Count completed rounds for this team
                rds_row = conn.execute(
                    "SELECT COUNT(*) FROM completed_rounds WHERE team_code = ?",
                    (team_code,),
                ).fetchone()
                rounds_done = rds_row[0] if rds_row else 0

                # Completion time
                completion_time = None
                if completed_at and started_at:
                    try:
                        start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                        end = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
                        completion_time = int((end - start).total_seconds())
                    except Exception:
                        pass

                conn.execute(
                    """INSERT INTO leaderboard_results
                       (team_code, team_name, final_score, correct_answers,
                        rounds_completed, hints_used, completion_time_seconds,
                        status, finished_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(team_code) DO UPDATE SET
                           team_name = excluded.team_name,
                           final_score = excluded.final_score,
                           correct_answers = excluded.correct_answers,
                           rounds_completed = excluded.rounds_completed,
                           hints_used = excluded.hints_used,
                           completion_time_seconds = excluded.completion_time_seconds,
                           status = excluded.status,
                           finished_at = excluded.finished_at""",
                    (
                        team_code, team_name, score, correct,
                        rounds_done, hints, completion_time, status, completed_at,
                    ),
                )
                synced += 1
    except Exception:
        pass
    return synced


def get_team_rank(team_code: str) -> Optional[int]:
    """Get the current rank of a team."""
    try:
        lb = get_leaderboard(limit=1000)
        for row in lb:
            if row.get("team_code") == team_code:
                return row["rank"]
        return None
    except Exception:
        return None


def finalise_game(team_code: str, treasure_code: str) -> bool:
    """Mark the game as completed and record the treasure code."""
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        update_session(
            team_code,
            {
                "status": "completed",
                "completed_at": now_iso,
                "treasure_code": treasure_code,
            },
        )
        team = get_team(team_code)
        session = get_session(team_code)
        if team and session:
            upsert_leaderboard(team_code, team["team_name"], session)
        return True
    except Exception:
        return False


# ── Event settings ────────────────────────────────────────────────────────────

def get_event_setting(key: str, default: str = "") -> str:
    try:
        with get_db() as conn:
            row = conn.execute("SELECT value FROM event_settings WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else default
    except Exception:
        return default


def set_event_setting(key: str, value: str) -> bool:
    try:
        now_iso = datetime.now(timezone.utc).isoformat()
        with get_db() as conn:
            conn.execute(
                """INSERT INTO event_settings (key, value, updated_at) VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at""",
                (key, value, now_iso),
            )
            return True
    except Exception:
        return False


# ── Organizer operations ──────────────────────────────────────────────────────

def get_all_teams_with_sessions() -> list[dict]:
    """Get all teams with their session info (for organizer dashboard)."""
    try:
        with get_db() as conn:
            teams = [dict(r) for r in conn.execute("SELECT * FROM teams ORDER BY id DESC").fetchall()]
            sessions = {
                r["team_code"]: dict(r)
                for r in conn.execute("SELECT * FROM game_sessions").fetchall()
            }
            lb = {
                r["team_code"]: dict(r)
                for r in conn.execute("SELECT * FROM leaderboard_results").fetchall()
            }

            for t in teams:
                t["session"] = sessions.get(t["team_code"])
                t["leaderboard"] = lb.get(t["team_code"])
            return teams
    except Exception:
        return []


def reset_team_game(team_code: str) -> bool:
    """Reset a team's game (organizer action)."""
    try:
        with get_db() as conn:
            conn.execute("DELETE FROM question_attempts WHERE team_code = ?", (team_code,))
            conn.execute("DELETE FROM completed_rounds WHERE team_code = ?", (team_code,))
            conn.execute("DELETE FROM game_sessions WHERE team_code = ?", (team_code,))
            conn.execute("DELETE FROM leaderboard_results WHERE team_code = ?", (team_code,))
        return True
    except Exception:
        return False


# ── Team Member & Faculty Profile Management ─────────────────────────────────

def get_club_members() -> list[dict]:
    """Get all club members ordered by display_order then id."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM club_members ORDER BY display_order ASC, id ASC"
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def get_club_member(member_id: int) -> Optional[dict]:
    """Get a specific club member by id."""
    try:
        with get_db() as conn:
            row = conn.execute("SELECT * FROM club_members WHERE id = ?", (member_id,)).fetchone()
            return dict(row) if row else None
    except Exception:
        return None


def add_club_member(
    name: str,
    role: str,
    bio: str = "",
    usn: str = "",
    photo_path: str = "",
    display_order: int = 0,
) -> int:
    """Add a new club member profile. Returns member id."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO club_members (name, role, bio, usn, photo_path, display_order, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, role, bio, usn, photo_path, display_order, now_iso, now_iso),
        )
        return cursor.lastrowid


def update_club_member(
    member_id: int,
    name: str,
    role: str,
    bio: str = "",
    usn: str = "",
    photo_path: Optional[str] = None,
    display_order: int = 0,
) -> bool:
    """Update an existing club member profile."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        if photo_path is not None:
            conn.execute(
                """UPDATE club_members
                   SET name = ?, role = ?, bio = ?, usn = ?, photo_path = ?, display_order = ?, updated_at = ?
                   WHERE id = ?""",
                (name, role, bio, usn, photo_path, display_order, now_iso, member_id),
            )
        else:
            conn.execute(
                """UPDATE club_members
                   SET name = ?, role = ?, bio = ?, usn = ?, display_order = ?, updated_at = ?
                   WHERE id = ?""",
                (name, role, bio, usn, display_order, now_iso, member_id),
            )
        return True


def delete_club_member(member_id: int) -> bool:
    """Delete a club member profile."""
    with get_db() as conn:
        conn.execute("DELETE FROM club_members WHERE id = ?", (member_id,))
        return True


def get_faculty_profiles() -> list[dict]:
    """Get all faculty profiles ordered by display_order then id."""
    try:
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM faculty_profiles ORDER BY display_order ASC, id ASC"
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []


def update_faculty_profile(
    faculty_id: int,
    name: str,
    designation: str,
    description: str,
    expertise: str,
    photo_path: Optional[str] = None,
) -> bool:
    """Update a faculty profile."""
    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        if photo_path is not None:
            conn.execute(
                """UPDATE faculty_profiles
                   SET name = ?, designation = ?, description = ?, expertise = ?, photo_path = ?, updated_at = ?
                   WHERE id = ?""",
                (name, designation, description, expertise, photo_path, now_iso, faculty_id),
            )
        else:
            conn.execute(
                """UPDATE faculty_profiles
                   SET name = ?, designation = ?, description = ?, expertise = ?, updated_at = ?
                   WHERE id = ?""",
                (name, designation, description, expertise, now_iso, faculty_id),
            )
        return True
