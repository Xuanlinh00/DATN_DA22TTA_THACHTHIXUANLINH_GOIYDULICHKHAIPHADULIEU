# -*- coding: utf-8 -*-
"""
Test Unsplash API trực tiếp
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

def test_unsplash(country, dest_type):
    """Test Unsplash với country + type"""
    
    # Mapping type sang keywords
    type_keywords = {
        'Beach': 'beach paradise tropical coastline',
        'Mountain': 'mountain peak alpine hiking landscape',
        'Historical': 'historical heritage ancient architecture landmark',
        'Cultural': 'culture traditional festival temple',
        'Adventure': 'adventure nature wilderness outdoor',
        'Religious': 'temple mosque church cathedral religious',
        'City': 'city skyline urban architecture downtown',
        'Nature': 'nature forest waterfall scenic landscape',
    }
    
    keywords = type_keywords.get(dest_type, dest_type)
    query = f"{country} {keywords}"
    
    print(f"Testing Unsplash API")
    print(f"Country: {country}")
    print(f"Type: {dest_type}")
    print(f"Query: {query}")
    print()
    
    if not UNSPLASH_ACCESS_KEY:
        print("✗ UNSPLASH_ACCESS_KEY not found!")
        return
    
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 3,
        "orientation": "landscape",
        "content_filter": "high"
    }
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            print(f"Total results: {data.get('total', 0)}")
            print(f"Found: {len(results)} images")
            print()
            
            for i, photo in enumerate(results, 1):
                print(f"{i}. {photo['urls']['regular']}")
                print(f"   Description: {photo.get('description', 'N/A')}")
                print(f"   Alt: {photo.get('alt_description', 'N/A')}")
                print()
        else:
            print(f"✗ Error: {response.text}")
    
    except Exception as e:
        print(f"✗ Exception: {e}")


if __name__ == "__main__":
    print("=" * 80)
    print("TEST UNSPLASH API")
    print("=" * 80)
    print()
    
    # Test với một vài ví dụ
    test_unsplash("Thailand", "Beach")
    print("\n" + "=" * 80 + "\n")
    
    test_unsplash("Germany", "Historical")
    print("\n" + "=" * 80 + "\n")
    
    test_unsplash("Japan", "Nature")
