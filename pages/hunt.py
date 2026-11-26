"""
pages/hunt.py — The main treasure hunt game page.
Handles all 10 rounds, timer, scoring, and progression.
"""
from __future__ import annotations

import streamlit as st
from datetime import datetime, timezone

from components.ui import (
    cyber_header, countdown_timer_js, render_round_grid,
    render_fragments, difficulty_badge, score_display
)
from database import db
from game.puzzles import get_round, generate_treasure_code, validate_answer


MAX_ATTEMPTS = 3
HINT_PENALTY = 5
POINTS_PER_QUESTION = 10


def _get_session_state() -> tuple:
    """Return (team, session) or (None, None) if unavailable."""
    tc = st.session_state.get("team_code")
    if not tc:
        return None, None
    team = db.get_team(tc)
    if not team:
        return None, None
    session = db.get_session(tc)
    if not session:
        session = db.get_or_create_session(tc)
    if session:
        session = db.expire_session_if_needed(session)
    return team, session


def _attempt_key(round_num: int, q_idx: int) -> str:
    return f"attempt_q_{round_num}_{q_idx}"


def _hint_key(round_num: int, q_idx: int) -> str:
    return f"hint_shown_{round_num}_{q_idx}"


def render():
    team, session = _get_session_state()
    if not team or not session:
        st.error("Could not load your game session. Please register or resume.")
        if st.button("Go to Registration"):
            st.session_state.page = "register"
            st.rerun()
        return

    tc = team["team_code"]
    team_name = team["team_name"]
    seed = session["puzzle_seed"]
    status = session.get("status", "active")

    # ── Handle expired / completed ────────────────────────────────────────────
    if status in ("expired", "completed"):
        st.session_state.page = "results"
        st.rerun()
        return

    deadline_iso = session.get("deadline", "")

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:rgba(0,212,255,0.04); border-bottom:1px solid rgba(0,212,255,0.2);
                padding:20px 24px; margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <div style="font-family:'Orbitron',monospace; font-size:1.2rem; color:#00d4ff; font-weight:700;">
                    🔐 THE LOST ALGORITHM
                </div>
                <div style="font-family:'Share Tech Mono',monospace; color:#8899bb; font-size:0.8rem;">
                    Team: <span style="color:#00ffea;">{team_name}</span> &nbsp;|&nbsp; Code: <span style="color:#00ffea;">{tc}</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Layout ────────────────────────────────────────────────────────────────
    col_main, col_side = st.columns([3, 1])

    with col_side:
        # Timer
        st.markdown("""
        <div style="font-family:'Orbitron',monospace; font-size:0.65rem; color:#8899bb; letter-spacing:3px; text-align:center; margin-bottom:5px;">
            TIME REMAINING
        </div>
        """, unsafe_allow_html=True)
        if deadline_iso:
            countdown_timer_js(deadline_iso)

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # Score
        score_display(session.get("total_score", 0))

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # Round progress
        completed_round_nums = db.get_completed_round_numbers(tc)
        current_round = session.get("current_round", 1)

        st.markdown("""
        <div style="font-family:'Orbitron',monospace; font-size:0.65rem; color:#8899bb; letter-spacing:3px; text-align:center; margin-bottom:8px;">
            ROUND PROGRESS
        </div>
        """, unsafe_allow_html=True)
        render_round_grid(completed_round_nums, current_round)

        # Fragments
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        completed_rounds_data = db.get_completed_rounds(tc)
        render_fragments(completed_rounds_data)

        # Stats
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        correct = session.get("correct_answers", 0)
        hints = session.get("hints_used", 0)
        rounds_done = len(completed_round_nums)
        st.markdown(f"""
        <div class="cyber-card" style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; padding:12px;">
            <div style="color:#8899bb; display:flex; justify-content:space-between; margin-bottom:4px;">
                <span>Correct Answers</span><span style="color:#00ff88;">{correct}/30</span>
            </div>
            <div style="color:#8899bb; display:flex; justify-content:space-between; margin-bottom:4px;">
                <span>Rounds Done</span><span style="color:#00d4ff;">{rounds_done}/10</span>
            </div>
            <div style="color:#8899bb; display:flex; justify-content:space-between;">
                <span>Hints Used</span><span style="color:#ff2d9b;">{hints}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Leaderboard shortcut
        if st.button("🏆 View Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()

    with col_main:
        # ── Round selection ───────────────────────────────────────────────────
        # Reload completed rounds
        completed_round_nums = db.get_completed_round_numbers(tc)
        current_round = session.get("current_round", 1)

        # Allow navigating completed rounds
        nav_round = st.session_state.get("nav_round", current_round)

        # Clamp nav_round
        max_accessible = current_round  # only current and completed
        if nav_round > max_accessible:
            nav_round = max_accessible
            st.session_state.nav_round = nav_round

        if nav_round < 1:
            nav_round = 1

        # Round navigation buttons (completed + current)
        accessible = sorted(completed_round_nums | {current_round})
        if len(accessible) > 1:
            nav_cols = st.columns(min(len(accessible), 10))
            for i, rn in enumerate(accessible):
                with nav_cols[i]:
                    icon = "✅" if rn in completed_round_nums else "▶"
                    btn_type = "primary" if rn == nav_round else "secondary"
                    if st.button(f"{icon} R{rn}", key=f"nav_r_{rn}", type=btn_type, use_container_width=True):
                        st.session_state.nav_round = rn
                        st.rerun()

        display_round = nav_round

        # ── Render the round ──────────────────────────────────────────────────
        _render_round(tc, session, seed, display_round, completed_round_nums, current_round)


def _render_round(tc: str, session: dict, seed: int, round_num: int, completed_rounds: set[int], current_round: int):
    """Render a single round's questions."""
    round_data = get_round(round_num, seed)
    is_completed = round_num in completed_rounds
    is_active = round_num == current_round

    # Round header
    icon = round_data.get("icon", "🔐")
    name = round_data["name"]
    desc = round_data["description"]

    status_badge = ""
    if is_completed:
        status_badge = '<span style="color:#00ff88; font-size:0.75rem; letter-spacing:2px;">✅ COMPLETED</span>'
    elif is_active:
        status_badge = '<span style="color:#00ffea; font-size:0.75rem; letter-spacing:2px; animation: glowPulse 2s infinite;">▶ ACTIVE</span>'

    st.markdown(f"""
    <div class="cyber-card" style="margin-bottom:20px;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
            <div>
                <div style="font-family:'Share Tech Mono',monospace; color:#445; font-size:0.7rem; letter-spacing:3px;">ROUND {round_num} OF 10</div>
                <div style="font-family:'Orbitron',monospace; font-size:1.3rem; color:#00d4ff; font-weight:700; margin:4px 0;">
                    {icon} {name}
                </div>
                <div style="color:#8899bb; font-size:0.9rem;">{desc}</div>
            </div>
            <div>{status_badge}</div>
        </div>
        <div style="margin-top:12px;">
            <div style="background:rgba(0,212,255,0.1); border-radius:4px; height:4px;">
                <div style="background:linear-gradient(90deg,#00d4ff,#7b2fff); border-radius:4px;
                             width:{_round_progress(tc, round_num)}%;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Render each question ──────────────────────────────────────────────────
    questions = round_data["questions"]
    all_solved = True

    for q in questions:
        q_idx = q["index"]
        solved = db.is_question_solved(tc, round_num, q_idx)
        if not solved:
            all_solved = False

        _render_question(tc, session, seed, round_num, q, solved, is_active, is_completed, questions)

    # ── Auto-complete the round if all questions solved ───────────────────────
    if all_solved and not is_completed and is_active:
        round_score = _calculate_round_score(tc, round_num)
        fragment = round_data["fragment"]
        db.complete_round(tc, session["id"], round_num, round_score, fragment)
        db.upsert_leaderboard(tc, get_team_name_safe(tc), db.get_session(tc) or session)

        st.balloons()

        if round_num == 10:
            # Generate treasure code and finalise
            treasure_code = generate_treasure_code(tc, seed)
            db.finalise_game(tc, treasure_code)
            st.success("🏆 VAULT UNLOCKED! You have completed all 10 rounds!")
            if st.button("🎯 VIEW FINAL RESULTS", type="primary"):
                st.session_state.page = "results"
                st.rerun()
        else:
            st.success(f"✅ Round {round_num} complete! Fragment earned: **{fragment}**")
            st.info(f"Round {round_num + 1} is now unlocked!")
            if st.button(f"▶ START ROUND {round_num + 1}", type="primary"):
                st.session_state.nav_round = round_num + 1
                st.rerun()


def _render_question(tc: str, session: dict, seed: int, round_num: int,
                     q: dict, solved: bool, is_active: bool, is_completed: bool,
                     all_questions: list):
    """Render a single question card."""
    q_idx = q["index"]
    attempts = db.get_question_attempts(tc, round_num, q_idx)
    attempt_count = len(attempts)
    hint_key = _hint_key(round_num, q_idx)
    max_attempts = MAX_ATTEMPTS

    card_class = "solved" if solved else ""
    lock_icon = "✅" if solved else ("🔒" if not is_active else "")

    st.markdown(f"""
    <div class="question-card {card_class}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <div style="font-family:'Orbitron',monospace; font-size:0.7rem; color:#445; letter-spacing:3px;">
                QUESTION {q_idx + 1} &nbsp; {difficulty_badge(q['difficulty'])}
            </div>
            <div>{lock_icon} &nbsp;
                <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#8899bb;">
                    {'✅ SOLVED · ' + str(next((a['points_awarded'] for a in attempts if a['is_correct']), 0)) + ' pts' if solved else
                     f'Attempts: {attempt_count}/{max_attempts}'}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander(
        f"{'✅' if solved else '❓'} Question {q_idx + 1}: {q['difficulty']}",
        expanded=not solved and is_active
    ):
        # Question text (uses markdown)
        st.markdown(q["text"])

        if solved:
            st.success("✅ Question solved!")
            # Show answer after solving
            st.markdown(f"**Answer:** `{q['answer_display']}`")
            return

        if not is_active:
            if is_completed:
                st.info("Round completed. The answer was: `" + q["answer_display"] + "`")
            else:
                st.warning("🔒 This round is not yet accessible.")
            return

        # Attempts exhausted
        if attempt_count >= max_attempts:
            st.error(f"❌ Maximum attempts ({max_attempts}) reached for this question.")
            st.markdown(f"**Correct Answer:** `{q['answer_display']}`")
            return

        # ── Answer form ───────────────────────────────────────────────────────
        col_ans, col_btn = st.columns([4, 1])
        with col_ans:
            user_answer = st.text_input(
                "Your answer",
                key=f"ans_{round_num}_{q_idx}",
                placeholder="Type your answer here...",
                label_visibility="collapsed"
            )
        with col_btn:
            submit_btn = st.button("Submit", key=f"sub_{round_num}_{q_idx}", type="primary")

        # ── Hint section ──────────────────────────────────────────────────────
        col_hint, col_penalty = st.columns([3, 2])
        with col_hint:
            show_hint = st.button(
                f"💡 Show Hint (-{HINT_PENALTY} pts)",
                key=f"hint_{round_num}_{q_idx}",
                help=f"Using a hint costs {HINT_PENALTY} points from this question's value."
            )
        with col_penalty:
            if st.session_state.get(hint_key):
                st.markdown(f'<div style="color:orange; font-size:0.8rem; padding:8px;">💡 {q["hint"]}</div>',
                            unsafe_allow_html=True)

        if show_hint and not st.session_state.get(hint_key):
            st.session_state[hint_key] = True
            # Apply hint penalty to session score
            current_session = db.get_session(tc)
            if current_session:
                new_score = max(0, current_session["total_score"] - HINT_PENALTY)
                db.update_session(tc, {
                    "total_score": new_score,
                    "hints_used": current_session["hints_used"] + 1
                })
            st.markdown(f'<div style="color:orange; font-size:0.8rem; padding:8px;">💡 {q["hint"]}</div>',
                        unsafe_allow_html=True)

        # ── Previous attempts ─────────────────────────────────────────────────
        if attempts:
            wrong_attempts = [a for a in attempts if not a["is_correct"]]
            if wrong_attempts:
                attempt_strs = []
                for a in wrong_attempts[-3:]:  # show last 3
                    attempt_strs.append(f'`{a["submitted_answer"][:30]}` — ❌')
                st.markdown(
                    "<div style='font-size:0.8rem; color:#8899bb; margin-top:8px;'>"
                    "Previous attempts: " + " | ".join(attempt_strs) + "</div>",
                    unsafe_allow_html=True
                )

        # ── Submission handler ────────────────────────────────────────────────
        if submit_btn:
            if not user_answer.strip():
                st.warning("Please enter an answer before submitting.")
            else:
                hint_used = bool(st.session_state.get(hint_key))
                is_correct = validate_answer(round_num, q_idx, user_answer, seed)

                # Points calculation
                if is_correct:
                    # Deduct penalty for each wrong attempt
                    penalty_per_wrong = 2
                    wrong_count = sum(1 for a in attempts if not a["is_correct"])
                    points = max(1, POINTS_PER_QUESTION - (wrong_count * penalty_per_wrong))
                    if hint_used:
                        points = max(1, points - HINT_PENALTY)
                else:
                    points = 0

                result = db.record_attempt(
                    team_code=tc,
                    session_id=session["id"],
                    round_number=round_num,
                    question_index=q_idx,
                    submitted_answer=user_answer.strip(),
                    is_correct=is_correct,
                    points_awarded=points,
                    hint_used=hint_used,
                )

                if result.get("already_solved"):
                    st.info("This question was already answered correctly.")
                elif is_correct:
                    st.success(f"✅ Correct! +{points} points")
                    st.rerun()
                else:
                    remaining = max_attempts - attempt_count - 1
                    if remaining > 0:
                        st.error(f"❌ Incorrect. {remaining} attempt(s) remaining.")
                    else:
                        st.error(f"❌ No more attempts. Answer: `{q['answer_display']}`")
                    st.rerun()


def _round_progress(tc: str, round_num: int) -> int:
    """Calculate round completion percentage (0-100)."""
    solved = sum(1 for i in range(3) if db.is_question_solved(tc, round_num, i))
    return int(solved / 3 * 100)


def _calculate_round_score(tc: str, round_num: int) -> int:
    """Sum all points awarded in this round."""
    attempts = db.get_round_attempts(tc, round_num)
    return sum(a["points_awarded"] for a in attempts if a["is_correct"])


def get_team_name_safe(tc: str) -> str:
    team = db.get_team(tc)
    return team["team_name"] if team else tc

