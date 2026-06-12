"""
Fetch real images for destinations from Wikipedia/Wikimedia Commons API.
Stores image URLs directly in MongoDB's `image` field for each destination.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import requests
import time
import urllib.parse
from pymongo import MongoClient
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path("backend/.env"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "travel_recommender")

SESSION = requests.Session()
SESSION.headers.update({
    'User-Agent': 'TravelRecommender/1.0 (Educational Project; contact: admin@example.com)',
    'Accept': 'application/json',
})


def get_commons_image(query):
    """Search Wikimedia Commons directly for media files (images) matching the query."""
    try:
        q = urllib.parse.quote(query)
        # srnamespace=6 restricts search to Media files (images, audio, video) on Commons
        url = f"https://commons.wikimedia.org/w/api.php?action=query&list=search&srnamespace=6&srsearch={q}&utf8=&format=json&srlimit=3"
        resp = SESSION.get(url, timeout=15)
        if resp.status_code != 200:
            return None
        
        data = resp.json()
        search_results = data.get('query', {}).get('search', [])
        if not search_results:
            return None
        
        for result in search_results:
            title = result['title']  # e.g., "File:Hyeopjae Beach, Jeju.jpg"
            
            # Fetch the actual thumbnail URL for this file title (width 960px for high quality)
            img_url = f"https://commons.wikimedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=imageinfo&iiprop=url&iiurlwidth=960&format=json"
            img_resp = SESSION.get(img_url, timeout=15)
            if img_resp.status_code != 200:
                continue
            
            img_data = img_resp.json()
            pages = img_data.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                imageinfo = page_info.get('imageinfo', [])
                if imageinfo:
                    # Return the 960px scaled thumbnail URL (falls back to direct URL)
                    thumb = imageinfo[0].get('thumburl')
                    if thumb:
                        return thumb
                    return imageinfo[0].get('url')
        return None
    except Exception as e:
        print(f"  [ERROR] Wikimedia Commons error for '{query}': {e}")
        return None


def is_generic_name(name):
    """Check if a destination name is generic/fictional."""
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


def main():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    destinations = list(db.destinations.find({}))
    print(f"Total destinations: {len(destinations)}")
    
    # Separate real and generic destinations
    real_dests = []
    generic_dests = []
    for d in destinations:
        name = d.get('Destination Name', '')
        if is_generic_name(name):
            generic_dests.append(d)
        else:
            real_dests.append(d)
    
    print(f"Real destinations: {len(real_dests)}")
    print(f"Generic/fictional destinations: {len(generic_dests)}")
    
    # Fetch Wikipedia images for real destinations
    updated = 0
    failed = 0
    skipped = 0
    
    for i, dest in enumerate(real_dests):
        name = dest.get('Destination Name', '')
        country = dest.get('Country', '')
        
        # Disable skipping to overwrite old incorrect Wikipedia article images
        # existing_img = dest.get('image')
        # if existing_img and isinstance(existing_img, str) and existing_img.startswith('http'):
        #     skipped += 1
        #     continue
        
        # Try multiple search queries
        queries = [
            name,  # exact name first
            f"{name} {country}",  # name + country
            f"{name} landmark",  # name + landmark
        ]
        
        img_url = None
        for q in queries:
            img_url = get_commons_image(q)
            if img_url:
                break
            time.sleep(0.2)
        
        if img_url:
            db.destinations.update_one(
                {"_id": dest["_id"]},
                {"$set": {"image": img_url}}
            )
            print(f"  [{i+1}/{len(real_dests)}] OK {name}: {img_url[:80]}...")
            updated += 1
        else:
            print(f"  [{i+1}/{len(real_dests)}] MISS {name}: No Wikipedia image found")
            failed += 1
        
        time.sleep(0.3)  # Respect API rate limits
    
    print(f"\n--- Results ---")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Skipped (already had image): {skipped}")
    print(f"Generic (handled by frontend): {len(generic_dests)}")
    
    # List generic destinations by country for reference
    print(f"\n--- Generic destinations by country ---")
    by_country = {}
    for d in generic_dests:
        c = d.get('Country', 'Unknown')
        by_country.setdefault(c, []).append(d.get('Destination Name', ''))
    for c, names in sorted(by_country.items()):
        print(f"  {c} ({len(names)}): {', '.join(names[:3])}...")


if __name__ == "__main__":
    main()
