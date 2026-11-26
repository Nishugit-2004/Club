# 🔐 The Lost Algorithm

**CSE Coding Club Treasure Hunt** — *Ten rounds. Thirty challenges. One hidden treasure.*

A futuristic cyberpunk treasure hunt website built with **Python + Streamlit + SQLite**.

---

## 🚀 Quick Start (Local Development & Testing)

The project uses **local SQLite (`treasure_hunt.db`)** and stores uploaded member photos in **`assets/team/`**, requiring **zero external cloud database setup**. The database and uploaded photos persist across app restarts.

### 1. Prerequisites

- Python 3.11 or Python 3.12
- Git (optional)

### 2. Required Packages

Install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Or install them directly:

```bash
pip install streamlit pandas Pillow pytest
```

### 3. Exact Entry-Point Filename

The main entry point for the Streamlit application is:

```bash
streamlit run app.py
```

Visit the local application in your browser at:
`http://localhost:8501`

---

## 💾 Local Persistence (SQLite & Photos)

- **Database File**: `treasure_hunt.db` in the project root.
  - Automatically created and initialized on first launch.
  - Holds all `teams`, `game_sessions`, `question_attempts`, `completed_rounds`, `leaderboard_results`, `event_settings`, `club_members`, and `faculty_profiles`.
  - Fully persistent between restarts.
- **Uploaded Photos**: Stored in `assets/team/`.
  - When the organizer creates or edits a member profile and uploads a photo, the image file is saved into `assets/team/` and its relative path is recorded in `treasure_hunt.db`.
  - These photos are rendered directly on the **About CSE** page.

---

## ⚙️ Organizer Dashboard & Member Profile Management

Access the Organizer Dashboard by clicking **⚙ Organizer** at the bottom of the left sidebar.

- **Default Local Organizer Password**: `admin123` (or set via `.streamlit/secrets.toml`).

### Managing Club Members & Photo Uploads:
1. Navigate to **⚙ Organizer** in the sidebar.
2. Enter the password (`admin123`) and click **🔓 Authenticate**.
3. Select the **🎖️ Club Members** tab.
4. **➕ Add New Member**:
   - Enter Full Name, Role, and Bio.
   - Set the Display Order.
   - Upload a photo (`.png`, `.jpg`, `.jpeg`, `.webp`).
   - Click **➕ Add Member Profile**. The photo is saved into `assets/team/` and displayed in the club gallery.
5. **✏️ Edit Existing Member**:
   - Select a member from the dropdown.
   - Update their name, role, bio, or display order.
   - Upload a replacement photo or delete the member profile.
6. Check the **🏛️ About CSE** page to see the updated profiles and photos rendered live.

---

## 📁 Project Structure

```
codingclub game/
├── app.py                      # Main Streamlit application entry point
├── requirements.txt            # Required Python packages
├── README.md                   # Documentation, setup & run guide
├── treasure_hunt.db            # Persistent SQLite database (auto-created)
├── .gitignore                  # Git ignore rules
├── .streamlit/
│   ├── config.toml             # Futuristic cyberpunk theme config
│   └── secrets.toml.example   # Optional credentials template
├── assets/
│   ├── css/
│   │   └── style.css           # Global cyberpunk styling
│   └── team/                   # Persistent uploaded team & member photos
├── components/
│   ├── __init__.py
│   └── ui.py                   # Reusable UI cards, headers, JS timer, badges
├── game/
│   ├── __init__.py
│   └── puzzles.py              # All 10 rounds, 30 challenges, per-team seeding
├── database/
│   ├── __init__.py
│   ├── db.py                   # SQLite database layer (auto-initializes schema)
│   └── schema.sql              # Reference SQL schema
├── pages/
│   ├── __init__.py
│   ├── home.py                 # Hero section, preview, rules, countdown
│   ├── about.py                # CSE Dept, faculty, dynamic club members with photos
│   ├── register.py             # Team registration & resume game
│   ├── hunt.py                 # Main 60-min treasure hunt gameplay
│   ├── results.py              # Vault unlocked, score breakdown, stats
│   ├── leaderboard.py          # Live public rankings
│   └── organizer.py            # Organizer portal: member profiles, photos, resets
└── tests/
    ├── test_database.py        # SQLite tests: teams, attempts, scoring, members
    ├── test_puzzles.py         # Puzzle generation & validation tests
    └── test_scoring.py         # Scoring, timer, penalties & ranking tests
```

---

## 🎮 Game Mechanics

| Property | Value |
|---|---|
| Total Rounds | 10 |
| Questions Per Round | 3 |
| Total Questions | 30 |
| Max Base Score | 300 pts |
| Duration | 60 minutes |
| Default Hint Penalty | −5 pts |
| Wrong Attempt Penalty | −2 pts |
| Max Attempts Per Question | 3 |

---

## 🧪 Running Automated Tests

Run the full unit test suite with `pytest`:

```bash
python -m pytest tests/ -v
```

All 49 unit tests verify:
- Team registration and duplicate prevention
- Persistent game session state and timer calculations
- Server-side answer validation across all 10 rounds
- Idempotent scoring (no duplicate points on re-submission)
- Sequential round unlocking and treasure fragments
- Live leaderboard rankings (score desc, time asc, hints asc)
- Club member profile creation, updates, and deletion in SQLite

---

## ☁️ Deploying to Streamlit Community Cloud

1. Commit and push the repository to GitHub:
   ```bash
   git add .
   git commit -m "feat: complete The Lost Algorithm with local SQLite"
   git push origin main
   ```
2. Log into [share.streamlit.io](https://share.streamlit.io).
3. Select your repository, set the branch to `main`, and the main file path to `app.py`.
4. (Optional) In **Advanced settings → Secrets**, add:
   ```toml
   [organizer]
   password = "YourCustomPassword"
   ```
5. Click **Deploy!**
