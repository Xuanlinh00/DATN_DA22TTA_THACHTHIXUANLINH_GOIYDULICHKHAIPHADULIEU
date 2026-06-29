# -*- coding: utf-8 -*-
"""
Fix all broken image URLs in imageService.js using Wikimedia Commons API.
Searches for real photos and gets actual thumbnail URLs.
"""
import re, sys, time, json, urllib.request, urllib.error, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

JS_FILE = r"frontend\src\services\imageService.js"
UA = 'TravelRecommenderFixer/1.0 (educational project; datn@student.com)'

# ── Better search queries for marketing-style destination names ──
SEARCH_OVERRIDES = {
    'Interlaken Adventure': 'Interlaken Switzerland landscape',
    'Maafushi Budget Beaches': 'Maafushi Maldives beach',
    'Oslo Fjords & Museum Peninsula': 'Oslo Norway fjord',
    'Tromsø Northern Lights Hunting': 'Tromsø northern lights aurora',
    'Amsterdam Historic Canal Cruise': 'Amsterdam canal houses',
    'Bruges Medieval Canal Tour': 'Bruges Belgium canal Minnewater',
    'Innsbruck Alpine Skiing': 'Innsbruck Austria Alps',
    'Dublin Guinness & Trinity College': 'Dublin Trinity College',
    'Reykjavik Blue Lagoon Spa': 'Blue Lagoon Grindavik Iceland',
    'Warsaw Old Town Restoration': 'Warsaw Old Town Market Square',
    'Tatra Mountains Zakopane': 'Tatra Mountains Poland',
    'Prague Charles Bridge & Castle': 'Prague Charles Bridge Castle',
    'Cesky Krumlov Castle Town': 'Český Krumlov castle',
    'Karlovy Vary Spa Town': 'Karlovy Vary Mill Colonnade',
    'Budapest Parliament on Danube': 'Budapest Parliament Danube',
    'Szechenyi Thermal Bath Pools': 'Széchenyi Thermal Bath Budapest',
    'Lake Balaton Resort Beaches': 'Lake Balaton Hungary',
    'Dubrovnik Game of Thrones Walls': 'Dubrovnik old town walls',
    'Plitvice Lakes Waterfall Trail': 'Plitvice Lakes waterfalls Croatia',
    'Split Diocletian Palace': 'Split Diocletian Palace Croatia',
    'Kuala Lumpur Petronas Towers': 'Kuala Lumpur Petronas Towers',
    'Penang Georgetown Heritage Art': 'Penang Georgetown heritage',
    'Langkawi Cable Car & SkyBridge': 'Langkawi SkyBridge',
    'Kota Kinabalu Nature Trekking': 'Kota Kinabalu Sabah',
    'El Nido Bacuit Bay Islands': 'El Nido Palawan Philippines',
    'Chocolate Hills Bohol Adventure': 'Chocolate Hills Bohol',
    'Intramuros Walled City Manila': 'Intramuros Fort Santiago Manila',
    'Koh Rong Tropical Beaches': 'Koh Rong Cambodia beach',
    'Luang Prabang Heritage Town': 'Luang Prabang Laos temple',
    'Vang Vieng Karst Nature Tour': 'Vang Vieng Laos karst',
    'Kuang Si Turquoise Waterfalls': 'Kuang Si Falls Laos',
    'Inle Lake Fisherman Villages': 'Inle Lake Myanmar fisherman',
    'Shwedagon Pagoda Yangon': 'Shwedagon Pagoda Yangon',
    'Sigiriya Ancient Lion Rock': 'Sigiriya Lion Rock Sri Lanka',
    'Ella Train & Nine Arch Bridge': 'Nine Arch Bridge Ella',
    'Temple of the Tooth Kandy': 'Temple Tooth Kandy',
    'Kathmandu Durbar Square Temples': 'Kathmandu Durbar Square',
    'Everest Base Camp Mountain Trek': 'Mount Everest Nepal',
    'Pokhara Phewa Lake Resort': 'Pokhara Phewa Lake',
    'Taipei 101 Observatory': 'Taipei 101',
    'Jiufen Old Street Lanterns': 'Jiufen Taiwan lanterns',
    'Gobi Desert Singing Dunes': 'Gobi Desert Khongoryn Els',
    'Terelj National Park Ger Camp': 'Terelj National Park Mongolia',
    'Astana Bayterek Tower': 'Bayterek Tower Astana',
    'Cartagena Spanish Walled City': 'Cartagena de Indias Colombia',
    'Coffee Triangle Plantation Tour': 'Coffee plantation Colombia',
    'Easter Island Rapa Nui Moai': 'Easter Island Moai',
    'Galapagos Islands Wildlife cruise': 'Galapagos Islands wildlife',
    'Arenal Volcano Hot Springs': 'Arenal Volcano Costa Rica',
    'Old Havana Classic Cars': 'Havana Cuba classic cars',
    'Varadero Beach Resorts': 'Varadero Beach Cuba',
    'Yasawa Islands Coral Reefs': 'Yasawa Islands Fiji',
    'Serengeti National Park Safari': 'Serengeti Tanzania safari',
    'Mount Kilimanjaro Summit Climb': 'Mount Kilimanjaro Tanzania',
    'Morondava Avenue of Baobabs': 'Avenue Baobabs Madagascar',
    'Phnom Penh Palace & Silver Pagoda': 'Phnom Penh Royal Palace',
    'Phu Quoc Sunset Beach': 'Phu Quoc island sunset',
    'Tromso Northern Lights Hunting': 'Tromsø northern lights',
    'Halong Bay Cruise': 'Ha Long Bay Vietnam',
    'Mekong Delta Floating Market': 'Mekong Delta floating market',
    'Hoi An Ancient Town': 'Hoi An ancient town lanterns',
    'Sahara Desert Camp Merzouga': 'Erg Chebbi Merzouga Sahara',
    'Marrakech Medina Souks': 'Marrakech medina souks',
    'Victoria Falls Zambia': 'Victoria Falls Zambia Zimbabwe',
    'Serengeti Wildebeest Migration': 'Serengeti wildebeest migration',
    'Acropolis of Athens': 'Acropolis Parthenon Athens',
    'Agadir Beach': 'Agadir Morocco beach',
    'Amazon Rainforest': 'Amazon rainforest Brazil',
    'Amboseli National Park': 'Amboseli National Park elephants',
    'Ayutthaya Historical Park': 'Ayutthaya Wat Chaiwatthanaram',
    'Banff National Park': 'Banff National Park Lake Louise',
    'Barceloneta Beach': 'Barceloneta Beach Barcelona',
    'Black Forest': 'Black Forest Germany',
    'Blue Mountains National Park': 'Blue Mountains Three Sisters Australia',
    'Blyde River Canyon Nature Reserve': 'Blyde River Canyon',
    'Buenos Aires': 'Buenos Aires La Boca Caminito',
    'Chamonix-Mont-Blanc': 'Mont Blanc Chamonix Alps',
    'Chichen Itza': 'Chichen Itza pyramid',
    'Christ the Redeemer': 'Christ Redeemer Rio de Janeiro',
    'Cologne Cathedral': 'Cologne Cathedral Germany',
    'Colosseum': 'Colosseum Rome Italy',
    'Copacabana Beach': 'Copacabana Beach Rio',
    'Copper Canyon': 'Copper Canyon Mexico',
    'Cusco': 'Cusco Peru city',
    'Dolomites': 'Dolomites Tre Cime Lavaredo',
    'Drakensberg Mountains': 'Drakensberg Mountains South Africa',
    'Essaouira Beach': 'Essaouira Morocco harbor',
    'Forbidden City': 'Forbidden City Beijing',
    'French Riviera': 'French Riviera Nice',
    'Gorges du Verdon': 'Gorges du Verdon France',
    'Ha Long Bay': 'Ha Long Bay Vietnam',
    'Hassan II Mosque': 'Hassan II Mosque Casablanca',
    'Himeji Castle': 'Himeji Castle Japan',
    'Iguazu Falls': 'Iguazu Falls',
    'Kruger National Park': 'Kruger National Park',
    'Loire Valley': 'Loire Valley Château Chambord',
    'Maasai Mara National Reserve': 'Maasai Mara Kenya',
    'Marrakech': 'Marrakech Jemaa el-Fnaa',
    'Meteora': 'Meteora Greece monasteries',
    'Nairobi': 'Nairobi Kenya skyline',
    'Neuschwanstein Castle': 'Neuschwanstein Castle',
    'Notre Dame Cathedral (Paris)': 'Notre-Dame Paris cathedral',
    'Ouro Preto': 'Ouro Preto Brazil',
    'Perito Moreno Glacier': 'Perito Moreno Glacier Argentina',
    'Phi Phi Islands': 'Phi Phi Islands Thailand',
    'Phong Nha-Ke Bang National Park': 'Phong Nha cave Vietnam',
    'Picos de Europa National Park': 'Picos de Europa Spain',
    'Quebec City': 'Quebec City Château Frontenac',
    'Queenstown': 'Queenstown New Zealand lake',
    'Rio de Janeiro': 'Rio de Janeiro',
    'Rishikesh': 'Rishikesh Lakshman Jhula',
    'Samaria Gorge': 'Samaria Gorge Crete',
    'Santorini': 'Santorini Oia sunset',
    'Sharm El Sheikh': 'Sharm El Sheikh Naama Bay',
    'Statue of Liberty': 'Statue of Liberty New York',
    'Table Mountain (Cape Town)': 'Table Mountain Cape Town',
    'Vancouver': 'Vancouver Canada skyline',
    'Vatican City': 'Vatican City St Peter',
    'Waitangi Treaty Grounds': 'Waitangi Treaty House',
    'Wat Arun (Bangkok)': 'Wat Arun Bangkok',
    'White Desert National Park': 'White Desert Egypt',
    'Zhangjiajie National Forest Park': 'Zhangjiajie National Forest',
    'Hvar Island Sun & Yacht Port': 'Hvar island Croatia',
    'Panama Canal Miraflores Locks': 'Panama Canal Miraflores locks',
    'To Sua Ocean Trench Swim': 'To Sua Ocean Trench Samoa',
    'Chamarel Coloured Earth Dunes': 'Chamarel Seven Coloured Earth',
    'Recoleta Cemetery (Buenos Aires)': 'Recoleta Cemetery Buenos Aires',
    'Pelourinho, Salvador': 'Pelourinho Salvador Bahia',
    'Tofino, Vancouver Island': 'Tofino Vancouver Island',
    'Wat Phra Kaeo (Temple of the Emerald Buddha)': 'Wat Phra Kaew Bangkok',
    'Hassan II Mosque (Casablanca)': 'Hassan II Mosque Casablanca',
    'Meteora Monasteries': 'Meteora Greece monasteries',
    'Santorini Caldera': 'Santorini caldera Oia',
    'Verdon Gorge': 'Gorges du Verdon',
    'Jaipur (Pink City)': 'Hawa Mahal Jaipur',
    'French Riviera Nice Beaches': 'French Riviera Nice beach',
    'Sapa Terrace Rice Fields': 'Sapa rice terraces Vietnam',
    'Trang An Scenic Landscape': 'Trang An Ninh Binh Vietnam',
    'Kyoto Fushimi Inari Shrine': 'Fushimi Inari Taisha Kyoto',
    'Osaka Dotonbori Street Food': 'Dotonbori Osaka Japan',
    'Grand Canyon South Rim': 'Grand Canyon South Rim',
    'New York Times Square Neon': 'Times Square New York',
    'Louvre Art Museum Paris': 'Louvre Museum Paris night',
    'Zhangjiajie Avatar Mountains': 'Zhangjiajie avatar mountains',
    'Shanghai The Bund Skyline': 'Shanghai Bund Pudong skyline',
    'Chiang Mai Lantern Festival': 'Chiang Mai lantern festival',
    'Phuket Patong Beach Party': 'Patong Beach Phuket',
    'Porto Douro Vineyard Valley': 'Douro Valley Portugal vineyard',
    'Tivoli Gardens Theme Park': 'Tivoli Gardens Copenhagen',
    'Reynisfjara Black Sand Beach': 'Reynisfjara black sand beach',
    'Boracay Island White Beach': 'Boracay White Beach',
    'Angkor Wat Heritage Park': 'Angkor Wat Cambodia',
    'Bagan Hot Air Balloon Valley': 'Bagan Burma temples',
    'Taroko Marble Gorge National Park': 'Taroko Gorge Taiwan',
    'Almaty Charyn Canyon': 'Charyn Canyon Kazakhstan',
    'Torres del Paine National Park': 'Torres del Paine Chile',
    'Negril Cliffs & Seven Mile Beach': 'Negril Jamaica beach',
    'La Digue Anse Source Beach': 'La Digue Seychelles beach',
    'Finnish Lakeland & Sauna Tour': 'Lake Saimaa Finland',
    'Killarney Ring of Kerry Tour': 'Ring of Kerry Ireland',
    'Copenhagen Nyhavn Harbour': 'Nyhavn Copenhagen',
    'Kronborg Castle Elsinore': 'Kronborg Castle Elsinore',
    'Rovaniemi Santa Claus Village': 'Santa Claus Village Rovaniemi',
    'Helsinki Cathedral & Market': 'Helsinki Cathedral',
    'Antwerp Diamond District': 'Antwerp diamond district',
    'Vienna Schonbrunn Palace': 'Schönbrunn Palace Vienna',
    'Hallstatt Alpine Village': 'Hallstatt Austria lake',
    'Salzburg Mozart Heritage': 'Salzburg Mozart monument',
    'Lisbon Alfama & Tram 28': 'Lisbon Tram 28 Alfama',
    'Algarve Cliffs & Caves': 'Algarve Portugal cliffs',
    'Sintra Pena Palace': 'Sintra Pena Palace Portugal',
    'Cliffs of Moher Coastal Walk': 'Cliffs of Moher Ireland',
    'Marina Bay Sands & Gardens': 'Marina Bay Sands Singapore',
    'Zermatt Matterhorn Peak': 'Matterhorn Zermatt Switzerland',
    'Maldives Overwater Villas': 'Maldives overwater villas',
    'Santorini Island Sunsets': 'Santorini Oia sunset',
    'Cappadocia Hot Balloons': 'Cappadocia balloons Turkey',
    'Burj Khalifa Dubai': 'Burj Khalifa Dubai',
    'Great Wall of China': 'Great Wall China Badaling',
    'Jaipur City': 'Jaipur City Palace',
    'Kerala Backwaters': 'Kerala backwaters India',
    'Seoul Tower & Palace': 'Gyeongbokgung Palace Seoul',
    'London Big Ben & Eye': 'London Big Ben Eye',
    'Istanbul Hagia Sophia': 'Hagia Sophia Istanbul',
    'Ubud Bali Cultural Tour': 'Ubud Bali Indonesia',
    'Goa Beaches': 'Goa beach India',
    'Jeju Island Beaches': 'Jeju Island Korea beach',
    'Sentosa Island Resort': 'Sentosa Island Singapore',
    'Stockholm Gamla Stan': 'Stockholm Gamla Stan',
    'Geirangerfjord Cruising': 'Geirangerfjord Norway',
    'Bergen Bryggen Wharf': 'Bergen Bryggen wharf Norway',
    'Lofoten Islands Scenic Tour': 'Lofoten Islands Norway',
    'Keukenhof Tulip Festival': 'Keukenhof tulips Netherlands',
    'Zaanse Schans Windmill Village': 'Zaanse Schans windmills',
    'Rotterdam Futuristic Architecture': 'Rotterdam architecture modern',
    'Giethoorn Village Without Roads': 'Giethoorn Netherlands village',
    'Brussels Grand Place': 'Brussels Grand Place Belgium',
    'Ghent Castle of the Counts': 'Gravensteen Ghent castle',
}

def search_wikimedia_image(search_term, min_size=600):
    """Search Wikimedia Commons for a photo and return thumbnail URL."""
    params = urllib.parse.urlencode({
        'action': 'query',
        'generator': 'search',
        'gsrnamespace': '6',
        'gsrsearch': search_term,
        'gsrlimit': '10',
        'prop': 'imageinfo',
        'iiprop': 'url|size|mime',
        'iiurlwidth': '960',
        'format': 'json',
    })
    url = 'https://commons.wikimedia.org/w/api.php?' + params
    
    req = urllib.request.Request(url)
    req.add_header('User-Agent', UA)
    
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        data = json.loads(resp.read().decode('utf-8'))
        
        if 'query' not in data or 'pages' not in data['query']:
            return None
        
        # Sort by title length (shorter = more likely main subject)
        pages = sorted(data['query']['pages'].values(), key=lambda p: len(p.get('title', '')))
        
        for page in pages:
            ii = page.get('imageinfo', [{}])[0]
            w = ii.get('width', 0)
            mime = ii.get('mime', '')
            title = page.get('title', '').lower()
            
            # Skip non-photos and small images
            if 'image' not in mime:
                continue
            if w < min_size:
                continue
            # Skip SVG, diagrams
            if 'svg' in title or 'diagram' in title or 'flag ' in title or 'coat of arms' in title:
                continue
            
            thumb = ii.get('thumburl')
            if thumb:
                return thumb
            # Fallback to full URL
            return ii.get('url')
        
        return None
    except Exception as e:
        print(f"      API error: {e}")
        return None

def check_url(url):
    """Quick check if URL is valid. Returns (ok, code)."""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', UA)
        resp = urllib.request.urlopen(req, timeout=15)
        ct = resp.headers.get('Content-Type', '')
        return ('image' in ct.lower()), resp.getcode()
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return None, e.code  # rate limited, assume OK
        return False, e.code
    except:
        return False, 0

def get_search_term(dest_name):
    """Get the best search term for a destination."""
    if dest_name in SEARCH_OVERRIDES:
        return SEARCH_OVERRIDES[dest_name]
    # Remove parenthesized suffixes
    clean = re.sub(r'\s*\([^)]*\)\s*$', '', dest_name).strip()
    return clean

def main():
    print("=" * 70)
    print("Wikimedia Commons Image Fixer - API-based verification")
    print("=" * 70)
    
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r"'([^']+)':\s*'(https://[^']+)'"
    matches = re.findall(pattern, content)
    print(f"\nFound {len(matches)} URLs in EXACT_DESTINATION_IMAGES\n")
    
    replacements = []  # list of (old_url, new_url, dest_name)
    ok_count = 0
    skip_count = 0
    no_fix = 0
    
    for i, (dest_name, url) in enumerate(matches):
        pct = f"[{i+1}/{len(matches)}]"
        ok, code = check_url(url)
        
        if ok is True:
            ok_count += 1
            print(f"  {pct} OK  [{code}] {dest_name}")
            time.sleep(1.5)
            continue
        
        if ok is None:
            skip_count += 1
            print(f"  {pct} SKIP [{code}] {dest_name} (rate limited, assuming OK)")
            time.sleep(2)
            continue
        
        # Broken URL - find replacement via API
        search_term = get_search_term(dest_name)
        print(f"  {pct} BROKEN [{code}] {dest_name}")
        print(f"       Searching: '{search_term}'")
        
        new_url = search_wikimedia_image(search_term)
        
        if new_url and new_url != url:
            replacements.append((url, new_url, dest_name))
            print(f"       -> FIXED: {new_url[:120]}...")
        elif new_url == url:
            print(f"       -> Same URL from API (keeping)")
            ok_count += 1
        else:
            no_fix += 1
            print(f"       -> NO REPLACEMENT FOUND")
        
        time.sleep(2)  # Be polite to Wikimedia API
    
    # ── Apply all replacements ──
    print(f"\n{'=' * 70}")
    print(f"RESULTS: {ok_count} OK, {len(replacements)} fixed, {no_fix} unfixable, {skip_count} skipped")
    print(f"{'=' * 70}")
    
    if replacements:
        new_content = content
        for old_url, new_url, dest_name in replacements:
            new_content = new_content.replace(old_url, new_url)
        
        with open(JS_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"\nUpdated {len(replacements)} URLs in {JS_FILE}")
        print("\nReplacements applied:")
        for old_url, new_url, dest_name in replacements:
            print(f"  {dest_name}")
    
    if no_fix > 0:
        print(f"\nWARNING: {no_fix} destinations still have broken URLs (no API results found)")
        print("These will fall back to category-based images (IMAGES_BY_TYPE)")

if __name__ == '__main__':
    main()
