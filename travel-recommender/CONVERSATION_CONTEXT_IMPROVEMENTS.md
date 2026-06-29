# Cải Tiến Xử Lý Ngữ Cảnh Hội Thoại (Conversation Context)

## 🎯 Mục Tiêu

Cải thiện khả năng chatbot **nhớ và tham chiếu** các đoạn chat trước đó trong cùng một phiên, giúp người dùng có thể:
- Hỏi tiếp các câu hỏi mà không cần nhắc lại thông tin
- Sử dụng đại từ tham chiếu như "đó", "này", "chỗ đó", "nơi vừa rồi"
- Có trải nghiệm hội thoại tự nhiên như với con người

## ✅ Các Cải Tiến Đã Thực Hiện

### 1. **Tăng Độ Sâu Lịch Sử Hội Thoại**
```python
# TRƯỚC: 12 turns (6 lượt)
recent = conversation_history[-12:-1]

# SAU: 16 turns (8 lượt)
recent = conversation_history[-16:-1]
```
**Lợi ích:** Chatbot có thể nhớ các cuộc hội thoại dài hơn, tham chiếu xa hơn trong lịch sử.

### 2. **Giữ Lại Context Messages**
```python
# TRƯỚC: Lọc bỏ hoàn toàn context messages
if is_ctx_msg:
    continue  # Bỏ qua

# SAU: Giữ lại nhưng đánh dấu
if is_ctx_msg and role == "user":
    turn_content = f"[Ngữ cảnh hệ thống: {turn_content}]"
```
**Lợi ích:** Gemini biết đâu là tin nhắn tự động, nhưng vẫn có đủ ngữ cảnh để hiểu.

### 3. **Mở Rộng Pattern Nhận Diện Follow-up**
```python
_CONTEXT_FOLLOWUP_PATTERNS = [
    # Từ tham chiếu ngữ cảnh
    "điểm đến này", "địa điểm này", "chỗ này", "nơi này",
    "điểm đến đó", "địa điểm đó", "chỗ đó", "nơi đó",
    
    # Từ tham chiếu thời gian
    "vừa rồi", "vừa gợi ý", "lúc nãy", "hồi nãy",
    "bạn đã nói", "bạn đã gợi ý", "như bạn đã",
    
    # Từ hỏi tiếp theo
    "còn", "thêm", "nữa", "khác", "tiếp theo",
    
    # Đại từ chỉ định
    "đó", "này", "ấy", "kia", "đấy",
]
```
**Lợi ích:** Hệ thống nhận diện tốt hơn khi user đang hỏi tiếp.

### 4. **Tracking Điểm Đến Đã Thảo Luận**
```python
# Lưu trữ các điểm đến đã đề cập
session["mentioned_destinations"] = []

# Cập nhật khi có gợi ý mới
if first_dest_name not in session["mentioned_destinations"]:
    session["mentioned_destinations"].append(first_dest_name)
    session["mentioned_destinations"] = session["mentioned_destinations"][-10:]
```
**Lợi ích:** Hệ thống biết những điểm đến nào đã được nhắc đến trong cuộc trò chuyện.

### 5. **Cải Thiện Logic Nhận Diện Tham Chiếu**
```python
# Kiểm tra có từ tham chiếu không
msg_lower = user_message.lower()
has_followup_pattern = any(p in msg_lower for p in _CONTEXT_FOLLOWUP_PATTERNS)
has_no_new_entities = (len(non_null) == 0 and has_history)

# Kích hoạt context followup nếu:
# - Có pattern tham chiếu HOẶC không có entity mới nhưng có lịch sử
# - Không phải filter hoàn toàn mới
is_context_followup = (
    len(ctx_dests_raw) > 0 and
    (has_followup_pattern or has_no_new_entities) and
    not _new_strong_filter
)
```

### 6. **Hướng Dẫn Rõ Ràng Cho Gemini**
```python
followup_instruction = f"""
⚡ NHIỆM VỤ NGAY LÚC NÀY (ƯU TIÊN CAO NHẤT):
Người dùng đang hỏi về điểm đến: 👉 {dest_names}
Họ có thể dùng các từ tham chiếu như "điểm đến này", "nơi đó", "chỗ đó"...
Hãy TRẢ LỜI TRỰC TIẾP về điểm đến này. KHÔNG được đề xuất điểm đến mới khác.
"""

current_query_context = f"""
❗ HƯỚNG DẪN XỬ LÝ HỘI THOẠI:
  • Đây là cuộc hội thoại nhiều lượt. Hãy đọc kỹ LỊCH SỬ HỘI THOẠI.
  • Nếu người dùng dùng từ tham chiếu... → họ đang ám chỉ điểm đến đã được nhắc.
  • Trả lời ĐÚNG điểm đến được đề cập, KHÔNG đoán sai hoặc gợi ý điểm khác.
"""
```

### 7. **Enhanced Logging**
```python
logger.info(f"[Session] History length: {len(session['history'])}, has_history={has_history}")
logger.info(f"[Session] Updated last_discussed_dest='{first_dest_name}'")
logger.info(f"[Session] Mentioned destinations: {session['mentioned_destinations']}")
logger.info(f"[Gemini] Using {len(contents)} conversation turns for context")
```
**Lợi ích:** Dễ debug và theo dõi cách hệ thống xử lý lịch sử.

## 📋 Test Cases

### Test 1: Tham chiếu điểm đến đã đề cập
```
User: "Tôi muốn đi du lịch biển vào mùa hè"
Bot: "Tôi gợi ý cho bạn Phuket, Thái Lan..."
User: "Chi phí ở đó khoảng bao nhiêu?"  ← "đó" = Phuket
```

### Test 2: Hỏi tiếp về thông tin đã nhắc
```
User: "Gợi ý cho tôi điểm đến mùa đông ở Châu Âu"
Bot: "Tôi gợi ý cho bạn Paris, London và Rome"
User: "Nơi nào trong số đó phù hợp với gia đình?"  ← "trong số đó"
```

### Test 3: Câu hỏi follow-up với đại từ
```
User: "Tôi muốn đi Tokyo"
Bot: "Tokyo là lựa chọn tuyệt vời!"
User: "Thời tiết ở đó như thế nào?"  ← "đó" = Tokyo
```

### Test 4: Hỏi tiếp về lịch sử trò chuyện
```
User: "Tôi thích du lịch mạo hiểm núi non"
Bot: "Bạn có thể thử Nepal hoặc Bhutan"
User: "Bạn vừa gợi ý gì cho tôi?"  ← Tham chiếu lại
```

### Test 5: Sử dụng từ 'này', 'kia', 'đấy'
```
User: "Nên đi Đà Nẵng hay Nha Trang?"
Bot: "Cả hai đều tuyệt vời, nhưng Đà Nẵng có nhiều hoạt động hơn"
User: "Thế ẩm thực ở chỗ này ra sao?"  ← "này" = Đà Nẵng
```

## 🚀 Cách Test

### 1. Chạy Test Script
```bash
cd backend
python test_conversation_context.py
```

### 2. Test Thực Tế Với Frontend
```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn api.routes:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

### 3. Kiểm Tra Logs
Xem terminal backend để theo dõi:
```
[Session] History length: 4, has_history=True
[Pipeline] has_followup_pattern=True, has_no_new_entities=False
[Pipeline] is_context_followup=True
[Session] Updated last_discussed_dest='Phuket'
[Gemini] Using 2 conversation turns for context
```

## 🎓 Cách Hoạt Động

### Flow Xử Lý Conversation Context

```
1. User gửi message + conversation_history
                ↓
2. Rebuild session["history"] từ frontend
   - Giữ lại ALL messages (kể cả context)
   - Đánh dấu context messages
   - Tránh duplicate
                ↓
3. Kiểm tra có pattern follow-up không?
   - Từ tham chiếu (đó, này, chỗ đó...)
   - Không có entity mới nhưng có history
                ↓
4. Xác định effective_viewing_dest
   - currentViewingDestination (URL)
   - last_discussed_dest (session)
   - mentioned_destinations (history)
                ↓
5. Build Gemini context với:
   - Recent 16 turns history
   - Current query + instructions
   - Follow-up instruction (nếu cần)
                ↓
6. Gemini generate response
   - Hiểu ngữ cảnh từ history
   - Tham chiếu đúng điểm đến
   - Trả lời tự nhiên
                ↓
7. Update session state
   - Append response to history
   - Update last_discussed_dest
   - Add to mentioned_destinations
```

## 📊 So Sánh Trước/Sau

| Tính năng | Trước | Sau |
|-----------|-------|-----|
| Số turns lưu | 12 (6 lượt) | 16 (8 lượt) |
| Context messages | Bỏ qua | Giữ lại + đánh dấu |
| Pattern follow-up | ~15 patterns | ~40+ patterns |
| Tracking điểm đến | Chỉ last_dest | List 10 destinations |
| Follow-up detection | Pattern only | Pattern + No entity logic |
| Gemini instructions | Cơ bản | Chi tiết + ví dụ |
| Logging | Minimal | Chi tiết debug |

## 🔍 Debug Tips

### Nếu bot không hiểu ngữ cảnh:
1. Kiểm tra `conversation_history` có được gửi đúng không
2. Xem log `[Session] History length` → phải > 0
3. Kiểm tra `has_followup_pattern` hoặc `has_no_new_entities`
4. Verify `is_context_followup` hoặc `is_viewing_dest_followup` = True

### Nếu bot tham chiếu sai điểm đến:
1. Xem `last_discussed_dest` có đúng không
2. Kiểm tra `mentioned_destinations` list
3. Verify `effective_viewing_dest` được set đúng
4. Đọc log `[Pipeline]` để hiểu logic decision

## 📝 Files Changed

1. **backend/nlp/gemini_module.py**
   - `process_chat_query()`: Session management + history sync
   - `generate_response()`: History processing + Gemini context
   - Pattern lists expansion
   - Enhanced logging

2. **backend/test_conversation_context.py** (NEW)
   - Test cases
   - Documentation
   - Usage examples

3. **CONVERSATION_CONTEXT_IMPROVEMENTS.md** (NEW)
   - This file - comprehensive documentation

## ✨ Kết Quả Mong Đợi

Sau khi cải tiến, chatbot sẽ:

✅ Hiểu và trả lời đúng khi user dùng đại từ tham chiếu  
✅ Nhớ các điểm đến đã thảo luận trong 8 lượt hội thoại  
✅ Không hỏi lại thông tin đã được cung cấp  
✅ Tự động nhận diện câu hỏi follow-up  
✅ Trả lời tự nhiên như hội thoại thực tế  
✅ Dễ debug với logging chi tiết  

## 🎉 Hoàn Thành!

Hệ thống đã được cải thiện đáng kể về khả năng xử lý ngữ cảnh hội thoại. Người dùng giờ đây có thể chat tự nhiên mà không cần lo lắng bot "quên" những gì vừa nói!
