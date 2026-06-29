# CÔNG THỨC ĐÚNG CHO TÀI LIỆU - SỬA CÁC LỖI ĐÃ CHỈ RA

## 1. CÔNG THỨC final_score (Mục 3.4.1.1) - BẢN ĐÚNG

### Công thức có điều kiện:

**Trường hợp 1: CÓ luật Apriori khớp (matching_rules > 0)**
```
final_score = 0.6 × content_score + 0.4 × apriori_score
```

**Trường hợp 2: KHÔNG có luật Apriori nào khớp (matching_rules = 0)**
```
final_score = content_score
```
*(Không nhân hệ số, không cộng apriori_score)*

### Collaborative Bonus (nếu có user_id):
```
IF destination IN top_50_CF_recommendations THEN
    final_score = min(final_score + 0.15, 1.0)
```
*(Cộng cố định +0.15, không phải một giá trị biến thiên, và cap tại 1.0)*

---

## 2. CÔNG THỨC apriori_score - BẢN ĐÚNG

**KHÔNG PHẢI:** `apriori_score(d) = Σ (confidence(r) × lift(r))`

**MÀ LÀ:**

```python
# Bước 1: Trích xuất các boost signal từ tất cả rules khớp
boosts = {
    'countries': {},
    'continents': {},
    'types': {},
    'costs': {}
}

# Với mỗi rule khớp, parse consequent để lấy các giá trị boost
for rule in matching_rules:
    # Ví dụ: consequent = "Country=France"
    # boost_value = confidence × lift
    # boosts['countries']['France'] = boost_value

# Bước 2: Tính apriori_score cho destination d
country_score   = boosts['countries'].get(d.Country, 0.0)
continent_score = boosts['continents'].get(d.Continent, 0.0)
type_score      = boosts['types'].get(d.Type, 0.0)
cost_score      = boosts['costs'].get(d.Cost_Category, 0.0)

# Bước 3: Tính tổng có trọng số
raw_score = (
    0.40 × country_score +
    0.25 × continent_score +
    0.20 × type_score +
    0.15 × cost_score
)

# Bước 4: Normalize về [0, 1]
apriori_score = min(raw_score, 1.0)
```

**Trọng số ưu tiên:**
- Country: 40%
- Continent: 25%
- Type: 20%
- Cost_Category: 15%

---

## 3. PSEUDOCODE ĐÚNG - Hàm get_recommendations()

```
FUNCTION get_recommendations(filters, limit, user_id):
    
    // ── Bước 1: Lọc ứng viên với Soft Relaxation ───────────────
    candidates = filter_destinations(filters)
    
    IF candidates.empty THEN
        // Nới lỏng tuần tự: country → budget → season → category
        relaxed_filters = relax_filters_sequentially(filters)
        candidates = filter_destinations(relaxed_filters)
    END IF
    
    // ── Bước 2: Xếp hạng Content-Based (TF-IDF) ────────────────
    ranked_candidates = content_recommender.rank_candidates(candidates, filters)
    
    // ── Bước 3: Tìm luật Apriori khớp ──────────────────────────
    matching_rules = get_matching_rules(filters)
    boosts = parse_consequent_boost(matching_rules)
    has_apriori = (matching_rules.length > 0)
    
    // ── Bước 4: Tính điểm Hybrid ────────────────────────────────
    FOR EACH destination IN ranked_candidates DO
        content_s = destination.content_score
        
        IF has_apriori THEN
            // Tính apriori_score
            country_score   = boosts['countries'][destination.Country]
            continent_score = boosts['continents'][destination.Continent]
            type_score      = boosts['types'][destination.Type]
            cost_score      = boosts['costs'][destination.Cost_Category]
            
            apriori_s = min(
                0.40 × country_score +
                0.25 × continent_score +
                0.20 × type_score +
                0.15 × cost_score,
                1.0
            )
            
            // Công thức Hybrid
            final_s = 0.6 × content_s + 0.4 × apriori_s
        ELSE
            // Không có rule → chỉ dùng content
            apriori_s = 0.0
            final_s = content_s
        END IF
        
        destination.apriori_score = apriori_s
        destination.final_score   = final_s
        destination.matched_rules = matching_rules.length
    END FOR
    
    // ── Bước 5: Collaborative Filtering Boost ──────────────────
    IF user_id IS NOT NULL THEN
        user_recs = collaborative_recommender.get_user_recommendations(user_id, 50)
        user_rec_names = {r.name for r in user_recs}
        
        FOR EACH destination IN ranked_candidates DO
            IF destination.name IN user_rec_names THEN
                destination.final_score = min(destination.final_score + 0.15, 1.0)
            END IF
        END FOR
    END IF
    
    // ── Bước 6: Sắp xếp và trả về Top-N ────────────────────────
    // Ưu tiên: destinations có Real_Description → sau đó theo final_score
    sorted_results = sort_by(has_description DESC, final_score DESC)
    
    RETURN sorted_results[:limit]
END FUNCTION
```

---

## 4. BẢNG 3.6: API ENDPOINTS ĐÚNG (Khớp với Code và Bảng 3.4)

| **Endpoint** | **Method** | **Mô tả** |
|-------------|-----------|-----------|
| `/api/recommendations` | **POST** | Gợi ý điểm đến dựa trên filters + user_id |
| `/api/search` | GET | Tìm kiếm full-text destinations |
| `/api/similar/<name>` | GET | Lấy destinations tương tự theo TF-IDF |
| `/api/rules` | GET | Lấy thông tin Apriori rules khớp |
| `/api/admin/run-clustering` | POST | Chạy K-Means clustering |
| `/api/admin/run-apriori` | POST | Chạy thuật toán Apriori mining |
| `/api/admin/refresh-cf` | POST | Làm mới Collaborative Filtering matrix |
| `/api/admin/reload-data` | POST | Tải lại dữ liệu từ MongoDB/CSV |
| `/api/admin/update-all-images` | POST | Cập nhật tất cả images từ Pixabay API |
| `/api/admin/users` | GET | Quản lý danh sách users |
| `/api/admin/ratings` | GET/POST/DELETE | Quản lý ratings |
| `/api/admin/rules` | GET | Xem tất cả Apriori rules |

**Lưu ý:** 
- Endpoint `/api/recommendations` dùng **POST** (không phải GET) vì cần gửi JSON body chứa filters
- Bảng này đã bổ sung các endpoint admin còn thiếu

---

## 5. JSON RESPONSE MẪU ĐÚNG

**Request:**
```json
POST /api/recommendations
{
  "filters": {
    "season": "Summer",
    "budget": "Mid-Range",
    "category": "Beach",
    "country": "Thailand"
  },
  "limit": 5,
  "user_id": 12345
}
```

**Response (Trường hợp CÓ Apriori rules):**
```json
{
  "results": [
    {
      "Destination Name": "Phuket Beach Resort",
      "Country": "Thailand",
      "Type": "Beach",
      "Cost_Category": "Mid-Range",
      "content_score": 0.91,
      "apriori_score": 0.76,
      "final_score": 0.85,      // = 0.6 × 0.91 + 0.4 × 0.76 = 0.546 + 0.304 = 0.85
      "matched_rules": 12,
      "Real_Description": "Beautiful beach..."
    }
  ],
  "relaxed_filters": []
}
```

**Response (Trường hợp KHÔNG có Apriori rules):**
```json
{
  "results": [
    {
      "Destination Name": "Hidden Beach",
      "content_score": 0.84,
      "apriori_score": 0.0,
      "final_score": 0.84,      // = content_score (không nhân hệ số)
      "matched_rules": 0
    }
  ]
}
```

**Response (Có CF boost):**
```json
{
  "results": [
    {
      "Destination Name": "Phuket Beach Resort",
      "content_score": 0.91,
      "apriori_score": 0.76,
      "final_score": 1.0,       // = min(0.85 + 0.15, 1.0) = 1.0 (capped)
      "matched_rules": 12,
      "cf_boosted": true
    }
  ]
}
```

---

## 6. MÔ TẢ COLLABORATIVE_BONUS ĐÚNG

**Cơ chế thực tế:**

1. **Điều kiện kích hoạt:** Chỉ khi `user_id` được cung cấp
2. **Lấy top-50 CF recommendations** cho user đó
3. **Kiểm tra membership:** Với mỗi destination trong ranked_candidates:
   - Nếu destination nằm trong top-50 CF → cộng **+0.15** (cố định)
   - Nếu không → giữ nguyên
4. **Cap tại 1.0:** `final_score = min(final_score + 0.15, 1.0)`

**KHÔNG PHẢI:**
- ❌ "Không có trọng số cố định"
- ❌ "Cộng trực tiếp giá trị biến thiên"
- ❌ "Bonus phụ thuộc vào vị trí trong top-50"

**MÀ LÀ:**
- ✅ Bonus **cố định +0.15** cho tất cả destinations trong top-50
- ✅ **Binary decision:** trong top-50 = +0.15, ngoài top-50 = +0
- ✅ **Hard cap** tại 1.0

---

## 7. TÓM TẮT CÁC ĐIỂM ĐÃ SỬA

| **Mục** | **Lỗi cũ** | **Bản đúng** |
|---------|-----------|--------------|
| **final_score** | Luôn cộng 3 thành phần | Có điều kiện: có rule → 0.6×content + 0.4×apriori; không có rule → content only |
| **apriori_score** | Σ(confidence × lift) | 0.4×country + 0.25×continent + 0.2×type + 0.15×cost, normalize [0,1] |
| **collaborative_bonus** | "Không trọng số cố định" | +0.15 cố định nếu trong top-50, cap 1.0 |
| **Endpoint method** | GET /api/recommendations | POST /api/recommendations |
| **JSON response** | Số học sai | Đã sửa: 0.6×0.91 + 0.4×0.76 = 0.85 |
| **Pseudocode** | Thiếu nhánh IF-ELSE | Đã bổ sung điều kiện has_apriori |

---

## 8. THAM CHIẾU CODE THẬT

**File:** `backend/recommender_engine.py`

**Hàm tính apriori_score:** Dòng 70-103
```python
def _compute_apriori_score(dest: dict, boosts: dict) -> float:
    country_score   = boosts['countries'].get(country, 0.0)
    continent_score = boosts['continents'].get(continent, 0.0)
    type_score      = boosts['types'].get(d_type, 0.0)
    cost_score      = boosts['costs'].get(cost, 0.0)
    
    raw = (
        0.40 * country_score +
        0.25 * continent_score +
        0.20 * type_score +
        0.15 * cost_score
    )
    return min(raw, 1.0)
```

**Hàm tính final_score:** Dòng 243-254
```python
if has_apriori:
    final_s = 0.60 * content_s + 0.40 * apriori_s
else:
    # No Apriori rules found → fall back to content-only
    final_s = content_s
```

**CF boost:** Dòng 260-266
```python
if item['Destination Name'] in user_rec_names:
    item['final_score'] = min(item['final_score'] + 0.15, 1.0)
```

---

**Ngày cập nhật:** 2024-06-27  
**Nguồn:** Phân tích từ `backend/recommender_engine.py` (code thật)
