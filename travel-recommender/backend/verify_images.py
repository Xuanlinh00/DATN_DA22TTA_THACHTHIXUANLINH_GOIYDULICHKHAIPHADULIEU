# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Get sample by country
countries = ['Morocco', 'Japan', 'France', 'Brazil', 'Australia', 'India', 'USA', 'Germany']
print("Sample destinations by country:")
for country in countries:
    dest = db.destinations.find_one({'Country': country})
    if dest:
        name = dest.get('Destination Name', dest.get('destination', 'N/A'))
        img = dest.get('image', 'NO IMAGE')
        dest_type = dest.get('Type', 'N/A')
        print(f"\n{country} ({dest_type}):")
        print(f"  Name: {name}")
        print(f"  Image: {img[:100]}")

# Count total and with images
total = db.destinations.count_documents({})
has_image = db.destinations.count_documents({'image': {'$exists': True, '$ne': None, '$ne': ''}})
print(f"\nTotal: {total}, With image: {has_image}")

# Show unique images count
all_images = [d.get('image') for d in db.destinations.find({}, {'image': 1})]
unique_images = len(set(img for img in all_images if img))
print(f"Unique image URLs: {unique_images}")
