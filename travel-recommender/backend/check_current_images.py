# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']
destinations = list(db.destinations.find({}, {'Destination Name': 1, 'image': 1, 'Country': 1, 'Type': 1}))

print(f"Total destinations: {len(destinations)}")
print("\n--- First 50 destinations with images ---")
for d in destinations[:50]:
    name = d.get('Destination Name', 'N/A')
    country = d.get('Country', 'N/A')
    dtype = d.get('Type', 'N/A')
    img = d.get('image', '')
    img_short = img[:100] if img else 'NO IMAGE'
    print(f"{name:<45} | {country:<15} | {dtype:<12} | {img_short}")
