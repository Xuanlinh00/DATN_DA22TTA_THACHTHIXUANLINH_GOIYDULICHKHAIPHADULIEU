# -*- coding: utf-8 -*-
"""
Monitor image update progress
"""
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mining.mongodb_storage import db_storage

def monitor(duration_seconds=300, interval_seconds=30):
    """
    Monitor image update progress
    
    Args:
        duration_seconds: Total monitoring time (default: 5 minutes)
        interval_seconds: Check interval (default: 30 seconds)
    """
    if not db_storage.is_connected():
        print("[ERROR] Database not connected")
        return
    
    collection = db_storage.db["destinations"]
    total = collection.count_documents({})
    
    print("=" * 80)
    print("GIÁM SÁT CẬP NHẬT HÌNH ẢNH")
    print("=" * 80)
    print(f"Tổng số destinations: {total}")
    print(f"Kiểm tra mỗi: {interval_seconds}s")
    print(f"Thời gian giám sát: {duration_seconds}s ({duration_seconds//60}phút)")
    print("=" * 80)
    print()
    
    start_time = time.time()
    last_count = 0
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > duration_seconds:
            print("\n[INFO] Hết thời gian giám sát")
            break
        
        # Đếm số lượng có hình
        has_image = collection.count_documents({
            "image": {"$exists": True, "$ne": None, "$regex": "^http"}
        })
        
        # Tính tốc độ
        if last_count > 0:
            speed = (has_image - last_count) / interval_seconds
            eta_seconds = (total - has_image) / speed if speed > 0 else 0
            eta_minutes = int(eta_seconds / 60)
        else:
            speed = 0
            eta_minutes = 0
        
        # Hiển thị
        progress_pct = has_image / total * 100
        progress_bar = "█" * int(progress_pct / 2) + "░" * (50 - int(progress_pct / 2))
        
        print(f"\r[{int(elapsed):3d}s] {progress_bar} {has_image:4d}/{total} ({progress_pct:5.1f}%) | "
              f"Tốc độ: {speed:.2f} img/s | ETA: {eta_minutes}phút", end="", flush=True)
        
        last_count = has_image
        
        # Nếu đã hoàn tất
        if has_image >= total:
            print("\n\n[SUCCESS] ✓ Đã cập nhật xong tất cả hình ảnh!")
            break
        
        time.sleep(interval_seconds)
    
    # Báo cáo cuối
    final_count = collection.count_documents({
        "image": {"$exists": True, "$ne": None, "$regex": "^http"}
    })
    
    print()
    print("=" * 80)
    print("KẾT QUẢ CUỐI CÙNG")
    print("=" * 80)
    print(f"Đã cập nhật: {final_count}/{total} ({final_count/total*100:.1f}%)")
    print(f"Còn lại: {total - final_count} ({(total-final_count)/total*100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=300, help="Monitor duration in seconds (default: 300 = 5min)")
    parser.add_argument("--interval", type=int, default=20, help="Check interval in seconds (default: 20)")
    args = parser.parse_args()
    
    monitor(duration_seconds=args.duration, interval_seconds=args.interval)
