"""
pages/home.py — Clean, cinematic landing page for The Lost Algorithm.
Keeps puzzle names, topics, clues, and challenges hidden until participants enter the hunt.
All HTML is dedented to prevent any raw text or code blocks from rendering.
"""
import textwrap
import streamlit as st
from components.ui import hero_section, cyber_header


def render():
    # ── 1. Cyberpunk Title, Subtitle & Tagline ───────────────────────────────
    hero_section()

    # ── 2. Primary CTA: Enter the Hunt ───────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 ENTER THE HUNT", type="primary", use_container_width=True, key="home_enter"):
            if st.session_state.get("team_code"):
                st.session_state.page = "hunt"
            else:
                st.session_state.page = "register"
            st.rerun()

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    # ── 3. Event Countdown (if configured) ────────────────────────────────────
    try:
        event_date_str = st.secrets.get("event", {}).get("date", "")
        if event_date_str:
            countdown_html = textwrap.dedent("""
            <div class="cyber-card" style="text-align:center; padding:18px;">
                <div style="font-family:'Share Tech Mono',monospace; color:#8899bb; font-size:0.75rem; letter-spacing:3px;">
                    EVENT COUNTDOWN
                </div>
                <div id="event-countdown" style="font-family:'Orbitron',monospace; font-size:2rem; color:#00d4ff; margin:8px 0;"></div>
            </div>
            """).strip()
            st.markdown(countdown_html, unsafe_allow_html=True)

            js_snippet = textwrap.dedent(f"""
            <script>
            (function() {{
                const target = new Date("{event_date_str}");
                function update() {{
                    const now = new Date();
                    const diff = Math.max(0, Math.floor((target - now) / 1000));
                    const d = Math.floor(diff / 86400);
                    const h = Math.floor((diff % 86400) / 3600).toString().padStart(2,'0');
                    const m = Math.floor((diff % 3600) / 60).toString().padStart(2,'0');
                    const s = (diff % 60).toString().padStart(2,'0');
                    const el = window.parent.document.getElementById('event-countdown');
                    if (el) {{
                        el.textContent = d > 0 ? d + 'd ' + h + ':' + m + ':' + s : h + ':' + m + ':' + s;
                    }}
                }}
                update();
                setInterval(update, 1000);
            }})();
            </script>
            """).strip()
            st.components.v1.html(js_snippet, height=0)
    except Exception:
        pass

    # ── 4. Introduction Text ──────────────────────────────────────────────────
    cyber_header("ABOUT THE HUNT", "Where logic unlocks the vault")

    col_info, col_metrics = st.columns([3, 2])

    with col_info:
        info_html = textwrap.dedent("""
        <div class="cyber-card" style="line-height:1.9; font-size:1.02rem; color:#e0e0ff;">
            <p>
            Welcome to <strong style="color:#00d4ff;">The Lost Algorithm</strong>, the annual competitive
            treasure hunt hosted by the <strong>Department of Computer Science and Engineering Coding Club</strong>.
            </p>
            <p style="color:#8899bb;">
            Teams of students enter a high-stakes digital arena to conquer
            <strong style="color:#00ffea;">ten sequential rounds of mysteries</strong>.
            All challenge topics, ciphers, code problems, and mathematical puzzles are strictly classified
            and will only reveal themselves as your team unlocks each chamber.
            </p>
            <p style="color:#8899bb;">
            You have <strong style="color:#00d4ff;">60 minutes</strong> on the clock.
            Every completed round awards an encrypted <strong style="color:#7b2fff;">treasure fragment</strong>.
            Synthesize all ten fragments before the countdown expires to breach the final vault and claim your rank.
            </p>
        </div>
        """).strip()
        st.markdown(info_html, unsafe_allow_html=True)

    
    # ── 5. Bottom Navigation Buttons ──────────────────────────────────────────
    st.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        if st.button("🚀 Register Team", use_container_width=True, key="home_reg_bottom"):
            st.session_state.page = "register"
            st.rerun()
    with b_col2:
        if st.button("🏆 Live Leaderboard", use_container_width=True, key="home_lb_bottom"):
            st.session_state.page = "leaderboard"
            st.rerun()
    with b_col3:
        if st.button("🏛️ About CSE Department", use_container_width=True, key="home_about_bottom"):
            st.session_state.page = "about"
            st.rerun()

    st.markdown("<div style='height:36px'></div>", unsafe_allow_html=True)