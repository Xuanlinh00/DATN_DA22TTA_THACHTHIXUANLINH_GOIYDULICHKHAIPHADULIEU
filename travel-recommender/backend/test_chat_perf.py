# -*- coding: utf-8 -*-
"""Test chatbot performance"""

import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from nlp.gemini_module import process_chat_query

print("=" * 80)
print("TESTING CHATBOT PERFORMANCE")
print("=" * 80)

test_queries = [
    "Xin chào",
    "Gợi ý du lịch Nhật Bản mùa xuân",
    "Tôi muốn đi biển giá rẻ",
]

for query in test_queries:
    print(f"\n{'─'*80}")
    print(f"USER: {query}")
    
    start = time.time()
    try:
        result = process_chat_query(query, session_id="test")
        elapsed = time.time() - start
        
        print(f"✓ SUCCESS ({elapsed:.2f}s)")
        print(f"  Intent: {result['intent']}")
        print(f"  Recs:   {len(result['recommendations'])} destinations")
        print(f"  Response: {result['response'][:100]}...")
    except Exception as e:
        elapsed = time.time() - start
        print(f"✗ ERROR ({elapsed:.2f}s): {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
