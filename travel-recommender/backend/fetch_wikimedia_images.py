# -*- coding: utf-8 -*-
"""
Use Wikimedia Commons API to find correct, working image URLs.
"""
import sys
import urllib.request
import urllib.parse
import json
import time
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

def get_wikimedia_url(filename):
    """Get direct URL for a Wikimedia Commons file using the API."""
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "1280",
        "format": "json"
    }
    url = api_url + "?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TravelApp/1.0 (travel-recommender)'})
        r = urllib.request.urlopen(req, timeout=8)
        data = json.loads(r.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            info = page.get('imageinfo', [])
            if info:
                return info[0].get('thumburl', info[0].get('url', ''))
    except Exception as e:
        print(f"  API Error for {filename}: {e}")
    return None

# Well-known Wikimedia Commons files (correct filenames)
WIKIMEDIA_FILES = {
    # ARGENTINA
    ("Argentina", "Adventure"):  "Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG",
    ("Argentina", "Beach"):      "Mar_del_Plata_Strand.jpg",
    ("Argentina", "City"):       "Puerto_Madero,_Buenos_Aires.jpg",
    ("Argentina", "Historical"): "Iguazu_Falls_Argentina.jpg",
    ("Argentina", "Nature"):     "Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG",
    ("Argentina", "Religious"):  "Catedral_de_Córdoba,_Argentina.jpg",

    # AUSTRALIA
    ("Australia", "Adventure"):  "Great_Barrier_Reef_tourist_photo.jpg",
    ("Australia", "Beach"):      "Whitehaven_Beach_Whitsundays.jpg",
    ("Australia", "City"):       "Sydney_Aerial_-_Nov_2008_(3108460498).jpg",
    ("Australia", "Historical"): "Uluru,_Ayers_Rock_2011_02.jpg",
    ("Australia", "Nature"):     "Blue_Mountains_escarpment_from_Govetts_Leap.jpg",
    ("Australia", "Religious"):  "St_Mary's_Cathedral,_Sydney.jpg",

    # BRAZIL
    ("Brazil", "Adventure"):     "Cataratas_do_Iguaçu_2.jpg",
    ("Brazil", "Beach"):         "Plage_d'Ipanema,_Rio_de_Janeiro.jpg",
    ("Brazil", "City"):          "Cristo_Redentor_Rio_de_Janeiro.jpg",
    ("Brazil", "Historical"):    "Pelourinho_panorama.jpg",
    ("Brazil", "Nature"):        "Pantanal_de_mato_grosso.jpg",
    ("Brazil", "Religious"):     "BasilicaNossaSenhoraAparecida.jpg",

    # CANADA
    ("Canada", "Adventure"):     "Moraine_Lake,_Banff_National_Park.jpg",
    ("Canada", "Beach"):         "Cavendish_Beach.jpg",
    ("Canada", "City"):          "Toronto_Skyline_2.jpg",
    ("Canada", "Historical"):    "Vieux-Quebec_panorama.jpg",
    ("Canada", "Nature"):        "Niagara_Falls,_Horseshoe_Falls.jpg",
    ("Canada", "Religious"):     "Notre-Dame_Basilica_Montreal.jpg",

    # CHINA
    ("China", "Adventure"):      "Zhangjiajie_National_Forest_Park.jpg",
    ("China", "Beach"):          "Sanya_Yalong_Bay.jpg",
    ("China", "City"):           "The_Bund,_Shanghai.jpg",
    ("China", "Historical"):     "Great_Wall_of_China_July_2006.jpg",
    ("China", "Nature"):         "Lijiang_River_cruise.jpg",
    ("China", "Religious"):      "Shaolin_Wushu_(martial_arts)_school.jpg",

    # EGYPT
    ("Egypt", "Adventure"):      "Kheops-Pyramid.jpg",
    ("Egypt", "Beach"):          "Hurghada.jpg",
    ("Egypt", "City"):           "Cairo_International_Airport.jpg",
    ("Egypt", "Historical"):     "Kheops-Pyramid.jpg",
    ("Egypt", "Nature"):         "White_Desert_(Sahara)_-_Egypt.jpg",
    ("Egypt", "Religious"):      "Abu_Simbel,_Ramesses_II_(Everhard_Bon).jpg",

    # FRANCE
    ("France", "Adventure"):     "Aiguille_du_Midi_2-edit2.jpg",
    ("France", "Beach"):         "Nice,_France_2.jpg",
    ("France", "City"):          "La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques,_Paris,_août_2014.jpg",
    ("France", "Historical"):    "Palace_of_Versailles,_France,_2015.jpg",
    ("France", "Nature"):        "Le_Mont_Saint-Michel_at_night.jpg",
    ("France", "Religious"):     "Notre-Dame_de_Paris,_4_October_2012.jpg",

    # GERMANY
    ("Germany", "Adventure"):    "Berchtesgadener_Hochthron.jpg",
    ("Germany", "Beach"):        "Kreidefelsen_auf_Rügen.jpg",
    ("Germany", "City"):         "Brandenburger_Tor_abends.jpg",
    ("Germany", "Historical"):   "Schloss_Neuschwanstein_2013.jpg",
    ("Germany", "Nature"):       "Schwarzwälder_Kirschtorte.jpg",
    ("Germany", "Religious"):    "Dom_Koeln_Mar_2010.jpg",

    # GREECE
    ("Greece", "Adventure"):     "Santorini_-_Sunset_at_Oia_02.jpg",
    ("Greece", "Beach"):         "Navagio_Beach_Zakynthos.jpg",
    ("Greece", "City"):          "The_Parthenon_in_Athens.jpg",
    ("Greece", "Historical"):    "Meteora_monasteries_rock_pillars.jpg",
    ("Greece", "Nature"):        "Samaria_Gorge_Trail.jpg",
    ("Greece", "Religious"):     "Meteora_monasteries_rock_pillars.jpg",

    # INDIA
    ("India", "Adventure"):      "Rishikesh_Ganges_-_Dec_2019.jpg",
    ("India", "Beach"):          "Goa_beach_India.jpg",
    ("India", "City"):           "India_Gate_in_New_Delhi.jpg",
    ("India", "Historical"):     "Taj_Mahal,_Agra,_India_edit3.jpg",
    ("India", "Nature"):         "Kerala_backwaters.jpg",
    ("India", "Religious"):      "Golden_Temple,_Amritsar,_India.jpg",

    # ITALY
    ("Italy", "Adventure"):      "Cinque_Terre_-_Vernazza.jpg",
    ("Italy", "Beach"):          "Positano_aerial.jpg",
    ("Italy", "City"):           "Colosseum_in_Rome,_Italy_-_April_2007.jpg",
    ("Italy", "Historical"):     "Basilica_di_San_Marco_(Venice)_2.jpg",
    ("Italy", "Nature"):         "Tuscany_img_4 9040.jpg",
    ("Italy", "Religious"):      "Basilique_Saint-Pierre_de_Rome.jpg",

    # JAPAN
    ("Japan", "Adventure"):      "Mount_Fuji_Japan_2015.jpg",
    ("Japan", "Beach"):          "Okinawa_Sunset_Beach.jpg",
    ("Japan", "City"):           "Shibuya_Night_2019.jpg",
    ("Japan", "Historical"):     "Fushimi_Inari-taisha_shrine,_Kyoto,_Japan.jpg",
    ("Japan", "Nature"):         "Arashiyama_bamboo_grove.jpg",
    ("Japan", "Religious"):      "Kinkaku-ji_Temple_Kyoto_Japan.jpg",

    # KENYA
    ("Kenya", "Adventure"):      "Lion_in_Maasai_Mara.jpg",
    ("Kenya", "Beach"):          "Diani_Beach,_Kenya.jpg",
    ("Kenya", "City"):           "Nairobi_CBD.jpg",
    ("Kenya", "Historical"):     "Lamu_old_town.jpg",
    ("Kenya", "Nature"):         "Wildebeest_in_Maasai_Mara.jpg",
    ("Kenya", "Religious"):      "Lamu_old_town.jpg",

    # MEXICO
    ("Mexico", "Adventure"):     "Barrancas_del_Cobre.jpg",
    ("Mexico", "Beach"):         "Cancun_Mexico_beach.jpg",
    ("Mexico", "City"):          "Catedral_Metropolitana_de_la_Ciudad_de_México.jpg",
    ("Mexico", "Historical"):    "Chichen_Itza_3.jpg",
    ("Mexico", "Nature"):        "Gran_Cenote_Tulum.jpg",
    ("Mexico", "Religious"):     "Basilica_de_Guadalupe.jpg",

    # MOROCCO
    ("Morocco", "Adventure"):    "Erg_Chebbi,_Morocco.jpg",
    ("Morocco", "Beach"):        "Agadir_beach.jpg",
    ("Morocco", "City"):         "Place_Jemaa_el-Fna_Marrakech.jpg",
    ("Morocco", "Historical"):   "Fes_medina_tanneries.jpg",
    ("Morocco", "Nature"):       "Atlas_Mountains_Morocco.jpg",
    ("Morocco", "Religious"):    "Hassan_II_Mosque,_Casablanca.jpg",

    # NEW ZEALAND
    ("New Zealand", "Adventure"):  "Queenstown_New_Zealand.jpg",
    ("New Zealand", "Beach"):      "Cathedral_Cove,_Hahei,_New_Zealand.jpg",
    ("New Zealand", "City"):       "Auckland,_from_One_Tree_Hill.jpg",
    ("New Zealand", "Historical"): "Hobbiton_Shire,_New_Zealand.jpg",
    ("New Zealand", "Nature"):     "Milford_Sound,_New_Zealand.jpg",
    ("New Zealand", "Religious"):  "ChristChurch_Cathedral_front.jpg",

    # PERU
    ("Peru", "Adventure"):       "Machu_Picchu,_Peru.jpg",
    ("Peru", "Beach"):           "Mancora_beach.jpg",
    ("Peru", "City"):            "Lima_Peru_Miraflores.jpg",
    ("Peru", "Historical"):      "Machu_Picchu,_Peru.jpg",
    ("Peru", "Nature"):          "Amazon_River_Brazil_2016.jpg",
    ("Peru", "Religious"):       "Cusco_Cathedral_(Cathedral_Basílica_de_la_Virgen_de_la_Asunción).jpg",

    # SOUTH AFRICA
    ("South Africa", "Adventure"):  "Kruger_lion.jpg",
    ("South Africa", "Beach"):      "Clifton_Beach_Cape_Town.jpg",
    ("South Africa", "City"):       "Cape_Town_City_Bowl_aerial.jpg",
    ("South Africa", "Historical"): "Robben_Island_prison.jpg",
    ("South Africa", "Nature"):     "Table_Mountain_DanieVDM.jpg",
    ("South Africa", "Religious"):  "Table_Mountain_DanieVDM.jpg",

    # SPAIN
    ("Spain", "Adventure"):      "Pyrenees_mountains_Spain.jpg",
    ("Spain", "Beach"):          "Formentera_beach_spain.jpg",
    ("Spain", "City"):           "Sagrada_Familia_01.jpg",
    ("Spain", "Historical"):     "Palace_of_the_Alhambra,_Granada,_Spain.jpg",
    ("Spain", "Nature"):         "Teide_pano.jpg",
    ("Spain", "Religious"):      "Catedral_de_Santiago_de_Compostela.jpg",

    # THAILAND
    ("Thailand", "Adventure"):   "Khao_Sok_National_Park_Thailand.jpg",
    ("Thailand", "Beach"):       "Phi_Phi_Don_view_point.jpg",
    ("Thailand", "City"):        "BTS_Skytrain_Bangkok.jpg",
    ("Thailand", "Historical"):  "Ayutthaya_Wat_Mahathat_Buddha_head_in_tree.jpg",
    ("Thailand", "Nature"):      "Doi_Inthanon_Chiang_Mai.jpg",
    ("Thailand", "Religious"):   "Wat_Phra_Kaeo_2_amk.jpg",

    # USA
    ("USA", "Adventure"):        "Grand_Canyon_National_Park_USA.jpg",
    ("USA", "Beach"):            "South_Beach_from_above.jpg",
    ("USA", "City"):             "NYC_wideangle_south_from_Top_of_the_Rock.jpg",
    ("USA", "Historical"):       "Statue_of_Liberty,_NY.jpg",
    ("USA", "Nature"):           "Grand_Prismatic_Spring,_Yellowstone_National_Park.jpg",
    ("USA", "Religious"):        "Washington_National_Cathedral_aerial.jpg",

    # VIETNAM
    ("Vietnam", "Adventure"):    "Sapa_Vietnam_rice_terraces.jpg",
    ("Vietnam", "Beach"):        "Ha_Long_Bay,_Vietnam.jpg",
    ("Vietnam", "City"):         "Ho_Chi_Minh_City_Skyline.jpg",
    ("Vietnam", "Historical"):   "Hoi_An_at_night.jpg",
    ("Vietnam", "Nature"):       "Phong_Nha-Ke_Bang_cave.jpg",
    ("Vietnam", "Religious"):    "One_Pillar_Pagoda.jpg",
}

def get_wikimedia_image_url(filename):
    """Get Wikimedia Commons image URL using API."""
    api_url = "https://commons.wikimedia.org/w/api.php"
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": f"File:{filename}",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "1280",
        "format": "json"
    })
    url = f"{api_url}?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TravelApp/1.0'})
        r = urllib.request.urlopen(req, timeout=10)
        data = json.loads(r.read().decode('utf-8'))
        pages = data.get('query', {}).get('pages', {})
        for page in pages.values():
            info = page.get('imageinfo', [])
            if info:
                thumb = info[0].get('thumburl', '')
                direct = info[0].get('url', '')
                return thumb or direct
    except Exception as e:
        print(f"  Error: {e}")
    return None

def main():
    print("=" * 60)
    print("FETCHING VERIFIED IMAGE URLS FROM WIKIMEDIA API")
    print("=" * 60)

    image_map = {}
    total = len(WIKIMEDIA_FILES)

    for idx, ((country, dest_type), filename) in enumerate(WIKIMEDIA_FILES.items(), 1):
        print(f"[{idx}/{total}] {country} | {dest_type}")
        url = get_wikimedia_image_url(filename)
        if url:
            image_map[(country, dest_type)] = url
            print(f"  OK: {url[:80]}")
        else:
            print(f"  FAIL: {filename}")
        time.sleep(0.3)  # Be polite to Wikimedia API

    print(f"\nGot {len(image_map)}/{total} image URLs")

    # Save to JSON
    json_data = {f"{k[0]}|{k[1]}": v for k, v in image_map.items()}
    with open('verified_image_map.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print("Saved to verified_image_map.json")

    # Update MongoDB
    print("\nUpdating MongoDB...")
    destinations = list(db.destinations.find({}))
    updated = 0

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

    print(f"Updated {updated}/{len(destinations)} destinations")
    print("Done!")

if __name__ == '__main__':
    main()
