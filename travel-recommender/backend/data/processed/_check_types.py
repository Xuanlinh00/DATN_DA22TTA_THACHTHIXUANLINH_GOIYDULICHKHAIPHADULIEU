import csv
rows = list(csv.DictReader(open('destinations_clean.csv', 'r', encoding='utf-8')))

# Check destinations with specific name keywords
keywords = ['Pagoda', 'Canyon', 'Mystic', 'Hidden', 'Temple', 'Valley', 'Beach', 'Falls']
for r in rows:
    name = r['Destination Name']
    for kw in keywords:
        if kw in name:
            print(f"{name:40s} Type={r['Type']:12s} Country={r['Country']:12s} img={'yes' if r.get('image') else 'no'}")
            break

# Also count unique type values
print("\n=== TYPE DISTRIBUTION ===")
from collections import Counter
types = Counter(r['Type'] for r in rows)
for t, c in types.most_common():
    print(f"  {t:15s} -> {c} destinations")

# Count how many have name-keyword that doesn't match type
print("\n=== NAME-TYPE MISMATCHES ===")
mismatches = 0
for r in rows:
    name = r['Destination Name'].lower()
    dtype = r['Type'].lower()
    if 'pagoda' in name and dtype != 'religious':
        print(f"  MISMATCH: {r['Destination Name']:35s} has Type={r['Type']} (should be Religious)")
        mismatches += 1
    elif 'temple' in name and dtype != 'religious':
        print(f"  MISMATCH: {r['Destination Name']:35s} has Type={r['Type']} (should be Religious)")
        mismatches += 1
    elif 'canyon' in name and dtype not in ('nature', 'adventure'):
        print(f"  MISMATCH: {r['Destination Name']:35s} has Type={r['Type']} (should be Nature/Adventure)")
        mismatches += 1
    elif 'beach' in name and dtype != 'beach':
        print(f"  MISMATCH: {r['Destination Name']:35s} has Type={r['Type']} (should be Beach)")
        mismatches += 1
    elif 'falls' in name and dtype != 'nature':
        print(f"  MISMATCH: {r['Destination Name']:35s} has Type={r['Type']} (should be Nature)")
        mismatches += 1
    elif 'waterfall' in name and dtype != 'nature':
        print(f"  MISMATCH: {r['Destination Name']:35s} has Type={r['Type']} (should be Nature)")
        mismatches += 1

print(f"\nTotal mismatches: {mismatches}")
