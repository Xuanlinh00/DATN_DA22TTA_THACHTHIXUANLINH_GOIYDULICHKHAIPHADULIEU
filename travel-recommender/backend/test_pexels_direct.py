# -*- coding: utf-8 -*-
"""
Test Pexels API trực tiếp
"""
import requests

PEXELS_API_KEY = "LKRcYOJhfxM5QrZIVdw9gPtk6bkVUv84XLZaW1P0zHAsgkxvEV2q0LhS"

def test_pexels(country, dest_type):
    """Test Pexels với country + type"""
    
    type_keywords = {
        'Beach': 'beach paradise tropical coastline ocean',
        'Historical': 'historical heritage ancient architecture landmark',
        'Nature': 'nature forest waterfall scenic landscape',
        'Religious': 'temple mosque church cathedral religious',
    }
    
    keywords = type_keywords.get(dest_type, dest_type)
    query = f"{country} {keywords}"
    
    print(f"Testing Pexels API")
    print(f"Country: {country}")
    print(f"Type: {dest_type}")
    print(f"Query: {query}")
    print()
    
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": 3,
        "orientation": "landscape"
    }
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            print(f"Found: {len(photos)} images")
            print()
            
            for i, photo in enumerate(photos, 1):
                print(f"{i}. {photo['src']['large2x']}")
                print(f"   Photographer: {photo.get('photographer', 'N/A')}")
                print(f"   Alt: {photo.get('alt', 'N/A')}")
                print()
        else:
            print(f"✗ Error: {response.text}")
    
    except Exception as e:
        print(f"✗ Exception: {e}")


if __name__ == "__main__":
    print("=" * 80)
    print("TEST PEXELS API")
    print("=" * 80)
    print()
    
    test_pexels("Thailand", "Beach")
    print("\n" + "=" * 80 + "\n")
    
    test_pexels("Germany", "Historical")
    print("\n" + "=" * 80 + "\n")
    
    test_pexels("Japan", "Nature")
