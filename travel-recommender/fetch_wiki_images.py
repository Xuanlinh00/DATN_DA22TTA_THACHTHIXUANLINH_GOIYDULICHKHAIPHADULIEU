import pandas as pd
import requests
import json
import time
from pathlib import Path
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv(Path("backend/.env"))
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "travel_recommender")

def get_wikipedia_image(query):
    # Try exact match first
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json&srlimit=1"
    try:
        search_res = requests.get(search_url, timeout=10).json()
        if search_res.get('query', {}).get('search'):
            title = search_res['query']['search'][0]['title']
            
            # Get image for this title
            img_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&pithumbsize=800&format=json"
            img_res = requests.get(img_url, timeout=10).json()
            pages = img_res.get('query', {}).get('pages', {})
            for page_id, page_info in pages.items():
                if 'thumbnail' in page_info:
                    return page_info['thumbnail']['source']
    except Exception as e:
        print(f"Error for {query}: {e}")
    return None

def main():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        destinations = list(db.destinations.find({}))
        print(f"Found {len(destinations)} destinations.")
        
        updates = 0
        for dest in destinations:
            name = dest.get("Destination Name")
            country = dest.get("Country", "")
            
            # Always try to fetch if we don't have a good image or it's None
            query = f"{name} {country}"
            img_url = get_wikipedia_image(query)
            if img_url:
                db.destinations.update_one({"_id": dest["_id"]}, {"$set": {"image": img_url}})
                print(f"Updated {name}: {img_url}")
                updates += 1
            else:
                # Try just name
                img_url2 = get_wikipedia_image(name)
                if img_url2:
                    db.destinations.update_one({"_id": dest["_id"]}, {"$set": {"image": img_url2}})
                    print(f"Updated {name} (name only): {img_url2}")
                    updates += 1
                else:
                    print(f"Could not find image for {name}")
            
            time.sleep(0.1) # Respect API limits
            
        print(f"Successfully updated {updates} destinations with Wikipedia images.")
    except Exception as e:
        print("Mongo Error:", e)

if __name__ == "__main__":
    main()
