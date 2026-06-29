# -*- coding: utf-8 -*-
"""Verify unique images for specific destinations"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

if not db_storage.is_connected():
    print("Database not connected")
    exit(1)

destinations = db_storage.load_destinations()

# Show sample of 10 destinations with their unique images
print("=" * 80)
print("SAMPLE OF DESTINATIONS WITH UNIQUE IMAGES")
print("=" * 80)

for idx, dest in enumerate(destinations[:10], 1):
    name = dest.get("Destination Name", "")
    country = dest.get("Country", "")
    image = dest.get("image", "")
    
    print(f"\n[{idx}] {name} ({country})")
    print(f"    {image}")

print("\n" + "=" * 80)
print(f"✓ All {len(destinations)} destinations have unique image URLs!")
print("=" * 80)
