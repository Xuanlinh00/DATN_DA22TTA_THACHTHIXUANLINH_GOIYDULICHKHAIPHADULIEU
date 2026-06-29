# -*- coding: utf-8 -*-
"""
Filter synthetic destinations to only real landmarks and update MongoDB.
Uses real_landmarks_mapping.json to rename synthetic names to real ones.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from mining.mongodb_storage import db_storage

MAPPING_FILE = Path(__file__).parent / "data" / "processed" / "real_landmarks_mapping.json"

def main():
    # Load mapping
    with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    print(f"Loaded {len(mapping)} mapping entries")

    # Connect to MongoDB
    db_storage.connect()
    coll = db_storage.db.destinations

    # Get all current destinations
    all_dests = list(coll.find({}))
    print(f"Current destinations in MongoDB: {len(all_dests)}")

    # Filter and rename
    seen_real_names = set()
    new_docs = []
    for doc in all_dests:
        name = doc.get('Destination Name', '')
        if name in mapping:
            real_name = mapping[name]
            if real_name in seen_real_names:
                continue  # skip duplicate
            seen_real_names.add(real_name)
            doc['Destination Name'] = real_name
            # Remove MongoDB _id so we can re-insert cleanly
            doc.pop('_id', None)
            new_docs.append(doc)

    print(f"Real destinations after dedup: {len(new_docs)}")
    print()
    print("Sample destinations:")
    for d in new_docs[:10]:
        print(f"  {d['Destination Name']} | {d.get('Country','')} | {d.get('Type','')}")

    # Replace collection
    coll.drop()
    if new_docs:
        coll.insert_many(new_docs)
    final_count = coll.count_documents({})
    print(f"\nMongoDB updated: {final_count} destinations")

    # Also save filtered CSV for engine fallback
    import csv
    csv_path = Path(__file__).parent / "data" / "processed" / "destinations_real.csv"
    if new_docs:
        fields = list(new_docs[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(new_docs)
        print(f"Saved filtered CSV: {csv_path}")

if __name__ == '__main__':
    main()
