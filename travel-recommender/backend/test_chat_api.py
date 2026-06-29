# -*- coding: utf-8 -*-
"""Test chat API endpoint"""

import requests
import json

url = "http://127.0.0.1:8000/api/chat"
payload = {
    "message": "Gợi ý du lịch biển",
    "session_id": "test",
    "conversation_history": [],
    "recommendation_context": None
}

print("Testing /api/chat endpoint...")
print(f"URL: {url}")
print(f"Payload: {json.dumps(payload, ensure_ascii=False)}\n")

try:
    response = requests.post(url, json=payload, timeout=30)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS")
        print(f"Response: {data.get('response', '')[:150]}...")
        print(f"Recommendations: {len(data.get('recommendations', []))}")
    else:
        print(f"✗ ERROR {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except Exception as e:
    print(f"✗ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()
