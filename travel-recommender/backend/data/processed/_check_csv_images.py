import csv
rows = list(csv.DictReader(open('destinations_clean.csv', 'r', encoding='utf-8')))

# Check specific destinations from the screenshots
targets = ['Mystic Pagoda (China)', 'Hidden Canyon (China)', 'Grand Pagoda (China)', 
           'Lush Plaza (China)', 'Ancient Valley (China)']

print("=== CSV IMAGE URLs FOR TARGET DESTINATIONS ===")
for r in rows:
    name = r['Destination Name']
    if name in targets:
        img = r.get('image', '')
        print(f"{name:35s} Type={r['Type']:12s}")
        print(f"  image: {img[:120]}")
        print()

# Also show total stats
has_img = sum(1 for r in rows if r.get('image','').startswith('http'))
print(f"\nTotal destinations: {len(rows)}")
print(f"With valid image URL: {has_img}")
print(f"Without image: {len(rows) - has_img}")

# Show a sample of unique photo IDs in the CSV
import re
photo_ids = set()
for r in rows:
    img = r.get('image', '')
    m = re.search(r'(photo-[0-9]+-[0-9a-f]+)', img)
    if m:
        photo_ids.add(m.group(1))
print(f"Unique photo IDs in CSV: {len(photo_ids)}")
