# -*- coding: utf-8 -*-
"""Test fallback response when Gemini fails"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from nlp.gemini_module import process_chat_query

print("Testing fallback response...")
try:
    result = process_chat_query("Gợi ý du lịch biển giá rẻ", session_id="test_fallback")
    print(f"\n✓ SUCCESS")
    print(f"Response length: {len(result['response'])} chars")
    print(f"Recommendations: {len(result['recommendations'])} destinations")
    print(f"Intent: {result['intent']}")
    print(f"\nResponse preview:\n{result['response'][:200]}...")
except Exception as e:
    print(f"\n✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
