# -*- coding: utf-8 -*-
"""
Auto Expand Destinations - Programmatically expands the dataset to ensure
each of the 67 countries has at least 5 high-quality destinations.
Nukes and regenerates the user ratings and transactions to scale up to:
- 330+ Destinations
- 67 Countries
- 10,050 Transactions (150 per country)
- 4,000+ ratings (200 users rating 10-30 destinations each)
"""
import sys
import os
import pandas as pd
import numpy as np
import copy
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mining.mongodb_storage import db_storage

# Template of extra destinations to add to countries to make sure they have at least 5
EXTRA_TEMPLATES = [
    {
        "suffix": "Hidden Valley Trail", "Type": "Nature", "Best Season": "Autumn",
        "Cost_Offset": -20, "Avg Rating": 4.6, "UNESCO Site": "No", "Broader_Type": "Nature",
        "Desc": "Khám phá thung lũng ẩn giấu yên bình và cung đường đi bộ dã ngoại ngắm cảnh tuyệt đẹp."
    },
    {
        "suffix": "Ancient Royal Palace", "Type": "Cultural", "Best Season": "Spring",
        "Cost_Offset": 10, "Avg Rating": 4.7, "UNESCO Site": "Yes", "Broader_Type": "Culture",
        "Desc": "Di tích cung điện hoàng gia cổ kính với kiến trúc độc đáo phản ánh bề dày lịch sử văn hóa."
    },
    {
        "suffix": "Coastal Horizon Beach", "Type": "Beach", "Best Season": "Summer",
        "Cost_Offset": 30, "Avg Rating": 4.8, "UNESCO Site": "No", "Broader_Type": "Nature",
        "Desc": "Bờ cát trắng hoang sơ và làn nước biển trong xanh lý tưởng cho bơi lội và ngắm hoàng hôn."
    },
    {
        "suffix": "Summit Peak Adventure", "Type": "Mountain", "Best Season": "Winter",
        "Cost_Offset": 40, "Avg Rating": 4.9, "UNESCO Site": "No", "Broader_Type": "Nature",
        "Desc": "Chinh phục đỉnh núi phủ tuyết trắng xóa tráng lệ với tầm nhìn toàn cảnh thung lũng hùng vĩ."
    },
    {
        "suffix": "Downtown Promenade", "Type": "Urban", "Best Season": "Spring",
        "Cost_Offset": 0, "Avg Rating": 4.5, "UNESCO Site": "No", "Broader_Type": "Culture",
        "Desc": "Khu đại lộ trung tâm hiện đại nhộn nhịp sầm uất với các cửa hàng, nhà hàng và hoạt động mua sắm."
    },
    {
        "suffix": "Historic Sanctuary Cathedral", "Type": "Historical", "Best Season": "Autumn",
        "Cost_Offset": -10, "Avg Rating": 4.6, "UNESCO Site": "Yes", "Broader_Type": "Culture",
        "Desc": "Thánh đường cổ kính linh thiêng sở hữu các bức họa và điêu khắc nghệ thuật vô giá từ nhiều thế kỷ trước."
    }
]

def auto_expand():
    print("\n[AUTO-EXPAND] Starting programmatic dataset expansion...")
    
    if not db_storage.is_connected():
        print("[ERROR] MongoDB is not connected.")
        return False
        
    # 1. Load current destinations
    destinations = db_storage.load_destinations()
    if not destinations:
        print("[WARNING] No destinations in MongoDB, checking CSV fallback...")
        csv_path = Path(__file__).parent.parent / "data" / "processed" / "destinations_clustered.csv"
        if csv_path.exists():
            df_csv = pd.read_csv(csv_path)
            destinations = df_csv.astype(object).where(pd.notnull(df_csv), None).to_dict('records')
            
    if not destinations:
        print("[ERROR] No destinations found to expand.")
        return False
        
    df_dests = pd.DataFrame(destinations)
    unique_countries = df_dests["Country"].unique().tolist()
    print(f"[AUTO-EXPAND] Currently have {len(df_dests)} destinations across {len(unique_countries)} countries.")
    
    # We will build a list of updated destinations
    updated_dests = destinations.copy()
    max_id = int(df_dests["DestinationID"].max()) if "DestinationID" in df_dests.columns else len(destinations)
    
    np.random.seed(42)
    new_additions_count = 0
    
    for country in unique_countries:
        country_dests = [d for d in updated_dests if d["Country"] == country]
        count = len(country_dests)
        
        # If a country has less than 5 destinations, generate more
        if count < 5:
            needed = 5 - count
            # Use one of the existing destinations as prototype to copy country metadata
            proto = country_dests[0]
            
            for j in range(needed):
                template = EXTRA_TEMPLATES[j % len(EXTRA_TEMPLATES)]
                name = f"{country} {template['suffix']}"
                
                # Check duplicate
                if any(d["Destination Name"].lower() == name.lower() for d in updated_dests):
                    # add index if duplicate
                    name = f"{country} {template['suffix']} {j+1}"
                    
                # Calculate cost based on prototype's average cost
                avg_cost = max(30.0, float(proto.get("Avg Cost (USD/day)") or 100) + template["Cost_Offset"])
                
                # Add small coordinate noise
                lat_noise = np.random.uniform(-0.15, 0.15)
                lon_noise = np.random.uniform(-0.15, 0.15)
                dest_lat = float(proto.get("destination_latitude") or proto.get("country_latitude") or 0) + lat_noise
                dest_lon = float(proto.get("destination_longitude") or proto.get("country_longitude") or 0) + lon_noise
                
                visitors = max(0.2, float(proto.get("Annual Visitors (M)") or 1.5) * np.random.uniform(0.5, 1.5))
                
                cost_cat = "Moderate"
                if avg_cost < 80:
                    cost_cat = "Budget"
                elif avg_cost < 150:
                    cost_cat = "Moderate"
                elif avg_cost < 250:
                    cost_cat = "Expensive"
                else:
                    cost_cat = "Luxury"
                    
                # Base index calculations
                base_col = float(proto.get("cost_of_living_index") or 50.0) * np.random.uniform(0.9, 1.1)
                
                new_id = max_id + new_additions_count + 1
                
                new_dest = copy.deepcopy(proto)
                new_dest.update({
                    "Destination Name": name,
                    "Type": template["Type"],
                    "Avg Cost (USD/day)": float(avg_cost),
                    "Best Season": template["Best Season"],
                    "Avg Rating": float(template["Avg Rating"]),
                    "Annual Visitors (M)": round(visitors, 2),
                    "UNESCO Site": template["UNESCO Site"],
                    "Broader_Type": template["Broader_Type"],
                    "Cost_Category": cost_cat,
                    "DestinationID": int(new_id),
                    "destination": int(new_id),
                    "Popularity": "Very High" if visitors > 5.0 else "High" if visitors > 2.0 else "Medium",
                    "BestTimeToVisit": f"{template['Best Season']} months",
                    "avg_review_rating": float(template["Avg Rating"]),
                    "review_count": int(np.random.randint(2000, 12000)),
                    "popularity_score": round(float(template["Avg Rating"] / 5.0 + visitors / 20.0), 2),
                    "cost_of_living_index": round(base_col, 2),
                    "rent_index": round(base_col * 0.5, 2),
                    "cost_of_living_plus_rent_index": round(base_col * 0.75, 2),
                    "groceries_index": round(base_col * 0.9, 2),
                    "restaurant_price_index": round(base_col * 0.95, 2),
                    "local_purchasing_power_index": round(150.0 - base_col * 0.8, 2),
                    "destination_latitude": float(dest_lat),
                    "destination_longitude": float(dest_lon),
                    "destination_budget_level": cost_cat,
                    "Cluster": 0,
                    "Description": f"{template['Desc']} Địa điểm tuyệt đẹp '{name}' đang chờ đón bước chân khám phá của bạn tại {country}."
                })
                
                # Remove _id if it was copied from proto
                if "_id" in new_dest:
                    del new_dest["_id"]
                    
                updated_dests.append(new_dest)
                new_additions_count += 1
                
    print(f"[AUTO-EXPAND] Generated {new_additions_count} extra destinations.")
    df_updated_dests = pd.DataFrame(updated_dests)
    
    # Save destinations to DB
    db_storage.save_destinations(df_updated_dests)
    
    # Save destinations to CSV
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    df_updated_dests.to_csv(data_dir / "destinations_clustered.csv", index=False)
    df_updated_dests.to_csv(data_dir / "destinations_clean.csv", index=False)
    print(f"[AUTO-EXPAND] Saved {len(df_updated_dests)} destinations to MongoDB and local CSVs.")
    
    # ── 2. TRANSACTIONS GENERATION ──
    # Generate exactly 150 transactions for EVERY single country in the database
    # This guarantees a massive transaction matrix of size: 67 countries * 150 = 10,050 rows
    print("\n[AUTO-EXPAND] Generating complete transactions binary matrix...")
    
    # Get all distinct columns from the current transaction schema
    # (Continent, Cost, Heritage, Quality, Season, Type)
    # We will build a fresh transaction DataFrame to ensure clean header structure
    cols = []
    
    # Continents
    for cnt in df_updated_dests["Continent"].unique():
        cols.append(f"Continent:{cnt}")
    # Cost
    for cst in ["Budget", "Moderate", "Expensive", "Luxury"]:
        cols.append(f"Cost:{cst}")
    # Season
    for ssn in ["Spring", "Summer", "Autumn", "Winter"]:
        cols.append(f"Season:{ssn}")
    # Type
    for typ in df_updated_dests["Type"].unique():
        cols.append(f"Type:{typ}")
        
    cols.extend(["Heritage:UNESCO", "Quality:Excellent", "Quality:Good", "Quality:Average"])
    
    # Add Country:Name columns for all 67 countries
    for country in unique_countries:
        cols.append(f"Country:{country}")
        
    # Create empty list of transaction rows
    new_trans_rows = []
    
    # Map country name to list of its destinations
    country_dest_map = {}
    for d in updated_dests:
        country_dest_map.setdefault(d["Country"], []).append(d)
        
    for country in unique_countries:
        c_dests = country_dest_map.get(country, [])
        
        # Generate 150 transactions for this country
        for _ in range(150):
            rep_dest = np.random.choice(c_dests)
            row = {col: False for col in cols}
            
            # Set target features
            row[f"Country:{country}"] = True
            row[f"Continent:{rep_dest['Continent']}"] = True
            row[f"Cost:{rep_dest['Cost_Category']}"] = True
            row[f"Season:{rep_dest['Best Season']}"] = True
            row[f"Type:{rep_dest['Type']}"] = True
            
            # UNESCO Site
            if rep_dest["UNESCO Site"] == "Yes" or np.random.rand() > 0.5:
                row["Heritage:UNESCO"] = True
                
            # Quality
            rating = rep_dest["Avg Rating"]
            if rating >= 4.7:
                row["Quality:Excellent"] = True if np.random.rand() > 0.3 else False
                row["Quality:Good"] = not row["Quality:Excellent"]
            else:
                row["Quality:Good"] = True if np.random.rand() > 0.4 else False
                row["Quality:Average"] = not row["Quality:Good"]
                
            new_trans_rows.append(row)
            
    df_trans_final = pd.DataFrame(new_trans_rows).fillna(False)
    
    # Save transactions
    db_storage.save_transactions(df_trans_final)
    df_trans_final.to_csv(data_dir / "transactions.csv", index=False)
    print(f"[AUTO-EXPAND] Saved final transactions matrix of shape {df_trans_final.shape} to DB and CSV.")
    
    # ── 3. COLLABORATIVE FILTERING RATINGS GENERATION ──
    # Clean/delete existing simulated ratings and let it regenerate for 200 users on all 330+ destinations
    print("\n[AUTO-EXPAND] Re-generating simulated user ratings matrix for CF...")
    db_storage.db.user_ratings.drop()
    
    from mining.collaborative_filtering import collaborative_recommender
    collaborative_recommender.load_or_generate_ratings()
    
    total_ratings_count = db_storage.db.user_ratings.count_documents({})
    print(f"[AUTO-EXPAND] Successfully populated {total_ratings_count} rating records in MongoDB.")
    
    print("\n[AUTO-EXPAND] Programmatic dataset expansion completed successfully!")
    print(f"Total destinations: {len(df_updated_dests)}")
    print(f"Total countries: {len(unique_countries)}")
    print(f"Total transactions: {len(df_trans_final)}")
    print(f"Total user ratings: {total_ratings_count}")
    print("Please trigger K-Means and Apriori rule mining to rebuild the data profiles.")
    return True

if __name__ == "__main__":
    auto_expand()
