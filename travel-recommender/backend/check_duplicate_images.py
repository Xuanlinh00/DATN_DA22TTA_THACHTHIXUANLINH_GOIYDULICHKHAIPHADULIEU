# -*- coding: utf-8 -*-
"""
check_duplicate_images.py
=========================
Kiểm tra các destination có hình ảnh trùng lặp
"""

import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

def check_duplicate_images():
    """Kiểm tra các destination có hình trùng lặp"""
    print("=" * 80)
    print("CHECKING FOR DUPLICATE IMAGES")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    print("\n[1] Loading destinations...")
    destinations = db_storage.load_destinations()
    
    if not destinations:
        print("[ERROR] No destinations found")
        return
    
    print(f"[OK] Found {len(destinations)} destinations")
    
    # Group destinations by image URL
    print("\n[2] Grouping by image URL...")
    image_groups = defaultdict(list)
    
    for dest in destinations:
        image_url = dest.get("image", "")
        dest_name = dest.get("Destination Name", "")
        country = dest.get("Country", "")
        
        if image_url and isinstance(image_url, str):
            image_groups[image_url].append({
                "name": dest_name,
                "country": country
            })
    
    # Find duplicates
    print("\n[3] Finding duplicates...")
    duplicates = {url: dests for url, dests in image_groups.items() if len(dests) > 1}
    
    if not duplicates:
        print("\n[OK] ✓ No duplicate images found!")
        print(f"Total unique images: {len(image_groups)}")
        return
    
    # Show duplicates
    print(f"\n[WARNING] Found {len(duplicates)} duplicate images!")
    print("-" * 80)
    
    for idx, (url, dests) in enumerate(duplicates.items(), 1):
        print(f"\n[{idx}] Duplicate Image: {url[:60]}...")
        print(f"    Used by {len(dests)} destinations:")
        for dest in dests:
            print(f"      • {dest['name']} ({dest['country']})")
    
    # Summary
    total_duplicates = sum(len(dests) for dests in duplicates.values())
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total destinations:     {len(destinations)}")
    print(f"Unique images:          {len(image_groups)}")
    print(f"Duplicate image URLs:   {len(duplicates)}")
    print(f"Total affected dests:   {total_duplicates}")
    print("=" * 80)


if __name__ == "__main__":
    check_duplicate_images()
