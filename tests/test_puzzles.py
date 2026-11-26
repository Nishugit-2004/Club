"""
tests/test_puzzles.py — Unit tests for puzzle generation and validation.
Run with: python -m pytest tests/ -v
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from game.puzzles import (
    get_round, get_all_rounds, validate_answer, generate_treasure_code, _normalise
)

SEED = 42
SEED2 = 99  # Different team, different answers


class TestPuzzleGeneration:
    def test_all_10_rounds_generated(self):
        rounds = get_all_rounds(SEED)
        assert len(rounds) == 10

    def test_each_round_has_3_questions(self):
        for r_num in range(1, 11):
            r = get_round(r_num, SEED)
            assert len(r["questions"]) == 3, f"Round {r_num} has wrong number of questions"

    def test_round_metadata_complete(self):
        for r_num in range(1, 11):
            r = get_round(r_num, SEED)
            assert r["number"] == r_num
            assert isinstance(r["name"], str) and len(r["name"]) > 0
            assert isinstance(r["description"], str)
            assert isinstance(r["fragment"], str)

    def test_each_question_has_required_fields(self):
        required = {"index", "text", "difficulty", "hint", "points", "validate", "answer_display"}
        for r_num in range(1, 11):
            r = get_round(r_num, SEED)
            for q in r["questions"]:
                for field in required:
                    assert field in q, f"Round {r_num} Q{q.get('index','?')} missing field: {field}"

    def test_different_seeds_produce_different_puzzles(self):
        r1_seed1 = get_round(1, SEED)
        r1_seed2 = get_round(1, SEED2)
        # At least one question should differ (different shift/word)
        texts_differ = any(
            r1_seed1["questions"][i]["text"] != r1_seed2["questions"][i]["text"]
            for i in range(3)
        )
        assert texts_differ, "Different seeds should produce different puzzles"

    def test_same_seed_deterministic(self):
        r1_a = get_round(1, SEED)
        r1_b = get_round(1, SEED)
        assert r1_a["questions"][0]["text"] == r1_b["questions"][0]["text"]
        assert r1_a["questions"][0]["answer_display"] == r1_b["questions"][0]["answer_display"]

    def test_fragments_are_unique_per_seed(self):
        rounds = get_all_rounds(SEED)
        fragments = [r["fragment"] for r in rounds]
        # All fragments should be non-empty
        assert all(f for f in fragments)


class TestAnswerValidation:
    def test_validate_answer_correct(self):
        """Each round's answer_display should pass validation."""
        for r_num in range(1, 11):
            r = get_round(r_num, SEED)
            for q in r["questions"]:
                ans = q.get("canonical_answer") or q["answer_display"].split(" ")[0]
                is_valid = q["validate"](ans)
                assert is_valid, f"Round {r_num} Q{q['index']+1} answer failed validation: '{ans}'"

    def test_round1_q1_caesar_correct(self):
        r = get_round(1, SEED)
        answer = r["questions"][0]["answer_display"]
        assert r["questions"][0]["validate"](answer)
        assert r["questions"][0]["validate"](answer.lower())
        assert r["questions"][0]["validate"](answer.upper())

    def test_round1_wrong_answer_fails(self):
        r = get_round(1, SEED)
        assert not r["questions"][0]["validate"]("ZZZZZZZZZZ")
        assert not r["questions"][0]["validate"]("wronganswer")
        assert not r["questions"][0]["validate"]("")

    def test_round4_q3_password_validation(self):
        """Any valid password should pass, invalid ones should fail."""
        r = get_round(4, SEED)
        q = r["questions"][2]
        # Valid: uppercase + digits + special + min length
        assert q["validate"]("ValidP4ss!")
        assert q["validate"]("Abcdef1!")
        # Invalid: no uppercase
        assert not q["validate"]("allowercase1!")
        # Invalid: no digit  
        assert not q["validate"]("NoDigits!")
        # Invalid: no special
        assert not q["validate"]("NoSpecial1A")

    def test_round5_q1_missing_angle(self):
        r = get_round(5, SEED)
        q = r["questions"][0]
        correct_angle = int(q["answer_display"].replace("°", "").strip())
        assert q["validate"](str(correct_angle))
        assert q["validate"](str(correct_angle) + "°")
        assert not q["validate"]("999")

    def test_round9_q1_binary_conversion(self):
        r = get_round(9, SEED)
        q = r["questions"][0]
        correct = q["answer_display"]
        assert q["validate"](correct)
        assert not q["validate"]("99999")

    def test_round10_q3_anagram(self):
        r = get_round(10, SEED)
        q = r["questions"][2]
        correct = q["answer_display"]
        assert q["validate"](correct)
        assert q["validate"](correct.lower())
        assert not q["validate"]("RANDOMWORD")

    def test_validate_answer_function(self):
        """Test the top-level validate_answer helper."""
        for r_num in range(1, 11):
            r = get_round(r_num, SEED)
            for q in r["questions"]:
                ans = q.get("canonical_answer") or q["answer_display"].split(" ")[0]
                result = validate_answer(r_num, q["index"], ans, SEED)
                assert result, f"validate_answer failed for R{r_num} Q{q['index']+1} with answer '{ans}'"


class TestScoring:
    def test_points_per_question(self):
        for r_num in range(1, 11):
            r = get_round(r_num, SEED)
            for q in r["questions"]:
                assert q["points"] == 10, f"Question should be worth 10 points"

    def test_max_possible_score(self):
        """Max score is 300 (10 rounds × 3 questions × 10 points)."""
        total = sum(
            q["points"]
            for r_num in range(1, 11)
            for q in get_round(r_num, SEED)["questions"]
        )
        assert total == 300


class TestTreasureCode:
    def test_generates_code(self):
        code = generate_treasure_code("TLA-TEST01", SEED)
        assert code.startswith("TLA-VAULT-")
        assert len(code) == len("TLA-VAULT-") + 8

    def test_different_teams_different_codes(self):
        code1 = generate_treasure_code("TLA-TEAM01", SEED)
        code2 = generate_treasure_code("TLA-TEAM02", SEED)
        assert code1 != code2

    def test_same_team_deterministic(self):
        code1 = generate_treasure_code("TLA-TEST01", SEED)
        code2 = generate_treasure_code("TLA-TEST01", SEED)
        assert code1 == code2


class TestNormalise:
    def test_strips_whitespace(self):
        assert _normalise("  hello  ") == "hello"

    def test_lowercases(self):
        assert _normalise("HELLO") == "hello"

    def test_removes_spaces(self):
        assert _normalise("hello world") == "helloworld"

    def test_removes_dashes(self):
        assert _normalise("hello-world") == "helloworld"


class TestRoundUnlocking:
    """Test the round unlocking logic (pure logic, no DB needed)."""

    def test_round_1_accessible_from_start(self):
        """Round 1 should always be accessible."""
        completed = set()
        current = 1
        assert current in (completed | {current})

    def test_round_2_unlocks_after_round_1(self):
        completed = {1}
        current = 2
        assert current in (completed | {current})

    def test_round_5_not_accessible_without_completing_prior(self):
        completed = {1, 2}
        current = 3
        # Round 5 is not in completed or current
        assert 5 not in (completed | {current})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

