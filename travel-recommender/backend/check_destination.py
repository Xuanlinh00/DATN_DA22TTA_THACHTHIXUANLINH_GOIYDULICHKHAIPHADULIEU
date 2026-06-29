# -*- coding: utf-8 -*-
"""
Check destination data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage
import json

def check_destination(name):
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    dest = collection.find_one({"Destination Name": name})
    
    if dest:
        # Remove _id for display
        if "_id" in dest:
            dest["_id"] = str(dest["_id"])
        
        print(json.dumps({
            "Destination Name": dest.get("Destination Name"),
            "Country": dest.get("Country"),
            "Type": dest.get("Type"),
            "destination_latitude": dest.get("destination_latitude"),
            "destination_longitude": dest.get("destination_longitude"),
            "country_latitude": dest.get("country_latitude"),
            "country_longitude": dest.get("country_longitude"),
            "image": dest.get("image", "")[:100] + "..." if dest.get("image") else None
        }, indent=2, ensure_ascii=False))
    else:
        print(f"Không tìm thấy: {name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        check_destination(" ".join(sys.argv[1:]))
    else:
        check_destination("Lush Pagoda (Thailand)")
