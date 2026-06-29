# -*- coding: utf-8 -*-
"""
update_destination_images.py
============================
Script để tự động cập nhật hình ảnh thực tế cho tất cả destinations trong MongoDB
sử dụng Unsplash API và Wikimedia Commons API
"""

import sys
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mining.mongodb_storage import db_storage
from services.image_service import get_image_service

def update_all_destination_images(batch_size=50, delay=1.0):
    """
    Cập nhật hình ảnh cho tất cả destinations
    
    Args:
        batch_size: Số lượng destinations xử lý mỗi lần
        delay: Thời gian delay giữa các lần gọi API (giây) để tránh rate limit
    """
    print("=" * 80)
    print("UPDATING DESTINATION IMAGES FROM REAL SOURCES")
    print("=" * 80)
    
    # Check connection
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    # Get all destinations
    print("\n[1] Loading destinations from MongoDB...")
    destinations_list = db_storage.load_destinations()
    
    if not destinations_list:
        print("[ERROR] No destinations found in database")
        return
    
    # Convert to DataFrame
    import pandas as pd
    destinations_df = pd.DataFrame(destinations_list)
    
    total = len(destinations_df)
    print(f"[OK] Found {total} destinations")
    
    # Initialize image service
    image_service = get_image_service(db_storage)
    
    # Process destinations
    print(f"\n[2] Fetching real images (batch_size={batch_size}, delay={delay}s)...")
    print("-" * 80)
    
    updated_count = 0
    skipped_count = 0
    failed_count = 0
    
    for index, row in destinations_df.iterrows():
        dest_name = row.get("Destination Name", "")
        country = row.get("Country", "")
        dest_type = row.get("Type", "")
        current_image = row.get("image", "")
        
        # Skip if destination already has a valid image URL
        if current_image and isinstance(current_image, str) and current_image.startswith("http"):
            skipped_count += 1
            if (index + 1) % 50 == 0:
                print(f"  Progress: {index + 1}/{total} (Updated: {updated_count}, Skipped: {skipped_count}, Failed: {failed_count})")
            continue
        
        try:
            # Fetch image
            image_url = image_service.get_destination_image(dest_name, country, dest_type)
            
            if image_url:
                # Update in database
                collection = db_storage.db["destinations"]
                result = collection.update_one(
                    {"Destination Name": dest_name},
                    {"$set": {"image": image_url}}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    print(f"  ✓ [{index + 1}/{total}] {dest_name} ({country})")
                    print(f"    → {image_url[:80]}...")
                else:
                    skipped_count += 1
            else:
                failed_count += 1
                print(f"  ✗ [{index + 1}/{total}] {dest_name} ({country}) - No image found")
            
            # Delay to avoid rate limiting
            if (index + 1) % batch_size == 0:
                print(f"\n  [BATCH COMPLETE] Processed {index + 1}/{total}")
                print(f"  Updated: {updated_count} | Skipped: {skipped_count} | Failed: {failed_count}")
                print(f"  Waiting {delay}s before next batch...\n")
                time.sleep(delay)
        
        except Exception as e:
            failed_count += 1
            print(f"  ✗ [{index + 1}/{total}] {dest_name} - Error: {e}")
    
    # Final summary
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)
    print(f"Total destinations: {total}")
    print(f"✓ Updated:         {updated_count}")
    print(f"○ Skipped:         {skipped_count}")
    print(f"✗ Failed:          {failed_count}")
    print("=" * 80)
    
    # Reload destinations to verify
    print("\n[3] Verifying updates...")
    updated_list = db_storage.load_destinations()
    import pandas as pd
    updated_df = pd.DataFrame(updated_list)
    valid_images = updated_df["image"].apply(
        lambda x: isinstance(x, str) and x.startswith("http")
    ).sum()
    
    print(f"  Destinations with valid images: {valid_images}/{total} ({valid_images/total*100:.1f}%)")
    print("\n[OK] Image update process completed!")


def update_missing_images_only(delay=1.0):
    """Chỉ cập nhật cho những destination chưa có hình"""
    print("=" * 80)
    print("UPDATING MISSING DESTINATION IMAGES")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    print("\n[1] Finding destinations without images...")
    destinations_list = db_storage.load_destinations()
    
    if not destinations_list:
        print("[ERROR] No destinations found in database")
        return
    
    # Convert to DataFrame
    import pandas as pd
    destinations_df = pd.DataFrame(destinations_list)
    
    # Filter destinations without valid images
    missing_images = destinations_df[
        ~destinations_df["image"].apply(
            lambda x: isinstance(x, str) and x.startswith("http")
        )
    ]
    
    total = len(missing_images)
    print(f"[OK] Found {total} destinations without images")
    
    if total == 0:
        print("[INFO] All destinations already have images!")
        return
    
    # Initialize image service
    image_service = get_image_service(db_storage)
    
    # Process
    print(f"\n[2] Fetching images (delay={delay}s)...")
    print("-" * 80)
    
    updated_count = 0
    failed_count = 0
    
    for index, row in missing_images.iterrows():
        dest_name = row.get("Destination Name", "")
        country = row.get("Country", "")
        dest_type = row.get("Type", "")
        
        try:
            image_url = image_service.get_destination_image(dest_name, country, dest_type)
            
            if image_url:
                collection = db_storage.db["destinations"]
                collection.update_one(
                    {"Destination Name": dest_name},
                    {"$set": {"image": image_url}}
                )
                
                updated_count += 1
                print(f"  ✓ [{updated_count}/{total}] {dest_name}")
                print(f"    → {image_url[:80]}...")
            else:
                failed_count += 1
                print(f"  ✗ {dest_name} - No image found")
            
            time.sleep(delay)
        
        except Exception as e:
            failed_count += 1
            print(f"  ✗ {dest_name} - Error: {e}")
    
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)
    print(f"Updated: {updated_count}/{total}")
    print(f"Failed:  {failed_count}/{total}")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Update destination images from real sources")
    parser.add_argument(
        "--mode",
        choices=["all", "missing"],
        default="missing",
        help="Update mode: 'all' for all destinations, 'missing' for only those without images"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of destinations to process before delay (only for 'all' mode)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between API calls to avoid rate limiting"
    )
    
    args = parser.parse_args()
    
    if args.mode == "all":
        update_all_destination_images(batch_size=args.batch_size, delay=args.delay)
    else:
        update_missing_images_only(delay=args.delay)
