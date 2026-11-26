
"""
pages/organizer.py — Protected organizer dashboard.
Manages teams, game sessions, event settings, leaderboard,
student team coordinators, and faculty profiles.
"""

from __future__ import annotations

import os
import re
import time
import pandas as pd
import streamlit as st
from datetime import datetime, timezone

from components.ui import cyber_header
from database import db


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

def _get_organizer_password() -> str:
    """Retrieve organizer password from secrets, env, or local default."""
    try:
        return st.secrets.get("organizer", {}).get("password", "admin123")
    except Exception:
        return os.environ.get("ORGANIZER_PASSWORD", "admin123")


def _check_auth() -> bool:
    if st.session_state.get("organizer_authenticated"):
        return True

    st.markdown("""
    <div class="hero-container" style="padding:30px 20px 20px;">
        <div class="hero-title" style="font-size:2rem;">
            ORGANIZER DASHBOARD
        </div>
        <div class="hero-subtitle">◈ RESTRICTED ACCESS ◈</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div class="cyber-card" style="text-align:center; padding:30px;">
            <div style="font-size:3rem; margin-bottom:10px;">🔐</div>
            <div style="font-family:'Orbitron',monospace; color:#00d4ff;
                        margin-bottom:10px; letter-spacing:2px;">
                ORGANIZER AUTHENTICATION
            </div>
            <div style="color:#8899bb; font-size:0.8rem;
                        margin-bottom:18px;">
                Enter organizer password
                (Default for local testing: <code>admin123</code>)
            </div>
        </div>
        """, unsafe_allow_html=True)

        password = st.text_input(
            "Password",
            type="password",
            key="org_password_input"
        )

        if st.button(
            "🔓 Authenticate",
            type="primary",
            use_container_width=True
        ):
            correct = _get_organizer_password()

            if password == correct:
                st.session_state.organizer_authenticated = True
                st.success("Authenticated successfully!")
                st.rerun()
            else:
                st.error("❌ Incorrect password.")

    return False


# ═══════════════════════════════════════════════════════════════════════════════
# PHOTO HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _resolve_photo_path(path_str: str | None) -> str | None:
    """Resolve photo path to an existing absolute or relative path."""
    if not path_str:
        return None

    if os.path.isabs(path_str) and os.path.exists(path_str):
        return path_str

    candidate = os.path.join(db.BASE_DIR, path_str)

    if os.path.exists(candidate):
        return candidate

    if os.path.exists(path_str):
        return path_str

    return None


def _save_uploaded_photo(
    uploaded_file,
    prefix: str = "member",
    target_dir: str | None = None
) -> str:
    """Save an uploaded image and return its relative path."""
    if not uploaded_file:
        return ""

    if target_dir is None:
        target_dir = (
            db.FACULTY_ASSETS_DIR
            if prefix.startswith("faculty")
            else db.TEAM_ASSETS_DIR
        )

    os.makedirs(target_dir, exist_ok=True)

    ext = os.path.splitext(uploaded_file.name)[1].lower()

    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
        ext = ".png"

    clean_name = re.sub(
        r"[^a-zA-Z0-9_]",
        "",
        os.path.splitext(uploaded_file.name)[0]
    )[:15]

    timestamp = int(time.time())

    filename = f"{prefix}_{timestamp}_{clean_name}{ext}"
    full_path = os.path.join(target_dir, filename)

    with open(full_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    rel_folder = (
        "faculty"
        if prefix.startswith("faculty")
        else "team"
    )

    return os.path.join("assets", rel_folder, filename)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORGANIZER DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render():

    if not _check_auth():
        return

    st.markdown("""
    <div class="hero-container" style="padding:20px;">
        <div class="hero-title" style="font-size:1.8rem;">
            ⚙ ORGANIZER DASHBOARD
        </div>
        <div class="hero-subtitle">◈ THE LOST ALGORITHM ◈</div>
    </div>
    """, unsafe_allow_html=True)

    tab_teams, tab_members, tab_faculty, tab_settings, tab_lb, tab_actions = st.tabs([
        "👥 Teams & Progress",
        "🎖️ Club Members",
        "👨‍🏫 Faculty Profiles",
        "⚙ Settings",
        "🏆 Leaderboard",
        "🛠 Actions",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. TEAMS & PROGRESS
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_teams:

        cyber_header(
            "REGISTERED TEAMS",
            "All teams with live game status stored in SQLite"
        )

        if st.button("🔄 Refresh Data", key="refresh_teams"):
            st.rerun()

        all_teams = db.get_all_teams_with_sessions()

        if not all_teams:
            st.info("No teams registered yet.")

        else:
            rows = []

            for t in all_teams:
                s = t.get("session") or {}

                rows.append({
                    "Team Name": t["team_name"],
                    "Captain": t["captain_name"],
                    "Team Code": t["team_code"],
                    "Registered": t.get(
                        "registered_at", ""
                    )[:19].replace("T", " "),
                    "Status": s.get("status", "not started"),
                    "Score": s.get("total_score", 0),
                    "Round": s.get("current_round", "—"),
                    "Correct": s.get("correct_answers", 0),
                    "Hints": s.get("hints_used", 0),
                })

            df = pd.DataFrame(rows)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 Export as CSV",
                data=csv,
                file_name="lost_algorithm_teams.csv",
                mime="text/csv",
                key="dl_teams_csv",
            )

            with st.expander("🔍 View Team Details"):

                team_names = [
                    t["team_name"] for t in all_teams
                ]

                selected = st.selectbox(
                    "Select team",
                    team_names,
                    key="sel_team_detail"
                )

                selected_team = next(
                    (
                        t for t in all_teams
                        if t["team_name"] == selected
                    ),
                    None
                )

                if selected_team:

                    tc = selected_team["team_code"]
                    s = selected_team.get("session") or {}

                    team_full = db.get_team(tc) or selected_team

                    col_a, col_b = st.columns(2)

                    with col_a:
                        st.markdown(f"""
                        **Team Code:** `{tc}`  
                        **Captain:** {selected_team['captain_name']}  
                        **Email:** {selected_team.get('captain_email', '—')}  
                        **College ID:** {selected_team.get('college_id', '—')}  
                        **Members:** {', '.join(team_full.get('member_names', []) or []) or '—'}  
                        **Participants:** {team_full.get('num_participants', '—')}
                        """)

                    with col_b:
                        st.markdown(f"""
                        **Status:** {s.get('status', 'not started')}  
                        **Score:** {s.get('total_score', 0)} / 300  
                        **Correct:** {s.get('correct_answers', 0)} / 30  
                        **Hints:** {s.get('hints_used', 0)}  
                        **Current Round:** {s.get('current_round', '—')}  
                        **Treasure Code:** `{s.get('treasure_code') or '—'}`
                        """)

                    completed = db.get_completed_round_numbers(tc)

                    st.markdown(
                        f"**Completed Rounds:** {sorted(completed) or 'None'}"
                    )

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. STUDENT TEAM COORDINATORS
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_members:

        cyber_header(
            "TEAM COORDINATORS",
            "Department of CSE - Student Team Members"
        )

        # Student team details.
        # Add each member's photo path in the photo_path field.

        team_members = [
            {
                "Sl No": 1,
                "Role": "President",
                "Name": "Mahima K",
                "USN": "1VA23CS092",
                "photo_path": "",
            },
            {
                "Sl No": 2,
                "Role": "Vice President",
                "Name": "Samyak D Karekar",
                "USN": "1VA24CS0121",
                "photo_path": "",
            },
            {
                "Sl No": 3,
                "Role": "Joint Secretary",
                "Name": "Shalini M Gowda",
                "USN": "1VA24CS125",
                "photo_path": "",
            },
            {
                "Sl No": 4,
                "Role": "Social Media",
                "Name": "Shankar SB",
                "USN": "1VA23CS145",
                "photo_path": "",
            },
            {
                "Sl No": 5,
                "Role": "Treasurer",
                "Name": "Aadita Nag",
                "USN": "1VA23CS001",
                "photo_path": "",
            },
            {
                "Sl No": 6,
                "Role": "Documentation Lead",
                "Name": "Kavyashree SN",
                "USN": "1VA24CS064",
                "photo_path": "",
            },
            {
                "Sl No": 7,
                "Role": "Membership Coordinator",
                "Name": "Harshitha N",
                "USN": "1VA24CS055",
                "photo_path": "",
            },
            {
                "Sl No": 8,
                "Role": "Membership Coordinator",
                "Name": "Suhail D Tamboli",
                "USN": "1VA23CS195",
                "photo_path": "",
            },
            {
                "Sl No": 9,
                "Role": "Secretary",
                "Name": "Jagadeesha",
                "USN": "1VA23CS065",
                "photo_path": "",
            },
        ]

        # Display the student coordinator table.

        team_df = pd.DataFrame([
            {
                "Sl No": member["Sl No"],
                "Role": member["Role"],
                "Name": member["Name"],
                "USN": member["USN"],
            }
            for member in team_members
        ])

        st.dataframe(
            team_df,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")

        st.subheader("Student Team Profiles")

        # Display student profiles in rows of three.

        for start in range(0, len(team_members), 3):

            cols = st.columns(3)

            for col, member in zip(
                cols,
                team_members[start:start + 3]
            ):

                with col:

                    with st.container(border=True):

                        photo_path = member["photo_path"]

                        if photo_path:

                            resolved_photo = _resolve_photo_path(
                                photo_path
                            )

                            if resolved_photo:
                                st.image(
                                    resolved_photo,
                                    use_container_width=True
                                )
                            else:
                                st.caption(
                                    f"Photo not found: {photo_path}"
                                )

                        else:
                            st.caption(
                                "Add photo path here."
                            )

                        st.markdown(
                            f"### {member['Name']}"
                        )

                        st.write(member["Role"])

                        st.caption(
                            f"USN: {member['USN']}"
                        )

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DEPARTMENT OF CSE FACULTY
    # ═══════════════════════════════════════════════════════════════════════════

    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DEPARTMENT OF CSE FACULTY
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_faculty:

        cyber_header(
            "FACULTY COORDINATORS",
            "Department of Computer Science & Engineering"
        )

        faculty_members = [
            {
                "name": "Dr. Varun E",
                "designation": "Associate Professor",
                "photo_path": "assets/faculty/varun.png",
            },
            {
                "name": "Prof Ramanjinamma G",
                "designation": "Assistant Professor",
                "photo_path": "assets/faculty/rama.png",
            },
            {
                "name": "Prof Lalitha K",
                "designation": "Assistant Professor",
                "photo_path": "assets/faculty/lalitha.png",
            },
        ]

        # Display faculty cards
        cols = st.columns(3)

        for col, faculty in zip(cols, faculty_members):

            with col:

                with st.container(border=True):

                    photo_path = faculty["photo_path"]
                    resolved_photo = _resolve_photo_path(photo_path)

                    if resolved_photo:

                        st.image(
                            resolved_photo,
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            f"Photo not found: {photo_path}"
                        )

                    st.markdown(
                        f"### {faculty['name']}"
                    )

                    st.write(
                        faculty["designation"]
                    )


    # ═══════════════════════════════════════════════════════════════════════════
    # 4. EVENT SETTINGS
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_settings:

        cyber_header(
            "EVENT SETTINGS",
            "Configure scoring and game rules (saved in SQLite)"
        )

        col_s1, col_s2 = st.columns(2)

        with col_s1:

            current_duration = db.get_event_setting(
                "duration_minutes", "60"
            )

            new_duration = st.number_input(
                "Game Duration (minutes)",
                min_value=10,
                max_value=180,
                value=int(current_duration),
                step=5
            )

            if st.button("Save Duration"):

                if db.set_event_setting(
                    "duration_minutes",
                    str(new_duration)
                ):
                    st.success("Duration updated in database.")

        with col_s2:

            current_attempts = db.get_event_setting(
                "max_attempts", "3"
            )

            new_attempts = st.number_input(
                "Max Attempts Per Question",
                min_value=1,
                max_value=10,
                value=int(current_attempts)
            )

            if st.button("Save Attempts"):

                if db.set_event_setting(
                    "max_attempts",
                    str(new_attempts)
                ):
                    st.success("Attempts limit updated.")

        col_s3, col_s4 = st.columns(2)

        with col_s3:

            current_penalty = db.get_event_setting(
                "hint_penalty", "5"
            )

            new_penalty = st.number_input(
                "Hint Penalty (points)",
                min_value=0,
                max_value=10,
                value=int(current_penalty)
            )

            if st.button("Save Hint Penalty"):

                if db.set_event_setting(
                    "hint_penalty",
                    str(new_penalty)
                ):
                    st.success("Hint penalty updated.")

        with col_s4:

            speed_bonus = db.get_event_setting(
                "speed_bonus_enabled", "true"
            )

            new_speed = st.toggle(
                "Enable Speed Bonus",
                value=(speed_bonus == "true")
            )

            if st.button("Save Speed Bonus"):

                if db.set_event_setting(
                    "speed_bonus_enabled",
                    "true" if new_speed else "false"
                ):
                    st.success("Speed bonus setting updated.")

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. LEADERBOARD VIEW
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_lb:

        cyber_header(
            "FULL LEADERBOARD",
            "All teams ranked from SQLite database"
        )

        if st.button("🔄 Refresh Leaderboard", key="refresh_lb"):
            st.rerun()

        lb = db.get_leaderboard(limit=100)

        if lb:

            lb_rows = []

            for row in lb:

                t_secs = row.get("completion_time_seconds")

                t_str = (
                    f"{t_secs // 60}m {t_secs % 60:02d}s"
                    if t_secs
                    else "—"
                )

                lb_rows.append({
                    "Rank": row.get("rank"),
                    "Team": row.get("team_name"),
                    "Score": row.get("final_score"),
                    "Correct": row.get("correct_answers"),
                    "Rounds": row.get("rounds_completed"),
                    "Hints": row.get("hints_used"),
                    "Time": t_str,
                    "Status": row.get("status"),
                })

            df_lb = pd.DataFrame(lb_rows)

            st.dataframe(
                df_lb,
                use_container_width=True,
                hide_index=True
            )

            csv_lb = df_lb.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 Export Leaderboard CSV",
                data=csv_lb,
                file_name="leaderboard.csv",
                mime="text/csv",
                key="dl_lb_csv"
            )

        else:
            st.info("No leaderboard data yet.")

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. ACTIONS & DATABASE INFO
    # ═══════════════════════════════════════════════════════════════════════════

    with tab_actions:

        cyber_header(
            "ADMIN ACTIONS",
            "Manage SQLite database and active sessions"
        )

        st.markdown(
            f"**Database File:** `{db.DB_PATH}`"
        )

        st.markdown(
            f"**Team Photos Directory:** `{db.TEAM_ASSETS_DIR}`"
        )

        with st.expander("🔄 Reset Team Game"):

            all_teams_basic = db.get_all_teams_with_sessions()

            team_opts = [
                t["team_name"] for t in all_teams_basic
            ]

            if team_opts:

                to_reset = st.selectbox(
                    "Team to reset",
                    team_opts,
                    key="reset_team_sel"
                )

                reset_team = next(
                    (
                        t for t in all_teams_basic
                        if t["team_name"] == to_reset
                    ),
                    None
                )

                if reset_team:

                    st.markdown(
                        f"This will delete all game sessions and "
                        f"attempts for **{to_reset}** "
                        f"(`{reset_team['team_code']}`)."
                    )

                    if st.button(
                        "⚠ Confirm Reset",
                        type="primary",
                        key="confirm_reset"
                    ):

                        ok = db.reset_team_game(
                            reset_team["team_code"]
                        )

                        if ok:
                            st.success(
                                f"Game reset for {to_reset}."
                            )
                            st.rerun()
                        else:
                            st.error("Reset failed.")

            else:
                st.info("No teams to reset.")

        st.markdown(
            "<div style='height:20px'></div>",
            unsafe_allow_html=True
        )

        if st.button("🚪 Logout", key="org_logout"):

            st.session_state.organizer_authenticated = False
            st.session_state.page = "home"

            st.rerun()
