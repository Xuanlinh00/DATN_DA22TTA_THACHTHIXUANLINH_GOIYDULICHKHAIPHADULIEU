# -*- coding: utf-8 -*-
"""Test image URL generation"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.fallback_images import get_fallback_image

# Test với 3 destinations khác nhau cùng country
dest1 = "Phuket Beach"
dest2 = "Krabi Beach"
dest3 = "Pattaya Beach"

url1 = get_fallback_image("Thailand", "Beach", dest1)
url2 = get_fallback_image("Thailand", "Beach", dest2)
url3 = get_fallback_image("Thailand", "Beach", dest3)

print("Testing URL generation:")
print(f"1. {dest1}: {url1}")
print(f"2. {dest2}: {url2}")
print(f"3. {dest3}: {url3}")
print(f"\nUnique URLs: {len({url1, url2, url3})}/3")
