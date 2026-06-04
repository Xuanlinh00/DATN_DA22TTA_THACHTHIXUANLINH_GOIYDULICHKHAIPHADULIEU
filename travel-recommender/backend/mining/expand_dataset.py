# -*- coding: utf-8 -*-
"""
Dataset Expansion Script - Adds 15+ famous destinations from 10 new countries
to expand the dataset diversity and updates MongoDB & local CSVs.
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from mining.mongodb_storage import db_storage

# New destinations data to expand
NEW_DESTINATIONS = [
    # South Korea
    {
        "Destination Name": "Seoul Tower & Palace", "Country": "South Korea", "Continent": "Asia",
        "Type": "Urban", "Avg Cost (USD/day)": 85.0, "Best Season": "Autumn", "Avg Rating": 4.7,
        "Annual Visitors (M)": 12.4, "UNESCO Site": "No", "Broader_Type": "Culture", "Cost_Category": "Moderate",
        "country_flag": "🇰🇷", "country_region": "Asia", "country_subregion": "Eastern Asia",
        "country_currency": "KRW", "country_currency_symbol": "₩", "country_languages": "Korean",
        "country_capital": "Seoul", "country_timezone": "UTC+09:00", "country_population": 51740000,
        "country_area": 100210, "country_alpha2": "KR", "country_alpha3": "KOR", "country_borders": "KP",
        "country_latitude": 35.9078, "country_longitude": 127.7669,
        "destination_latitude": 37.5512, "destination_longitude": 126.9882, "destination_budget_level": "Moderate",
        "Description": "Khám phá tháp Namsan Seoul, các cung điện cổ kính Gyeongbokgung xen lẫn các khu mua sắm sầm uất Myeongdong."
    },
    {
        "Destination Name": "Jeju Island Beaches", "Country": "South Korea", "Continent": "Asia",
        "Type": "Beach", "Avg Cost (USD/day)": 95.0, "Best Season": "Summer", "Avg Rating": 4.6,
        "Annual Visitors (M)": 15.0, "UNESCO Site": "Yes", "Broader_Type": "Nature", "Cost_Category": "Moderate",
        "country_flag": "🇰🇷", "country_region": "Asia", "country_subregion": "Eastern Asia",
        "country_currency": "KRW", "country_currency_symbol": "₩", "country_languages": "Korean",
        "country_capital": "Seoul", "country_timezone": "UTC+09:00", "country_population": 51740000,
        "country_area": 100210, "country_alpha2": "KR", "country_alpha3": "KOR", "country_borders": "KP",
        "country_latitude": 35.9078, "country_longitude": 127.7669,
        "destination_latitude": 33.4996, "destination_longitude": 126.5312, "destination_budget_level": "Moderate",
        "Description": "Hòn đảo thiên đường với các bãi biển cát trắng, thác nước hùng vĩ và đỉnh núi lửa Hallasan độc đáo."
    },
    # Singapore
    {
        "Destination Name": "Marina Bay Sands & Gardens", "Country": "Singapore", "Continent": "Asia",
        "Type": "Urban", "Avg Cost (USD/day)": 280.0, "Best Season": "Spring", "Avg Rating": 4.9,
        "Annual Visitors (M)": 20.2, "UNESCO Site": "No", "Broader_Type": "Modern", "Cost_Category": "Luxury",
        "country_flag": "🇸🇬", "country_region": "Asia", "country_subregion": "South-Eastern Asia",
        "country_currency": "SGD", "country_currency_symbol": "$", "country_languages": "English, Malay, Mandarin, Tamil",
        "country_capital": "Singapore", "country_timezone": "UTC+08:00", "country_population": 5686000,
        "country_area": 728, "country_alpha2": "SG", "country_alpha3": "SGP", "country_borders": "",
        "country_latitude": 1.3521, "country_longitude": 103.8198,
        "destination_latitude": 1.2879, "destination_longitude": 103.8596, "destination_budget_level": "Luxury",
        "Description": "Biểu tượng hiện đại của Singapore với siêu công viên cây xanh nhân tạo Gardens by the Bay và hồ bơi vô cực trên cao."
    },
    {
        "Destination Name": "Sentosa Island Resort", "Country": "Singapore", "Continent": "Asia",
        "Type": "Beach", "Avg Cost (USD/day)": 180.0, "Best Season": "Summer", "Avg Rating": 4.5,
        "Annual Visitors (M)": 19.0, "UNESCO Site": "No", "Broader_Type": "Adventure", "Cost_Category": "Expensive",
        "country_flag": "🇸🇬", "country_region": "Asia", "country_subregion": "South-Eastern Asia",
        "country_currency": "SGD", "country_currency_symbol": "$", "country_languages": "English, Malay, Mandarin, Tamil",
        "country_capital": "Singapore", "country_timezone": "UTC+08:00", "country_population": 5686000,
        "country_area": 728, "country_alpha2": "SG", "country_alpha3": "SGP", "country_borders": "",
        "country_latitude": 1.3521, "country_longitude": 103.8198,
        "destination_latitude": 1.2494, "destination_longitude": 103.8303, "destination_budget_level": "Expensive",
        "Description": "Hòn đảo vui chơi giải trí hàng đầu với công viên Universal Studios, các bãi biển nhân tạo xinh đẹp và resort cao cấp."
    },
    # Switzerland
    {
        "Destination Name": "Zermatt Matterhorn Peak", "Country": "Switzerland", "Continent": "Europe",
        "Type": "Mountain", "Avg Cost (USD/day)": 320.0, "Best Season": "Winter", "Avg Rating": 4.9,
        "Annual Visitors (M)": 2.5, "UNESCO Site": "No", "Broader_Type": "Nature", "Cost_Category": "Luxury",
        "country_flag": "🇨🇭", "country_region": "Europe", "country_subregion": "Western Europe",
        "country_currency": "CHF", "country_currency_symbol": "CHF", "country_languages": "German, French, Italian, Romansh",
        "country_capital": "Bern", "country_timezone": "UTC+01:00", "country_population": 8570000,
        "country_area": 41285, "country_alpha2": "CH", "country_alpha3": "CHE", "country_borders": "FR, DE, IT, AT, LI",
        "country_latitude": 46.8182, "country_longitude": 8.2275,
        "destination_latitude": 45.9763, "destination_longitude": 7.6586, "destination_budget_level": "Luxury",
        "Description": "Trải nghiệm trượt tuyết và ngắm đỉnh núi Matterhorn hình chóp nổi tiếng thế giới tại ngôi làng không khói xe Zermatt."
    },
    {
        "Destination Name": "Interlaken Adventure", "Country": "Switzerland", "Continent": "Europe",
        "Type": "Adventure", "Avg Cost (USD/day)": 210.0, "Best Season": "Summer", "Avg Rating": 4.8,
        "Annual Visitors (M)": 3.1, "UNESCO Site": "No", "Broader_Type": "Nature", "Cost_Category": "Expensive",
        "country_flag": "🇨🇭", "country_region": "Europe", "country_subregion": "Western Europe",
        "country_currency": "CHF", "country_currency_symbol": "CHF", "country_languages": "German, French, Italian, Romansh",
        "country_capital": "Bern", "country_timezone": "UTC+01:00", "country_population": 8570000,
        "country_area": 41285, "country_alpha2": "CH", "country_alpha3": "CHE", "country_borders": "FR, DE, IT, AT, LI",
        "country_latitude": 46.8182, "country_longitude": 8.2275,
        "destination_latitude": 46.6863, "destination_longitude": 7.8632, "destination_budget_level": "Expensive",
        "Description": "Thành phố nằm giữa hai hồ nước tuyệt đẹp Brienz và Thun, trung tâm của các môn thể thao mạo hiểm như nhảy dù, leo núi."
    },
    # United Kingdom
    {
        "Destination Name": "London Big Ben & Eye", "Country": "United Kingdom", "Continent": "Europe",
        "Type": "Urban", "Avg Cost (USD/day)": 190.0, "Best Season": "Spring", "Avg Rating": 4.7,
        "Annual Visitors (M)": 19.1, "UNESCO Site": "Yes", "Broader_Type": "Culture", "Cost_Category": "Expensive",
        "country_flag": "🇬🇧", "country_region": "Europe", "country_subregion": "Northern Europe",
        "country_currency": "GBP", "country_currency_symbol": "£", "country_languages": "English",
        "country_capital": "London", "country_timezone": "UTC+00:00", "country_population": 66830000,
        "country_area": 242495, "country_alpha2": "GB", "country_alpha3": "GBR", "country_borders": "IE",
        "country_latitude": 55.3781, "country_longitude": -3.4360,
        "destination_latitude": 51.5007, "destination_longitude": -0.1246, "destination_budget_level": "Expensive",
        "Description": "Khám phá thủ đô London với tháp đồng hồ Big Ben cổ kính, vòng quay London Eye bên sông Thames và cung điện Buckingham."
    },
    # Maldives
    {
        "Destination Name": "Maldives Overwater Villas", "Country": "Maldives", "Continent": "Asia",
        "Type": "Beach", "Avg Cost (USD/day)": 450.0, "Best Season": "Winter", "Avg Rating": 4.9,
        "Annual Visitors (M)": 1.7, "UNESCO Site": "No", "Broader_Type": "Nature", "Cost_Category": "Luxury",
        "country_flag": "🇲🇻", "country_region": "Asia", "country_subregion": "Southern Asia",
        "country_currency": "MVR", "country_currency_symbol": "Rf", "country_languages": "Dhivehi",
        "country_capital": "Malé", "country_timezone": "UTC+05:00", "country_population": 530000,
        "country_area": 300, "country_alpha2": "MV", "country_alpha3": "MDV", "country_borders": "",
        "country_latitude": 3.2028, "country_longitude": 73.2207,
        "destination_latitude": 4.1755, "destination_longitude": 73.5093, "destination_budget_level": "Luxury",
        "Description": "Thiên đường nghỉ dưỡng với các villa nổi trên mặt nước biển xanh ngọc trong vắt, rặng san hô phong phú bậc nhất."
    },
    {
        "Destination Name": "Maafushi Budget Beaches", "Country": "Maldives", "Continent": "Asia",
        "Type": "Beach", "Avg Cost (USD/day)": 60.0, "Best Season": "Winter", "Avg Rating": 4.4,
        "Annual Visitors (M)": 0.5, "UNESCO Site": "No", "Broader_Type": "Nature", "Cost_Category": "Budget",
        "country_flag": "🇲🇻", "country_region": "Asia", "country_subregion": "Southern Asia",
        "country_currency": "MVR", "country_currency_symbol": "Rf", "country_languages": "Dhivehi",
        "country_capital": "Malé", "country_timezone": "UTC+05:00", "country_population": 530000,
        "country_area": 300, "country_alpha2": "MV", "country_alpha3": "MDV", "country_borders": "",
        "country_latitude": 3.2028, "country_longitude": 73.2207,
        "destination_latitude": 3.9442, "destination_longitude": 73.4891, "destination_budget_level": "Budget",
        "Description": "Khám phá Maldives tiết kiệm tại đảo dân sinh Maafushi với các tour ngắm cá heo, lặn biển và bãi biển cát trắng."
    },
    # Turkey
    {
        "Destination Name": "Cappadocia Hot Balloons", "Country": "Turkey", "Continent": "Asia",
        "Type": "Adventure", "Avg Cost (USD/day)": 110.0, "Best Season": "Autumn", "Avg Rating": 4.8,
        "Annual Visitors (M)": 3.8, "UNESCO Site": "Yes", "Broader_Type": "Nature", "Cost_Category": "Moderate",
        "country_flag": "🇹🇷", "country_region": "Asia", "country_subregion": "Western Asia",
        "country_currency": "TRY", "country_currency_symbol": "₺", "country_languages": "Turkish",
        "country_capital": "Ankara", "country_timezone": "UTC+03:00", "country_population": 83150000,
        "country_area": 783562, "country_alpha2": "TR", "country_alpha3": "TUR", "country_borders": "AM, AZ, BG, GE, GR, IR, IQ, SY",
        "country_latitude": 38.9637, "country_longitude": 35.2433,
        "destination_latitude": 38.6431, "destination_longitude": 34.8289, "destination_budget_level": "Moderate",
        "Description": "Chiêm ngưỡng thung lũng đá kỳ vĩ của Cappadocia trên những quả khinh khí cầu rực rỡ sắc màu vào lúc bình minh."
    },
    {
        "Destination Name": "Istanbul Hagia Sophia", "Country": "Turkey", "Continent": "Europe",
        "Type": "Cultural", "Avg Cost (USD/day)": 50.0, "Best Season": "Spring", "Avg Rating": 4.7,
        "Annual Visitors (M)": 14.5, "UNESCO Site": "Yes", "Broader_Type": "Culture", "Cost_Category": "Budget",
        "country_flag": "🇹🇷", "country_region": "Europe", "country_subregion": "Southern Europe",
        "country_currency": "TRY", "country_currency_symbol": "₺", "country_languages": "Turkish",
        "country_capital": "Ankara", "country_timezone": "UTC+03:00", "country_population": 83150000,
        "country_area": 783562, "country_alpha2": "TR", "country_alpha3": "TUR", "country_borders": "AM, AZ, BG, GE, GR, IR, IQ, SY",
        "country_latitude": 38.9637, "country_longitude": 35.2433,
        "destination_latitude": 41.0082, "destination_longitude": 28.9784, "destination_budget_level": "Budget",
        "Description": "Thành phố nối liền hai lục địa Á-Âu lịch sử với thánh đường cổ kính Hagia Sophia và chợ gia vị Grand Bazaar sầm uất."
    },
    # UAE
    {
        "Destination Name": "Burj Khalifa Dubai", "Country": "United Arab Emirates", "Continent": "Asia",
        "Type": "Urban", "Avg Cost (USD/day)": 260.0, "Best Season": "Winter", "Avg Rating": 4.8,
        "Annual Visitors (M)": 16.7, "UNESCO Site": "No", "Broader_Type": "Modern", "Cost_Category": "Luxury",
        "country_flag": "🇦🇪", "country_region": "Asia", "country_subregion": "Western Asia",
        "country_currency": "AED", "country_currency_symbol": "د.إ", "country_languages": "Arabic, English",
        "country_capital": "Abu Dhabi", "country_timezone": "UTC+04:00", "country_population": 9770000,
        "country_area": 83600, "country_alpha2": "AE", "country_alpha3": "ARE", "country_borders": "OM, SA",
        "country_latitude": 23.4241, "country_longitude": 53.8478,
        "destination_latitude": 25.1972, "destination_longitude": 55.2744, "destination_budget_level": "Luxury",
        "Description": "Đứng trên đỉnh tòa nhà cao nhất thế giới Burj Khalifa và ngắm nhạc nước Dubai Fountain hoành tráng giữa sa mạc."
    },
    # China
    {
        "Destination Name": "Great Wall of China", "Country": "China", "Continent": "Asia",
        "Type": "Cultural", "Avg Cost (USD/day)": 75.0, "Best Season": "Autumn", "Avg Rating": 4.8,
        "Annual Visitors (M)": 10.0, "UNESCO Site": "Yes", "Broader_Type": "Culture", "Cost_Category": "Moderate",
        "country_flag": "🇨🇳", "country_region": "Asia", "country_subregion": "Eastern Asia",
        "country_currency": "CNY", "country_currency_symbol": "¥", "country_languages": "Mandarin",
        "country_capital": "Beijing", "country_timezone": "UTC+08:00", "country_population": 1402000000,
        "country_area": 9600000, "country_alpha2": "CN", "country_alpha3": "CHN", "country_borders": "AF, BT, MMR, IN, KAZ, KG, LAO, MNG, NPL, KP, PK, RU, TJK, VN",
        "country_latitude": 35.8617, "country_longitude": 104.1954,
        "destination_latitude": 40.4319, "destination_longitude": 116.5704, "destination_budget_level": "Moderate",
        "Description": "Kỳ quan Vạn Lý Trường Thành uốn lượn qua các dãy núi trùng điệp, minh chứng lịch sử vĩ đại của Trung Hoa."
    },
    # Indonesia
    {
        "Destination Name": "Ubud Bali Cultural Tour", "Country": "Indonesia", "Continent": "Asia",
        "Type": "Cultural", "Avg Cost (USD/day)": 70.0, "Best Season": "Summer", "Avg Rating": 4.7,
        "Annual Visitors (M)": 6.3, "UNESCO Site": "No", "Broader_Type": "Culture", "Cost_Category": "Moderate",
        "country_flag": "🇮🇩", "country_region": "Asia", "country_subregion": "South-Eastern Asia",
        "country_currency": "IDR", "country_currency_symbol": "Rp", "country_languages": "Indonesian",
        "country_capital": "Jakarta", "country_timezone": "UTC+07:00", "country_population": 270600000,
        "country_area": 1904569, "country_alpha2": "ID", "country_alpha3": "IDN", "country_borders": "TL, MY, PG",
        "country_latitude": -0.7893, "country_longitude": 113.9213,
        "destination_latitude": -8.5069, "destination_longitude": 115.2625, "destination_budget_level": "Moderate",
        "Description": "Trải nghiệm văn hóa tâm linh độc đáo của đảo Bali tại Ubud với ruộng bậc thang Tegallalang và các ngôi đền Hindu cổ kính."
    },
    # Greece
    {
        "Destination Name": "Santorini Island Sunsets", "Country": "Greece", "Continent": "Europe",
        "Type": "Beach", "Avg Cost (USD/day)": 290.0, "Best Season": "Summer", "Avg Rating": 4.9,
        "Annual Visitors (M)": 2.0, "UNESCO Site": "No", "Broader_Type": "Nature", "Cost_Category": "Luxury",
        "country_flag": "🇬🇷", "country_region": "Europe", "country_subregion": "Southern Europe",
        "country_currency": "EUR", "country_currency_symbol": "€", "country_languages": "Greek",
        "country_capital": "Athens", "country_timezone": "UTC+02:00", "country_population": 10720000,
        "country_area": 131957, "country_alpha2": "GR", "country_alpha3": "GRC", "country_borders": "AL, BG, TR, MKD",
        "country_latitude": 39.0742, "country_longitude": 21.8243,
        "destination_latitude": 36.3932, "destination_longitude": 25.4615, "destination_budget_level": "Luxury",
        "Description": "Hòn đảo thần thoại Hy Lạp nổi tiếng với những ngôi nhà vách đá màu trắng mái vòm xanh và cảnh hoàng hôn lãng mạn bậc nhất."
    }
]

def expand():
    print("[EXPAND] Loading current destinations...")
    current_records = db_storage.load_destinations()
    
    # Fallback to CSV if MongoDB load empty
    csv_path = Path(__file__).parent.parent / "data" / "processed" / "destinations_clustered.csv"
    if not current_records:
        print("[WARNING] No destinations in MongoDB, checking CSV fallback...")
        if csv_path.exists():
            df_csv = pd.read_csv(csv_path)
            current_records = df_csv.astype(object).where(pd.notnull(df_csv), None).to_dict('records')
            print(f"[EXPAND] Loaded {len(current_records)} destinations from CSV")
        else:
            current_records = []
            
    df_current = pd.DataFrame(current_records)
    
    added_count = 0
    records_to_save = current_records.copy()
    
    existing_names = set()
    if not df_current.empty and 'Destination Name' in df_current.columns:
        existing_names = set(df_current['Destination Name'].str.lower().tolist())
        
    for dest in NEW_DESTINATIONS:
        if dest["Destination Name"].lower() not in existing_names:
            records_to_save.append(dest)
            added_count += 1
            print(f"[EXPAND] Added new destination: {dest['Destination Name']} ({dest['Country']})")
            
    if added_count > 0:
        # Save to MongoDB
        if db_storage.is_connected():
            success = db_storage.save_destinations(records_to_save)
            if success:
                print(f"[EXPAND] Successfully saved {len(records_to_save)} destinations to MongoDB")
            else:
                print("[ERROR] Failed to save expanded destinations to MongoDB")
        else:
            print("[WARNING] MongoDB is not connected. Data will only be saved to local CSV.")
            
        # Write back to local CSV files to keep files updated
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        df_expanded = pd.DataFrame(records_to_save)
        
        # Save to destinations_clustered.csv
        clustered_csv = data_dir / "destinations_clustered.csv"
        df_expanded.to_csv(clustered_csv, index=False)
        print(f"[EXPAND] Saved to {clustered_csv.name}")
        
        # Save to destinations_clean.csv
        clean_csv = data_dir / "destinations_clean.csv"
        if clean_csv.exists():
            df_expanded.to_csv(clean_csv, index=False)
            print(f"[EXPAND] Saved to {clean_csv.name}")
            
        print(f"[EXPAND] Dataset successfully expanded! Added {added_count} destinations.")
    else:
        print("[EXPAND] No new destinations to add. All are already present in the dataset.")

if __name__ == "__main__":
    expand()
