# -*- coding: utf-8 -*-
"""
Find all unique country+type combinations in the DB, then print them.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

pipeline = [
    {"$group": {"_id": {"country": "$Country", "type": "$Type"}, "count": {"$sum": 1}}},
    {"$sort": {"_id.country": 1, "_id.type": 1}}
]
results = list(db.destinations.aggregate(pipeline))
print(f"Total unique country+type combos: {len(results)}")
for r in results:
    print(f"  {r['_id']['country']} | {r['_id']['type']} | {r['count']} destinations")
