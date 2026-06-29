# -*- coding: utf-8 -*-
"""
Kiểm tra nhanh trạng thái hình ảnh
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

def quick_check():
    """Kiểm tra nhanh"""
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    
    total = collection.count_documents({})
    has_image = collection.count_documents({
        "image": {"$exists": True, "$ne": None, "$regex": "^http"}
    })
    
    print("=" * 60)
    print("TRẠNG THÁI HÌNH ẢNH HIỆN TẠI")
    print("=" * 60)
    print(f"Tổng số destinations : {total}")
    print(f"Đã có hình ảnh       : {has_image} ({has_image/total*100:.1f}%)")
    print(f"Chưa có hình         : {total - has_image} ({(total-has_image)/total*100:.1f}%)")
    print("=" * 60)
    
    # Lấy 5 ví dụ có hình
    print("\nVÍ DỤ 5 ĐỊA ĐIỂM ĐÃ CÓ HÌNH:")
    examples = collection.find(
        {"image": {"$regex": "^http"}}, 
        {"Destination Name": 1, "Country": 1, "image": 1}
    ).limit(5)
    
    for i, dest in enumerate(examples, 1):
        name = dest.get("Destination Name", "")
        country = dest.get("Country", "")
        image = dest.get("image", "")[:70]
        print(f"{i}. {name[:40]:40s} | {country:15s}")
        print(f"   {image}...")

if __name__ == "__main__":
    quick_check()
