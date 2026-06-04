# -*- coding: utf-8 -*-
"""
Process and Merge POI - Clean, merge, and deduplicate POI datasets (USA, Iran, India)
and seed the result into MongoDB.
"""
import sys
import pandas as pd
from pathlib import Path

# Fix Windows console encoding issues for Vietnamese characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Define paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Import MongoDB storage
sys.path.append(str(BASE_DIR))
from mining.mongodb_storage import db_storage

def process_and_merge():
    print("================================================================================")
    print("🚀 BẮT ĐẦU: TIẾN TRÌNH GỘP VÀ CHUẨN HÓA DỮ LIỆU ĐIỂM THAM QUAN (POI)")
    print("================================================================================")

    # File paths
    usa_path = RAW_DIR / "cleaned_data_USA.csv"
    iran_path = RAW_DIR / "cleaned_data_Iran.csv"
    india_path = RAW_DIR / "cleaned_data_India.csv"
    output_path = PROCESSED_DIR / "poi_clean.csv"

    # Check existence
    for name, p in [("USA", usa_path), ("Iran", iran_path), ("India", india_path)]:
        if not p.exists():
            print(f"[LỖI] Không tìm thấy file dữ liệu: {p}")
            return False

    # Load dataframes
    print("📂 Đang tải dữ liệu thô đã làm sạch ban đầu...")
    df_usa = pd.read_csv(usa_path)
    df_iran = pd.read_csv(iran_path)
    df_india = pd.read_csv(india_path)

    print(f"   -> USA: {df_usa.shape[0]} dòng")
    print(f"   -> Iran: {df_iran.shape[0]} dòng")
    print(f"   -> India: {df_india.shape[0]} dòng")

    # Concatenate
    print("\n🔗 Tiến hành gộp 3 bộ dữ liệu quốc tế...")
    df_merged = pd.concat([df_usa, df_iran, df_india], ignore_index=True)
    print(f"   -> Kích thước sau gộp: {df_merged.shape[0]} dòng")

    # Drop columns that are not needed (like original index columns if present)
    if 'Unnamed: 0' in df_merged.columns:
        df_merged = df_merged.drop(columns=['Unnamed: 0'])

    # Standardize names and remove trailing spaces
    for col in ['name', 'city', 'country', 'main_category']:
        if col in df_merged.columns:
            df_merged[col] = df_merged[col].astype(str).str.strip()

    # Drop duplicate records based on name and city
    before_dedup = df_merged.shape[0]
    df_merged = df_merged.drop_duplicates(subset=['name', 'city'], keep='first')
    after_dedup = df_merged.shape[0]
    print(f"   -> Xóa trùng lặp (trùng tên & thành phố): Đã loại bỏ {before_dedup - after_dedup} dòng")
    print(f"   -> Kích thước sau khi lọc trùng: {after_dedup} dòng")

    # Add Category and City columns (required by MongoDB seed / other parts of application)
    print("\n⚙️ Bổ sung các cột định dạng Title Case (Category & City)...")
    df_merged['Category'] = df_merged['main_category'].apply(lambda x: str(x).title())
    df_merged['City'] = df_merged['city'].apply(lambda x: str(x).title())

    # Align/reorder columns to match standard schema of poi_clean.csv
    cols_order = [
        'name', 'main_category', 'rating', 'reviews', 'categories', 'address', 
        'city', 'country', 'state', 'zipcode', 'broader_category', 
        'Weighted_Score', 'Weighted_Average', 'All_Cities', 'Category', 'City'
    ]
    
    # Ensure all target columns exist (fill with None if missing, though they shouldn't be)
    for col in cols_order:
        if col not in df_merged.columns:
            df_merged[col] = None
            
    df_final = df_merged[cols_order].copy()
    
    # Save processed unified POI csv
    print(f"\n💾 Lưu kết quả thành công vào: '{output_path.name}'")
    df_final.to_csv(output_path, index=True, index_label='Unnamed: 0')
    print(f"   -> File đã lưu có kích thước: {df_final.shape[0]} dòng, {df_final.shape[1]} cột")

    # Display breakdown
    print("\n📊 Phân bố Điểm tham quan (POI) theo quốc gia:")
    print(df_final['country'].value_counts().to_string())

    # Seeding to MongoDB
    print("\n🛢️ Bắt đầu cập nhật bộ dữ liệu POI vào cơ sở dữ liệu MongoDB...")
    if db_storage.is_connected():
        success = db_storage.save_poi(df_final)
        if success:
            print("   ✅ Đã cập nhật thành công dữ liệu POI vào MongoDB!")
        else:
            print("   ❌ Cập nhật dữ liệu vào MongoDB thất bại.")
    else:
        print("   ⚠️ Không thể kết nối với MongoDB, vui lòng kiểm tra xem MongoDB Server đang chạy.")

    print("\n================================================================================")
    print("✨ TIẾN TRÌNH HOÀN TẤT THÀNH CÔNG!")
    print("================================================================================")
    return True

if __name__ == "__main__":
    process_and_merge()
