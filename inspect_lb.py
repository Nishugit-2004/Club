"""Inspect leaderboard data and all teams."""
from database.db import get_leaderboard, get_all_teams_with_sessions

lb = get_leaderboard(50)
print(f"Total leaderboard entries: {len(lb)}")
for r in lb:
    print(r)

print()
teams = get_all_teams_with_sessions()
print(f"Total registered teams: {len(teams)}")
for t in teams:
    sess = t.get("session") or {}
    lb_entry = t.get("leaderboard") or {}
    print(
        f"  Team: {t['team_name']} | "
        f"Session score: {sess.get('total_score', 0)} | "
        f"Session status: {sess.get('status', 'no-session')} | "
        f"LB score: {lb_entry.get('final_score', 'not on LB')}"
    )
