# -*- coding: utf-8 -*-
"""
Utility script to add a new country and its destination to the database,
and automatically generate matching transactions so data mining (Apriori/K-Means)
can operate on the new data.
"""
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from mining.mongodb_storage import db_storage

def add_country_and_mine_data(
    dest_name="Stockholm Gamla Stan",
    country="Sweden",
    continent="Europe",
    dest_type="Cultural",
    avg_cost=120.0,
    best_season="Summer",
    avg_rating=4.8,
    visitors=3.5,
    unesco="Yes",
    lat=59.3293,
    lon=18.0686
):
    print(f"\n[ADD-COUNTRY] Starting process to add {country} ({dest_name})...")
    
    if not db_storage.is_connected():
        print("[ERROR] MongoDB is not connected. Run mongod first.")
        return False

    # 1. Prepare Destination record
    new_dest = {
        "Destination Name": dest_name,
        "Country": country,
        "Continent": continent,
        "Type": dest_type,
        "Avg Cost (USD/day)": float(avg_cost),
        "Best Season": best_season,
        "Avg Rating": float(avg_rating),
        "Annual Visitors (M)": float(visitors),
        "UNESCO Site": unesco,
        "Broader_Type": "Culture" if dest_type in ["Cultural", "Historical"] else "Nature",
        "Cost_Category": "Budget" if avg_cost < 80 else "Moderate" if avg_cost < 150 else "Expensive" if avg_cost < 250 else "Luxury",
        "country_flag": "📍",
        "country_region": continent,
        "country_subregion": continent,
        "country_currency": "USD",
        "country_currency_symbol": "$",
        "country_languages": "English",
        "country_capital": "Capital",
        "country_timezone": "UTC",
        "country_population": 10000000,
        "country_area": 50000,
        "country_alpha2": country[:2].upper(),
        "country_alpha3": country[:3].upper(),
        "country_borders": "",
        "country_latitude": float(lat),
        "country_longitude": float(lon),
        "destination_latitude": float(lat),
        "destination_longitude": float(lon),
        "destination_budget_level": "Moderate",
        "Description": f"Khám phá điểm đến tuyệt vời {dest_name} tại quốc gia {country}."
    }

    # Load current destinations from MongoDB
    current_dests = db_storage.load_destinations()
    df_dests = pd.DataFrame(current_dests)
    
    # Check if duplicate
    if not df_dests.empty and dest_name.lower() in df_dests['Destination Name'].str.lower().tolist():
        print(f"[INFO] Destination '{dest_name}' already exists.")
    else:
        current_dests.append(new_dest)
        db_storage.save_destinations(current_dests)
        print(f"[OK] Added '{dest_name}' to MongoDB destinations.")

        # Save to local CSV files to keep local files in sync
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        df_expanded = pd.DataFrame(current_dests)
        df_expanded.to_csv(data_dir / "destinations_clustered.csv", index=False)
        if (data_dir / "destinations_clean.csv").exists():
            df_expanded.to_csv(data_dir / "destinations_clean.csv", index=False)
        print("[OK] Synchronized local destinations CSV files.")

    # 2. Generate and Add Transactions for the new country
    # Apriori needs transactions to find association rules!
    print(f"[TRANSACTIONS] Generating transactions for Country:{country}...")
    
    transactions = db_storage.load_transactions()
    if not transactions:
        print("[WARNING] No transactions found in MongoDB. Cannot append.")
        return False
        
    df_trans = pd.DataFrame(transactions)
    new_col = f"Country:{country}"
    
    # Fill new column with False for all existing rows
    df_trans[new_col] = False
    
    # Generate 150 new synthetic transaction rows where this country is visited
    # Match the features: Continent, Cost, Season, Type
    new_rows = []
    np.random.seed(42)
    
    for i in range(150):
        # Create a blank row
        row = {col: False for col in df_trans.columns}
        
        # Set new country and its features to True
        row[new_col] = True
        row[f"Continent:{continent}"] = True
        row[f"Cost:{new_dest['Cost_Category']}"] = True
        row[f"Season:{best_season}"] = True
        row[f"Type:{dest_type}"] = True
        
        # Add some random variations (quality, unesco, etc.)
        if unesco == "Yes" or np.random.rand() > 0.5:
            row["Heritage:UNESCO"] = True
            
        row["Quality:Excellent"] = True if np.random.rand() > 0.4 else False
        row["Quality:Good"] = True if not row["Quality:Excellent"] else False
        
        new_rows.append(row)
        
    # Append new rows to transactions dataframe
    df_new_trans = pd.DataFrame(new_rows)
    df_updated_trans = pd.concat([df_trans, df_new_trans], ignore_index=True).fillna(False)
    
    # Save back to MongoDB
    db_storage.save_transactions(df_updated_trans)
    print(f"[OK] Saved {len(df_updated_trans)} transactions (added 150) to MongoDB.")
    
    # Save to local CSV
    trans_csv = Path(__file__).parent.parent / "data" / "processed" / "transactions.csv"
    df_updated_trans.to_csv(trans_csv, index=False)
    print(f"[OK] Saved updated transactions to {trans_csv.name}.")
    
    print(f"\n[SUCCESS] Country '{country}' added! Go to Admin Dashboard to re-run K-Means and Apriori.")
    return True

if __name__ == "__main__":
    # Example: Let's add Sweden as a test!
    add_country_and_mine_data(
        dest_name="Stockholm Gamla Stan",
        country="Sweden",
        continent="Europe",
        dest_type="Cultural",
        avg_cost=120.0,
        best_season="Summer",
        avg_rating=4.8,
        visitors=3.5,
        unesco="Yes",
        lat=59.3293,
        lon=18.0686
    )
