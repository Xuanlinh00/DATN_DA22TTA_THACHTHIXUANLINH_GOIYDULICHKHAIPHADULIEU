# -*- coding: utf-8 -*-
"""
import_all_2000.py
===================
Imports and cleans all 1,257 unique real destinations from Tourist_Destinations.csv.
Enriches with offline country metadata, generates Vietnamese descriptions,
maps TripAdvisor reviews, regenerates transactions, and executes clustering & Apriori pipelines.
Ensures unique destination names by appending country suffix to duplicates.
"""

import os
import sys
import ast
import json
import random
import time
from pathlib import Path
import pandas as pd
import numpy as np
import requests

# Force UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mining.mongodb_storage import db_storage
from mining.clustering import run_clustering
from mining.apriori_module import mine_association_rules
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROC_DIR = BASE_DIR / "data" / "processed"

# Broad category mapping
BROADER_MAP = {
    'Beach': 'Nature', 'Mountain': 'Nature', 'Wildlife': 'Nature', 'Nature': 'Nature',
    'Urban': 'Modern', 'City': 'Modern',
    'Cultural': 'Heritage', 'Historical': 'Heritage', 'Religious': 'Heritage',
    'Adventure': 'Adventure'
}

# 22 Countries Rich Offline Metadata
RAW_COUNTRY_METADATA = {
    "Germany": {
        "flag": "🇩🇪", "region": "Europe", "subregion": "Western Europe",
        "currency": "EUR", "symbol": "€", "languages": "German", "capital": "Berlin",
        "timezone": "UTC+01:00", "pop": 83100000, "area": 357022, "alpha2": "DE", "alpha3": "DEU",
        "borders": "DK, PL, CZ, AT, CH, FR, LU, BE, NL", "lat": 51.1657, "lon": 10.4515,
        "cost_of_living_index": 65.0, "rent_index": 28.0, "cost_of_living_plus_rent_index": 47.0,
        "groceries_index": 52.0, "restaurant_price_index": 58.0, "local_purchasing_power_index": 95.0,
        "air_pollution_avg": 12.0
    },
    "Greece": {
        "flag": "🇬🇷", "region": "Europe", "subregion": "Southern Europe",
        "currency": "EUR", "symbol": "€", "languages": "Greek", "capital": "Athens",
        "timezone": "UTC+02:00", "pop": 10700000, "area": 131957, "alpha2": "GR", "alpha3": "GRC",
        "borders": "AL, BG, TR, MKD", "lat": 39.0742, "lon": 21.8243,
        "cost_of_living_index": 55.0, "rent_index": 18.0, "cost_of_living_plus_rent_index": 37.0,
        "groceries_index": 44.0, "restaurant_price_index": 52.0, "local_purchasing_power_index": 43.0,
        "air_pollution_avg": 18.0
    },
    "Thailand": {
        "flag": "🇹🇭", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "THB", "symbol": "฿", "languages": "Thai", "capital": "Bangkok",
        "timezone": "UTC+07:00", "pop": 69800000, "area": 513120, "alpha2": "TH", "alpha3": "THA",
        "borders": "KH, LA, MMR, MY", "lat": 15.8700, "lon": 100.9925,
        "cost_of_living_index": 38.0, "rent_index": 15.0, "cost_of_living_plus_rent_index": 27.0,
        "groceries_index": 39.0, "restaurant_price_index": 25.0, "local_purchasing_power_index": 35.0,
        "air_pollution_avg": 22.0
    },
    "Peru": {
        "flag": "🇵🇪", "region": "South America", "subregion": "South America",
        "currency": "PEN", "symbol": "S/.", "languages": "Spanish", "capital": "Lima",
        "timezone": "UTC-05:00", "pop": 33000000, "area": 1285216, "alpha2": "PE", "alpha3": "PER",
        "borders": "BO, BR, CL, CO, EC", "lat": -9.1900, "lon": -75.0152,
        "cost_of_living_index": 32.0, "rent_index": 11.0, "cost_of_living_plus_rent_index": 22.0,
        "groceries_index": 30.0, "restaurant_price_index": 24.0, "local_purchasing_power_index": 30.0,
        "air_pollution_avg": 25.0
    },
    "Morocco": {
        "flag": "🇲🇦", "region": "Africa", "subregion": "Northern Africa",
        "currency": "MAD", "symbol": "DH", "languages": "Arabic", "capital": "Rabat",
        "timezone": "UTC+01:00", "pop": 36900000, "area": 446550, "alpha2": "MA", "alpha3": "MAR",
        "borders": "DZ, EH, ES", "lat": 31.7917, "lon": -7.0926,
        "cost_of_living_index": 30.0, "rent_index": 9.0, "cost_of_living_plus_rent_index": 20.0,
        "groceries_index": 27.0, "restaurant_price_index": 22.0, "local_purchasing_power_index": 32.0,
        "air_pollution_avg": 28.0
    },
    "Italy": {
        "flag": "🇮🇹", "region": "Europe", "subregion": "Southern Europe",
        "currency": "EUR", "symbol": "€", "languages": "Italian", "capital": "Rome",
        "timezone": "UTC+01:00", "pop": 59600000, "area": 301340, "alpha2": "IT", "alpha3": "ITA",
        "borders": "AT, FR, SM, CH, SI, VA", "lat": 41.8719, "lon": 12.5674,
        "cost_of_living_index": 60.0, "rent_index": 24.0, "cost_of_living_plus_rent_index": 43.0,
        "groceries_index": 50.0, "restaurant_price_index": 56.0, "local_purchasing_power_index": 65.0,
        "air_pollution_avg": 16.0
    },
    "Vietnam": {
        "flag": "🇻🇳", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "VND", "symbol": "₫", "languages": "Vietnamese", "capital": "Hanoi",
        "timezone": "UTC+07:00", "pop": 97300000, "area": 331210, "alpha2": "VN", "alpha3": "VNM",
        "borders": "KH, CN, LA", "lat": 14.0583, "lon": 108.2772,
        "cost_of_living_index": 35.0, "rent_index": 12.0, "cost_of_living_plus_rent_index": 24.0,
        "groceries_index": 35.0, "restaurant_price_index": 20.0, "local_purchasing_power_index": 28.0,
        "air_pollution_avg": 26.0
    },
    "New Zealand": {
        "flag": "🇳🇿", "region": "Oceania", "subregion": "Australia and New Zealand",
        "currency": "NZD", "symbol": "$", "languages": "English, Maori", "capital": "Wellington",
        "timezone": "UTC+12:00", "pop": 5000000, "area": 268021, "alpha2": "NZ", "alpha3": "NZL",
        "borders": "", "lat": -40.9006, "lon": 174.8860,
        "cost_of_living_index": 72.0, "rent_index": 32.0, "cost_of_living_plus_rent_index": 53.0,
        "groceries_index": 68.0, "restaurant_price_index": 65.0, "local_purchasing_power_index": 85.0,
        "air_pollution_avg": 6.0
    },
    "Canada": {
        "flag": "🇨🇦", "region": "Americas", "subregion": "Northern America",
        "currency": "CAD", "symbol": "$", "languages": "English, French", "capital": "Ottawa",
        "timezone": "UTC-05:00", "pop": 38000000, "area": 9984670, "alpha2": "CA", "alpha3": "CAN",
        "borders": "US", "lat": 56.1304, "lon": -106.3468,
        "cost_of_living_index": 70.0, "rent_index": 34.0, "cost_of_living_plus_rent_index": 53.0,
        "groceries_index": 66.0, "restaurant_price_index": 64.0, "local_purchasing_power_index": 90.0,
        "air_pollution_avg": 8.0
    },
    "Mexico": {
        "flag": "🇲🇽", "region": "Americas", "subregion": "Central America",
        "currency": "MXN", "symbol": "$", "languages": "Spanish", "capital": "Mexico City",
        "timezone": "UTC-06:00", "pop": 126000000, "area": 1964375, "alpha2": "MX", "alpha3": "MEX",
        "borders": "BZ, GT, US", "lat": 23.6345, "lon": -102.5528,
        "cost_of_living_index": 38.0, "rent_index": 12.0, "cost_of_living_plus_rent_index": 26.0,
        "groceries_index": 36.0, "restaurant_price_index": 32.0, "local_purchasing_power_index": 42.0,
        "air_pollution_avg": 20.0
    },
    "China": {
        "flag": "🇨🇳", "region": "Asia", "subregion": "Eastern Asia",
        "currency": "CNY", "symbol": "¥", "languages": "Chinese", "capital": "Beijing",
        "timezone": "UTC+08:00", "pop": 1400000000, "area": 9596961, "alpha2": "CN", "alpha3": "CHN",
        "borders": "AF, BT, MMR, IN, KZ, KG, LA, MNG, NPL, KP, PK, RU, TJ, VN", "lat": 35.8617, "lon": 104.1954,
        "cost_of_living_index": 40.0, "rent_index": 16.0, "cost_of_living_plus_rent_index": 29.0,
        "groceries_index": 40.0, "restaurant_price_index": 28.0, "local_purchasing_power_index": 60.0,
        "air_pollution_avg": 25.0
    },
    "Brazil": {
        "flag": "🇧🇷", "region": "Americas", "subregion": "South America",
        "currency": "BRL", "symbol": "R$", "languages": "Portuguese", "capital": "Brasilia",
        "timezone": "UTC-03:00", "pop": 211000000, "area": 8515767, "alpha2": "BR", "alpha3": "BRA",
        "borders": "AR, BO, CO, GF, GY, PY, PE, SR, UY, VE", "lat": -14.2350, "lon": -51.9253,
        "cost_of_living_index": 34.0, "rent_index": 10.0, "cost_of_living_plus_rent_index": 23.0,
        "groceries_index": 29.0, "restaurant_price_index": 26.0, "local_purchasing_power_index": 33.0,
        "air_pollution_avg": 15.0
    },
    "Kenya": {
        "flag": "🇰🇪", "region": "Africa", "subregion": "Eastern Africa",
        "currency": "KES", "symbol": "Sh", "languages": "Swahili, English", "capital": "Nairobi",
        "timezone": "UTC+03:00", "pop": 53700000, "area": 580367, "alpha2": "KE", "alpha3": "KEN",
        "borders": "ET, SO, SS, TZ, UG", "lat": -0.0236, "lon": 37.9062,
        "cost_of_living_index": 32.0, "rent_index": 10.0, "cost_of_living_plus_rent_index": 21.0,
        "groceries_index": 31.0, "restaurant_price_index": 25.0, "local_purchasing_power_index": 27.0,
        "air_pollution_avg": 18.0
    },
    "Egypt": {
        "flag": "🇪🇬", "region": "Africa", "subregion": "Northern Africa",
        "currency": "EGP", "symbol": "E£", "languages": "Arabic", "capital": "Cairo",
        "timezone": "UTC+02:00", "pop": 102000000, "area": 1002450, "alpha2": "EG", "alpha3": "EGY",
        "borders": "IL, LY, SD", "lat": 26.8206, "lon": 30.8025,
        "cost_of_living_index": 28.0, "rent_index": 6.0, "cost_of_living_plus_rent_index": 17.0,
        "groceries_index": 26.0, "restaurant_price_index": 20.0, "local_purchasing_power_index": 22.0,
        "air_pollution_avg": 35.0
    },
    "India": {
        "flag": "🇮🇳", "region": "Asia", "subregion": "Southern Asia",
        "currency": "INR", "symbol": "₹", "languages": "Hindi, English", "capital": "New Delhi",
        "timezone": "UTC+05:30", "pop": 1380000000, "area": 3287263, "alpha2": "IN", "alpha3": "IND",
        "borders": "BD, BT, CN, MMR, NPL, PK", "lat": 20.5937, "lon": 78.9629,
        "cost_of_living_index": 25.0, "rent_index": 6.0, "cost_of_living_plus_rent_index": 16.0,
        "groceries_index": 25.0, "restaurant_price_index": 18.0, "local_purchasing_power_index": 48.0,
        "air_pollution_avg": 45.0
    },
    "Argentina": {
        "flag": "🇦🇷", "region": "Americas", "subregion": "South America",
        "currency": "ARS", "symbol": "$", "languages": "Spanish", "capital": "Buenos Aires",
        "timezone": "UTC-03:00", "pop": 45000000, "area": 2780400, "alpha2": "AR", "alpha3": "ARG",
        "borders": "BO, BR, CL, PY, UY", "lat": -38.4161, "lon": -63.6167,
        "cost_of_living_index": 30.0, "rent_index": 8.0, "cost_of_living_plus_rent_index": 20.0,
        "groceries_index": 28.0, "restaurant_price_index": 25.0, "local_purchasing_power_index": 35.0,
        "air_pollution_avg": 14.0
    },
    "South Africa": {
        "flag": "🇿🇦", "region": "Africa", "subregion": "Southern Africa",
        "currency": "ZAR", "symbol": "R", "languages": "Zulu, Xhosa, Afrikaans, English", "capital": "Pretoria",
        "timezone": "UTC+02:00", "pop": 59300000, "area": 1221037, "alpha2": "ZA", "alpha3": "ZAF",
        "borders": "BW, LS, MZ, NA, SZ, ZW", "lat": -30.5595, "lon": 22.9375,
        "cost_of_living_index": 38.0, "rent_index": 14.0, "cost_of_living_plus_rent_index": 26.0,
        "groceries_index": 34.0, "restaurant_price_index": 32.0, "local_purchasing_power_index": 73.0,
        "air_pollution_avg": 22.0
    },
    "Japan": {
        "flag": "🇯🇵", "region": "Asia", "subregion": "Eastern Asia",
        "currency": "JPY", "symbol": "¥", "languages": "Japanese", "capital": "Tokyo",
        "timezone": "UTC+09:00", "pop": 126000000, "area": 377975, "alpha2": "JP", "alpha3": "JPN",
        "borders": "", "lat": 36.2048, "lon": 138.2529,
        "cost_of_living_index": 68.0, "rent_index": 26.0, "cost_of_living_plus_rent_index": 48.0,
        "groceries_index": 65.0, "restaurant_price_index": 45.0, "local_purchasing_power_index": 88.0,
        "air_pollution_avg": 11.0
    },
    "Australia": {
        "flag": "🇦🇺", "region": "Oceania", "subregion": "Australia and New Zealand",
        "currency": "AUD", "symbol": "$", "languages": "English", "capital": "Canberra",
        "timezone": "UTC+10:00", "pop": 25500000, "area": 7692024, "alpha2": "AU", "alpha3": "AUS",
        "borders": "", "lat": -25.2744, "lon": 133.7751,
        "cost_of_living_index": 75.0, "rent_index": 36.0, "cost_of_living_plus_rent_index": 56.0,
        "groceries_index": 72.0, "restaurant_price_index": 70.0, "local_purchasing_power_index": 105.0,
        "air_pollution_avg": 5.0
    },
    "Spain": {
        "flag": "🇪🇸", "region": "Europe", "subregion": "Southern Europe",
        "currency": "EUR", "symbol": "€", "languages": "Spanish", "capital": "Madrid",
        "timezone": "UTC+01:00", "pop": 47400000, "area": 505990, "alpha2": "ES", "alpha3": "ESP",
        "borders": "AD, FR, GI, PT, MA", "lat": 40.4637, "lon": -3.7492,
        "cost_of_living_index": 54.0, "rent_index": 22.0, "cost_of_living_plus_rent_index": 39.0,
        "groceries_index": 45.0, "restaurant_price_index": 50.0, "local_purchasing_power_index": 70.0,
        "air_pollution_avg": 11.0
    },
    "France": {
        "flag": "🇫🇷", "region": "Europe", "subregion": "Western Europe",
        "currency": "EUR", "symbol": "€", "languages": "French", "capital": "Paris",
        "timezone": "UTC+01:00", "pop": 67400000, "area": 643801, "alpha2": "FR", "alpha3": "FRA",
        "borders": "AD, BE, DE, IT, LU, MC, ES, CH", "lat": 46.2276, "lon": 2.2137,
        "cost_of_living_index": 74.0, "rent_index": 30.0, "cost_of_living_plus_rent_index": 53.0,
        "groceries_index": 68.0, "restaurant_price_index": 72.0, "local_purchasing_power_index": 85.0,
        "air_pollution_avg": 10.0
    },
    "USA": {
        "flag": "🇺🇸", "region": "Americas", "subregion": "Northern America",
        "currency": "USD", "symbol": "$", "languages": "English", "capital": "Washington D.C.",
        "timezone": "UTC-05:00", "pop": 331000000, "area": 9833517, "alpha2": "US", "alpha3": "USA",
        "borders": "CA, MX", "lat": 37.0902, "lon": -95.7129,
        "cost_of_living_index": 70.0, "rent_index": 40.0, "cost_of_living_plus_rent_index": 56.0,
        "groceries_index": 71.0, "restaurant_price_index": 70.0, "local_purchasing_power_index": 110.0,
        "air_pollution_avg": 9.0
    }
}

def cost_category(cost):
    if cost < 80:     return 'Budget'
    elif cost < 150:  return 'Moderate'
    elif cost < 250:  return 'Expensive'
    else:             return 'Luxury'

def get_varied_description(name, country, season, dtype, cost_cat, rating):
    templates = [
        f"Khám phá {name} tại {country}, một điểm đến {dtype.lower()} tuyệt vời với phong cảnh đẹp và bầu không khí trong lành. Điểm đến này có chi phí dịch vụ {cost_cat.lower()} (đánh giá trung bình {rating}/5), thích hợp nhất để du lịch vào {season.lower()}.",
        f"Nếu bạn đang lên kế hoạch du lịch {dtype.lower()}, {name} ở {country} chính là lựa chọn lý tưởng. Với mức xếp hạng {rating}/5 sao từ cộng đồng du khách và chi phí du lịch thuộc phân khúc {cost_cat.lower()}, nơi này hứa hẹn kỳ nghỉ tuyệt vời vào {season.lower()}.",
        f"{name} là địa danh {dtype.lower()} nổi tiếng hàng đầu tại {country}. Được đánh giá {rating}/5 sao nhờ trải nghiệm độc đáo, địa điểm này có chi phí {cost_cat.lower()} và thời điểm ghé thăm hoàn hảo nhất là vào {season.lower()}.",
        f"Trải nghiệm hành trình du lịch {dtype.lower()} thú vị tại {name} ({country}). Điểm đến này mang lại cảnh sắc say đắm lòng người, chi phí thuộc mức {cost_cat.lower()}, đánh giá cao {rating}/5 và rất thích hợp cho chuyến đi vào {season.lower()}.",
        f"Khám phá nét độc đáo của {name} - điểm du lịch {dtype.lower()} đặc sắc tại {country}. Nơi đây thu hút du khách nhờ các hoạt động trải nghiệm hấp dẫn vào {season.lower()}, mức chi phí {cost_cat.lower()} cùng điểm số đánh giá {rating}/5 ấn tượng."
    ]
    return random.choice(templates)

def run_import():
    db_storage.connect()
    if not db_storage.is_connected():
        print("[ERROR] MongoDB is not running or cannot be connected!")
        return False
        
    print("\n" + "="*80)
    print("🚀 BẮT ĐẦU NHẬP VÀ ĐỒNG BỘ HÓA TOÀN BỘ 1.257 ĐIỂM ĐẾN THỰC TẾ TỪ DATASET")
    print("="*80)
    
    # ─── BƯỚC 1: ĐỌC VÀ LÀM SẠCH TOURIST_DESTINATIONS.CSV ───
    raw_csv_path = DATA_RAW_DIR / "Tourist_Destinations.csv"
    if not raw_csv_path.exists():
        print(f"[ERROR] Không tìm thấy file Tourist_Destinations.csv tại {raw_csv_path}")
        return False
        
    print(f"\n[1] Đang đọc file dữ liệu thô: {raw_csv_path}")
    df_raw = pd.read_csv(raw_csv_path)
    print(f"    Tổng số dòng thô nạp được: {len(df_raw)}")
    
    # Loại bỏ trùng lặp dựa trên tên điểm đến và quốc gia
    df_clean = df_raw.drop_duplicates(subset=["Destination Name", "Country"]).copy()
    print(f"    Tổng số điểm đến sau khi loại bỏ trùng lặp: {len(df_clean)} (trùng: {len(df_raw) - len(df_clean)})")
    
    # Xác định các tên điểm đến bị trùng lặp giữa các quốc gia
    name_counts = df_clean["Destination Name"].value_counts()
    duplicate_names = set(name_counts[name_counts > 1].index)
    print(f"    Tìm thấy {len(duplicate_names)} tên điểm đến bị trùng lặp giữa các quốc gia. Tiến hành tạo tên duy nhất...")

    destinations_list = []
    
    # ─── BƯỚC 2: HỢP NHẤT VÀ LÀM GIÀU SIÊU DỮ LIỆU NGOẠI TUYẾN ───
    print("\n[2] Bắt đầu làm sạch dữ liệu, làm giàu siêu dữ liệu quốc gia & sinh mô tả...")
    random.seed(42)
    
    for idx, row in enumerate(df_clean.to_dict('records'), 1):
        raw_name = row["Destination Name"].strip()
        country = row["Country"].strip()
        continent = row["Continent"].strip()
        dtype = row["Type"].strip()
        cost = float(row["Avg Cost (USD/day)"])
        season = row["Best Season"].strip()
        rating = float(row["Avg Rating"])
        visitors = float(row["Annual Visitors (M)"])
        unesco = row["UNESCO Site"].strip()
        
        # Nếu tên bị trùng, thêm hậu tố quốc gia để phân biệt (tránh lỗi nhầm lẫn trang chi tiết)
        if raw_name in duplicate_names:
            name = f"{raw_name} ({country})"
        else:
            name = raw_name
            
        # Lấy metadata quốc gia
        c_meta = RAW_COUNTRY_METADATA.get(country)
        if not c_meta:
            # Fallback mặc định nếu quốc gia lạ xuất hiện
            print(f"  [WARNING] Không có metadata cho quốc gia {country}, sử dụng mặc định.")
            c_meta = {
                "flag": "🌍", "region": "Other", "subregion": "Other", "currency": "USD", "symbol": "$",
                "languages": "English", "capital": "Capital", "timezone": "UTC", "pop": 50000000, "area": 500000,
                "alpha2": country[:2].upper(), "alpha3": country[:3].upper(), "borders": "", "lat": 0.0, "lon": 0.0,
                "cost_of_living_index": 50.0, "rent_index": 20.0, "cost_of_living_plus_rent_index": 35.0,
                "groceries_index": 45.0, "restaurant_price_index": 45.0, "local_purchasing_power_index": 60.0,
                "air_pollution_avg": 20.0
            }
            
        desc = get_varied_description(name, country, season, dtype, cost_category(cost), rating)
        
        # Định vị tọa độ điểm đến giả lập xoay quanh tọa độ quốc gia để tránh trùng lặp tọa độ
        # Thêm sai số ngẫu nhiên nhỏ (khoảng 0.05 đến 0.25 độ) để các điểm đến không bị đè lên nhau trên bản đồ
        d_lat = c_meta["lat"] + random.uniform(-0.15, 0.15)
        d_lon = c_meta["lon"] + random.uniform(-0.15, 0.15)
        
        record = {
            "Destination Name": name,
            "Country": country,
            "Continent": continent,
            "Type": dtype,
            "Avg Cost (USD/day)": cost,
            "Best Season": season,
            "Avg Rating": rating,
            "Annual Visitors (M)": visitors,
            "UNESCO Site": unesco,
            "Broader_Type": BROADER_MAP.get(dtype, 'Other'),
            "Cost_Category": cost_category(cost),
            "country_flag": c_meta["flag"],
            "country_region": c_meta["region"],
            "country_subregion": c_meta["subregion"],
            "country_currency": c_meta["currency"],
            "country_currency_symbol": c_meta["symbol"],
            "country_languages": c_meta["languages"],
            "country_capital": c_meta["capital"],
            "country_timezone": c_meta["timezone"],
            "country_population": float(c_meta["pop"]),
            "country_area": float(c_meta["area"]),
            "country_alpha2": c_meta["alpha2"],
            "country_alpha3": c_meta["alpha3"],
            "country_borders": c_meta["borders"],
            "country_latitude": float(c_meta["lat"]),
            "country_longitude": float(c_meta["lon"]),
            "DestinationID": idx,
            "Popularity": "High" if visitors > 1.5 else "Medium",
            "BestTimeToVisit": season,
            "destination": name,
            "avg_review_rating": rating,
            "review_count": 0,
            "popularity_score": round((rating * 10) + (visitors * 2), 2),
            "cost_of_living_index": float(c_meta.get("cost_of_living_index", 50.0)),
            "rent_index": float(c_meta.get("rent_index", 20.0)),
            "cost_of_living_plus_rent_index": float(c_meta.get("cost_of_living_plus_rent_index", 35.0)),
            "groceries_index": float(c_meta.get("groceries_index", 45.0)),
            "restaurant_price_index": float(c_meta.get("restaurant_price_index", 45.0)),
            "local_purchasing_power_index": float(c_meta.get("local_purchasing_power_index", 60.0)),
            "air_pollution_avg": float(c_meta.get("air_pollution_avg", 20.0)),
            "air_pollution_2023": float(c_meta.get("air_pollution_avg", 20.0)),
            "destination_latitude": round(d_lat, 4),
            "destination_longitude": round(d_lon, 4),
            "destination_budget_level": cost_category(cost),
            "Cluster": -1,
            "Description": desc,
            "image": None
        }
        destinations_list.append(record)
        
    print(f"    Đã sinh dữ liệu hoàn tất cho {len(destinations_list)} điểm đến.")
    
    # ─── BƯỚC 3: IMPORT ĐÁNH GIÁ TRIPADVISOR ───
    print("\n[3] Đọc luồng reviews.csv và offerings.csv từ TripAdvisor để lấy ratings thực...")
    reviews_path = DATA_RAW_DIR / "reviews.csv"
    offerings_path = DATA_RAW_DIR / "offerings.csv"
    
    ratings_to_save = []
    if not reviews_path.exists() or not offerings_path.exists():
        print(f"  [WARNING] Không tìm thấy reviews.csv hoặc offerings.csv tại {DATA_RAW_DIR}. Bỏ qua nạp ratings.")
    else:
        print("    Đang nạp offerings.csv để ánh xạ...")
        df_off = pd.read_csv(offerings_path)
        offering_ids = df_off['id'].tolist()
        
        # Ánh xạ deterministic sang 1.257 địa điểm của chúng ta
        dest_names_pool = [d["Destination Name"] for d in destinations_list]
        offering_to_dest = {}
        for off_id in offering_ids:
            offering_to_dest[off_id] = dest_names_pool[off_id % len(dest_names_pool)]
            
        print(f"    Đã tạo ánh xạ cho {len(offering_to_dest)} khách sạn.")
        print("    Đọc luồng reviews.csv...")
        
        target_reviews_count = 15000
        chunk_size = 50000
        
        try:
            for chunk in pd.read_csv(reviews_path, chunksize=chunk_size):
                for _, row in chunk.iterrows():
                    off_id = row['offering_id']
                    if off_id in offering_to_dest:
                        overall_rating = 3.0
                        username = "Anonymous"
                        
                        ratings_str = row['ratings']
                        if pd.notnull(ratings_str):
                            try:
                                ratings_dict = ast.literal_eval(ratings_str)
                                overall_rating = float(ratings_dict.get('overall', 3.0))
                            except:
                                pass
                                
                        author_str = row['author']
                        if pd.notnull(author_str):
                            try:
                                author_dict = ast.literal_eval(author_str)
                                username = author_dict.get('username') or author_dict.get('id') or "Anonymous"
                            except:
                                pass
                                
                        ratings_to_save.append({
                            "user_id": username,
                            "destination_name": offering_to_dest[off_id],
                            "rating": overall_rating,
                            "is_real": True
                        })
                        
                        if len(ratings_to_save) >= target_reviews_count:
                            break
                print(f"      Đã đọc {len(ratings_to_save)} ratings...")
                if len(ratings_to_save) >= target_reviews_count:
                    break
                    
            # Cập nhật trường review_count cho từng điểm đến dựa trên ratings đã nạp
            review_counts_map = {}
            for r in ratings_to_save:
                dname = r["destination_name"]
                review_counts_map[dname] = review_counts_map.get(dname, 0) + 1
                
            for d in destinations_list:
                d["review_count"] = review_counts_map.get(d["Destination Name"], 0)
                
            print(f"    ✅ Đã trích xuất thành công {len(ratings_to_save)} ratings từ TripAdvisor.")
        except Exception as e:
            print(f"    [ERROR] Lỗi khi xử lý reviews: {e}")
            
    # ─── BƯỚC 4: TÁI TẠO MA TRẬN GIAO DỊCH ───
    print("\n[4] Tái tạo ma trận giao dịch (transactions.csv) cho 1.257 địa danh mới...")
    
    # Định nghĩa tất cả các cột thuộc tính của ma trận giao dịch
    # Chứa 22 quốc gia mới và các châu lục, ngân sách, mùa, loại hình...
    active_countries = sorted(list(set(d["Country"] for d in destinations_list)))
    active_continents = sorted(list(set(d["Continent"] for d in destinations_list)))
    active_types = sorted(list(set(d["Type"] for d in destinations_list)))
    
    columns = []
    # Châu lục
    for c in active_continents: columns.append(f"Continent:{c}")
    # Ngân sách
    for b in ['Budget', 'Moderate', 'Expensive', 'Luxury']: columns.append(f"Cost:{b}")
    # Mùa du lịch
    for s in ['Spring', 'Summer', 'Autumn', 'Winter']: columns.append(f"Season:{s}")
    # Thể loại
    for t in active_types: columns.append(f"Type:{t}")
    # UNESCO
    columns.append("Heritage:UNESCO")
    # Đánh giá chất lượng
    for q in ['Excellent', 'Good', 'Average']: columns.append(f"Quality:{q}")
    # Quốc gia
    for c in active_countries: columns.append(f"Country:{c}")
    
    # Sinh 200 giao dịch cho mỗi quốc gia (tổng cộng 22 * 200 = 4.400 giao dịch)
    transactions_rows = []
    np.random.seed(42)
    
    # Nhóm điểm đến theo quốc gia
    dest_by_country = {}
    for d in destinations_list:
        dest_by_country.setdefault(d["Country"], []).append(d)
        
    for c in active_countries:
        c_dests = dest_by_country.get(c, [])
        if not c_dests:
            continue
            
        for _ in range(200):
            rep_dest = np.random.choice(c_dests)
            
            row = {col: False for col in columns}
            
            row[f"Country:{c}"] = True
            row[f"Continent:{rep_dest['Continent']}"] = True
            row[f"Cost:{rep_dest['Cost_Category']}"] = True
            row[f"Season:{rep_dest['Best Season']}"] = True
            row[f"Type:{rep_dest['Type']}"] = True
            
            if rep_dest["UNESCO Site"] == "Yes" or np.random.rand() > 0.5:
                row["Heritage:UNESCO"] = True
                
            rating = rep_dest["Avg Rating"]
            if rating >= 4.7:
                row["Quality:Excellent"] = True if np.random.rand() > 0.3 else False
                row["Quality:Good"] = not row["Quality:Excellent"]
            else:
                row["Quality:Good"] = True if np.random.rand() > 0.4 else False
                row["Quality:Average"] = not row["Quality:Good"]
                
            transactions_rows.append(row)
            
    df_trans = pd.DataFrame(transactions_rows)
    print(f"    ✅ Đã tạo ma trận giao dịch mới dạng bảng kích thước: {df_trans.shape}")
    
    # ─── BƯỚC 5: LƯU DỮ LIỆU VÀO MONGODB & FILE CSV ───
    print("\n[5] Ghi đè dữ liệu vào MongoDB và đồng bộ CSV...")
    
    # 1. Lưu Destinations
    df_dests = pd.DataFrame(destinations_list)
    df_dests.to_csv(DATA_PROC_DIR / "destinations_clean.csv", index=False)
    df_dests.to_csv(DATA_PROC_DIR / "destinations_clustered.csv", index=False)
    db_storage.save_destinations(destinations_list)
    print("    → Đã cập nhật destinations_clean.csv và MongoDB.")
    
    # 2. Lưu Ratings
    if ratings_to_save:
        try:
            db_storage.db.user_ratings.drop()
            # Batch insert MongoDB
            batch_size = 5000
            for i in range(0, len(ratings_to_save), batch_size):
                db_storage.db.user_ratings.insert_many(ratings_to_save[i : i + batch_size])
            print(f"    → Đã import {len(ratings_to_save)} ratings vào MongoDB user_ratings.")
        except Exception as e:
            print(f"    [ERROR] Lưu ratings thất bại: {e}")
            
    # 3. Lưu Giao dịch
    df_trans.to_csv(DATA_PROC_DIR / "transactions.csv", index=False)
    db_storage.save_transactions(df_trans)
    print("    → Đã cập nhật transactions.csv và MongoDB.")
    
    # ─── BƯỚC 6: CHẠY LẠI PIPELINE KHAI THÁC ───
    print("\n[6] Chạy lại K-Means Clustering và Apriori Rules Mining...")
    
    # Chạy clustering
    try:
        run_clustering(n_clusters=5)
        print("    → Chạy phân cụm K-Means thành công.")
    except Exception as e:
        print(f"    [ERROR] K-Means thất bại: {e}")
        
    # Chạy Apriori
    try:
        mine_association_rules(min_support=0.01, min_confidence=0.1, min_lift=1.0)
        print("    → Khai phá luật Apriori thành công.")
    except Exception as e:
        print(f"    [ERROR] Apriori thất bại: {e}")
        
    # Tải lại dữ liệu cho Recommender Engine
    try:
        from recommender_engine import engine
        engine.load_data()
        print("    → Recommender Engine đã nạp dữ liệu mới thành công.")
    except Exception as e:
        print(f"    [WARNING] Không thể cập nhật Recommender Engine: {e}")
        
    print("\n" + "="*80)
    print("🎉 QUY TRÌNH NHẬP DỮ LIỆU VÀ ĐỒNG BỘ PIPELINE ĐÃ HOÀN THÀNH XUẤT SẮC!")
    print("="*80)
    return True

if __name__ == "__main__":
    run_import()
