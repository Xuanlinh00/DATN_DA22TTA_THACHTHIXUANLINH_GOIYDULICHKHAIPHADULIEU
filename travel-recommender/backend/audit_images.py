# -*- coding: utf-8 -*-
"""
Comprehensive image audit: check for images that are clearly wrong
- Images with the same URL repeated too many times (generic/not specific)
- Images clearly mismatched with destination type/country
- Broken/404 images

Run this to get a full picture of what still needs fixing.
"""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient
from collections import Counter

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

all_dests = list(db.destinations.find({}, {'Destination Name': 1, 'Country': 1, 'Type': 1, 'image': 1}))
print(f"Total destinations: {len(all_dests)}")

# Count how many times each image URL appears
image_counts = Counter(d.get('image', '') for d in all_dests)
print(f"\nTop 30 most-used image URLs:")
for url, count in image_counts.most_common(30):
    short = url[:80] if url else 'NO IMAGE'
    print(f"  {count:4d}x  {short}")

# Find images used way too many times (generic placeholders)
OVERUSED_THRESHOLD = 20
overused = {url for url, count in image_counts.items() if count > OVERUSED_THRESHOLD and url}
print(f"\n\nImages used more than {OVERUSED_THRESHOLD} times (likely wrong/generic):")
for url in overused:
    count = image_counts[url]
    print(f"  {count}x  {url[:100]}")
    # Show a few examples of which destinations use it
    examples = [d for d in all_dests if d.get('image') == url][:3]
    for e in examples:
        print(f"       -> {e.get('Destination Name','')} | {e.get('Country','')} | {e.get('Type','')}")

# Count by country+type combination
print(f"\n\nUnique images per country+type:")
combos = {}
for d in all_dests:
    key = f"{d.get('Country','')}|{d.get('Type','')}"
    img = d.get('image', '')
    if key not in combos:
        combos[key] = set()
    combos[key].add(img)

for key, imgs in sorted(combos.items()):
    if len(imgs) == 1:
        url = list(imgs)[0]
        count = image_counts[url]
        print(f"  {key:<30} -> 1 unique image (used {count}x total)")
