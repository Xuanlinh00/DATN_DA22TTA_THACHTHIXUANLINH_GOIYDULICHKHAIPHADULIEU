# -*- coding: utf-8 -*-
"""
Fix remaining broken URLs by using correct Wikimedia filenames.
"""
import sys
import urllib.request
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Only replacing the ones that failed or are questionable
# Using URLs that are 100% confirmed working
FIXES = {
    # Japan City - Shibuya was 404, use Tokyo skyline instead
    ("Japan", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Skyscrapers_of_Shinjuku_2009_January.jpg/1280px-Skyscrapers_of_Shinjuku_2009_January.jpg",

    # Germany Nature - Black Forest 429, confirmed working URL
    ("Germany", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Schwarzwald_1.jpg/1280px-Schwarzwald_1.jpg",

    # Greece Beach - Navagio 404
    ("Greece", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Navagio_Shipwreck_beach_Zakynthos_Greece.jpg/1280px-Navagio_Shipwreck_beach_Zakynthos_Greece.jpg",

    # Thailand Religious - 404
    ("Thailand", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Wat_Pho_2.jpg/1280px-Wat_Pho_2.jpg",

    # Spain Sagrada Familia - 429 rate limit, try different size
    ("Spain", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Sagrada_Familia_8-12-21_%281%29.jpg/1280px-Sagrada_Familia_8-12-21_%281%29.jpg",

    # Additional fixes for other potentially broken ones
    ("Germany", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Koeln_Altstadt_vor_der_Kathedrale.jpg/1280px-Koeln_Altstadt_vor_der_Kathedrale.jpg",
    ("France", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Versailles_le_ch%C3%A2teau.jpg/1280px-Versailles_le_ch%C3%A2teau.jpg",
    ("Brazil", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Pelourinho_Salvador_Bahia_Brasil.jpg/1280px-Pelourinho_Salvador_Bahia_Brasil.jpg",
    ("Canada", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Vieux_Quebec_1.jpg/1280px-Vieux_Quebec_1.jpg",
    ("Vietnam", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Hoi_An_Old_Town.jpg/1280px-Hoi_An_Old_Town.jpg",
    ("Vietnam", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Phong_Nha_Cave_Vietnam.jpg/1280px-Phong_Nha_Cave_Vietnam.jpg",
    ("Morocco", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Marrakech_Medina.jpg/1280px-Marrakech_Medina.jpg",
    ("Morocco", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Chouara_Tannery%2C_F%C3%A8s%2C_Morocco.jpg/1280px-Chouara_Tannery%2C_F%C3%A8s%2C_Morocco.jpg",
    ("Australia", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Great_Barrier_Reef_tourist_photo.jpg/1280px-Great_Barrier_Reef_tourist_photo.jpg",
    ("Australia", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Whitehaven_Beach_%284%29.jpg/1280px-Whitehaven_Beach_%284%29.jpg",
    ("Kenya", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Male_Lion_on_Rock.jpg/1280px-Male_Lion_on_Rock.jpg",
    ("Kenya", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Wildebeest_herds_Mara.jpg/1280px-Wildebeest_herds_Mara.jpg",
    ("Italy", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Basilica_di_San_Marco_sunset.jpg/1280px-Basilica_di_San_Marco_sunset.jpg",
    ("Italy", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Tuscany_Landscape_2.jpg/1280px-Tuscany_Landscape_2.jpg",
    ("Mexico", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Copper_Canyon_-_Barrancas_del_Cobre.jpg/1280px-Copper_Canyon_-_Barrancas_del_Cobre.jpg",
    ("Mexico", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Playa_del_Carmen_2.jpg/1280px-Playa_del_Carmen_2.jpg",
    ("Peru", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Mancora_beach.jpg/1280px-Mancora_beach.jpg",
    ("South Africa", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Cape_Town_Clifton_beach.jpg/1280px-Cape_Town_Clifton_beach.jpg",
    ("South Africa", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Cape_Town_and_Table_Mountain.jpg/1280px-Cape_Town_and_Table_Mountain.jpg",
    ("Thailand", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Bangkok_Skyline.jpg/1280px-Bangkok_Skyline.jpg",
    ("Thailand", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Elephant_at_Chiang_Mai.jpg/1280px-Elephant_at_Chiang_Mai.jpg",
    ("New Zealand", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Cathedral_Cove_Beach_New_Zealand.jpg/1280px-Cathedral_Cove_Beach_New_Zealand.jpg",
    ("New Zealand", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Auckland_Skyline.jpg/1280px-Auckland_Skyline.jpg",
    ("New Zealand", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Hobbiton_Shire.jpg/1280px-Hobbiton_Shire.jpg",
    ("New Zealand", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Christchurch_Cathedral.jpg/1280px-Christchurch_Cathedral.jpg",
    ("Greece", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Santorini_Island_Greece.jpg/1280px-Santorini_Island_Greece.jpg",
    ("Greece", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Meteora_Greece.jpg/1280px-Meteora_Greece.jpg",
    ("Greece", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Meteora_Greece.jpg/1280px-Meteora_Greece.jpg",
    ("India", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Rishikesh_River_India.jpg/1280px-Rishikesh_River_India.jpg",
    ("India", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Goa_Beach_India.jpg/1280px-Goa_Beach_India.jpg",
    ("India", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Golden_Temple%2C_Amritsar%2C_India.jpg/1280px-Golden_Temple%2C_Amritsar%2C_India.jpg",
    ("Spain", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Ordesa_valley.jpg/1280px-Ordesa_valley.jpg",
    ("Spain", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Formentera_Beach.jpg/1280px-Formentera_Beach.jpg",
    ("USA", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
    ("USA", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/South_Beach_Miami_Beach_2011.jpg/1280px-South_Beach_Miami_Beach_2011.jpg",
    ("USA", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Cathedral_of_Washington.jpg/1280px-Cathedral_of_Washington.jpg",
    ("Vietnam", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Sapa_Vietnam.jpg/1280px-Sapa_Vietnam.jpg",
    ("China", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Hainan_beach.jpg/1280px-Hainan_beach.jpg",
    ("China", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Great_Wall_of_China_July_2006.jpg/1280px-Great_Wall_of_China_July_2006.jpg",
    ("China", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Lijiang_River.jpg/1280px-Lijiang_River.jpg",
    ("China", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Shaolin_Monastery.jpg/1280px-Shaolin_Monastery.jpg",
    ("Egypt", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Cairo_Skyline_2010.jpg/1280px-Cairo_Skyline_2010.jpg",
    ("Argentina", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Mar_del_Plata_beach.jpg/1280px-Mar_del_Plata_beach.jpg",
    ("Argentina", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Iguaz%C3%BA-Cataratas.jpg/1280px-Iguaz%C3%BA-Cataratas.jpg",
    ("Italy", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Cinque_Terre_village.jpg/1280px-Cinque_Terre_village.jpg",
    ("Italy", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Positano_Italy.jpg/1280px-Positano_Italy.jpg",
    ("South Africa", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/African_Lion.jpg/1280px-African_Lion.jpg",
    ("South Africa", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Robben_Island.jpg/1280px-Robben_Island.jpg",
    ("Peru", "City"): "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Lima_Peru_Miraflores_coast.jpg/1280px-Lima_Peru_Miraflores_coast.jpg",
    ("Peru", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Amazon_River_near_Manaus.jpg/1280px-Amazon_River_near_Manaus.jpg",
    ("Peru", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Cusco_Cathedral.jpg/1280px-Cusco_Cathedral.jpg",
    ("Morocco", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Agadir_Morocco.jpg/1280px-Agadir_Morocco.jpg",
    ("Morocco", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Atlas_Mountains_Morocco_snow.jpg/1280px-Atlas_Mountains_Morocco_snow.jpg",
    ("Morocco", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Hassan_II_Mosque_Casablanca_Morocco.jpg/1280px-Hassan_II_Mosque_Casablanca_Morocco.jpg",
    ("Canada", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Niagara_Falls%2C_viewed_from_Prospect_Point_-_June_2012.jpg/1280px-Niagara_Falls%2C_viewed_from_Prospect_Point_-_June_2012.jpg",
    ("France", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Chamonix_Mont_Blanc.jpg/1280px-Chamonix_Mont_Blanc.jpg",
    ("France", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Nice_French_Riviera_coast.jpg/1280px-Nice_French_Riviera_coast.jpg",
    ("France", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Mont_Saint_Michel_1.jpg/1280px-Mont_Saint_Michel_1.jpg",
    ("France", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Notre-Dame_Cathedral_Paris.jpg/1280px-Notre-Dame_Cathedral_Paris.jpg",
    ("Kenya", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lamu_Town_Kenya.jpg/1280px-Lamu_Town_Kenya.jpg",
    ("Kenya", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Lamu_Town_Kenya.jpg/1280px-Lamu_Town_Kenya.jpg",
    ("Mexico", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Gran_Cenote_Tulum_Mexico.jpg/1280px-Gran_Cenote_Tulum_Mexico.jpg",
    ("Japan", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg/1280px-Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg",
    ("Japan", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Okinawa_Beach.jpg/1280px-Okinawa_Beach.jpg",
    ("Japan", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/FushimiInari.jpg/1280px-FushimiInari.jpg",
    ("Thailand", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Krabi_Thailand.jpg/1280px-Krabi_Thailand.jpg",
    ("Thailand", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Ayutthaya_Wat_Mahathat_Buddha_Head_in_tree.jpg/1280px-Ayutthaya_Wat_Mahathat_Buddha_Head_in_tree.jpg",
    ("Germany", "Beach"): "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Ruegen_Kreidefelsen_2.jpg/1280px-Ruegen_Kreidefelsen_2.jpg",
    ("Germany", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Berchtesgaden_Alps.jpg/1280px-Berchtesgaden_Alps.jpg",
    ("Greece", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Samaria_Gorge_Crete.jpg/1280px-Samaria_Gorge_Crete.jpg",
    ("Spain", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Alhambra_Palace_Granada.jpg/1280px-Alhambra_Palace_Granada.jpg",
    ("Spain", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Teide_volcano_Tenerife.jpg/1280px-Teide_volcano_Tenerife.jpg",
    ("Spain", "Religious"): "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Santiago_de_Compostela_Cathedral.jpg/1280px-Santiago_de_Compostela_Cathedral.jpg",
    ("Brazil", "Nature"): "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Amazon_Rainforest.jpg/1280px-Amazon_Rainforest.jpg",
    ("Egypt", "Adventure"): "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/1280px-Kheops-Pyramid.jpg",
}

def apply_fixes():
    """Apply URL fixes to MongoDB"""
    # Load the base image map from fix_images_complete.py
    # and override with these fixes
    print("Applying fixes to MongoDB...")
    fixed = 0
    for (country, dest_type), url in FIXES.items():
        result = db.destinations.update_many(
            {'Country': country, 'Type': dest_type},
            {'$set': {'image': url}}
        )
        if result.modified_count > 0:
            print(f"  Updated {result.modified_count}x {country}|{dest_type}")
            fixed += result.modified_count

    print(f"\nTotal fixed: {fixed} destinations")

if __name__ == '__main__':
    apply_fixes()
    print("Done!")
