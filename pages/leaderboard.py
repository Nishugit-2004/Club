"""
pages/leaderboard.py — Live public leaderboard.
"""
import streamlit as st
from components.ui import cyber_header, render_leaderboard
from database import db


def render():
    st.markdown("""
    <div class="hero-container" style="padding:30px 20px 20px;">
        <div class="hero-title" style="font-size:2.2rem;">LEADERBOARD</div>
        <div class="hero-subtitle">◈ LIVE RANKINGS ◈</div>
    </div>
    """, unsafe_allow_html=True)

    cyber_header("LIVE RANKINGS", "Updated in real-time as teams complete rounds")

    # Ranking rules explanation
    col_info, col_lb = st.columns([1, 3])

    with col_info:
        st.markdown("""
        <div class="cyber-card">
            <div style="font-family:'Orbitron',monospace; font-size:0.75rem; color:#00d4ff; letter-spacing:2px; margin-bottom:12px;">
                RANKING CRITERIA
            </div>
            <ol style="color:#8899bb; font-size:0.85rem; padding-left:20px; line-height:2.0;">
                <li><strong style="color:#e0e0ff;">Highest Score</strong></li>
                <li><strong style="color:#e0e0ff;">Fastest Completion</strong></li>
                <li><strong style="color:#e0e0ff;">Fewest Hints</strong></li>
            </ol>
            <div class="cyber-divider"></div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#445; margin-top:10px;">
                LEGEND<br>
                ✅ Completed<br>
                ⌛ Time Expired<br>
                ⚡ Active
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with col_lb:
        if not db.is_db_available():
            st.warning("Database not configured. Leaderboard unavailable.")
        else:
            lb_data = db.get_leaderboard(limit=50)
            my_team = ""
            if st.session_state.get("team_code"):
                team = db.get_team(st.session_state["team_code"])
                if team:
                    my_team = team["team_name"]

            if not lb_data:
                st.markdown("""
                <div class="cyber-card" style="text-align:center; padding:40px;">
                    <div style="font-size:3rem; margin-bottom:10px;">📊</div>
                    <div style="font-family:'Orbitron',monospace; color:#8899bb;">No teams have started yet.</div>
                    <div style="color:#445; font-size:0.85rem; margin-top:8px;">Be the first to register and play!</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Header row
                st.markdown("""
                <div style="display:flex; padding:8px 16px; font-family:'Orbitron',monospace; font-size:0.65rem;
                             color:#445; letter-spacing:2px; margin-bottom:4px;">
                    <div style="width:50px;">RANK</div>
                    <div style="flex:1;">TEAM</div>
                    <div style="width:80px; text-align:right;">SCORE</div>
                    <div style="width:80px; text-align:right;">TIME</div>
                    <div style="width:30px; text-align:right;">ST</div>
                </div>
                """, unsafe_allow_html=True)

                render_leaderboard(lb_data, my_team_name=my_team)

                st.markdown(f"""
                <div style="font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:#445; text-align:center; margin-top:12px;">
                    Showing {len(lb_data)} team(s) · Rankings update live
                </div>
                """, unsafe_allow_html=True)

    # ── Call to action ────────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔐 Enter the Hunt", type="primary", use_container_width=True):
            if st.session_state.get("team_code"):
                st.session_state.page = "hunt"
            else:
                st.session_state.page = "register"
            st.rerun()
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

