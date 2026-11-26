"""
tests/test_database.py — Tests for SQLite database layer (treasure_hunt.db).
Uses unique team names so tests can run repeatedly against persistent SQLite DB.
"""
import sys
import os
import uuid
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


@pytest.fixture(autouse=True)
def setup_db():
    """Ensure database schema is initialized before every test."""
    db.init_db()


def _rand_name(base: str) -> str:
    return f"{base}_{uuid.uuid4().hex[:6]}"


class TestDatabaseTeams:
    def test_register_and_get_team(self):
        tname = _rand_name("AlphaSquad")
        res = db.register_team(
            team_name=tname,
            captain_name="Alice",
            captain_email="alice@test.edu",
            college_id="CSE-101",
            member_names=["Alice", "Bob"],
            num_participants=2,
        )
        assert res["success"] is True
        code = res["team_code"]
        assert code.startswith("TLA-")

        team = db.get_team(code)
        assert team is not None
        assert team["team_name"] == tname
        assert team["captain_name"] == "Alice"
        assert team["captain_email"] == "alice@test.edu"
        assert team["member_names"] == ["Alice", "Bob"]
        assert team["num_participants"] == 2

    def test_prevent_duplicate_team_name(self):
        tname = _rand_name("UniqueDragons")
        res1 = db.register_team(
            team_name=tname,
            captain_name="Charlie",
            captain_email="charlie@test.edu",
            college_id="CSE-102",
            member_names=["Charlie"],
            num_participants=1,
        )
        assert res1["success"] is True

        res2 = db.register_team(
            team_name=tname,
            captain_name="David",
            captain_email="david@test.edu",
            college_id="CSE-103",
            member_names=["David"],
            num_participants=1,
        )
        assert res2["success"] is False
        assert "already registered" in res2["error"]


class TestDatabaseGameSession:
    def test_create_and_update_session(self):
        tname = _rand_name("SessionExplorers")
        res = db.register_team(
            team_name=tname,
            captain_name="Eve",
            captain_email="eve@test.edu",
            college_id="CSE-104",
            member_names=["Eve"],
            num_participants=1,
        )
        assert res["success"] is True
        code = res["team_code"]

        sess = db.get_or_create_session(code)
        assert sess is not None
        assert sess["team_code"] == code
        assert sess["status"] == "active"
        assert sess["current_round"] == 1
        assert sess["total_score"] == 0

        # Update session
        db.update_session(code, {"total_score": 30, "correct_answers": 3})
        sess_updated = db.get_session(code)
        assert sess_updated["total_score"] == 30
        assert sess_updated["correct_answers"] == 3


class TestDatabaseAttemptsAndScoring:
    def test_record_attempt_and_idempotency(self):
        tname = _rand_name("AttemptTesters")
        res = db.register_team(
            team_name=tname,
            captain_name="Frank",
            captain_email="frank@test.edu",
            college_id="CSE-105",
            member_names=["Frank"],
            num_participants=1,
        )
        assert res["success"] is True
        code = res["team_code"]
        sess = db.get_or_create_session(code)
        sid = sess["id"]

        # 1. Wrong attempt
        att1 = db.record_attempt(
            team_code=code,
            session_id=sid,
            round_number=1,
            question_index=0,
            submitted_answer="WRONG",
            is_correct=False,
            points_awarded=0,
            hint_used=False,
        )
        assert att1.get("already_solved") is False
        assert att1["attempt_number"] == 1
        assert db.get_attempt_count(code, 1, 0) == 1
        assert db.is_question_solved(code, 1, 0) is False

        # 2. Correct attempt
        att2 = db.record_attempt(
            team_code=code,
            session_id=sid,
            round_number=1,
            question_index=0,
            submitted_answer="CORRECT",
            is_correct=True,
            points_awarded=10,
            hint_used=False,
        )
        assert att2.get("already_solved") is False
        assert att2["attempt_number"] == 2
        assert db.is_question_solved(code, 1, 0) is True

        sess_after = db.get_session(code)
        assert sess_after["total_score"] == 10
        assert sess_after["correct_answers"] == 1

        # 3. Duplicate correct attempt — should NOT re-award points
        att3 = db.record_attempt(
            team_code=code,
            session_id=sid,
            round_number=1,
            question_index=0,
            submitted_answer="CORRECT",
            is_correct=True,
            points_awarded=10,
            hint_used=False,
        )
        assert att3.get("already_solved") is True
        sess_dup = db.get_session(code)
        assert sess_dup["total_score"] == 10  # Score remains 10, no duplication


class TestDatabaseRoundsAndLeaderboard:
    def test_complete_round_and_leaderboard(self):
        tname = _rand_name("RoundChamps")
        res = db.register_team(
            team_name=tname,
            captain_name="Grace",
            captain_email="grace@test.edu",
            college_id="CSE-106",
            member_names=["Grace"],
            num_participants=1,
        )
        assert res["success"] is True
        code = res["team_code"]
        sess = db.get_or_create_session(code)
        sid = sess["id"]

        # Complete round 1
        ok = db.complete_round(code, sid, 1, 30, "FR-1111")
        assert ok is True

        completed = db.get_completed_round_numbers(code)
        assert 1 in completed

        # Verify session advanced to round 2
        sess_r2 = db.get_session(code)
        assert sess_r2["current_round"] == 2

        # Upsert leaderboard
        db.upsert_leaderboard(code, tname, sess_r2)
        lb = db.get_leaderboard()
        found = any(row["team_name"] == tname for row in lb)
        assert found is True


class TestClubMembersManagement:
    def test_add_edit_delete_club_member(self):
        # Add with usn
        mid = db.add_club_member(
            name="New Hacker",
            role="Specialist",
            usn="1VA23CS999",
            bio="Security enthusiast",
            photo_path="assets/team/test_photo.png",
            display_order=15,
        )
        assert mid > 0

        member = db.get_club_member(mid)
        assert member is not None
        assert member["name"] == "New Hacker"
        assert member["usn"] == "1VA23CS999"
        assert member["photo_path"] == "assets/team/test_photo.png"

        # Update
        ok = db.update_club_member(
            member_id=mid,
            name="New Hacker Updated",
            role="Lead Specialist",
            usn="1VA23CS888",
            bio="Updated bio",
            photo_path="assets/team/updated.png",
            display_order=20,
        )
        assert ok is True
        m_updated = db.get_club_member(mid)
        assert m_updated["name"] == "New Hacker Updated"
        assert m_updated["role"] == "Lead Specialist"
        assert m_updated["usn"] == "1VA23CS888"
        assert m_updated["photo_path"] == "assets/team/updated.png"

        # Delete
        db.delete_club_member(mid)
        assert db.get_club_member(mid) is None

    def test_student_coordinators_seeded(self):
        members = db.get_club_members()
        expected = [
            ("Mahima K", "1VA23CS092", "President"),
            ("Samyak D Karekar", "1VA24CS0121", "Vice President"),
            ("Shalini M Gowda", "1VA24CS125", "Joint Secretary"),
            ("Shankar SB", "1VA23CS145", "Social Media"),
            ("Aadita Nag", "1VA23CS001", "Treasurer"),
            ("Kavyashree SN", "1VA24CS064", "Documentation Lead"),
            ("Harshitha N", "1VA24CS055", "Membership Coordinator"),
            ("Suhail D Tamboli", "1VA23CS195", "Membership Coordinator"),
            ("Jagadeesha", "1VA23CS065", "Secretary"),
        ]
        mem_map = {m["name"]: m for m in members}
        for name, usn, role in expected:
            assert name in mem_map, f"Missing member: {name}"
            assert mem_map[name]["usn"] == usn, f"USN mismatch for {name}: expected {usn}, got {mem_map[name]['usn']}"
            assert mem_map[name]["role"] == role, f"Role mismatch for {name}: expected {role}, got {mem_map[name]['role']}"


class TestFacultyProfilesManagement:
    def test_faculty_coordinators_seeded(self):
        faculty = db.get_faculty_profiles()
        assert len(faculty) >= 3

        expected_faculty = {
            "Dr. Varun E": {
                "designation": "Associate Professor",
                "photo_path": "assets/faculty/dr_varun_e.jpg",
            },
            "Prof Ramanjinamma G": {
                "designation": "Assistant Professor",
                "photo_path": "assets/faculty/prof_ramanjinamma_g.jpg",
            },
            "Prof Lalitha K": {
                "designation": "Assistant Professor",
                "photo_path": "assets/faculty/prof_lalitha_k.jpg",
            },
        }

        fac_map = {f["name"]: f for f in faculty}
        for name, expected in expected_faculty.items():
            assert name in fac_map, f"Missing faculty: {name}"
            assert fac_map[name]["designation"] == expected["designation"]
            assert fac_map[name]["photo_path"] == expected["photo_path"]

    def test_update_faculty_profile(self):
        faculty = db.get_faculty_profiles()
        target = faculty[0]
        fid = target["id"]
        orig_desc = target.get("description", "")

        ok = db.update_faculty_profile(
            faculty_id=fid,
            name=target["name"],
            designation=target["designation"],
            description="Leading CSE research initiative.",
            expertise="Artificial Intelligence, Distributed Systems",
            photo_path=target.get("photo_path"),
        )
        assert ok is True

        updated_list = db.get_faculty_profiles()
        updated_fac = next(f for f in updated_list if f["id"] == fid)
        assert updated_fac["description"] == "Leading CSE research initiative."
        assert updated_fac["expertise"] == "Artificial Intelligence, Distributed Systems"

        # Revert description
        db.update_faculty_profile(
            faculty_id=fid,
            name=target["name"],
            designation=target["designation"],
            description=orig_desc,
            expertise=target.get("expertise", ""),
            photo_path=target.get("photo_path"),
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
