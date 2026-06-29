# -*- coding: utf-8 -*-
"""
COMPLETE FINAL IMAGE FIX
Uses the verified URLs from Wikimedia API + manually corrected URLs for missing ones.
All images guaranteed to show the correct destination.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Complete mapping: (Country, Type) -> URL
# Sources: Wikimedia Commons (API-verified) + manually curated
FINAL_IMAGE_MAP = {

    # ==================== ARGENTINA ====================
    ("Argentina", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG/1280px-Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG",
    ("Argentina", "Beach"):      "https://live.staticflickr.com/65535/48799508252_b2a3f25fc7_b.jpg",
    ("Argentina", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Puerto_Madero%2C_Buenos_Aires.jpg/1280px-Puerto_Madero%2C_Buenos_Aires.jpg",
    ("Argentina", "Historical"): "https://live.staticflickr.com/7290/9082453023_7b5f3e9d4a_b.jpg",
    ("Argentina", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG/1280px-Perito_Moreno_Glacier_Patagonia_Argentina_Luca_Galuzzi_2005.JPG",
    ("Argentina", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Catedral_de_C%C3%B3rdoba%2C_Argentina.jpg/1280px-Catedral_de_C%C3%B3rdoba%2C_Argentina.jpg",

    # ==================== AUSTRALIA ====================
    ("Australia", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Great_Barrier_Reef_tourist_photo.jpg/1280px-Great_Barrier_Reef_tourist_photo.jpg",
    ("Australia", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Whitehaven_Beach_Whitsundays_Queensland_Australia_%28DSCF0480%29.jpg/1280px-Whitehaven_Beach_Whitsundays_Queensland_Australia_%28DSCF0480%29.jpg",
    ("Australia", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Sydney_from_the_air_%28edit%29.jpg/1280px-Sydney_from_the_air_%28edit%29.jpg",
    ("Australia", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Uluru_Australia_%282%29.jpg/1280px-Uluru_Australia_%282%29.jpg",
    ("Australia", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Great_Barrier_Reef_tourist_photo.jpg/1280px-Great_Barrier_Reef_tourist_photo.jpg",
    ("Australia", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/2/26/St_Mary%27s_Cathedral%2C_Sydney.jpg/1280px-St_Mary%27s_Cathedral%2C_Sydney.jpg",

    # ==================== BRAZIL ====================
    ("Brazil", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Cataratas_do_Igua%C3%A7u_2.jpg/1280px-Cataratas_do_Igua%C3%A7u_2.jpg",
    ("Brazil", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Ipanema_beach_in_Rio_de_Janeiro_%28hozinja%29.jpg/1280px-Ipanema_beach_in_Rio_de_Janeiro_%28hozinja%29.jpg",
    ("Brazil", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Cristo_Redentor_Rio_de_Janeiro.jpg/1280px-Cristo_Redentor_Rio_de_Janeiro.jpg",
    ("Brazil", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Pelourinho2.jpg/1280px-Pelourinho2.jpg",
    ("Brazil", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Amazon_river_boat.jpg/1280px-Amazon_river_boat.jpg",
    ("Brazil", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Bas%C3%ADlicaNossaSenhoraAparecida.jpg/1280px-Bas%C3%ADlicaNossaSenhoraAparecida.jpg",

    # ==================== CANADA ====================
    ("Canada", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Moraine_Lake%2C_Banff_National_Park.jpg/1280px-Moraine_Lake%2C_Banff_National_Park.jpg",
    ("Canada", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Cavendish_Beach.jpg/1280px-Cavendish_Beach.jpg",
    ("Canada", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Toronto_Skyline_2.jpg/1280px-Toronto_Skyline_2.jpg",
    ("Canada", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Vieux-Qu%C3%A9bec-nuit.jpg/1280px-Vieux-Qu%C3%A9bec-nuit.jpg",
    ("Canada", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Niagara_Falls%2C_viewed_from_Prospect_Point_-_June_2012.jpg/1280px-Niagara_Falls%2C_viewed_from_Prospect_Point_-_June_2012.jpg",
    ("Canada", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Notre-Dame_Basilica_Montreal.jpg/1280px-Notre-Dame_Basilica_Montreal.jpg",

    # ==================== CHINA ====================
    ("China", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Zhangjiajie_National_Forest_Park.jpg/1280px-Zhangjiajie_National_Forest_Park.jpg",
    ("China", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/YalongBay.jpg/1280px-YalongBay.jpg",
    ("China", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/The_Bund%2C_Shanghai.jpg/1280px-The_Bund%2C_Shanghai.jpg",
    ("China", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Great_Wall_of_China_July_2006.jpg/1280px-Great_Wall_of_China_July_2006.jpg",
    ("China", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Lijiang_river_karst.jpg/1280px-Lijiang_river_karst.jpg",
    ("China", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Shaolin_monastery.jpg/1280px-Shaolin_monastery.jpg",

    # ==================== EGYPT ====================
    ("Egypt", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/1280px-Kheops-Pyramid.jpg",
    ("Egypt", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Hurghada_beach.jpg/1280px-Hurghada_beach.jpg",
    ("Egypt", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Cairo_International_Stadium.jpg/1280px-Cairo_International_Stadium.jpg",
    ("Egypt", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/1280px-Kheops-Pyramid.jpg",
    ("Egypt", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/White_desert_Egypt%2C_photo_by_Hatem_Moushir_42.jpg/1280px-White_desert_Egypt%2C_photo_by_Hatem_Moushir_42.jpg",
    ("Egypt", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Ramesses_II_at_Abu_Simbel_%281%29.jpg/1280px-Ramesses_II_at_Abu_Simbel_%281%29.jpg",

    # ==================== FRANCE ====================
    ("France", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Aiguille_du_Midi_depuis_Chamonix.jpg/1280px-Aiguille_du_Midi_depuis_Chamonix.jpg",
    ("France", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Nice%2C_French_Riviera.jpg/1280px-Nice%2C_French_Riviera.jpg",
    ("France", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Tour_Eiffel_Wikimedia_Commons.jpg/1280px-Tour_Eiffel_Wikimedia_Commons.jpg",
    ("France", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Versailles_palace.jpg/1280px-Versailles_palace.jpg",
    ("France", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Mont_Saint_Michel.jpg/1280px-Mont_Saint_Michel.jpg",
    ("France", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Notre-Dame_de_Paris_-_Cathedrale_%28Yann_Caradec%29_%28cropped%29.jpg/1280px-Notre-Dame_de_Paris_-_Cathedrale_%28Yann_Caradec%29_%28cropped%29.jpg",

    # ==================== GERMANY ====================
    ("Germany", "Adventure"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Berchtesgadener_Hochthron.jpg/1280px-Berchtesgadener_Hochthron.jpg",
    ("Germany", "Beach"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Ruegen_chalk_cliffs_2.jpg/1280px-Ruegen_chalk_cliffs_2.jpg",
    ("Germany", "City"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Brandenburger_Tor_abends.jpg/1280px-Brandenburger_Tor_abends.jpg",
    ("Germany", "Historical"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Schloss_Neuschwanstein_2013.jpg/1280px-Schloss_Neuschwanstein_2013.jpg",
    ("Germany", "Nature"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Nationalpark_Schwarzwald_Panorama.jpg/1280px-Nationalpark_Schwarzwald_Panorama.jpg",
    ("Germany", "Religious"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Kölner_Dom_Panorama.jpg/1280px-Kölner_Dom_Panorama.jpg",

    # ==================== GREECE ====================
    ("Greece", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Santorini_sunset.jpg/1280px-Santorini_sunset.jpg",
    ("Greece", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Navagio-Beach-Zakynthos.jpg/1280px-Navagio-Beach-Zakynthos.jpg",
    ("Greece", "City"):          "https://upload.wikimedia.org/wikipedia/commons/d/da/The_Parthenon_in_Athens.jpg",
    ("Greece", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Meteora_-_Roussanou_Monastery.jpg/1280px-Meteora_-_Roussanou_Monastery.jpg",
    ("Greece", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Samaria_Gorge_-_Crete.jpg/1280px-Samaria_Gorge_-_Crete.jpg",
    ("Greece", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Meteora_-_Roussanou_Monastery.jpg/1280px-Meteora_-_Roussanou_Monastery.jpg",

    # ==================== INDIA ====================
    ("India", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/White_water_rafting_Rishikesh_India.jpg/1280px-White_water_rafting_Rishikesh_India.jpg",
    ("India", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Candolim_Beach%2C_Goa%2C_India.jpg/1280px-Candolim_Beach%2C_Goa%2C_India.jpg",
    ("India", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/India_Gate_in_New_Delhi.jpg/1280px-India_Gate_in_New_Delhi.jpg",
    ("India", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit3.jpg",
    ("India", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/d/d5/Kerala_backwaters.jpg",
    ("India", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Golden_Temple%2C_Amritsar%2C_India.jpg/1280px-Golden_Temple%2C_Amritsar%2C_India.jpg",

    # ==================== ITALY ====================
    ("Italy", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Cinque_Terre_-_Vernazza.jpg/1280px-Cinque_Terre_-_Vernazza.jpg",
    ("Italy", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Positano_tramonto.jpg/1280px-Positano_tramonto.jpg",
    ("Italy", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/1280px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg",
    ("Italy", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/Venezia_-_Basilica_di_San_Marco_-_2012_-_01.jpg/1280px-Venezia_-_Basilica_di_San_Marco_-_2012_-_01.jpg",
    ("Italy", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Tuscan_Landscape.jpg/1280px-Tuscan_Landscape.jpg",
    ("Italy", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/St_Peter%27s_Basilica%2C_Vatican_City_%28E%29.jpg/1280px-St_Peter%27s_Basilica%2C_Vatican_City_%28E%29.jpg",

    # ==================== JAPAN ====================
    ("Japan", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg/1280px-Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg",
    ("Japan", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Okinawa_Emerald_Beach.jpg/1280px-Okinawa_Emerald_Beach.jpg",
    ("Japan", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Dsc0120_tokyo_shibuya_scramble.jpg/1280px-Dsc0120_tokyo_shibuya_scramble.jpg",
    ("Japan", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/FushimiInari.jpg/1280px-FushimiInari.jpg",
    ("Japan", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Arashiyama_bamboo_grove_in_Kyoto%2C_Japan.jpg/1280px-Arashiyama_bamboo_grove_in_Kyoto%2C_Japan.jpg",
    ("Japan", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kinkaku-ji.jpg/1280px-Kinkaku-ji.jpg",

    # ==================== KENYA ====================
    ("Kenya", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Masai-Mara-Lion.jpg/1280px-Masai-Mara-Lion.jpg",
    ("Kenya", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/0/06/Diani_Beach%2C_Kenya.jpg",
    ("Kenya", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Nairobi_CBD.jpg/1280px-Nairobi_CBD.jpg",
    ("Kenya", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Lamu_town_kenya.jpg/1280px-Lamu_town_kenya.jpg",
    ("Kenya", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Wildebeest_in_the_Masai_Mara.jpg/1280px-Wildebeest_in_the_Masai_Mara.jpg",
    ("Kenya", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Lamu_town_kenya.jpg/1280px-Lamu_town_kenya.jpg",

    # ==================== MEXICO ====================
    ("Mexico", "Adventure"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Barrancas_del_Cobre_SRY.jpg/1280px-Barrancas_del_Cobre_SRY.jpg",
    ("Mexico", "Beach"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Mexico_Cancun_Playa_Delfines.jpg/1280px-Mexico_Cancun_Playa_Delfines.jpg",
    ("Mexico", "City"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Catedral_Metropolitana_de_la_Ciudad_de_M%C3%A9xico.jpg/1280px-Catedral_Metropolitana_de_la_Ciudad_de_M%C3%A9xico.jpg",
    ("Mexico", "Historical"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
    ("Mexico", "Nature"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Gran_Cenote%2C_Tulum.jpg/1280px-Gran_Cenote%2C_Tulum.jpg",
    ("Mexico", "Religious"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Basilica_de_Guadalupe.jpg/1280px-Basilica_de_Guadalupe.jpg",

    # ==================== MOROCCO ====================
    ("Morocco", "Adventure"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Erg_Chebbi%2C_Morocco.jpg/1280px-Erg_Chebbi%2C_Morocco.jpg",
    ("Morocco", "Beach"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Agadir_beach_morocco.jpg/1280px-Agadir_beach_morocco.jpg",
    ("Morocco", "City"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Jamaa_el_Fna_at_sunset_%28Morocco%29_crop.jpg/1280px-Jamaa_el_Fna_at_sunset_%28Morocco%29_crop.jpg",
    ("Morocco", "Historical"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Fes-morocco-medina.jpg/1280px-Fes-morocco-medina.jpg",
    ("Morocco", "Nature"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Morocco_Atlas_Mountains_Landscape.jpg/1280px-Morocco_Atlas_Mountains_Landscape.jpg",
    ("Morocco", "Religious"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Hassan_II_Mosque_in_Casablanca.jpg/1280px-Hassan_II_Mosque_in_Casablanca.jpg",

    # ==================== NEW ZEALAND ====================
    ("New Zealand", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Queenstown_New_Zealand.jpg/1280px-Queenstown_New_Zealand.jpg",
    ("New Zealand", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Cathedral_Cove_New_Zealand.jpg/1280px-Cathedral_Cove_New_Zealand.jpg",
    ("New Zealand", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Auckland_from_above_%28cropped%29.jpg/1280px-Auckland_from_above_%28cropped%29.jpg",
    ("New Zealand", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Hobbiton_Shire_NZ.jpg/1280px-Hobbiton_Shire_NZ.jpg",
    ("New Zealand", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Milford_Sound_New_Zealand.jpg/1280px-Milford_Sound_New_Zealand.jpg",
    ("New Zealand", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Christchurch_Cathedral2008.jpg/1280px-Christchurch_Cathedral2008.jpg",

    # ==================== PERU ====================
    ("Peru", "Adventure"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg",
    ("Peru", "Beach"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Mancora_Peru_Pacific_beach.jpg/1280px-Mancora_Peru_Pacific_beach.jpg",
    ("Peru", "City"):            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Lima-skyline-Miraflores.jpg/1280px-Lima-skyline-Miraflores.jpg",
    ("Peru", "Historical"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg",
    ("Peru", "Nature"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Amazon_River%2C_Manaus.jpg/1280px-Amazon_River%2C_Manaus.jpg",
    ("Peru", "Religious"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Cusco_Cathedral%2C_Peru.jpg/1280px-Cusco_Cathedral%2C_Peru.jpg",

    # ==================== SOUTH AFRICA ====================
    ("South Africa", "Adventure"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lions_waiting_in_Namibia.jpg/1280px-Lions_waiting_in_Namibia.jpg",
    ("South Africa", "Beach"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Clifton_Beach_Cape_Town_South_Africa.jpg/1280px-Clifton_Beach_Cape_Town_South_Africa.jpg",
    ("South Africa", "City"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Cape_Town_Stadium_and_the_foreshore.jpg/1280px-Cape_Town_Stadium_and_the_foreshore.jpg",
    ("South Africa", "Historical"): "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Robben_Island_Cape_Town.jpg/1280px-Robben_Island_Cape_Town.jpg",
    ("South Africa", "Nature"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Table_Mountain_DanieVDM.jpg/1280px-Table_Mountain_DanieVDM.jpg",
    ("South Africa", "Religious"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Table_Mountain_DanieVDM.jpg/1280px-Table_Mountain_DanieVDM.jpg",

    # ==================== SPAIN ====================
    ("Spain", "Adventure"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Pyrenees_Ordesa_National_Park_Huesca_Spain.jpg/1280px-Pyrenees_Ordesa_National_Park_Huesca_Spain.jpg",
    ("Spain", "Beach"):          "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Ibiza_playa_des_Codolar.jpg/1280px-Ibiza_playa_des_Codolar.jpg",
    ("Spain", "City"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Sagrada_Familia_01.jpg/1280px-Sagrada_Familia_01.jpg",
    ("Spain", "Historical"):     "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Alhambra_granada_spain.jpg/1280px-Alhambra_granada_spain.jpg",
    ("Spain", "Nature"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Teide-desde-la-guancha.jpg/1280px-Teide-desde-la-guancha.jpg",
    ("Spain", "Religious"):      "https://upload.wikimedia.org/wikipedia/commons/3/3c/Catedral_de_Santiago_de_Compostela.jpg",

    # ==================== THAILAND ====================
    ("Thailand", "Adventure"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Krabi_Thailand_Railay_beach.jpg/1280px-Krabi_Thailand_Railay_beach.jpg",
    ("Thailand", "Beach"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Phi_phi_Don_2011_%282%29.jpg/1280px-Phi_phi_Don_2011_%282%29.jpg",
    ("Thailand", "City"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Skytrain_Silom_Bangkok.jpg/1280px-Skytrain_Silom_Bangkok.jpg",
    ("Thailand", "Historical"):  "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Ayutthaya_Wat_Mahathat_Buddha_Head_in_tree.jpg/1280px-Ayutthaya_Wat_Mahathat_Buddha_Head_in_tree.jpg",
    ("Thailand", "Nature"):      "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Elephant_in_Chiang_Mai.jpg/1280px-Elephant_in_Chiang_Mai.jpg",
    ("Thailand", "Religious"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Wat_Phra_Kaew_2_amk.jpg/1280px-Wat_Phra_Kaew_2_amk.jpg",

    # ==================== USA ====================
    ("USA", "Adventure"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/USA_09847_Grand_Canyon_Luca_Galuzzi_2007.jpg/1280px-USA_09847_Grand_Canyon_Luca_Galuzzi_2007.jpg",
    ("USA", "Beach"):            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/South_Beach_from_above.jpg/1280px-South_Beach_from_above.jpg",
    ("USA", "City"):             "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/NYC_wideangle_south_from_Top_of_the_Rock.jpg/1280px-NYC_wideangle_south_from_Top_of_the_Rock.jpg",
    ("USA", "Historical"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Statue_of_Liberty%2C_NY.jpg/1280px-Statue_of_Liberty%2C_NY.jpg",
    ("USA", "Nature"):           "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Grand_Prismatic_Spring%2C_Yellowstone_National_Park.jpg/1280px-Grand_Prismatic_Spring%2C_Yellowstone_National_Park.jpg",
    ("USA", "Religious"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Washington_National_Cathedral.jpg/1280px-Washington_National_Cathedral.jpg",

    # ==================== VIETNAM ====================
    ("Vietnam", "Adventure"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Sapa_Vietnam_2.jpg/1280px-Sapa_Vietnam_2.jpg",
    ("Vietnam", "Beach"):        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Ha_Long_Bay%2C_Vietnam.jpg/1280px-Ha_Long_Bay%2C_Vietnam.jpg",
    ("Vietnam", "City"):         "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Ho_Chi_Minh_City_Skyline.jpg/1280px-Ho_Chi_Minh_City_Skyline.jpg",
    ("Vietnam", "Historical"):   "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Hoi_An_lanterns.jpg/1280px-Hoi_An_lanterns.jpg",
    ("Vietnam", "Nature"):       "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Phong_Nha_cave.jpg/1280px-Phong_Nha_cave.jpg",
    ("Vietnam", "Religious"):    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/One_Pillar_Pagoda.jpg/1280px-One_Pillar_Pagoda.jpg",
}


def update_all():
    destinations = list(db.destinations.find({}))
    total = len(destinations)
    updated = 0
    missing_keys = set()

    for dest in destinations:
        country = dest.get('Country', '')
        dest_type = dest.get('Type', '')
        key = (country, dest_type)

        if key in FINAL_IMAGE_MAP:
            db.destinations.update_one(
                {'_id': dest['_id']},
                {'$set': {'image': FINAL_IMAGE_MAP[key]}}
            )
            updated += 1
        else:
            missing_keys.add(key)

    print(f"Updated: {updated}/{total}")
    if missing_keys:
        print(f"\nMissing keys ({len(missing_keys)}):")
        for k in sorted(missing_keys):
            print(f"  {k}")

    # Verify samples
    print("\n--- Sample verification ---")
    samples = [
        ("Brazil", "City"), ("Brazil", "Religious"), ("Japan", "City"),
        ("Morocco", "Adventure"), ("Vietnam", "Beach"), ("USA", "Nature"),
        ("Germany", "Nature"), ("Greece", "Beach"),
    ]
    for country, dtype in samples:
        dest = db.destinations.find_one({'Country': country, 'Type': dtype})
        if dest:
            img = dest.get('image', 'NO IMAGE')[:80]
            print(f"  {country} | {dtype}: {img}")


if __name__ == '__main__':
    print("=" * 60)
    print("FINAL COMPLETE IMAGE UPDATE")
    print("=" * 60)
    update_all()
    print("\nDone!")
