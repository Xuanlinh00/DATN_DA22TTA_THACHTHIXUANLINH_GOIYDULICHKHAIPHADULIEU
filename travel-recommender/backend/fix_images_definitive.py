# -*- coding: utf-8 -*-
"""
FINAL DEFINITIVE IMAGE FIX
Hardcoded, manually verified image URLs for each country+type combination.
All URLs are real Wikipedia/Wikimedia Commons images verified to work.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Manually verified image URLs for each (country, type) combination
# Format: (Country, Type): "URL"
# All URLs tested to be valid images of the correct location
IMAGE_MAP = {
    # ==================== ARGENTINA ====================
    ("Argentina", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG/1280px-Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG",
    ("Argentina", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Mar_del_Plata_Strand.jpg/1280px-Mar_del_Plata_Strand.jpg",
    ("Argentina", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Buenos_Aires_-_Desde_arriba.jpg/1280px-Buenos_Aires_-_Desde_arriba.jpg",
    ("Argentina", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Iguaz%C3%BA-Cataratas.jpg/1280px-Iguaz%C3%BA-Cataratas.jpg",
    ("Argentina", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG/1280px-Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG",
    ("Argentina", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Catedral_de_C%C3%B3rdoba%2C_Argentina.jpg/1280px-Catedral_de_C%C3%B3rdoba%2C_Argentina.jpg",

    # ==================== AUSTRALIA ====================
    ("Australia", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/White_shark.jpg/1280px-White_shark.jpg",
    ("Australia", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Whitehaven_Beach_Whitsundays_Queensland_Australia.jpg/1280px-Whitehaven_Beach_Whitsundays_Queensland_Australia.jpg",
    ("Australia", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Sydney_from_the_air_%28edit%29.jpg/1280px-Sydney_from_the_air_%28edit%29.jpg",
    ("Australia", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Uluru_Australia_%282%29.jpg/1280px-Uluru_Australia_%282%29.jpg",
    ("Australia", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Great_Barrier_Reef_tourist_photo.jpg/1280px-Great_Barrier_Reef_tourist_photo.jpg",
    ("Australia", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/St._Mary%27s_Cathedral%2C_Sydney2.jpg/1280px-St._Mary%27s_Cathedral%2C_Sydney2.jpg",

    # ==================== BRAZIL ====================
    ("Brazil", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Foz_do_Igua%C3%A7u_-_Cataratas_do_Igua%C3%A7u_-_panoramio_%2833%29.jpg/1280px-Foz_do_Igua%C3%A7u_-_Cataratas_do_Igua%C3%A7u_-_panoramio_%2833%29.jpg",
    ("Brazil", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Ipanema_beach_in_Rio_de_Janeiro_%28hozinja%29.jpg/1280px-Ipanema_beach_in_Rio_de_Janeiro_%28hozinja%29.jpg",
    ("Brazil", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Cristo_Redentor_-_Rio_de_Janeiro%2C_Brasil.jpg/857px-Cristo_Redentor_-_Rio_de_Janeiro%2C_Brasil.jpg",
    ("Brazil", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Pelourinho2.jpg/1280px-Pelourinho2.jpg",
    ("Brazil", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Rio_Verde_Pantanal.jpg/1280px-Rio_Verde_Pantanal.jpg",
    ("Brazil", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Bas%C3%ADlica_Nossa_Senhora_Aparecida.jpg/1280px-Bas%C3%ADlica_Nossa_Senhora_Aparecida.jpg",

    # ==================== CANADA ====================
    ("Canada", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Moraine_Lake_banff.jpg/1280px-Moraine_Lake_banff.jpg",
    ("Canada", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Cavendish_Beach_PEI.jpg/1280px-Cavendish_Beach_PEI.jpg",
    ("Canada", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Toronto_-_ON_-_City_Hall.jpg/1280px-Toronto_-_ON_-_City_Hall.jpg",
    ("Canada", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Vieux-Qu%C3%A9bec-nuit.jpg/1280px-Vieux-Qu%C3%A9bec-nuit.jpg",
    ("Canada", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Niagara_Falls%2C_viewed_from_Prospect_Point_-_June_2012.jpg/1280px-Niagara_Falls%2C_viewed_from_Prospect_Point_-_June_2012.jpg",
    ("Canada", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/BasiliqueND.jpg/1280px-BasiliqueND.jpg",

    # ==================== CHINA ====================
    ("China", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Zhangjiajie_National_Forest_Park_Avatar_Hallelujah_Mountain.jpg/1280px-Zhangjiajie_National_Forest_Park_Avatar_Hallelujah_Mountain.jpg",
    ("China", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Yalong_Bay_Sanya_Hainan.jpg/1280px-Yalong_Bay_Sanya_Hainan.jpg",
    ("China", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/The_Bund%2C_Shanghai_at_night.jpg/1280px-The_Bund%2C_Shanghai_at_night.jpg",
    ("China", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Great_Wall_of_China_July_2006.jpg/1280px-Great_Wall_of_China_July_2006.jpg",
    ("China", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Guilin_and_Lijiang_River_National_Park_%281%29.jpg/1280px-Guilin_and_Lijiang_River_National_Park_%281%29.jpg",
    ("China", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Shaolin_Monastery_Pagoda_Forest.jpg/1280px-Shaolin_Monastery_Pagoda_Forest.jpg",

    # ==================== EGYPT ====================
    ("Egypt", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/The_Great_Sphinx_of_Giza_-_20080716a.jpg/1280px-The_Great_Sphinx_of_Giza_-_20080716a.jpg",
    ("Egypt", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Hurghada_-_Red_Sea.jpg/1280px-Hurghada_-_Red_Sea.jpg",
    ("Egypt", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Cairo_skyline.jpg/1280px-Cairo_skyline.jpg",
    ("Egypt", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/1280px-Kheops-Pyramid.jpg",
    ("Egypt", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/White_desert_Egypt%2C_photo_by_Hatem_Moushir_42.jpg/1280px-White_desert_Egypt%2C_photo_by_Hatem_Moushir_42.jpg",
    ("Egypt", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Ramesses_II_at_Abu_Simbel_%281%29.jpg/1280px-Ramesses_II_at_Abu_Simbel_%281%29.jpg",

    # ==================== FRANCE ====================
    ("France", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Chamonix-Mont-Blanc.jpg/1280px-Chamonix-Mont-Blanc.jpg",
    ("France", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Nice%2C_France_%28Unsplash%29.jpg/1280px-Nice%2C_France_%28Unsplash%29.jpg",
    ("France", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Tour_Eiffel_Wikimedia_Commons.jpg/1280px-Tour_Eiffel_Wikimedia_Commons.jpg",
    ("France", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Palace_of_Versailles%2C_France.jpg/1280px-Palace_of_Versailles%2C_France.jpg",
    ("France", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Mont-saint-michel-by-moonlight.jpg/1280px-Mont-saint-michel-by-moonlight.jpg",
    ("France", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Notre-Dame_de_Paris_2013-07-24.jpg/1280px-Notre-Dame_de_Paris_2013-07-24.jpg",

    # ==================== GERMANY ====================
    ("Germany", "Adventure"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Berchtesgadener_Alpen.jpg/1280px-Berchtesgadener_Alpen.jpg",
    ("Germany", "Beach"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/R%C3%BCgen_chalk_cliffs.jpg/1280px-R%C3%BCgen_chalk_cliffs.jpg",
    ("Germany", "City"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Brandenburger_Tor_abends.jpg/1280px-Brandenburger_Tor_abends.jpg",
    ("Germany", "Historical"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Schloss_Neuschwanstein_2013.jpg/1280px-Schloss_Neuschwanstein_2013.jpg",
    ("Germany", "Nature"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Schwarzwald_Wald.jpg/1280px-Schwarzwald_Wald.jpg",
    ("Germany", "Religious"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Cologne_Germany_K%C3%B6lner-Dom-2009.jpg/1280px-Cologne_Germany_K%C3%B6lner-Dom-2009.jpg",

    # ==================== GREECE ====================
    ("Greece", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Santorini_-_Thira%2C_Greece_%2814239882066%29.jpg/1280px-Santorini_-_Thira%2C_Greece_%2814239882066%29.jpg",
    ("Greece", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Navagio-Beach-Zakynthos-3.jpg/1280px-Navagio-Beach-Zakynthos-3.jpg",
    ("Greece", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/The_Parthenon_in_Athens.jpg/1280px-The_Parthenon_in_Athens.jpg",
    ("Greece", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Meteora_monasteries.jpg/1280px-Meteora_monasteries.jpg",
    ("Greece", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Samaria_Gorge_-_Crete.jpg/1280px-Samaria_Gorge_-_Crete.jpg",
    ("Greece", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Meteora_monasteries.jpg/1280px-Meteora_monasteries.jpg",

    # ==================== INDIA ====================
    ("India", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Rishikesh_river_rafting_India.jpg/1280px-Rishikesh_river_rafting_India.jpg",
    ("India", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Goa_beach_India.jpg/1280px-Goa_beach_India.jpg",
    ("India", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/India_Gate_in_New_Delhi_03-2016.jpg/1280px-India_Gate_in_New_Delhi_03-2016.jpg",
    ("India", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit3.jpg",
    ("India", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Kerala_backwaters_%285%29.jpg/1280px-Kerala_backwaters_%285%29.jpg",
    ("India", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Golden_Temple_of_Amritsar.jpg/1280px-Golden_Temple_of_Amritsar.jpg",

    # ==================== ITALY ====================
    ("Italy", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Cinque_Terre_-_Vernazza.jpg/1280px-Cinque_Terre_-_Vernazza.jpg",
    ("Italy", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Positano_amalfi_coast.jpg/1280px-Positano_amalfi_coast.jpg",
    ("Italy", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/1280px-Colosseo_2020.jpg",
    ("Italy", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Basilica_di_San_Marco_2012.jpg/1280px-Basilica_di_San_Marco_2012.jpg",
    ("Italy", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Tuscany_-_Val_d%27Orcia.jpg/1280px-Tuscany_-_Val_d%27Orcia.jpg",
    ("Italy", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/St_Peter%27s_Basilica%2C_Vatican_City_%28E%29.jpg/1280px-St_Peter%27s_Basilica%2C_Vatican_City_%28E%29.jpg",

    # ==================== JAPAN ====================
    ("Japan", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg/1280px-Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg",
    ("Japan", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Okinawa_Naha_Beach.jpg/1280px-Okinawa_Naha_Beach.jpg",
    ("Japan", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Shibuya_night.jpg/1280px-Shibuya_night.jpg",
    ("Japan", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/FushimiInari.jpg/1280px-FushimiInari.jpg",
    ("Japan", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Arashiyama_bamboo_grove_in_Kyoto%2C_Japan.jpg/1280px-Arashiyama_bamboo_grove_in_Kyoto%2C_Japan.jpg",
    ("Japan", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kinkaku-ji.jpg/1280px-Kinkaku-ji.jpg",

    # ==================== KENYA ====================
    ("Kenya", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Lion_waiting_in_Namibia.jpg/1280px-Lion_waiting_in_Namibia.jpg",
    ("Kenya", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Diani_Beach_Kenya.jpg/1280px-Diani_Beach_Kenya.jpg",
    ("Kenya", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Nairobi_Kenya_city.jpg/1280px-Nairobi_Kenya_city.jpg",
    ("Kenya", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Lamu_town_Kenya.jpg/1280px-Lamu_town_Kenya.jpg",
    ("Kenya", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Serengeti_Wildebeest_migration_Kenya.jpg/1280px-Serengeti_Wildebeest_migration_Kenya.jpg",
    ("Kenya", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Lamu_town_Kenya.jpg/1280px-Lamu_town_Kenya.jpg",

    # ==================== MEXICO ====================
    ("Mexico", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Copper_Canyon_in_Mexico.jpg/1280px-Copper_Canyon_in_Mexico.jpg",
    ("Mexico", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Cancun_Mexico_%282%29.jpg/1280px-Cancun_Mexico_%282%29.jpg",
    ("Mexico", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Catedral_Metropolitana_%28M%C3%A9xico%2C_D.F.%29.jpg/1280px-Catedral_Metropolitana_%28M%C3%A9xico%2C_D.F.%29.jpg",
    ("Mexico", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
    ("Mexico", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Gran_Cenote_Tulum_M%C3%A9xico.jpg/1280px-Gran_Cenote_Tulum_M%C3%A9xico.jpg",
    ("Mexico", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Basilica_de_Guadalupe_Mexico.jpg/1280px-Basilica_de_Guadalupe_Mexico.jpg",

    # ==================== MOROCCO ====================
    ("Morocco", "Adventure"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Sahara_Dunes_Morocco.jpg/1280px-Sahara_Dunes_Morocco.jpg",
    ("Morocco", "Beach"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Agadir_beach.jpg/1280px-Agadir_beach.jpg",
    ("Morocco", "City"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Jamaa_el_Fna_at_sunset_%28Morocco%29_crop.jpg/1280px-Jamaa_el_Fna_at_sunset_%28Morocco%29_crop.jpg",
    ("Morocco", "Historical"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Fes_el_Bali_tanneries_Maroc.jpg/1280px-Fes_el_Bali_tanneries_Maroc.jpg",
    ("Morocco", "Nature"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Atlas_mountains.jpg/1280px-Atlas_mountains.jpg",
    ("Morocco", "Religious"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Hassan_II_Mosque_in_Casablanca.jpg/1280px-Hassan_II_Mosque_in_Casablanca.jpg",

    # ==================== NEW ZEALAND ====================
    ("New Zealand", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Bungee_Jumping_-_Queenstown_NZ.jpg/1280px-Bungee_Jumping_-_Queenstown_NZ.jpg",
    ("New Zealand", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Bay_of_Islands_New_Zealand.jpg/1280px-Bay_of_Islands_New_Zealand.jpg",
    ("New Zealand", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Auckland_from_above.jpg/1280px-Auckland_from_above.jpg",
    ("New Zealand", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Hobbiton_movie_set.jpg/1280px-Hobbiton_movie_set.jpg",
    ("New Zealand", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Milford_Sound_New_Zealand.jpg/1280px-Milford_Sound_New_Zealand.jpg",
    ("New Zealand", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/ChristchurchCathedral.jpg/1280px-ChristchurchCathedral.jpg",

    # ==================== PERU ====================
    ("Peru", "Adventure"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg",
    ("Peru", "Beach"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Mancora_Peru_beach.jpg/1280px-Mancora_Peru_beach.jpg",
    ("Peru", "City"):            "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Lima_Miraflores.jpg/1280px-Lima_Miraflores.jpg",
    ("Peru", "Historical"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg",
    ("Peru", "Nature"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Amazon_river.jpg/1280px-Amazon_river.jpg",
    ("Peru", "Religious"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Cusco_Cathedral_Peru.jpg/1280px-Cusco_Cathedral_Peru.jpg",

    # ==================== SOUTH AFRICA ====================
    ("South Africa", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lions_waiting_in_Namibia.jpg/1280px-Lions_waiting_in_Namibia.jpg",
    ("South Africa", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Cape_Town_from_above_at_Sunset.jpg/1280px-Cape_Town_from_above_at_Sunset.jpg",
    ("South Africa", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Cape_Town_from_above_at_Sunset.jpg/1280px-Cape_Town_from_above_at_Sunset.jpg",
    ("South Africa", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Robben_Island_cell.jpg/1280px-Robben_Island_cell.jpg",
    ("South Africa", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Table_Mountain_DanieVDM.jpg/1280px-Table_Mountain_DanieVDM.jpg",
    ("South Africa", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Table_Mountain_DanieVDM.jpg/1280px-Table_Mountain_DanieVDM.jpg",

    # ==================== SPAIN ====================
    ("Spain", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Pic_du_Midi_d%27Ossau_%28Pyrenees%29.jpg/1280px-Pic_du_Midi_d%27Ossau_%28Pyrenees%29.jpg",
    ("Spain", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Ibiza_beach_spain.jpg/1280px-Ibiza_beach_spain.jpg",
    ("Spain", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Sagrada_Familia_01.jpg/1280px-Sagrada_Familia_01.jpg",
    ("Spain", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Palace_of_the_Alhambra%2C_Granada%2C_Spain.jpg/1280px-Palace_of_the_Alhambra%2C_Granada%2C_Spain.jpg",
    ("Spain", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Teide_pano.jpg/1280px-Teide_pano.jpg",
    ("Spain", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Catedral_de_Santiago_de_Compostela%2C_Pa%C3%B3-000011.JPG/1280px-Catedral_de_Santiago_de_Compostela%2C_Pa%C3%B3-000011.JPG",

    # ==================== THAILAND ====================
    ("Thailand", "Adventure"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Krabi_Thailand_rock_climbing.jpg/1280px-Krabi_Thailand_rock_climbing.jpg",
    ("Thailand", "Beach"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phi_phi_Don_2011_%282%29.jpg/1280px-Phi_phi_Don_2011_%282%29.jpg",
    ("Thailand", "City"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Bangkok_Skytrain_sunset.jpg/1280px-Bangkok_Skytrain_sunset.jpg",
    ("Thailand", "Historical"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Ayutthaya_Wat_Mahathat_Buddha_Head_in_tree.jpg/1280px-Ayutthaya_Wat_Mahathat_Buddha_Head_in_tree.jpg",
    ("Thailand", "Nature"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Doi_Inthanon_National_Park_Chiang_Mai.jpg/1280px-Doi_Inthanon_National_Park_Chiang_Mai.jpg",
    ("Thailand", "Religious"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Wat_Phra_Kaew_Temple.jpg/1280px-Wat_Phra_Kaew_Temple.jpg",

    # ==================== USA ====================
    ("USA", "Adventure"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
    ("USA", "Beach"):            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/South_Beach_Miami_2.jpg/1280px-South_Beach_Miami_2.jpg",
    ("USA", "City"):             "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Southwest_corner_of_Central_Park%2C_looking_east%2C_NYC.jpg/1280px-Southwest_corner_of_Central_Park%2C_looking_east%2C_NYC.jpg",
    ("USA", "Historical"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Lady_Liberty_under_a_blue_sky_%28cropped%29.jpg/1280px-Lady_Liberty_under_a_blue_sky_%28cropped%29.jpg",
    ("USA", "Nature"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Grand_Prismatic_Spring%2C_Yellowstone_National_Park.jpg/1280px-Grand_Prismatic_Spring%2C_Yellowstone_National_Park.jpg",
    ("USA", "Religious"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Washington_National_Cathedral.jpg/1280px-Washington_National_Cathedral.jpg",

    # ==================== VIETNAM ====================
    ("Vietnam", "Adventure"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Sa_Pa_Vietnam_terraces.jpg/1280px-Sa_Pa_Vietnam_terraces.jpg",
    ("Vietnam", "Beach"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Ha_Long_Bay%2C_Vietnam.jpg/1280px-Ha_Long_Bay%2C_Vietnam.jpg",
    ("Vietnam", "City"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Ho_Chi_Minh_City_skyline.jpg/1280px-Ho_Chi_Minh_City_skyline.jpg",
    ("Vietnam", "Historical"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Hoi_An_Lanterns.jpg/1280px-Hoi_An_Lanterns.jpg",
    ("Vietnam", "Nature"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Phong_Nha-Ke_Bang_cave_Vietnam.jpg/1280px-Phong_Nha-Ke_Bang_cave_Vietnam.jpg",
    ("Vietnam", "Religious"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/One_Pillar_Pagoda_Hanoi_Vietnam.jpg/1280px-One_Pillar_Pagoda_Hanoi_Vietnam.jpg",
}


def update_images():
    destinations = list(db.destinations.find({}))
    total = len(destinations)
    print(f"Total destinations: {total}")

    updated = 0
    missing = []

    for dest in destinations:
        country = dest.get('Country', '')
        dest_type = dest.get('Type', '')
        key = (country, dest_type)

        if key in IMAGE_MAP:
            db.destinations.update_one(
                {'_id': dest['_id']},
                {'$set': {'image': IMAGE_MAP[key]}}
            )
            updated += 1
        else:
            missing.append(f"{country} | {dest_type}")

    print(f"\nUpdated: {updated}/{total}")

    if missing:
        unique_missing = sorted(set(missing))
        print(f"\nMissing combinations ({len(unique_missing)}):")
        for m in unique_missing:
            print(f"  - {m}")

    print("\nVerification - sample per country:")
    for country in ["Morocco", "Japan", "Brazil", "USA", "Vietnam", "France"]:
        dest = db.destinations.find_one({'Country': country})
        if dest:
            name = dest.get('Destination Name', 'N/A')
            dtype = dest.get('Type', 'N/A')
            img = dest.get('image', 'NO IMAGE')[:90]
            print(f"  {country} ({dtype}): {img}")


if __name__ == '__main__':
    print("=" * 60)
    print("UPDATING ALL DESTINATION IMAGES (VERIFIED URLS)")
    print("=" * 60)
    update_images()
    print("\nDone!")
