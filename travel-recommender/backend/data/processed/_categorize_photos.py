import csv, json, re
from collections import defaultdict

rows = list(csv.DictReader(open('destinations_clean.csv', 'r', encoding='utf-8')))

def resolve_category(name):
    """Resolve image category from destination name keywords"""
    n = name.lower()
    if 'falls' in n or 'waterfall' in n: return 'waterfall'
    if 'beach' in n or 'coast' in n or 'island' in n or 'bay' in n: return 'beach'
    if 'temple' in n or 'pagoda' in n or 'shrine' in n or 'church' in n or 'mosque' in n or 'cathedral' in n: return 'religious'
    if 'ruins' in n or 'castle' in n or 'palace' in n or 'fort' in n or 'ancient' in n or 'historic' in n: return 'historical'
    if 'forest' in n or 'jungle' in n or 'canyon' in n or 'valley' in n or 'park' in n or 'lake' in n or 'mountain' in n or 'peak' in n: return 'nature'
    if 'plaza' in n or 'city' in n or 'urban' in n or 'market' in n or 'square' in n: return 'urban'
    return 'default'

# Extract photo IDs and categorize by NAME KEYWORDS (not CSV Type)
category_photos = defaultdict(list)
for r in rows:
    img = r.get('image', '').strip()
    name = r.get('Destination Name', '').strip()
    if not img or not name:
        continue
    m = re.search(r'photo-([0-9]+-[0-9a-f]+)', img)
    if m:
        photo_id = m.group(1)
        cat = resolve_category(name)
        category_photos[cat].append(photo_id)

# Deduplicate and limit
output = {}
for cat in sorted(category_photos.keys()):
    ids = list(dict.fromkeys(category_photos[cat]))
    output[cat] = ids
    print(f"  {cat:15s} -> {len(ids)} unique photos")

total = sum(len(v) for v in output.values())
print(f"\nTotal categorized photos: {total}")

with open('categorized_photo_ids.json', 'w') as f:
    json.dump(output, f, indent=2)

# Also generate JS code
print("\n=== JS CODE FOR IMAGES_BY_TYPE ===")
for cat, ids in sorted(output.items()):
    urls = [f"'https://images.unsplash.com/photo-{pid}?w=800&auto=format&fit=crop&q=60'" for pid in ids[:25]]
    print(f"  {cat}: [")
    for u in urls:
        print(f"    {u},")
    print(f"  ],")
