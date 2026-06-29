# -*- coding: utf-8 -*-
"""
Test different Unsplash URL formats to find what works.
"""
import sys, urllib.request
sys.stdout.reconfigure(encoding='utf-8')

# Test known working IDs first
working_ids = [
    "1474044159687-1ee9f3a51722",  # Grand Canyon - confirmed OK
    "1528127269322-539801943592",  # Ha Long Bay - confirmed OK
    "1552832230-c0197dd311b5",     # Colosseum - confirmed OK
    "1564507592333-c60657eea523",  # Taj Mahal - confirmed OK
    "1502602898657-3e91760cbb34",  # Eiffel Tower - confirmed OK
    "1570077188670-e3a8d69ac5ff",  # Santorini - confirmed OK
    "1542051841857-5f90071e7989",  # Kinkaku-ji - confirmed OK
    "1553913861-c0fddf2619ee",     # Pyramids - confirmed OK
]

# Test broken ones with different approaches
test_ids = [
    # Morocco beach options
    ("Morocco coast", "1496442932756-8be6ce879e80"),
    ("Morocco beach2", "1527254388049-fad85ed3d849"),
    ("Morocco3", "1542574271-7f3b92e6c821"),
    # Brazil city options
    ("Brazil rio1", "1483729600049-1516b81b6f11"),
    ("Brazil rio2", "1598431850616-3de3b63cce00"),
    ("Brazil rio3", "1505850557893-8d580ba1e67e"),
    # Germany forest
    ("Germany forest1", "1507003211169-0a1dd7228f2d"),
    ("Germany forest2", "1542621334-8427b2b7bf7e"),
    # Kenya safari
    ("Kenya lion1", "1547471080-72555699c34c"),
    ("Kenya lion2", "1500662985866-10e00e3b56c3"),
    # South Africa
    ("Cape Town1", "1576485290814-1c72aa4bbb8e"),
    ("Cape Town2", "1495567960429-29cf8ee76cb0"),
    # China Great Wall
    ("China wall1", "1508804185872-173106a94b53"),
    ("China wall2", "1547471080-72555699c34c"),
]

print("Testing potential replacement IDs...")
for name, photo_id in test_ids:
    url = f"https://images.unsplash.com/photo-{photo_id}?w=400&q=80"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        r = urllib.request.urlopen(req, timeout=6)
        ct = r.headers.get('Content-Type','')
        print(f"  OK  [{ct[:10]}] {name} -> {photo_id}")
    except Exception as e:
        print(f"  FAIL {name} -> {photo_id}: {str(e)[:40]}")
