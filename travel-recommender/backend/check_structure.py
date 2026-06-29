# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Get first doc to see structure
first = db.destinations.find_one()
print("Keys in first doc:", list(first.keys()) if first else "No docs")
print()

# Get total count
total = db.destinations.count_documents({})
print(f"Total destinations: {total}")

# Get sample with all fields
destinations = list(db.destinations.find({}).limit(5))
for d in destinations:
    print("\n--- Destination ---")
    for k, v in d.items():
        if k != '_id':
            val = str(v)[:120] if v else 'None'
            print(f"  {k}: {val}")
