# -*- coding: utf-8 -*-
"""
fix_duplicate_images.py
=======================
Sửa các hình ảnh trùng lặp bằng cách cập nhật lại với logic mới
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage
from services.fallback_images import get_fallback_image

def fix_duplicate_images():
    """Cập nhật lại tất cả hình ảnh với logic mới"""
    print("=" * 80)
    print("FIXING DUPLICATE IMAGES")
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
    
    # Update images
    print("\n[2] Updating images with new logic...")
    collection = db_storage.db["destinations"]
    
    updated_count = 0
    failed_count = 0
    
    for idx, dest in enumerate(destinations, 1):
        dest_name = dest.get("Destination Name", "")
        country = dest.get("Country", "")
        dest_type = dest.get("Type", "")
        
        try:
            # Generate new image URL with fixed logic
            new_image_url = get_fallback_image(country, dest_type, dest_name)
            
            # Update in database
            result = collection.update_one(
                {"Destination Name": dest_name},
                {"$set": {"image": new_image_url}}
            )
            
            if result.modified_count > 0:
                updated_count += 1
                if idx % 50 == 0:
                    print(f"  Progress: {idx}/{len(destinations)} (Updated: {updated_count})")
            
        except Exception as e:
            failed_count += 1
            print(f"  ✗ Error updating {dest_name}: {e}")
    
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)
    print(f"Total destinations:  {len(destinations)}")
    print(f"✓ Updated:          {updated_count}")
    print(f"✗ Failed:           {failed_count}")
    print("=" * 80)
    
    # Verify no duplicates
    print("\n[3] Verifying no duplicates...")
    from collections import defaultdict
    
    updated_destinations = db_storage.load_destinations()
    image_groups = defaultdict(list)
    
    for dest in updated_destinations:
        image_url = dest.get("image", "")
        dest_name = dest.get("Destination Name", "")
        
        # Check if image_url is valid (not None, not empty, is string)
        if image_url and isinstance(image_url, str) and image_url.strip():
            image_groups[image_url].append(dest_name)
    
    duplicates = {url: names for url, names in image_groups.items() if len(names) > 1}
    
    if duplicates:
        print(f"\n[WARNING] Still found {len(duplicates)} duplicate images!")
        for url, names in list(duplicates.items())[:5]:  # Show first 5
            print(f"  • {url[:60]}... → {len(names)} destinations")
    else:
        print("\n[OK] ✓ No duplicates found! All images are unique.")
        print(f"Total unique images: {len(image_groups)}")
        print(f"Coverage: {len(image_groups)}/{len(updated_destinations)} ({len(image_groups)/len(updated_destinations)*100:.1f}%)")


if __name__ == "__main__":
    fix_duplicate_images()
