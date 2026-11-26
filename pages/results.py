"""
pages/results.py — Final results and treasure vault page.
"""
from __future__ import annotations

import streamlit as st
from datetime import datetime, timezone

from components.ui import cyber_header, render_leaderboard
from database import db


def _fmt_time(seconds: int | None) -> str:
    if seconds is None:
        return "—"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s"


def _accuracy(correct: int) -> str:
    return f"{(correct / 30 * 100):.1f}%"


def render():
    tc = st.session_state.get("team_code")

    if not tc:
        st.warning("No active session. Please register or resume your game.")
        if st.button("Go to Registration"):
            st.session_state.page = "register"
            st.rerun()
        return

    team = db.get_team(tc)
    session = db.get_session(tc)

    if not team or not session:
        st.error("Could not load your results. Please check your team code.")
        return

    status = session.get("status", "active")

    # ── Still active — go back to hunt ───────────────────────────────────────
    if status == "active":
        st.info("Your game is still active!")
        if st.button("▶ Return to Hunt"):
            st.session_state.page = "hunt"
            st.rerun()
        return

    # ── Calculate timing ──────────────────────────────────────────────────────
    started_at = session.get("started_at", "")
    completed_at = session.get("completed_at") or session.get("deadline", "")

    completion_secs = None
    time_remaining_secs = None

    if started_at and completed_at:
        try:
            start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            end = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
            completion_secs = max(0, int((end - start).total_seconds()))

            deadline = datetime.fromisoformat(session["deadline"].replace("Z", "+00:00"))
            time_remaining_secs = max(0, int((deadline - end).total_seconds()))
        except Exception:
            pass

    total_score = session.get("total_score", 0)
    correct_answers = session.get("correct_answers", 0)
    hints_used = session.get("hints_used", 0)
    completed_round_nums = db.get_completed_round_numbers(tc)
    rounds_completed = len(completed_round_nums)
    treasure_code = session.get("treasure_code", "???")
    rank = db.get_team_rank(tc)

    # ── Page header ───────────────────────────────────────────────────────────
    if status == "completed":
        st.markdown("""
        <div class="vault-container">
            <div class="vault-icon">🏆</div>
            <div class="hero-title">VAULT UNLOCKED!</div>
            <div class="hero-subtitle">◈ THE LOST ALGORITHM HAS BEEN FOUND ◈</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="vault-container">
            <div style="font-size:4rem;">⌛</div>
            <div class="hero-title" style="color:#ff2d9b !important;">TIME EXPIRED</div>
            <div class="hero-subtitle">◈ YOUR SESSION HAS ENDED ◈</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Team info ─────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center; padding:10px 0 20px;">
        <span style="font-family:'Share Tech Mono',monospace; color:#8899bb;">Team: </span>
        <span style="font-family:'Orbitron',monospace; color:#00ffea; font-size:1.2rem;">{team['team_name']}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Treasure code (only if completed) ────────────────────────────────────
    if status == "completed" and treasure_code and treasure_code != "???":
        st.markdown("""
        <div style="text-align:center; margin:10px 0 20px;">
            <div style="font-family:'Orbitron',monospace; font-size:0.75rem; color:#8899bb; letter-spacing:3px; margin-bottom:8px;">
                TREASURE CODE
            </div>
        </div>
        """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f'<div class="treasure-code">{treasure_code}</div>', unsafe_allow_html=True)

    # ── Score grid ────────────────────────────────────────────────────────────
    cyber_header("FINAL RESULTS", f"Team: {team['team_name']}")

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        (col1, "FINAL SCORE", f"{total_score} / 300", "#00d4ff"),
        (col2, "ACCURACY", _accuracy(correct_answers), "#00ff88" if correct_answers > 20 else "#ff2d9b"),
        (col3, "RANK", f"#{rank}" if rank else "—", "gold"),
        (col4, "COMPLETION TIME", _fmt_time(completion_secs), "#7b2fff"),
    ]

    for col, label, value, color in metrics:
        with col:
            st.markdown(f"""
            <div class="cyber-card" style="text-align:center; padding:20px 10px;">
                <div style="font-family:'Orbitron',monospace; font-size:0.65rem; color:#8899bb; letter-spacing:2px;">{label}</div>
                <div style="font-family:'Orbitron',monospace; font-size:1.6rem; color:{color}; font-weight:900; margin-top:8px;">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    metrics2 = [
        (col5, "CORRECT ANSWERS", f"{correct_answers} / 30", "#00ff88"),
        (col6, "ROUNDS COMPLETED", f"{rounds_completed} / 10", "#00d4ff"),
        (col7, "HINTS USED", str(hints_used), "#ff2d9b"),
        (col8, "TIME REMAINING", _fmt_time(time_remaining_secs), "#00ffea" if status == "completed" else "#445"),
    ]

    for col, label, value, color in metrics2:
        with col:
            st.markdown(f"""
            <div class="cyber-card" style="text-align:center; padding:20px 10px;">
                <div style="font-family:'Orbitron',monospace; font-size:0.65rem; color:#8899bb; letter-spacing:2px;">{label}</div>
                <div style="font-family:'Orbitron',monospace; font-size:1.6rem; color:{color}; font-weight:900; margin-top:8px;">{value}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Round-by-round breakdown ──────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("ROUND BREAKDOWN", "Score per round")

    completed_rounds_data = db.get_completed_rounds(tc)
    round_scores = {r["round_number"]: r["round_score"] for r in completed_rounds_data}
    round_fragments = {r["round_number"]: r.get("fragment", "—") for r in completed_rounds_data}

    round_names = [
        "Cipher Breaker", "The Five Houses", "Sound of Secrets", "Vibe Coding",
        "Triangle of Logic", "The Bug Hunter", "The Network Maze",
        "The Memory Palace", "The Final Protocol", "The Treasure Vault"
    ]

    cols = st.columns(5)
    for i, rnum in enumerate(range(1, 11)):
        with cols[i % 5]:
            done = rnum in completed_round_nums
            score = round_scores.get(rnum, 0)
            frag = round_fragments.get(rnum, "—")
            color = "#00ff88" if done else "#445"
            icon = "✅" if done else ("⌛" if status == "expired" else "🔒")

            st.markdown(f"""
            <div class="cyber-card" style="text-align:center; padding:14px 8px; margin-bottom:8px;">
                <div style="font-size:1.2rem;">{icon}</div>
                <div style="font-family:'Orbitron',monospace; font-size:0.6rem; color:#8899bb; letter-spacing:1px;">ROUND {rnum}</div>
                <div style="font-size:0.7rem; color:#8899bb; margin:4px 0;">{round_names[i]}</div>
                <div style="font-family:'Orbitron',monospace; font-size:1.1rem; color:{color}; font-weight:700;">
                    {score} pts
                </div>
                {f'<div style="font-size:0.65rem; color:#7b2fff; margin-top:4px;">{frag}</div>' if done else ''}
            </div>
            """, unsafe_allow_html=True)

    # ── Leaderboard preview ───────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("LIVE LEADERBOARD", "Your standing among all teams")

    lb_data = db.get_leaderboard(limit=10)
    render_leaderboard(lb_data, my_team_name=team["team_name"])

    # ── Actions ───────────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🏆 Full Leaderboard", use_container_width=True):
            st.session_state.page = "leaderboard"
            st.rerun()
    with col_b:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col_c:
        if status == "active":
            if st.button("▶ Return to Hunt", use_container_width=True, type="primary"):
                st.session_state.page = "hunt"
                st.rerun()

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

