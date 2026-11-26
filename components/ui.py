
"""
components/ui.py — Reusable UI helpers and CSS injection for The Lost Algorithm.
"""

from __future__ import annotations

import os
import textwrap
import html

import streamlit as st
from datetime import datetime, timezone


# ═══════════════════════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════════════════════

def load_css() -> None:
    """Inject global CSS into the Streamlit app."""
    css_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "css",
        "style.css",
    )

    css = ""

    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read().strip()
        except Exception:
            css = ""

    if css:
        st.markdown(
            f"<style>\n{css}\n</style>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# HERO SECTION
# ═══════════════════════════════════════════════════════════════════════════════

def hero_section() -> None:
    """Render the hero section on the home page."""

    html_content = textwrap.dedent("""
    <div class="hero-container">
        <div class="hero-title">THE LOST ALGORITHM</div>
        <div class="hero-subtitle">◈ CSE CODING CLUB TREASURE HUNT ◈</div>
        <div class="hero-tagline">
            Ten rounds. Thirty challenges. One hidden treasure.
        </div>
    </div>
    """).strip()

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CYBER HEADER
# ═══════════════════════════════════════════════════════════════════════════════

def cyber_header(title: str, subtitle: str = "") -> None:
    """Render a section header."""

    safe_title = html.escape(str(title))
    safe_subtitle = html.escape(str(subtitle))

    sub_html = (
        f'<p style="color:#8899bb; font-family:monospace; '
        f'letter-spacing:1px; margin:0;">{safe_subtitle}</p>'
        if subtitle
        else ""
    )

    html_content = textwrap.dedent(f"""
    <div style="margin:1.5rem 0 1rem;">
        <h2 style="font-family:'Orbitron',monospace;
                   color:#00d4ff; letter-spacing:3px; margin:0;">
            {safe_title}
        </h2>
        {sub_html}
        <div class="cyber-divider" style="margin-top:10px;"></div>
    </div>
    """).strip()

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# GLASS CARD
# ═══════════════════════════════════════════════════════════════════════════════

def card(content: str, extra_class: str = "") -> None:
    """Render a glass card."""

    html_content = (
        f'<div class="cyber-card {html.escape(extra_class)}">'
        f'{content}</div>'
    )

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FACULTY COORDINATOR CARDS
# ═══════════════════════════════════════════════════════════════════════════════

def _resolve_image_path(path: str | None) -> str | None:
    """Resolve an image path relative to the project root."""

    if not path:
        return None

    if os.path.isabs(path) and os.path.exists(path):
        return path

    # Resolve relative paths from the project root.
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )

    candidate = os.path.join(project_root, path)

    if os.path.exists(candidate):
        return candidate

    # Also support paths relative to the current working directory.
    if os.path.exists(path):
        return path

    return None


def render_faculty_cards(faculty_members: list[dict]) -> None:
    """
    Display faculty members in responsive Streamlit cards.

    Each faculty dictionary should contain:
        name
        designation
        photo_path

    Example:
        {
            "name": "Dr. Varun E",
            "designation": "Associate Professor",
            "photo_path": "assets/faculty/dr_varun_e.jpg",
        }
    """

    if not faculty_members:
        st.info("No faculty members found.")
        return

    for start in range(0, len(faculty_members), 3):

        cols = st.columns(3)

        for col, faculty in zip(
            cols,
            faculty_members[start:start + 3],
        ):

            with col:

                with st.container(border=True):

                    photo_path = faculty.get("photo_path", "")
                    name = faculty.get("name", "Faculty Member")
                    designation = faculty.get("designation", "")

                    # Display the faculty photo.
                    resolved_photo = _resolve_image_path(photo_path)

                    if resolved_photo:

                        st.image(
                            resolved_photo,
                            use_container_width=True,
                        )

                    else:

                        st.markdown(
                            """
                            <div style="
                                display:flex;
                                justify-content:center;
                                align-items:center;
                                height:160px;
                                background:#0b1224;
                                border-radius:12px;
                                font-size:60px;
                            ">
                                👨‍🏫
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # Display name and designation.
                    st.markdown(
                        f"### {html.escape(str(name))}"
                    )

                    st.write(
                        html.escape(str(designation))
                    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCORE DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def score_display(score: int, max_score: int = 300) -> None:
    """Display the current score."""

    html_content = textwrap.dedent(f"""
    <div style="text-align:center; padding:10px;">
        <div style="font-family:'Share Tech Mono',monospace;
                    color:#8899bb; font-size:0.75rem;
                    letter-spacing:2px;">
            CURRENT SCORE
        </div>
        <div class="score-badge">{score} / {max_score}</div>
    </div>
    """).strip()

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE WARNING
# ═══════════════════════════════════════════════════════════════════════════════

def db_unavailable_warning() -> None:
    """Show a warning if database access fails."""

    html_content = textwrap.dedent("""
    <div style="background:rgba(255,165,0,0.1);
                border:2px solid orange;
                border-radius:10px;
                padding:20px;
                margin:20px 0;">
        <h3 style="color:orange; font-family:'Orbitron',monospace;">
            ⚠ DATABASE INITIALIZATION ISSUE
        </h3>
        <p style="color:#e0e0ff;">
            Could not write or read from local SQLite file
            <code>treasure_hunt.db</code>.
        </p>
    </div>
    """).strip()

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# COUNTDOWN TIMER
# ═══════════════════════════════════════════════════════════════════════════════

def countdown_timer_js(deadline_iso: str) -> None:
    """Render a lightweight JavaScript countdown timer."""

    js_code = textwrap.dedent(f"""
    <div id="timer-display" class="timer-display">--:--</div>

    <script>
    (function() {{

        const deadline = new Date("{deadline_iso}");

        function updateTimer() {{

            const now = new Date();

            const diff = Math.max(
                0,
                Math.floor((deadline - now) / 1000)
            );

            const mins = Math.floor(diff / 60)
                .toString()
                .padStart(2, '0');

            const secs = (diff % 60)
                .toString()
                .padStart(2, '0');

            const el = document.getElementById('timer-display');

            if (el) {{

                el.textContent = mins + ':' + secs;

                el.className =
                    'timer-display' +
                    (diff < 300 ? ' timer-warning' : '') +
                    (diff < 60 ? ' timer-critical' : '');
            }}

            if (diff <= 0) {{

                clearInterval(interval);

                setTimeout(
                    () => window.location.reload(),
                    1000
                );
            }}
        }}

        updateTimer();

        const interval = setInterval(updateTimer, 1000);

    }})();
    </script>
    """).strip()

    st.components.v1.html(
        js_code,
        height=80,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND GRID
# ═══════════════════════════════════════════════════════════════════════════════

def render_round_grid(
    completed: set[int],
    current: int,
) -> None:
    """Render the 10-round progress grid."""

    cols = st.columns(5)

    for i, round_num in enumerate(range(1, 11)):

        col = cols[i % 5]

        with col:

            if round_num in completed:
                state = "completed"
                icon = "✅"

            elif round_num == current:
                state = "active"
                icon = "▶"

            else:
                state = "locked"
                icon = "🔒"

            color = (
                "#00ff88"
                if state == "completed"
                else "#00d4ff"
                if state == "active"
                else "#445"
            )

            html_content = textwrap.dedent(f"""
            <div class="round-card {state}"
                 style="text-align:center; padding:12px 8px;">

                <div style="font-size:1.2rem">{icon}</div>

                <div style="font-family:'Orbitron',monospace;
                            font-size:0.65rem;
                            color:#8899bb;
                            letter-spacing:1px;">
                    ROUND
                </div>

                <div style="font-family:'Orbitron',monospace;
                            font-size:1rem;
                            color:{color};
                            font-weight:700;">
                    {round_num}
                </div>

            </div>
            """).strip()

            st.markdown(
                html_content,
                unsafe_allow_html=True,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TREASURE FRAGMENTS
# ═══════════════════════════════════════════════════════════════════════════════

def render_fragments(completed_rounds: list[dict]) -> None:
    """Display earned treasure fragments."""

    if not completed_rounds:
        return

    fragment_html = "".join(
        f'<span class="fragment-pill earned">'
        f'🔷 {html.escape(str(r.get("fragment", "??")))}'
        f'</span>'
        for r in completed_rounds
    )

    st.markdown(
        f'<div class="fragments-strip">{fragment_html}</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DIFFICULTY BADGE
# ═══════════════════════════════════════════════════════════════════════════════

def difficulty_badge(diff: str) -> str:

    css = {
        "EASY": "diff-easy",
        "MEDIUM": "diff-medium",
        "HARD": "diff-hard",
        "VERY HARD": "diff-hard",
    }.get(diff, "diff-easy")

    return f'<span class="{css}">[{html.escape(str(diff))}]</span>'


# ═══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def render_leaderboard(
    rows: list[dict],
    my_team_name: str = "",
) -> None:
    """Render the leaderboard table."""

    if not rows:
        st.info("No teams on the leaderboard yet.")
        return

    medals = {
        1: "🥇",
        2: "🥈",
        3: "🥉",
    }

    for row in rows[:20]:

        rank = row.get("rank", "—")

        is_mine = (
            row.get("team_name", "").lower()
            == my_team_name.lower()
            if my_team_name
            else False
        )

        medal = medals.get(rank, f"#{rank}")

        status = row.get("status", "active")

        status_badge = (
            "✅"
            if status == "completed"
            else "⌛"
            if status == "expired"
            else "⚡"
        )

        time_str = "—"

        if row.get("completion_time_seconds"):

            m, s = divmod(
                row["completion_time_seconds"],
                60,
            )

            time_str = f"{m}m {s}s"

        row_class = f"rank-{rank}" if rank <= 3 else ""

        if is_mine:
            row_class += " my-team"

        team_name = html.escape(str(row.get("team_name", "")))

        score = row.get("final_score", 0)

        score_color = "#00ffea" if is_mine else "#e0e0ff"

        html_content = textwrap.dedent(f"""
        <div class="leaderboard-row {row_class}">

            <div style="width:50px;
                        font-family:'Orbitron',monospace;
                        font-weight:700;
                        color:#00d4ff;">
                {medal}
            </div>

            <div style="flex:1;
                        font-weight:600;
                        color:{score_color};">
                {team_name} {'← You' if is_mine else ''}
            </div>

            <div style="width:80px;
                        text-align:right;
                        font-family:'Share Tech Mono',monospace;
                        color:#00d4ff;">
                {score}pts
            </div>

            <div style="width:80px;
                        text-align:right;
                        font-family:'Share Tech Mono',monospace;
                        color:#8899bb;
                        font-size:0.8rem;">
                {time_str}
            </div>

            <div style="width:30px;
                        text-align:right;">
                {status_badge}
            </div>

        </div>
        """).strip()

        st.markdown(
            html_content,
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# TEAM CODE DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def team_code_display(team_code: str) -> None:
    """Display the team code in a prominent copyable style."""

    safe_team_code = html.escape(str(team_code))

    html_content = textwrap.dedent(f"""
    <div style="text-align:center; padding:20px;">

        <div style="font-family:'Orbitron',monospace;
                    font-size:0.8rem;
                    color:#8899bb;
                    letter-spacing:3px;
                    margin-bottom:8px;">
            YOUR TEAM CODE
        </div>

        <div style="font-family:'Share Tech Mono',monospace;
                    font-size:2rem;
                    letter-spacing:0.3em;
                    color:#00ffea;
                    background:rgba(0,255,234,0.07);
                    border:2px solid rgba(0,255,234,0.4);
                    border-radius:10px;
                    padding:14px 28px;
                    display:inline-block;
                    box-shadow:0 0 25px rgba(0,255,234,0.2);">
            {safe_team_code}
        </div>

        <div style="color:#8899bb;
                    font-size:0.8rem;
                    margin-top:10px;
                    font-family:monospace;">
            Save this code — you'll need it to resume your game!
        </div>

    </div>
    """).strip()

    st.markdown(
        html_content,
        unsafe_allow_html=True,
    )
