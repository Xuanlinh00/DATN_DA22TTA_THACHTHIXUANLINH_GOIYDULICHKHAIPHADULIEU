# -*- coding: utf-8 -*-
"""Sample some duplicate images to see what's happening"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

if not db_storage.is_connected():
    print("Database not connected")
    exit(1)

destinations = db_storage.load_destinations()

image_groups = defaultdict(list)

for dest in destinations:
    image_url = dest.get("image", "")
    dest_name = dest.get("Destination Name", "")
    country = dest.get("Country", "")
    
    if image_url and isinstance(image_url, str) and image_url.strip():
        image_groups[image_url].append({
            "name": dest_name,
            "country": country
        })

# Find ALL duplicates
count = 0
for url, dests in image_groups.items():
    if len(dests) > 1:
        count += 1
        print(f"\nDuplicate #{count}:")
        print(f"URL: {url}")
        print(f"Destinations ({len(dests)}):")
        for d in dests:
            print(f"  - {d['name']} ({d['country']})")
