"""Test leaderboard sync and ranking logic."""
import sys
sys.path.insert(0, ".")
from database.db import sync_all_active_sessions_to_leaderboard, get_leaderboard

n = sync_all_active_sessions_to_leaderboard()
print(f"Synced {n} teams to leaderboard")

lb = get_leaderboard(50)
print(f"Leaderboard now has {len(lb)} entries:")
for r in lb:
    rank = r["rank"]
    name = r["team_name"]
    score = r["final_score"]
    rounds = r["rounds_completed"]
    status = r["status"]
    hints = r["hints_used"]
    ct = r["completion_time_seconds"]
    print(f"  Rank {rank}: {name} | Score={score} | Rounds={rounds} | Hints={hints} | Time={ct} | Status={status}")
