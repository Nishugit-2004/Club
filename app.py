"""
app.py — The Lost Algorithm: CSE Coding Club Treasure Hunt
Main entry point for the Streamlit application.
"""
import streamlit as st

# ── Page config must be first Streamlit call ────────────────────────────────
st.set_page_config(
    page_title="The Lost Algorithm",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "The Lost Algorithm — CSE Coding Club Treasure Hunt",
    },
)

# ── Imports ──────────────────────────────────────────────────────────────────
from components.ui import load_css, hero_section, cyber_header, db_unavailable_warning
from database.db import is_db_available, get_team, get_session, expire_session_if_needed
from pages import home, register, hunt, results, leaderboard, about, organizer

# ── Load styles ──────────────────────────────────────────────────────────────
load_css()

# ── Session state defaults ───────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "team_code" not in st.session_state:
    st.session_state.team_code = None
if "nav_round" not in st.session_state:
    st.session_state.nav_round = 1
if "hint_shown" not in st.session_state:
    st.session_state.hint_shown = {}

# ── Navigation sidebar ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:10px 0 20px;">
        <div style="font-family:'Orbitron',monospace; font-size:0.9rem; color:#00d4ff; letter-spacing:3px;">
            THE LOST<br>ALGORITHM
        </div>
        <div style="color:#445; font-size:0.65rem; letter-spacing:2px; margin-top:4px;">◈ CSE CODING CLUB ◈</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    nav_items = {
        "🏠 Home": "home",
        "🏛️ About CSE": "about",
        "📋 Register": "register",
        "🗺️ Treasure Hunt": "hunt",
        "🏆 Leaderboard": "leaderboard",
        "🎯 My Results": "results",
    }

    for label, page_key in nav_items.items():
        if st.button(label, use_container_width=True, key=f"nav_{page_key}"):
            st.session_state.page = page_key
            st.rerun()

    st.divider()

    # Team status in sidebar
    tc = st.session_state.get("team_code")
    if tc:
        st.markdown(f"""
        <div style="background:rgba(0,212,255,0.08); border:1px solid rgba(0,212,255,0.3);
                    border-radius:8px; padding:12px; font-family:monospace; text-align:center;">
            <div style="color:#8899bb; font-size:0.65rem; letter-spacing:2px;">ACTIVE TEAM</div>
            <div style="color:#00ffea; font-size:0.85rem; font-weight:bold; margin-top:4px;">{tc}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Leave Game", use_container_width=True):
            st.session_state.team_code = None
            st.session_state.page = "home"
            st.rerun()
    else:
        team_code_input = st.text_input("🔑 Enter Team Code", placeholder="TLA-XXXXXX", key="sidebar_code_input")
        if st.button("▶ Resume Game", use_container_width=True) and team_code_input.strip():
            code = team_code_input.strip().upper()
            team = get_team(code)
            if team:
                st.session_state.team_code = code
                st.session_state.page = "hunt"
                st.rerun()
            else:
                st.error("Team code not found.")

    st.divider()
    # Organizer link (hidden, low-key)
    if st.button("⚙ Organizer", use_container_width=True, key="nav_organizer"):
        st.session_state.page = "organizer"
        st.rerun()


# ── Database check ────────────────────────────────────────────────────────────
if not is_db_available() and st.session_state.page not in ("home", "about", "organizer"):
    db_unavailable_warning()
    st.stop()

# ── Route to page ─────────────────────────────────────────────────────────────
page = st.session_state.get("page", "home")

if page == "home":
    home.render()
elif page == "about":
    about.render()
elif page == "register":
    register.render()
elif page == "hunt":
    if not st.session_state.get("team_code"):
        st.session_state.page = "register"
        st.rerun()
    else:
        hunt.render()
elif page == "leaderboard":
    leaderboard.render()
elif page == "results":
    results.render()
elif page == "organizer":
    organizer.render()
else:
    home.render()

