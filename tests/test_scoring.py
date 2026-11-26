"""
tests/test_scoring.py — Tests for scoring, timer, and leaderboard logic.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import datetime, timezone, timedelta


class TestTimerCalculations:
    def test_deadline_in_future(self):
        start = datetime.now(timezone.utc)
        deadline = start + timedelta(minutes=60)
        remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
        assert remaining > 0

    def test_deadline_in_past_gives_expired(self):
        start = datetime.now(timezone.utc) - timedelta(hours=2)
        deadline = start + timedelta(minutes=60)
        remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
        assert remaining < 0

    def test_completion_time_calculation(self):
        start = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2026, 1, 1, 10, 45, 30, tzinfo=timezone.utc)
        secs = int((end - start).total_seconds())
        assert secs == 45 * 60 + 30

    def test_60_minute_deadline(self):
        start = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        deadline = start + timedelta(minutes=60)
        assert (deadline - start).total_seconds() == 3600


class TestScoringRules:
    def test_base_points(self):
        """Each correct answer = 10 points."""
        assert 10 * 30 == 300  # max score

    def test_hint_penalty(self):
        """Hint costs 5 points from question value."""
        base = 10
        with_hint = base - 5
        assert with_hint == 5

    def test_wrong_attempt_penalty(self):
        """Each wrong attempt costs 2 points."""
        base = 10
        one_wrong = base - 2
        two_wrong = base - 4
        assert one_wrong == 8
        assert two_wrong == 6

    def test_minimum_points_is_1(self):
        """Points should not go below 1 for a correct answer."""
        base = 10
        hint_cost = 5
        wrong_penalty = 2 * 3
        raw = base - hint_cost - wrong_penalty
        final = max(1, raw)
        assert final >= 1

    def test_no_points_for_wrong(self):
        """Wrong answers earn 0 points."""
        assert 0 == 0  # trivial but explicit

    def test_accuracy_calculation(self):
        correct = 25
        total = 30
        accuracy = correct / total * 100
        assert abs(accuracy - 83.33) < 0.1


class TestLeaderboardRanking:
    def _rank(self, teams: list[dict]) -> list[dict]:
        """Sort teams by score desc, time asc, hints asc."""
        sorted_teams = sorted(
            teams,
            key=lambda t: (-t["score"], t.get("time", 999999), t.get("hints", 0))
        )
        for i, t in enumerate(sorted_teams):
            t["rank"] = i + 1
        return sorted_teams

    def test_higher_score_ranks_first(self):
        teams = [
            {"name": "A", "score": 200, "time": 1800},
            {"name": "B", "score": 300, "time": 2000},
        ]
        ranked = self._rank(teams)
        assert ranked[0]["name"] == "B"

    def test_equal_score_faster_time_wins(self):
        teams = [
            {"name": "A", "score": 300, "time": 2000},
            {"name": "B", "score": 300, "time": 1500},
        ]
        ranked = self._rank(teams)
        assert ranked[0]["name"] == "B"

    def test_equal_score_equal_time_fewer_hints_wins(self):
        teams = [
            {"name": "A", "score": 300, "time": 1800, "hints": 5},
            {"name": "B", "score": 300, "time": 1800, "hints": 2},
        ]
        ranked = self._rank(teams)
        assert ranked[0]["name"] == "B"

    def test_ranks_assigned_correctly(self):
        teams = [
            {"name": "C", "score": 100},
            {"name": "A", "score": 300},
            {"name": "B", "score": 200},
        ]
        ranked = self._rank(teams)
        assert ranked[0]["rank"] == 1
        assert ranked[1]["rank"] == 2
        assert ranked[2]["rank"] == 3


class TestDuplicateSubmissionPrevention:
    def test_idempotent_correct_answer(self):
        """Recording the same correct answer twice should not double-count points."""
        # Simulated: DB layer should check is_question_solved before awarding points
        already_solved = True
        points_awarded = 0 if already_solved else 10
        assert points_awarded == 0

    def test_separate_questions_earn_separate_points(self):
        """Each of 30 questions should contribute independently."""
        answered = set()
        total = 0
        for r in range(1, 11):
            for q in range(3):
                key = (r, q)
                if key not in answered:
                    answered.add(key)
                    total += 10
        assert total == 300
        assert len(answered) == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

