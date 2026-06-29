# -*- coding: utf-8 -*-
"""
Test Pixabay API trực tiếp
"""
import requests

PIXABAY_API_KEY = "48556894-3db39c35b54ee3c9e25919f82"

def test_pixabay(country, dest_type):
    """Test Pixabay với country + type"""
    
    type_keywords = {
        'Beach': 'beach ocean tropical paradise coast',
        'Historical': 'historical architecture monument heritage',
        'Nature': 'nature forest waterfall landscape',
        'Religious': 'temple church mosque cathedral',
    }
    
    keywords = type_keywords.get(dest_type, dest_type)
    query = f"{country}+{keywords}".replace(" ", "+")
    
    print(f"Testing Pixabay API")
    print(f"Country: {country}")
    print(f"Type: {dest_type}")
    print(f"Query: {query}")
    print()
    
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "category": "travel",
        "per_page": 3,
        "safesearch": "true"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", [])
            print(f"Total: {data.get('totalHits', 0)}")
            print(f"Found: {len(hits)} images")
            print()
            
            for i, hit in enumerate(hits, 1):
                print(f"{i}. {hit['largeImageURL']}")
                print(f"   Tags: {hit.get('tags', 'N/A')}")
                print()
        else:
            print(f"✗ Error: {response.text}")
    
    except Exception as e:
        print(f"✗ Exception: {e}")


if __name__ == "__main__":
    print("=" * 80)
    print("TEST PIXABAY API")
    print("=" * 80)
    print()
    
    test_pixabay("Thailand", "Beach")
    print("\n" + "=" * 80 + "\n")
    
    test_pixabay("Germany", "Historical")
    print("\n" + "=" * 80 + "\n")
    
    test_pixabay("Japan", "Nature")
