"""
Fix incorrect Wikipedia image URLs in destinations CSV.
Strategy: 
- For destinations with PDF/DJVU/wrong Wikipedia URLs, clear the image field
  so the frontend falls back to the curated EXACT_DESTINATION_IMAGES or IMAGES_BY_TYPE
- For destinations missing images entirely, same approach
- Also update MongoDB if available
"""
import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("backend/.env"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "travel_recommender")

# List of destinations with BAD image URLs that need to be cleared
BAD_IMAGE_DESTINATIONS = [
    # PDF/DJVU files
    'Interlaken Adventure',
    'Tromsø Northern Lights Hunting',
    'Tromso Northern Lights Hunting', 
    'Amsterdam Historic Canal Cruise',
    'Bruges Medieval Canal Tour',
    'Hvar Island Sun & Yacht Port',
    'Penang Georgetown Heritage Art',
    'Inle Lake Fisherman Villages',
    'Coffee Triangle Plantation Tour',
    'Galapagos Islands Wildlife cruise',
    'To Sua Ocean Trench Swim',
    'Phuket Patong Beach Party',
    # No image
    'Maafushi Budget Beaches',
    'Vang Vieng Karst Nature Tour',
    # Wrong content (not matching the destination)
    'Innsbruck Alpine Skiing',          # Shows portrait photo
    'Oslo Fjords & Museum Peninsula',   # Shows unrelated boats/barrels
    'Cartagena Spanish Walled City',    # Shows Spanish Cartagena, not Colombian
    'New York Times Square Neon',       # Shows diner instead of Times Square
    'Pokhara Phewa Lake Resort',        # Shows temple instead of lake
    'Panama Canal Miraflores Locks',    # Shows old 1914 photo
]

def fix_csv_images():
    csv_paths = [
        'backend/data/processed/destinations_clustered.csv',
        'backend/data/processed/destinations_clean.csv'
    ]
    
    for path in csv_paths:
        full_path = os.path.join(os.getcwd(), path)
        if not os.path.exists(full_path):
            print(f"File not found: {path}")
            continue
            
        df = pd.read_csv(full_path)
        
        if 'image' not in df.columns:
            df['image'] = ''
        
        updated = 0
        for idx, row in df.iterrows():
            name = row.get('Destination Name', '')
            if name in BAD_IMAGE_DESTINATIONS:
                old_url = str(row.get('image', ''))
                # Clear the image so frontend falls back to curated images
                df.at[idx, 'image'] = ''
                updated += 1
                print(f"  Cleared: {name}")
                if old_url and old_url != 'nan' and old_url.startswith('http'):
                    print(f"    Was: {old_url[:80]}...")
        
        df.to_csv(full_path, index=False)
        print(f"\nCleared {updated} bad images in {path}\n")

def fix_mongodb_images():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        updated = 0
        for name in BAD_IMAGE_DESTINATIONS:
            result = db.destinations.update_one(
                {"Destination Name": name},
                {"$set": {"image": ""}}
            )
            if result.modified_count > 0:
                updated += 1
                print(f"  MongoDB cleared: {name}")
        
        print(f"\nCleared {updated} bad images in MongoDB\n")
        client.close()
    except Exception as e:
        print(f"MongoDB update skipped: {e}")

if __name__ == '__main__':
    print("=== Fixing CSV images ===")
    fix_csv_images()
    
    print("=== Fixing MongoDB images ===")
    fix_mongodb_images()
    
    print("Done! The frontend will now use curated images from imageService.js")
    print("Restart the backend to see changes.")
