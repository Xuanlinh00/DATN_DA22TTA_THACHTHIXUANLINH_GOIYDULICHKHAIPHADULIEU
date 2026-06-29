"""
Test script to verify conversation context handling improvements
Kiểm tra khả năng chatbot nhớ và tham chiếu lại các đoạn chat trước đó
"""
import sys
import json

# Test cases for conversation context
test_conversations = [
    {
        "name": "Test 1: Tham chiếu điểm đến đã đề cập",
        "messages": [
            {"role": "user", "content": "Tôi muốn đi du lịch biển vào mùa hè"},
            # Giả sử bot đã gợi ý Phuket
            {"role": "assistant", "content": "Tôi gợi ý cho bạn Phuket, Thái Lan - một điểm đến biển tuyệt vời vào mùa hè"},
            {"role": "user", "content": "Chi phí ở đó khoảng bao nhiêu?"}  # "đó" tham chiếu Phuket
        ]
    },
    {
        "name": "Test 2: Hỏi tiếp về thông tin đã nhắc",
        "messages": [
            {"role": "user", "content": "Gợi ý cho tôi điểm đến mùa đông ở Châu Âu"},
            {"role": "assistant", "content": "Tôi gợi ý cho bạn Paris, London và Rome"},
            {"role": "user", "content": "Nơi nào trong số đó phù hợp với gia đình có trẻ nhỏ?"}
        ]
    },
    {
        "name": "Test 3: Câu hỏi follow-up với đại từ",
        "messages": [
            {"role": "user", "content": "Tôi muốn đi Tokyo"},
            {"role": "assistant", "content": "Tokyo là lựa chọn tuyệt vời! Mùa xuân là thời điểm đẹp nhất"},
            {"role": "user", "content": "Thời tiết ở đó như thế nào?"}  # "đó" = Tokyo
        ]
    },
    {
        "name": "Test 4: Hỏi tiếp về lịch sử trò chuyện",
        "messages": [
            {"role": "user", "content": "Tôi thích du lịch mạo hiểm núi non"},
            {"role": "assistant", "content": "Bạn có thể thử Nepal hoặc Bhutan"},
            {"role": "user", "content": "Bạn vừa gợi ý gì cho tôi?"}  # Tham chiếu lại câu trước
        ]
    },
    {
        "name": "Test 5: Sử dụng từ 'này', 'kia', 'đấy'",
        "messages": [
            {"role": "user", "content": "Nên đi Đà Nẵng hay Nha Trang?"},
            {"role": "assistant", "content": "Cả hai đều tuyệt vời, nhưng Đà Nẵng có nhiều hoạt động hơn"},
            {"role": "user", "content": "Thế ẩm thực ở chỗ này ra sao?"}  # "này" = Đà Nẵng
        ]
    }
]

def format_conversation_for_api(messages):
    """Format messages into the API conversation_history format"""
    return [
        {
            "role": msg["role"],
            "content": msg["content"],
            "isContextMessage": False
        }
        for msg in messages[:-1]  # Exclude last message (current query)
    ]

def test_conversation_context():
    """Test conversation context handling"""
    print("=" * 80)
    print("KIỂM TRA KHẢ NĂNG NHỚ VÀ THAM CHIẾU LỊCH SỬ HỘI THOẠI")
    print("=" * 80)
    print()
    
    for i, test in enumerate(test_conversations, 1):
        print(f"\n{'─' * 80}")
        print(f"📋 {test['name']}")
        print('─' * 80)
        
        messages = test['messages']
        
        # Display conversation history
        print("\n💬 Lịch sử hội thoại:")
        for j, msg in enumerate(messages[:-1], 1):
            role_emoji = "👤" if msg["role"] == "user" else "🤖"
            print(f"{role_emoji} {msg['role'].upper()}: {msg['content']}")
        
        print(f"\n❓ Câu hỏi hiện tại (cần xử lý):")
        current_msg = messages[-1]
        print(f"   👤 USER: {current_msg['content']}")
        
        # Prepare API request
        conversation_history = format_conversation_for_api(messages)
        
        print(f"\n📊 Phân tích:")
        print(f"   • Số lượng tin nhắn trong lịch sử: {len(conversation_history)}")
        print(f"   • Câu hỏi có chứa từ tham chiếu: ", end="")
        
        reference_words = ['đó', 'này', 'kia', 'đấy', 'ở đó', 'chỗ đó', 'nơi đó', 
                          'điểm đó', 'bạn vừa', 'trong số', 'nơi nào', 'chỗ này']
        has_reference = any(word in current_msg['content'].lower() for word in reference_words)
        print("✓ Có" if has_reference else "✗ Không")
        
        print(f"\n🎯 Kỳ vọng:")
        print(f"   • Bot phải hiểu ngữ cảnh từ lịch sử hội thoại")
        print(f"   • Bot phải tham chiếu đúng điểm đến/thông tin đã nhắc")
        print(f"   • Không được hỏi lại hoặc trả lời sai ngữ cảnh")
        
        # Show API request format
        print(f"\n📤 API Request Format:")
        api_request = {
            "message": current_msg['content'],
            "session_id": f"test_session_{i}",
            "conversation_history": conversation_history,
            "recommendation_context": None
        }
        print(json.dumps(api_request, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 80)
    print("✅ CÁC CẢI TIẾN ĐÃ THỰC HIỆN:")
    print("=" * 80)
    print("""
1. ✓ Tăng số lượng turns được lưu từ 12 lên 16 (8 lượt hội thoại)
2. ✓ Giữ lại context messages với label để Gemini biết
3. ✓ Mở rộng danh sách pattern nhận diện câu hỏi follow-up
4. ✓ Lưu trữ mentioned_destinations để tracking các điểm đã thảo luận
5. ✓ Cải thiện logic nhận diện khi user dùng đại từ tham chiếu
6. ✓ Thêm hướng dẫn rõ ràng cho Gemini về cách xử lý lịch sử
7. ✓ Log chi tiết để debug conversation context
8. ✓ Merge consecutive same-role messages để tránh lỗi API
    """)
    
    print("\n📝 HƯỚNG DẪN TEST THỰC TÊ:")
    print("""
1. Khởi động backend: cd backend && python -m uvicorn api.routes:app --reload
2. Mở frontend và bắt đầu chat
3. Thử các trường hợp test ở trên
4. Kiểm tra log để xem conversation_history được xử lý
5. Verify bot trả lời đúng ngữ cảnh và tham chiếu đúng
    """)

if __name__ == "__main__":
    test_conversation_context()
