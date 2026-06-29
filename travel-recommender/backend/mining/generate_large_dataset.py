# -*- coding: utf-8 -*-
"""
Tao ra Tap du lieu lon - Them 36 quoc gia moi va 190+ diem den moi
de mo rong kich thuoc tap du lieu len 300+ diem den va 60+ quoc gia,
va tao ra cac hang giao dich tuong ung trong ma tran giao dich nhi phan
de Apriori co the khai pha so luong lon cac luat.
"""
import sys
import os
import pandas as pd
import numpy as np
import copy
from pathlib import Path

# Them thu muc cha vao duong dan
sys.path.insert(0, str(Path(__file__).parent.parent))
from mining.mongodb_storage import db_storage

# 36 quoc gia moi cung voi sieu du lieu
COUNTRY_METADATA = {
    "Norway": {
        "flag": "🇳🇴", "region": "Europe", "subregion": "Northern Europe",
        "currency": "NOK", "symbol": "kr", "languages": "Norwegian", "capital": "Oslo",
        "timezone": "UTC+01:00", "pop": 5400000, "area": 385207, "alpha2": "NO", "alpha3": "NOR",
        "borders": "SE, FI, RU", "lat": 60.4720, "lon": 8.4689
    },
    "Netherlands": {
        "flag": "🇳🇱", "region": "Europe", "subregion": "Western Europe",
        "currency": "EUR", "symbol": "€", "languages": "Dutch", "capital": "Amsterdam",
        "timezone": "UTC+01:00", "pop": 17400000, "area": 41850, "alpha2": "NL", "alpha3": "NLD",
        "borders": "DE, BE", "lat": 52.1326, "lon": 5.2913
    },
    "Belgium": {
        "flag": "🇧🇪", "region": "Europe", "subregion": "Western Europe",
        "currency": "EUR", "symbol": "€", "languages": "Dutch, French, German", "capital": "Brussels",
        "timezone": "UTC+01:00", "pop": 11500000, "area": 30689, "alpha2": "BE", "alpha3": "BEL",
        "borders": "FR, DE, LU, NL", "lat": 50.5039, "lon": 4.4699
    },
    "Austria": {
        "flag": "🇦🇹", "region": "Europe", "subregion": "Western Europe",
        "currency": "EUR", "symbol": "€", "languages": "German", "capital": "Vienna",
        "timezone": "UTC+01:00", "pop": 8900000, "area": 83871, "alpha2": "AT", "alpha3": "AUT",
        "borders": "DE, CZ, SK, HU, SI, IT, CH, LI", "lat": 47.5162, "lon": 14.5501
    },
    "Portugal": {
        "flag": "🇵🇹", "region": "Europe", "subregion": "Southern Europe",
        "currency": "EUR", "symbol": "€", "languages": "Portuguese", "capital": "Lisbon",
        "timezone": "UTC+00:00", "pop": 10300000, "area": 92212, "alpha2": "PT", "alpha3": "PRT",
        "borders": "ES", "lat": 39.3999, "lon": -8.2245
    },
    "Ireland": {
        "flag": "🇮🇪", "region": "Europe", "subregion": "Northern Europe",
        "currency": "EUR", "symbol": "€", "languages": "English, Irish", "capital": "Dublin",
        "timezone": "UTC+00:00", "pop": 4900000, "area": 70273, "alpha2": "IE", "alpha3": "IRL",
        "borders": "GB", "lat": 53.4129, "lon": -8.2439
    },
    "Denmark": {
        "flag": "🇩🇰", "region": "Europe", "subregion": "Northern Europe",
        "currency": "DKK", "symbol": "kr", "languages": "Danish", "capital": "Copenhagen",
        "timezone": "UTC+01:00", "pop": 5800000, "area": 43094, "alpha2": "DK", "alpha3": "DNK",
        "borders": "DE", "lat": 56.2639, "lon": 9.5018
    },
    "Finland": {
        "flag": "🇫🇮", "region": "Europe", "subregion": "Northern Europe",
        "currency": "EUR", "symbol": "€", "languages": "Finnish, Swedish", "capital": "Helsinki",
        "timezone": "UTC+02:00", "pop": 5500000, "area": 338424, "alpha2": "FI", "alpha3": "FIN",
        "borders": "SE, NO, RU", "lat": 61.9241, "lon": 25.7482
    },
    "Iceland": {
        "flag": "🇮🇸", "region": "Europe", "subregion": "Northern Europe",
        "currency": "ISK", "symbol": "kr", "languages": "Icelandic", "capital": "Reykjavik",
        "timezone": "UTC+00:00", "pop": 360000, "area": 103000, "alpha2": "IS", "alpha3": "ISL",
        "borders": "", "lat": 64.9631, "lon": -19.0208
    },
    "Poland": {
        "flag": "🇵🇱", "region": "Europe", "subregion": "Eastern Europe",
        "currency": "PLN", "symbol": "zł", "languages": "Polish", "capital": "Warsaw",
        "timezone": "UTC+01:00", "pop": 38000000, "area": 312696, "alpha2": "PL", "alpha3": "POL",
        "borders": "BY, CZ, DE, LT, RU, SK, UA", "lat": 51.9194, "lon": 19.1451
    },
    "Czech Republic": {
        "flag": "🇨🇿", "region": "Europe", "subregion": "Eastern Europe",
        "currency": "CZK", "symbol": "Kč", "languages": "Czech", "capital": "Prague",
        "timezone": "UTC+01:00", "pop": 10700000, "area": 78867, "alpha2": "CZ", "alpha3": "CZE",
        "borders": "AT, DE, PL, SK", "lat": 49.8175, "lon": 15.4730
    },
    "Hungary": {
        "flag": "🇭🇺", "region": "Europe", "subregion": "Eastern Europe",
        "currency": "HUF", "symbol": "Ft", "languages": "Hungarian", "capital": "Budapest",
        "timezone": "UTC+01:00", "pop": 9800000, "area": 93028, "alpha2": "HU", "alpha3": "HUN",
        "borders": "AT, HR, RO, RS, SK, SI, UA", "lat": 47.1625, "lon": 19.5033
    },
    "Croatia": {
        "flag": "🇭🇷", "region": "Europe", "subregion": "Southern Europe",
        "currency": "EUR", "symbol": "€", "languages": "Croatian", "capital": "Zagreb",
        "timezone": "UTC+01:00", "pop": 4100000, "area": 56594, "alpha2": "HR", "alpha3": "HRV",
        "borders": "BA, HU, ME, RS, SI", "lat": 45.1000, "lon": 15.2000
    },
    "Malaysia": {
        "flag": "🇲🇾", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "MYR", "symbol": "RM", "languages": "Malay", "capital": "Kuala Lumpur",
        "timezone": "UTC+08:00", "pop": 32000000, "area": 329847, "alpha2": "MY", "alpha3": "MYS",
        "borders": "BN, ID, TH", "lat": 4.2105, "lon": 101.9758
    },
    "Philippines": {
        "flag": "🇵🇭", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "PHP", "symbol": "₱", "languages": "Filipino, English", "capital": "Manila",
        "timezone": "UTC+08:00", "pop": 109000000, "area": 300000, "alpha2": "PH", "alpha3": "PHL",
        "borders": "", "lat": 12.8797, "lon": 121.7740
    },
    "Cambodia": {
        "flag": "🇰🇭", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "KHR", "symbol": "៛", "languages": "Khmer", "capital": "Phnom Penh",
        "timezone": "UTC+07:00", "pop": 16700000, "area": 181035, "alpha2": "KH", "alpha3": "KHM",
        "borders": "LA, TH, VN", "lat": 12.5657, "lon": 104.9910
    },
    "Laos": {
        "flag": "🇱🇦", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "LAK", "symbol": "₭", "languages": "Lao", "capital": "Vientiane",
        "timezone": "UTC+07:00", "pop": 7200000, "area": 236800, "alpha2": "LA", "alpha3": "LAO",
        "borders": "KH, CN, MMR, TH, VN", "lat": 19.8563, "lon": 102.4955
    },
    "Myanmar": {
        "flag": "🇲🇲", "region": "Asia", "subregion": "South-Eastern Asia",
        "currency": "MMK", "symbol": "K", "languages": "Burmese", "capital": "Naypyidaw",
        "timezone": "UTC+06:30", "pop": 54000000, "area": 676578, "alpha2": "MM", "alpha3": "MMR",
        "borders": "BD, CN, IN, LA, TH", "lat": 21.9162, "lon": 95.9560
    },
    "Sri Lanka": {
        "flag": "🇱🇰", "region": "Asia", "subregion": "Southern Asia",
        "currency": "LKR", "symbol": "₨", "languages": "Sinhala, Tamil", "capital": "Colombo",
        "timezone": "UTC+05:30", "pop": 21900000, "area": 65610, "alpha2": "LK", "alpha3": "LKA",
        "borders": "", "lat": 7.8731, "lon": 80.7718
    },
    "Nepal": {
        "flag": "🇳🇵", "region": "Asia", "subregion": "Southern Asia",
        "currency": "NPR", "symbol": "₨", "languages": "Nepali", "capital": "Kathmandu",
        "timezone": "UTC+05:45", "pop": 29100000, "area": 147181, "alpha2": "NP", "alpha3": "NPL",
        "borders": "CN, IN", "lat": 28.3949, "lon": 84.1240
    },
    "Taiwan": {
        "flag": "🇹🇼", "region": "Asia", "subregion": "Eastern Asia",
        "currency": "TWD", "symbol": "NT$", "languages": "Mandarin", "capital": "Taipei",
        "timezone": "UTC+08:00", "pop": 23600000, "area": 36193, "alpha2": "TW", "alpha3": "TWN",
        "borders": "", "lat": 23.6978, "lon": 120.9605
    },
    "Mongolia": {
        "flag": "🇲🇳", "region": "Asia", "subregion": "Eastern Asia",
        "currency": "MNT", "symbol": "₮", "languages": "Mongolian", "capital": "Ulaanbaatar",
        "timezone": "UTC+08:00", "pop": 3300000, "area": 1564116, "alpha2": "MN", "alpha3": "MNG",
        "borders": "CN, RU", "lat": 46.8625, "lon": 103.8467
    },
    "Kazakhstan": {
        "flag": "🇰🇿", "region": "Asia", "subregion": "Central Asia",
        "currency": "KZT", "symbol": "₸", "languages": "Kazakh, Russian", "capital": "Astana",
        "timezone": "UTC+06:00", "pop": 18800000, "area": 2724900, "alpha2": "KZ", "alpha3": "KAZ",
        "borders": "CN, KG, RU, TJ, UZ", "lat": 48.0196, "lon": 66.9237
    },
    "Colombia": {
        "flag": "🇨🇴", "region": "South America", "subregion": "South America",
        "currency": "COP", "symbol": "$", "languages": "Spanish", "capital": "Bogota",
        "timezone": "UTC-05:00", "pop": 50880000, "area": 1141748, "alpha2": "CO", "alpha3": "COL",
        "borders": "BR, EC, PA, PE, VE", "lat": 4.5709, "lon": -74.2973
    },
    "Chile": {
        "flag": "🇨🇱", "region": "South America", "subregion": "South America",
        "currency": "CLP", "symbol": "$", "languages": "Spanish", "capital": "Santiago",
        "timezone": "UTC-04:00", "pop": 19100000, "area": 756096, "alpha2": "CL", "alpha3": "CHL",
        "borders": "AR, BO, PE", "lat": -35.6751, "lon": -71.5430
    },
    "Ecuador": {
        "flag": "🇪🇨", "region": "South America", "subregion": "South America",
        "currency": "USD", "symbol": "$", "languages": "Spanish", "capital": "Quito",
        "timezone": "UTC-05:00", "pop": 17600000, "area": 283561, "alpha2": "EC", "alpha3": "ECU",
        "borders": "CO, PE", "lat": -1.8312, "lon": -78.1834
    },
    "Costa Rica": {
        "flag": "🇨🇷", "region": "North America", "subregion": "Central America",
        "currency": "CRC", "symbol": "₡", "languages": "Spanish", "capital": "San Jose",
        "timezone": "UTC-06:00", "pop": 5000000, "area": 51100, "alpha2": "CR", "alpha3": "CRI",
        "borders": "Nicaragua, Panama", "lat": 9.7489, "lon": -83.7534
    },
    "Panama": {
        "flag": "🇵🇦", "region": "North America", "subregion": "Central America",
        "currency": "PAB", "symbol": "B/.", "languages": "Spanish", "capital": "Panama City",
        "timezone": "UTC-05:00", "pop": 4300000, "area": 75420, "alpha2": "PA", "alpha3": "PAN",
        "borders": "Colombia, Costa Rica", "lat": 8.5380, "lon": -80.7821
    },
    "Cuba": {
        "flag": "🇨🇺", "region": "North America", "subregion": "Caribbean",
        "currency": "CUP", "symbol": "$", "languages": "Spanish", "capital": "Havana",
        "timezone": "UTC-05:00", "pop": 11300000, "area": 109884, "alpha2": "CU", "alpha3": "CUB",
        "borders": "", "lat": 21.5218, "lon": -77.7812
    },
    "Jamaica": {
        "flag": "🇯🇲", "region": "North America", "subregion": "Caribbean",
        "currency": "JMD", "symbol": "$", "languages": "English", "capital": "Kingston",
        "timezone": "UTC-05:00", "pop": 2900000, "area": 10991, "alpha2": "JM", "alpha3": "JAM",
        "borders": "", "lat": 18.1096, "lon": -77.2975
    },
    "Fiji": {
        "flag": "🇫🇯", "region": "Oceania", "subregion": "Melanesia",
        "currency": "FJD", "symbol": "$", "languages": "English, Fijian", "capital": "Suva",
        "timezone": "UTC+12:00", "pop": 900000, "area": 18274, "alpha2": "FJ", "alpha3": "FJI",
        "borders": "", "lat": -17.7134, "lon": 178.0650
    },
    "Samoa": {
        "flag": "🇼🇸", "region": "Oceania", "subregion": "Polynesia",
        "currency": "WST", "symbol": "WS$", "languages": "Samoan, English", "capital": "Apia",
        "timezone": "UTC+13:00", "pop": 200000, "area": 2831, "alpha2": "WS", "alpha3": "WSM",
        "borders": "", "lat": -13.7590, "lon": -172.1046
    },
    "Tanzania": {
        "flag": "🇹🇿", "region": "Africa", "subregion": "Eastern Africa",
        "currency": "TZS", "symbol": "Sh", "languages": "Swahili, English", "capital": "Dodoma",
        "timezone": "UTC+03:00", "pop": 59700000, "area": 947303, "alpha2": "TZ", "alpha3": "TZA",
        "borders": "BI, CGO, CO, KE, MW, MZ, RW, UG, ZM", "lat": -6.3690, "lon": 34.8888
    },
    "Madagascar": {
        "flag": "🇲🇬", "region": "Africa", "subregion": "Eastern Africa",
        "currency": "MGA", "symbol": "Ar", "languages": "Malagasy, French", "capital": "Antananarivo",
        "timezone": "UTC+03:00", "pop": 27700000, "area": 587041, "alpha2": "MG", "alpha3": "MDG",
        "borders": "", "lat": -18.7669, "lon": 46.8691
    },
    "Seychelles": {
        "flag": "🇸🇨", "region": "Africa", "subregion": "Eastern Africa",
        "currency": "SCR", "symbol": "₨", "languages": "Seychellois Creole, English, French", "capital": "Victoria",
        "timezone": "UTC+04:00", "pop": 98000, "area": 452, "alpha2": "SC", "alpha3": "SYC",
        "borders": "", "lat": -4.6796, "lon": 55.4920
    },
    "Mauritius": {
        "flag": "🇲🇺", "region": "Africa", "subregion": "Eastern Africa",
        "currency": "MUR", "symbol": "₨", "languages": "English, French", "capital": "Port Louis",
        "timezone": "UTC+04:00", "pop": 1300000, "area": 2040, "alpha2": "MU", "alpha3": "MUS",
        "borders": "", "lat": -20.3484, "lon": 57.5522
    }
}

# Cac diem den noi tieng tren 36 quoc gia nay + bo sung cho cac quoc gia hien co
NEW_DESTINATIONS_DATA = [
    # ── Norway ──
    {"Name": "Oslo Fjords & Museum Peninsula", "Country": "Norway", "Type": "Urban", "Cost": 180, "Season": "Summer", "Rating": 4.7, "Visitors": 2.1, "UNESCO": "No", "Lat": 59.9139, "Lon": 10.7522, "Desc": "Trải nghiệm đi du thuyền ngắm vịnh Oslo, tham quan bảo tàng tàu Viking cổ và thưởng thức ẩm thực Bắc Âu sang trọng."},
    {"Name": "Tromsø Northern Lights Hunting", "Country": "Norway", "Type": "Adventure", "Cost": 230, "Season": "Winter", "Rating": 4.9, "Visitors": 0.8, "UNESCO": "No", "Lat": 69.6492, "Lon": 18.9553, "Desc": "Điểm săn cực quang hàng đầu thế giới với các tour trượt tuyết bằng xe kéo chó Husky và ngắm vịnh hẹp tuyết phủ."},
    {"Name": "Geirangerfjord Cruising", "Country": "Norway", "Type": "Mountain", "Cost": 190, "Season": "Summer", "Rating": 4.8, "Visitors": 1.2, "UNESCO": "Yes", "Lat": 62.1015, "Lon": 7.2058, "Desc": "Vịnh hẹp ngập tràn thác nước ngoạn mục như Seven Sisters, bao bọc bởi những vách đá dựng đứng kỳ vĩ."},
    {"Name": "Bergen Bryggen Wharf", "Country": "Norway", "Type": "Cultural", "Cost": 160, "Season": "Spring", "Rating": 4.6, "Visitors": 1.8, "UNESCO": "Yes", "Lat": 60.3913, "Lon": 5.3221, "Desc": "Khu phố cổ bến cảng thời trung cổ với những ngôi nhà gỗ nghiêng độc đáo sơn màu rực rỡ bên bờ biển."},
    {"Name": "Lofoten Islands Scenic Tour", "Country": "Norway", "Type": "Nature", "Cost": 210, "Season": "Summer", "Rating": 4.9, "Visitors": 0.9, "UNESCO": "No", "Lat": 67.9931, "Lon": 13.6393, "Desc": "Quần đảo đẹp huyền ảo với các ngôi làng chài rorbu đỏ thắm nằm sát mép vịnh nước xanh ngắt và núi cao."},

    # ── Netherlands ──
    {"Name": "Amsterdam Historic Canal Cruise", "Country": "Netherlands", "Type": "Urban", "Cost": 140, "Season": "Spring", "Rating": 4.8, "Visitors": 8.5, "UNESCO": "Yes", "Lat": 52.3676, "Lon": 4.9041, "Desc": "Khám phá thủ đô Amsterdam bằng du thuyền len lỏi qua hệ thống kênh đào cổ kính thơ mộng thế kỷ 17."},
    {"Name": "Keukenhof Tulip Festival", "Country": "Netherlands", "Type": "Nature", "Cost": 110, "Season": "Spring", "Rating": 4.9, "Visitors": 1.6, "UNESCO": "No", "Lat": 52.2713, "Lon": 4.5464, "Desc": "Khu vườn tulip lớn nhất hành tinh, phô diễn hàng triệu bông hoa rực rỡ sắc màu mỗi khi xuân về."},
    {"Name": "Zaanse Schans Windmill Village", "Country": "Netherlands", "Type": "Cultural", "Cost": 85, "Season": "Summer", "Rating": 4.6, "Visitors": 2.2, "UNESCO": "No", "Lat": 52.4729, "Lon": 4.8219, "Desc": "Bảo tàng mở tái hiện sinh động nông thôn Hà Lan thế kỷ 18 với cối xay gió khổng lồ và xưởng làm guốc gỗ."},
    {"Name": "Rotterdam Futuristic Architecture", "Country": "Netherlands", "Type": "City", "Cost": 125, "Season": "Autumn", "Rating": 4.5, "Visitors": 2.0, "UNESCO": "No", "Lat": 51.9244, "Lon": 4.4777, "Desc": "Thành phố cảng hiện đại nổi bật với nhà khối lập phương nghiêng, cầu Erasmus và chợ ẩm thực mái vòm khổng lồ."},
    {"Name": "Giethoorn Village Without Roads", "Country": "Netherlands", "Type": "Nature", "Cost": 130, "Season": "Summer", "Rating": 4.8, "Visitors": 1.1, "UNESCO": "No", "Lat": 52.7402, "Lon": 6.0796, "Desc": "Ngôi làng cổ tích không có đường đi cho xe cộ, người dân di chuyển hoàn toàn bằng thuyền trên các kênh rạch nhỏ."},

    # ── Belgium ──
    {"Name": "Brussels Grand Place", "Country": "Belgium", "Type": "Cultural", "Cost": 115, "Season": "Summer", "Rating": 4.7, "Visitors": 5.2, "UNESCO": "Yes", "Lat": 50.8467, "Lon": 4.3524, "Desc": "Quảng trường trung tâm cổ kính lộng lẫy bao quanh bởi tòa thị chính Gothic và các tòa nhà mạ vàng sang trọng."},
    {"Name": "Bruges Medieval Canal Tour", "Country": "Belgium", "Type": "Historical", "Cost": 135, "Season": "Spring", "Rating": 4.8, "Visitors": 2.5, "UNESCO": "Yes", "Lat": 51.2093, "Lon": 3.2247, "Desc": "Thành phố thời trung cổ bảo tồn nguyên vẹn với phố đá cuội, nhà thờ gạch đỏ và kênh đào uốn lượn."},
    {"Name": "Ghent Castle of the Counts", "Country": "Belgium", "Type": "Historical", "Cost": 105, "Season": "Autumn", "Rating": 4.6, "Visitors": 1.4, "UNESCO": "No", "Lat": 51.0543, "Lon": 3.7174, "Desc": "Khám phá lâu đài Gravensteen sừng sững từ thế kỷ 12 và khu bến cảng Graslei nhộn nhịp."},
    {"Name": "Antwerp Diamond District", "Country": "Belgium", "Type": "Urban", "Cost": 140, "Season": "Winter", "Rating": 4.5, "Visitors": 1.8, "UNESCO": "No", "Lat": 51.2194, "Lon": 4.4025, "Desc": "Trung tâm giao dịch kim cương lớn nhất thế giới kết hợp nhà ga xe lửa Antwerpen-Centraal đẹp lộng lẫy."},

    # ── Austria ──
    {"Name": "Vienna Schonbrunn Palace", "Country": "Austria", "Type": "Cultural", "Cost": 130, "Season": "Autumn", "Rating": 4.8, "Visitors": 3.6, "UNESCO": "Yes", "Lat": 48.1858, "Lon": 16.3122, "Desc": "Cung điện mùa hè Baroque tráng lệ của hoàng gia Habsburg với những khu vườn bạt ngàn và đồi ngắm cảnh."},
    {"Name": "Hallstatt Alpine Village", "Country": "Austria", "Type": "Mountain", "Cost": 165, "Season": "Autumn", "Rating": 4.9, "Visitors": 1.2, "UNESCO": "Yes", "Lat": 47.5622, "Lon": 13.6493, "Desc": "Thị trấn bên hồ nước huyền ảo nép mình dưới chân núi tuyết Alps, điểm đến chụp ảnh lãng mạn hàng đầu."},
    {"Name": "Salzburg Mozart Heritage", "Country": "Austria", "Type": "Historical", "Cost": 120, "Season": "Summer", "Rating": 4.7, "Visitors": 2.4, "UNESCO": "Yes", "Lat": 47.8018, "Lon": 13.0448, "Desc": "Thành phố quê hương Mozart với pháo đài Hohensalzburg sừng sững và bối cảnh bộ phim The Sound of Music."},
    {"Name": "Innsbruck Alpine Skiing", "Country": "Austria", "Type": "Mountain", "Cost": 150, "Season": "Winter", "Rating": 4.7, "Visitors": 1.6, "UNESCO": "No", "Lat": 47.2692, "Lon": 11.4041, "Desc": "Khu nghỉ dưỡng tuyết cao cấp nằm giữa thung lũng tuyết phủ, lý tưởng cho trượt tuyết và leo núi Alps."},

    # ── Portugal ──
    {"Name": "Lisbon Alfama & Tram 28", "Country": "Portugal", "Type": "Urban", "Cost": 90, "Season": "Spring", "Rating": 4.7, "Visitors": 4.0, "UNESCO": "No", "Lat": 38.7167, "Lon": -9.1333, "Desc": "Tuyến xe điện cổ điển màu vàng leo qua các con dốc quanh co thuộc khu phố cổ Alfama đậm chất Fado."},
    {"Name": "Porto Douro Vineyard Valley", "Country": "Portugal", "Type": "Nature", "Cost": 115, "Season": "Autumn", "Rating": 4.8, "Visitors": 2.1, "UNESCO": "Yes", "Lat": 41.1579, "Lon": -8.6291, "Desc": "Thung lũng sông Douro ngút ngàn đồi chè rượu vang bậc thang, cảnh sắc dòng sông xanh ngắt thơ mộng."},
    {"Name": "Algarve Cliffs & Caves", "Country": "Portugal", "Type": "Beach", "Cost": 110, "Season": "Summer", "Rating": 4.8, "Visitors": 2.8, "UNESCO": "No", "Lat": 37.0179, "Lon": -7.9304, "Desc": "Đường bờ biển phía nam tuyệt mỹ với các vòm đá vôi khổng lồ nhô ra biển và hang động Benagil kỳ ảo."},
    {"Name": "Sintra Pena Palace", "Country": "Portugal", "Type": "Cultural", "Cost": 100, "Season": "Spring", "Rating": 4.8, "Visitors": 1.9, "UNESCO": "Yes", "Lat": 38.7878, "Lon": -9.3906, "Desc": "Cung điện lãng mạn đầy màu sắc vàng, đỏ, xanh ngự trị trên đỉnh đồi mờ sương đẹp tựa tranh vẽ."},

    # ── Ireland ──
    {"Name": "Cliffs of Moher Coastal Walk", "Country": "Ireland", "Type": "Nature", "Cost": 105, "Season": "Summer", "Rating": 4.9, "Visitors": 1.5, "UNESCO": "No", "Lat": 52.9719, "Lon": -9.4309, "Desc": "Vách đá dựng đứng cao hơn 200 mét đâm thẳng ra Đại Tây Dương, bao phủ bởi thảm cỏ xanh mướt mát."},
    {"Name": "Dublin Guinness & Trinity College", "Country": "Ireland", "Type": "Urban", "Cost": 125, "Season": "Summer", "Rating": 4.6, "Visitors": 2.2, "UNESCO": "No", "Lat": 53.3438, "Lon": -6.2546, "Desc": "Trải nghiệm nhà máy bia Guinness lịch sử và ghé thăm thư viện cổ kính Long Room tráng lệ."},
    {"Name": "Killarney Ring of Kerry Tour", "Country": "Ireland", "Type": "Nature", "Cost": 110, "Season": "Spring", "Rating": 4.7, "Visitors": 1.1, "UNESCO": "No", "Lat": 52.0592, "Lon": -9.5065, "Desc": "Cung đường ven biển vòng quanh bán đảo Iveragh ngắm hồ nước hoang sơ và lâu đài cổ kính."},

    # ── Denmark ──
    {"Name": "Copenhagen Nyhavn Harbour", "Country": "Denmark", "Type": "Urban", "Cost": 155, "Season": "Summer", "Rating": 4.8, "Visitors": 4.5, "UNESCO": "No", "Lat": 55.6761, "Lon": 12.5683, "Desc": "Bến cảng lịch sử nổi tiếng với các dãy nhà sắc màu rực rỡ, nhà hàng ngoài trời nhộn nhịp bên dòng kênh."},
    {"Name": "Tivoli Gardens Theme Park", "Country": "Denmark", "Type": "Adventure", "Cost": 135, "Season": "Summer", "Rating": 4.7, "Visitors": 4.2, "UNESCO": "No", "Lat": 55.6737, "Lon": 12.5681, "Desc": "Công viên giải trí lâu đời thứ hai thế giới, sự pha trộn độc đáo giữa vườn hoa lãng mạn và tàu lượn."},
    {"Name": "Kronborg Castle Elsinore", "Country": "Denmark", "Type": "Historical", "Cost": 120, "Season": "Autumn", "Rating": 4.6, "Visitors": 0.8, "UNESCO": "Yes", "Lat": 56.0390, "Lon": 12.6220, "Desc": "Lâu đài thời Phục hưng nổi tiếng sừng sững bên bờ biển Baltic, bối cảnh vở kịch Hamlet của Shakespeare."},

    # ── Finland ──
    {"Name": "Rovaniemi Santa Claus Village", "Country": "Finland", "Type": "Adventure", "Cost": 195, "Season": "Winter", "Rating": 4.8, "Visitors": 1.0, "UNESCO": "No", "Lat": 66.5436, "Lon": 25.8475, "Desc": "Ngôi làng chính thức của Ông già Noel nằm trên vòng Cực Bắc, ngập tràn tuyết trắng và tuần lộc mùa đông."},
    {"Name": "Helsinki Cathedral & Market", "Country": "Finland", "Type": "City", "Cost": 120, "Season": "Summer", "Rating": 4.5, "Visitors": 1.5, "UNESCO": "No", "Lat": 60.1702, "Lon": 24.9520, "Desc": "Nhà thờ mái vòm xanh ngọc uy nghi sừng sững bên quảng trường Senate và chợ hải sản ven cảng Baltic."},
    {"Name": "Finnish Lakeland & Sauna Tour", "Country": "Finland", "Type": "Nature", "Cost": 140, "Season": "Summer", "Rating": 4.7, "Visitors": 0.7, "UNESCO": "No", "Lat": 61.5000, "Lon": 28.3000, "Desc": "Nghỉ dưỡng tại nhà gỗ bên hồ nước trong vắt, tắm hơi sauna truyền thống và chèo thuyền giữa rừng thông."},

    # ── Iceland ──
    {"Name": "Reykjavik Blue Lagoon Spa", "Country": "Iceland", "Type": "Nature", "Cost": 240, "Season": "Winter", "Rating": 4.9, "Visitors": 1.1, "UNESCO": "No", "Lat": 63.8794, "Lon": -22.4451, "Desc": "Hồ nước nóng địa nhiệt màu xanh lam sữa tự nhiên giữa lòng nham thạch đen sẫm độc đáo cực kỳ thư giãn."},
    {"Name": "Gullfoss Golden Waterfall", "Country": "Iceland", "Type": "Nature", "Cost": 140, "Season": "Summer", "Rating": 4.8, "Visitors": 1.0, "UNESCO": "No", "Lat": 64.3271, "Lon": -20.1199, "Desc": "Thác nước khổng lồ hai tầng đổ xuống hẻm núi sâu, tạo ra những dải cầu vồng rực rỡ vào những ngày nắng."},
    {"Name": "Reynisfjara Black Sand Beach", "Country": "Iceland", "Type": "Beach", "Cost": 160, "Season": "Spring", "Rating": 4.8, "Visitors": 0.9, "UNESCO": "No", "Lat": 63.4018, "Lon": -19.0189, "Desc": "Bãi biển cát đen tuyền bao quanh bởi các cột đá bazan hình thù đối xứng kỳ lạ và những ngọn sóng dữ dội."},
    {"Name": "Jokulsarlon Glacier Lagoon", "Country": "Iceland", "Type": "Mountain", "Cost": 220, "Season": "Winter", "Rating": 4.9, "Visitors": 0.6, "UNESCO": "No", "Lat": 64.0489, "Lon": -16.1777, "Desc": "Hồ nước ngập tràn những khối băng trôi màu xanh ngọc bích từ sông băng lớn nhất châu Âu đổ ra biển."},

    # ── Poland ──
    {"Name": "Krakow Wawel Castle & Square", "Country": "Poland", "Type": "Historical", "Cost": 60, "Season": "Spring", "Rating": 4.8, "Visitors": 3.2, "UNESCO": "Yes", "Lat": 50.0614, "Lon": 19.9383, "Desc": "Quảng trường thời trung cổ lớn nhất châu Âu cổ kính với lâu đài hoàng gia Wawel tráng lệ bên sông Vistula."},
    {"Name": "Warsaw Old Town Restoration", "Country": "Poland", "Type": "Historical", "Cost": 65, "Season": "Autumn", "Rating": 4.6, "Visitors": 2.5, "UNESCO": "Yes", "Lat": 52.2497, "Lon": 21.0122, "Desc": "Khu phố cổ được phục dựng ngoạn mục và tỉ mỉ sau Thế chiến II với quảng trường và lâu đài hoàng gia."},
    {"Name": "Tatra Mountains Zakopane", "Country": "Poland", "Type": "Mountain", "Cost": 75, "Season": "Winter", "Rating": 4.7, "Visitors": 1.5, "UNESCO": "No", "Lat": 49.2992, "Lon": 19.9496, "Desc": "Thị trấn nghỉ dưỡng dưới chân dãy núi Tatra phủ đầy tuyết, lý tưởng cho leo núi và trượt tuyết giá rẻ."},

    # ── Czech Republic ──
    {"Name": "Prague Charles Bridge & Castle", "Country": "Czech Republic", "Type": "Historical", "Cost": 75, "Season": "Autumn", "Rating": 4.9, "Visitors": 6.2, "UNESCO": "Yes", "Lat": 50.0755, "Lon": 14.4378, "Desc": "Cầu đá Charles cổ kính với 30 bức tượng thánh dẫn lối vào lâu đài cổ Prague tráng lệ ngự trên đỉnh đồi."},
    {"Name": "Cesky Krumlov Castle Town", "Country": "Czech Republic", "Type": "Cultural", "Cost": 70, "Season": "Summer", "Rating": 4.8, "Visitors": 1.1, "UNESCO": "Yes", "Lat": 48.8127, "Lon": 14.3140, "Desc": "Ngôi làng trung cổ cổ tích uốn lượn theo dòng sông Vltava dịu mát dưới chân lâu đài đá tráng lệ."},
    {"Name": "Karlovy Vary Spa Town", "Country": "Czech Republic", "Type": "Nature", "Cost": 90, "Season": "Spring", "Rating": 4.6, "Visitors": 1.3, "UNESCO": "No", "Lat": 50.2305, "Lon": 12.8711, "Desc": "Thành phố suối khoáng nóng nổi tiếng thế giới với kiến trúc Baroque lộng lẫy và các cột vòi nước uống trực tiếp."},

    # ── Hungary ──
    {"Name": "Budapest Parliament on Danube", "Country": "Hungary", "Type": "Cultural", "Cost": 70, "Season": "Autumn", "Rating": 4.9, "Visitors": 3.8, "UNESCO": "Yes", "Lat": 47.4979, "Lon": 19.0402, "Desc": "Tòa nhà quốc hội khổng lồ kiểu Gothic soi bóng xuống sông Danube, cảnh sắc rực rỡ nghẹt thở khi đêm xuống."},
    {"Name": "Szechenyi Thermal Bath Pools", "Country": "Hungary", "Type": "Nature", "Cost": 80, "Season": "Winter", "Rating": 4.7, "Visitors": 2.2, "UNESCO": "No", "Lat": 47.5188, "Lon": 19.0825, "Desc": "Hồ bơi nước nóng ngoài trời kiến trúc tân cổ điển bốc hơi nghi ngút giữa tuyết lạnh mùa đông Budapest."},
    {"Name": "Lake Balaton Resort Beaches", "Country": "Hungary", "Type": "Beach", "Cost": 60, "Season": "Summer", "Rating": 4.5, "Visitors": 1.7, "UNESCO": "No", "Lat": 46.8530, "Lon": 17.7288, "Desc": "Được coi là 'biển' của Hungary, hồ nước ngọt lớn nhất Trung Âu thích hợp cho bơi lội, đi thuyền mùa hè."},

    # ── Croatia ──
    {"Name": "Dubrovnik Game of Thrones Walls", "Country": "Croatia", "Type": "Historical", "Cost": 150, "Season": "Summer", "Rating": 4.9, "Visitors": 1.4, "UNESCO": "Yes", "Lat": 42.6507, "Lon": 18.0944, "Desc": "Bức tường thành đá cổ bao bọc phố cổ Dubrovnik vươn ra biển Adriatic trong vắt, bối cảnh phim Kings Landing."},
    {"Name": "Plitvice Lakes Waterfall Trail", "Country": "Croatia", "Type": "Nature", "Cost": 110, "Season": "Spring", "Rating": 4.9, "Visitors": 1.7, "UNESCO": "Yes", "Lat": 44.8654, "Lon": 15.5820, "Desc": "16 hồ nước xanh thẳm nối tiếp nhau bằng hàng trăm dòng thác chảy tràn qua những rặng đá vôi phủ rêu phong."},
    {"Name": "Split Diocletian Palace", "Country": "Croatia", "Type": "Historical", "Cost": 120, "Season": "Summer", "Rating": 4.7, "Visitors": 2.0, "UNESCO": "Yes", "Lat": 43.5081, "Lon": 16.4402, "Desc": "Cung điện La Mã cổ đại xây dựng từ thế kỷ 4, nay là trái tim nhộn nhịp ngập tràn quán xá của thành phố Split."},
    {"Name": "Hvar Island Sun & Yacht Port", "Country": "Croatia", "Type": "Beach", "Cost": 140, "Season": "Summer", "Rating": 4.8, "Visitors": 0.8, "UNESCO": "No", "Lat": 43.1729, "Lon": 16.4428, "Desc": "Hòn đảo tràn ngập nắng mặt trời, các cánh đồng oải hương thơm mát và bến cảng du thuyền sang trọng."},

    # ── Malaysia ──
    {"Name": "Kuala Lumpur Petronas Towers", "Country": "Malaysia", "Type": "Urban", "Cost": 60, "Season": "Spring", "Rating": 4.7, "Visitors": 8.0, "UNESCO": "No", "Lat": 3.1578, "Lon": 101.7120, "Desc": "Tháp đôi chọc trời mang tính biểu tượng của Malaysia với cầu treo bầu trời skybridge nối liền hai tòa tháp."},
    {"Name": "Penang Georgetown Heritage Art", "Country": "Malaysia", "Type": "Cultural", "Cost": 40, "Season": "Winter", "Rating": 4.7, "Visitors": 3.0, "UNESCO": "Yes", "Lat": 5.4141, "Lon": 100.3288, "Desc": "Khu phố cổ đa văn hóa nổi tiếng với các bức tranh tường 3D sống động và thiên đường ẩm thực đường phố."},
    {"Name": "Langkawi Cable Car & SkyBridge", "Country": "Malaysia", "Type": "Adventure", "Cost": 75, "Season": "Winter", "Rating": 4.6, "Visitors": 2.2, "UNESCO": "No", "Lat": 6.3500, "Lon": 99.8000, "Desc": "Tuyến cáp treo siêu dốc leo lên đỉnh núi Machinchang đi bộ trên cây cầu treo cong vắt giữa không trung."},
    {"Name": "Kota Kinabalu Nature Trekking", "Country": "Malaysia", "Type": "Mountain", "Cost": 90, "Season": "Summer", "Rating": 4.8, "Visitors": 0.7, "UNESCO": "Yes", "Lat": 6.0150, "Lon": 116.5390, "Desc": "Chinh phục đỉnh núi Kinabalu cao hơn 4000 mét thuộc công viên quốc gia đa dạng sinh học hàng đầu."},

    # ── Philippines ──
    {"Name": "Boracay Island White Beach", "Country": "Philippines", "Type": "Beach", "Cost": 70, "Season": "Winter", "Rating": 4.8, "Visitors": 1.9, "UNESCO": "No", "Lat": 11.9674, "Lon": 121.9248, "Desc": "Bãi biển cát trắng mịn dài 4km nước nông trong vắt, nổi tiếng với các hoạt động lướt ván buồm, chèo thuyền."},
    {"Name": "El Nido Bacuit Bay Islands", "Country": "Philippines", "Type": "Nature", "Cost": 85, "Season": "Spring", "Rating": 4.9, "Visitors": 0.9, "UNESCO": "No", "Lat": 11.1953, "Lon": 119.4182, "Desc": "Những hòn đảo đá vôi dựng đứng che chở cho các phá nước (lagoon) xanh màu ngọc bích hoang sơ kỳ vĩ."},
    {"Name": "Chocolate Hills Bohol Adventure", "Country": "Philippines", "Type": "Nature", "Cost": 55, "Season": "Spring", "Rating": 4.6, "Visitors": 1.2, "UNESCO": "No", "Lat": 9.8254, "Lon": 124.1684, "Desc": "Hơn 1200 ngọn đồi hình nón đối xứng hoàn hảo chuyển màu nâu socola khi mùa khô đến."},
    {"Name": "Intramuros Walled City Manila", "Country": "Philippines", "Type": "Cultural", "Cost": 50, "Season": "Winter", "Rating": 4.5, "Visitors": 2.5, "UNESCO": "No", "Lat": 14.5896, "Lon": 120.9747, "Desc": "Khu thành trì Tây Ban Nha lịch sử xây dựng từ thế kỷ 16 với pháo đài Fort Santiago cổ kính."},

    # ── Cambodia ──
    {"Name": "Angkor Wat Heritage Park", "Country": "Cambodia", "Type": "Cultural", "Cost": 50, "Season": "Winter", "Rating": 4.9, "Visitors": 4.0, "UNESCO": "Yes", "Lat": 13.4125, "Lon": 103.8670, "Desc": "Kỳ quan đền Angkor cổ kính và bí ẩn bao bọc trong rễ cây cổ thụ của khu di tích lịch sử vĩ đại nhất Khmer."},
    {"Name": "Phnom Penh Palace & Silver Pagoda", "Country": "Cambodia", "Type": "Cultural", "Cost": 40, "Season": "Winter", "Rating": 4.5, "Visitors": 1.3, "UNESCO": "No", "Lat": 11.5621, "Lon": 104.9151, "Desc": "Hoàng cung lộng lẫy kiến trúc Khmer truyền thống nổi bật với ngôi chùa Bạc lấp lánh hàng nghìn viên gạch bạc."},
    {"Name": "Koh Rong Tropical Beaches", "Country": "Cambodia", "Type": "Beach", "Cost": 60, "Season": "Winter", "Rating": 4.7, "Visitors": 0.8, "UNESCO": "No", "Lat": 10.4282, "Lon": 103.2207, "Desc": "Thiên đường đảo ngập tràn bãi cát hoang sơ, nước biển lặng sóng lấp lánh sinh vật phát quang sinh học ban đêm."},

    # ── Laos ──
    {"Name": "Luang Prabang Heritage Town", "Country": "Laos", "Type": "Cultural", "Cost": 35, "Season": "Winter", "Rating": 4.7, "Visitors": 0.7, "UNESCO": "Yes", "Lat": 19.8896, "Lon": 102.1347, "Desc": "Thị trấn yên bình giao thoa kiến trúc thuộc địa Pháp và đền chùa cổ kính, nổi tiếng với lễ khất thực sáng sớm."},
    {"Name": "Vang Vieng Karst Nature Tour", "Country": "Laos", "Type": "Adventure", "Cost": 30, "Season": "Winter", "Rating": 4.4, "Visitors": 0.5, "UNESCO": "No", "Lat": 18.9242, "Lon": 102.4468, "Desc": "Thị trấn phiêu lưu nằm bên sông Nam Song với hoạt động trượt ống tubing, chèo kayak và leo hang động đá vôi."},
    {"Name": "Kuang Si Turquoise Waterfalls", "Country": "Laos", "Type": "Nature", "Cost": 25, "Season": "Winter", "Rating": 4.8, "Visitors": 0.9, "UNESCO": "No", "Lat": 19.7483, "Lon": 101.9922, "Desc": "Thác nước nhiều tầng đổ xuống những hồ chứa tự nhiên màu xanh ngọc bích tuyệt đẹp giữa rừng nhiệt đới."},

    # ── Myanmar ──
    {"Name": "Bagan Hot Air Balloon Valley", "Country": "Myanmar", "Type": "Cultural", "Cost": 45, "Season": "Winter", "Rating": 4.9, "Visitors": 0.5, "UNESCO": "Yes", "Lat": 21.1717, "Lon": 94.8585, "Desc": "Ngắm hoàng hôn tuyệt mỹ trên vùng đồng bằng Bagan chứa hàng nghìn ngôi đền tháp gạch đỏ linh thiêng."},
    {"Name": "Inle Lake Fisherman Villages", "Country": "Myanmar", "Type": "Cultural", "Cost": 48, "Season": "Winter", "Rating": 4.6, "Visitors": 0.3, "UNESCO": "No", "Lat": 20.5890, "Lon": 96.9304, "Desc": "Khám phá cuộc sống của người dân Intha trên các khu vườn nổi và kỹ thuật chèo thuyền bằng một chân kỳ diệu."},
    {"Name": "Shwedagon Pagoda Yangon", "Country": "Myanmar", "Type": "Cultural", "Cost": 40, "Season": "Winter", "Rating": 4.8, "Visitors": 1.1, "UNESCO": "No", "Lat": 16.7984, "Lon": 96.1497, "Desc": "Ngôi đại bảo tháp dát vàng rực rỡ cao 99 mét lưu giữ những sợi tóc linh thiêng của Đức Phật."},

    # ── Sri Lanka ──
    {"Name": "Sigiriya Ancient Lion Rock", "Country": "Sri Lanka", "Type": "Cultural", "Cost": 55, "Season": "Spring", "Rating": 4.8, "Visitors": 1.0, "UNESCO": "Yes", "Lat": 7.9570, "Lon": 80.7600, "Desc": "Cung điện cổ kính xây trên đỉnh một tảng đá núi lửa khổng lồ vách thẳng đứng đầy huyền bí giữa thảm rừng."},
    {"Name": "Ella Train & Nine Arch Bridge", "Country": "Sri Lanka", "Type": "Nature", "Cost": 35, "Season": "Spring", "Rating": 4.7, "Visitors": 0.8, "UNESCO": "No", "Lat": 6.8724, "Lon": 81.0478, "Desc": "Hành trình xe lửa ngắm đồi chè xanh mướt và check-in cây cầu chín nhịp kiểu thuộc địa độc đáo."},
    {"Name": "Temple of the Tooth Kandy", "Country": "Sri Lanka", "Type": "Cultural", "Cost": 45, "Season": "Spring", "Rating": 4.6, "Visitors": 1.4, "UNESCO": "Yes", "Lat": 7.2936, "Lon": 80.6413, "Desc": "Đền thờ linh thiêng cất giữ xá lợi răng của Đức Phật, trung tâm tôn giáo lớn của Sri Lanka."},

    # ── Nepal ──
    {"Name": "Kathmandu Durbar Square Temples", "Country": "Nepal", "Type": "Cultural", "Cost": 30, "Season": "Autumn", "Rating": 4.6, "Visitors": 0.6, "UNESCO": "Yes", "Lat": 27.7008, "Lon": 85.3001, "Desc": "Tổ hợp quảng trường hoàng cung cũ với kiến trúc đền tháp nhiều tầng bằng gỗ chạm khắc tuyệt mỹ."},
    {"Name": "Everest Base Camp Mountain Trek", "Country": "Nepal", "Type": "Mountain", "Cost": 220, "Season": "Autumn", "Rating": 4.9, "Visitors": 0.1, "UNESCO": "No", "Lat": 28.0072, "Lon": 86.8556, "Desc": "Chinh phục cung đường leo núi ngoạn mục ngắm đỉnh Everest hùng vĩ phủ tuyết trắng xóa đầy thử thách."},
    {"Name": "Pokhara Phewa Lake Resort", "Country": "Nepal", "Type": "Mountain", "Cost": 40, "Season": "Autumn", "Rating": 4.8, "Visitors": 0.9, "UNESCO": "No", "Lat": 28.2096, "Lon": 83.9581, "Desc": "Thành phố nghỉ dưỡng thanh bình soi bóng xuống mặt hồ tĩnh lặng dưới bóng dãy Himalaya sừng sững."},

    # ── Taiwan ──
    {"Name": "Taipei 101 Observatory", "Country": "Taiwan", "Type": "Urban", "Cost": 80, "Season": "Autumn", "Rating": 4.7, "Visitors": 6.8, "UNESCO": "No", "Lat": 25.0340, "Lon": 121.5645, "Desc": "Tòa nhà chọc trời từng cao nhất thế giới sở hữu đài quan sát ngắm cảnh tuyệt hảo và con lắc cản gió khổng lồ."},
    {"Name": "Jiufen Old Street Lanterns", "Country": "Taiwan", "Type": "Cultural", "Cost": 65, "Season": "Spring", "Rating": 4.6, "Visitors": 3.2, "UNESCO": "No", "Lat": 25.1099, "Lon": 121.8452, "Desc": "Thị trấn cổ sườn núi lãng mạn với đèn lồng đỏ, trà quán cổ kính truyền cảm hứng cho phim Spirited Away."},
    {"Name": "Taroko Marble Gorge National Park", "Country": "Taiwan", "Type": "Nature", "Cost": 75, "Season": "Spring", "Rating": 4.8, "Visitors": 1.9, "UNESCO": "No", "Lat": 24.1624, "Lon": 121.6214, "Desc": "Hẻm núi đá cẩm thạch khổng lồ bị chia cắt bởi dòng sông xanh ngọc xiết chảy đầy ấn tượng."},

    # ── Mongolia ──
    {"Name": "Gobi Desert Singing Dunes", "Country": "Mongolia", "Type": "Adventure", "Cost": 75, "Season": "Summer", "Rating": 4.8, "Visitors": 0.1, "UNESCO": "No", "Lat": 43.6000, "Lon": 104.1000, "Desc": "Cưỡi lạc đà hai bướu vượt sa mạc Gobi hoang vu và cồn cát hát Khongoryn Els vang dội trong gió chiều."},
    {"Name": "Terelj National Park Ger Camp", "Country": "Mongolia", "Type": "Nature", "Cost": 65, "Season": "Summer", "Rating": 4.6, "Visitors": 0.3, "UNESCO": "No", "Lat": 47.9856, "Lon": 107.4411, "Desc": "Nghỉ ngơi trong lều tròn Ger truyền thống và hòa mình vào cuộc sống cưỡi ngựa chăn thả của thảo nguyên."},

    # ── Kazakhstan ──
    {"Name": "Almaty Charyn Canyon", "Country": "Kazakhstan", "Type": "Nature", "Cost": 70, "Season": "Autumn", "Rating": 4.7, "Visitors": 0.3, "UNESCO": "No", "Lat": 43.3551, "Lon": 79.0833, "Desc": "Hẻm núi đá đỏ tráng lệ được tạo hình gió cát tự nhiên kỳ vĩ được mệnh danh Grand Canyon châu Á."},
    {"Name": "Astana Bayterek Tower", "Country": "Kazakhstan", "Type": "City", "Cost": 80, "Season": "Summer", "Rating": 4.5, "Visitors": 0.8, "UNESCO": "No", "Lat": 51.1283, "Lon": 71.4304, "Desc": "Đài quan sát hình dáng cây đời nâng quả trứng vàng huyền thoại giữa thủ đô hiện đại siêu thực Astana."},

    # ── Colombia ──
    {"Name": "Cartagena Spanish Walled City", "Country": "Colombia", "Type": "Historical", "Cost": 85, "Season": "Winter", "Rating": 4.8, "Visitors": 1.6, "UNESCO": "Yes", "Lat": 10.3910, "Lon": -75.4794, "Desc": "Phố cổ Tây Ban Nha quyến rũ bên biển Caribê nổi bật với các ban công đầy hoa rực rỡ và tường thành đá."},
    {"Name": "Coffee Triangle Plantation Tour", "Country": "Colombia", "Type": "Nature", "Cost": 70, "Season": "Autumn", "Rating": 4.8, "Visitors": 0.8, "UNESCO": "Yes", "Lat": 5.0689, "Lon": -75.5174, "Desc": "Tham quan đồi chè cà phê trập trùng của vùng Andes cổ kính và chiêm ngưỡng những cây cọ sáp Cocora siêu cao."},

    # ── Chile ──
    {"Name": "Easter Island Rapa Nui Moai", "Country": "Chile", "Type": "Cultural", "Cost": 170, "Season": "Spring", "Rating": 4.9, "Visitors": 0.1, "UNESCO": "Yes", "Lat": -27.1127, "Lon": -109.3497, "Desc": "Khám phá các tượng đá đầu người Moai bí ẩn khổng lồ xếp dọc bờ biển hòn đảo biệt lập giữa Thái Bình Dương."},
    {"Name": "Torres del Paine National Park", "Country": "Chile", "Type": "Mountain", "Cost": 140, "Season": "Summer", "Rating": 4.9, "Visitors": 0.3, "UNESCO": "Yes", "Lat": -50.9423, "Lon": -72.9673, "Desc": "Kỳ quan thiên nhiên của vùng Patagonia Nam Cực với những tháp đá cao vút sương mờ soi bóng xuống hồ băng xanh."},

    # ── Ecuador ──
    {"Name": "Galapagos Islands Wildlife cruise", "Country": "Ecuador", "Type": "Nature", "Cost": 270, "Season": "Spring", "Rating": 4.9, "Visitors": 0.2, "UNESCO": "Yes", "Lat": -0.8293, "Lon": -90.9821, "Desc": "Thiên đường sinh học hoang dã với cự đà biển, rùa khổng lồ, chim hải âu chân xanh không hề sợ con người."},

    # ── Costa Rica ──
    {"Name": "Arenal Volcano Hot Springs", "Country": "Costa Rica", "Type": "Adventure", "Cost": 115, "Season": "Winter", "Rating": 4.8, "Visitors": 1.3, "UNESCO": "No", "Lat": 10.4678, "Lon": -84.6427, "Desc": "Khám phá núi lửa hình nón Arenal hùng vĩ, ngâm mình trong suối nước nóng địa nhiệt rừng mưa nhiệt đới."},

    # ── Panama ──
    {"Name": "Panama Canal Miraflores Locks", "Country": "Panama", "Type": "Urban", "Cost": 100, "Season": "Winter", "Rating": 4.5, "Visitors": 1.0, "UNESCO": "No", "Lat": 8.9819, "Lon": -79.5193, "Desc": "Trung tâm du khách ngắm nhìn các tàu container siêu trọng được nâng hạ qua kênh đào nối liền hai đại dương."},

    # ── Cuba ──
    {"Name": "Old Havana Classic Cars", "Country": "Cuba", "Type": "Historical", "Cost": 70, "Season": "Winter", "Rating": 4.7, "Visitors": 1.9, "UNESCO": "Yes", "Lat": 23.1136, "Lon": -82.3666, "Desc": "Trải nghiệm đi taxi cổ mui trần rực rỡ sắc màu qua những quảng trường cổ kính Baroque đượm màu thời gian."},
    {"Name": "Varadero Beach Resorts", "Country": "Cuba", "Type": "Beach", "Cost": 105, "Season": "Winter", "Rating": 4.6, "Visitors": 1.4, "UNESCO": "No", "Lat": 23.1539, "Lon": -81.2514, "Desc": "Mũi đất biển cát trắng phau trải dài 20km ngập tràn các resort trọn gói thư giãn bên làn nước xanh ngọc."},

    # ── Jamaica ──
    {"Name": "Negril Cliffs & Seven Mile Beach", "Country": "Jamaica", "Type": "Beach", "Cost": 120, "Season": "Winter", "Rating": 4.7, "Visitors": 1.3, "UNESCO": "No", "Lat": 18.2831, "Lon": -78.3496, "Desc": "Check-in bãi biển tuyệt đẹp và trải nghiệm nhảy cầu Rick's Cafe mạo hiểm trên giai điệu reggae sôi động."},

    # ── Fiji ──
    {"Name": "Yasawa Islands Coral Reefs", "Country": "Fiji", "Type": "Beach", "Cost": 270, "Season": "Winter", "Rating": 4.9, "Visitors": 0.5, "UNESCO": "No", "Lat": -17.2000, "Lon": 177.2500, "Desc": "Quần đảo san hô thiên đường của Thái Bình Dương với các căn villa gỗ nổi trên biển trong vắt như gương."},

    # ── Samoa ──
    {"Name": "To Sua Ocean Trench Swim", "Country": "Samoa", "Type": "Nature", "Cost": 75, "Season": "Summer", "Rating": 4.9, "Visitors": 0.2, "UNESCO": "No", "Lat": -14.0531, "Lon": -171.5204, "Desc": "Hố bơi tự nhiên khổng lồ sâu 30m giữa lòng đá núi lửa, phủ đầy cỏ cây xanh tốt đâm nhánh sát nước biển."},

    # ── Tanzania ──
    {"Name": "Serengeti National Park Safari", "Country": "Tanzania", "Type": "Wildlife", "Cost": 210, "Season": "Summer", "Rating": 4.9, "Visitors": 0.5, "UNESCO": "Yes", "Lat": -2.1540, "Lon": 34.6857, "Desc": "Hành trình xe jeep chiêm ngưỡng cuộc di cư vĩ đại của hàng triệu linh dương đầu bò và cảnh đi săn của sư tử."},
    {"Name": "Mount Kilimanjaro Summit Climb", "Country": "Tanzania", "Type": "Mountain", "Cost": 250, "Season": "Winter", "Rating": 4.8, "Visitors": 0.1, "UNESCO": "Yes", "Lat": -3.0674, "Lon": 37.3556, "Desc": "Hành trình leo núi chinh phục đỉnh Uhuru cao 5895m tuyết phủ quanh năm được mệnh danh nóc nhà châu Phi."},

    # ── Madagascar ──
    {"Name": "Morondava Avenue of Baobabs", "Country": "Madagascar", "Type": "Nature", "Cost": 55, "Season": "Spring", "Rating": 4.8, "Visitors": 0.2, "UNESCO": "No", "Lat": -20.3015, "Lon": 44.4184, "Desc": "Con đường đất đỏ nổi tiếng được che bóng bởi hàng chục cây Baobab khổng lồ hơn 800 tuổi vươn tán độc đáo."},

    # ── Seychelles ──
    {"Name": "La Digue Anse Source Beach", "Country": "Seychelles", "Type": "Beach", "Cost": 270, "Season": "Spring", "Rating": 4.9, "Visitors": 0.3, "UNESCO": "No", "Lat": -4.3713, "Lon": 55.8344, "Desc": "Bãi biển biểu tượng thế giới nổi bật với cát hồng mịn, rặng dừa nghiêng bóng và tảng đá granite nhẵn bóng khổng lồ."},

    # ── Mauritius ──
    {"Name": "Chamarel Coloured Earth Dunes", "Country": "Mauritius", "Type": "Nature", "Cost": 90, "Season": "Winter", "Rating": 4.7, "Visitors": 0.9, "UNESCO": "No", "Lat": -20.4431, "Lon": 57.3739, "Desc": "Khu cồn cát uốn lượn lấp lánh 7 màu sắc địa chất độc đáo nổi tiếng giữa thảo nguyên xanh."},

    # ── Additions to existing countries ──
    {"Name": "Sapa Terrace Rice Fields", "Country": "Vietnam", "Type": "Mountain", "Cost": 40, "Season": "Autumn", "Rating": 4.8, "Visitors": 2.5, "UNESCO": "No", "Lat": 22.3364, "Lon": 103.8438, "Desc": "Chiêm ngưỡng những ruộng bậc thang chín vàng óng trập trùng quanh mây núi Fansipan thơ mộng sương mù."},
    {"Name": "Phu Quoc Sunset Beach", "Country": "Vietnam", "Type": "Beach", "Cost": 75, "Season": "Winter", "Rating": 4.7, "Visitors": 4.5, "UNESCO": "No", "Lat": 10.2625, "Lon": 103.9575, "Desc": "Hòn đảo ngọc phía nam Việt Nam nổi tiếng với hoàng hôn rực đỏ, cát trắng, sao biển và hải sản tươi ngon."},
    {"Name": "Trang An Scenic Landscape", "Country": "Vietnam", "Type": "Cultural", "Cost": 50, "Season": "Spring", "Rating": 4.8, "Visitors": 3.2, "UNESCO": "Yes", "Lat": 20.2539, "Lon": 105.8872, "Desc": "Quần thể danh thắng di sản kép thế giới với dòng sông xanh biếc uốn lượn qua các hang động karst xuyên thủy sâu thăm thẳm."},
    {"Name": "Kyoto Fushimi Inari Shrine", "Country": "Japan", "Type": "Cultural", "Cost": 90, "Season": "Autumn", "Rating": 4.9, "Visitors": 9.5, "UNESCO": "Yes", "Lat": 34.9671, "Lon": 135.7727, "Desc": "Đường mòn leo núi linh thiêng lợp bởi hơn 10,000 cổng Torri màu đỏ son rực rỡ uốn lượn trên núi rừng."},
    {"Name": "Osaka Dotonbori Street Food", "Country": "Japan", "Type": "Urban", "Cost": 85, "Season": "Spring", "Rating": 4.7, "Visitors": 8.0, "UNESCO": "No", "Lat": 34.6687, "Lon": 135.5013, "Desc": "Khu phố đêm sầm uất ngợp ánh đèn neon, biển hiệu 3D nổi và thiên đường các món ăn đường phố takoyaki."},
    {"Name": "Grand Canyon South Rim", "Country": "USA", "Type": "Mountain", "Cost": 150, "Season": "Spring", "Rating": 4.9, "Visitors": 6.0, "UNESCO": "Yes", "Lat": 36.0544, "Lon": -112.1401, "Desc": "Hẻm núi đá đỏ cắt xẻ kỳ vĩ khổng lồ kiến tạo hàng triệu năm bởi dòng sông Colorado vĩ đại."},
    {"Name": "New York Times Square Neon", "Country": "USA", "Type": "Urban", "Cost": 220, "Season": "Winter", "Rating": 4.6, "Visitors": 15.0, "UNESCO": "No", "Lat": 40.7580, "Lon": -73.9855, "Desc": "Trái tim rực sáng neon của New York với các buổi diễn kịch Broadway đỉnh cao và không khí đô thị náo nhiệt."},
    {"Name": "Louvre Art Museum Paris", "Country": "France", "Type": "Cultural", "Cost": 130, "Season": "Spring", "Rating": 4.8, "Visitors": 9.6, "UNESCO": "Yes", "Lat": 48.8606, "Lon": 2.3376, "Desc": "Bảo tàng nghệ thuật lớn nhất thế giới, nơi lưu trữ bức tranh nàng Mona Lisa và kim tự tháp kính nổi tiếng."},
    {"Name": "French Riviera Nice Beaches", "Country": "France", "Type": "Beach", "Cost": 180, "Season": "Summer", "Rating": 4.7, "Visitors": 4.1, "UNESCO": "No", "Lat": 43.7102, "Lon": 7.2620, "Desc": "Bờ biển xanh ngọc Địa Trung Hải trải dài tuyệt đẹp với lối đi dạo Promenade des Anglais ngập tràn ánh nắng."},
    {"Name": "Zhangjiajie Avatar Mountains", "Country": "China", "Type": "Mountain", "Cost": 90, "Season": "Autumn", "Rating": 4.9, "Visitors": 4.5, "UNESCO": "Yes", "Lat": 29.3140, "Lon": 110.4326, "Desc": "Các cột đá sa thạch khổng lồ vươn thẳng lên trời mây mờ che phủ, cảm hứng cho phim giả tưởng nổi tiếng Avatar."},
    {"Name": "Shanghai The Bund Skyline", "Country": "China", "Type": "Urban", "Cost": 80, "Season": "Autumn", "Rating": 4.7, "Visitors": 10.0, "UNESCO": "No", "Lat": 31.2397, "Lon": 121.4898, "Desc": "Ngắm sự tương phản tuyệt mỹ giữa bến cảng kiến trúc cổ phương Tây và các siêu tháp chọc trời Lục Gia Chủy."},
    {"Name": "Chiang Mai Lantern Festival", "Country": "Thailand", "Type": "Cultural", "Cost": 55, "Season": "Autumn", "Rating": 4.8, "Visitors": 2.8, "UNESCO": "No", "Lat": 18.7883, "Lon": 98.9853, "Desc": "Lễ hội thả đèn trời Yi Peng lung linh huyền ảo với hàng vạn ngọn đèn giấy bay lên trời đêm cố đô."},
    {"Name": "Phuket Patong Beach Party", "Country": "Thailand", "Type": "Beach", "Cost": 75, "Season": "Winter", "Rating": 4.5, "Visitors": 5.4, "UNESCO": "No", "Lat": 7.8920, "Lon": 98.2956, "Desc": "Bãi biển dài rực rỡ với các môn thể thao nước ban ngày và khu phố đi bộ Bangla Road sôi động ban đêm."}
]

def generate():
    print("\n[GENERATE] Starting large travel dataset generation...")
    
    # 1. Load current destinations
    current_records = db_storage.load_destinations()
    
    # Fallback to CSV if MongoDB is empty
    csv_path = Path(__file__).parent.parent / "data" / "processed" / "destinations_clustered.csv"
    if not current_records and csv_path.exists():
        df_csv = pd.read_csv(csv_path)
        current_records = df_csv.astype(object).where(pd.notnull(df_csv), None).to_dict('records')
        print(f"[GENERATE] Loaded {len(current_records)} destinations from CSV")
        
    df_current = pd.DataFrame(current_records)
    existing_names = set()
    if not df_current.empty and 'Destination Name' in df_current.columns:
        existing_names = set(df_current['Destination Name'].str.lower().tolist())
        
    max_id = 0
    if not df_current.empty and 'DestinationID' in df_current.columns:
        max_id = int(df_current['DestinationID'].max())
        
    added_destinations = []
    
    # Process destinations to add
    for i, dest in enumerate(NEW_DESTINATIONS_DATA):
        name = dest["Name"]
        if name.lower() in existing_names:
            continue
            
        country = dest["Country"]
        continent = ""
        
        # Get country metadata
        c_meta = COUNTRY_METADATA.get(country)
        if c_meta:
            continent = c_meta["region"]
            flag = c_meta["flag"]
            region = c_meta["region"]
            subregion = c_meta["subregion"]
            currency = c_meta["currency"]
            symbol = c_meta["symbol"]
            languages = c_meta["languages"]
            capital = c_meta["capital"]
            timezone = c_meta["timezone"]
            pop = c_meta["pop"]
            area = c_meta["area"]
            alpha2 = c_meta["alpha2"]
            alpha3 = c_meta["alpha3"]
            borders = c_meta["borders"]
            c_lat = c_meta["lat"]
            c_lon = c_meta["lon"]
        else:
            # Fallback to existing country if present in existing dataset
            match_country = df_current[df_current['Country'] == country]
            if not match_country.empty:
                row = match_country.iloc[0]
                continent = row.get('Continent', 'Asia')
                flag = row.get('country_flag', '📍')
                region = row.get('country_region', continent)
                subregion = row.get('country_subregion', continent)
                currency = row.get('country_currency', 'USD')
                symbol = row.get('country_currency_symbol', '$')
                languages = row.get('country_languages', 'English')
                capital = row.get('country_capital', 'Capital')
                timezone = row.get('country_timezone', 'UTC')
                pop = int(row.get('country_population', 1000000))
                area = int(row.get('country_area', 50000))
                alpha2 = row.get('country_alpha2', country[:2].upper())
                alpha3 = row.get('country_alpha3', country[:3].upper())
                borders = row.get('country_borders', '')
                c_lat = float(row.get('country_latitude', dest["Lat"]))
                c_lon = float(row.get('country_longitude', dest["Lon"]))
            else:
                print(f"[WARNING] Country metadata not found for {country}. Skipping.")
                continue
                
        # Prep destination record fields
        dest_type = dest["Type"]
        avg_cost = dest["Cost"]
        best_season = dest["Season"]
        avg_rating = dest["Rating"]
        visitors = dest["Visitors"]
        unesco = dest["UNESCO"]
        
        # Broader type mapping
        b_type = "Culture" if dest_type in ["Cultural", "Historical", "Urban", "City", "Religious"] else "Nature"
        
        # Cost Category
        if avg_cost < 80:
            cost_cat = "Budget"
        elif avg_cost < 150:
            cost_cat = "Moderate"
        elif avg_cost < 250:
            cost_cat = "Expensive"
        else:
            cost_cat = "Luxury"
            
        next_id = max_id + len(added_destinations) + 1
        
        # Synthetic numeric stats for indexes (Numbeo mock)
        base_col = 40.0
        if cost_cat == "Budget":
            base_col = np.random.uniform(30.0, 50.0)
        elif cost_cat == "Moderate":
            base_col = np.random.uniform(50.0, 75.0)
        elif cost_cat == "Expensive":
            base_col = np.random.uniform(75.0, 100.0)
        else:
            base_col = np.random.uniform(100.0, 130.0)
            
        col_index = round(base_col, 2)
        rent_idx = round(base_col * 0.5, 2)
        col_plus_rent = round(base_col * 0.75, 2)
        groceries = round(base_col * 0.9, 2)
        restaurant = round(base_col * 0.95, 2)
        purchasing = round(150.0 - base_col * 0.8, 2)
        pollution = round(np.random.uniform(10.0, 55.0), 2)
        
        new_dest = {
            "Destination Name": name,
            "Country": country,
            "Continent": continent,
            "Type": dest_type,
            "Avg Cost (USD/day)": float(avg_cost),
            "Best Season": best_season,
            "Avg Rating": float(avg_rating),
            "Annual Visitors (M)": float(visitors),
            "UNESCO Site": unesco,
            "Broader_Type": b_type,
            "Cost_Category": cost_cat,
            "country_flag": flag,
            "country_region": region,
            "country_subregion": subregion,
            "country_currency": currency,
            "country_currency_symbol": symbol,
            "country_languages": languages,
            "country_capital": capital,
            "country_timezone": timezone,
            "country_population": int(pop),
            "country_area": int(area),
            "country_alpha2": alpha2,
            "country_alpha3": alpha3,
            "country_borders": borders,
            "country_latitude": float(c_lat),
            "country_longitude": float(c_lon),
            "DestinationID": int(next_id),
            "Popularity": "Very High" if visitors > 5.0 else "High" if visitors > 2.0 else "Medium",
            "BestTimeToVisit": f"{best_season} months",
            "destination": int(next_id),
            "avg_review_rating": float(avg_rating),
            "review_count": int(np.random.randint(1000, 15000)),
            "popularity_score": round(float(avg_rating / 5.0 + visitors / 20.0), 2),
            "cost_of_living_index": col_index,
            "rent_index": rent_idx,
            "cost_of_living_plus_rent_index": col_plus_rent,
            "groceries_index": groceries,
            "restaurant_price_index": restaurant,
            "local_purchasing_power_index": purchasing,
            "air_pollution_avg": pollution,
            "air_pollution_2023": pollution,
            "destination_latitude": float(dest["Lat"]),
            "destination_longitude": float(dest["Lon"]),
            "destination_budget_level": cost_cat,
            "Cluster": 0, # Se duoc phan cum boi KMeans
            "Description": dest["Desc"]
        }
        added_destinations.append(new_dest)
        
    print(f"[GENERATE] Prepared {len(added_destinations)} new destinations.")
    
    if not added_destinations:
        print("[GENERATE] No new destinations to add.")
        return True
        
    # Append and update dataframe
    df_updated_dests = pd.concat([df_current, pd.DataFrame(added_destinations)], ignore_index=True)
    
    # Save to MongoDB
    if db_storage.is_connected():
        db_storage.save_destinations(df_updated_dests)
    else:
        print("[WARNING] MongoDB not connected, cannot save destinations to DB.")
        
    # Save to CSV
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    data_dir.mkdir(parents=True, exist_ok=True)
    df_updated_dests.to_csv(data_dir / "destinations_clustered.csv", index=False)
    df_updated_dests.to_csv(data_dir / "destinations_clean.csv", index=False)
    print(f"[GENERATE] Saved destinations to destinations_clustered.csv and destinations_clean.csv.")
    
    # ── 2. MO RONG GIAO DICH ──
    print("\n[TRANSACTIONS] Expanding transactions binary matrix...")
    transactions = db_storage.load_transactions()
    if not transactions and (data_dir / "transactions.csv").exists():
        df_trans_csv = pd.read_csv(data_dir / "transactions.csv")
        transactions = df_trans_csv.to_dict('records')
        print(f"[TRANSACTIONS] Loaded {len(transactions)} from CSV.")
        
    if not transactions:
        print("[ERROR] No existing transactions found. Cannot generate rules.")
        return False
        
    df_trans = pd.DataFrame(transactions)
    
    # Chung ta se tao 150 hang giao dich cho moi quoc gia MOI duoc them vao.
    # Tong so quoc gia moi la 36.
    # Tong so giao dich moi = 36 * 150 = 5,400 hang!
    # Hay them chung vao. Truoc tien, dam bao cac cot cho tat ca quoc gia da ton tai trong df_trans
    unique_new_countries = list(set([d["Country"] for d in added_destinations]))
    
    for c in unique_new_countries:
        new_col = f"Country:{c}"
        if new_col not in df_trans.columns:
            df_trans[new_col] = False
            
    # Dong thoi dam bao tat ca cac loai hinh deu duoc the hien
    unique_new_types = list(set([d["Type"] for d in added_destinations]))
    for t in unique_new_types:
        new_col = f"Type:{t}"
        if new_col not in df_trans.columns:
            df_trans[new_col] = False
            
    # Tao cac hang giao dich
    new_rows = []
    np.random.seed(42)
    
    # Anh xa ten quoc gia voi danh sach cac diem den cua no
    country_dest_map = {}
    for d in added_destinations:
        country_dest_map.setdefault(d["Country"], []).append(d)
        
    for c in unique_new_countries:
        c_dests = country_dest_map.get(c, [])
        if not c_dests:
            continue
            
        # Tao 150 giao dich cho quoc gia nay
        for _ in range(150):
            # Chon ngau nhien mot diem den cua quoc gia nay de the hien cac dac trung
            rep_dest = np.random.choice(c_dests)
            
            # Tao mot hang trong cho tat ca cac cot trong df_trans voi gia tri False
            row = {col: False for col in df_trans.columns}
            
            # Thiet lap cac dac trung muc tieu
            row[f"Country:{c}"] = True
            row[f"Continent:{rep_dest['Continent']}"] = True
            row[f"Cost:{rep_dest['Cost_Category']}"] = True
            row[f"Season:{rep_dest['Best Season']}"] = True
            row[f"Type:{rep_dest['Type']}"] = True
            
            # Dac trung Dia diem UNESCO
            if rep_dest["UNESCO Site"] == "Yes" or np.random.rand() > 0.5:
                row["Heritage:UNESCO"] = True
                
            # Cac luat ve chat luong
            rating = rep_dest["Avg Rating"]
            if rating >= 4.7:
                row["Quality:Excellent"] = True if np.random.rand() > 0.3 else False
                row["Quality:Good"] = not row["Quality:Excellent"]
            else:
                row["Quality:Good"] = True if np.random.rand() > 0.4 else False
                row["Quality:Average"] = not row["Quality:Good"]
                
            new_rows.append(row)
            
    # Ket hop cac giao dich hien co va moi
    df_new_trans = pd.DataFrame(new_rows)
    df_updated_trans = pd.concat([df_trans, df_new_trans], ignore_index=True).fillna(False)
    
    # Luu cac giao dich
    if db_storage.is_connected():
        db_storage.save_transactions(df_updated_trans)
    else:
        print("[WARNING] MongoDB not connected, cannot save transactions to DB.")
        
    df_updated_trans.to_csv(data_dir / "transactions.csv", index=False)
    print(f"[TRANSACTIONS] Saved updated transactions matrix of shape {df_updated_trans.shape} (added {len(df_new_trans)} rows).")
    
    print("\n[SUCCESS] Large travel dataset expansion completed successfully!")
    print(f"Total destinations: {len(df_updated_dests)} (added {len(added_destinations)})")
    print(f"Total countries: {df_updated_dests['Country'].nunique()}")
    print(f"Total transactions: {len(df_updated_trans)} (added {len(df_new_trans)})")
    print("Please trigger K-Means and Apriori Rule mining via the Admin Dashboard or command line to update results.")
    return True

if __name__ == "__main__":
    generate()
