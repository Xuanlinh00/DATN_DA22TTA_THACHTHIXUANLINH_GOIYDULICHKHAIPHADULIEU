# -*- coding: utf-8 -*-
"""Fix the 7 failed Wikipedia lookups with alternative article titles + verified URLs."""
import sys, json, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

def get_wiki_image(article_title):
    encoded = urllib.parse.quote(article_title.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TravelApp/1.0', 'Accept': 'application/json'})
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read().decode('utf-8'))
        orig = data.get('originalimage', {})
        thumb = data.get('thumbnail', {})
        import re
        if orig.get('source'):
            return orig['source']
        if thumb.get('source'):
            return re.sub(r'/\d+px-', '/1280px-', thumb['source'])
    except Exception as e:
        print(f"  Error: {e}")
    return None

# Alternative article names for the 7 failed ones
ALTERNATIVES = {
    ("Brazil", "City"):       ["Rio de Janeiro", "Corcovado"],
    ("Canada", "Religious"):  ["Notre-Dame Basilica (Montreal)", "Montreal"],
    ("Greece", "Beach"):      ["Zakynthos", "Greek islands"],
    ("Morocco", "City"):      ["Marrakesh", "Medina of Marrakesh"],
    ("Peru", "City"):         ["Lima", "Lima Metropolitan Area"],
    ("USA", "Beach"):         ["Miami Beach, Florida", "Miami Beach"],
    ("Vietnam", "Historical"): ["Hoi An", "Ancient Town of Hoi An"],
}

print("Fixing 7 failed combinations...")
fixed = 0
for (country, dtype), articles in ALTERNATIVES.items():
    url = None
    for article in articles:
        print(f"  Trying: {article}")
        url = get_wiki_image(article)
        if url:
            print(f"  Found: {url[:80]}")
            break
    
    if url:
        result = db.destinations.update_many(
            {'Country': country, 'Type': dtype},
            {'$set': {'image': url}}
        )
        print(f"  Updated {result.modified_count} destinations for {country}|{dtype}")
        fixed += result.modified_count
    else:
        print(f"  STILL FAILED: {country}|{dtype}")

print(f"\nFixed {fixed} additional destinations")

# Final verification - check all sample types
print("\n=== FINAL VERIFICATION ===")
samples = [
    ("Japan", "Beach"), ("Japan", "City"), ("Japan", "Religious"),
    ("Morocco", "Beach"), ("Morocco", "City"), ("Morocco", "Adventure"),
    ("Brazil", "City"), ("Brazil", "Beach"), ("Brazil", "Religious"),
    ("Vietnam", "Beach"), ("Vietnam", "Historical"), ("Vietnam", "City"),
    ("Germany", "Nature"), ("Germany", "Historical"), ("Germany", "City"),
    ("India", "Historical"), ("USA", "Adventure"), ("France", "City"),
]
for country, dtype in samples:
    d = db.destinations.find_one({'Country': country, 'Type': dtype})
    if d:
        img = d.get('image', 'NO IMAGE')
        print(f"  {country:<15} {dtype:<12}: {img[:80]}")

print("\nDone! Please refresh the browser (Ctrl+F5).")
