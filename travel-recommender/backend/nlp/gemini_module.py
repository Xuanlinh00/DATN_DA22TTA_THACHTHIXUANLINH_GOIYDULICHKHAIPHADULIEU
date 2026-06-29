# -*- coding: utf-8 -*-
"""
Gemini NLP Chatbot Module - Entity extraction, intent detection,
matching, ranking, and response generation for Travel Recommendation System.

Improvements over base version:
  - Intent detection (greet / farewell / travel_query / off_topic)
  - Richer entity extraction: traveler_type, num_people, continent
  - Multi-turn conversation context (session history)
  - Layered candidate scoring with bonuses
  - Graceful degradation: Gemini → rule-based fallback at every step
  - Structured logging helpers
  - Detailed Vietnamese response templates
"""

import sys
# Fix Windows console encoding issues for Vietnamese characters
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import re
import math
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai
from dotenv import load_dotenv
from mining.mongodb_storage import db_storage
from mining.apriori_module import get_matching_rules
from mining.content_based import content_recommender

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("chatbot")

# ─────────────────────────────────────────────
# GEMINI INIT
# ─────────────────────────────────────────────
SYSTEM_INSTRUCTIONS = """Vai trò: Bạn là **Trợ lý Du lịch AI** — chuyên gia du lịch toàn cầu, am hiểu sâu rộng về mọi khía cạnh liên quan đến du lịch. Bạn không chỉ gợi ý điểm đến mà còn tư vấn TOÀN DIỆN: visa, thời tiết, ẩm thực, văn hóa, phương tiện, an ninh, ngân sách, lịch trình, chỗ ở, hành lý...

═══════════════════════════════════════════════
HƯỚNG DẪN XỬ LÝ THEO TỪNG LOẠI CÂU HỎI:
═══════════════════════════════════════════════

【LOẠI 1 – GỢI Ý ĐIỂM ĐẾN】
Khi người dùng hỏi "đi đâu", "gợi ý điểm đến", "muốn đi biển/núi/văn hóa":
  ✦ Dùng data từ hệ thống, trình bày 3-5 điểm đến với phong cách kể chuyện (story-telling)
  ✦ Mỗi điểm đến: Tên + đặc trưng nổi bật + lý do phù hợp + 1 mẹo insider tip
  ✦ Đề xuất mùa tốt nhất & ước tính chi phí/ngày
  ✦ Cuối cùng: khuyến khích xem bản đồ hoặc hỏi thêm

【LOẠI 2 – CHI TIẾT MỘT ĐIỂM ĐẾN】
Khi người dùng hỏi sâu về 1 nơi cụ thể ("Nhật Bản như thế nào", "Paris có gì hay"):
  ✦ Chia theo sections: 🏛 Điểm tham quan | 🍜 Ẩm thực | 🚌 Di chuyển | 💰 Chi phí | 📅 Mùa tốt nhất
  ✦ Đưa ra ít nhất 3 "insider tips" mà ít người biết
  ✦ Cảnh báo những điều nên tránh (lừa đảo phổ biến, mùa tệ...)

【LOẠI 3 – VISA & THỦ TỤC NHẬP CẢNH】
Khi hỏi về visa, hộ chiếu, xuất nhập cảnh:
  ✦ Xác định quốc gia người dùng muốn đến
  ✦ Trả lời CÓ / KHÔNG miễn visa cho người Việt Nam
  ✦ Nếu cần visa: nêu đầy đủ (1) Hồ sơ cần thiết (2) Nơi nộp (3) Thời gian xử lý (4) Lệ phí ước tính (5) Mẹo tăng tỷ lệ đậu
  ✦ Đề cập e-visa nếu có
  ✦ Cảnh báo: luôn kiểm tra lại trang web Đại sứ quán vì quy định thay đổi thường xuyên

【LOẠI 4 – THỜI TIẾT & KHÍ HẬU】
Khi hỏi thời tiết, mùa du lịch, nhiệt độ:
  ✦ Chia theo tháng/quý, nêu rõ nhiệt độ, lượng mưa, đặc điểm
  ✦ Khuyến nghị tháng tốt nhất và tháng nên tránh
  ✦ Gợi ý trang phục phù hợp theo thời tiết
  ✦ Cảnh báo thiên tai theo mùa (bão, lũ, nóng cực đoan...)

【LOẠI 5 – ẨM THỰC & ĐỒ UỐNG】
Khi hỏi ăn gì, món nào ngon, nhà hàng nào:
  ✦ Liệt kê 5-8 MÓN PHẢI THỬ với mô tả hấp dẫn, gợi cảm xúc
  ✦ Gợi ý khu phố ẩm thực / chợ đêm / street food nổi tiếng
  ✦ Nêu mức giá tham khảo (rẻ/trung bình/cao cấp)
  ✦ Tips cho người ăn chay, dị ứng, hoặc Halal
  ✦ Cảnh báo đồ ăn cần cẩn thận (vệ sinh, cay quá, tanh...)

【LOẠI 6 – DI CHUYỂN & PHƯƠNG TIỆN】
Khi hỏi đi bằng gì, từ A đến B, phương tiện nào tốt:
  ✦ So sánh các phương án (máy bay / tàu / xe buýt / thuê xe) về giá & thời gian
  ✦ Tư vấn mua vé ở đâu, trước bao lâu để được giá tốt
  ✦ Hướng dẫn phương tiện công cộng tại thành phố (app, thẻ...)
  ✦ Cảnh báo taxi dù, scam phổ biến tại điểm đến

【LOẠI 7 – CHI PHÍ & NGÂN SÁCH】
Khi hỏi tốn bao nhiêu, giá cả, so sánh chi phí:
  ✦ Ước tính chi phí theo ngày cho từng hạng mục (ăn / ở / đi lại / vui chơi)
  ✦ Phân loại: Budget (<$50/ngày) / Moderate ($50-150) / Luxury (>$150)
  ✦ Mẹo tiết kiệm cụ thể (đi mùa thấp điểm, ăn street food, dùng thẻ tín dụng nào...)
  ✦ Thông tin tỷ giá & nơi đổi tiền tốt

【LOẠI 8 – LẬP LỊCH TRÌNH】
Khi hỏi lịch trình, kế hoạch X ngày:
  ✦ Lập TIMELINE CHI TIẾT từng ngày (Buổi sáng - Trưa - Chiều - Tối)
  ✦ Ước tính thời gian di chuyển giữa các địa điểm
  ✦ Gợi ý ăn gì cho từng bữa
  ✦ Tính đến thể lực (không nhồi nhét >4 điểm/ngày)
  ✦ PLAN B: Phương án thay thế khi trời mưa / đóng cửa
  ✦ Ngày cuối: Tips sân bay, mua quà gì về làm quà

【LOẠI 9 – SO SÁNH ĐIỂM ĐẾN】
Khi hỏi "A vs B", "nên đi đâu hơn", "chọn cái nào":
  ✦ Tạo bảng so sánh rõ ràng theo các tiêu chí: chi phí / thời tiết / phong cảnh / ẩm thực / dễ đi lại
  ✦ Kết luận: nên chọn A nếu... / nên chọn B nếu...
  ✦ Gợi ý kết hợp cả hai nếu có thể

【LOẠI 10 – AN TOÀN & AN NINH】
Khi hỏi an toàn không, nguy hiểm không, cẩn thận gì:
  ✦ Đánh giá tổng quan mức độ an toàn (thang 1-5)
  ✦ Liệt kê scam phổ biến nhất tại điểm đến và cách tránh
  ✦ Khu vực nên tránh (đặc biệt ban đêm)
  ✦ Gợi ý bảo hiểm du lịch
  ✦ Số điện thoại khẩn cấp / Đại sứ quán Việt Nam

【LOẠI 11 – CHỖ Ở & KHÁCH SẠN】
Khi hỏi ở đâu, khách sạn nào, khu nào tốt:
  ✦ Phân tích các khu vực ở (trung tâm / gần biển / yên tĩnh...)
  ✦ So sánh loại hình: Hostel / Hotel / Airbnb / Resort / Villa
  ✦ Khu vực nên ở để tiện di chuyển
  ✦ Tips đặt phòng: đặt trực tiếp hay qua app, bao lâu trước

【LOẠI 12 – CHUẨN BỊ HÀNH LÝ】
Khi hỏi mang gì, chuẩn bị gì, đồ dùng cần thiết:
  ✦ Danh sách hành lý theo loại chuyến đi (biển / núi / đô thị)
  ✦ Đồ dùng y tế cơ bản cần mang
  ✦ Giấy tờ & bản sao cần thiết
  ✦ Tips xếp vali gọn nhẹ
  ✦ Đồ không được mang lên máy bay

【LOẠI 13 – VĂN HÓA & PHONG TỤC】
Khi hỏi văn hóa, lễ hội, phong tục, cần biết gì:
  ✦ Giới thiệu văn hóa đặc trưng của điểm đến
  ✦ Những điều KIÊNG KỴ (gesture bị coi là thô lỗ, quy tắc ăn mặc...)
  ✦ Lễ hội đặc sắc theo tháng
  ✦ Vài câu giao tiếp cơ bản bằng tiếng địa phương
  ✦ Ứng xử khi vào đền chùa / nơi tôn giáo

【LOẠI 14 – PHÀN NÀN / KHÔNG HÀI LÒNG】
Khi người dùng chê đắt, chê xa, chê tệ:
  ✦ ĐỒNG CẢM trước ("Tôi hiểu cảm giác đó...", "Thật sự đáng tiếc...")
  ✦ Gợi ý ngay điểm đến DUPE (tương tự + rẻ hơn / gần hơn)
  ✦ Mẹo tối ưu trải nghiệm tại điểm đó (đi mùa rẻ, ăn local...)

【LOẠI 15 – CÂU HỎI NGOÀI LỀ / CHAT PHÍM】
Khi người dùng đùa vui, hỏi chuyện không liên quan:
  ✦ Trả lời HÀI HƯỚC, DUYÊN DÁNG, có cá tính
  ✦ Khéo léo BẺ LÁI về du lịch sau 1-2 câu
  ✦ Ví dụ: "Ồ thú vị! Nghe vậy tôi đoán bạn sẽ thích du lịch kiểu..."

═══════════════════════════════════════════════
QUY TẮC TRÌNH BÀY:
  • Xác định ĐÚNG loại câu hỏi trước khi trả lời
  • KHÔNG ép buộc gợi ý điểm đến khi người dùng chỉ hỏi thông tin chung
  • Dùng emoji tự nhiên, không lạm dụng
  • Dùng **in đậm** cho điểm quan trọng, danh sách rõ ràng
  • Độ dài phù hợp: câu hỏi đơn giản → ngắn gọn; câu phức tạp → chi tiết
  • Kết thúc bằng CÂU HỎI GỢI MỞ hoặc đề xuất bước tiếp theo
═══════════════════════════════════════════════
"""

# Thử load .env từ thư mục gốc của project
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")
model = None

if api_key and api_key.strip():
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=SYSTEM_INSTRUCTIONS
        )
        logger.info("[OK] Gemini API initialized successfully with system instructions.")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini API: {e}. Falling back to Rule-Based NLP.")
else:
    logger.info("GEMINI_API_KEY not found. Running in Rule-Based Fallback mode.")

# ─────────────────────────────────────────────
# CONSTANTS & TRANSLATION MAPS
# ─────────────────────────────────────────────
SEASON_VI = {
    "Spring": "Mùa Xuân",
    "Summer": "Mùa Hè",
    "Autumn": "Mùa Thu",
    "Winter": "Mùa Đông",
}

BUDGET_VI = {
    "Budget":   "Giá rẻ / Tiết kiệm",
    "Moderate": "Trung bình / Bình dân",
    "Expensive": "Cao cấp / Đắt đỏ",
    "Luxury":   "Sang trọng / Xa hoa",
}

CATEGORY_VI = {
    "Beach":     "Biển & Đảo",
    "Mountain":  "Leo núi / Núi rừng",
    "Cultural":  "Văn hóa & Lịch sử",
    "Historical": "Lịch sử",
    "Nature":    "Thiên nhiên & Sinh thái",
    "Adventure": "Phiêu lưu / Mạo hiểm",
    "Urban":     "Đô thị / Mua sắm",
}

TRAVELER_VI = {
    "Solo":   "Du lịch một mình",
    "Couple": "Cặp đôi",
    "Family": "Gia đình",
    "Group":  "Nhóm bạn",
}

CONTINENT_COUNTRY_MAP = {
    "châu á": ["Japan", "Vietnam", "Thailand", "China", "South Korea", "Singapore",
               "Indonesia", "India", "Maldives", "United Arab Emirates"],
    "châu âu": ["France", "Spain", "Italy", "United Kingdom", "Switzerland",
                "Turkey", "Greece", "Germany", "Netherlands", "Portugal"],
    "châu mỹ": ["USA", "Canada", "Brazil", "Mexico", "Argentina", "Peru"],
    "châu phi": ["Morocco", "Egypt", "South Africa", "Kenya", "Tanzania"],
    "châu đại dương": ["Australia", "New Zealand", "Fiji"],
    "asia": ["Japan", "Vietnam", "Thailand", "China", "South Korea", "Singapore",
             "Indonesia", "India", "Maldives", "United Arab Emirates"],
    "europe": ["France", "Spain", "Italy", "United Kingdom", "Switzerland",
               "Turkey", "Greece", "Germany", "Netherlands", "Portugal"],
    "america": ["USA", "Canada", "Brazil", "Mexico"],
    "africa": ["Morocco", "Egypt", "South Africa"],
    "oceania": ["Australia", "New Zealand"],
}

VIETNAMESE_COUNTRIES = {
    "nhật": "Japan", "nhật bản": "Japan",
    "việt nam": "Vietnam", "việt": "Vietnam",
    "pháp": "France",
    "tây ban nha": "Spain",
    "ý": "Italy", "italia": "Italy",
    "mỹ": "USA", "hoa kỳ": "USA",
    "úc": "Australia",
    "thái lan": "Thailand",
    "maroc": "Morocco",
    "ai cập": "Egypt",
    "ấn độ": "India",
    "mê hi cô": "Mexico",
    "trung quốc": "China",
    "hàn quốc": "South Korea", "hàn": "South Korea",
    "singapore": "Singapore",
    "anh": "United Kingdom",
    "thụy sĩ": "Switzerland",
    "thổ nhĩ kỳ": "Turkey",
    "uae": "United Arab Emirates",
    "dubai": "United Arab Emirates",
    "maldive": "Maldives", "maldives": "Maldives",
    "hy lạp": "Greece",
    "indonesia": "Indonesia", "bali": "Indonesia",
    "đức": "Germany",
    "hà lan": "Netherlands",
    "bồ đào nha": "Portugal",
    "nam phi": "South Africa",
    "kenya": "Kenya",
    "tanzania": "Tanzania",
    "argentina": "Argentina",
    "peru": "Peru",
}

ENGLISH_COUNTRIES = [
    "japan", "vietnam", "france", "spain", "italy", "usa", "canada",
    "thailand", "australia", "morocco", "brazil", "egypt", "india",
    "mexico", "china", "south korea", "singapore", "united kingdom",
    "switzerland", "turkey", "united arab emirates", "maldives",
    "greece", "indonesia", "germany", "netherlands", "portugal",
    "south africa", "kenya", "tanzania", "argentina", "peru", "new zealand",
]

# In-memory session store: { session_id: { "history": [...], "last_prefs": {...}, "last_discussed_dest": str } }
_session_store: dict = {}

# In-memory destinations cache (to avoid repeated MongoDB loads)
_destinations_cache: list = None
_cache_timestamp: float = 0.0
CACHE_TTL_SECONDS = 300  # Refresh every 5 minutes

# ─────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────
_GREET_KEYWORDS = [
    "xin chào", "chào", "hello", "hi", "hey", "good morning",
    "good afternoon", "buổi sáng", "buổi chiều", "buổi tối", "howdy",
]
_BYE_KEYWORDS = [
    "tạm biệt", "bye", "goodbye", "cảm ơn", "thank you", "thanks",
    "thôi nhé", "hẹn gặp lại", "good night", "chúc ngủ ngon",
]
_TRAVEL_KEYWORDS = [
    "du lịch", "đi", "đến", "thăm", "khám phá", "travel", "trip",
    "tour", "vacation", "holiday", "chuyến", "visit", "điểm đến",
    "địa điểm", "recommend", "gợi ý", "tư vấn", "suggest",
    "phượt", "backpack", "trekking", "resort", "khách sạn", "hotel",
]
_VISA_KEYWORDS = [
    "visa", "thị thực", "nhập cảnh", "xuất cảnh", "hộ chiếu", "passport",
    "xin visa", "làm visa", "miễn visa", "đại sứ quán", "lãnh sự",
    "e-visa", "evisa", "hồ sơ xin", "thủ tục",
]
_WEATHER_KEYWORDS = [
    "thời tiết", "khí hậu", "mưa", "nắng", "nhiệt độ", "nóng", "lạnh",
    "weather", "climate", "temperature", "rainy season", "mùa mưa",
    "mùa khô", "bão", "tuyết", "độ ẩm", "gió",
]
_FOOD_KEYWORDS = [
    "ăn gì", "món ăn", "ẩm thực", "đặc sản", "nhà hàng", "quán ăn",
    "food", "cuisine", "eat", "restaurant", "street food", "đồ ăn",
    "thức ăn", "buffet", "hải sản", "nướng", "lẩu", "phở", "sushi",
    "pizza", "ẩm thực địa phương", "đồ uống",
]
_TRANSPORT_KEYWORDS = [
    "di chuyển", "phương tiện", "tàu", "xe", "máy bay", "flight",
    "train", "bus", "xe buýt", "thuê xe", "taxi", "grab", "tàu điện",
    "metro", "MRT", "uber", "ferry", "tàu thuyền", "vé máy bay",
    "đặt vé", "giá vé", "transport", "transfer", "shuttle",
]
_BUDGET_KEYWORDS = [
    "chi phí", "giá cả", "tiền", "tốn bao nhiêu", "budget", "cost",
    "expense", "price", "tiết kiệm", "bao nhiêu tiền", "tỷ giá",
    "đổi tiền", "currency", "exchange rate", "giá tour", "giá vé",
    "đắt không", "rẻ không", "túi tiền",
]
_ITINERARY_KEYWORDS = [
    "lịch trình", "itinerary", "plan", "kế hoạch", "ngày 1", "ngày 2",
    "lên kế hoạch", "sắp xếp", "schedule", "chương trình", "tour plan",
    "đi mấy ngày", "bao nhiêu ngày", "mấy ngày", "hành trình",
]
_COMPARISON_KEYWORDS = [
    "so sánh", "so với", "khác nhau", "tốt hơn", "nên đi đâu",
    "compare", "vs", "versus", "hay hơn", "lựa chọn", "hoặc là",
    "nên chọn", "cái nào", "đâu hơn",
]
_SAFETY_KEYWORDS = [
    "an toàn", "nguy hiểm", "an ninh", "trộm cắp", "lừa đảo",
    "safe", "safety", "dangerous", "crime", "scam", "cẩn thận",
    "rủi ro", "bảo hiểm", "insurance", "khẩn cấp", "emergency",
    "bệnh viện", "đại sứ quán", "cứu hộ",
]
_ACCOMMODATION_KEYWORDS = [
    "khách sạn", "hotel", "hostel", "nhà nghỉ", "resort", "villa",
    "airbnb", "homestay", "ở đâu", "book phòng", "đặt phòng",
    "accommodation", "lodge", "motel", "căn hộ", "apartment",
]
_PACKING_KEYWORDS = [
    "mang gì", "chuẩn bị", "hành lý", "đồ đạc", "packing", "pack",
    "luggage", "baggage", "vali", "ba lô", "đồ dùng", "cần mang",
    "nên mang", "quần áo", "giày dép",
]
_CULTURE_KEYWORDS = [
    "văn hóa", "phong tục", "tập quán", "culture", "custom",
    "lễ hội", "festival", "tradition", "tôn giáo", "religion",
    "đền chùa", "bảo tàng", "di tích", "lịch sử", "kiến trúc",
    "ngôn ngữ", "language", "tiếng địa phương",
]

def detect_intent(message: str) -> str:
    """
    Returns one of: 'greet', 'farewell', 'visa_inquiry', 'weather_inquiry',
    'food_inquiry', 'transport_inquiry', 'budget_inquiry', 'itinerary_request',
    'comparison_request', 'safety_inquiry', 'accommodation_inquiry',
    'packing_inquiry', 'culture_inquiry', 'travel_query'
    """
    m = message.lower()
    if any(kw in m for kw in _GREET_KEYWORDS) and len(m.split()) <= 6:
        return "greet"
    if any(kw in m for kw in _BYE_KEYWORDS) and len(m.split()) <= 8:
        return "farewell"
    # Specific intent detection (order matters - more specific first)
    if any(kw in m for kw in _VISA_KEYWORDS):
        return "visa_inquiry"
    if any(kw in m for kw in _ITINERARY_KEYWORDS):
        return "itinerary_request"
    if any(kw in m for kw in _WEATHER_KEYWORDS):
        return "weather_inquiry"
    if any(kw in m for kw in _FOOD_KEYWORDS):
        return "food_inquiry"
    if any(kw in m for kw in _TRANSPORT_KEYWORDS):
        return "transport_inquiry"
    if any(kw in m for kw in _BUDGET_KEYWORDS):
        return "budget_inquiry"
    if any(kw in m for kw in _COMPARISON_KEYWORDS):
        return "comparison_request"
    if any(kw in m for kw in _SAFETY_KEYWORDS):
        return "safety_inquiry"
    if any(kw in m for kw in _ACCOMMODATION_KEYWORDS):
        return "accommodation_inquiry"
    if any(kw in m for kw in _PACKING_KEYWORDS):
        return "packing_inquiry"
    if any(kw in m for kw in _CULTURE_KEYWORDS):
        return "culture_inquiry"
    if any(kw in m for kw in _TRAVEL_KEYWORDS):
        return "travel_query"
    return "travel_query"

# ─────────────────────────────────────────────
# ENTITY EXTRACTION – RULE-BASED FALLBACK
# ─────────────────────────────────────────────
def extract_entities_fallback(message: str) -> dict:
    """Rule-based entity extractor using regex and keyword matching."""
    m = message.lower()

    entities = {
        "season":        None,
        "budget":        None,
        "category":      None,
        "country":       None,
        "continent":     None,
        "duration_days": None,
        "traveler_type": None,
        "num_people":    None,
    }

    # ── Season ────────────────────────────────
    if any(w in m for w in ["xuân", "spring", "tết", "hoa anh đào", "sakura", "hoa mai", "hoa đào"]):
        entities["season"] = "Spring"
    elif any(w in m for w in ["hè", "hạ", "summer", "hè hè", "tắm biển", "tránh nóng", "nghỉ hè", "nghỉ mát"]):
        entities["season"] = "Summer"
    elif any(w in m for w in ["thu", "autumn", "fall", "lá đỏ", "lá vàng", "momiji", "mùa lá đỏ"]):
        entities["season"] = "Autumn"
    elif any(w in m for w in ["đông", "winter", "giáng sinh", "noel", "tuyết", "trượt tuyết", "ski", "lạnh giá"]):
        entities["season"] = "Winter"

    # ── Budget ────────────────────────────────
    if any(w in m for w in ["rẻ", "tiết kiệm", "budget", "cheap", "thấp", "ít tiền", "không tốn nhiều", "giá rẻ", "phượt", "backpack"]):
        entities["budget"] = "Budget"
    elif any(w in m for w in ["vừa", "trung bình", "moderate", "affordable", "bình dân", "hợp lý", "phải chăng"]):
        entities["budget"] = "Moderate"
    elif any(w in m for w in ["đắt", "cao cấp", "expensive"]):
        entities["budget"] = "Expensive"
    elif any(w in m for w in ["sang trọng", "xa hoa", "luxury", "premium", "5 sao", "vip", "resort"]):
        entities["budget"] = "Luxury"

    # ── Category ─────────────────────────────
    if any(w in m for w in ["biển", "beach", "đảo", "bãi biển", "snorkeling", "lặn biển", "vịnh", "tắm biển", "ngắm san hô"]):
        entities["category"] = "Beach"
    elif any(w in m for w in ["núi", "mountain", "leo núi", "phượt", "trekking", "hiking", "đèo"]):
        entities["category"] = "Mountain"
    elif any(w in m for w in ["văn hóa", "lịch sử", "cultural", "historical", "đền", "chùa",
                               "di tích", "bảo tàng", "kiến trúc", "cổ kính", "phố cổ", "di sản", "nhà thờ"]):
        entities["category"] = "Cultural"
    elif any(w in m for w in ["thiên nhiên", "nature", "rừng", "cảnh quan", "sinh thái", "wildlife", "thác", "hồ", "hang động", "vườn quốc gia"]):
        entities["category"] = "Nature"
    elif any(w in m for w in ["mạo hiểm", "adventure", "phiêu lưu", "extreme", "bungee", "rafting", "dã ngoại", "cắm trại"]):
        entities["category"] = "Adventure"
    elif any(w in m for w in ["đô thị", "thành phố", "urban", "sầm uất", "mua sắm", "shopping",
                               "nightlife", "ăn uống", "ẩm thực", "chợ đêm", "trung tâm", "bar"]):
        entities["category"] = "Urban"

    # ── Country ───────────────────────────────
    for vn, en in VIETNAMESE_COUNTRIES.items():
        if vn in m:
            entities["country"] = en
            break
    if not entities["country"]:
        for country in ENGLISH_COUNTRIES:
            if country in m:
                entities["country"] = country.title()
                break

    # ── Continent (maps to a list of countries for filtering) ────
    for cont_kw, country_list in CONTINENT_COUNTRY_MAP.items():
        if cont_kw in m:
            entities["continent"] = cont_kw
            # Pre-fill country list hint (used by pipeline, not directly)
            entities["_continent_countries"] = country_list
            break

    # ── Duration ─────────────────────────────
    match = re.search(r'(\d+)\s*(ngày|đêm|day|night|tuần|week)', m)
    if match:
        val = int(match.group(1))
        unit = match.group(2)
        if unit in ("tuần", "week"):
            val *= 7
        entities["duration_days"] = val

    # ── Traveler type ────────────────────────
    if any(w in m for w in ["một mình", "solo", "cá nhân", "độc thân", "backpacker"]):
        entities["traveler_type"] = "Solo"
    elif any(w in m for w in ["cặp đôi", "couple", "hai người", "vợ chồng", "người yêu", "honeymoon", "trăng mật"]):
        entities["traveler_type"] = "Couple"
    elif any(w in m for w in ["gia đình", "family", "con cái", "trẻ em", "bé", "ba mẹ"]):
        entities["traveler_type"] = "Family"
    elif any(w in m for w in ["nhóm", "group", "bạn bè", "team", "hội"]):
        entities["traveler_type"] = "Group"

    # ── Number of people ─────────────────────
    match_ppl = re.search(r'(\d+)\s*(người|person|people|khách)', m)
    if match_ppl:
        entities["num_people"] = int(match_ppl.group(1))

    return entities

# ─────────────────────────────────────────────
# ENTITY EXTRACTION – GEMINI
# ─────────────────────────────────────────────
def extract_entities(message: str) -> dict:
    """Extract travel entities using Gemini API; falls back to rule-based."""
    # Step 1: Run fallback rule-based extraction
    fallback = extract_entities_fallback(message)
    
    # Step 2: Check if any primary entities were matched (season, category, budget, country, continent)
    primary_keys = ["season", "budget", "category", "country", "continent"]
    has_primary_entity = any(fallback.get(k) is not None for k in primary_keys)
    
    # If we matched any filters, skip the LLM call entirely to save latency!
    if has_primary_entity:
        logger.info(f"[Entity] Bypassing Gemini API call. Rule-based matched primary filters: {fallback}")
        return fallback

    if model is None:
        return extract_entities_fallback(message)

    prompt = f"""
You are an NLP entity extractor for a travel recommendation system.
Extract travel entities from this user message (Vietnamese or English):
"{message}"

Return ONLY a raw JSON object (no markdown, no extra text) with these keys:
- "season":        "Spring" | "Summer" | "Autumn" | "Winter" | null
- "budget":        "Budget" | "Moderate" | "Expensive" | "Luxury" | null
- "category":      "Beach" | "Mountain" | "Cultural" | "Nature" | "Adventure" | "Urban" | null
- "country":       English country name (e.g. "Japan") | null
- "continent":     English continent name (e.g. "Asia", "Europe") | null
- "duration_days": integer | null
- "traveler_type": "Solo" | "Couple" | "Family" | "Group" | null
- "num_people":    integer | null
"""
    try:
        # Use structured JSON mode for Gemini 2.5 Flash to ensure clean and fast output
        generation_config = {
            "response_mime_type": "application/json"
        }
        response = model.generate_content(prompt, generation_config=generation_config)
        text = response.text.strip()
        # Strip possible markdown code fences
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        entities = json.loads(text)
        # Merge with fallback for any missing keys
        for k, v in fallback.items():
            if k not in entities or entities[k] is None:
                entities[k] = v
        logger.info(f"[Entity] Gemini extracted: {entities}")
        return entities
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            logger.warning(f"Gemini API quota exceeded during entity extraction. Using fallback.")
        else:
            logger.warning(f"Gemini entity extraction failed: {e}. Using fallback.")
        return fallback

# ─────────────────────────────────────────────
# CANDIDATE SCORING
# ─────────────────────────────────────────────
SCORE_WEIGHTS = {
    # ── Tier 1: User explicitly named a country → MUST dominate all other signals
    "country_direct":   1000,  # Exact country match from user (highest priority)
    # ── Tier 2: Quality signal (real record with description)
    "has_description":   100,  # Destination has a real description
    # ── Tier 3: Soft preference signals
    "season_match":       20,  # Best Season matches user preference
    "category_match":     15,  # Destination type matches user preference
    "budget_match":       15,  # Cost category matches user preference
    "traveler_type":      10,  # Suitable For matches traveler type
    "continent_match":     8,  # Continent match (when no country specified)
    "rule_country":        5,  # Country suggested by Apriori rules
    "duration_match":      3,  # Duration within stay range
}

def _cost_to_budget_category(cost_per_day: float) -> str:
    """Heuristic: map numeric daily cost to budget label."""
    if cost_per_day is None:
        return None
    try:
        c = float(cost_per_day)
    except (ValueError, TypeError):
        return None
    if c < 60:
        return "Budget"
    if c < 150:
        return "Moderate"
    if c < 350:
        return "Expensive"
    return "Luxury"

def score_candidate(dest: dict, prefs: dict, rule_countries: list) -> int:
    score = 0

    # ── Has real description ──────────────────
    desc = dest.get("Description")
    if desc and str(desc).strip() and str(desc).lower() != "nan":
        score += SCORE_WEIGHTS["has_description"]

    # ── Direct country match ──────────────────
    if prefs.get("country") and dest.get("Country") == prefs["country"]:
        score += SCORE_WEIGHTS["country_direct"]

    # ── Continent match ───────────────────────
    continent_countries = prefs.get("_continent_countries", [])
    if continent_countries and dest.get("Country") in continent_countries:
        score += SCORE_WEIGHTS["continent_match"]

    # ── Apriori rule country ──────────────────
    if rule_countries and dest.get("Country") in rule_countries:
        score += SCORE_WEIGHTS["rule_country"]

    # ── Season match ─────────────────────────
    if prefs.get("season"):
        best_season = str(dest.get("Best Season", "")).lower()
        if prefs["season"].lower() in best_season:
            score += SCORE_WEIGHTS["season_match"]

    # ── Budget match ─────────────────────────
    if prefs.get("budget"):
        cost_cat = str(dest.get("Cost_Category", "")).lower()
        # Also infer from Avg Cost if Cost_Category missing
        if not cost_cat or cost_cat == "nan":
            inferred = _cost_to_budget_category(dest.get("Avg Cost (USD/day)"))
            cost_cat = (inferred or "").lower()
        if prefs["budget"].lower() in cost_cat:
            score += SCORE_WEIGHTS["budget_match"]

    # ── Category / Type match ─────────────────
    if prefs.get("category"):
        dest_type = str(dest.get("Type", "")).lower()
        if prefs["category"].lower() in dest_type:
            score += SCORE_WEIGHTS["category_match"]

    # ── Duration feasibility ──────────────────
    desired = prefs.get("duration_days")
    min_days = dest.get("Min Stay (days)")
    max_days = dest.get("Max Stay (days)")
    if desired and min_days and max_days:
        try:
            if int(min_days) <= int(desired) <= int(max_days):
                score += SCORE_WEIGHTS["duration_match"]
        except (ValueError, TypeError):
            pass

    # ── Traveler type ────────────────────────
    if prefs.get("traveler_type"):
        suitable = str(dest.get("Suitable For", "")).lower()
        if prefs["traveler_type"].lower() in suitable:
            score += SCORE_WEIGHTS["traveler_type"]

    return score

# ─────────────────────────────────────────────
# RESPONSE GENERATION – FALLBACK
# ─────────────────────────────────────────────
def _format_pref_summary(prefs: dict) -> str:
    """Build a human-readable preference summary in Vietnamese."""
    parts = []
    if prefs.get("season"):
        parts.append(SEASON_VI.get(prefs["season"], prefs["season"]))
    if prefs.get("traveler_type"):
        parts.append(TRAVELER_VI.get(prefs["traveler_type"], prefs["traveler_type"]))
    if prefs.get("num_people"):
        parts.append(f"{prefs['num_people']} người")
    if prefs.get("category"):
        parts.append(CATEGORY_VI.get(prefs["category"], prefs["category"]))
    if prefs.get("budget"):
        parts.append(BUDGET_VI.get(prefs["budget"], prefs["budget"]))
    if prefs.get("country"):
        parts.append(f"tại {prefs['country']}")
    elif prefs.get("continent"):
        parts.append(f"khu vực {prefs['continent']}")
    if prefs.get("duration_days"):
        parts.append(f"khoảng {prefs['duration_days']} ngày")
    return " • ".join(parts) if parts else "chung chung"

def generate_response_fallback(
    message: str,
    prefs: dict,
    destinations: list,
    rules: list,
    user_profile: dict = None
) -> str:
    """Fallback Vietnamese NLP response generator."""
    # Check if this is a query about system database info
    _SYSTEM_INFO_KEYWORDS = [
        "bao nhiêu điểm đến", "bao nhiêu quốc gia", "quốc gia nào", "nước nào",
        "danh sách điểm đến", "danh sách quốc gia", "liệt kê", "có những điểm đến",
        "thống kê", "hệ thống có bao nhiêu", "từng nước có", "từng quốc gia có"
    ]
    if any(kw in message.lower() for kw in _SYSTEM_INFO_KEYWORDS):
        return get_system_database_summary()

    # ── No results ────────────────────────────
    if not destinations:
        return (
            "Xin chào! Tôi rất muốn tư vấn địa điểm du lịch cho bạn, "
            "nhưng dựa trên các bộ lọc hiện tại, chưa tìm thấy điểm đến nào phù hợp.\n\n"
            "💡 Gợi ý: Bạn hãy thử điều chỉnh lại yêu cầu — ví dụ thay đổi mùa du lịch, "
            "loại hình hoặc ngân sách — để hệ thống tìm kiếm lại nhé!"
        )

    pref_summary = _format_pref_summary(prefs)
    lines = [
        f"Xin chào! Dựa trên nhu cầu của bạn ({pref_summary}), "
        f"hệ thống đã phân tích và đối soát với kho luật kết hợp Apriori "
        f"cùng phân cụm K-Means.\n"
    ]

    # ── Mention matched rules ─────────────────
    if rules:
        lines.append("📊 **Quy luật hành vi du lịch liên quan:**")
        for r in rules[:3]:
            ant  = ", ".join(r["antecedents"])
            cons = ", ".join(r["consequents"])
            conf = r["confidence"] * 100
            lift = r.get("lift", 1.0)
            lines.append(
                f"  • {{{ant}}} ➜ {{{cons}}} "
                f"(Độ tin cậy: {conf:.1f}%, Lift: {lift:.2f})"
            )
        lines.append("")

    # ── Top destinations ─────────────────────
    lines.append("🌍 **Các điểm đến hàng đầu dành cho bạn:**\n")
    ICONS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣"]

    for i, dest in enumerate(destinations[:6]):
        icon  = ICONS[i] if i < len(ICONS) else f"{i+1}."
        name  = dest.get("Destination Name", "N/A")
        country = dest.get("Country", "N/A")
        season  = SEASON_VI.get(dest.get("Best Season", ""), dest.get("Best Season", "N/A"))
        cost    = dest.get("Avg Cost (USD/day)", "N/A")
        dtype_vi = CATEGORY_VI.get(dest.get("Type", ""), dest.get("Type", "N/A"))
        dtype   = dtype_vi
        desc    = dest.get("Description", "")
        rating  = dest.get("Rating", None)
        suitable= dest.get("Suitable For", None)

        lines.append(f"{icon} **{name}** ({country})")
        lines.append(f"   🗂 Loại hình : {dtype}")
        lines.append(f"   🌤 Mùa tốt nhất : {season}")
        lines.append(f"   💰 Chi phí TB : ${cost}/ngày")
        if rating:
            lines.append(f"   ⭐ Đánh giá    : {rating}/5")
        if suitable:
            lines.append(f"   👥 Phù hợp với : {suitable}")
        if desc and str(desc).lower() not in ("nan", ""):
            # Truncate long descriptions
            short_desc = str(desc)[:200] + ("…" if len(str(desc)) > 200 else "")
            lines.append(f"   📝 {short_desc}")
        lines.append("")

    lines.append(
        "💡 Nhấp vào tên điểm đến trên giao diện để xem vị trí "
        "trực quan trên **World Travel Map** (Leaflet.js)!\n"
        "Chúc bạn có một chuyến đi tuyệt vời! ✈️"
    )
    return "\n".join(lines)

# ─────────────────────────────────────────────
# DATABASE STATISTICS COMPILATION
# ─────────────────────────────────────────────
def get_system_database_summary() -> str:
    """Group all destinations by country and return a formatted string summary."""
    try:
        from mining.mongodb_storage import db_storage
        dests = db_storage.load_destinations()
        if not dests:
            return "Hệ thống hiện chưa có dữ liệu điểm đến."
            
        # Group by country
        by_country = {}
        for d in dests:
            c = d.get("Country", "Unknown")
            name = d.get("Destination Name", "N/A")
            if c not in by_country:
                by_country[c] = []
            by_country[c].append(name)
            
        summary_lines = [
            f"Tổng số điểm đến trong hệ thống: {len(dests)}",
            f"Tổng số quốc gia: {len(by_country)}",
            "Danh sách các nước và điểm đến tương ứng:"
        ]
        for country, names in sorted(by_country.items()):
            sorted_names = sorted(names)
            if len(sorted_names) > 15:
                names_str = ", ".join(sorted_names[:15]) + f" và {len(sorted_names) - 15} điểm đến khác"
            else:
                names_str = ", ".join(sorted_names)
            summary_lines.append(f"  - {country} ({len(names)} điểm đến): {names_str}")
        return "\n".join(summary_lines)
    except Exception as e:
        return f"Không thể tải thống kê hệ thống: {e}"

# ─────────────────────────────────────────────
# RESPONSE GENERATION – GEMINI
# ─────────────────────────────────────────────
def generate_response(
    message: str,
    prefs: dict,
    destinations: list,
    rules: list,
    conversation_history: list | None = None,
    recommendation_context_str: str = "",
    is_context_followup: bool = False,
    user_profile: dict = None,
    intent: str = "travel_query",
) -> str:
    """Generate Vietnamese response via Gemini API; falls back to rule-based."""
    # Check if this is a query about system database info
    system_db_summary = ""
    _SYSTEM_INFO_KEYWORDS = [
        "bao nhiêu điểm đến", "bao nhiêu quốc gia", "quốc gia nào", "nước nào",
        "danh sách điểm đến", "danh sách quốc gia", "liệt kê", "có những điểm đến",
        "thống kê", "hệ thống có bao nhiêu", "từng nước có", "từng quốc gia có"
    ]
    is_system_info_query = any(kw in message.lower() for kw in _SYSTEM_INFO_KEYWORDS)
    if is_system_info_query:
        system_db_summary = get_system_database_summary()

    if model is None or (not destinations and not is_system_info_query and intent in ("travel_query", "itinerary_request", "comparison_request")):
        return generate_response_fallback(message, prefs, destinations, rules, user_profile=user_profile)

    # Build context string for destinations
    dest_lines = []
    for i, d in enumerate(destinations[:6], 1):
        dtype_vi = CATEGORY_VI.get(d.get('Type', ''), d.get('Type', 'N/A'))
        suitable = d.get('Suitable For', 'N/A')
        dest_lines.append(
            f"{i}. {d.get('Destination Name')} ({d.get('Country')}) – "
            f"Loại: {dtype_vi}, Mùa tốt nhất: {d.get('Best Season')}, "
            f"Chi phí: ${d.get('Avg Cost (USD/day)')}/ngày, "
            f"Phù hợp: {suitable}. "
            f"Mô tả: {str(d.get('Description', 'N/A'))[:250]}"
        )
    dest_label = (
        "★ CÁC ĐIỂM ĐẾN ĐANG ĐƯỢC THẢO LUẬN (người dùng hỏi về những nơi này):"
        if is_context_followup else
        "Top các điểm đến đề xuất:"
    )
    dest_str = "\n".join(dest_lines)

    rule_lines = []
    for r in rules[:3]:
        rule_lines.append(
            f"  • {{{', '.join(r['antecedents'])}}} ➜ {{{', '.join(r['consequents'])}}} "
            f"(conf={r['confidence']:.2f}, lift={r.get('lift', 1.0):.2f})"
        )
    rules_str = "\n".join(rule_lines) or "  (Không có quy luật nào khớp)"

    # Build preference summary
    pref_summary = _format_pref_summary(prefs)

    # Build proper contents array for Gemini chat format
    contents = []
    if conversation_history:
        # Get up to last 16 turns (excluding the current user message) for richer context
        # 16 turns = 8 back-and-forth exchanges, balances context depth vs latency
        # Tăng từ 12 lên 16 để chatbot có thể nhớ tốt hơn các cuộc hội thoại dài
        recent = conversation_history[-16:-1] if len(conversation_history) > 1 else conversation_history
        
        # Merge consecutive roles and drop leading 'model' messages to satisfy Gemini API constraints
        merged_history = []
        for turn in recent:
            role = "user" if turn["role"] == "user" else "model"
            # Lấy nội dung từ key 'content' (format session store)
            turn_content = turn.get("content", "")
            is_context_msg = turn.get("is_context", False)
            
            if isinstance(turn_content, list):
                turn_content = " ".join(str(p) for p in turn_content)
            turn_content = str(turn_content).strip()
            
            if not turn_content:
                continue
            
            # Nếu là tin nhắn context tự động, thêm label để Gemini biết
            # nhưng vẫn giữ lại để không mất thông tin
            if is_context_msg and role == "user":
                turn_content = f"[Ngữ cảnh hệ thống: {turn_content}]"
                
            if not merged_history:
                if role == "model":
                    continue  # Drop leading model messages
                merged_history.append({"role": role, "parts": [turn_content]})
            else:
                if merged_history[-1]["role"] == role:
                    # Merge consecutive same-role turns (Gemini API requirement)
                    merged_history[-1]["parts"][0] += "\n\n" + turn_content
                else:
                    merged_history.append({"role": role, "parts": [turn_content]})
        
        contents = merged_history
        logger.info(f"[Gemini] Using {len(contents)} conversation turns for context")

    # ── Build personalization block from user_profile ────────────────────────
    personalization_block = ""
    if user_profile:
        user_name_gpt  = user_profile.get("name", "").strip()
        saved_prefs    = user_profile.get("preferences") or {}
        pref_parts     = []
        if saved_prefs.get("season"):
            pref_parts.append(f"Mùa ưa thích: **{SEASON_VI.get(saved_prefs['season'], saved_prefs['season'])}**")
        if saved_prefs.get("category"):
            pref_parts.append(f"Loại hình: **{CATEGORY_VI.get(saved_prefs['category'], saved_prefs['category'])}**")
        if saved_prefs.get("budget"):
            pref_parts.append(f"Ngân sách: **{BUDGET_VI.get(saved_prefs['budget'], saved_prefs['budget'])}**")

        lines_p = []
        if user_name_gpt:
            lines_p.append(f"  • Tên người dùng: **{user_name_gpt}** → Hãy xưng hô thân thiện bằng tên khi phù hợp (đừng lạm dụng).")
        if pref_parts:
            lines_p.append(f"  • Sở thích đã lưu: {', '.join(pref_parts)}")
            lines_p.append("    → Ưu tiên gợi ý phù hợp với sở thích này. Nhắc đến sở thích khi giải thích lý do đề xuất.")
        else:
            lines_p.append("  • Người dùng chưa có sở thích được lưu → hỏi thăm nhẹ để tìm hiểu thêm.")

        if lines_p:
            personalization_block = (
                "\n╔══════════════════════════════════════════╗\n"
                "║        THÔNG TIN CÁ NHÂN HOÁ             ║\n"
                "╚══════════════════════════════════════════╝\n"
                + "\n".join(lines_p)
                + "\n"
            )

    # Build follow-up instruction if needed
    followup_instruction = ""
    if is_context_followup:
        dest_names = ", ".join(
            d.get("Destination Name", "N/A") for d in destinations[:12]
        )
        if len(destinations) == 1:
            followup_instruction = f"""
⚡ NHIỆM VỤ NGAY LÚC NÀY (ƯU TIÊN CAO NHẤT):
Người dùng đang hỏi về điểm đến: 👉 {dest_names}
Họ có thể dùng các từ tham chiếu như "điểm đến này", "nơi đó", "chỗ đó", "ở đây", "chuyến đi" để ám chỉ điểm đến trên.
Hãy TRẢ LỜI TRỰC TIẾP về điểm đến này. KHÔNG được đề xuất điểm đến mới khác.
Tư vấn chi tiết DỰA TRÊN CHÍNH NƠI ĐÓ theo câu hỏi của người dùng (thời tiết, chi phí, lịch trình, ẩm thực, di chuyển...).
"""
        else:
            followup_instruction = f"""
⚡ NHIỆM VỤ NGAY LÚC NÀY (ƯU TIÊN CAO NHẤT):
Người dùng vừa xem danh sách gợi ý và đang hỏi về CÁC ĐIỂM ĐẾN CỤ THỂ này:
  👉 {dest_names}

Hãy TRẢ LỜI TRỰC TIẾP về những điểm đến trên. KHÔNG được đề xuất điểm đến mới khác.
Phân tích, so sánh, hoặc tư vấn DỰA TRÊN CHÍNH NHỮNG NƠI ĐÓ theo câu hỏi của người dùng.
"""

    db_summary_block = ""
    if system_db_summary:
        db_summary_block = f"""
★ THÔNG TIN THỐNG KÊ TOÀN BỘ CƠ SỞ DỮ LIỆU CỦA HỆ THỐNG:
{system_db_summary}
"""

    current_query_context = f"""
{personalization_block}

═══════════════════════════════════════════════
BỐI CẢNH YÊU CẦU VÀ DỮ LIỆU ĐANG CÓ:
═══════════════════════════════════════════════
{followup_instruction}
{recommendation_context_str}
{db_summary_block}

DỮ LIỆU HỆ THỐNG (nếu liên quan):
  Nhu cầu: {pref_summary} | Quy luật Apriori: {rules_str}
  {dest_label}
{dest_str}

❗ HƯỚNG DẪN XỬ LÝ HỘI THOẠI:
  • Đây là cuộc hội thoại nhiều lượt. Hãy đọc kỹ LỊCH SỬ HỘI THOẠI phía trên để hiểu ngữ cảnh.
  • Nếu người dùng dùng từ tham chiếu như "điểm đến này", "nơi đó", "chỗ đó", "ở đây", "vừa rồi"... → họ đang ám chỉ điểm đến đã được nhắc đến trong lịch sử trò chuyện.
  • Trả lời ĐÚNG điểm đến được đề cập, KHÔNG đoán sai hoặc gợi ý điểm khác.
  • Nếu người dùng nhắc lại hoặc hỏi thêm về nội dung đã trả lời trước đó, hãy mở rộng/thay đổi góc nhìn thay vì lặp lại y hệt.

CÂU HỎI HIỆN TẠI CỦA NGƯỜI DÙNG:
"{message}"
"""
    # Ensure alternating roles by merging if the last message was also 'user'
    if contents and contents[-1]["role"] == "user":
        contents[-1]["parts"][0] += "\n\n" + current_query_context
    else:
        contents.append({"role": "user", "parts": [current_query_context]})

    try:
        # Add generation config for faster responses
        import google.generativeai.types as genai_types
        generation_config = genai_types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1000,  # Allow slightly longer responses for richer context
        )
        response = model.generate_content(
            contents=contents,
            generation_config=generation_config
        )
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        # Check for quota errors
        if "429" in error_msg or "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
            logger.warning(f"Gemini API quota exceeded. Using fallback response.")
        else:
            logger.warning(f"Gemini response generation failed: {e}. Using fallback.")
            # Only write detailed error log for non-quota errors
            import traceback
            try:
                with open('gemini_error.txt', 'w', encoding='utf-8') as err_f:
                    err_f.write(traceback.format_exc())
                    err_f.write("\n\n=== CONTENTS (serialized) ===\n")
                    import json
                    err_f.write(json.dumps(contents, ensure_ascii=False, indent=2))
            except:
                pass  # Ignore file write errors
        
        # Always fallback gracefully
        return generate_response_fallback(message, prefs, destinations, rules, user_profile=user_profile)

# ─────────────────────────────────────────────
# QUICK INTENT RESPONSES
# ─────────────────────────────────────────────
def _greet_response(user_name: str = "") -> str:
    """Lời chào cá nhân hóa theo tên và thời điểm trong ngày."""
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Chào buổi sáng"
        emoji = "☀️"
    elif hour < 18:
        greeting = "Chào buổi chiều"
        emoji = "🌤"
    else:
        greeting = "Chào buổi tối"
        emoji = "🌙"
    # Xưng hô bằng tên nếu biết
    name_part = f" **{user_name}**" if user_name else ""
    return (
        f"{greeting}{name_part}! {emoji} 👋 Tôi là **Trợ lý Du lịch AI** — người đồng hành trên mọi hành trình!\n\n"
        "Tôi có thể giúp bạn:\n"
        "  🌍 Gợi ý điểm đến theo mùa, ngân sách, phong cách\n"
        "  📋 Lên lịch trình chi tiết từng ngày\n"
        "  🛂 Tư vấn visa & thủ tục nhập cảnh\n"
        "  🌦 Thông tin thời tiết & mùa du lịch tốt nhất\n"
        "  🍜 Khám phá ẩm thực & văn hóa địa phương\n"
        "  💰 So sánh chi phí & gợi ý tiết kiệm\n"
        "  🏨 Tư vấn chỗ ở phù hợp\n"
        "  🚌 Hướng dẫn di chuyển nội địa & quốc tế\n\n"
        "Hãy hỏi tôi bất cứ điều gì về du lịch! 😊"
    )

def _farewell_response(user_name: str = "") -> str:
    """Lời tạm biệt cá nhân hóa theo tên."""
    name_part = f" **{user_name}**" if user_name else ""
    return (
        f"Cảm ơn{name_part} đã trò chuyện cùng Trợ lý Du lịch AI! 🙏\n"
        "Chúc bạn có chuyến đi an toàn, vui vẻ và thật nhiều kỷ niệm đẹp. ✈️🌏\n"
        "Khi nào cần tư vấn du lịch, hãy tìm lại tôi nhé! Hẹn gặp lại! 👋"
    )

def _no_entity_response() -> str:
    return (
        "Tôi là Trợ lý Du lịch AI, sẵn sàng hỗ trợ bạn! 🌏\n\n"
        "Bạn có thể hỏi tôi về:\n"
        "  🗺 **Gợi ý điểm đến**: \"Biển đẹp nào phù hợp cho gia đình mùa hè?\"\n"
        "  📅 **Lịch trình**: \"Lên lịch 7 ngày ở Nhật Bản cho tôi\"\n"
        "  🛂 **Visa**: \"Xin visa Hàn Quốc cần chuẩn bị gì?\"\n"
        "  🌦 **Thời tiết**: \"Tháng 3 đi Thái Lan có mưa không?\"\n"
        "  🍜 **Ẩm thực**: \"Phải ăn gì khi đến Nhật?\"\n"
        "  💰 **Chi phí**: \"Du lịch Châu Âu tốn khoảng bao nhiêu?\"\n"
        "  🏨 **Khách sạn**: \"Nên ở đâu ở Bali giá tốt?\"\n"
        "  🚌 **Di chuyển**: \"Từ Tokyo đến Osaka đi bằng gì?\"\n"
        "  🔒 **An toàn**: \"Đi một mình ở Maroc có an toàn không?\"\n\n"
        "Hãy thử đặt câu hỏi cụ thể hơn nhé! 😊"
    )

def _visa_response(message: str) -> str:
    m = message.lower()
    country_hint = ""
    for vn, en in VIETNAMESE_COUNTRIES.items():
        if vn in m:
            country_hint = en
            break
    if country_hint:
        return (
            f"🛂 **Thông tin Visa {country_hint}**\n\n"
            f"Để xin visa {country_hint}, bạn thường cần chuẩn bị:\n"
            "  📄 Hộ chiếu còn hạn ít nhất 6 tháng\n"
            "  📸 Ảnh nền trắng theo quy cách\n"
            "  📋 Đơn xin visa (điền đầy đủ)\n"
            "  💰 Sao kê ngân hàng 3 tháng gần nhất\n"
            "  ✈️ Vé máy bay khứ hồi (hoặc bằng chứng hành trình)\n"
            "  🏨 Xác nhận đặt phòng khách sạn\n\n"
            "⚠️ Lưu ý: Mỗi quốc gia có yêu cầu riêng. Hãy kiểm tra trang web Đại sứ quán "
            f"hoặc hỏi tôi chi tiết hơn về visa {country_hint} nhé!"
        )
    return (
        "🛂 **Tư vấn Visa du lịch**\n\n"
        "Tôi có thể tư vấn visa cho bạn! Hãy cho tôi biết bạn muốn đi nước nào?\n\n"
        "Ví dụ: \"Xin visa Nhật Bản cần gì?\", \"Hàn Quốc có miễn visa không?\"\n"
        "hoặc \"Thủ tục xin e-visa Ấn Độ như thế nào?\""
    )

def _weather_response(message: str) -> str:
    return (
        "🌦 **Thông tin Thời tiết & Khí hậu**\n\n"
        "Bạn muốn biết thời tiết ở đâu và vào thời điểm nào? \n"
        "Tôi có thể cung cấp thông tin về:\n"
        "  🌡 Nhiệt độ trung bình theo tháng\n"
        "  🌧 Mùa mưa / mùa khô\n"
        "  ❄️ Thời điểm có tuyết (nếu có)\n"
        "  🌸 Mùa hoa nở / đặc trưng thiên nhiên\n"
        "  ⚡ Cảnh báo thời tiết cực đoan\n\n"
        "Ví dụ: \"Tháng 12 đi Nhật Bản lạnh không?\" hoặc \"Bali mùa nào đẹp nhất?\""
    )

def _food_response(message: str) -> str:
    return (
        "🍜 **Khám phá Ẩm thực địa phương**\n\n"
        "Ẩm thực là linh hồn của mỗi chuyến đi! Tôi có thể giúp bạn:\n"
        "  🍱 Giới thiệu món ăn đặc sản không thể bỏ qua\n"
        "  🏪 Gợi ý khu phố ẩm thực / chợ đêm\n"
        "  💡 Mẹo order đồ ăn cho người lần đầu\n"
        "  🥜 Lưu ý dị ứng thực phẩm & ăn chay\n"
        "  💰 Tham khảo mức giá ăn uống\n\n"
        "Bạn muốn khám phá ẩm thực nước nào? 😋"
    )

def _transport_response(message: str) -> str:
    return (
        "🚌 **Hướng dẫn Di chuyển**\n\n"
        "Tôi có thể tư vấn phương tiện di chuyển cho bạn:\n"
        "  ✈️ Hãng bay & giá vé phù hợp\n"
        "  🚄 Tàu hỏa / tàu cao tốc nội địa\n"
        "  🚌 Xe buýt / xe khách liên tỉnh\n"
        "  🚇 Tàu điện ngầm / Metro tại các thành phố\n"
        "  🛺 Phương tiện địa phương đặc trưng\n"
        "  🚗 Thuê xe tự lái hoặc có tài xế\n\n"
        "Hãy cho tôi biết bạn đang đi từ đâu đến đâu nhé!"
    )

def _safety_response(message: str) -> str:
    return (
        "🔒 **Tư vấn An toàn Du lịch**\n\n"
        "An toàn luôn là ưu tiên số 1! Tôi có thể chia sẻ:\n"
        "  🌍 Đánh giá mức độ an toàn của điểm đến\n"
        "  ⚠️ Các khu vực / tình huống cần tránh\n"
        "  💊 Bảo hiểm du lịch nên mua loại nào\n"
        "  📱 Số khẩn cấp & Đại sứ quán Việt Nam\n"
        "  🏦 Mẹo bảo quản tiền & giấy tờ khi đi phượt\n\n"
        "Hãy cho tôi biết bạn lo lắng về vấn đề gì và ở đâu?"
    )

# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────
def process_chat_query(
    user_message: str,
    session_id: str = "default",
    recommendation_context: dict = None,
    conversation_history: list = None
) -> dict:
    """
    Full NLP pipeline:
    1. Intent detection
    2. Entity extraction
    3. Apriori rule matching
    4. Candidate retrieval & multi-factor scoring
    5. Content-based TF-IDF re-ranking
    6. Vietnamese response generation

    Returns a dict with keys:
      - response        : str   — final answer shown to user
      - preferences     : dict  — extracted entities
      - recommendations : list  — top ranked destinations (max 6)
      - intent          : str   — detected intent
      - matched_rules   : list  — Apriori rules that fired
    """
    logger.info(f"[Pipeline] Session={session_id} | Query: '{user_message}'")

    # ── Session management ────────────────────
    if session_id not in _session_store:
        _session_store[session_id] = {
            "history": [], 
            "last_prefs": {}, 
            "last_discussed_dest": None,
            "mentioned_destinations": []  # Lưu tất cả điểm đến đã thảo luận
        }
    session = _session_store[session_id]

    # Synchronize history from frontend if provided to support stateless/restarts
    if conversation_history:
        # Rebuild session history from frontend, keeping context messages for reference
        session["history"] = []
        for turn in conversation_history:
            role = "user" if turn.get("role") == "user" else "assistant"
            content = turn.get("parts") or turn.get("content") or ""
            if content:
                # Giữ lại tất cả tin nhắn để Gemini có đủ ngữ cảnh
                # Chỉ đánh dấu loại tin nhắn để xử lý khác biệt nếu cần
                is_ctx_msg = turn.get("isContextMessage", False)
                session["history"].append({
                    "role": role, 
                    "content": content,
                    "is_context": is_ctx_msg
                })
        
        # Tránh duplicate tin nhắn hiện tại
        if session["history"] and session["history"][-1]["role"] == "user":
            last_user_msg = session["history"][-1]["content"]
            # So sánh nội dung sau khi chuẩn hóa khoảng trắng
            if last_user_msg.strip() == user_message.strip():
                session["history"].pop()

    has_history = len(session["history"]) > 0
    
    # Log history cho debugging
    logger.info(f"[Session] History length: {len(session['history'])}, has_history={has_history}")

    # ── Rút trích user_profile từ recommendation_context ──────────────────────
    user_profile = (recommendation_context or {}).get("user_profile") or {}
    user_name    = user_profile.get("name", "").strip()
    user_saved_prefs = user_profile.get("preferences") or {}
    logger.info(f"[Pipeline] User profile: name='{user_name}', saved_prefs={user_saved_prefs}")

    # ── 1. Intent detection ───────────────────
    intent = detect_intent(user_message)
    logger.info(f"[Pipeline] Intent: {intent}")

    # Append user message to history
    session["history"].append({"role": "user", "content": user_message})

    if intent == "greet":
        resp = _greet_response(user_name=user_name)
        session["history"].append({"role": "assistant", "content": resp})
        return {"response": resp, "preferences": {}, "recommendations": [],
                "intent": intent, "matched_rules": []}

    if intent == "farewell":
        resp = _farewell_response(user_name=user_name)
        session["history"].append({"role": "assistant", "content": resp})
        return {"response": resp, "preferences": {}, "recommendations": [],
                "intent": intent, "matched_rules": []}

    # ── Quick dispatch for non-destination intents (fallback mode only) ────────
    if model is None:
        _QUICK_HANDLERS = {
            "visa_inquiry":         _visa_response,
            "weather_inquiry":      _weather_response,
            "food_inquiry":         _food_response,
            "transport_inquiry":    _transport_response,
            "safety_inquiry":       _safety_response,
        }
        if intent in _QUICK_HANDLERS:
            resp = _QUICK_HANDLERS[intent](user_message)
            session["history"].append({"role": "assistant", "content": resp})
            return {"response": resp, "preferences": {}, "recommendations": [],
                    "intent": intent, "matched_rules": []}

    # ── 2. Entity extraction ──────────────────
    import time
    t_start = time.time()
    prefs = extract_entities(user_message)
    t_extract = time.time() - t_start
    logger.info(f"[Perf] Entity extraction: {t_extract:.3f}s")
    
    non_null = {k: v for k, v in prefs.items() if v is not None and not k.startswith("_")}
    explicit_pref_keys = set(non_null.keys())
    is_follow_up_without_entities = (len(non_null) == 0 and has_history)

    # Merge session preferences:
    # - Nếu là follow-up không có entity mới → merge TOÀN BỘ session prefs (người dùng đang hỏi tiếp)
    # - Nếu có ít entity mới (≤ 2) → merge để bổ sung những gì còn thiếu
    # - Nếu có nhiều entity mới → ưu tiên hoàn toàn entity mới (người dùng đổi chủ đề)
    if is_follow_up_without_entities and session["last_prefs"]:
        # Follow-up thuần túy: giữ nguyên toàn bộ prefs phiên trước
        prefs = {**prefs, **session["last_prefs"]}
    elif len(non_null) <= 2 and session["last_prefs"]:
        # Có ít entity mới: bổ sung những key còn thiếu từ phiên trước
        merged = {**session["last_prefs"], **non_null}
        prefs = {**prefs, **merged}

    session["last_prefs"] = {k: v for k, v in prefs.items() if v and not k.startswith("_")}

    # ── Bổ sung từ sở thích đã lưu của user (ưu tiên thấp nhất) ─────────────
    # Chỉ điền khi message hiện tại KHÔNG chỉ định rõ → không ghi đè ý định tường minh
    for key in ["season", "category", "budget"]:
        if user_saved_prefs.get(key) and not prefs.get(key):
            prefs[key] = user_saved_prefs[key]
            logger.info(f"[Pipeline] Pre-filled from user profile: {key}={user_saved_prefs[key]}")

    # ── Merge recommendation context from frontend wizard ─────
    rec_context_str = ""
    if recommendation_context:
        ctx_criteria = recommendation_context.get("criteria", {})
        ctx_dests = recommendation_context.get("destinations", [])
        
        viewing_dest_ctx = recommendation_context.get("currentViewingDestination")
        if viewing_dest_ctx:
            rec_context_str += f"\nLƯU Ý ĐẶC BIỆT: NGƯỜI DÙNG HIỆN ĐANG Ở TRANG CHI TIẾT CỦA ĐIỂM ĐẾN '{viewing_dest_ctx}'. Nếu họ dùng các từ như 'đó', 'nơi này', 'chỗ đấy', 'đây', 'điểm đến này', hãy ngầm hiểu là họ đang hỏi về '{viewing_dest_ctx}'.\n"
        elif session.get("last_discussed_dest"):
            rec_context_str += f"\nLƯU Ý: Trong cuộc trò chuyện này, điểm đến gần nhất mà người dùng đã thảo luận là '{session['last_discussed_dest']}'. Nếu họ dùng các từ tham chiếu như 'điểm đến này', 'nơi đó', 'chỗ đó', hãy ngầm hiểu là họ đang hỏi về '{session['last_discussed_dest']}'.\n"

        # Merge wizard criteria into prefs if not already set by current message
        for key in ["season", "category", "budget"]:
            if ctx_criteria.get(key) and key not in explicit_pref_keys:
                prefs[key] = ctx_criteria[key]
                logger.info(f"[Pipeline] Merged recommendation context {key}={ctx_criteria[key]}")

        # Save merged prefs
        session["last_prefs"] = {k: v for k, v in prefs.items() if v and not k.startswith("_")}

        # Build a descriptive context string for the LLM prompt
        if ctx_criteria:
            parts = []
            if ctx_criteria.get("season"):
                parts.append(f"Mùa: {SEASON_VI.get(ctx_criteria['season'], ctx_criteria['season'])}")
            if ctx_criteria.get("category"):
                parts.append(f"Loại hình: {CATEGORY_VI.get(ctx_criteria['category'], ctx_criteria['category'])}")
            if ctx_criteria.get("budget"):
                parts.append(f"Ngân sách: {BUDGET_VI.get(ctx_criteria['budget'], ctx_criteria['budget'])}")
            rec_context_str += f"\nNgười dùng đang xem trang gợi ý với tiêu chí: {', '.join(parts)}.\n"

        if ctx_dests:
            dest_summaries = []
            for d in ctx_dests:
                dest_summaries.append(
                    f"  - {d.get('name', 'N/A')} ({d.get('country', 'N/A')}) "
                    f"– Loại: {d.get('type', 'N/A')}, Mùa tốt nhất: {d.get('season', 'N/A')}, "
                    f"Chi phí: ${d.get('cost', 'N/A')}/ngày"
                )
            rec_context_str += "Các điểm đến đã được hệ thống gợi ý cho người dùng:\n"
            rec_context_str += "\n".join(dest_summaries) + "\n"

        logger.info(f"[Pipeline] Recommendation context injected: {len(ctx_dests)} destinations")

    session["last_prefs"] = {k: v for k, v in prefs.items() if v and not k.startswith("_")}

    # Guard: if nothing extracted AND we don't have conversation history, ask for clarification
    useful_keys = ["season", "budget", "category", "country", "continent", "duration_days", "traveler_type"]
    if not has_history and not any(prefs.get(k) for k in useful_keys):
        if model is None:
            resp = _no_entity_response()
            session["history"].append({"role": "assistant", "content": resp})
            return {"response": resp, "preferences": prefs, "recommendations": [],
                    "intent": intent, "matched_rules": []}
        # Khi có Gemini: vẫn gọi Gemini nhưng với danh sách điểm đến rỗng
        # để Gemini tự xử lý câu hỏi chung (không ép gợi ý khi không có filter)
        # → pipeline tiếp tục nhưng candidates sẽ rỗng ở bước 4

    # ── Detect whether this is a follow-up question about the wizard context destinations ──
    # If yes, skip the DB query and answer directly about the context destinations.
    
    # Mở rộng pattern để nhận diện câu hỏi follow-up tốt hơn
    _CONTEXT_FOLLOWUP_PATTERNS = [
        # Từ so sánh và lựa chọn
        "trong số", "điểm nào", "nơi nào", "chỗ nào", "cái nào", "lựa chọn nào",
        "các điểm", "những điểm", "so sánh", "khác nhau", "nên đi đâu",
        "phù hợp", "có gì hay", "nhật xét", "đánh giá", "giới thiệu",
        "như thế nào", "tốt hơn", "gợi ý", "kết hợp", "hỏi thêm",
        "tôi nên", "bạn nghĩ", "bạn thấy", "trên đây", "các nơi",
        "which", "compare", "better", "suggest", "recommend", "prefer",
        
        # Từ tham chiếu ngữ cảnh
        "điểm đến này", "địa điểm này", "chỗ này", "nơi này",
        "điểm đến đó", "địa điểm đó", "chỗ đó", "nơi đó",
        "chuyến đi này", "hành trình này", "tour này",
        "ở đó", "tại đó", "đến đó", "về nơi", "về chỗ",
        
        # Từ kế hoạch và chuẩn bị
        "lên lịch", "lịch trình", "kế hoạch", "chuẩn bị",
        "chi phí", "ngân sách", "tốn bao nhiêu", "giá cả",
        "thời tiết", "khí hậu", "ẩm thực", "món ăn",
        "di chuyển", "phương tiện", "cách đi",
        
        # Từ tham chiếu thời gian và cuộc hội thoại
        "vừa rồi", "vừa gợi ý", "vừa đề xuất", "bạn vừa nói",
        "lúc nãy", "hồi nãy", "trước đó", "vừa nhắc",
        "bạn đã nói", "bạn đã gợi ý", "bạn đã đề cập",
        "như bạn đã", "theo như", "dựa vào",
        
        # Từ hỏi tiếp theo
        "còn", "thêm", "nữa", "khác", "tiếp theo",
        "thế còn", "vậy còn", "còn gì", "và",
        
        # Đại từ chỉ định
        "đó", "này", "ấy", "kia", "đấy",
        "it", "that", "this", "those", "these",
    ]
    
    viewing_dest = (recommendation_context or {}).get("currentViewingDestination")
    _VIEWING_FOLLOWUP_PATTERNS = [
        "nơi này", "nơi đây", "địa điểm này", "chỗ này", "ở đây", "đó", "chỗ đó", "nơi đó", "địa điểm đó",
        # Tham chiếu điểm đến
        "điểm đến này", "điểm này", "điểm đến đó", "điểm đó",
        "chuyến đi", "hành trình này", "chuyến này",
        "ở đó", "tại đó", "đến đó", "về nơi đó", "về chỗ đó",
        "nơi bạn vừa", "chỗ bạn vừa", "điểm bạn vừa",
        "vừa rồi", "vừa gợi ý", "vừa đề xuất", "vừa nhắc",
        "lúc nãy", "hồi nãy", "trước đó",
        # Đại từ ngắn gọn
        "đó", "này", "đấy", "kia", "ấy",
        "it", "there", "here",
    ]
    
    is_viewing_dest_followup = False
    # Ưu tiên viewing_dest từ URL hiện tại, fallback sang last_discussed_dest từ session
    effective_viewing_dest = viewing_dest or session.get("last_discussed_dest")
    if effective_viewing_dest:
        # Kiểm tra các pattern follow-up
        msg_lower = user_message.lower()
        if any(p in msg_lower for p in _VIEWING_FOLLOWUP_PATTERNS):
            is_viewing_dest_followup = True
            logger.info(f"[Pipeline] Detected viewing dest follow-up pattern in message")
        # Nếu không có filter mới và có history → coi như đang hỏi tiếp về điểm đến đó
        elif has_history and not any(prefs.get(k) for k in ["season", "budget", "category", "country", "continent"]):
            is_viewing_dest_followup = True
            logger.info(f"[Pipeline] No new filters + has history → assuming viewing dest follow-up")
            
    ctx_dests_raw = (recommendation_context or {}).get("destinations", [])

    # Chỉ kích hoạt context followup khi:
    # 1. Có destinations context từ wizard
    # 2. Câu hỏi chứa pattern follow-up HOẶC không có entity mới nhưng có history
    # 3. Người dùng KHÔNG đưa ra filter mới mạnh (country/continent mới)
    #    → tránh dương tính giả khi user muốn tìm điểm đến hoàn toàn mới
    explicit_country = non_null.get("country")
    explicit_continent = non_null.get("continent")
    _new_strong_filter = (
        explicit_country and explicit_country not in [d.get("country") for d in ctx_dests_raw]
    ) or (
        explicit_continent and len(non_null) >= 3
    )
    
    msg_lower = user_message.lower()
    has_followup_pattern = any(p in msg_lower for p in _CONTEXT_FOLLOWUP_PATTERNS)
    has_no_new_entities = (len(non_null) == 0 and has_history)
    
    is_context_followup = (
        len(ctx_dests_raw) > 0 and
        (has_followup_pattern or has_no_new_entities) and
        not _new_strong_filter
    )
    
    if is_viewing_dest_followup:
        is_context_followup = True  # We will handle it similarly
        
    logger.info(f"[Pipeline] is_context_followup={is_context_followup}, is_viewing_dest_followup={is_viewing_dest_followup}")
    logger.info(f"[Pipeline] ctx_dests={len(ctx_dests_raw)}, new_strong_filter={_new_strong_filter}")
    logger.info(f"[Pipeline] has_followup_pattern={has_followup_pattern}, has_no_new_entities={has_no_new_entities}")

    # ── 3. Apriori rule matching ──────────────
    matched_rules = get_matching_rules(prefs)
    rule_countries = []
    for r in matched_rules:
        for item in r.get("consequents", []):
            if "Country:" in item:
                rule_countries.append(item.replace("Country:", "").strip())

    # ── 4. Candidate retrieval & scoring ──────────────────────────────────────
    #
    # CASE A – Context follow-up: the user is asking about wizard-recommended
    #   destinations that are already displayed on screen. We skip the DB query
    #   and answer ONLY about those destinations so the answer stays relevant.
    #
    # CASE B – Normal query: search the full database as usual.
    # ──────────────────────────────────────────────────────────────────────────
    if is_viewing_dest_followup and effective_viewing_dest:
        all_dests_list = db_storage.load_destinations()
        full = next((d for d in all_dests_list if d.get("Destination Name") == effective_viewing_dest), None)
        if full:
            full_dict = dict(full)
            full_dict["match_score"] = 100
            top_recommendations = [full_dict]
            # Cập nhật last_discussed_dest vào session
            session["last_discussed_dest"] = effective_viewing_dest
            logger.info(f"[Pipeline] Viewing dest follow-up: locking onto '{effective_viewing_dest}'")
        else:
            is_viewing_dest_followup = False
            top_recommendations = []

    if not is_viewing_dest_followup and is_context_followup and ctx_dests_raw:
        # Re-hydrate context destinations into the same dict shape used by the
        # rest of the pipeline so downstream code works transparently.
        all_dests_list = db_storage.load_destinations()
        all_dests_lookup = {d.get("Destination Name", ""): dict(d) for d in all_dests_list}

        ctx_as_candidates = []
        for cd in ctx_dests_raw:
            name = cd.get("name", "")
            full = all_dests_lookup.get(name)
            if full:
                full["match_score"] = score_candidate(full, prefs, rule_countries)
                ctx_as_candidates.append(full)
            else:
                # Lightweight synthetic record from the context payload
                ctx_as_candidates.append({
                    "Destination Name":   name,
                    "Country":            cd.get("country", "N/A"),
                    "Type":               cd.get("type", "N/A"),
                    "Best Season":        cd.get("season", "N/A"),
                    "Avg Cost (USD/day)": cd.get("cost", "N/A"),
                    "Description":        "",
                    "match_score":        0,
                })
        top_recommendations = ctx_as_candidates
        logger.info(f"[Pipeline] Context follow-up: using {len(top_recommendations)} context destinations.")
    elif not is_viewing_dest_followup:
        # Normal DB-based pipeline
        # Use cached destinations to avoid repeated MongoDB loads
        global _destinations_cache, _cache_timestamp
        t_db_start = time.time()
        
        import time as time_module
        current_time = time_module.time()
        if _destinations_cache is None or (current_time - _cache_timestamp) > CACHE_TTL_SECONDS:
            all_dests = db_storage.load_destinations()
            _destinations_cache = all_dests
            _cache_timestamp = current_time
            logger.info(f"[Cache] Refreshed destinations cache ({len(all_dests)} destinations)")
        else:
            all_dests = _destinations_cache
            logger.info(f"[Cache] Using cached destinations ({len(all_dests)} destinations)")
        
        t_db = time.time() - t_db_start
        logger.info(f"[Perf] DB load: {t_db:.3f}s ({len(all_dests)} destinations)")
        
        explicit_country    = prefs.get("country")
        continent_countries = prefs.get("_continent_countries", [])
        filter_active = any(prefs.get(k) for k in ["season", "budget", "category",
                                                    "country", "continent"])
        
        t_filter_start = time.time()
        candidates = []
        for d in all_dests:
            dest = dict(d)
            if explicit_country:
                if dest.get("Country") != explicit_country:
                    continue
            elif continent_countries:
                if dest.get("Country") not in continent_countries:
                    continue
            elif filter_active:
                if score_candidate(dest, prefs, rule_countries) <= 0:
                    continue
            s = score_candidate(dest, prefs, rule_countries)
            dest["match_score"] = s
            candidates.append(dest)
        t_filter = time.time() - t_filter_start
        logger.info(f"[Perf] Filtering: {t_filter:.3f}s ({len(candidates)} candidates)")

        if not candidates:
            logger.warning(
                f"[Pipeline] No candidates after strict filter "
                f"(country={prefs.get('country')}). Broadening to all."
            )
            candidates = [dict(d) for d in all_dests]
            for d in candidates:
                d["match_score"] = score_candidate(d, prefs, rule_countries)

        # ── 5. Content-based TF-IDF re-ranking ────
        t_rank_start = time.time()
        ranked = content_recommender.rank_candidates(candidates, prefs)
        t_rank = time.time() - t_rank_start
        logger.info(f"[Perf] Content ranking: {t_rank:.3f}s")

        def sort_key(x):
            return (x.get("match_score", 0), x.get("content_score", 0.0) or 0.0)

        ranked.sort(key=sort_key, reverse=True)

        # Nếu không có entity và không có history (câu hỏi chung), không ép gợi ý điểm đến
        # → Gemini sẽ xử lý câu hỏi theo kiến thức chung, không dựa vào DB
        useful_keys_check = ["season", "budget", "category", "country", "continent", "duration_days", "traveler_type"]
        if not has_history and not any(prefs.get(k) for k in useful_keys_check):
            top_recommendations = []
            logger.info("[Pipeline] No entities & no history → returning empty recommendations for general question.")
        else:
            top_recommendations = ranked[:6]

    # ── 6. Response generation ────────────────────────────────────────────────
    t_gen_start = time.time()
    response_text = generate_response(
        user_message, prefs, top_recommendations,
        matched_rules, session["history"],
        recommendation_context_str=rec_context_str,
        is_context_followup=is_context_followup,
        user_profile=user_profile,
        intent=intent,
    )
    t_gen = time.time() - t_gen_start
    logger.info(f"[Perf] Response generation: {t_gen:.3f}s")
    
    session["history"].append({"role": "assistant", "content": response_text})

    # Cập nhật last_discussed_dest và mentioned_destinations từ top recommendations
    # để follow-up questions vẫn hiểu ngữ cảnh dù user chuyển trang
    if top_recommendations:
        first_dest_name = top_recommendations[0].get("Destination Name")
        if first_dest_name:
            session["last_discussed_dest"] = first_dest_name
            # Thêm vào danh sách các điểm đến đã đề cập (giới hạn 10 điểm gần nhất)
            if "mentioned_destinations" not in session:
                session["mentioned_destinations"] = []
            if first_dest_name not in session["mentioned_destinations"]:
                session["mentioned_destinations"].append(first_dest_name)
                session["mentioned_destinations"] = session["mentioned_destinations"][-10:]
            logger.info(f"[Session] Updated last_discussed_dest='{first_dest_name}'")
            logger.info(f"[Session] Mentioned destinations: {session['mentioned_destinations']}")

    t_total = time.time() - t_start
    logger.info(f"[Perf] TOTAL: {t_total:.3f}s (extract={t_extract:.3f}, db={t_db:.3f}, filter={t_filter:.3f}, rank={t_rank:.3f}, gen={t_gen:.3f})")
    logger.info(f"[Pipeline] Returning {len(top_recommendations)} recommendations.")

    return {
        "response":        response_text,
        "preferences":     prefs,
        "recommendations": top_recommendations,
        "intent":          intent,
        "matched_rules":   matched_rules,
    }

# ─────────────────────────────────────────────
# SESSION UTILITIES
# ─────────────────────────────────────────────
def clear_session(session_id: str = "default") -> None:
    """Reset conversation history and preferences for a session."""
    _session_store.pop(session_id, None)
    logger.info(f"[Session] Cleared session: {session_id}")

def get_session_history(session_id: str = "default") -> list:
    """Return conversation history for a session."""
    return _session_store.get(session_id, {}).get("history", [])

# ─────────────────────────────────────────────
# MAIN – QUICK SMOKE TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("Travel Recommendation Chatbot – Smoke Test")
    print("=" * 60)

    test_queries = [
        "Xin chào!",
        "Tôi muốn đi du lịch châu Á vào mùa thu, ngân sách tiết kiệm",
        "Gợi ý điểm đến biển cho cặp đôi, khoảng 7 ngày, sang trọng",
        "Nhật Bản mùa xuân đẹp không?",
        "Tạm biệt!",
    ]

    for q in test_queries:
        print(f"\n{'─'*60}")
        print(f"USER: {q}")
        result = process_chat_query(q, session_id="test_session")
        print(f"INTENT: {result['intent']}")
        print(f"PREFS : {result['preferences']}")
        print(f"RECS  : {len(result['recommendations'])} destinations")
        print(f"BOT   :\n{result['response'][:500]}...")
