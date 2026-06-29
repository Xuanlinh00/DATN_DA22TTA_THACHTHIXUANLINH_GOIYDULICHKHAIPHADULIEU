# -*- coding: utf-8 -*-
"""
Kiểm tra tất cả hình ảnh trong database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage
import pandas as pd

def check_all_images():
    """Kiểm tra tất cả hình ảnh trong database"""
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    destinations = list(collection.find({}))
    
    print("=" * 100)
    print("KIỂM TRA HÌNH ẢNH TẤT CẢ DESTINATIONS")
    print("=" * 100)
    print()
    
    total = len(destinations)
    has_valid_image = 0
    has_no_image = 0
    has_invalid_image = 0
    
    no_image_list = []
    invalid_image_list = []
    
    for i, dest in enumerate(destinations, 1):
        name = dest.get("Destination Name", "Unknown")
        image = dest.get("image")
        country = dest.get("Country", "")
        dest_type = dest.get("Type", "")
        
        # Kiểm tra hình ảnh
        if image and isinstance(image, str) and image.startswith("http"):
            has_valid_image += 1
            # Hiển thị một số ví dụ
            if i <= 10:
                print(f"✓ [{i:4d}] {name[:50]:50s} | {country[:15]:15s} | {image[:60]}")
        elif not image or str(image).lower() == "nan" or image == "":
            has_no_image += 1
            no_image_list.append({
                "name": name,
                "country": country,
                "type": dest_type
            })
            if len(no_image_list) <= 10:
                print(f"✗ [{i:4d}] {name[:50]:50s} | {country[:15]:15s} | KHÔNG CÓ HÌNH")
        else:
            has_invalid_image += 1
            invalid_image_list.append({
                "name": name,
                "country": country,
                "type": dest_type,
                "image": str(image)[:100]
            })
            if len(invalid_image_list) <= 10:
                print(f"⚠ [{i:4d}] {name[:50]:50s} | {country[:15]:15s} | HÌNH KHÔNG HỢP LỆ: {str(image)[:30]}")
    
    # Tổng kết
    print()
    print("=" * 100)
    print("TỔNG KẾT")
    print("=" * 100)
    print(f"Tổng số destinations      : {total}")
    print(f"✓ Có hình hợp lệ          : {has_valid_image} ({has_valid_image/total*100:.1f}%)")
    print(f"✗ Không có hình           : {has_no_image} ({has_no_image/total*100:.1f}%)")
    print(f"⚠ Hình không hợp lệ       : {has_invalid_image} ({has_invalid_image/total*100:.1f}%)")
    print()
    
    # Chi tiết các địa điểm cần sửa
    if no_image_list:
        print("=" * 100)
        print(f"CHI TIẾT {len(no_image_list)} ĐỊA ĐIỂM KHÔNG CÓ HÌNH")
        print("=" * 100)
        for i, item in enumerate(no_image_list[:20], 1):  # Hiển thị 20 đầu tiên
            print(f"{i:3d}. {item['name'][:60]:60s} | {item['country']:15s} | {item['type']}")
        if len(no_image_list) > 20:
            print(f"... và {len(no_image_list) - 20} địa điểm khác")
        print()
    
    if invalid_image_list:
        print("=" * 100)
        print(f"CHI TIẾT {len(invalid_image_list)} ĐỊA ĐIỂM CÓ HÌNH KHÔNG HỢP LỆ")
        print("=" * 100)
        for i, item in enumerate(invalid_image_list[:20], 1):
            print(f"{i:3d}. {item['name'][:60]:60s}")
            print(f"     Image: {item['image']}")
        if len(invalid_image_list) > 20:
            print(f"... và {len(invalid_image_list) - 20} địa điểm khác")
        print()
    
    # Phân tích theo quốc gia
    print("=" * 100)
    print("PHÂN TÍCH THEO QUỐC GIA (Top 10)")
    print("=" * 100)
    
    df = pd.DataFrame(destinations)
    country_stats = []
    
    for country in df['Country'].unique()[:20]:  # Top 20 quốc gia
        country_dests = df[df['Country'] == country]
        total_country = len(country_dests)
        
        valid_images = country_dests['image'].apply(
            lambda x: isinstance(x, str) and x.startswith("http")
        ).sum()
        
        country_stats.append({
            'country': country,
            'total': total_country,
            'valid': valid_images,
            'percent': valid_images/total_country*100 if total_country > 0 else 0
        })
    
    # Sắp xếp theo % hợp lệ thấp nhất
    country_stats = sorted(country_stats, key=lambda x: x['percent'])
    
    print(f"{'Quốc gia':<20} | {'Tổng':>6} | {'Có hình':>8} | {'%':>6}")
    print("-" * 50)
    for stat in country_stats[:10]:
        print(f"{stat['country']:<20} | {stat['total']:>6} | {stat['valid']:>8} | {stat['percent']:>5.1f}%")
    
    print()
    return {
        'total': total,
        'valid': has_valid_image,
        'no_image': has_no_image,
        'invalid': has_invalid_image,
        'no_image_list': no_image_list,
        'invalid_image_list': invalid_image_list
    }


def suggest_fix():
    """Đề xuất cách sửa"""
    print()
    print("=" * 100)
    print("ĐỀ XUẤT SỬA CHỮA")
    print("=" * 100)
    print()
    print("Để cập nhật hình ảnh cho các địa điểm chưa có hình hoặc hình không hợp lệ:")
    print()
    print("1. Cập nhật TẤT CẢ địa điểm chưa có hình:")
    print("   python fix_destinations_data.py --images")
    print()
    print("2. Cập nhật chỉ các địa điểm ưu tiên (sửa file fix_destinations_data.py trước):")
    print("   Sửa biến priority_destinations trong fix_destinations_data.py")
    print("   python fix_destinations_data.py --images")
    print()
    print("3. Chạy update_destination_images.py với chế độ missing:")
    print("   python mining/update_destination_images.py --mode missing --delay 1.5")
    print()
    print("⚠ LƯU Ý:")
    print("  - Unsplash API giới hạn 50 requests/giờ cho development")
    print("  - Nên cập nhật từ từ để tránh rate limit")
    print("  - Một số địa điểm dữ liệu giả lập có thể không tìm được hình chính xác")
    print()


if __name__ == "__main__":
    result = check_all_images()
    suggest_fix()
