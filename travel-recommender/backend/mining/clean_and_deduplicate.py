# -*- coding: utf-8 -*-
"""
Clean and Deduplicate Module - Demo of Data Cleaning & Preprocessing
This script demonstrates:
1. Loading raw travel datasets
2. Checking and removing duplicate records
3. Filtering invalid values (ratings, costs) and filling missing values
4. Feature engineering and calculating custom travel popularity/engagement metrics
5. Printing summary statistics and sample cleaned data
"""
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Fix Windows console encoding issues for Vietnamese characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Define paths
BASE_DIR = Path(__file__).parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def run_cleaning_demo():
    print("================================================================================")
    f"🚀 DEMO: QUÁ TRÌNH LÀM SẠCH VÀ LỌC DỮ LIỆU DATASET (DATA PREPROCESSING & FILTERING)"
    print("================================================================================")
    
    # ─── PHẦN 1: LÀM SẠCH DỮ LIỆU ĐIỂM ĐẾN (TOURIST DESTINATIONS) ───
    dest_path = RAW_DIR / "Tourist_Destinations.csv"
    if not dest_path.exists():
        print(f"[LỖI] Không tìm thấy file dữ liệu gốc: {dest_path}")
        return
        
    print(f"\n📂 Bước 1: Đọc tệp tin gốc: '{dest_path.name}'")
    df_raw = pd.read_csv(dest_path)
    print(f"   -> Kích thước ban đầu: {df_raw.shape[0]} dòng, {df_raw.shape[1]} cột")
    
    # 1. Kiểm tra dữ liệu trùng lặp
    print("\n📂 Bước 2: Kiểm tra dữ liệu trùng lặp (Deduplication)...")
    # Tạo bản sao
    df_clean = df_raw.copy()
    
    # Tìm kiếm các dòng trùng tên điểm đến và quốc gia
    dup_mask = df_clean.duplicated(subset=["Destination Name", "Country"], keep=False)
    dup_count = dup_mask.sum()
    print(f"   -> Số lượng dòng bị trùng lặp phát hiện: {dup_count}")
    
    if dup_count > 0:
        print("   -> Các dòng bị trùng lặp tiêu biểu:")
        print(df_clean[dup_mask][["Destination Name", "Country"]].head(4))
        
        # Tiến hành xóa trùng lặp
        df_clean = df_clean.drop_duplicates(subset=["Destination Name", "Country"], keep="first")
        print(f"   -> Đã xóa các dòng trùng (chỉ giữ lại dòng đầu tiên). Kích thước mới: {df_clean.shape[0]} dòng.")
    else:
        print("   -> Không có dòng nào trùng lặp tuyệt đối.")
        
    # 2. Lọc dữ liệu lỗi (Data Filtering)
    print("\n📂 Bước 3: Lọc dữ liệu lỗi & Điền khuyết (Data Filtering & Imputation)...")
    
    # Kiểm tra rating có nằm trong khoảng [1.0, 5.0]
    invalid_rating = df_clean[(df_clean["Avg Rating"] < 1.0) | (df_clean["Avg Rating"] > 5.0)]
    print(f"   -> Số dòng có điểm đánh giá rating không hợp lệ (< 1.0 hoặc > 5.0): {len(invalid_rating)}")
    
    # Kiểm tra chi phí âm hoặc bằng 0
    invalid_cost = df_clean[df_clean["Avg Cost (USD/day)"] <= 0]
    print(f"   -> Số dòng có chi phí ngày du lịch không hợp lệ (<= 0 USD): {len(invalid_cost)}")
    
    # Thực hiện lọc
    df_clean = df_clean[
        (df_clean["Avg Rating"] >= 1.0) & (df_clean["Avg Rating"] <= 5.0) &
        (df_clean["Avg Cost (USD/day)"] > 0)
    ].copy()
    
    # Điền giá trị khuyết thiếu cho lượng khách du lịch hàng năm (Annual Visitors) bằng median
    null_visitors = df_clean["Annual Visitors (M)"].isnull().sum()
    print(f"   -> Số dòng bị thiếu dữ liệu lượng khách 'Annual Visitors (M)': {null_visitors}")
    if null_visitors > 0:
        median_val = df_clean["Annual Visitors (M)"].median()
        df_clean["Annual Visitors (M)"] = df_clean["Annual Visitors (M)"].fillna(median_val)
        print(f"   -> Đã điền các giá trị trống bằng giá trị trung vị (Median): {median_val:.2f} M")
        
    # 3. Tính toán các chỉ số mới (Feature Engineering & Engagement Metrics)
    print("\n📂 Bước 4: Tính toán các chỉ số và độ tương tác (Engagement & Popularity Metrics)...")
    
    # Chỉ số chi phí trên mỗi điểm đánh giá (Hiệu quả chi phí - Cost per Rating)
    df_clean["Cost_Per_Rating"] = df_clean["Avg Cost (USD/day)"] / df_clean["Avg Rating"]
    
    # Định nghĩa nhãn mức độ phổ biến dựa trên lượng khách và rating (giống Trending trong demo của bạn)
    # Phổ biến cao nếu: Khách hàng năm >= 5 triệu lượt, HOẶC (Khách >= 2 triệu lượt và đánh giá >= 4.7)
    df_clean["Is_Highly_Popular"] = (
        (df_clean["Annual Visitors (M)"] >= 5.0) | 
        ((df_clean["Annual Visitors (M)"] >= 2.0) & (df_clean["Avg Rating"] >= 4.7))
    )
    
    # In thống kê kết quả lọc
    popular_count = df_clean["Is_Highly_Popular"].sum()
    popular_pct = df_clean["Is_Highly_Popular"].mean() * 100
    not_popular_count = (~df_clean["Is_Highly_Popular"]).sum()
    
    print(f"   📊 Kết quả phân tích độ phổ biến:")
    print(f"      ★ Điểm đến Phổ biến Cao (Highly Popular): {popular_count} ({popular_pct:.1f}%)")
    print(f"      ★ Điểm đến Phổ thông/Ít khách: {not_popular_count}")
    
    # Hiển thị mẫu dữ liệu đã làm sạch
    print("\n📂 Bước 5: Mẫu dữ liệu đã làm sạch & Tính toán Metric (5 dòng đầu):")
    cols_to_show = [
        "Destination Name", "Country", "Type", "Avg Cost (USD/day)", 
        "Avg Rating", "Annual Visitors (M)", "Cost_Per_Rating", "Is_Highly_Popular"
    ]
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_clean[cols_to_show].head(5).to_string(index=False))
    
    
    # ─── PHẦN 2: LÀM SẠCH DỮ LIỆU ĐIỂM THAM QUAN CHI TIẾT (POI) ───
    poi_path = RAW_DIR / "raw_data_India.csv"
    if poi_path.exists():
        print("\n" + "="*50)
        print("📂 Bước 6: Làm sạch bổ sung tệp POI du lịch ('raw_data_India.csv')")
        print("="*50)
        df_poi = pd.read_csv(poi_path)
        print(f"   -> Kích thước ban đầu: {df_poi.shape[0]} dòng, {df_poi.shape[1]} cột")
        
        # Loại bỏ các cột không cần thiết cho giải thuật khai phá
        cols_to_drop = ["link", "Unnamed: 0"]
        cols_to_drop = [c for c in cols_to_drop if c in df_poi.columns]
        if cols_to_drop:
            df_poi = df_poi.drop(columns=cols_to_drop)
            print(f"   -> Đã loại bỏ các cột rác: {cols_to_drop}")
            
        # Lọc sạch khoảng trắng ở tên cột và dữ liệu chữ
        df_poi.columns = df_poi.columns.str.strip()
        df_poi["name"] = df_poi["name"].astype(str).str.strip()
        df_poi["main_category"] = df_poi["main_category"].astype(str).str.strip()
        
        # Loại bỏ POI không có xếp hạng hoặc số lượt reviews <= 0
        df_poi_clean = df_poi[(df_poi["rating"] >= 1.0) & (df_poi["reviews"] > 0)].copy()
        
        # Tính tỷ lệ số review trên điểm số (Mức độ thảo luận tích cực)
        df_poi_clean["Review_Density"] = df_poi_clean["reviews"] * df_poi_clean["rating"]
        
        print(f"   -> Sau khi lọc hàng trống & không hợp lệ: {df_poi_clean.shape[0]} dòng.")
        print("\n   📊 Danh sách Top 3 điểm tham quan nổi tiếng tại Ấn Độ (POI):")
        poi_show = df_poi_clean.sort_values(by="reviews", ascending=False).head(3)
        print(poi_show[["name", "main_category", "rating", "reviews", "Review_Density"]].to_string(index=False))

    print("\n================================================================================")
    print("✨ QUÁ TRÌNH LÀM SẠCH DỮ LIỆU HOÀN TẤT THÀNH CÔNG!")
    print("================================================================================")

if __name__ == "__main__":
    run_cleaning_demo()
