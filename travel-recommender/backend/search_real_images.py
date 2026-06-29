# -*- coding: utf-8 -*-
"""
Search DuckDuckGo for real images for each country+type combination.
Uses rate limiting to avoid being blocked.
"""
import sys
import time
import json
sys.stdout.reconfigure(encoding='utf-8')
from duckduckgo_search import DDGS
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# All 132 country+type combinations from the DB
# Curated search queries to get the most iconic/accurate images
SEARCH_QUERIES = {
    # ARGENTINA
    ("Argentina", "Adventure"): "Patagonia Argentina hiking mountains",
    ("Argentina", "Beach"): "Mar del Plata Argentina beach coast",
    ("Argentina", "City"): "Buenos Aires Argentina skyline cityscape",
    ("Argentina", "Historical"): "Iguazu Falls Argentina waterfall",
    ("Argentina", "Nature"): "Perito Moreno glacier Argentina Patagonia",
    ("Argentina", "Religious"): "Cathedral Cordoba Argentina baroque church",

    # AUSTRALIA
    ("Australia", "Adventure"): "Great Barrier Reef Australia diving snorkeling",
    ("Australia", "Beach"): "Whitehaven Beach Australia turquoise water",
    ("Australia", "City"): "Sydney Opera House Harbour Bridge Australia",
    ("Australia", "Historical"): "Uluru Ayers Rock Australia sunset",
    ("Australia", "Nature"): "Blue Mountains Australia eucalyptus forest",
    ("Australia", "Religious"): "St Mary Cathedral Sydney Australia",

    # BRAZIL
    ("Brazil", "Adventure"): "Amazon rainforest Brazil river wildlife",
    ("Brazil", "Beach"): "Ipanema beach Rio de Janeiro Brazil sunset",
    ("Brazil", "City"): "Christ Redeemer Rio de Janeiro Brazil",
    ("Brazil", "Historical"): "Pelourinho Salvador Bahia Brazil colonial",
    ("Brazil", "Nature"): "Pantanal Brazil wetlands wildlife",
    ("Brazil", "Religious"): "Aparecida Cathedral Brazil largest church",

    # CANADA
    ("Canada", "Adventure"): "Banff National Park Canada Rocky Mountains",
    ("Canada", "Beach"): "Prince Edward Island Canada beach",
    ("Canada", "City"): "Toronto skyline Canada CN Tower",
    ("Canada", "Historical"): "Old Quebec City Canada historic streets",
    ("Canada", "Nature"): "Niagara Falls Canada waterfall",
    ("Canada", "Religious"): "Notre-Dame Basilica Montreal Canada",

    # CHINA
    ("China", "Adventure"): "Zhangjiajie Avatar mountains China",
    ("China", "Beach"): "Sanya beach Hainan China tropical",
    ("China", "City"): "Shanghai Pudong skyline China modern",
    ("China", "Historical"): "Great Wall of China Badaling section",
    ("China", "Nature"): "Li River Guilin China landscape",
    ("China", "Religious"): "Shaolin Temple China Buddhist monks",

    # EGYPT
    ("Egypt", "Adventure"): "Sinai desert Egypt camel sunset",
    ("Egypt", "Beach"): "Hurghada Red Sea Egypt beach resort",
    ("Egypt", "City"): "Cairo Egypt Nile River cityscape",
    ("Egypt", "Historical"): "Pyramids of Giza Egypt Sphinx ancient",
    ("Egypt", "Nature"): "White Desert Egypt chalk formations",
    ("Egypt", "Religious"): "Abu Simbel temple Egypt Ramesses",

    # FRANCE
    ("France", "Adventure"): "Chamonix Mont Blanc Alps France skiing",
    ("France", "Beach"): "Nice Promenade Anglais Riviera France beach",
    ("France", "City"): "Eiffel Tower Paris France night lights",
    ("France", "Historical"): "Versailles Palace gardens France",
    ("France", "Nature"): "Dordogne valley France countryside",
    ("France", "Religious"): "Mont Saint Michel France abbey island",

    # GERMANY
    ("Germany", "Adventure"): "Bavaria Alps Germany hiking trails",
    ("Germany", "Beach"): "Rugen island Germany Baltic Sea beach",
    ("Germany", "City"): "Berlin Brandenburg Gate Germany",
    ("Germany", "Historical"): "Neuschwanstein Castle Bavaria Germany",
    ("Germany", "Nature"): "Black Forest Germany autumn",
    ("Germany", "Religious"): "Cologne Cathedral Germany Gothic",

    # GREECE
    ("Greece", "Adventure"): "Santorini caldera Greece sailing",
    ("Greece", "Beach"): "Navagio Shipwreck beach Zakynthos Greece",
    ("Greece", "City"): "Athens Acropolis Parthenon Greece",
    ("Greece", "Historical"): "Meteora monasteries rock pillars Greece",
    ("Greece", "Nature"): "Samaria Gorge Crete Greece landscape",
    ("Greece", "Religious"): "Orthodox Church Santorini blue dome Greece",

    # INDIA
    ("India", "Adventure"): "Rishikesh Ganges river rafting India Himalayas",
    ("India", "Beach"): "Goa beach India palm trees tropical",
    ("India", "City"): "Mumbai India Gateway of India skyline",
    ("India", "Historical"): "Taj Mahal Agra India sunrise",
    ("India", "Nature"): "Kerala backwaters India houseboat",
    ("India", "Religious"): "Golden Temple Amritsar India Sikh",

    # ITALY
    ("Italy", "Adventure"): "Dolomites Italy mountain hiking Alps",
    ("Italy", "Beach"): "Amalfi Coast Italy beach cliffs",
    ("Italy", "City"): "Rome Colosseum Italy ancient ruins",
    ("Italy", "Historical"): "Venice Grand Canal Italy gondola",
    ("Italy", "Nature"): "Tuscany Italy vineyard rolling hills",
    ("Italy", "Religious"): "Vatican St Peters Basilica Rome Italy",

    # JAPAN
    ("Japan", "Adventure"): "Mount Fuji Japan hiking snow",
    ("Japan", "Beach"): "Okinawa Japan coral reef beach",
    ("Japan", "City"): "Tokyo Shibuya crossing Japan neon lights",
    ("Japan", "Historical"): "Kyoto Fushimi Inari shrine torii gates Japan",
    ("Japan", "Nature"): "Arashiyama bamboo forest Kyoto Japan",
    ("Japan", "Religious"): "Kinkaku-ji Golden Pavilion Kyoto Japan",

    # KENYA
    ("Kenya", "Adventure"): "Maasai Mara Safari Kenya wildlife migration",
    ("Kenya", "Beach"): "Diani Beach Kenya Indian Ocean",
    ("Kenya", "City"): "Nairobi Kenya skyline modern city",
    ("Kenya", "Historical"): "Lamu Old Town Kenya Swahili architecture",
    ("Kenya", "Nature"): "Mount Kenya National Park Africa",
    ("Kenya", "Religious"): "Nairobi Cathedral Kenya church",

    # MEXICO
    ("Mexico", "Adventure"): "Copper Canyon Mexico Barrancas",
    ("Mexico", "Beach"): "Cancun Mexico Caribbean beach turquoise",
    ("Mexico", "City"): "Mexico City Zocalo cathedral historic",
    ("Mexico", "Historical"): "Chichen Itza pyramid Mexico Mayan",
    ("Mexico", "Nature"): "Cenote Mexico crystal clear water jungle",
    ("Mexico", "Religious"): "Guadalupe Basilica Mexico City pilgrimage",

    # MOROCCO
    ("Morocco", "Adventure"): "Sahara Desert Morocco sand dunes camel",
    ("Morocco", "Beach"): "Agadir beach Morocco Atlantic Ocean",
    ("Morocco", "City"): "Marrakech medina Morocco souk colorful",
    ("Morocco", "Historical"): "Fes el Bali Morocco ancient medina tanneries",
    ("Morocco", "Nature"): "Atlas Mountains Morocco Toubkal snow",
    ("Morocco", "Religious"): "Hassan II Mosque Casablanca Morocco ocean",

    # NEW ZEALAND
    ("New Zealand", "Adventure"): "Queenstown New Zealand bungee jumping fjord",
    ("New Zealand", "Beach"): "Bay of Islands New Zealand beach",
    ("New Zealand", "City"): "Auckland New Zealand harbor Sky Tower",
    ("New Zealand", "Historical"): "Hobbiton New Zealand Shire movie set",
    ("New Zealand", "Nature"): "Milford Sound New Zealand fiord mountains",
    ("New Zealand", "Religious"): "Christchurch Cathedral New Zealand",

    # PERU
    ("Peru", "Adventure"): "Inca Trail Peru hiking trek Andes",
    ("Peru", "Beach"): "Mancora beach Peru Pacific Ocean surfing",
    ("Peru", "City"): "Lima Peru Miraflores Pacific coast cliffs",
    ("Peru", "Historical"): "Machu Picchu Peru Inca ruins mountains",
    ("Peru", "Nature"): "Amazon Peru jungle wildlife rainforest",
    ("Peru", "Religious"): "Cusco Cathedral Peru baroque colonial",

    # SOUTH AFRICA
    ("South Africa", "Adventure"): "Kruger National Park South Africa safari lion",
    ("South Africa", "Beach"): "Cape Town Clifton beach South Africa",
    ("South Africa", "City"): "Cape Town Table Mountain South Africa",
    ("South Africa", "Historical"): "Robben Island Cape Town South Africa",
    ("South Africa", "Nature"): "Garden Route South Africa coast forest",
    ("South Africa", "Religious"): "Regina Mundi Church Soweto South Africa",

    # SPAIN
    ("Spain", "Adventure"): "Pyrenees Spain hiking mountains",
    ("Spain", "Beach"): "Ibiza beach Spain Mediterranean turquoise",
    ("Spain", "City"): "Sagrada Familia Barcelona Spain Gaudi",
    ("Spain", "Historical"): "Alhambra Palace Granada Spain Moorish",
    ("Spain", "Nature"): "Picos de Europa Spain national park",
    ("Spain", "Religious"): "Santiago de Compostela Cathedral Spain pilgrimage",

    # THAILAND
    ("Thailand", "Adventure"): "Krabi Thailand rock climbing sea kayaking",
    ("Thailand", "Beach"): "Phi Phi Islands Thailand crystal water beach",
    ("Thailand", "City"): "Bangkok Thailand skyline Chao Phraya river",
    ("Thailand", "Historical"): "Ayutthaya ancient temples Thailand",
    ("Thailand", "Nature"): "Chiang Mai Thailand jungle elephants",
    ("Thailand", "Religious"): "Wat Phra Kaew Temple of Emerald Buddha Bangkok",

    # USA
    ("USA", "Adventure"): "Grand Canyon USA Colorado River hiking",
    ("USA", "Beach"): "Miami South Beach Florida USA art deco",
    ("USA", "City"): "New York City Manhattan skyline USA night",
    ("USA", "Historical"): "Statue of Liberty New York USA",
    ("USA", "Nature"): "Yellowstone National Park USA geysers bison",
    ("USA", "Religious"): "Washington National Cathedral USA Gothic",

    # VIETNAM
    ("Vietnam", "Adventure"): "Ha Giang loop Vietnam motorbike mountains",
    ("Vietnam", "Beach"): "Ha Long Bay Vietnam limestone karsts emerald water",
    ("Vietnam", "City"): "Ho Chi Minh City Vietnam motorbike streets",
    ("Vietnam", "Historical"): "Hoi An Ancient Town Vietnam lanterns",
    ("Vietnam", "Nature"): "Sapa Vietnam rice terraces mountains",
    ("Vietnam", "Religious"): "One Pillar Pagoda Hanoi Vietnam Buddhist",
}

def search_image(query, retries=3):
    """Search DuckDuckGo for an image URL."""
    for attempt in range(retries):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=query,
                    max_results=5,
                    type_image="photo",
                    size="large"
                ))
            # Filter out PDFs, SVGs, GIFs and non-image files
            valid = [r for r in results if r.get('image') and
                     any(r['image'].lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']) and
                     'pdf' not in r['image'].lower()]
            if valid:
                return valid[0]['image']
            # If no valid with extension, just return first result
            if results:
                return results[0]['image']
        except Exception as e:
            print(f"  [attempt {attempt+1}] Error: {e}")
            time.sleep(3)
    return None

def main():
    print("=" * 60)
    print("SEARCHING REAL IMAGES FOR EACH COUNTRY+TYPE COMBINATION")
    print("=" * 60)

    image_map = {}
    total = len(SEARCH_QUERIES)
    idx = 0

    for (country, dest_type), query in SEARCH_QUERIES.items():
        idx += 1
        print(f"[{idx}/{total}] {country} | {dest_type}")
        print(f"  Query: {query}")

        url = search_image(query)
        if url:
            image_map[(country, dest_type)] = url
            print(f"  Found: {url[:80]}")
        else:
            print(f"  FAILED - using fallback")

        # Sleep to avoid rate limiting
        time.sleep(2)

    # Save results to JSON for inspection
    json_data = {f"{k[0]}|{k[1]}": v for k, v in image_map.items()}
    with open('image_map_results.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"\nSaved {len(image_map)} image URLs to image_map_results.json")

    # Update MongoDB
    print("\nUpdating MongoDB...")
    updated = 0
    failed = 0
    destinations = list(db.destinations.find({}))

    for dest in destinations:
        country = dest.get('Country', '')
        dest_type = dest.get('Type', '')
        key = (country, dest_type)

        if key in image_map:
            db.destinations.update_one(
                {'_id': dest['_id']},
                {'$set': {'image': image_map[key]}}
            )
            updated += 1
        else:
            failed += 1

    print(f"Updated: {updated}, No image found: {failed}")
    print("\nDone!")

if __name__ == '__main__':
    main()
