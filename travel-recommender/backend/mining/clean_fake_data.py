# -*- coding: utf-8 -*-
"""
Clean Fake Data Script - Removes generic/fake destinations from CSV files and MongoDB.
"""
import sys
import os
import pandas as pd
from pathlib import Path

# Setup paths to import from backend modules
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from mining.mongodb_storage import db_storage

def is_generic_name(name):
    """Check if a destination name is generic/fictional."""
    if not isinstance(name, str):
        return False
        
    generic_prefixes = ['Crystal', 'Golden', 'Grand', 'Lush', 'Mystic', 'Sacred', 'Serene', 'Hidden', 'Ancient']
    generic_suffixes = [
        'Hidden Valley Trail', 'Ancient Royal Palace', 'Coastal Horizon Beach', 
        'Summit Peak Adventure', 'Valley', 'Beach', 'Canyon', 'Falls', 'Forest',
        'Pagoda', 'Park', 'Plaza', 'Ruins', 'Temple',
    ]
    
    parts = name.split(' ')
    # Check "Prefix + Suffix" pattern like "Golden Temple", "Mystic Ruins"
    if len(parts) == 2 and parts[0] in generic_prefixes:
        return True
    
    # Check country + generic suffix like "Sweden Hidden Valley Trail"
    for suffix in generic_suffixes:
        if name.endswith(suffix) and len(name) > len(suffix):
            return True
            
    return False

def clean_csv_file(csv_path):
    """Filters generic destinations out of a CSV file and saves it back."""
    if not csv_path.exists():
        print(f"[WARNING] CSV file not found: {csv_path}")
        return
        
    print(f"[CLEANUP] Processing CSV: {csv_path.name}")
    df = pd.read_csv(csv_path)
    initial_len = len(df)
    
    # Filter out generic destinations
    df_clean = df[df['Destination Name'].apply(lambda x: not is_generic_name(x))]
    final_len = len(df_clean)
    
    df_clean.to_csv(csv_path, index=False)
    print(f"[CLEANUP] CSV {csv_path.name} cleaned: {initial_len} -> {final_len} (removed {initial_len - final_len} records)")

def main():
    print("[CLEANUP] Starting data cleanup process...")
    
    # 1. Clean CSV files
    processed_dir = BASE_DIR / "data" / "processed"
    dest_clustered_csv = processed_dir / "destinations_clustered.csv"
    dest_clean_csv = processed_dir / "destinations_clean.csv"
    
    clean_csv_file(dest_clustered_csv)
    clean_csv_file(dest_clean_csv)
    
    # 2. Clean MongoDB collections
    if not db_storage.is_connected():
        print("[ERROR] MongoDB is not connected! Cannot update database.")
        sys.exit(1)
        
    print("\n[CLEANUP] Cleaning MongoDB collections...")
    
    # a. Load existing destinations from DB
    destinations = list(db_storage.db.destinations.find({}))
    initial_db_len = len(destinations)
    
    real_destinations = [d for d in destinations if not is_generic_name(d.get('Destination Name'))]
    final_db_len = len(real_destinations)
    
    # Save clean destinations back to MongoDB (this drops the collection first)
    # Remove MongoDB's '_id' field before saving so new ones are generated cleanly
    for rd in real_destinations:
        rd.pop('_id', None)
        
    db_storage.save_destinations(real_destinations)
    print(f"[CLEANUP] destinations collection cleaned: {initial_db_len} -> {final_db_len} (removed {initial_db_len - final_db_len} records)")
    
    # b. Clean user_ratings collection
    ratings = list(db_storage.db.user_ratings.find({}))
    initial_ratings_len = len(ratings)
    
    generic_ratings_dest_names = []
    for r in ratings:
        dest_name = r.get('destination_name')
        if is_generic_name(dest_name):
            generic_ratings_dest_names.append(dest_name)
            
    if generic_ratings_dest_names:
        # Deduplicate
        generic_ratings_dest_names = list(set(generic_ratings_dest_names))
        # Delete matching ratings
        result = db_storage.db.user_ratings.delete_many({"destination_name": {"$in": generic_ratings_dest_names}})
        print(f"[CLEANUP] user_ratings collection cleaned: removed {result.deleted_count} ratings for generic destinations")
    else:
        print("[CLEANUP] user_ratings collection: no generic destination ratings to remove")
        
    # c. Drop unused destination_clusters collection if it exists
    if 'destination_clusters' in db_storage.db.list_collection_names():
        db_storage.db.destination_clusters.drop()
        print("[CLEANUP] Dropped unused destination_clusters collection")
        
    print("\n[CLEANUP] Data cleanup completed successfully!")

if __name__ == "__main__":
    main()
