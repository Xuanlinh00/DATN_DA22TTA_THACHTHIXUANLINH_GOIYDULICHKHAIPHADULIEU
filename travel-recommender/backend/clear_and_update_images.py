# -*- coding: utf-8 -*-
"""
Xóa tất cả hình ảnh cũ và cập nhật lại với thuật toán mới
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage
from services.image_service import get_image_service
import time

def clear_all_images():
    """Xóa tất cả hình ảnh và cache cũ"""
    print("=" * 80)
    print("XÓA TẤT CẢ HÌNH ẢNH VÀ CACHE CŨ")
    print("=" * 80)
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return False
    
    # Xóa hình trong destinations
    collection = db_storage.db["destinations"]
    result = collection.update_many(
        {},
        {"$unset": {"image": ""}}
    )
    print(f"✓ Đã xóa hình trong {result.modified_count} destinations")
    
    # Xóa image cache
    cache_collection = db_storage.db["image_cache"]
    result = cache_collection.delete_many({})
    print(f"✓ Đã xóa {result.deleted_count} entries trong image cache")
    
    print()
    return True


def update_with_new_algorithm(batch_size=50, delay=0.2):
    """Cập nhật lại với thuật toán mới - ưu tiên type + country"""
    print("=" * 80)
    print("CẬP NHẬT HÌNH ẢNH VỚI THUẬT TOÁN MỚI")
    print("=" * 80)
    print("Chiến lược: Tìm hình dựa trên COUNTRY + TYPE thay vì tên giả lập")
    print("=" * 80)
    print()
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    destinations = list(collection.find({}))
    
    total = len(destinations)
    print(f"[INFO] Tìm thấy {total} destinations\n")
    
    image_service = get_image_service(db_storage)
    
    updated = 0
    failed = 0
    
    for i, dest in enumerate(destinations, 1):
        name = dest.get("Destination Name", "Unknown")
        country = dest.get("Country", "")
        dest_type = dest.get("Type", "")
        
        print(f"[{i}/{total}] {name[:40]:40s} | {country:15s} | {dest_type}")
        
        # Lấy hình với thuật toán mới
        image_url = image_service.get_destination_image(name, country, dest_type)
        
        if image_url:
            collection.update_one(
                {"Destination Name": name},
                {"$set": {"image": image_url}}
            )
            updated += 1
            print(f"  ✓ {image_url[:70]}...")
        else:
            failed += 1
            print(f"  ✗ Không tìm thấy")
        
        print()
        
        # Delay và report progress
        if i % batch_size == 0:
            print(f"[PROGRESS] {i}/{total} | Updated: {updated} | Failed: {failed}")
            print(f"[RATE] Success: {updated/i*100:.1f}%")
            print()
        
        time.sleep(delay)
    
    # Final report
    print("=" * 80)
    print("HOÀN TẤT")
    print("=" * 80)
    print(f"Tổng:     {total}")
    print(f"✓ Updated: {updated} ({updated/total*100:.1f}%)")
    print(f"✗ Failed:  {failed} ({failed/total*100:.1f}%)")
    print("=" * 80)


def test_new_algorithm():
    """Test thuật toán mới với vài ví dụ"""
    print("=" * 80)
    print("TEST THUẬT TOÁN MỚI")
    print("=" * 80)
    print()
    
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    image_service = get_image_service(db_storage)
    
    # Lấy 10 destinations ngẫu nhiên
    collection = db_storage.db["destinations"]
    samples = list(collection.aggregate([{"$sample": {"size": 10}}]))
    
    for dest in samples:
        name = dest.get("Destination Name", "")
        country = dest.get("Country", "")
        dest_type = dest.get("Type", "")
        
        print(f"Destination: {name}")
        print(f"Country:     {country}")
        print(f"Type:        {dest_type}")
        
        # Xóa cache để test thuật toán mới
        cache_collection = db_storage.db["image_cache"]
        cache_collection.delete_one({"destination_name": name})
        
        image_url = image_service.get_destination_image(name, country, dest_type)
        
        if image_url:
            print(f"✓ Image:     {image_url[:80]}...")
        else:
            print(f"✗ No image found")
        
        print()
        time.sleep(0.5)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clear và update images với thuật toán mới")
    parser.add_argument("--test", action="store_true", help="Test với 10 samples")
    parser.add_argument("--clear", action="store_true", help="Xóa tất cả hình cũ")
    parser.add_argument("--update", action="store_true", help="Update tất cả")
    parser.add_argument("--all", action="store_true", help="Clear + Update")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay giữa requests (default: 0.2)")
    
    args = parser.parse_args()
    
    if args.test:
        test_new_algorithm()
    elif args.all:
        if clear_all_images():
            print("\nĐợi 3 giây trước khi update...\n")
            time.sleep(3)
            update_with_new_algorithm(delay=args.delay)
    elif args.clear:
        clear_all_images()
    elif args.update:
        update_with_new_algorithm(delay=args.delay)
    else:
        print("Sử dụng: python clear_and_update_images.py --test|--clear|--update|--all")
        print("\nVí dụ:")
        print("  python clear_and_update_images.py --test          # Test với 10 samples")
        print("  python clear_and_update_images.py --all --delay 0.15  # Clear & update tất cả")
