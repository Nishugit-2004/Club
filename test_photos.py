"""Test that photo paths resolve correctly."""
from pages.about import _encode_image
from database.db import get_faculty_profiles, get_club_members

print("=== FACULTY PHOTO RESOLUTION ===")
for f in get_faculty_profiles():
    result = _encode_image(f["photo_path"])
    status = "OK (image found)" if result else "MISSING (placeholder will show)"
    print(f"  {f['name']}: {f['photo_path']} -> {status}")

print()
print("=== STUDENT MEMBER PHOTO RESOLUTION ===")
for m in get_club_members():
    result = _encode_image(m["photo_path"])
    status = "OK (image found)" if result else "placeholder"
    print(f"  {m['name']}: {repr(m['photo_path'])} -> {status}")
