"""Fetch verified travel images from Wikimedia Commons API."""
import requests
import json

CATEGORIES = {
    "waterfall": ["Niagara Falls", "Iguazu Falls", "Victoria Falls", "Havasu Falls", "Kuang Si Falls", "Plitvice waterfalls", "Angel Falls", "Gullfoss waterfall", "Yosemite Falls", "Ban Gioc Falls", "Seljalandsfoss waterfall", "Detian Falls", "Multnomah Falls", "Rhine Falls", "Dudhsagar Falls"],
    "beach": ["Maldives beach", "Bora Bora lagoon", "Whitehaven Beach", "Navagio Beach Zakynthos", "Maya Bay Thailand", "Anse Source d'Argent", "Copacabana Beach", "Waikiki Beach", "Bondi Beach", "Phu Quoc beach", "Boracay white beach", "El Nido beach", "Phi Phi beach", "Haad Rin beach", "Langkawi beach"],
    "mountain": ["Mount Fuji Japan", "Mount Everest Nepal", "Matterhorn Switzerland", "Mont Blanc Alps", "Mount Kilimanjaro", "Table Mountain Cape Town", "Dolomites Italy", "Patagonia Torres del Paine", "Mount Rainier", "Himalayas Nepal", "Swiss Alps", "Norwegian fjords mountains", "Zhangjiajie mountains", "Banff mountains Canada", "Atlas mountains Morocco"],
    "religious": ["Angkor Wat Cambodia", "Borobudur temple Indonesia", "Shwedagon Pagoda Myanmar", "Wat Phra Kaew Bangkok", "Todaiji temple Nara", "Tiger's Nest Bhutan", "Prambanan temple", "Bagan temples Myanmar", "Golden Temple Amritsar", "Sagrada Familia Barcelona", "Notre Dame Paris", "Hagia Sophia Istanbul", "Fushimi Inari shrine Kyoto", "Tiger Nest monastery", "Kinkaku-ji Kyoto"],
    "historical": ["Colosseum Rome", "Machu Picchu Peru", "Petra Jordan", "Great Wall China", "Taj Mahal India", "Chichen Itza Mexico", "Acropolis Athens", "Stonehenge England", "Angkor Thom Cambodia", "Forbidden City Beijing", "Pompeii ruins Italy", "Ephesus Turkey", "Hampi ruins India", "Sigiriya Sri Lanka", "Persepolis Iran"],
    "nature": ["Amazon rainforest Brazil", "Banff National Park", "Swiss National Park", "Fiordland New Zealand", "Serengeti Tanzania", "Zhangjiajie forest", "Black Forest Germany", "Olympic National Park", "Yosemite Valley", "Ha Long Bay Vietnam", "Galapagos Islands", "Lake Bled Slovenia", "Norwegian fjords", "Lake Baikal Russia", "Iguazu National Park"],
    "adventure": ["Everest base camp trek", "Kilimanjaro climb", "Great Barrier Reef diving", "white water rafting", "skydiving", "rock climbing mountain", "safari Serengeti", "bungee jumping", "kayaking fjord", "paragliding Alps", "ice climbing", "scuba diving coral", "zip line forest", "camel trek desert", "hot air balloon Cappadocia"],
    "cultural": ["Japanese tea ceremony", "Indian Holi festival", "Thai floating market", "Chinese New Year", "Bali rice terraces", "Moroccan souk market", "Turkish bazaar", "Mexican Day of the Dead", "Vietnamese lantern festival", "Cambodian Apsara dance", "Korean hanbok", "Geisha Kyoto Japan", "Indian Diwali festival", "Tibetan prayer flags", "Maori culture New Zealand"],
    "urban": ["Tokyo skyline night", "New York Manhattan skyline", "Dubai skyline Burj Khalifa", "Paris Eiffel Tower city", "London skyline Thames", "Singapore Marina Bay", "Hong Kong skyline", "Shanghai Bund skyline", "Istanbul Bosphorus city", "Barcelona city aerial", "Prague old town aerial", "Amsterdam canals aerial", "Vienna city center", "Sydney Opera House harbor", "Rio de Janeiro Christ Redeemer"],
    "default": ["Globe travel map", "Airport departure board", "Travel backpack mountains", "Road trip highway", "Train station Europe", "Passport stamps travel", "Airplane window view", "Compass navigation", "Hot air balloons festival", "World map vintage", "Suitcase travel stickers", "Adventure hiking trail", "Sunset silhouette travel", "Boat harbor marina", "Camping tent stars"],
}

HEADERS = {'User-Agent': 'TravelRecommenderBot/1.0 (educational project; student@university.edu)'}

def fetch_images(search_term, limit=3):
    """Fetch image thumbnails from Wikimedia Commons."""
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrnamespace": "6",
        "gsrsearch": search_term,
        "gsrlimit": limit * 3,
        "prop": "imageinfo",
        "iiprop": "url|size|mime",
        "iiurlwidth": "600",
        "format": "json"
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        results = []
        for pid, page in pages.items():
            info = page.get("imageinfo", [{}])[0]
            mime = info.get("mime", "")
            thumb = info.get("thumburl", "")
            w = info.get("thumbwidth", 0)
            h = info.get("thumbheight", 0)
            title = page.get("title", "")
            # Only JPEG images, reasonable size, has thumbnail
            if mime in ("image/jpeg", "image/png") and thumb and w > 0 and h > 0:
                # Skip SVGs, GIFs, TIFFs, and very narrow images
                if w < 100 or h < 100:
                    continue
                # Skip obvious non-photo files
                title_lower = title.lower()
                if any(skip in title_lower for skip in ['.svg', '.gif', '.tif', '.pdf', 'icon', 'logo', 'flag', 'coat of arms', 'map ', 'diagram']):
                    continue
                results.append({
                    "title": title,
                    "thumb": thumb,
                    "w": w,
                    "h": h,
                    "search": search_term
                })
        return results
    except Exception as e:
        print(f"  Error fetching '{search_term}': {e}")
        return []

all_results = {}
for cat, terms in CATEGORIES.items():
    print(f"\n=== {cat.upper()} ===")
    cat_urls = []
    for term in terms:
        imgs = fetch_images(term, limit=2)
        for img in imgs:
            if img["thumb"] not in [u["thumb"] for u in cat_urls]:
                cat_urls.append(img)
                print(f"  [{term}] {img['title'][:60]} => {img['thumb'][:80]}...")
            if len(cat_urls) >= 15:
                break
        if len(cat_urls) >= 15:
            break
    all_results[cat] = cat_urls
    print(f"  Found {len(cat_urls)} images for {cat}")

# Save results
with open("wikimedia_verified.json", "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\n=== SUMMARY ===")
for cat, imgs in all_results.items():
    print(f"  {cat}: {len(imgs)} images")
print(f"\nSaved to wikimedia_verified.json")
