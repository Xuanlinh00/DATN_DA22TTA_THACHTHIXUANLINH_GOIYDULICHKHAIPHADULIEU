import csv, json, re
from collections import defaultdict

rows = list(csv.DictReader(open('destinations_clean.csv', 'r', encoding='utf-8')))

# Extract unique photo IDs grouped by country+type
country_type_photos = defaultdict(lambda: defaultdict(list))

for r in rows:
    img = r.get('image', '').strip()
    country = r.get('Country', '').strip()
    dtype = r.get('Type', '').strip()
    if not img or not country or not dtype:
        continue
    # Extract photo ID: photo-XXXXXXXXXX-XXXXXXXXXXXX
    m = re.search(r'(photo-[0-9]+-[0-9a-f]+)', img)
    if m:
        photo_id = m.group(1)
        country_type_photos[country][dtype].append(photo_id)

# Deduplicate and limit to 6 per combo
output = {}
total = 0
for c in sorted(country_type_photos.keys()):
    output[c] = {}
    for t in sorted(country_type_photos[c].keys()):
        ids = list(dict.fromkeys(country_type_photos[c][t]))[:6]
        output[c][t] = ids
        total += len(ids)

with open('country_type_photo_ids.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"Total photo IDs: {total}")
print(f"File size: {len(json.dumps(output))} bytes")
