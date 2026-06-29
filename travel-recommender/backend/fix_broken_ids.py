# -*- coding: utf-8 -*-
"""Fix the 4 broken Unsplash IDs and update MongoDB"""
import sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

def u(photo_id):
    return f"https://images.unsplash.com/photo-{photo_id}?w=1280&q=80&fit=crop"

def test_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=8)
        ct = r.headers.get('Content-Type','')
        return 'image' in ct
    except:
        return False

# Fix the broken ones + improve others
FIXES = {
    # Morocco Beach - 1551410624-56ef00fa4c6e was 404
    ("Morocco", "Beach"):    u("1539020140153-6f9c7f89ecfe"),  # Agadir/Morocco coast

    # Brazil City - 1518639192441-dc48c36bf060 was 404
    ("Brazil", "City"):      u("1483729600049-1516b81b6f11"),  # Rio de Janeiro skyline

    # Germany Nature - 1485628483296-6af69ab76f68 was 404
    ("Germany", "Nature"):   u("1467621233048-3e57db1b6dd6"),  # German forest

    # Thailand Beach - 1504214212580-049572a9a3be was 404
    ("Thailand", "Beach"):   u("1528181304800-259b08848526"),  # Phi Phi Islands

    # Additional improvements for better accuracy:
    ("China", "Historical"): u("1508804185872-173106a94b53"),  # Great Wall China
    ("Morocco", "City"):     u("1539020140153-6f9c7f89ecfe"),  # Marrakech souk
    ("Peru", "Historical"):  u("1526772662643-74532e786f92"),  # Machu Picchu
    ("New Zealand", "Nature"): u("1491555103944-7c647fd857e6"),  # Milford Sound NZ
    ("South Africa", "City"): u("1504916122839-c38b0abb0f7d"),  # Cape Town
    ("Kenya", "Adventure"):  u("1516426122078-a0a584ac26c5"),  # Safari Kenya lion
    ("Vietnam", "City"):     u("1583417267826-aebc4d1542e1"),  # Ho Chi Minh City
}

print("Testing and applying fixes...")
for (country, dtype), url in FIXES.items():
    ok = test_url(url)
    status = "OK" if ok else "FAIL"
    print(f"  [{status}] {country}|{dtype}: {url[35:75]}")
    if ok:
        result = db.destinations.update_many(
            {'Country': country, 'Type': dtype},
            {'$set': {'image': url}}
        )
        print(f"         → Updated {result.modified_count} destinations")

print("\nDone!")
