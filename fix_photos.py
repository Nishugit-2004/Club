"""Fix photo paths in the database to match actual asset files."""
from database.db import get_db
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()
with get_db() as conn:
    # Faculty - map names to actual files
    conn.execute("UPDATE faculty_profiles SET photo_path = ?, updated_at = ? WHERE display_order = ?",
                 ("assets/faculty/varun.png", now, 1))
    conn.execute("UPDATE faculty_profiles SET photo_path = ?, updated_at = ? WHERE display_order = ?",
                 ("assets/faculty/rama.png", now, 2))
    conn.execute("UPDATE faculty_profiles SET photo_path = ?, updated_at = ? WHERE display_order = ?",
                 ("assets/faculty/lalitha.png", now, 3))
    # Student members - map known photos
    conn.execute("UPDATE club_members SET photo_path = ?, updated_at = ? WHERE name = ?",
                 ("assets/team/suhail.png", now, "Suhail D Tamboli"))

print("DB photo paths updated successfully!")
