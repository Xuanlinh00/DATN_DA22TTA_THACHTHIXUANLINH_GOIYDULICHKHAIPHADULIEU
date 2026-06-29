import csv, json
from collections import defaultdict

rows = list(csv.DictReader(open('destinations_clean.csv', 'r', encoding='utf-8')))

# Extract unique image URLs grouped by country
country_images = defaultdict(list)
country_type_images = defaultdict(lambda: defaultdict(list))

for r in rows:
    img = r.get('image', '').strip()
    country = r.get('Country', '').strip()
    dtype = r.get('Type', '').strip()
    name = r.get('Destination Name', '').strip()
    if img and img.startswith('http') and country:
        country_images[country].append(img)
        country_type_images[country][dtype].append(img)

# Deduplicate
for c in country_images:
    country_images[c] = list(dict.fromkeys(country_images[c]))

for c in country_type_images:
    for t in country_type_images[c]:
        country_type_images[c][t] = list(dict.fromkeys(country_type_images[c][t]))

print("=== IMAGES PER COUNTRY ===")
for c in sorted(country_images.keys()):
    print(f"  {c:15s} -> {len(country_images[c])} unique images")

print(f"\nTotal unique images: {sum(len(v) for v in country_images.values())}")

# Output as JSON for use in JS
output = {}
for c in sorted(country_type_images.keys()):
    output[c] = {}
    for t in sorted(country_type_images[c].keys()):
        output[c][t] = country_type_images[c][t][:10]  # max 10 per type

with open('country_type_image_pools.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nWrote country_type_image_pools.json")
