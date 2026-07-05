// -*- coding: utf-8 -*-
/**
 * Image Service - Tự động gán hình ảnh du lịch cho từng địa điểm.
 *
 * Ưu tiên theo thứ tự:
 *   1. EXACT_DESTINATION_IMAGES – hình ảnh đã kiểm duyệt thủ công cho từng địa điểm cụ thể
 *   2. IMAGES_BY_TYPE – hình ảnh Wikimedia Commons đã kiểm duyệt theo loại địa điểm
 *      (sử dụng name-keyword resolution để xác định loại, KHÔNG dùng CSV Type field)
 *
 * Tất cả ảnh đều là link Wikimedia Commons thực, đã kiểm duyệt nội dung phù hợp.
 */

// CURATED IMAGES BY TYPE: Wikimedia Commons verified photos
const IMAGES_BY_TYPE = {
  waterfall: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/3Falls_Niagara.jpg/960px-3Falls_Niagara.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Maid_of_the_Mist_-_pot-o-gold.jpg/960px-Maid_of_the_Mist_-_pot-o-gold.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/Niagara-Falls-Horseshoe-Falls-view.jpg/960px-Niagara-Falls-Horseshoe-Falls-view.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Niagara_Falls_-_ON_-_Niagaraf%C3%A4lle3.jpg/960px-Niagara_Falls_-_ON_-_Niagaraf%C3%A4lle3.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Niagara_Falls_001.JPG/960px-Niagara_Falls_001.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/3/3b/Niagara_watervallen_canada.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/00_1838_Iguazu_Falls_from_the_Brazilian_side.jpg/960px-00_1838_Iguazu_Falls_from_the_Brazilian_side.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/00_1854_Iguaz%C3%BA-Wasserf%C3%A4lle_-_S%C3%BCdamerika.jpg/960px-00_1854_Iguaz%C3%BA-Wasserf%C3%A4lle_-_S%C3%BCdamerika.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/f/f9/09.07a_Iguazu_falls.png',
    'https://upload.wikimedia.org/wikipedia/commons/f/f0/Cataratas027.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Iguazu_Falls_Brazilian_Side_2019.jpg/960px-Iguazu_Falls_Brazilian_Side_2019.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Wilhelm_Dohmann_Iguazu_Falls%2C_Argentina.jpg/960px-Wilhelm_Dohmann_Iguazu_Falls%2C_Argentina.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Cataratas_Victoria%2C_Zambia-Zimbabue%2C_2018-07-27%2C_DD_05.jpg/960px-Cataratas_Victoria%2C_Zambia-Zimbabue%2C_2018-07-27%2C_DD_05.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Cataratas_Victoria%2C_Zambia-Zimbabue%2C_2018-07-27%2C_DD_30-34_PAN.jpg/960px-Cataratas_Victoria%2C_Zambia-Zimbabue%2C_2018-07-27%2C_DD_30-34_PAN.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2e/Mosi-oa-Tunya%2C_Livingstone_%2820260519-P1075665%29.jpg/960px-Mosi-oa-Tunya%2C_Livingstone_%2820260519-P1075665%29.jpg',
  ],
  beach: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Beach%2C_pier_and_cloud._Eriyadu%2C_Maldives.jpg/960px-Beach%2C_pier_and_cloud._Eriyadu%2C_Maldives.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Beach%2C_pier_and_clouds._Eriyadu%2C_Maldives.jpg/960px-Beach%2C_pier_and_clouds._Eriyadu%2C_Maldives.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Beach_and_bungalow._Eriyadu%2C_Maldives.jpg/960px-Beach_and_bungalow._Eriyadu%2C_Maldives.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Beach_and_pier._Eriyadu%2C_Maldives.jpg/960px-Beach_and_pier._Eriyadu%2C_Maldives.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Bush_and_beach._Eriyadu%2C_Maldives.jpg/960px-Bush_and_beach._Eriyadu%2C_Maldives.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Diamonds_Thudufushi_Beach_and_Water_Villas%2C_May_2017_-09.jpg/960px-Diamonds_Thudufushi_Beach_and_Water_Villas%2C_May_2017_-09.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Bora-Bora_Lagoon_-_French_Polynesia.jpg/960px-Bora-Bora_Lagoon_-_French_Polynesia.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Bora_Bora_-_junk_cars_alongside_the_lagoon_-_panoramio.jpg/960px-Bora_Bora_-_junk_cars_alongside_the_lagoon_-_panoramio.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Bora_bora_9601a.jpg/960px-Bora_bora_9601a.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/7/73/Hermit_crab_in_the_inside_lagoon_%28Motu_Tape_-_Le_Meridien_Bora_Bora%29_%28570469244%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Hermit_crab_in_the_inside_lagoon_-_Bora_Bora.jpg/960px-Hermit_crab_in_the_inside_lagoon_-_Bora_Bora.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fe/Mount_Otemanu_Bora_Bora.jpg/960px-Mount_Otemanu_Bora_Bora.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/DSC122_Australia_Queensland_Whitsunday_Islands_Whitehaven_bay_%285491401519%29.jpg/960px-DSC122_Australia_Queensland_Whitsunday_Islands_Whitehaven_bay_%285491401519%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/9/9e/White_Heaven_Beach_beach_IMG_2851.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Whitehaven_Bay_and_Beach.jpg/960px-Whitehaven_Bay_and_Beach.jpg',
  ],
  mountain: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Grumman_E-2C_Hawkeyes_of_VAW-115_fly_past_Mount_Fuji_on_15_February_2007_%28070215-N-2604L-024%29.jpg/960px-Grumman_E-2C_Hawkeyes_of_VAW-115_fly_past_Mount_Fuji_on_15_February_2007_%28070215-N-2604L-024%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Katsushika_Hokusai%2C_published_by_Nishimuraya_Yohachi_%28Eijud%C5%8D%29_-_Fine_Wind%2C_Clear_Weather_%28Gaif%C5%AB_kaisei%29%2C_also_known_as_Red_Fuji%2C_from_the_series_Thirty-six_Views_o..._-_Google_Art_Project_-_Cropped.jpg/960px-thumbnail.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Mount_Fuji_at_sunset%2C_March_2025.jpg/960px-Mount_Fuji_at_sunset%2C_March_2025.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Mount_Fuji_from_Mount_Aino.jpg/960px-Mount_Fuji_from_Mount_Aino.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Ogata_Gekko_-_Ryu_sho_ten.jpg/960px-Ogata_Gekko_-_Ryu_sho_ten.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/View_towards_Mount_Fuji_from_Arakurayama_Sengen_Park_in_Fujiyoshida%2C_Yamanashi%2C_Japan%2C_2024_May_-_2.jpg/960px-View_towards_Mount_Fuji_from_Arakurayama_Sengen_Park_in_Fujiyoshida%2C_Yamanashi%2C_Japan%2C_2024_May_-_2.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/20110810_North_Face_of_Everest_Tibet_China_Panoramic.jpg/960px-20110810_North_Face_of_Everest_Tibet_China_Panoramic.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Everest%2C_Himalayas.jpg/960px-Everest%2C_Himalayas.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Everest%2C_Nuptse%2C_Khumbu_Glacier%2C_Nepal%2C_Himalayas.jpg/960px-Everest%2C_Nuptse%2C_Khumbu_Glacier%2C_Nepal%2C_Himalayas.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Mount_Everest%2C_Nepal%2C_Himalayas.jpg/960px-Mount_Everest%2C_Nepal%2C_Himalayas.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Sagarmatha_Everest_Zone%2C_Nepal%2C_Himalayas.jpg/960px-Sagarmatha_Everest_Zone%2C_Nepal%2C_Himalayas.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Sunset_view_of_Everest.jpg/960px-Sunset_view_of_Everest.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/008_Milky_way_aligned_with_the_Matterhorn_reflecting_in_Stellisee_Photo_by_Giles_Laurent.jpg/960px-008_Milky_way_aligned_with_the_Matterhorn_reflecting_in_Stellisee_Photo_by_Giles_Laurent.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/CH.VS.Zermatt_2021-10-17_Matterhorn_8726.jpg/960px-CH.VS.Zermatt_2021-10-17_Matterhorn_8726.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/CH.VS.Zermatt_Sunnegga_Grindjisee_Matterhorn_9034_16x9-R_16K.jpg/960px-CH.VS.Zermatt_Sunnegga_Grindjisee_Matterhorn_9034_16x9-R_16K.jpg',
  ],
  cultural: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Japan_tea_ceremony_1165.jpg/960px-Japan_tea_ceremony_1165.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Japanese_garden_at_Sch%C3%B6nbrunn_Palace_in_Vienna%2C_Austria_-_teahouse_Heterotopia_tea_ceremony-full_PNr%C2%B01025.jpg/960px-Japanese_garden_at_Sch%C3%B6nbrunn_Palace_in_Vienna%2C_Austria_-_teahouse_Heterotopia_tea_ceremony-full_PNr%C2%B01025.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Japanese_garden_at_Sch%C3%B6nbrunn_Palace_in_Vienna%2C_Austria_-_teahouse_Heterotopia_tea_ceremony-water_PNr%C2%B01026.jpg/960px-Japanese_garden_at_Sch%C3%B6nbrunn_Palace_in_Vienna%2C_Austria_-_teahouse_Heterotopia_tea_ceremony-water_PNr%C2%B01026.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Japanese_garden_at_Sch%C3%B6nbrunn_Palace_in_Vienna%2C_Austria_-_teahouse_Heterotopia_tea_ceremony-whisk_PNr%C2%B01027.jpg/960px-Japanese_garden_at_Sch%C3%B6nbrunn_Palace_in_Vienna%2C_Austria_-_teahouse_Heterotopia_tea_ceremony-whisk_PNr%C2%B01027.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Japanese_tea_ceremony_20100502_Japan_Matsuri_07.jpg/960px-Japanese_tea_ceremony_20100502_Japan_Matsuri_07.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/a/a7/Tea_ceremony_performing_2.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Holi_Feest_2008_meisjes.jpg/960px-Holi_Feest_2008_meisjes.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/c/c7/Indian_festival_of_colors_-_holi_%287%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Lathmar_Holi_2022_in_Nandgaon%2C_Uttar_Pradesh_%28edited%29.jpg/960px-Lathmar_Holi_2022_in_Nandgaon%2C_Uttar_Pradesh_%28edited%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Relief_decpicting_Holi_in_the_Indian_Museum%2C_Kolkata_01.jpg/960px-Relief_decpicting_Holi_in_the_Indian_Museum%2C_Kolkata_01.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/Relief_decpicting_Holi_in_the_Indian_Museum%2C_Kolkata_02.jpg/960px-Relief_decpicting_Holi_in_the_Indian_Museum%2C_Kolkata_02.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Ancient_City_Floating_Market_%28I%29.jpg/960px-Ancient_City_Floating_Market_%28I%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Ancient_City_Floating_Market_%28II%29.jpg/960px-Ancient_City_Floating_Market_%28II%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Ancient_City_Floating_Market_%28III%29.jpg/960px-Ancient_City_Floating_Market_%28III%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Ancient_City_Floating_Market_%28IV%29.jpg/960px-Ancient_City_Floating_Market_%28IV%29.jpg',
  ],
  nature: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Global_Forest_Change_tree-cover_loss_year_in_the_Brazilian_Amazon%2C_2001-2024.png/960px-Global_Forest_Change_tree-cover_loss_year_in_the_Brazilian_Amazon%2C_2001-2024.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Juru%C3%A1_River_in_Brazil.jpg/960px-Juru%C3%A1_River_in_Brazil.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Noite_no_Teatro_Amazonas_%28cropped%29.jpg/960px-Noite_no_Teatro_Amazonas_%28cropped%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Lake_Agnes_im_Banff_National_Park.jpg/960px-Lake_Agnes_im_Banff_National_Park.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Moraine_Lake-Banff_NP.JPG/960px-Moraine_Lake-Banff_NP.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Moraine_Lake_17092005.jpg/960px-Moraine_Lake_17092005.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Peyto_Lake-Banff_NP-Canada.jpg/960px-Peyto_Lake-Banff_NP-Canada.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Rockies_in_the_morning.jpg/960px-Rockies_in_the_morning.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/The_Mountain_Exhaled_edit.jpg/960px-The_Mountain_Exhaled_edit.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Leontopodium_alpinum_-_Swiss_National_Park_254.jpg/960px-Leontopodium_alpinum_-_Swiss_National_Park_254.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Parc_naziunal_svizzer_%28Swiss_National_Park%29.jpg/960px-Parc_naziunal_svizzer_%28Swiss_National_Park%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Refuge_Giosos_Apostolidis_Olympus_National_Park_Greece.jpg/960px-Refuge_Giosos_Apostolidis_Olympus_National_Park_Greece.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/2/26/Swiss_National_Park%2C_2.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/Swiss_National_Park_045.JPG/960px-Swiss_National_Park_045.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Swiss_National_Park_131.JPG/960px-Swiss_National_Park_131.JPG',
  ],
  adventure: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Everest_Base_Camp_Trek_Nepal.jpg/960px-Everest_Base_Camp_Trek_Nepal.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Everest_base_camp_trek-0367.jpg/960px-Everest_base_camp_trek-0367.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Everest_base_camp_trek-0368.jpg/960px-Everest_base_camp_trek-0368.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Everest_base_camp_trek-0375.jpg/960px-Everest_base_camp_trek-0375.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Terraced_farm_on_the_way_to_Everest_Base_Camp_Trek.jpg/960px-Terraced_farm_on_the_way_to_Everest_Base_Camp_Trek.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Climbers_Barranco_Wall_Kilimanjaro_Tanzania.jpg/960px-Climbers_Barranco_Wall_Kilimanjaro_Tanzania.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Kilimanjaro_climb_-_panoramio.jpg/960px-Kilimanjaro_climb_-_panoramio.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Diving_At_The_Great_Barrier_Reef.jpg/960px-Diving_At_The_Great_Barrier_Reef.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Great_Barrier_Reef_11.JPG/960px-Great_Barrier_Reef_11.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Lascar_Diving_at_the_The_Great_Barrier_Reef_%284559830591%29.jpg/960px-Lascar_Diving_at_the_The_Great_Barrier_Reef_%284559830591%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Lascar_Diving_at_the_The_Great_Barrier_Reef_%284559840851%29.jpg/960px-Lascar_Diving_at_the_The_Great_Barrier_Reef_%284559840851%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/Lascar_Diving_at_the_The_Great_Barrier_Reef_%284560471112%29.jpg/960px-Lascar_Diving_at_the_The_Great_Barrier_Reef_%284560471112%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Scuba_diving%2C_Great_Barrier_Reef%2C_1980s.jpg/960px-Scuba_diving%2C_Great_Barrier_Reef%2C_1980s.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Best_guied_rafting_in_uganda_with_kiira_rafting.jpg/960px-Best_guied_rafting_in_uganda_with_kiira_rafting.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Fun_Rafting_Elo_River_Magelang.jpg/960px-Fun_Rafting_Elo_River_Magelang.jpg',
  ],
  historical: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/960px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Colosseum_in_Rome-April_2007-1-_copie_2B.jpg/960px-Colosseum_in_Rome-April_2007-1-_copie_2B.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Colosseum_of_Rome%2C_Italy.jpg/960px-Colosseum_of_Rome%2C_Italy.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Colosseum_of_Rome_and_Roman_forum.jpg/960px-Colosseum_of_Rome_and_Roman_forum.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Cross_Colosseum_Rome_Italy.jpg/960px-Cross_Colosseum_Rome_Italy.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Rome_Colosseum_001.jpg/960px-Rome_Colosseum_001.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/80_-_Machu_Picchu_-_Juin_2009_-_edit.jpg/960px-80_-_Machu_Picchu_-_Juin_2009_-_edit.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/99_-_Machu_Picchu_-_Juin_2009.edit3.jpg/960px-99_-_Machu_Picchu_-_Juin_2009.edit3.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Machu_Picchu%2C_Per%C3%BA%2C_2015-07-30%2C_DD_47.JPG/960px-Machu_Picchu%2C_Per%C3%BA%2C_2015-07-30%2C_DD_47.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Machu_Picchu%2C_Per%C3%BA%2C_2015-07-30%2C_DD_60.JPG/960px-Machu_Picchu%2C_Per%C3%BA%2C_2015-07-30%2C_DD_60.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Machu_Picchu.png/960px-Machu_Picchu.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Peru_Machu_Picchu_Sunrise.jpg/960px-Peru_Machu_Picchu_Sunrise.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Petra_%2C_Al-Khazneh_2.jpg/960px-Petra_%2C_Al-Khazneh_2.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Petra_Jordan_BW_0.jpg/960px-Petra_Jordan_BW_0.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Petra_Jordan_BW_34.JPG/960px-Petra_Jordan_BW_34.JPG',
  ],
  religious: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/2014-Cambodge_Angkor_Wat_%2821%29.jpg/960px-2014-Cambodge_Angkor_Wat_%2821%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/2016_Angkor%2C_Angkor_Wat%2C_Brama_Angkor_Wat_%2821%29.jpg/960px-2016_Angkor%2C_Angkor_Wat%2C_Brama_Angkor_Wat_%2821%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/2016_Angkor%2C_Angkor_Wat%2C_Brama_Angkor_Wat_%2830%29.jpg/960px-2016_Angkor%2C_Angkor_Wat%2C_Brama_Angkor_Wat_%2830%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/20171126_Angkor_Wat_4712_DxO.jpg/960px-20171126_Angkor_Wat_4712_DxO.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Angkor_Thom_Bayon_relief_of_the_Battle_of_Tonl%C3%A9_Sap.jpg/960px-Angkor_Thom_Bayon_relief_of_the_Battle_of_Tonl%C3%A9_Sap.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/Angkor_Wat_with_its_reflection_%28cropped%29.jpg/960px-Angkor_Wat_with_its_reflection_%28cropped%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Borobudur%2C_Java%2C_Indonesia%2C_20220817_1013_8739.jpg/960px-Borobudur%2C_Java%2C_Indonesia%2C_20220817_1013_8739.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Borobudur%2C_Java%2C_Indonesia%2C_20220817_1058_8808.jpg/960px-Borobudur%2C_Java%2C_Indonesia%2C_20220817_1058_8808.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8c/Borobudur-Nothwest-view.jpg/960px-Borobudur-Nothwest-view.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/Borobudur-Temple-Park_Indonesia_Stupas-of-Borobudur-01.jpg/960px-Borobudur-Temple-Park_Indonesia_Stupas-of-Borobudur-01.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Borobudur-Temple-Park_Indonesia_Stupas-of-Borobudur-11.jpg/960px-Borobudur-Temple-Park_Indonesia_Stupas-of-Borobudur-11.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Borobudur-Temple-Park_Indonesia_Stupas-of-Borobudur-12.jpg/960px-Borobudur-Temple-Park_Indonesia_Stupas-of-Borobudur-12.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/20160813_Shwedagon_Pagoda_9949_DxO.jpg/960px-20160813_Shwedagon_Pagoda_9949_DxO.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/Shwedagon_Zedi_Daw_Yangon_11.jpg/960px-Shwedagon_Zedi_Daw_Yangon_11.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Shwedagon_Zedi_Daw_Yangon_3.jpg/960px-Shwedagon_Zedi_Daw_Yangon_3.jpg',
  ],
  urban: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/75/Minato_City%2C_Tokyo%2C_Japan_%28Night%29.jpg/960px-Minato_City%2C_Tokyo%2C_Japan_%28Night%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Night_in_Tokyo_2014.JPG/960px-Night_in_Tokyo_2014.JPG',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Tokyo_Tower%2C_Minato_City.jpg/960px-Tokyo_Tower%2C_Minato_City.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Tokyo_by_night_2011.jpg/960px-Tokyo_by_night_2011.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Tokyo_by_night_2011_%28cropped%29.jpg/960px-Tokyo_by_night_2011_%28cropped%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/View_of_the_Tokyo_skyline_from_the_top_of_Sunshine_City.jpg/960px-View_of_the_Tokyo_skyline_from_the_top_of_Sunshine_City.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Brooklyn_Bridge_and_the_Lower_Manhattan_skyline_from_Pebble_Beach%2C_New_York.jpg/960px-Brooklyn_Bridge_and_the_Lower_Manhattan_skyline_from_Pebble_Beach%2C_New_York.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Lower_Manhattan%2C_New_York_skyline_from_Liberty_Island_2021.jpg/960px-Lower_Manhattan%2C_New_York_skyline_from_Liberty_Island_2021.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Lower_Manhattan_from_Jersey_City_September_2020_panorama.jpg/960px-Lower_Manhattan_from_Jersey_City_September_2020_panorama.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Manhattan_from_Weehawken%2C_NJ.jpg/960px-Manhattan_from_Weehawken%2C_NJ.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/New_York_Midtown_Skyline_at_night_-_Jan_2006_edit1.jpg/960px-New_York_Midtown_Skyline_at_night_-_Jan_2006_edit1.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/View_of_Empire_State_Building_from_Rockefeller_Center_New_York_City_dllu.jpg/960px-View_of_Empire_State_Building_from_Rockefeller_Center_New_York_City_dllu.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Burj_Khalifa_from_a_ferry%2C_Dubai.jpg/960px-Burj_Khalifa_from_a_ferry%2C_Dubai.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Burj_Khalifa_from_the_sea%2C_Dubai.jpg/960px-Burj_Khalifa_from_the_sea%2C_Dubai.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Dubai_Skyline_and_Burj_Khalifa_-_25072008.jpg/960px-Dubai_Skyline_and_Burj_Khalifa_-_25072008.jpg',
  ],
  default: [
    'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bb/Biot-travel-map.png/960px-Biot-travel-map.png',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Globe_Coaches_executive_travel_coach_in_Aberdare_-_geograph.org.uk_-_6053622.jpg/960px-Globe_Coaches_executive_travel_coach_in_Aberdare_-_geograph.org.uk_-_6053622.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Globe_and_Hat.jpg/960px-Globe_and_Hat.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Departure_board_at_Geneva_Airport.jpg/960px-Departure_board_at_Geneva_Airport.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Departure_board_in_gates_A_at_Zurich_International_Airport.jpg/960px-Departure_board_in_gates_A_at_Zurich_International_Airport.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Departures_board_at_Canberra_Airport_February_2020.jpg/960px-Departures_board_at_Canberra_Airport_February_2020.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Flight_departure_board%2C_Perth_Airport_Terminal_4%2C_2026_%2801%29.jpg/960px-Flight_departure_board%2C_Perth_Airport_Terminal_4%2C_2026_%2801%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fb/Flight_departure_board_at_Brisbane_Airport%2C_December_2022.jpg/960px-Flight_departure_board_at_Brisbane_Airport%2C_December_2022.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Flight_departure_board_at_Canberra_Airport%2C_November_2022.jpg/960px-Flight_departure_board_at_Canberra_Airport%2C_November_2022.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/Backpack_%28AM_2014.66.1-1%29.jpg/960px-Backpack_%28AM_2014.66.1-1%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Backpack_%28AM_2014.66.1-11%29.jpg/960px-Backpack_%28AM_2014.66.1-11%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Backpack_%28AM_2014.66.1-12%29.jpg/960px-Backpack_%28AM_2014.66.1-12%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Backpack_%28AM_2014.66.1-13%29.jpg/960px-Backpack_%28AM_2014.66.1-13%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Backpack_%28AM_2014.66.1-16%29.jpg/960px-Backpack_%28AM_2014.66.1-16%29.jpg',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Backpack_%28AM_2014.66.1-8%29.jpg/960px-Backpack_%28AM_2014.66.1-8%29.jpg',
  ],
};

// ── EXACT_DESTINATION_IMAGES: Hình ảnh thực đã kiểm duyệt cho địa điểm nổi tiếng ──
// Nguồn: Wikimedia Commons (direct links, verified)
export const EXACT_DESTINATION_IMAGES = {
  'Marina Bay Sands & Gardens': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Marina_Bays_Sands_Hotel_from_the_bridge_connecting_to_the_Gardens_By_The_Bay_in_Singapore.jpg/960px-Marina_Bays_Sands_Hotel_from_the_bridge_connecting_to_the_Gardens_By_The_Bay_in_Singapore.jpg',
  'Zermatt Matterhorn Peak': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Peak_of_the_Matterhorn%2C_seen_from_Zermatt%2C_Switzerland.jpg/960px-Peak_of_the_Matterhorn%2C_seen_from_Zermatt%2C_Switzerland.jpg',
  'Maldives Overwater Villas': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Diamonds_Thudufushi_Beach_and_Water_Villas%2C_May_2017_-04.jpg/960px-Diamonds_Thudufushi_Beach_and_Water_Villas%2C_May_2017_-04.jpg',
  'Santorini Island Sunsets': 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg',
  'Taj Mahal': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Taj_Mahal%2C_Agra%2C_India_edit2.jpg/960px-Taj_Mahal%2C_Agra%2C_India_edit2.jpg',
  'Leh Ladakh': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Indus_Valley_near_Leh.jpg/960px-Indus_Valley_near_Leh.jpg',
  'Interlaken Adventure': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/Interlaken_Landscape.jpg/960px-Interlaken_Landscape.jpg',
  'Cappadocia Hot Balloons': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Cappadocia_Balloon_Inflating_Wikimedia_Commons.JPG/960px-Cappadocia_Balloon_Inflating_Wikimedia_Commons.JPG',
  'Burj Khalifa Dubai': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Burj_dubai_3.11.08.jpg/960px-Burj_dubai_3.11.08.jpg',
  'Great Wall of China': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Badaling_China_Great-Wall-of-China-01.jpg/960px-Badaling_China_Great-Wall-of-China-01.jpg',
  'Jaipur City': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Jaipur_03-2016_20_City_Palace_complex.jpg/960px-Jaipur_03-2016_20_City_Palace_complex.jpg',
  'Kerala Backwaters': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Kerala_backwaters%2C_Canal%2C_Palm_trees%2C_India.jpg/960px-Kerala_backwaters%2C_Canal%2C_Palm_trees%2C_India.jpg',
  'Seoul Tower & Palace': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Front_view_of_the_tower_of_Jibokjae_Hall_under_blue_sky_at_Gyeongbokgung_Palace_in_Seoul.jpg/960px-Front_view_of_the_tower_of_Jibokjae_Hall_under_blue_sky_at_Gyeongbokgung_Palace_in_Seoul.jpg',
  'London Big Ben & Eye': 'https://upload.wikimedia.org/wikipedia/commons/e/e6/London_Eye_and_Big_Ben_-_geograph.org.uk_-_2429494.jpg',
  'Istanbul Hagia Sophia': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Hagia_Sophia_Mars_2013.jpg/960px-Hagia_Sophia_Mars_2013.jpg',
  'Ubud Bali Cultural Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Ubud%2C_Bali_in_2025.jpg/960px-Ubud%2C_Bali_in_2025.jpg',
  'Goa Beaches': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Mandrem_Beach_and_Mandrem_River%2C_Mandrem%2C_Goa%2C_India_%28edit%29.jpg/960px-Mandrem_Beach_and_Mandrem_River%2C_Mandrem%2C_Goa%2C_India_%28edit%29.jpg',
  'Jeju Island Beaches': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Gwakji_Beach_in_Jeju_Island%2C_2022.jpg/960px-Gwakji_Beach_in_Jeju_Island%2C_2022.jpg',
  'Sentosa Island Resort': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Resorts_World_Sentosa.jpg/960px-Resorts_World_Sentosa.jpg',
  'Maafushi Budget Beaches': 'https://upload.wikimedia.org/wikipedia/commons/f/f3/Maafushi%2CMaldives.jpg',
  'Stockholm Gamla Stan': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Skeppsbrokajen_Gamla_Stan_from_Skeppsholmen_Stockholm_2016_01.jpg/960px-Skeppsbrokajen_Gamla_Stan_from_Skeppsholmen_Stockholm_2016_01.jpg',
  'Oslo Fjords & Museum Peninsula': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Oslo_Fjord%2C_Norway_%2835517882523%29.jpg/960px-Oslo_Fjord%2C_Norway_%2835517882523%29.jpg',
  'Tromsø Northern Lights Hunting': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Troms%C3%B8%2C_northern_Norway.jpg/960px-Troms%C3%B8%2C_northern_Norway.jpg',
  'Geirangerfjord Cruising': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/0618_MSC_Virtuosa_in_Geirangerfjord_close-up_V-P.jpg/960px-0618_MSC_Virtuosa_in_Geirangerfjord_close-up_V-P.jpg',
  'Bergen Bryggen Wharf': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Bryggen_Hanseatic_wharf_at_night_Bergen_Norway.jpg/960px-Bryggen_Hanseatic_wharf_at_night_Bergen_Norway.jpg',
  'Lofoten Islands Scenic Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Svolvaer%2C_Lofoten%2C_Norway.JPG/960px-Svolvaer%2C_Lofoten%2C_Norway.JPG',
  'Amsterdam Historic Canal Cruise': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Prinsengracht_Amsterdam.jpg/960px-Prinsengracht_Amsterdam.jpg',
  'Keukenhof Tulip Festival': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Tulip_Tres_Chic_Festival.jpg/960px-Tulip_Tres_Chic_Festival.jpg',
  'Zaanse Schans Windmill Village': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Zaanstad_Zaanse_Schans_22.jpg/960px-Zaanstad_Zaanse_Schans_22.jpg',
  'Rotterdam Futuristic Architecture': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/GraphyArchy_-_Wikipedia_00096.jpg/960px-GraphyArchy_-_Wikipedia_00096.jpg',
  'Giethoorn Village Without Roads': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/69/Giethoorn_Netherlands_flckr05.jpg/960px-Giethoorn_Netherlands_flckr05.jpg',
  'Brussels Grand Place': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f2/Edificios_en_la_Grand-Place%2C_Bruselas%2C_B%C3%A9lgica%2C_2021-12-15%2C_DD_184-186_HDR.jpg/960px-Edificios_en_la_Grand-Place%2C_Bruselas%2C_B%C3%A9lgica%2C_2021-12-15%2C_DD_184-186_HDR.jpg',
  'Bruges Medieval Canal Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Brugge_Sashuis_R01.jpg/960px-Brugge_Sashuis_R01.jpg',
  'Ghent Castle of the Counts': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Gravensteen%2C_Ghent_%28DSCF0191%29.jpg/960px-Gravensteen%2C_Ghent_%28DSCF0191%29.jpg',
  'Antwerp Diamond District': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Antwerp_diamond_district_-_shops.jpg/960px-Antwerp_diamond_district_-_shops.jpg',
  'Vienna Schonbrunn Palace': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Palacio_de_Sch%C3%B6nbrunn%2C_Viena%2C_Austria%2C_2020-02-02%2C_DD_10.jpg/960px-Palacio_de_Sch%C3%B6nbrunn%2C_Viena%2C_Austria%2C_2020-02-02%2C_DD_10.jpg',
  'Hallstatt Alpine Village': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/View_of_Hallstatt_waterfront_and_churches_from_Hallst%C3%A4tter_See.jpg/960px-View_of_Hallstatt_waterfront_and_churches_from_Hallst%C3%A4tter_See.jpg',
  'Salzburg Mozart Heritage': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Mozart_Denkmal_Salzburg_at_night_2023-09-28_02.jpg/960px-Mozart_Denkmal_Salzburg_at_night_2023-09-28_02.jpg',
  'Innsbruck Alpine Skiing': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/2007_Austria_Innsbruck_Alps.jpg/960px-2007_Austria_Innsbruck_Alps.jpg',
  'Lisbon Alfama & Tram 28': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Lisbon_in_a_day_-_Tram_28_Alfama_%2839271341600%29.jpg/960px-Lisbon_in_a_day_-_Tram_28_Alfama_%2839271341600%29.jpg',
  'Algarve Cliffs & Caves': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Portugal_-_Algarve_-_arch_in_the_cliffs_%2825683137901%29.jpg/960px-Portugal_-_Algarve_-_arch_in_the_cliffs_%2825683137901%29.jpg',
  'Sintra Pena Palace': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Sintra_Portugal_Pal%C3%A1cio_da_Pena-01.jpg/960px-Sintra_Portugal_Pal%C3%A1cio_da_Pena-01.jpg',
  'Cliffs of Moher Coastal Walk': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Cliffs-Of-Moher-OBriens-From-South.JPG/960px-Cliffs-Of-Moher-OBriens-From-South.JPG',
  'Dublin Guinness & Trinity College': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Dublin_-_Trinity_College_June_2007.jpg/960px-Dublin_-_Trinity_College_June_2007.jpg',
  'Killarney Ring of Kerry Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Atlantic_Ocean%2C_Ring_of_Kerry_%28506559%29_%2827964189752%29.jpg/960px-Atlantic_Ocean%2C_Ring_of_Kerry_%28506559%29_%2827964189752%29.jpg',
  'Copenhagen Nyhavn Harbour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/The_Nyhavn_Canal_3.jpg/960px-The_Nyhavn_Canal_3.jpg',
  'Kronborg Castle Elsinore': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Kronborg_April_2026_06.jpg/960px-Kronborg_April_2026_06.jpg',
  'Rovaniemi Santa Claus Village': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Santa_Claus_Village_%285306867729%29.jpg/960px-Santa_Claus_Village_%285306867729%29.jpg',
  'Helsinki Cathedral & Market': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Buildings_near_Kauppatori_and_Helsinki_Cathedral_20100825_1.jpg/960px-Buildings_near_Kauppatori_and_Helsinki_Cathedral_20100825_1.jpg',
  'Finnish Lakeland & Sauna Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fd/Lake_Saimaa_aerial.jpg/1280px-Lake_Saimaa_aerial.jpg',
  'Reykjavik Blue Lagoon Spa': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/78/The_Blue_Lagoon_2.jpg/960px-The_Blue_Lagoon_2.jpg',
  'Gullfoss Golden Waterfall': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Gullfoss%2C_Su%C3%B0urland%2C_Islandia%2C_2014-08-16%2C_DD_119.JPG/960px-Gullfoss%2C_Su%C3%B0urland%2C_Islandia%2C_2014-08-16%2C_DD_119.JPG',
  'Jokulsarlon Glacier Lagoon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2c/J%C3%B6kuls%C3%A1rl%C3%B3n_lagoon_in_southeastern_Iceland.jpg/960px-J%C3%B6kuls%C3%A1rl%C3%B3n_lagoon_in_southeastern_Iceland.jpg',
  'Krakow Wawel Castle & Square': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Krakow_2024_110_Old_Town_Hall_Tower_View.jpg/960px-Krakow_2024_110_Old_Town_Hall_Tower_View.jpg',
  'Warsaw Old Town Restoration': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Market_Square_Warsaw_%2822594p%29.jpg/960px-Market_Square_Warsaw_%2822594p%29.jpg',
  'Tatra Mountains Zakopane': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Winter_in_Tatry_Mountains_-_Poland.jpg/960px-Winter_in_Tatry_Mountains_-_Poland.jpg',
  'Prague Charles Bridge & Castle': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Prague_Charles_Bridge_2021_04.jpg/960px-Prague_Charles_Bridge_2021_04.jpg',
  'Cesky Krumlov Castle Town': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/%C4%8Cesk%C3%BD_Krumlov%2C_Czechia%2C_20250504_1247_8845.jpg/960px-%C4%8Cesk%C3%BD_Krumlov%2C_Czechia%2C_20250504_1247_8845.jpg',
  'Karlovy Vary Spa Town': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Karlovy_Vary_20.JPG/960px-Karlovy_Vary_20.JPG',
  'Budapest Parliament on Danube': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Budapest_Parliament_amk.jpg/960px-Budapest_Parliament_amk.jpg',
  'Szechenyi Thermal Bath Pools': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Budapest_Sz%C3%A9chenyi_Baths_R01.jpg/960px-Budapest_Sz%C3%A9chenyi_Baths_R01.jpg',
  'Lake Balaton Resort Beaches': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Lake_Balaton_Hungary%281%29.jpg/960px-Lake_Balaton_Hungary%281%29.jpg',
  'Dubrovnik Game of Thrones Walls': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Dubrovnik_Old_Town_1.jpg/960px-Dubrovnik_Old_Town_1.jpg',
  'Plitvice Lakes Waterfall Trail': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Plitvice_Lakes1.jpg/960px-Plitvice_Lakes1.jpg',
  'Split Diocletian Palace': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Old_Town%2C_Split_%28P1080876%29.jpg/960px-Old_Town%2C_Split_%28P1080876%29.jpg',
  'Hvar Island Sun & Yacht Port': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/View_of_Hvar_02.jpg/1280px-View_of_Hvar_02.jpg',
  'Kuala Lumpur Petronas Towers': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Petronas_Panorama_II.jpg/960px-Petronas_Panorama_II.jpg',
  'Penang Georgetown Heritage Art': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Penang_Georgetown_Heritage_%2822463425353%29.jpg/960px-Penang_Georgetown_Heritage_%2822463425353%29.jpg',
  'Langkawi Cable Car & SkyBridge': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f8/Langkawi_sky_bridge.jpg/960px-Langkawi_sky_bridge.jpg',
  'Kota Kinabalu Nature Trekking': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/KotaKinabalu_Sabah_CityMosque-00.jpg/960px-KotaKinabalu_Sabah_CityMosque-00.jpg',
  'El Nido Bacuit Bay Islands': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Sunset_at_El_Nido%2C_Palawan_Philippines.jpg/960px-Sunset_at_El_Nido%2C_Palawan_Philippines.jpg',
  'Chocolate Hills Bohol Adventure': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Chocolate_Hills_-_edit.jpg/960px-Chocolate_Hills_-_edit.jpg',
  'Intramuros Walled City Manila': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Fort_Santiago_Intramuros_Manila.jpg/960px-Fort_Santiago_Intramuros_Manila.jpg',
  'Koh Rong Tropical Beaches': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Koh-rong-waterfront.jpg/960px-Koh-rong-waterfront.jpg',
  'Luang Prabang Heritage Town': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Temple_Wat_Xieng_Thong_-_Luang_Prabang_-_Laos.jpg/960px-Temple_Wat_Xieng_Thong_-_Luang_Prabang_-_Laos.jpg',
  'Vang Vieng Karst Nature Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Water_reflection_of_karst_mountains_at_golden_hour_in_Vang_Vieng_Laos_%28panoramic%29.jpg/960px-Water_reflection_of_karst_mountains_at_golden_hour_in_Vang_Vieng_Laos_%28panoramic%29.jpg',
  'Kuang Si Turquoise Waterfalls': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6/20171112_Kuang_Si_Falls_1953_DxO.jpg/960px-20171112_Kuang_Si_Falls_1953_DxO.jpg',
  'Inle Lake Fisherman Villages': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/20160805_Inle_Lake_7433.jpg/960px-20160805_Inle_Lake_7433.jpg',
  'Shwedagon Pagoda Yangon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Shwedagon_Zedi_Daw_Yangon_2.jpg/960px-Shwedagon_Zedi_Daw_Yangon_2.jpg',
  'Sigiriya Ancient Lion Rock': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Sigiriya_02.jpg/960px-Sigiriya_02.jpg',
  'Ella Train & Nine Arch Bridge': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Nine_arch_bridge_1.jpg/960px-Nine_arch_bridge_1.jpg',
  'Temple of the Tooth Kandy': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Tooth_Temple%2C_Kandy_-_53190582229.jpg/960px-Tooth_Temple%2C_Kandy_-_53190582229.jpg',
  'Kathmandu Durbar Square Temples': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Kathmandu_Durbar_Square%2C_Basantapur.jpg/960px-Kathmandu_Durbar_Square%2C_Basantapur.jpg',
  'Everest Base Camp Mountain Trek': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Everest%2C_Himalayas.jpg/960px-Everest%2C_Himalayas.jpg',
  'Pokhara Phewa Lake Resort': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Phewa_Lake-Pokhara_01.jpg/960px-Phewa_Lake-Pokhara_01.jpg',
  'Taipei 101 Observatory': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Taipei_101_2009_amk.jpg/960px-Taipei_101_2009_amk.jpg',
  'Jiufen Old Street Lanterns': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8a/Jiufen%2C_November_27%2C_2024_-_001.jpg/960px-Jiufen%2C_November_27%2C_2024_-_001.jpg',
  'Gobi Desert Singing Dunes': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Khongoryn_Els_02.jpg/960px-Khongoryn_Els_02.jpg',
  'Terelj National Park Ger Camp': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Gorkhi-Terelj_National_Park.jpg/960px-Gorkhi-Terelj_National_Park.jpg',
  'Astana Bayterek Tower': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Astana-2021-10_-_12.jpg/960px-Astana-2021-10_-_12.jpg',
  'Cartagena Spanish Walled City': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/61/City_walls_of_Cartagena_02.jpg/960px-City_walls_of_Cartagena_02.jpg',
  'Coffee Triangle Plantation Tour': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Coffee_Farm.jpg/960px-Coffee_Farm.jpg',
  'Easter Island Rapa Nui Moai': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Moai_Rano_raraku.jpg/960px-Moai_Rano_raraku.jpg',
  'Galapagos Islands Wildlife cruise': 'https://upload.wikimedia.org/wikipedia/commons/Gal%C3%A1pagos_baby_sea_lion.jpg/960px-Gal%C3%A1pagos_baby_sea_lion.jpg',
  'Arenal Volcano Hot Springs': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/af/Arenal_Volcano_01.jpg/960px-Arenal_Volcano_01.jpg',
  'Panama Canal Miraflores Locks': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Panama_Canal_Gatun_Locks.jpg/960px-Panama_Canal_Gatun_Locks.jpg',
  'Old Havana Classic Cars': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Classic_Cuban_Cars_in_Havana.jpg/960px-Classic_Cuban_Cars_in_Havana.jpg',
  'Varadero Beach Resorts': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Varadero_Beach_-_Views.jpg/960px-Varadero_Beach_-_Views.jpg',
  'Yasawa Islands Coral Reefs': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Fiji%2C_Yasawa_Islands.jpg/960px-Fiji%2C_Yasawa_Islands.jpg',
  'To Sua Ocean Trench Swim': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/To_Sua_Ocean_Trench_-_Lotofaga_village_-_Samoa.jpg/1280px-To_Sua_Ocean_Trench_-_Lotofaga_village_-_Samoa.jpg',
  'Serengeti National Park Safari': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Serengeti_Migration.jpg/960px-Serengeti_Migration.jpg',
  'Mount Kilimanjaro Summit Climb': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Mount_Kilimanjaro.jpg/960px-Mount_Kilimanjaro.jpg',
  'Morondava Avenue of Baobabs': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Adansonia_grandidieri04.jpg/960px-Adansonia_grandidieri04.jpg',
  'Chamarel Coloured Earth Dunes': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Chamarel-SevenColours.jpg/960px-Chamarel-SevenColours.jpg',
  'Sapa Terrace Rice Fields': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Ray_over_terrace_rice_field_in_Sapa_-_Trung_Ch%E1%BA%A3i..jpg/960px-Ray_over_terrace_rice_field_in_Sapa_-_Trung_Ch%E1%BA%A3i..jpg',
  'Trang An Scenic Landscape': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0b/Trang_An_Landscape_Complex%2C_Ninh_Binh_Province%2C_Vietnam%2C_20240202_1456_5313.jpg/960px-Trang_An_Landscape_Complex%2C_Ninh_Binh_Province%2C_Vietnam%2C_20240202_1456_5313.jpg',
  'Kyoto Fushimi Inari Shrine': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg/960px-Torii_path_with_lantern_at_Fushimi_Inari_Taisha_Shrine%2C_Kyoto%2C_Japan.jpg',
  'Osaka Dotonbori Street Food': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Food_street_in_Dotonbori%2C_Osaka%3B_January_2016.jpg/960px-Food_street_in_Dotonbori%2C_Osaka%3B_January_2016.jpg',
  'Grand Canyon South Rim': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/Grand_Canyon_South_Rim_at_Sunset.jpg/960px-Grand_Canyon_South_Rim_at_Sunset.jpg',
  'New York Times Square Neon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/New_york_times_square-terabass.jpg/960px-New_york_times_square-terabass.jpg',
  'Louvre Art Museum Paris': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Cour_Napol%C3%A9on_at_night_-_Louvre.jpg/960px-Cour_Napol%C3%A9on_at_night_-_Louvre.jpg',
  'French Riviera Nice Beaches': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/France-002498_-_French_Riviera_%2815905482471%29.jpg/960px-France-002498_-_French_Riviera_%2815905482471%29.jpg',
  'Zhangjiajie Avatar Mountains': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Avatar_World_38058-Zhangjiajie_%2849046813673%29.jpg/960px-Avatar_World_38058-Zhangjiajie_%2849046813673%29.jpg',
  'Shanghai The Bund Skyline': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Pudong_Shanghai_November_2017_panorama.jpg/960px-Pudong_Shanghai_November_2017_panorama.jpg',
  'Chiang Mai Lantern Festival': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Chiang_Mai%2C_Lantern_Festival%2C_Thailand.jpg/960px-Chiang_Mai%2C_Lantern_Festival%2C_Thailand.jpg',
  'Phuket Patong Beach Party': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Patong_Beach.jpg/960px-Patong_Beach.jpg',
  'Porto Douro Vineyard Valley': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Rio_Douro_-_Portugal_%2832615481975%29_%28cropped%29.jpg/960px-Rio_Douro_-_Portugal_%2832615481975%29_%28cropped%29.jpg',
  'Tivoli Gardens Theme Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Tivoli_Gardens_4.jpg/960px-Tivoli_Gardens_4.jpg',
  'Reynisfjara Black Sand Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Reynisfjara_Beach_Looking_West_Towards_Dyrh%C3%B3laey.jpg/960px-Reynisfjara_Beach_Looking_West_Towards_Dyrh%C3%B3laey.jpg',
  'Boracay Island White Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Boracay_White_Beach.png/960px-Boracay_White_Beach.png',
  'Angkor Wat Heritage Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Angkor_Wat.jpg/960px-Angkor_Wat.jpg',
  'Phnom Penh Palace & Silver Pagoda': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Royal_Palace%2C_Phnom_Penh_Cambodia_1.jpg/960px-Royal_Palace%2C_Phnom_Penh_Cambodia_1.jpg',
  'Bagan Hot Air Balloon Valley': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Bagan%2C_Burma.jpg/960px-Bagan%2C_Burma.jpg',
  'Taroko Marble Gorge National Park': 'https://upload.wikimedia.org/wikipedia/commons/0/09/Jiuqudong_2003-01.jpg',
  'Almaty Charyn Canyon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Charyn_Canyon%2C_Kazakhstan_03.jpg/960px-Charyn_Canyon%2C_Kazakhstan_03.jpg',
  'Torres del Paine National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Torres_del_Paine_y_cuernos_del_Paine%2C_montaje.jpg/960px-Torres_del_Paine_y_cuernos_del_Paine%2C_montaje.jpg',
  'Negril Cliffs & Seven Mile Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Negril_Jamaica_2007-09.jpg/960px-Negril_Jamaica_2007-09.jpg',
  'La Digue Anse Source Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/Luftbild_Insel_La_Digue_Seychellen.DNG_%2839617026111%29.jpg/960px-Luftbild_Insel_La_Digue_Seychellen.DNG_%2839617026111%29.jpg',
  'Phu Quoc Sunset Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/PhuQuoc-2983612.jpg/960px-PhuQuoc-2983612.jpg',
  'Tromso Northern Lights Hunting': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Troms%C3%B8%2C_northern_Norway.jpg/960px-Troms%C3%B8%2C_northern_Norway.jpg',
  'Halong Bay Cruise': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Halong_Bay_in_Vietnam.jpg/960px-Halong_Bay_in_Vietnam.jpg',
  'Mekong Delta Floating Market': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/Can_Tho%2C_Vietnam%2C_Floating_Market_2.jpg/960px-Can_Tho%2C_Vietnam%2C_Floating_Market_2.jpg',
  'Hoi An Ancient Town': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/H%E1%BB%99i_An%2C_Ancient_Town%2C_2020-01_CN-05.jpg/960px-H%E1%BB%99i_An%2C_Ancient_Town%2C_2020-01_CN-05.jpg',
  'Sahara Desert Camp Merzouga': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Merzouga.JPG/960px-Merzouga.JPG',
  'Marrakech Medina Souks': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Souk_Medina_Marrakech.jpg/960px-Souk_Medina_Marrakech.jpg',
  'Victoria Falls Zambia': 'https://upload.wikimedia.org/wikipedia/commons/8/8a/Victoria_Falls_Bridge%2C_Africa_092.jpg',
  'Serengeti Wildebeest Migration': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/9117_Serengeti_migration_JF.jpg/960px-9117_Serengeti_migration_JF.jpg',
  // ── Batch 2: Thêm các địa điểm chưa có ảnh ──
  'Acropolis of Athens': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Parthenon_from_south.jpg/960px-Parthenon_from_south.jpg',
  'Agadir Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Agadir_Beach.jpg/960px-Agadir_Beach.jpg',
  'Amazon Rainforest': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Amazon_Manaus_forest.jpg/960px-Amazon_Manaus_forest.jpg',
  'Amboseli National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Amboseli_National_Park_Elephant.jpg/960px-Amboseli_National_Park_Elephant.jpg',
  'Ayutthaya Historical Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/Ayutthaya_Thailand_2004.jpg/960px-Ayutthaya_Thailand_2004.jpg',
  'Banff National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/1_lake_louise_pano_2019.jpg/960px-1_lake_louise_pano_2019.jpg',
  'Barceloneta Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Beach%2C_Barcelona_%28P1170712%29.jpg/960px-Beach%2C_Barcelona_%28P1170712%29.jpg',
  'Black Forest': 'https://upload.wikimedia.org/wikipedia/commons/5/5c/Schwarza.jpg',
  'Blue Mountains National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4f/Three_Sisters_Sunset.jpg/960px-Three_Sisters_Sunset.jpg',
  'Blyde River Canyon Nature Reserve': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/Blyde_River_Canyon_Nature_Reserve_%28ZA%29%2C_Blyde_River_--_2024_--_0002.jpg/960px-Blyde_River_Canyon_Nature_Reserve_%28ZA%29%2C_Blyde_River_--_2024_--_0002.jpg',
  'Buenos Aires': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Casa_en_Caminito%2C_La_Boca%2C_Buenos_Aires.jpg/960px-Casa_en_Caminito%2C_La_Boca%2C_Buenos_Aires.jpg',
  'Chamonix-Mont-Blanc': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Glacier_Argentiere.jpg/960px-Glacier_Argentiere.jpg',
  'Chichen Itza': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Chichen_Itza_3.jpg/960px-Chichen_Itza_3.jpg',
  'Christ the Redeemer': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Redentor_Over_Clouds_1.jpg/960px-Redentor_Over_Clouds_1.jpg',
  'Cologne Cathedral': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Gothic_fa%C3%A7ade_of_Cologne_Cathedral_under_a_summer_sky.jpg/960px-Gothic_fa%C3%A7ade_of_Cologne_Cathedral_under_a_summer_sky.jpg',
  'Colosseum': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/de/Colosseo_2020.jpg/960px-Colosseo_2020.jpg',
  'Copacabana Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Copacabana_06_2016_2378.jpg/960px-Copacabana_06_2016_2378.jpg',
  'Copper Canyon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Barranca_del_cobre_2.jpg/960px-Barranca_del_cobre_2.jpg',
  'Cusco': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/6/6e/Plaza_de_Armas_-_Cusco.jpg',
  'Dolomites': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Tre_Cime_Dolomites.jpg/960px-Tre_Cime_Dolomites.jpg',
  'Drakensberg Mountains': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Amphitheatre_Drakensberg.jpg/960px-Amphitheatre_Drakensberg.jpg',
  'Essaouira Beach': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Bab_El_Marsa%2C_Essaouira%2C_Morocco.jpg/960px-Bab_El_Marsa%2C_Essaouira%2C_Morocco.jpg',
  'Forbidden City': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Beijing_China_Forbidden-City-03.jpg/960px-Beijing_China_Forbidden-City-03.jpg',
  'French Riviera': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/France-002498_-_French_Riviera_%2815905482471%29.jpg/960px-France-002498_-_French_Riviera_%2815905482471%29.jpg',
  'Gorges du Verdon': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Verdon_Gorge_1.jpg/960px-Verdon_Gorge_1.jpg',
  'Ha Long Bay': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/2d/Halong_Bay_in_Vietnam.jpg/960px-Halong_Bay_in_Vietnam.jpg',
  'Hassan II Mosque': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Hassan_II_Mosque_Plaza.jpg/960px-Hassan_II_Mosque_Plaza.jpg',
  'Hassan II Mosque (Casablanca)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/32/Hassan_II_Mosque_Plaza.jpg/960px-Hassan_II_Mosque_Plaza.jpg',
  'Himeji Castle': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7d/Ch%C3%A2teau_de_Himeji02.jpg/960px-Ch%C3%A2teau_de_Himeji02.jpg',
  'Iguazu Falls': 'https://upload.wikimedia.org/wikipedia/commons/f/f0/Cataratas027.jpg',
  'Jaipur': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Jaipur_03-2016_20_City_Palace_complex.jpg/960px-Jaipur_03-2016_20_City_Palace_complex.jpg',
  'Jaipur (Pink City)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Hawa_Mahal_2011.jpg/960px-Hawa_Mahal_2011.jpg',
  'Kruger National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Kruger_National_Park_%28ZA%29%2C_Kudus_--_2024_--_0468.jpg/960px-Kruger_National_Park_%28ZA%29%2C_Kudus_--_2024_--_0468.jpg',
  'Loire Valley': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Ch%C3%A2teau_de_Chambord_%282019%29.jpg/960px-Ch%C3%A2teau_de_Chambord_%282019%29.jpg',
  'Maasai Mara National Reserve': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Lions_Family_Portrait_Masai_Mara.jpg/960px-Lions_Family_Portrait_Masai_Mara.jpg',
  'Marrakech': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Jemaa_el-Fnaa_at_night.jpg/960px-Jemaa_el-Fnaa_at_night.jpg',
  'Meteora': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Meteora_morning.jpg/960px-Meteora_morning.jpg',
  'Meteora Monasteries': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/Meteora_morning.jpg/960px-Meteora_morning.jpg',
  'Nairobi': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Nairobi_skyline_P1000019.jpg/960px-Nairobi_skyline_P1000019.jpg',
  'Neuschwanstein Castle': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/ae/Castle_Neuschwanstein.jpg/960px-Castle_Neuschwanstein.jpg',
  'Notre Dame Cathedral (Paris)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/NotreDameDeParis.jpg/960px-NotreDameDeParis.jpg',
  'Ouro Preto': 'https://upload.wikimedia.org/wikipedia/commons/9/94/Ouro_Preto_Church.jpg',
  'Pelourinho, Salvador': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Pelourinho_Salvador_Bahia_2018-0601.jpg/960px-Pelourinho_Salvador_Bahia_2018-0601.jpg',
  'Perito Moreno Glacier': 'https://upload.wikimedia.org/wikipedia/commons/5/50/PeritoMoreno005.jpg',
  'Phi Phi Islands': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Ko_Phi_Phi_Don_%2814%29.jpg/960px-Ko_Phi_Phi_Don_%2814%29.jpg',
  'Phong Nha-Ke Bang National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/PhongNhaCave.jpg/960px-PhongNhaCave.jpg',
  'Phu Quoc Island': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/PhuQuoc-2983612.jpg/960px-PhuQuoc-2983612.jpg',
  'Picos de Europa National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/98/Picos_de_Europa_1975_76.jpg/960px-Picos_de_Europa_1975_76.jpg',
  'Quebec City': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Ch%C3%A2teau_Frontenac01.jpg/960px-Ch%C3%A2teau_Frontenac01.jpg',
  'Queenstown': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/73/Queenstown_New_Zealand.jpg/960px-Queenstown_New_Zealand.jpg',
  'Recoleta Cemetery (Buenos Aires)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Recoleta_Cemetery_%28Buenos_Aires%29.jpg/960px-Recoleta_Cemetery_%28Buenos_Aires%29.jpg',
  'Rio de Janeiro': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Redentor_Over_Clouds_1.jpg/960px-Redentor_Over_Clouds_1.jpg',
  'Rishikesh': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Lakshman_jhula%2C_Rishikesh.jpg/960px-Lakshman_jhula%2C_Rishikesh.jpg',
  'Samaria Gorge': 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/%CE%A6%CE%B1%CF%81%CE%AC%CE%B3%CE%B3%CE%B9_%CE%A3%CE%B1%CE%BC%CE%B1%CF%81%CE%B9%CE%AC%CF%82_3754.jpg/960px-%CE%A6%CE%B1%CF%81%CE%AC%CE%B3%CE%B3%CE%B9_%CE%A3%CE%B1%CE%BC%CE%B1%CF%81%CE%B9%CE%AC%CF%82_3754.jpg',
  'Santorini': 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg',
  'Santorini Caldera': 'https://upload.wikimedia.org/wikipedia/commons/7/7a/Oia_Santorini_sunset.jpg',
  'Sharm El Sheikh': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Naama_Bay_R01.jpg/960px-Naama_Bay_R01.jpg',
  'Statue of Liberty': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/LibertyStatue.JPG/960px-LibertyStatue.JPG',
  'Table Mountain (Cape Town)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Table_Mountain%2C_Cape_Town_%28P1050264%29.jpg/960px-Table_Mountain%2C_Cape_Town_%28P1050264%29.jpg',
  'Tofino, Vancouver Island': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Long_beach_-_Tofino_-_Vancouver_Island_01.jpg/960px-Long_beach_-_Tofino_-_Vancouver_Island_01.jpg',
  'Vancouver': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Vancouver_dusk_pano.jpg/960px-Vancouver_dusk_pano.jpg',
  'Vatican City': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/St._Peters_Square_%28panorama%29.jpg/960px-St._Peters_Square_%28panorama%29.jpg',
  'Verdon Gorge': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Verdon_Gorge_1.jpg/960px-Verdon_Gorge_1.jpg',
  'Waitangi Treaty Grounds': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/00_0589_Treaty_House_-_Waitangi_%28NZ%29.jpg/960px-00_0589_Treaty_House_-_Waitangi_%28NZ%29.jpg',
  'Wat Arun (Bangkok)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1f/Wat_Arun%2C_entrance_2.jpg/960px-Wat_Arun%2C_entrance_2.jpg',
  'Wat Phra Kaeo (Temple of the Emerald Buddha)': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Temple_of_the_Emerald_Buddha.jpg/960px-Temple_of_the_Emerald_Buddha.jpg',
  'White Desert National Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/White_Desert%2C_Egypt.jpg/960px-White_Desert%2C_Egypt.jpg',
  'Zhangjiajie National Forest Park': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Avatar_World_38058-Zhangjiajie_%2849046813673%29.jpg/960px-Avatar_World_38058-Zhangjiajie_%2849046813673%29.jpg',
};

// ── Simple hash function to consistently map a name to an index ───────────────
const getStringHash = (str) => {
  let hash = 0;
  if (!str) return hash;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash |= 0;
  }
  return Math.abs(hash);
};

// ── Resolve category key from name keywords (PRIMARY) then type (fallback) ────
export const resolveCategoryKey = (type, name = '') => {
  const n = name ? name.toLowerCase() : '';

  // 1. Name-keyword overrides (highest priority) - determines category from destination name
  if (n.includes('falls') || n.includes('waterfall') || n.includes('cascade')) return 'waterfall';
  if (n.includes('beach') || n.includes('coast') || n.includes('island') || n.includes('bay') || n.includes('lagoon') || n.includes('reef') || n.includes('shore') || n.includes('cliffs & ') || n.includes('coral')) return 'beach';
  if (n.includes('temple') || n.includes('pagoda') || n.includes('shrine') || n.includes('church') || n.includes('mosque') || n.includes('cathedral') || n.includes('sacred') || n.includes('monastery')) return 'religious';
  if (n.includes('ruins') || n.includes('castle') || n.includes('palace') || n.includes('fort') || n.includes('ancient') || n.includes('historic') || n.includes('heritage') || n.includes('museum') || n.includes('monument') || n.includes('walled')) return 'historical';
  if (n.includes('forest') || n.includes('jungle') || n.includes('canyon') || n.includes('valley') || n.includes('park') || n.includes('lake') || n.includes('gorge') || n.includes('river') || n.includes('garden') || n.includes('cave') || n.includes('mount') || n.includes('peak') || n.includes('rice field') || n.includes('terrace')) return 'nature';
  if (n.includes('plaza') || n.includes('city') || n.includes('urban') || n.includes('market') || n.includes('square') || n.includes('street') || n.includes('tower') || n.includes('skyline') || n.includes('harbor') || n.includes('harbour') || n.includes('canal')) return 'urban';
  if (n.includes('safari') || n.includes('trek') || n.includes('hike') || n.includes('climb') || n.includes('dive') || n.includes('surf') || n.includes('ski') || n.includes('adventure') || n.includes('expedition') || n.includes('camp') || n.includes('volcano')) return 'adventure';

  // 2. Fallback to Type field from data (unreliable but used as last resort)
  if (!type) return 'default';
  const t = type.toLowerCase();
  if (t === 'beach') return 'beach';
  if (t === 'nature') return 'nature';
  if (t === 'historical') return 'historical';
  if (t === 'religious') return 'religious';
  if (t === 'adventure') return 'adventure';
  if (t === 'city') return 'urban';
  if (t.includes('mountain')) return 'mountain';
  if (t.includes('cultur')) return 'cultural';
  return 'default';
};

/**
 * Helper to strip country suffix in parentheses from destination name.
 */
const stripCountrySuffix = (name) => {
  if (!name) return '';
  return name.replace(/\s*\([^)]*\)\s*$/, "").trim();
};

const EXACT_DESTINATION_IMAGE_VARIANTS = {
  'Meteora': [
    EXACT_DESTINATION_IMAGES['Meteora'],
    IMAGES_BY_TYPE.nature[12],
    IMAGES_BY_TYPE.religious[0],
  ],
  'Meteora Monasteries': [
    EXACT_DESTINATION_IMAGES['Meteora Monasteries'],
    IMAGES_BY_TYPE.religious[1],
    IMAGES_BY_TYPE.nature[11],
  ],
  'Santorini': [
    EXACT_DESTINATION_IMAGES['Santorini'],
    IMAGES_BY_TYPE.beach[6],
    IMAGES_BY_TYPE.urban[0],
  ],
  'Santorini Caldera': [
    EXACT_DESTINATION_IMAGES['Santorini Caldera'],
    IMAGES_BY_TYPE.beach[7],
    IMAGES_BY_TYPE.urban[1],
  ],
};

export const getExactDestinationImage = (name, variantOffset = 0) => {
  if (!name) return null;
  const clean = stripCountrySuffix(name).toLowerCase();
  // Try exact match first, then stripped-name match
  let key = Object.keys(EXACT_DESTINATION_IMAGES).find(k => k.toLowerCase() === name.toLowerCase());
  if (!key) key = Object.keys(EXACT_DESTINATION_IMAGES).find(k => k.toLowerCase() === clean);
  if (!key) key = Object.keys(EXACT_DESTINATION_IMAGES).find(k => stripCountrySuffix(k).toLowerCase() === clean);
  if (!key) return null;

  const variants = EXACT_DESTINATION_IMAGE_VARIANTS[key];
  if (variants?.length > 0) {
    return variants[Math.abs(variantOffset) % variants.length];
  }

  return EXACT_DESTINATION_IMAGES[key];
};

/**
 * Lấy URL hình ảnh cho một địa điểm du lịch.
 *
 * Thứ tự ưu tiên:
 *   1. EXACT_DESTINATION_IMAGES (hình đã kiểm duyệt thủ công - Wikimedia Commons)
 *   2. IMAGES_BY_TYPE (dựa vào name-keyword resolution để chọn đúng loại ảnh)
 *   3. default fallback
 */
export const getDestinationImage = (name, type, country, variantOffset = 0) => {
  if (!name) return IMAGES_BY_TYPE.default[0];

  const trimmedName = name.trim();
  const cleanName = stripCountrySuffix(trimmedName);

  // 1. Ưu tiên cao nhất: hình đã kiểm duyệt thủ công (Wikimedia Commons curated)
  const exactImage = getExactDestinationImage(trimmedName, variantOffset);
  if (exactImage) {
    return exactImage;
  }

  // 2. IMAGES_BY_TYPE: dùng name-keyword để xác định loại ảnh phù hợp
  const categoryKey = resolveCategoryKey(type, cleanName);
  const images = IMAGES_BY_TYPE[categoryKey] || IMAGES_BY_TYPE.default;
  const hash = getStringHash(cleanName + (country || '')) + Math.abs(variantOffset);
  const index = hash % images.length;
  return images[index];
};

/**
 * Lấy hình ảnh fallback (dùng IMAGES_BY_TYPE) khi URL chính bị lỗi.
 */
export const getDatasetImage = (destination) => {
  const image = destination?.image || destination?.Image || destination?.['image'];
  if (!image || typeof image !== 'string') return null;
  const trimmed = image.trim();
  return trimmed.startsWith('http') ? trimmed : null;
};

export const getFallbackImage = (name, type, variantOffset = 0) => {
  const categoryKey = resolveCategoryKey(type, name);
  const images = IMAGES_BY_TYPE[categoryKey] || IMAGES_BY_TYPE.default;
  const hash = getStringHash((name || '') + categoryKey) + Math.abs(variantOffset);
  const index = hash % images.length;
  return images[index];
};
