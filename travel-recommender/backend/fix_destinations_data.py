# -*- coding: utf-8 -*-
"""
fix_destinations_data.py
========================
Script để sửa dữ liệu địa điểm:
1. Cập nhật lại tọa độ chính xác cho các địa điểm
2. Cập nhật lại hình ảnh đúng với địa điểm
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage
from services.image_service import get_image_service
import time

def fix_coordinates_priority():
    """
    Đảm bảo tọa độ destination được ưu tiên.
    Nếu không có destination coordinates, copy từ country coordinates.
    """
    print("=" * 80)
    print("KIỂM TRA VÀ SỬA TỌA ĐỘ")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    destinations = list(collection.find({}))
    
    print(f"\n[INFO] Tìm thấy {len(destinations)} destinations")
    
    updated = 0
    no_coords = 0
    
    for dest in destinations:
        name = dest.get("Destination Name", "Unknown")
        dest_lat = dest.get("destination_latitude")
        dest_lon = dest.get("destination_longitude")
        country_lat = dest.get("country_latitude")
        country_lon = dest.get("country_longitude")
        
        # Nếu không có tọa độ destination nhưng có tọa độ country
        import pandas as pd
        if (dest_lat is None or pd.isna(dest_lat) or dest_lon is None or pd.isna(dest_lon)):
            if country_lat is not None and not pd.isna(country_lat) and country_lon is not None and not pd.isna(country_lon):
                # Copy country coords vào destination coords
                collection.update_one(
                    {"Destination Name": name},
                    {"$set": {
                        "destination_latitude": country_lat,
                        "destination_longitude": country_lon
                    }}
                )
                print(f"  ✓ {name}: Đã copy tọa độ từ quốc gia")
                updated += 1
            else:
                print(f"  ⚠ {name}: Không có tọa độ nào")
                no_coords += 1
    
    print(f"\n[SUMMARY]")
    print(f"  Updated: {updated}")
    print(f"  No coordinates: {no_coords}")
    print()


def update_images_for_specific_destinations():
    """
    Cập nhật lại hình ảnh cho các địa điểm có vấn đề.
    """
    print("=" * 80)
    print("CẬP NHẬT HÌNH ẢNH")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    # Danh sách các địa điểm cần cập nhật lại (ví dụ)
    # Có thể để trống để cập nhật tất cả
    priority_destinations = [
        "Lush Pagoda (Thailand)",
        # Thêm các địa điểm khác nếu cần
    ]
    
    image_service = get_image_service(db_storage)
    collection = db_storage.db["destinations"]
    
    if priority_destinations:
        # Cập nhật các địa điểm ưu tiên
        print(f"\n[INFO] Cập nhật {len(priority_destinations)} địa điểm ưu tiên\n")
        for dest_name in priority_destinations:
            dest = collection.find_one({"Destination Name": dest_name})
            if not dest:
                print(f"  ✗ Không tìm thấy: {dest_name}")
                continue
            
            country = dest.get("Country", "")
            dest_type = dest.get("Type", "")
            
            # Xóa cache cũ để force refresh
            cache_collection = db_storage.db["image_cache"]
            cache_collection.delete_one({
                "destination_name": dest_name,
                "country": country
            })
            
            # Lấy hình mới
            print(f"  Đang lấy hình cho: {dest_name} ({country})")
            image_url = image_service.get_destination_image(dest_name, country, dest_type)
            
            if image_url:
                collection.update_one(
                    {"Destination Name": dest_name},
                    {"$set": {"image": image_url}}
                )
                print(f"  ✓ Đã cập nhật: {image_url[:80]}...\n")
            else:
                print(f"  ✗ Không tìm thấy hình\n")
            
            time.sleep(1)  # Delay để tránh rate limit
    else:
        # Cập nhật tất cả các địa điểm chưa có hình hoặc hình bị lỗi
        print("\n[INFO] Tìm các địa điểm cần cập nhật hình...\n")
        
        destinations = list(collection.find({}))
        needs_update = []
        
        for dest in destinations:
            image = dest.get("image")
            # Kiểm tra nếu không có hình hoặc hình không hợp lệ
            if not image or not isinstance(image, str) or not image.startswith("http"):
                needs_update.append(dest)
        
        print(f"[INFO] Tìm thấy {len(needs_update)} địa điểm cần cập nhật\n")
        
        for i, dest in enumerate(needs_update, 1):
            name = dest.get("Destination Name", "Unknown")
            country = dest.get("Country", "")
            dest_type = dest.get("Type", "")
            
            print(f"[{i}/{len(needs_update)}] {name}")
            image_url = image_service.get_destination_image(name, country, dest_type)
            
            if image_url:
                collection.update_one(
                    {"Destination Name": name},
                    {"$set": {"image": image_url}}
                )
                print(f"  ✓ {image_url[:80]}...\n")
            else:
                print(f"  ✗ Không tìm thấy\n")
            
            if i % 10 == 0:
                time.sleep(2)  # Delay sau mỗi 10 requests


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sửa dữ liệu destinations")
    parser.add_argument(
        "--coordinates",
        action="store_true",
        help="Sửa tọa độ"
    )
    parser.add_argument(
        "--images",
        action="store_true",
        help="Cập nhật hình ảnh"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Chạy tất cả"
    )
    
    args = parser.parse_args()
    
    if args.all or args.coordinates:
        fix_coordinates_priority()
    
    if args.all or args.images:
        update_images_for_specific_destinations()
    
    if not (args.coordinates or args.images or args.all):
        print("Sử dụng: python fix_destinations_data.py --coordinates|--images|--all")
