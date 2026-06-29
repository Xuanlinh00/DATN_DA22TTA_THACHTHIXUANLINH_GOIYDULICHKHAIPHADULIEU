# -*- coding: utf-8 -*-
import sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

test_cases = [
    ("Japan Beach", "1526481280693-3bfa7568e0f3"),
    ("Morocco Beach", "1551410624-56ef00fa4c6e"),
    ("Brazil City", "1518639192441-dc48c36bf060"),
    ("Germany Nature", "1485628483296-6af69ab76f68"),
    ("USA Adventure", "1474044159687-1ee9f3a51722"),
    ("Vietnam Beach", "1528127269322-539801943592"),
    ("Italy Colosseum", "1552832230-c0197dd311b5"),
    ("India Taj Mahal", "1564507592333-c60657eea523"),
    ("France Eiffel", "1502602898657-3e91760cbb34"),
    ("Thailand Beach", "1504214212580-049572a9a3be"),
    ("Greece Santorini", "1570077188670-e3a8d69ac5ff"),
    ("Japan Kinkaku-ji", "1542051841857-5f90071e7989"),
    ("Egypt Pyramids", "1553913861-c0fddf2619ee"),
    ("Australia Uluru", "1529528744093-6f8abeee511d"),
    ("Morocco Sahara", "1518548419970-58e3b4079ab2"),
]

ok = fail = 0
for name, photo_id in test_cases:
    url = f"https://images.unsplash.com/photo-{photo_id}?w=400&q=80"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=8)
        ct = r.headers.get('Content-Type','')
        print(f"OK  [{ct[:10]}] {name}")
        ok += 1
    except Exception as e:
        print(f"FAIL {name}: {e}")
        fail += 1

print(f"\n{ok} OK, {fail} FAIL out of {len(test_cases)}")
