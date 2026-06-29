# -*- coding: utf-8 -*-
"""Fix USA destinations and verify results"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Map USA images based on type
USA_IMAGES = {
    "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
    "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Statue_of_Liberty%2C_NY.jpg/1280px-Statue_of_Liberty%2C_NY.jpg",
    "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Miami_Beach_Florida_USA.jpg/1280px-Miami_Beach_Florida_USA.jpg",
    "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
    "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Statue_of_Liberty%2C_NY.jpg/1280px-Statue_of_Liberty%2C_NY.jpg",
    "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
}

TYPE_BROADER_MAP = {
    "Beach": "Beach", "Nature": "Nature", "Heritage": "Heritage",
    "Cultural": "Heritage", "Religious": "Religious", "Adventure": "Adventure",
    "City": "Heritage", "Mountain": "Nature", "Wildlife": "Nature", "Luxury": "Beach",
}

usa_dests = list(db.destinations.find({'Country': 'USA'}))
print(f"USA destinations: {len(usa_dests)}")

updated = 0
for dest in usa_dests:
    dest_type = dest.get('Type', '')
    broader_type = dest.get('Broader_Type', '')
    type_key = TYPE_BROADER_MAP.get(dest_type, TYPE_BROADER_MAP.get(broader_type, 'default'))
    new_image = USA_IMAGES.get(type_key, USA_IMAGES['default'])
    db.destinations.update_one({'_id': dest['_id']}, {'$set': {'image': new_image}})
    updated += 1

print(f"Updated {updated} USA destinations")

# Verify - show 10 sample destinations
print("\n--- Verification: Sample destinations ---")
samples = list(db.destinations.find({}).limit(10))
for s in samples:
    name = s.get('Destination Name', s.get('destination', 'N/A'))
    country = s.get('Country', 'N/A')
    img = s.get('image', 'NO IMAGE')[:80]
    print(f"{name} | {country} | {img}")
