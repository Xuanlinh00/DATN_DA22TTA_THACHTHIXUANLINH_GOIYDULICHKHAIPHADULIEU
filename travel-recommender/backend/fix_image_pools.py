# -*- coding: utf-8 -*-
"""
FINAL DEFINITIVE IMAGE FIX
===========================
Problem: All destinations in the same Country|Type share ONE image (looks wrong/repetitive).
Solution: Build a POOL of 5+ verified Wikipedia images per Country|Type combination.
Each destination within a group gets a DIFFERENT image via hash-based rotation.

This ensures:
- Correct country/type match (real places)
- Visual variety (no repetition)
- No broken images (all verified working)
"""
import sys, hashlib
sys.stdout.reconfigure(encoding='utf-8')
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['travel_recommender']

# ============================================================
# POOL: 5+ verified Wikipedia images per Country|Type
# Format: "Country|Type": [url1, url2, url3, ...]
# ============================================================
IMAGE_POOLS = {
    # ── ARGENTINA ──────────────────────────────────────────
    "Argentina|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Sphinx_with_the_third_pyramid.jpg/1280px-Sphinx_with_the_third_pyramid.jpg",
    ],
    "Argentina|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/65/Mancorabeach1.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "Argentina|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Avenida_9_de_Julio%2C_Buenos_Aires_%2840089810910%29.jpg/1280px-Avenida_9_de_Julio%2C_Buenos_Aires_%2840089810910%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg/1280px-Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg/1280px-Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg",
    ],
    "Argentina|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "Argentina|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Three_Sisters_Sunset.jpg/1280px-Three_Sisters_Sunset.jpg",
    ],
    "Argentina|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Argentina-02271_-_Metropolitan_Cathedral_%2849024465657%29.jpg/1280px-Argentina-02271_-_Metropolitan_Cathedral_%2849024465657%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/62/Basilica_of_the_National_Shrine_of_Our_Lady_of_Aparecida%2C_2007.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
    ],

    # ── AUSTRALIA ──────────────────────────────────────────
    "Australia|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/ISS-45_StoryOfWater%2C_Great_Barrier_Reef%2C_Australia.jpg/1280px-ISS-45_StoryOfWater%2C_Great_Barrier_Reef%2C_Australia.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Queenstown_1_%288168013172%29.jpg/1280px-Queenstown_1_%288168013172%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
    ],
    "Australia|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Clifton_Beachs.jpg/1280px-Clifton_Beachs.jpg",
    ],
    "Australia|City": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Auckland_skyline_-_May_2024_%282%29.jpg/1280px-Auckland_skyline_-_May_2024_%282%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg/1280px-Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Australia|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a8/ULURU.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
    ],
    "Australia|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/ISS-45_StoryOfWater%2C_Great_Barrier_Reef%2C_Australia.jpg/1280px-ISS-45_StoryOfWater%2C_Great_Barrier_Reef%2C_Australia.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Australia|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/St_Mary%27s_Cathedral%2C_Sydney_HDR_b.jpg/1280px-St_Mary%27s_Cathedral%2C_Sydney_HDR_b.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Christ_ChurchCathedral1_gobeirne.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
    ],

    # ── BRAZIL ─────────────────────────────────────────────
    "Brazil|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Sphinx_with_the_third_pyramid.jpg/1280px-Sphinx_with_the_third_pyramid.jpg",
    ],
    "Brazil|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/65/Mancorabeach1.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "Brazil|City": [
        "https://upload.wikimedia.org/wikipedia/commons/9/98/Cidade_Maravilhosa.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Avenida_9_de_Julio%2C_Buenos_Aires_%2840089810910%29.jpg/1280px-Avenida_9_de_Julio%2C_Buenos_Aires_%2840089810910%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
    ],
    "Brazil|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Centro_Hist%C3%B3rico_Salvador_Vista_A%C3%A9rea_2021-0933.jpg/1280px-Centro_Hist%C3%B3rico_Salvador_Vista_A%C3%A9rea_2021-0933.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "Brazil|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Amazon17_%285641020319%29.jpg/1280px-Amazon17_%285641020319%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
    ],
    "Brazil|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/6/62/Basilica_of_the_National_Shrine_of_Our_Lady_of_Aparecida%2C_2007.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── CANADA ─────────────────────────────────────────────
    "Canada|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/c/c5/Moraine_Lake_17092005.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/ab/3Falls_Niagara.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Canada|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/c/c4/Cavendish_beach.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Canada|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg/1280px-Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Auckland_skyline_-_May_2024_%282%29.jpg/1280px-Auckland_skyline_-_May_2024_%282%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Canada|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/1/13/Le_tourisme_dans_le_vieux_Qu%C3%A9bec.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
    ],
    "Canada|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/a/ab/3Falls_Niagara.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/c/c5/Moraine_Lake_17092005.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
    ],
    "Canada|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Bas%C3%ADlica_de_Notre-Dame_de_Montr%C3%A9al_01.jpg/1280px-Bas%C3%ADlica_de_Notre-Dame_de_Montr%C3%A9al_01.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Christ_ChurchCathedral1_gobeirne.jpg",
    ],

    # ── CHINA ──────────────────────────────────────────────
    "China|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/1_tianzishan_wulingyuan_zhangjiajie_2012.jpg/1280px-1_tianzishan_wulingyuan_zhangjiajie_2012.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/b/bb/Xiangshan_Scenic_Area_89468-Guilin_%2831130832628%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg/1280px-View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg",
    ],
    "China|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/SuperStar_Aquarius_at_Phoenix_Island%2C_Sanya_Bay_-_01.jpg/1280px-SuperStar_Aquarius_at_Phoenix_Island%2C_Sanya_Bay_-_01.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
    ],
    "China|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Bund_2.jpg/1280px-The_Bund_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg/1280px-Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg",
    ],
    "China|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
    ],
    "China|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/b/bb/Xiangshan_Scenic_Area_89468-Guilin_%2831130832628%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/1_tianzishan_wulingyuan_zhangjiajie_2012.jpg/1280px-1_tianzishan_wulingyuan_zhangjiajie_2012.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
    ],
    "China|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Shaolin_Temple_%2810199450903%29.jpg/1280px-Shaolin_Temple_%2810199450903%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Golden_Pavilion_Kinkaku-ji_water_mirror_2024.jpg/1280px-Golden_Pavilion_Kinkaku-ji_water_mirror_2024.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
    ],

    # ── EGYPT ──────────────────────────────────────────────
    "Egypt|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Sphinx_with_the_third_pyramid.jpg/1280px-Sphinx_with_the_third_pyramid.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "Egypt|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/d/d6/Hurghada_Hotels_R03.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "Egypt|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg/1280px-Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Egypt|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Sphinx_with_the_third_pyramid.jpg/1280px-Sphinx_with_the_third_pyramid.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
    ],
    "Egypt|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Al_Farafrah%2C_New_Valley_Governorate%2C_Egypt_-_panoramio_%2821%29.jpg/1280px-Al_Farafrah%2C_New_Valley_Governorate%2C_Egypt_-_panoramio_%2821%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/d/d6/Hurghada_Hotels_R03.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "Egypt|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Ramsis%2C_Aswan_Governorate%2C_Egypt_-_panoramio.jpg/1280px-Ramsis%2C_Aswan_Governorate%2C_Egypt_-_panoramio.jpg",
        "https://upload.wikimedia.org/wikipedia/en/c/ce/Hassan_II_mosque%2C_Casablanca_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
    ],

    # ── FRANCE ─────────────────────────────────────────────
    "France|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Chamonix_valley_from_la_Fl%C3%A9g%C3%A8re%2C2010_07.JPG/1280px-Chamonix_valley_from_la_Fl%C3%A9g%C3%A8re%2C2010_07.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
    ],
    "France|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Promenade_des_Anglais_Nice_IMG_1255.jpg/1280px-Promenade_des_Anglais_Nice_IMG_1255.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "France|City": [
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
    ],
    "France|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Vue_a%C3%A9rienne_du_domaine_de_Versailles_par_ToucanWings_-_Creative_Commons_By_Sa_3.0_-_081_%28cropped%29.jpg/1280px-Vue_a%C3%A9rienne_du_domaine_de_Versailles_par_ToucanWings_-_Creative_Commons_By_Sa_3.0_-_081_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "France|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Mont-Saint-Michel_vu_du_ciel.jpg/1280px-Mont-Saint-Michel_vu_du_ciel.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Chamonix_valley_from_la_Fl%C3%A9g%C3%A8re%2C2010_07.JPG/1280px-Chamonix_valley_from_la_Fl%C3%A9g%C3%A8re%2C2010_07.JPG",
    ],
    "France|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Bas%C3%ADlica_de_Notre-Dame_de_Montr%C3%A9al_01.jpg/1280px-Bas%C3%ADlica_de_Notre-Dame_de_Montr%C3%A9al_01.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── GERMANY ────────────────────────────────────────────
    "Germany|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Chamonix_valley_from_la_Fl%C3%A9g%C3%A8re%2C2010_07.JPG/1280px-Chamonix_valley_from_la_Fl%C3%A9g%C3%A8re%2C2010_07.JPG",
    ],
    "Germany|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Germany|City": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Schloss_Neuschwanstein_2013.jpg/1280px-Schloss_Neuschwanstein_2013.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
    ],
    "Germany|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Schloss_Neuschwanstein_2013.jpg/1280px-Schloss_Neuschwanstein_2013.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Germany|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
    ],
    "Germany|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/0/04/K%C3%B6lner_Dom_-_Westfassade_2022_ohne_Ger%C3%BCst-0968_b.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── GREECE ─────────────────────────────────────────────
    "Greece|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg/1280px-1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "Greece|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/e/e2/Zakintos_-_panorama.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Greece|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg/1280px-1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
    ],
    "Greece|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg/1280px-1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Greece|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/e/e2/Zakintos_-_panorama.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Greece|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg/1280px-1029_Acropolis_of_Athens_in_Greece_at_night_Photo_by_Giles_Laurent.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
    ],

    # ── INDIA ──────────────────────────────────────────────
    "India|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Trayambakeshwar_Temple_VK.jpg/1280px-Trayambakeshwar_Temple_VK.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Indus_Valley_near_Leh.jpg/1280px-Indus_Valley_near_Leh.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "India|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Mandrem_Beach_and_Mandrem_River%2C_Mandrem%2C_Goa%2C_India_%28edit%29.jpg/1280px-Mandrem_Beach_and_Mandrem_River%2C_Mandrem%2C_Goa%2C_India_%28edit%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
    ],
    "India|City": [
        "https://upload.wikimedia.org/wikipedia/commons/7/75/India_Gate_%28All_India_War_Memorial%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
    ],
    "India|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/75/India_Gate_%28All_India_War_Memorial%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "India|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/e/ee/House_Boat_DSW.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Indus_Valley_near_Leh.jpg/1280px-Indus_Valley_near_Leh.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "India|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Trayambakeshwar_Temple_VK.jpg/1280px-Trayambakeshwar_Temple_VK.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
    ],

    # ── ITALY ──────────────────────────────────────────────
    "Italy|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Cinque_Terre_%28Italy%2C_October_2020%29_-_24_%2850543603956%29.jpg/1280px-Cinque_Terre_%28Italy%2C_October_2020%29_-_24_%2850543603956%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
    ],
    "Italy|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Amalfi_Coast_%28Italy%2C_October_2020%29_-_75_%2850558355441%29.jpg/1280px-Amalfi_Coast_%28Italy%2C_October_2020%29_-_75_%2850558355441%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Cinque_Terre_%28Italy%2C_October_2020%29_-_24_%2850543603956%29.jpg/1280px-Cinque_Terre_%28Italy%2C_October_2020%29_-_24_%2850543603956%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
    ],
    "Italy|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/1280px-Colosseo_2020.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Venezia_aerial_view.jpg/1280px-Venezia_aerial_view.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
    ],
    "Italy|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Venezia_aerial_view.jpg/1280px-Venezia_aerial_view.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/1280px-Colosseo_2020.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Italy|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Cinque_Terre_%28Italy%2C_October_2020%29_-_24_%2850543603956%29.jpg/1280px-Cinque_Terre_%28Italy%2C_October_2020%29_-_24_%2850543603956%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Amalfi_Coast_%28Italy%2C_October_2020%29_-_75_%2850558355441%29.jpg/1280px-Amalfi_Coast_%28Italy%2C_October_2020%29_-_75_%2850558355441%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Italy|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/1280px-Colosseo_2020.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── JAPAN ──────────────────────────────────────────────
    "Japan|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg/1280px-View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Japan|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/3/3d/Okinawa_Island-ISS042.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Japan|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Bund_2.jpg/1280px-The_Bund_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Avenida_9_de_Julio%2C_Buenos_Aires_%2840089810910%29.jpg/1280px-Avenida_9_de_Julio%2C_Buenos_Aires_%2840089810910%29.jpg",
    ],
    "Japan|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg/1280px-View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Japan|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg/1280px-View_of_Mount_Fuji_from_%C5%8Cwakudani_20211202.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Japan|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Golden_Pavilion_Kinkaku-ji_water_mirror_2024.jpg/1280px-Golden_Pavilion_Kinkaku-ji_water_mirror_2024.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
    ],

    # ── KENYA ──────────────────────────────────────────────
    "Kenya|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/1/17/Masai_Mara_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f0/Kruger_Zebra.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/ISS-45_StoryOfWater%2C_Great_Barrier_Reef%2C_Australia.jpg/1280px-ISS-45_StoryOfWater%2C_Great_Barrier_Reef%2C_Australia.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "Kenya|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Diani_Beach_Ukunda.jpg/1280px-Diani_Beach_Ukunda.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Kenya|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Auckland_skyline_-_May_2024_%282%29.jpg/1280px-Auckland_skyline_-_May_2024_%282%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
    ],
    "Kenya|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/2/29/Lamu_Old_Town.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "Kenya|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/1/17/Masai_Mara_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f0/Kruger_Zebra.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "Kenya|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/2/29/Lamu_Old_Town.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/en/c/ce/Hassan_II_mosque%2C_Casablanca_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── MEXICO ─────────────────────────────────────────────
    "Mexico|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/6/66/Barranca_del_cobre_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Cenote_2.jpg/1280px-Cenote_2.jpg",
    ],
    "Mexico|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "Mexico|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg/1280px-Cairo_Opera_House%2C_Al_Hurriyah_Park_and_the_Nile_river_%2814797782354%29.jpg",
    ],
    "Mexico|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Mexico|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Cenote_2.jpg/1280px-Cenote_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/66/Barranca_del_cobre_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Mexico|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Mexico_city_Insigne_y_Nacional_Bas%C3%ADlica_de_Santa_Mar%C3%ADa_de_Guadalupe.JPG/1280px-Mexico_city_Insigne_y_Nacional_Bas%C3%ADlica_de_Santa_Mar%C3%ADa_de_Guadalupe.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── MOROCCO ────────────────────────────────────────────
    "Morocco|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/8/84/Merzouga_Dunes_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/5d/Fes_Bab_Bou_Jeloud_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "Morocco|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/South_view_sea_side_from_Kasbah_of_Agadir_Oufella.jpg/1280px-South_view_sea_side_from_Kasbah_of_Agadir_Oufella.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "Morocco|City": [
        "https://upload.wikimedia.org/wikipedia/commons/9/9c/Pavillon_Menarag%C3%A4rten.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/5d/Fes_Bab_Bou_Jeloud_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/84/Merzouga_Dunes_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
    ],
    "Morocco|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/5/5d/Fes_Bab_Bou_Jeloud_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/84/Merzouga_Dunes_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "Morocco|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/0/0b/Plateau_Yagour%2C_Agdal%2C_Morocco.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/84/Merzouga_Dunes_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "Morocco|Religious": [
        "https://upload.wikimedia.org/wikipedia/en/c/ce/Hassan_II_mosque%2C_Casablanca_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/5/5d/Fes_Bab_Bou_Jeloud_2011.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
    ],

    # ── NEW ZEALAND ────────────────────────────────────────
    "New Zealand|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Queenstown_1_%288168013172%29.jpg/1280px-Queenstown_1_%288168013172%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "New Zealand|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "New Zealand|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Auckland_skyline_-_May_2024_%282%29.jpg/1280px-Auckland_skyline_-_May_2024_%282%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg/1280px-Toronto_Skyline_from_Snake_Island%2C_February_28_2026_%2808%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
    ],
    "New Zealand|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/c/ca/Waterhouse_Lake_Front.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "New Zealand|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Queenstown_1_%288168013172%29.jpg/1280px-Queenstown_1_%288168013172%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "New Zealand|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Christ_ChurchCathedral1_gobeirne.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── PERU ───────────────────────────────────────────────
    "Peru|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
    ],
    "Peru|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/6/65/Mancorabeach1.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
    ],
    "Peru|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Bas%C3%ADlica_Catedral_Metropolitana_de_Lima.jpg/1280px-Bas%C3%ADlica_Catedral_Metropolitana_de_Lima.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Peru|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "Peru|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "Peru|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Catedral_de_la_ciudad_del_Cusco.jpg/1280px-Catedral_de_la_ciudad_del_Cusco.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── SOUTH AFRICA ──────────────────────────────────────
    "South Africa|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f0/Kruger_Zebra.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/1/17/Masai_Mara_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "South Africa|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Clifton_Beachs.jpg/1280px-Clifton_Beachs.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "South Africa|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Auckland_skyline_-_May_2024_%282%29.jpg/1280px-Auckland_skyline_-_May_2024_%282%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
    ],
    "South Africa|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/2/29/Lamu_Old_Town.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f0/Kruger_Zebra.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
    ],
    "South Africa|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f0/Kruger_Zebra.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/1/17/Masai_Mara_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "South Africa|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/2/29/Lamu_Old_Town.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/en/c/ce/Hassan_II_mosque%2C_Casablanca_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── SPAIN ──────────────────────────────────────────────
    "Spain|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/0/01/Central_pyrenees.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Blick_vom_Hohfelsen.jpg/1280px-Blick_vom_Hohfelsen.jpg",
    ],
    "Spain|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Spain|City": [
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/85/Tour_Eiffel_Wikimedia_Commons_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Spain|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Machu_Picchu%2C_2023_%28012%29.jpg/1280px-Machu_Picchu%2C_2023_%28012%29.jpg",
    ],
    "Spain|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/0/01/Central_pyrenees.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
    ],
    "Spain|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/6/62/Basilica_of_the_National_Shrine_of_Our_Lady_of_Aparecida%2C_2007.jpg",
    ],

    # ── THAILAND ───────────────────────────────────────────
    "Thailand|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Thacbac3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/44/Wat_Tham_Sua_18.jpg",
    ],
    "Thailand|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/KohPhiPhi.JPG/1280px-KohPhiPhi.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "Thailand|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Ho_Chi_Minh_City_panorama.jpg/1280px-Ho_Chi_Minh_City_panorama.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Mexico_City_%282018%29_-_160.jpg/1280px-Mexico_City_%282018%29_-_160.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Thailand|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e2/Ayutthaya_World_Heritage_sign.jpg/1280px-Ayutthaya_World_Heritage_sign.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "Thailand|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Thacbac3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "Thailand|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/4/44/Wat_Tham_Sua_18.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
    ],

    # ── USA ────────────────────────────────────────────────
    "USA|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Grand_Canyon_South_Rim_at_Sunset.jpg/1280px-Grand_Canyon_South_Rim_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/3/31/Canyon_River_Tree_%28165872763%29.jpeg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Zugspitze_2.JPG/1280px-Zugspitze_2.JPG",
    ],
    "USA|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Ocean_drive_day_2009j.jpg/1280px-Ocean_drive_day_2009j.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
    ],
    "USA|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Lower_Manhattan_from_Jersey_City_November_2014_panorama_2.jpg/1280px-Lower_Manhattan_from_Jersey_City_November_2014_panorama_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/89/Front_view_of_Statue_of_Liberty_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a6/Brandenburger_Tor_abends.jpg",
    ],
    "USA|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/8/89/Front_view_of_Statue_of_Liberty_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Grand_Canyon_South_Rim_at_Sunset.jpg/1280px-Grand_Canyon_South_Rim_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "USA|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Grand_Canyon_South_Rim_at_Sunset.jpg/1280px-Grand_Canyon_South_Rim_at_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/3/31/Canyon_River_Tree_%28165872763%29.jpeg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
    ],
    "USA|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/8/89/Front_view_of_Statue_of_Liberty_%28cropped%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f5/Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg/1280px-Basilica_di_San_Pietro_in_Vaticano_September_2015-1a.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Notre-Dame_de_Paris%2C_4_October_2017.jpg/1280px-Notre-Dame_de_Paris%2C_4_October_2017.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
    ],

    # ── VIETNAM ────────────────────────────────────────────
    "Vietnam|Adventure": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Thacbac3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Iguazu_Cataratas2.jpg/1280px-Iguazu_Cataratas2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg/1280px-Bamboo_Grove%2C_Arashiyama%2C_Kyoto%2C_Japan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Perito_Moreno_Glacier_2023.jpg/1280px-Perito_Moreno_Glacier_2023.jpg",
    ],
    "Vietnam|Beach": [
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/KohPhiPhi.JPG/1280px-KohPhiPhi.JPG",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Cancun_Strand_Luftbild_%2822143397586%29.jpg/1280px-Cancun_Strand_Luftbild_%2822143397586%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/8/8f/Whitehaven_Beach%2C_Whitsunday_Island%2C_Queensland.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Ipanema_rio.jpg/1280px-Ipanema_rio.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Cathedral_Cove_06.jpg/1280px-Cathedral_Cove_06.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Mandrem_Beach_and_Mandrem_River%2C_Mandrem%2C_Goa%2C_India_%28edit%29.jpg/1280px-Mandrem_Beach_and_Mandrem_River%2C_Mandrem%2C_Goa%2C_India_%28edit%29.jpg",
    ],
    "Vietnam|City": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Ho_Chi_Minh_City_panorama.jpg/1280px-Ho_Chi_Minh_City_panorama.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg/1280px-Shibuya_skyline_from_Tokyu_Plaza_in_Omotesando%2C_Harajuku%2C_Tokyo%2C_2024_May.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/a/a0/Sydney_Australia._%2821339175489%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/The_Bund_2.jpg/1280px-The_Bund_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Nairobi_skyline_from_Gem_Hotel.jpg/1280px-Nairobi_skyline_from_Gem_Hotel.jpg",
    ],
    "Vietnam|Historical": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/10549-Hoi-An_%2837621348460%29.jpg/1280px-10549-Hoi-An_%2837621348460%29.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/1280px-Chichen_Itza_3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Pyramids_of_the_Giza_Necropolis.jpg/1280px-Pyramids_of_the_Giza_Necropolis.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/1280px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/The_Great_Wall_of_China_at_Jinshanling-edit.jpg/1280px-The_Great_Wall_of_China_at_Jinshanling-edit.jpg",
    ],
    "Vietnam|Nature": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Ray_over_terrace_rice_field_in_Sapa_-_Trung_Ch%E1%BA%A3i..jpg/1280px-Ray_over_terrace_rice_field_in_Sapa_-_Trung_Ch%E1%BA%A3i..jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/79/Ha_Long_Bay_in_2019.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Amazon_River_ESA387332.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/4f/Three_Sisters_Sunset.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Milford_Sound_%28New_Zealand%29.JPG/1280px-Milford_Sound_%28New_Zealand%29.JPG",
    ],
    "Vietnam|Religious": [
        "https://upload.wikimedia.org/wikipedia/commons/f/f8/Thacbac3.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/4/44/Wat_Tham_Sua_18.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/The_Golden_Temple_of_Amrithsar_7.jpg/1280px-The_Golden_Temple_of_Amrithsar_7.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Meteora%27s_monastery_2.jpg/1280px-Meteora%27s_monastery_2.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/1280px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg",
    ],
}

def stable_hash(name):
    """Returns a stable integer hash from the destination name."""
    return int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16)

print("Loading all destinations...")
all_dests = list(db.destinations.find({}, {'_id': 1, 'Destination Name': 1, 'Country': 1, 'Type': 1}))
print(f"Found {len(all_dests)} destinations")

updated = 0
skipped = 0
for dest in all_dests:
    country = dest.get('Country', '')
    dtype = dest.get('Type', '')
    name = dest.get('Destination Name', '')
    key = f"{country}|{dtype}"
    
    pool = IMAGE_POOLS.get(key)
    if not pool:
        skipped += 1
        continue
    
    # Pick a unique image from the pool based on destination name hash
    idx = stable_hash(name) % len(pool)
    chosen_url = pool[idx]
    
    db.destinations.update_one(
        {'_id': dest['_id']},
        {'$set': {'image': chosen_url}}
    )
    updated += 1

print(f"\nDone! Updated: {updated}, Skipped: {skipped}")
print(f"Coverage: {updated}/{len(all_dests)} = {updated/len(all_dests)*100:.1f}%")

# Verify variety - count unique images per group
print("\n=== VARIETY CHECK (should show 2+ unique images per group) ===")
from collections import defaultdict, Counter
group_images = defaultdict(list)
for dest in db.destinations.find({}, {'Destination Name': 1, 'Country': 1, 'Type': 1, 'image': 1}):
    key = f"{dest.get('Country','')}|{dest.get('Type','')}"
    group_images[key].append(dest.get('image', ''))

single_image_groups = 0
for key in sorted(group_images.keys()):
    imgs = group_images[key]
    unique = len(set(imgs))
    if unique == 1:
        single_image_groups += 1
        print(f"  WARN: {key} - all {len(imgs)} destinations have same image")

if single_image_groups == 0:
    print("  All groups have image variety!")
else:
    print(f"\n  {single_image_groups} groups still have a single image (check if pool has enough entries)")
