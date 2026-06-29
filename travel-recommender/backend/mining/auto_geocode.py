# -*- coding: utf-8 -*-
"""
auto_geocode.py
===============
Tự động lấy tọa độ địa lý (lat/lon) cho các điểm đến du lịch
và metadata quốc gia (cờ, tiền tệ, múi giờ...) từ các API miễn phí.

Thay thế cho việc nhập thủ công trong generate_large_dataset.py.

Công nghệ sử dụng:
  - geopy + Nominatim (OpenStreetMap): Geocoding điểm đến → lat/lon
  - CountriesNow API (countriesnow.space): Metadata quốc gia (miễn phí, không cần key)
  - RateLimiter: Tuân thủ giới hạn 1 request/giây của Nominatim

Cách dùng:
  1. Chạy script để sinh ra file geocoded_data.json
  2. Dùng file đó trong generate_large_dataset.py thay vì hardcode

  python auto_geocode.py                        # geocode tất cả
  python auto_geocode.py --country "Vietnam"    # chỉ 1 quốc gia
  python auto_geocode.py --test                 # test 3 địa điểm
"""

import sys
import json
import time
import argparse
import requests
from pathlib import Path

# geopy đã có trong requirements.txt (geopy==2.4.0)
try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
except ImportError:
    print("[ERROR] Thiếu thư viện geopy. Chạy: pip install geopy")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────
# DANH SÁCH CÁC ĐIỂM ĐẾN CẦN GEOCODE
# Thêm địa điểm mới vào đây — không cần nhập tọa độ thủ công
# ─────────────────────────────────────────────────────────────
DESTINATIONS_TO_GEOCODE = [
    # Tên điểm đến đầy đủ để Nominatim tra cứu chính xác hơn
    # Format: {"name": "Tên hiển thị", "query": "Chuỗi tìm kiếm", "country": "Tên quốc gia"}
    {"name": "Oslo Fjords & Museum Peninsula",      "query": "Oslo, Norway",                        "country": "Norway"},
    {"name": "Tromsø Northern Lights Hunting",      "query": "Tromsø, Norway",                      "country": "Norway"},
    {"name": "Geirangerfjord Cruising",             "query": "Geirangerfjord, Norway",              "country": "Norway"},
    {"name": "Bergen Bryggen Wharf",                "query": "Bryggen, Bergen, Norway",             "country": "Norway"},
    {"name": "Lofoten Islands Scenic Tour",         "query": "Lofoten, Norway",                     "country": "Norway"},
    {"name": "Amsterdam Historic Canal Cruise",     "query": "Amsterdam, Netherlands",              "country": "Netherlands"},
    {"name": "Keukenhof Tulip Festival",            "query": "Keukenhof, Lisse, Netherlands",      "country": "Netherlands"},
    {"name": "Zaanse Schans Windmill Village",      "query": "Zaanse Schans, Netherlands",          "country": "Netherlands"},
    {"name": "Rotterdam Futuristic Architecture",   "query": "Rotterdam, Netherlands",              "country": "Netherlands"},
    {"name": "Giethoorn Village Without Roads",     "query": "Giethoorn, Netherlands",              "country": "Netherlands"},
    {"name": "Brussels Grand Place",                "query": "Grand Place, Brussels, Belgium",      "country": "Belgium"},
    {"name": "Bruges Medieval Canal Tour",          "query": "Bruges, Belgium",                     "country": "Belgium"},
    {"name": "Ghent Castle of the Counts",          "query": "Gravensteen, Ghent, Belgium",         "country": "Belgium"},
    {"name": "Antwerp Diamond District",            "query": "Antwerp, Belgium",                    "country": "Belgium"},
    {"name": "Vienna Schonbrunn Palace",            "query": "Schönbrunn Palace, Vienna, Austria",  "country": "Austria"},
    {"name": "Hallstatt Alpine Village",            "query": "Hallstatt, Austria",                  "country": "Austria"},
    {"name": "Salzburg Mozart Heritage",            "query": "Salzburg, Austria",                   "country": "Austria"},
    {"name": "Innsbruck Alpine Skiing",             "query": "Innsbruck, Austria",                  "country": "Austria"},
    {"name": "Lisbon Alfama & Tram 28",             "query": "Alfama, Lisbon, Portugal",            "country": "Portugal"},
    {"name": "Porto Douro Vineyard Valley",         "query": "Porto, Portugal",                     "country": "Portugal"},
    {"name": "Algarve Cliffs & Caves",              "query": "Algarve, Portugal",                   "country": "Portugal"},
    {"name": "Sintra Pena Palace",                  "query": "Pena Palace, Sintra, Portugal",       "country": "Portugal"},
    {"name": "Cliffs of Moher Coastal Walk",        "query": "Cliffs of Moher, Ireland",            "country": "Ireland"},
    {"name": "Dublin Guinness & Trinity College",   "query": "Dublin, Ireland",                     "country": "Ireland"},
    {"name": "Killarney Ring of Kerry Tour",        "query": "Killarney, Ireland",                  "country": "Ireland"},
    {"name": "Copenhagen Nyhavn Harbour",           "query": "Nyhavn, Copenhagen, Denmark",         "country": "Denmark"},
    {"name": "Tivoli Gardens Theme Park",           "query": "Tivoli Gardens, Copenhagen, Denmark", "country": "Denmark"},
    {"name": "Kronborg Castle Elsinore",            "query": "Kronborg Castle, Helsingør, Denmark", "country": "Denmark"},
    {"name": "Rovaniemi Santa Claus Village",       "query": "Rovaniemi, Finland",                  "country": "Finland"},
    {"name": "Helsinki Cathedral & Market",         "query": "Helsinki Cathedral, Helsinki, Finland","country": "Finland"},
    {"name": "Finnish Lakeland & Sauna Tour",       "query": "Lakeland, Finland",                   "country": "Finland"},
    {"name": "Reykjavik Blue Lagoon Spa",           "query": "Blue Lagoon, Iceland",                "country": "Iceland"},
    {"name": "Gullfoss Golden Waterfall",           "query": "Gullfoss, Iceland",                   "country": "Iceland"},
    {"name": "Reynisfjara Black Sand Beach",        "query": "Reynisfjara, Iceland",                "country": "Iceland"},
    {"name": "Jokulsarlon Glacier Lagoon",          "query": "Jökulsárlón, Iceland",                "country": "Iceland"},
    {"name": "Krakow Wawel Castle & Square",        "query": "Wawel Castle, Kraków, Poland",        "country": "Poland"},
    {"name": "Warsaw Old Town Restoration",         "query": "Old Town, Warsaw, Poland",            "country": "Poland"},
    {"name": "Tatra Mountains Zakopane",            "query": "Zakopane, Poland",                    "country": "Poland"},
    {"name": "Prague Charles Bridge & Castle",      "query": "Charles Bridge, Prague, Czech Republic","country": "Czech Republic"},
    {"name": "Cesky Krumlov Castle Town",           "query": "Český Krumlov, Czech Republic",       "country": "Czech Republic"},
    {"name": "Karlovy Vary Spa Town",               "query": "Karlovy Vary, Czech Republic",        "country": "Czech Republic"},
    {"name": "Budapest Parliament on Danube",       "query": "Hungarian Parliament, Budapest",      "country": "Hungary"},
    {"name": "Szechenyi Thermal Bath Pools",        "query": "Széchenyi Baths, Budapest, Hungary",  "country": "Hungary"},
    {"name": "Lake Balaton Resort Beaches",         "query": "Lake Balaton, Hungary",               "country": "Hungary"},
    {"name": "Dubrovnik Game of Thrones Walls",     "query": "Dubrovnik, Croatia",                  "country": "Croatia"},
    {"name": "Plitvice Lakes Waterfall Trail",      "query": "Plitvice Lakes, Croatia",             "country": "Croatia"},
    {"name": "Split Diocletian Palace",             "query": "Diocletian Palace, Split, Croatia",   "country": "Croatia"},
    {"name": "Hvar Island Sun & Yacht Port",        "query": "Hvar, Croatia",                       "country": "Croatia"},
    {"name": "Angkor Wat Heritage Park",            "query": "Angkor Wat, Cambodia",                "country": "Cambodia"},
    {"name": "Phnom Penh Palace & Silver Pagoda",   "query": "Royal Palace, Phnom Penh, Cambodia",  "country": "Cambodia"},
    {"name": "Serengeti National Park Safari",      "query": "Serengeti National Park, Tanzania",   "country": "Tanzania"},
    {"name": "Mount Kilimanjaro Summit Climb",      "query": "Mount Kilimanjaro, Tanzania",         "country": "Tanzania"},
    {"name": "Galapagos Islands Wildlife cruise",   "query": "Galápagos Islands, Ecuador",          "country": "Ecuador"},
    {"name": "Easter Island Rapa Nui Moai",         "query": "Easter Island, Chile",                "country": "Chile"},
    {"name": "Torres del Paine National Park",      "query": "Torres del Paine, Chile",             "country": "Chile"},
    {"name": "Cartagena Spanish Walled City",       "query": "Cartagena, Colombia",                 "country": "Colombia"},
    {"name": "Everest Base Camp Mountain Trek",     "query": "Everest Base Camp, Nepal",            "country": "Nepal"},
    {"name": "Pokhara Phewa Lake Resort",           "query": "Pokhara, Nepal",                      "country": "Nepal"},
    # Thêm địa điểm mới tại đây — không cần tọa độ thủ công
]

# ─────────────────────────────────────────────────────────────
# CÀI ĐẶT
# ─────────────────────────────────────────────────────────────
OUTPUT_FILE = Path(__file__).parent / "geocoded_data.json"
COUNTRIESNOW_BASE = "https://countriesnow.space/api/v0.1/countries"
REQUEST_TIMEOUT = 10   # giây
MAX_RETRIES = 3        # số lần thử lại khi timeout

# Cache toàn bộ dữ liệu quốc gia (tải 1 lần, dùng nhiều lần)
_COUNTRYNOW_CACHE: dict = {}


# ─────────────────────────────────────────────────────────────
# MODULE 1: LẤY TỌA ĐỘ ĐIỂM ĐẾN — Nominatim (OpenStreetMap)
# ─────────────────────────────────────────────────────────────
def build_geocoder():
    """Khởi tạo geocoder Nominatim với rate limiter 1 req/giây."""
    geolocator = Nominatim(
        user_agent="travel-recommender-datn/1.0",
        timeout=REQUEST_TIMEOUT
    )
    # Tuân thủ chính sách sử dụng Nominatim: tối đa 1 request/giây
    geocode_fn = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=1.1,   # hơi cao hơn 1 giây để an toàn
        error_wait_seconds=5.0,
        max_retries=MAX_RETRIES,
        return_value_on_exception=None
    )
    return geocode_fn


def geocode_destination(geocode_fn, query: str, name: str) -> dict | None:
    """
    Tra cứu tọa độ cho một địa điểm.
    Trả về dict {"lat": float, "lon": float} hoặc None nếu thất bại.
    """
    try:
        location = geocode_fn(query, language="en", exactly_one=True)
        if location:
            print(f"  ✅ {name}: ({location.latitude:.4f}, {location.longitude:.4f})")
            return {
                "lat": round(location.latitude, 6),
                "lon": round(location.longitude, 6),
                "display_name": location.address
            }
        else:
            print(f"  ⚠️  {name}: Không tìm thấy kết quả cho '{query}'")
            return None
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"  ❌ {name}: Lỗi kết nối — {e}")
        return None
    except Exception as e:
        print(f"  ❌ {name}: Lỗi không xác định — {e}")
        return None


# ─────────────────────────────────────────────────────────────
# MODULE 2: LẤY METADATA QUỐC GIA — CountriesNow API
# API: https://countriesnow.space (miễn phí, không cần API key)
# ─────────────────────────────────────────────────────────────

def _load_countrynow_data() -> bool:
    """
    Tải trước toàn bộ dữ liệu từ CountriesNow API vào bộ nhớ (1 lần).
    Hiệu quả hơn gọi từng quốc gia riêng lẻ.
    Lưu vào _COUNTRYNOW_CACHE với key = tên quốc gia.
    """
    global _COUNTRYNOW_CACHE
    if _COUNTRYNOW_CACHE:
        return True  # Đã tải rồi

    print("[API] Đang tải dữ liệu quốc gia từ CountriesNow API...")
    endpoints = {
        "info":     f"{COUNTRIESNOW_BASE}/info?returns=unicodeFlag,currency,capital,dialCode,name",
        "position": f"{COUNTRIESNOW_BASE}/positions",
        "iso":      f"{COUNTRIESNOW_BASE}/iso",
    }

    data_info     = []
    data_position = {}
    data_iso      = {}

    try:
        # 1. Lấy flag, currency, capital
        r = requests.get(endpoints["info"], timeout=REQUEST_TIMEOUT)
        if r.status_code == 200 and not r.json().get("error"):
            data_info = r.json().get("data", [])
            print(f"  [API] Đã tải {len(data_info)} quốc gia (flag/currency/capital)")
        else:
            print(f"  [API] Lỗi tải info: {r.status_code}")
            return False
    except Exception as e:
        print(f"  [API] Không kết nối được CountriesNow: {e}")
        return False

    try:
        # 2. Lấy tọa độ quốc gia (lat/lon)
        r2 = requests.get(endpoints["position"], timeout=REQUEST_TIMEOUT)
        if r2.status_code == 200 and not r2.json().get("error"):
            for item in r2.json().get("data", []):
                data_position[item["name"]] = {"lat": item.get("lat", 0), "lon": item.get("long", 0)}
    except Exception:
        pass  # position là optional

    try:
        # 3. Lấy ISO alpha2/alpha3
        r3 = requests.get(endpoints["iso"], timeout=REQUEST_TIMEOUT)
        if r3.status_code == 200 and not r3.json().get("error"):
            for item in r3.json().get("data", []):
                data_iso[item["name"]] = {"alpha2": item.get("Iso2", ""), "alpha3": item.get("Iso3", "")}
    except Exception:
        pass  # iso là optional

    # Gộp tất cả vào cache
    for item in data_info:
        name = item.get("name", "")
        if not name:
            continue
        cca2 = data_iso.get(name, {}).get("alpha2", "")
        cca3 = data_iso.get(name, {}).get("alpha3", "")
        pos  = data_position.get(name, {"lat": 0, "lon": 0})
        flag = item.get("unicodeFlag", "")
        # Sinh flag từ alpha2 nếu chưa có
        if not flag and cca2:
            flag = "".join(chr(0x1F1E6 + ord(ch) - ord('A')) for ch in cca2.upper())

        _COUNTRYNOW_CACHE[name] = {
            "flag":     flag or "🌍",
            "currency": item.get("currency", "USD"),
            "capital":  item.get("capital", ""),
            "alpha2":   cca2,
            "alpha3":   cca3,
            "lat":      round(float(pos.get("lat", 0)), 4),
            "lon":      round(float(pos.get("lon", 0)), 4),
            # Các trường không có trong CountriesNow — để trống, pycountry bổ sung
            "region":    "",
            "subregion": "",
            "symbol":    item.get("currency", "$")[:1] if item.get("currency") else "$",
            "languages": "",
            "timezone":  "UTC",
            "pop":       0,
            "area":      0,
            "borders":   "",
            "source":    "countrynow_api"
        }

    print(f"  [API] Cache sẵn sàng: {len(_COUNTRYNOW_CACHE)} quốc gia")
    return True


def fetch_country_metadata(country_name: str) -> dict | None:
    """
    Lấy metadata quốc gia theo thứ tự ưu tiên:
      1. CountriesNow API — countriesnow.space (online, miễn phí, không cần key)
      2. pycountry — offline fallback (flag + alpha2/alpha3 cơ bản)

    Trả về dict chứa: flag, currency, capital, alpha2, alpha3, lat, lon...
    """
    # ── Ưu tiên 1: CountriesNow API ──
    loaded = _load_countrynow_data()
    if loaded and _COUNTRYNOW_CACHE:
        # Tìm chính xác
        if country_name in _COUNTRYNOW_CACHE:
            meta = _COUNTRYNOW_CACHE[country_name].copy()
            print(f"  [API] {country_name}: cap={meta.get('capital')} | cur={meta.get('currency')} | {meta.get('flag')}")
            return meta
        # Tìm gần đúng (không phân biệt hoa thường)
        name_lower = country_name.lower()
        for key, val in _COUNTRYNOW_CACHE.items():
            if key.lower() == name_lower:
                meta = val.copy()
                print(f"  [API] {country_name} (khớp: '{key}'): {meta.get('capital')} | {meta.get('currency')}")
                return meta
        print(f"  [API] '{country_name}' không có trong CountriesNow — thử pycountry...")

    # ── Fallback: pycountry (offline) ──
    return _fetch_metadata_pycountry(country_name)


def _fetch_metadata_pycountry(country_name: str) -> dict | None:
    """
    Fallback offline dùng pycountry (flag + alpha2/alpha3).
    Không có tiền tệ, timezone, dân số — chỉ thông tin định danh.
    """
    try:
        import pycountry
    except ImportError:
        print("  [OFFLINE] pycountry chưa cài. Chạy: pip install pycountry")
        return None

    country = pycountry.countries.get(name=country_name)
    if not country:
        try:
            results = pycountry.countries.search_fuzzy(country_name)
            country = results[0] if results else None
        except Exception:
            country = None

    if not country:
        print(f"  [OFFLINE] Không tìm thấy '{country_name}' trong pycountry")
        return None

    cca2 = country.alpha_2
    cca3 = country.alpha_3
    flag = "".join(chr(0x1F1E6 + ord(ch) - ord('A')) for ch in cca2.upper())
    print(f"  [OFFLINE] {country_name}: alpha2={cca2}, flag={flag}")
    return {
        "flag": flag, "region": "", "subregion": "",
        "currency": "USD", "symbol": "$", "languages": "",
        "capital": "", "timezone": "UTC", "pop": 0, "area": 0,
        "alpha2": cca2, "alpha3": cca3, "borders": "",
        "lat": 0.0, "lon": 0.0, "source": "pycountry_offline"
    }




# ─────────────────────────────────────────────────────────────
# PIPELINE CHÍNH
# ─────────────────────────────────────────────────────────────
def run_geocoding(filter_country: str = None, test_mode: bool = False):
    """
    Chạy toàn bộ pipeline:
    1. Geocode tọa độ từng điểm đến (Nominatim)
    2. Lấy metadata từng quốc gia (REST Countries)
    3. Lưu kết quả ra geocoded_data.json

    Args:
        filter_country: Nếu cung cấp, chỉ xử lý quốc gia này.
        test_mode: Nếu True, chỉ xử lý 3 điểm đến đầu tiên.
    """
    # Load kết quả đã lưu trước (để tiếp tục nếu bị ngắt giữa chừng)
    existing_data = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        print(f"[INFO] Đã tải {len(existing_data.get('destinations', {}))} điểm đến đã geocode từ cache.")

    destinations_cache = existing_data.get("destinations", {})
    countries_cache    = existing_data.get("countries", {})

    # Lọc danh sách cần xử lý
    to_process = DESTINATIONS_TO_GEOCODE
    if filter_country:
        to_process = [d for d in to_process if d["country"].lower() == filter_country.lower()]
        if not to_process:
            print(f"[WARNING] Không tìm thấy địa điểm nào cho quốc gia: {filter_country}")
            return
    if test_mode:
        to_process = to_process[:3]
        print("[TEST MODE] Chỉ geocode 3 địa điểm đầu tiên.")

    # ── Bước 1: Geocode tọa độ điểm đến ──
    print(f"\n{'='*60}")
    print(f"BƯỚC 1: GEOCODE TỌA ĐỘ ĐIỂM ĐẾN ({len(to_process)} địa điểm)")
    print(f"{'='*60}")
    print("[INFO] Tốc độ: ~1 request/giây → Ước tính:", 
          f"{len(to_process)} giây ({len(to_process)/60:.1f} phút)\n")

    geocode_fn = build_geocoder()
    new_geocoded = 0
    failed_geocode = []

    for i, dest in enumerate(to_process, 1):
        name = dest["name"]
        print(f"[{i}/{len(to_process)}] {name}")

        # Bỏ qua nếu đã có trong cache
        if name in destinations_cache:
            print(f"  ⏩ Đã có trong cache, bỏ qua.")
            continue

        result = geocode_destination(geocode_fn, dest["query"], name)
        if result:
            result["country"] = dest["country"]
            destinations_cache[name] = result
            new_geocoded += 1
        else:
            failed_geocode.append(name)

        # Lưu định kỳ sau mỗi 10 địa điểm (phòng ngắt giữa chừng)
        if i % 10 == 0:
            _save_cache(destinations_cache, countries_cache)
            print(f"  💾 Đã lưu tiến trình ({i}/{len(to_process)})")

    # ── Bước 2: Lấy metadata quốc gia ──
    unique_countries = list(set(d["country"] for d in to_process))
    print(f"\n{'='*60}")
    print(f"BƯỚC 2: LẤY METADATA QUỐC GIA ({len(unique_countries)} quốc gia)")
    print(f"{'='*60}\n")

    for i, country in enumerate(unique_countries, 1):
        print(f"[{i}/{len(unique_countries)}] {country}")
        if country in countries_cache:
            print(f"  ⏩ Đã có trong cache, bỏ qua.")
            continue
        meta = fetch_country_metadata(country)
        if meta:
            countries_cache[country] = meta
        else:
            print(f"  ⚠️  Bỏ qua {country}, cần nhập metadata thủ công.")
        time.sleep(0.5)  # lịch sự với API

    # ── Bước 3: Lưu kết quả cuối ──
    _save_cache(destinations_cache, countries_cache)

    # ── Báo cáo ──
    print(f"\n{'='*60}")
    print("KẾT QUẢ GEOCODING")
    print(f"{'='*60}")
    print(f"  ✅ Geocode thành công: {new_geocoded} điểm đến mới")
    print(f"  📦 Tổng trong cache  : {len(destinations_cache)} điểm đến")
    print(f"  🌍 Metadata quốc gia : {len(countries_cache)} quốc gia")
    if failed_geocode:
        print(f"\n  ❌ Thất bại ({len(failed_geocode)} điểm đến) — cần nhập tọa độ thủ công:")
        for name in failed_geocode:
            print(f"     - {name}")
    print(f"\n  💾 Đã lưu tại: {OUTPUT_FILE}")


def _save_cache(destinations: dict, countries: dict):
    """Lưu kết quả ra file JSON."""
    output = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_destinations": len(destinations),
        "total_countries": len(countries),
        "destinations": destinations,
        "countries": countries
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
# HÀM TIỆN ÍCH: ĐỌC TỌA ĐỘ ĐÃ GEOCODE
# (Dùng trong generate_large_dataset.py thay vì hardcode)
# ─────────────────────────────────────────────────────────────
def load_geocoded_coords(destination_name: str) -> tuple[float, float] | tuple[None, None]:
    """
    Đọc tọa độ đã geocode từ file cache.

    Ví dụ dùng trong generate_large_dataset.py:
        from mining.auto_geocode import load_geocoded_coords
        lat, lon = load_geocoded_coords("Oslo Fjords & Museum Peninsula")

    Returns:
        (lat, lon) nếu tìm thấy, (None, None) nếu không có.
    """
    if not OUTPUT_FILE.exists():
        return None, None
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        dest = data.get("destinations", {}).get(destination_name)
        if dest:
            return dest["lat"], dest["lon"]
    except Exception:
        pass
    return None, None


def load_country_metadata(country_name: str) -> dict | None:
    """
    Đọc metadata quốc gia đã lấy từ REST Countries API.

    Ví dụ dùng trong generate_large_dataset.py:
        from mining.auto_geocode import load_country_metadata
        meta = load_country_metadata("Norway")
        # meta = {"flag": "🇳🇴", "currency": "NOK", "capital": "Oslo", ...}

    Returns:
        dict metadata hoặc None.
    """
    if not OUTPUT_FILE.exists():
        return None
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("countries", {}).get(country_name)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tự động geocode tọa độ điểm đến và metadata quốc gia"
    )
    parser.add_argument(
        "--country", "-c",
        type=str,
        default=None,
        help="Chỉ geocode cho một quốc gia cụ thể (ví dụ: --country Norway)"
    )
    parser.add_argument(
        "--test", "-t",
        action="store_true",
        help="Test mode: chỉ geocode 3 địa điểm đầu tiên"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("  AUTO GEOCODE — Travel Recommender DATN")
    print("  Nguồn: Nominatim (OSM) + REST Countries API")
    print("=" * 60)
    run_geocoding(filter_country=args.country, test_mode=args.test)
