# -*- coding: utf-8 -*-
"""
Sửa các địa điểm cụ thể có vấn đề về tọa độ và hình ảnh
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

# Mapping các địa điểm cần sửa với tọa độ thực tế và tên tìm kiếm đúng
FIXES = {
    "Lush Pagoda (Thailand)": {
        "search_name": "Phi Phi Islands Thailand",  # Tên thực tế để tìm hình
        "latitude": 7.7407,   # Phi Phi Islands coordinates
        "longitude": 98.7784,
        "description": "Trải nghiệm hành trình du lịch beach thú vị tại Phi Phi Islands (Thailand). Điểm đến này nổi tiếng với cảnh sắc đẹp như trong mơ, chi phí phù hợp mức Moderate và mùa du lịch lý tưởng nhất là Spring."
    },
    # Thêm các địa điểm khác cần sửa ở đây
}

def fix_destinations():
    """Sửa các địa điểm cụ thể"""
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    
    print("=" * 80)
    print("SỬA CÁC ĐỊA ĐIỂM CỤ THỂ")
    print("=" * 80)
    print()
    
    for dest_name, fixes in FIXES.items():
        print(f"Đang sửa: {dest_name}")
        
        # Cập nhật trong database
        update_data = {}
        
        if "latitude" in fixes:
            update_data["destination_latitude"] = fixes["latitude"]
        if "longitude" in fixes:
            update_data["destination_longitude"] = fixes["longitude"]
        if "description" in fixes:
            update_data["Description"] = fixes["description"]
        
        # Lấy hình ảnh mới với tên tìm kiếm đúng
        if "search_name" in fixes:
            from services.image_service import get_image_service
            image_service = get_image_service(db_storage)
            
            dest = collection.find_one({"Destination Name": dest_name})
            if dest:
                country = dest.get("Country", "")
                dest_type = dest.get("Type", "")
                
                # Xóa cache cũ
                cache_collection = db_storage.db["image_cache"]
                cache_collection.delete_many({
                    "$or": [
                        {"destination_name": dest_name},
                        {"destination_name": fixes["search_name"]}
                    ]
                })
                
                # Lấy hình mới với tên đúng
                image_url = image_service.get_destination_image(
                    fixes["search_name"], 
                    country, 
                    dest_type
                )
                
                if image_url:
                    update_data["image"] = image_url
                    print(f"  ✓ Hình ảnh mới: {image_url[:80]}...")
        
        # Cập nhật vào database
        if update_data:
            result = collection.update_one(
                {"Destination Name": dest_name},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"  ✓ Đã cập nhật tọa độ: ({fixes.get('latitude')}, {fixes.get('longitude')})")
                print(f"  ✓ Đã cập nhật thành công!")
            else:
                print(f"  ⚠ Không tìm thấy hoặc không có thay đổi")
        
        print()

if __name__ == "__main__":
    fix_destinations()
