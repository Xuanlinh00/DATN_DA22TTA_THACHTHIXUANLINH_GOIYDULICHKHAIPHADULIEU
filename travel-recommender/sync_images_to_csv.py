import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("backend/.env"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "travel_recommender")

def sync_images():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    destinations = list(db.destinations.find({}, {"_id": 0, "Destination Name": 1, "image": 1}))
    
    img_map = {d.get("Destination Name"): d.get("image") for d in destinations if d.get("Destination Name")}
    
    csv_paths = [
        "backend/data/processed/destinations_clustered.csv",
        "backend/data/processed/destinations_clean.csv"
    ]
    
    for path in csv_paths:
        full_path = os.path.join(os.getcwd(), path)
        if os.path.exists(full_path):
            df = pd.read_csv(full_path)
            if "image" not in df.columns:
                df["image"] = ""
            
            updated_count = 0
            for idx, row in df.iterrows():
                name = row.get("Destination Name")
                if name in img_map and img_map[name]:
                    df.at[idx, "image"] = img_map[name]
                    updated_count += 1
                    
            df.to_csv(full_path, index=False)
            print(f"Updated {updated_count} images in {path}")
        else:
            print(f"File not found: {full_path}")

if __name__ == "__main__":
    sync_images()
