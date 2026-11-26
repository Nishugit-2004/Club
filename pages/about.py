"""
pages/about.py — CSE Department, Faculty Coordinators, and Student Team Members page.
Loaded dynamically from SQLite database (treasure_hunt.db).
"""
import base64
import os
import streamlit as st
from components.ui import cyber_header
from database import db


def _get_image_html(photo_path: str, fallback_emoji: str, size: int = 80) -> str:
    """Generate HTML for either the uploaded/linked image or the emoji avatar."""
    if photo_path:
        full_path = photo_path if os.path.isabs(photo_path) else os.path.join(db.BASE_DIR, photo_path)
        if os.path.exists(full_path):
            try:
                with open(full_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")
                ext = os.path.splitext(full_path)[1].lower().replace(".", "")
                mime = "image/jpeg" if ext in ("jpg", "jpeg") else ("image/png" if ext == "png" else f"image/{ext}")
                return f"""
                <div style="width:{size}px; height:{size}px; border-radius:50%; margin:0 auto 12px;
                            border: 2px solid #00d4ff; box-shadow:0 0 15px rgba(0,212,255,0.4); overflow:hidden;">
                    <img src="data:{mime};base64,{encoded}" style="width:100%; height:100%; object-fit:cover; display:block;" />
                </div>
                """
            except Exception:
                pass

    return f"""
    <div class="profile-avatar" style="width:{size}px; height:{size}px; font-size:{size // 2.5}px;">
        {fallback_emoji}
    </div>
    """


def render():
    # ── Department intro ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-container" style="padding:40px 20px 30px;">
        <div class="hero-title" style="font-size:2.5rem;">DEPARTMENT OF CSE</div>
        <div class="hero-subtitle">◈ COMPUTER SCIENCE & ENGINEERING ◈</div>
    </div>
    """, unsafe_allow_html=True)

    cyber_header("ABOUT THE DEPARTMENT", "Shaping the future of technology")

    st.markdown("""
    <div class="cyber-card" style="line-height:1.9; font-size:1.05rem; color:#e0e0ff;">
        <p>
        The <strong style="color:#00d4ff;">Department of Computer Science and Engineering</strong> is committed
        to producing skilled, innovative, and industry-ready graduates who will drive
        the next wave of technological advancement. Through rigorous academics, hands-on
        laboratories, and an active research culture, the department nurtures both
        technical excellence and creative problem-solving.
        </p>
        <p style="color:#8899bb;">
        Our curriculum spans foundational computer science—algorithms, data structures,
        operating systems, and networks—through to cutting-edge domains including
        artificial intelligence, machine learning, cloud computing, cybersecurity,
        and software engineering. Students engage in research projects, industry
        internships, hackathons, and competitive programming to build a complete
        professional profile.
        </p>
        <p style="color:#8899bb;">
        The department proudly hosts the <strong style="color:#00ffea;">CSE Coding Club</strong>,
        a student-led organisation that organises technical events, workshops, and
        competitive programming contests throughout the academic year.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Department achievements ───────────────────────────────────────────────
    achievements = [
        ("🏅", "Competitive Excellence", "Students regularly rank in national and international competitive programming contests."),
        ("🔬", "Active Research", "Faculty and students publish in peer-reviewed journals and conferences across AI, security, and systems."),
        ("🤝", "Industry Partnerships", "Strong ties with leading technology companies providing internship and placement opportunities."),
        ("🎓", "Holistic Development", "Beyond academics — coding clubs, tech fests, and leadership programmes shape well-rounded professionals."),
    ]

    cols = st.columns(2)
    for i, (icon, title, desc) in enumerate(achievements):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="cyber-card" style="display:flex; gap:14px; align-items:flex-start; padding:16px;">
                <div style="font-size:1.8rem;">{icon}</div>
                <div>
                    <div style="font-family:'Orbitron',monospace; font-size:0.85rem; color:#00d4ff; font-weight:700;">{title}</div>
                    <div style="color:#8899bb; font-size:0.9rem; margin-top:5px;">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── 1. Faculty Profiles (Department of CSE) ────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("FACULTY COORDINATORS", "Department of Computer Science & Engineering")

    faculty_list = db.get_faculty_profiles()
    faculty_emojis = ["👨‍🏫", "👩‍🏫", "👨‍💻"]

    if faculty_list:
        fac_cols = st.columns(min(len(faculty_list), 3))
        for i, f in enumerate(faculty_list):
            with fac_cols[i % 3]:
                emoji = faculty_emojis[i % len(faculty_emojis)]
                img_html = _get_image_html(f.get("photo_path", ""), emoji, size=90)
                st.markdown(f"""
                <div class="profile-card" style="min-height:360px;">
                    {img_html}
                    <div style="font-family:'Orbitron',monospace; font-size:1rem; color:#00ffea; font-weight:700; margin-bottom:4px;">{f['name']}</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#7b2fff; letter-spacing:1px; margin-bottom:12px;">{f['designation']}</div>
                    <div style="color:#8899bb; font-size:0.85rem; line-height:1.6; margin-bottom:12px;">{f.get('description','')}</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.72rem; color:#00d4ff; opacity:0.85;">{f.get('expertise','')}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── 2. Student Team Members (CSE Coding Club Coordinators) ─────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("STUDENT COORDINATORS", "CSE Coding Club Leadership Team")

    members = db.get_club_members()
    member_emojis = ["👑", "⚡", "🤝", "📱", "💰", "📝", "👥", "🎯", "📜"]

    if members:
        # Display 3x3 responsive grid for all 9 coordinators
        mem_cols = st.columns(3)
        for i, m in enumerate(members):
            with mem_cols[i % 3]:
                emoji = member_emojis[i % len(member_emojis)]
                img_html = _get_image_html(m.get("photo_path", ""), emoji, size=75)
                order_num = m.get("display_order") or (i + 1)
                usn_display = m.get("usn", "")

                st.markdown(f"""
                <div class="profile-card" style="padding:18px 14px; margin-bottom:16px; position:relative;">
                    <div style="display:inline-block; position:absolute; top:12px; left:14px; background:rgba(0,212,255,0.12);
                                border:1px solid rgba(0,212,255,0.4); border-radius:12px; padding:2px 8px;
                                font-family:'Share Tech Mono',monospace; font-size:0.68rem; color:#00d4ff;">
                        SL NO: {order_num}
                    </div>
                    <div style="height:10px;"></div>
                    {img_html}
                    <div style="font-family:'Orbitron',monospace; font-size:0.92rem; color:#00ffea; font-weight:700; margin-bottom:4px;">{m['name']}</div>
                    <div style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#7b2fff; font-weight:600; letter-spacing:1px; margin-bottom:6px;">{m['role']}</div>
                    {f'''<div style="display:inline-block; background:rgba(123,47,255,0.1); border:1px solid rgba(123,47,255,0.3);
                                border-radius:4px; padding:2px 8px; font-family:'Share Tech Mono',monospace;
                                font-size:0.75rem; color:#e0e0ff; margin-bottom:8px;">USN: {usn_display}</div>''' if usn_display else ''}
                    <div style="color:#8899bb; font-size:0.78rem; line-height:1.5;">{m.get('bio','')}</div>
                </div>
                """, unsafe_allow_html=True)

    # ── Coding Club intro ─────────────────────────────────────────────────────
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("THE CODING CLUB", "Where algorithms come to life")

    st.markdown("""
    <div class="cyber-card" style="line-height:1.9; color:#e0e0ff;">
        <p>
        The <strong style="color:#00d4ff;">CSE Coding Club</strong> is a student-led technical community
        that nurtures a culture of problem-solving, innovation, and collaborative learning.
        Founded by passionate programmers, the club serves as a launchpad for students
        to transform classroom knowledge into real-world skills.
        </p>
        <div style="display:flex; flex-wrap:wrap; gap:10px; margin-top:16px;">
            <span style="background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3); border-radius:20px;
                         padding:5px 14px; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00d4ff;">
                🏆 Competitive Programming
            </span>
            <span style="background:rgba(123,47,255,0.1); border:1px solid rgba(123,47,255,0.3); border-radius:20px;
                         padding:5px 14px; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#7b2fff;">
                💡 Hackathons
            </span>
            <span style="background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.3); border-radius:20px;
                         padding:5px 14px; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00ff88;">
                🔐 Treasure Hunts
            </span>
            <span style="background:rgba(255,45,155,0.1); border:1px solid rgba(255,45,155,0.3); border-radius:20px;
                         padding:5px 14px; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#ff2d9b;">
                📚 Workshops
            </span>
            <span style="background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3); border-radius:20px;
                         padding:5px 14px; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00d4ff;">
                🌐 Open Source Projects
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
