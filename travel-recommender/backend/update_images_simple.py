# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage
from services.image_service import get_image_service

print("Updating images...")

if not db_storage.is_connected():
    print("DB not connected")
    sys.exit(1)

collection = db_storage.db["destinations"]
image_service = get_image_service(db_storage)

destinations = list(collection.find({}))
total = len(destinations)

for i, dest in enumerate(destinations, 1):
    name = dest.get("Destination Name", "")
    country = dest.get("Country", "")
    dest_type = dest.get("Type", "")
    
    image_url = image_service.get_destination_image(name, country, dest_type)
    
    collection.update_one(
        {"Destination Name": name},
        {"$set": {"image": image_url}}
    )
    
    if i % 100 == 0:
        print(f"Progress: {i}/{total}")

print(f"Done! Updated {total} destinations")
