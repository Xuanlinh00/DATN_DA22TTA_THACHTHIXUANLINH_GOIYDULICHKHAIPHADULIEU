# -*- coding: utf-8 -*-
"""Test chat with conversation history like frontend sends"""

import requests
import json

url = "http://127.0.0.1:8000/api/chat"

# Test 1: First message (no history)
print("=" * 80)
print("TEST 1: First message (no history)")
print("=" * 80)
payload1 = {
    "message": "Xin chào",
    "session_id": "frontend_test",
    "conversation_history": [],
    "recommendation_context": None
}

try:
    r1 = requests.post(url, json=payload1, timeout=10)
    print(f"Status: {r1.status_code}")
    if r1.status_code == 200:
        data1 = r1.json()
        print(f"✓ Response: {data1['response'][:100]}...")
        
        # Test 2: Follow-up with history
        print("\n" + "=" * 80)
        print("TEST 2: Follow-up with history")
        print("=" * 80)
        
        payload2 = {
            "message": "Gợi ý du lịch biển giá rẻ",
            "session_id": "frontend_test",
            "conversation_history": [
                {"role": "user", "content": "Xin chào"},
                {"role": "assistant", "content": data1['response']}
            ],
            "recommendation_context": None
        }
        
        r2 = requests.post(url, json=payload2, timeout=30)
        print(f"Status: {r2.status_code}")
        if r2.status_code == 200:
            data2 = r2.json()
            print(f"✓ Response: {data2['response'][:100]}...")
            print(f"✓ Recommendations: {len(data2['recommendations'])}")
        else:
            print(f"✗ ERROR: {r2.text[:300]}")
    else:
        print(f"✗ ERROR: {r1.text[:300]}")
        
except Exception as e:
    print(f"✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
