# -*- coding: utf-8 -*-
"""
Comprehensive destination image fixer.
Maps destinations to correct images based on country + type using curated Wikimedia/Unsplash URLs.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient
import random

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# Curated high-quality images by country - real landmark photos
# Each country has multiple images for different destination types
COUNTRY_IMAGES = {
    # AFRICA
    "Morocco": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Agadir_beach.jpg/1280px-Agadir_beach.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Toubkal_Atlas_Mountains_Morocco.jpg/1280px-Toubkal_Atlas_Mountains_Morocco.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Marrakech_medina.jpg/1280px-Marrakech_medina.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Hassan_II_Mosque_in_Casablanca%2C_Morocco.jpg/1280px-Hassan_II_Mosque_in_Casablanca%2C_Morocco.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Toubkal_Atlas_Mountains_Morocco.jpg/1280px-Toubkal_Atlas_Mountains_Morocco.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Chefchaouen%2C_Morocco.jpg/1280px-Chefchaouen%2C_Morocco.jpg"
    },
    "Egypt": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/1280px-Kheops-Pyramid.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Hurghada_Egypt.jpg/1280px-Hurghada_Egypt.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/White_Desert_Egypt.jpg/1280px-White_Desert_Egypt.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Abu_Simbel%2C_Ramesses_II.jpg/1280px-Abu_Simbel%2C_Ramesses_II.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Sinai_desert_egypt.jpg/1280px-Sinai_desert_egypt.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Kheops-Pyramid.jpg/1280px-Kheops-Pyramid.jpg"
    },
    "South Africa": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Table_Mountain_DanieVDM.jpg/1280px-Table_Mountain_DanieVDM.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Boulders_Beach_Penguins_Cape_Town.jpg/1280px-Boulders_Beach_Penguins_Cape_Town.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Kruger_National_Park_Lion.jpg/1280px-Kruger_National_Park_Lion.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Robben_Island_South_Africa.jpg/1280px-Robben_Island_South_Africa.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Table_Mountain_DanieVDM.jpg/1280px-Table_Mountain_DanieVDM.jpg"
    },
    "Kenya": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Maasai_Mara_Africa.jpg/1280px-Maasai_Mara_Africa.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Mount_Kenya_National_Park.jpg/1280px-Mount_Kenya_National_Park.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Diani_Beach_Kenya.jpg/1280px-Diani_Beach_Kenya.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Lamu_Old_Town_Kenya.jpg/1280px-Lamu_Old_Town_Kenya.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Maasai_Mara_Africa.jpg/1280px-Maasai_Mara_Africa.jpg"
    },
    "Tanzania": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Kilimanjaro-tanzanie.jpg/1280px-Kilimanjaro-tanzanie.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Kilimanjaro-tanzanie.jpg/1280px-Kilimanjaro-tanzanie.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Zanzibar_beach.jpg/1280px-Zanzibar_beach.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Kilimanjaro-tanzanie.jpg/1280px-Kilimanjaro-tanzanie.jpg"
    },
    "Ethiopia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Lalibela_church_Ethiopia.jpg/1280px-Lalibela_church_Ethiopia.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Simien_Mountains_Ethiopia.jpg/1280px-Simien_Mountains_Ethiopia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Lalibela_church_Ethiopia.jpg/1280px-Lalibela_church_Ethiopia.jpg"
    },
    "Ghana": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Accra_beach_Ghana.jpg/1280px-Accra_beach_Ghana.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Cape_Coast_Castle_Ghana.jpg/1280px-Cape_Coast_Castle_Ghana.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Cape_Coast_Castle_Ghana.jpg/1280px-Cape_Coast_Castle_Ghana.jpg"
    },
    "Nigeria": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Yankari_game_reserve_Nigeria.jpg/1280px-Yankari_game_reserve_Nigeria.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Olumo_Rock_Abeokuta.jpg/1280px-Olumo_Rock_Abeokuta.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Yankari_game_reserve_Nigeria.jpg/1280px-Yankari_game_reserve_Nigeria.jpg"
    },
    "Senegal": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Dakar_beach_Senegal.jpg/1280px-Dakar_beach_Senegal.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Pink_Lake_Retba_Senegal.jpg/1280px-Pink_Lake_Retba_Senegal.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Dakar_beach_Senegal.jpg/1280px-Dakar_beach_Senegal.jpg"
    },
    "Namibia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Namib_desert_Sossusvlei.jpg/1280px-Namib_desert_Sossusvlei.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Etosha_National_Park_Namibia.jpg/1280px-Etosha_National_Park_Namibia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Namib_desert_Sossusvlei.jpg/1280px-Namib_desert_Sossusvlei.jpg"
    },
    "Madagascar": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Avenue_of_the_Baobabs_Madagascar.jpg/1280px-Avenue_of_the_Baobabs_Madagascar.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Nosy_Be_beach_Madagascar.jpg/1280px-Nosy_Be_beach_Madagascar.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Avenue_of_the_Baobabs_Madagascar.jpg/1280px-Avenue_of_the_Baobabs_Madagascar.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Avenue_of_the_Baobabs_Madagascar.jpg/1280px-Avenue_of_the_Baobabs_Madagascar.jpg"
    },
    "Zimbabwe": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Victoria_Falls_Zimbabwe.jpg/1280px-Victoria_Falls_Zimbabwe.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Great_Zimbabwe_Ruins.jpg/1280px-Great_Zimbabwe_Ruins.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Victoria_Falls_Zimbabwe.jpg/1280px-Victoria_Falls_Zimbabwe.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Victoria_Falls_Zimbabwe.jpg/1280px-Victoria_Falls_Zimbabwe.jpg"
    },
    "Botswana": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Okavango_Delta_Botswana.jpg/1280px-Okavango_Delta_Botswana.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Okavango_Delta_Botswana.jpg/1280px-Okavango_Delta_Botswana.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Okavango_Delta_Botswana.jpg/1280px-Okavango_Delta_Botswana.jpg"
    },
    "Uganda": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Mountain_gorillas_Uganda.jpg/1280px-Mountain_gorillas_Uganda.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Mountain_gorillas_Uganda.jpg/1280px-Mountain_gorillas_Uganda.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Mountain_gorillas_Uganda.jpg/1280px-Mountain_gorillas_Uganda.jpg"
    },
    "Zambia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Victoria_Falls_Zimbabwe.jpg/1280px-Victoria_Falls_Zimbabwe.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Victoria_Falls_Zimbabwe.jpg/1280px-Victoria_Falls_Zimbabwe.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Victoria_Falls_Zimbabwe.jpg/1280px-Victoria_Falls_Zimbabwe.jpg"
    },
    "Tunisia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Carthage_ruins_Tunisia.jpg/1280px-Carthage_ruins_Tunisia.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Hammamet_beach_Tunisia.jpg/1280px-Hammamet_beach_Tunisia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Carthage_ruins_Tunisia.jpg/1280px-Carthage_ruins_Tunisia.jpg"
    },
    "Cameroon": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Mount_Cameroon.jpg/1280px-Mount_Cameroon.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Mount_Cameroon.jpg/1280px-Mount_Cameroon.jpg"
    },
    "Ivory Coast": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Abidjan_Ivory_Coast.jpg/1280px-Abidjan_Ivory_Coast.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Abidjan_Ivory_Coast.jpg/1280px-Abidjan_Ivory_Coast.jpg"
    },
    "Mozambique": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Vilanculos_beach_Mozambique.jpg/1280px-Vilanculos_beach_Mozambique.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Vilanculos_beach_Mozambique.jpg/1280px-Vilanculos_beach_Mozambique.jpg"
    },
    "Rwanda": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Volcanoes_National_Park_Rwanda.jpg/1280px-Volcanoes_National_Park_Rwanda.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Volcanoes_National_Park_Rwanda.jpg/1280px-Volcanoes_National_Park_Rwanda.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Volcanoes_National_Park_Rwanda.jpg/1280px-Volcanoes_National_Park_Rwanda.jpg"
    },
    "Seychelles": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Anse_Source_d%27Argent%2C_La_Digue%2C_Seychelles.jpg/1280px-Anse_Source_d%27Argent%2C_La_Digue%2C_Seychelles.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Anse_Source_d%27Argent%2C_La_Digue%2C_Seychelles.jpg/1280px-Anse_Source_d%27Argent%2C_La_Digue%2C_Seychelles.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Anse_Source_d%27Argent%2C_La_Digue%2C_Seychelles.jpg/1280px-Anse_Source_d%27Argent%2C_La_Digue%2C_Seychelles.jpg"
    },
    "Mauritius": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Le_Morne_beach_Mauritius.jpg/1280px-Le_Morne_beach_Mauritius.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Le_Morne_beach_Mauritius.jpg/1280px-Le_Morne_beach_Mauritius.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Le_Morne_beach_Mauritius.jpg/1280px-Le_Morne_beach_Mauritius.jpg"
    },
    "Algeria": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Djemila_Algeria.jpg/1280px-Djemila_Algeria.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Sahara_desert_Algeria.jpg/1280px-Sahara_desert_Algeria.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Sahara_desert_Algeria.jpg/1280px-Sahara_desert_Algeria.jpg"
    },
    "Libya": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Leptis_Magna_Libya.jpg/1280px-Leptis_Magna_Libya.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Leptis_Magna_Libya.jpg/1280px-Leptis_Magna_Libya.jpg"
    },

    # ASIA
    "Japan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Shinjuku_I-Land_from_Shinjuku_Chuo_Park_201009.jpg/1280px-Shinjuku_I-Land_from_Shinjuku_Chuo_Park_201009.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Arashiyama_Bamboo_Forest.jpg/1280px-Arashiyama_Bamboo_Forest.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Naha_Okinawa_beach.jpg/1280px-Naha_Okinawa_beach.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kinkaku-ji_Kyoto_Japan.jpg/1280px-Kinkaku-ji_Kyoto_Japan.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg/1280px-Mount_Fuji_from_Hotel_Mt_Fuji_2004-07-22_cropped.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Kinkaku-ji_Kyoto_Japan.jpg/1280px-Kinkaku-ji_Kyoto_Japan.jpg"
    },
    "China": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Forbidden_City_Beijing.jpg/1280px-Forbidden_City_Beijing.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Zhangjiajie_China.jpg/1280px-Zhangjiajie_China.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Shaolin_Monastery_China.jpg/1280px-Shaolin_Monastery_China.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Great_Wall_of_China_July_2006.jpg/1280px-Great_Wall_of_China_July_2006.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Hainan_Beach_China.jpg/1280px-Hainan_Beach_China.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Great_Wall_of_China_July_2006.jpg/1280px-Great_Wall_of_China_July_2006.jpg"
    },
    "India": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit3.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Golden_Temple_Amritsar.jpg/1280px-Golden_Temple_Amritsar.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Kerala_backwaters_India.jpg/1280px-Kerala_backwaters_India.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Goa_beach_India.jpg/1280px-Goa_beach_India.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Rishikesh_adventure_rafting.jpg/1280px-Rishikesh_adventure_rafting.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Taj_Mahal%2C_Agra%2C_India_edit3.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit3.jpg"
    },
    "Thailand": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Phi_phi_Don_from_viewpoint.jpg/1280px-Phi_phi_Don_from_viewpoint.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Wat_Pho_temple_Bangkok.jpg/1280px-Wat_Pho_temple_Bangkok.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Chiang_Mai_doi_inthanon.jpg/1280px-Chiang_Mai_doi_inthanon.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Wat_Arun_Bangkok_Thailand.jpg/1280px-Wat_Arun_Bangkok_Thailand.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Phi_phi_Don_from_viewpoint.jpg/1280px-Phi_phi_Don_from_viewpoint.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Phi_phi_Don_from_viewpoint.jpg/1280px-Phi_phi_Don_from_viewpoint.jpg"
    },
    "Vietnam": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Ha_Long_Bay%2C_Vietnam.jpg/1280px-Ha_Long_Bay%2C_Vietnam.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Hoi_An_Ancient_Town.jpg/1280px-Hoi_An_Ancient_Town.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Da_Nang_Beach_Vietnam.jpg/1280px-Da_Nang_Beach_Vietnam.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Sapa_Vietnam_terraces.jpg/1280px-Sapa_Vietnam_terraces.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Hoi_An_Ancient_Town.jpg/1280px-Hoi_An_Ancient_Town.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Ha_Long_Bay%2C_Vietnam.jpg/1280px-Ha_Long_Bay%2C_Vietnam.jpg"
    },
    "Indonesia": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Bali_Indonesia_Kuta_Beach.jpg/1280px-Bali_Indonesia_Kuta_Beach.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Komodo_island_Indonesia.jpg/1280px-Komodo_island_Indonesia.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Borobudur_temple_Indonesia.jpg/1280px-Borobudur_temple_Indonesia.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Tanah_Lot_Bali_temple.jpg/1280px-Tanah_Lot_Bali_temple.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Komodo_island_Indonesia.jpg/1280px-Komodo_island_Indonesia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Bali_Indonesia_Kuta_Beach.jpg/1280px-Bali_Indonesia_Kuta_Beach.jpg"
    },
    "Malaysia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Petronas_Towers_Kuala_Lumpur.jpg/1280px-Petronas_Towers_Kuala_Lumpur.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Taman_Negara_Malaysia_rainforest.jpg/1280px-Taman_Negara_Malaysia_rainforest.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Langkawi_beach_Malaysia.jpg/1280px-Langkawi_beach_Malaysia.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Taman_Negara_Malaysia_rainforest.jpg/1280px-Taman_Negara_Malaysia_rainforest.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Petronas_Towers_Kuala_Lumpur.jpg/1280px-Petronas_Towers_Kuala_Lumpur.jpg"
    },
    "Philippines": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Palawan_El_Nido_Philippines.jpg/1280px-Palawan_El_Nido_Philippines.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Chocolate_Hills_Bohol_Philippines.jpg/1280px-Chocolate_Hills_Bohol_Philippines.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Intramuros_Manila_Philippines.jpg/1280px-Intramuros_Manila_Philippines.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Palawan_El_Nido_Philippines.jpg/1280px-Palawan_El_Nido_Philippines.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Palawan_El_Nido_Philippines.jpg/1280px-Palawan_El_Nido_Philippines.jpg"
    },
    "Cambodia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Angkor_Wat%2C_Camboya%2C_2013-08-16%2C_DD_48.JPG/1280px-Angkor_Wat%2C_Camboya%2C_2013-08-16%2C_DD_48.JPG",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Angkor_Wat%2C_Camboya%2C_2013-08-16%2C_DD_48.JPG/1280px-Angkor_Wat%2C_Camboya%2C_2013-08-16%2C_DD_48.JPG",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Angkor_Wat%2C_Camboya%2C_2013-08-16%2C_DD_48.JPG/1280px-Angkor_Wat%2C_Camboya%2C_2013-08-16%2C_DD_48.JPG"
    },
    "Myanmar": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Bagan_Myanmar_temples.jpg/1280px-Bagan_Myanmar_temples.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Shwedagon_pagoda_Yangon.jpg/1280px-Shwedagon_pagoda_Yangon.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Bagan_Myanmar_temples.jpg/1280px-Bagan_Myanmar_temples.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Bagan_Myanmar_temples.jpg/1280px-Bagan_Myanmar_temples.jpg"
    },
    "Nepal": {
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg/1280px-Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Pashupatinath_temple_Nepal.jpg/1280px-Pashupatinath_temple_Nepal.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg/1280px-Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Bhaktapur_Durbar_Square_Nepal.jpg/1280px-Bhaktapur_Durbar_Square_Nepal.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg/1280px-Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg"
    },
    "Sri Lanka": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Sigiriya_rock_fortress_Sri_Lanka.jpg/1280px-Sigiriya_rock_fortress_Sri_Lanka.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Mirissa_Beach_Sri_Lanka.jpg/1280px-Mirissa_Beach_Sri_Lanka.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Temple_of_the_Tooth_Kandy_Sri_Lanka.jpg/1280px-Temple_of_the_Tooth_Kandy_Sri_Lanka.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Yala_National_Park_Sri_Lanka.jpg/1280px-Yala_National_Park_Sri_Lanka.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Sigiriya_rock_fortress_Sri_Lanka.jpg/1280px-Sigiriya_rock_fortress_Sri_Lanka.jpg"
    },
    "Bangladesh": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Sundarbans_National_Park.jpg/1280px-Sundarbans_National_Park.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Somapura_Mahavihara_Paharpur_Bangladesh.jpg/1280px-Somapura_Mahavihara_Paharpur_Bangladesh.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Sundarbans_National_Park.jpg/1280px-Sundarbans_National_Park.jpg"
    },
    "Pakistan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Lahore_Fort_Pakistan.jpg/1280px-Lahore_Fort_Pakistan.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/K2_Pakistan.jpg/1280px-K2_Pakistan.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/K2_Pakistan.jpg/1280px-K2_Pakistan.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Lahore_Fort_Pakistan.jpg/1280px-Lahore_Fort_Pakistan.jpg"
    },
    "Maldives": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Maldives_beach_resort.jpg/1280px-Maldives_beach_resort.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Maldives_beach_resort.jpg/1280px-Maldives_beach_resort.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Maldives_beach_resort.jpg/1280px-Maldives_beach_resort.jpg"
    },
    "Bhutan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Tigers_Nest_Monastery_Bhutan.jpg/1280px-Tigers_Nest_Monastery_Bhutan.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Tigers_Nest_Monastery_Bhutan.jpg/1280px-Tigers_Nest_Monastery_Bhutan.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Bhutan_mountains_Himalaya.jpg/1280px-Bhutan_mountains_Himalaya.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Tigers_Nest_Monastery_Bhutan.jpg/1280px-Tigers_Nest_Monastery_Bhutan.jpg"
    },
    "Singapore": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Singapore_Marina_Bay_Sands.jpg/1280px-Singapore_Marina_Bay_Sands.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Gardens_by_the_Bay_Singapore.jpg/1280px-Gardens_by_the_Bay_Singapore.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Singapore_Marina_Bay_Sands.jpg/1280px-Singapore_Marina_Bay_Sands.jpg"
    },
    "South Korea": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Gyeongbokgung_Palace_Seoul.jpg/1280px-Gyeongbokgung_Palace_Seoul.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Seoraksan_National_Park_South_Korea.jpg/1280px-Seoraksan_National_Park_South_Korea.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Jeju_Island_beach_South_Korea.jpg/1280px-Jeju_Island_beach_South_Korea.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Gyeongbokgung_Palace_Seoul.jpg/1280px-Gyeongbokgung_Palace_Seoul.jpg"
    },
    "Taiwan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Taipei_101_from_the_Elephant_Mountain.jpg/1280px-Taipei_101_from_the_Elephant_Mountain.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Taroko_National_Park_Taiwan.jpg/1280px-Taroko_National_Park_Taiwan.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Taipei_101_from_the_Elephant_Mountain.jpg/1280px-Taipei_101_from_the_Elephant_Mountain.jpg"
    },
    "Jordan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Petra_Jordan.jpg/1280px-Petra_Jordan.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Petra_Jordan.jpg/1280px-Petra_Jordan.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Wadi_Rum_Jordan.jpg/1280px-Wadi_Rum_Jordan.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Petra_Jordan.jpg/1280px-Petra_Jordan.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Petra_Jordan.jpg/1280px-Petra_Jordan.jpg"
    },
    "Israel": {
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Jerusalem_Old_City_Wall.jpg/1280px-Jerusalem_Old_City_Wall.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Masada_Israel.jpg/1280px-Masada_Israel.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Tel_Aviv_beach_Israel.jpg/1280px-Tel_Aviv_beach_Israel.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Jerusalem_Old_City_Wall.jpg/1280px-Jerusalem_Old_City_Wall.jpg"
    },
    "Saudi Arabia": {
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Masjid_al-Haram_Mecca.jpg/1280px-Masjid_al-Haram_Mecca.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Hegra_AlUla_Saudi_Arabia.jpg/1280px-Hegra_AlUla_Saudi_Arabia.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Asir_National_Park_Saudi_Arabia.jpg/1280px-Asir_National_Park_Saudi_Arabia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Masjid_al-Haram_Mecca.jpg/1280px-Masjid_al-Haram_Mecca.jpg"
    },
    "UAE": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Dubai_Marina_Skyline.jpg/1280px-Dubai_Marina_Skyline.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Jumeirah_beach_Dubai_UAE.jpg/1280px-Jumeirah_beach_Dubai_UAE.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Liwa_desert_Abu_Dhabi.jpg/1280px-Liwa_desert_Abu_Dhabi.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Dubai_Marina_Skyline.jpg/1280px-Dubai_Marina_Skyline.jpg"
    },
    "Turkey": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Hagia_Sophia_Istanbul.jpg/1280px-Hagia_Sophia_Istanbul.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Cappadocia_Turkey_balloons.jpg/1280px-Cappadocia_Turkey_balloons.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Oludeniz_beach_Turkey.jpg/1280px-Oludeniz_beach_Turkey.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Hagia_Sophia_Istanbul.jpg/1280px-Hagia_Sophia_Istanbul.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Cappadocia_Turkey_balloons.jpg/1280px-Cappadocia_Turkey_balloons.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Cappadocia_Turkey_balloons.jpg/1280px-Cappadocia_Turkey_balloons.jpg"
    },
    "Iran": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Persepolis_Iran.jpg/1280px-Persepolis_Iran.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Nasir_ol_molk_Mosque_Iran.jpg/1280px-Nasir_ol_molk_Mosque_Iran.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Persepolis_Iran.jpg/1280px-Persepolis_Iran.jpg"
    },
    "Oman": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Muscat_Oman_Sultan_Qaboos_Mosque.jpg/1280px-Muscat_Oman_Sultan_Qaboos_Mosque.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Wadi_Shab_Oman.jpg/1280px-Wadi_Shab_Oman.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Wadi_Shab_Oman.jpg/1280px-Wadi_Shab_Oman.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Muscat_Oman_Sultan_Qaboos_Mosque.jpg/1280px-Muscat_Oman_Sultan_Qaboos_Mosque.jpg"
    },
    "Qatar": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Doha_Qatar_skyline.jpg/1280px-Doha_Qatar_skyline.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Doha_Qatar_skyline.jpg/1280px-Doha_Qatar_skyline.jpg"
    },
    "Georgia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Gergeti_Trinity_Church_Georgia.jpg/1280px-Gergeti_Trinity_Church_Georgia.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Caucasus_mountains_Georgia.jpg/1280px-Caucasus_mountains_Georgia.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Gergeti_Trinity_Church_Georgia.jpg/1280px-Gergeti_Trinity_Church_Georgia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Gergeti_Trinity_Church_Georgia.jpg/1280px-Gergeti_Trinity_Church_Georgia.jpg"
    },
    "Armenia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Geghard_Monastery_Armenia.jpg/1280px-Geghard_Monastery_Armenia.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Geghard_Monastery_Armenia.jpg/1280px-Geghard_Monastery_Armenia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Geghard_Monastery_Armenia.jpg/1280px-Geghard_Monastery_Armenia.jpg"
    },
    "Azerbaijan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Baku_flame_towers_Azerbaijan.jpg/1280px-Baku_flame_towers_Azerbaijan.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Baku_flame_towers_Azerbaijan.jpg/1280px-Baku_flame_towers_Azerbaijan.jpg"
    },
    "Kazakhstan": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Charyn_Canyon_Kazakhstan.jpg/1280px-Charyn_Canyon_Kazakhstan.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Nur_Sultan_Astana_Kazakhstan.jpg/1280px-Nur_Sultan_Astana_Kazakhstan.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Charyn_Canyon_Kazakhstan.jpg/1280px-Charyn_Canyon_Kazakhstan.jpg"
    },
    "Uzbekistan": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Samarkand_Registan.jpg/1280px-Samarkand_Registan.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Samarkand_Registan.jpg/1280px-Samarkand_Registan.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Samarkand_Registan.jpg/1280px-Samarkand_Registan.jpg"
    },
    "Mongolia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Mongolia_steppe_landscape.jpg/1280px-Mongolia_steppe_landscape.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Mongolia_steppe_landscape.jpg/1280px-Mongolia_steppe_landscape.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Mongolia_steppe_landscape.jpg/1280px-Mongolia_steppe_landscape.jpg"
    },

    # EUROPE
    "France": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Tour_eiffel_at_sunrise_from_the_trocadero.jpg/1280px-Tour_eiffel_at_sunrise_from_the_trocadero.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/French_Alps_Chamonix.jpg/1280px-French_Alps_Chamonix.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Nice_beach_French_Riviera.jpg/1280px-Nice_beach_French_Riviera.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/French_Alps_Chamonix.jpg/1280px-French_Alps_Chamonix.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Notre-Dame_de_Paris_2013-07-24.jpg/1280px-Notre-Dame_de_Paris_2013-07-24.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Tour_eiffel_at_sunrise_from_the_trocadero.jpg/1280px-Tour_eiffel_at_sunrise_from_the_trocadero.jpg"
    },
    "Italy": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/1280px-Colosseo_2020.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Dolomites_Italy_Alps.jpg/1280px-Dolomites_Italy_Alps.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Amalfi_coast_beach_Italy.jpg/1280px-Amalfi_coast_beach_Italy.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/St_Peters_Basilica_Vatican.jpg/1280px-St_Peters_Basilica_Vatican.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Dolomites_Italy_Alps.jpg/1280px-Dolomites_Italy_Alps.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/1280px-Colosseo_2020.jpg"
    },
    "Spain": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Sagrada_Familia_Barcelona.jpg/1280px-Sagrada_Familia_Barcelona.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Ibiza_beach_Spain.jpg/1280px-Ibiza_beach_Spain.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Teide_volcano_Tenerife_Spain.jpg/1280px-Teide_volcano_Tenerife_Spain.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Cathedral_of_Santiago_de_Compostela.jpg/1280px-Cathedral_of_Santiago_de_Compostela.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Teide_volcano_Tenerife_Spain.jpg/1280px-Teide_volcano_Tenerife_Spain.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Sagrada_Familia_Barcelona.jpg/1280px-Sagrada_Familia_Barcelona.jpg"
    },
    "Greece": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Acropolis_Athens.jpg/1280px-Acropolis_Athens.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Santorini_Greece_beach.jpg/1280px-Santorini_Greece_beach.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Meteora_Greece_monasteries.jpg/1280px-Meteora_Greece_monasteries.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Meteora_Greece_monasteries.jpg/1280px-Meteora_Greece_monasteries.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Santorini_Greece_beach.jpg/1280px-Santorini_Greece_beach.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Santorini_Greece_beach.jpg/1280px-Santorini_Greece_beach.jpg"
    },
    "Germany": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Neuschwanstein_Castle_Bavaria.jpg/1280px-Neuschwanstein_Castle_Bavaria.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Black_Forest_Germany.jpg/1280px-Black_Forest_Germany.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Cologne_Cathedral_Germany.jpg/1280px-Cologne_Cathedral_Germany.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Black_Forest_Germany.jpg/1280px-Black_Forest_Germany.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Neuschwanstein_Castle_Bavaria.jpg/1280px-Neuschwanstein_Castle_Bavaria.jpg"
    },
    "United Kingdom": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/London_Skyline_%28125508655%29.jpeg/1280px-London_Skyline_%28125508655%29.jpeg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Scottish_Highlands_landscape.jpg/1280px-Scottish_Highlands_landscape.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Stonehenge_total_2022.jpg/1280px-Stonehenge_total_2022.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Scottish_Highlands_landscape.jpg/1280px-Scottish_Highlands_landscape.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/London_Skyline_%28125508655%29.jpeg/1280px-London_Skyline_%28125508655%29.jpeg"
    },
    "Switzerland": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Matterhorn_mountain_Switzerland.jpg/1280px-Matterhorn_mountain_Switzerland.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Matterhorn_mountain_Switzerland.jpg/1280px-Matterhorn_mountain_Switzerland.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Geneva_Switzerland_Lake.jpg/1280px-Geneva_Switzerland_Lake.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Matterhorn_mountain_Switzerland.jpg/1280px-Matterhorn_mountain_Switzerland.jpg"
    },
    "Austria": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Schoenbrunn_palace_Vienna.jpg/1280px-Schoenbrunn_palace_Vienna.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hallstatt_Austria_lake.jpg/1280px-Hallstatt_Austria_lake.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hallstatt_Austria_lake.jpg/1280px-Hallstatt_Austria_lake.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Hallstatt_Austria_lake.jpg/1280px-Hallstatt_Austria_lake.jpg"
    },
    "Netherlands": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Amsterdam_canal_Netherlands.jpg/1280px-Amsterdam_canal_Netherlands.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Keukenhof_Netherlands_tulips.jpg/1280px-Keukenhof_Netherlands_tulips.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Amsterdam_canal_Netherlands.jpg/1280px-Amsterdam_canal_Netherlands.jpg"
    },
    "Belgium": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Grand_Place_Brussels_Belgium.jpg/1280px-Grand_Place_Brussels_Belgium.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Grand_Place_Brussels_Belgium.jpg/1280px-Grand_Place_Brussels_Belgium.jpg"
    },
    "Portugal": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Belem_Tower_Lisbon_Portugal.jpg/1280px-Belem_Tower_Lisbon_Portugal.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Algarve_beach_Portugal.jpg/1280px-Algarve_beach_Portugal.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Douro_Valley_Portugal.jpg/1280px-Douro_Valley_Portugal.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Belem_Tower_Lisbon_Portugal.jpg/1280px-Belem_Tower_Lisbon_Portugal.jpg"
    },
    "Czech Republic": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Prague_Old_Town_Square.jpg/1280px-Prague_Old_Town_Square.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/Prague_Old_Town_Square.jpg/1280px-Prague_Old_Town_Square.jpg"
    },
    "Poland": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Krakow_Wawel_Castle_Poland.jpg/1280px-Krakow_Wawel_Castle_Poland.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Tatra_Mountains_Poland.jpg/1280px-Tatra_Mountains_Poland.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Krakow_Wawel_Castle_Poland.jpg/1280px-Krakow_Wawel_Castle_Poland.jpg"
    },
    "Hungary": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Budapest_Parliament_Building.jpg/1280px-Budapest_Parliament_Building.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/Budapest_Parliament_Building.jpg/1280px-Budapest_Parliament_Building.jpg"
    },
    "Croatia": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Dubrovnik_Croatia_Old_Town.jpg/1280px-Dubrovnik_Croatia_Old_Town.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Dubrovnik_Croatia_Old_Town.jpg/1280px-Dubrovnik_Croatia_Old_Town.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Plitvice_Lakes_Croatia.jpg/1280px-Plitvice_Lakes_Croatia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Dubrovnik_Croatia_Old_Town.jpg/1280px-Dubrovnik_Croatia_Old_Town.jpg"
    },
    "Norway": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Geiranger_fjord_Norway.jpg/1280px-Geiranger_fjord_Norway.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Geiranger_fjord_Norway.jpg/1280px-Geiranger_fjord_Norway.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Bryggen_Bergen_Norway.jpg/1280px-Bryggen_Bergen_Norway.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Geiranger_fjord_Norway.jpg/1280px-Geiranger_fjord_Norway.jpg"
    },
    "Sweden": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Northern_Lights_Sweden.jpg/1280px-Northern_Lights_Sweden.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Stockholm_Old_Town_Sweden.jpg/1280px-Stockholm_Old_Town_Sweden.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Stockholm_Old_Town_Sweden.jpg/1280px-Stockholm_Old_Town_Sweden.jpg"
    },
    "Denmark": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Copenhagen_Nyhavn_Denmark.jpg/1280px-Copenhagen_Nyhavn_Denmark.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Copenhagen_Nyhavn_Denmark.jpg/1280px-Copenhagen_Nyhavn_Denmark.jpg"
    },
    "Finland": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Northern_Lights_Finland.jpg/1280px-Northern_Lights_Finland.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Northern_Lights_Finland.jpg/1280px-Northern_Lights_Finland.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Northern_Lights_Finland.jpg/1280px-Northern_Lights_Finland.jpg"
    },
    "Iceland": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Kirkjufell_Iceland.jpg/1280px-Kirkjufell_Iceland.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Northern_Lights_Iceland.jpg/1280px-Northern_Lights_Iceland.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Kirkjufell_Iceland.jpg/1280px-Kirkjufell_Iceland.jpg"
    },
    "Ireland": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Cliffs_of_Moher_Ireland.jpg/1280px-Cliffs_of_Moher_Ireland.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Dublin_Ireland_Temple_Bar.jpg/1280px-Dublin_Ireland_Temple_Bar.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Cliffs_of_Moher_Ireland.jpg/1280px-Cliffs_of_Moher_Ireland.jpg"
    },
    "Russia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Saint_Basil%27s_Cathedral_Moscow.jpg/1280px-Saint_Basil%27s_Cathedral_Moscow.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Lake_Baikal_Russia.jpg/1280px-Lake_Baikal_Russia.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Saint_Basil%27s_Cathedral_Moscow.jpg/1280px-Saint_Basil%27s_Cathedral_Moscow.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Saint_Basil%27s_Cathedral_Moscow.jpg/1280px-Saint_Basil%27s_Cathedral_Moscow.jpg"
    },
    "Ukraine": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Kyiv-Pechersk_Lavra_Ukraine.jpg/1280px-Kyiv-Pechersk_Lavra_Ukraine.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Kyiv-Pechersk_Lavra_Ukraine.jpg/1280px-Kyiv-Pechersk_Lavra_Ukraine.jpg"
    },
    "Romania": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Bran_Castle_Romania.jpg/1280px-Bran_Castle_Romania.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Carpathian_Mountains_Romania.jpg/1280px-Carpathian_Mountains_Romania.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Bran_Castle_Romania.jpg/1280px-Bran_Castle_Romania.jpg"
    },
    "Bulgaria": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Rila_Monastery_Bulgaria.jpg/1280px-Rila_Monastery_Bulgaria.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Golden_Sands_Bulgaria.jpg/1280px-Golden_Sands_Bulgaria.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Rila_Monastery_Bulgaria.jpg/1280px-Rila_Monastery_Bulgaria.jpg"
    },
    "Serbia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Belgrade_fortress_Serbia.jpg/1280px-Belgrade_fortress_Serbia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Belgrade_fortress_Serbia.jpg/1280px-Belgrade_fortress_Serbia.jpg"
    },
    "Slovakia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Tatra_mountains_Slovakia.jpg/1280px-Tatra_mountains_Slovakia.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Bratislava_castle_Slovakia.jpg/1280px-Bratislava_castle_Slovakia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Bratislava_castle_Slovakia.jpg/1280px-Bratislava_castle_Slovakia.jpg"
    },
    "Slovenia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Lake_Bled_Slovenia.jpg/1280px-Lake_Bled_Slovenia.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Lake_Bled_Slovenia.jpg/1280px-Lake_Bled_Slovenia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Lake_Bled_Slovenia.jpg/1280px-Lake_Bled_Slovenia.jpg"
    },
    "Albania": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Ksamil_beach_Albania.jpg/1280px-Ksamil_beach_Albania.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Gjirokaster_Albania.jpg/1280px-Gjirokaster_Albania.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Ksamil_beach_Albania.jpg/1280px-Ksamil_beach_Albania.jpg"
    },
    "Montenegro": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Kotor_bay_Montenegro.jpg/1280px-Kotor_bay_Montenegro.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Kotor_bay_Montenegro.jpg/1280px-Kotor_bay_Montenegro.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Kotor_bay_Montenegro.jpg/1280px-Kotor_bay_Montenegro.jpg"
    },
    "Kosovo": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Prizren_Kosovo.jpg/1280px-Prizren_Kosovo.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/13/Prizren_Kosovo.jpg/1280px-Prizren_Kosovo.jpg"
    },
    "North Macedonia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Ohrid_North_Macedonia.jpg/1280px-Ohrid_North_Macedonia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Ohrid_North_Macedonia.jpg/1280px-Ohrid_North_Macedonia.jpg"
    },
    "Bosnia and Herzegovina": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Mostar_bridge_Bosnia.jpg/1280px-Mostar_bridge_Bosnia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Mostar_bridge_Bosnia.jpg/1280px-Mostar_bridge_Bosnia.jpg"
    },
    "Luxembourg": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Luxembourg_City.jpg/1280px-Luxembourg_City.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Luxembourg_City.jpg/1280px-Luxembourg_City.jpg"
    },
    "Malta": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Valletta_Malta.jpg/1280px-Valletta_Malta.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Malta_Blue_Lagoon.jpg/1280px-Malta_Blue_Lagoon.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Valletta_Malta.jpg/1280px-Valletta_Malta.jpg"
    },
    "Cyprus": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Aphrodite_beach_Cyprus.jpg/1280px-Aphrodite_beach_Cyprus.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Paphos_Castle_Cyprus.jpg/1280px-Paphos_Castle_Cyprus.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Aphrodite_beach_Cyprus.jpg/1280px-Aphrodite_beach_Cyprus.jpg"
    },

    # AMERICAS
    "United States": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/24701-nature-natural-beauty-natural-beauty.jpg/1280px-24701-nature-natural-beauty-natural-beauty.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Miami_Beach_Florida_USA.jpg/1280px-Miami_Beach_Florida_USA.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/24701-nature-natural-beauty-natural-beauty.jpg/1280px-24701-nature-natural-beauty-natural-beauty.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Grand_Canyon_National_Park_USA.jpg/1280px-Grand_Canyon_National_Park_USA.jpg"
    },
    "Canada": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Banff_National_Park_Canada.jpg/1280px-Banff_National_Park_Canada.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Quebec_City_Canada.jpg/1280px-Quebec_City_Canada.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Banff_National_Park_Canada.jpg/1280px-Banff_National_Park_Canada.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Banff_National_Park_Canada.jpg/1280px-Banff_National_Park_Canada.jpg"
    },
    "Mexico": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Chichen_Itza_Mexico.jpg/1280px-Chichen_Itza_Mexico.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Cancun_Mexico_beach.jpg/1280px-Cancun_Mexico_beach.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Copper_Canyon_Mexico.jpg/1280px-Copper_Canyon_Mexico.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Copper_Canyon_Mexico.jpg/1280px-Copper_Canyon_Mexico.jpg",
        "Religious": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Chichen_Itza_Mexico.jpg/1280px-Chichen_Itza_Mexico.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Chichen_Itza_Mexico.jpg/1280px-Chichen_Itza_Mexico.jpg"
    },
    "Brazil": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Christ_the_Redeemer_-_Corcovado.jpg/1280px-Christ_the_Redeemer_-_Corcovado.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Amazon_rainforest_Brazil.jpg/1280px-Amazon_rainforest_Brazil.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Rio_de_Janeiro_Ipanema_beach.jpg/1280px-Rio_de_Janeiro_Ipanema_beach.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Iguazu_Falls_Brazil.jpg/1280px-Iguazu_Falls_Brazil.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Christ_the_Redeemer_-_Corcovado.jpg/1280px-Christ_the_Redeemer_-_Corcovado.jpg"
    },
    "Argentina": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Perito_Moreno_glacier_Argentina.jpg/1280px-Perito_Moreno_glacier_Argentina.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Buenos_Aires_Argentina.jpg/1280px-Buenos_Aires_Argentina.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Perito_Moreno_glacier_Argentina.jpg/1280px-Perito_Moreno_glacier_Argentina.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Perito_Moreno_glacier_Argentina.jpg/1280px-Perito_Moreno_glacier_Argentina.jpg"
    },
    "Peru": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Amazon_rainforest_Peru.jpg/1280px-Amazon_rainforest_Peru.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Machu_Picchu%2C_Peru.jpg/1280px-Machu_Picchu%2C_Peru.jpg"
    },
    "Colombia": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Cartagena_Colombia_old_city.jpg/1280px-Cartagena_Colombia_old_city.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Cocora_Valley_Colombia.jpg/1280px-Cocora_Valley_Colombia.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Tayrona_National_Park_Colombia.jpg/1280px-Tayrona_National_Park_Colombia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Cartagena_Colombia_old_city.jpg/1280px-Cartagena_Colombia_old_city.jpg"
    },
    "Chile": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Torres_del_Paine_Chile.jpg/1280px-Torres_del_Paine_Chile.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Torres_del_Paine_Chile.jpg/1280px-Torres_del_Paine_Chile.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Easter_Island_Moai.jpg/1280px-Easter_Island_Moai.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Torres_del_Paine_Chile.jpg/1280px-Torres_del_Paine_Chile.jpg"
    },
    "Ecuador": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Galapagos_Islands_Ecuador.jpg/1280px-Galapagos_Islands_Ecuador.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Galapagos_Islands_Ecuador.jpg/1280px-Galapagos_Islands_Ecuador.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Quito_Ecuador_historic.jpg/1280px-Quito_Ecuador_historic.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Galapagos_Islands_Ecuador.jpg/1280px-Galapagos_Islands_Ecuador.jpg"
    },
    "Bolivia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Salar_de_Uyuni_Bolivia.jpg/1280px-Salar_de_Uyuni_Bolivia.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Tiwanaku_Bolivia.jpg/1280px-Tiwanaku_Bolivia.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Salar_de_Uyuni_Bolivia.jpg/1280px-Salar_de_Uyuni_Bolivia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Salar_de_Uyuni_Bolivia.jpg/1280px-Salar_de_Uyuni_Bolivia.jpg"
    },
    "Venezuela": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Angel_Falls_Venezuela.jpg/1280px-Angel_Falls_Venezuela.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Angel_Falls_Venezuela.jpg/1280px-Angel_Falls_Venezuela.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Angel_Falls_Venezuela.jpg/1280px-Angel_Falls_Venezuela.jpg"
    },
    "Cuba": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Havana_Cuba_old_town.jpg/1280px-Havana_Cuba_old_town.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Varadero_beach_Cuba.jpg/1280px-Varadero_beach_Cuba.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Havana_Cuba_old_town.jpg/1280px-Havana_Cuba_old_town.jpg"
    },
    "Jamaica": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Seven_Mile_Beach_Jamaica.jpg/1280px-Seven_Mile_Beach_Jamaica.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Blue_Lagoon_Jamaica.jpg/1280px-Blue_Lagoon_Jamaica.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Seven_Mile_Beach_Jamaica.jpg/1280px-Seven_Mile_Beach_Jamaica.jpg"
    },
    "Costa Rica": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Arenal_volcano_Costa_Rica.jpg/1280px-Arenal_volcano_Costa_Rica.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Arenal_volcano_Costa_Rica.jpg/1280px-Arenal_volcano_Costa_Rica.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Manuel_Antonio_National_Park_Costa_Rica.jpg/1280px-Manuel_Antonio_National_Park_Costa_Rica.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Arenal_volcano_Costa_Rica.jpg/1280px-Arenal_volcano_Costa_Rica.jpg"
    },
    "Guatemala": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Tikal_Guatemala.jpg/1280px-Tikal_Guatemala.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Lake_Atitlan_Guatemala.jpg/1280px-Lake_Atitlan_Guatemala.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/Tikal_Guatemala.jpg/1280px-Tikal_Guatemala.jpg"
    },
    "Panama": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Panama_Canal.jpg/1280px-Panama_Canal.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Bocas_del_Toro_Panama.jpg/1280px-Bocas_del_Toro_Panama.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Panama_Canal.jpg/1280px-Panama_Canal.jpg"
    },
    "Dominican Republic": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Punta_Cana_beach_Dominican_Republic.jpg/1280px-Punta_Cana_beach_Dominican_Republic.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Punta_Cana_beach_Dominican_Republic.jpg/1280px-Punta_Cana_beach_Dominican_Republic.jpg"
    },
    "Puerto Rico": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flamenco_Beach_Culebra_Puerto_Rico.jpg/1280px-Flamenco_Beach_Culebra_Puerto_Rico.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Old_San_Juan_Puerto_Rico.jpg/1280px-Old_San_Juan_Puerto_Rico.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flamenco_Beach_Culebra_Puerto_Rico.jpg/1280px-Flamenco_Beach_Culebra_Puerto_Rico.jpg"
    },
    "Uruguay": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Punta_del_Este_Uruguay.jpg/1280px-Punta_del_Este_Uruguay.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Colonia_del_Sacramento_Uruguay.jpg/1280px-Colonia_del_Sacramento_Uruguay.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Colonia_del_Sacramento_Uruguay.jpg/1280px-Colonia_del_Sacramento_Uruguay.jpg"
    },
    "Paraguay": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Iguazu_Falls_Paraguay.jpg/1280px-Iguazu_Falls_Paraguay.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Iguazu_Falls_Paraguay.jpg/1280px-Iguazu_Falls_Paraguay.jpg"
    },
    "Honduras": {
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Copan_ruins_Honduras.jpg/1280px-Copan_ruins_Honduras.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Roatan_Honduras.jpg/1280px-Roatan_Honduras.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Copan_ruins_Honduras.jpg/1280px-Copan_ruins_Honduras.jpg"
    },
    "Nicaragua": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Ometepe_Island_Nicaragua.jpg/1280px-Ometepe_Island_Nicaragua.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Granada_Nicaragua.jpg/1280px-Granada_Nicaragua.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Granada_Nicaragua.jpg/1280px-Granada_Nicaragua.jpg"
    },
    "El Salvador": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Santa_Ana_volcano_El_Salvador.jpg/1280px-Santa_Ana_volcano_El_Salvador.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/El_Tunco_beach_El_Salvador.jpg/1280px-El_Tunco_beach_El_Salvador.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Santa_Ana_volcano_El_Salvador.jpg/1280px-Santa_Ana_volcano_El_Salvador.jpg"
    },

    # OCEANIA
    "Australia": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Sydney_Australia_Opera_House.jpg/1280px-Sydney_Australia_Opera_House.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Sydney_Australia_Opera_House.jpg/1280px-Sydney_Australia_Opera_House.jpg",
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Whitehaven_Beach_Australia.jpg/1280px-Whitehaven_Beach_Australia.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Uluru-Kata_Tjuta_National_Park_Australia.jpg/1280px-Uluru-Kata_Tjuta_National_Park_Australia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Sydney_Australia_Opera_House.jpg/1280px-Sydney_Australia_Opera_House.jpg"
    },
    "New Zealand": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Milford_Sound_New_Zealand.jpg/1280px-Milford_Sound_New_Zealand.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Milford_Sound_New_Zealand.jpg/1280px-Milford_Sound_New_Zealand.jpg",
        "Heritage": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Rotorua_New_Zealand_geysers.jpg/1280px-Rotorua_New_Zealand_geysers.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Milford_Sound_New_Zealand.jpg/1280px-Milford_Sound_New_Zealand.jpg"
    },
    "Fiji": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Fiji_beach.jpg/1280px-Fiji_beach.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Fiji_beach.jpg/1280px-Fiji_beach.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Fiji_beach.jpg/1280px-Fiji_beach.jpg"
    },
    "Papua New Guinea": {
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Papua_New_Guinea_landscape.jpg/1280px-Papua_New_Guinea_landscape.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Papua_New_Guinea_landscape.jpg/1280px-Papua_New_Guinea_landscape.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Papua_New_Guinea_landscape.jpg/1280px-Papua_New_Guinea_landscape.jpg"
    },
    "Palau": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Palau_rock_islands.jpg/1280px-Palau_rock_islands.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Palau_rock_islands.jpg/1280px-Palau_rock_islands.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Palau_rock_islands.jpg/1280px-Palau_rock_islands.jpg"
    },
    "Vanuatu": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vanuatu_beach.jpg/1280px-Vanuatu_beach.jpg",
        "Adventure": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vanuatu_beach.jpg/1280px-Vanuatu_beach.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Vanuatu_beach.jpg/1280px-Vanuatu_beach.jpg"
    },
    "Solomon Islands": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Solomon_Islands.jpg/1280px-Solomon_Islands.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Solomon_Islands.jpg/1280px-Solomon_Islands.jpg"
    },
    "Samoa": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Samoa_beach.jpg/1280px-Samoa_beach.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Samoa_beach.jpg/1280px-Samoa_beach.jpg"
    },
    "Tonga": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tonga_beach.jpg/1280px-Tonga_beach.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Tonga_beach.jpg/1280px-Tonga_beach.jpg"
    },
    "French Polynesia": {
        "Beach": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Bora_Bora_French_Polynesia.jpg/1280px-Bora_Bora_French_Polynesia.jpg",
        "Nature": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Bora_Bora_French_Polynesia.jpg/1280px-Bora_Bora_French_Polynesia.jpg",
        "default": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Bora_Bora_French_Polynesia.jpg/1280px-Bora_Bora_French_Polynesia.jpg"
    },
}

# Type/broader type mapping
TYPE_BROADER_MAP = {
    "Beach": "Beach",
    "Nature": "Nature",
    "Heritage": "Heritage",
    "Cultural": "Heritage",
    "Religious": "Religious",
    "Adventure": "Adventure",
    "City": "Heritage",
    "Mountain": "Nature",
    "Wildlife": "Nature",
    "Luxury": "Beach",
}

# Fallback images by broader type for countries not found
FALLBACK_BY_TYPE = {
    "Beach": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1280&q=80",
    "Nature": "https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1280&q=80",
    "Heritage": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=1280&q=80",
    "Religious": "https://images.unsplash.com/photo-1548013146-72479768bada?w=1280&q=80",
    "Adventure": "https://images.unsplash.com/photo-1551632811-561732d1e306?w=1280&q=80",
    "default": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1280&q=80",
}

def get_image_for_destination(country, dest_type, broader_type):
    """Get appropriate image URL for a destination based on country and type."""
    # Map destination type to our categories
    type_key = TYPE_BROADER_MAP.get(dest_type, TYPE_BROADER_MAP.get(broader_type, "default"))
    
    # Look up country images
    if country in COUNTRY_IMAGES:
        country_imgs = COUNTRY_IMAGES[country]
        # Try specific type first
        if type_key in country_imgs:
            return country_imgs[type_key]
        # Try broader type
        if broader_type in country_imgs:
            return country_imgs[broader_type]
        # Use country default
        return country_imgs.get("default", FALLBACK_BY_TYPE.get(type_key, FALLBACK_BY_TYPE["default"]))
    
    # Country not found - use type fallback
    return FALLBACK_BY_TYPE.get(type_key, FALLBACK_BY_TYPE["default"])


def update_all_images():
    """Update all destination images in MongoDB."""
    destinations = list(db.destinations.find({}))
    total = len(destinations)
    print(f"Found {total} destinations to update.")
    
    updated = 0
    country_stats = {}
    
    for dest in destinations:
        country = dest.get('Country', '')
        dest_type = dest.get('Type', '')
        broader_type = dest.get('Broader_Type', '')
        dest_name = dest.get('Destination Name', dest.get('destination', 'Unknown'))
        
        new_image = get_image_for_destination(country, dest_type, broader_type)
        
        db.destinations.update_one(
            {'_id': dest['_id']},
            {'$set': {'image': new_image}}
        )
        
        updated += 1
        if country not in country_stats:
            country_stats[country] = 0
        country_stats[country] += 1
        
        if updated % 100 == 0:
            print(f"  Updated {updated}/{total}...")
    
    print(f"\nDone! Updated {updated} destination images.")
    print(f"\nCountries processed: {len(country_stats)}")
    
    # Show which countries weren't in our mapping
    missing_countries = [c for c in country_stats.keys() if c not in COUNTRY_IMAGES]
    if missing_countries:
        print(f"\nCountries using fallback images ({len(missing_countries)}):")
        for c in sorted(missing_countries):
            print(f"  - {c} ({country_stats[c]} destinations)")

if __name__ == '__main__':
    print("=" * 60)
    print("UPDATING ALL DESTINATION IMAGES")
    print("=" * 60)
    update_all_images()
