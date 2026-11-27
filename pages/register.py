"""
pages/register.py — Team registration and game entry page.
"""
import streamlit as st
from components.ui import cyber_header
from database.db import register_team, get_team, is_db_available


def render():
    st.markdown("""
    <div class="hero-container" style="padding:30px 20px 20px;">
        <div class="hero-title" style="font-size:2.2rem;">TEAM REGISTRATION</div>
        <div class="hero-subtitle">◈ REGISTER TO ENTER THE HUNT ◈</div>
    </div>
    """, unsafe_allow_html=True)

    if not is_db_available():
        st.error("⚠ Database not configured. Contact the organizer.")
        return

    # ── Tabs: Register vs Resume ─────────────────────────────────────────────
    tab_reg, tab_resume = st.tabs(["📋 Register New Team", "🔑 Resume Existing Game"])

    # ── Registration tab ─────────────────────────────────────────────────────
    with tab_reg:
        cyber_header("NEW TEAM REGISTRATION", "Fill all fields to receive your team code")

        col_form, col_info = st.columns([3, 2])

        with col_form:
            with st.form("registration_form", clear_on_submit=False):
                team_name = st.text_input(
                    "Team Name *",
                    placeholder="e.g. Binary Bandits",
                    help="Must be unique. This will appear on the leaderboard."
                )
                captain_name = st.text_input("Captain's Name *", placeholder="Full name")
                captain_email = st.text_input("Captain's Email *", placeholder="email@college.edu")
                college_id = st.text_input("College ID *", placeholder="Your institution ID")

                st.markdown("**Team Members** (up to 4 names, one per line)")
                member_text = st.text_area(
                    "Member Names",
                    placeholder="Alice\nBob\nCarol\nDave",
                    height=100,
                    help="Enter each member's name on a new line."
                )

                num_participants = st.number_input(
                    "Total Number of Participants *",
                    min_value=1, max_value=5, value=2
                )

                submitted = st.form_submit_button("⚡ REGISTER TEAM", type="primary", use_container_width=True)

            if submitted:
                # Validate
                errors = []
                if not team_name.strip():
                    errors.append("Team name is required.")
                elif len(team_name.strip()) < 3:
                    errors.append("Team name must be at least 3 characters.")
                elif len(team_name.strip()) > 50:
                    errors.append("Team name must be 50 characters or less.")

                if not captain_name.strip():
                    errors.append("Captain's name is required.")
                if not captain_email.strip() or "@" not in captain_email:
                    errors.append("A valid captain email is required.")
                if not college_id.strip():
                    errors.append("College ID is required.")
                if num_participants < 1:
                    errors.append("At least 1 participant is required.")

                # Sanitise member names
                member_names = [n.strip() for n in member_text.strip().split("\n") if n.strip()]

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    with st.spinner("Registering your team..."):
                        result = register_team(
                            team_name=team_name.strip(),
                            captain_name=captain_name.strip(),
                            captain_email=captain_email.strip().lower(),
                            college_id=college_id.strip(),
                            member_names=member_names,
                            num_participants=num_participants,
                        )

                    if result["success"]:
                        team_code = result["team_code"]
                        st.session_state.team_code = team_code
                        st.session_state.registered_team_code = team_code
                        st.success("✅ Registration Successful!")
                        if st.button("🎯 START THE HUNT", type="primary", use_container_width=True, key="start_hunt_btn"):
                            st.session_state.page = "hunt"
                            st.rerun()
                    else:
                        st.error(f"❌ {result['error']}")

        with col_info:
            st.markdown("""
            <div class="cyber-card">
                <div style="font-family:'Orbitron',monospace; font-size:0.85rem; color:#00d4ff; margin-bottom:14px; letter-spacing:2px;">HOW IT WORKS</div>
                <div style="color:#e0e0ff; font-size:0.9rem; line-height:1.8;">
                    <p>1️⃣ Fill in your team details and register.</p>
                    <p>2️⃣ Receive a unique <strong style="color:#00ffea;">team code</strong>.</p>
                    <p>3️⃣ Save your team code — you'll need it to resume the game.</p>
                    <p>4️⃣ Click <em>Start the Hunt</em> to begin.</p>
                    <p>5️⃣ The 60-minute countdown starts with Round 1.</p>
                </div>
            </div>
            <div class="cyber-card" style="margin-top:16px;">
                <div style="font-family:'Orbitron',monospace; font-size:0.85rem; color:#ff2d9b; margin-bottom:10px;">⚠ IMPORTANT</div>
                <ul style="color:#8899bb; font-size:0.85rem; padding-left:20px; line-height:1.8;">
                    <li>One registration per team.</li>
                    <li>Your team name will be visible on the leaderboard.</li>
                    <li>The timer cannot be paused once started.</li>
                    <li>Use your team code to resume if the browser closes.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # ── Resume tab ───────────────────────────────────────────────────────────
    with tab_resume:
        cyber_header("RESUME YOUR GAME", "Enter your team code to continue")

        col_r, col_blank = st.columns([2, 2])
        with col_r:
            resume_code = st.text_input(
                "Team Code",
                placeholder="TLA-XXXXXX",
                key="resume_code_input",
                help="Enter the team code you received during registration."
            )

            if st.button("▶ RESUME GAME", type="primary", use_container_width=True, key="resume_btn"):
                code = resume_code.strip().upper()
                if not code:
                    st.error("Please enter your team code.")
                else:
                    with st.spinner("Looking up your team..."):
                        team = get_team(code)

                    if team:
                        st.session_state.team_code = code
                        st.success(f"✅ Welcome back, **{team['team_name']}**!")
                        st.info("Redirecting to the hunt...")
                        st.session_state.page = "hunt"
                        st.rerun()
                    else:
                        st.error("❌ Team code not found. Check the code and try again.")

        with col_blank:
            st.markdown("""
            <div class="cyber-card">
                <div style="font-family:'Orbitron',monospace; font-size:0.85rem; color:#00d4ff; margin-bottom:12px;">RESUME NOTES</div>
                <ul style="color:#8899bb; font-size:0.9rem; padding-left:20px; line-height:1.9;">
                    <li>Your timer continues from where it left off.</li>
                    <li>All completed rounds and scores are preserved.</li>
                    <li>Unsolved questions can still be attempted.</li>
                    <li>Team code format: <code style="color:#00ffea;">TLA-XXXXXX</code></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

