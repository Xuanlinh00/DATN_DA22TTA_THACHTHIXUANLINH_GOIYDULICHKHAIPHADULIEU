# -*- coding: utf-8 -*-
"""
Use Wikipedia REST API to get real, correct thumbnail images.
Format: https://en.wikipedia.org/api/rest_v1/page/summary/{article_title}
Returns guaranteed correct images from Wikipedia articles.
"""
import sys
import json
import time
import urllib.request
import urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Wikipedia article titles for each (Country, Type) combination
# These are actual Wikipedia article titles that have good thumbnail images
WIKI_ARTICLES = {
    # ARGENTINA
    ("Argentina", "Adventure"):  "Perito Moreno Glacier",
    ("Argentina", "Beach"):      "Mar del Plata",
    ("Argentina", "City"):       "Buenos Aires",
    ("Argentina", "Historical"): "Iguazu Falls",
    ("Argentina", "Nature"):     "Iguazu Falls",
    ("Argentina", "Religious"):  "Buenos Aires Metropolitan Cathedral",

    # AUSTRALIA
    ("Australia", "Adventure"):  "Great Barrier Reef",
    ("Australia", "Beach"):      "Whitehaven Beach",
    ("Australia", "City"):       "Sydney Opera House",
    ("Australia", "Historical"): "Uluru",
    ("Australia", "Nature"):     "Blue Mountains (New South Wales)",
    ("Australia", "Religious"):  "St Mary's Cathedral, Sydney",

    # BRAZIL
    ("Brazil", "Adventure"):     "Iguazu Falls",
    ("Brazil", "Beach"):         "Ipanema",
    ("Brazil", "City"):          "Christ the Redeemer",
    ("Brazil", "Historical"):    "Pelourinho",
    ("Brazil", "Nature"):        "Amazon rainforest",
    ("Brazil", "Religious"):     "Basilica of Our Lady of Aparecida",

    # CANADA
    ("Canada", "Adventure"):     "Banff National Park",
    ("Canada", "Beach"):         "Cavendish, Prince Edward Island",
    ("Canada", "City"):          "Toronto",
    ("Canada", "Historical"):    "Old Quebec",
    ("Canada", "Nature"):        "Niagara Falls",
    ("Canada", "Religious"):     "Notre-Dame Basilica, Montreal",

    # CHINA
    ("China", "Adventure"):      "Zhangjiajie National Forest Park",
    ("China", "Beach"):          "Sanya",
    ("China", "City"):           "The Bund",
    ("China", "Historical"):     "Great Wall of China",
    ("China", "Nature"):         "Guilin",
    ("China", "Religious"):      "Shaolin Monastery",

    # EGYPT
    ("Egypt", "Adventure"):      "Great Sphinx of Giza",
    ("Egypt", "Beach"):          "Hurghada",
    ("Egypt", "City"):           "Cairo",
    ("Egypt", "Historical"):     "Giza pyramid complex",
    ("Egypt", "Nature"):         "White Desert National Park",
    ("Egypt", "Religious"):      "Abu Simbel temples",

    # FRANCE
    ("France", "Adventure"):     "Chamonix",
    ("France", "Beach"):         "Nice",
    ("France", "City"):          "Eiffel Tower",
    ("France", "Historical"):    "Palace of Versailles",
    ("France", "Nature"):        "Mont Saint-Michel",
    ("France", "Religious"):     "Notre-Dame de Paris",

    # GERMANY
    ("Germany", "Adventure"):    "Zugspitze",
    ("Germany", "Beach"):        "Rügen",
    ("Germany", "City"):         "Brandenburg Gate",
    ("Germany", "Historical"):   "Neuschwanstein Castle",
    ("Germany", "Nature"):       "Black Forest",
    ("Germany", "Religious"):    "Cologne Cathedral",

    # GREECE
    ("Greece", "Adventure"):     "Santorini",
    ("Greece", "Beach"):         "Navagio beach",
    ("Greece", "City"):          "Acropolis of Athens",
    ("Greece", "Historical"):    "Meteora",
    ("Greece", "Nature"):        "Samaria Gorge",
    ("Greece", "Religious"):     "Meteora",

    # INDIA
    ("India", "Adventure"):      "Rishikesh",
    ("India", "Beach"):          "Goa",
    ("India", "City"):           "India Gate",
    ("India", "Historical"):     "Taj Mahal",
    ("India", "Nature"):         "Kerala backwaters",
    ("India", "Religious"):      "Golden Temple",

    # ITALY
    ("Italy", "Adventure"):      "Cinque Terre",
    ("Italy", "Beach"):          "Amalfi Coast",
    ("Italy", "City"):           "Colosseum",
    ("Italy", "Historical"):     "Venice",
    ("Italy", "Nature"):         "Tuscany",
    ("Italy", "Religious"):      "St. Peter's Basilica",

    # JAPAN
    ("Japan", "Adventure"):      "Mount Fuji",
    ("Japan", "Beach"):          "Okinawa Island",
    ("Japan", "City"):           "Shibuya, Tokyo",
    ("Japan", "Historical"):     "Fushimi Inari-taisha",
    ("Japan", "Nature"):         "Arashiyama Bamboo Grove",
    ("Japan", "Religious"):      "Kinkaku-ji",

    # KENYA
    ("Kenya", "Adventure"):      "Maasai Mara National Reserve",
    ("Kenya", "Beach"):          "Diani Beach",
    ("Kenya", "City"):           "Nairobi",
    ("Kenya", "Historical"):     "Lamu Old Town",
    ("Kenya", "Nature"):         "Maasai Mara National Reserve",
    ("Kenya", "Religious"):      "Lamu Old Town",

    # MEXICO
    ("Mexico", "Adventure"):     "Copper Canyon",
    ("Mexico", "Beach"):         "Cancún",
    ("Mexico", "City"):          "Mexico City Metropolitan Cathedral",
    ("Mexico", "Historical"):    "Chichen Itza",
    ("Mexico", "Nature"):        "Cenote",
    ("Mexico", "Religious"):     "Basilica of Our Lady of Guadalupe",

    # MOROCCO
    ("Morocco", "Adventure"):    "Erg Chebbi",
    ("Morocco", "Beach"):        "Agadir",
    ("Morocco", "City"):         "Jemaa el-Fna",
    ("Morocco", "Historical"):   "Fes el Bali",
    ("Morocco", "Nature"):       "Atlas Mountains",
    ("Morocco", "Religious"):    "Hassan II Mosque",

    # NEW ZEALAND
    ("New Zealand", "Adventure"):  "Queenstown, New Zealand",
    ("New Zealand", "Beach"):      "Cathedral Cove",
    ("New Zealand", "City"):       "Auckland",
    ("New Zealand", "Historical"): "Hobbiton Movie Set",
    ("New Zealand", "Nature"):     "Milford Sound",
    ("New Zealand", "Religious"):  "ChristChurch Cathedral",

    # PERU
    ("Peru", "Adventure"):       "Machu Picchu",
    ("Peru", "Beach"):           "Máncora",
    ("Peru", "City"):            "Miraflores District",
    ("Peru", "Historical"):      "Machu Picchu",
    ("Peru", "Nature"):          "Amazon River",
    ("Peru", "Religious"):       "Cusco Cathedral",

    # SOUTH AFRICA
    ("South Africa", "Adventure"):  "Kruger National Park",
    ("South Africa", "Beach"):      "Clifton, Cape Town",
    ("South Africa", "City"):       "Cape Town",
    ("South Africa", "Historical"): "Robben Island",
    ("South Africa", "Nature"):     "Table Mountain",
    ("South Africa", "Religious"):  "Table Mountain",

    # SPAIN
    ("Spain", "Adventure"):      "Pyrenees",
    ("Spain", "Beach"):          "Formentera",
    ("Spain", "City"):           "Sagrada Família",
    ("Spain", "Historical"):     "Alhambra",
    ("Spain", "Nature"):         "Teide National Park",
    ("Spain", "Religious"):      "Santiago de Compostela Cathedral",

    # THAILAND
    ("Thailand", "Adventure"):   "Krabi",
    ("Thailand", "Beach"):       "Ko Phi Phi",
    ("Thailand", "City"):        "Bangkok",
    ("Thailand", "Historical"):  "Ayutthaya Historical Park",
    ("Thailand", "Nature"):      "Doi Inthanon",
    ("Thailand", "Religious"):   "Wat Phra Kaew",

    # USA
    ("USA", "Adventure"):        "Grand Canyon",
    ("USA", "Beach"):            "South Beach, Miami Beach",
    ("USA", "City"):             "New York City",
    ("USA", "Historical"):       "Statue of Liberty",
    ("USA", "Nature"):           "Yellowstone National Park",
    ("USA", "Religious"):        "Washington National Cathedral",

    # VIETNAM
    ("Vietnam", "Adventure"):    "Sa Pa",
    ("Vietnam", "Beach"):        "Ha Long Bay",
    ("Vietnam", "City"):         "Ho Chi Minh City",
    ("Vietnam", "Historical"):   "Hội An",
    ("Vietnam", "Nature"):       "Phong Nha-Kẻ Bàng National Park",
    ("Vietnam", "Religious"):    "One Pillar Pagoda",
}


def get_wikipedia_image(article_title, min_size=300):
    """
    Get thumbnail image URL from Wikipedia REST API.
    Returns URL string or None if not found.
    """
    encoded = urllib.parse.quote(article_title.replace(' ', '_'))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'TravelRecommender/1.0 (educational project)',
            'Accept': 'application/json'
        })
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read().decode('utf-8'))
        
        # Get the best quality thumbnail available
        original = data.get('originalimage', {})
        thumbnail = data.get('thumbnail', {})
        
        # Prefer original if it's large enough
        if original.get('width', 0) >= min_size:
            return original.get('source', '')
        elif thumbnail.get('width', 0) >= min_size:
            # Try to get larger version by replacing size in URL
            thumb_url = thumbnail.get('source', '')
            if thumb_url:
                # Replace the size parameter to get larger image
                import re
                thumb_url = re.sub(r'/\d+px-', '/1280px-', thumb_url)
                return thumb_url
        
        # Return whatever we have
        return (original.get('source') or thumbnail.get('source') or '')
    
    except Exception as e:
        return None


def main():
    print("=" * 65)
    print("FETCHING WIKIPEDIA IMAGES FOR ALL 132 COUNTRY+TYPE COMBOS")
    print("=" * 65)
    
    image_map = {}
    total = len(WIKI_ARTICLES)
    failed = []

    for idx, ((country, dest_type), article) in enumerate(WIKI_ARTICLES.items(), 1):
        sys.stdout.write(f"\r[{idx}/{total}] {country} | {dest_type} - {article[:30]:<30}")
        sys.stdout.flush()
        
        url = get_wikipedia_image(article)
        
        if url:
            image_map[(country, dest_type)] = url
        else:
            failed.append((country, dest_type, article))
        
        time.sleep(0.3)  # Be nice to Wikipedia API
    
    print(f"\n\nSuccessful: {len(image_map)}/{total}")
    
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for c, t, a in failed:
            print(f"  {c}|{t}: {a}")
    
    # Save results
    json_data = {f"{k[0]}|{k[1]}": v for k, v in image_map.items()}
    with open('wikipedia_images.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to wikipedia_images.json")
    
    # Update MongoDB
    print("\nUpdating MongoDB...")
    destinations = list(db.destinations.find({}))
    updated = not_found = 0
    
    for dest in destinations:
        country = dest.get('Country', '')
        dest_type = dest.get('Type', '')
        key = (country, dest_type)
        
        if key in image_map and image_map[key]:
            db.destinations.update_one(
                {'_id': dest['_id']},
                {'$set': {'image': image_map[key]}}
            )
            updated += 1
        else:
            not_found += 1
    
    print(f"Updated: {updated}, No image: {not_found}")
    
    # Sample verification
    print("\n--- Sample results ---")
    for country, dtype in [("Japan","Beach"), ("Morocco","Beach"), ("Brazil","City"),
                            ("Germany","Nature"), ("Vietnam","Beach"), ("India","Historical")]:
        d = db.destinations.find_one({'Country': country, 'Type': dtype})
        if d:
            img = d.get('image', 'NO IMAGE')
            print(f"  {country}|{dtype}: {img[:90]}")
    
    print("\nDone! Please refresh the browser.")


if __name__ == '__main__':
    main()
