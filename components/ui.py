
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

    st.markdown(
        '<div class="hero-container">'
        '<div class="hero-title">THE LOST ALGORITHM</div>'
        '<div class="hero-subtitle">◈ CSE CODING CLUB TREASURE HUNT ◈</div>'
        '<div class="hero-tagline">Ten rounds. Thirty challenges. One hidden treasure.</div>'
        '</div>',
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
        f'<p style="color:#8899bb;font-family:monospace;letter-spacing:1px;margin:0;">{safe_subtitle}</p>'
        if subtitle else ""
    )
    st.markdown(
        f'<div style="margin:1.5rem 0 1rem;">'
        f'<h2 style="font-family:\'Orbitron\',monospace;color:#00d4ff;letter-spacing:3px;margin:0;">{safe_title}</h2>'
        f'{sub_html}'
        f'<div class="cyber-divider" style="margin-top:10px;"></div>'
        f'</div>',
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

    st.markdown(
        f'<div style="text-align:center;padding:10px;">'
        f'<div style="font-family:\'Share Tech Mono\',monospace;color:#8899bb;font-size:0.75rem;letter-spacing:2px;">CURRENT SCORE</div>'
        f'<div class="score-badge">{score} / {max_score}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# DATABASE WARNING
# ═══════════════════════════════════════════════════════════════════════════════

def db_unavailable_warning() -> None:
    """Show a warning if database access fails."""

    st.markdown(
        '<div style="background:rgba(255,165,0,0.1);border:2px solid orange;border-radius:10px;padding:20px;margin:20px 0;">'
        '<h3 style="color:orange;font-family:\'Orbitron\',monospace;">⚠ DATABASE INITIALIZATION ISSUE</h3>'
        '<p style="color:#e0e0ff;">Could not write or read from local SQLite file <code>treasure_hunt.db</code>.</p>'
        '</div>',
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

            st.markdown(
                f'<div class="round-card {state}" style="text-align:center;padding:12px 8px;">'
                f'<div style="font-size:1.2rem">{icon}</div>'
                f'<div style="font-family:\'Orbitron\',monospace;font-size:0.65rem;color:#8899bb;letter-spacing:1px;">ROUND</div>'
                f'<div style="font-family:\'Orbitron\',monospace;font-size:1rem;color:{color};font-weight:700;">{round_num}</div>'
                f'</div>',
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
    """Render the leaderboard table with proper HTML rendering."""

    if not rows:
        st.markdown(
            '<div class="cyber-card" style="text-align:center;padding:40px;">'
            '<div style="font-size:3rem;margin-bottom:10px;">📊</div>'
            '<div style="font-family:\"Orbitron\",monospace;color:#8899bb;">No teams on the leaderboard yet.</div>'
            '<div style="color:#445;font-size:0.85rem;margin-top:8px;">Be the first to register and play!</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}

    # ── Top-3 Podium highlight ────────────────────────────────────────────────
    top3 = [r for r in rows if isinstance(r.get("rank"), int) and r["rank"] <= 3]
    if top3:
        podium_colors = {1: ("gold", "rgba(255,215,0,0.12)"), 2: ("silver", "rgba(192,192,192,0.08)"), 3: ("#cd7f32", "rgba(205,127,50,0.08)")}
        podium_html = '<div style="display:flex;gap:12px;margin-bottom:20px;flex-wrap:wrap;">'
        for r in sorted(top3, key=lambda x: x["rank"]):
            rk = r["rank"]
            bc, bg = podium_colors.get(rk, ("#00d4ff", "rgba(0,212,255,0.08)"))
            tn = html.escape(str(r.get("team_name", "")))
            sc = r.get("final_score", 0)
            rds = r.get("rounds_completed", 0)
            md = medals.get(rk, f"#{rk}")
            ct = r.get("completion_time_seconds")
            ts = f"{ct // 60}m {ct % 60}s" if ct else "—"
            podium_html += (
                f'<div style="flex:1;min-width:140px;background:{bg};border:1.5px solid {bc};'
                f'border-radius:12px;padding:16px 12px;text-align:center;">'
                f'<div style="font-size:1.8rem;margin-bottom:4px;">{md}</div>'
                f'<div style="font-family:\'Orbitron\',monospace;font-size:0.78rem;color:{bc};'
                f'font-weight:700;margin-bottom:4px;word-break:break-word;">{tn}</div>'
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:1rem;color:#00ffea;font-weight:700;">{sc}pts</div>'
                f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.68rem;color:#8899bb;margin-top:4px;">{rds} rounds · {ts}</div>'
                f'</div>'
            )
        podium_html += '</div>'
        st.markdown(podium_html, unsafe_allow_html=True)

    # ── Full table ────────────────────────────────────────────────────────────
    for row in rows[:50]:
        rank = row.get("rank")
        try:
            rank_int = int(rank)
        except (TypeError, ValueError):
            rank_int = 999

        is_mine = bool(
            my_team_name
            and row.get("team_name", "").lower() == my_team_name.lower()
        )

        medal = medals.get(rank_int, f"#{rank_int}")
        status = row.get("status", "active")
        status_badge = "✅" if status == "completed" else "⌛" if status == "expired" else "⚡"

        ct = row.get("completion_time_seconds")
        time_str = f"{ct // 60}m {ct % 60}s" if ct else "—"

        rds = row.get("rounds_completed", 0)
        team_name = html.escape(str(row.get("team_name", "")))
        score = row.get("final_score", 0)
        you_label = " ← You" if is_mine else ""

        # Border colour by rank
        if rank_int == 1:
            border = "gold"
        elif rank_int == 2:
            border = "silver"
        elif rank_int == 3:
            border = "#cd7f32"
        elif is_mine:
            border = "#00ffea"
        else:
            border = "transparent"

        bg = "rgba(0,212,255,0.06)" if is_mine else "rgba(10,20,40,0.7)"
        name_color = "#00ffea" if is_mine else "#e0e0ff"
        medal_color = "gold" if rank_int == 1 else "silver" if rank_int == 2 else "#cd7f32" if rank_int == 3 else "#00d4ff"

        row_html = (
            f'<div style="display:flex;align-items:center;padding:11px 16px;margin:4px 0;'
            f'border-radius:8px;background:{bg};border-left:3px solid {border};'
            f'border:1px solid {border};transition:all 0.2s;">'
            f'<div style="width:54px;font-family:\'Orbitron\',monospace;font-weight:700;color:{medal_color};font-size:1rem;">'
            f'{medal}</div>'
            f'<div style="flex:1;font-weight:600;color:{name_color};font-size:0.92rem;word-break:break-word;">'
            f'{team_name}{you_label}</div>'
            f'<div style="width:60px;text-align:center;font-family:\'Share Tech Mono\',monospace;'
            f'font-size:0.75rem;color:#8899bb;">{rds}rds</div>'
            f'<div style="width:80px;text-align:right;font-family:\'Share Tech Mono\',monospace;'
            f'color:#00d4ff;font-weight:700;">{score}pts</div>'
            f'<div style="width:76px;text-align:right;font-family:\'Share Tech Mono\',monospace;'
            f'color:#8899bb;font-size:0.78rem;">{time_str}</div>'
            f'<div style="width:34px;text-align:right;font-size:1rem;">{status_badge}</div>'
            f'</div>'
        )
        st.markdown(row_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TEAM CODE DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════

def team_code_display(team_code: str) -> None:
    """Display the team code in a prominent copyable style."""
    safe_code = html.escape(str(team_code))
    st.markdown(
        '<div style="text-align:center;padding:24px 10px;">'
        '<div style="font-family:\'Orbitron\',monospace;font-size:0.8rem;color:#8899bb;letter-spacing:3px;margin-bottom:10px;">YOUR TEAM CODE</div>'
        f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:2rem;letter-spacing:0.3em;color:#00ffea;background:rgba(0,255,234,0.07);border:2px solid rgba(0,255,234,0.4);border-radius:10px;padding:14px 28px;display:inline-block;box-shadow:0 0 25px rgba(0,255,234,0.2);">{safe_code}</div>'
        '<div style="color:#8899bb;font-size:0.8rem;margin-top:12px;font-family:monospace;">Save this code — you\'ll need it to resume your game!</div>'
        '</div>',
        unsafe_allow_html=True,
    )
