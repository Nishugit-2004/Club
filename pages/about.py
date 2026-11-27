"""
pages/about.py — CSE Department, Faculty Coordinators, and Student Team Members page.
Loaded dynamically from SQLite database (treasure_hunt.db).
"""
import base64
import os
import streamlit as st
from components.ui import cyber_header
from database import db


# ── Resolve & encode image ───────────────────────────────────────────────────

def _encode_image(photo_path: str) -> tuple[str, str] | None:
    """
    Resolve photo_path (relative or absolute) → (base64_data, mime_type).
    Returns None if the file cannot be found or read.
    """
    if not photo_path:
        return None

    full_path = (
        photo_path
        if os.path.isabs(photo_path)
        else os.path.join(db.BASE_DIR, photo_path)
    )

    if not os.path.exists(full_path):
        return None

    try:
        with open(full_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        ext = os.path.splitext(full_path)[1].lower().lstrip(".")
        mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "png": "image/png", "gif": "image/gif",
                    "webp": "image/webp"}
        mime = mime_map.get(ext, f"image/{ext}")
        return data, mime
    except Exception:
        return None


# ── Reusable card HTML builders ──────────────────────────────────────────────

def _photo_circle_html(photo_path: str, fallback_emoji: str, size: int = 110) -> str:
    """Return HTML for a circular photo (real image or emoji fallback)."""
    encoded = _encode_image(photo_path)
    if encoded:
        b64, mime = encoded
        return (
            f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
            f'margin:0 auto 14px;border:3px solid #00d4ff;'
            f'box-shadow:0 0 22px rgba(0,212,255,0.55);overflow:hidden;flex-shrink:0;">'
            f'<img src="data:{mime};base64,{b64}" '
            f'style="width:100%;height:100%;object-fit:cover;object-position:center top;display:block;" />'
            f'</div>'
        )
    # Clean placeholder with gradient background + emoji
    fs = max(size // 3, 18)
    return (
        f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
        f'margin:0 auto 14px;border:2.5px solid rgba(0,212,255,0.4);'
        f'box-shadow:0 0 18px rgba(0,212,255,0.25);overflow:hidden;flex-shrink:0;'
        f'background:linear-gradient(135deg,#0d2060 0%,#1a0a4a 100%);'
        f'display:flex;align-items:center;justify-content:center;font-size:{fs}px;">'
        f'{fallback_emoji}'
        f'</div>'
    )


def _photo_rect_html(photo_path: str, fallback_emoji: str, width: str = "100%", height: int = 220) -> str:
    """Return HTML for a rectangular photo (real image or emoji placeholder)."""
    encoded = _encode_image(photo_path)
    if encoded:
        b64, mime = encoded
        return (
            f'<div style="width:{width};height:{height}px;border-radius:12px 12px 0 0;'
            f'overflow:hidden;margin:-1px -1px 0 -1px;">'
            f'<img src="data:{mime};base64,{b64}" '
            f'style="width:100%;height:100%;object-fit:cover;object-position:center top;display:block;" />'
            f'</div>'
        )
    # Placeholder block
    return (
        f'<div style="width:{width};height:{height}px;border-radius:12px 12px 0 0;'
        f'background:linear-gradient(135deg,#0b1a3a 0%,#140830 100%);'
        f'display:flex;align-items:center;justify-content:center;'
        f'border-bottom:1px solid rgba(0,212,255,0.15);">'
        f'<div style="text-align:center;">'
        f'<div style="font-size:52px;margin-bottom:6px;">{fallback_emoji}</div>'
        f'<div style="font-family:\'Share Tech Mono\',monospace;font-size:0.65rem;'
        f'color:rgba(0,212,255,0.4);letter-spacing:2px;">NO PHOTO</div>'
        f'</div>'
        f'</div>'
    )


# ── Main render ──────────────────────────────────────────────────────────────

def render():
    # ── Department intro ─────────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-container" style="padding:40px 20px 30px;">
        <div class="hero-title" style="font-size:2.5rem;">DEPARTMENT OF CSE</div>
        <div class="hero-subtitle">◈ COMPUTER SCIENCE &amp; ENGINEERING ◈</div>
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

    # ════════════════════════════════════════════════════════════════════════
    # 1. FACULTY COORDINATORS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("FACULTY COORDINATORS", "Department of Computer Science & Engineering")

    faculty_list = db.get_faculty_profiles()
    faculty_emojis = ["👨‍🏫", "👩‍🏫", "👨‍💻"]

    if not faculty_list:
        st.info("No faculty profiles found.")
    else:
        n_fac = min(len(faculty_list), 3)
        fac_cols = st.columns(n_fac)
        for i, f in enumerate(faculty_list):
            emoji = faculty_emojis[i % len(faculty_emojis)]
            photo_html = _photo_rect_html(f.get("photo_path", ""), emoji, height=240)

            name       = f.get("name", "Faculty Member")
            desig      = f.get("designation", "")
            desc       = f.get("description", "")
            expertise  = f.get("expertise", "")

            with fac_cols[i % 3]:
                st.markdown(f"""
                <div class="profile-card" style="padding:0; overflow:hidden; min-height:420px;">
                    {photo_html}
                    <div style="padding:18px 16px 20px;">
                        <div style="font-family:'Orbitron',monospace; font-size:0.95rem;
                                    color:#00ffea; font-weight:700; margin-bottom:4px;
                                    word-break:break-word; line-height:1.3;">
                            {name}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.78rem;
                                    color:#7b2fff; letter-spacing:1px; margin-bottom:12px;">
                            {desig}
                        </div>
                        <div style="color:#8899bb; font-size:0.84rem; line-height:1.65;
                                    margin-bottom:12px;">
                            {desc}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.70rem;
                                    color:#00d4ff; opacity:0.85; word-break:break-word;">
                            {expertise}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════════
    # 2. STUDENT COORDINATORS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    cyber_header("STUDENT COORDINATORS", "CSE Coding Club Leadership Team")

    members = db.get_club_members()
    member_emojis = ["👑", "⚡", "🤝", "📱", "💰", "📝", "👥", "🎯", "📜"]

    if not members:
        st.info("No student coordinator profiles found.")
    else:
        mem_cols = st.columns(3)
        for i, m in enumerate(members):
            emoji      = member_emojis[i % len(member_emojis)]
            order_num  = m.get("display_order") or (i + 1)
            name       = m.get("name", "")
            role       = m.get("role", "")
            usn        = m.get("usn", "")
            bio        = m.get("bio", "")
            photo_path = m.get("photo_path", "")

            # Build circular photo (75 px) — centred in the card
            photo_html = _photo_circle_html(photo_path, emoji, size=110)

            # USN badge (optional)
            usn_html = ""
            if usn:
                usn_html = (
                    f'<div style="display:inline-block;background:rgba(123,47,255,0.1);'
                    f'border:1px solid rgba(123,47,255,0.3);border-radius:4px;'
                    f'padding:2px 8px;font-family:\'Share Tech Mono\',monospace;'
                    f'font-size:0.73rem;color:#e0e0ff;margin-bottom:8px;">'
                    f'USN: {usn}</div>'
                )

            with mem_cols[i % 3]:
                st.markdown(f"""
                <div class="profile-card" style="padding:18px 14px 18px; margin-bottom:16px; position:relative; min-height:300px;">
                    <div style="display:inline-block; position:absolute; top:12px; left:14px;
                                background:rgba(0,212,255,0.12); border:1px solid rgba(0,212,255,0.4);
                                border-radius:12px; padding:2px 8px;
                                font-family:'Share Tech Mono',monospace;
                                font-size:0.68rem; color:#00d4ff;">
                        SL NO: {order_num}
                    </div>
                    <div style="height:28px;"></div>
                    <div style="text-align:center;">
                        {photo_html}
                        <div style="font-family:'Orbitron',monospace; font-size:0.88rem;
                                    color:#00ffea; font-weight:700; margin-bottom:4px;
                                    word-break:break-word; line-height:1.3;">
                            {name}
                        </div>
                        <div style="font-family:'Share Tech Mono',monospace; font-size:0.73rem;
                                    color:#7b2fff; font-weight:600; letter-spacing:1px;
                                    margin-bottom:8px;">
                            {role}
                        </div>
                        {usn_html}
                        <div style="color:#8899bb; font-size:0.78rem; line-height:1.5;
                                    text-align:left;">
                            {bio}
                        </div>
                    </div>
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
            <span style="background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3);
                         border-radius:20px; padding:5px 14px;
                         font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00d4ff;">
                🏆 Competitive Programming
            </span>
            <span style="background:rgba(123,47,255,0.1); border:1px solid rgba(123,47,255,0.3);
                         border-radius:20px; padding:5px 14px;
                         font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#7b2fff;">
                💡 Hackathons
            </span>
            <span style="background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.3);
                         border-radius:20px; padding:5px 14px;
                         font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00ff88;">
                🔐 Treasure Hunts
            </span>
            <span style="background:rgba(255,45,155,0.1); border:1px solid rgba(255,45,155,0.3);
                         border-radius:20px; padding:5px 14px;
                         font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#ff2d9b;">
                📚 Workshops
            </span>
            <span style="background:rgba(0,212,255,0.1); border:1px solid rgba(0,212,255,0.3);
                         border-radius:20px; padding:5px 14px;
                         font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:#00d4ff;">
                🌐 Open Source Projects
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
