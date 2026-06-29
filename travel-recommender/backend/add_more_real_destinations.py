# -*- coding: utf-8 -*-
"""Add more real destinations from EXACT_DESTINATION_IMAGES to MongoDB."""
import json, sys, random
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from mining.mongodb_storage import db_storage

# Real destinations with verified metadata
# Format: (Name, Country, Type, Best_Season, Avg_Cost, Avg_Rating, Description)
MORE_DESTINATIONS = [
    ("Marina Bay Sands & Gardens", "Singapore", "Urban", "All Year", 250, 4.7, "Khu phức hợp giải trí và khu vườn siêu cây nổi tiếng nhất Singapore."),
    ("Zermatt Matterhorn Peak", "Switzerland", "Mountain", "Winter", 350, 4.9, "Đỉnh núi Matterhorn huyền thoại, biểu tượng của Thụy Sĩ."),
    ("Maldives Overwater Villas", "Maldives", "Beach", "Winter", 500, 4.9, "Thiên đường nghỉ dưỡng với biệt thự trên mặt nước trong xanh."),
    ("Santorini Island Sunsets", "Greece", "Beach", "Summer", 200, 4.8, "Hòn đảo tuyệt đẹp với hoàng hôn ngoạn mục và kiến trúc trắng xanh."),
    ("Taj Mahal", "India", "Historical", "Winter", 50, 4.9, "Kỳ quan thế giới, lăng mộ đá cẩm thạch trắng tuyệt đẹp."),
    ("Leh Ladakh", "India", "Adventure", "Summer", 80, 4.7, "Vùng cao nguyên hoang sơ với phong cảnh núi non hùng vĩ."),
    ("Interlaken Adventure", "Switzerland", "Adventure", "Summer", 300, 4.8, "Trung tâm thể thao mạo hiểm giữa hai hồ nước tuyệt đẹp."),
    ("Cappadocia Hot Balloons", "Turkey", "Adventure", "Spring", 120, 4.8, "Thung lũng đá kỳ quan với hàng trăm khinh khí cầu bay cùng lúc."),
    ("Burj Khalifa Dubai", "UAE", "Urban", "Winter", 250, 4.7, "Tòa tháp cao nhất thế giới, biểu tượng của Dubai hiện đại."),
    ("Great Wall of China", "China", "Historical", "Autumn", 60, 4.8, "Vạn Lý Trường Thành - kỳ quan kiến trúc vĩ đại nhất lịch sử nhân loại."),
    ("Jaipur City", "India", "Cultural", "Winter", 45, 4.5, "Thành phố hồng với cung điện và pháo đài tráng lệ."),
    ("Kerala Backwaters", "India", "Nature", "Winter", 55, 4.6, "Mạng lưới sông ngòi và kênh rạch tuyệt đẹp giữa rừng dừa."),
    ("Seoul Tower & Palace", "South Korea", "Cultural", "Autumn", 120, 4.6, "Thủ đô Hàn Quốc với cung điện cổ và tháp Namsan hiện đại."),
    ("London Big Ben & Eye", "United Kingdom", "Urban", "Summer", 200, 4.7, "London với tháp đồng hồ Big Ben và vòng quay London Eye nổi tiếng."),
    ("Istanbul Hagia Sophia", "Turkey", "Historical", "Spring", 80, 4.8, "Thánh đường Hagia Sophia - kiệt tác kiến trúc Byzantine."),
    ("Ubud Bali Cultural Tour", "Indonesia", "Cultural", "Summer", 70, 4.7, "Trung tâm văn hóa Bali với ruộng bậc thang và đền cổ."),
    ("Goa Beaches", "India", "Beach", "Winter", 40, 4.4, "Bãi biển nhiệt đới nổi tiếng nhất Ấn Độ."),
    ("Jeju Island Beaches", "South Korea", "Beach", "Summer", 130, 4.5, "Đảo núi lửa tuyệt đẹp của Hàn Quốc."),
    ("Sentosa Island Resort", "Singapore", "Beach", "All Year", 180, 4.5, "Đảo giải trí hàng đầu Đông Nam Á."),
    ("Stockholm Gamla Stan", "Sweden", "Historical", "Summer", 180, 4.6, "Phố cổ trung cổ quyến rũ nhất Scandinavia."),
    ("Tromso Northern Lights Hunting", "Norway", "Adventure", "Winter", 200, 4.8, "Thành phố cực quang đẹp nhất Na Uy."),
    ("Geirangerfjord Cruising", "Norway", "Nature", "Summer", 180, 4.9, "Vịnh hẹp đẹp nhất Na Uy với thác nước hùng vĩ."),
    ("Bergen Bryggen Wharf", "Norway", "Historical", "Summer", 170, 4.6, "Bến tàu Hanseatic đầy màu sắc, di sản UNESCO."),
    ("Lofoten Islands Scenic Tour", "Norway", "Nature", "Summer", 160, 4.8, "Quần đảo hoang sơ với phong cảnh ngoạn mục."),
    ("Amsterdam Historic Canal Cruise", "Netherlands", "Cultural", "Spring", 160, 4.6, "Du thuyền trên kênh đào cổ kính của Amsterdam."),
    ("Keukenhof Tulip Festival", "Netherlands", "Nature", "Spring", 130, 4.7, "Vườn hoa tulip lớn nhất thế giới."),
    ("Zaanse Schans Windmill Village", "Netherlands", "Cultural", "Spring", 100, 4.5, "Làng cối xay gió truyền thống Hà Lan."),
    ("Giethoorn Village Without Roads", "Netherlands", "Nature", "Summer", 90, 4.6, "Làng cổ không đường bộ, chỉ có kênh rạch."),
    ("Brussels Grand Place", "Belgium", "Historical", "Spring", 140, 4.6, "Quảng trường lớn Brussels - kiệt tác kiến trúc Baroque."),
    ("Vienna Schonbrunn Palace", "Austria", "Historical", "Spring", 150, 4.8, "Cung điện mùa hè tráng lệ của Hoàng gia Áo."),
    ("Hallstatt Alpine Village", "Austria", "Nature", "Summer", 140, 4.9, "Làng cổ bên hồ đẹp nhất thế giới."),
    ("Salzburg Mozart Heritage", "Austria", "Cultural", "Winter", 140, 4.6, "Thành phố quê hương Mozart với kiến trúc Baroque."),
    ("Lisbon Alfama & Tram 28", "Portugal", "Cultural", "Spring", 100, 4.6, "Khu phố cổ Lisbon với xe điện cổ điển."),
    ("Algarve Cliffs & Caves", "Portugal", "Beach", "Summer", 90, 4.7, "Bờ biển với vách đá và hang động ngoạn mục."),
    ("Sintra Pena Palace", "Portugal", "Historical", "Spring", 85, 4.8, "Cung điện Pena rực rỡ trên đỉnh đồi."),
    ("Cliffs of Moher Coastal Walk", "Ireland", "Nature", "Summer", 110, 4.7, "Vách đá cao nhất châu Âu với tầm nhìn Đại Tây Dương."),
    ("Copenhagen Nyhavn Harbour", "Denmark", "Urban", "Summer", 170, 4.6, "Bến cảng đầy màu sắc biểu tượng của Copenhagen."),
    ("Rovaniemi Santa Claus Village", "Finland", "Cultural", "Winter", 160, 4.5, "Làng Ông già Noel chính thức tại Phần Lan."),
    ("Helsinki Cathedral & Market", "Finland", "Cultural", "Summer", 150, 4.5, "Nhà thờ trắng Helsinki và chợ truyền thống."),
    ("Reykjavik Blue Lagoon Spa", "Iceland", "Adventure", "Winter", 200, 4.7, "Suối nước nóng Blue Lagoon nổi tiếng nhất Iceland."),
    ("Gullfoss Golden Waterfall", "Iceland", "Nature", "Summer", 180, 4.8, "Thác nước vàng hùng vĩ của Iceland."),
    ("Jokulsarlon Glacier Lagoon", "Iceland", "Nature", "Winter", 190, 4.9, "Đầm phá sông băng với tảng băng trôi xanh biếc."),
    ("Krakow Wawel Castle & Square", "Poland", "Historical", "Spring", 70, 4.6, "Lâu đài Wawel và quảng trường cổ Krakow."),
    ("Prague Charles Bridge & Castle", "Czech Republic", "Historical", "Spring", 90, 4.8, "Cầu Charles và lâu đài Prague - viên ngọc châu Âu."),
    ("Budapest Parliament on Danube", "Hungary", "Historical", "Spring", 80, 4.7, "Tòa nhà quốc hội Budapest soi bóng sông Danube."),
    ("Dubrovnik Game of Thrones Walls", "Croatia", "Historical", "Summer", 120, 4.7, "Thành cổ Dubrovnik - bối cảnh Game of Thrones."),
    ("Plitvice Lakes Waterfall Trail", "Croatia", "Nature", "Spring", 80, 4.8, "Hệ thống hồ và thác nước bậc thang tuyệt đẹp."),
    ("Kuala Lumpur Petronas Towers", "Malaysia", "Urban", "All Year", 80, 4.6, "Tháp đôi Petronas - biểu tượng Malaysia hiện đại."),
    ("Penang Georgetown Heritage Art", "Malaysia", "Cultural", "All Year", 50, 4.5, "Phố cổ Georgetown với nghệ thuật đường phố độc đáo."),
    ("Langkawi Cable Car & SkyBridge", "Malaysia", "Adventure", "All Year", 70, 4.5, "Cáp treo và cầu trên không ngoạn mục tại Langkawi."),
    ("El Nido Bacuit Bay Islands", "Philippines", "Beach", "Winter", 55, 4.7, "Vịnh đảo đá vôi tuyệt đẹp tại Palawan."),
    ("Chocolate Hills Bohol Adventure", "Philippines", "Nature", "Winter", 45, 4.4, "Đồi sô-cô-la độc đáo tại đảo Bohol."),
    ("Boracay Island White Beach", "Philippines", "Beach", "Winter", 75, 4.6, "Bãi biển cát trắng nổi tiếng nhất Philippines."),
    ("Angkor Wat Heritage Park", "Cambodia", "Historical", "Winter", 35, 4.9, "Quần thể đền Angkor Wat - kỳ quan thế giới."),
    ("Bagan Hot Air Balloon Valley", "Myanmar", "Historical", "Winter", 45, 4.8, "Thung lũng hàng nghìn ngôi đền cổ với khinh khí cầu."),
    ("Inle Lake Fisherman Villages", "Myanmar", "Cultural", "Winter", 40, 4.6, "Hồ Inle với làng nổi và ngư dân chèo bằng chân."),
    ("Kyoto Fushimi Inari Shrine", "Japan", "Religious", "Spring", 120, 4.8, "Đền Fushimi Inari với hàng nghìn cổng torii đỏ."),
    ("Osaka Dotonbori Street Food", "Japan", "Cultural", "Autumn", 110, 4.7, "Phố ẩm thực Dotonbori - thiên đường ăn uống Nhật Bản."),
    ("Grand Canyon South Rim", "USA", "Nature", "Spring", 100, 4.9, "Hẻm núi lớn nhất thế giới với cảnh quan ngoạn mục."),
    ("New York Times Square Neon", "USA", "Urban", "Autumn", 250, 4.6, "Quảng trường Thời đại - trung tâm giải trí New York."),
    ("Louvre Art Museum Paris", "France", "Cultural", "Spring", 180, 4.8, "Bảo tàng nghệ thuật lớn nhất thế giới tại Paris."),
    ("French Riviera Nice Beaches", "France", "Beach", "Summer", 160, 4.5, "Bờ biển Pháp với bãi biển Địa Trung Hải tuyệt đẹp."),
    ("Zhangjiajie Avatar Mountains", "China", "Nature", "Autumn", 65, 4.8, "Núi đá sa thạch kỳ quan - cảm hứng cho phim Avatar."),
    ("Shanghai The Bund Skyline", "China", "Urban", "Autumn", 100, 4.6, "Bến Thượng Hải với đường chân trời ngoạn mục."),
    ("Chiang Mai Lantern Festival", "Thailand", "Cultural", "Winter", 40, 4.7, "Lễ hội đèn trời Yi Peng huyền diệu tại Chiang Mai."),
    ("Phuket Patong Beach Party", "Thailand", "Beach", "Winter", 55, 4.4, "Bãi biển Patong sôi động nhất Thái Lan."),
    ("Porto Douro Vineyard Valley", "Portugal", "Cultural", "Autumn", 90, 4.6, "Thung lũng rượu vang Douro tuyệt đẹp."),
    ("Reynisfjara Black Sand Beach", "Iceland", "Beach", "Summer", 170, 4.7, "Bãi biển cát đen núi lửa độc đáo nhất thế giới."),
    ("Phnom Penh Palace & Silver Pagoda", "Cambodia", "Historical", "Winter", 30, 4.5, "Cung điện hoàng gia và chùa Bạc tại Phnom Penh."),
    ("Taroko Marble Gorge National Park", "Taiwan", "Nature", "Autumn", 70, 4.7, "Hẻm núi đá cẩm thạch ngoạn mục tại Đài Loan."),
    ("Almaty Charyn Canyon", "Kazakhstan", "Nature", "Summer", 50, 4.6, "Hẻm núi Charyn - Grand Canyon thu nhỏ của Trung Á."),
    ("Torres del Paine National Park", "Chile", "Nature", "Summer", 120, 4.9, "Công viên quốc gia với núi đá granite và sông băng."),
    ("Phu Quoc Sunset Beach", "Vietnam", "Beach", "Winter", 60, 4.5, "Đảo Phú Quốc với bãi biển hoàng hôn tuyệt đẹp."),
    ("Sapa Terrace Rice Fields", "Vietnam", "Nature", "Autumn", 40, 4.6, "Ruộng bậc thang Sa Pa - kiệt tác nông nghiệp vùng cao."),
    ("Trang An Scenic Landscape", "Vietnam", "Nature", "Spring", 30, 4.7, "Quần thể danh thắng Tràng An - di sản UNESCO."),
]

def main():
    db_storage.connect()
    coll = db_storage.db.destinations

    # Get existing destination names
    existing = set(d['Destination Name'] for d in coll.find({}, {'Destination Name': 1}))
    print(f"Existing destinations: {len(existing)}")

    # Find new ones to add
    new_docs = []
    for name, country, dtype, season, cost, rating, desc in MORE_DESTINATIONS:
        if name not in existing:
            # Determine cost category
            if cost <= 50:
                cost_cat = "budget"
            elif cost <= 120:
                cost_cat = "moderate"
            elif cost <= 250:
                cost_cat = "expensive"
            else:
                cost_cat = "luxury"

            # Determine continent
            continent_map = {
                "Singapore": "Asia", "Switzerland": "Europe", "Maldives": "Asia",
                "Greece": "Europe", "India": "Asia", "Turkey": "Asia",
                "UAE": "Asia", "China": "Asia", "South Korea": "Asia",
                "United Kingdom": "Europe", "Indonesia": "Asia", "Sweden": "Europe",
                "Norway": "Europe", "Netherlands": "Europe", "Belgium": "Europe",
                "Austria": "Europe", "Portugal": "Europe", "Ireland": "Europe",
                "Denmark": "Europe", "Finland": "Europe", "Iceland": "Europe",
                "Poland": "Europe", "Czech Republic": "Europe", "Hungary": "Europe",
                "Croatia": "Europe", "Malaysia": "Asia", "Philippines": "Asia",
                "Cambodia": "Asia", "Myanmar": "Asia", "Japan": "Asia",
                "USA": "North America", "France": "Europe", "Chile": "South America",
                "Kazakhstan": "Asia", "Taiwan": "Asia", "Vietnam": "Asia",
                "Thailand": "Asia",
            }
            continent = continent_map.get(country, "Unknown")

            doc = {
                'Destination Name': name,
                'Country': country,
                'Type': dtype,
                'Best Season': season,
                'Avg Cost (USD/day)': cost,
                'Avg Rating': rating,
                'Cost_Category': cost_cat,
                'Continent': continent,
                'Broader_Type': dtype,
                'Description': desc,
                'UNESCO Site': 'No',
                'country_flag': '',
                'country_currency': '',
                'country_capital': '',
            }
            new_docs.append(doc)

    print(f"New destinations to add: {len(new_docs)}")

    if new_docs:
        coll.insert_many(new_docs)

    final_count = coll.count_documents({})
    print(f"\nMongoDB total: {final_count} destinations")

    # Update CSV fallback
    import csv
    all_docs = list(coll.find({}, {"_id": 0}))
    csv_path = Path(__file__).parent / "data" / "processed" / "destinations_real.csv"
    if all_docs:
        fields = list(all_docs[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(all_docs)
        print(f"Updated CSV: {csv_path} ({len(all_docs)} rows)")

if __name__ == '__main__':
    main()
