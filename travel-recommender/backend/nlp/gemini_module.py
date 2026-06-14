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
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
model = None

if api_key and api_key.strip():
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("[OK] Gemini API initialized successfully.")
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

# In-memory session store: { session_id: { "history": [...], "last_prefs": {...} } }
_session_store: dict = {}

# ─────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────
_GREET_KEYWORDS = [
    "xin chào", "chào", "hello", "hi", "hey", "good morning",
    "good afternoon", "buổi sáng", "buổi chiều", "buổi tối",
]
_BYE_KEYWORDS = [
    "tạm biệt", "bye", "goodbye", "cảm ơn", "thank you", "thanks",
    "thôi nhé", "hẹn gặp lại",
]
_TRAVEL_KEYWORDS = [
    "du lịch", "đi", "đến", "thăm", "khám phá", "travel", "trip",
    "tour", "vacation", "holiday", "chuyến", "visit", "điểm đến",
    "địa điểm", "recommend", "gợi ý", "tư vấn", "suggest",
]

def detect_intent(message: str) -> str:
    """
    Returns one of: 'greet', 'farewell', 'travel_query', 'off_topic'
    """
    m = message.lower()
    if any(kw in m for kw in _GREET_KEYWORDS) and len(m.split()) <= 6:
        return "greet"
    if any(kw in m for kw in _BYE_KEYWORDS) and len(m.split()) <= 8:
        return "farewell"
    if any(kw in m for kw in _TRAVEL_KEYWORDS):
        return "travel_query"
    # Fallback: if any entity can be extracted, treat as travel query
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
    if any(w in m for w in ["xuân", "spring", "tết"]):
        entities["season"] = "Spring"
    elif any(w in m for w in ["hè", "hạ", "summer", "hè hè"]):
        entities["season"] = "Summer"
    elif any(w in m for w in ["thu", "autumn", "fall"]):
        entities["season"] = "Autumn"
    elif any(w in m for w in ["đông", "winter", "giáng sinh", "noel"]):
        entities["season"] = "Winter"

    # ── Budget ────────────────────────────────
    if any(w in m for w in ["rẻ", "tiết kiệm", "budget", "cheap", "thấp", "ít tiền", "không tốn nhiều"]):
        entities["budget"] = "Budget"
    elif any(w in m for w in ["vừa", "trung bình", "moderate", "affordable", "bình dân", "hợp lý", "phải chăng"]):
        entities["budget"] = "Moderate"
    elif any(w in m for w in ["đắt", "cao cấp", "expensive"]):
        entities["budget"] = "Expensive"
    elif any(w in m for w in ["sang trọng", "xa hoa", "luxury", "premium", "5 sao", "vip"]):
        entities["budget"] = "Luxury"

    # ── Category ─────────────────────────────
    if any(w in m for w in ["biển", "beach", "đảo", "bãi biển", "snorkeling", "lặn biển"]):
        entities["category"] = "Beach"
    elif any(w in m for w in ["núi", "mountain", "leo núi", "phượt", "trekking", "hiking"]):
        entities["category"] = "Mountain"
    elif any(w in m for w in ["văn hóa", "lịch sử", "cultural", "historical", "đền", "chùa",
                               "di tích", "bảo tàng", "kiến trúc"]):
        entities["category"] = "Cultural"
    elif any(w in m for w in ["thiên nhiên", "nature", "rừng", "cảnh quan", "sinh thái", "wildlife"]):
        entities["category"] = "Nature"
    elif any(w in m for w in ["mạo hiểm", "adventure", "phiêu lưu", "extreme", "bungee", "rafting"]):
        entities["category"] = "Adventure"
    elif any(w in m for w in ["đô thị", "thành phố", "urban", "sầm uất", "mua sắm", "shopping",
                               "nightlife", "ăn uống", "ẩm thực"]):
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
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip possible markdown code fences
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text)
        entities = json.loads(text)
        # Merge with fallback for any missing keys
        fallback = extract_entities_fallback(message)
        for k, v in fallback.items():
            if k not in entities or entities[k] is None:
                entities[k] = v
        logger.info(f"[Entity] Gemini extracted: {entities}")
        return entities
    except Exception as e:
        logger.warning(f"Gemini entity extraction failed: {e}. Using fallback.")
        return extract_entities_fallback(message)

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
    rules: list
) -> str:
    """Fallback Vietnamese NLP response generator."""

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
        dtype   = dest.get("Type", "N/A")
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
# RESPONSE GENERATION – GEMINI
# ─────────────────────────────────────────────
def generate_response(
    message: str,
    prefs: dict,
    destinations: list,
    rules: list,
    conversation_history: list | None = None,
    recommendation_context_str: str = ""
) -> str:
    """Generate Vietnamese response via Gemini API; falls back to rule-based."""
    if model is None or not destinations:
        return generate_response_fallback(message, prefs, destinations, rules)

    # Build context string for top-6 destinations
    dest_lines = []
    for i, d in enumerate(destinations[:6], 1):
        dest_lines.append(
            f"{i}. {d.get('Destination Name')} ({d.get('Country')}) – "
            f"Loại: {d.get('Type')}, Mùa tốt nhất: {d.get('Best Season')}, "
            f"Chi phí: ${d.get('Avg Cost (USD/day)')}/ngày, "
            f"Phù hợp: {d.get('Suitable For', 'N/A')}. "
            f"Mô tả: {str(d.get('Description', 'N/A'))[:250]}"
        )
    dest_str  = "\n".join(dest_lines)

    rule_lines = []
    for r in rules[:3]:
        rule_lines.append(
            f"  • {{{', '.join(r['antecedents'])}}} ➜ {{{', '.join(r['consequents'])}}} "
            f"(conf={r['confidence']:.2f}, lift={r.get('lift', 1.0):.2f})"
        )
    rules_str = "\n".join(rule_lines) or "  (Không có quy luật nào khớp)"

    # Build preference summary
    pref_summary = _format_pref_summary(prefs)

    # Optional: include recent conversation history for context
    history_str = ""
    if conversation_history:
        recent = conversation_history[-10:]  # last 5 turns
        history_str = "\nLỊCH SỬ HỘI THOẠI TRƯỚC ĐÓ:\n"
        for turn in recent:
            role = "Người dùng" if turn["role"] == "user" else "Trợ lý AI"
            history_str += f"  - {role}: {turn['content']}\n"

    prompt = f"""
Bạn là trợ lý ảo tư vấn du lịch thông minh, sử dụng AI và khai phá dữ liệu.

{history_str}
{recommendation_context_str}

CÂU HỎI HIỆN TẠI CỦA NGƯỜI DÙNG:
"{message}"

THÔNG TIN TRÍCH XUẤT VÀ DỮ LIỆU ĐỀ XUẤT:
  - Nhu cầu hiện tại: {pref_summary}
  - Sở thích/tiêu chí: Mùa {prefs.get('season')}, Ngân sách {prefs.get('budget')}, Loại hình {prefs.get('category')}, Quốc gia {prefs.get('country')}, Loại khách {prefs.get('traveler_type')}, Số ngày {prefs.get('duration_days')}
  - Quy luật Apriori khai phá từ MongoDB:
{rules_str}
  - Top các điểm đến đề xuất từ hệ thống:
{dest_str}

---
HƯỚNG DẪN TRẢ LỜI (HÃY ĐỌC KỸ VÀ TUÂN THỦ NGHIÊM NGẶT):

Bạn là một chuyên gia du lịch đa tài, luôn hướng tới việc cung cấp câu trả lời CỰC KỲ CHI TIẾT, ĐA NGỮ CẢNH và TRÁNH SỰ NHÀM CHÁN, LẶP LẠI KẾT CẤU.

Trường hợp A: Người dùng đang yêu cầu danh sách gợi ý điểm đến mới hoặc thay đổi tiêu chí:
  - Tóm tắt ngắn gọn và tự nhiên nhu cầu của họ.
  - Trình bày 3 điểm đến hàng đầu: Hãy miêu tả chúng theo cách khơi gợi cảm xúc (như kể một câu chuyện ngắn về nơi đó) thay vì chỉ liệt kê thông số.
  - Bổ sung "Mẹo du lịch độc quyền" (thời tiết, đồ cần mang) phù hợp riêng cho từng nơi.
  - Linh hoạt giải thích lý do đề xuất (nếu có quy luật).
  - Khéo léo nhắc người dùng có thể xem bản đồ để hình dung vị trí.

Trường hợp B: Người dùng hỏi tiếp nối, muốn đi sâu vào 1 điểm đến, hoặc hỏi về lịch trình, kinh nghiệm thực tế:
  - SỰ ĐA DẠNG TRONG CÁCH TIẾP CẬN (QUAN TRỌNG): KHÔNG lặp lại một khuôn mẫu cứng nhắc (như luôn là Ẩm thực -> Đi lại -> Lưu ý). Tùy thuộc vào câu hỏi mà bạn có thể đổi mới cách trả lời: 
      + Có thể kể chuyện về lịch sử bí ẩn của vùng đất.
      + Có thể viết dưới dạng "Checklist sinh tồn" hoặc "Bí kíp phượt thủ".
      + Có thể so sánh thú vị hoặc đưa ra lịch trình phá cách.
  - PHÂN TÍCH ĐA CHIỀU: Đào sâu vào nhiều khía cạnh (văn hóa, món ăn lạ, cách di chuyển tiết kiệm, chi phí thực tế) nhưng trình bày chúng thật tự nhiên.
  - ĐÓNG VAI CHUYÊN GIA BẢN ĐỊA: Đưa ra những lời khuyên "người trong cuộc" (insider tips) và các góc khuất ít người biết.

LƯU Ý CHUNG VỀ TRÌNH BÀY & GIỌNG ĐIỆU:
- GIỌNG ĐIỆU LINH HOẠT: Hãy thay đổi linh hoạt - có lúc hài hước rôm rả, có lúc sâu lắng nhẹ nhàng, có lúc dứt khoát như một phượt thủ chuyên nghiệp.
- BỐ CỤC SÁNG TẠO: Chia đoạn, sử dụng in đậm, in nghiêng, hoặc gạch đầu dòng một cách tinh tế. Không gò ép vào một form duy nhất cho mọi câu hỏi.
- Sử dụng emoji thông minh, tự nhiên để tạo cảm hứng xách ba lô lên và đi.
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini response generation failed: {e}. Using fallback.")
        return generate_response_fallback(message, prefs, destinations, rules)

# ─────────────────────────────────────────────
# QUICK INTENT RESPONSES
# ─────────────────────────────────────────────
def _greet_response() -> str:
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Chào buổi sáng"
    elif hour < 18:
        greeting = "Chào buổi chiều"
    else:
        greeting = "Chào buổi tối"
    return (
        f"{greeting}! 👋 Tôi là trợ lý tư vấn du lịch AI của hệ thống.\n\n"
        "Tôi có thể giúp bạn:\n"
        "  🌍 Gợi ý điểm đến theo mùa, ngân sách, loại hình\n"
        "  📊 Phân tích xu hướng du lịch từ dữ liệu thực\n"
        "  🗺 Định vị điểm đến trên bản đồ thế giới\n\n"
        "Hãy cho tôi biết bạn muốn đi đâu, vào mùa nào, "
        "với ngân sách bao nhiêu nhé! 😊"
    )

def _farewell_response() -> str:
    return (
        "Cảm ơn bạn đã sử dụng hệ thống tư vấn du lịch! 🙏\n"
        "Chúc bạn có chuyến đi an toàn và thật nhiều kỷ niệm đẹp. ✈️🌏\n"
        "Hẹn gặp lại bạn lần sau!"
    )

def _no_entity_response() -> str:
    return (
        "Xin lỗi, tôi chưa hiểu rõ yêu cầu du lịch của bạn. 🤔\n\n"
        "Bạn có thể thử hỏi theo dạng:\n"
        '  • "Gợi ý điểm đến mùa hè, ngân sách trung bình"\n'
        '  • "Tôi muốn đi Nhật Bản vào mùa thu, 7 ngày"\n'
        '  • "Điểm đến biển phù hợp cho cặp đôi, giá rẻ"\n\n'
        "Hoặc hỏi tôi về bất kỳ quốc gia, mùa, loại hình du lịch nào bạn thích! 🌐"
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
        _session_store[session_id] = {"history": [], "last_prefs": {}}
    session = _session_store[session_id]

    # Synchronize history from frontend if provided to support stateless/restarts
    if conversation_history:
        session["history"] = []
        for turn in conversation_history:
            role = "user" if turn.get("role") == "user" else "assistant"
            content = turn.get("parts") or turn.get("content") or ""
            if content:
                session["history"].append({"role": role, "content": content})
        
        # If the last message in synchronized history is the current message, remove it
        # so it doesn't get duplicated when we append it below.
        if session["history"] and session["history"][-1]["role"] == "user" and session["history"][-1]["content"] == user_message:
            session["history"].pop()

    has_history = len(session["history"]) > 0

    # ── 1. Intent detection ───────────────────
    intent = detect_intent(user_message)
    logger.info(f"[Pipeline] Intent: {intent}")

    # Append user message to history
    session["history"].append({"role": "user", "content": user_message})

    if intent == "greet":
        resp = _greet_response()
        session["history"].append({"role": "assistant", "content": resp})
        return {"response": resp, "preferences": {}, "recommendations": [],
                "intent": intent, "matched_rules": []}

    if intent == "farewell":
        resp = _farewell_response()
        session["history"].append({"role": "assistant", "content": resp})
        return {"response": resp, "preferences": {}, "recommendations": [],
                "intent": intent, "matched_rules": []}

    # ── 2. Entity extraction ──────────────────
    prefs = extract_entities(user_message)

    # Carry over prefs from last turn if current message only refines one field
    non_null = {k: v for k, v in prefs.items() if v is not None and not k.startswith("_")}
    if len(non_null) <= 2 and session["last_prefs"]:
        merged = {**session["last_prefs"], **non_null}
        prefs = {**prefs, **merged}
        logger.info(f"[Pipeline] Merged with previous prefs: {prefs}")

    # Save for next turn
    session["last_prefs"] = {k: v for k, v in prefs.items() if v and not k.startswith("_")}
    logger.info(f"[Pipeline] Final preferences: {prefs}")

    # Guard: if nothing extracted, ask for clarification
    useful_keys = ["season", "budget", "category", "country", "continent",
                   "duration_days", "traveler_type"]

    # ── Merge recommendation context from frontend wizard ─────
    rec_context_str = ""
    if recommendation_context:
        ctx_criteria = recommendation_context.get("criteria", {})
        ctx_dests = recommendation_context.get("destinations", [])

        # Merge wizard criteria into prefs if not already set by current message
        for key in ["season", "category", "budget"]:
            if ctx_criteria.get(key) and not prefs.get(key):
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
            for d in ctx_dests[:6]:
                dest_summaries.append(
                    f"  - {d.get('name', 'N/A')} ({d.get('country', 'N/A')}) "
                    f"– Loại: {d.get('type', 'N/A')}, Mùa tốt nhất: {d.get('season', 'N/A')}, "
                    f"Chi phí: ${d.get('cost', 'N/A')}/ngày"
                )
            rec_context_str += "Các điểm đến đã được hệ thống gợi ý cho người dùng:\n"
            rec_context_str += "\n".join(dest_summaries) + "\n"

        logger.info(f"[Pipeline] Recommendation context injected: {len(ctx_dests)} destinations")

    # Guard: if nothing extracted AND we don't have conversation history, ask for clarification
    if not has_history and not any(prefs.get(k) for k in useful_keys):
        resp = _no_entity_response()
        session["history"].append({"role": "assistant", "content": resp})
        return {"response": resp, "preferences": prefs, "recommendations": [],
                "intent": intent, "matched_rules": []}

    # ── 3. Apriori rule matching ──────────────
    matched_rules = get_matching_rules(prefs)
    rule_countries = []
    for r in matched_rules:
        for item in r.get("consequents", []):
            if "Country:" in item:
                rule_countries.append(item.replace("Country:", "").strip())

    # ── 4. Candidate retrieval & scoring ──────
    all_dests = db_storage.load_destinations()

    explicit_country    = prefs.get("country")              # e.g. "Japan"
    continent_countries = prefs.get("_continent_countries", [])
    filter_active = any(prefs.get(k) for k in ["season", "budget", "category",
                                                "country", "continent"])
    candidates = []
    for d in all_dests:
        dest = dict(d)   # defensive copy

        # ── Hard filter: when user explicitly names a country,
        #    ONLY include destinations from that country so we never
        #    recommend South Korea when user asked for Japan.
        if explicit_country:
            if dest.get("Country") != explicit_country:
                continue    # skip all other countries

        # ── Continent filter: restrict to continent when no specific country named.
        elif continent_countries:
            if dest.get("Country") not in continent_countries:
                continue

        # ── General filter: at least one preference signal must score > 0.
        elif filter_active:
            if score_candidate(dest, prefs, rule_countries) <= 0:
                continue

        s = score_candidate(dest, prefs, rule_countries)
        dest["match_score"] = s
        candidates.append(dest)

    # ── Safety net: if strict filter produced zero results, broaden to all
    if not candidates:
        logger.warning(
            f"[Pipeline] No candidates after strict filter "
            f"(country={explicit_country}). Broadening to all destinations."
        )
        candidates = [dict(d) for d in all_dests]
        for d in candidates:
            d["match_score"] = score_candidate(d, prefs, rule_countries)
        logger.info(f"[Pipeline] Broadened pool: {len(candidates)} destinations.")

    # ── 5. Content-based TF-IDF re-ranking ────
    ranked = content_recommender.rank_candidates(candidates, prefs)

    def sort_key(x):
        return (x.get("match_score", 0), x.get("content_score", 0.0) or 0.0)

    ranked.sort(key=sort_key, reverse=True)
    top_recommendations = ranked[:6]

    # ── 6. Response generation ────────────────
    response_text = generate_response(
        user_message, prefs, top_recommendations,
        matched_rules, session["history"],
        recommendation_context_str=rec_context_str
    )
    session["history"].append({"role": "assistant", "content": response_text})

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