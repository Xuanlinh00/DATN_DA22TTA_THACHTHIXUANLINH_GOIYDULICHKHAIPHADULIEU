# -*- coding: utf-8 -*-
"""
update_images_real_landmarks.py
===============================
Script mapping all destinations to real-world landmarks using Gemini and 
fetching real, high-quality images from Wikimedia Commons and Unsplash.
Includes automatic duplicate and invalid image (flags, book scans, portraits) detection.
"""

import os
import sys
import json
import time
import re
import urllib.parse
from pathlib import Path
import pandas as pd
import requests

# Set UTF-8 encoding for console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mining.mongodb_storage import db_storage
import google.generativeai as genai
from dotenv import load_dotenv

# Load env
_root_env = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=_root_env, override=True)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
gemini_model = None
if api_key and api_key.strip():
    try:
        genai.configure(api_key=api_key)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        print("[OK] Gemini API configured successfully.")
    except Exception as e:
        print(f"[WARNING] Gemini configuration failed: {e}")
else:
    print("[WARNING] GEMINI_API_KEY is not set.")

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

DATA_PROC_DIR = Path(__file__).parent.parent / "data" / "processed"
MAPPING_FILE = DATA_PROC_DIR / "real_landmarks_mapping.json"

def is_invalid_image_url(url):
    """Check if the image URL is missing, placeholder, duplicate or incorrect (flag, book scan, portrait, etc.)"""
    if not url or not isinstance(url, str) or not url.startswith("http"):
        return True
    if "placehold.co" in url:
        return True
        
    url_lower = url.lower()
    
    # Exclude non-photo/non-image formats (e.g. pdf, djvu, svg, gif)
    valid_exts = (".jpg", ".jpeg", ".png", ".webp")
    parsed = urllib.parse.urlparse(url_lower)
    path = parsed.path
    if not any(path.endswith(ext) for ext in valid_exts):
        return True
        
    # Blacklist keywords indicating non-scenic/incorrect images
    blacklist = [
        "flag", "emblem", "logo", "map", "vector", "coat_of_arms", "coat_of_arm", 
        "book", "journal", "document", "illustration", "sketch", "drawing", 
        "archive", "page_", "_page", "scan", "diagram", "pdf", "djvu", "svg", 
        "chart", "table", "graph", "text", "paper", "writing", "stamp", "coin", 
        "portrait", "face", "author", "person", "man_", "_man", "woman", 
        "profile", "bio", "headshot", "passport", "identity", "card", "id_",
        "staff", "team", "corporate", "office", "screenshot"
    ]
    if any(word in url_lower for word in blacklist):
        return True
        
    return False

def load_mapping_cache():
    if MAPPING_FILE.exists():
        try:
            with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] Error reading mapping cache: {e}")
    return {}

def save_mapping_cache(mapping):
    try:
        MAPPING_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(MAPPING_FILE, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARNING] Error writing mapping cache: {e}")

def map_batch_to_real_landmarks(batch):
    if not gemini_model:
        return None
        
    list_str = "\n".join([f"- {d['name']} | Country: {d['country']} | Type: {d['type']}" for d in batch])
    
    prompt = f"""
    You are a travel database expert. I have a list of synthetic (fake) or generic tourist destinations with their country and tourism type.
    For each, map it to a REAL, famous, and beautiful tourist destination (landmark/city/attraction) in that country that matches the type.
    
    IMPORTANT:
    1. If the destination name is already a real, famous tourist landmark (e.g. 'Eiffel Tower', 'Hạ Long Bay', 'Chichen Itza', 'Grand Canyon', 'Taj Mahal', 'Colosseum'), keep it as the real name.
    2. Otherwise, if it is a synthetic name (e.g. 'Serene Temple (Morocco)', 'Lush Pagoda (Thailand)', 'Sacred Valley (Germany)'), map it to a real landmark in that country (e.g., 'Hassan II Mosque' for Morocco, 'Wat Arun' for Thailand, 'Bavarian Alps' for Germany).
    3. Ensure the mapped real names are widely recognizable English/local landmark names so that search engines can easily find photos of them.
    4. The key in the JSON response MUST match the "Destination Name" EXACTLY (e.g., "Serene Temple (Morocco)").
    
    Format the response as a valid JSON object matching this structure:
    {{
       "synthetic_name": "real_name"
    }}
    Do not add any explanations or markdown formatting, just return a raw JSON string.
    
    List of destinations:
    {list_str}
    """
    
    for attempt in range(5):
        try:
            response = gemini_model.generate_content(prompt)
            text = response.text.strip().replace("```json", "").replace("```", "").strip()
            result = json.loads(text)
            return result
        except Exception as e:
            print(f"  [GEMINI] Attempt {attempt + 1} failed: {e}")
            wait_time = 15 if "429" in str(e) else 3
            print(f"  Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
            
    return None

def get_wikimedia_image(query, exclude_urls=None):
    if exclude_urls is None:
        exclude_urls = set()
        
    search_url = "https://commons.wikimedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 10,      # Fetch up to 10 results to have backup options
        "gsrnamespace": 6,  # File namespace
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 800
    }
    headers = {"User-Agent": "TravelRecommenderApp/1.0 (travel@example.com)"}
    try:
        response = requests.get(search_url, params=search_params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            # Sort pages by index/relevance
            sorted_pages = sorted(pages.values(), key=lambda p: p.get("index", 999))
            
            for page_data in sorted_pages:
                title = page_data.get("title", "").lower()
                
                # Title blacklist
                title_blacklist = ["flag", "map", "logo", "emblem", "coat of arms", "vector", "book", "journal", "document", "illustration", "sketch", "drawing", "diagram", "scan", "page"]
                if any(word in title for word in title_blacklist):
                    continue
                    
                imageinfo = page_data.get("imageinfo", [])
                if imageinfo:
                    url = imageinfo[0].get("url")
                    if url:
                        # URL blacklist
                        if is_invalid_image_url(url):
                            continue
                        if url not in exclude_urls:
                            return url
        return None
    except Exception as e:
        print(f"  [WIKIMEDIA ERROR] {e}")
        return None

def get_unsplash_image(query, exclude_urls=None):
    if not UNSPLASH_ACCESS_KEY:
        return None
    if exclude_urls is None:
        exclude_urls = set()
        
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 10,      # Fetch up to 10 results to have backup options
        "orientation": "landscape",
        "content_filter": "high"
    }
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            for r in results:
                url_candidate = r["urls"].get("regular") or r["urls"].get("full")
                if url_candidate:
                    if is_invalid_image_url(url_candidate):
                        continue
                    if url_candidate not in exclude_urls:
                        return url_candidate
        elif response.status_code == 429:
            print("[WARNING] Unsplash rate limit reached")
        return None
    except Exception as e:
        print(f"  [UNSPLASH ERROR] {e}")
        return None

def update_all_images(overwrite_all=False):
    print("=" * 80)
    print("MAPPING SYNTHETIC DESTINATIONS TO REAL LANDMARKS AND FETCHING SCENIC UNIQUE IMAGES")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
        
    collection = db_storage.db["destinations"]
    destinations = list(collection.find({}))
    
    total = len(destinations)
    print(f"[INFO] Found {total} destinations in MongoDB.")
    
    # Analyze existing image URLs to find duplicates or invalid ones
    image_frequencies = {}
    for dest in destinations:
        img = dest.get("image")
        if img and isinstance(img, str) and img.startswith("http") and not is_invalid_image_url(img):
            image_frequencies[img] = image_frequencies.get(img, 0) + 1
            
    duplicate_urls = {img for img, count in image_frequencies.items() if count > 1}
    print(f"[INFO] Image statistics:")
    print(f"  Total valid image URLs:      {len(image_frequencies)}")
    print(f"  Duplicate URLs detected:      {len(duplicate_urls)}")
    
    # 1. Load or build mappings
    mapping = load_mapping_cache()
    to_map = []
    
    for dest in destinations:
        name = dest.get("Destination Name", "")
        # If mapping is missing, or maps synthetic name to itself, map it again
        if name not in mapping or (mapping[name] == name and "(" in name):
            to_map.append({
                "name": name,
                "country": dest.get("Country", ""),
                "type": dest.get("Type", "")
            })
            
    if to_map:
        print(f"[INFO] Need to map {len(to_map)} destinations to real landmarks...")
        batch_size = 40
        for i in range(0, len(to_map), batch_size):
            batch = to_map[i : i + batch_size]
            print(f"  Mapping batch {i//batch_size + 1}/{(len(to_map)-1)//batch_size + 1} ({len(batch)} items)...")
            batch_mapping = map_batch_to_real_landmarks(batch)
            if batch_mapping:
                mapping.update(batch_mapping)
                save_mapping_cache(mapping)
                print(f"  ✓ Saved mappings. Cache size: {len(mapping)}")
            else:
                print(f"  [ERROR] Failed to map batch. Exiting to prevent corruption.")
                return
            time.sleep(8)  # Safety delay between batches to avoid 429
            
    print(f"[OK] Mappings ready. Total cached mappings: {len(mapping)}")
    
    # 2. Fetch images for all destinations
    print("\n[INFO] Starting unique image fetching process...")
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    # Track used URLs to avoid assigning the same image twice
    used_urls = set()
    
    # First, populate used_urls with existing unique valid images that we will keep
    for dest in destinations:
        img = dest.get("image")
        if img and isinstance(img, str) and img.startswith("http"):
            if not is_invalid_image_url(img) and img not in duplicate_urls:
                used_urls.add(img)
                
    print(f"[INFO] Keeping {len(used_urls)} existing unique and valid image URLs.")
    
    for idx, dest in enumerate(destinations, 1):
        name = dest.get("Destination Name", "")
        country = dest.get("Country", "")
        dest_type = dest.get("Type", "")
        current_image = dest.get("image", "")
        
        is_invalid = is_invalid_image_url(current_image)
        is_duplicate = current_image in duplicate_urls
        
        # Decide if we need to fetch a new image
        if not (is_invalid or is_duplicate) and not overwrite_all:
            skipped_count += 1
            if idx % 100 == 0 or idx == total:
                print(f"  Progress: {idx}/{total} (Updated: {updated_count}, Skipped: {skipped_count}, Failed: {failed_count})")
            continue
            
        real_name = mapping.get(name, name)
        
        # Clean real name (remove text inside parentheses)
        clean_query = re.sub(r'\([^)]*\)', '', real_name).strip()
        # Add country if not in query already
        if country.lower() not in clean_query.lower():
            search_query = f"{clean_query}, {country}"
        else:
            search_query = clean_query
            
        print(f"[{idx}/{total}] Fetching for: '{name}' | Query: '{search_query}' " + 
              ("(Duplicate)" if is_duplicate else "(Invalid/Flag/Scan/Portrait)" if is_invalid else ""))
        
        image_url = None
        
        # Step 1: Wikimedia Commons (Free, no rate limit)
        image_url = get_wikimedia_image(search_query, used_urls)
        if image_url:
            print(f"  ✓ Found on Wikimedia: {image_url[:80]}...")
            time.sleep(0.05)
        else:
            # Step 2: Unsplash fallback
            print(f"  ⚠ Not found on Wikimedia. Trying Unsplash for: '{search_query}'")
            image_url = get_unsplash_image(search_query, used_urls)
            if image_url:
                print(f"  ✓ Found on Unsplash: {image_url[:80]}...")
                time.sleep(0.5)
            else:
                # Step 3: Generic fallback country + type
                fallback_query = f"{country} {dest_type} landscape travel"
                print(f"  ⚠ Try generic fallback on Wikimedia: '{fallback_query}'")
                image_url = get_wikimedia_image(fallback_query, used_urls)
                if image_url:
                    print(f"    ✓ Fallback found on Wikimedia: {image_url[:80]}...")
                else:
                    # Final fallback to Unsplash generic
                    image_url = get_unsplash_image(f"{country} {dest_type} nature", used_urls)
                    if image_url:
                        print(f"    ✓ Fallback found on Unsplash: {image_url[:80]}...")
                        
        if image_url:
            collection.update_one(
                {"Destination Name": name},
                {"$set": {"image": image_url}}
            )
            dest["image"] = image_url
            used_urls.add(image_url)
            updated_count += 1
        else:
            failed_count += 1
            print(f"  ✗ Failed to find any unique scenic image for: '{name}'")
            
        if idx % 50 == 0 or idx == total:
            print(f"\n[STATUS] Progress: {idx}/{total} | Updated: {updated_count} | Skipped: {skipped_count} | Failed: {failed_count}\n")
            
    print("\n" + "=" * 80)
    print("IMAGE FETCHING AND DUPLICATE/INVALID CORRECTION COMPLETE")
    print("=" * 80)
    print(f"Total processed: {total}")
    print(f"✓ Updated:       {updated_count}")
    print(f"○ Skipped:       {skipped_count}")
    print(f"✗ Failed:        {failed_count}")
    print(f"Total unique valid images now: {len(used_urls)}")
    print("=" * 80)
    
    # 3. Save to destinations_clean.csv and destinations_clustered.csv
    print("\n[INFO] Saving updated data back to CSV files for persistence...")
    try:
        db_dests = list(collection.find({}, {"_id": 0}))
        df = pd.DataFrame(db_dests)
        
        clean_csv = DATA_PROC_DIR / "destinations_clean.csv"
        clustered_csv = DATA_PROC_DIR / "destinations_clustered.csv"
        
        df.to_csv(clean_csv, index=False)
        df.to_csv(clustered_csv, index=False)
        print(f"  ✓ Saved to {clean_csv.name}")
        print(f"  ✓ Saved to {clustered_csv.name}")
        print("[OK] Data synchronized successfully.")
    except Exception as e:
        print(f"[ERROR] Error saving updated CSVs: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update images using real landmarks mapping")
    parser.add_argument("--overwrite-all", action="store_true", help="Force update all destinations")
    args = parser.parse_args()
    
    update_all_images(overwrite_all=args.overwrite_all)
