# -*- coding: utf-8 -*-
"""
Auto Image Fetcher - Searches Unsplash for each destination name and populates the dataset.
"""
import os
import re
import time
import urllib.request
import urllib.parse
import pandas as pd
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
CSV_FILES = [
    DATA_DIR / "destinations_clustered.csv",
    DATA_DIR / "destinations_clean.csv"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_unsplash_image(query):
    """Search Yahoo Images (Bing CDN) and return the first matching image URL"""
    url = f"https://images.search.yahoo.com/search/images?p={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
            # Find Bing CDN image urls in the HTML
            # Example: https://tse3.mm.bing.net/th?id=OIP....
            pattern = r'https://tse[0-9]\.mm\.bing\.net/th\?id=[a-zA-Z0-9\.\-\_&;=\?]+'
            matches = re.findall(pattern, html)
            
            if matches:
                # Replace HTML entities like &amp; if any
                img_url = matches[0].replace('&amp;', '&')
                return img_url
    except Exception as e:
        print(f"  [ERROR] Failed to fetch image for '{query}': {e}")
    return None

def process_datasets():
    print("[IMAGE_FETCHER] Starting automatic image fetching from Unsplash...")
    
    # We will process files
    for csv_path in CSV_FILES:
        if not csv_path.exists():
            print(f"[WARNING] File not found: {csv_path}")
            continue
            
        print(f"\n[IMAGE_FETCHER] Processing: {csv_path.name}")
        df = pd.read_csv(csv_path)
        
        # Ensure 'image' column exists
        if 'image' not in df.columns:
            df['image'] = None
            
        updated_count = 0
        
        # Iterating and fetching
        for idx, row in df.iterrows():
            dest_name = row['Destination Name']
            country = row['Country']
            current_img = row['image']
            
            # Skip if already has a custom image link (not null/nan)
            if pd.notnull(current_img) and str(current_img).strip().startswith("http"):
                continue
                
            query = f"{dest_name} {country} travel"
            print(f"-> Fetching image for: {dest_name}, {country}...", end="", flush=True)
            
            img_url = fetch_unsplash_image(query)
            if img_url:
                df.at[idx, 'image'] = img_url
                print(" [OK]")
                updated_count += 1
            else:
                print(" [FAILED]")
                
            # Avoid hammering Unsplash
            time.sleep(1.5)
            
        if updated_count > 0:
            df.to_csv(csv_path, index=False)
            print(f"[SUCCESS] Updated {updated_count} images in {csv_path.name}")
        else:
            print(f"[INFO] No updates needed for {csv_path.name}")
            
    print("\n[IMAGE_FETCHER] Seeding the updated data to MongoDB...")
    # Import and run seed
    try:
        from mongodb_storage import db_storage
        if db_storage.is_connected():
            db_storage.seed_all()
            print("[SUCCESS] Data successfully seeded to MongoDB!")
        else:
            print("[ERROR] MongoDB not running, cannot seed database automatically.")
    except Exception as e:
        print(f"[ERROR] Seeding failed: {e}")

if __name__ == "__main__":
    process_datasets()
