"""Generate JS IMAGES_BY_TYPE from wikimedia_verified.json."""
import json

with open("wikimedia_verified.json", "r", encoding="utf-8") as f:
    data = json.load(f)

import sys
sys.stdout.reconfigure(encoding='utf-8')
print("// CURATED IMAGES BY TYPE: Wikimedia Commons verified photos")
print("const IMAGES_BY_TYPE = {")

for cat in ["waterfall", "beach", "mountain", "cultural", "nature", "adventure", "historical", "religious", "urban", "default"]:
    imgs = data.get(cat, [])
    print(f"  {cat}: [")
    for img in imgs:
        url = img["thumb"]
        # Use 960px width for better quality
        url = url.replace("/600px-", "/960px-").replace("/thumb/", "/thumb/")
        # Escape single quotes in URL
        url = url.replace("'", "\\'")
        print(f"    '{url}',")
    print(f"  ],")

print("};")
